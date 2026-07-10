import cProfile
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timedblock(
    label: str,
    *,
    fmt: str = "{}:{:0.5f} seconds",
    rlog: Callable = print,
) -> Generator:
    """
    The function is transformed to contextmanager using the yield protocol, to make it easy to handle
    'interesting' code blocks.

    Args:
        label: name of the timed block
        fmt: formated output, needs at least two empy positons - for the named block and for the timing  {}, {}
        rlog: logger function

    Returns:
        Prints the time spent in the block with the given label; default is print(), but there could be any
        callable functions, which accepts the formatted string

    """
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        rlog(fmt.format(label, end - start))


@contextmanager
def profiledblock(path: Path) -> Generator:
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield
    finally:
        profiler.disable()
        profiler.dump_stats(str(path.absolute()))
