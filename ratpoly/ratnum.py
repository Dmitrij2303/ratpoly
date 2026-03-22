from __future__ import annotations

from fractions import Fraction
from math import gcd as math_gcd


class RatNum:
    """Immutable rational number with NaN support."""

    __slots__ = ("_value",)

    def __init__(self, numerator: int | Fraction | "RatNum" = 0, denominator: int = 1) -> None:
        """Creates a rational number `numerator / denominator`.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `numerator` must be an integer, `Fraction`, or `RatNum`.
        @modifies `self`.
        @effects Creates a new immutable `RatNum`; if `denominator == 0`, creates `NaN`.
        @throws `TypeError` if the arguments cannot be converted to a rational number.
        @returns Nothing.
        """

        if isinstance(numerator, RatNum) and denominator == 1:
            value = numerator._value
        elif isinstance(numerator, Fraction) and denominator == 1:
            value = numerator
        elif denominator == 0:
            value = None
        else:
            value = Fraction(numerator, denominator)
        object.__setattr__(self, "_value", value)

    @classmethod
    def nan(cls) -> "RatNum":
        """Creates the special `NaN` value.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Creates a new `RatNum` object representing `NaN`.
        @throws Nothing.
        @returns A `RatNum` object with value `NaN`.
        """

        result = cls.__new__(cls)
        object.__setattr__(result, "_value", None)
        return result

    @classmethod
    def _from_fraction(cls, value: Fraction | None) -> "RatNum":
        if value is None:
            return cls.nan()
        result = cls.__new__(cls)
        object.__setattr__(result, "_value", value)
        return result

    @staticmethod
    def _coerce(value: int | Fraction | "RatNum") -> "RatNum":
        if isinstance(value, RatNum):
            return value
        return RatNum(value)

    def is_nan(self) -> bool:
        """Checks whether the number is `NaN`.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns the flag of the special `NaN` value.
        @throws Nothing.
        @returns `True` if the object is `NaN`, otherwise `False`.
        """

        return self._value is None

    def is_negative(self) -> bool:
        """Checks whether the number is negative.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Compares the number with zero.
        @throws Nothing.
        @returns `True` if the number is less than zero and is not `NaN`, otherwise `False`.
        """

        return self._value is not None and self._value < 0

    def is_positive(self) -> bool:
        """Checks whether the number is positive.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Compares the number with zero.
        @throws Nothing.
        @returns `True` if the number is greater than zero and is not `NaN`, otherwise `False`.
        """

        return self._value is not None and self._value > 0

    def compare_to(self, other: int | Fraction | "RatNum") -> int:
        """Compares two rational numbers.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `other` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Compares values using the rule: `NaN == NaN` and `NaN >` any regular number.
        @throws `TypeError` if `other` cannot be converted to `RatNum`.
        @returns `-1`, `0`, or `1`.
        """

        other_num = self._coerce(other)
        if self.is_nan() and other_num.is_nan():
            return 0
        if self.is_nan():
            return 1
        if other_num.is_nan():
            return -1
        return (self._value > other_num._value) - (self._value < other_num._value)

    def float_value(self) -> float:
        """Converts the rational number to `float`.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns the floating-point representation of the number.
        @throws Nothing.
        @returns `float("nan")` for `NaN`, otherwise a regular `float` value.
        """

        return float("nan") if self.is_nan() else float(self._value)

    def int_value(self) -> int:
        """Converts the rational number to `int` by truncating toward zero.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires The number must not be `NaN`.
        @modifies Nothing.
        @effects Converts the number to Python's integer type.
        @throws `ValueError` if the value is `NaN`.
        @returns An integer value.
        """

        if self.is_nan():
            raise ValueError("NaN cannot be converted to int")
        return int(self._value)

    def gcd(self) -> int:
        """Returns the GCD of the numerator and denominator.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Computes the GCD using the internal representation of the number.
        @throws Nothing.
        @returns `0` for `NaN`, otherwise the GCD of the numerator and denominator.
        """

        if self.is_nan():
            return 0
        return math_gcd(abs(self._value.numerator), abs(self._value.denominator))

    def __neg__(self) -> "RatNum":
        """Returns the additive inverse of the number.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Creates a new number equal to `-self`.
        @throws Nothing.
        @returns `NaN` for `NaN`, otherwise a number with the opposite sign.
        """

        return RatNum.nan() if self.is_nan() else RatNum._from_fraction(-self._value)

    def __add__(self, other: int | Fraction | "RatNum") -> "RatNum":
        """Adds two rational numbers.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `other` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns the sum `self + other`.
        @throws `TypeError` if `other` cannot be converted to `RatNum`.
        @returns A new `RatNum` object.
        """

        other_num = self._coerce(other)
        if self.is_nan() or other_num.is_nan():
            return RatNum.nan()
        return RatNum._from_fraction(self._value + other_num._value)

    def __sub__(self, other: int | Fraction | "RatNum") -> "RatNum":
        """Subtracts one rational number from another.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `other` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns the difference `self - other`.
        @throws `TypeError` if `other` cannot be converted to `RatNum`.
        @returns A new `RatNum` object.
        """

        other_num = self._coerce(other)
        return self + (-other_num)

    def __mul__(self, other: int | Fraction | "RatNum") -> "RatNum":
        """Multiplies two rational numbers.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `other` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns the product `self * other`.
        @throws `TypeError` if `other` cannot be converted to `RatNum`.
        @returns A new `RatNum` object.
        """

        other_num = self._coerce(other)
        if self.is_nan() or other_num.is_nan():
            return RatNum.nan()
        return RatNum._from_fraction(self._value * other_num._value)

    def __truediv__(self, other: int | Fraction | "RatNum") -> "RatNum":
        """Divides one rational number by another.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires `other` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns the quotient `self / other`.
        @throws `TypeError` if `other` cannot be converted to `RatNum`.
        @returns `NaN` if any operand is `NaN` or the divisor is zero, otherwise a new `RatNum` object.
        """

        other_num = self._coerce(other)
        if self.is_nan() or other_num.is_nan() or other_num._value == 0:
            return RatNum.nan()
        return RatNum._from_fraction(self._value / other_num._value)

    def __str__(self) -> str:
        """Converts the number to a string.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Builds the canonical string representation of the number.
        @throws Nothing.
        @returns A string of the form `a/b`, `a`, or `NaN`.
        """

        if self.is_nan():
            return "NaN"
        if self._value.denominator == 1:
            return str(self._value.numerator)
        return f"{self._value.numerator}/{self._value.denominator}"

    def __hash__(self) -> int:
        """Computes the hash of the object.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns a stable hash based on the value of the object.
        @throws Nothing.
        @returns An integer hash.
        """

        return hash(("RatNum", "NaN")) if self.is_nan() else hash(("RatNum", self._value))

    def __eq__(self, other: object) -> bool:
        """Checks whether two `RatNum` objects are equal.

        Representation Fields:
        - `_value`: `Fraction` for a regular number or `None` for `NaN`.
        Representation Invariant:
        - `_value is None` or `_value` is stored as a reduced fraction.
        Abstraction Function:
        - `None -> NaN`, `Fraction(n, d) -> n / d`.

        @requires Nothing.
        @modifies Nothing.
        @effects Compares two objects by their mathematical value.
        @throws Nothing.
        @returns `True` if the values are equal, otherwise `False`.
        """

        if not isinstance(other, RatNum):
            return False
        if self.is_nan() or other.is_nan():
            return self.is_nan() and other.is_nan()
        return self._value == other._value
