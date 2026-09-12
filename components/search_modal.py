from playwright.sync_api import Page, expect


class SearchModal:
    def __init__(self, page: Page) -> None:
        # Responsive duplicate forms require the observed active panel ID.
        self.root = page.locator("#nav-search")
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
