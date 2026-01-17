from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.submit_button = "input[type='submit'], button[type='submit']"
        self.forgot_password_link = "a[href*='/account/reset']"
        self.error_message = ".js-login-general-error"
        self.login_nav_link = "a[href*='login']"

    def navigate_to_login(self):
        """Navigate to login page via header or direct URL."""
        self.navigate(f"{self.BASE_URL}/account/login/")

    def login(self, email, password):
        self.fill(self.email_input, email)
        self.fill(self.password_input, password)
        self.click(self.submit_button)
        self.page.wait_for_load_state("domcontentloaded")

    def get_error_message(self):
        self.wait_for_element(self.error_message, timeout=20000)
        return self.get_text(self.error_message)
