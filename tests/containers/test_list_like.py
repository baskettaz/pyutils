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
