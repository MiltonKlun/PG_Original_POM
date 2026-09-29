# Defect reports: pgoriginal.com

Defects found in the public store while building and running this suite.
All were reproduced read-only: nothing was added to a cart, submitted or
changed. Automated checks that track each defect run weekly; on the live
store they're strict expected failures, so a fix is reported automatically.

**Status of all reports:** open, not yet reported to PG Original.

| ID | Summary | Severity | Standard | Tracked by |
|---|---|---|---|---|
| [DEF-06](#def-06-focus-stays-behind-the-overlay-when-the-menu-or-cart-opens) | Opening the menu or cart leaves keyboard focus behind the overlay | High | WCAG 2.4.3, 2.1.1 | `test_keyboard.py::test_opening_a_panel_moves_focus_into_it` |
| [DEF-04](#def-04-close-controls-have-no-name-and-two-cant-be-focused) | Close controls have no accessible name; menu and cart ones can't be focused | High | WCAG 4.1.2, 2.1.1 | `test_keyboard.py::test_close_control_is_named_and_focusable` |
| [DEF-05](#def-05-escape-doesnt-close-header-panels) | Escape doesn't close search, menu or cart | Medium | WAI-ARIA dialog pattern | `test_keyboard.py::test_escape_closes_panel_and_returns_focus` |
| [DEF-07](#def-07-the-open-cart-drawer-cant-be-scrolled-by-keyboard) | The open cart drawer can't be scrolled by keyboard | Medium | WCAG 2.1.1 | `test_accessibility.py::test_open_panel_meets_wcag_aa[cart]` |
| [DEF-01](#def-01-product-pages-dont-publish-their-own-structured-data) | Product pages don't publish their own structured data | Medium | schema.org `Product` / `Offer` | `test_catalog_integrity.py::test_product_page_publishes_its_price_as_structured_data` |
| [DEF-02](#def-02-the-restock-alert-apps-configuration-request-fails) | The restock-alert app's configuration request fails on every page | Medium | — | Network observation |
| [DEF-03](#def-03-login-labels-arent-associated-with-their-fields) | Login labels aren't associated with their fields | Low | WCAG 1.3.1, 3.3.2 | `test_accessibility.py::test_login_fields_have_associated_labels` |
| [DEF-08](#def-08-duplicate-idemail-on-the-contact-page) | Duplicate `id="email"` on the contact page | Low | HTML validity | Site contract observation |

Severity reflects impact on shoppers: **High** blocks a task for keyboard or
screen-reader users; **Medium** degrades a feature or its discoverability;
**Low** has a working fallback.

---

## DEF-06: Focus stays behind the overlay when the menu or cart opens

- **Observed:** 2026-09-28, Chromium, desktop 1440×1000
- **Steps:** 1. Open `https://www.pgoriginal.com/`. 2. Press Tab until the cart
  icon in the header is focused. 3. Press Enter. 4. Press Tab repeatedly.
- **Expected:** the drawer opens and focus moves into it, so the next Tab
  reaches the drawer's content (items, checkout, close).
- **Actual:** the drawer opens but focus stays on the header icon behind the
  overlay. Tab moves through links hidden behind the drawer; the first Tab
  stop inside the open drawer came after **143** presses. The menu behaves
  the same way. The search panel does move focus into its input.
- **Impact:** keyboard and screen-reader users can't practically reach the
  cart or the menu.

## DEF-04: Close controls have no name, and two can't be focused

- **Observed:** 2026-09-28
- **Steps:** open the search panel, the menu and the cart drawer; inspect each
  close (×) control in the accessibility tree, and try to focus it with Tab.
- **Expected:** each close control is a button with a name such as "Cerrar
  carrito", reachable by keyboard.
- **Actual:** all three have an empty accessible name. The cart control is an
  `<a>` without `href`; the menu control is a `<div>`. Neither can receive
  keyboard focus.
- **Impact:** screen readers announce an unlabeled element, and together with
  DEF-05 keyboard users have no way to close the menu or the cart.

## DEF-05: Escape doesn't close header panels

- **Observed:** 2026-09-27 (menu), 2026-09-28 (search and cart)
- **Steps:** open the search panel, the menu or the cart with the keyboard,
  then press Escape.
- **Expected:** the panel closes and focus returns to the control that opened
  it, as in the WAI-ARIA modal dialog pattern.
- **Actual:** nothing happens; the panel stays open. While the menu is open it
  also intercepts clicks on the header.

## DEF-07: The open cart drawer can't be scrolled by keyboard

- **Observed:** 2026-09-28, axe-core 4.12.1
- **Steps:** open the cart drawer and run an axe-core scan (WCAG 2.1 A/AA).
- **Expected:** no violations.
- **Actual:** `scrollable-region-focusable` on `#modal-cart`: the drawer is a
  scrollable region with no focusable content or focusable container, so
  keyboard users can't scroll it.

## DEF-01: Product pages don't publish their own structured data

- **Observed:** 2026-09-28 on four product pages, including
  `/productos/remeras-mw-mustang/` and `/productos/remera-mu/`
- **Steps:** open a product page and list its
  `<script type="application/ld+json">` blocks.
- **Expected:** a `Product` block whose `mainEntityOfPage` is the page URL,
  with the current price and availability in its `Offer`.
- **Actual:** the page has `Organization`, `WebPage` and 3–6 `Product` blocks,
  all for *related* products; none describes the product being viewed.
- **Impact:** search engines get no structured price or availability for any
  product page, which limits rich results in search.

## DEF-02: The restock-alert app's configuration request fails

- **Observed:** 2026-09-28, on every page load
- **Steps:** open any page with the browser's network panel open; filter for
  `Cheguei`.
- **Expected:** HTTP 200 for the app's settings file.
- **Actual:** HTTP 403 for
  `empreender-sa-east-1.s3.sa-east-1.amazonaws.com/Cheguei/public/settings/nuvem_shop-693159.json`.
- **Impact:** the "notify me when back in stock" feature likely doesn't
  load. It's a third-party app request, so the suite's page-health checks
  record it but don't fail on it.

## DEF-03: Login labels aren't associated with their fields

- **Observed:** 2026-09-12, re-verified 2026-09-28
- **Steps:** open `/account/login/` and inspect the Email and Contraseña
  labels and inputs.
- **Expected:** each label is associated with its input (`for`/`id` or
  wrapping), so clicking the label focuses the field and assistive technology
  reads the label.
- **Actual:** labels have `for="email"` and `for="password"`, but the inputs
  have no `id`. The inputs are named only by their placeholders
  (`ej.: tuemail@email.com`), which disappear as soon as the user types.
  Automated scans pass because a placeholder counts as a name; the issue
  needs a manual or label-based check.

## DEF-08: Duplicate `id="email"` on the contact page

- **Observed:** 2026-09-27
- **Actual:** the contact form's email input and the footer newsletter input
  both use `id="email"`. The contact label still resolves to the right field,
  so the practical impact is low; it's an HTML validity issue.

---

## Investigated and withdrawn

- **"Home page images without `alt`" (2026-09-27):** the three `<img>`
  elements without `alt` are invisible 0×0 placeholders with no content
  image, not images shoppers see. Not a defect.

## What automated scanning did and didn't find

axe-core found **no** WCAG A/AA violations on the five main pages in their
default state. DEF-04, DEF-05 and DEF-06, the most serious issues, were found
by keyboard checks, and DEF-07 only by scanning with the cart drawer open.
Automated scans are a floor, not a verdict.
