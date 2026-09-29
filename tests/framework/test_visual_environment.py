"""The visual reference environment must be the same everywhere it is used."""

import re
from pathlib import Path

import pytest

from config.visual import REFERENCE_IMAGE
from scripts.visual import command

pytestmark = pytest.mark.framework

ROOT = Path(__file__).resolve().parents[2]


def test_ci_renders_screenshots_in_the_reference_image():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert f"image: {REFERENCE_IMAGE}" in workflow


def test_reference_image_matches_the_pinned_playwright():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pinned = re.search(r"^playwright==(\S+)$", requirements, re.MULTILINE)
    assert pinned is not None
    assert f":v{pinned[1]}-" in REFERENCE_IMAGE
    assert "@sha256:" in REFERENCE_IMAGE


def test_local_runner_compares_or_updates_in_the_reference_image():
    compare, update = command(update=False), command(update=True)
    assert REFERENCE_IMAGE in compare
    assert "--visual" in compare[-1]
    assert "--update-baselines" not in compare[-1]
    assert "--update-baselines" in update[-1]
