"""Plugin-owned browser lifecycle and explicitly requested page objects."""

import logging
import pytest
from playwright.sync_api import expect
from config.test_data import contact_data, load_data
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.shop_page import ShopPage


@pytest.fixture(scope="session")
def test_data():
    return load_data()


@pytest.fixture
def fake_data(request, settings):
    return contact_data(request.node.nodeid, settings.seed)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, pytestconfig):
    args = {**browser_context_args, "locale": "es-AR"}
    if not pytestconfig.getoption("device"):
        args["viewport"] = {"width": 1440, "height": 1000}
    return args


@pytest.fixture(autouse=True)
def configure_ui(request, settings):
    if request.node.get_closest_marker("framework"):
        return
    page = request.getfixturevalue("page")
    page.set_default_timeout(settings.action_timeout)
    page.set_default_navigation_timeout(settings.navigation_timeout)
    expect.set_options(timeout=settings.assertion_timeout)
    logging.getLogger("test").info(
        "case=%s target=%s seed=%s", request.node.nodeid, settings.target, settings.seed
    )


@pytest.fixture
def home_page(page):
    return HomePage(page)


@pytest.fixture
def shop_page(page):
    return ShopPage(page)


@pytest.fixture
def product_page(page):
    return ProductPage(page)


@pytest.fixture
def contact_page(page):
    return ContactPage(page)


@pytest.fixture
def login_page(page):
    return LoginPage(page)
