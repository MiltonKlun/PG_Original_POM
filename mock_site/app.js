"use strict";
// Cart amounts keep two decimals (live cart markup is unverified); listing and
// product prices use the storefront's short form, e.g. $29.000.
const format = (cents, digits) => '$' + new Intl.NumberFormat('es-AR', {minimumFractionDigits: digits, maximumFractionDigits: 2}).format(cents / 100);
const money = cents => format(cents, 2);
const moneyShort = cents => format(cents, cents % 100 ? 2 : 0);
const escapeHTML = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const unique = values => [...new Set(values.filter(Boolean))];
const sizesOf = product => unique(product.variants.map(v => v.size));
const colorsOf = product => unique(product.variants.map(v => v.color));
const cartKey = 'pg-qa-cart';
const cart = () => JSON.parse(localStorage.getItem(cartKey) || '[]');
function saveCart(lines) { localStorage.setItem(cartKey, JSON.stringify(lines)); renderCart(); }
function renderCart() {
  const lines = cart();
  document.querySelector('#modal-cart .alert-info').hidden = lines.length > 0;
  document.querySelector('.js-cart-subtotal').textContent = money(lines.reduce((sum, line) => sum + line.price * line.quantity, 0));
  document.querySelector('.cart-lines').innerHTML = lines.map((line, index) => `<article class="js-cart-item"><strong class="cart-item-name">${escapeHTML(line.name)}</strong><p>${escapeHTML(line.variant)}</p><label>Cantidad<input type="number" min="1" value="${line.quantity}" data-cart-index="${index}"></label><p class="js-cart-item-subtotal">${money(line.price * line.quantity)}</p><button data-remove-index="${index}">Quitar</button></article>`).join('');
  document.querySelectorAll('[data-cart-index]').forEach(input => input.addEventListener('change', () => {
    const value = Number(input.value);
    if (!Number.isInteger(value) || value < 1) { renderCart(); return; }
    const lines = cart(); lines[Number(input.dataset.cartIndex)].quantity = value; saveCart(lines);
  }));
  document.querySelectorAll('[data-remove-index]').forEach(button => button.addEventListener('click', () => saveCart(cart().filter((_, i) => i !== Number(button.dataset.removeIndex)))));
}
// Mirrors the public per-variant card metadata: option0/option1 in variant order.
function variantData(product) {
  return product.variants.map(v => {
    const data = {price_short: moneyShort(v.price), price_number_raw: v.price, compare_at_price_short: v.compare_at ? moneyShort(v.compare_at) : null, compare_at_price_number_raw: v.compare_at, available: product.available};
    [v.size, v.color].filter(Boolean).forEach((value, i) => { data['option' + i] = value; });
    return data;
  });
}
function cardHTML(product) {
  const [first] = product.variants;
  const compare = first.compare_at ? `<span class="price-compare">${moneyShort(first.compare_at)}</span>` : '';
  return `<article class="item-product"><div class="js-product-container" data-variants="${escapeHTML(JSON.stringify(variantData(product)))}"><a class="item-link" href="/productos/${product.slug}/" aria-label="${escapeHTML(product.name)}"><div class="product-art" aria-hidden="true">PG</div><h2 class="item-name">${escapeHTML(product.name)}</h2><p><span class="js-price-display">${moneyShort(first.price)}</span> ${compare}</p></a>${product.available ? '' : '<p>Sin stock</p>'}</div></article>`;
}
function optionsHTML(kind, label, values) {
  if (!values.length) return '';
  return `<div><p>${label}</p>${values.map((v, i) => `<a class="js-insta-variant ${i===0?'selected':''}" title="${v}" data-option="${v}" data-kind="${kind}">${v}</a>`).join('')}</div>`;
}
// JSON-LD as the live store publishes it: an Offer priced in whole units for
// the default (first) variant, keyed to the product page URL.
function structuredData(product) {
  const [first] = product.variants;
  const url = `${location.origin}/productos/${product.slug}/`;
  const data = {'@context': 'https://schema.org/', '@type': 'Product', mainEntityOfPage: {'@type': 'WebPage', '@id': url}, name: product.name, offers: {'@type': 'Offer', url, priceCurrency: 'ARS', price: String(first.price / 100), availability: product.available ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock'}};
  return `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>`;
}
function productHTML(product, related) {
  return `${structuredData(product)}${related ? structuredData(related) : ''}<h1>${escapeHTML(product.name)}</h1><div id="price_display" class="js-price-display price"></div><div id="compare_price_display" class="js-compare-price-display price-compare"></div><form id="product_form">${optionsHTML('size', 'Talle', sizesOf(product))}${optionsHTML('color', 'Color', colorsOf(product))}<label>Cantidad<input name="quantity" type="number" value="1" min="1"></label><input class="js-addtocart" type="submit" value="Agregar al carrito" ${product.available?'':'disabled'}>${product.available?'':'<p>Sin stock</p>'}</form>`;
}
function selectedVariant(product) {
  const chosen = Object.fromEntries([...document.querySelectorAll('.js-insta-variant.selected')].map(el => [el.dataset.kind, el.dataset.option]));
  return product.variants.find(v => (!v.size || v.size === chosen.size) && (!v.color || v.color === chosen.color));
}
function showPrice(product) {
  const variant = selectedVariant(product);
  const price = document.querySelector('#price_display');
  const compare = document.querySelector('#compare_price_display');
  price.textContent = moneyShort(variant.price);
  price.dataset.productPrice = variant.price;
  if (variant.compare_at) compare.textContent = moneyShort(variant.compare_at);
  compare.style.display = variant.compare_at ? 'block' : 'none';
}
function filtersHTML(products, color, size) {
  const labels = (name, values, valuesOf, active) => values.map(value => `<label class="js-filter-checkbox" data-filter-name="${name}" data-filter-value="${value}"><input type="checkbox" ${active===value?'checked':''}> ${value} (${products.filter(p => valuesOf(p).includes(value)).length})</label>`).join('');
  return `<div class="filters">${labels('Color', unique(products.flatMap(colorsOf)), colorsOf, color)}${labels('Talle', unique(products.flatMap(sizesOf)), sizesOf, size)}<a href="/productos/" class="js-remove-all-filters-private">Borrar filtros</a></div>`;
}
// Page-shell controls exist in the static HTML, so wire them before any data
// request: a slow catalog response must not make visible controls inert.
function wireShell() {
  document.querySelectorAll('header [data-toggle]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); const panel = document.querySelector(link.dataset.toggle); panel.hidden = false;
    if (panel.id === 'nav-search') panel.querySelector('input').focus();
  }));
  document.querySelector('#nav-search .js-modal-close').addEventListener('click', e => { e.preventDefault(); document.querySelector('#nav-search').hidden = true; });
  document.querySelectorAll('#nav-hamburger .js-toggle-menu-panel').forEach(toggle => toggle.addEventListener('click', e => { e.preventDefault(); toggle.nextElementSibling.hidden = false; }));
  document.querySelector('#nav-hamburger .js-toggle-menu-close').addEventListener('click', () => { document.querySelector('#nav-hamburger').hidden = true; });
  document.querySelector('#modal-cart .modal-close').addEventListener('click', () => { document.querySelector('#modal-cart').hidden = true; });
  document.querySelector('.cookies').hidden = localStorage.getItem('pg-qa-consent') === 'yes';
  document.querySelector('.js-acknowledge-cookies').addEventListener('click', () => {localStorage.setItem('pg-qa-consent','yes');document.querySelector('.cookies').hidden = true;});
}
async function initialize() {
  wireShell();
  const response = await fetch('/catalog.json');
  if (!response.ok) throw new Error('Cannot load synthetic catalog');
  const {page_size: pageSize, products} = await response.json();
  const main = document.querySelector('main');
  const path = location.pathname.replace(/\/$/, '') || '/';
  const params = new URLSearchParams(location.search);
  if (path === '/') {
    main.innerHTML = '<h1>PG Original / QA lab</h1><p>Deterministic shopping scenarios. Synthetic products, isolated carts, meaningful assertions.</p><div class="grid">' + products.map(cardHTML).join('') + '</div>';
  } else if (path === '/productos' || path === '/search') {
    const query = params.get('q') || '';
    const color = params.get('Color');
    const size = params.get('Talle');
    const filtered = products.filter(p => p.name.toLowerCase().includes(query.toLowerCase()) && (!color || colorsOf(p).includes(color)) && (!size || sizesOf(p).includes(size)));
    let shown = Math.min(filtered.length, pageSize * Math.max(1, Number(params.get('mpage')) || 1));
    main.innerHTML = `<h1>${path==='/search'?'Resultados de búsqueda':'Productos'}</h1>${path==='/productos'?filtersHTML(products, color, size):''}<div class="grid">${filtered.slice(0, shown).map(cardHTML).join('')}</div>${filtered.length?'':`<p>No encontramos nada para "${escapeHTML(query)}"</p>`}<div class="js-load-more"><a class="btn">Mostrar más productos</a></div>`;
    main.querySelectorAll('.js-filter-checkbox input').forEach(input => input.addEventListener('change', () => {
      const label = input.closest('label');
      location.href = input.checked ? `/productos/?${label.dataset.filterName}=${encodeURIComponent(label.dataset.filterValue)}` : '/productos/';
    }));
    // Like the live store: scrolling to the end of the list appends the next
    // page (infinite scroll); the "Mostrar más productos" fallback stays hidden.
    main.querySelector('.js-load-more').style.display = 'none';
    window.addEventListener('scroll', () => {
      const atEnd = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 200;
      if (!atEnd || shown >= filtered.length) return;
      const next = filtered.slice(shown, shown + pageSize);
      main.querySelector('.grid').insertAdjacentHTML('beforeend', next.map(cardHTML).join(''));
      shown += next.length;
      params.set('mpage', String(Math.ceil(shown / pageSize)));
      history.replaceState(null, '', `${location.pathname}?${params}`);
    });
  } else if (path.startsWith('/productos/')) {
    const product = products.find(p => path === '/productos/' + p.slug);
    if (!product) throw new Error('Unknown fixture product');
    // Like the live store, also embed JSON-LD for a related product.
    main.innerHTML = productHTML(product, products.find(p => p !== product));
    // The client form has an animation placeholder sharing the button's class.
    const placeholder = document.createElement('div');
    placeholder.className = 'js-addtocart js-addtocart-placeholder disabled';
    placeholder.hidden = true;
    document.querySelector('#product_form').append(placeholder);
    showPrice(product);
    document.querySelectorAll('.js-insta-variant').forEach(option => option.addEventListener('click', () => {
      document.querySelectorAll(`[data-kind="${option.dataset.kind}"]`).forEach(el=>el.classList.remove('selected'));
      option.classList.add('selected');
      showPrice(product);
    }));
    document.querySelector('#product_form').addEventListener('submit', event => {
      event.preventDefault();
      if (!product.available) return;
      const quantity = Number(event.target.elements.quantity.value);
      if (!Number.isInteger(quantity) || quantity < 1) return;
      const variant = [...document.querySelectorAll('.js-insta-variant.selected')].map(el=>el.dataset.option).join(' / ');
      const unitPrice = selectedVariant(product).price;
      const lines = cart(); const existing = lines.find(line => line.id===product.id && line.variant===variant);
      if (existing) existing.quantity += quantity;
      else lines.push({id:product.id, name:product.name, variant, price:unitPrice, quantity});
      saveCart(lines); document.querySelector('#cart-status').textContent = 'Agregado al carrito';
    });
  } else if (path === '/account/login') {
    main.innerHTML = '<h1>Iniciar sesión</h1><form id="login-form"><label>Email<input name="email" type="email" required></label><label>Contraseña<input name="password" type="password" required></label><button>Iniciar sesión</button><a href="/account/reset">¿Olvidaste tu contraseña?</a><p class="js-login-general-error" hidden></p></form>';
    document.querySelector('#login-form').addEventListener('submit', event => {event.preventDefault(); const error=document.querySelector('.js-login-general-error'); error.textContent='Credenciales incorrectas'; error.hidden=false;});
  } else if (path === '/account/reset') {
    main.innerHTML = '<h1>CAMBIAR CONTRASEÑA</h1><label>Email<input type="email"></label><button disabled>Enviar email</button>';
  } else if (path === '/contacto') {
    main.innerHTML = '<h1>Contacto</h1><form id="contact-form"><label for="name">Nombre</label><input id="name" name="name"><label for="email">Email</label><input id="email" name="email" type="email"><label for="phone">Teléfono</label><input id="phone" type="tel"><label for="message">Mensaje</label><textarea id="message" name="message"></textarea><button name="contact" disabled>Enviar</button></form>';
    document.querySelector('#contact-form').addEventListener('submit', e=>e.preventDefault());
  }
  // Mimic the observed duplicate newsletter email without sending anything.
  const newsletter=document.createElement('input');newsletter.id='email';newsletter.type='email';newsletter.setAttribute('aria-label','Newsletter (disabled simulation)');document.querySelector('footer').append(newsletter);
  renderCart();
  document.documentElement.dataset.ready = 'true';
}
initialize().catch(error => {document.querySelector('main').textContent = 'Simulation failed: ' + error.message; throw error;});
