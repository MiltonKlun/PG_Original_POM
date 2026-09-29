import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.smoke, pytest.mark.live_safe]


def test_menu_reaches_product(home_page):
    shop = home_page.open().open_shop_from_menu()
    expect(shop.page).to_have_url(re.compile(r"/productos/?$"))
    name = shop.first_product_name()
    product = shop.open_product(name)
    expect(product.heading).to_have_text(name)
    expect(product.add_button).to_be_enabled()
