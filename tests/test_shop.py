import re
import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
@pytest.mark.live_safe
def test_shop_product_details(shop_page, product_page):
    shop_page.open()
    name = shop_page.first_product_name()
    shop_page.open_product(name)
    expect(product_page.heading).to_have_text(name)
    expect(product_page.price).to_have_text(re.compile(r"\$[\d.,]+"))
    expect(product_page.add_button).to_be_enabled()


@pytest.mark.shop
@pytest.mark.mock_only
def test_add_to_cart_flow(shop_page, product_page):
    shop_page.open()
    shop_page.open_product("QA Remera")
    product_page.select_variant(size="M", color="Negro")
    product_page.add_to_cart()
    product_page.cart.open()
    expect(product_page.cart.item("QA Remera", "M / Negro")).to_be_visible()
    expect(product_page.cart.quantity("QA Remera", "M / Negro")).to_have_value("1")
