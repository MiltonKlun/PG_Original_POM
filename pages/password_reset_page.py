from playwright.sync_api import Page

from config import ui_text
from pages.base_page import BasePage


class PasswordResetPage(BasePage):
    path = "/account/reset/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.reset_heading = page.get_by_role("heading", name=ui_text.RESET_HEADING)
