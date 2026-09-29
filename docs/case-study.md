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

## Keeping the simulation honest

A simulation is only useful while it looks like the real thing. When I
re-checked the live store, two page-object methods turned out to have been
written against markup the mock had invented: the cart drawer's "Cerrar
carrito" button doesn't exist live (the real control is an unnamed icon
link), and the menu's SHOP entry is a toggle that opens a sub-panel, not a
link to the shop. Both would have failed on production while the mock suite
stayed green.

I fixed the mock to match the observed markup rather than the other way
round, added the real pricing model (prices per variant, with a compare-at
price only on promotions), the size filter and load-more pagination, and
wrote read-only locator contract checks that run against both targets. The
menu journey now passes on live too.

## An intermittent failure, traced to its cause

After the page-object refactor, one full run in six failed: a product page
stayed blank. The trace showed the navigation request ending in
`net::ERR_NO_BUFFER_SPACE`, a Windows socket-exhaustion error, not a locator
problem. The local server spoke HTTP/1.0, opening a new socket for every
request, and hours of back-to-back runs had left thousands of sockets in
`TIME_WAIT`. I first suspected the server's listen backlog, but 400
concurrent requests succeeded at the default size, so I dropped that theory.
Switching the server to HTTP/1.1 keep-alive, as nginx does, cut connections
per UI run from 290 to 72.

That change then exposed a second, older bug on Linux CI: the simulation
wired its cookie and header buttons only after the product catalog loaded,
so a click during a slow response did nothing. A test that holds the catalog
request open reproduced it on every run; wiring the controls first fixed it,
and a new mutant keeps it from coming back.

## Testing production without distorting it

Read-only isn't the same as harmless. Watching the network showed that
every live page load fired ad pixels, a recommendation widget, telemetry
collectors and the store's own visit counter, so a weekly suite was quietly
inflating PG Original's analytics. Live runs now abort those requests (about
240 per run) while everything the page needs still loads, identify
themselves with a user-agent suffix, skip `robots.txt`-disallowed paths when
checking links, and stay serial and weekly.

With that in place, the live checks go beyond "the page loads": every
listing card's price must match the variant data it publishes, the listing,
product page and price attribute must agree, variant prices must follow
selection, and infinite-scroll pagination must add products without
repeats. One check found a real defect: product pages publish JSON-LD only
for *related* products, never for the product being viewed. That check is a
strict expected failure on live (reported with its defect ID, and it will
flag the day the store fixes it) and passes on the simulation, which
publishes correct structured data.

## Accessibility: what the scanner missed

An axe-core scan of the five main live pages reported no WCAG A/AA
violations. Keyboard checks told a different story: opening the cart from
the keyboard left focus on the header icon behind the overlay, and reaching
the drawer took 143 Tab presses; the close controls had no name and, for the
menu and cart, couldn't be focused at all; Escape closed nothing. Scanning
with the cart open found one more issue. Along the way I withdrew one of my
own earlier findings: "images without alt" were invisible placeholders.

The simulation now implements the accessible behavior, with mutants that
remove it, and the live defects are strict expected failures, so the
weekly report shows exactly which are still open.

## Real markup, without touching the store

The mock proves the tests detect wrong outcomes; the weekly live run proves
the page objects still fit the real site. In between, pull requests had no
way to exercise real markup. I added a third target: the read-only live
suite records its traffic once, a script merges and sanitizes it (no
cookies, placeholder images, no trackers or bot challenges), and
`TARGET=snapshot` replays it through Playwright's HAR routing. Anything the
recording lacks is aborted. To prove the replay never reaches the network, I
ran it behind a proxy that refuses every connection: a live test failed at
once, and the whole snapshot suite passed. A weekly job re-records the store
and compares the selectors the page objects use on both recordings, so a
theme change opens an issue instead of silently breaking the next live run.

The first pull-request run of the snapshot job failed on the login page, in
fixture setup rather than in a test. The trace showed the cookie banner's
dismiss control resolved but hidden, then visible a moment later. The store's
script shows the banner after load; when it appeared just after my 500 ms
wait, the fallback check saw it visible and raised instead of dismissing it.
The snapshot's heavier parallel load made the timing visible, but the same
race existed on live. The fix dismisses a banner that turns up late and still
fails on one that can't be dismissed; repeated parallel runs and a live
check passed afterwards.

The refresh job's own first run on `main` also failed: its replay step
reused the recording's run ID, and the single-use rule refused it. That
opened a false drift issue, which I closed with the cause and fixed in the
workflow. The selector comparison in the same run had found no drift.

Screenshots of the simulation are now compared with reviewed baselines. I
set the budget from measurement, not guesswork: recoloring one struck-through
price changes about 345 pixels, and repeated runs change none, so the limit
is 25. My first baselines were per platform: Windows from my machine, Linux
from the CI runner. A clean clone on a plain Ubuntu machine failed all six,
because its fonts differed from the runner's. Baselines now come from one
pinned environment, Playwright's Docker image, in CI and locally; normal runs
skip the visual checks and say why. Repeating the comparison in that image
then exposed a flaky screenshot of the product page taken before its content
rendered. Waiting for the page's own URL, its heading and its fonts fixed it:
eight repeated runs, no changes.

## Results

| Measure | Value |
|---|---|
| Collected cases | 241: 79 UI, 162 offline framework |
| Mutation score | 27 of 27 injected defects detected (first measured at 6 of 13) |
| Mock run (Windows, Chromium) | 44 s serial, 22 s with parallel workers |
| Snapshot replay | 42 live-safe checks on recorded live markup, offline, on every pull request |
| Live read-only cases | 43 (`live_safe`), all in the weekly live run, 11 of them expected failures for known store defects; about 240 tracking requests blocked per run |
| Browsers | Chromium, Firefox, WebKit on the mock; Pixel 7 emulation smoke |
| CI | Required static and framework checks on Ubuntu and Windows, plus mock UI on Ubuntu; visual checks in a pinned container and snapshot replay on every pull request; weekly live, snapshot refresh and compatibility runs; nightly flaky-test check |
| Defects found in the live store | 8, reported privately to the client; 6 tracked by `live_defect` checks; one earlier finding withdrawn after inspection |

## Trade-offs and limits

The mock trades backend realism for reproducibility. Its cart, login
rejection and form states are simulated, so passing them says nothing about
production checkout, payments, email delivery or authentication. The live
checks are deliberately narrow. A separate trial store was considered for
cart and checkout and not adopted: it would need an account owned by the
store, its theme would differ, and checkout would still need a payment
sandbox. With a resettable client staging store, the same POM and target
seam could run those flows against real platform logic.
