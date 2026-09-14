"use strict";
const money = cents => '$' + new Intl.NumberFormat('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(cents / 100);
const escapeHTML = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
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
function cardHTML(product) {
  const variants = product.colors.map(color => ({option1: color}));
  return `<article class="item-product"><div data-variants="${escapeHTML(JSON.stringify(variants))}"><a class="item-link" href="/productos/${product.slug}/" aria-label="${escapeHTML(product.name)}"><div class="product-art" aria-hidden="true">PG</div><h2 class="item-name">${escapeHTML(product.name)}</h2><p>${money(product.price)}</p></a>${product.available ? '' : '<p>Sin stock</p>'}</div></article>`;
}
function productHTML(product) {
  return `<h1>${escapeHTML(product.name)}</h1><div id="price_display" class="price">${money(product.price)}</div><form id="product_form"><div>${product.sizes.length ? '<p>Talle</p>' : ''}${product.sizes.map((v,i) => `<a class="js-insta-variant ${i===0?'selected':''}" title="${v}" data-option="${v}" data-kind="size">${v}</a>`).join('')}</div><div>${product.colors.length ? '<p>Color</p>' : ''}${product.colors.map((v,i) => `<a class="js-insta-variant ${i===0?'selected':''}" title="${v}" data-option="${v}" data-kind="color">${v}</a>`).join('')}</div><label>Cantidad<input name="quantity" type="number" value="1" min="1"></label><input class="js-addtocart" type="submit" value="Agregar al carrito" ${product.available?'':'disabled'}>${product.available?'':'<p>Sin stock</p>'}</form>`;
}
async function initialize() {
  const response = await fetch('/catalog.json');
  if (!response.ok) throw new Error('Cannot load synthetic catalog');
  const products = await response.json();
  const main = document.querySelector('main');
  const path = location.pathname.replace(/\/$/, '') || '/';
  const params = new URLSearchParams(location.search);
  document.querySelectorAll('header [data-toggle]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); const panel = document.querySelector(link.dataset.toggle); panel.hidden = false;
    if (panel.id === 'nav-search') panel.querySelector('input').focus();
  }));
  document.querySelector('#nav-search .js-modal-close').addEventListener('click', e => { e.preventDefault(); document.querySelector('#nav-search').hidden = true; });
  document.querySelector('.cart-close').addEventListener('click', () => {document.querySelector('#modal-cart').hidden = true;});
  document.querySelector('.cookies').hidden = localStorage.getItem('pg-qa-consent') === 'yes';
  document.querySelector('.js-acknowledge-cookies').addEventListener('click', () => {localStorage.setItem('pg-qa-consent','yes');document.querySelector('.cookies').hidden = true;});
  if (path === '/') {
    main.innerHTML = '<h1>PG Original / QA lab</h1><p>Deterministic shopping scenarios. Synthetic products, isolated carts, meaningful assertions.</p><div class="grid">' + products.map(cardHTML).join('') + '</div>';
  } else if (path === '/productos' || path === '/search') {
    const query = params.get('q') || '';
    const color = params.get('Color');
    const filtered = products.filter(p => p.name.toLowerCase().includes(query.toLowerCase()) && (!color || p.colors.includes(color)));
    main.innerHTML = `<h1>${path==='/search'?'Resultados de búsqueda':'Productos'}</h1>${path==='/productos'?`<label class="js-filter-checkbox" data-filter-name="Color" data-filter-value="Negro"><input type="checkbox" ${color==='Negro'?'checked':''}>Negro</label><a href="/productos/" class="js-remove-all-filters-private">Borrar filtros</a>`:''}<div class="grid">${filtered.map(cardHTML).join('')}</div>${filtered.length?'':`<p>No encontramos nada para "${escapeHTML(query)}"</p>`}`;
    const filter = main.querySelector('.js-filter-checkbox input');
    if (filter) filter.addEventListener('change', () => {location.href = filter.checked ? '/productos/?Color=Negro' : '/productos/';});
  } else if (path.startsWith('/productos/')) {
    const product = products.find(p => path === '/productos/' + p.slug);
    if (!product) throw new Error('Unknown fixture product');
    main.innerHTML = productHTML(product);
    document.querySelectorAll('.js-insta-variant').forEach(option => option.addEventListener('click', () => {
      document.querySelectorAll(`[data-kind="${option.dataset.kind}"]`).forEach(el=>el.classList.remove('selected'));
      option.classList.add('selected');
    }));
    document.querySelector('#product_form').addEventListener('submit', event => {
      event.preventDefault();
      if (!product.available) return;
      const quantity = Number(event.target.elements.quantity.value);
      if (!Number.isInteger(quantity) || quantity < 1) return;
      const variant = [...document.querySelectorAll('.js-insta-variant.selected')].map(el=>el.dataset.option).join(' / ');
      const lines = cart(); const existing = lines.find(line => line.id===product.id && line.variant===variant);
      if (existing) existing.quantity += quantity;
      else lines.push({id:product.id, name:product.name, variant, price:product.price, quantity});
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
