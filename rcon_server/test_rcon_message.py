from rcon_packet import RCONPacket
from rcon_message import RCONMessage

import unittest

class RCONMessageTest(unittest.TestCase):

    def setUp(self):
        self.packet1 = RCONPacket(id=1,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test1")
        self.packet2 = RCONPacket(id=2,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test2")
        self.packet3 = RCONPacket(id=3,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test3")

    def test_init_empty(self):
        """Tests the empty constructor."""
        message = RCONMessage()
        self.assertEqual(message.packets, list())

    def test_init_single_packet(self):
        """Tests with a single packet."""
        message = RCONMessage(self.packet1)
        self.assertEqual(message.packets == list())
        self.assertEqual(len(message.packets, 1))
        self.assertEqual(message.packets[0], 1)

    def test_init_single_packet(self):
        """Tests with multiple packets."""
        message = RCONMessage([self.packet1, self.packet2])
        self.assertTrue(isinstance(message.packets, list))
        self.assertEqual(len(message.packets), 2)
        self.assertEqual(message.packets[0], self.packet1)
        self.assertEqual(message.packets[1], self.packet2)

    def test_add_packet(self):
        """Tests adding a packet."""
        message = RCONMessage(self.packet1)
        message.add_packet(self.packet2)
        self.assertEqual(message.packets[0], self.packet1)
        self.assertEqual(message.packets[1], self.packet2)

    def test_iter_empty(self):
        """Tests the empty iterator."""
        message = RCONMessage()
        i = 0
        for _ in message:
            i += 1
        self.assertEqual(i,0)

    def test_iter(self):
        """Test the iterator with some elements."""
        message = RCONMessage([self.packet1, self.packet2])
        i = 0
        for _ in message:
            i += 1
        self.assertEqual(i,2)

    def test_msg_empty(self):
        """Tests the msg function without packets."""
        message = RCONMessage()
        self.assertEqual(message.msg(), b"")

    def test_msg_one_packet(self):
        """Tests the msg function with exactly one packet."""
        message = RCONMessage(self.packet1)
        self.assertEqual(message.msg(), self.packet1.msg())

    def test_msg_multiple_packets(self):
        """Tests the msg function with multiple packets."""
        message = RCONMessage([self.packet1, self.packet2])
        self.assertEqual(message.msg(), self.packet1.msg() + self.packet2.msg())

    def test_body_empty(self):
        """Tests the body with an empty message."""
        message = RCONMessage()
        self.assertEqual("", message.body)

    def test_body_empty(self):
        """Tests the body with an one packet."""
        message = RCONMessage(self.packet1)
        self.assertEqual("test1", message.body)

    def test_body_empty(self):
        """Tests the body with multiple packets."""
        message = RCONMessage([self.packet1, self.packet2])
        self.assertEqual("test1test2", message.body)
