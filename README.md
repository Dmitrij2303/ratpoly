# RatPoly

- `RatNum` — неизменяемое рациональное число с поддержкой `NaN`
- `RatPoly` — неизменяемый полином с рациональными коэффициентами

Проект написан на Python и использует только стандартную библиотеку.

## Что реализовано

### RatNum

Поддерживаются операции:

- `is_nan()`
- `is_negative()`
- `is_positive()`
- `compare_to()`
- `float_value()`
- `int_value()`
- унарный `-`
- `+`
- бинарный `-`
- `*`
- `/`
- `gcd()`
- `__str__()`
- `__hash__()`
- `__eq__()`

### RatPoly

Поддерживаются операции:

- `degree()`
- `get_coeff()`
- `is_nan()`
- `scale_coeff()`
- унарный `-`
- `+`
- бинарный `-`
- `*`
- `/`
- `eval()`
- `differentiate()`
- `anti_differentiate()`
- `integrate()`
- `value_of()`
- `__str__()`
- `__hash__()`
- `__eq__()`

## Структура проекта

```text
ratpoly/
├── README.md
├── ratpoly/
│   ├── __init__.py
│   ├── ratnum.py
│   └── ratpoly.py
└── tests/
    ├── test_ratnum.py
    └── test_ratpoly.py
```

## Основные идеи реализации

- `RatNum` хранит обычные рациональные числа через `fractions.Fraction`
- значение `NaN` хранится отдельно как специальное состояние
- `RatPoly` хранит только ненулевые коэффициенты
- нулевой полином хранится как пустой набор членов
- оба класса сделаны неизменяемыми

## Как запустить тесты

Из корня проекта:

```bash
python3 -m unittest discover -s tests -v
```

## Примеры использования

```python
from ratpoly import RatNum, RatPoly

# Rational numbers
a = RatNum(1, 2)
b = RatNum(3, 4)
print(a + b)      # 5/4
print(a * b)      # 3/8
print(RatNum(1, 0))  # NaN

# Polynomials
p = RatPoly({2: 1, 1: RatNum(3, 2), 0: -4})
q = RatPoly.value_of("x+1")

print(p)              # x^2+3/2*x-4
print(q)              # x+1
print(p + q)          # x^2+5/2*x-3
print(p.differentiate())   # 2*x+3/2
print(q.eval(RatNum(2)))   # 3
```

## Формат строкового представления

### RatNum

Примеры:

- `1/2`
- `-7/3`
- `5`
- `0`
- `NaN`

### RatPoly

Примеры:

- `x^2+3/2*x-4`
- `x+1`
- `-x^2+x-1`
- `0`
- `NaN`

Метод `RatPoly.value_of(...)` разбирает строки в формате, который возвращает `RatPoly.__str__()`.

## Примечания

- Деление на ноль в `RatNum` дает `NaN`
- Любая арифметика с `NaN` дает `NaN`
- В сравнении `NaN` считается равным самому себе и больше любого обычного рационального числа
- Деление полиномов реализовано как деление в столбик над рациональными числами
