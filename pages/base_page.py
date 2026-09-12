import logging
from playwright.sync_api import Page
from components.navbar import Navbar
from components.search_modal import SearchModal
from components.cart_drawer import CartDrawer
from components.cookie_banner import CookieBanner


class BasePage:
    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.logger = logging.getLogger(type(self).__name__)
        self.navbar = Navbar(page)
        self.search = SearchModal(page)
        self.cart = CartDrawer(page)
        self.cookies = CookieBanner(page)
        self.header = page.locator("header")
        self.footer = page.locator("footer")
        self.heading = page.get_by_role("heading", level=1)

    def open(self) -> None:
        self._open_path(self.path)

    def _open_path(self, path: str) -> None:
        self.logger.info("Opening %s", path)
        response = self.page.goto(path, wait_until="domcontentloaded")
        if response is None or not response.ok:
            status = response.status if response else "no response"
            raise RuntimeError(f"Navigation to {path} failed: {status}")
        self.cookies.dismiss_if_present()
