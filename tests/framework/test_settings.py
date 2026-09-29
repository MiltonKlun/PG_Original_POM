import pytest

from config.settings import Settings, check_parallel, eligible, worker_port

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
        ("snapshot", "http://127.0.0.1:8090"),
        ("snapshot", "https://example.com"),
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


def test_snapshot_replays_the_store_origin():
    settings = Settings.resolve("snapshot")
    assert settings.base_url == "https://www.pgoriginal.com"
    assert settings.replays_store
    assert not Settings.resolve("live").replays_store


def test_snapshot_runs_live_safe_tests_that_stay_in_the_browser():
    assert eligible({"live_safe"}, "snapshot")
    assert eligible({"framework"}, "snapshot")
    assert not eligible({"mock_only"}, "snapshot")
    assert not eligible({"live_safe", "needs_network"}, "snapshot")
    assert eligible({"live_safe", "needs_network"}, "live")


@pytest.mark.parametrize(
    "worker,port", [(None, 8090), ("", 8090), ("gw0", 8091), ("gw7", 8098)]
)
def test_each_parallel_worker_gets_its_own_mock_port(worker, port):
    assert worker_port(worker) == port


def test_unexpected_worker_id_is_rejected():
    with pytest.raises(ValueError):
        worker_port("worker-1")


@pytest.mark.parametrize("workers", [None, 0, "0"])
def test_serial_runs_are_allowed_on_every_target(workers):
    for target in ("mock", "live", "snapshot"):
        check_parallel(target, workers)


@pytest.mark.parametrize("workers", [2, "auto", "logical"])
def test_live_runs_cannot_be_parallel(workers):
    check_parallel("mock", workers)
    check_parallel("snapshot", workers)
    with pytest.raises(ValueError, match="serial"):
        check_parallel("live", workers)
