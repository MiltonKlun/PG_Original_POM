from pages.base_page import BasePage


class Navbar(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self._search_link = "text=Buscar"
        self._cart_link = "a:has-text('Carrito')"

    def open_search(self) -> None:
        self.click(self._search_link)

    def open_cart(self) -> None:
        self.click(self._cart_link)

    def navigate_to_shop(self) -> None:
        """Navigate to the shop page."""
        self.navigate(f"{self.BASE_URL}/productos/")

    def navigate_to_home(self) -> None:
        """Navigate to the home page."""
        self.click("text=Inicio")
