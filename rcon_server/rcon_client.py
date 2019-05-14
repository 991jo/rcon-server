import socket

from .rcon_packet import RCONPacket

class PasswordError(Exception):
    """Exception which is thrown when the password is incorrect."""
    pass

class ConnectionClosedError(Exception):
    """Exception which is thrown when the connection is closed"""
    pass

class PacketIDMissmatch(Exception):
    """Exception thrown when the ID of the received packet does not match."""
    pass

class PacketTypeMissmatch(Exception):
    """
    Exception thrown when the type of the received packet does not match
    to what was expected.
    """
    pass

class RCONClient():

    def __init__(self, ip, port, password):
        """
        Initializes the RCONClient with the given *ip*, *port*, and *password*.
        The connect and login methods need to be called before commands can be
        send.
        :param ip: str, an ip or domain name to connect to
        :param port: int, a tcp port to connect to
        :param password: str, the rcon password to use
        """
        self.next_id = 1
        self._ip = ip
        self._port = port
        self._password = password
        self._buffer = b""  # empty buffer for socket connection

    def send_packet(self, packet):
        """Sends the given packet to the server.
        Raises an error when the connection is not working.
        This method does not increase the next_id counter!"""
        self._socket.sendall(packet.msg())

    def recv_packet(self):
        """Receives one packet from the connection."""
        while True: # receive data until enougth data is available for a whole
                    # packet
            data = self._socket.recv(4096)
            # check for closed socket
            if len(data) == 0:
                raise ConnectionClosedError
            self._buffer += data

            # try to build a packet
            packet, buffer = RCONPacket.from_buffer(self._buffer)
            if packet is not None:
                self._buffer = buffer
                return packet

    def login(self):
        """
        Sends the rcon password.
        This raises a PasswordError when the password is wrong.
        """
        auth_id = self.next_id
        login_packet = RCONPacket(auth_id,
                                  RCONPacket.SERVERDATA_AUTH,
                                  self._password)
        self.next_id += 1
        self.send_packet(login_packet)
        first_response= self.recv_packet()
        second_response= self.recv_packet()
        if first_response.type != RCONPacket.SERVERDATA_RESPONSE_VALUE:
            raise PacketTypeMissmatch("Expected SERVERDATA_RESPONSE_VALUE, "
                                    "received %d" % first_response.type)

        if second_response.type != RCONPacket.SERVERDATA_AUTH_RESPONSE:
            raise PacketTypeMissmatch("Expected SERVERDATA_AUTH_RESPONSE, "
                                    "received %d" % second_response.type)

        if first_response.id != auth_id:
            raise PacketIDMissmatch(
                    f"Packet ID should be {auth_id} but is {second_answer.id}.")

        if second_response.id == -1:
            raise PasswordError("invalid password")

        # everything should be okay now.
        # login should be successful
        # one could check the content of the body but this should not
        # be necessary

    def connect(self):
        """
        Connects to the server.
        This may raise an Error if the connections fails.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._ip, self._port))

    def disconnect(self):
        """
        Disconnects from the server.
        This may raise an Error if closing the connection fails.
        """
        self._socket.close()

    def send_command(self, command):
        """
        Sends the given command to the server and returns the output as a
        string.

        :param command: str, the command to send.
        """
        command_id = self.next_id
        self.next_id += 1
        check_id = self.next_id
        self.next_id += 1

        command_packet = RCONPacket(command_id, RCONPacket.SERVERDATA_EXECCOMMAND,
                                    command)
        check_packet = RCONPacket(check_id, RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                  "")
        self.send_packet(command_packet)
        self.send_packet(check_packet)

        response = ""

        # receive packages until a packet with the check_id is received.
        # the package after that with the content 0x0000 0001 0000 0000
        # is dropped
        while True:
            packet = self.recv_packet()
            if packet.type != RCONPacket.SERVERDATA_RESPONSE_VALUE:
                # wrong packet type received. TODO
                pass
            if packet.id == command_id:
                response += packet.body
            elif packet.id == check_id and packet.body == "":
                # final packet received
                # receive the 0x0000 0001 0000 0000 packet
                _ = self.recv_packet()
                break

        return response
