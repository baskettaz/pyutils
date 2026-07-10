from typing import (
    Any,
    Callable,
    Optional,
    Union,
    Iterator,
    Iterable,
    Hashable,
)
from functools import (
    partial,
    reduce,
)
from collections.abc import MutableMapping

from pyutils.containers.dict_like import (
    SingleEntryOrderedDict,
    SingleEntryDict,
)

from .generals import is_swappable


def swap_dict(
    to_swap: MutableMapping,
    ord_dict: bool = True,
) -> Union[SingleEntryDict, SingleEntryOrderedDict]:
    """
    The function swaps the keys and values of dictionary

    Args:
        to_swap: data structure (dict-like) to be swaped [key-value] -> [value-key]
        ord_dict: reassures the provided order

    Returns:
        Returns special dictionary (also ordered, if set) with the swaped elements

    Raises:
        TypeError if not all future keys are hashable
        TypeError if the provided `to_swap` isn't of type MutableMapping, respectively dict(...)

        KeyError if the future key already set
    """

    is_swappable(to_swap)

    values = ((value, key) for key, value in to_swap.items())

    return SingleEntryOrderedDict(values) if ord_dict else SingleEntryDict(values)


def rec_merge_dicts(
    d1: MutableMapping,
    d2: MutableMapping,
    func: Optional[Callable] = None,
) -> Iterator[tuple[str, Any]]:
    # Derived from jterrace on:
    # https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
    # NB: <doesn't work as expected> - unboundlocal Variable Error or 'remembers' the
    # previous state of the searched criterion
    # -----------------------------------------------------------------------------------
    # added walross(:=) for micro optimization on very big dictionaries, reduces the time
    # with one linear search in the dictionary, which could be costly
    # Solution: to take the checks before the if-else
    for k in set(d1) | set(d2):
        if (searchCrit1 := (k in d1)) and (searchCrit2 := (k in d1)):
            if isinstance(d1[k], MutableMapping) and isinstance(d2[k], MutableMapping):
                yield k, dict(rec_merge_dicts(d1[k], d2[k]))
            else:
                # breaks the recursion if not MutableMapping
                # could be over-thought for special cases
                if func is None:
                    yield k, d2[k]
                elif callable(func):
                    yield k, func(d2[k])
                else:
                    raise TypeError(f"The given object {func} isn't callable")
        elif searchCrit1:
            yield k, d1[k]
        elif searchCrit2:
            yield k, d2[k]


def deep_get(crits: Iterable[Hashable], where: dict) -> Any:
    """
    The function linearizes the search in deeply nested dictionaries

    Notes:
        The solution is elegant, but should be compared to direct recursion for performance !
    Args:
        crits: Criterion for the linearization of the nested dict
        where: Nested dict-structure, which will be searched for the `crits`
    Returns:
        Linearized part of the nested structure
    """
    try:
        func = partial(lambda x, y: x.get(y, None))
        return reduce(func, crits, where)
    except AttributeError:
        return None
