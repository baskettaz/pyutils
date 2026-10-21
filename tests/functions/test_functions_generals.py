import pytest

from pyutils.functions.generals import is_generator, is_hashable, is_swappable, parse_safe_nsplits


@pytest.mark.parametrize(
    "line,nsplits,sep,maxsplit,fillvalue,expected",
    # fmt: off
    [
        ("a b c", 5, None, -1, "x", ["a", "b", "c", "x", "x"]),
        ("1,2,3", 4, ",", -1, "0", ["1", "2", "3", "0"]),
        ("", 3, None, -1, "-", ["-", "-", "-"]),
        ("foo bar", 2, None, -1, None, ["foo", "bar"]),
        ("foo", 1, None, -1, "z", ["foo"]),
    ],
    # fmt: on
)
def test_parse_safe_nsplits(line, nsplits, sep, maxsplit, fillvalue, expected):
    result = list(parse_safe_nsplits(line, nsplits, sep, maxsplit, fillvalue))
    assert result == expected


def test_hashable_and_generator_checks() -> None:
    assert is_hashable("abc") is True
    assert is_hashable([]) is False
    assert is_generator((x for x in range(3))) is True
    assert is_generator([1, 2, 3]) is False


def test_is_swappable_requires_hashable_values() -> None:
    assert is_swappable({"a": 1, "b": 2}) is True
    assert is_swappable({"a": [1], "b": 2}) is True

    with pytest.raises(TypeError):
        is_swappable([])
