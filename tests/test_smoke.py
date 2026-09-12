import pytest


@pytest.mark.smoke
@pytest.mark.live_safe
def test_home_page_load(page, home_page):
    """Verify the home page loads correctly."""
    home = home_page
    home.open()
    assert home.is_loaded(), "Home page failed to load title"
    assert home.is_visible("header"), "Header is not visible"
    assert home.is_visible("footer"), "Footer is not visible"


@pytest.mark.smoke
@pytest.mark.live_safe
def test_search_modal_opens(page, home_page):
    """Verify search modal can be opened."""
    home = home_page
    home.open()
    home.navbar.open_search()
    page.wait_for_selector(
        ".js-search-input >> visible=true", state="visible", timeout=5000
    )
    assert page.is_visible(
        ".js-search-input >> visible=true"
    ), "Search input not visible"
