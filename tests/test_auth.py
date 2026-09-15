import re
import pytest
from playwright.sync_api import expect
from config.test_data import load_data


@pytest.mark.auth
@pytest.mark.mock_only
@pytest.mark.parametrize(
    "user", load_data()["auth"]["invalid_users"], ids=lambda user: user["id"]
)
def test_login_failure(login_page, user):
    login_page.open()
    login_page.fill_credentials(user["email"], user["password"])
    login_page.submit()
    expect(login_page.error_message).to_have_text("Credenciales incorrectas")
    expect(login_page.form).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/account/login/?$"))


@pytest.mark.auth
@pytest.mark.mock_only
@pytest.mark.parametrize(
    "email,password",
    [("not-an-email", "unused"), ("", "unused"), ("qa@example.com", "")],
    ids=["malformed-email", "missing-email", "missing-password"],
)
def test_login_native_validation(login_page, email, password):
    login_page.open()
    login_page.fill_credentials(email, password)
    expect(login_page.invalid_inputs).to_have_count(1)
    expect(login_page.error_message).to_be_hidden()


@pytest.mark.auth
@pytest.mark.live_safe
def test_forgot_password_link(login_page):
    login_page.open()
    login_page.open_password_reset()
