from pages.home_page import HomePage
from pages.cart_page import CartPage
import pytest


def test_cart_is_empty_initially(page, home_page):
    """
    Verify that the cart is empty when first visited.
    """
    home_page.navigate()
    home_page.navbar.open_cart()

    cart_page = CartPage(page)

    # Wait a bit for sidecart/page load
    page.wait_for_load_state("domcontentloaded")

    # Assert cart is visible
    # We might need to handle the case where open_cart is a toggle
    # cart_page.is_visible() might be tricky if it's a sidebar, we'll try to assert emptiness directly first

    # Check if empty message is there
    # Note: text might vary, but "vacío" is standard Spanish for empty.
    # We'll assert specific text if known, otherwise we check item count is 0

    # If explicit text fails, we can check count.
    assert cart_page.is_empty(), "Cart should be empty initially"
