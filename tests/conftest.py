"""Plugin-owned browser lifecycle and explicitly requested page objects."""

import logging
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Error,
    Page,
    Request,
    Response,
    Route,
    expect,
)

from config import live_policy
from config.settings import Settings
from config.test_data import ContactInput, SuiteData, contact_data, load_data
from pages.base_page import BasePage
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


def default_user_agent(browser: Browser) -> str:
    context = browser.new_context()
    try:
        return str(context.new_page().evaluate("navigator.userAgent"))
    finally:
        context.close()


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any],
    pytestconfig: pytest.Config,
    settings: Settings,
    request: pytest.FixtureRequest,
) -> dict[str, Any]:
    args = {**browser_context_args, "locale": "es-AR"}
    if not pytestconfig.getoption("device"):
        args["viewport"] = {"width": 1440, "height": 1000}
    if settings.target == "live":
        # Identify weekly live traffic; keep any device emulation user agent.
        base = args.get("user_agent") or default_user_agent(
            request.getfixturevalue("browser")
        )
        args["user_agent"] = f"{base} {live_policy.USER_AGENT_SUFFIX}"
    return args


@pytest.fixture
def network_guard(context: BrowserContext, settings: Settings) -> Iterator[None]:
    """Mock: abort any request leaving the mock origin, and fail the test.
    Live: abort analytics and tracking requests (config/live_policy.py)."""
    external: list[str] = []
    blocked: Counter[str] = Counter()

    def forbidden(url: str) -> bool:
        return urlsplit(url).scheme in {"http", "https"} and origin(url) != origin(
            settings.base_url
        )

    def record(request: Request) -> None:
        if settings.target == "mock" and forbidden(request.url):
            parts = urlsplit(request.url)
            external.append(f"{parts.scheme}://{parts.netloc}{parts.path}")

    def guard(route: Route) -> None:
        url = route.request.url
        rule = live_policy.blocked_by(url) if settings.target == "live" else None
        if rule is not None:
            blocked[rule.purpose] += 1
            route.abort("blockedbyclient")
        elif settings.target == "mock" and forbidden(url):
            route.abort()
        else:
            route.continue_()

    # Request events also report redirects that do not invoke route handlers.
    context.on("request", record)
    context.route("**/*", guard)
    yield
    if blocked:
        browser_log.info("Blocked tracking requests: %s", dict(blocked))
    assert not external, f"Mock attempted external requests: {external}"


@pytest.fixture
def ui_timeouts(page: Page, settings: Settings) -> None:
    page.set_default_timeout(settings.action_timeout)
    page.set_default_navigation_timeout(settings.navigation_timeout)
    expect.set_options(timeout=settings.assertion_timeout)


@dataclass
class Diagnostics:
    """Problems the page itself reported while the test ran."""

    page_errors: list[str] = field(default_factory=list)
    first_party_failures: list[str] = field(default_factory=list)


@pytest.fixture
def browser_diagnostics(page: Page, settings: Settings) -> Diagnostics:
    """Record uncaught JavaScript errors and failed first-party responses."""
    first_party = urlsplit(settings.base_url).hostname
    found = Diagnostics()

    def page_error(error: Error) -> None:
        # Keep the error type only: messages may contain page or session data.
        found.page_errors.append(error.name or "Error")
        browser_log.error("JavaScript error: %s", error.name)

    def failed_response(response: Response) -> None:
        parts = urlsplit(response.url)
        if parts.hostname == first_party and response.status >= 400:
            found.first_party_failures.append(f"HTTP {response.status} {parts.path}")
            browser_log.error("First-party HTTP %s %s", response.status, parts.path)

    page.on("pageerror", page_error)
    page.on("response", failed_response)
    return found


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
def opened_page(
    request: pytest.FixtureRequest,
    home_page: HomePage,
    shop_page: ShopPage,
    login_page: LoginPage,
    contact_page: ContactPage,
) -> BasePage:
    """Open the page named by indirect parametrization."""
    if request.param == "product":
        shop_page.open()
        return shop_page.open_product(shop_page.first_product_name())
    pages: dict[str, BasePage] = {
        "home": home_page,
        "shop": shop_page,
        "login": login_page,
        "contact": contact_page,
    }
    return pages[request.param].open()


@pytest.fixture
def catalog_name(settings: Settings, test_data: SuiteData, shop_page: ShopPage) -> str:
    if settings.target == "mock":
        return test_data.shop.shirt.name
    shop_page.open()
    return shop_page.first_product_name()
