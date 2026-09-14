import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.live_safe]


def test_search_results(home_page, shop_page, catalog_name):
    home_page.open()
    home_page.navbar.open_search()
    home_page.search.search(catalog_name)
    expect(shop_page.product_names).to_contain_text([catalog_name])


def test_search_empty(home_page, shop_page):
    home_page.open()
    home_page.navbar.open_search()
    home_page.search.search("zzqaimpossible987654")
    expect(shop_page.empty_results).to_be_visible()
    expect(shop_page.cards).to_have_count(0)
