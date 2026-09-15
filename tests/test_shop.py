import pytest
from playwright.sync_api import expect
from config.money import ars_minor_units


@pytest.mark.smoke
@pytest.mark.live_safe
def test_shop_product_details(shop_page, product_page):
    shop_page.open()
    name = shop_page.first_product_name()
    shop_page.open_product(name)
    expect(product_page.heading).to_have_text(name)
    expect(product_page.price).to_be_visible()
    assert ars_minor_units(product_page.price.inner_text()) > 0
    expect(product_page.add_button).to_be_enabled()


@pytest.mark.shop
@pytest.mark.mock_only
def test_filter_color_and_clear(shop_page):
    shop_page.open()
    expect(shop_page.cards).to_have_count(3)
    shop_page.filter_color("Negro")
    expect(shop_page.cards).to_have_count(1)
    assert all("Negro" in colors for colors in shop_page.displayed_variant_values())
    shop_page.clear_filter()
    expect(shop_page.cards).to_have_count(3)


@pytest.mark.shop
@pytest.mark.mock_only
def test_unavailable_product(shop_page, product_page, test_data):
    shop_page.open()
    shop_page.open_product(test_data["shop"]["unavailable"]["name"])
    expect(product_page.unavailable).to_be_visible()
    expect(product_page.add_button).to_be_disabled()
    product_page.cart.open()
    expect(product_page.cart.items).to_have_count(0)
