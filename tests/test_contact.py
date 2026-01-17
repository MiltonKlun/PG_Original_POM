import pytest
from pages.contact_page import ContactPage


@pytest.mark.contact
def test_contact_form_validation(page_obj):
    """
    Verify that submitting an empty form triggers validation errors.
    This demonstrates handling of 'Disabled' buttons and Form Validation.
    """
    contact_page = ContactPage(page_obj)
    contact_page.navigate_to_contact()

    # The button is disabled by default.
    submit_btn = page_obj.locator(contact_page.submit_button)
    assert submit_btn.is_disabled(), "Submit button should be disabled initially"

    page_obj.evaluate(
        "(selector) => { const btn = document.querySelector(selector); if (btn) btn.disabled = false; }",
        contact_page.submit_button,
    )
    page_obj.wait_for_timeout(500)
    assert page_obj.is_enabled(
        contact_page.submit_button
    ), "Button failed to enable via JS hack"

    page_obj.evaluate(
        "(selector) => document.querySelector(selector).click()",
        contact_page.submit_button,
    )
    page_obj.wait_for_timeout(4000)
    error_msg = contact_page.get_error_message()
    if error_msg == "":
        pass
    assert error_msg != "", "Validation error message should appear"

@pytest.mark.contact
def test_contact_form_fill(page_obj, fake_data):
    """
    Verify form can be filled using dynamic data (Faker).
    We do NOT submit to avoid spamming the owner, or we submit and expect ReCaptcha block.
    """
    contact_page = ContactPage(page_obj)
    contact_page.navigate_to_contact()
    
    # Dynamic data
    contact_page.fill(contact_page.name_input, fake_data["name"])
    contact_page.fill(contact_page.email_input, fake_data["email"])
    contact_page.fill(contact_page.message_input, fake_data["message"])
    
    # Verify values stuck
    assert page_obj.input_value(contact_page.name_input) == fake_data["name"]
