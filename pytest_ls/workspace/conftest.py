import pytest


@pytest.fixture
def foo_in_conftest() -> str:
    return "foo"
