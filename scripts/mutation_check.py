"""Measure how many injected storefront defects the UI suite detects.

Each mutant from tests/mutation/catalog.json is applied to a disposable copy of
the repository, the mock UI suite runs against it, and the mutant counts as
killed only if pytest reports test failures. The unmodified copy must pass
first; otherwise no score is produced.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "tests" / "mutation" / "catalog.json"
COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    ".venv*",
    "venv",
    "reports",
    "test-results",
    "logs",
    "proofs",
    "__pycache__",
    ".pytest_cache",
)
# Evidence flags are dropped: only the pass/fail outcome matters here.
PYTEST_ARGS = [
    "tests",
    "-m",
    "not framework",
    "-q",
    "-rfE",
    "-p",
    "no:cacheprovider",
    "-o",
    "addopts=--strict-markers --strict-config",
]


@dataclass(frozen=True)
class Edit:
    find: str
    replace: str


@dataclass(frozen=True)
class Mutant:
    id: str
    description: str
    file: str
    edits: tuple[Edit, ...]
    killed_by: tuple[str, ...]


@dataclass(frozen=True)
class Outcome:
    id: str
    description: str
    status: str
    failing: tuple[str, ...]
    expected_killer_failed: bool
    duration_seconds: float


def load_catalog(path: Path = CATALOG) -> list[Mutant]:
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))["mutants"]
        mutants = [
            Mutant(
                id=row["id"],
                description=row["description"],
                file=row["file"],
                edits=tuple(Edit(e["find"], e["replace"]) for e in row["edits"]),
                killed_by=tuple(row["killed_by"]),
            )
            for row in rows
        ]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid mutant catalog {path}: {exc}") from exc
    if not mutants:
        raise ValueError(f"Invalid mutant catalog {path}: no mutants")
    ids = [m.id for m in mutants]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Invalid mutant catalog {path}: duplicate IDs")
    for m in mutants:
        if not m.edits or not m.killed_by:
            raise ValueError(f"{m.id}: edits and killed_by must be nonempty")
        if Path(m.file).is_absolute() or ".." in Path(m.file).parts:
            raise ValueError(f"{m.id}: file must be a repository-relative path")
    return mutants


def apply_edits(text: str, edits: tuple[Edit, ...]) -> str:
    # Checkouts may use CRLF (core.autocrlf); snippets are written with LF.
    text = text.replace("\r\n", "\n")
    for edit in edits:
        count = text.count(edit.find)
        if count != 1:
            raise ValueError(
                f"Snippet must occur exactly once, found {count}: {edit.find!r}"
            )
        if edit.find == edit.replace:
            raise ValueError(f"Edit does not change the source: {edit.find!r}")
        text = text.replace(edit.find, edit.replace, 1)
    return text


def classify(returncode: int) -> str:
    # pytest: 0 all passed, 1 tests failed; anything else is not a valid result.
    if returncode == 0:
        return "survived"
    if returncode == 1:
        return "killed"
    raise RuntimeError(f"pytest exited with code {returncode}; result is invalid")


def failing_tests(output: str) -> tuple[str, ...]:
    return tuple(
        line.split()[1]
        for line in output.splitlines()
        if line.startswith(("FAILED ", "ERROR ")) and len(line.split()) > 1
    )


def node_function(node_id: str) -> str:
    return node_id.split("::")[-1].split("[")[0]


def score(outcomes: list[Outcome]) -> float:
    if not outcomes:
        raise ValueError("No mutation outcomes to score")
    killed = sum(o.status == "killed" for o in outcomes)
    return round(100 * killed / len(outcomes), 1)


def render_markdown(outcomes: list[Outcome]) -> str:
    killed = sum(o.status == "killed" for o in outcomes)
    lines = [
        "## Mutation score",
        "",
        f"**{score(outcomes)}%**: {killed} of {len(outcomes)} injected defects "
        "detected by the mock UI suite.",
        "",
        "| Mutant | Injected defect | Result | Failing tests |",
        "|---|---|---|---|",
    ]
    for o in outcomes:
        result = "killed" if o.status == "killed" else "**survived**"
        if o.status == "killed" and not o.expected_killer_failed:
            result += " (unexpected test)"
        failing = ", ".join(sorted({node_function(n) for n in o.failing})) or "-"
        lines.append(f"| {o.id} | {o.description} | {result} | {failing} |")
    return "\n".join(lines) + "\n"


def run_suite(workdir: Path, run_id: str) -> tuple[int, str]:
    env = {**os.environ, "TARGET": "mock"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST_ARGS, "--run-id", run_id],
        cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return proc.returncode, proc.stdout + proc.stderr


def evaluate(mutant: Mutant, workdir: Path) -> Outcome:
    target = workdir / mutant.file
    original = target.read_text(encoding="utf-8")
    started = monotonic()
    try:
        target.write_text(apply_edits(original, mutant.edits), encoding="utf-8")
        returncode, output = run_suite(workdir, f"mutation-{mutant.id.lower()}")
    finally:
        target.write_text(original, encoding="utf-8")
    failing = failing_tests(output)
    return Outcome(
        id=mutant.id,
        description=mutant.description,
        status=classify(returncode),
        failing=failing,
        expected_killer_failed=any(
            node_function(node) in mutant.killed_by for node in failing
        ),
        duration_seconds=round(monotonic() - started, 2),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--only", action="append", help="Mutant ID (repeatable)")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    mutants = load_catalog(args.catalog)
    if args.only:
        unknown = set(args.only) - {m.id for m in mutants}
        if unknown:
            parser.error(f"Unknown mutant IDs: {sorted(unknown)}")
        mutants = [m for m in mutants if m.id in args.only]
    stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    output = args.output or ROOT / "reports" / f"mutation-{stamp}"

    scratch = Path(tempfile.mkdtemp(prefix="pg-mutation-"))
    try:
        workdir = scratch / "repo"
        shutil.copytree(ROOT, workdir, ignore=COPY_IGNORE)
        returncode, log = run_suite(workdir, "mutation-baseline")
        if returncode != 0:
            print(log)
            print("Baseline suite failed; mutation score not computed.")
            return 2
        outcomes = []
        for mutant in mutants:
            outcome = evaluate(mutant, workdir)
            print(f"{outcome.id} {outcome.status} ({outcome.duration_seconds}s)")
            outcomes.append(outcome)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    markdown = render_markdown(outcomes)
    output.mkdir(parents=True, exist_ok=True)
    (output / "mutation.md").write_text(markdown, encoding="utf-8")
    (output / "mutation.json").write_text(
        json.dumps(
            {
                "score": score(outcomes),
                "min_score": args.min_score,
                "outcomes": [asdict(o) for o in outcomes],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(markdown)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as stream:
            stream.write(markdown)
    if score(outcomes) < args.min_score:
        print(f"Mutation score below required {args.min_score}%")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
