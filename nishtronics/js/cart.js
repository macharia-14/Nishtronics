/* ═══════════════════════════════════════
   NISHTRONICS — CART PAGE
   ═══════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', renderCartPage);

function renderCartPage() {
  const cart = getCart();
  const emptyEl = document.getElementById('cartEmpty');
  const contentEl = document.getElementById('cartContent');
  const itemsEl = document.getElementById('coItems');
  if (!cart.length) {
    emptyEl && (emptyEl.style.display = 'block');
    contentEl && (contentEl.style.display = 'none');
    return;
  }
  emptyEl && (emptyEl.style.display = 'none');
  contentEl && (contentEl.style.display = 'block');
  if (itemsEl) {
    itemsEl.innerHTML = cart.map(item => `
      <div class="co-row">
        <div class="co-thumb"><img src="${item.image||'images/placeholder.svg'}" alt="${item.name}" onerror="this.onerror=null;this.src='images/placeholder.svg'"></div>
        <div class="co-info">
          <div class="co-brand">${item.brand}</div>
          <div class="co-name">${item.name}</div>
          <div class="co-unit">${formatKsh(item.price)} each</div>
          <div class="ci-controls" style="margin-top:.5rem;">
            <button class="qty-btn" onclick="cpQty('${item.id}',-1)">−</button>
            <span class="qty-n" id="qty-${item.id}">${item.qty}</span>
            <button class="qty-btn" onclick="cpQty('${item.id}',1)">+</button>
            <button class="btn btn-ghost btn-sm" onclick="cpRemove('${item.id}')" style="margin-left:auto;padding:.2rem .5rem;font-size:.68rem;">Remove</button>
          </div>
        </div>
        <div class="co-sub" id="sub-${item.id}">${formatKsh(item.price * item.qty)}</div>
      </div>`).join('');
  }
  updateSummary();
}

function updateSummary() {
  const total = cartTotal();
  const count = cartCount();
  const el = id => document.getElementById(id);
  if (el('sumItems')) el('sumItems').textContent = `${count} item${count !== 1 ? 's' : ''}`;
  if (el('sumTotal')) el('sumTotal').textContent = formatKsh(total);
  if (el('sumFinal')) el('sumFinal').textContent = formatKsh(total);
}

function cpQty(id, d) {
  changeQty(id, d);
  const cart = getCart();
  const item = cart.find(i => i.id === id);
  if (!item) return renderCartPage();
  const qEl = document.getElementById(`qty-${id}`);
  const sEl = document.getElementById(`sub-${id}`);
  if (qEl) qEl.textContent = item.qty;
  if (sEl) sEl.textContent = formatKsh(item.price * item.qty);
  updateSummary();
}

function cpRemove(id) { removeFromCart(id); renderCartPage(); toast('Item removed', 'info'); }
function cpClear() { if (!confirm('Clear your cart?')) return; saveCart([]); renderCartPage(); }

async function sendWhatsAppOrder() {
  const cart = getCart();
  if (!cart.length) { toast('Your cart is empty', 'warning'); return; }
  const name  = document.getElementById('oName')?.value.trim();
  const phone = document.getElementById('oPhone')?.value.trim();
  const del   = document.getElementById('oDelivery')?.value || 'Pickup';
  const loc   = document.getElementById('oLocation')?.value.trim() || '';
  const notes = document.getElementById('oNotes')?.value.trim() || '';
  if (!name)  { toast('Please enter your name', 'warning'); document.getElementById('oName')?.focus(); return; }
  if (!phone) { toast('Please enter your phone number', 'warning'); document.getElementById('oPhone')?.focus(); return; }
  const lines = cart.map(i => `  • ${i.name} x${i.qty} = ${formatKsh(i.price * i.qty)}`).join('\n');
  const total = formatKsh(cartTotal());
  const locLine = del === 'Delivery' && loc ? `\n📍 Delivery to: ${loc}` : '';
  const noteLine = notes ? `\n📝 Notes: ${notes}` : '';
  const msg = `🛒 *NEW ORDER — Nishtronics Soundlabs*\n\n👤 *Name:* ${name}\n📞 *Phone:* ${phone}\n🚚 *Fulfilment:* ${del}${locLine}\n\n📦 *Items:*\n${lines}\n\n💰 *TOTAL: ${total}*${noteLine}\n\nPlease confirm availability and provide payment details. Thank you!`;
  window.open(`https://wa.me/254700000000?text=${encodeURIComponent(msg)}`, '_blank');

  // Log to Firebase if connected
  if (window.FIREBASE_READY) {
    try { await fsAddOrder({ customer: name, phone, delivery: del, location: loc, items: cart, total: cartTotal(), notes, status: 'new' }); }
    catch(e) { console.log('Firebase order log failed:', e); }
  }
}
