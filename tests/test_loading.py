import pytest
from playwright.sync_api import Route, expect

pytestmark = [pytest.mark.smoke, pytest.mark.mock_only]


def test_page_controls_work_before_catalog_loads(page, home_page):
    # Hold the catalog request open: header and consent controls must not
    # depend on product data, or a slow response makes clicks do nothing.
    def hold(route: Route) -> None:
        pass  # Never answered; the request stays pending until teardown.

    page.route("**/catalog.json", hold)
    home_page.open()  # Dismissing the cookie banner must hide it.
    home_page.navbar.open_search()
    expect(home_page.search.input).to_be_visible()
