// ─── CONFIG ───
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : window.location.origin;

// ─── AUTH ───
const Auth = {
  getToken() { return localStorage.getItem('inv_token'); },
  getEmail() { return localStorage.getItem('inv_email'); },
  setToken(token, email) {
    localStorage.setItem('inv_token', token);
    localStorage.setItem('inv_email', email);
  },
  clear() {
    localStorage.removeItem('inv_token');
    localStorage.removeItem('inv_email');
  },
  isLoggedIn() { return !!this.getToken(); },
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/login.html';
    }
  },
  logout() {
    this.clear();
    window.location.href = '/login.html';
  }
};

// ─── API ───
const Api = {
  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (res.status === 401) { Auth.logout(); return; }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || 'Request failed');
    }
    if (res.status === 204) return null;
    return res.json();
  },

  get(path) { return this.request('GET', path); },
  post(path, body) { return this.request('POST', path, body); },
  put(path, body) { return this.request('PUT', path, body); },
  delete(path) { return this.request('DELETE', path); },

  async download(path, filename) {
    const token = Auth.getToken();
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Download failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};

// ─── TOAST ───
function toast(msg, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.3s';
    setTimeout(() => el.remove(), 300);
  }, 3000);
}

// ─── MODAL ───
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Close modal on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ─── SIDEBAR ───
function initSidebar() {
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay && overlay.classList.toggle('open');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    });
  }

  // Set active nav item
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('href') && path.includes(item.getAttribute('href').replace('.html', ''))) {
      item.classList.add('active');
    }
  });

  // Set email in sidebar footer
  const emailEl = document.getElementById('admin-email');
  if (emailEl) emailEl.textContent = Auth.getEmail() || 'admin';

  // Logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', () => Auth.logout());
}

// ─── FORMAT HELPERS ───
function formatCurrency(val) {
  return '₹' + Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function deptBadge(dept) {
  const cls = dept.replace(' ', '\\ ');
  return `<span class="dept-badge dept-${dept}">${dept}</span>`;
}

function lowStockBadge(isLow) {
  return isLow
    ? `<span class="badge badge-low">LOW</span>`
    : `<span class="badge badge-ok">OK</span>`;
}

// ─── LOW STOCK COUNT IN NAV ───
async function updateLowStockBadge() {
  if (!Auth.isLoggedIn()) return;
  try {
    const products = await Api.get('/products/low-stock');
    const badges = document.querySelectorAll('.low-stock-badge');
    badges.forEach(b => {
      if (products.length > 0) {
        b.textContent = products.length;
        b.style.display = 'inline';
      } else {
        b.style.display = 'none';
      }
    });
  } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  updateLowStockBadge();
});
