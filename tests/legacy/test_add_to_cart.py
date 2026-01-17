from pages.shop_page import ShopPage
from pages.cart_page import CartPage
import pytest


def test_add_item_to_cart(page, home_page):
    """
    Verify that a user can add a product to the cart from the Shop page.
    """
    shop_page = ShopPage(page)
    # Direct navigation for stability
    shop_page.navigate()

    # Ensure products are loaded
    page.wait_for_load_state("domcontentloaded")

    # Add the first product
    shop_page.add_first_product_to_cart()

    # The cart might not open automatically.
    # We verify the item by opening the cart explicitly.
    home_page.navbar.open_cart()

    cart_page = CartPage(page)
    # Verify item is in cart
    cart_page.wait_for_item_to_appear()
    assert cart_page.get_item_count() > 0, "Cart should have at least one item"
