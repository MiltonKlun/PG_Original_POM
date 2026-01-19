import pytest
from pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_load(page_obj):
    """Verify the home page loads correctly."""
    home = HomePage(page_obj)
    assert home.is_loaded(), "Home page failed to load title"
    assert home.is_visible("header"), "Header is not visible"
    assert home.is_visible("footer"), "Footer is not visible"

@pytest.mark.smoke
def test_search_modal_opens(page_obj):
    """Verify search modal can be opened."""
    home = HomePage(page_obj)
    home.navbar.open_search()
    page_obj.wait_for_selector(".js-search-input >> visible=true", state="visible", timeout=5000)
    assert home.is_visible(".js-search-input"), "Search input not visible"
