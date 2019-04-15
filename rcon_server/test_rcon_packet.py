import unittest

from rcon_packet import RCONPacket

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
        self.assertEqual(b"\x00\x00\x00\x0E", packet.msg()[:4])
        self.assertEqual(packet.terminator, packet.msg()[-1:])
        self.assertEqual(packet.terminator, packet.msg()[-2:-1])

        packet.id = 64
        self.assertEqual(b"\x00\x00\x00\x40", packet.msg()[4:8])

        packet.type = 2
        self.assertEqual(b"\x00\x00\x00\x02", packet.msg()[8:12])

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
