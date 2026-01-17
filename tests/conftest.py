import pytest
import logging
import json
import os
from playwright.sync_api import Page
from pages.base_page import BasePage
from faker import Faker

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("logs/test_execution.log"), logging.StreamHandler()],
)


@pytest.fixture(scope="session")
def test_data():
    """Load test data from JSON file."""
    with open("data/test_data.json", "r") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def fake_data():
    """Generate dynamic test data."""
    fake = Faker()
    return {
        "name": fake.name(),
        "email": fake.email(),
        "message": fake.text(max_nb_chars=200)
    }

@pytest.fixture(scope="session")
def base_url():
    """Defines the application base URL."""
    return BasePage.BASE_URL

@pytest.fixture(scope="function")
def page_obj(page: Page, base_url, request):
    """
    Fixture to setup the page object with base configuration.
    Navigates to the base URL and handles global popups (cookies).
    """
    logger = logging.getLogger("Fixture")
    test_name = request.node.name
    logger.info(f"Setting up test: {test_name}")
    
    page.goto(base_url)

    try:
        cookie_btn = page.query_selector(".js-acknowledge-cookies")
        if cookie_btn:
            cookie_btn.click()
            logger.info("Dismissed cookie banner")
    except Exception:
        pass
    yield page
    
    logger.info(f"Teardown test: {test_name}")
