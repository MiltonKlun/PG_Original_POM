import pytest


@pytest.mark.contact
@pytest.mark.mock_only
def test_contact_form_validation(page, contact_page):
    """Observe the disabled control without overriding client validation."""
    contact_page = contact_page
    contact_page.open()
    submit_btn = page.locator(contact_page.submit_button)
    assert submit_btn.is_disabled()


@pytest.mark.contact
@pytest.mark.live_safe
def test_contact_form_fill(page, fake_data, contact_page):
    """
    Verify form can be filled using dynamic data (Faker).
    This test fills fields without submitting.
    """
    contact_page = contact_page
    contact_page.open()

    # Dynamic data
    contact_page.fill(contact_page.name_input, fake_data["name"])
    contact_page.fill(contact_page.email_input, fake_data["email"])
    contact_page.fill(contact_page.message_input, fake_data["message"])

    # Verify values stuck
    assert page.input_value(contact_page.name_input) == fake_data["name"]
