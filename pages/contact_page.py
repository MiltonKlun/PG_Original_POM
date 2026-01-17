from pages.base_page import BasePage


class ContactPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name_input = "#name"
        self.email_input = "#email"
        self.message_input = "#message"
        self.submit_button = "button[name='contact'].btn-primary"
        self.success_message = ".alert-success"
        self.error_message = ".alert-danger"

    def navigate_to_contact(self):
        """Navigate to contact page directly."""
        self.navigate(f"{self.BASE_URL}/contacto/")

    def submit_form(self, name, email, message):
        """Fill and submit the contact form."""
        self.fill(self.name_input, name)
        self.fill(self.email_input, email)
        self.fill(self.message_input, message)
        self.click(self.submit_button)

    def get_error_message(self):
        """Retrieve validation error message."""
        try:
            # Specific selector found by browser agent
            selector = "div.alert.alert-danger"
            self.wait_for_element(selector, timeout=5000)
            return self.get_text(selector)
        except:
            return ""
