from typing import Any
import pytest

from pyutils.descriptors.computed_properties import (
    SizedString,
    UnsignedInteger,
    UnsignedFloat,
    check_attributes,
    checkedmeta,
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
