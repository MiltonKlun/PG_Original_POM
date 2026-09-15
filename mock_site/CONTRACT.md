# Local storefront behavior contract

This is a synthetic QA simulation, not a deployed copy of PG Original or client
staging. Page objects reflect observed public markup; the local behaviors below
define the synthetic test environment.
No external assets, analytics, authentication, email or payment services exist.

| Route | Requirement and expected transition | POM/scenario |
|---|---|---|
| `/` | Brand/title, header/footer; SHOP link opens products | Home / HOME |
| Every page | Buscador opens/focuses `#nav-search`; close hides it; form GET `/search/?q=...` | Navbar, SearchModal / SEARCH |
| `/productos/` | Three synthetic cards, uniquely named `.item-link`/`.item-name` | Shop / PDP |
| `/search/` | Case-insensitive name substring; unknown query displays `No encontramos nada para` and no cards | Shop / search results |
| `/productos/?Color=Negro` | Visible color label toggles checked state, results include only products offering Negro; clear removes query and restores all cards | Shop / filter |
| `/productos/qa-remera/` | QA Remera, 29,000.00 ARS, sizes S/M, colors Negro/Blanco; selected variant anchors mirror observed class/title | Product / CART-ADD |
| `/productos/qa-gorra/` | QA Gorra, 15,000.00 ARS, no variants, available | Product / no-variant |
| `/productos/qa-agotado/` | QA Agotado, 12,000.00 ARS; disabled add control and Sin stock text | Product / unavailable |
| Every page | `#modal-cart` initially closed; header opens empty state or stored lines | CartDrawer / cart |
| `/account/login/` | Required email/password; valid-format invalid credentials show `Credenciales incorrectas`; no session created | Login / AUTH-INVALID |
| `/account/reset/` | CAMBIAR CONTRASEÑA heading; email and disabled send button; never sends mail | Login / RESET |
| `/contacto/` | Name/email/message retain values; native email type validation; submit stays disabled, mirroring observed challenged state | Contact / CONTACT-FILL/VALIDATION |
| `/__health` | Exact response `pgoriginal-mock-v1` | Server identity |
| Unknown route | 404, never fallback to home | Server route checks |

## Simulation-only rules

Cart additions persist in localStorage per browser context. Identity is product
ID + selected size/color; repeated identical additions increase quantity.
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

`catalog.json` drives the mock; tests must use independent expected fixture
values, never import this file to derive the assertions being checked.

Both Python and nginx serve the same directory routes and local static assets.
Normal UI execution must fail if it attempts any external HTTP(S) request.
