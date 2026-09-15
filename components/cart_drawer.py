from playwright.sync_api import Page, Locator, expect
from components.navbar import Navbar


class CartDrawer:
    def __init__(self, page: Page) -> None:
        self.navbar = Navbar(page)
        # Drawer/line classes are documented in the mock contract; live line
        # mutation behavior is intentionally unverified and excluded from live.
        self.root = page.locator("#modal-cart")
        self.items = self.root.locator(".js-cart-item")
        self.empty_message = self.root.locator(".alert-info")
        self.subtotal = self.root.locator(".js-cart-subtotal")

    def open(self) -> None:
        self.navbar.open_cart()
        expect(self.root).to_be_visible()

    def close(self) -> None:
        self.root.get_by_role("button", name="Cerrar carrito", exact=True).click()
        expect(self.root).to_be_hidden()

    def item(self, name: str, variant: str = "") -> Locator:
        row = self.items.filter(has=self.root.page.get_by_text(name, exact=True))
        if variant:
            row = row.filter(has=self.root.page.get_by_text(variant, exact=True))
        return row

    def quantity(self, name: str, variant: str = "") -> Locator:
        return self.item(name, variant).get_by_role("spinbutton")

    def amount(self, name: str, variant: str = "") -> Locator:
        return self.item(name, variant).locator(".js-cart-item-subtotal")

    def set_quantity(self, name: str, quantity: int, variant: str = "") -> None:
        if quantity < 1:
            raise ValueError("Cart quantity must be positive")
        control = self.quantity(name, variant)
        control.fill(str(quantity))
        control.press("Tab")
        expect(control).to_have_value(str(quantity))

    def remove_item(self, name: str, variant: str = "") -> None:
        row = self.item(name, variant)
        row.get_by_role("button", name="Quitar", exact=True).click()
        expect(row).to_have_count(0)
