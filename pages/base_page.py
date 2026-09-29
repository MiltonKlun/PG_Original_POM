import logging
import re
from functools import cached_property
from string import Formatter
from typing import Literal, Self
from urllib.parse import urlsplit
from playwright.sync_api import Page
from components.base_component import Disclosure
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

    def disclosure(self, name: Literal["search", "menu", "cart"]) -> Disclosure:
        """Keyboard view of a header panel: its trigger, panel and close."""
        if name == "search":
            search = self.search
            return Disclosure(self.navbar.search_link, search.root, search.close_button)
        if name == "menu":
            nav = self.navbar
            return Disclosure(nav.menu_link, nav.menu, nav.menu_close_button)
        return Disclosure(self.cart.trigger, self.cart.root, self.cart.close_button)

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

    def wait_for_load(self) -> None:
        """Wait for the page's subresources, not just its DOM."""
        self.page.wait_for_load_state("load")

    def linked_paths(self) -> list[str]:
        """Unique same-origin link paths on the page, sorted."""
        origin = urlsplit(self.page.url).netloc
        hrefs = self.page.locator("a[href]").evaluate_all(
            "links => links.map(link => link.href)"
        )
        paths = {
            urlsplit(href).path
            for href in hrefs
            if urlsplit(href).netloc == origin
            and urlsplit(href).scheme in ("http", "https")
        }
        return sorted(paths)

    def open(self, **params: str) -> Self:
        path = self.url_for(**params)
        self.logger.info("Opening %s", path)
        response = self.page.goto(path, wait_until="domcontentloaded")
        if response is None or not response.ok:
            status = response.status if response else "no response"
            raise RuntimeError(f"Navigation to {path} failed: {status}")
        self.cookies.dismiss_if_present()
        return self
