"""Read-only page health checks that run on both targets."""

import pytest
from config.live_policy import crawl_allowed
from pages.base_page import BasePage
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.shop_page import ShopPage

pytestmark = pytest.mark.live_safe

MAX_LINKS_CHECKED = 25


@pytest.fixture(params=["home", "shop", "product", "contact"])
def opened_page(
    request: pytest.FixtureRequest,
    home_page: HomePage,
    shop_page: ShopPage,
    contact_page: ContactPage,
) -> BasePage:
    if request.param == "product":
        shop_page.open()
        return shop_page.open_product(shop_page.first_product_name())
    pages: dict[str, BasePage] = {
        "home": home_page,
        "shop": shop_page,
        "contact": contact_page,
    }
    return pages[request.param].open()


def test_page_loads_without_errors(opened_page, browser_diagnostics):
    # Third-party failures (e.g. a store app's config) are out of scope here.
    opened_page.wait_for_load()
    assert browser_diagnostics.first_party_failures == []
    assert browser_diagnostics.page_errors == []


def test_home_links_resolve(home_page):
    home_page.open()
    paths = [p for p in home_page.linked_paths() if p and crawl_allowed(p)]
    assert paths, "Home page has no crawlable first-party links"
    # Evenly spaced, deterministic sample keeps live traffic small.
    sample = paths[:: max(1, len(paths) // MAX_LINKS_CHECKED)][:MAX_LINKS_CHECKED]
    broken = []
    for path in sample:
        response = home_page.page.request.get(path, max_redirects=5)
        if response.status >= 400:
            broken.append(f"{response.status} {path}")
    assert not broken, "Broken links:\n" + "\n".join(broken)
