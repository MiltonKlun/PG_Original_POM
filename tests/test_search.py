import pytest
from playwright.sync_api import expect
from config.test_data import load_data


@pytest.mark.live_safe
def test_search_results(home_page, catalog_name):
    results = home_page.open().search_for(catalog_name)
    expect(results.product_names).to_contain_text([catalog_name])


@pytest.mark.live_safe
def test_search_empty(home_page):
    results = home_page.open().search_for("zzqaimpossible987654")
    expect(results.empty_results).to_be_visible()
    expect(results.cards).to_have_count(0)


@pytest.mark.mock_only
@pytest.mark.parametrize("case", load_data().search_cases, ids=lambda c: c.id)
def test_search_filters_catalog(home_page, case):
    # Exact result set: matches must appear and non-matching products must not.
    results = home_page.open().search_for(case.term)
    expect(results.cards).to_have_count(len(case.expected))
    assert sorted(results.displayed_names()) == list(case.expected)
