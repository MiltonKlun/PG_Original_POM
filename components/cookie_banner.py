from playwright.sync_api import expect

from components.base_component import BaseComponent


class CookieBanner(BaseComponent):
    """Cookie notice; its root is the dismiss control, the only stable hook.

    The storefront supplies a stable action class but no accessible name.
    """

    def dismiss_if_present(self) -> None:
        try:
            expect(self.root).to_be_visible(timeout=500)
        except AssertionError:
            # Only absence is optional. A detected but unclickable banner must fail.
            if self.root.count() == 0 or not self.root.is_visible():
                return
            raise
        self.root.click()
        expect(self.root).to_be_hidden()
