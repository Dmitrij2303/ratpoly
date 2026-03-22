import unittest

from ratpoly import RatNum, RatPoly


class RatPolyTest(unittest.TestCase):
    def test_zero_degree_and_coeff(self) -> None:
        poly = RatPoly()
        self.assertEqual(poly.degree(), 0)
        self.assertEqual(poly.get_coeff(3), RatNum(0))
        self.assertEqual(str(poly), "0")

    def test_str_and_value_of_roundtrip(self) -> None:
        poly = RatPoly({2: RatNum(1), 1: RatNum(3, 2), 0: RatNum(-4)})
        text = str(poly)
        self.assertEqual(text, "x^2+3/2*x-4")
        self.assertEqual(RatPoly.value_of(text), poly)
        self.assertEqual(RatPoly.value_of("-x^2+x-1"), RatPoly({2: -1, 1: 1, 0: -1}))

    def test_add_sub_and_scale(self) -> None:
        left = RatPoly({2: 1, 0: 1})
        right = RatPoly({1: 2, 0: -1})
        self.assertEqual(left + right, RatPoly({2: 1, 1: 2}))
        self.assertEqual(left - right, RatPoly({2: 1, 1: -2, 0: 2}))
        self.assertEqual(left.scale_coeff(RatNum(1, 2)), RatPoly({2: RatNum(1, 2), 0: RatNum(1, 2)}))

    def test_mul_and_div(self) -> None:
        left = RatPoly({1: 1, 0: 1})
        right = RatPoly({1: 1, 0: -1})
        product = left * right
        self.assertEqual(product, RatPoly({2: 1, 0: -1}))
        self.assertEqual(product / left, right)
        self.assertTrue((product / RatPoly()).is_nan())

    def test_eval(self) -> None:
        poly = RatPoly({2: 1, 0: 1})
        self.assertEqual(poly.eval(RatNum(2)), RatNum(5))
        self.assertAlmostEqual(poly.eval(0.5), 1.25)

    def test_calculus(self) -> None:
        poly = RatPoly({2: 3, 1: 2, 0: 1})
        self.assertEqual(poly.differentiate(), RatPoly({1: 6, 0: 2}))
        primitive = poly.anti_differentiate(RatNum(5))
        self.assertEqual(primitive, RatPoly({3: 1, 2: 1, 1: 1, 0: 5}))
        self.assertEqual(RatPoly({1: 2}).integrate(0, 3), RatNum(9))

    def test_nan_hash_and_eq(self) -> None:
        nan_poly = RatPoly.nan()
        self.assertTrue(nan_poly.is_nan())
        self.assertEqual(nan_poly, RatPoly.value_of("NaN"))
        self.assertEqual(hash(nan_poly), hash(RatPoly.nan()))
        self.assertTrue((nan_poly + RatPoly({0: 1})).is_nan())


if __name__ == "__main__":
    unittest.main()
