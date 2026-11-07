/**
 * Pan & Tobacco B2B Wholesale App - Client Side Controller
 */

// Application State
const state = {
  platform_mode: 'white_label', // 'white_label' or 'marketplace'
  active_wholesaler_id: 1,
  active_wholesaler: null,
  wholesalers: [],
  categories: [],
  products: [],
  retailers: [],
  active_retailer_id: 1,
  selected_category: 'all',
  search_query: '',
  cart: {}, // productId -> { product, box_qty }
  current_tab: 'retailer', // 'retailer' or 'admin'
  admin_subtab: 'orders',
  admin_orders: [],
  admin_inventory: [],
  latest_order: null
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', async () => {
  await loadInitialData();
  lucide.createIcons();
});

async function loadInitialData() {
  await fetchConfig();
  await Promise.all([
    fetchWholesalers(),
    fetchCategories(),
    fetchRetailers(),
    fetchProducts()
  ]);
  renderHeaderAndHero();
  renderCategories();
  renderProducts();
  renderRetailerSelect();
  updateCartUI();
}

// --- API CALLS ---
async function fetchConfig() {
  try {
    const res = await fetch('/api/config');
    const data = await res.json();
    if (data.success) {
      state.platform_mode = data.platform_mode;
      state.active_wholesaler = data.active_wholesaler;
      state.active_wholesaler_id = data.active_wholesaler ? data.active_wholesaler.id : 1;
    }
  } catch (err) {
    console.error('Error fetching config:', err);
  }
}

async function fetchWholesalers() {
  try {
    const res = await fetch('/api/wholesalers');
    const data = await res.json();
    if (data.success) {
      state.wholesalers = data.wholesalers;
      if (!state.active_wholesaler && state.wholesalers.length > 0) {
        state.active_wholesaler = state.wholesalers[0];
        state.active_wholesaler_id = state.wholesalers[0].id;
      }
    }
  } catch (err) {
    console.error('Error fetching wholesalers:', err);
  }
}

async function fetchCategories() {
  try {
    const res = await fetch(`/api/categories?wholesaler_id=${state.active_wholesaler_id}`);
    const data = await res.json();
    if (data.success) {
      state.categories = data.categories;
    }
  } catch (err) {
    console.error('Error fetching categories:', err);
  }
}

