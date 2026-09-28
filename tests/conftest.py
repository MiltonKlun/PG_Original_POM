"""Plugin-owned browser lifecycle and explicitly requested page objects."""

import logging
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import (
    BrowserContext,
    Error,
    Page,
    Request,
    Response,
    Route,
    expect,
)

from config.settings import Settings
from config.test_data import ContactInput, SuiteData, contact_data, load_data
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.shop_page import ShopPage

browser_log = logging.getLogger("browser")


def origin(url: str) -> tuple[str, str | None, int]:
    parts = urlsplit(url)
    return (
        parts.scheme,
        parts.hostname,
        parts.port or (443 if parts.scheme == "https" else 80),
    )


@pytest.fixture(scope="session")
def test_data() -> SuiteData:
    return load_data()


@pytest.fixture
def fake_data(request: pytest.FixtureRequest, settings: Settings) -> ContactInput:
    return contact_data(request.node.nodeid, settings.seed)


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], pytestconfig: pytest.Config
) -> dict[str, Any]:
    args = {**browser_context_args, "locale": "es-AR"}
    if not pytestconfig.getoption("device"):
        args["viewport"] = {"width": 1440, "height": 1000}
    return args


@pytest.fixture
def network_guard(context: BrowserContext, settings: Settings) -> Iterator[None]:
    """In mock runs, abort and report any request that leaves the mock origin."""
    external: list[str] = []
    if settings.target == "mock":

        def forbidden(url: str) -> bool:
            return urlsplit(url).scheme in {"http", "https"} and origin(url) != origin(
                settings.base_url
            )

        def record(request: Request) -> None:
            if forbidden(request.url):
                parts = urlsplit(request.url)
                external.append(f"{parts.scheme}://{parts.netloc}{parts.path}")

        def guard(route: Route) -> None:
            if forbidden(route.request.url):
                route.abort()
            else:
                route.continue_()

        # Request events also report redirects that do not invoke route handlers.
        context.on("request", record)
        context.route("**/*", guard)
    yield
    assert not external, f"Mock attempted external requests: {external}"


@pytest.fixture
def ui_timeouts(page: Page, settings: Settings) -> None:
    page.set_default_timeout(settings.action_timeout)
    page.set_default_navigation_timeout(settings.navigation_timeout)
    expect.set_options(timeout=settings.assertion_timeout)


@pytest.fixture
def browser_diagnostics(page: Page, settings: Settings) -> None:
    """Log JavaScript error types and failed first-party responses."""
    first_party = urlsplit(settings.base_url).hostname

    def page_error(error: Error) -> None:
        # Capture error types without copying potentially sensitive JS messages.
        browser_log.error("JavaScript error: %s", error.name)

    def failed_response(response: Response) -> None:
        parts = urlsplit(response.url)
        if parts.hostname == first_party and response.status >= 400:
            browser_log.error("First-party HTTP %s %s", response.status, parts.path)

    page.on("pageerror", page_error)
    page.on("response", failed_response)


@pytest.fixture(autouse=True)
def configure_ui(request: pytest.FixtureRequest, settings: Settings) -> None:
    if request.node.get_closest_marker("framework"):
        return
    # Guard first so routing is in place before any page navigates.
    for name in ("network_guard", "ui_timeouts", "browser_diagnostics"):
        request.getfixturevalue(name)
    logging.getLogger("test").info(
        "case=%s target=%s seed=%s", request.node.nodeid, settings.target, settings.seed
    )


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def shop_page(page: Page) -> ShopPage:
    return ShopPage(page)


@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


@pytest.fixture
def contact_page(page: Page) -> ContactPage:
    return ContactPage(page)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def catalog_name(settings: Settings, test_data: SuiteData, shop_page: ShopPage) -> str:
    if settings.target == "mock":
        return test_data.shop.shirt.name
    shop_page.open()
    return shop_page.first_product_name()
