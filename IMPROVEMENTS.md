# PG Original POM — Improvement Plan

An executable QA automation and portfolio roadmap, based on the actual repository rather than the completion marks in the previous plan.

**Assessment date:** 2026-09-12. **Baseline:** commit `a0fc620`, branch `feature/framework-improvements`. **Repository:** `MiltonKlun/PG_Original_POM`, public, default branch `main`.

**Status:** implementation in progress; Phases 0 through 6 completed. Checkboxes record verified work only. Following the owner's answers, this document supersedes `01-PG-ORIGINAL-POM.md` as the implementation roadmap; that file remains untouched as historical context. The old plan's “do not relitigate” decisions and checked tasks are not authoritative for this roadmap.

## 1. Outcome and scope

Turn the existing Python + synchronous Playwright + Pytest project into a credible QA automation portfolio that demonstrates maintainable POM design, meaningful business assertions, reproducible execution, and transparent reporting about a real client storefront.

The recommended execution model retains the previous plan's local storefront for deterministic framework checks and separate checks against PG Original. A local simulation proves the automation works against its documented contract. It does **not** prove that the client's production application works. Keep that distinction visible in reports, coverage documentation, workflow names, and the README.

The core plan includes stronger coverage of browsing, search, product selection, cart behavior, and non-submitting form checks. It does not include real purchases, payment processing, password-reset emails, contact delivery, account creation, anti-bot circumvention, production load testing, or an application rewrite. Those require separate scope and suitable environments.

### Owner decisions and implementation choices

The owner answered all three assessment questions. There are no unanswered scope questions blocking the core plan. The table distinguishes the owner's decisions from the implementation choices made under their request to assess what is most professional.

| ID | Owner answer | Selected implementation | Status |
|---|---|---|---|
| D1 | “Retain local mock CI plus live checks.” | Local mock for required CI; separate live checks. Docker serves the mock in CI; Python is the default local quickstart. | Confirmed. Do not ask again. |
| D2 | No test environment exists; the owner permits choosing whether to create one or test live based on professional judgment. | Build a local simulation, clearly labeled as such. Use live browsing and non-submitting checks. Keep cart mutations, invalid-login submissions and simulated validation local. No dedicated accounts were supplied or are required. Prepare a bounded weekly read-only smoke workflow. | Core environment strategy resolved. Real staging, transactions, messages and credentials remain future scope, not core blockers. |
| D3 | Challenge the old plan, retain useful work, discard low-value work, and add independent improvements. | This plan replaces the old roadmap and includes stronger coverage, simpler POM composition, JUnit + pytest-html reporting, and evidence-driven portfolio documentation. | Confirmed. Do not preserve an old decision solely because it was labeled final. |

**How to handle new uncertainty:** inspect the real behavior and available documentation first. If a business contract remains unknown, mark only the dependent task blocked with the exact missing fact and continue independent work. Do not invent a staging environment or interpret general portfolio authorization as permission to send real messages or purchases. The core implementation below needs neither.

### Choices specified by this plan

- Keep Python 3.12 and synchronous Playwright with Pytest. Verify compatible dependency versions in a fresh environment; do not copy the old plan's version numbers or the global environment blindly.
- Keep Black and Flake8, with compatible line-length configuration. Do not add a second formatter or migrate language/framework for portfolio optics.
- Prefer domain actions and typed Locators over generic `click`/`fill` wrappers. Use composition for shared UI modules; keep `BasePage` small.
- Use standard Playwright `expect` assertions by default. Remove `pytest-check` once migrated; optional soft assertions are not a requirement for a professional suite.
- Remove unused Allure integration and its documentation together. Use JUnit XML, Playwright evidence, a GitHub summary, and a self-contained pytest-html report as specified in Phase 6; do not install two reporting stacks.
- Do not promise a version tag such as `v2.0.0` until the release scope is known. Prepare release notes; publish only when requested.
- Commit this plan with the eventual implementation when appropriate; do not add `IMPROVEMENTS.md` to `.gitignore`.

## 2. Verified assessment

### What was examined

Read every Python source file in `pages/`, `components/`, and `tests/`, including package initializers; `requirements.txt`; `pytest.ini`; `.github/workflows/test.yml`; `.gitignore`; `README.md`; `CLAUDE.md`; `LICENSE`; all three files in `docs/agents/`; `data/test_data.json`; and the complete existing modernization plan. Inspected the logo and three existing screenshots, repository state/history, open GitHub issues, and recent Actions results. No open issues were returned at assessment time.

Read public home, shop, and contact pages for context and current official Playwright/Pytest/GitHub documentation. Public page extraction does not establish runtime selectors, visibility, CAPTCHA behavior, or form submission rules. The login page fetch returned a tool error; this is **not evidence of bot detection**. No live browser suite, form submission, cart mutation, or purchase was executed during this assessment.

### Baseline checks and limits

