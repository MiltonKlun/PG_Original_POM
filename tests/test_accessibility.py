"""Automated WCAG 2.1 A/AA scans (axe-core), read-only, on both targets."""

import pytest
from playwright.sync_api import expect
from config.accessibility import scan

pytestmark = [pytest.mark.a11y, pytest.mark.live_safe]


def report(violations):
    return "\n".join(str(v) for v in violations)


@pytest.mark.parametrize(
    "opened_page", ["home", "shop", "product", "login", "contact"], indirect=True
)
def test_page_meets_wcag_aa(opened_page):
    opened_page.wait_for_load()
    violations = scan(opened_page.page)
    assert not violations, report(violations)


@pytest.mark.parametrize(
    "panel",
    [
        "search",
        "menu",
        pytest.param(
            "cart",
            marks=pytest.mark.live_defect(
                "DEF-07: the open cart drawer is a scrollable region that "
                "keyboard users can't focus (axe scrollable-region-focusable)"
            ),
        ),
    ],
)
def test_open_panel_meets_wcag_aa(home_page, panel):
    home_page.open().disclosure(panel).open_with_keyboard()
    violations = scan(home_page.page)
    assert not violations, report(violations)


@pytest.mark.live_defect(
    "DEF-03: login fields are named only by placeholders; their visible "
    "labels aren't associated with the inputs"
)
def test_login_fields_have_associated_labels(login_page):
    login_page.open()
    expect(login_page.email_by_label).to_have_count(1)
    expect(login_page.password_by_label).to_have_count(1)
