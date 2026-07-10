import pickle
from copy import deepcopy

import pytest

from pyutils.containers.dict_like import DefaultOrderedDict
from pyutils.containers.dict_like import DefaultSingleEntryDict
from pyutils.containers.dict_like import SafeEntryDict
from pyutils.containers.dict_like import SingleEntryDict
from pyutils.containers.dict_like import SingleEntryOrderedDict
from pyutils.containers.dict_like import SortedDict


def test_default_single_entry_dict_empty_list():
    d = DefaultSingleEntryDict(list)
    l = d["a"]
    assert not l
    assert isinstance(l, list)


def test_default_single_entry_dict_list_with_elements():
    d = DefaultSingleEntryDict(list)
    d["a"]
    d["a"].append(1)
    d["a"].append(2)
    d["a"].append(3)
    d["b"]

    l = d["a"]
    assert l == [1, 2, 3]
    assert not d["b"]


def test_key_error_without_default_single_entry_dict():
    d = DefaultSingleEntryDict()
    with pytest.raises(KeyError):
        _ = d["missing"]


def test_default_factory_creates_values():
    d = DefaultOrderedDict(int)
    assert d["missing"] == 0
    d["existing"] = 5
    assert d["existing"] == 5


def test_key_error_without_default_factory():
    d = DefaultOrderedDict()
    with pytest.raises(KeyError):
        _ = d["missing"]


def test_type_error_on_non_callable_default_factory():
    with pytest.raises(TypeError):
        DefaultOrderedDict(123)


def test_preserves_insertion_order():
    d = DefaultOrderedDict(int)
    d["a"] = 1
    d["b"] = 2
    d["c"]

    assert list(d.keys()) == ["a", "b", "c"]
    assert list(d.values()) == [1, 2, 0]


def test_copy_method():
    d = DefaultOrderedDict(list)
    d["x"].append(1)
    d2 = d.copy()

    assert isinstance(d2, DefaultOrderedDict)
    assert d2["x"] == [1]
    assert d2.default_factory is list


def test_deepcopy_method():
    d = DefaultOrderedDict(list)
    d["x"].append(1)
    d2 = deepcopy(d)

    assert d2["x"] == [1]
    assert d2["x"] is not d["x"]
    assert d2.default_factory is list


def test_repr_output():
    d = DefaultOrderedDict(int)
    d["a"] = 42
    d["b"] = 43
    r = repr(d)
    assert "DefaultOrderedDict" in r
    assert "int" in r
    assert "'a': 42" in r


def test_pickle_roundtrip():
    d = DefaultOrderedDict(str)
    d["x"]
    d["y"] = "hello"
    data = pickle.dumps(d)
    d2 = pickle.loads(data)

    assert isinstance(d2, DefaultOrderedDict)
    assert d2["x"] == ""
    assert d2["y"] == "hello"
    assert d2.default_factory is str


def test_single_entry_dict_add_once():
    d = SingleEntryDict()
    d["a"] = 1

    assert d["a"] == 1


def test_single_entry_dict_duplicate_key_raises():
    d = SingleEntryDict()
    d["a"] = 1

    with pytest.raises(KeyError, match=r"The key='a' exists alredy!"):
        d["a"] = 2


def test_single_entry_ordered_dict_add_once():
    d = SingleEntryOrderedDict()
    d["x"] = 10
    d["y"] = 20

    assert d["x"] == 10
    assert list(d.keys()) == ["x", "y"]


def test_single_entry_ordered_dict_duplicate_key_raises():
    d = SingleEntryOrderedDict()
    d["x"] = 100

    with pytest.raises(KeyError, match=r"The key='x' exists alredy!"):
        d["x"] = 200


def test_order_is_preserved():
    d = SingleEntryOrderedDict()
    d["one"] = 1
    d["two"] = 2
    d["three"] = 3

    assert list(d.items()) == [("one", 1), ("two", 2), ("three", 3)]


@pytest.fixture
def sample_dict():
    return SortedDict(dict(s=1, a=2, n=3, i=4, t=5, y=6))


def test_init_empty():
    d = SortedDict()

    assert len(d) == 0
    assert repr(d) == "SortedDict({})"


def test_init_with_dict():
    d = SortedDict({"b": 2, "a": 1})

    assert d.items() == [("a", 1), ("b", 2)]


def test_copy(sample_dict):
    copy = sample_dict.copy()

    assert copy.items() == sample_dict.items()
    assert copy is not sample_dict


def test_clear(sample_dict):
    sample_dict.clear()

    assert len(sample_dict) == 0


