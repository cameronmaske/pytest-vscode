import sys
import pytest
import pytest_lsp
import pygls.uris as uri
from pytest_lsp import ClientServerConfig
import pathlib
import asyncio

root_path = pathlib.Path(__file__).parent.parent / "workspace"


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
def path_to_uri():
    def _(filepath):
        return uri.from_fs_path(str(root_path / filepath))

    return _


@pytest_lsp.fixture(
    scope="session",
    config=ClientServerConfig(
        server_command=[sys.executable, "-m", "pytest_ls"],
        root_uri=uri.from_fs_path(str(root_path)),
    ),
)
async def client():
    pass
