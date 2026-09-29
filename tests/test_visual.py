"""Visual regression of the stable simulation pages against reviewed baselines."""

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.mock_only, pytest.mark.visual]

PAGES = ["home", "shop", "product", "login", "contact"]


@pytest.mark.parametrize("opened_page", PAGES, indirect=True)
def test_page_matches_baseline(opened_page, visual_check, request):
    opened_page.wait_for_load()
    visual_check(opened_page.page, request.node.callspec.params["opened_page"])


def test_cart_with_one_item_matches_baseline(shop_page, test_data, visual_check):
    shirt = test_data.shop.shirt
    product = shop_page.open().open_product(shirt.name)
    product.select_variant(size=shirt.default.size, color=shirt.default.color)
    product.add_to_cart()
    product.cart.open()
    expect(product.cart.item(shirt.name, shirt.default.label)).to_be_visible()
    visual_check(product.cart.root, "cart-drawer")
