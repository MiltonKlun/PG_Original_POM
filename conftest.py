"""Configuration and target enforcement; safe during offline collection."""

import os
from collections.abc import Iterator

import pytest

from config.reporting import RunReport
from config.settings import Settings, check_parallel, eligible, worker_port

SETTINGS = pytest.StashKey[Settings]()
RUN_REPORT = "pg-run-report"


def run_report_blocked(config: pytest.Config) -> bool:
    return config.pluginmanager.is_blocked(RUN_REPORT)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--seed", type=int, default=1729, help="Synthetic data seed")
    parser.addoption("--run-id", default=None, help="Unique evidence run ID")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    # pytest-xdist workers get their own mock port and write evidence into the
    # controller's run directory; only the controller writes reports.
    workerinput = getattr(config, "workerinput", None)
    try:
        settings = Settings.resolve(
            os.environ.get("TARGET", "mock"),
            config.getoption("base_url"),
            config.getoption("seed"),
            mock_port=worker_port(os.environ.get("PYTEST_XDIST_WORKER")),
        )
        if workerinput is None:
            check_parallel(settings.target, config.getoption("numprocesses", None))
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    config.stash[SETTINGS] = settings
    if workerinput is not None:
        if "pg_output" in workerinput:
            config.option.output = workerinput["pg_output"]
        if "pg_log_stem" in workerinput and not config.option.log_file:
            config.option.log_file = (
                f"{workerinput['pg_log_stem']}-{workerinput['workerid']}.log"
            )
    # `-p no:pg-run-report` (e.g. in git hooks) skips report files entirely.
    elif not (config.option.collectonly or run_report_blocked(config)):
        config.pluginmanager.register(
            RunReport(config, config.stash[SETTINGS]), RUN_REPORT
        )


def pytest_report_header(config: pytest.Config) -> str:
    settings = config.stash[SETTINGS]
    return (
        f"target={settings.target} base_url={settings.base_url} "
        f"seed={settings.seed} (mock results do not verify production)"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        try:
            allowed = eligible(
                {m.name for m in item.iter_markers()}, config.stash[SETTINGS].target
            )
        except ValueError as exc:
            raise pytest.UsageError(f"{item.nodeid}: {exc}") from exc
        (selected if allowed else deselected).append(item)
        defect = item.get_closest_marker("live_defect")
        if defect and config.stash[SETTINGS].target == "live":
            # Strict: once the store fixes the defect, the pass is reported so
            # the marker gets removed. Only assertion failures count as expected.
            item.add_marker(
                pytest.mark.xfail(
                    reason=defect.args[0], strict=True, raises=AssertionError
                )
            )
    items[:] = selected
    config.hook.pytest_deselected(items=deselected)


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return pytestconfig.stash[SETTINGS]


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> Iterator[str]:
    if settings.target == "live":
        yield settings.base_url
    else:
        from scripts.serve_mock import mock_target

        with mock_target(settings) as url:
            yield url
