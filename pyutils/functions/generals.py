from collections.abc import MutableMapping
from types import GeneratorType
from typing import (
    Any,
    Optional,
    Generator,
)
from itertools import zip_longest


def is_hashable(item: Any) -> bool:
    try:
        hash(item)
        return True
    except TypeError:
        return False


def is_generator(x: Any) -> bool:
    return isinstance(x, GeneratorType)


def _validate_swapping(to_swap: MutableMapping) -> None:
    # sentinels
    if not isinstance(to_swap, MutableMapping):
        raise TypeError(
            "The given data is not from MutableMapping type;\nPlease  fix this error and try again.",
        )

    if not all(is_hashable(value) for value in to_swap.values()):
        TypeError("Not all future keys could be swapped !")


def is_swappable(to_swap: MutableMapping) -> bool | None:
    _validate_swapping(to_swap)

    return True


def parse_safe_nsplits(
    line: str,
    nsplits: int = 0,
    sep: Optional[str] = "",
    maxsplit: int = -1,
    fillvalue: Any = None,
) -> Generator[Any, None, None]:
    """
    Splits a string into a specified number of fields, safely handling missing values.

    Args:
        line (str): The input string to split.
        nsplits (int, optional): The number of splits/fields to return. If 0, no limit is applied. Defaults to 0.
        sep (str, optional): The separator to use for splitting. If None, any whitespace is a separator. Defaults to None.
        maxsplit (int, optional): Maximum number of splits to do. Defaults to 0 (no limit).
        fillvalue (Any, optional): Value to use for missing fields if the split result is shorter than nsplits. Defaults to None.
    """

    fields = line.strip().split(sep=None if not sep else sep, maxsplit=maxsplit)

    yield from (value for value, _ in zip_longest(fields, range(nsplits), fillvalue=fillvalue))
