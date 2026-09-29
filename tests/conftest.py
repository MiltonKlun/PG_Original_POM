"""Plugin-owned browser lifecycle and explicitly requested page objects."""

import logging
import re
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Error,
    Locator,
    Page,
    Request,
    Response,
    Route,
    expect,
)

from config import live_policy
from config.settings import Settings
from config.test_data import ContactInput, SuiteData, contact_data, load_data
from config.visual import baseline_path, compare_images
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
    if settings.replays_store or pytestconfig.getoption("record_snapshot"):
        # Service worker requests bypass routing, so they could be neither
        # recorded nor replayed.
        args["service_workers"] = "block"
    return args


@pytest.fixture
def network_guard(
    context: BrowserContext, settings: Settings, pytestconfig: pytest.Config
) -> Iterator[None]:
    """Mock: abort any request leaving the mock origin, and fail the test.
    Live: abort analytics and tracking requests (config/live_policy.py).
    Snapshot: serve the recording; abort anything it does not contain."""
    external: list[str] = []
    blocked: Counter[str] = Counter()
    unrecorded: Counter[str] = Counter()

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
        if settings.replays_store:
            # Reached only when the recording has no matching entry.
            unrecorded[urlsplit(url).hostname or "?"] += 1
            route.abort("internetdisconnected")
        elif rule is not None:
            blocked[rule.purpose] += 1
            route.abort("blockedbyclient")
        elif settings.target == "mock" and forbidden(url):
            route.abort()
        else:
            route.continue_()

    # Request events also report redirects that do not invoke route handlers.
    context.on("request", record)
    context.route("**/*", guard)
    if settings.replays_store:
        # Registered last, so it answers first; misses fall back to the guard.
        context.route_from_har(
            pytestconfig.getoption("snapshot_har"), not_found="fallback"
        )
    yield
    if blocked:
        browser_log.info("Blocked tracking requests: %s", dict(blocked))
    if unrecorded:
        browser_log.info("Requests missing from the snapshot: %s", dict(unrecorded))
    assert not external, f"Mock attempted external requests: {external}"


@pytest.fixture
def snapshot_recorder(
    request: pytest.FixtureRequest, context: BrowserContext, pytestconfig: pytest.Config
) -> None:
    """Record this test's live traffic; the HAR is written when the context
    closes. scripts/snapshot.py merges and sanitizes the recordings."""
    folder = pytestconfig.getoption("record_snapshot")
    if folder is None:
        return
    folder.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    context.route_from_har(
        folder / f"{name}.har",
        update=True,
        update_content="embed",
        update_mode="minimal",
    )


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
    names = ("network_guard", "snapshot_recorder", "ui_timeouts", "browser_diagnostics")
    for name in names:
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


VisualCheck = Callable[[Page | Locator, str], None]


@pytest.fixture
def visual_check(
    pytestconfig: pytest.Config, browser_name: str, output_path: str
) -> VisualCheck:
    """Compare a screenshot with its reviewed baseline (config/visual.py)."""
    update = pytestconfig.getoption("update_baselines")
    if not (update or pytestconfig.getoption("visual")):
        # Fonts differ between machines: only the reference container's
        # rendering matches the baselines.
        pytest.skip("Visual checks run in the reference container: scripts/visual.py")
    if browser_name != "chromium" or pytestconfig.getoption("device"):
        pytest.skip("Visual baselines are reviewed for desktop Chromium only")

    def check(target: Page | Locator, name: str) -> None:
        if isinstance(target, Page):
            actual = target.screenshot(
                full_page=True, animations="disabled", caret="hide"
            )
        else:
            actual = target.screenshot(animations="disabled", caret="hide")
        baseline = baseline_path(name)
        if update:
            baseline.parent.mkdir(parents=True, exist_ok=True)
            baseline.write_bytes(actual)
            return
        evidence = Path(output_path)
        evidence.mkdir(parents=True, exist_ok=True)
        if not baseline.is_file():
            (evidence / f"{name}-actual.png").write_bytes(actual)
            pytest.fail(
                f"No reviewed baseline {baseline.name}: run scripts/visual.py"
                " --update, review the image and commit it"
            )
        result = compare_images(actual, baseline.read_bytes())
        if not result.passed:
            (evidence / f"{name}-actual.png").write_bytes(actual)
            (evidence / f"{name}-expected.png").write_bytes(baseline.read_bytes())
            if result.diff_png:
                (evidence / f"{name}-diff.png").write_bytes(result.diff_png)
            pytest.fail(f"{name} differs from {baseline.name}: {result.describe()}")

    return check
