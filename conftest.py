"""Configuration and target enforcement; safe during offline collection."""

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import pytest
from config.settings import Settings, eligible

SETTINGS = pytest.StashKey[Settings]()


def pytest_addoption(parser):
    parser.addoption("--seed", type=int, default=1729, help="Synthetic data seed")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    try:
        config.stash[SETTINGS] = Settings.resolve(
            os.environ.get("TARGET", "mock"),
            config.getoption("base_url"),
            config.getoption("seed"),
        )
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    if not config.option.collectonly and not config.option.log_file:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = Path(__file__).parent / "logs" / f"{run_id}-{uuid4().hex[:8]}.log"
        path.parent.mkdir(exist_ok=True)
        config.option.log_file = str(path)


def pytest_report_header(config):
    settings = config.stash[SETTINGS]
    return (
        f"target={settings.target} base_url={settings.base_url} "
        f"seed={settings.seed} (mock results do not verify production)"
    )


def pytest_collection_modifyitems(config, items):
    selected, deselected = [], []
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
def settings(pytestconfig):
    return pytestconfig.stash[SETTINGS]


@pytest.fixture(scope="session")
def base_url(settings):
    if settings.target == "live":
        yield settings.base_url
    else:
        from scripts.serve_mock import mock_target

        with mock_target(settings) as url:
            yield url
