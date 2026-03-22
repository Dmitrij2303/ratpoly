import math
import unittest

from ratpoly import RatNum


class RatNumTest(unittest.TestCase):
    def test_str_and_normalization(self) -> None:
        self.assertEqual(str(RatNum(2, 4)), "1/2")
        self.assertEqual(str(RatNum(-8, 2)), "-4")
        self.assertEqual(str(RatNum(0, 5)), "0")

    def test_nan_behavior(self) -> None:
        nan = RatNum(1, 0)
        self.assertTrue(nan.is_nan())
        self.assertTrue((nan + RatNum(1)).is_nan())
        self.assertTrue((nan * RatNum(5)).is_nan())
        self.assertEqual(nan.compare_to(RatNum(100)), 1)
        self.assertEqual(nan.compare_to(RatNum.nan()), 0)
        self.assertEqual(nan, RatNum.nan())

    def test_arithmetic(self) -> None:
        left = RatNum(1, 2)
        right = RatNum(1, 3)
        self.assertEqual(left + right, RatNum(5, 6))
        self.assertEqual(left - right, RatNum(1, 6))
        self.assertEqual(left * right, RatNum(1, 6))
        self.assertEqual(left / right, RatNum(3, 2))
        self.assertTrue((left / RatNum(0)).is_nan())

    def test_sign_compare_and_negation(self) -> None:
        value = RatNum(-3, 5)
        self.assertTrue(value.is_negative())
        self.assertFalse(value.is_positive())
        self.assertEqual((-value), RatNum(3, 5))
        self.assertEqual(RatNum(5).compare_to(RatNum(4)), 1)
        self.assertEqual(RatNum(4).compare_to(RatNum(5)), -1)

    def test_conversions_and_gcd(self) -> None:
        value = RatNum(7, 2)
        self.assertAlmostEqual(value.float_value(), 3.5)
        self.assertEqual(value.int_value(), 3)
        self.assertEqual(value.gcd(), 1)
        self.assertTrue(math.isnan(RatNum.nan().float_value()))
        with self.assertRaises(ValueError):
            RatNum.nan().int_value()

    def test_hash_and_eq(self) -> None:
        self.assertEqual(hash(RatNum(2, 4)), hash(RatNum(1, 2)))
        self.assertEqual(RatNum(2, 4), RatNum(1, 2))
        self.assertNotEqual(RatNum(1, 2), RatNum(2, 3))


if __name__ == "__main__":
    unittest.main()
