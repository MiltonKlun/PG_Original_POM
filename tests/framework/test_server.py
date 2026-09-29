from http.client import HTTPConnection
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from config.settings import Settings
from scripts.serve_mock import (
    PUBLIC_DIRS,
    PUBLIC_FILES,
    ROOT,
    MockServer,
    mock_target,
    verify_mock,
)

pytestmark = pytest.mark.framework


def test_routes_and_cleanup():
    with MockServer(port=0) as server:
        verify_mock(server.url)
        for route in [
            "/",
            "/contacto/",
            "/account/login/",
            "/account/reset/",
            "/productos/qa-remera/",
            "/productos/pg-buzo/",
            "/productos/pg-gorro/",
            "/search/?q=missing",
        ]:
            with urlopen(server.url + route) as response:
                assert response.status == 200
                assert "text/html" in response.headers["Content-Type"]
        with pytest.raises(HTTPError) as error:
            urlopen(server.url + "/not-a-route/")
        assert error.value.code == 404
    assert not server.thread.is_alive()


def test_explicit_reuse_does_not_stop_owner():
    with MockServer(port=0) as owner:
        settings = Settings.resolve("mock", owner.url)
        with mock_target(settings) as url:
            assert url == owner.url
        verify_mock(owner.url)


def test_wrong_application_and_occupied_port(tmp_path):
    (tmp_path / "__health").write_text("another application")
    with MockServer(port=0, root=tmp_path) as other:
        with pytest.raises(RuntimeError, match="identity mismatch"):
            verify_mock(other.url, timeout=1)
        with (
            pytest.raises(RuntimeError, match="occupied"),
            MockServer(port=other.server.server_port),
        ):
            pass


def test_cleanup_on_failure():
    with pytest.raises(ValueError), MockServer(port=0) as server:
        raise ValueError("test failed")
    assert not server.thread.is_alive()


@pytest.mark.parametrize(
    "path",
    [
        "/CONTRACT.md",
        "/Dockerfile",
        "/nginx.conf",
        "/.dockerignore",
        "/account/",
        "/%2e%2e/conftest.py",
    ],
)
def test_repository_files_and_listings_not_served(path):
    with MockServer(port=0) as server:
        with pytest.raises(HTTPError) as error:
            urlopen(server.url + path)
        assert error.value.code == 404


def test_public_surface_matches_docker_image():
    # Both serving modes must expose the same files: parse the image's COPY lines.
    files: set[str] = set()
    dirs: set[str] = set()
    for line in (ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines():
        words = line.split()
        if words[:1] == ["COPY"] and not words[-1].startswith("/"):
            for source in words[1:-1]:
                (dirs if source.endswith("/") else files).add(source.rstrip("/"))
    assert files == PUBLIC_FILES
    assert dirs == PUBLIC_DIRS


def test_connections_are_kept_alive():
    # One socket serves several requests, as nginx does; fewer sockets per run.
    with MockServer(port=0) as server:
        connection = HTTPConnection("127.0.0.1", server.server.server_port, timeout=5)
        for route in ("/app.js", "/catalog.json"):
            connection.request("GET", route)
            response = connection.getresponse()
            response.read()
            assert response.status == 200
            assert response.version == 11
            assert not response.will_close
        connection.close()
