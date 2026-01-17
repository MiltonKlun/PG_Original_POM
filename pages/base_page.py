from playwright.sync_api import Page
import logging


class BasePage:
    BASE_URL = "https://www.pgoriginal.com"

    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.__class__.__name__ != "Navbar":
            from components.navbar import Navbar
            self.navbar = Navbar(page)

    def navigate(self, url: str):
        """Navigate to a URL and wait for load state."""
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def click(self, selector: str):
        """Wrapper for click with logging."""
        self.logger.info(f"Clicking element: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Wrapper for fill with logging."""
        self.logger.info(f"Filling element: {selector} with '{text}'")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return self.page.text_content(selector)

    def wait_for_element(self, selector: str, state="visible", timeout=10000):
        """Wait for element state."""
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        return self.page.is_visible(selector)
