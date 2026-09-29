"""Record, build and check the snapshot target (TARGET=snapshot).

A snapshot is the live store's traffic, recorded by the read-only live suite
and replayed offline with Playwright's HAR routing. `record` runs the live
suite with --record-snapshot, then `build` merges the per-test recordings
into one sanitized file:

- one response per request (method, URL and body), preferring a success;
- no cookies and only the headers a replay needs;
- raster images replaced by a 1x1 placeholder (the store's photos are not
  republished, and the tests do not depend on image content);
- nothing from analytics, trackers or bot challenges (reCAPTCHA, Turnstile).
"""

import argparse
import ast
import base64
import json
import os
import struct
import subprocess
import sys
import zlib
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Page, sync_playwright

from config.live_policy import blocked_by
from config.settings import LIVE_ORIGIN, SNAPSHOT_HAR
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.shop_page import ShopPage

ROOT = Path(__file__).resolve().parents[1]
LIVE_SELECTION = "live_safe and not needs_network"
POM_SOURCES = ("pages", "components")
INVENTORY_PAGES = ("home", "shop", "product", "login", "contact")
# Match count per selector; null when the browser cannot parse the selector.
COUNT_MATCHES = """selectors => selectors.map(selector => {
    try { return document.querySelectorAll(selector).length; }
    catch { return null; }
})"""

# page -> selector -> matches (None: not a valid browser selector)
Inventory = dict[str, dict[str, bool | None]]
Change = tuple[str, str, bool | None, bool | None]

# Bot challenges must never be replayed; without them the widgets stay empty.
CHALLENGE_HOSTS = {"www.google.com", "www.gstatic.com", "challenges.cloudflare.com"}
KEPT_HEADERS = {"content-type", "location"}
RASTER_TYPES = ("image/png", "image/jpeg", "image/webp", "image/gif", "image/avif")


def png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data)
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


# A 1x1 transparent PNG: 8-bit RGBA, one filter byte plus one pixel.
PLACEHOLDER_PNG = (
    b"\x89PNG\r\n\x1a\n"
    + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    + png_chunk(b"IDAT", zlib.compress(bytes(5)))
    + png_chunk(b"IEND", b"")
)

Entry = dict[str, Any]


def request_key(entry: Entry) -> tuple[str, str, str]:
    request = entry["request"]
    body = (request.get("postData") or {}).get("text", "")
    return request["method"], request["url"], body


def keep(entry: Entry) -> bool:
    url = entry["request"]["url"]
    host = urlsplit(url).hostname or ""
    return (
        entry["response"]["status"] > 0  # Aborted or cancelled: nothing to replay.
        and host not in CHALLENGE_HOSTS
        and blocked_by(url) is None
    )


def headers(items: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"name": h["name"], "value": h["value"]}
        for h in items
        if h["name"].lower() in KEPT_HEADERS
        or h["name"].lower().startswith("access-control-")
    ]


def sanitize(entry: Entry) -> Entry:
    request, response = entry["request"], entry["response"]
    content = dict(response["content"])
    if content.get("mimeType", "").split(";")[0] in RASTER_TYPES:
        content = {
            "size": len(PLACEHOLDER_PNG),
            "mimeType": "image/png",
            "text": base64.b64encode(PLACEHOLDER_PNG).decode(),
            "encoding": "base64",
        }
    response_headers = [
        {"name": "content-type", "value": content["mimeType"]}
        if h["name"].lower() == "content-type"
        else h
        for h in headers(response["headers"])
    ]
    clean_request: Entry = {
        "method": request["method"],
        "url": request["url"],
        "httpVersion": request.get("httpVersion", "HTTP/1.1"),
        "cookies": [],
        "headers": headers(request["headers"]),
        "queryString": request.get("queryString", []),
        "headersSize": -1,
        "bodySize": -1,
    }
    if "postData" in request:
        clean_request["postData"] = request["postData"]
    return {
        "startedDateTime": entry["startedDateTime"],
        "time": 0,
        "request": clean_request,
        "response": {
            "status": response["status"],
            "statusText": response.get("statusText", ""),
            "httpVersion": response.get("httpVersion", "HTTP/1.1"),
            "cookies": [],
            "headers": response_headers,
            "content": content,
            "headersSize": -1,
            "bodySize": -1,
            "redirectURL": response.get("redirectURL", ""),
        },
        "cache": {},
        "timings": {"send": 0, "wait": 0, "receive": 0},
    }


def merge(recordings: Iterable[Path]) -> list[Entry]:
    """One sanitized entry per request; a success wins over an error status."""
    chosen: dict[tuple[str, str, str], Entry] = {}
    for path in sorted(recordings):
        har = json.loads(path.read_text(encoding="utf-8"))
        for entry in filter(keep, har["log"]["entries"]):
            key = request_key(entry)
            previous = chosen.get(key)
            if previous is None or (
                previous["response"]["status"] >= 400 > entry["response"]["status"]
            ):
                chosen[key] = entry
    return [sanitize(chosen[key]) for key in sorted(chosen)]


def build(raw: Path, output: Path) -> dict[str, int]:
    recordings = list(raw.glob("*.har"))
    if not recordings:
        raise SystemExit(f"No recordings in {raw}")
    entries = merge(recordings)
    har = {
        "log": {
            "version": "1.2",
            "creator": {"name": "PG_Original_POM snapshot", "version": "1"},
            "entries": entries,
        }
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(har, indent=1, ensure_ascii=False) + "\n", "utf-8")
    return {"recordings": len(recordings), "entries": len(entries)}


