import unittest

from .rcon_server import RCONServer
from .rcon_connection import RCONConnection
from .rcon_packet import RCONPacket

test_password = "test"


class DummyTransport():

    def __init__(self, protocol):
        """
        Initializes a new DummyTransport.

        The Transport calls the required methods of the protocol when
        opening/sending/closing the connection.
        :param protocol: The asyncio.Protocol by which the transport is used
        """
        self.protocol = protocol
        self.protocol.connection_made(self)
        self.buffer = b""  # a buffer for the data received from the test end
        self.closed = False

    def write(self, data):
        """
        Write data from the tested code to the fixture.
        This method should only be used by the tested code.

        :param data: byte-string
        """
        assert not self.closed
        self.buffer += data

    def read(self):
        """
        Read data send by the tested code.

        :return: byte-string
        """
        data = self.buffer
        self.buffer = b""
        return data

    def write_to_test(self, data):
        """
        Write data from the fixture to the tested code.

        :param data: byte-string
        """
        assert not self.closed
        self.protocol.data_received(data)

    def close(self):
        """
        Close the connection from the side of the tested code.
        """
        self.closed = True


class DummyRCONServer(RCONServer):

    def __init__(self):
        super().__init__(self, password=test_password)

    def handle_execcommand(self, packet, connection):
        response = RCONPacket(packet.id,
                              RCONPacket.SERVERDATA_RESPONSE_VALUE,
                              packet.body)
        connection.send_packet(response)


# Testcases

class RCONConnectionTest(unittest.TestCase):

    def setUp(self):
        """
        Creates a DummyRCONServer, a RCONConnection and a DummyTransport
        and connects them.
        """
        self.rcon_server = DummyRCONServer()
        self.connection = RCONConnection(self.rcon_server)
        self.transport = DummyTransport(self.connection)

        self.login_packet = RCONPacket(id=1000,
                                       type=RCONPacket.SERVERDATA_AUTH,
                                       body=test_password)

    def test_send_packet(self):
        """Tests if the Connection transmits RCONPackets correctly."""
        packet_in = RCONPacket(id=1,
                               type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                               body="test")
        self.connection.send_packet(packet_in)
        buffer = self.transport.read()
        packet_out, remaining_buffer = RCONPacket.from_buffer(buffer)

        self.assertEqual(remaining_buffer, b"")
        self.assertEqual(packet_in.type, packet_out.type)
        self.assertEqual(packet_in.id, packet_out.id)
        self.assertEqual(packet_in.body, packet_out.body)

    def test_password_successfull(self):

        # send login packet
        self.transport.write_to_test(self.login_packet.msg())

        # receive data from the tested code
        buffer = self.transport.read()

        first_packet, buffer = RCONPacket.from_buffer(buffer)
        second_packet, buffer = RCONPacket.from_buffer(buffer)

        self.assertEqual(buffer, b"")

        self.assertEqual(first_packet.id, self.login_packet.id)
        self.assertEqual(first_packet.type, RCONPacket.SERVERDATA_RESPONSE_VALUE)
        self.assertEqual(first_packet.body, "")

        self.assertEqual(second_packet.id, self.login_packet.id)
        self.assertEqual(second_packet.type, RCONPacket.SERVERDATA_AUTH_RESPONSE)
        self.assertEqual(second_packet.body, "")

    def test_password_fail(self):
        # build invalid login packet

        invalid_login_packet = RCONPacket(1, RCONPacket.SERVERDATA_AUTH, test_password + "2")

        # send login packet
        self.transport.write_to_test(invalid_login_packet.msg())

        # receive data from the tested code
        buffer = self.transport.read()

        first_packet, buffer = RCONPacket.from_buffer(buffer)
        second_packet, buffer = RCONPacket.from_buffer(buffer)

        self.assertEqual(buffer, b"")

        self.assertEqual(first_packet.id, invalid_login_packet.id)
        self.assertEqual(first_packet.type, RCONPacket.SERVERDATA_RESPONSE_VALUE)
        self.assertEqual(first_packet.body, "")

        self.assertEqual(second_packet.id, -1)
        self.assertEqual(second_packet.type, RCONPacket.SERVERDATA_AUTH_RESPONSE)
        self.assertEqual(second_packet.body, "")

    def test_regular_command(self):
        # login
        self.test_password_successfull()

        command_packet = RCONPacket(id=2,
                                    type=RCONPacket.SERVERDATA_EXECCOMMAND,
                                    body="commandtest")

        self.transport.write_to_test(command_packet.msg())

        buffer = self.transport.read()
        response, buffer = RCONPacket.from_buffer(buffer)

        self.assertEqual(buffer, b"")

        self.assertEqual(response.id, command_packet.id)
        self.assertEqual(response.type, RCONPacket.SERVERDATA_RESPONSE_VALUE)
        self.assertEqual(response.body, "commandtest")

    def test_multipacket(self):
        # TODO Feature is missing in the RCONPacket an need to be implemented there first
        pass

    def test_mirrored_packet(self):
        """For details regarding mirrored packets see [https://developer.valvesoftware.com/wiki/Source_RCON_Protocol#Multiple-packet_Responses]"""
        self.test_password_successfull()
        packet = RCONPacket(10, RCONPacket.SERVERDATA_RESPONSE_VALUE, "")

        self.transport.write_to_test(packet.msg())
        buffer = self.transport.read()

        first_packet, buffer = RCONPacket.from_buffer(buffer)
        second_packet, buffer = RCONPacket.from_buffer(buffer)

        self.assertEqual(buffer, b"")

        self.assertEqual(first_packet.id, 10)
        self.assertEqual(first_packet.type, RCONPacket.SERVERDATA_RESPONSE_VALUE)
        self.assertEqual(first_packet.body, "")

        self.assertEqual(second_packet.id, 10)
        self.assertEqual(second_packet.type, RCONPacket.SERVERDATA_RESPONSE_VALUE)
        self.assertEqual(second_packet.body, "\x00\x00\x00\x01\x00\x00\x00\x00")

    def test_close_connection(self):
        """
        Check if a connection is closed correctly.
        This also checks the state of the connection.
        """
        self.assertEqual(self.connection.state, "unauthenticated")

        # login to the server
        self.test_password_successfull()

        self.assertEqual(self.connection.state, "authenticated")
        self.assertFalse(self.transport.closed)

        self.connection.close_connection()

        self.assertEqual(self.connection.state, "closed")
        self.assertTrue(self.transport.closed)
