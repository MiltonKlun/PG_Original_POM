# Observed storefront contract

What the page objects rely on, as observed on the public site. These are UI
observations, not server-side guarantees. No cart mutations, credential
submissions, contact messages or reset emails were sent while collecting them.

**Platform:** Tiendanube (confirmed by `robots.txt`).
**First observed:** 2026-09-12, Chromium, desktop 1440×1000.
**Last re-verified:** 2026-09-27, Playwright 1.62 / Chromium.

## Surfaces

| Surface | Observed contract | Locator choice and reason | Limits |
|---|---|---|---|
| Home | `/`, title `PG Original Ind`, header, footer | Semantic `header`/`footer`; footer has a single `SHOP` link (the menu repeats category links) | — |
| Search | Header link named `Buscador` opens `#nav-search`, focusing its `input[name=q]`; close is an unnamed `.js-modal-close` anchor | Scoped to `#nav-search` because a second, hidden search form exists | — |
| Search results | GET `/search/?q=<term>`; cards are `.item-product`; empty state text contains `No encontramos nada para` | — | Result counts change with the catalog; tests never hard-code live counts |
| Shop | `/productos/`, heading `Productos`, 12 cards rendered initially | `.item-product` scopes each card; `a.item-link` is the text link (image and text links share a name) | — |
| Pagination | `.js-load-more` contains an `<a>` without `href`, text `Mostrar más productos`; clicking appends the next 12 cards and the URL becomes `?mpage=2` | Match the text inside `.js-load-more` (no link role without `href`) | 2026-09-27: 12 → 24 cards, 24 unique names |
| Filters | Color and Talle labels wrap hidden checkboxes in duplicated responsive sections; `data-filter-name` / `data-filter-value` (Talle: S, M, L, Xl, Xxl); label text includes result counts, e.g. `S (19)` | Click the **visible** label, matched by `data-filter-value` (text matching would confuse `S` with `XS`, and counts change) | Negro → `/productos/?Color=Negro`, S → `/productos/?Talle=S`; all results offered the value; `Borrar filtros` (`.js-remove-all-filters-private`) restored the list |
| Product | `/productos/<slug>/`; `#product_form` owns variants, quantity and add; `#price_display` is the current price with raw minor units in `data-product-price`; `#compare_price_display` the original, set to `display:none` when the variant has no discount | IDs separate the PDP from hidden quick-shop forms and instalment prices | Prices are never fixed in live tests; the contract check asserts displayed price == `data-product-price` |
| Add control | `#product_form` contains the submit **and** a decorative `div.js-addtocart` placeholder | `input[type="submit"].js-addtocart`; the broad class matched both | Found by a failing live smoke run, see the [case study](case-study.md) |
| Variants | Visible anchors `.js-insta-variant` with `title`, `data-option`, and a `selected` class; hidden selects underneath | `get_by_title` scoped to the form | Option order (size/color) varies by product; card metadata is read by key, not position |
| Variant pricing | Price depends on the variant. Example 2026-09-27: `REMERAS MW MUSTANG` Negro `$29.000` with compare-at `$39.000`; Blanco `$39.000` with no compare-at | — | Modeled in the simulation and tested there; a live read-only check is planned |
| Cart drawer | Header `a[data-toggle="#modal-cart"]` opens `#modal-cart`; empty text `El carrito de compras está vacío.`; `.js-cart-subtotal` present; closed by an icon-only `a.js-modal-close.modal-close` in the drawer header | Drawer is shared by all pages; close is located by class because it has no accessible name | Open and close verified 2026-09-27. Line items, quantity, removal and totals are unverified on live by design |
| Menu | `a[data-toggle="#nav-hamburger"]` opens `#nav-hamburger`; `SHOP` is an `a.js-toggle-menu-panel` with `href="#"` (a hidden duplicate exists) that opens a `.js-menu-panel` containing `Ver todos los productos` → `/productos/` | Role + name: only the visible SHOP toggle matches | Menu → SHOP → Ver todos → product verified 2026-09-27 |
| Login | `/account/login/`, `#login-form`; email and password `required`; submit `Iniciar sesión` | Scoped by `input[name=…]`: labels have `for="email"`/`for="password"` but the inputs have no `id`, so labels aren't associated | Rejection copy unverified; the mock's error message is synthetic |
| Reset | Link `/account/reset` (no trailing slash); heading `CAMBIAR CONTRASEÑA`; send button disabled | Accept an optional trailing slash; assert the destination heading | No reset request is ever sent |
| Contact | `/contacto/`, `#contact-form`; labels Nombre, Email, Teléfono, Mensaje; `type=email`; none marked `required`; submit `button[name=contact]` disabled while Turnstile is unresolved; hidden honeypot field | Scoped to the form because the newsletter reuses `id="email"` | Filling fields doesn't enable submit; server validation unverified |

## Simulation differences

The local storefront (`mock_site/`) reproduces the markup above where it's
known, including the icon-only cart close, the SHOP menu panel, Color/Talle
filters with counts, load-more pagination and per-variant prices, and simulates behavior that can't be exercised on production:
catalog data, browser-local cart storage, cart arithmetic, login rejection,
unavailable stock and the disabled contact state. It includes no challenge
provider, analytics, newsletter, payments or external assets. See
[`mock_site/CONTRACT.md`](../mock_site/CONTRACT.md) for the simulated rules.

## Accessibility and HTML observations (2026-09-27)

Observed while re-verifying the contract. These are defects in the public
site, not in the automation:

1. Login labels point to `id`s that don't exist, so screen readers don't
   announce field names (WCAG 1.3.1 / 4.1.2).
2. Icon-only close controls in the cart drawer and menu have no accessible
   name (WCAG 4.1.2).
3. The hamburger menu doesn't close on Escape; while open, it intercepts
   clicks on the header.
4. Three images on the home page have no `alt` attribute (WCAG 1.1.1).
5. `/contacto/` has two elements with `id="email"` (contact form and
   newsletter).

## Third-party traffic

A home page load contacts about 15 third-party hosts, including the Facebook
pixel, Cloudflare Insights and recommendation widgets. Live runs are kept
serial, weekly and read-only to limit their footprint on the store's
analytics.

## Locator contract checks

`tests/test_contract.py` resolves the page objects' own locators on both
targets without changing state: header and footer, cart drawer open/close,
menu SHOP panel, listing cards, filters, load-more control, card variant
metadata, product form and price attribute, login and contact fields. They
run in every mock CI run and in the weekly live workflow, so markup drift is
reported as a precise locator failure.
