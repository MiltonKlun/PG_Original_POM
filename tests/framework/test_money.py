import pytest

from config.money import ars_minor_units, format_ars

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


@pytest.mark.parametrize(
    "minor_units,display",
    [
        (0, "$0,00"),
        (950, "$9,50"),
        (123456, "$1.234,56"),
        (2900000, "$29.000,00"),
        (5800000, "$58.000,00"),
        (123456789, "$1.234.567,89"),
    ],
)
def test_format_round_trips(minor_units, display):
    assert format_ars(minor_units) == display
    assert ars_minor_units(display) == minor_units


@pytest.mark.parametrize("value", [-1, 1.5, "100", None, True])
def test_format_rejects_non_minor_units(value):
    with pytest.raises(ValueError):
        format_ars(value)


@pytest.mark.parametrize(
    "minor_units,display",
    [(2900000, "$29.000"), (0, "$0"), (2396694, "$23.966,94"), (950, "$9,50")],
)
def test_short_format_omits_only_zero_cents(minor_units, display):
    assert format_ars(minor_units, short=True) == display
    assert ars_minor_units(display) == minor_units
