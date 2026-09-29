"""Read-only page health checks that run on both targets."""

import pytest
from config.live_policy import crawl_allowed

pytestmark = pytest.mark.live_safe

MAX_LINKS_CHECKED = 25


@pytest.mark.parametrize(
    "opened_page", ["home", "shop", "product", "contact"], indirect=True
)
def test_page_loads_without_errors(opened_page, browser_diagnostics):
    # Third-party failures (e.g. a store app's config) are out of scope here.
    opened_page.wait_for_load()
    assert browser_diagnostics.first_party_failures == []
    assert browser_diagnostics.page_errors == []


def test_home_links_resolve(home_page):
    home_page.open()
    paths = [p for p in home_page.linked_paths() if p and crawl_allowed(p)]
    assert paths, "Home page has no crawlable first-party links"
    # Evenly spaced, deterministic sample keeps live traffic small.
    sample = paths[:: max(1, len(paths) // MAX_LINKS_CHECKED)][:MAX_LINKS_CHECKED]
    broken = []
    for path in sample:
        response = home_page.page.request.get(path, max_redirects=5)
        if response.status >= 400:
            broken.append(f"{response.status} {path}")
    assert not broken, "Broken links:\n" + "\n".join(broken)
