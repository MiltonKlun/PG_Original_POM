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

`contract` additionally marks the read-only locator checks in
`tests/test_contract.py`, which run on both targets. `live_defect(reason)`
marks a check that fails on live because of a known store defect: on live
it becomes a strict expected failure (reported as `xfailed` with its defect
ID, and failing the run once the store is fixed); on the simulation it must
pass.

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
| LOADING | P1 | With the catalog request held open, the cookie banner still dismisses and search still opens | `test_loading.py::test_page_controls_work_before_catalog_loads` | Mock |
| MENU | P1 | Hamburger menu → SHOP panel → all products → first available product; heading matches | `test_navigation.py::test_menu_reaches_product` | Mock + live |
| RESULTS | P1 | Known term returns the product; impossible term shows empty state and no cards | `test_search.py::test_search_results`, `test_search_empty` | Mock + live |
| RESULT-SET | P1 | Partial lowercase, exact and shared-prefix terms return exactly the expected products, and nothing else | `test_search.py::test_search_filters_catalog` (3 datasets) | Mock |
| FILTER | P1 | Color and Talle filters check their control, return exactly the expected products, each offering the value; clearing restores the first page | `test_shop.py::test_filter_and_clear` (2 datasets) | Mock |
| PAGINATION | P1 | Scrolling to the end appends the second page with no repeats and updates `?mpage` | `test_shop.py::test_load_more_catalog` | Mock |
| PDP | P0 | Selected card name equals PDP heading; current price parses to a positive ARS amount; add control enabled | `test_shop.py::test_shop_product_details` | Mock + live |
| PRICE-PROMO | P0 | Returning to a discounted variant shows its price and the compare-at price | `test_shop.py::test_discounted_variant_shows_compare_price` | Mock |
| PRICE-VARIANT | P0 | A regular-priced variant updates the price, hides compare-at and reaches the cart at that price | `test_shop.py::test_regular_variant_price_reaches_cart` | Mock |
| CART-ADD | P0 | Exact product, variant, quantity, line amount and subtotal; empty-cart message hidden | `test_cart.py::test_add_to_cart_flow` | Mock |
| CART-ADD-QTY | P0 | Adding quantity 2 from the product page creates one line with quantity 2 and doubled amounts | `test_cart.py::test_add_with_quantity` | Mock |
| CART-MERGE | P0 | Adding the same variant again increases its quantity; another variant becomes a separate line | `test_cart.py::test_repeat_add_merges_line` | Mock |
| CART-QTY | P0 | Quantity 1 → 2 doubles line amount and subtotal exactly | `test_cart.py::test_cart_quantity` | Mock |
| CART-REMOVE | P0 | Removing the only line restores the empty state and zero subtotal | `test_cart.py::test_cart_remove` | Mock |
| CART-REMOVE-ONE | P0 | Removing one of two lines keeps the other line and recomputes the subtotal | `test_cart.py::test_remove_one_of_two_lines` | Mock |
| CART-PERSIST | P0 | Cart line, quantity and subtotal survive navigation to another page | `test_cart.py::test_cart_persists_across_navigation` | Mock |
| CART-EMPTY | P0 | A new browser context starts with an empty cart | `test_cart.py::test_cart_starts_empty` | Mock |
| NO-VARIANT | P0 | Product page shows the selected product; product without variants can be added at its price | `test_cart.py::test_cart_without_variants` | Mock |
| SOLD-OUT | P0 | Product page shows the selected product; "Sin stock" shown, add disabled, cart stays empty | `test_shop.py::test_unavailable_product` | Mock |
| AUTH-INVALID | P1 | Named invalid credentials are rejected and the user stays on login | `test_auth.py::test_login_failure` (2 datasets) | Mock |
| AUTH-NATIVE | P1 | Malformed/missing email and missing password are blocked client-side | `test_auth.py::test_login_native_validation` (3 cases) | Mock |
| RESET | P1 | "Olvidaste" link reaches the reset page (optional trailing slash) with its heading | `test_auth.py::test_forgot_password_link` | Mock + live |
| CONTACT | P1 | Fields keep seeded, accented and whitespace inputs; malformed emails are invalid; submit is never clicked | `test_contact.py::test_contact_*` (6 cases) | Mock (the live form's contract is in CONTRACT) |
| MONEY | P0 | ARS display parsing to integer minor units; ambiguous or installment text rejected; formatting round-trips | `framework/test_money.py` (30 cases) | Offline |
| CONTRACT | P1 | Page-object locators resolve without changing state: header, cart drawer, menu panel, listing, filters, card metadata, product form and price attribute, login, contact | `test_contract.py` (7 cases) | Mock + live |
| LISTING-DATA | P0 | Every card: positive variant prices, shown price = first variant's price, compare-at above price, "Sin stock" exactly when nothing is available | `test_catalog_integrity.py::test_listing_cards_match_their_variant_data` | Mock + live |
| PRICE-SOURCES | P0 | Listing card price = product page price = `data-product-price` | `test_catalog_integrity.py::test_product_page_price_matches_listing` | Mock + live |
| STRUCTURED-DATA | P1 | Product page price = its own JSON-LD offer | `test_catalog_integrity.py::test_product_page_publishes_its_price_as_structured_data` | Mock; live: strict xfail DEF-01 |
| VARIANT-PRICE | P0 | A product with variant-based prices: each price/compare-at combination shows as published when selected | `test_catalog_integrity.py::test_variant_prices_follow_selection` | Mock + live |
| SIZE-FILTER | P1 | First size filter option returns only products offering that size (case-insensitive) | `test_catalog_integrity.py::test_size_filter_results_offer_the_size` | Mock + live |
| LOAD-MORE | P1 | Scrolling appends new products, keeps the first page, no repeats | `test_catalog_integrity.py::test_load_more_appends_new_products` | Mock + live |
| PAGE-HEALTH | P1 | Home, listing, product and contact load with no uncaught JavaScript errors or failed first-party responses | `test_page_health.py::test_page_loads_without_errors` (4 pages) | Mock + live |
| LINKS | P1 | Up to 25 crawlable home-page links (robots.txt respected) return non-error status | `test_page_health.py::test_home_links_resolve` | Mock + live |

Totals: 166 collected cases, of which 55 are UI and 111 are offline framework
checks. 25 UI cases are `live_safe`, and the weekly live run executes all of
them.

## Test data

- Named datasets in `data/test_data.json` drive parametrized auth and contact
  cases with readable IDs.
- Expected product values live in test data and are **never** read from the
  mock's own `catalog.json`, so the test and the system under test can't
  agree on a wrong value.
- Generated contact data uses Faker `es_AR`, seeded from `--seed` plus the test
  node ID. Values repeat per case and don't depend on execution order. All
  generated emails use `example.com`.
- Money is compared in integer minor units, never binary floats. Expected
  display text is derived from test data with `format_ars`, not hard-coded.

## Live traffic policy

PG Original allowed this read-only testing for portfolio purposes. To keep
the footprint small and honest:

- Live runs are serial, weekly (plus manual runs), with no retries.
- Ad pixels, analytics, telemetry, the recommendation widget and the store's
  own visit counter are blocked (`config/live_policy.py`); everything the
  page needs still loads. The site contract lists every host and decision.
- Requests carry a `PGOriginalQA/1.0 (+repository URL)` user-agent suffix.
- `robots.txt` disallows `/account/` and `/search/` for crawlers. The suite
  isn't a crawler, but the link check skips every disallowed path and samples
  at most 25 links; scenario tests visit login and search only as a user would.
- Nothing is ever submitted: no cart, login, contact or password-reset action.

## Page object design

- Pages extend a small `BasePage` that declares a relative `path` template
  (`/productos/{slug}/`). One `open(**params)` validates parameters as URL
  slugs and fails before navigating if they're missing, unexpected or unsafe.
- Shared UI regions are components rooted in a `Locator` (header, search
  panel, cart drawer, cookie notice), built on first use and composed into
  pages. The cart drawer receives its header trigger instead of creating a
  second navbar.
- Navigation returns the destination page object
  (`home.open_shop().open_product(name)`), so a journey is explicit and mypy
  checks every step.
- Store copy lives in `config/ui_text.py`; test data is parsed into frozen,
  validated dataclasses with readable errors.

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
| Live read-only | Weekly / manual | All `live_safe` cases, Chromium, serial, no retries, trackers blocked | No; a failure stays visible |
| Mutation score | Weekly / manual / PRs touching tests or the mock | All mutants against the mock UI suite; fails below 90% | No |
| Security | PR / push to `main` / weekly / manual | pip-audit on both pinned requirement files, including resolved sub-dependencies; zizmor (auditor level) on all workflows | No |

A change is ready when the required checks are green with no unexplained
skips, xfails or reruns. Sensitivity was verified by deliberately breaking
cart insertion, product identity and an expected price: each made the
corresponding test fail, with trace, screenshot and video retained.

## Test effectiveness (mutation testing)

A passing suite only matters if it fails when the product is wrong. The
catalog in [`tests/mutation/catalog.json`](../tests/mutation/catalog.json)
lists realistic storefront defects: search not filtering, repeat adds
duplicating lines, quantity ignored, cart lost on navigation, wrong line
removed, wrong totals, variant not recorded, filter not applied, sold-out
product purchasable, stale empty-cart message, quantity edits not saved and
the wrong product heading.

`scripts/mutation_check.py` applies each defect to a disposable copy of the
simulation, runs the UI suite, and counts the defect as detected only when
tests fail. The unmodified copy must pass first, and runs that end in any
other way (interrupted, no tests collected) are rejected rather than scored.
A framework check fails when the storefront changes and a mutant no longer
applies, so the catalog can't silently go stale.

```text
python scripts/mutation_check.py --min-score 90
python scripts/mutation_check.py --only M05
```

| Date | Suite | Score |
|---|---|---|
| 2026-09-27 | Before adding the tests below | 46.2% (6 of 13) |
| 2026-09-27 | With result-set, add-quantity, merge, persistence and partial-removal tests | 100% (13 of 13) |
| 2026-09-27 | Simulation aligned with live markup; 6 mutants added for variant pricing, pagination, size filter and menu | 100% (19 of 19) |
| 2026-09-28 | Page objects refactored; mutant added for controls wired only after data loads | 100% (20 of 20) |
| 2026-09-28 | Catalog integrity checks; mutants for wrong JSON-LD price, wrong card price, missing sold-out label | 100% (23 of 23) |

The weekly and pull-request workflow fails below 90%.

## Known gaps

- Mutants cover the simulation's JavaScript only; defects in live-only
  behavior are covered by the read-only checks, not by the mutation score.
- Live coverage is read-only by design: cart, checkout and authentication
  behavior is verified only in the simulation.
- No automated accessibility, visual or performance checks yet.
