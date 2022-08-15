import pytest
from pytest_lsp import Client
from loguru import logger

from pygls.lsp.types import (
    CompletionList,
)
from pathlib import Path
import pygls.uris as Uri


async def completion_request(
    client: Client, test_uri: str, text: str, line: int, column: int = None
) -> CompletionList:
    """
    line: Mirror's vscode (incremented from 1 as opposed as 0)
    column: Mirr's vscode (incremented from 1 as opposed as 0)
    """
    filepath = Path(Uri.to_fs_path(test_uri))
    extension = filepath.suffix
    lang_mapping = {".py": "python"}
    lang_id = lang_mapping[extension]

    # Open the file and pass contents
    with open(filepath, mode="r", encoding="utf-8") as _file:
        print("read")
        client.notify_did_open(test_uri, lang_id, _file.read())

    response = await client.completion_request(test_uri, line - 1, column - 1)

    client.notify_did_close(test_uri)
    return response


@pytest.mark.asyncio
async def test_completion(client: Client, path_to_uri):
    test_uri = path_to_uri("test_simple.py")

    result = await completion_request(client, test_uri, line=14, column=32, text="fo")

    assert len(result.items) > 0
