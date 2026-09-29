"""Run the visual checks in the reference container (Playwright's Docker image).

Screenshots depend on the fonts a machine has, so baselines are compared in
one environment only: the image CI uses (config/visual.py). Requires Docker.

    python -m scripts.visual            # compare with the baselines
    python -m scripts.visual --update   # rewrite them for review
"""

import argparse
import shutil
import subprocess
from pathlib import Path

from config.visual import REFERENCE_IMAGE

ROOT = Path(__file__).resolve().parents[1]
# Runs inside the container, which runs as root: evidence and baselines are
# handed back to the owner of the checkout.
INNER = (
    "python -m pip install -q --root-user-action=ignore --disable-pip-version-check"
    " -r requirements.txt"
    " && python -m pytest tests -m visual --visual -p no:cacheprovider{extra};"
    " code=$?; chown -R $(stat -c %u:%g /work) reports test-results logs"
    " tests/visual 2>/dev/null; exit $code"
)


def command(update: bool, docker: str = "docker") -> list[str]:
    extra = " --update-baselines" if update else ""
    return [
        docker,
        "run",
        "--rm",
        "--ipc=host",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "-v",
        f"{ROOT}:/work",
        "-w",
        "/work",
        REFERENCE_IMAGE,
        "bash",
        "-c",
        INNER.format(extra=extra),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--update", action="store_true", help="Rewrite the baselines for review"
    )
    args = parser.parse_args(argv)
    docker = shutil.which("docker")
    if docker is None:
        print("Docker is required to render screenshots in the reference container")
        return 2
    return subprocess.run(command(args.update, docker), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
