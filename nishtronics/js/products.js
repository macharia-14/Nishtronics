/* ═══════════════════════════════════════
   NISHTRONICS — PRODUCTS PAGE
   ═══════════════════════════════════════ */
let allProducts = [];
let activeCat = 'all', activeBrand = 'all', searchQ = '', sortMode = '';

document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('productGrid').innerHTML = renderSkeletons(8);
  await initFirebase();
  let products = await fsGetProducts();
  if (!products) { const r = await fetch('data/products.json'); products = await r.json(); }
  allProducts = products;
  window.PRODUCTS = products;
  buildBrandChips();
  bindFilters();
  applyFilters();
});

function buildBrandChips() {
  const brands = ['all', ...new Set(allProducts.map(p => p.brand))];
  const c = document.getElementById('brandChips');
  if (!c) return;
  c.innerHTML = brands.map(b =>
    `<button class="chip ${b==='all'?'active':''}" data-brand="${b}">${b==='all'?'All Brands':b}</button>`).join('');
  c.querySelectorAll('[data-brand]').forEach(btn => btn.addEventListener('click', () => {
    c.querySelectorAll('[data-brand]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); activeBrand = btn.dataset.brand; applyFilters();
  }));
}

function bindFilters() {
  document.querySelectorAll('#catChips [data-cat]').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('#catChips [data-cat]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); activeCat = btn.dataset.cat; applyFilters();
  }));
  let debounce;
  document.getElementById('searchInput')?.addEventListener('input', e => {
    clearTimeout(debounce); debounce = setTimeout(() => { searchQ = e.target.value.toLowerCase().trim(); applyFilters(); }, 200);
  });
  document.getElementById('sortSelect')?.addEventListener('change', e => { sortMode = e.target.value; applyFilters(); });
}

function applyFilters() {
  let f = allProducts.filter(p => {
    const mC = activeCat === 'all' || p.category === activeCat;
    const mB = activeBrand === 'all' || p.brand === activeBrand;
    const mS = !searchQ || p.name.toLowerCase().includes(searchQ) || p.brand.toLowerCase().includes(searchQ) || p.category.toLowerCase().includes(searchQ) || (p.description||'').toLowerCase().includes(searchQ);
    return mC && mB && mS;
  });
  if (sortMode === 'price-asc') f.sort((a, b) => a.price - b.price);
  else if (sortMode === 'price-desc') f.sort((a, b) => b.price - a.price);
  else if (sortMode === 'name') f.sort((a, b) => a.name.localeCompare(b.name));
  renderGrid(f);
}

function renderGrid(products) {
  const grid = document.getElementById('productGrid');
  const info = document.getElementById('resultsInfo');
  if (!grid) return;
  if (info) info.innerHTML = `Showing <strong>${products.length}</strong> of <strong>${allProducts.length}</strong> products`;
  if (!products.length) {
    grid.innerHTML = `<div class="no-res"><div class="ico">🔍</div><h3 style="margin-bottom:.5rem;">No products found</h3><p>Try adjusting your search or filters.</p></div>`;
    return;
  }
  grid.innerHTML = products.map(p => renderProductCard(p)).join('');
  initScrollReveal();
}
