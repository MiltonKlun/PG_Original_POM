# QA strategy and coverage

## Scope and decisions

The owner confirmed local mock CI plus separate live checks, reported no
staging environment, and authorized replacing the earlier modernization plan
with an independently assessed roadmap. `IMPROVEMENTS.md` is authoritative.

The local simulation verifies automation contracts with deterministic data.
Live checks verify selected public storefront behavior. They are separate
results. No staging server or dedicated accounts exist. Live automation is
limited to browsing/search, opening drawers, and non-submitting form checks.
Cart changes, invalid login submissions and simulated validation stay local.
Checkout, purchases, email delivery, account creation and anti-bot bypass are
excluded. Planned live cadence: serial weekly Monday 09:00 UTC, no retries.

## Baseline and reconciliation (Phase 0)

Implementation started from `a0fc620` on `improve/phase-0-contract`.
Rechecked 2026-09-12: 8 Chromium cases collect; Black reports 6 files requiring
formatting; Flake8 reports 33 findings. These are collection/static results,
not a fresh passing browser suite. The historical 2026-06-30 Actions run
28482991764 had 6 passes and 2 deselections, and uploaded no artifacts.

Every completion mark in the old plan's Phase 1 was reconciled:

| Old task | Actual baseline |
|---|---|
| 1.1 Ignore old plan/add follow-ups | Plan and test-results untracked; no FOLLOWUPS.md; logs already ignored. Preserve existing untracked files. |
| 1.2 Pin/remove Allure | Dependencies unpinned; Allure still present. |
| 1.3 Headless/output/legacy | Still headed, output proofs, legacy exclusion present; no legacy directory in this checkout. |
| 1.4 Move pytest-check import | Import still inside product test. |
| 1.5 Remove valid_user | Unused fake credentials still present. |
| 1.6 Fix CI | setup-python v4, wrong artifact path and old overrides still present. |
| 1.7 Formatting/lint | No .flake8; checks fail as reported above. |

No old completion mark is carried forward without implementation evidence.

## Scenario traceability

Priority P0 covers shopping correctness; P1 covers navigation/form behavior.
All current cases are UI journey tests. The legacy `integration` marker does
not signify lower-level API integration. Future statuses below remain planned
until their implementation and evidence are recorded.

| ID / priority | Baseline node (under tests/) | Intended coverage / precondition | Target / status |
|---|---|---|---|
| HOME / P1 | test_smoke.py::test_home_page_load | Brand/title, header/footer and shop destination | Shared / baseline weak assertions |
| SEARCH / P1 | test_smoke.py::test_search_modal_opens | Search visible/focused, close state | Shared / baseline open-only |
| PDP / P0 | test_shop.py::test_shop_product_details | Available named card → same heading, valid current price | Shared / baseline visibility-only |
| CART-ADD / P0 | test_shop.py::test_add_to_cart_flow | Empty cart; explicit product/variant/quantity → matching cart line | Mock / baseline drawer-only |
| CONTACT-VALIDATION / P1 | test_contact.py::test_contact_form_validation | Observe native rules, never alter disabled control | Mock for simulated rules / unsafe baseline to replace |
| CONTACT-FILL / P1 | test_contact.py::test_contact_form_fill | Name/email/message retain seeded inputs; no submit | Shared / baseline checks only name |
| AUTH-INVALID / P1 | test_auth.py::test_login_failure | Named invalid credentials → simulated rejection, unauthenticated | Mock / baseline overlay to remove |
| RESET / P1 | test_auth.py::test_forgot_password_link | Link → reset destination identity; no email request | Shared after follow-up / baseline weak URL assertion |

## Required expansion mapping

