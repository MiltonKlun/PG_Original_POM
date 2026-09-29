import re
import pytest
from playwright.sync_api import expect
from config.money import ars_minor_units, format_ars
from config.test_data import load_data


@pytest.mark.smoke
@pytest.mark.live_safe
def test_shop_product_details(shop_page):
    shop_page.open()
    name = shop_page.first_product_name()
    product = shop_page.open_product(name)
    expect(product.heading).to_have_text(name)
    expect(product.price).to_be_visible()
    assert ars_minor_units(product.price.inner_text()) > 0
    expect(product.add_button).to_be_enabled()


@pytest.mark.shop
@pytest.mark.mock_only
@pytest.mark.parametrize("case", load_data().filter_cases, ids=lambda c: c.id)
def test_filter_and_clear(shop_page, test_data, case):
    page_size = test_data.shop.catalog.page_size
    shop_page.open()
    expect(shop_page.cards).to_have_count(page_size)
    shop_page.apply_filter(case.name, case.value)
    expect(shop_page.cards).to_have_count(len(case.expected))
    assert sorted(shop_page.displayed_names()) == list(case.expected)
    assert all(case.value in values for values in shop_page.displayed_variant_values())
    shop_page.clear_filter()
    expect(shop_page.cards).to_have_count(page_size)


@pytest.mark.shop
@pytest.mark.mock_only
def test_load_more_catalog(shop_page, test_data):
    # Fixture catalog spans two pages; loading more must append, not repeat.
    catalog = test_data.shop.catalog
    shop_page.open()
    expect(shop_page.cards).to_have_count(catalog.page_size)
    shop_page.load_more()
    expect(shop_page.cards).to_have_count(len(catalog.products))
    assert sorted(shop_page.displayed_names()) == list(catalog.products)
    expect(shop_page.page).to_have_url(re.compile(r"[?&]mpage=2\b"))


@pytest.mark.shop
@pytest.mark.mock_only
def test_discounted_variant_shows_compare_price(shop_page, test_data):
    # Leave and return to the promotion so the price must be recalculated.
    shirt = test_data.shop.shirt
    tier = shirt.discounted
    product = shop_page.open().open_product(shirt.name)
    product.select_variant(color=shirt.regular.color)
    product.select_variant(color=tier.color)
    expect(product.price).to_have_text(format_ars(tier.price, short=True))
    assert tier.compare_at is not None
    expect(product.compare_price).to_have_text(format_ars(tier.compare_at, short=True))


@pytest.mark.shop
@pytest.mark.mock_only
def test_regular_variant_price_reaches_cart(shop_page, test_data):
    # Switching away from the promotion updates the price and hides compare-at.
    shirt = test_data.shop.shirt
    tier = shirt.regular
    product = shop_page.open().open_product(shirt.name)
    product.select_variant(size=shirt.default.size, color=tier.color)
    expect(product.price).to_have_text(format_ars(tier.price, short=True))
    expect(product.compare_price).to_be_hidden()
    product.add_to_cart()
    product.cart.open()
    expect(product.cart.amount(shirt.name, tier.label)).to_have_text(
        format_ars(tier.price)
    )


@pytest.mark.shop
@pytest.mark.mock_only
def test_unavailable_product(shop_page, test_data):
    name = test_data.shop.unavailable
    product = shop_page.open().open_product(name)
    expect(product.heading).to_have_text(name)
    expect(product.unavailable).to_be_visible()
    expect(product.add_button).to_be_disabled()
    product.cart.open()
    expect(product.cart.items).to_have_count(0)
