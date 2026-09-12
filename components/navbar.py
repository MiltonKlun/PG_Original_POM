from playwright.sync_api import Page, expect


class Navbar:
    def __init__(self, page: Page) -> None:
        self.root = page.locator("header")
        self.search_link = self.root.get_by_role("link", name="Buscador", exact=True)
        # Header drawer/menu links do not have stable accessible text on mobile.
        self.cart_link = self.root.locator('a[data-toggle="#modal-cart"]')
        self.menu_link = self.root.locator('a[data-toggle="#nav-hamburger"]')
        self.menu = page.locator("#nav-hamburger")

    def open_search(self) -> None:
        self.search_link.click()

    def open_cart(self) -> None:
        self.cart_link.click()

    def open_menu(self) -> None:
        self.menu_link.click()
        expect(self.menu).to_be_visible()
