import { PORTFOLIO_DATA } from './data.js';

document.addEventListener('DOMContentLoaded', () => {
  renderSidebar();
  renderDashboard();
  setupDrawers();
});

function renderSidebar() {
  const sidebar = document.getElementById('sidebar-nav');
  // Dynamic generation can go here, for now it's static links in HTML
}

function renderDashboard() {
  const overviewGrid = document.getElementById('overview-grid');
  const heatmapGrid = document.getElementById('heatmap-grid');
  const macroGrid = document.getElementById('macro-grid');
  
  // Render Overview Matrix (Top Movers)
  const topAssets = ['MSFT', 'NVDA', 'META', 'MU'];
  topAssets.forEach(ticker => {
    const data = PORTFOLIO_DATA.assets[ticker];
    overviewGrid.innerHTML += `
      <div class="bento-card" onclick="openDrawer('${ticker}')" style="cursor:pointer">
        <div class="flex-between mb-2">
          <span style="font-weight:700; font-size:16px" class="text-${data.color}">${ticker}</span>
          <span class="metric-badge bg-${data.color}">${data.action}</span>
        </div>
        <div class="metric-value">$${data.price}</div>
        <div class="metric-sub">Target: $${data.target} (+${data.upside}%)</div>
      </div>
    `;
  });

  // Render Heatmap (All)
  Object.values(PORTFOLIO_DATA.assets).forEach(data => {
    heatmapGrid.innerHTML += `
      <div class="bento-card" onclick="openDrawer('${data.id}')" style="cursor:pointer">
        <div class="flex-between mb-2">
          <span style="font-weight:600; font-size:14px">${data.id}</span>
          <span class="text-${data.color}" style="font-size:12px; font-weight:600">+${data.upside}%</span>
        </div>
        <div class="metric-value" style="font-size:22px;">$${data.price}</div>
        <div class="flex-gap mt-2" style="font-size:11px; color:var(--text-muted); flex-wrap:wrap;">
          <span>P/E ${data.pe}</span> <span>${data.mcap}</span> <span>${data.revGrowth} rev</span>
        </div>
        <div class="bar-chart">
          <div class="bar-track">
            <div class="bar-fill bg-${data.color}" style="width: ${Math.min(data.upside, 100)}%"></div>
          </div>
        </div>
        <div style="font-size:12px; color:var(--text-secondary); line-height:1.4">${data.insights}</div>
      </div>
    `;
  });

  // Render Macro
  PORTFOLIO_DATA.macro.forEach(item => {
    macroGrid.innerHTML += `
      <div class="bento-card" style="padding:16px; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:500">${item.label}</span>
        <span class="metric-badge bg-${item.risk === 'high' ? 'red' : 'amber'}">${item.val}</span>
      </div>
    `;
  });
}

function setupDrawers() {
  window.openDrawer = (ticker) => {
    const data = PORTFOLIO_DATA.deepDives[ticker];
    if (!data) return; // Only 3 are fully populated in demo
    
    document.getElementById('drawer-title').innerText = ticker + " Deep Dive";
    
    // metrics
    const metricsHtml = data.metrics.map(m => `
      <div class="bento-card" style="padding:16px;">
        <div class="metric-value" style="font-size:20px">${m.val}</div>
        <div class="metric-sub">${m.lbl}</div>
      </div>
    `).join('');
    document.getElementById('drawer-metrics').innerHTML = metricsHtml;

    document.getElementById('drawer-bluf').innerText = data.bluf;
    
    // cases
    document.getElementById('drawer-bull').innerHTML = data.bull.map(t => `<li style="margin-bottom:8px; font-size:13px"><span class="text-green mr-2">▲</span> ${t}</li>`).join('');
    document.getElementById('drawer-bear').innerHTML = data.bear.map(t => `<li style="margin-bottom:8px; font-size:13px"><span class="text-red mr-2">▼</span> ${t}</li>`).join('');
    
    // anim and open
    document.getElementById('drawer-overlay').classList.add('open');
    document.getElementById('side-drawer').classList.add('open');
  };

  window.closeDrawer = () => {
    document.getElementById('drawer-overlay').classList.remove('open');
    document.getElementById('side-drawer').classList.remove('open');
  };
}
