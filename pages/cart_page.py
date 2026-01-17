from playwright.sync_api import Page
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._cart_container = page.locator("#modal-cart")
        self._empty_cart_message = page.locator(
            "text=El carrito de compras está vacío."
        )
        self._cart_items = page.locator("#modal-cart .cart-item-name")

    def is_visible(self) -> bool:
        return self._cart_container.first.is_visible()

    def is_empty(self) -> bool:
        return self._empty_cart_message.first.is_visible()

    def get_item_count(self) -> int:
        return self._cart_items.count()

    def wait_for_item_to_appear(self) -> None:
        self._cart_items.first.wait_for(state="visible", timeout=10000)
