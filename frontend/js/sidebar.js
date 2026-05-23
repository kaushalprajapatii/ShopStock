// Sidebar HTML generator
function getSidebarHTML() {
  return `
  <div class="sidebar-overlay" id="sidebar-overlay"></div>
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-brand">
      <h1>ShopStock</h1>
      <p>Inventory Manager</p>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section-label">Main</div>
      <a class="nav-item" href="/dashboard.html">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        Dashboard
      </a>
      <div class="nav-section-label">Inventory</div>
      <a class="nav-item" href="/products.html">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        Products
      </a>
      <a class="nav-item" href="/low-stock.html">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Low Stock
        <span class="nav-badge low-stock-badge" style="display:none">0</span>
      </a>
      <div class="nav-section-label">Transactions</div>
      <a class="nav-item" href="/transactions.html">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        Transactions
      </a>
      <div class="nav-section-label">Export</div>
      <a class="nav-item" href="/export.html">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Export
      </a>
    </nav>
    <div class="sidebar-footer">
      <span id="admin-email">admin</span>
      <button class="logout-btn" id="logout-btn">Logout</button>
    </div>
  </aside>`;
}

// Inject sidebar into page
function injectSidebar() {
  const placeholder = document.getElementById('sidebar-placeholder');
  if (placeholder) {
    placeholder.innerHTML = getSidebarHTML();
  }
}

document.addEventListener('DOMContentLoaded', injectSidebar);
