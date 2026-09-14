import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.smoke, pytest.mark.mock_only]


def test_menu_reaches_product(home_page, shop_page, product_page, test_data):
    home_page.open()
    home_page.navbar.open_shop_from_menu()
    name = test_data["shop"]["shirt"]["name"]
    shop_page.open_product(name)
    expect(product_page.heading).to_have_text(name)
    expect(product_page.add_button).to_be_enabled()
