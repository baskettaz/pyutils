from collections.abc import (
    Iterable,
    Iterator,
)
from typing import (
    Any,
    Generic,
    TypeVar,
)


from pyutils.functions.for_iterables import flatten


T = TypeVar("T")


class OrderedSet(Generic[T]):
    @staticmethod
    def is_iterable(obj: Any) -> bool:
        return obj and isinstance(obj, Iterable)

    def __init__(self, iterable: Iterable[T] | None = None):
        # Note:
        # -----
        # Here the current regular dict implementation, which could be changed in the future,
        # if this would be the case please change dict with OrderedDict to preserve the order.
        self._data: dict[T, None] = {}

        if self.is_iterable(iterable):
            self.update(flatten(iterable))

    def add(self, item: T) -> None:
        self._data[item] = None

    def update(self, iterable: Iterable[T]) -> None:
        for x in iterable:
            self.add(x)

    def discard(self, item: T) -> None:
        self._data.pop(item, None)

    def __contains__(self, item: T) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self._data)})"

    def __str__(self) -> str:
        result = "\n".join(f"{element}" for element in self._data)
        return f"OrderedSet({result})"

    def __getitem__(self, index: int) -> T:
        keys = list(self._data)
        return keys[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderedSet):
            return False
        return self._data == other._data

    def __or__(self, other: Iterable[T]) -> "OrderedSet":
        """Union: self | other"""
        new_ordered_set = OrderedSet(self._data.keys())
        new_ordered_set.update(other)
        return new_ordered_set

    def __and__(self, other: Iterable[T]) -> "OrderedSet":
        """Intersection: self & other"""
        return OrderedSet(x for x in self if x in other)

    def __sub__(self, other: Iterable[T]) -> "OrderedSet":
        """Difference: self - other"""
        return OrderedSet(x for x in self if x not in other)

    def __xor__(self, other: Iterable[T]) -> "OrderedSet":
        """Symmetric difference: self ^ other"""
        result = []
        seen = set()

        # elements in self but not in other
        for x in self:
            if x not in other:
                result.append(x)
                seen.add(x)

        # elements in other but not in self
        for x in other:
            if x not in self._data and x not in seen:
                result.append(x)

        return OrderedSet(result)

    def __ior__(self, other: Iterable[T]) -> "OrderedSet":
        self.update(other)
        return self

    def __iand__(self, other: Iterable[T]) -> "OrderedSet":
        self._data = {x: None for x in self if x in other}
        return self

    def __isub__(self, other: Iterable[T]) -> "OrderedSet":
        self._data = {x: None for x in self if x not in other}
        return self

    def __ixor__(self, other: Iterable[T]) -> "OrderedSet":
        result = self ^ other
        self._data = {x: None for x in result}
        return self
