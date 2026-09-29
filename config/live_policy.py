"""Rules that keep read-only live runs from polluting the store's analytics.

Observed on 2026-09-28: a page load on pgoriginal.com contacts ad pixels,
recommendation widgets, telemetry collectors and the store's own visit
counter. Live runs abort those requests; everything the storefront needs to
render and behave (platform scripts, CDN images, fonts, reCAPTCHA) still loads.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

# Appended to the browser's own user agent so the store can identify, and
# filter, this suite's weekly traffic.
USER_AGENT_SUFFIX = "PGOriginalQA/1.0 (+https://github.com/MiltonKlun/PG_Original_POM)"


@dataclass(frozen=True)
class BlockRule:
    host: str  # Matches the host and its subdomains.
    path_prefix: str
    purpose: str

    def matches(self, url: str) -> bool:
        parts = urlsplit(url)
        host = parts.hostname or ""
        on_host = host == self.host or host.endswith("." + self.host)
        return on_host and parts.path.startswith(self.path_prefix)


BLOCK_RULES = (
    BlockRule("facebook.net", "/", "Meta Pixel"),
    BlockRule("facebook.com", "/", "Meta Pixel"),
    BlockRule("cloudflareinsights.com", "/", "Cloudflare Web Analytics"),
    BlockRule("pinterest.com", "/", "Pinterest tag and widgets"),
    BlockRule("crossup.ai", "/", "Recommendation widget"),
    BlockRule("crossup-templates.pages.dev", "/", "Recommendation widget"),
    BlockRule("apps-telemetry-collector-v2.tiendanube.com", "/", "App telemetry"),
    BlockRule("unpkg.com", "/web-vitals", "Real-user performance monitoring"),
    BlockRule("google-analytics.com", "/", "Google Analytics"),
    BlockRule("googletagmanager.com", "/", "Google Tag Manager"),
    BlockRule("doubleclick.net", "/", "Google ads"),
    BlockRule("www.pgoriginal.com", "/stats/", "Store visit statistics"),
)

# From https://www.pgoriginal.com/robots.txt: paths crawlers must not fetch.
# Link checks skip them; scenario tests visit /account/ and /search/ only as
# a user would, serially and weekly, with the owner's permission.
ROBOTS_DISALLOWED = (
    "/admin/",
    "/account/",
    "/checkout/",
    "/discount/",
    "/comprar/",
    "/comprar-express/",
    "/completar-compra-express/",
    "/search/",
    "/envio/",
    "/fb-comment/",
    "/ar/comprar/",
    "/ar/comprar-express/",
    "/ar/completar-compra-express/",
)


def blocked_by(url: str) -> BlockRule | None:
    return next((rule for rule in BLOCK_RULES if rule.matches(url)), None)


def crawl_allowed(path: str) -> bool:
    normalized = path if path.endswith("/") else path + "/"
    return not any(normalized.startswith(prefix) for prefix in ROBOTS_DISALLOWED)
