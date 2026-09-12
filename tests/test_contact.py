import pytest
from playwright.sync_api import expect


@pytest.mark.contact
@pytest.mark.mock_only
def test_contact_form_validation(contact_page):
    contact_page.open()
    expect(contact_page.submit_button).to_be_disabled()
    contact_page.fill_form("QA Example", "invalid-email", "Non-submitting check")
    expect(contact_page.invalid_email).to_be_visible()


@pytest.mark.contact
@pytest.mark.live_safe
def test_contact_form_fill(contact_page, fake_data):
    contact_page.open()
    contact_page.fill_form(**fake_data)
    expect(contact_page.name_input).to_have_value(fake_data["name"])
    expect(contact_page.email_input).to_have_value(fake_data["email"])
    expect(contact_page.message_input).to_have_value(fake_data["message"])
