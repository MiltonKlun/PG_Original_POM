"""Serve the same static routes locally and in nginx; no external dependencies."""

import argparse
import os
import socket
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread, Event
from time import monotonic
from urllib.error import URLError
from urllib.request import build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1] / "mock_site"
IDENTITY = "pgoriginal-mock-v1"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Browser diagnostics record failed requests; no raw request logging.


class LocalHTTPServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR permits competing listeners; require ownership.
    allow_reuse_address = os.name != "nt"

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class MockServer:
    def __init__(self, host="127.0.0.1", port=8090, root=ROOT):
        self.host, self.port, self.root = host, port, root
        self.server = None
        self.thread = None

    def __enter__(self):
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

    def __exit__(self, *exc):
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
def mock_target(settings):
    if settings.external_server:
        verify_mock(settings.base_url)
        yield settings.base_url
    else:
        from urllib.parse import urlsplit

        parts = urlsplit(settings.base_url)
        with MockServer(parts.hostname, parts.port or 80) as server:
            verify_mock(server.url)
            yield server.url


def main():
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
