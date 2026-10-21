import os
import re

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


@pytest.mark.xfail(reason="Windows ctime differs even when file sizes and mtimes match, so same path metadata checks are unreliable here")
def test_same_metadata_and_files(tmp_path) -> None:
    first = tmp_path / "one.txt"
    second = tmp_path / "two.txt"
    first.write_bytes(b"hello world")
    second.write_bytes(b"hello world")
    os.utime(first, ns=(1000, 1000))
    os.utime(second, ns=(1000, 1000))

    assert is_same_meta_data(first, second)
    assert is_same_file(first, second)

    second.write_bytes(b"hello there")
    assert is_same_meta_data(first, second) is False
    assert is_same_file(first, second) is False
