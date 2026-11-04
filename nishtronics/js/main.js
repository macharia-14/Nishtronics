/* ═══════════════════════════════════════════
   NISHTRONICS SOUNDLABS — MAIN JS
   ═══════════════════════════════════════════ */

/* ─── NAV ─── */
const nav = document.getElementById('nav') || document.querySelector('.nav');
const menuBtn = document.getElementById('menuBtn');
const mobileMenu = document.getElementById('mobileMenu');
let lastScrollY = 0;

window.addEventListener('scroll', () => {
  const y = window.pageYOffset;
  if (nav) {
    nav.classList.toggle('hidden', y > lastScrollY && y > 100);
    nav.classList.toggle('scrolled', y > 20);
  }
  lastScrollY = y;
  document.getElementById('scrollTop')?.classList.toggle('show', y > 400);
}, { passive: true });

menuBtn?.addEventListener('click', () => {
  menuBtn.classList.toggle('open');
  mobileMenu?.classList.toggle('open');
  document.body.style.overflow = mobileMenu?.classList.contains('open') ? 'hidden' : '';
});
mobileMenu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  menuBtn?.classList.remove('open');
  mobileMenu.classList.remove('open');
  document.body.style.overflow = '';
}));

document.getElementById('scrollTop')?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// Active nav link
const curPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(a => {
  a.classList.toggle('active', (a.getAttribute('href') || '').split('/').pop() === curPage);
});

/* ─── CART ─── */
const CART_KEY = 'nish_cart_v2';
function getCart() { try { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); } catch { return []; } }
function saveCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); updateCartUI(); renderCartPanel(); }
function cartCount() { return getCart().reduce((s, i) => s + i.qty, 0); }
function cartTotal() { return getCart().reduce((s, i) => s + i.price * i.qty, 0); }
function formatKsh(n) { return 'KSh ' + Math.round(n).toLocaleString('en-KE'); }

function updateCartUI() {
  const n = cartCount();
  document.querySelectorAll('.cart-pip').forEach(el => {
    el.textContent = n;
    el.classList.toggle('zero', n === 0);
  });
}

function addToCart(p) {
  const cart = getCart();
  const ex = cart.find(i => i.id === p.id);
  if (ex) ex.qty++;
  else cart.push({ id: p.id, name: p.name, brand: p.brand, price: p.price, image: productImg(p), qty: 1 });
  saveCart(cart);
  toast(`${p.name.slice(0, 30)}… added ✓`, 'success');
  openCart();
  document.querySelectorAll('.cart-pip').forEach(el => { el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); });
}
function removeFromCart(id) { saveCart(getCart().filter(i => i.id !== id)); }
function changeQty(id, d) { const c = getCart(); const it = c.find(i => i.id === id); if (it) { it.qty = Math.max(1, it.qty + d); saveCart(c); } }
function addToCartById(id) { const p = (window.PRODUCTS || []).find(p => p.id === id); if (p?.inStock !== false) addToCart(p); }
function cartRemoveItem(id) { removeFromCart(id); }
function cartChangeQty(id, d) { changeQty(id, d); }

