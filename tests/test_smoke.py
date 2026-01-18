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
    # Expect the search input to be visible.
    # Note: There might be multiple .js-search-input elements (desktop/mobile).
    # We wait for *any* of them to be visible, or refine the selector.
    # Using specific filter for visibility if possible, or usually just increasing timeout helps if it's animation.
    # Given the error "resolved to 2 elements", we should be specific.
    # Let's try matching the one that becomes visible.
    page_obj.wait_for_selector(".js-search-input >> visible=true", state="visible", timeout=15000)
    assert home.is_visible(".js-search-input"), "Search input not visible"
