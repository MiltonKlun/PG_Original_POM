from playwright.sync_api import Locator, expect
from components.base_component import BaseComponent


class SearchModal(BaseComponent):
    """Search panel; root is the active #nav-search (a hidden duplicate exists)."""

    def __init__(self, root: Locator) -> None:
        super().__init__(root)
        self.input = self.root.get_by_role("searchbox")
        # Live close anchor has no accessible name.
        self.close_button = self.root.locator(".js-modal-close")

    def search(self, term: str) -> None:
        expect(self.root).to_be_visible()
        self.input.fill(term)
        self.input.press("Enter")

    def close(self) -> None:
        self.close_button.click()
        expect(self.root).to_be_hidden()
