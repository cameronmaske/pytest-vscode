import pytest


@pytest.fixture
def c() -> int:
    return 1


@pytest.fixture
def a() -> int:
    return 2


def test_foo():
    pass
