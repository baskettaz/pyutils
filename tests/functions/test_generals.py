from pyutils.functions.generals import parse_safe_nsplits

import pytest

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
