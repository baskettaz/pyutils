import logging
from contextlib import contextmanager


@contextmanager
def debug_logging(level=logging.DEBUG):
    """
    Temporarily set the root logger level for the duration of a with-block.

    Parameters
    - level (int): logging level to set (e.g. logging.DEBUG, logging.INFO). Default: logging.DEBUG.

    Yields
    - None. The context manager is used for its side-effect (temporary level change).

    Example:
        >>> with debug_logging(logging.CRITICAL):
        ...    do_something()
    """
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)

    try:
        yield
    finally:
        logger.setLevel(old_level)



@contextmanager
def log_level(level, name:str):
    """
    Temporarily set the logging level for a named logger and yield the logger.

    Parameters
    - level (int): logging level to set (e.g. logging.DEBUG, logging.INFO).
    - name (str): the logger name (passed to logging.getLogger(name)).

    Yields
    - logging.Logger: the logger instance whose level has been temporarily changed.

    Behavior
    - Saves the target logger's current effective level, sets the requested level,
      yields the logger for use inside the with-block, and restores the original level
      on exit (including when exceptions occur).

    Example:
        >>> with log_level(logging.INFO, "my.package.module") as logger:
        ...    logger.info("This will be shown at INFO level")
    """
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)
