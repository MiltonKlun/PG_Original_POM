import json
import re
from decimal import Decimal
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Page, expect

from config import ui_text
from pages.base_page import BasePage


class ProductPage(BasePage):
    path = "/productos/{slug}/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # IDs separate the PDP from hidden quickshop forms and old/instalment prices.
        self.form = page.locator("#product_form")
        self.price = page.locator("#price_display")
        # Hidden (display:none) when the selected variant has no discount.
        self.compare_price = page.locator("#compare_price_display")
        # Live form also has a div.js-addtocart animation placeholder.
        self.add_button = self.form.locator('input[type="submit"].js-addtocart')
        self.quantity = self.form.get_by_role("spinbutton")
        self.unavailable = self.form.get_by_text(ui_text.OUT_OF_STOCK, exact=True)
        self.structured_data = page.locator('script[type="application/ld+json"]')

    def select_variant(
        self, *, size: str | None = None, color: str | None = None
    ) -> None:
        self.select_options(*(value for value in (size, color) if value is not None))

    def select_options(self, *values: str) -> None:
        """Select option values in order, e.g. the optionN values of a variant."""
        for value in values:
            # Visible anchors lack a role/href; their observed title is stable.
            option = self.form.get_by_title(value, exact=True)
            option.click()
            expect(option).to_have_class(re.compile(r"\bselected\b"))

    def structured_price(self) -> int:
        """Offer price, in minor units, from this page's own JSON-LD Product.

        Pages also embed JSON-LD for related products, so match the product
        whose mainEntityOfPage is the current URL.
        """
        path = urlsplit(self.page.url).path
        texts = self.structured_data.evaluate_all("els => els.map(e => e.textContent)")
        for text in texts:
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            for item in data if isinstance(data, list) else [data]:
                if self._describes(item, path):
                    return int(Decimal(str(item["offers"]["price"])) * 100)
        raise AssertionError(f"No JSON-LD Product describes {path}")

    @staticmethod
    def _describes(item: Any, path: str) -> bool:
        if not isinstance(item, dict) or item.get("@type") != "Product":
            return False
        page_id = (item.get("mainEntityOfPage") or {}).get("@id", "")
        return bool(urlsplit(page_id).path == path)

    def add_to_cart(self, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be positive")
        self.quantity.fill(str(quantity))
        self.add_button.click()
