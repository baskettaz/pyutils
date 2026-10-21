import mmap
import re
from collections.abc import (
    Iterable,
    Iterator,
)
from pathlib import Path
from re import (
    Pattern,
    RegexFlag,
)
from typing import (
    Any,
)

from difflib import SequenceMatcher


def multisplit(
    text: str,
    separators: Iterable[str],
    keep_sep: bool = False,
    flags: RegexFlag | None = None,
) -> list:
    """
    The function is somewhat similar to the regular 'text'.split(...) function, but for multiple symbols.

    Note:
        The regular `split` has `maxsplit=` argument, which isn't considered here

    Args:
        text: text which should be splitted
        separators: iterable of all relevant separators
        keep_sep: keep the separators in the result
        flags: RegEx flags

    Returns:
        List with of the splitted characters
    """
    pattern = "|".join(sep for sep in set(separators))
    pattern = f"[{pattern}]" if not keep_sep else f"({pattern})"
    pattern = re.compile(pattern, flags=flags) if flags else re.compile(pattern)

    return [v for v in pattern.split(text) if v]


def multireplace(text: str, old: Iterable[str], repl: str) -> str:
    """
    The function is somewhat similar to the regular 'text'.replace(...) function, but for multiple symbols.

    Note:
        Interesting comparison will be to see the str.maketrans({}), which is valid only for single char replacements |

    Args:
        text: text which should be splitted
        old: iterable of all relevant separators
        repl: replacement for the old strings

    Returns:
        List with of the splitted characters
    """
    pattern = re.compile("|".join(re.escape(sep) for sep in set(old)))
    return pattern.sub(repl, text)


def find_pattern(path: Path, pattern: Pattern[bytes]) -> Iterator[Any]:
    """
    Notes:
        The pattern has to be of type bytes b'...', because the mapped file will be read in bytes.

    Advantages of the strategy:
        * low memory usage (maps the file directly into memory), efficient for large files
        * fast searching, the regex operates directly on the memory-mapped object(buffer-like)
        * avoids loading the entire file into string
        * lazy yield
    """
    with open(path, "rb") as file:
        with mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            yield from pattern.finditer(mmap_obj)


def is_fuzzy_match(query: str, text: str, expected_ratio: float = 0.5) -> bool:
    """
    Check whether a query matches a text using substring or fuzzy matching.

    A direct substring match always returns True. Otherwise, the
    similarity ratio must be greater than expected_ratio.
    """
    query = query.lower()
    text = text.lower()

    # direct substring = always good
    if query in text:
        return True

    # fuzzy similarity
    ratio = SequenceMatcher(None, query, text).ratio()

    return ratio > expected_ratio


def is_same_meta_data(first: Path, second: Path) -> bool:
    "Checks only if the main meta-data (size, creation time and update time) are the same"
    return (
        first.stat().st_size == second.stat().st_size
        and first.stat().st_ctime == second.stat().st_ctime
        and first.stat().st_mtime == second.stat().st_mtime
    )


def is_same_file(first: Path, second: Path, chunk_size: int = 8192) -> bool:
    "Goes for the extra mile and checks chunk by chunk if everything ok"
    if not is_same_meta_data(first, second):
        return False

    with open(first, "rb") as f1, open(second, "rb") as f2:
        while True:
            b1 = f1.read(chunk_size)
            b2 = f2.read(chunk_size)
            if b1 != b2:
                return False
            if not b1:  # EOF
                return True
