# Test strategy

## Context

PG Original sells apparel through a Tiendanube storefront at
[pgoriginal.com](https://www.pgoriginal.com/). There is no staging
environment, no test accounts and no payment sandbox. Every action on the
public site affects a real business, so the strategy separates **what can be
verified safely on production** from **what needs a controllable
environment**.

## Test environments

| Target | What it is | What it can prove | What it cannot prove |
|---|---|---|---|
| `mock` (default) | Local synthetic storefront in `mock_site/`, served by Python or nginx/Docker. Markup follows the observed live contract; catalog, cart, login rejection and form rules are simulated. | The automation works, assertions detect wrong business outcomes, and runs are deterministic and isolated. | That production behaves the same way. |
| `live` | `https://www.pgoriginal.com`, read-only. | Selected public pages, search, product details and form controls work today, and the locators still match real markup. | Cart, checkout, authentication, email or payment behavior. |

Mock results are always reported as mock results. A green mock run is never
presented as evidence about production.

## Scope

**In scope:** home and navigation, search (results and empty state), shop
listing and color filter, product detail identity and current price, variant
selection, cart add/quantity/remove/empty state (mock), unavailable products
(mock), negative login and native validation (mock), password-reset
navigation, contact form fields and validation without submitting.

**Out of scope:** real purchases, payment, checkout, valid login, account
creation, contact delivery, reset emails, CAPTCHA/Turnstile circumvention,
load and security testing.

## Target eligibility

Every UI test carries exactly one eligibility marker, enforced at collection
time in `conftest.py`:

| Marker | Meaning | Selected on live |
|---|---|---|
| `live_safe` | Observed, non-submitting behavior | Yes |
| `mock_only` | Mutates state, submits a form, or depends on simulated rules | Never |
| `framework` | Offline checks of the framework itself (no browser/server) | Yes |

A test marked both `live_safe` and `mock_only` fails collection. On
`TARGET=live`, any UI test without `live_safe` is deselected even when `-m`
is omitted, so a forgotten marker cannot send a cart mutation to production.
In mock runs, any request to a non-local origin is aborted and fails the test.

## Risk-based scenario map

P0 = revenue or order correctness, P1 = discovery and forms.

| ID | Risk | Scenario / key assertions | Node(s) under `tests/` | Target |
|---|---|---|---|---|
| HOME | P1 | Brand title, header/footer, SHOP link reaches `/productos/` | `test_smoke.py::test_home_page_load` | Mock + live |
| SEARCH | P1 | Search opens, input is visible and focused, close hides it | `test_smoke.py::test_search_modal_opens` | Mock + live |
| MENU | P1 | Hamburger menu → shop → product | `test_navigation.py::test_menu_reaches_product` | Mock |
| RESULTS | P1 | Known term returns the product; impossible term shows empty state and no cards | `test_search.py::test_search_results`, `test_search_empty` | Mock + live |
| FILTER | P1 | Color filter checks its control, results offer that color, clearing restores the list | `test_shop.py::test_filter_color_and_clear` | Mock |
| PDP | P0 | Selected card name equals PDP heading; current price parses to a positive ARS amount; add control enabled | `test_shop.py::test_shop_product_details` | Mock + live |
| CART-ADD | P0 | Exact product, variant, quantity, line amount and subtotal | `test_cart.py::test_add_to_cart_flow` | Mock |
| CART-QTY | P0 | Quantity 1 → 2 doubles line amount and subtotal exactly | `test_cart.py::test_cart_quantity` | Mock |
| CART-REMOVE | P0 | Removing the only line restores the empty state and zero subtotal | `test_cart.py::test_cart_remove` | Mock |
| CART-EMPTY | P0 | A new browser context starts with an empty cart | `test_cart.py::test_cart_starts_empty` | Mock |
| NO-VARIANT | P0 | Product without variants can be added at its price | `test_cart.py::test_cart_without_variants` | Mock |
| SOLD-OUT | P0 | Unavailable product shows "Sin stock", add is disabled, cart stays empty | `test_shop.py::test_unavailable_product` | Mock |
| AUTH-INVALID | P1 | Named invalid credentials are rejected and the user stays on login | `test_auth.py::test_login_failure` (2 datasets) | Mock |
| AUTH-NATIVE | P1 | Malformed/missing email and missing password are blocked client-side | `test_auth.py::test_login_native_validation` (3 cases) | Mock |
| RESET | P1 | "Olvidaste" link reaches the reset page (optional trailing slash) with its heading | `test_auth.py::test_forgot_password_link` | Mock + live |
| CONTACT | P1 | Fields keep seeded, accented and whitespace inputs; malformed emails are invalid; submit is never clicked | `test_contact.py::test_contact_*` (6 cases) | Fill: mock + live; disabled submit: mock |
| MONEY | P0 | ARS display parsing to integer minor units; ambiguous or installment text rejected | `framework/test_money.py` (15 cases) | Offline |

Totals: 62 collected cases, of which 25 are UI and 37 are offline framework
checks. 11 UI cases are `live_safe`; the weekly live smoke runs the 3 that
are also `smoke`.

## Test data

- Named datasets in `data/test_data.json` drive parametrized auth and contact
  cases with readable IDs.
- Expected product values live in test data and are **never** read from the
  mock's own `catalog.json`, so the test and the system under test can't
  agree on a wrong value.
- Generated contact data uses Faker `es_AR`, seeded from `--seed` plus the test
  node ID. Values repeat per case and don't depend on execution order. All
  generated emails use `example.com`.
- Money is compared in integer minor units, never binary floats.

## Assertion policy

- Web-first `expect` assertions for anything the UI updates; plain `assert`
  only for values already computed.
- Tests own business expectations. Page objects may wait for the
  postcondition of their own action (e.g. a variant shows as selected), but do
  not decide pass/fail for a scenario.
- No fixed sleeps, forced clicks, JavaScript that enables disabled controls,
  broad exception swallowing, automatic retries, or skips that hide failures.
- A timeout is investigated with the trace; it isn't labeled "bot blocking"
  without evidence.

## Execution and exit criteria

| Pipeline | Trigger | Selection | Blocking |
|---|---|---|---|
| Mock CI | PR / push to `main` | Static checks + framework tests (Ubuntu, Windows); all UI tests, Chromium against Docker/nginx | Yes (required checks) |
| Compatibility | Weekly / manual | Full mock UI on Firefox and WebKit; Chromium Pixel 7 emulation smoke | No |
| Live smoke | Weekly / manual | `smoke and live_safe`, Chromium, serial, no retries | No; a failure stays visible |

A change is ready when the required checks are green with no unexplained
skips, xfails or reruns. Sensitivity was verified by deliberately breaking
cart insertion, product identity and an expected price: each made the
corresponding test fail, with trace, screenshot and video retained.

## Known gaps

Assessed 2026-09-27 by injecting realistic defects into a copy of the mock:

- Search doesn't assert that non-matching products are excluded.
- No case adds a quantity above 1, adds the same variant twice, keeps the cart
  across navigation, or removes one line out of several.
- Live pricing varies by variant (e.g. one color on promotion, another at list
  price). The mock uses one price per product, and this isn't tested yet.
- Some mock markup (cart close control, menu SHOP entry) differs from live and
  is being aligned; see the [site contract](site-contract.md).
- No automated accessibility, visual or performance checks yet.
