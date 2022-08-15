import argparse
from loguru import logger
import os
import sys
from pygls.lsp.methods import (
    HOVER,
    COMPLETION,
    SET_TRACE_NOTIFICATION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    INITIALIZED,
    COMPLETION_ITEM_RESOLVE,
    TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS,
)
from pygls.lsp.types.general_messages import InitializedParams
from typing import Optional
from pygls.lsp.types import (
    ConfigurationItem,
    ConfigurationParams,
    Diagnostic,
    DiagnosticSeverity,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    Hover,
    MarkupContent,
    Position,
    Range,
    Range,
    TextDocumentPositionParams,
)
from pygls.lsp.types import (
    CompletionList,
    CompletionParams,
    CompletionOptions,
    CompletionItem,
)


from _pytest.config import get_config, _prepareconfig
from pathlib import Path
from _pytest.config import Config
import inspect


from _pytest.compat import getlocation

from typing import Set, Tuple
from _pytest.main import wrap_session
from _pytest.python import showfixtures, Session, _pretty_fixture_path


def find_fixtures(config: Config, session: Session):
    import _pytest.config

    session.perform_collect()
    curdir = Path.cwd()
    tw = _pytest.config.create_terminal_writer(config)
    verbose = config.getvalue("verbose")
    print(config.rootpath)
    print("here")

    fm = session._fixturemanager

    available = []
    seen: Set[Tuple[str, str]] = set()

    for argname, fixturedefs in fm._arg2fixturedefs.items():
        assert fixturedefs is not None
        if not fixturedefs:
            continue
        for fixturedef in fixturedefs:
            loc = getlocation(fixturedef.func, str(curdir))
            if (fixturedef.argname, loc) in seen:
                continue
            seen.add((fixturedef.argname, loc))
            doc = inspect.getdoc(fixturedef.func)
            available.append(
                (
                    len(fixturedef.baseid),
                    fixturedef.func.__module__,
                    _pretty_fixture_path(fixturedef.func),
                    fixturedef.argname,
                    fixturedef,
                    doc,
                )
            )

    available.sort()
    return available


def list_fixtures():
    config = get_config()
    config.parse([])
    fixtures = wrap_session(config, find_fixtures)
    print(fixtures)


# HACK: Needed for prod where we use user's installed python.
# sys.path.append(os.path.join(os.getcwd(), 'venv', 'lib', 'python3.8', 'site-packages'))

from pygls.server import LanguageServer

server = LanguageServer()


@server.feature(HOVER)
def hover(ls, params: TextDocumentPositionParams) -> Optional[Hover]:
    logger.info("hover")


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    logger.info("did_change")


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    logger.info(params.text_document.text)
    logger.info(ls.workspace.root_path)
    logger.info(list(ls.workspace.documents.values())[0].source)

    logger.info(text_doc.source)
    with open(text_doc.path, mode="r", encoding="utf-8") as doc_file:
        logger.info(doc_file.read())
    logger.info(text_doc.source)
    logger.info(f"did_open {text_doc}")
    list_fixtures()


@server.feature(INITIALIZED)
def init(ls, params: Optional[InitializedParams]):
    logger.info("init")


@server.feature(
    COMPLETION,
    CompletionOptions(
        trigger_characters=[">", ".", ":", "`", "<", "/"], resolve_provider=True
    ),
)
def on_completion(ls: LanguageServer, params: CompletionParams):
    logger.info(ls)
    logger.info(params.dict())
    logger.info("on_completion")
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    pos = params.position
    # breakpoint()
    logger.info(doc.lines)
    line = doc.lines[pos.line]
    logger.info(line)

    return CompletionList(is_incomplete=False, items=[])


@server.feature(COMPLETION_ITEM_RESOLVE)
def on_completion_resolve(ls, item: CompletionItem) -> CompletionItem:
    pass


# logging.basicConfig(filename="pygls.log", level=logging.DEBUG, filemode="w")


def add_arguments(parser):
    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=2087, help="Bind to this port")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    logger.info(f"Starting server {args}")
    if args.tcp:
        server.start_tcp(args.host, args.port)
    else:
        server.start_io()


if __name__ == "__main__":
    main()
