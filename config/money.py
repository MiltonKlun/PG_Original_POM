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


def format_ars(minor_units: int) -> str:
    """Render minor units as the storefront's cart amount, e.g. $58.000,00."""
    if type(minor_units) is not int or minor_units < 0:
        raise ValueError(
            f"Amount must be non-negative integer minor units: {minor_units!r}"
        )
    whole, cents = divmod(minor_units, 100)
    return f"${whole:,}".replace(",", ".") + f",{cents:02d}"
