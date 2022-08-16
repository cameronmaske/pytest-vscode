from pytest_ls.parser import should_autocomplete, is_test_file

import pytest


@pytest.mark.parametrize(
    "row,col,expected",
    [
        (14, 23, (True, "test_autocomplete")),
        (19, 18, (True, "TestAutocomplete.test_foo")),
        (10, 18, (True, "fuzz_in_file")),
        (10, 5, (False, None)),
        (21, 1, (False, None)),
        (1, 1, (False, None)),
    ],
)
def test_should_autocomplete(row, col, expected, file_contents):
    assert should_autocomplete(row, col, file_contents("test_simple.py")) == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("test_foo.py", True),
        ("foo_test.py", False),
        ("main.py", False),
        ("conftest.py", True),
    ],
)
def test_is_file__default_glob(filename, expected):
    assert is_test_file(filename) == expected


@pytest.mark.parametrize(
    "filename, file_globs, expected",
    [
        ("test_foo.py", ["*_check.py"], False),
        ("foo_check.py", ["*_check.py"], True),
        ("foo_check.py", ["test_*.py", "*_check.py"], True),
        ("main.py", ["test_*.py", "*_check.py"], False),
        ("conftest.py", ["*_check.py"], True),
    ],
)
def test_is_file__with_file_glob(filename, file_globs, expected):
    assert is_test_file(filename, file_globs) == expected
