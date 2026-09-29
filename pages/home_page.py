from playwright.sync_api import Page

from config import ui_text
from pages.base_page import BasePage
from pages.shop_page import ShopPage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Footer has one SHOP link; navigation menu contains repeated categories.
        self.shop_link = self.footer.get_by_role("link", name=ui_text.SHOP, exact=True)

    def open_shop(self) -> ShopPage:
        self.shop_link.click()
        return ShopPage(self.page)

    def open_shop_from_menu(self) -> ShopPage:
        self.navbar.open_shop_from_menu()
        return ShopPage(self.page)

    def search_for(self, term: str) -> ShopPage:
        """Search from the header; results use the listing layout."""
        self.navbar.open_search()
        self.search.search(term)
        return ShopPage(self.page)
