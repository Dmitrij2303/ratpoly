from __future__ import annotations

import re
from fractions import Fraction

from .ratnum import RatNum


class RatPoly:
    """Immutable polynomial with rational coefficients."""

    __slots__ = ("_terms", "_nan")

    def __init__(self, terms: dict[int, int | Fraction | RatNum] | None = None) -> None:
        """Creates a polynomial from a dictionary `{degree: coefficient}`.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires All degrees must be non-negative and all coefficients must be convertible to `RatNum`.
        @modifies `self`.
        @effects Creates a new immutable polynomial and removes zero coefficients.
        @throws `ValueError` if a negative degree is found.
        @returns Nothing.
        """

        if terms is None:
            clean: dict[int, Fraction] = {}
            is_nan = False
        else:
            clean = {}
            is_nan = False
            for degree, coeff in terms.items():
                if degree < 0:
                    raise ValueError("degree must be non-negative")
                rat = self._coerce_coeff(coeff)
                if rat.is_nan():
                    is_nan = True
                    clean = {}
                    break
                if rat._value != 0:
                    clean[degree] = clean.get(degree, Fraction(0)) + rat._value
            clean = {degree: coeff for degree, coeff in clean.items() if coeff != 0}
        object.__setattr__(self, "_terms", tuple(sorted(clean.items())))
        object.__setattr__(self, "_nan", is_nan)

    @classmethod
    def nan(cls) -> "RatPoly":
        """Creates the special `NaN` polynomial.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Creates a new `RatPoly` object representing `NaN`.
        @throws Nothing.
        @returns A `NaN` polynomial.
        """

        result = cls.__new__(cls)
        object.__setattr__(result, "_terms", ())
        object.__setattr__(result, "_nan", True)
        return result

    @classmethod
    def _from_fraction_terms(cls, terms: dict[int, Fraction] | None = None, *, nan: bool = False) -> "RatPoly":
        if nan:
            return cls.nan()
        result = cls.__new__(cls)
        clean = {degree: coeff for degree, coeff in (terms or {}).items() if coeff != 0}
        object.__setattr__(result, "_terms", tuple(sorted(clean.items())))
        object.__setattr__(result, "_nan", False)
        return result

    @staticmethod
    def _coerce_coeff(value: int | Fraction | RatNum) -> RatNum:
        if isinstance(value, RatNum):
            return value
        if isinstance(value, Fraction):
            return RatNum._from_fraction(value)
        return RatNum(value)

    def _term_dict(self) -> dict[int, Fraction]:
        return dict(self._terms)

    def degree(self) -> int:
        """Returns the degree of the polynomial.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns the highest degree of a non-zero term.
        @throws Nothing.
        @returns `0` for the zero polynomial and for `NaN`; otherwise the leading degree.
        """

        return 0 if not self._terms else self._terms[-1][0]

    def get_coeff(self, degree: int) -> RatNum:
        """Returns the coefficient for the given degree.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `degree >= 0`.
        @modifies Nothing.
        @effects Looks up the coefficient of `x^degree`.
        @throws `ValueError` if `degree < 0`.
        @returns `NaN` for a `NaN` polynomial, zero if the degree is absent, otherwise the coefficient.
        """

        if degree < 0:
            raise ValueError("degree must be non-negative")
        if self.is_nan():
            return RatNum.nan()
        for current_degree, coeff in self._terms:
            if current_degree == degree:
                return RatNum._from_fraction(coeff)
        return RatNum(0)

    def is_nan(self) -> bool:
        """Checks whether the polynomial is `NaN`.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns the special-state flag.
        @throws Nothing.
        @returns `True` if the polynomial is `NaN`, otherwise `False`.
        """

        return self._nan

    def scale_coeff(self, scalar: int | Fraction | RatNum) -> "RatPoly":
        """Multiplies all polynomial coefficients by a scalar.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `scalar` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns a new polynomial with scaled coefficients.
        @throws `TypeError` if `scalar` cannot be converted to `RatNum`.
        @returns A new `RatPoly` object.
        """

        rat = self._coerce_coeff(scalar)
        if self.is_nan() or rat.is_nan():
            return RatPoly.nan()
        return RatPoly._from_fraction_terms(
            {degree: coeff * rat._value for degree, coeff in self._terms}
        )

    def __neg__(self) -> "RatPoly":
        """Returns the additive inverse of the polynomial.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Creates a new polynomial equal to `-self`.
        @throws Nothing.
        @returns A new `RatPoly` object.
        """

        return RatPoly.nan() if self.is_nan() else self.scale_coeff(RatNum(-1))

    def __add__(self, other: "RatPoly") -> "RatPoly":
        """Adds two polynomials.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `other` must be a `RatPoly` object.
        @modifies Nothing.
        @effects Returns the sum of the polynomials.
        @throws Nothing.
        @returns A new `RatPoly` object or `NotImplemented` for a foreign type.
        """

        if not isinstance(other, RatPoly):
            return NotImplemented
        if self.is_nan() or other.is_nan():
            return RatPoly.nan()
        result = self._term_dict()
        for degree, coeff in other._terms:
            result[degree] = result.get(degree, Fraction(0)) + coeff
            if result[degree] == 0:
                del result[degree]
        return RatPoly._from_fraction_terms(result)

    def __sub__(self, other: "RatPoly") -> "RatPoly":
        """Subtracts one polynomial from another.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `other` must be a `RatPoly` object.
        @modifies Nothing.
        @effects Returns the difference of the polynomials.
        @throws Nothing.
        @returns A new `RatPoly` object or `NotImplemented` for a foreign type.
        """

        if not isinstance(other, RatPoly):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other: "RatPoly") -> "RatPoly":
        """Multiplies two polynomials.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `other` must be a `RatPoly` object.
        @modifies Nothing.
        @effects Returns the product of the polynomials.
        @throws Nothing.
        @returns A new `RatPoly` object or `NotImplemented` for a foreign type.
        """

        if not isinstance(other, RatPoly):
            return NotImplemented
        if self.is_nan() or other.is_nan():
            return RatPoly.nan()
        result: dict[int, Fraction] = {}
        for left_degree, left_coeff in self._terms:
            for right_degree, right_coeff in other._terms:
                degree = left_degree + right_degree
                result[degree] = result.get(degree, Fraction(0)) + left_coeff * right_coeff
        return RatPoly._from_fraction_terms(result)

    def __truediv__(self, other: "RatPoly") -> "RatPoly":
        """Divides one polynomial by another using long division.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `other` must be a `RatPoly` object.
        @modifies Nothing.
        @effects Returns the quotient of polynomial division over the field of rational numbers.
        @throws Nothing.
        @returns A new `RatPoly`, `NaN` for division by zero/`NaN`, or `NotImplemented` for a foreign type.
        """

        if not isinstance(other, RatPoly):
            return NotImplemented
        if self.is_nan() or other.is_nan() or not other._terms:
            return RatPoly.nan()
        remainder = self._term_dict()
        divisor = other._term_dict()
        quotient: dict[int, Fraction] = {}
        divisor_degree = max(divisor)
        divisor_lead = divisor[divisor_degree]
        while remainder and max(remainder) >= divisor_degree:
            remainder_degree = max(remainder)
            remainder_lead = remainder[remainder_degree]
            step_degree = remainder_degree - divisor_degree
            step_coeff = remainder_lead / divisor_lead
            quotient[step_degree] = quotient.get(step_degree, Fraction(0)) + step_coeff
            for degree, coeff in divisor.items():
                current_degree = degree + step_degree
                updated = remainder.get(current_degree, Fraction(0)) - coeff * step_coeff
                if updated == 0:
                    remainder.pop(current_degree, None)
                else:
                    remainder[current_degree] = updated
        return RatPoly._from_fraction_terms(quotient)

    def eval(self, x: int | float | Fraction | RatNum) -> RatNum | float:
        """Evaluates the polynomial at a given point.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `x` must be a number or `RatNum`.
        @modifies Nothing.
        @effects Substitutes `x` into the polynomial and computes the result.
        @throws `TypeError` if `x` cannot be interpreted as a number.
        @returns `RatNum` for rational input and `float` for floating-point input.
        """

        if isinstance(x, float):
            if self.is_nan():
                return float("nan")
            return sum(float(coeff) * (x ** degree) for degree, coeff in self._terms)
        rat = self._coerce_coeff(x)
        if self.is_nan() or rat.is_nan():
            return RatNum.nan()
        total = Fraction(0)
        for degree, coeff in self._terms:
            total += coeff * (rat._value ** degree)
        return RatNum._from_fraction(total)

    def differentiate(self) -> "RatPoly":
        """Returns the formal derivative of the polynomial.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Builds and returns the formal derivative of the polynomial.
        @throws Nothing.
        @returns A new `RatPoly` object.
        """

        if self.is_nan():
            return RatPoly.nan()
        result = {degree - 1: coeff * degree for degree, coeff in self._terms if degree > 0}
        return RatPoly._from_fraction_terms(result)

    def anti_differentiate(self, constant: int | Fraction | RatNum = RatNum(0)) -> "RatPoly":
        """Builds an antiderivative of the polynomial.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `constant` must be convertible to `RatNum`.
        @modifies Nothing.
        @effects Returns an antiderivative polynomial with the given integration constant.
        @throws `TypeError` if `constant` cannot be converted to `RatNum`.
        @returns A new `RatPoly` object.
        """

        const = self._coerce_coeff(constant)
        if self.is_nan() or const.is_nan():
            return RatPoly.nan()
        result = {degree + 1: coeff / Fraction(degree + 1) for degree, coeff in self._terms}
        if const._value != 0:
            result[0] = const._value
        return RatPoly._from_fraction_terms(result)

    def integrate(self, lower: int | float | Fraction | RatNum, upper: int | float | Fraction | RatNum) -> RatNum | float:
        """Computes the definite integral on an interval.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `lower` and `upper` must be numbers or `RatNum`.
        @modifies Nothing.
        @effects Computes `F(upper) - F(lower)`, where `F` is an antiderivative of the polynomial.
        @throws `TypeError` if the bounds cannot be interpreted as numbers.
        @returns `RatNum` for rational bounds and `float` for floating-point bounds.
        """

        primitive = self.anti_differentiate()
        upper_value = primitive.eval(upper)
        lower_value = primitive.eval(lower)
        if isinstance(upper_value, float) or isinstance(lower_value, float):
            return float(upper_value) - float(lower_value)
        return upper_value - lower_value

    @classmethod
    def value_of(cls, text: str) -> "RatPoly":
        """Creates a polynomial from its string representation.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires `text` must be a non-empty string in the `__str__` format.
        @modifies Nothing.
        @effects Parses the string and builds the corresponding polynomial.
        @throws `ValueError` if the string cannot be parsed.
        @returns A new `RatPoly` object.
        """

        if text is None:
            raise ValueError("text must not be None")
        source = text.replace(" ", "")
        if not source:
            raise ValueError("empty polynomial")
        if source == "NaN":
            return cls.nan()
        if source == "0":
            return cls()
        if source[0] not in "+-":
            source = "+" + source
        tokens = re.findall(r"[+-][^+-]+", source)
        if not tokens:
            raise ValueError(f"cannot parse polynomial: {text}")
        result: dict[int, Fraction] = {}
        for token in tokens:
            sign = -1 if token[0] == "-" else 1
            body = token[1:]
            if "x" not in body:
                coeff = Fraction(body)
                degree = 0
            else:
                if "*x" in body:
                    coeff_part, x_part = body.split("*", 1)
                    coeff = Fraction(coeff_part)
                elif body.startswith("x"):
                    coeff = Fraction(1)
                    x_part = body
                else:
                    raise ValueError(f"cannot parse term: {token}")
                if x_part == "x":
                    degree = 1
                elif x_part.startswith("x^"):
                    degree = int(x_part[2:])
                else:
                    raise ValueError(f"cannot parse term: {token}")
            result[degree] = result.get(degree, Fraction(0)) + sign * coeff
            if result[degree] == 0:
                del result[degree]
        return cls._from_fraction_terms(result)

    def __str__(self) -> str:
        """Converts the polynomial to its canonical string form.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Builds a string compatible with `value_of`.
        @throws Nothing.
        @returns A string like `x^2+1/2*x-3`, `0`, or `NaN`.
        """

        if self.is_nan():
            return "NaN"
        if not self._terms:
            return "0"
        pieces: list[str] = []
        for degree, coeff in reversed(self._terms):
            sign = "-" if coeff < 0 else "+"
            abs_coeff = -coeff if coeff < 0 else coeff
            coeff_text = str(RatNum._from_fraction(abs_coeff))
            if degree == 0:
                body = coeff_text
            else:
                x_part = "x" if degree == 1 else f"x^{degree}"
                body = x_part if abs_coeff == 1 else f"{coeff_text}*{x_part}"
            pieces.append((sign, body))
        first_sign, first_body = pieces[0]
        text = first_body if first_sign == "+" else first_sign + first_body
        for sign, body in pieces[1:]:
            text += sign + body
        return text

    def __hash__(self) -> int:
        """Computes the hash of the object.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Returns a stable hash based on the value of the object.
        @throws Nothing.
        @returns An integer hash.
        """

        return hash(("RatPoly", "NaN")) if self.is_nan() else hash(("RatPoly", self._terms))

    def __eq__(self, other: object) -> bool:
        """Checks whether two polynomials are equal.

        Representation Fields:
        - `_terms`: a sorted tuple of pairs `(degree, coefficient)`.
        - `_nan`: a flag for the special `NaN` state.
        Representation Invariant:
        - if `_nan == False`, then degrees are unique, non-negative, and coefficients are non-zero;
        - the zero polynomial is stored as an empty tuple.
        Abstraction Function:
        - `_nan == True -> NaN`;
        - otherwise `_terms` represents the sum `coeff * x^degree`.

        @requires Nothing.
        @modifies Nothing.
        @effects Compares two objects by their mathematical value.
        @throws Nothing.
        @returns `True` if the polynomials are equivalent, otherwise `False`.
        """

        if not isinstance(other, RatPoly):
            return False
        if self.is_nan() or other.is_nan():
            return self.is_nan() and other.is_nan()
        return self._terms == other._terms
