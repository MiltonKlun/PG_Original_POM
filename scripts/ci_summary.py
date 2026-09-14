"""Render existing pytest evidence into a GitHub summary; require actual JUnit."""

import json
import os
import sys
from pathlib import Path
from xml.etree import ElementTree


def render(path: Path) -> str:
    summary = json.loads(path.read_text(encoding="utf-8"))
    junit = ElementTree.parse(summary["junit"])
    cases = len(junit.findall(".//testcase"))
    counts = summary["counts"]
    lines = [
        f"## PG Original: {summary['target']}",
        "",
        f"Revision: `{summary['revision']}`",
        f"Browser: {', '.join(summary['browser'])}; "
        f"device: {summary['device'] or 'desktop'}; seed: {summary['seed']}",
        f"Exit code: {summary['exit_code']}; "
        f"duration: {summary['duration_seconds']}s",
        "",
        "| Result | Count |",
        "|---|---:|",
        *[f"| {name} | {value} |" for name, value in counts.items()],
        f"| deselected | {summary['deselected']} |",
        f"| collection errors | {summary['collection_errors']} |",
        f"| JUnit cases | {cases} |",
        "",
    ]
    if summary["target"] == "mock":
        lines.append("Synthetic local storefront; this does not certify production.")
    else:
        lines.append(
            "Read-only client checks. A failure needs investigation; "
            "a timeout alone is not a confirmed product defect."
        )
    repository = os.environ.get("GITHUB_REPOSITORY")
    run = os.environ.get("GITHUB_RUN_ID")
    if repository and run:
        lines.append(
            f"[Run and downloadable artifacts]"
            f"(https://github.com/{repository}/actions/runs/{run})"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        message = render(Path(sys.argv[1]))
        result = 0
    except (OSError, ValueError, KeyError, IndexError, ElementTree.ParseError) as exc:
        message = f"## Missing or invalid test evidence\n\n{exc}\n"
        result = 1
    print(message)
    destination = os.environ.get("GITHUB_STEP_SUMMARY")
    if destination:
        with Path(destination).open("a", encoding="utf-8") as stream:
            stream.write(message)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
