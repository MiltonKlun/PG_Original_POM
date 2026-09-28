from playwright.sync_api import Page
from config import ui_text
from pages.base_page import BasePage


class ContactPage(BasePage):
    path = "/contacto/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Form scope excludes duplicate newsletter email IDs.
        self.form = page.locator("#contact-form")
        self.name_input = self.form.get_by_label(ui_text.CONTACT_NAME, exact=True)
        self.email_input = self.form.get_by_label(ui_text.CONTACT_EMAIL, exact=True)
        self.message_input = self.form.get_by_label(ui_text.CONTACT_MESSAGE, exact=True)
        self.invalid_email = self.form.locator('input[name="email"]:invalid')
        self.submit_button = self.form.get_by_role(
            "button", name=ui_text.CONTACT_SUBMIT, exact=True
        )

    def fill_form(self, name: str, email: str, message: str) -> None:
        self.logger.info("Filling contact fields (values omitted)")
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.message_input.fill(message)
