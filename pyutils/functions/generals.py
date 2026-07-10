from collections.abc import MutableMapping
from types import GeneratorType
from typing import (
    Any,
)


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
