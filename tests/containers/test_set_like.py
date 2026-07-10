from collections.abc import Generator

import pytest

from pyutils.containers.set_like import OrderedSet


@pytest.fixture(scope="function")
def left() -> Generator[OrderedSet]:
    yield OrderedSet([1, 2, 3, 3, 3, 4])


@pytest.fixture(scope="function")
def right() -> Generator[OrderedSet]:
    yield OrderedSet([3, 3, 3, 4, 5])


def test_addition(left):
    left.add(5)
    result = left._data
    expected = {1: None, 2: None, 3: None, 4: None, 5: None}

    assert result == expected


def test_update(left):
    left.update([1, 2, 3, 4, 5])
    result = left._data
    expected = {1: None, 2: None, 3: None, 4: None, 5: None}

    assert result == expected


def test_discard(left):
    left.discard(1)

    result = left._data
    expected = {2: None, 3: None, 4: None}

    assert result == expected


def test_contains(left):
    for num in range(1, 5):
        assert num in left


def test_iter_one(left):
    for first, second in zip(left, range(1, 5), strict=True):
        assert first == second


def test_iter_two(left):
    element = next(iter(left))
    assert element == 1


def test_length(left):
    assert len(left) == 4


def test_repr(left):
    assert repr(left) == "OrderedSet([1, 2, 3, 4])"


def test_get_item(left):
    assert left[0] == 1
    assert left[2] == 3
    assert left[-1] == 4


def test_eq(left):
    assert left == OrderedSet([1, 2, 3, 4])


def test_or(left, right):
    result = left | right
    expected = OrderedSet([1, 2, 3, 4, 5])

    assert result == expected
    assert id(left) != id(result)


def test_and(left, right):
    result = left & right
    expected = OrderedSet([3, 4])

    assert result == expected
    assert id(left) != id(result)


def test_sub(left, right):
    result = left - right
    expected = OrderedSet([1, 2])

    assert result == expected
    assert id(left) != id(result)


def test_xor(left, right):
    result = left ^ right
    expected = OrderedSet([1, 2, 5])

    assert result == expected
    assert id(left) != id(result)


def test_ior(left, right):
    left |= right
    expected = OrderedSet([1, 2, 3, 4, 5])

    assert left == expected


def test_iand(left, right):
    left &= right
    expected = OrderedSet([3, 4])

    assert left == expected


def test_isub(left, right):
    left -= right
    expected = OrderedSet([1, 2])

    assert left == expected


def test_ixor(left, right):
    left ^= right
    expected = OrderedSet([1, 2, 5])

    assert left == expected
