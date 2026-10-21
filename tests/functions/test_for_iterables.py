import pytest

from pyutils.functions.for_iterables import dedupe, flatten, safe_itemgetter


def test_flatten_handles_nested_iterables() -> None:
    nested = [1, [2, (3, 4)], (5, ["a", "bc"]), ["d", ["ef"]]]

    assert list(flatten(nested)) == [1, 2, 3, 4, 5, "a", "bc", "d", "ef"]


def test_safe_itemgetter_works_for_dict_and_object() -> None:
    class Sample:
        def __init__(self) -> None:
            self.alpha = "A"
            self.beta = 2

    sample = Sample()

    assert tuple(safe_itemgetter("alpha", "missing", default="N")(sample)) == ("A", "N")
    assert tuple(safe_itemgetter("alpha", "beta")( {"alpha": "A", "beta": 2} )) == ("A", 2)

    with pytest.raises(TypeError):
        safe_itemgetter(["alpha"])


def test_dedupe_keeps_order_and_respects_key() -> None:
    assert list(dedupe([1, 2, 1, 3, 2, 3])) == [1, 2, 3]
    assert list(dedupe(["aa", "b", "cc", "dd", "ee"], key=len)) == ["aa", "b"]
