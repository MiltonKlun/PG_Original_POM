import logging
import re
from functools import cached_property
from string import Formatter
from typing import Self
from playwright.sync_api import Page
from components.cart_drawer import CartDrawer
from components.cookie_banner import CookieBanner
from components.navbar import Navbar
from components.search_modal import SearchModal

# Path parameters become URL segments: allow only slug characters.
_SEGMENT = re.compile(r"[a-z0-9-]+")


class BasePage:
    """Shared page behavior. Subclasses declare a relative `path` template."""

    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.logger = logging.getLogger(type(self).__name__)
        self.header = page.locator("header")
        self.footer = page.locator("footer")
        self.heading = page.get_by_role("heading", level=1)

    @cached_property
    def navbar(self) -> Navbar:
        return Navbar(self.header)

    @cached_property
    def search(self) -> SearchModal:
        # Responsive duplicate forms require the observed active panel ID.
        return SearchModal(self.page.locator("#nav-search"))

    @cached_property
    def cart(self) -> CartDrawer:
        return CartDrawer(self.page.locator("#modal-cart"), self.navbar.cart_link)

    @cached_property
    def cookies(self) -> CookieBanner:
        return CookieBanner(self.page.locator(".js-acknowledge-cookies"))

    def url_for(self, **params: str) -> str:
        fields = {name for _, name, _, _ in Formatter().parse(self.path) if name}
        if set(params) != fields:
            expected = ", ".join(sorted(fields)) or "no parameters"
            raise TypeError(f"{type(self).__name__}.open() takes {expected}")
        for name, value in params.items():
            if not _SEGMENT.fullmatch(value):
                raise ValueError(
                    f"{name} must contain lowercase letters, digits or hyphens"
                )
        return self.path.format(**params)

    def open(self, **params: str) -> Self:
        path = self.url_for(**params)
        self.logger.info("Opening %s", path)
        response = self.page.goto(path, wait_until="domcontentloaded")
        if response is None or not response.ok:
            status = response.status if response else "no response"
            raise RuntimeError(f"Navigation to {path} failed: {status}")
        self.cookies.dismiss_if_present()
        return self
