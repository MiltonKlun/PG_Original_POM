from playwright.sync_api import Locator, expect
from components.base_component import BaseComponent
from config import ui_text


class Navbar(BaseComponent):
    """Site header; root is the <header> element."""

    def __init__(self, root: Locator) -> None:
        super().__init__(root)
        self.search_link = self.root.get_by_role(
            "link", name=ui_text.SEARCH_LINK, exact=True
        )
        # Header drawer/menu links do not have stable accessible text on mobile.
        self.cart_link = self.root.locator('a[data-toggle="#modal-cart"]')
        self.menu_link = self.root.locator('a[data-toggle="#nav-hamburger"]')
        # The menu panel the header opens is rendered outside <header>.
        self.menu = self.page.locator("#nav-hamburger")
        # SHOP is a submenu toggle (href="#"); a hidden duplicate exists in the DOM.
        self.menu_shop_toggle = self.menu.get_by_role(
            "link", name=ui_text.SHOP, exact=True
        )
        self.menu_all_products = self.menu.get_by_role(
            "link", name=ui_text.ALL_PRODUCTS, exact=True
        )
        # The SHOP sub-panel has its own close control; only one is visible.
        self.menu_close_button = self.menu.locator(".js-toggle-menu-close:visible")

    def open_search(self) -> None:
        self.search_link.click()

    def open_menu(self) -> None:
        self.menu_link.click()
        expect(self.menu).to_be_visible()

    def expand_shop_menu(self) -> None:
        self.open_menu()
        self.menu_shop_toggle.click()
        expect(self.menu_all_products).to_be_visible()

    def open_shop_from_menu(self) -> None:
        self.expand_shop_menu()
        self.menu_all_products.click()
