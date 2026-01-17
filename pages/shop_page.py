from pages.base_page import BasePage


class ShopPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.product_card = ".item-product"
        self.product_name = ".item-name"
        self.filter_checkbox = ".js-filter-checkbox"

    def navigate_to_shop(self):
        self.navigate(f"{self.BASE_URL}/productos/")

    def select_product_by_index(self, index: int):
        """Click on the Nth product in the list."""
        self.logger.info(f"Selecting product at index {index}")
        self.wait_for_element(self.product_card)
        products = self.page.locator(self.product_card)

        count = products.count()
        if count <= index:
            raise Exception(f"Index {index} out of range. Found {count} products.")

        products.nth(index).click()

    def get_product_names(self):
        """Return list of visible product names."""
        self.wait_for_element(self.product_name)
        return self.page.locator(self.product_name).all_text_contents()
