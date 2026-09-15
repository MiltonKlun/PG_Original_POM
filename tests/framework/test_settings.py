import pytest
from config.settings import Settings, eligible

pytestmark = pytest.mark.framework


def test_default_is_local():
    assert Settings.resolve().base_url == "http://127.0.0.1:8090"


@pytest.mark.parametrize(
    "target,url",
    [
        ("typo", None),
        ("mock", "https://www.pgoriginal.com"),
        ("live", "http://www.pgoriginal.com"),
        ("live", "https://www.pgoriginal.com.evil.test"),
        ("mock", "http://user:password@localhost:8090"),
        ("mock", "http://localhost:8090/path"),
        ("mock", "http://localhost:8090?q=1"),
        ("mock", "http://localhost:8090#fragment"),
        ("mock", "http://localhost:bad"),
        ("mock", ""),
    ],
)
def test_invalid_configuration_fails(target, url):
    with pytest.raises(ValueError):
        Settings.resolve(target, url)


def test_explicit_local_server_and_seed():
    settings = Settings.resolve("mock", "http://localhost:8765/", 123)
    assert settings.external_server
    assert settings.base_url == "http://localhost:8765"
    assert settings.seed == 123


def test_live_enforcement():
    assert eligible({"live_safe", "smoke"}, "live")
    assert eligible({"framework"}, "live")
    assert not eligible({"auth", "mock_only"}, "live")
    assert not eligible(set(), "live")
    assert eligible({"mock_only"}, "mock")
    with pytest.raises(ValueError, match="both"):
        eligible({"live_safe", "mock_only"}, "mock")
