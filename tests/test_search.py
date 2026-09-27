import pytest
from playwright.sync_api import expect
from config.test_data import load_data


@pytest.mark.live_safe
def test_search_results(home_page, shop_page, catalog_name):
    home_page.open()
    home_page.navbar.open_search()
    home_page.search.search(catalog_name)
    expect(shop_page.product_names).to_contain_text([catalog_name])


@pytest.mark.live_safe
def test_search_empty(home_page, shop_page):
    home_page.open()
    home_page.navbar.open_search()
    home_page.search.search("zzqaimpossible987654")
    expect(shop_page.empty_results).to_be_visible()
    expect(shop_page.cards).to_have_count(0)


@pytest.mark.mock_only
@pytest.mark.parametrize("case", load_data()["search_cases"], ids=lambda c: c["id"])
def test_search_filters_catalog(home_page, shop_page, case):
    # Exact result set: matches must appear and non-matching products must not.
    home_page.open()
    home_page.navbar.open_search()
    home_page.search.search(case["term"])
    expect(shop_page.cards).to_have_count(len(case["expected"]))
    names = [name.strip() for name in shop_page.product_names.all_inner_texts()]
    assert sorted(names) == case["expected"]
