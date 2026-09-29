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
| Pagination | Infinite scroll: scrolling to the last card appends the next 12 cards and updates the URL to `?mpage=N`. The `.js-load-more` "Mostrar más productos" control starts as `display:none` and appeared only after several automatic loads (60 cards, `?mpage=5`) | `load_more()` scrolls to the end of the list; the button is not required | 2026-09-28: 12 → 24 on one scroll, names unique |
| Listing prices | A card shows its **first variant's** price; it shows "Sin stock" exactly when no variant is available | Read from each card's `data-variants` | Verified on 30 cards over two pages, 2026-09-28 |
| Structured data | Product pages embed JSON-LD `Organization`, `WebPage` and `Product` blocks for **related** products; offers are priced in whole units (`"price": "27000"`) | Match the `Product` whose `mainEntityOfPage.@id` is the page URL | No block describes the viewed product: DEF-01 below |
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

## Store defects observed

Observed while re-verifying the contract. These are defects in the public
site, not in the automation.

**DEF-01 (2026-09-28): product pages lack their own structured data.** On
every product page checked, JSON-LD describes only related products, so
search engines get no price or availability for the product being viewed.
The shared check `test_product_page_publishes_its_price_as_structured_data`
is a strict expected failure on live and passes on the simulation.

**DEF-02 (2026-09-28): a store app's configuration request fails.** Every
page load gets HTTP 403 for the restock-alert app's settings file
(`empreender-sa-east-1.s3…/Cheguei/public/settings/nuvem_shop-693159.json`),
so the "notify me when back in stock" feature likely doesn't load. It's a
third-party request, so page-health checks don't fail on it.

### Accessibility and HTML (2026-09-27)

1. Login labels point to `id`s that don't exist, so screen readers don't
   announce field names (WCAG 1.3.1 / 4.1.2).
2. Icon-only close controls in the cart drawer and menu have no accessible
   name (WCAG 4.1.2).
3. The hamburger menu doesn't close on Escape; while open, it intercepts
   clicks on the header.
4. Three images on the home page have no `alt` attribute (WCAG 1.1.1).
5. `/contacto/` has two elements with `id="email"` (contact form and
   newsletter).

## Third-party traffic and the live traffic policy

Observed 2026-09-28 over home, listing and one product page:

| Request | Purpose | Live runs |
|---|---|---|
| `connect.facebook.net`, `*.pinterest.com` | Ad pixels | Blocked |
| `static.cloudflareinsights.com`, `unpkg.com/web-vitals` | Web analytics, real-user monitoring | Blocked |
| `api.crossup.ai`, `carousel.crossup.ai`, `recomendaciones-sdk.crossup-templates.pages.dev` | Recommendation widget (42 requests per 3 pages) | Blocked |
| `apps-telemetry-collector-v2.tiendanube.com` | App telemetry | Blocked |
| `www.pgoriginal.com/stats/record_visit/` | The store's own visit counter | Blocked |
| `acdn-us.mitiendanube.com`, `nsk-cdn-static.tiendanube.com`, fonts, reCAPTCHA, AFIP badge, restock-alert app | Needed to render and behave normally | Allowed |

Rules live in [`config/live_policy.py`](../config/live_policy.py) with unit
tests. A full live run aborts about 240 tracking requests and receives no
tracker responses. Live requests also carry a `PGOriginalQA/1.0` user-agent
suffix, so the store can identify and filter this traffic.
