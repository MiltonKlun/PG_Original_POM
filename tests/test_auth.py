import pytest


@pytest.mark.auth
@pytest.mark.mock_only
def test_login_failure(page, test_data, login_page):
    """Test that invalid credentials show an error."""
    login_page = login_page
    login_page.open()

    user = test_data["auth"]["invalid_user"]
    login_page.login(user["email"], user["password"])
    assert login_page.get_error_message() != "", "Error message empty"


@pytest.mark.auth
def test_forgot_password_link(page, login_page):
    """Verify forgot password link works."""
    login_page = login_page
    login_page.open()

    assert login_page.is_visible(
        login_page.forgot_password_link
    ), "Forgot password link not visible"
    login_page.click(login_page.forgot_password_link)

    try:
        page.wait_for_url("**/reset**", timeout=15000)
    except Exception:
        pass

    assert (
        "reset" in page.url
    ), f"Failed to navigate to recovery. Current URL: {page.url}"
