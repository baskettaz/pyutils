from __future__ import annotations

import bisect
import re
from collections import OrderedDict
from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any, Self, TypeVar

from _typeshed import SupportsRichComparison


K = TypeVar("K", bound=SupportsRichComparison)


class DefaultDictMixin(dict):
    "Custom ordered dictionary, similar to the classic defaultdict"

    # Source: http://stackoverflow.com/a/6190500/562769

    def __init__(self, *a, default_factory: Callable | None = None, **kw):
        if default_factory is not None and not callable(default_factory):
            raise TypeError("first argument must be callable")
        super().__init__(*a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key) -> Any:
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key) -> Any:
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self) -> tuple:
        args = tuple() if self.default_factory is None else (self.default_factory,)
        return type(self), args, None, None, iter(self.items())

    def copy(self) -> Self:
        return self.__copy__()

    def __copy__(self) -> Self:
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo) -> Self:
        return type(self)(self.default_factory, deepcopy(dict(self)))

    def __repr__(self) -> str:
        default = f"{self.default_factory}"
        text = f"{super().__repr__()}"
        indx = text.index("(") + 1
        return "".join([text[:indx], default, ", ", text[indx:]])


class DefaultOrderedDict(DefaultDictMixin, OrderedDict):
    pass


class SingleEntryDict(dict):
    "Custom dictionary class that throws an error on duplicate key assignment"

    # Source:
    # https://stackoverflow.com/questions/73143580/add-element-to-dict-but-dont-overwrite-value-when-key-exists
    def __setitem__(self, key: K, value: Any) -> None:
        if key not in self:
            super().__setitem__(key, value)
        else:
            raise KeyError(f"The {key=} exists alredy!")


class DefaultSingleEntryDict(DefaultDictMixin, SingleEntryDict):
    pass


class SafeEntryDict(dict):
    "Custom dictionary that makes new key with (xx) if already exists. See New Folder analogy in Windows"

    pattern = re.compile(r"(?P<base>.*)\((?P<increment>\d+)\)")

    def __init__(self, iterable: Iterable[tuple[K, Any]] | None = None):
        super().__init__()
        if iterable:
            for k, v in iterable:
                self[k] = v  # use our overridden __setitem__

    def __setitem__(self, key: K, value: Any) -> None:
        if key not in self:
            super().__setitem__(key, value)
        elif not isinstance(key, str):
            raise KeyError(f"The {key=} must be a string")
        else:
            if values := self.pattern.match(key):
                base, increment = values.groups()
            else:
                base = key
                increment = 1

            results = [
                int(values.group("increment")) for item in self if (values := self.pattern.match(item)) and base in item
            ]

            super().__setitem__(
                f"{base}({max(results) + 1 if results else increment})",
                value,
            )


class SingleEntryOrderedDict(OrderedDict):
    """
    Custom dictionary class that throws an error on duplicate key assignment,
    but for an ordered dictionary
    """

    def __setitem__(self, key: K, value: Any) -> None:
        if key not in self:
            super().__setitem__(key, value)
        else:
            raise KeyError(f"The {key=} exists alredy!")