| Plan task / risk | Scenario / precondition / expected result | Planned node family | Eligibility |
|---|---|---|---|
| 5.1 / P1 | HOME plus usable shop navigation | test_smoke.py::test_home_page_load | Shared |
| 5.2 / P1 | SEARCH plus focus/close | test_smoke.py::test_search_modal_opens | Shared |
| 5.3 / P1 | Known term has matching identity; impossible term has empty state | test_search.py::test_search_* | Shared after observation |
| 5.4 / P1 | Apply one color filter; matching results; clear restores list | test_shop.py::test_filter_* | Local until result/reset observed |
| 5.5 / P0 | PDP selected identity and current price | test_shop.py::test_shop_product_details | Shared |
| 5.6 / P0 | CART-ADD exact identity/variant/quantity/amount | test_cart.py::test_add_to_cart_flow | Mock |
| 5.7 / P0 | Quantity 1→2 doubles synthetic undiscounted line/subtotal | test_cart.py::test_cart_quantity | Mock |
| 5.8 / P0 | Remove sole item → empty/zero; independent context starts empty | test_cart.py::test_cart_* | Mock |
| 5.9 / P0 | Unavailable fixture cannot be added normally | test_shop.py::test_unavailable_product | Mock |
| 5.10 / P1 | Invalid auth datasets with distinct client/server expectations | test_auth.py::test_login_* | Mock |
| 5.11 / P1 | RESET destination identity | test_auth.py::test_forgot_password_link | Shared after follow-up |
| 5.12 / P1 | Seeded/explicit accented, malformed-email, whitespace cases | test_contact.py::test_contact_* | Fill shared; simulated rules mock |

## Evidence and exit policy

Record node IDs, target, commit, browser, seed, runtime and result totals per
phase in the improvement plan. Raw browser artifacts remain ignored; link
reviewed summaries/reports. Use `docs/site-contract.md` for observations and
unverified behavior. A timeout is not proof of anti-bot blocking.

No arbitrary coverage percentage is claimed. Coverage measures the scenarios
above, their assertions and their target-specific evidence. No unexplained
skips, xfails or retries are accepted in the deterministic gate. Deliberately
broken cart insertion and product identity must fail their corresponding tests.

## Implemented scenario map (Phase 5)

All eight baseline scenarios are retained and strengthened. CART-ADD moved
from test_shop.py to `test_cart.py::test_add_to_cart_flow`; auth failure now
collects two named cases. Contact fill retains the seeded case and adds two
explicit input cases plus two native invalid-email cases. No contact submission
or enabled-after-fill claim exists. Tests import expected fixtures from
`data/test_data.json`, never from the mock catalog.

| Plan tasks | Implemented node(s), under tests/ | Evidence/eligibility |
|---|---|---|
| 5.1 | test_smoke.py::test_home_page_load | Mock + observed live; shop navigation included |
| 5.2 | test_smoke.py::test_search_modal_opens | Open/focus/close; mock + observed live |
| 5.3 | test_search.py::test_search_results, test_search_empty | Mock; live-safe discovery supported |
| 5.4 | test_shop.py::test_filter_color_and_clear | Mock fixed counts; separate live observation recorded |
| 5.5 | test_shop.py::test_shop_product_details | Selected identity and positive ARS current price |
| 5.6 | test_cart.py::test_add_to_cart_flow | Mock identity/variant/quantity/line/subtotal |
| 5.7 | test_cart.py::test_cart_quantity | Mock quantity 1 to 2, exact amounts |
| 5.8 | test_cart.py::test_cart_remove, test_cart_starts_empty | Mock removal/zero/isolated initial state |
| 5.9 | test_shop.py::test_unavailable_product | Mock disabled action, empty cart |
| 5.10 | test_auth.py::test_login_failure, test_login_native_validation | Mock: 2 rejection + 3 native validation cases |
| 5.11 | test_auth.py::test_forgot_password_link | Observed slash-optional route + heading |
| 5.12 | test_contact.py::test_contact_* | 6 non-submitting cases; simulated disabled check mock-only |
| 5.13 | framework/test_money.py | 15 pure parsing cases; no binary floating-point |

Test module runs, reordered representative cases, and repeated full runs are
recorded in the phase execution log. Passes are target-specific, not a claim
that all live scenarios passed. Browser evidence paths use `test-results/`.
