"""Parse observed ARS display amounts without accepting ambiguous formats."""

import re
from decimal import Decimal

_PATTERN = re.compile(
    r"^\$\s*(?P<amount>(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{2})?)\s*(?:ARS)?$"
)


def ars_minor_units(text: str) -> int:
    match = _PATTERN.fullmatch(text.replace("\u00a0", " ").strip())
    if not match:
        raise ValueError(f"Not an ARS display amount: {text!r}")
    normalized = match["amount"].replace(".", "").replace(",", ".")
    return int(Decimal(normalized) * 100)


def format_ars(minor_units: int, *, short: bool = False) -> str:
    """Render minor units as a storefront amount: $58.000,00 (cart) or, with
    short=True, the listing/product form that omits zero cents: $58.000."""
    if type(minor_units) is not int or minor_units < 0:
        raise ValueError(
            f"Amount must be non-negative integer minor units: {minor_units!r}"
        )
    whole, cents = divmod(minor_units, 100)
    text = f"${whole:,}".replace(",", ".")
    return text if short and not cents else f"{text},{cents:02d}"
