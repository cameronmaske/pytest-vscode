import argparse

from pytest_ls.server import create_server
from pytest_ls.config import log


def add_arguments(parser):
    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=2087, help="Bind to this port")
    parser.add_argument("--cwd", default=None, help="The root directory of pytest")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    log.info(f"Starting server {args}")
    server = create_server(cwd=args.cwd)

    if args.tcp:
        server.start_tcp(args.host, args.port)
    else:
        server.start_io()


if __name__ == "__main__":
    main()
