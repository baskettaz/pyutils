from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from numbers import Number
from typing import Any, SupportsIndex, overload


class GenericCustomList(list):
    def __init__(self, iterable: Iterable) -> None:
        super().__init__(self._validate_item(item) for item in iterable)

    @overload
    def __setitem__(self, index: SupportsIndex, value: Any) -> None: ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[Any]) -> None: ...

    def __setitem__(self, index: SupportsIndex | slice, value: Any) -> None:
        # force evaluation of the iterable
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Number)):
            transformed = [self._validate_item(element) for element in value]
            super().__setitem__(index, transformed)
        else:
            super().__setitem__(index, self._validate_item(value))

    def insert(self, index: SupportsIndex, item: Any) -> None:
        super().insert(index, self._validate_item(item))

    def append(self, item: Any) -> None:
        super().append(self._validate_item(item))

    def extend(self, other: Iterable[Any]) -> None:
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(self._validate_item(item) for item in other)

    def _validate_item(self, value: Any) -> Any:
        raise NotImplementedError

    def __str__(self) -> str:
        args = ", ".join(str(value) for value in self)
        return f"{self.__class__.__name__}([{args}])"

    def __repr__(self) -> str:
        args = ", ".join(str(value) for value in self)
        return f"{self.__class__.__name__}([{args}])"


class StringOnlyList(GenericCustomList):
    def _validate_item(self, value: Any) -> Any:
        return str(value)


class NumberOnlyList(GenericCustomList):
    def _validate_item(self, value: Any) -> Any:
        if isinstance(value, (int, float, complex)):
            return value
        raise TypeError(f"numeric value expected, got {type(value).__name__}")


class UniqueDeque(deque):
    def __init__(self, iterable: Iterable = (), maxlen: int = 5):
        self.unique: set = set()
        # fmt: off
        super().__init__(
            iterable = self.preselect(iterable),
            maxlen   = maxlen,
        )
        # fmt: on

    def preselect(self, iterable: Iterable) -> Iterable:
        for item in iterable:
            if item in self.unique:
                continue

            self.unique.add(item)
            yield item

    def append(self, item: Any) -> None:
        if item not in self.unique:
            if self.maxlen is not None and len(self) >= self.maxlen:
                removed = self.popleft()
                self.unique.discard(removed)

            self.unique.add(item)
            super().append(item)

    def appendleft(self, item: Any) -> None:
        if item not in self.unique:
            if self.maxlen is not None and len(self) >= self.maxlen:
                removed = self.pop()
                self.unique.discard(removed)
            self.unique.add(item)
            super().appendleft(item)
