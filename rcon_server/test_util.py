import unittest

from util import to_int32, from_int32, check_int32

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

class TestFromInt32(unittest.TestCase):

    def test_positive(self):
        """
        Tests various positive numbers
        """
        self.assertEqual(from_int32(b"\x00\x00\x00\x01"), 1)
        self.assertEqual(from_int32(b"\x00\x00\x00\x0A"), 10)
        self.assertEqual(from_int32(b"\x00\x00\x00\x2A"), 42)
        self.assertEqual(from_int32(b"\x00\x00\x02\x00"), 512)
        self.assertEqual(from_int32(b"\x02\x00\x00\x00"), 2**25)

    def test_negative(self):
        """
        Tests various negative numbers
        """
        self.assertEqual(from_int32(b"\xFF\xFF\xFF\xFF"), -1)
        self.assertEqual(from_int32(b"\xFF\xFF\xFF\xF6"), -10)
        self.assertEqual(from_int32(b"\xFF\xFF\xFF\xD6"), -42)
        self.assertEqual(from_int32(b"\xFF\xFF\xFE\x00"), -512)
        self.assertEqual(from_int32(b"\xFE\x00\x00\x00"), -2**25)

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
