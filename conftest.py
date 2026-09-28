"""Configuration and target enforcement; safe during offline collection."""

import os
from collections.abc import Iterator

import pytest
from config.settings import Settings, eligible
from config.reporting import RunReport

SETTINGS = pytest.StashKey[Settings]()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--seed", type=int, default=1729, help="Synthetic data seed")
    parser.addoption("--run-id", default=None, help="Unique evidence run ID")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    try:
        config.stash[SETTINGS] = Settings.resolve(
            os.environ.get("TARGET", "mock"),
            config.getoption("base_url"),
            config.getoption("seed"),
        )
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    if not config.option.collectonly:
        config.pluginmanager.register(
            RunReport(config, config.stash[SETTINGS]), "pg-run-report"
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
