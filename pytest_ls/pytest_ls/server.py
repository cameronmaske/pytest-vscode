from typing import Optional

from pygls.lsp.methods import (
    COMPLETION,
    COMPLETION_ITEM_RESOLVE,
    HOVER,
    INITIALIZED,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    InitializeParams,
    Hover,
    TextDocumentPositionParams,
)
from pygls.server import LanguageServer
import pygls.uris as uri
from pytest_ls.config import log

from .brain import Brain


class PytestLanguageServer(LanguageServer):
    def __init__(self, cwd=None):
        log.info("server.init")
        self.brain = Brain(cwd=cwd)
        super().__init__()


def create_server(**kwargs):
    log.info(f"Creating server [{kwargs}]")
    server = PytestLanguageServer(**kwargs)
    configure_server_methods(server)
    return server


def configure_server_methods(server: PytestLanguageServer):
    @server.feature(INITIALIZED)
    def init(ls: PytestLanguageServer, params: InitializeParams):
        log.info(f"init")
        ls.brain.init()

    @server.feature(HOVER)
    def hover(
        ls: PytestLanguageServer, params: TextDocumentPositionParams
    ) -> Optional[Hover]:
        log.info("hover", ls, params)

    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: PytestLanguageServer, params: DidChangeTextDocumentParams):
        log.info("did_change", ls, params)

    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: PytestLanguageServer, params: DidOpenTextDocumentParams):
        log.info("did_open", ls, params)

        document = ls.workspace.get_document(params.text_document.uri)

        with open(document.path, mode="r", encoding="utf-8") as document_file:
            log.info(document_file.read())

    @server.feature(
        COMPLETION,
        CompletionOptions(
            trigger_characters=[">", ".", ":", "`", "<", "/"],
            resolve_provider=True,  # TODO: Figure out trigger_characters
        ),
    )
    def on_completion(
        ls: PytestLanguageServer, params: Optional[CompletionParams] = None
    ) -> CompletionList:
        log.info("on_completion")
        if params:
            file_path = uri.to_fs_path(params.text_document.uri)
            file_contents = ls.workspace.get_document(params.text_document.uri).source
            ls.brain.completions(
                line=params.position.line,
                column=params.position.character,
                file_contents=file_contents,
                file_path=file_path,
            )

        return CompletionList(is_incomplete=False, items=[])

    @server.feature(COMPLETION_ITEM_RESOLVE)
    def on_completion_resolve(
        ls: PytestLanguageServer, item: CompletionItem
    ) -> CompletionItem:
        log.info("on_completion_resolve", ls, item)

    return server
