import pytest

from config.accessibility import Violation, axe_source, parse_violations

pytestmark = pytest.mark.framework


def test_engine_is_bundled_locally():
    # Served from the pinned wheel: no CDN request at scan time.
    assert axe_source().startswith("/*! axe v4.")


def test_violations_are_summarized_readably():
    result = {
        "violations": [
            {
                "id": "color-contrast",
                "impact": "serious",
                "help": "Elements must meet minimum color contrast ratio thresholds",
                "nodes": [{"target": [".price-compare"]}, {"target": ["#a"]}],
            }
        ]
    }
    violations = parse_violations(result)
    assert violations == [
        Violation(
            rule="color-contrast",
            impact="serious",
            help="Elements must meet minimum color contrast ratio thresholds",
            targets=(".price-compare", "#a"),
        )
    ]
    assert str(violations[0]).startswith("color-contrast (serious):")
    assert "[.price-compare, #a]" in str(violations[0])


def test_no_violations_parse_to_empty_list():
    assert parse_violations({"violations": []}) == []
