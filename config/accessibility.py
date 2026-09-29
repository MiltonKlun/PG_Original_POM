"""Automated accessibility scans with axe-core, served from the local package.

The engine (axe-core, MPL-2.0) ships inside the pinned axe-playwright-python
wheel, so scans never load scripts from a CDN at runtime. Automated rules find
only part of real accessibility problems; keyboard checks in
tests/test_keyboard.py cover what axe can't see.
"""

from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Any

from playwright.sync_api import Page

# WCAG 2.1 levels A and AA; best-practice rules are informational only.
WCAG_TAGS = ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa")


@dataclass(frozen=True)
class Violation:
    rule: str
    impact: str | None
    help: str
    targets: tuple[str, ...]

    def __str__(self) -> str:
        where = ", ".join(self.targets[:3])
        return f"{self.rule} ({self.impact}): {self.help} [{where}]"


@lru_cache(maxsize=1)
def axe_source() -> str:
    return files("axe_playwright_python").joinpath("axe.min.js").read_text("utf-8")


def parse_violations(result: dict[str, Any]) -> list[Violation]:
    return [
        Violation(
            rule=v["id"],
            impact=v.get("impact"),
            help=v["help"],
            targets=tuple(str(node["target"][0]) for node in v["nodes"]),
        )
        for v in result["violations"]
    ]


def scan(page: Page) -> list[Violation]:
    """Run WCAG 2.1 A/AA rules against the page in its current state."""
    page.add_script_tag(content=axe_source())
    result = page.evaluate(
        """tags => axe.run(document, {
            runOnly: {type: 'tag', values: tags},
            resultTypes: ['violations'],
        })""",
        list(WCAG_TAGS),
    )
    return parse_violations(result)
