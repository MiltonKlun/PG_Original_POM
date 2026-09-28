from playwright.sync_api import Page
from config import ui_text
from pages.base_page import BasePage
from pages.password_reset_page import PasswordResetPage


class LoginPage(BasePage):
    path = "/account/login/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.form = page.locator("#login-form")
        # Live form labels have no associated IDs; scope by native input type.
        self.email_input = self.form.locator('input[name="email"]')
        self.password_input = self.form.locator('input[name="password"]')
        self.submit_button = self.form.get_by_role("button", name=ui_text.LOGIN_SUBMIT)
        self.forgot_password_link = self.form.get_by_role(
            "link", name=ui_text.FORGOT_PASSWORD
        )
        self.invalid_inputs = self.form.locator("input:invalid")
        self.error_message = self.form.locator(".js-login-general-error")

    def fill_credentials(self, email: str, password: str) -> None:
        self.logger.info("Filling login fields (values omitted)")
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self) -> None:
        self.submit_button.click()

    def open_password_reset(self) -> PasswordResetPage:
        self.forgot_password_link.click()
        return PasswordResetPage(self.page)
