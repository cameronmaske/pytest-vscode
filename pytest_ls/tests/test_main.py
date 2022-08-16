import pytest
from pytest_lsp import Client

from pygls.lsp.types import (
    CompletionList,
)
from pathlib import Path
import pygls.uris as Uri


async def completion_request(
    client: Client, test_uri: str, text: str, line: int, column: int = None
) -> CompletionList:
    """_summary_

    Args:
        client (Client): _description_
        test_uri (str): _description_
        text (str): _description_
        line (int): Mirror's vscode (incremented from 1 as opposed as 0)
        column (int, optional): Mirror's vscode (incremented from 1 as opposed as 0)

    Returns:
        CompletionList: _description_
    """
    filepath = Path(Uri.to_fs_path(test_uri))
    extension = filepath.suffix
    lang_mapping = {".py": "python"}
    lang_id = lang_mapping[extension]

    # Open the file and pass contents
    with open(filepath, mode="r", encoding="utf-8") as _file:
        client.notify_did_open(test_uri, lang_id, _file.read())

    response = await client.completion_request(test_uri, line, column)

    client.notify_did_close(test_uri)
    return response


@pytest.mark.asyncio
async def test_completion(client: Client, path_to_uri):
    test_uri = path_to_uri("test_simple.py")

    result = await completion_request(client, test_uri, line=14, column=23, text="fo")

    assert len(result.items) > 0
