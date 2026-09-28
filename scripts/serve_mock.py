"""Serve the same static routes locally and in nginx; no external dependencies."""

import argparse
import os
import socket
from collections.abc import Iterator
from contextlib import contextmanager
from email.message import Message
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from threading import Thread, Event
from time import monotonic
from typing import IO, Any, BinaryIO, Self
from urllib.error import URLError
from urllib.parse import unquote, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request

from config.settings import Settings

ROOT = Path(__file__).resolve().parents[1] / "mock_site"
IDENTITY = "pgoriginal-mock-v1"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message,
        newurl: str,
    ) -> Request | None:
        return None


# Same public surface as the nginx image (see mock_site/Dockerfile COPY lines).
PUBLIC_FILES = {"index.html", "app.js", "style.css", "catalog.json", "__health"}
PUBLIC_DIRS = {"productos", "contacto", "account", "search"}


def is_public(url_path: str) -> bool:
    parts = [part for part in unquote(urlsplit(url_path).path).split("/") if part]
    if not parts:
        return True
    if parts[0] in PUBLIC_DIRS:
        return True
    return len(parts) == 1 and parts[0] in PUBLIC_FILES


class Handler(SimpleHTTPRequestHandler):
    # Keep-alive, as nginx does: HTTP/1.0 opens a socket per request, and on
    # Windows the resulting TIME_WAIT churn surfaced as ERR_NO_BUFFER_SPACE.
    protocol_version = "HTTP/1.1"
    timeout = 5  # Idle keep-alive connections close instead of waiting forever.

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Browser diagnostics record failed requests; no raw request logging.

    def send_head(self) -> BytesIO | BinaryIO | None:
        # Contract, Dockerfile and server config are repository files, not site.
        if not is_public(self.path):
            self.send_error(404)
            return None
        return super().send_head()

    def list_directory(self, path: str | os.PathLike[str]) -> BytesIO | None:
        self.send_error(404)  # nginx refuses listings too (autoindex off).
        return None


class LocalHTTPServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR permits competing listeners; require ownership.
    allow_reuse_address = os.name != "nt"

    def server_bind(self) -> None:
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class MockServer:
    # Set when the context is entered.
    server: LocalHTTPServer
    thread: Thread
    url: str

    def __init__(
        self, host: str = "127.0.0.1", port: int = 8090, root: Path = ROOT
    ) -> None:
        self.host, self.port, self.root = host, port, root

    def __enter__(self) -> Self:
        try:
            self.server = LocalHTTPServer(
                (self.host, self.port), partial(Handler, directory=str(self.root))
            )
        except OSError as exc:
            raise RuntimeError(
                f"Cannot start mock on {self.host}:{self.port}; "
                "port occupied or unavailable"
            ) from exc
        self.url = f"http://{self.host}:{self.server.server_port}"
        self.thread = Thread(
            target=self.server.serve_forever, daemon=True, name="pgoriginal-mock"
        )
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError("Mock server thread did not stop")


def verify_mock(url: str, timeout: float = 30) -> None:
    deadline = monotonic() + timeout
    opener = build_opener(NoRedirect)
    last_error = None
    while monotonic() < deadline:
        try:
            with opener.open(url + "/__health", timeout=min(1, timeout)) as response:
                identity = response.read(100).decode().strip()
            if identity != IDENTITY:
                raise RuntimeError(
                    "Port serves another application; mock identity mismatch"
                )
            return
        except (URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            Event().wait(min(0.1, max(0, deadline - monotonic())))
    raise RuntimeError(f"Mock readiness timed out at {url}/__health: {last_error}")


@contextmanager
def mock_target(settings: Settings) -> Iterator[str]:
    if settings.external_server:
        verify_mock(settings.base_url)
        yield settings.base_url
    else:
        parts = urlsplit(settings.base_url)
        host = parts.hostname or "127.0.0.1"  # Settings guarantees a loopback host.
        with MockServer(host, parts.port or 80) as server:
            verify_mock(server.url)
            yield server.url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host", default="127.0.0.1", choices=["127.0.0.1", "localhost"]
    )
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args()
    with MockServer(args.host, args.port) as server:
        print(f"PG Original mock: {server.url}", flush=True)
        try:
            Event().wait()
        except KeyboardInterrupt:
            pass  # Exiting the context closes only our server.


if __name__ == "__main__":
    main()
