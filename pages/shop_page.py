import json
from typing import Any
from playwright.sync_api import Locator, Page, expect
from config import ui_text
from pages.base_page import BasePage
from pages.product_page import ProductPage


class ShopPage(BasePage):
    """Product listing; also the layout of search results."""

    path = "/productos/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Storefront product cards have no semantic list-item role.
        self.cards = page.locator(".item-product")
        self.product_names = self.cards.locator(".item-name")
        self.empty_results = page.get_by_text(ui_text.NO_RESULTS, exact=False)
        # Responsive filter labels wrap hidden checkboxes; click the visible label.
        self.filters = page.locator(".js-filter-checkbox:visible")
        self.clear_filters = page.locator(".js-remove-all-filters-private:visible")
        # The load-more anchor has no href, so it has no link role.
        self.load_more_button = page.locator(".js-load-more").get_by_text(
            ui_text.LOAD_MORE, exact=True
        )

    def first_product_name(self) -> str:
        # Deliberate discovery of the first available card, not ambiguity masking.
        card = self.cards.filter(has_not_text=ui_text.OUT_OF_STOCK).first
        expect(card).to_be_visible()
        return card.locator(".item-name").inner_text().strip()

    def displayed_names(self) -> list[str]:
        return [name.strip() for name in self.product_names.all_inner_texts()]

    def open_product(self, name: str) -> ProductPage:
        card = self.cards.filter(has=self.page.get_by_text(name, exact=True))
        expect(card).to_have_count(1)
        # Live image and text links share a name; this is the observed text link.
        card.locator("a.item-link").click()
        return ProductPage(self.page)

    def filter_options(self, name: str) -> Locator:
        return self.filters.and_(self.page.locator(f'[data-filter-name="{name}"]'))

    def apply_filter(self, name: str, value: str) -> None:
        # Label text includes result counts ("S (19)"); match the value attribute.
        label = self.filter_options(name).and_(
            self.page.locator(f'[data-filter-value="{value}"]')
        )
        expect(label).to_have_count(1)
        label.click()
        expect(label.locator("input")).to_be_checked()

    def clear_filter(self) -> None:
        self.clear_filters.click()
        expect(self.filters.locator("input:checked")).to_have_count(0)

    def load_more(self) -> None:
        shown = self.cards.count()
        self.load_more_button.click()
        expect(self.cards.nth(shown)).to_be_visible()

    def card_variants(self) -> list[list[dict[str, Any]]]:
        # Public card metadata drives the storefront's own variant choices.
        variants = []
        for card in self.cards.all():
            raw = card.locator("[data-variants]").get_attribute("data-variants")
            if raw is None:
                raise AssertionError("Product card has no data-variants metadata")
            variants.append(json.loads(raw))
        return variants

    def displayed_variant_values(self) -> list[set[str]]:
        # Option position varies by product, so read every optionN value.
        return [
            {
                value
                for v in variants
                for key, value in v.items()
                if key.startswith("option") and isinstance(value, str)
            }
            for variants in self.card_variants()
        ]
