import pytest
from pages.contact_page import ContactPage


@pytest.mark.contact
@pytest.mark.interactive
def test_contact_form_validation(page_obj):
    """Observe the disabled control without overriding client validation."""
    contact_page = ContactPage(page_obj)
    contact_page.navigate_to_contact()
    submit_btn = page_obj.locator(contact_page.submit_button)
    assert submit_btn.is_disabled()


@pytest.mark.contact
def test_contact_form_fill(page_obj, fake_data):
    """
    Verify form can be filled using dynamic data (Faker).
    This test fills fields without submitting.
    """
    contact_page = ContactPage(page_obj)
    contact_page.navigate_to_contact()

    # Dynamic data
    contact_page.fill(contact_page.name_input, fake_data["name"])
    contact_page.fill(contact_page.email_input, fake_data["email"])
    contact_page.fill(contact_page.message_input, fake_data["message"])

    # Verify values stuck
    assert page_obj.input_value(contact_page.name_input) == fake_data["name"]
