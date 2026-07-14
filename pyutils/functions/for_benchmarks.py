import cProfile
import time
from collections.abc import (
    Callable,
    Generator,
)
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
    Context manager that measures the elapsed wall-clock time of a code block.

    This uses time.perf_counter() to get a high-resolution elapsed time
    measurement. When the block exits (even if via exception), the elapsed
    seconds are formatted using `fmt` and passed to `rlog`.

    Parameters
    ----------
    label : str
        A short name for the timed block that will be inserted into the format.
    fmt : str, optional
        A format string with (at least) two replacement fields. The first will
        receive `label` and the second will receive the elapsed seconds as a
        floating point number. Default: "{}:{:0.5f} seconds".
    rlog : Callable[[str], Any], optional
        A callable that accepts a single string argument. By default, the
        built-in `print` function is used. You can provide any logger-like
        callable (for example, `logging.Logger.info`) to integrate with an
        application's logging system.

    Yields
    ------
    None
        The context manager yields control to the caller; no value is provided.

    Examples
    --------
    >>> with timedblock("work"):
    ...     do_some_work()
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        rlog(fmt.format(label, end - start))


@contextmanager
def profiledblock(path: Path) -> Generator:
    """
    Context manager that runs cProfile around a block and writes stats to `path`.

    Parameters
    ----------
    path : pathlib.Path
        File path where the profiler stats will be written using
        `cProfile.Profile.dump_stats()`. The stats file is the standard binary
        format that can be read by the `pstats` module or visualizers such as
        `snakeviz`. Example extension: `.prof` or `.pstats`.

    Yields
    ------
    None
        The context manager yields control to the caller; profiling is active
        while inside the block.

    Notes
    -----
    - The profiler is enabled on entering and disabled on exit (even on
      exceptions).
    - `dump_stats()` will attempt to write the file at `path`. Ensure that the
      parent directory exists beforehand, otherwise an OSError may be raised.
    - The written file can be inspected with the standard library:

        import pstats
        p = pstats.Stats("path/to/file.prof")
        p.strip_dirs().sort_stats("cumulative").print_stats(20)

      or with third-party tools like `snakeviz` for a graphical view.

    Examples
    --------
    >>> from pathlib import Path
    >>> out = Path("profiles/run1.prof")
    >>> out.parent.mkdir(parents=True, exist_ok=True)
    >>> with profiledblock(out):
    ...     execute_heavy_function()
    """
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield
    finally:
        # always disable the profiler and write stats on exit
        profiler.disable()
        profiler.dump_stats(str(path.absolute()))
