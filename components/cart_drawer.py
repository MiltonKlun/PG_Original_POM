from playwright.sync_api import Locator, expect
from components.base_component import BaseComponent
from config import ui_text


class CartDrawer(BaseComponent):
    """Shared cart drawer; root is #modal-cart, opened by a header trigger."""

    def __init__(self, root: Locator, trigger: Locator) -> None:
        super().__init__(root)
        self.trigger = trigger
        # Drawer/line classes are documented in the mock contract; live line
        # mutation behavior is intentionally unverified and excluded from live.
        self.items = self.root.locator(".js-cart-item")
        self.empty_message = self.root.locator(".alert-info")
        self.subtotal = self.root.locator(".js-cart-subtotal")
        # Class hook only: live renders an unnamed icon <a>, the simulation a
        # named <button> (see DEF-04 in the defect report).
        self.close_button = self.root.locator(".js-modal-close.modal-close")

    def open(self) -> None:
        self.trigger.click()
        expect(self.root).to_be_visible()

    def close(self) -> None:
        self.close_button.click()
        expect(self.root).to_be_hidden()

    def item(self, name: str, variant: str = "") -> Locator:
        row = self.items.filter(has=self.page.get_by_text(name, exact=True))
        if variant:
            row = row.filter(has=self.page.get_by_text(variant, exact=True))
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
        row.get_by_role("button", name=ui_text.REMOVE_LINE, exact=True).click()
        expect(row).to_have_count(0)
