"""Read-only catalog checks that run on both targets.

They discover their data from what the listing publishes, so no live price
or product is hard-coded, and they never add to cart.
"""

from typing import Any
import pytest
from playwright.sync_api import expect
from config.money import ars_minor_units

pytestmark = [pytest.mark.shop, pytest.mark.live_safe]

MAX_VARIANTS_CHECKED = 6


def option_values(variant: dict[str, Any]) -> list[str]:
    keys = sorted(k for k in variant if k.startswith("option") and variant[k])
    return [variant[k] for k in keys]


def test_listing_cards_match_their_variant_data(shop_page):
    shop_page.open()
    cards = shop_page.card_summaries()
    assert cards, "Listing shows no products"
    problems = []
    for card in cards:
        prices = [v["price_number_raw"] for v in card.variants]
        if not card.variants or any(type(p) is not int or p <= 0 for p in prices):
            problems.append(f"{card.name}: missing or non-positive variant prices")
            continue
        if card.displayed_price != card.variants[0]["price_short"]:
            problems.append(
                f"{card.name}: shows {card.displayed_price}, "
                f"first variant costs {card.variants[0]['price_short']}"
            )
        for variant in card.variants:
            compare = variant.get("compare_at_price_number_raw")
            if compare is not None and compare <= variant["price_number_raw"]:
                problems.append(f"{card.name}: compare-at price not above price")
        if card.sold_out == any(v["available"] for v in card.variants):
            problems.append(f"{card.name}: 'Sin stock' label disagrees with stock")
    assert not problems, "\n".join(problems)


def open_first_available(shop_page):
    shop_page.open()
    card = next(c for c in shop_page.card_summaries() if not c.sold_out)
    product = shop_page.open_product(card.name)
    expect(product.heading).to_have_text(card.name)
    return card, product


def test_product_page_price_matches_listing(shop_page):
    card, product = open_first_available(shop_page)
    shown = ars_minor_units(product.price.inner_text())
    raw = product.price.get_attribute("data-product-price")
    assert raw is not None
    assert shown == ars_minor_units(card.displayed_price), "Listing and page differ"
    assert shown == int(raw), "Displayed price differs from data-product-price"


@pytest.mark.live_defect(
    "DEF-01: live product pages publish JSON-LD only for related products, "
    "never for the product being viewed (observed 2026-09-28)"
)
def test_product_page_publishes_its_price_as_structured_data(shop_page):
    _, product = open_first_available(shop_page)
    shown = ars_minor_units(product.price.inner_text())
    assert shown == product.structured_price(), "Displayed price differs from JSON-LD"


def test_variant_prices_follow_selection(shop_page):
    # Pick a product whose variants have different prices, then check one
    # variant per price/compare-at combination against the published data.
    shop_page.open()
    card = next(
        (
            c
            for c in shop_page.card_summaries()
            if len({v["price_number_raw"] for v in c.variants if v["available"]}) > 1
        ),
        None,
    )
    if card is None:
        pytest.skip("No product on the first listing page has variant-based prices")
    samples: dict[tuple[Any, Any], dict[str, Any]] = {}
    for variant in card.variants:
        key = (variant["price_short"], variant.get("compare_at_price_short"))
        if variant["available"]:
            samples.setdefault(key, variant)
    product = shop_page.open_product(card.name)
    for variant in list(samples.values())[:MAX_VARIANTS_CHECKED]:
        product.select_options(*option_values(variant))
        expect(product.price).to_have_text(variant["price_short"])
        if variant.get("compare_at_price_short"):
            expect(product.compare_price).to_have_text(
                variant["compare_at_price_short"]
            )
        else:
            expect(product.compare_price).to_be_hidden()


def test_size_filter_results_offer_the_size(shop_page):
    shop_page.open()
    sizes = shop_page.filter_values("Talle")
    assert sizes, "No size filter options"
    size = sizes[0]
    shop_page.apply_filter("Talle", size)
    expect(shop_page.cards.first).to_be_visible()
    offered = [
        {value.casefold() for value in values}
        for values in shop_page.displayed_variant_values()
    ]
    # Filter labels and variant names differ in case on the live store (Xl/XL).
    assert all(size.casefold() in values for values in offered)
    shop_page.clear_filter()


def test_load_more_appends_new_products(shop_page):
    # Precondition: the catalog spans more than one listing page.
    shop_page.open()
    before = shop_page.displayed_names()
    shop_page.load_more()
    after = shop_page.displayed_names()
    assert after[: len(before)] == before, "Loading more changed the first page"
    assert len(after) > len(before)
    assert len(set(after)) == len(after), "Loading more repeated products"
