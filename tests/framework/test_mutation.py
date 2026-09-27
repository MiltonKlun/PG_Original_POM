import json
import pytest
from scripts.mutation_check import (
    ROOT,
    Edit,
    Outcome,
    apply_edits,
    classify,
    failing_tests,
    load_catalog,
    render_markdown,
    score,
)

pytestmark = pytest.mark.framework


def outcome(mutant_id, status, failing=(), expected=True):
    return Outcome(mutant_id, "defect", status, failing, expected, 1.0)


def test_every_mutant_applies_to_current_storefront():
    # Fails when the storefront changes and a mutant no longer matches it.
    for mutant in load_catalog():
        source = (ROOT / mutant.file).read_text(encoding="utf-8")
        assert apply_edits(source, mutant.edits) != source


@pytest.mark.parametrize(
    "text,edit",
    [
        ("a b", Edit("missing", "x")),
        ("same same", Edit("same", "other")),
        ("a b", Edit("a", "a")),
    ],
    ids=["missing", "ambiguous", "no-op"],
)
def test_invalid_edits_rejected(text, edit):
    with pytest.raises(ValueError):
        apply_edits(text, (edit,))


def test_multiline_snippet_matches_crlf_checkout():
    edit = Edit("a();\n  b();", "a();")
    assert apply_edits("x\r\na();\r\n  b();\r\n", (edit,)) == "x\na();\n"


def test_edits_apply_in_order():
    assert apply_edits("abc", (Edit("a", "x"), Edit("xb", "y"))) == "yc"


def row(**overrides):
    base = {
        "id": "M1",
        "description": "defect",
        "file": "mock_site/app.js",
        "edits": [{"find": "a", "replace": "b"}],
        "killed_by": ["test_a"],
    }
    return {**base, **overrides}


@pytest.mark.parametrize(
    "mutants",
    [
        [],
        [row(edits=[])],
        [row(killed_by=[])],
        [row(), row()],
        [row(file="../outside.js")],
        [{"id": "M1"}],
    ],
    ids=["empty", "no-edits", "no-killer", "duplicate-id", "outside-repo", "keys"],
)
def test_invalid_catalog_rejected(tmp_path, mutants):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"mutants": mutants}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_catalog(path)


@pytest.mark.parametrize("code,status", [(0, "survived"), (1, "killed")])
def test_pytest_exit_codes(code, status):
    assert classify(code) == status


@pytest.mark.parametrize("code", [2, 3, 4, 5])
def test_interrupted_or_empty_runs_are_not_results(code):
    with pytest.raises(RuntimeError):
        classify(code)


def test_failing_tests_parsed_from_summary():
    output = "\n".join(
        [
            "..F",
            "FAILED tests/test_cart.py::test_cart_quantity[chromium] - AssertionError",
            "ERROR tests/test_cart.py::test_add_to_cart_flow[chromium] - Timeout",
            "1 failed, 1 error, 23 passed",
        ]
    )
    assert failing_tests(output) == (
        "tests/test_cart.py::test_cart_quantity[chromium]",
        "tests/test_cart.py::test_add_to_cart_flow[chromium]",
    )


def test_score_and_report():
    outcomes = [
        outcome("M1", "killed", ("tests/test_a.py::test_a[chromium]",)),
        outcome("M2", "survived"),
        outcome("M3", "killed", ("tests/test_b.py::test_b[chromium]",), False),
        outcome("M4", "killed", ("tests/test_a.py::test_a[chromium]",)),
    ]
    assert score(outcomes) == 75.0
    report = render_markdown(outcomes)
    assert "**75.0%**: 3 of 4" in report
    assert "| M2 | defect | **survived** | - |" in report
    assert "killed (unexpected test) | test_b |" in report
    with pytest.raises(ValueError):
        score([])
