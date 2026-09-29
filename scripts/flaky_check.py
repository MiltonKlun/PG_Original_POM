"""Detect flaky tests: run the mock suite several times and compare outcomes.

Nothing is retried or hidden. A test whose outcome differs between runs is
flaky; a test that fails in every run is reported as consistently failing.
Either makes the check exit non-zero.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASSING = {"passed", "xfailed", "skipped"}


def load_outcomes(summary_path: Path) -> dict[str, str]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return {node: record["status"] for node, record in summary["tests"].items()}


def compare(runs: list[dict[str, str]]) -> tuple[dict[str, list[str]], list[str]]:
    """Return (flaky tests with their per-run outcomes, consistently failing)."""
    if not runs:
        raise ValueError("No runs to compare")
    nodes = sorted(set().union(*runs))
    history = {node: [run.get(node, "missing") for run in runs] for node in nodes}
    flaky = {node: seen for node, seen in history.items() if len(set(seen)) > 1}
    failing = [
        node
        for node, seen in history.items()
        if node not in flaky and seen[0] not in PASSING
    ]
    return flaky, failing


def render_markdown(
    runs: int, total: int, flaky: dict[str, list[str]], failing: list[str]
) -> str:
    lines = [
        "## Flaky test check",
        "",
        f"{runs} runs of {total} tests: **{len(flaky)} flaky**, "
        f"**{len(failing)} failing in every run**.",
        "",
    ]
    if flaky:
        lines += ["| Test | Outcomes per run |", "|---|---|"]
        lines += [f"| `{node}` | {', '.join(seen)} |" for node, seen in flaky.items()]
        lines.append("")
    if failing:
        lines += ["Failing in every run:", ""]
        lines += [f"- `{node}`" for node in failing]
        lines.append("")
    return "\n".join(lines)


def run_once(run_id: str, workers: str, selection: str) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-m",
            selection,
            "-q",
            "-p",
            "no:cacheprovider",
            "-n",
            workers,
            "--run-id",
            run_id,
        ],
        cwd=ROOT,
        env={**os.environ, "TARGET": "mock"},
        check=False,  # Failures are data here; the comparison decides.
    )
    summary = ROOT / "reports" / run_id / "summary.json"
    if not summary.exists():
        raise RuntimeError(f"Run {run_id} produced no summary; the run did not finish")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--workers", default="auto")
    parser.add_argument("-m", "--selection", default="not framework")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.runs < 2:
        parser.error("--runs must be at least 2 to compare outcomes")

    stamp = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    runs = [
        load_outcomes(run_once(f"flaky-{stamp}-{i}", args.workers, args.selection))
        for i in range(1, args.runs + 1)
    ]
    flaky, failing = compare(runs)
    total = len(set().union(*runs))
    markdown = render_markdown(args.runs, total, flaky, failing)
    output = args.output or ROOT / "reports" / f"flaky-{stamp}"
    output.mkdir(parents=True, exist_ok=True)
    (output / "flaky.md").write_text(markdown, encoding="utf-8")
    (output / "flaky.json").write_text(
        json.dumps({"runs": args.runs, "flaky": flaky, "failing": failing}, indent=2),
        encoding="utf-8",
    )
    print(markdown)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with Path(step_summary).open("a", encoding="utf-8") as stream:
            stream.write(markdown)
    return 1 if flaky or failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
