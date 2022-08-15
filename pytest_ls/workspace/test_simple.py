import pytest


@pytest.fixture
def foo_in_file() -> bool:
    return True


@pytest.fixture
def fuzz_in_file() -> bool:
    return True


def test_autocomplete():
    pass
