import unittest

from rcon_packet import RCONPacket
from util import to_int32

class TestRconPacket(unittest.TestCase):

    def test_size(self):
        """
        Tests the size function
        """
        packet = RCONPacket()
        self.assertEqual(10, packet.size)
        packet.body = "asdf"
        self.assertEqual(14, packet.size)

    def test_msg(self):
        """
        Tests if the msg function returns the correct packet.
        """
        packet = RCONPacket()
        self.assertEqual(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                         packet.msg()[4:])

        packet.body = "AAAA"
        self.assertEqual(b"AAAA", packet.msg()[12:-2])
        self.assertEqual(b"\x0E\x00\x00\x00", packet.msg()[:4])
        self.assertEqual(packet.terminator, packet.msg()[-1:])
        self.assertEqual(packet.terminator, packet.msg()[-2:-1])

        packet.id = 64
        self.assertEqual(b"\x40\x00\x00\x00", packet.msg()[4:8])

        packet.type = 2
        self.assertEqual(b"\x02\x00\x00\x00", packet.msg()[8:12])

    def test_wrong_packet_type(self):
        """
        Tests if the correct exception is thrown when the value is a invalid
        value is given to the type attribute.
        """
        packet = RCONPacket()
        with self.assertRaises(ValueError):
            packet.type = -1
        with self.assertRaises(ValueError):
            packet.type = 1
        with self.assertRaises(ValueError):
            packet.type = 4
        with self.assertRaises(ValueError):
            packet.type = "test"

    def test_to_large_id(self):
        packet = RCONPacket()
        with self.assertRaises(ValueError):
            packet.id = 2**35
        with self.assertRaises(ValueError):
            packet.id = -2**35

    def test_from_buffer_empty_buffer(self):
        buffer = b""
        packet, remaining_buffer = RCONPacket.from_buffer(buffer)
        self.assertTrue(packet is None)
        self.assertEqual(remaining_buffer, buffer)

    def test_from_buffer_to_small_buffer(self):
        buffer = b"abcd"
        packet, remaining_buffer = RCONPacket.from_buffer(buffer)
        self.assertTrue(packet is None)
        self.assertEqual(remaining_buffer, buffer)

    def test_from_buffer_incomplete_body(self):
        size = to_int32(4+4+10+1+1) # 10 bytes body
        type = to_int32(0)
        id = to_int32(0)
        buffer = size + type + id + b"test"
        packet, remaining_buffer = RCONPacket.from_buffer(buffer)
        self.assertTrue(packet is None)
        self.assertEqual(remaining_buffer, buffer)

    def test_from_buffer_exactly_matching(self):
        size = to_int32(4+4+10+1+1) # 10 bytes body
        type = to_int32(0)
        id = to_int32(0)
        buffer = size + type + id + b"testtestte\x00\x00"
        packet, remaining_buffer = RCONPacket.from_buffer(buffer)
        self.assertFalse(packet is None)
        self.assertEqual(remaining_buffer, b"")
        self.assertEqual(packet.id, 0)
        self.assertEqual(packet.type, 0)
        self.assertEqual(packet.body, "testtestte")
        self.assertEqual(packet.size, 20)

    def test_from_buffer_larger(self):
        size = to_int32(4+4+10+1+1) # 10 bytes body
        type = to_int32(0)
        id = to_int32(0)
        buffer = size + type + id + b"testtestte\x00\x00asdf"
        packet, remaining_buffer = RCONPacket.from_buffer(buffer)
        self.assertFalse(packet is None)
        self.assertEqual(remaining_buffer, b"asdf")
        self.assertEqual(packet.id, 0)
        self.assertEqual(packet.type, 0)
        self.assertEqual(packet.body, "testtestte")
        self.assertEqual(packet.size, 20)
