# Case study: testing a live storefront without a test environment

## The problem

PG Original runs its store on Tiendanube. When I tested it there was no
staging site, no test accounts and no payment sandbox. Everything reachable
was production, with real customers and real orders. So I needed automation
that:

1. could be run on every change, deterministically, without touching
   production;
2. still told me something true about the real site;
3. never confused those two kinds of results.

My first version was a small Playwright suite of eight tests against the live
site. It worked as a demo, but it had problems I would flag in anyone's code
review:

| Weakness in the first version | Why it mattered |
|---|---|
| The contact test used JavaScript to enable a disabled submit button, then clicked it | The test changed the behavior it claimed to verify |
| A catch-all exception handler painted a "blocked by anti-bot" overlay on any failure | Real failures were relabeled with an invented cause |
| "Add to cart" passed if the drawer opened, even when the cart was empty | The test couldn't detect the main bug it existed for |
| Every input value, passwords included, went to the log | Test evidence leaked data |
| `Navbar` inherited from `BasePage`, which also built a `Navbar` | Circular design held together by a class-name check |
| Hard-coded URL, unseeded Faker, cwd-relative paths, unpinned dependencies | Runs weren't reproducible |

## Decisions

**Two targets, never mixed.** A local synthetic storefront (`mock_site/`)
reproduces the observed markup and simulates what can't be exercised safely
in production (cart arithmetic, login rejection, stock). A separate live
target runs only non-submitting checks. The target is validated before any
browser starts: the mock accepts only loopback HTTP, live accepts only the
store's HTTPS origin, and in mock runs any external request fails the test.

**Eligibility enforced in code, not by convention.** Each UI test is
`live_safe` or `mock_only`. On the live target, collection drops everything
that isn't `live_safe`, even if someone forgets `-m`. A test can't claim both.

**Composition over inheritance in the POM.** `BasePage` is small and composes
independent `Navbar`, `SearchModal`, `CartDrawer` and `CookieBanner` objects.
Page objects own locators and user actions; tests own expected values and
assertions. Locators are scoped to the owning container (e.g. `#product_form`,
`#contact-form`) to resolve the store's duplicated responsive markup, never
by grabbing `.first`.

**Assertions on business outcomes.** A product test checks that the name on
the card I clicked is the heading of the page I landed on, and that the
current price (not the crossed-out price or an instalment amount) parses to
a positive ARS value. A cart test checks product, variant, quantity, line
amount and subtotal against independent test data. Money is parsed into
integer minor units with a strict parser that rejects ambiguous formats.

**Evidence that survives failure.** Each run writes JUnit, a self-contained
HTML report and a JSON summary tagged with target, browser, seed and git
revision. Failures keep trace, screenshot and video. The CI summary refuses
to render if the JUnit file is missing, so a crashed run can't look green.

| Earlier assertion | Current assertion |
|---|---|
| Product page element is visible | Clicked card name == PDP heading; current ARS price > 0 |
| Cart drawer opened | Exact product, variant, quantity, line amount and subtotal |
| Contact submit "worked" after forcing it on | Native email validity observed; submit left untouched |
| "Probably blocked by anti-bot" | Real failure, target and trace retained for diagnosis |

## A real failure investigation

The first live smoke run after the refactor passed home and search but failed
the product test with a strict-mode locator error. The trace showed that
`#product_form` contained two elements with class `.js-addtocart`: the real
submit input and a hidden animation placeholder. My locator matched both.

This was an automation defect exposed by real markup, not a store defect and
not bot detection. I scoped the locator to `input[type="submit"].js-addtocart`
and added the same placeholder to the local storefront, so every mock run now
exercises that ambiguity. The corrected live smoke passed in 8 seconds, with
no cart action taken.

## Proving the tests can fail

A passing suite only means something if it fails for the right reasons. On
disposable copies I:

- broke cart insertion: the "UI says *Agregado al carrito* but the cart is
  empty" state ([screenshot](evidence/mock-cart-error.png)) made the cart
  fixture fail with a setup error, with trace, video and screenshot kept;
- broke product identity: the PDP assertion failed;
- in CI, changed one expected price by one cent on a throwaway PR: exactly
  the two dependent cart assertions failed, the job stayed red, and all
  artifacts uploaded. Reverting it returned CI to green; the change was never
  merged.

Hand-picked experiments prove a point once. To measure it continuously I
built a small mutation-testing harness: a catalog of 13 realistic storefront
defects, each applied to a disposable copy of the simulation while the UI
suite runs. The first measurement was humbling: **6 of 13 (46%)** were
detected. Search could return the whole catalog, a repeat add could create a
duplicate line, the chosen quantity could be ignored, the cart could vanish on
navigation, and "remove" could empty everything, all with a green suite.

The fix wasn't more tests for their own sake but sharper oracles: exact
result sets for search instead of "contains", quantity above 1, repeated adds,
a navigation step after adding, and removal from a two-line cart. The score
went to **13 of 13**, and a weekly workflow now fails if it drops below 90%.
Details are in the [test strategy](test-strategy.md#test-effectiveness-mutation-testing).

## Results

| Measure | Value |
|---|---|
| Collected cases | 99: 32 UI, 67 offline framework |
| Mutation score | 13 of 13 injected defects detected (was 6 of 13) |
| Mock run (Windows, Chromium) | ~15 s |
| Live read-only cases | 11 (`live_safe`), 3 in the weekly smoke |
| Browsers | Chromium, Firefox, WebKit on the mock; Pixel 7 emulation smoke |
| CI | Required static and framework checks on Ubuntu and Windows, plus mock UI on Ubuntu; weekly live and compatibility runs |
| Defects in the store's markup | 5 accessibility/HTML issues documented in the [site contract](site-contract.md) |

## Trade-offs and limits

The mock trades backend realism for reproducibility. Its cart, login
rejection and form states are simulated, so passing them says nothing about
production checkout, payments, email delivery or authentication. The live
checks are deliberately narrow. With a resettable client staging store, the
same POM and target seam could run cart and checkout flows against real
platform logic.
