import pytest
from pages.shop_page import ShopPage
from pages.product_page import ProductPage


@pytest.mark.smoke
def test_shop_product_details(page_obj):
    """Test navigating to shop and viewing a product."""
    shop = ShopPage(page_obj)
    shop.navigate_to_shop()

    names = shop.get_product_names()
    assert len(names) > 0, "No products found in shop"

    import pytest_check as check

    shop.select_product_by_index(0)
    product = ProductPage(page_obj)
    
    check.is_true(product.is_visible(product.product_price), "Price not visible on PDP")
    check.is_true(product.is_visible(product.add_to_cart_btn), "Add to Cart button not visible")

@pytest.mark.integration
def test_add_to_cart_flow(page_obj):
    """Test full add to cart flow."""
    shop = ShopPage(page_obj)
    shop.navigate_to_shop()
    shop.select_product_by_index(0)

    product = ProductPage(page_obj)

    if product.is_visible(product.variant_select):
        product.page.locator(product.variant_select).first.click()
        product.page.locator(product.variant_select).first.click()

    product.add_to_cart()
    
    try:
        product.page.locator(product.success_link).wait_for(state="visible", timeout=5000)
        product.click(product.success_link)
    except Exception:
        print("Success link (toast) not visible/clickable. Using Navbar fallback.")
        product.navbar.open_cart()

    product.wait_for_element(product.cart_sidebar)
    assert product.is_visible(product.cart_sidebar), "Cart sidebar did not open"
