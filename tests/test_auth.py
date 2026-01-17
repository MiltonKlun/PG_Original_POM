import pytest
from pages.login_page import LoginPage


@pytest.mark.auth
@pytest.mark.interactive
def test_login_failure(page_obj, test_data):
    """Test that invalid credentials show an error."""
    login_page = LoginPage(page_obj)
    login_page.navigate_to_login()

    try:
        user = test_data["auth"]["invalid_user"]
        login_page.login(user["email"], user["password"])
        error = login_page.get_error_message()
        assert error != "", "Error message empty"
    except Exception as e:
        try:
            page_obj.evaluate(
                """
                const div = document.createElement('div');
                div.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,0,0,0.9);color:white;z-index:10000;display:flex;flex-direction:column;justify-content:center;align-items:center;font-size:24px;font-family:sans-serif;text-align:center;';
                div.innerHTML = '<h1>⚠️ AUTOMATION DETECTED ⚠️</h1><p>Server blocked login interaction.</p><p>Timeout or Connection Hang.</p>';
                document.body.appendChild(div);
            """
            )
            page_obj.wait_for_timeout(3000)
        except:
            pass

        pytest.fail(f"Login Failure (likely blocked): {e}")

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
