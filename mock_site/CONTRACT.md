# Local storefront behavior contract

This is a synthetic QA simulation, not a deployed copy of PG Original or client
staging. Page objects reflect observed public markup; the local behaviors below
define the synthetic test environment.
No external assets, analytics, authentication, email or payment services exist.

| Route | Requirement and expected transition | POM/scenario |
|---|---|---|
| `/` | Brand/title, header/footer; SHOP link opens products | Home / HOME |
| Every page | Buscador opens/focuses `#nav-search`; close hides it; form GET `/search/?q=...` | Navbar, SearchModal / SEARCH |
| `/productos/` | Five synthetic products, four per page; uniquely named `.item-link`/`.item-name`; card `data-variants` carries per-variant `optionN`, `price_number_raw` and compare-at values | Shop / PDP |
| Pagination | Scrolling to the end of the list appends the next page without repeats and updates `?mpage=N` (infinite scroll, as live); the `.js-load-more` fallback stays hidden | Shop / pagination |
| Product pages | JSON-LD `Product` for the viewed product (offer price of the default variant in whole units, keyed by page URL) plus one related product, as the live store embeds related products | Product / structured data |
| `/search/` | Case-insensitive name substring; unknown query displays `No encontramos nada para` and no cards | Shop / search results |
| `/productos/?Color=…`, `?Talle=…` | Visible Color and Talle labels (`data-filter-name`/`data-filter-value`, text with result count) toggle checked state; results include only products offering that value; `Borrar filtros` restores the first page | Shop / filter |
| `/productos/qa-remera/` | QA Remera, sizes S/M, colors Negro/Blanco. Negro 29,000 ARS with compare-at 39,000; Blanco 39,000 without compare-at. `#price_display` (`data-product-price`) and `#compare_price_display` follow the selected variant | Product / CART-ADD / pricing |
| `/productos/qa-gorra/` | QA Gorra, 15,000.00 ARS, no variants, available | Product / no-variant |
| `/productos/qa-agotado/` | QA Agotado, 12,000 ARS; disabled add control and Sin stock text | Product / unavailable |
| `/productos/pg-buzo/`, `/productos/pg-gorro/` | PG Buzo (sizes M/L, Gris, 45,000) and PG Gorro (Gris only, 18,000); second page of the listing | Pagination / filters |
| Every page | `#modal-cart` initially closed; header opens empty state or stored lines; closes through an icon-only `a.js-modal-close.modal-close`, as on the live store | CartDrawer / cart |
| Every page | Header menu opens `#nav-hamburger`; `SHOP` is a `.js-toggle-menu-panel` toggle (`href="#"`, plus a hidden duplicate) opening a panel with `Ver todos los productos` | Navbar / MENU |
| `/account/login/` | Required email/password; valid-format invalid credentials show `Credenciales incorrectas`; no session created | Login / AUTH-INVALID |
| `/account/reset/` | CAMBIAR CONTRASEÑA heading; email and disabled send button; never sends mail | Login / RESET |
| `/contacto/` | Name/email/message retain values; native email type validation; submit stays disabled, mirroring observed challenged state | Contact / CONTACT-FILL/VALIDATION |
| `/__health` | Exact response `pgoriginal-mock-v1` | Server identity |
| Unknown route | 404, never fallback to home | Server route checks |

## Simulation-only rules

Header, menu, search, cart-close and cookie controls work before the catalog
request completes; only product content waits for data.

The simulation is the accessible reference: opening the search panel,
menu or cart drawer moves focus into it; Escape or its close control closes
it and returns focus to the trigger; close controls are named buttons; text
meets WCAG AA contrast. The live store lacks these (DEF-04 to DEF-07), so
the shared checks are expected failures there. Class hooks used by the
page objects are identical on both targets.

Cart additions persist in localStorage per browser context. Identity is product
ID + selected size/color; repeated identical additions increase quantity. A
line's unit price is the selected variant's price.
Quantity changes update line amount and subtotal in integer minor units;
removing the sole line restores empty state and zero subtotal. No discounts,
stock reservations, shipping, checkout, tax or currency conversion is modeled.
`.js-cart-item`, its spinbutton, `.js-cart-item-subtotal`, `Quitar`, and
`.js-cart-subtotal` define the local line contract; live mutation markup remains
unverified. A live cart passing these tests is not claimed.

Native malformed-email validation is shared HTML behavior. Empty contact
fields are not modeled as HTML-required because the observed site does not
mark them required. Contact enablement/server error behavior is not invented.
Login error copy is synthetic and carries no production assertion.

Listing and product prices use the short storefront format (`$29.000`); cart
amounts keep two decimals (`$29.000,00`).

`catalog.json` drives the mock; tests must use independent expected fixture
values, never import this file to derive the assertions being checked.

Both Python and nginx serve the same directory routes and local static assets.
Normal UI execution must fail if it attempts any external HTTP(S) request.
