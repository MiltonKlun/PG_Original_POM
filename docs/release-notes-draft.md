# Release notes draft — portfolio modernization

Version/tag: not assigned. Publication: pending owner request and remote CI
acceptance. Implementation code baseline for final local validation: `68a09f4`.

## Changes

- Default to an isolated synthetic storefront, with Python lifecycle management
  and digest-pinned Docker/nginx serving; enforce target and network boundaries.
- Replace recursive shared-page design and generic wrappers with POM composition
  and meaningful product/cart assertions.
- Expand eight original scenarios to 62 cases (37 offline, 25 UI), including
  named inputs, ARS arithmetic and mobile-emulation navigation smoke.
- Replace misleading validation/failure injections with observed behavior,
  native form checks and real pytest outcomes.
- Add hashed universal dependency pins, strict static/marker checks, standalone
  HTML/JUnit/JSON reports, traces, screenshots and video on failure.
- Prepare separate mock, live and compatibility workflows and contribution docs.

## Migration

Python 3.12 is required. Install from the hashed requirements and reinstall
matching Playwright browsers. Default `python -m pytest` now uses the local
simulation. Set `TARGET=live` explicitly for approved read-only checks. Existing
generic wrappers/CartPage and pytest-check/Allure integration were removed.
Reports now use unique run directories; custom run IDs cannot be reused.

## Validation and remaining gates

Read [release-verification.json](evidence/release-verification.json) for clean
checkout totals and [the case study](case-study.md) for failure investigations.
No skipped/retried local cases are accepted. Mock failures do not certify client
behavior. No checkout, payment, account creation or message delivery was tested.

Before publication, complete Tasks 7.1/7.2: passing and deliberate-failure PR
runs, artifact inspection on the exact SHA, and the required repository checks
described in [ci-maintenance.md](ci-maintenance.md). Do not advertise the core
milestone as met until those gates pass. Live schedules and badges become active
only when the workflows are published.

Suggested About text:

> Python Playwright QA portfolio for PG Original: composed page objects,
> deterministic local CI, read-only live smoke, and reproducible failure evidence.

Suggested topics: `python`, `playwright`, `pytest`, `page-object-model`,
`qa-automation`, `test-automation`, `github-actions`, `docker`, `portfolio`.
