# From an eight-test demo to a verifiable QA portfolio

PG Original is a real client storefront, but this project has no staging site,
test accounts or transaction sandbox. The engineering problem was to demonstrate
useful automation without conflating a simulated order with production quality.
The approved approach pairs a deterministic local storefront with a small,
separate live browsing suite.

## What changed and why

At baseline `a0fc620`, eight scenarios collected, but assertion quality and
architecture limited their value. Shared navigation inherited from the page
base, selectors and actions were mixed, data was incompletely used, reporting
instructions did not match installed tooling, and tests could force a disabled
contact control or show an invented failure overlay.

Those behaviors were removed. A small `BasePage` now owns navigation and composes
independent Navbar, SearchModal, CartDrawer and CookieBanner objects. Tests own
assertions; POM objects hide observed selector details and expose domain actions.
Playwright's plugin owns browser/context teardown and failure evidence. This
keeps one lifecycle and avoids a second custom test framework.

| Earlier weakness | Current observable assertion |
|---|---|
| Product presence could pass for the wrong selection | Selected card name must equal the PDP heading; current ARS price parses to a positive amount |
| An open cart could be treated as a successful add | Exact product and variant, quantity, line amount and subtotal must agree with independent expectations |
| Contact control changed by injected JavaScript | Original disabled state and native email rules are observed; no contact submission |
| Broad exception handling invented a bot-block explanation | Real pytest failure/error, target and browser evidence are retained for investigation |

Risk-based coverage prioritizes discovery, product identity and cart arithmetic.
The suite grew to 62 cases: 37 offline and 25 UI. Named inputs cover negative
authentication, accented/whitespace contact data and strict currency parsing.
Seeded Faker values use example.com and repeat per case. Every UI scenario has
its own context; the mock rejects external requests. Three consecutive full
Phase 5 runs passed 61 cases in 11.09–12.09 seconds before the menu smoke case
was added. They were not reruns that concealed failures.

## A real failure investigation

On 2026-09-14, the first three-case live smoke passed home navigation and search
but failed the product check. The trace showed a strict locator error: the
product form contained both a submit input and an animation placeholder with
class `.js-addtocart`. The broad locator matched both.

The fix scopes the action to `input[type="submit"].js-addtocart`. The local
storefront now includes the same duplicate placeholder so ordinary product
and cart scenarios exercise that ambiguity. The corrected live smoke passed
three cases in 8.06 seconds. No cart action was executed. This was an automation
defect revealed by live markup, not a client purchase failure or a bot block.

A separate deliberate local cart-insertion defect demonstrated failure
sensitivity: the fixture could not establish its added-product precondition, so
pytest correctly reported a **setup error**, retained a trace/video/screenshot,
and agreed with JUnit and the JSON summary. A deliberate PDP identity defect
produced an assertion failure. The
[reviewed screenshot](evidence/mock-cart-error.png) depicts only the simulated
cart experiment. Raw live traces remain private.

## Evidence and tradeoffs

The implementation at `68a09f4` adds the final selector correction, menu case
and CI workflows. During that change, Windows Chromium passed all 62 checks in
14.58 seconds; clean Debian/Python 3.12 containers passed 62 in Chromium
(18.38s), Firefox (29.79s) and WebKit (25.25s). These measurements came from the
working tree that became that commit, seed 1729. Windows Firefox and WebKit also
passed all 25 UI cases, and Pixel 7 Chromium emulation passed four smoke cases.
Final clean-checkout measurements and exact revisions are recorded separately in
[release-verification.json](evidence/release-verification.json).

The mock trades backend realism for reproducible CI. Its catalog, cart storage,
login rejection and disabled contact state are simulated; neither its success
nor the three live smoke passes establish checkout, payment, delivery or valid
authentication. The live selector regression demonstrates why the separate live
contract checks matter. A client staging integration is the next substantive
extension when resettable data and authorized actions are available.

The workflows prepare Windows/Ubuntu quality checks, Docker-served Chromium
mock UI, separate weekly live smoke and bounded compatibility checks. Remote
passing/failing PR artifacts and branch protection still require publication
acceptance. This is a locally validated candidate, not a claim of an already
green release pipeline. See [CI maintenance](ci-maintenance.md).
