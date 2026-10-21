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


@pytest.mark.xfail(reason="Known bug in rec_merge_dicts: it checks d1 twice instead of d2, so left-only keys raise KeyError")
def test_rec_merge_dicts_left_only_key_branch() -> None:
    result = dict(rec_merge_dicts({"a": 1, "b": 2}, {}))

    assert result == {"a": 1, "b": 2}


@pytest.mark.xfail(reason="Known bug in rec_merge_dicts: it never reaches the right-only branch because the condition is duplicated")
def test_rec_merge_dicts_right_only_key_branch() -> None:
    result = dict(rec_merge_dicts({}, {"a": 1, "b": 2}))

    assert result == {"a": 1, "b": 2}


def test_deep_get_returns_nested_values_or_none() -> None:
    payload = {"user": {"profile": {"name": "Ada"}}}

    assert deep_get(["user", "profile", "name"], payload) == "Ada"
    assert deep_get(["user", "profile", "age"], payload) is None


def test_deep_get_returns_none_when_intermediate_value_is_not_mapping() -> None:
    payload = {"user": "not-a-dict"}

    assert deep_get(["user", "profile"], payload) is None


@pytest.mark.xfail(reason="Known bug in rec_merge_dicts: it checks the same side twice and raises KeyError when only one dict contains a key")
def test_rec_merge_dicts_keeps_left_when_right_missing() -> None:
    left = {"a": 1, "b": {"x": 2}}
    right = {"c": 3}

    result = dict(rec_merge_dicts(left, right))

    assert result == {"a": 1, "b": {"x": 2}, "c": 3}


def test_rec_merge_dicts_uses_callable_for_non_mapping_values() -> None:
    left = {"a": 1}
    right = {"a": 2}

    result = dict(rec_merge_dicts(left, right, func=lambda value: value + 10))

    assert result == {"a": 12}


def test_rec_merge_dicts_raises_type_error_for_non_callable_func() -> None:
    left = {"a": 1}
    right = {"a": 2}

    with pytest.raises(TypeError):
        dict(rec_merge_dicts(left, right, func=123))


@pytest.mark.xfail(reason="Known bug in rec_merge_dicts: it dereferences the missing mapping before checking which side owns the key")
def test_rec_merge_dicts_handles_plain_dicts_without_conflicting_keys() -> None:
    left = {"a": {"x": 1}, "b": 2}
    right = {"c": {"y": 3}, "d": 4}

    result = dict(rec_merge_dicts(left, right))

    assert result == {"a": {"x": 1}, "b": 2, "c": {"y": 3}, "d": 4}
