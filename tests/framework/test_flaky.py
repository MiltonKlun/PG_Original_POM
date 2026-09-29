import json

import pytest

from scripts.flaky_check import compare, load_outcomes, render_markdown

pytestmark = pytest.mark.framework

A, B, C = "tests/test_a.py::a", "tests/test_b.py::b", "tests/test_c.py::c"


def test_stable_passing_runs_report_nothing():
    runs = [{A: "passed", B: "xfailed"}, {A: "passed", B: "xfailed"}]
    assert compare(runs) == ({}, [])


def test_outcome_changing_between_runs_is_flaky():
    runs = [{A: "passed", B: "passed"}, {A: "failed", B: "passed"}, {A: "passed"}]
    flaky, failing = compare(runs)
    assert flaky == {
        A: ["passed", "failed", "passed"],
        B: ["passed", "passed", "missing"],
    }
    assert failing == []


def test_failure_in_every_run_is_failing_not_flaky():
    runs = [{A: "failed", C: "error"}, {A: "failed", C: "error"}]
    assert compare(runs) == ({}, [A, C])


def test_no_runs_is_an_error():
    with pytest.raises(ValueError):
        compare([])


def test_outcomes_read_from_run_summary(tmp_path):
    summary = tmp_path / "summary.json"
    summary.write_text(
        json.dumps({"tests": {A: {"status": "passed", "duration": 1.2}}}),
        encoding="utf-8",
    )
    assert load_outcomes(summary) == {A: "passed"}


def test_report_lists_each_flaky_test():
    report = render_markdown(3, 10, {A: ["passed", "failed", "passed"]}, [C])
    assert "3 runs of 10 tests: **1 flaky**, **1 failing in every run**" in report
    assert f"| `{A}` | passed, failed, passed |" in report
    assert f"- `{C}`" in report
