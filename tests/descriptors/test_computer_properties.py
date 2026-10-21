from typing import Any

import pytest

from pyutils.descriptors.computed_properties import (
    Descriptor,
    Integer,
    MaxSized,
    String,
    SizedString,
    Typed,
    Unsigned,
    UnsignedFloat,
    UnsignedInteger,
    check_attributes,
    checkedmeta,
    lazyproperty,
)


def all_stock_cases(stock: Any) -> None:
    Stock = stock

    # Correct parameters
    # ==================
    stock = Stock("ACME", 50, 91.1)

    assert stock.name == "ACME"
    assert isinstance(stock.name, str) and len(stock.name) < 8
    assert stock.shares == 50
    assert isinstance(stock.shares, int) and stock.shares >= 0
    assert stock.price == 91.1
    assert isinstance(stock.price, float) and stock.price >= 0

    # Full combinatoric of the bad parameters
    # =======================================
    with pytest.raises(ValueError):
        Stock("ACMEACMEACME", 50, 91.1)

    with pytest.raises(TypeError):
        Stock(1, 50, 91.1)

    with pytest.raises(ValueError):
        Stock("ACME", -50, 91.1)

    with pytest.raises(TypeError):
        Stock("ACME", "50", 91.1)

    with pytest.raises(ValueError):
        Stock("ACME", 50, -91.1)

    with pytest.raises(TypeError):
        Stock("ACME", 50, "91.1")


def test_first_approach_direct():
    class Stock:
        name = SizedString("name", size=8)
        shares = UnsignedInteger("shares")
        price = UnsignedFloat("price")

        def __init__(self, name, shares, price):
            self.name = name
            self.shares = shares
            self.price = price

    all_stock_cases(Stock)


def test_second_approach_decorator():
    @check_attributes(name=SizedString(size=8), shares=UnsignedInteger, price=UnsignedFloat)
    class Stock2:
        def __init__(self, name, shares, price):
            self.name = name
            self.shares = shares
            self.price = price

    all_stock_cases(Stock2)


def test_third_approach_metaclass():
    class Stock3(metaclass=checkedmeta):
        name = SizedString("name", size=8)
        shares = UnsignedInteger("shares")
        price = UnsignedFloat("price")

        def __init__(self, name, shares, price):
            self.name = name
            self.shares = shares
            self.price = price

    all_stock_cases(Stock3)


def test_lazyproperty_descriptor_and_validation_branches():
    class Demo:
        def __init__(self) -> None:
            self.base = 2

        @lazyproperty
        def total(self):
            return self.base * 3

    demo = Demo()
    assert demo.total == 6
    assert demo.__dict__["total"] == 6
    assert Demo.total.__get__(None, Demo) is Demo.total

    class Box:
        value = Descriptor("value")

        def __init__(self, value):
            self.value = value

    box = Box("alpha")
    assert box.value == "alpha"

    class Person:
        age = Typed("age", expected_type=int)

        def __init__(self, age):
            self.age = age

    p = Person(5)
    assert p.age == 5
    with pytest.raises(TypeError):
        Person("bad")

    class Count:
        total = Unsigned("total")

        def __init__(self, total):
            self.total = total

    assert Count(7).total == 7
    with pytest.raises(ValueError):
        Count(-1)

    with pytest.raises(TypeError):
        MaxSized()

    class Limited:
        word = MaxSized("word", size=4)

        def __init__(self, word):
            self.word = word

    assert Limited("abc").word == "abc"
    with pytest.raises(ValueError):
        Limited("longer")

    @check_attributes(name=lambda key: String(key), age=lambda key: UnsignedInteger(key))
    class Employee:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    employee = Employee("Ada", 7)
    assert employee.name == "Ada"
    assert employee.age == 7

    class PersonMeta(metaclass=checkedmeta):
        name = String("name")
        age = Integer("age")

    assert PersonMeta.__dict__["name"].name == "name"
    assert PersonMeta.__dict__["age"].name == "age"
