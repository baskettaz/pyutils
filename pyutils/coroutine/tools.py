import re
import time
from dataclasses import dataclass
from io import IOBase
from typing import (
    Any,
    Callable,
    Coroutine,
    Iterable,
)

from .generics import coroutine

__all__ = [
    "grep",
    "follow",
    "printer",
    "func_filter",
    "filter_on_field",
    "broadcast"
]


@coroutine
def grep(pattern: str, target: Coroutine) -> None:
    cpat = re.compile(pattern)
    try:
        while 1:
            line = yield
            if cpat.search(line):
                target.send(line)
    except GeneratorExit:
        pass


@dataclass
class GrepHandler:
    """
    OO-Analogy for the grep-coroutine
    """

    pattern: str
    target: Coroutine

    def __post_init__(self):
        self.pattern = re.compile(self.pattern)

    def send(self, line):
        if self.pattern.search(line):
            self.target.send(line)


def follow(thefile: IOBase, target: Coroutine) -> None:
    thefile.seek(0, 2)

    while 1:
        for line in thefile:
            if not line:
                time.sleep(0.1)
                continue
            target.send(line)


@coroutine
def printer():
    while 1:
        line = yield
        print(line)


@coroutine
def func_filter(func: Callable, target: Coroutine) -> None:
    while 1:
        item = yield
        target.send(func(item))


@coroutine
def filter_on_field(key: str, value: Any, target: Coroutine) -> None:
    while 1:
        fields_dict = yield
        if fields_dict.get(key) == value:
            target.send(fields_dict)


@coroutine
def broadcast(targets: Iterable) -> None:
    while 1:
        item = yield
        for target in targets:
            target.send(item)


if __name__ == "__main__":
    f = open("test.txt", "r")

    broadcaster = lambda: broadcast(
        [
            grep("python", printer()),
            grep("ply", printer()),
            grep("swig", printer()),
        ]
    )

    follow(f, broadcaster())
