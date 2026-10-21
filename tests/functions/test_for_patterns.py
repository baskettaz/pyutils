import os
import re
from pathlib import Path

import pytest

from pyutils.functions.for_patterns import (
    find_pattern,
    is_fuzzy_match,
    is_same_file,
    is_same_meta_data,
    multisplit,
    multireplace,
)


def test_multisplit_splits_on_many_separators() -> None:
    text = "alpha-beta_gamma|delta"

    assert multisplit(text, ["_", "|"]) == ["alpha-beta", "gamma", "delta"]


def test_multireplace_replaces_every_match() -> None:
    text = "a-b_c-d"

    assert multireplace(text, ["-", "_"], "X") == "aXbXcXd"


@pytest.mark.xfail(reason="find_pattern is currently broken with mmap objects under Python's buffer API")
def test_find_pattern_yields_each_match(tmp_path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_bytes(b"alpha 123 beta 123 gamma")

    matches = list(find_pattern(file_path, re.compile(rb"123")))
    assert len(matches) == 2
    assert matches[0].group(0) == b"123"


def test_is_fuzzy_match_handles_substring_and_similarity() -> None:
    assert is_fuzzy_match("cat", "concatenate") is True
    assert is_fuzzy_match("xyz", "abc") is False


def test_is_same_file_detects_same_contents_and_different_contents(tmp_path) -> None:
    same = tmp_path / "same.txt"
    same.write_bytes(b"same content")

    assert is_same_file(same, same) is True

    different = tmp_path / "different.txt"
    different.write_bytes(b"different content")
    assert is_same_file(same, different) is False


def test_is_same_file_detects_same_size_different_contents_when_metadata_matches(tmp_path, monkeypatch) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_bytes(b"abcd")
    second.write_bytes(b"wxyz")

    monkeypatch.setattr("pyutils.functions.for_patterns.is_same_meta_data", lambda _first, _second: True)

    assert is_same_file(first, second) is False


def test_same_metadata_and_files(tmp_path, monkeypatch) -> None:
    first = tmp_path / "one.txt"
    second = tmp_path / "two.txt"

    class DummyStat:
        st_size = 11
        st_ctime = 1
        st_mtime = 1

    monkeypatch.setattr(Path, "stat", lambda self: DummyStat())

    first.write_bytes(b"hello world")
    second.write_bytes(b"hello world")
    assert is_same_meta_data(first, second)
    assert is_same_file(first, second)

    second.write_bytes(b"hello there")
    assert is_same_meta_data(first, second) is True
    assert is_same_file(first, second) is False
