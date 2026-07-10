from collections.abc import Callable, Generator, Hashable, Iterable, Iterator
from typing import (
    Any,
)

from .generals import is_hashable


def flatten(items, ignore_types=(str, bytes)):
    # Python Cookbook, David Beazley, 3rd Edition, Recipe 4.14
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x)
        else:
            yield x


def safe_itemgetter(*items: Iterable, default: Any = None) -> Callable:
    if any(not is_hashable(item) for item in items):
        raise TypeError("Item must be hashable")

    def helper(obj: Any) -> Generator:
        if isinstance(obj, dict):
            yield from (obj.get(item, default) for item in items)
        else:
            yield from (getattr(obj, item, default) for item in items)  # type: ignore

    return helper


def dedupe(
    items: Iterable[Hashable],
    key: Callable | None = None,
) -> Iterator[Any]:
    """
    The function remove the duplicated elements and keeps the order

    Note:
        The `key` must provide function, which returns hashable result;

    Args:
        items: Iterable of the elements which will be deduplicate
        key: Transformational function for special cases

    Returns:
        Iterable of unique (hashable) elements
    """

    seen = set()
    for item in items:
        val = item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(val)
