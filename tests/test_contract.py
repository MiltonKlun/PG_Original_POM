"""Locator contract shared by the simulation and the live store.

Each check resolves the page objects' own locators without changing state, so
markup drift on either target fails here with a precise locator instead of as
an unclear scenario failure.
"""

import pytest
from playwright.sync_api import expect
from config.money import ars_minor_units

pytestmark = [pytest.mark.contract, pytest.mark.live_safe]


def test_header_and_footer(home_page):
    home_page.open()
    expect(home_page.navbar.search_link).to_be_visible()
    expect(home_page.navbar.cart_link).to_be_visible()
    expect(home_page.navbar.menu_link).to_be_visible()
    expect(home_page.shop_link).to_be_visible()


def test_cart_drawer(home_page):
    home_page.open()
    home_page.cart.open()
    expect(home_page.cart.empty_message).to_be_visible()
    expect(home_page.cart.subtotal).to_be_attached()
    home_page.cart.close()


def test_menu_shop_panel(home_page):
    home_page.open()
    home_page.navbar.expand_shop_menu()


def test_product_listing(shop_page):
    shop_page.open()
    card = shop_page.cards.first
    expect(card.locator("a.item-link")).to_be_visible()
    expect(card.locator(".item-name")).to_be_visible()
    expect(shop_page.filter_options("Color").first).to_be_visible()
    expect(shop_page.filter_options("Talle").first).to_be_visible()
    expect(shop_page.load_more_button).to_be_attached()
    # Every card publishes per-variant prices in integer minor units.
    for variants in shop_page.card_variants():
        assert variants
        assert all(type(v["price_number_raw"]) is int for v in variants)


def test_product_form(shop_page, product_page):
    shop_page.open()
    shop_page.open_product(shop_page.first_product_name())
    expect(product_page.add_button).to_have_count(1)
    expect(product_page.quantity).to_have_count(1)
    expect(product_page.compare_price).to_be_attached()
    # Displayed current price agrees with the element's raw price attribute.
    raw = product_page.price.get_attribute("data-product-price")
    assert int(raw) == ars_minor_units(product_page.price.inner_text())


def test_login_form(login_page):
    login_page.open()
    expect(login_page.email_input).to_have_attribute("type", "email")
    expect(login_page.email_input).to_have_attribute("required", "")
    expect(login_page.password_input).to_have_attribute("required", "")
    expect(login_page.submit_button).to_be_visible()
    expect(login_page.forgot_password_link).to_be_visible()


def test_contact_form(contact_page):
    contact_page.open()
    expect(contact_page.name_input).to_be_visible()
    expect(contact_page.email_input).to_have_attribute("type", "email")
    expect(contact_page.message_input).to_be_visible()
    expect(contact_page.submit_button).to_be_disabled()
