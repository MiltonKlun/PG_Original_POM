import pytest
from playwright.sync_api import expect


@pytest.mark.auth
@pytest.mark.mock_only
def test_login_failure(login_page, test_data):
    login_page.open()
    user = test_data["auth"]["invalid_user"]
    login_page.fill_credentials(user["email"], user["password"])
    login_page.submit()
    expect(login_page.error_message).to_have_text("Credenciales incorrectas")
    expect(login_page.form).to_be_visible()


@pytest.mark.auth
@pytest.mark.live_safe
def test_forgot_password_link(login_page):
    login_page.open()
    login_page.open_password_reset()