def test_get(sample_dict):
    assert sample_dict.get("i") == 4
    assert sample_dict.get("z", 99) == 99


def test_getAt(sample_dict):
    assert sample_dict.getAt(0) == 2  # 'a'
    assert sample_dict.getAt(5) == 6  # 'y'
    with pytest.raises(IndexError):
        sample_dict.getAt(999)


def test_setAt(sample_dict):
    sample_dict.setAt(0, 42)
    assert sample_dict.getAt(0) == 42
    with pytest.raises(IndexError):
        sample_dict.setAt(999, 1)


def test_update_with_dict(sample_dict):
    sample_dict.update({"a": 10, "z": 1})
    assert sample_dict.items()[0] == ("a", 10)
    assert ("z", 1) in sample_dict.items()


def test_update_with_kwargs(sample_dict):
    sample_dict.update(x=10, z=5)
    assert sample_dict["x"] == 10
    assert sample_dict["z"] == 5


def test_update_with_sorted_dict():
    d1 = SortedDict({"a": 1})
    d2 = SortedDict({"b": 2})
    d1.update(d2)
    assert d1.items() == [("a", 1), ("b", 2)]


def test_from_keys():
    d = SortedDict.from_keys("KYLIE", 7)
    assert d.items() == [("E", 7), ("I", 7), ("K", 7), ("L", 7), ("Y", 7)]


def test_setdefault(sample_dict):
    sample_dict.setdefault("r", -10)
    assert sample_dict["r"] == -10
    sample_dict.setdefault("n", 999)
    assert sample_dict["n"] == 3


def test_pop(sample_dict):
    assert sample_dict.pop("n") == 3
    assert "n" not in sample_dict
    assert sample_dict.pop("missing", 42) == 42


def test_popitem(sample_dict):
    before = len(sample_dict)
    sample_dict.popitem()
    assert len(sample_dict) == before - 1


def test_keys_values_items(sample_dict):
    assert sample_dict.keys() == ["a", "i", "n", "s", "t", "y"]
    assert sample_dict.values() == [2, 4, 3, 1, 5, 6]
    assert sample_dict.items() == [
        ("a", 2),
        ("i", 4),
        ("n", 3),
        ("s", 1),
        ("t", 5),
        ("y", 6),
    ]


def test_iter(sample_dict):
    assert list(iter(sample_dict)) == ["a", "i", "n", "s", "t", "y"]
    assert list(sample_dict.iterkeys()) == sample_dict.keys()
    assert list(sample_dict.itervalues()) == sample_dict.values()
    assert list(sample_dict.iteritems()) == sample_dict.items()


def test_has_key_contains(sample_dict):
    assert sample_dict.has_key("a") is True
    assert sample_dict.has_key("z") is False
    assert "a" in sample_dict
    assert "z" not in sample_dict


def test_len(sample_dict):
    assert len(sample_dict) == 6
    del sample_dict["n"]
    assert len(sample_dict) == 5


def test_delitem(sample_dict):
    del sample_dict["a"]
    assert "a" not in sample_dict
    with pytest.raises(KeyError):
        del sample_dict["not_present"]


def test_getitem_setitem(sample_dict):
    assert sample_dict["i"] == 4
    sample_dict["z"] = 10
    assert sample_dict["z"] == 10
    assert "z" in sample_dict
    assert "z" in sample_dict.keys()


def test_repr(sample_dict):
    result = repr(sample_dict)
    assert result.startswith("SortedDict({")
    assert "'a': 2" in result


@pytest.mark.parametrize(
    "actions, expected",
    [
        (
            [("file", 1), ("file", 2), ("file", 3)],
            {"file": 1, "file(1)": 2, "file(2)": 3},
        ),
        (
            [("data(1)", "a"), ("data(1)", "b")],
            {"data(1)": "a", "data(2)": "b"},
        ),
        (
            [("file", 1), ("something(2)", 2), ("file", 3)],
            {"file": 1, "something(2)": 2, "file(1)": 3},
        ),
    ],
    ids=lambda v: f"{v}",
)
def test_safe_entry_dict_with_iterables(actions, expected):
    result = SafeEntryDict(actions)
    assert dict(result) == expected


@pytest.mark.parametrize(
    "values",
    [
        ([(1, "a"), (1, "b")]),
        ([((1, 2, 3), "a"), ((1, 2, 3), "b")]),
    ],
    ids=lambda v: f"{v}",
)
def test_safe_entry_dict_with_int_key(values):
    with pytest.raises(KeyError):
        SafeEntryDict(values)
