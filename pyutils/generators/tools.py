import bz2
import fnmatch
import gzip
import os
import re
import time
from io import IOBase
from pathlib import Path
from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
)


__all__ = [
    "OPENERS",
    "gen_find",
    "get_extension",
    "get_opener",
    "gen_open",
    "gen_cat",
    "gen_grep",
    "field_map",
    "follow",
]

# fmt: off
OPENERS = {
    ".gzip" : lambda x : gzip.open(x),
    ".bz2"  : lambda x : bz2.BZ2File(x),
    # tarfile
    # zlib
    # zipfile
}
# fmt: on


def gen_find(filepat: str, top: str) -> Path:
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            yield Path(path) / name


def get_extension(name: str) -> str:
    # NB! No error handling !
    extension = name.rsplit(".")[-1]
    return f".{extension}"


def get_opener(extension: str) -> Callable:
    if func := OPENERS.get(extension):
        return func
    else:
        # fallback: last resort
        return open


def gen_open(filenames: Iterable) -> Any:
    for name in filenames:
        extension = get_extension(name)
        function = get_opener(extension)

        yield function(name)


def gen_cat(sources: Iterable) -> str:
    for src in sources:
        yield from src


def gen_grep(pat: str, lines: Iterable) -> str:
    cpat = re.compile(pat)
    for line in lines:
        if cpat.search(line):
            yield line


def field_map(dictseq: Iterable[dict], name: Hashable, func: Callable) -> dict:
    for subdict in dictseq:
        subdict[name] = func(subdict[name])
        yield subdict


def follow(thefile: IOBase) -> str:
    thefile.seek(0, 2)

    while 1:
        for line in thefile:
            if not line:
                time.sleep(0.1)
                continue
            yield line
