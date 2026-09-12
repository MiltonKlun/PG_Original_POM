# Observed storefront contract

Observed 2026-09-12 using headless Chromium 120 / Playwright 1.40, desktop
1440×1000. These observations describe public UI, not server-side guarantees.
No cart mutations, credential submissions, contact delivery or reset emails
were performed. Raw local observations are in ignored `logs/phase-0/`; they
may contain session data and must not be published wholesale.

| Surface | Route / observed contract | Locator rationale | Verification / limits |
|---|---|---|---|
| Home | `/`, title `PG Original Ind`, header and footer | Semantic header/footer; brand title | HTTP 200 and rendered UI verified. |
| Search | Header link accessible name `Buscador`; opens `#nav-search`; focuses its single `input[name=q]` | Scope to `#nav-search` because a second hidden search form exists | Open and focus verified. Close control is an unnamed `.js-modal-close` anchor. |
| Search results | GET `/search/?q=<term>` | Results use `.item-product`; empty state contains `No encontramos nada para` | Impossible query `zzqaimpossible987654` returned empty-result state. |
| Shop | `/productos/`, heading `Productos` | `.item-product` scopes each card; `.item-link` has the product's accessible name | HTTP 200, 12 initially rendered cards at observation time; count is not a requirement. Avoid generic first anchor (may be hidden). |
| Filter | Color and size labels wrap hidden checkbox inputs | `.js-filter-checkbox[data-filter-name=Color][data-filter-value=Negro]` exists in duplicated responsive sections | Label/control structure verified. Clicking hidden input timed out; use the visible label in follow-up. Result/reset behavior remains unverified. |
| Product | `/productos/remeras-mw-mustang/`, heading `REMERAS MW MUSTANG` | `#product_form` owns variant/quantity/add controls; `#price_display` is current price | Current price `$29.000`, original `$39.000` at observation; do not fix live expected prices. |
| Variant | Visible anchors with `.js-insta-variant`, `data-option`, `data-variation-id`, selected class; hidden underlying selects | Scope to `#product_form`; options have `title` (including color); size/color order varies by product | Controls observed; live add-to-cart deliberately unverified. Do not click the first variant twice. |
| Cart | Header `a[data-toggle="#modal-cart"]` opens shared `#modal-cart`; empty message `El carrito de compras está vacío.` | Drawer selector is necessary: no dedicated cart page for this interaction | Open/empty state verified. Item insertion, quantity, removal and totals are local-simulation contracts until authorized live evidence exists. |
| Login | `/account/login/`, `#login-form`; email/password required; submit `Iniciar sesión` | Scope to form to exclude newsletter email and other submit buttons | HTTP 200; controls verified. Credential rejection/error copy unverified; local negative auth must be labeled simulated. |
| Reset | Link href `/account/reset`; direct `/account/reset/` renders email/disabled `Enviar email` | Accept optional trailing slash; assert destination content rather than generic URL substring | Direct navigation HTTP 200. Initial link inspection used an over-specific trailing-slash wait and timed out; link destination requires follow-up, not a bot-block diagnosis. |
| Contact | `/contacto/`, `#contact-form`; labels Nombre, Email, Teléfono, Mensaje; email input type email | Scope to form because newsletter duplicates `id=email`; use labels within the form | Fields not marked HTML-required. Synthetic name/email/message filling verified without submit. |
| Contact validation | `button[name=contact]` disabled with empty and filled fields; form has `data-turnstile-bound=1` and challenge control | Expose submit locator for observation only | Never assume filling enables submit. Native malformed-email validity can be inspected without submitting; server validation is unverified. |

## Simulation differences

The local storefront will use synthetic catalog data and browser-context-local
cart storage. Negative login, unavailable stock, cart arithmetic and any
additional contact validation are simulation-only. Shared POM selectors must
follow observed markup; no target-specific branches or invented production
test IDs. The simulation will not include challenge providers, analytics,
newsletter delivery, payments or external assets.

## Follow-up evidence

Recheck reset-link navigation, visible-label filter selection/reset, search
closing, and responsive menu behavior using the pinned browser during later
implementation. Record observed differences here before changing assertions.
