import json
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class ShopPage(BasePage):
    path = "/productos/"

    def open(self) -> None:
        self._open_path(self.path)

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Storefront product cards have no semantic list-item role.
        self.cards = page.locator(".item-product")
        self.product_names = self.cards.locator(".item-name")
        self.empty_results = page.get_by_text("No encontramos nada para", exact=False)
        # Responsive filter labels wrap hidden checkboxes; click the visible label.
        self.filters = page.locator(".js-filter-checkbox:visible")
        self.clear_filters = page.locator(".js-remove-all-filters-private:visible")
        # The load-more anchor has no href, so it has no link role.
        self.load_more_button = page.locator(".js-load-more").get_by_text(
            "Mostrar más productos", exact=True
        )

    def first_product_name(self) -> str:
        # Deliberate discovery of the first available card, not ambiguity masking.
        card = self.cards.filter(has_not_text="Sin stock").first
        expect(card).to_be_visible()
        return card.locator(".item-name").inner_text().strip()

    def open_product(self, name: str) -> None:
        card = self.cards.filter(has=self.page.get_by_text(name, exact=True))
        expect(card).to_have_count(1)
        # Live image and text links share a name; this is the observed text link.
        card.locator("a.item-link").click()

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

    def card_variants(self) -> list[list[dict]]:
        # Public card metadata drives the storefront's own variant choices.
        return [
            json.loads(card.locator("[data-variants]").get_attribute("data-variants"))
            for card in self.cards.all()
        ]

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
