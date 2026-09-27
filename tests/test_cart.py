import pytest
from playwright.sync_api import expect
from config.money import format_ars

pytestmark = [pytest.mark.shop, pytest.mark.mock_only]


@pytest.fixture
def shirt(test_data):
    return test_data["shop"]["shirt"]


@pytest.fixture
def shirt_page(shop_page, product_page, shirt):
    shop_page.open()
    shop_page.cart.open()
    expect(shop_page.cart.items).to_have_count(0)
    shop_page.cart.close()
    shop_page.open_product(shirt["name"])
    product_page.select_variant(size=shirt["size"], color=shirt["color"])
    return product_page


@pytest.fixture
def added_product(shirt_page, shirt):
    shirt_page.add_to_cart()
    shirt_page.cart.open()
    expect(shirt_page.cart.item(shirt["name"], shirt["variant"])).to_be_visible()
    return shirt_page.cart, shirt


def test_add_to_cart_flow(added_product):
    cart, item = added_product
    expect(cart.items).to_have_count(1)
    expect(cart.empty_message).to_be_hidden()
    expect(cart.quantity(item["name"], item["variant"])).to_have_value("1")
    expect(cart.amount(item["name"], item["variant"])).to_have_text(
        format_ars(item["price"])
    )
    expect(cart.subtotal).to_have_text(format_ars(item["price"]))


def test_add_with_quantity(shirt_page, shirt):
    shirt_page.add_to_cart(quantity=2)
    shirt_page.cart.open()
    expect(shirt_page.cart.items).to_have_count(1)
    expect(shirt_page.cart.quantity(shirt["name"], shirt["variant"])).to_have_value("2")
    expect(shirt_page.cart.amount(shirt["name"], shirt["variant"])).to_have_text(
        format_ars(2 * shirt["price"])
    )
    expect(shirt_page.cart.subtotal).to_have_text(format_ars(2 * shirt["price"]))


def test_repeat_add_merges_line(shirt_page, shirt):
    # Same product + variant merges into one line; another variant is a new line.
    cart, other = shirt_page.cart, shirt["alternate"]
    shirt_page.add_to_cart()
    shirt_page.add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(1)
    expect(cart.quantity(shirt["name"], shirt["variant"])).to_have_value("2")
    cart.close()
    shirt_page.select_variant(size=other["size"], color=other["color"])
    shirt_page.add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(2)
    expect(cart.quantity(shirt["name"], other["variant"])).to_have_value("1")
    expect(cart.quantity(shirt["name"], shirt["variant"])).to_have_value("2")
    expect(cart.subtotal).to_have_text(format_ars(3 * shirt["price"]))


def test_cart_quantity(added_product):
    cart, item = added_product
    cart.set_quantity(item["name"], 2, item["variant"])
    expect(cart.amount(item["name"], item["variant"])).to_have_text(
        format_ars(2 * item["price"])
    )
    expect(cart.subtotal).to_have_text(format_ars(2 * item["price"]))


def test_cart_persists_across_navigation(added_product, home_page):
    _, item = added_product
    home_page.open()
    home_page.cart.open()
    expect(home_page.cart.items).to_have_count(1)
    expect(home_page.cart.quantity(item["name"], item["variant"])).to_have_value("1")
    expect(home_page.cart.subtotal).to_have_text(format_ars(item["price"]))


def test_cart_remove(added_product):
    cart, item = added_product
    cart.remove_item(item["name"], item["variant"])
    expect(cart.items).to_have_count(0)
    expect(cart.empty_message).to_be_visible()
    expect(cart.subtotal).to_have_text(format_ars(0))


def test_remove_one_of_two_lines(added_product, shop_page, product_page, test_data):
    cart, shirt = added_product
    cap = test_data["shop"]["cap"]
    cart.close()
    shop_page.open()
    shop_page.open_product(cap["name"])
    product_page.add_to_cart()
    cart.open()
    expect(cart.items).to_have_count(2)
    cart.remove_item(shirt["name"], shirt["variant"])
    expect(cart.items).to_have_count(1)
    expect(cart.item(cap["name"])).to_be_visible()
    expect(cart.empty_message).to_be_hidden()
    expect(cart.subtotal).to_have_text(format_ars(cap["price"]))


def test_cart_starts_empty(home_page):
    home_page.open()
    home_page.cart.open()
    expect(home_page.cart.items).to_have_count(0)
    expect(home_page.cart.empty_message).to_be_visible()


def test_cart_without_variants(shop_page, product_page, test_data):
    item = test_data["shop"]["cap"]
    shop_page.open()
    shop_page.open_product(item["name"])
    expect(product_page.heading).to_have_text(item["name"])
    product_page.add_to_cart()
    product_page.cart.open()
    expect(product_page.cart.item(item["name"])).to_be_visible()
    expect(product_page.cart.subtotal).to_have_text(format_ars(item["price"]))
