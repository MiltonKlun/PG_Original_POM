import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/account/login/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.form = page.locator("#login-form")
        # Live form labels have no associated IDs; scope by native input type.
        self.email_input = self.form.locator('input[name="email"]')
        self.password_input = self.form.locator('input[name="password"]')
        self.submit_button = self.form.get_by_role(
            "button", name=re.compile("Iniciar", re.I)
        )
        self.forgot_password_link = self.form.get_by_role(
            "link", name=re.compile("Olvidaste")
        )
        self.error_message = self.form.locator(".js-login-general-error")
        self.reset_heading = page.get_by_role(
            "heading", name=re.compile("CAMBIAR CONTRASE", re.I)
        )

    def fill_credentials(self, email: str, password: str) -> None:
        self.logger.info("Filling login fields (values omitted)")
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self) -> None:
        self.submit_button.click()

    def open_password_reset(self) -> None:
        self.forgot_password_link.click()
        expect(self.page).to_have_url(re.compile(r"/account/reset/?$"))
        expect(self.reset_heading).to_be_visible()
