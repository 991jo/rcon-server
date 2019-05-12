from rcon_packet import RCONPacket
from rcon_message import RCONMessage

import unittest

class RCONMessageTest(unittest.TestCase):

    def setUp(self):
        self.packet1 = RCONPacket(id=1,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test1")
        self.packet2 = RCONPacket(id=1,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test2")
        self.packet3 = RCONPacket(id=1,
                                      type=RCONPacket.SERVERDATA_RESPONSE_VALUE,
                                      body="test3")
        self.empty_message = RCONMessage(id=0,
                                         type=RCONPacket.SERVERDATA_AUTH,
                                         body="")
        self.empty_packet = RCONPacket(id=0,
                                       type=RCONPacket.SERVERDATA_AUTH,
                                       body="")
        self.very_long_body = "a"*5000

    def test_init_empty(self):
        """Tests the empty constructor. an completely empty constructor is invalid."""
        with self.assertRaises(AssertionError):
            message = RCONMessage()

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
        i = 0
        for p in self.empty_message:
            i += 1
            self.assertEqual(p.body, "")
        self.assertEqual(i,1)

    def test_iter(self):
        """Test the iterator with some elements."""
        message = RCONMessage([self.packet1, self.packet2])
        i = 0
        for _ in message:
            i += 1
        self.assertEqual(i,2)

    def test_msg_empty(self):
        """Tests the msg function an empty packet."""
        self.assertEqual(self.empty_message.msg(), self.empty_packet.msg())

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
        self.assertEqual("", self.empty_message.body)

    def test_body_one_packet(self):
        """Tests the body with an one packet."""
        message = RCONMessage(self.packet1)
        self.assertEqual("test1", message.body)

    def test_body_multiple_packets(self):
        """Tests the body with multiple packets."""
        message = RCONMessage([self.packet1, self.packet2])
        self.assertEqual("test1test2", message.body)

    def test_body_setter_single_packet(self):
        """Test the body setter with a data for a single packet"""
        message = RCONMessage(id=0, type=RCONPacket.SERVERDATA_AUTH, body="test")
        self.assertEqual("test", message.body)
        self.assertEqual(len(message.packets), 1)

    def test_body_setter_multiple_packets(self):
        """Test the body setter with a data for multiple packets"""
        message = RCONMessage(id=0,
                              type=RCONPacket.SERVERDATA_AUTH,
                              body=self.very_long_body)
        self.assertEqual(self.very_long_body, message.body)
        self.assertEqual(len(message.packets), 2)

    def test_id_getter(self):
        """Tests the getter for the id."""
        self.assertEqual(self.empty_message.id, self.empty_packet.id)

    def test_id_setter_single_packet(self):
        """Tests the setter for the id with a single packet."""
        message = RCONMessage(id=0, type=RCONPacket.SERVERDATA_AUTH, body="test")
        self.assertEqual(message.id, 0)
        message.id = 1
        self.assertEqual(message.id, 1)

    def test_id_setter_multiple_packets(self):
        """Tests the setter for the id with multiple packets."""
        message = RCONMessage(id=0,
                              type=RCONPacket.SERVERDATA_AUTH,
                              body=self.very_long_body)
        self.assertEqual(message.id, 0)
        for packet in message.packets:
            self.assertEqual(packet.id, 0)

        message.id = 1
        self.assertEqual(message.id, 1)
        for packet in message.packets:
            self.assertEqual(packet.id, 1)

    def test_type_getter(self):
        """Test the type getter"""
        self.assertEqual(self.empty_message.type, RCONPacket.SERVERDATA_AUTH)

    def test_type_setter_single_packet(self):
        """Test the type setter with data for a single packet"""
        message = RCONMessage(id=0, type=RCONPacket.SERVERDATA_AUTH, body="test")
        self.assertEqual(message.type, RCONPacket.SERVERDATA_AUTH)
        message.type = RCONPacket.SERVERDATA_AUTH_RESPONSE
        self.assertEqual(message.type, RCONPacket.SERVERDATA_AUTH_RESPONSE)

    def test_type_setter_multiple_packets(self):
        """Test the type setter with data for a multiple packets"""
        message = RCONMessage(id=0,
                              type=RCONPacket.SERVERDATA_AUTH,
                              body=self.very_long_body)
        self.assertEqual(message.type, RCONPacket.SERVERDATA_AUTH)
        for packet in message.packets:
            self.assertEqual(packet.type, RCONPacket.SERVERDATA_AUTH)
        message.type = RCONPacket.SERVERDATA_AUTH_RESPONSE
        self.assertEqual(message.type, RCONPacket.SERVERDATA_AUTH_RESPONSE)
        for packet in message.packets:
            self.assertEqual(packet.type, RCONPacket.SERVERDATA_AUTH_RESPONSE)

    def test_size_getter_single_packet(self):
        pass

    def test_size_getter_multiple_packet(self):
        pass
