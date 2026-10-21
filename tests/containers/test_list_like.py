import pytest

from pyutils.containers.list_like import NumberOnlyList, StringOnlyList, UniqueDeque


def test_string_only_list_casts_values() -> None:
    items = StringOnlyList([1, 2.5, None, True])

    assert items == ["1", "2.5", "None", "True"]
    assert str(items) == "StringOnlyList([1, 2.5, None, True])"


def test_number_only_list_validates_values() -> None:
    numeric = NumberOnlyList([1, 2.5])
    numeric[1] = 3
    numeric.append(4 + 5j)
    numeric.extend([6, 7])

    assert numeric == [1, 3, 4 + 5j, 6, 7]

    with pytest.raises(TypeError):
        numeric.append("bad")


def test_unique_deque_deduplicates_and_tracks_maxlen() -> None:
    dq = UniqueDeque([1, 2, 2, 3], maxlen=3)

    assert list(dq) == [1, 2, 3]

    dq.append(2)
    dq.append(4)
    assert list(dq) == [2, 3, 4]

    dq.appendleft(5)
    assert list(dq) == [5, 2, 3]


def test_generic_list_setitem_and_extend_and_repr() -> None:
    class IntList(NumberOnlyList):
        pass

    numbers = IntList([1, 2])
    numbers[0] = 7
    numbers[1:2] = [8, 9]
    numbers.insert(0, 10)
    numbers.extend((11, 12))

    assert repr(numbers) == "IntList([10, 7, 8, 9, 11, 12])"
    assert str(numbers) == "IntList([10, 7, 8, 9, 11, 12])"

    with pytest.raises(TypeError):
        numbers.append("bad")

    with pytest.raises(TypeError):
        numbers.__setitem__(0, ["bad"])


def test_unique_deque_drops_oldest_when_full_from_append_and_appendleft() -> None:
    dq = UniqueDeque([1, 2], maxlen=2)
    dq.append(3)
    assert list(dq) == [2, 3]

    dq.appendleft(4)
    assert list(dq) == [4, 2]


def test_string_only_list_extend_accepts_non_list_iterables() -> None:
    items = StringOnlyList([1])
    items.extend((2, 3.5))

    assert items == ["1", "2", "3.5"]


def test_unique_deque_skips_duplicate_appendleft() -> None:
    dq = UniqueDeque([1, 2], maxlen=2)
    dq.appendleft(1)

    assert list(dq) == [1, 2]
