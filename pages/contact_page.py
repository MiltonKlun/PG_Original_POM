from playwright.sync_api import Page
from pages.base_page import BasePage


class ContactPage(BasePage):
    path = "/contacto/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Form scope excludes duplicate newsletter email IDs.
        self.form = page.locator("#contact-form")
        self.name_input = self.form.get_by_label("Nombre", exact=True)
        self.invalid_email = self.form.locator('input[name="email"]:invalid')
        self.email_input = self.form.get_by_label("Email", exact=True)
        self.message_input = self.form.get_by_label("Mensaje", exact=True)
        self.submit_button = self.form.get_by_role("button", name="Enviar", exact=True)

    def fill_form(self, name: str, email: str, message: str) -> None:
        self.logger.info("Filling contact fields (values omitted)")
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.message_input.fill(message)
