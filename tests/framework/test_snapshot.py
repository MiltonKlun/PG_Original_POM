import base64
import json

import pytest

from scripts.snapshot import (
    PLACEHOLDER_PNG,
    build,
    drift,
    merge,
    pom_selectors,
    render_drift,
)

pytestmark = pytest.mark.framework

HOME = "https://www.pgoriginal.com/"


def entry(url, status=200, mime="text/html", text="<html></html>", **request):
    return {
        "startedDateTime": "2026-09-29T12:00:00.000Z",
        "request": {
            "method": request.get("method", "GET"),
            "url": url,
            "headers": [
                {"name": "Cookie", "value": "session=secret"},
                {"name": "User-Agent", "value": "browser"},
            ],
            **({"postData": request["post"]} if "post" in request else {}),
        },
        "response": {
            "status": status,
            "headers": [
                {"name": "Content-Type", "value": mime},
                {"name": "Set-Cookie", "value": "session=secret"},
                {"name": "Access-Control-Allow-Origin", "value": "*"},
                {"name": "Server", "value": "cloudflare"},
            ],
            "content": {"size": len(text), "mimeType": mime, "text": text},
        },
    }


def write_har(path, *entries):
    path.write_text(json.dumps({"log": {"entries": list(entries)}}), "utf-8")
    return path


def test_success_wins_over_an_error_for_the_same_request(tmp_path):
    first = write_har(tmp_path / "a.har", entry(HOME, status=503, text="down"))
    second = write_har(tmp_path / "b.har", entry(HOME, text="up"))
    [kept] = merge([first, second])
    assert kept["response"]["content"]["text"] == "up"


def test_requests_differing_by_body_are_kept_apart(tmp_path):
    one = entry(HOME, method="POST", post={"text": "page=1"}, text="1")
    two = entry(HOME, method="POST", post={"text": "page=2"}, text="2")
    har = write_har(tmp_path / "a.har", one, two)
    assert len(merge([har])) == 2


def test_trackers_challenges_and_aborted_requests_are_dropped(tmp_path):
    har = write_har(
        tmp_path / "a.har",
        entry("https://connect.facebook.net/en_US/fbevents.js"),
        entry("https://www.pgoriginal.com/stats/visit"),
        entry("https://www.google.com/recaptcha/api2/anchor"),
        entry("https://challenges.cloudflare.com/turnstile/v0/api.js"),
        entry("https://acdn-us.mitiendanube.com/app.js", status=-1),
        entry(HOME),
    )
    assert [e["request"]["url"] for e in merge([har])] == [HOME]


def test_cookies_and_unneeded_headers_are_removed(tmp_path):
    [kept] = merge([write_har(tmp_path / "a.har", entry(HOME))])
    assert kept["request"]["headers"] == []
    names = {h["name"].lower() for h in kept["response"]["headers"]}
    assert names == {"content-type", "access-control-allow-origin"}
    assert "secret" not in json.dumps(kept)


def test_raster_images_become_a_placeholder(tmp_path):
    photo = entry(HOME + "photo.webp", mime="image/webp", text="UklGRi4AAABXRUJQ")
    icon = entry(HOME + "icon.svg", mime="image/svg+xml", text="<svg/>")
    kept = {
        e["request"]["url"]: e
        for e in merge([write_har(tmp_path / "a.har", photo, icon)])
    }
    content = kept[HOME + "photo.webp"]["response"]["content"]
    assert base64.b64decode(content["text"]) == PLACEHOLDER_PNG
    assert content["mimeType"] == "image/png"
    assert kept[HOME + "icon.svg"]["response"]["content"]["text"] == "<svg/>"


def test_build_writes_one_sorted_recording(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    write_har(raw / "b.har", entry(HOME + "b"))
    write_har(raw / "a.har", entry(HOME + "a"), entry(HOME + "b"))
    output = tmp_path / "out" / "store.har"
    assert build(raw, output) == {"recordings": 2, "entries": 2}
    urls = [
        e["request"]["url"]
        for e in json.loads(output.read_text("utf-8"))["log"]["entries"]
    ]
    assert urls == [HOME + "a", HOME + "b"]


def test_selector_inventory_comes_from_the_page_objects():
    selectors = pom_selectors()
    assert {"#modal-cart", "#product_form", ".item-product"} <= set(selectors)
    # Playwright's :visible filter is dropped; run-time f-strings are skipped.
    assert ".js-filter-checkbox" in selectors
    assert not any(":visible" in s or "{" in s for s in selectors)


def test_only_selectors_that_stop_matching_are_drift():
    before = {"shop": {".item-product": True, ".js-load-more": False, "a": True}}
    after = {"shop": {".item-product": False, ".js-load-more": True, "a": True}}
    lost, other = drift(before, after)
    assert lost == [("shop", ".item-product", True, False)]
    assert other == [("shop", ".js-load-more", False, True)]


def test_a_page_missing_from_the_new_recording_loses_its_selectors():
    lost, _ = drift({"login": {"#login-form": True}}, {})
    assert lost == [("login", "#login-form", True, None)]


def test_drift_report_lists_lost_selectors():
    report = render_drift([("shop", ".item-product", True, False)], [], 30)
    assert "30 page-object selectors" in report
    assert "**1 no longer match**" in report
    assert "| shop | `.item-product` | matches | no match |" in report
