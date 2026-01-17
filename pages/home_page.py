from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.hero_banner = ".section-slider"
        self.featured_products = ".section-featured-products"
        self.search_button = ".js-search-button"
        self.search_input = ".js-search-input"

    def is_loaded(self):
        """Verify home page specific elements are visible."""
        self.wait_for_element("body")
        return self.page.title() != ""

    def search_for(self, term: str):
        """Open search and search for a term."""
        self.click(self.search_button)
        self.wait_for_element(self.search_input)
        self.fill(self.search_input, term)
        self.page.keyboard.press("Enter")
