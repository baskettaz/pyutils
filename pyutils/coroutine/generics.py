from collections.abc import Callable, Generator
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")


def coroutine(func: Callable) -> Any:
    """
    This decorator primes the function, which will be used to push the results.

    Args
    ----
        func: any callable, which has been foreseen for coroutine
    """

    @wraps(func)
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def coro_filter(target: Generator[T, T, None]) -> None:
    """
    The coroutine is used as general AND filter in the processing chain.
    This could be further developed to consider OR-cases if needed.

    Notes
    -----
        Could be used N-times if needed
    """
    target.throw(NotImplementedError, "The filter - function isn't implemented!")


@coroutine
def empty_filter(target: Generator[T, T, None]) -> Generator[None, T, None]:
    "No filtering"
    while 1:
        element = yield
        target.send(element)


@coroutine
def coro_reduce(target: Generator[T, T, None]) -> None:
    """
    The coroutine takes off there, where the filter functions ends and reduces
    the results in such a manner that the sink could work with them.

    Notes
    -----
        Could be used N-times if needed
    """
    target.throw(NotImplementedError, "The reduce - function isn't implemented!")


@coroutine
def no_reduce(target: Generator[T, T, None]) -> Generator[None, T, None]:
    "No reduction"
    while 1:
        element = yield
        target.send(element)


@coroutine
def coro_create(target: Generator) -> None:
    """
    The function takes in consideration the concrete case and as response,
    models the 'automatons' in nested while-loops.
    """
    target.throw(
        NotImplementedError,
        "The create_structure - function isn't implemented!",
    )


@coroutine
def get_coro_sink(sink: Any) -> Generator[None, T, None]:
    """
    The endpoint in the whole processing chain. The results must be saved in the
    predefined sink, which is somewhat fussy defined in the function arguments.
    """
    try:
        while 1:
            element = yield
            sink.add(element)
    except AttributeError:
        raise NotImplementedError("The get_sink - function isn't implemented!")
