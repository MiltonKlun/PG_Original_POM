from dataclasses import dataclass

import pytest
from playwright.sync_api import expect

from components.cart_drawer import CartDrawer
from config.money import format_ars
from config.test_data import SuiteData, VariantProduct
from pages.product_page import ProductPage
from pages.shop_page import ShopPage

pytestmark = [pytest.mark.shop, pytest.mark.mock_only]


@dataclass(frozen=True)
class AddedProduct:
    """Cart state after adding the default shirt variant once."""

    cart: CartDrawer
    product: VariantProduct


@pytest.fixture
def shirt(test_data: SuiteData) -> VariantProduct:
    return test_data.shop.shirt


@pytest.fixture
def shirt_page(shop_page: ShopPage, shirt: VariantProduct) -> ProductPage:
    shop_page.open()
    shop_page.cart.open()
    expect(shop_page.cart.items).to_have_count(0)
    shop_page.cart.close()
    product = shop_page.open_product(shirt.name)
    product.select_variant(size=shirt.default.size, color=shirt.default.color)
    return product


@pytest.fixture
def added_product(shirt_page: ProductPage, shirt: VariantProduct) -> AddedProduct:
    shirt_page.add_to_cart()
    shirt_page.cart.open()
    expect(shirt_page.cart.item(shirt.name, shirt.default.label)).to_be_visible()
    return AddedProduct(shirt_page.cart, shirt)


def test_add_to_cart_flow(added_product):
    cart, item = added_product.cart, added_product.product
    expect(cart.items).to_have_count(1)
    expect(cart.empty_message).to_be_hidden()
    expect(cart.quantity(item.name, item.default.label)).to_have_value("1")
    expect(cart.amount(item.name, item.default.label)).to_have_text(
        format_ars(item.price)
    )
    expect(cart.subtotal).to_have_text(format_ars(item.price))


def test_add_with_quantity(shirt_page, shirt):
    cart, label = shirt_page.cart, shirt.default.label
    shirt_page.add_to_cart(quantity=2)
    cart.open()
    expect(cart.items).to_have_count(1)
    expect(cart.quantity(shirt.name, label)).to_have_value("2")
    expect(cart.amount(shirt.name, label)).to_have_text(format_ars(2 * shirt.price))
    expect(cart.subtotal).to_have_text(format_ars(2 * shirt.price))


def test_repeat_add_merges_line(shirt_page, shirt):
    # Same product + variant merges into one line; another variant is a new line.
    cart, other = shirt_page.cart, shirt.alternate
    shirt_page.add_to_cart()
    shirt_page.add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(1)
    expect(cart.quantity(shirt.name, shirt.default.label)).to_have_value("2")
    cart.close()
    shirt_page.select_variant(size=other.size, color=other.color)
    shirt_page.add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(2)
    expect(cart.quantity(shirt.name, other.label)).to_have_value("1")
    expect(cart.quantity(shirt.name, shirt.default.label)).to_have_value("2")
    expect(cart.subtotal).to_have_text(format_ars(3 * shirt.price))


def test_cart_quantity(added_product):
    cart, item = added_product.cart, added_product.product
    cart.set_quantity(item.name, 2, item.default.label)
    expect(cart.amount(item.name, item.default.label)).to_have_text(
        format_ars(2 * item.price)
    )
    expect(cart.subtotal).to_have_text(format_ars(2 * item.price))


def test_cart_persists_across_navigation(added_product, home_page):
    item = added_product.product
    cart = home_page.open().cart
    cart.open()
    expect(cart.items).to_have_count(1)
    expect(cart.quantity(item.name, item.default.label)).to_have_value("1")
    expect(cart.subtotal).to_have_text(format_ars(item.price))


def test_cart_remove(added_product):
    cart, item = added_product.cart, added_product.product
    cart.remove_item(item.name, item.default.label)
    expect(cart.items).to_have_count(0)
    expect(cart.empty_message).to_be_visible()
    expect(cart.subtotal).to_have_text(format_ars(0))


def test_remove_one_of_two_lines(added_product, shop_page, test_data):
    cart, shirt = added_product.cart, added_product.product
    cap = test_data.shop.cap
    cart.close()
    shop_page.open().open_product(cap.name).add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(2)
    cart.remove_item(shirt.name, shirt.default.label)
    expect(cart.items).to_have_count(1)
    expect(cart.item(cap.name)).to_be_visible()
    expect(cart.empty_message).to_be_hidden()
    expect(cart.subtotal).to_have_text(format_ars(cap.price))


def test_cart_starts_empty(home_page):
    cart = home_page.open().cart
    cart.open()
    expect(cart.items).to_have_count(0)
    expect(cart.empty_message).to_be_visible()


def test_cart_without_variants(shop_page, test_data):
    cap = test_data.shop.cap
    product = shop_page.open().open_product(cap.name)
    expect(product.heading).to_have_text(cap.name)
    product.add_to_cart()
    product.cart.open()
    expect(product.cart.item(cap.name)).to_be_visible()
    expect(product.cart.subtotal).to_have_text(format_ars(cap.price))
