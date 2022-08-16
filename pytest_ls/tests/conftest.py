import sys
import pytest
import pytest_lsp
import pygls.uris as uri
from pytest_lsp import ClientServerConfig
import pathlib
import asyncio

ROOT_PATH = pathlib.Path(__file__).parent.parent / "workspace"


@pytest.fixture(scope="session")
def event_loop():
    # We need to redefine the event_loop fixture to match the scope of our
    # client_server fixture.
    #
    # https://github.com/pytest-dev/pytest-asyncio/issues/68#issuecomment-334083751
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def root_path():
    return ROOT_PATH


@pytest.fixture
def path_to_uri(root_path):
    def _(filepath):
        return uri.from_fs_path(str(root_path / filepath))

    return _


@pytest.fixture
def file_contents(root_path):
    def _(filepath):
        with open(str(root_path / filepath), mode="r", encoding="utf-8") as _file:
            return _file.read()

    return _


@pytest_lsp.fixture(
    scope="session",
    config=ClientServerConfig(
        server_command=[sys.executable, "-m", "pytest_ls", "--cwd", ROOT_PATH],
        root_uri=uri.from_fs_path(str(root_path)),
    ),
)
async def client():
    pass
