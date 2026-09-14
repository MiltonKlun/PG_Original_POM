import pytest
from config.money import ars_minor_units

pytestmark = pytest.mark.framework


@pytest.mark.parametrize(
    "display,expected",
    [
        ("$29.000", 2900000),
        ("$29.000,00", 2900000),
        ("$23.966,94", 2396694),
        (" $ 0,00 ARS ", 0),
        ("$\u00a01.234,56", 123456),
        ("$9,50", 950),
    ],
)
def test_observed_formats(display, expected):
    assert ars_minor_units(display) == expected


@pytest.mark.parametrize(
    "display",
    [
        "",
        "ARS",
        "$29,000.00",
        "$1.23",
        "$-2",
        "3 x $9.666,67",
        "$1,999",
        "$1.000 $2.000",
        "$NaN",
    ],
)
def test_ambiguous_or_nonprice_text_rejected(display):
    with pytest.raises(ValueError):
        ars_minor_units(display)
