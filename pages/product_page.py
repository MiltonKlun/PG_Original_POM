from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_to_cart_btn = ".js-addtocart"
        self.variant_select = ".js-insta-variant"
        self.product_price = ".js-price-display"
        self.success_link = ".js-open-cart"
        self.cart_sidebar = "#modal-cart"

    def add_to_cart(self):
        """Add the current product to cart."""
        self.logger.info("Adding product to cart")
        self.click(self.add_to_cart_btn)

    def select_variant(self, variant_text: str):
        """Select a size/color variant."""
        self.logger.info(f"Selecting variant: {variant_text}")
        locator = self.page.get_by_text(variant_text, exact=True)
        locator.click()

    def get_price(self) -> str:
        return self.get_text(self.product_price)
