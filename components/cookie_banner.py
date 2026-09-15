from playwright.sync_api import Page, expect


class CookieBanner:
    def __init__(self, page: Page) -> None:
        # Storefront supplies a stable action class but no accessible name contract.
        self.dismiss_button = page.locator(".js-acknowledge-cookies")

    def dismiss_if_present(self) -> None:
        try:
            expect(self.dismiss_button).to_be_visible(timeout=500)
        except AssertionError:
            # Only absence is optional. A detected but unclickable banner must fail.
            if self.dismiss_button.count() == 0 or not self.dismiss_button.is_visible():
                return
            raise
        self.dismiss_button.click()
        expect(self.dismiss_button).to_be_hidden()
