import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # IDs separate the PDP from hidden quickshop forms and old/instalment prices.
        self.form = page.locator("#product_form")
        self.price = page.locator("#price_display")
        self.add_button = self.form.locator(".js-addtocart")
        self.quantity = self.form.get_by_role("spinbutton")
        self.unavailable = self.form.get_by_text("Sin stock", exact=True)

    def open(self, slug: str) -> None:
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(
                "Product slug must contain lowercase letters, digits or hyphens"
            )
        self._open_path(f"/productos/{slug}/")

    def select_variant(
        self, *, size: str | None = None, color: str | None = None
    ) -> None:
        for value in (size, color):
            if value is not None:
                # Visible anchors lack a role/href; their observed title is stable.
                option = self.form.get_by_title(value, exact=True)
                option.click()
                expect(option).to_have_class(re.compile(r"\bselected\b"))

    def add_to_cart(self, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be positive")
        self.quantity.fill(str(quantity))
        self.add_button.click()