/* ─── CART PANEL ─── */
function openCart() {
  let panel = document.getElementById('cartPanel');
  if (!panel) { injectCartPanel(); panel = document.getElementById('cartPanel'); }
  panel?.classList.add('open');
  document.getElementById('cartVeil')?.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeCart() {
  document.getElementById('cartPanel')?.classList.remove('open');
  document.getElementById('cartVeil')?.classList.remove('open');
  document.body.style.overflow = '';
}

function injectCartPanel() {
  if (document.getElementById('cartPanel')) return;
  document.body.insertAdjacentHTML('beforeend', `
  <div class="cart-veil" id="cartVeil"></div>
  <div class="cart-panel" id="cartPanel">
    <div class="cart-panel-head">
      <div>
        <h3>Your Cart</h3>
        <div style="font-size:.68rem;color:var(--t3);font-family:var(--fm);margin-top:.1rem;" id="cartSubtitle"></div>
      </div>
      <button class="icon-btn" id="cartClose" aria-label="Close cart">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="cart-items" id="cartPanelItems"></div>
    <div class="cart-panel-foot" id="cartFoot" style="display:none;">
      <div class="cart-tot-row">
        <span class="ctl-lbl">Total</span>
        <span class="ctl-val" id="cartTotalDisp">KSh 0</span>
      </div>
      <a href="cart.html" class="btn btn-gold btn-full btn-lg" onclick="closeCart()">Checkout via WhatsApp →</a>
      <p class="cart-note">Pre-fills your full order on WhatsApp. We confirm and quote.</p>
    </div>
  </div>`);
  document.getElementById('cartVeil')?.addEventListener('click', closeCart);
  document.getElementById('cartClose')?.addEventListener('click', closeCart);
  renderCartPanel();
}

function renderCartPanel() {
  const itemsEl = document.getElementById('cartPanelItems');
  const footEl = document.getElementById('cartFoot');
  const subtitleEl = document.getElementById('cartSubtitle');
  if (!itemsEl) return;
  const cart = getCart();
  updateCartUI();
  const n = cartCount();
  if (subtitleEl) subtitleEl.textContent = n ? `${n} item${n !== 1 ? 's' : ''}` : '';
  if (!cart.length) {
    itemsEl.innerHTML = `<div class="cart-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      <p style="margin-top:.75rem;font-size:.88rem;">Your cart is empty</p>
      <a href="products.html" class="btn btn-outline btn-sm" style="margin-top:1rem;" onclick="closeCart()">Browse Products</a>
    </div>`;
    if (footEl) footEl.style.display = 'none';
    return;
  }
  itemsEl.innerHTML = cart.map(item => `
    <div class="ci">
      <div class="ci-thumb"><img src="${item.image||'images/placeholder.svg'}" alt="${item.name}" onerror="this.onerror=null;this.src='images/placeholder.svg'"/></div>
      <div class="ci-info">
        <div class="ci-brand">${item.brand}</div>
        <div class="ci-name">${item.name}</div>
        <div class="ci-price">${formatKsh(item.price * item.qty)}</div>
        <div class="ci-controls">
          <button class="qty-btn" onclick="cartChangeQty('${item.id}',-1);renderCartPanel()">−</button>
          <span class="qty-n">${item.qty}</span>
          <button class="qty-btn" onclick="cartChangeQty('${item.id}',1);renderCartPanel()">+</button>
          <button class="icon-btn del" onclick="cartRemoveItem('${item.id}');renderCartPanel()" style="width:24px;height:24px;margin-left:auto;" title="Remove">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>
    </div>`).join('');
  if (footEl) {
    footEl.style.display = 'block';
    const tv = document.getElementById('cartTotalDisp');
    if (tv) tv.textContent = formatKsh(cartTotal());
  }
}

// Open cart on nav button click
document.addEventListener('click', e => {
  if (e.target.closest('#openCart, [data-open-cart]')) { e.preventDefault(); openCart(); }
});

const THEME_KEY = 'nishtronics_theme';
function applyTheme(theme) {
  const isLight = theme === 'light';
  document.body.classList.toggle('theme-light', isLight);
  const toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.textContent = isLight ? '🌙' : '☀️';
    toggle.setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
  }
  localStorage.setItem(THEME_KEY, theme);
}

// Initialise cart + theme on load
document.addEventListener('DOMContentLoaded', () => {
  updateCartUI();
  if (!document.getElementById('cartPanel')) injectCartPanel();
  initScrollReveal();
  initLightbox();
  document.getElementById('yr') && (document.getElementById('yr').textContent = new Date().getFullYear());
  document.querySelectorAll('.footer-year, [data-year]').forEach(el => el.textContent = new Date().getFullYear());

  const storedTheme = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(storedTheme);
  document.getElementById('themeToggle')?.addEventListener('click', () => {
    const active = document.body.classList.contains('theme-light') ? 'dark' : 'light';
    applyTheme(active);
  });
});

/* ─── HELPERS ─── */
const BADGE_MAP = {
  'bestseller': 'b-gold',
  'new': 'b-green',
  'popular': 'b-blue',
  'high-end': 'b-purple',
  '2nd-hand': 'b-orange',
  'custom': 'b-teal'
};

// Photo convention: drop images/products/<product-id>.webp and it is picked up automatically.
// An explicit p.image (path or URL) wins. Missing files fall back to the placeholder.
function productImg(p) { return p.image || ('images/products/' + p.id + '.webp'); }

