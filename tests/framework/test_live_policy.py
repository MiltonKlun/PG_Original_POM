import pytest

from config.live_policy import blocked_by, crawl_allowed

pytestmark = pytest.mark.framework


@pytest.mark.parametrize(
    "url",
    [
        "https://connect.facebook.net/signals/config/260193131258697",
        "https://static.cloudflareinsights.com/beacon.min.js",
        "https://log.pinterest.com/",
        "https://recomendaciones-sdk.crossup-templates.pages.dev/_next/static/a.js",
        "https://api.crossup.ai/brain/v1/suggestions/get-suggestions",
        "https://apps-telemetry-collector-v2.tiendanube.com/v1/traces",
        "https://unpkg.com/web-vitals@3.5.2/dist/web-vitals.js",
        "https://www.pgoriginal.com/stats/record_visit/",
    ],
)
def test_observed_tracking_requests_are_blocked(url):
    assert blocked_by(url) is not None


@pytest.mark.parametrize(
    "url",
    [
        "https://www.pgoriginal.com/productos/remeras-mw-mustang/",
        "https://acdn-us.mitiendanube.com/stores/693/159/products/img.webp",
        "https://nsk-cdn-static.tiendanube.com/initializer-0.47.0.min.js",
        "https://fonts.gstatic.com/s/roboto/v48/font.woff2",
        "https://www.google.com/recaptcha/api2/webworker.js",
        "https://unpkg.com/some-library/dist/lib.js",
        "https://notfacebook.net/page",
    ],
)
def test_storefront_resources_are_not_blocked(url):
    assert blocked_by(url) is None


@pytest.mark.parametrize(
    "path,allowed",
    [
        ("/productos/", True),
        ("/pg-racing/actc/", True),
        ("/account/login/", False),
        ("/account/register", False),
        ("/search/", False),
        ("/comprar/", False),
    ],
)
def test_link_checks_respect_robots(path, allowed):
    assert crawl_allowed(path) is allowed