def record(raw: Path, run_id: str) -> int:
    """Run the read-only live suite serially, recording each test."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-m",
            LIVE_SELECTION,
            "-p",
            "no:cacheprovider",
            "--record-snapshot",
            str(raw),
            "--run-id",
            run_id,
        ],
        cwd=ROOT,
        env={**os.environ, "TARGET": "live"},
        check=False,
    ).returncode


def pom_selectors(root: Path = ROOT) -> list[str]:
    """CSS selectors the page objects pass to locator(), as literal strings.

    Playwright's own `:visible` filter is dropped so the browser can evaluate
    the selector; selectors built at run time (f-strings) are not included.
    """
    found: set[str] = set()
    for folder in POM_SOURCES:
        for path in sorted((root / folder).glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "locator"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    found.add(node.args[0].value.replace(":visible", ""))
    return sorted(found)


def page_openers(page: Page) -> dict[str, Callable[[], object]]:
    """The pages the read-only suite covers, opened through the page objects."""
    shop = ShopPage(page)

    def product() -> object:
        return shop.open().open_product(shop.first_product_name())

    return {
        "home": HomePage(page).open,
        "shop": shop.open,
        "product": product,
        "login": LoginPage(page).open,
        "contact": ContactPage(page).open,
    }


def inventory(har: Path, selectors: list[str]) -> Inventory:
    """Which POM selectors match on each page of a recording (None: invalid)."""
    result: Inventory = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(
                base_url=LIVE_ORIGIN,
                locale="es-AR",
                viewport={"width": 1440, "height": 1000},
                service_workers="block",
            )
            # Offline: the recording answers, anything else is aborted.
            context.route("**/*", lambda route: route.abort())
            context.route_from_har(har, not_found="fallback")
            page = context.new_page()
            for name, open_page in page_openers(page).items():
                open_page()
                page.wait_for_load_state("load")
                counts = page.evaluate(COUNT_MATCHES, selectors)
                result[name] = {
                    selector: None if count is None else count > 0
                    for selector, count in zip(selectors, counts, strict=True)
                }
        finally:
            browser.close()
    return result


PageMatches = Mapping[str, Mapping[str, bool | None]]


def drift(before: PageMatches, after: PageMatches) -> tuple[list[Change], list[Change]]:
    """Return (selectors that stopped matching, every other change)."""
    lost: list[Change] = []
    other: list[Change] = []
    for page in sorted(before.keys() | after.keys()):
        was, now = before.get(page, {}), after.get(page, {})
        for selector in sorted(was.keys() | now.keys()):
            change = (page, selector, was.get(selector), now.get(selector))
            if change[2] is True and change[3] is not True:
                lost.append(change)
            elif change[2] != change[3]:
                other.append(change)
    return lost, other


def render_drift(lost: list[Change], other: list[Change], selectors: int) -> str:
    def rows(changes: list[Change]) -> list[str]:
        state = {True: "matches", False: "no match", None: "n/a"}
        return ["| Page | Selector | Committed | Live now |", "|---|---|---|---|"] + [
            f"| {page} | `{selector}` | {state[was]} | {state[now]} |"
            for page, selector, was, now in changes
        ]

    lines = [
        "## Snapshot drift",
        "",
        f"{selectors} page-object selectors compared on {len(INVENTORY_PAGES)} "
        f"pages: **{len(lost)} no longer match**, {len(other)} other changes.",
        "",
    ]
    if lost:
        lines += ["Selectors the page objects rely on that stopped matching:", ""]
        lines += [*rows(lost), ""]
    if other:
        lines += ["Other changes (informational):", "", *rows(other), ""]
    return "\n".join(lines)


def compare(committed: Path, fresh: Path, output: Path) -> int:
    selectors = pom_selectors()
    before, after = inventory(committed, selectors), inventory(fresh, selectors)
    lost, other = drift(before, after)
    markdown = render_drift(lost, other, len(selectors))
    output.mkdir(parents=True, exist_ok=True)
    for name, data in (("committed", before), ("fresh", after)):
        (output / f"inventory-{name}.json").write_text(
            json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
    (output / "drift.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with Path(step_summary).open("a", encoding="utf-8") as stream:
            stream.write(markdown)
    return 1 if lost else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    rec = commands.add_parser("record", help="Record the live store and build")
    rec.add_argument("--output", type=Path, default=SNAPSHOT_HAR)
    bld = commands.add_parser("build", help="Build from existing recordings")
    bld.add_argument("raw", type=Path)
    bld.add_argument("--output", type=Path, default=SNAPSHOT_HAR)
    cmp = commands.add_parser("compare", help="Selector drift between recordings")
    cmp.add_argument("fresh", type=Path)
    cmp.add_argument("--committed", type=Path, default=SNAPSHOT_HAR)
    cmp.add_argument("--output", type=Path, default=ROOT / "reports" / "snapshot")
    args = parser.parse_args(argv)

    if args.command == "compare":
        return compare(args.committed, args.fresh, args.output)
    if args.command == "record":
        stamp = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
        raw = ROOT / "reports" / f"snapshot-raw-{stamp}"
        code = record(raw, f"snapshot-record-{stamp}")
        if code not in (0, 1):  # 1: test failures, still a faithful recording.
            print(f"Live recording run did not complete (exit {code})")
            return code
    else:
        raw = args.raw
    print(json.dumps(build(raw, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
