import re
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.smoke, pytest.mark.live_safe]


def test_home_page_load(home_page):
    home_page.open()
    expect(home_page.page).to_have_title(re.compile("PG Original", re.I))
    expect(home_page.header).to_be_visible()
    expect(home_page.footer).to_be_visible()


def test_search_modal_opens(home_page):
    home_page.open()
    home_page.navbar.open_search()
    expect(home_page.search.input).to_be_visible()
    expect(home_page.search.input).to_be_focused()
    home_page.search.close()
