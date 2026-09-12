import pytest
from pages.login_page import LoginPage


@pytest.mark.auth
@pytest.mark.interactive
def test_login_failure(page_obj, test_data):
    """Test that invalid credentials show an error."""
    login_page = LoginPage(page_obj)
    login_page.navigate_to_login()

    user = test_data["auth"]["invalid_user"]
    login_page.login(user["email"], user["password"])
    assert login_page.get_error_message() != "", "Error message empty"


@pytest.mark.auth
def test_forgot_password_link(page_obj):
    """Verify forgot password link works."""
    login_page = LoginPage(page_obj)
    login_page.navigate_to_login()

    assert login_page.is_visible(
        login_page.forgot_password_link
    ), "Forgot password link not visible"
    login_page.click(login_page.forgot_password_link)

    try:
        page_obj.wait_for_url("**/reset**", timeout=15000)
    except Exception:
        pass

    assert (
        "reset" in page_obj.url
    ), f"Failed to navigate to recovery. Current URL: {page_obj.url}"
