"""Keyboard operation of the header panels, read-only, on both targets.

The simulation is the accessible reference; gaps on the live store are
known defects, reported as strict expected failures there.
"""

import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.a11y, pytest.mark.live_safe]

NAMED_CLOSE = pytest.mark.live_defect(
    "DEF-04: the search, menu and cart close controls have no accessible "
    "name, and the menu and cart ones can't be focused from the keyboard"
)
ESCAPE = pytest.mark.live_defect("DEF-05: Escape doesn't close header panels")
FOCUS = pytest.mark.live_defect(
    "DEF-06: opening the menu or cart leaves focus on the trigger, behind the "
    "overlay; reaching the open cart took 143 Tab presses"
)


@pytest.mark.parametrize(
    "panel",
    ["search", pytest.param("menu", marks=FOCUS), pytest.param("cart", marks=FOCUS)],
)
def test_opening_a_panel_moves_focus_into_it(home_page, panel):
    disclosure = home_page.open().disclosure(panel)
    disclosure.open_with_keyboard()
    expect(disclosure.focus_inside).to_have_count(1)


@pytest.mark.parametrize(
    "panel", [pytest.param(name, marks=ESCAPE) for name in ("search", "menu", "cart")]
)
def test_escape_closes_panel_and_returns_focus(home_page, panel):
    disclosure = home_page.open().disclosure(panel)
    disclosure.open_with_keyboard()
    disclosure.close_with_escape()
    expect(disclosure.panel).to_be_hidden()
    expect(disclosure.trigger).to_be_focused()


@pytest.mark.parametrize(
    "panel",
    [pytest.param(name, marks=NAMED_CLOSE) for name in ("search", "menu", "cart")],
)
def test_close_control_is_named_and_focusable(home_page, panel):
    disclosure = home_page.open().disclosure(panel)
    disclosure.open_with_keyboard()
    expect(disclosure.close_control).to_have_accessible_name(re.compile(r"\S"))
    disclosure.close_control.focus()
    expect(disclosure.close_control).to_be_focused()
