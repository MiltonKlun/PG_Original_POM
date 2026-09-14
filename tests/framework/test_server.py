from urllib.request import urlopen
from urllib.error import HTTPError
import pytest
from scripts.serve_mock import MockServer, verify_mock, mock_target
from config.settings import Settings

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
        with pytest.raises(RuntimeError, match="occupied"):
            with MockServer(port=other.server.server_port):
                pass


def test_cleanup_on_failure():
    with pytest.raises(ValueError):
        with MockServer(port=0) as server:
            raise ValueError("test failed")
    assert not server.thread.is_alive()
