"""Per-run artifacts and a target-specific summary, without altering outcomes."""

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from uuid import uuid4

import pytest
from pytest_metadata.plugin import metadata_key


def revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip() + ("+working-tree" if dirty.stdout else "")
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


class RunReport:
    def __init__(self, config, settings):
        self.config = config
        self.settings = settings
        self.started = monotonic()
        self.records = {}
        self.deselected = 0
        self.collection_errors = 0
        root = Path(config.rootpath)
        browsers = config.getoption("browser") or ["chromium"]
        run_id = config.getoption("run_id") or (
            f"{settings.target}-{'-'.join(browsers)}-"
            f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
        )
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
            raise pytest.UsageError(
                "--run-id must be 1-100 letters, digits, '_' or '-'"
            )
        self.directory = root / "reports" / run_id
        # Explicit run IDs are one-use: do not overwrite evidence accidentally.
        if self.directory.exists():
            raise pytest.UsageError(f"Run directory already exists: {self.directory}")
        self.directory.mkdir(parents=True)
        if not config.option.xmlpath:
            config.option.xmlpath = str(self.directory / "results.xml")
        if not config.option.htmlpath:
            config.option.htmlpath = str(self.directory / "report.html")
        config.option.self_contained_html = True
        if config.option.output == "test-results":
            config.option.output = str(root / "test-results" / run_id)
        if not config.option.log_file:
            log = root / "logs" / f"{run_id}.log"
            log.parent.mkdir(exist_ok=True)
            config.option.log_file = str(log)
        self.metadata = {
            "run_id": run_id,
            "target": settings.target,
            "base_url": settings.base_url,
            "browser": browsers,
            "device": config.getoption("device"),
            "seed": settings.seed,
            "revision": revision(root),
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "browser_artifacts": str(Path(config.option.output)),
            "junit": config.option.xmlpath,
            "html": config.option.htmlpath,
        }

    def pytest_sessionstart(self, session):
        session.config.stash[metadata_key].update(self.metadata)

    def pytest_deselected(self, items):
        self.deselected += len(items)

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors += 1

    def pytest_runtest_logreport(self, report):
        result = self.records.setdefault(
            report.nodeid, {"status": "passed", "duration": 0}
        )
        result["duration"] += report.duration
        if report.failed:
            result["status"] = "error" if report.when != "call" else "failed"
        elif report.skipped and result["status"] == "passed":
            result["status"] = "xfailed" if hasattr(report, "wasxfail") else "skipped"
        elif hasattr(report, "wasxfail") and report.passed:
            result["status"] = "xpassed"

    def pytest_sessionfinish(self, session, exitstatus):
        counts = dict.fromkeys(
            ["passed", "failed", "error", "skipped", "xfailed", "xpassed"], 0
        )
        counts.update(Counter(record["status"] for record in self.records.values()))
        summary = {
            **self.metadata,
            "exit_code": int(exitstatus),
            "counts": counts,
            "deselected": self.deselected,
            "collection_errors": self.collection_errors,
            "duration_seconds": round(monotonic() - self.started, 3),
            "tests": self.records,
        }
        (self.directory / "summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_line(f"Run summary: {self.directory / 'summary.json'}")

    def pytest_html_report_title(self, report):
        report.title = f"PG Original | {self.settings.target} | QA results"
