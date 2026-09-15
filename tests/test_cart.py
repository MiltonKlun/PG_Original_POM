import pytest
from playwright.sync_api import expect
from config.money import ars_minor_units

pytestmark = [pytest.mark.shop, pytest.mark.mock_only]


@pytest.fixture
def added_product(shop_page, product_page, test_data):
    item = test_data["shop"]["shirt"]
    shop_page.open()
    shop_page.cart.open()
    expect(shop_page.cart.items).to_have_count(0)
    shop_page.cart.close()
    shop_page.open_product(item["name"])
    product_page.select_variant(size=item["size"], color=item["color"])
    product_page.add_to_cart()
    product_page.cart.open()
    expect(product_page.cart.item(item["name"], item["variant"])).to_be_visible()
    return product_page.cart, item


def test_add_to_cart_flow(added_product):
    cart, item = added_product
    expect(cart.items).to_have_count(1)
    expect(cart.quantity(item["name"], item["variant"])).to_have_value("1")
    assert (
        ars_minor_units(cart.amount(item["name"], item["variant"]).inner_text())
        == item["price"]
    )
    assert ars_minor_units(cart.subtotal.inner_text()) == item["price"]


def test_cart_quantity(added_product):
    cart, item = added_product
    cart.set_quantity(item["name"], 2, item["variant"])
    expect(cart.amount(item["name"], item["variant"])).to_have_text("$58.000,00")
    assert ars_minor_units(cart.subtotal.inner_text()) == 2 * item["price"]


def test_cart_remove(added_product):
    cart, item = added_product
    cart.remove_item(item["name"], item["variant"])
    expect(cart.items).to_have_count(0)
    expect(cart.empty_message).to_be_visible()
    assert ars_minor_units(cart.subtotal.inner_text()) == 0


def test_cart_starts_empty(home_page):
    home_page.open()
    home_page.cart.open()
    expect(home_page.cart.items).to_have_count(0)
    expect(home_page.cart.empty_message).to_be_visible()


def test_cart_without_variants(shop_page, product_page, test_data):
    item = test_data["shop"]["cap"]
    shop_page.open()
    shop_page.open_product(item["name"])
    product_page.add_to_cart()
    product_page.cart.open()
    expect(product_page.cart.item(item["name"])).to_be_visible()
    assert ars_minor_units(product_page.cart.subtotal.inner_text()) == item["price"]