async function fetchProducts() {
  try {
    const wid = state.active_wholesaler_id;
    let url = `/api/products?wholesaler_id=${wid}`;
    if (state.selected_category && state.selected_category !== 'all') {
      url += `&category_id=${state.selected_category}`;
    }
    if (state.search_query) {
      url += `&search=${encodeURIComponent(state.search_query)}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    if (data.success) {
      state.products = data.products;
    }
  } catch (err) {
    console.error('Error fetching products:', err);
  }
}

async function fetchRetailers() {
  try {
    const res = await fetch('/api/retailers');
    const data = await res.json();
    if (data.success) {
      state.retailers = data.retailers;
    }
  } catch (err) {
    console.error('Error fetching retailers:', err);
  }
}

// --- RENDER FUNCTIONS ---

function renderHeaderAndHero() {
  const w = state.active_wholesaler;
  if (!w) return;

  // Header Title & Logo
  const brandTitle = document.getElementById('brand-title');
  const brandCity = document.getElementById('brand-city');
  const brandLogoIcon = document.getElementById('brand-logo-icon');
  const activeModeLabel = document.getElementById('active-mode-label');
  const btnWhitelabel = document.getElementById('btn-mode-whitelabel');
  const btnMarketplace = document.getElementById('btn-mode-marketplace');

  if (state.platform_mode === 'white_label') {
    brandTitle.textContent = w.name;
    brandCity.textContent = w.city;
    activeModeLabel.textContent = `Dedicated Store: ${w.name}`;
    activeModeLabel.className = 'font-semibold text-emerald-400';

    btnWhitelabel.className = 'px-2.5 py-1 rounded text-xs font-semibold bg-emerald-600 text-white transition-all shadow-sm';
    btnMarketplace.className = 'px-2.5 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white transition-all';

    document.getElementById('single-wholesaler-banner').classList.remove('hidden');
    document.getElementById('marketplace-banner').classList.add('hidden');
  } else {
    brandTitle.textContent = "Pan Mandi Wholesale B2B";
    brandCity.textContent = "Multi-Wholesaler Hub";
    activeModeLabel.textContent = "Zomato-Style Multi-Wholesaler Marketplace";
    activeModeLabel.className = 'font-semibold text-amber-400';

    btnMarketplace.className = 'px-2.5 py-1 rounded text-xs font-semibold bg-amber-500 text-slate-950 transition-all shadow-sm font-bold';
    btnWhitelabel.className = 'px-2.5 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white transition-all';

    document.getElementById('single-wholesaler-banner').classList.add('hidden');
    document.getElementById('marketplace-banner').classList.remove('hidden');
    renderMarketplaceCards();
  }

  // Hero section in single wholesaler
  document.getElementById('hero-shop-name').textContent = w.name;
  document.getElementById('hero-shop-tagline').textContent = w.tagline || 'Sabse Bada Stock, Asli Wholesale Bhav';
  document.getElementById('hero-delivery-time').textContent = w.delivery_time;
  document.getElementById('hero-min-order').textContent = `₹${w.min_order_amount}`;
  document.getElementById('hero-free-delivery').textContent = `Above ₹${w.free_delivery_above}`;

  // WhatsApp Helpline link
  const waBtn = document.getElementById('header-whatsapp-btn');
  if (w.whatsapp) {
    const cleanWA = w.whatsapp.replace('+', '').replace(' ', '');
    waBtn.href = `https://api.whatsapp.com/send?phone=${cleanWA}&text=${encodeURIComponent(`Namaste ${w.name}, mujhe wholesale order ke baare me jankari chahiye.`)}`;
  }
}

function renderMarketplaceCards() {
  const container = document.getElementById('wholesalers-card-grid');
  if (!container) return;

  container.innerHTML = state.wholesalers.map(wh => {
    const isSelected = wh.id === state.active_wholesaler_id;
    return `
      <div class="bg-slate-800/90 rounded-2xl p-4 border ${isSelected ? 'border-amber-400 ring-2 ring-amber-400/30' : 'border-slate-700'} hover:border-amber-400 transition-all flex flex-col justify-between space-y-3">
        <div class="space-y-1.5">
          <div class="flex items-start justify-between gap-2">
            <h4 class="font-bold text-white text-sm">${wh.name}</h4>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-400 text-slate-950 flex items-center gap-1">
              ★ ${wh.rating}
            </span>
          </div>
          <p class="text-xs text-slate-300">${wh.tagline || 'Direct Mandi Supply'}</p>
          <p class="text-[11px] text-slate-400 flex items-center gap-1">
            📍 ${wh.address}, ${wh.city}
          </p>
        </div>

        <div class="bg-slate-900/80 p-2.5 rounded-xl border border-slate-700/60 flex items-center justify-between text-xs">
          <div>
            <span class="text-slate-400 block text-[10px]">Min. Order:</span>
            <span class="font-bold text-white">₹${wh.min_order_amount}</span>
          </div>
          <div class="text-right">
            <span class="text-slate-400 block text-[10px]">Delivery:</span>
            <span class="font-semibold text-emerald-400">${wh.delivery_time}</span>
          </div>
        </div>

        <button onclick="selectMarketplaceWholesaler(${wh.id})" class="w-full py-2 rounded-xl text-xs font-bold transition-all ${isSelected ? 'bg-amber-400 text-slate-950 font-black' : 'bg-slate-700 hover:bg-slate-600 text-white'}">
          ${isSelected ? '✓ Browsing This Wholesaler' : 'Order From Here →'}
        </button>
      </div>
    `;
  }).join('');
}

function renderCategories() {
  const container = document.getElementById('categories-container');
  if (!container) return;

  const allPill = `
    <button onclick="selectCategory('all')" id="cat-pill-all" class="category-pill whitespace-nowrap px-4 py-2 rounded-xl text-xs font-bold transition-all ${state.selected_category === 'all' ? 'bg-emerald-700 text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}">
      Sabhi Items (All)
    </button>
  `;

  const catPills = state.categories.map(c => {
    const isSelected = state.selected_category === c.id;
    return `
      <button onclick="selectCategory('${c.id}')" id="cat-pill-${c.id}" class="category-pill whitespace-nowrap px-4 py-2 rounded-xl text-xs font-semibold transition-all ${isSelected ? 'bg-emerald-700 text-white shadow-xs font-bold' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}">
        ${c.name} (${c.hindi_name})
      </button>
    `;
  }).join('');

  container.innerHTML = allPill + catPills;
}

function renderProducts() {
  const grid = document.getElementById('products-grid');
  const countBadge = document.getElementById('products-count-badge');
  const title = document.getElementById('current-category-title');

  if (countBadge) countBadge.textContent = `${state.products.length} Items`;
  if (title) {
    if (state.selected_category === 'all') {
      title.textContent = "All Wholesale Box Items";
    } else {
      const found = state.categories.find(c => c.id === state.selected_category);
      title.textContent = found ? `${found.name} (${found.hindi_name})` : "Wholesale Items";
    }
  }

  if (!grid) return;

  if (state.products.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-500 bg-white rounded-2xl border border-slate-200">
        <i data-lucide="package-search" class="w-12 h-12 mx-auto text-slate-300 mb-2"></i>
        <p class="font-bold text-slate-700">Koi item nahi mila</p>
        <p class="text-xs text-slate-400">Search badal kar ya doosri category select karein</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  grid.innerHTML = state.products.map(p => {
    const cartItem = state.cart[p.id];
    const qtyInCart = cartItem ? cartItem.box_qty : 0;
    const marginAmount = (p.retailer_margin_amount || (p.mrp - p.wholesale_price)).toFixed(1);
    const marginPct = (p.retailer_margin_pct || ((p.mrp - p.wholesale_price) / p.mrp * 100)).toFixed(0);

    return `
      <div class="bg-white rounded-2xl border border-slate-200 hover:border-emerald-500 shadow-xs hover:shadow-md transition-all flex flex-col justify-between overflow-hidden">
        
        <!-- Card Top & Badge -->
        <div class="p-4 space-y-2">
          <div class="flex items-center justify-between gap-1">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
              ${p.brand || 'B2B'}
            </span>
            ${p.badge ? `<span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-100 text-amber-900 border border-amber-300">${p.badge}</span>` : ''}
          </div>

          <div>
            <h4 class="font-extrabold text-slate-900 text-sm leading-snug">${p.name}</h4>
            <p class="text-xs text-slate-500 font-medium hindi-font">${p.hindi_name || ''}</p>
          </div>

          <!-- Box Specs Pill -->
          <div class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold">
            <i data-lucide="package" class="w-3.5 h-3.5 text-slate-500"></i>
            <span>${p.box_size_desc}</span>
          </div>

          <!-- Pricing & Margin Breakdown -->
          <div class="pt-2 border-t border-slate-100 space-y-1">
            <div class="flex items-baseline justify-between">
              <div>
                <span class="text-[10px] text-slate-400 block font-medium">Wholesale Rate:</span>
                <div class="flex items-baseline gap-1.5">
                  <span class="text-lg font-black text-emerald-800">₹${p.wholesale_price}</span>
                  <span class="text-xs text-slate-400 line-through">₹${p.mrp}</span>
                </div>
              </div>

              <!-- Retailer Margin Pill -->
              <div class="text-right">
                <span class="text-[10px] text-slate-400 block font-medium">Pan Shop Munafa:</span>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-900 text-xs font-extrabold">
                  +₹${marginAmount} (${marginPct}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Box Quantity Selector Footer -->
        <div class="p-3 bg-slate-50 border-t border-slate-100">
          ${qtyInCart === 0 ? `
            <div class="flex items-center gap-1.5">
              <button onclick="changeCartQty(${p.id}, 1)" class="flex-1 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-transform active:scale-95 shadow-xs">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                <span>Add Box</span>
              </button>
              <button onclick="changeCartQty(${p.id}, 5)" title="Quick Add 5 Boxes" class="px-2.5 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-900 font-bold text-xs rounded-xl transition-colors">
                +5
              </button>
            </div>
          ` : `
            <div class="flex items-center justify-between bg-white border border-emerald-600 rounded-xl p-1 shadow-xs">
              <button onclick="changeCartQty(${p.id}, -1)" class="w-8 h-8 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 flex items-center justify-center font-black">
                -
              </button>
              <div class="text-center px-2">
                <span class="font-extrabold text-sm text-slate-900">${qtyInCart}</span>
                <span class="text-[10px] text-slate-500 block leading-tight">Boxes</span>
              </div>
              <button onclick="changeCartQty(${p.id}, 1)" class="w-8 h-8 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white flex items-center justify-center font-black">
                +
              </button>
            </div>
          `}
        </div>

      </div>
    `;
  }).join('');

  lucide.createIcons();
}

function renderRetailerSelect() {
  const sel = document.getElementById('select-active-retailer');
  if (!sel) return;

  sel.innerHTML = state.retailers.map(r => {
    return `<option value="${r.id}" ${r.id === state.active_retailer_id ? 'selected' : ''}>${r.shop_name} (${r.area})</option>`;
  }).join('');

  updateRetailerKhataDisplay();
}

function updateRetailerKhataDisplay() {
  const ret = state.retailers.find(r => r.id === state.active_retailer_id);
  const display = document.getElementById('retailer-khata-display');
  const addressInput = document.getElementById('order-address-input');

  if (ret && display) {
    display.textContent = `₹${ret.khata_balance}`;
    if (addressInput && !addressInput.value) {
      addressInput.value = `${ret.address}, ${ret.area}, ${ret.city}`;
    }
  }
}

function onRetailerSelectChange(rid) {
  state.active_retailer_id = parseInt(rid);
  updateRetailerKhataDisplay();
}

// --- CART LOGIC ---
function changeCartQty(productId, delta) {
  const p = state.products.find(item => item.id === productId);
  if (!p) return;

  if (!state.cart[productId]) {
    if (delta > 0) {
      state.cart[productId] = { product: p, box_qty: delta };
    }
  } else {
    state.cart[productId].box_qty += delta;
    if (state.cart[productId].box_qty <= 0) {
      delete state.cart[productId];
    }
  }

  updateCartUI();
  renderProducts(); // re-render cards with updated qty
}

function updateCartUI() {
  const items = Object.values(state.cart);
  const totalBoxes = items.reduce((acc, it) => acc + it.box_qty, 0);
  const subtotal = items.reduce((acc, it) => acc + (it.product.wholesale_price * it.box_qty), 0);
  const totalProfit = items.reduce((acc, it) => acc + ((it.product.mrp - it.product.wholesale_price) * it.box_qty), 0);

  // Badge count
  const badge = document.getElementById('cart-count-badge');
  if (badge) badge.textContent = totalBoxes;

  // Floating Cart Bar
  const floatingBar = document.getElementById('floating-cart-bar');
  if (floatingBar) {
    if (totalBoxes > 0) {
      floatingBar.classList.remove('hidden');
      document.getElementById('floating-cart-boxes').textContent = `${totalBoxes} 📦`;
      document.getElementById('floating-cart-items-count').textContent = items.length;
      document.getElementById('floating-cart-total').textContent = `₹${subtotal.toFixed(2)}`;
    } else {
      floatingBar.classList.add('hidden');
    }
  }

  // Cart Modal Inner Calculation
  const w = state.active_wholesaler || { min_order_amount: 1000, free_delivery_above: 2500, delivery_charges: 50 };
  const deliveryCharges = subtotal >= w.free_delivery_above ? 0 : (subtotal > 0 ? w.delivery_charges : 0);
  const totalPayable = subtotal + deliveryCharges;

  const subtotalEl = document.getElementById('cart-subtotal-val');
  const deliveryEl = document.getElementById('cart-delivery-val');
  const profitEl = document.getElementById('cart-profit-val');
  const totalEl = document.getElementById('cart-total-val');

  if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
  if (deliveryEl) deliveryEl.textContent = deliveryCharges === 0 ? 'FREE' : `₹${deliveryCharges}`;
  if (profitEl) profitEl.textContent = `₹${totalProfit.toFixed(2)}`;
  if (totalEl) totalEl.textContent = `₹${totalPayable.toFixed(2)}`;

  // Delivery progress bar
  const progressBar = document.getElementById('cart-progress-bar');
  const deliveryMsg = document.getElementById('cart-delivery-msg');
  if (progressBar && deliveryMsg) {
    if (subtotal >= w.free_delivery_above) {
      progressBar.style.width = '100%';
      deliveryMsg.textContent = '🎉 Badiya! Free Godown Delivery Applied';
    } else {
      const pct = Math.min(100, Math.round((subtotal / w.free_delivery_above) * 100));
      progressBar.style.width = `${pct}%`;
      const needed = (w.free_delivery_above - subtotal).toFixed(0);
      deliveryMsg.textContent = `₹${needed} aur add karein Free Delivery ke liye`;
    }
  }

  // Render items in modal
  renderCartModalItems();
}

function renderCartModalItems() {
  const container = document.getElementById('cart-items-container');
  if (!container) return;

  const items = Object.values(state.cart);
  if (items.length === 0) {
    container.innerHTML = `
      <div class="py-12 text-center text-slate-400 space-y-2">
        <i data-lucide="shopping-bag" class="w-12 h-12 mx-auto text-slate-300"></i>
        <p class="font-bold text-slate-700">Aapka wholesale cart khali hai</p>
        <p class="text-xs text-slate-400">Box aur pettie add karne ke liye catalog dekhein</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = items.map(it => {
    const p = it.product;
    const lineTotal = (p.wholesale_price * it.box_qty).toFixed(2);
    return `
      <div class="flex items-center justify-between p-3 bg-white rounded-xl border border-slate-200 text-xs">
        <div class="flex-1 pr-2">
          <h5 class="font-bold text-slate-900">${p.name}</h5>
          <p class="text-[11px] text-slate-500">${p.box_size_desc} • ₹${p.wholesale_price}/box</p>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200">
            <button onclick="changeCartQty(${p.id}, -1)" class="w-6 h-6 rounded flex items-center justify-center font-bold text-slate-700 hover:bg-white">-</button>
            <span class="px-2 font-bold text-slate-900">${it.box_qty}</span>
            <button onclick="changeCartQty(${p.id}, 1)" class="w-6 h-6 rounded flex items-center justify-center font-bold text-slate-700 hover:bg-white">+</button>
          </div>

          <div class="text-right min-w-[70px]">
            <span class="font-extrabold text-slate-900">₹${lineTotal}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

function toggleCartModal(open) {
  const modal = document.getElementById('cart-modal');
  if (open) {
    updateCartUI();
    modal.classList.remove('hidden');
  } else {
    modal.classList.add('hidden');
  }
}

function updatePaymentModeStyle() {
  const radios = document.getElementsByName('payment_mode');
  radios.forEach(r => {
    const label = r.closest('label');
    if (r.checked) {
      label.className = 'payment-option cursor-pointer border-2 border-emerald-600 bg-emerald-50/50 p-2.5 rounded-xl flex flex-col items-center text-center transition-all';
    } else {
      label.className = 'payment-option cursor-pointer border border-slate-200 bg-white p-2.5 rounded-xl flex flex-col items-center text-center transition-all';
    }
  });
}

// --- SUBMIT ORDER ---
async function submitWholesaleOrder() {
  const items = Object.values(state.cart).map(it => ({
    product_id: it.product.id,
    box_qty: it.box_qty
  }));

  if (items.length === 0) {
    alert("Kripya pehle items cart me add karein!");
    return;
  }

  const ret = state.retailers.find(r => r.id === state.active_retailer_id) || {
    shop_name: 'Pan Shop Customer',
    owner_name: 'Retailer',
    phone: '+91 98765 00000',
    address: 'City'
  };

  const paymentRadios = document.getElementsByName('payment_mode');
  let selectedMode = 'COD';
  paymentRadios.forEach(r => { if (r.checked) selectedMode = r.value; });

  const address = document.getElementById('order-address-input').value || ret.address;
  const btn = document.getElementById('btn-submit-order');
  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin mr-2">⏳</span> Order Submit Ho Raha Hai...`;

  try {
    const payload = {
      wholesaler_id: state.active_wholesaler_id,
      retailer_id: state.active_retailer_id,
      retailer_name: ret.shop_name,
      retailer_phone: ret.phone,
      retailer_address: address,
      payment_mode: selectedMode,
      items: items
    };

    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      state.latest_order = data;
      // Clear Cart
      state.cart = {};
      updateCartUI();
      renderProducts();
      toggleCartModal(false);

      // Open Success Modal
      showOrderSuccess(data);
      // Refresh admin orders in background
      loadAdminOrders('all');
      fetchRetailers();
    } else {
      alert(`Error: ${data.error || 'Order place nahi ho paya'}`);
    }
  } catch (err) {
    console.error(err);
    alert("Connection error while submitting order.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4 mr-1"></i> Order Confirm Karein`;
    lucide.createIcons();
  }
}

function showOrderSuccess(orderData) {
  document.getElementById('success-order-code').textContent = orderData.order_code;
  document.getElementById('success-order-total').textContent = `₹${orderData.total_amount}`;
  document.getElementById('success-order-boxes').textContent = `${orderData.total_boxes} Boxes`;

  const waBtn = document.getElementById('btn-success-whatsapp');
  if (waBtn && orderData.whatsapp_url) {
    waBtn.href = orderData.whatsapp_url;
  }

  document.getElementById('order-success-modal').classList.remove('hidden');
}

function toggleSuccessModal(open) {
  const modal = document.getElementById('order-success-modal');
  if (open) modal.classList.remove('hidden');
  else modal.classList.add('hidden');
}

// --- PRINT / INVOICE MODAL ---
async function printCurrentOrderInvoice(orderId) {
  const idToFetch = orderId || (state.latest_order ? state.latest_order.order_id : null);
  if (!idToFetch) return;

  try {
    const res = await fetch(`/api/orders/${idToFetch}`);
    const data = await res.json();
    if (data.success) {
      const order = data.order;
      const w = state.active_wholesaler;

      document.getElementById('inv-wholesaler-name').textContent = order.wholesaler_name || w.name;
      document.getElementById('inv-wholesaler-address').textContent = w.address;
      document.getElementById('inv-wholesaler-phone').textContent = order.wholesaler_phone || w.phone;
      document.getElementById('inv-order-code').textContent = order.order_code;
      document.getElementById('inv-order-date').textContent = order.created_at;
      document.getElementById('inv-order-payment').textContent = order.payment_mode;
      document.getElementById('inv-retailer-name').textContent = order.retailer_name;
      document.getElementById('inv-retailer-phone').textContent = order.retailer_phone;
      document.getElementById('inv-total-boxes').textContent = order.total_boxes;
      document.getElementById('inv-total-amount').textContent = `₹${order.total_amount}`;

      const tbody = document.getElementById('inv-items-tbody');
      tbody.innerHTML = (order.items || []).map(it => `
        <tr>
          <td class="py-1">${it.product_name} <br><span class="text-[9px] text-slate-500">${it.box_size_desc}</span></td>
          <td class="py-1 text-center font-bold">${it.box_qty}</td>
          <td class="py-1 text-right">₹${it.price_per_box}</td>
          <td class="py-1 text-right font-bold">₹${it.subtotal}</td>
        </tr>
      `).join('');

      document.getElementById('invoice-modal').classList.remove('hidden');
    }
  } catch (err) {
    console.error(err);
  }
}

function toggleInvoiceModal(open) {
  const modal = document.getElementById('invoice-modal');
  if (open) modal.classList.remove('hidden');
  else modal.classList.add('hidden');
}

// --- FILTER & SEARCH ---
function selectCategory(catId) {
  state.selected_category = catId;
  renderCategories();
  fetchProducts().then(() => renderProducts());
}

function handleSearch(term) {
  state.search_query = term;
  fetchProducts().then(() => renderProducts());
}

// --- TAB SWITCHING (Retailer Store vs Wholesaler Admin) ---
function switchMainTab(tab) {
  state.current_tab = tab;
  const viewRetailer = document.getElementById('view-retailer');
  const viewAdmin = document.getElementById('view-admin');
  const tabBtnRetailer = document.getElementById('tab-btn-retailer');
  const tabBtnAdmin = document.getElementById('tab-btn-admin');

  if (tab === 'retailer') {
    viewRetailer.classList.remove('hidden');
    viewAdmin.classList.add('hidden');
    tabBtnRetailer.className = 'px-3 py-1.5 rounded-lg bg-white shadow-xs text-slate-900 font-semibold flex items-center gap-1.5 transition-all';
    tabBtnAdmin.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition-all';
  } else {
    viewRetailer.classList.add('hidden');
    viewAdmin.classList.remove('hidden');
    tabBtnAdmin.className = 'px-3 py-1.5 rounded-lg bg-white shadow-xs text-slate-900 font-semibold flex items-center gap-1.5 transition-all';
    tabBtnRetailer.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition-all';
    // Load admin data
    loadAdminStats();
    loadAdminOrders('all');
    loadAdminInventory();
    loadAdminKhata();
  }
}

// --- ADMIN DASHBOARD OPERATIONS ---
function switchAdminSubtab(sub) {
  state.admin_subtab = sub;
  const tabs = ['orders', 'inventory', 'khata'];
  tabs.forEach(t => {
    const btn = document.getElementById(`admin-subtab-${t}`);
    const content = document.getElementById(`admin-content-${t}`);
    if (t === sub) {
      btn.className = 'px-4 py-2.5 font-bold text-xs border-b-2 border-indigo-600 text-indigo-700 flex items-center gap-2';
      content.classList.remove('hidden');
    } else {
      btn.className = 'px-4 py-2.5 font-semibold text-xs text-slate-600 hover:text-slate-900 flex items-center gap-2';
      content.classList.add('hidden');
    }
  });
}

async function loadAdminStats() {
  try {
    const res = await fetch(`/api/stats?wholesaler_id=${state.active_wholesaler_id}`);
    const data = await res.json();
    if (data.success) {
      const s = data.stats;
      document.getElementById('stat-total-sales').textContent = `₹${s.total_sales.toLocaleString()}`;
      document.getElementById('stat-pending-orders').textContent = s.pending_orders;
      document.getElementById('stat-khata-due').textContent = `₹${s.total_khata_due.toLocaleString()}`;
      document.getElementById('stat-total-products').textContent = s.total_products;
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadAdminOrders(status = 'all') {
  try {
    const res = await fetch(`/api/orders?wholesaler_id=${state.active_wholesaler_id}&status=${status}`);
    const data = await res.json();
    if (data.success) {
      state.admin_orders = data.orders;
      renderAdminOrdersTable();
    }
  } catch (err) {
    console.error(err);
  }
}

function renderAdminOrdersTable() {
  const tbody = document.getElementById('admin-orders-tbody');
  if (!tbody) return;

  if (state.admin_orders.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-slate-400">Koi order uplabdh nahi hai</td></tr>`;
    return;
  }

  tbody.innerHTML = state.admin_orders.map(o => {
    let statusBadge = '';
    if (o.order_status === 'pending') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 animate-pulse">Pending (Pack Karein)</span>';
    else if (o.order_status === 'confirmed') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">Confirmed (Ready)</span>';
    else if (o.order_status === 'out_for_delivery') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800">Out For Delivery</span>';
    else if (o.order_status === 'delivered') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">Delivered</span>';

    const itemsSummary = (o.items || []).map(it => `<div>• ${it.product_name} (${it.box_qty} Box)</div>`).join('');

    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="p-3 font-mono font-bold text-slate-900">${o.order_code}<br><span class="text-[10px] text-slate-400">${o.created_at}</span></td>
        <td class="p-3">
          <div class="font-bold text-slate-900">${o.retailer_name}</div>
          <div class="text-[11px] text-slate-500">${o.retailer_phone}</div>
          <div class="text-[10px] text-slate-400 truncate max-w-xs">${o.retailer_address}</div>
        </td>
        <td class="p-3 text-[11px] text-slate-700 max-w-xs">${itemsSummary || `${o.total_boxes} Boxes`}</td>
        <td class="p-3">
          <div class="font-black text-slate-900">₹${o.total_amount}</div>
          <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold ${o.payment_mode === 'KHATA' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-slate-100 text-slate-700'}">${o.payment_mode}</span>
        </td>
        <td class="p-3">${statusBadge}</td>
        <td class="p-3 text-right space-x-1 whitespace-nowrap">
          ${o.order_status === 'pending' ? `
            <button onclick="updateOrderStatus(${o.id}, 'confirmed')" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-[10px] font-bold">Accept & Pack</button>
          ` : o.order_status === 'confirmed' ? `
            <button onclick="updateOrderStatus(${o.id}, 'out_for_delivery')" class="px-2.5 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-[10px] font-bold">Dispatch (रवाना)</button>
          ` : o.order_status === 'out_for_delivery' ? `
            <button onclick="updateOrderStatus(${o.id}, 'delivered')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-bold">Delivered</button>
          ` : ''}
          <button onclick="printCurrentOrderInvoice(${o.id})" title="Print Bill" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-[10px] font-bold">
            Bill 🖨️
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function updateOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch(`/api/orders/${orderId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    const data = await res.json();
    if (data.success) {
      loadAdminOrders('all');
      loadAdminStats();
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadAdminInventory() {
  try {
    const res = await fetch(`/api/products?wholesaler_id=${state.active_wholesaler_id}`);
    const data = await res.json();
    if (data.success) {
      state.admin_inventory = data.products;
      renderAdminInventoryTable();
    }
  } catch (err) {
    console.error(err);
  }
}

function renderAdminInventoryTable() {
  const tbody = document.getElementById('admin-inventory-tbody');
  if (!tbody) return;

  tbody.innerHTML = state.admin_inventory.map(p => {
    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="p-3">
          <div class="font-bold text-slate-900">${p.name}</div>
          <div class="text-[10px] text-slate-500">${p.brand} • ${p.hindi_name || ''}</div>
        </td>
        <td class="p-3 text-slate-600">${p.category_name}</td>
        <td class="p-3 font-semibold text-slate-700">${p.box_size_desc}</td>
        <td class="p-3">
          <input type="number" step="0.5" id="inv-price-${p.id}" value="${p.wholesale_price}" class="w-20 px-2 py-1 text-xs border border-slate-300 rounded font-bold text-emerald-800">
        </td>
        <td class="p-3 text-slate-500 font-semibold">₹${p.mrp}</td>
        <td class="p-3 text-emerald-700 font-bold">+₹${p.retailer_margin_amount} (${p.retailer_margin_pct}%)</td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${p.in_stock ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}">
            ${p.in_stock ? 'In Stock' : 'Out of Stock'}
          </span>
        </td>
        <td class="p-3 text-right">
          <button onclick="saveInventoryRate(${p.id})" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-bold">
            Rate Update
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function saveInventoryRate(pid) {
  const input = document.getElementById(`inv-price-${pid}`);
  if (!input) return;
  const newRate = parseFloat(input.value);

  try {
    const res = await fetch(`/api/products/${pid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wholesale_price: newRate })
    });
    const data = await res.json();
    if (data.success) {
      alert("Rate safaltapoorvak update ho gaya!");
      loadAdminInventory();
      fetchProducts().then(() => renderProducts());
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadAdminKhata() {
  await fetchRetailers();
  const tbody = document.getElementById('admin-khata-tbody');
  if (!tbody) return;

  tbody.innerHTML = state.retailers.map(r => {
    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="p-3 font-bold text-slate-900">${r.shop_name}</td>
        <td class="p-3 text-slate-600">${r.owner_name}<br><span class="text-[10px] text-slate-400">${r.phone}</span></td>
        <td class="p-3 text-slate-500">${r.area}, ${r.city}</td>
        <td class="p-3 font-semibold text-slate-700">₹${r.credit_limit}</td>
        <td class="p-3">
          <span class="font-extrabold text-sm ${r.khata_balance > 0 ? 'text-red-600' : 'text-emerald-700'}">
            ₹${r.khata_balance}
          </span>
        </td>
        <td class="p-3 text-right">
          <button onclick="openKhataPaymentModal(${r.id}, '${r.shop_name.replace(/'/g, "\\'")}', ${r.khata_balance})" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-bold">
            Record Payment (जमा करें)
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function openKhataPaymentModal(rid, shopName, currBal) {
  document.getElementById('khata-retailer-id').value = rid;
  document.getElementById('khata-modal-shop-name').textContent = shopName;
  document.getElementById('khata-modal-curr-bal').textContent = `₹${currBal}`;
  document.getElementById('khata-amount').value = '';
  document.getElementById('khata-payment-modal').classList.remove('hidden');
}

function toggleKhataModal(open) {
  const modal = document.getElementById('khata-payment-modal');
  if (open) modal.classList.remove('hidden');
  else modal.classList.add('hidden');
}

async function submitKhataPayment(e) {
  e.preventDefault();
  const rid = document.getElementById('khata-retailer-id').value;
  const amount = parseFloat(document.getElementById('khata-amount').value);
  const note = document.getElementById('khata-note').value;

  try {
    const res = await fetch('/api/khata/payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ retailer_id: rid, amount: amount, notes: note })
    });
    const data = await res.json();
    if (data.success) {
      alert("Payment khate me jama ho gaya!");
      toggleKhataModal(false);
      loadAdminKhata();
      loadAdminStats();
    }
  } catch (err) {
    console.error(err);
  }
}

// --- ADD NEW PRODUCT ---
function toggleAddProductModal(open) {
  const modal = document.getElementById('add-product-modal');
  if (open) modal.classList.remove('hidden');
  else modal.classList.add('hidden');
}

async function submitNewProduct(e) {
  e.preventDefault();
  const payload = {
    wholesaler_id: state.active_wholesaler_id,
    name: document.getElementById('prod-name').value,
    hindi_name: document.getElementById('prod-hindi-name').value,
    category_id: document.getElementById('prod-category').value,
    brand: document.getElementById('prod-brand').value,
    box_size_desc: document.getElementById('prod-box-desc').value,
    wholesale_price: parseFloat(document.getElementById('prod-price').value),
    mrp: parseFloat(document.getElementById('prod-mrp').value)
  };

  try {
    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      alert("Item safaltapoorvak add ho gaya!");
      toggleAddProductModal(false);
      loadAdminInventory();
      fetchProducts().then(() => renderProducts());
    }
  } catch (err) {
    console.error(err);
  }
}

// --- WHITE-LABEL BRANDING & BUSINESS MODEL TOGGLE ---
async function setPlatformMode(mode) {
  state.platform_mode = mode;
  try {
    await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform_mode: mode })
    });
  } catch (err) {
    console.error(err);
  }
  renderHeaderAndHero();
}

function selectMarketplaceWholesaler(wid) {
  state.active_wholesaler_id = wid;
  state.active_wholesaler = state.wholesalers.find(w => w.id === wid);
  renderHeaderAndHero();
  renderMarketplaceCards();
  // Clear cart when switching wholesaler to avoid mixed fulfillment
  state.cart = {};
  updateCartUI();
  fetchProducts().then(() => renderProducts());
}

function toggleWhiteLabelModal(open) {
  const modal = document.getElementById('whitelabel-modal');
  if (open) {
    const w = state.active_wholesaler;
    if (w) {
      document.getElementById('wl-name').value = w.name || '';
      document.getElementById('wl-tagline').value = w.tagline || '';
      document.getElementById('wl-phone').value = w.phone || '';
      document.getElementById('wl-whatsapp').value = w.whatsapp || '';
      document.getElementById('wl-upi').value = w.upi_id || '';
      document.getElementById('wl-min-order').value = w.min_order_amount || 1000;
      document.getElementById('wl-address').value = w.address || '';
      document.getElementById('wl-delivery-time').value = w.delivery_time || '2 - 4 Ghante';
      document.getElementById('wl-color').value = w.theme_color || '#15803d';
    }
    modal.classList.remove('hidden');
  } else {
    modal.classList.add('hidden');
  }
}

async function saveWhiteLabelSettings(e) {
  e.preventDefault();
  const wid = state.active_wholesaler_id;
  const payload = {
    name: document.getElementById('wl-name').value,
    tagline: document.getElementById('wl-tagline').value,
    phone: document.getElementById('wl-phone').value,
    whatsapp: document.getElementById('wl-whatsapp').value,
    upi_id: document.getElementById('wl-upi').value,
    min_order_amount: parseFloat(document.getElementById('wl-min-order').value),
    address: document.getElementById('wl-address').value,
    delivery_time: document.getElementById('wl-delivery-time').value,
    theme_color: document.getElementById('wl-color').value
  };

  try {
    const res = await fetch(`/api/wholesalers/${wid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      // Update local state
      Object.assign(state.active_wholesaler, payload);
      toggleWhiteLabelModal(false);
      renderHeaderAndHero();
      alert("✨ Wholesaler Branding Update Ho Gayi! Dukan ka naam aur details turant badal gayi hain.");
    }
  } catch (err) {
    console.error(err);
  }
}
