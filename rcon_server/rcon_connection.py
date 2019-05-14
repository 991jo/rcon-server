import asyncio
import logging

from .rcon_packet import RCONPacket

logger = logging.getLogger(name="RCONServer")

class RCONConnection(asyncio.Protocol):
    def __init__(self, rcon_server):
        """Initializes a new connection with a client.

        :param rcon_server: The RCONServer which handles the commands
        :param conn: the connection (tcp socket)
        """
        logger.info("started initialization of a RCON Connection")
        self._rcon_server = rcon_server
        self._state = "unauthenticated"

        # State machine for the connection:
        # 1. "unauthenticated
        # 2. "authenticated
        # 3. "closed"
        # State transitions: 1 -> 2 -> 3

        self._buffer = b"" # buffer for the data received from the connection
        self._running = True
        self._transport = None

        # append the RCONConnection to the RCONServer Connections
        self._rcon_server.connections.append(self)

    def connection_made(self, transport):
        """This method is called when a client connects and the transport
        is initialized. Transport is a TCP connection in this case."""
        logger.info("connection made")
        self._transport = transport

    def connection_lost(self, exc):
        """This method is called when the transport is closed.
        If *exc* is None either the connection has received a regular EOF or
        the connection was closed from this side. If *exc* is an Exception
        the other side has closed the connection not orderly."""
        self._state = "closed"

    def data_received(self, data):
        """This method is called when the socket has received data."""
        # check if the state of the RCON connection is not closed
        if self._state != "closed":
            self._buffer += data
            # check if packet is complete
            packet, buffer = RCONPacket.from_buffer(self._buffer)
            if packet is not None:
                self._buffer = buffer
                self._handle_packet(packet)
        else:
            self._transport.close()

    def eof_received(self):
        """This method is called when the other side has closed its connection.
        :return: False because the transport may close itself.
        """
        self._state = "closed"

    def close_connection(self):
        """
        Closes the connection. This is used when the password is written
        or the client sends an invalid command. This also closes the underlying
        transport.
        """
        logger.info("closing")
        self._state = "closed"
        self._transport.close()

    def _handle_packet(self, packet):
        """
        Handles the received packet.
        :param packet: a RCONPacket
        """
        logger.info(f"received packet {packet!r}")

        # Handling of empty SERVERDATA_RESPONSE_VALUE packages precedes everything.
        if (self._state != "closed"
                and packet.body == ""
                and packet.type == RCONPacket.SERVERDATA_RESPONSE_VALUE):
            logger.info("empty packet received")
            self._handle_empty_response_value(packet)
            return

        if self._state == "unauthenticated":
            # First packet needs to be a authentication packet
            if packet.type == RCONPacket.SERVERDATA_AUTH:
                if self._rcon_server.check_password(packet.body):
                    self._handle_correct_login(packet)
                else:
                    logger.info("incorrect login received")
                    self._handle_incorrect_login(packet)
            else:
                #invalid packet, close connection?
                self.close_connection()

        elif self._state == "authenticated":
            # only valid packet shoud be an SERVERDATA_EXECCOMMAND
            if packet.type == RCONPacket.SERVERDATA_EXECCOMMAND:
                self._rcon_server.handle_execcommand(packet, self)
            else:
                #invalid packet, close connection?
                self.close_connection()

        elif self._state == "closed":
            # no packets are valid here, close the connection
            self.close_connection()

        # do something when a fallthrough happens

    def _handle_empty_response_value(self, packet):
        """
        This method handles empty SERVERDATA_RESPONSE_VALUE packets.
        According to [https://developer.valvesoftware.com/wiki/Source_RCON_Protocol#Multiple-packet_Responses]
        first an empty SERVERDATA_RESPONSE_VALUE packet is send, followed by
        an other SERVERDATA_RESPONSE_VALUE packet with "0x0000 0001 0000 0000"
        as the body.

        :param packet: a RCONPacket with type == SERVERDATA_RESPONSE_VALUE and
        body == ""
        """
        assert packet.type == RCONPacket.SERVERDATA_RESPONSE_VALUE
        assert packet.body == ""

        first_packet = RCONPacket(packet.id,
                                  RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                  body="")
        second_packet = RCONPacket(packet.id,
                                   RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                   body="\x00\x00\x00\x01\x00\x00\x00\x00")
        self.send_packet(first_packet)
        self.send_packet(second_packet)

    def _handle_correct_login(self, packet):
        """
        Called when a correct login happens.
        Sends an empty SERVERDATA_RESPONSE_VALUE and an empty
        SERVERDATA_AUTH_RESPONSE, both with a id matching to the initial packet.
        Changes the state of the connection to authenticated.
        """

        id = packet.id
        # send empty SERVERDATA_RESPONSE_VALUE
        response_value = RCONPacket(id, RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                    "")
        # send SERVERDATA_AUTH_RESPONSE
        auth_response = RCONPacket(id, RCONPacket.SERVERDATA_AUTH_RESPONSE,
                                   "")
        self.send_packet(response_value)
        self.send_packet(auth_response)
        self._state = "authenticated"
        logger.info("connection authenticated")

    def _handle_incorrect_login(self, packet):
        """
        Called when a incorrect login happens.
        Sends an empty SERVERDATA_RESPONSE_VALUE packet with a matching id and
        a SERVERDATA_AUTH_RESPONSE with -1 as id.
        """

        id = packet.id
        # send empty SERVERDATA_RESPONSE_VALUE
        response_value = RCONPacket(id, RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                    "")
        # send a SERVERDATA_AUTH_RESPONSE with id=-1
        auth_response = RCONPacket(-1, RCONPacket.SERVERDATA_AUTH_RESPONSE,
                                   "")
        self.send_packet(response_value)
        self.send_packet(auth_response)
        logger.warning("incorrect authentication")

    @property
    def state(self):
        """
        :return: the state of the connection.
        It is either "unauthenticated", "authenticated" or "closed"
        """
        return self._state

    def send_packet(self, packet):
        """
        Sends the given packet.
        :param packet: a RCONPacket.
        """
        logger.info(f"sending packet {packet!r}")
        self._transport.write(packet.msg())
