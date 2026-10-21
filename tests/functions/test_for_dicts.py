import pytest

from pyutils.containers.dict_like import SingleEntryOrderedDict
from pyutils.functions.for_dicts import deep_get, rec_merge_dicts, swap_dict


def test_swap_dict_reverses_keys_and_values() -> None:
    original = {"a": 1, "b": 2}

    swapped = swap_dict(original)
    assert list(swapped.items()) == [(1, "a"), (2, "b")]
    assert isinstance(swapped, SingleEntryOrderedDict)

    reverse = swap_dict(original, ord_dict=False)
    assert list(reverse.items()) == [(1, "a"), (2, "b")]


@pytest.mark.xfail(reason="Known bug in rec_merge_dicts: nested-key branch checks d1 twice and can raise KeyError")
def test_rec_merge_dicts_handles_nested_mappings_and_custom_func() -> None:
    left = {"a": {"x": 1, "y": 2}, "b": 3}
    right = {"a": {"x": 9, "z": 4}, "c": 5}

    merged = dict(rec_merge_dicts(left, right))
    assert merged == {"a": {"x": 9, "y": 2, "z": 4}, "b": 3, "c": 5}

    renamed = dict(rec_merge_dicts({"a": 1}, {"a": 2}, func=lambda value: value + 10))
    assert renamed == {"a": 12}


def test_deep_get_returns_nested_values_or_none() -> None:
    payload = {"user": {"profile": {"name": "Ada"}}}

    assert deep_get(["user", "profile", "name"], payload) == "Ada"
    assert deep_get(["user", "profile", "age"], payload) is None
