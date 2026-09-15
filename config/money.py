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
