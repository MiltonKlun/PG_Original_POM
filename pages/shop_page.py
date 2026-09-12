import json
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ShopPage(BasePage):
    path = "/productos/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Storefront product cards have no semantic list-item role.
        self.cards = page.locator(".item-product")
        self.product_names = self.cards.locator(".item-name")
        self.empty_results = page.get_by_text("No encontramos nada para", exact=False)
        # Responsive filter labels wrap hidden checkboxes; click the visible label.
        self.color_filters = page.locator(
            '.js-filter-checkbox[data-filter-name="Color"]:visible'
        )
        self.clear_filters = page.locator(".js-remove-all-filters-private:visible")

    def first_product_name(self) -> str:
        # Deliberate discovery of the first available card, not ambiguity masking.
        card = self.cards.filter(has_not_text="Sin stock").first
        expect(card).to_be_visible()
        return card.locator(".item-name").inner_text().strip()

    def open_product(self, name: str) -> None:
        card = self.cards.filter(has=self.page.get_by_text(name, exact=True))
        expect(card).to_have_count(1)
        card.get_by_role("link", name=name, exact=True).click()

    def filter_color(self, color: str) -> None:
        label = self.color_filters.filter(has_text=color)
        expect(label).to_have_count(1)
        label.click()
        expect(label.get_by_role("checkbox")).to_be_checked()

    def clear_filter(self) -> None:
        self.clear_filters.click()
        expect(self.color_filters.get_by_role("checkbox")).not_to_be_checked()

    def displayed_colors(self) -> list[set[str]]:
        # Public card metadata drives the storefront's own variant choices.
        return [
            {
                v["option1"]
                for v in json.loads(
                    card.locator("[data-variants]").get_attribute("data-variants")
                )
            }
            for card in self.cards.all()
        ]