class SortedDict:
    """
    A dictionary sorted by keys.

    The initialization is costly because all keys in the dictionary must be sorted.
    This applies also to the `update()` method.
    """

    def __init__(self, dictionary: dict | SortedDict = dict()) -> None:
        self.__keys: list = []
        self.__dict: dict = dict()
        if dictionary is not None:
            if isinstance(dictionary, type(self)):
                self.__dict = dictionary.__dict.copy()
                self.__keys = dictionary.__keys[:]
            else:
                self.__dict = dict(dictionary).copy()
                self.__keys = sorted(self.__dict.keys())

    def update(
        self,
        dictionary: dict | SortedDict | None = None,
        **kwargs,
    ) -> None:
        "Updates this dictionary with another dictionary and/or key-value pairs as a keyword"

        if dictionary is None:
            pass
        elif isinstance(dictionary, type(self)):
            self.__dict.update(dictionary.__dict)
        elif isinstance(dictionary, dict) or not hasattr(dictionary, "items"):
            self.__dict.update(dictionary)
        else:
            for key, value in dictionary.items():
                self.__dict[key] = value
        if kwargs:
            self.__dict.update(kwargs)
        self.__keys = sorted(self.__dict.keys())

    @classmethod
    def from_keys(cls, iterable, value=None):
        "A class method that returns a `SortedDict` whose keys come from the iterable and which start values are as `value`"

        dictionary = cls()
        for key in iterable:
            dictionary[key] = value
        return dictionary

    def getAt(self, index: int) -> Any:
        """
        Returns the value of the element at the specified index position.

        Args:
            index (int): Der Index des gesuchten Elements.
        """
        return self.__dict[self.__keys[index]]

    def setAt(self, index: int, value: Any) -> None:
        """
        Sets the value of the element at the specified index position.

        Args:
            index (int): Der Index des zu setzenden Elements.
            value (Any): Der zu setzende Wert.
        """
        self.__dict[self.__keys[index]] = value

    def copy(self) -> SortedDict:
        "Shallow copy of the `SortedDict`"
        dictionary = SortedDict()
        dictionary.__keys = self.__keys[:]
        dictionary.__dict = self.__dict.copy()
        return dictionary

    def clear(self) -> None:
        "Clears the `SortedDict`"

        self.__keys = []
        self.__dict = {}

    def get(self, key: K, value: Any = None) -> Any:
        "Returns the value of the `key` or the default `value` if the key does not exist"
        return self.__dict.get(key, value)

    def setdefault(self, key: K, value: Any) -> dict:
        "Sets a default value for a specific key"
        if key not in self.__dict:
            bisect.insort_left(self.__keys, key)
        return self.__dict.setdefault(key, value)

    def pop(self, key: K, value: Any = None) -> Any:
        "Removes and returns (pops) the value for a concrete key , otherwise returns the default value"
        if key not in self.__dict:
            return value
        i = bisect.bisect_left(self.__keys, key)
        del self.__keys[i]
        return self.__dict.pop(key, value)

    def popitem(self) -> Any:
        "Removes and returns(pops) arbitrary element of the dictionary."

        item = self.__dict.popitem()
        i = bisect.bisect_left(self.__keys, item[0])
        del self.__keys[i]
        return item

    def keys(self) -> list:
        "Returns the dictionary keys in ascending order"
        return self.__keys[:]

    def values(self) -> list:
        "Returns the dictionary values in key order"
        return [self.__dict[key] for key in self.__keys]

    def items(self) -> list[tuple]:
        "Returns the elements of the dictionary in key order"
        return [(key, self.__dict[key]) for key in self.__keys]

    def __iter__(self) -> Iterable:
        "Returns an iterator over the dictionary's keys in sorted order"
        return iter(self.__keys)

    def iterkeys(self) -> Iterable:
        "Returns an iterator over the dictionary's keys"
        return iter(self.__keys)

    def itervalues(self) -> Any:
        "Returns an iterator over the dictionary's values in key order"
        for key in self.__keys:
            yield self.__dict[key]

    def iteritems(self) -> Any:
        "Returns an iterator over the dictionary's key-value pairs in key order"
        for key in self.__keys:
            yield key, self.__dict[key]

    def has_key(self, key: K) -> bool:
        "Returns True if the key is in the dictionary; False otherwise"
        return key in self.__dict

    def __contains__(self, key: K) -> bool:
        "Returns True if the key is in the dictionary; False otherwise"
        return key in self.__dict

    def __len__(self) -> int:
        "Returns the number of elements in the dictionary"
        return len(self.__dict)

    def __delitem__(self, key: K) -> None:
        "Deletes the item with the specified key from the dictionary"
        del self.__dict[key]
        i = bisect.bisect_left(self.__keys, key)
        del self.__keys[i]

    def __getitem__(self, key: K) -> Any:
        "Returns the value of the element with the specified key"
        return self.__dict[key]

    def __setitem__(self, key: K, value: Any) -> None:
        """
        Sets the value of the specified key to the given value if the key is in the dictionary;
        otherwise, adds the key with the value.
        """
        if key not in self.__dict:
            bisect.insort_left(self.__keys, key)
        self.__dict[key] = value

    def __repr__(self) -> str:
        """
        Returns an evaluable string (eval()) representation of the dictionary.

        Notes:
            Alternative implementation using a list comprehension:

            return "SortedDict({{{0}}})".format(", ".join(
                   ["{0!r}: {1!r}".format((key, self.__dict[key])) \
                    for key in self.__keys]))
        """
        pieces = []
        for key in self.__keys:
            pieces.append(f"{key!r}: {self.__dict[key]!r}")
        return "SortedDict({{{0}}})".format(", ".join(pieces))
