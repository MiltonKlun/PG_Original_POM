from playwright.sync_api import Page
from pages.base_page import BasePage


class HomePage(BasePage):
    def open(self) -> None:
        self._open_path(self.path)

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Footer has one SHOP link; navigation menu contains repeated categories.
        self.shop_link = self.footer.get_by_role("link", name="SHOP", exact=True)

    def open_shop(self) -> None:
        self.shop_link.click()