function renderProductCard(p) {
  const badge = p.badge ? `<span class="badge ${BADGE_MAP[p.badge]||''}">${p.badge}</span>` : '';
  const oosBadge = !p.inStock ? `<span class="badge b-oos" style="left:auto;right:.65rem;">Out of Stock</span>` : '';
  const specs = p.specs ? Object.entries(p.specs).slice(0,3).map(([,v]) => `<span class="spec-pill">${v}</span>`).join('') : '';
  const waMsg = encodeURIComponent(`Hi, I'm interested in the ${p.name} (${formatKsh(p.price)}) 🎵`);
  const addBtn = p.inStock !== false
    ? `<button class="btn btn-gold btn-sm btn-full" onclick="addToCartById('${p.id}')">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
        Add to Cart</button>`
    : `<button class="btn btn-ghost btn-sm btn-full" disabled>Out of Stock</button>`;
  const waBtn = `<a href="https://wa.me/254700000000?text=${waMsg}" class="btn btn-wa btn-sm btn-full" target="_blank" rel="noopener">
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
    Ask on WhatsApp</a>`;
  return `
  <div class="p-card ${!p.inStock ? 'oos' : ''} reveal" data-id="${p.id}">
    <div class="p-card-img">
      <img src="${productImg(p)}" alt="${p.name}" loading="lazy" onerror="this.onerror=null;this.src='images/placeholder.svg'">
      ${badge}${oosBadge}
      <div class="p-card-overlay">${addBtn}${waBtn}</div>
    </div>
    <div class="p-card-body">
      <div class="pc-brand">${p.brand}</div>
      <div class="pc-name">${p.name}</div>
      <p class="pc-desc">${p.description}</p>
      ${specs ? `<div class="spec-pills">${specs}</div>` : ''}
      <div class="pc-price">${formatKsh(p.price)}</div>
      ${addBtn}
    </div>
  </div>`;
}

function renderSkeletons(n = 8) {
  return Array(n).fill(0).map(() => `
    <div class="skel-card">
      <div class="skeleton skel-img"></div>
      <div class="skel-body">
        <div class="skeleton skel-line skel-s"></div>
        <div class="skeleton skel-line skel-m" style="margin-top:.4rem"></div>
        <div class="skeleton skel-line skel-l" style="margin-top:.4rem"></div>
        <div class="skeleton skel-line skel-s" style="margin-top:.75rem"></div>
      </div>
    </div>`).join('');
}

/* ─── TOAST ─── */
function getStack() {
  let s = document.getElementById('toastStack');
  if (!s) { s = document.createElement('div'); s.id = 'toastStack'; s.className = 'toast-stack'; document.body.appendChild(s); }
  return s;
}
function toast(msg, type = 'info') {
  const icons = { success: '✓', warning: '⚠', info: '♪' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-ico">${icons[type]||'ℹ'}</span><span class="toast-msg">${msg}</span>`;
  getStack().appendChild(el);
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('show')));
  setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 400); }, 3000);
}

/* ─── SCROLL REVEAL ─── */
function initScrollReveal() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        e.target.style.transitionDelay = `${(i % 4) * 55}ms`;
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
}
function revealNew() { initScrollReveal(); }

/* ─── LIGHTBOX ─── */
function initLightbox() {
  const lb = document.getElementById('lightbox');
  if (!lb) return;
  const img = document.getElementById('lbImg');
  let imgs = [], cur = 0;
  document.querySelectorAll('[data-lb]').forEach((el, i) => {
    imgs.push(el.dataset.lb || el.querySelector('img')?.src);
    el.addEventListener('click', () => { cur = i; openLb(imgs[i]); });
  });
  function openLb(src) { img.src = src; lb.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeLb() { lb.classList.remove('open'); document.body.style.overflow = ''; }
  document.getElementById('lbClose')?.addEventListener('click', closeLb);
  lb.addEventListener('click', e => { if (e.target === lb) closeLb(); });
  document.getElementById('lbPrev')?.addEventListener('click', () => { cur = (cur - 1 + imgs.length) % imgs.length; openLb(imgs[cur]); });
  document.getElementById('lbNext')?.addEventListener('click', () => { cur = (cur + 1) % imgs.length; openLb(imgs[cur]); });
  document.addEventListener('keydown', e => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') closeLb();
    if (e.key === 'ArrowLeft') { cur = (cur - 1 + imgs.length) % imgs.length; openLb(imgs[cur]); }
    if (e.key === 'ArrowRight') { cur = (cur + 1) % imgs.length; openLb(imgs[cur]); }
  });
}
