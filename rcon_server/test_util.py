import unittest

from util import to_int32, from_int32, check_int32

class TestToInt32(unittest.TestCase):

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertEqual(to_int32(1), b"\x01\x00\x00\x00")
        self.assertEqual(to_int32(10), b"\x0A\x00\x00\x00")
        self.assertEqual(to_int32(42), b"\x2A\x00\x00\x00")
        self.assertEqual(to_int32(512), b"\x00\x02\x00\x00")
        self.assertEqual(to_int32(2**25), b"\x00\x00\x00\x02")

    def test_negative(self):
        """
        Tests various negative numbers
        """
        self.assertEqual(to_int32(-1), b"\xFF\xFF\xFF\xFF")
        self.assertEqual(to_int32(-10), b"\xF6\xFF\xFF\xFF")
        self.assertEqual(to_int32(-42), b"\xD6\xFF\xFF\xFF")
        self.assertEqual(to_int32(-512), b"\x00\xFE\xFF\xFF")
        self.assertEqual(to_int32(-2**25), b"\x00\x00\x00\xFE")

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

class TestFromInt32(unittest.TestCase):

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertEqual(from_int32(b"\x01\x00\x00\x00"), 1)
        self.assertEqual(from_int32(b"\x0A\x00\x00\x00"), 10)
        self.assertEqual(from_int32(b"\x2A\x00\x00\x00"), 42)
        self.assertEqual(from_int32(b"\x00\x02\x00\x00"), 512)
        self.assertEqual(from_int32(b"\x00\x00\x00\x02"), 2**25)

    def test_negative(self):
        """
        Tests various negative numbers
        """
        self.assertEqual(from_int32(b"\xFF\xFF\xFF\xFF"), -1)
        self.assertEqual(from_int32(b"\xF6\xFF\xFF\xFF"), -10)
        self.assertEqual(from_int32(b"\xD6\xFF\xFF\xFF"), -42)
        self.assertEqual(from_int32(b"\x00\xFe\xFF\xFF"), -512)
        self.assertEqual(from_int32(b"\x00\x00\x00\xFE"), -2**25)

    def test_zero(self):
        """
        Tests the 0
        """
        self.assertEqual(from_int32(b"\x00\x00\x00\x00"), 0)

class TestCheckInt32(unittest.TestCase):

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertTrue(check_int32(1))
        self.assertTrue(check_int32(10))
        self.assertTrue(check_int32(42))
        self.assertTrue(check_int32(512))
        self.assertTrue(check_int32(2**25))
        self.assertFalse(check_int32(2**32))
        self.assertFalse(check_int32(2**35))

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertTrue(check_int32(-1))
        self.assertTrue(check_int32(-10))
        self.assertTrue(check_int32(-42))
        self.assertTrue(check_int32(-512))
        self.assertTrue(check_int32(-2**25))
        self.assertFalse(check_int32(-2**32))
        self.assertFalse(check_int32(-2**35))

    def test_zero(self):
        """
        Tests the 0
        """
        self.assertTrue(check_int32(0))
