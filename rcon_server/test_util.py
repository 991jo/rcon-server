import unittest

from util import to_int32

class TestToInt32(unittest.TestCase):

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertEqual(to_int32(1), b"\x00\x00\x00\x01")
        self.assertEqual(to_int32(10), b"\x00\x00\x00\x0A")
        self.assertEqual(to_int32(42), b"\x00\x00\x00\x2A")
        self.assertEqual(to_int32(512), b"\x00\x00\x02\x00")
        self.assertEqual(to_int32(2**25), b"\x02\x00\x00\x00")

    def test_negative(self):
        """
        Tests various negative numbers
        """
        self.assertEqual(to_int32(-1), b"\xFF\xFF\xFF\xFF")
        self.assertEqual(to_int32(-10), b"\xFF\xFF\xFF\xF6")
        self.assertEqual(to_int32(-42), b"\xFF\xFF\xFF\xD6")
        self.assertEqual(to_int32(-512), b"\xFF\xFF\xFE\x00")
        self.assertEqual(to_int32(-2**25), b"\xFE\x00\x00\x00")

    def test_overflow(self):
        """
        Tests an overflow error.
        """
        with self.assertRaises(OverflowError):
            to_int32(2**33)

    def test_underflow(self):
        """
        Tests an underflow error.
        """
        with self.assertRaises(OverflowError):
            to_int32(-2**33)