| Check | Result |
|---|---|
| Parse all repository Python files with `ast.parse` | Passed. |
| `python -m pytest --collect-only -q -o addopts=` | 8 Chromium cases collected. Collection is not test execution. |
| `python -m black --check pages components tests` | Failed: 6 files would be reformatted. |
| `python -m flake8 pages components tests --statistics --count` | Failed: 33 findings with current default configuration, including 2 bare `except` clauses. |
| Latest available successful Actions run | [Run 28482991764](https://github.com/MiltonKlun/PG_Original_POM/actions/runs/28482991764), 2026-06-30, commit `2a23d0d`: 6 passed, 2 deselected in 22.71 seconds. This is a historical run on a different commit. |
| Artifact upload in that run | Warning: no files found at `reports/`; no artifacts uploaded. |
| Initial working tree | Untracked `01-PG-ORIGINAL-POM.md` and `test-results/`; preserve them. |

The installed global environment reported Python 3.12.4, Playwright 1.40.0, pytest 8.4.2, and pytest-playwright 0.7.2. These identify the assessment environment, not recommended dependency pins. The repository has no lock or verified clean-install baseline.

### Findings, ordered by impact

| ID | Priority | Evidence | Why it matters / destination |
|---|---|---|---|
| F01 | P0 | Old plan marks Phase 1 complete; actual dependencies, config, CI, data, and missing `.flake8` contradict it. | Agents could skip necessary work. Reconcile in Phase 0. |
| F02 | P0 | `tests/test_contact.py` enables a disabled button and clicks through injected JavaScript. `tests/test_auth.py` paints an invented automation-block overlay after arbitrary exceptions. | Tests change the behavior/evidence they claim to verify. Remove in Phases 1 and 3. |
| F03 | P0 | `BasePage.fill()` logs every input value, including password and contact data. | Logs and artifacts could expose data. Remove value logging in Phase 1; handle artifact limits in Phase 6. |
| F04 | P0 | `test_add_to_cart_flow` double-clicks the first variant, catches any toast error, then only asserts drawer visibility. `CartPage` is unused by tests. | An empty cart can satisfy the test. Implement identity/variant/quantity assertions in Phases 3–5. |
| F05 | P1 | `BasePage` constructs `Navbar`; `Navbar` inherits `BasePage`; recursion is avoided by class-name comparison and a local import. `CartPage.is_visible()` changes the parent's required arguments. | Fragile composition and inconsistent interfaces. Fix in Phase 3. |
| F06 | P1 | String-based page actions, instantaneous visibility assertions, arbitrary sleeps, bare/broad exception handling. | Timing races and hidden failures. Fix in Phase 3. |
| F07 | P1 | Hardcoded live URL; `page_obj` always loads home; data and logging paths depend on current working directory; Faker is unseeded. | Poor isolation, extra navigation, weak reproducibility. Fix in Phase 2. |
| F08 | P1 | CI writes `proofs/` but uploads `reports/`; no traces, JUnit output, or enforced lint gate. | A green badge has limited diagnostic value. Fix in Phases 1, 6, 7. |
| F09 | P1 | Home accepts any nonempty title. PDP checks price/button visibility, not product identity. Contact fill checks only name. Search execution/filter/cart changes are uncovered. | Coverage claims exceed demonstrated outcomes. Fix in Phase 5. |
| F10 | P1 | Dependencies unpinned; local default headed; README says Python 3.8+ while CI uses 3.12. | Setup is not reproducible. Fix in Phases 1 and 8. |
| F11 | P2 | JSON contains one invalid user, unused fake valid credentials, unused contact data; no parametrization. | External JSON alone does not demonstrate multiple datasets or boundaries. Fix in Phases 2 and 5. |
| F12 | P2 | Static “Complete”/“Passing” badges; README misstates inheritance and claims flaky-free execution, checkout datasets, and generated edge-case coverage. | Portfolio credibility requires accurate claims. Fix in Phase 8. |

**Existing strengths to retain:** a compact codebase, sensible initial separation into page objects and tests, function-scoped Playwright browser contexts, feature markers, an existing Actions workflow, client context, and clear ownership/license information. This project needs stronger implementation and evidence, not a large generic framework.

### Corrections to the earlier plan

1. Its “complete” marks are not implementation evidence in this checkout.
2. A mock built merely to satisfy existing selectors can reproduce weak tests. Define behavior and independent expected data before HTML.
3. `contacto.html` does not satisfy navigation to `/contacto/`; a reset page nested under `/account/login/` does not satisfy `/account/reset/`. Both serving modes must use identical routes.
4. A separate cart page does not satisfy the current shared drawer contract. Model the drawer on every applicable page.
5. Excluding `interactive` from mock CI would continue excluding the negative-auth/contact cases the mock is supposed to enable. Replace ambiguous markers with explicit target eligibility.
6. Filling name/email/message does not establish that CAPTCHA-dependent submit behavior becomes enabled. Observe and document the actual rule first.
7. Broad `except Exception: pass`, generic “likely blocked” messages, and blanket `continue-on-error` do not provide trustworthy classification.
8. Unix-only `make` and inline environment assignments do not constitute a Windows quickstart. Provide PowerShell and POSIX commands, plus a Python entry point where lifecycle management is needed.
9. Installing `allure-pytest` does not require decorators to produce a basic report when `--alluredir` is supplied. Its removal is a simplification choice; the verified CI defect is that no results are generated at the uploaded path.

## 3. Executor rules and phase dependencies

1. Read this file, `CLAUDE.md`, applicable repository instructions, and any recorded owner answers before editing. Inspect `git status` and the current commit; do not reset or overwrite unrelated work.
2. Execute the phases in order. Within a phase, task IDs define order unless an explicit dependency says otherwise. No delegation is required.
3. Use a small reviewable branch/PR per phase when implementation is requested. Work from the integrated previous phase. Do not branch repeatedly from the original baseline and lose earlier work. Do not publish, merge, change remote settings, or release merely because a checklist mentions it; follow the user's authorization for that session.
4. Each task specifies files, behavior, and completion evidence. Mark `[x]` only after verification, recording the commit, commands, result, and remaining limitations in the execution log below. A phase with a failed gate is incomplete.
5. Preserve baseline scenarios when replacing tests. Record old-to-new node mappings in `docs/test-strategy.md`; renamed or split tests are acceptable. Never delete a failing case merely to obtain green CI.
6. Adapt routine selector/name/file differences with an inline note. If a business contract cannot be observed or a material decision changes, update the dependent task before implementing it. Do not invent client behavior. Continue unrelated tasks.
7. All test and framework failures remain failures. Record confirmed environmental blocks separately, with evidence. A generic timeout alone is not an anti-bot diagnosis.
8. No fixed sleeps, force-enabling controls, synthetic production error overlays, unconditional retries, exception swallowing, or hidden live-to-mock fallback.
9. Prefer meaningful behavioral checks for new logic. Do not add tests that only mirror wrappers, file layout, or line counts. Framework settings, money parsing, marker enforcement, and server lifecycle merit small offline tests.
10. Regenerate the dependency resolution whenever later tasks add or remove a package; recheck clean installation and `pip check`.
11. Keep the scope bounded. Put deferred work in Section 10 with its prerequisite; do not create a second competing active roadmap.

**Dependency chain:** Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8. D1–D3 are resolved above. Additional live actions outside D2 require a separate scope change; they are unnecessary for the core milestone.

## 4. Ordered implementation phases

### Phase 0 — Establish an accurate contract and scope

**Purpose:** give implementation agents evidence and one agreed direction. No application or test behavior changes in this phase.

- [x] **0.1 — Reconcile project state.** Recheck the baseline commands above and compare every old Phase 1 completion claim with the current checkout. Record the new baseline in `docs/test-strategy.md`. Keep the older untracked plan intact unless the owner asks to archive it. **Done when:** the document explicitly distinguishes implemented, proposed, and historical work.
- [x] **0.2 — Transfer the resolved scope into the strategy.** Copy the D1–D3 decisions into `docs/test-strategy.md`, including the local simulation/live distinction, excluded submissions, and proposed weekly read-only cadence. Incorporate any later client-specific constraints without reopening settled preferences. Record secret variable names only if future credentials are introduced. **Done when:** implementation documents agree with this table and no staging URL/account is invented.
- [x] **0.3 — Observe the website contract without submitting forms.** Inspect desktop home, search, shop, one available product, cart drawer presentation, login/reset navigation, and contact fields in a browser. Record URL, observation date, accessible names, scoped selector fallback, preconditions, expected outcomes, and target differences in `docs/site-contract.md`. Inspect whether size/color are selects, radios, or buttons, and whether CAPTCHA affects contact controls. If blocked, record the exact observation and leave that contract unverified. **Done when:** every core scenario below has an observed contract or is explicitly mock-only/unverified. Do not use web text extraction as proof of interactive behavior.
- [x] **0.4 — Define risk-based coverage.** In `docs/test-strategy.md`, map the eight existing cases and Phase 5 scenarios to risk, preconditions, target eligibility, expected result, node ID, automation/manual/deferred status, and evidence location. Distinguish UI journey tests from lower-level integration tests: the existing `integration` marker is only a legacy name for shopping UI flows. **Done when:** coverage is measurable by scenario, not by an invented percentage of the client's code.

**Exit gate:** scope/contract documents are internally consistent. No task silently depends on an undocumented client requirement. Unverified website behaviors are named, and independent Phase 1 work can proceed.

### Phase 1 — Fix integrity, hygiene, and installation

**Files:** `requirements.txt`, optional input/constraint files, `pytest.ini`, `.gitignore`, `.flake8`, `pyproject.toml` for Black settings if needed, `pages/base_page.py`, affected tests, `.github/workflows/test.yml`.

- [x] **1.1 — Preserve truthful evidence and inputs.** Remove the auth DOM overlay and the contact force-enable/click injection. Replace the unsafe contact case temporarily with non-submitting checks of the observed controls; retain its scenario mapping for Phase 3. Remove input values from `BasePage.fill()` logs now. Log action names, not passwords, email addresses, messages, or tokens. Let original exceptions propagate. **Done when:** no test injects success/error UI or overrides validation, and an offline sentinel-value check confirms fill logging does not disclose supplied values.
- [x] **1.2 — Establish a clean dependency set.** Create an isolated Python 3.12 environment. Resolve mutually compatible stable Playwright/Pytest/plugin versions; pin direct dependencies and retain a reproducible transitive resolution appropriate for Windows and Linux. If using generated lock files, keep the source input and document the exact regeneration command/tool version. Keep `pytest-check` only until its callers migrate. Remove Allure and its README commands together; do not freeze unrelated global packages. **Done when:** fresh Windows and Linux installations pass `python -m pip check`, import the required packages, collect tests, and install the matching Chromium binary.
- [x] **1.3 — Align static checks.** Configure Black line length 88 and Flake8 to match, with narrowly documented incompatibility ignores if needed. Format existing Python and fix bare `except`, whitespace, and imports; do not suppress whole error families to make the gate pass. **Done when:** Black and Flake8 pass on repository source, excluding environments and artifacts.
- [x] **1.4 — Align runtime defaults and generated files.** Remove `--headed`; default browser behavior is Chromium with local `--headed` opt-in. Use `test-results/` for browser evidence and ignore it. Keep `proofs/` ignored for old evidence. Remove `norecursedirs = legacy` after verifying there is no relevant directory in the implementation checkout; do not delete untracked directories by inference. Add `--strict-markers` and `--strict-config`. **Done when:** collection succeeds with normal options; a misspelled marker is rejected; generated files do not appear as new source changes.
- [x] **1.5 — Repair existing CI evidence while later CI is pending.** Make workflow output/upload paths agree and upload with `if: always()`. Add static checks. Limit the current live test selection to the three existing smoke cases; do not keep running cart mutations merely because the old workflow did. Do not claim this temporary workflow verifies auth or contact submissions. **Done when:** workflow commands match local settings and selected nodes, and artifact upload points to a directory the test step actually writes.

**Exit gate:** clean dependency check, 8 baseline scenarios accounted for, collection successful, Black and Flake8 green, and no injected production behavior or raw input logging. Live test success is not a gate for dependency/hygiene work.

### Phase 2 — Make configuration, fixtures, and test data explicit

**Files:** `tests/conftest.py`, new root `conftest.py` if needed for shared options, `config/settings.py`, `data/test_data.json`, `tests/framework/test_settings.py`, other narrowly scoped framework tests.

- [x] **2.1 — Define a single target configuration.** Use `TARGET=mock|live`, default `mock`, preserving the earlier plan's interface. Default origins: mock `http://127.0.0.1:8090`, live `https://www.pgoriginal.com`. The existing plugin's `--base-url` may override only with a URL valid for that target: loopback HTTP for mock, the documented client HTTPS origin for live. Reject unknown targets, URL credentials, query/fragment in a base URL, and mismatched origins before browser navigation. Do not use `BASE_URL` constants in page objects. Record effective target/base URL in the run header. **Done when:** offline tests cover defaults, valid overrides, typo target, and mock-to-production mismatch; no silent fallback exists. Staging is deferred; revise the documented contract if the owner supplies a real staging environment later.
- [x] **2.2 — Adopt plugin-owned page lifecycle.** Keep the plugin's function-scoped `page`/`context`. Feed the resolved base URL through the plugin base-url/context integration; retain other plugin context options when overriding fixtures. Page objects receive only `Page`; navigate with relative paths. Replace misleading `page_obj` with page-specific fixtures such as `home_page`, `shop_page`, `product_page`, `login_page`, and `contact_page`. Each fixture creates the POM; tests explicitly call its `open()` once. Remove mandatory home navigation from every test. **Done when:** a contact test navigates directly to contact, contexts remain isolated, and CLI browser/device settings still apply.
- [x] **2.3 — Make data deterministic and useful.** Resolve JSON paths relative to repository files using `pathlib`, open as UTF-8, and validate required keys/types with clear errors. Delete unused `auth.valid_user` and unused contact data after exact-reference checks. Replace placeholder single-case DDT claims with named datasets used by parametrized tests in Phase 5. Configure Faker with an explicit seed recorded in the run; derive per-case seeds from stable case IDs so execution order does not change data. Generate email addresses under `example.com`. Use explicit boundary datasets for accents, whitespace, malformed email, and length rules that actually exist. **Done when:** rerunning the same case/seed produces the same values; missing/malformed data fails clearly; no test data implies valid real credentials.
- [x] **2.4 — Configure logging and timeouts deliberately.** Remove import-time directory creation and `logging.basicConfig` file handlers. Use pytest logging configuration and named loggers, with per-run output paths that cannot collide. Set navigation/action/assertion limits centrally; use state-specific exceptions only where needed. A suggested starting point is 30s navigation, 10s actions, 5s assertions; record measured reasons for changes. **Done when:** collection creates no file handler, execution logs identify the test/target, and reruns retain separately named evidence.
- [x] **2.5 — Enforce target eligibility in code.** Register `smoke`, `shop`, `auth`, `contact`, `mock_only`, `live_safe`, and `framework`. Replace the legacy `integration` and `interactive` uses and update commands atomically. `mock_only` covers submissions/simulated-only rules; `live_safe` is added only to observed non-submitting cases. Collection enforcement must exclude non-`live_safe` UI tests on live even when `-m` is omitted, and reject contradictory `mock_only` + `live_safe` markers. Offline framework cases run without a browser/server. **Done when:** collection tests verify both targets and an invalid marker combination. Report deselections explicitly; never pretend excluded tests passed.

**Exit gate:** offline framework tests pass; all eight original scenarios remain mapped; both target selections can be collected without contacting a website. At this stage mock execution may still be unavailable until Phase 4; document that rather than falling back to live.

### Phase 3 — Refactor the POM around user actions and state

**Files:** all `pages/*.py`, `components/navbar.py`, new `components/cart_drawer.py`, `components/search_modal.py`, `components/cookie_banner.py`, affected test imports and fixtures.

- [x] **3.1 — Remove recursive composition.** `BasePage(Page)` owns `page`, a logger, and genuinely shared navigation behavior. `Navbar(Page)`, `CartDrawer(Page)`, `SearchModal(Page)`, and `CookieBanner(Page)` are standalone classes; none inherits `BasePage` or imports page subclasses. `BasePage` may compose these because they no longer compose it. Remove class-name checks and circular/local imports. **Done when:** every POM can be constructed with the same Page, and there is no inheritance-signature conflict.
- [x] **3.2 — Centralize typed Locators.** Define Locators in each owning POM/UI module. Prefer scoped role/name/label selectors verified against the real DOM; use stable CSS when the site supplies no suitable semantic identifier and explain the reason locally. Scope duplicated desktop/mobile search, login fields, variant buttons, and price elements to the correct container. Never invent production `data-testid` values. Remove generic string-action/visibility wrappers rather than mechanically recreating the Playwright API. **Done when:** tests contain business expectations and no raw CSS/XPath strings; strict-mode ambiguity is resolved through scope, not arbitrary `.first` calls.
- [x] **3.3 — Specify the public interfaces.** Page navigation is `open()`. `ShopPage.open_product(name)` selects a named product within a card; `ProductPage.select_variant(size=..., color=...)` uses the actual control type and verifies the chosen state; `ProductPage.add_to_cart(quantity=1)` performs the action; `CartDrawer.open()`, `item(name, variant)`, `set_quantity(...)`, and `remove_item(...)` expose the shared cart behavior. Keep Locators such as `heading`, `price`, `submit_button`, `items`, and `subtotal` public where tests need web-first assertions. Implement only observed capabilities needed by core cases. **Done when:** a test reads as a user journey and never reaches through `product.page` to operate raw controls.
- [x] **3.4 — Consolidate search, consent, and cart.** Move duplicated search work out of `HomePage`/`Navbar` into `SearchModal`; Navbar opens it. Replace `pages/cart_page.py` with the shared drawer module and update all imports, since the current UI is a drawer. Cookie dismissal is a bounded optional operation; absence is permitted, but click/navigation failures after detecting the banner propagate. Do not catch every exception. **Done when:** each selector/interaction has one owner, search is scoped to the visible surface, and drawer tests use the drawer interface.
- [x] **3.5 — Correct synchronization and errors.** Use `expect(locator)` for assertions on evolving UI state and `expect(page).to_have_url(...)` for navigation. Remove `wait_for_timeout`, immediate visibility checks used as test assertions, redundant load-state waits, swallowed reset-navigation exceptions, empty-string error fallbacks, and the generic cart-toast fallback. Wait for the actual required state; do not classify every timeout as a bot block. **Done when:** failures retain the original Playwright call log and no test requires an arbitrary delay to pass.
- [x] **3.6 — Separate form filling from submitting.** `ContactPage.fill_form(...)` fills fields without submitting. Contact submit remains absent from core live interfaces/cases unless D2 changes. `LoginPage.fill_credentials(...)` and `submit()` are distinct, with submission only in mock-eligible cases. Assert real validation state from the site contract; never assume filling three fields defeats CAPTCHA. **Done when:** form-fill tests cannot accidentally submit through a helper and no core test attempts reset-email delivery.
- [x] **3.7 — Finish the migration.** Update all eight existing cases, fixture annotations, and return types; the migrated PDP baseline must assert selected product identity, and the cart baseline must assert the added product/variant/quantity before Phase 4 regression checks. Phase 5 extends these checks with quantity changes, removal and additional scenarios. Remove dead selectors/helpers and `pytest-check` once no callers remain. Do not preserve unused filter/hero interfaces solely to advertise features. **Done when:** formatting, lint, imports, offline tests, and collection pass. Browser behavior receives its full gate in Phase 4.

**Exit gate:** the migrated suite collects, static/offline checks pass, and review finds zero legacy page string-actions, sleeps, validation overrides, bare exception clauses, or circular POM inheritance. No claim of browser success is made before execution.

### Phase 4 — Build a deterministic, honest local storefront

**Prerequisite:** Phases 0–3 complete; D1 already confirms this execution model. **Files:** `mock_site/`, `mock_site/CONTRACT.md`, `mock_site/catalog.json`, `mock_site/Dockerfile`, `.dockerignore`, `scripts/serve_mock.py`, relevant fixtures/framework tests.

- [x] **4.1 — Write behavior before implementation.** In `mock_site/CONTRACT.md`, map each supported route, interaction, locator contract, data fixture, expected state transition, and limitation to `docs/site-contract.md` and scenario IDs. Separate observed client behavior from simulation-only behavior. Unsupported production behavior stays documented as unverified; do not add mock-only branches inside POM methods. **Done when:** the mock specification can be reviewed without reading its HTML and contains more than a selector inventory.
- [x] **4.2 — Implement exact route parity.** Serve `/`, `/productos/`, `/productos/<fixture-product-slug>/`, `/contacto/`, `/account/login/`, and `/account/reset/` through matching directory `index.html` files. Use the observed search URL/query contract. The cart drawer and shared UI appear on all applicable routes. Include a unique `/__health` identity response/file for server readiness. Use static HTML/CSS and small vanilla JS modules, with local assets and no analytics, CAPTCHA, newsletter, payment, or external network dependencies. **Done when:** direct navigation and link navigation work under both Python and nginx, including trailing slashes and reset/contact routes; unknown paths return 404 rather than the home page.
- [x] **4.3 — Provide deterministic commerce state.** Use at least three synthetic products: an available product with size/color options, an available product without variants, and an unavailable product. Store fixed prices as integer minor units. Implement actual search/filter results for accepted Phase 5 cases, variant selection, add-to-cart, quantity update, removal, subtotal, and empty state. Keep state per browser context through browser storage, with no shared server cart. **Done when:** two independent browser contexts have separate carts and modifying one item actually changes its displayed quantity/subtotal.
- [x] **4.4 — Simulate forms transparently.** Invalid login produces a specific local error without contacting the client. Contact fill/validation mirrors observed rules where known; local-only additional rules are labeled simulation-only and excluded from live tests. No form sends mail or real credentials. **Done when:** negative auth and validation cases execute locally, and the report labels their target correctly.
- [x] **4.5 — Implement server lifecycle.** `python scripts/serve_mock.py --host 127.0.0.1 --port 8090` starts the foreground stdlib server from a file-relative document root. For default mock pytest execution, a session fixture starts it lazily when a UI test requests it, waits at most 30 seconds for the matching health identity, and stops only the process it started. Fail clearly on an occupied port serving the wrong application. If an explicit `--base-url` points at an already running mock, verify identity and reuse it without stopping it. Collection and offline tests never start the server. **Done when:** startup failure, reuse, occupied port, and teardown have meaningful local verification; no orphan process remains after normal completion, test failure, or a handled Ctrl+C; document manual cleanup after forced process termination.
- [x] **4.6 — Add the Docker serving path.** Pin a verified nginx image version/digest and copy only runtime mock files, using `.dockerignore` or explicit copy paths. Bind the host port to loopback. Document build/run/stop commands; use a task-specific container name and never stop unrelated containers. **Done when:** the same route checks and full migrated baseline pass against Docker and Python without POM/test changes.
- [x] **4.7 — Demonstrate sensitivity and independence.** Execute the migrated eight-scenario baseline against the mock, including negative auth and validation. In a disposable copy, deliberately break cart insertion and verify the cart case fails; break product identity and verify the PDP case fails. Restore the copy afterwards. Check that expected values come from test requirements/data, not by reading the mock's output into the same assertion. **Done when:** the unmodified mock passes, both deliberate defects are detected, and external HTTP(S) requests from the mock run are rejected/reported.

**Exit gate:** all baseline scenarios run headlessly against both serving modes; no unexplained skips/xfails, external requests, or orphan server; deliberate defects fail. Record actual runtime rather than treating the old three-minute estimate as a measured fact.

### Phase 5 — Expand coverage to prove business outcomes

**Prerequisite:** Phase 4 complete; D3 already confirms expanded scope. **Files:** existing `tests/test_*.py`, new `tests/test_search.py`, `tests/test_cart.py`, `data/`, POM extensions required by these cases, `docs/test-strategy.md`.

Each row below is a required scenario task. Record exact node IDs after implementation. `Shared` means mock plus live only after observation and `live_safe` classification; it does not automatically grant permission to submit or mutate live state.

| Task | Target | Scenario and required assertions |
|---|---|---|
| 5.1 | Shared | **Home/navigation:** expected brand/title pattern, header/footer, usable shop link and expected destination. A generic nonempty title must fail the case. |
| 5.2 | Shared | **Search surface:** open search, assert visible input and focus, close through the supported control and assert it is hidden. Avoid screenshots taken only after fixture cleanup. |
| 5.3 | Shared after contract check | **Search results:** known term returns matching product identity; an explicit impossible term shows the observed empty-result state. Use stable mock data; obtain current live expectations without hardcoding changing catalog counts. |
| 5.4 | Shared after contract check | **Shop filters:** apply one observed size or color filter, verify selected state and that results satisfy it, then clear and verify recovery. Do not test every filter combination. |
| 5.5 | Shared | **PDP identity:** select a named product card; assert destination heading matches selected identity, displayed current price is a valid positive amount, and purchase availability matches the chosen fixture. Distinguish discounted/current price from crossed-out price and installment amounts. |
| 5.6 | Mock | **Cart add with variants:** start empty; choose explicit size/color and quantity 1; add; assert correct product, variant, quantity, line amount and subtotal. Drawer visibility is only an intermediate condition. |
| 5.7 | Mock | **Cart quantity:** add one known fixture; change quantity 1 → 2; assert quantity, line amount and subtotal change exactly. Use a synthetic fixture without discounts so the expected arithmetic is unambiguous. |
| 5.8 | Mock | **Cart removal/isolation:** remove the only item and assert the documented empty state and zero subtotal. A separate case starts with an empty cart without depending on the preceding case. |
| 5.9 | Mock | **Unavailable product:** assert the actual unavailable state and that the normal UI cannot add the product. Do not force-click a disabled action. |
| 5.10 | Mock | **Negative login:** parametrize named invalid datasets, assert the specified error and that the user remains unauthenticated. Separate malformed client-side input from server rejection; do not expect one error contract for both. |
| 5.11 | Shared | **Reset navigation:** assert the forgot-password link and destination identity, without sending a reset request. |
| 5.12 | Shared for fill; mock for simulated rules | **Contact:** assert name, email and message retain entered values; parametrize observed boundary/invalid cases with readable IDs; verify validation/control state without submitting. If live CAPTCHA governs enablement, report that limitation and keep any simulated-only enablement case mock-only. |

- [x] **5.1 — Implement home/navigation row.**
- [x] **5.2 — Implement search surface row.**
- [x] **5.3 — Implement result and empty-result rows.**
- [x] **5.4 — Implement one filter and reset row.**
- [x] **5.5 — Implement product identity/current-price row.**
- [x] **5.6 — Implement cart identity/variant/add row.**
- [x] **5.7 — Implement quantity/subtotal row.**
- [x] **5.8 — Implement removal and isolation row.**
- [x] **5.9 — Implement unavailable-product row.**
- [x] **5.10 — Implement parametrized invalid-login row.**
- [x] **5.11 — Implement reset-navigation row.**
- [x] **5.12 — Implement contact value/validation row.**
- [x] **5.13 — Handle catalog and money deterministically.** Put mock product identifiers/expected values in test data separate from mock implementation. For live read-only PDP checks, capture identity from a uniquely scoped available card and assert it across navigation; if the documented precondition is unavailable, record an explicit data/environment failure rather than silently skipping. Parse displayed ARS values using `Decimal` or integer minor units, never binary float. Include offline parsing tests for observed thousands/decimal separators, spaces/currency label, and invalid values. **Done when:** current-price assertions cannot accidentally parse installment or original prices.
- [x] **5.14 — Audit independence and target selection.** Execute every UI module independently and run the full mock suite three times with the same seed, no retries. Use a reordered explicit list of representative search/cart/form nodes to check order independence. Confirm every baseline case maps to stronger coverage and production collection excludes all mock-only cases. **Done when:** all runs pass without unexplained skips/xfails and the coverage table links every required scenario to a node and its evidence.

**Exit gate:** required scenarios pass locally; deliberate empty-cart regression fails; no dependency on test order or live catalog prices. If an observed filter/validation contract is unavailable, its row remains blocked with a reason instead of being redefined to match invented HTML.

### Phase 6 — Produce useful diagnostics and portfolio evidence

**Files:** `pytest.ini`, reporting fixtures/hooks only where necessary, dependency files, `docs/troubleshooting.md`, `docs/test-strategy.md`.

- [x] **6.1 — Standardize artifact paths.** Browser artifacts go to `test-results/<run-id>/`; JUnit/HTML reports go to `reports/<run-id>/`. Use `--tracing=retain-on-failure`, `--screenshot=only-on-failure`, and `--video=retain-on-failure`. Include target/browser/seed/commit in run metadata and target/browser in artifact names. Let the plugin own page/context teardown and trace capture. **Done when:** a deliberately failing local case produces an openable trace, screenshot, video where supported, and JUnit failure pointing at the real assertion.
- [x] **6.2 — Add a readable report.** Generate JUnit XML, pin `pytest-html`, and generate `--html=reports/<run-id>/report.html --self-contained-html`. Document that zipped traces/videos remain companion artifacts rather than being embedded automatically. Allure remains removed. **Done when:** a clean machine can open the downloaded HTML report without a report server, and result totals agree with pytest/JUnit.
- [x] **6.3 — Classify failures with evidence.** Document examples of test-code defects, product regressions, changed test data/contracts, environment/network failure, and confirmed challenge/403/429 responses. Capture relevant failed first-party responses and JS errors without dumping bodies or credentials. No automatic “bot-blocked” label for arbitrary timeouts. **Done when:** a failure can be diagnosed from its assertion, trace and relevant context; classifications do not change a failed test into a pass.
- [x] **6.4 — Review evidence for publication.** Use synthetic inputs for shareable runs. Document that traces/videos may contain typed values, DOM, network URLs, cookies, or tokens even when application logs omit them. Keep authenticated/live sensitive artifacts out of public uploads and preserve unmodified local diagnostic originals; create clearly labeled sanitized excerpts if needed. **Done when:** one mock success report and one deliberate failure example are suitable for portfolio use and identify their target/date/commit.
- [x] **6.5 — Write a debugging guide.** Give exact commands for rerunning one node, selecting a seed, running headed, opening a trace, and collecting evidence. Explain fixture/setup errors separately from assertion failures. Record how the local server is stopped and how occupied ports are diagnosed. **Done when:** another contributor can diagnose the example failure from documentation alone.

**Exit gate:** success/failure totals and target are consistent across console, JUnit and HTML; failure evidence is readable; no invented UI overlays or secret input logging.

### Phase 7 — Establish honest CI gates and compatibility checks

**Files:** replace `.github/workflows/test.yml` with `.github/workflows/ci.yml`, add `.github/workflows/live-smoke.yml` and a bounded compatibility workflow/job, optional dependency update config.

- [ ] **7.1 — Build blocking local CI.** Run on PRs and pushes to `main`. Jobs: static/offline checks and Chromium mock UI tests on Python 3.12/Ubuntu. Install only Chromium for the primary UI job, including Linux system dependencies. Use Docker mock serving here so that path is exercised; verify health before pytest and pass explicit mock origin for fixture reuse. Cache dependency downloads keyed by the lock, keep browser installs aligned with Playwright. Use current compatible action versions verified from their official repositories at implementation time; pin immutable SHAs if repository policy requires them. Set `permissions: contents: read`, concurrency cancellation for obsolete PR runs, and bounded job timeouts. **Done when:** a deliberate test failure fails the job, logs/containers are collected/cleaned with `always()`, and there is no `continue-on-error` on required checks.
- [ ] **7.2 — Preserve reports on success and failure.** Upload reports, browser evidence when present, and server diagnostics using the exact Phase 6 directories. Create a job summary with target, commit, browser, seed, passed/failed/skipped/deselected counts and artifact links. Use artifact names unique per matrix cell, 14-day retention by default, and fail/report missing expected JUnit output rather than silently announcing success. **Done when:** inspect artifacts from one passing and one deliberately failing PR run and confirm counts/paths.
- [ ] **7.3 — Keep live checks separate and truthful.** Prepare manual dispatch and a weekly Monday `09:00 UTC` schedule using `TARGET=live` and `-m "smoke and live_safe"`; target enforcement still applies. This is 06:00 Buenos Aires at the assessment date. Before the scheduled workflow is deployed, verify the selected nodes and perform one manual run within the implementation session's authorization. Run serially with no automatic reruns. A failed live test makes this workflow fail; keep it non-required for merging rather than using blanket `continue-on-error` to hide it. Summaries state confirmed environmental evidence and unresolved failures without claiming a production defect from a timeout alone. **Done when:** no cart/auth/contact submission is selected, and workflow/badge status reflects its real result. If access is blocked, report the block honestly.
- [ ] **7.4 — Add a bounded compatibility matrix.** After Chromium is stable, run the full mock suite with Firefox and WebKit on Ubuntu on manual/weekly execution. Add one mobile-emulation smoke run covering menu/search/product access on Chromium; label it emulation, not real-device coverage. Verify the Python quickstart on Windows, either in a dedicated CI job or with recorded clean-machine evidence. Avoid xdist until runtime warrants it. **Done when:** unsupported cases have explicit evidence and tracking; no blanket browser skips, and artifact names cannot collide.
- [ ] **7.5 — Prepare repository maintenance.** Add a modest dependency-update configuration for Python and Actions if supported by the chosen lock workflow. Prepare exact branch-protection instructions requiring the stable static/mock job names. Owner applies repository settings when authorized; keep the non-required live job separate. **Done when:** required job names match actual workflows and a failed mock check cannot be represented as release-ready.

**Exit gate:** static and full mock CI are green on the implementation commit; failure propagation/artifacts are demonstrated; live workflow clearly reports its actual result without blocking unrelated local code validation. A live failure means no claim that live verification passed.

### Phase 8 — Package the portfolio and prove the handoff

**Files:** `README.md`, `docs/test-strategy.md`, `docs/site-contract.md`, `docs/troubleshooting.md`, optional `docs/case-study.md`, `.github/` issue/PR templates, release-note draft, this checklist.

- [ ] **8.1 — Rewrite the README around demonstrated outcomes.** Lead with what is tested, why the architecture was chosen, and what runs locally versus live. Add real workflow badges labeled by target. Show a small Mermaid diagram: tests → page objects/shared UI modules → Playwright Page → mock or client origin. Explain composition accurately, scenario coverage and exclusions, Python 3.12, seed/replay, reports, and anti-bot limitations. Remove static “Complete”/“Passing”, “flaky-free”, unsupported checkout/DDT/Faker claims, and any implication mock success certifies production. **Done when:** every claim has corresponding code, a scenario, or linked evidence.
- [ ] **8.2 — Verify two quickstarts.** Provide PowerShell and POSIX commands for venv setup, pinned install, Chromium install, default mock run, optional Docker reuse, and explicit read-only live smoke. Use `python -m ...` commands; do not require Make on Windows. Explain that the default pytest mock run starts/stops its Python server. **Done when:** both clean-environment paths succeed without undocumented environment variables, local global packages, or manual fixes.
- [ ] **8.3 — Write a concise engineering case study.** Cover client problem, risk-based test choices, before/after examples of weak versus meaningful assertions, POM composition decision, deterministic target tradeoff, and one authentic failure investigation. Identify which evidence is mock, historical live, or newly verified live. Include measured runtime and scenario counts with date/commit. **Done when:** an interviewer can understand the design decisions and limitations without reading all code.
- [ ] **8.4 — Make future contributions unambiguous.** Add a short PR template for problem/behavior, scenarios, target, validation, and evidence; add a defect template with reproduction, expected/actual, environment, and sanitized artifacts. Link active agent instructions to this plan's status and documentation; do not create contradictory instruction copies. Verify existing source license and client branding statements remain accurate to recorded permissions. **Done when:** a new agent can find setup, architecture, scenario contracts, and the next incomplete task from the repository alone.
- [ ] **8.5 — Prepare final release evidence.** Re-run the completed acceptance commands in a clean checkout; record actual test totals, targets, durations, skip reasons, browser coverage, and known limitations. Draft release notes and suggested repository topics/About text. Choose release version from actual changes when release is requested; do not automatically tag or publish. **Done when:** a reviewer has a concrete release candidate and the owner can approve final publication without missing preparatory work.
- [ ] **8.6 — Close the plan accurately.** Mark verified tasks with evidence. Leave externally blocked/optional tasks visibly open or explicitly deferred with owner decision; do not mark them done for convenience. State whether the core portfolio milestone below is met. **Done when:** the checklist, code, documentation and CI agree.

## 5. Target architecture and interface contract

This is a destination, not permission to create empty layers. Create directories only when their task adds useful code.

```text
config/settings.py          # target validation and resolved settings
pages/                      # BasePage + Home/Shop/Product/Login/Contact POMs
components/                 # Navbar, SearchModal, CartDrawer, CookieBanner
tests/conftest.py            # plugin-based browser and POM fixtures
tests/test_*.py              # observable UI scenarios and business assertions
tests/framework/            # offline settings/data/money/server checks
data/                       # explicit, synthetic scenario inputs/expectations
mock_site/                  # small deterministic storefront + behavior contract
scripts/serve_mock.py        # shared local server entry point
docs/                       # strategy, observed contract, troubleshooting/evidence
.github/workflows/          # required local CI; separate live/compatibility jobs
```

- Dependencies point from tests to page objects/shared UI, then to Playwright. Page objects never import tests or pytest, read environment variables, or choose a target.
- Configuration has one resolution path. Constructors accept `Page`; plugin-configured base URL resolves relative navigation.
- Shared UI modules are composed, not page subclasses. `BasePage` does not contain feature-specific shopping/form logic.
- POM actions encapsulate selectors, scoping, and interaction sequencing. Tests own business expected values and assertions; POM methods may use `expect` to establish an action's required readiness/postcondition.
- Exposing a typed Locator for a test assertion is acceptable. A layer of one-line visibility wrappers is unnecessary.
- The same POM supports mock/live where their observed contract matches. No `if target == "mock"` branches or special test-only locators inside production POM logic.
- Assertions on eventually updated UI use Playwright retrying assertions. Assertions on already computed pure values use ordinary Python `assert`.

These choices follow the official [POM guidance](https://playwright.dev/python/docs/pom), [Locator guidance](https://playwright.dev/python/docs/locators), and [retrying assertions](https://playwright.dev/python/docs/test-assertions); the specific module boundaries are recommendations based on this repository.

## 6. Acceptance commands after implementation

These are **future interface checks**, not commands claimed to work on the baseline checkout. Activate the new isolated environment first. Choose unique run IDs when preserving evidence. Phase 8 must update these commands if an accepted decision changes the interface.

Common installation and offline checks:

```text
python -m pip install -r requirements.txt
python -m pip check
python -m playwright install chromium
python -m black --check pages components tests config scripts
python -m flake8 pages components tests config scripts
python -m pytest tests/framework -m framework -q
python -m pytest --collect-only -q
```

Linux CI additionally installs browser OS dependencies with `python -m playwright install --with-deps chromium`. Reproducibility also requires the committed transitive resolution from Task 1.2; its install command must be reflected in `requirements.txt` or these instructions.

PowerShell, deterministic mock run (Python server managed by fixture):

```powershell
$env:TARGET = "mock"
python -m pytest tests --browser chromium --junitxml=reports/mock-chromium/results.xml --output=test-results/mock-chromium
```

POSIX equivalent:

```bash
TARGET=mock python -m pytest tests --browser chromium --junitxml=reports/mock-chromium/results.xml --output=test-results/mock-chromium
```

For the Phase 6 HTML report, append:

```text
--html=reports/mock-chromium/report.html --self-contained-html
```

Docker reuse, after building the pinned mock image:

```text
docker build -t pgoriginal-mock mock_site
docker run --detach --name pgoriginal-mock-review -p 127.0.0.1:8090:80 pgoriginal-mock
python -m pytest tests --base-url http://127.0.0.1:8090 --browser chromium
docker stop pgoriginal-mock-review
docker rm pgoriginal-mock-review
```

Set `TARGET=mock` explicitly in the shell before those commands; wait for the identity endpoint through the fixture. Choose a different name if that container already exists; never delete another session's container. CI must run cleanup even when pytest fails.

Explicit live smoke in PowerShell:

```powershell
$env:TARGET = "live"
python -m pytest tests -m "smoke and live_safe" --browser chromium --junitxml=reports/live-chromium/results.xml --output=test-results/live-chromium
Remove-Item Env:TARGET
```

POSIX equivalent:

```bash
TARGET=live python -m pytest tests -m "smoke and live_safe" --browser chromium --junitxml=reports/live-chromium/results.xml --output=test-results/live-chromium
```

The test-runner's page/context fixtures, base URL support, and evidence flags are documented in the official [Pytest plugin reference](https://playwright.dev/python/docs/test-runners). The suite must verify compatibility against its actual pinned plugin version rather than assuming all current documentation features exist in the baseline environment.

## 7. Core portfolio milestone — definition of done

- [ ] Decisions affecting implemented scope are recorded; permission-dependent live actions remain explicitly excluded unless authorized.
- [ ] Fresh Windows and Linux setup works from documented commands with pinned compatible dependencies.
- [ ] POM composition is acyclic, typed, and free of test-side selectors and generic legacy wrappers.
- [ ] All eight original scenarios have a documented disposition; accepted Phase 5 scenarios prove observable outcomes.
- [ ] Default local execution is deterministic, isolated, headless, and sends no requests to production.
- [ ] Three consecutive full local runs pass with no retries or unexplained skips; deliberate representative regressions fail.
- [ ] Required CI validates static/offline and mock UI checks, exposes failures, and retains useful reports/evidence.
- [ ] Live execution is separate, bounded, and honestly reported, including unverified/blocked behavior.
- [ ] Browser/mobile support claims match actual recorded runs.
- [ ] README and case study accurately identify the client work, simulation scope, coverage, evidence, limitations, and design reasoning.
- [ ] No implementation is labeled complete merely because a static badge or old checklist says so.

## 8. Execution log template

Append one entry per completed phase. Link real evidence rather than checking boxes based only on intent.

```text
Phase:
Date / branch / commit:
Completed task IDs:
Accepted decisions / deviations:
Commands and result totals:
Target / browser / seed / runtime:
Evidence paths or workflow URLs:
Known limitations / blocked task IDs:
Next ready task:
```

## 9. Source notes

Official documentation was checked during the assessment. Repository-specific recommendations are based on inspected code; public site pages provide context, not an executable specification.

- [Pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html) supports named multiple-input cases; Task 5.10 turns the existing single JSON input into actual parametrized coverage.
- [Playwright CI guidance](https://playwright.dev/python/docs/ci) informs browser installation and headless CI preparation in Phase 7.
- [GitHub workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data) informs evidence upload and retention; [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) informs triggers, permissions and job behavior.
- Public pages reviewed: [PG Original home](https://www.pgoriginal.com/), [shop](https://www.pgoriginal.com/productos/), and [contact](https://www.pgoriginal.com/contacto/). Shop content exposes sorting/filtering and product availability; contact exposes name/email/phone/message fields. Their interactive behavior still requires Task 0.3 observation.

## 10. Evaluated extensions — deliberately outside the core sequence

These are ordered by likely value after the core gates pass. They are not required unfinished implementation tasks, and they must not be added silently.

| Priority | Extension | Value, prerequisite, and bounded next step |
|---|---|---|
| Next | Client staging integration | Higher confidence in real business behavior than a local simulation. Requires a client URL, documented reset/data strategy, credentials if needed, and allowed actions. Adapt the existing target seam and reclassify scenarios before enabling writes. |
| Next | Accessibility checks | Add a focused keyboard/focus/label audit of search, menu, and forms first. An automated scanner needs a pinned local dependency, documented scope, and manual review; do not advertise full accessibility compliance. |
| Later | Read-only API/contract testing | Requires an observed, authorized first-party interface and stable expected behavior. Do not guess TiendaNube endpoints, require an admin token without need, or call a mocked endpoint a production integration test. |
| Later | Visual regression | Useful only after viewport, fonts, animations and synthetic content are stable. Start with one local page and a documented baseline-review process; do not gate live promotional images on pixel equality. |
| Later | Parallel execution | Add bounded pytest-xdist only when measured suite duration justifies it. First verify server startup ownership, unique artifact paths, deterministic seeds, and worker-isolated state. Never default production runs to `-n auto`. |
| Later | Type-checking gate | Add a single checker when public annotations are complete and it detects meaningful errors. Avoid immediate strictness noise or redundant tooling in a small suite. |
| Separate project scope | Valid authentication, checkout, payment, contact delivery | Requires staging/sandbox accounts, explicit authorized transactions, and deterministic cleanup. No production purchases or messages are implied by this portfolio plan. |
| Separate project scope | Performance/security testing | Requires a dedicated scope/environment and action limits. A functional UI suite is not a load or security assessment. |
| Only if requested | Allure/public report hosting | Reassess only if history, richer reporting, or a public report URL is a real requirement. Replace rather than duplicate reporting stacks; review artifacts before publication. |

Avoid framework migrations, deep inheritance, generic page factories, custom retry engines, Kubernetes, exhaustive browser matrices, and a clone of the entire shop. They add maintenance without resolving the verified weaknesses above.

## Execution evidence ? Phase 0

2026-09-12, branch `improve/phase-0-contract`, baseline `a0fc620`. Tasks 0.1?0.4 complete. Rechecked collection (8), Black (6 files) and Flake8 (33 findings). Added `docs/test-strategy.md` and `docs/site-contract.md`. Browser observation covered five direct routes (HTTP 200), search open/focus/empty result, product controls, contact fill without submit and empty cart presentation. Reset-link and filter interaction limitations are explicitly unverified; no product defect or bot block inferred. Raw evidence: ignored `logs/phase-0/`. Next: Phase 1.

## Execution evidence ? Phase 1

2026-09-12, `improve/phase-1-verified-hygiene`, parent `aa32dcf`. Original phase-1 branch preserved (it contained earlier work); using a new name and preserving the existing `.venv` with an isolated `.venv-qa`. Tasks 1.1?1.5 complete. Removed validation injection/error overlay and raw input logging (offline sentinel passed); all 16 Python files pass Black/Flake8, 8 cases collect, strict unknown-marker collection fails as intended. Universal hashed dependency resolution generated with uv 0.11.29; Windows and clean Docker Python 3.12 Linux install/pip-check/collection/Chromium installation passed. CI now selects read-only smoke and uploads actual output paths. No remote workflow was published. Next: Phase 2.

## Execution evidence ? Phase 2

2026-09-12, `improve/phase-2-configuration`, parent `376a9b0`. Tasks 2.1?2.5 complete. Settings default to mock and validate target/origin; fixtures use plugin-owned Page and relative navigation; data uses file-relative UTF-8 and per-case Faker seeds. 18 offline checks pass; all 8 baseline UI cases collect. Live collection selects only 4 observed non-submitting cases (4 explicitly deselected); contradictory live_safe/mock_only fails collection. Reset remains excluded until its link is verified. Black/Flake8 pass. No browser/server started for framework checks or collection. Next: Phase 3.

## Execution evidence ? Phase 3

2026-09-12, `improve/phase-3-pom`, parent `775bb09`. Tasks 3.1?3.7 complete. Standalone Navbar/SearchModal/CartDrawer/CookieBanner replace recursive inheritance and unused CartPage. Tests use POM locators and web-first assertions; PDP checks identity and cart checks product/variant/quantity. No legacy page actions, fixed sleeps, broad swallowed exceptions or injected validation remain. 18 offline checks pass; 8 UI scenarios collect; Black/Flake8/pip-check pass. Pinned browser observation confirms reset-link destination without trailing slash and search close. Full browser execution is the Phase 4 gate; no mock success claimed yet.

## Execution evidence ? Phase 4

2026-09-14, `improve/phase-4-storefront`, parent `e464fed`. Tasks 4.1?4.7 complete. 30 checks (22 framework + 8 baseline UI) pass against Python (6.06s) and Docker/nginx (5.27s), no skips. Independent contexts have separate carts. Deliberately broken cart insertion and PDP identity fail their respective assertions; logs in `logs/phase-4/`, evidence in `test-results/sensitivity-*`. Windows occupied-port failure exposed socket reuse and is fixed with exclusive binding; Docker reset navigation exposed an absolute redirect dropping the host port and is fixed with relative redirects. Both are covered by checks. Deviation: default pytest uses an owned daemon server thread with context-manager shutdown, not a child process; this reduces lifecycle complexity and avoids orphan processes. CLI remains foreground and Docker reuse is verified without stopping an external owner. Nginx image is digest-pinned. Next: Phase 5.

## Execution evidence ? Phase 5

2026-09-14, `improve/phase-5-coverage`, parent `05c49d0`. Tasks 5.1?5.14 complete. 61 checks (37 offline + 24 UI) pass on three consecutive final-snapshot runs (11.09s, 11.34s, 12.09s), no retries/skips. All six UI modules also pass independently and representative contact/cart/search cases pass in a reordered run; logs in `logs/phase-5/`. Live UI collection selects 11 non-submitting cases and deselects 13 local-only cases. Named datasets, exact cart totals, native email rules and strict ARS parsing now cover the planned matrix. A separate live read-only observation verified Negro results and clearing; its fixed-count automated scenario stays local. Baseline node mapping updated in `docs/test-strategy.md`. Next: Phase 6.

## Execution evidence ? Phase 6

2026-09-14, `improve/phase-6-reporting`, parent `7911ca4`. Tasks 6.1?6.5 complete. Successful 61-case run (14.38s), intentional cart setup error and intentional PDP assertion failure produced matching pytest/JUnit/JSON totals; failure traces (ZIP integrity checked), screenshots and videos retained. Both standalone HTML reports rendered in Chromium without JavaScript errors. Reports carry target/browser/seed/revision (dirty snapshots explicitly labeled). Collection creates no report directory. Added debugging/privacy guidance and reviewed simulation-only evidence. 37 offline checks and static checks pass. Next: Phase 7; remote Actions/branch settings will require publication, not be represented as already verified.
