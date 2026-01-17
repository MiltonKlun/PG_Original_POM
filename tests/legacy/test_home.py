from pages.home_page import HomePage


def test_home_page_loads_successfully(home_page: HomePage):
    """
    Verify that the home page loads and displays the expected title.
    """
    home_page.navigate()
    assert home_page.is_loaded(), "Home page should be loaded with correct title"
    assert home_page.navbar._search_link.is_visible(), "Search link should be visible"
