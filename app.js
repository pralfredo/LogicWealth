const $ = (id) => document.getElementById(id);
const fmtPct = (x, d=1) => Number.isFinite(x) ? `${(x*100).toFixed(d)}%` : '—';
const fmtNum = (x, d=2) => Number.isFinite(x) ? x.toFixed(d) : '—';
const fmtMoney = (x) => Number.isFinite(x) ? `$${Math.round(x).toLocaleString()}` : '—';

const defaultValues = {
  backend:'auto', capital:1000000, cardinality:18, minWeight:0.025, maxWeight:0.095,
  esgMin:58, liqMin:8000000, corrMax:0.90, betaMin:0.80, betaMax:1.15, volMax:0.26,
  whyNot:'NVDA', techMax:0.26, healthMax:0.22, energyMax:0.12, utilitiesMin:0.04, staplesMin:0.05
};

const STATIC_UNIVERSE = [
  { ticker: "AAPL", sector: "Technology", price: 195.30, expected_return: 0.112, volatility: 0.215, beta: 1.18, esg: 72, adv: 62000000 },
  { ticker: "MSFT", sector: "Technology", price: 420.10, expected_return: 0.105, volatility: 0.198, beta: 1.05, esg: 78, adv: 35000000 },
  { ticker: "NVDA", sector: "Technology", price: 890.40, expected_return: 0.168, volatility: 0.352, beta: 1.72, esg: 64, adv: 48000000 },
  { ticker: "AVGO", sector: "Technology", price: 1320.20, expected_return: 0.124, volatility: 0.287, beta: 1.21, esg: 66, adv: 4200000 },
  { ticker: "ORCL", sector: "Technology", price: 124.60, expected_return: 0.081, volatility: 0.221, beta: 1.02, esg: 70, adv: 11000000 },
  { ticker: "CRM", sector: "Technology", price: 271.50, expected_return: 0.092, volatility: 0.263, beta: 1.18, esg: 76, adv: 6500000 },
  { ticker: "ADBE", sector: "Technology", price: 525.80, expected_return: 0.089, volatility: 0.244, beta: 1.11, esg: 79, adv: 3300000 },
  { ticker: "AMD", sector: "Technology", price: 162.40, expected_return: 0.141, volatility: 0.338, beta: 1.68, esg: 67, adv: 59000000 },
  { ticker: "INTC", sector: "Technology", price: 32.70, expected_return: 0.052, volatility: 0.301, beta: 1.24, esg: 62, adv: 42000000 },
  { ticker: "CSCO", sector: "Technology", price: 48.90, expected_return: 0.059, volatility: 0.181, beta: 0.86, esg: 74, adv: 18000000 },

  { ticker: "GOOGL", sector: "Communication Services", price: 173.20, expected_return: 0.098, volatility: 0.226, beta: 1.07, esg: 71, adv: 28000000 },
  { ticker: "META", sector: "Communication Services", price: 486.10, expected_return: 0.121, volatility: 0.292, beta: 1.31, esg: 63, adv: 17000000 },
  { ticker: "NFLX", sector: "Communication Services", price: 642.30, expected_return: 0.109, volatility: 0.315, beta: 1.26, esg: 68, adv: 3800000 },
  { ticker: "DIS", sector: "Communication Services", price: 103.40, expected_return: 0.061, volatility: 0.244, beta: 1.12, esg: 70, adv: 9500000 },
  { ticker: "TMUS", sector: "Communication Services", price: 176.80, expected_return: 0.074, volatility: 0.169, beta: 0.72, esg: 73, adv: 4700000 },

  { ticker: "AMZN", sector: "Consumer Discretionary", price: 184.70, expected_return: 0.113, volatility: 0.274, beta: 1.23, esg: 65, adv: 41000000 },
  { ticker: "TSLA", sector: "Consumer Discretionary", price: 178.20, expected_return: 0.137, volatility: 0.448, beta: 2.05, esg: 59, adv: 96000000 },
  { ticker: "HD", sector: "Consumer Discretionary", price: 342.50, expected_return: 0.071, volatility: 0.188, beta: 0.94, esg: 72, adv: 3900000 },
  { ticker: "MCD", sector: "Consumer Discretionary", price: 285.90, expected_return: 0.064, volatility: 0.142, beta: 0.61, esg: 77, adv: 2700000 },
  { ticker: "NKE", sector: "Consumer Discretionary", price: 94.30, expected_return: 0.056, volatility: 0.236, beta: 1.03, esg: 75, adv: 8200000 },

  { ticker: "JPM", sector: "Financials", price: 198.40, expected_return: 0.084, volatility: 0.217, beta: 1.12, esg: 69, adv: 9300000 },
  { ticker: "BAC", sector: "Financials", price: 39.10, expected_return: 0.078, volatility: 0.241, beta: 1.20, esg: 66, adv: 37000000 },
  { ticker: "GS", sector: "Financials", price: 456.80, expected_return: 0.086, volatility: 0.229, beta: 1.15, esg: 68, adv: 2300000 },
  { ticker: "MS", sector: "Financials", price: 96.50, expected_return: 0.081, volatility: 0.222, beta: 1.11, esg: 70, adv: 7100000 },
  { ticker: "V", sector: "Financials", price: 276.40, expected_return: 0.087, volatility: 0.173, beta: 0.92, esg: 76, adv: 6700000 },
  { ticker: "MA", sector: "Financials", price: 456.10, expected_return: 0.091, volatility: 0.181, beta: 0.96, esg: 75, adv: 3100000 },
  { ticker: "AXP", sector: "Financials", price: 238.70, expected_return: 0.082, volatility: 0.226, beta: 1.18, esg: 67, adv: 2900000 },

  { ticker: "UNH", sector: "Healthcare", price: 512.50, expected_return: 0.083, volatility: 0.177, beta: 0.74, esg: 73, adv: 3900000 },
  { ticker: "JNJ", sector: "Healthcare", price: 151.80, expected_return: 0.067, volatility: 0.134, beta: 0.62, esg: 83, adv: 9800000 },
  { ticker: "LLY", sector: "Healthcare", price: 883.20, expected_return: 0.128, volatility: 0.241, beta: 0.87, esg: 78, adv: 3100000 },
  { ticker: "PFE", sector: "Healthcare", price: 28.90, expected_return: 0.042, volatility: 0.201, beta: 0.69, esg: 76, adv: 35000000 },
  { ticker: "MRK", sector: "Healthcare", price: 128.40, expected_return: 0.074, volatility: 0.159, beta: 0.58, esg: 81, adv: 8900000 },
  { ticker: "ABBV", sector: "Healthcare", price: 171.20, expected_return: 0.071, volatility: 0.166, beta: 0.64, esg: 74, adv: 6200000 },
  { ticker: "TMO", sector: "Healthcare", price: 575.90, expected_return: 0.076, volatility: 0.196, beta: 0.82, esg: 79, adv: 1600000 },

  { ticker: "PG", sector: "Consumer Staples", price: 166.40, expected_return: 0.061, volatility: 0.121, beta: 0.48, esg: 80, adv: 7200000 },
  { ticker: "KO", sector: "Consumer Staples", price: 62.10, expected_return: 0.052, volatility: 0.113, beta: 0.43, esg: 78, adv: 14000000 },
  { ticker: "PEP", sector: "Consumer Staples", price: 178.80, expected_return: 0.057, volatility: 0.128, beta: 0.51, esg: 79, adv: 5600000 },
  { ticker: "COST", sector: "Consumer Staples", price: 812.40, expected_return: 0.082, volatility: 0.174, beta: 0.78, esg: 76, adv: 2200000 },
  { ticker: "WMT", sector: "Consumer Staples", price: 67.20, expected_return: 0.064, volatility: 0.139, beta: 0.55, esg: 77, adv: 16000000 },

  { ticker: "XOM", sector: "Energy", price: 114.50, expected_return: 0.073, volatility: 0.238, beta: 1.05, esg: 58, adv: 18000000 },
  { ticker: "CVX", sector: "Energy", price: 157.30, expected_return: 0.069, volatility: 0.221, beta: 0.98, esg: 60, adv: 8500000 },
  { ticker: "COP", sector: "Energy", price: 112.70, expected_return: 0.076, volatility: 0.257, beta: 1.11, esg: 59, adv: 6400000 },

  { ticker: "NEE", sector: "Utilities", price: 74.20, expected_return: 0.074, volatility: 0.169, beta: 0.71, esg: 86, adv: 11000000 },
  { ticker: "DUK", sector: "Utilities", price: 102.60, expected_return: 0.053, volatility: 0.137, beta: 0.44, esg: 75, adv: 3900000 },
  { ticker: "SO", sector: "Utilities", price: 78.40, expected_return: 0.055, volatility: 0.132, beta: 0.41, esg: 74, adv: 5100000 },

  { ticker: "CAT", sector: "Industrials", price: 337.90, expected_return: 0.083, volatility: 0.224, beta: 1.09, esg: 65, adv: 3100000 },
  { ticker: "GE", sector: "Industrials", price: 162.70, expected_return: 0.092, volatility: 0.251, beta: 1.18, esg: 68, adv: 7200000 },
  { ticker: "HON", sector: "Industrials", price: 203.40, expected_return: 0.071, volatility: 0.181, beta: 0.96, esg: 73, adv: 2900000 },
  { ticker: "RTX", sector: "Industrials", price: 105.80, expected_return: 0.066, volatility: 0.176, beta: 0.82, esg: 62, adv: 6100000 },

  { ticker: "PLD", sector: "Real Estate", price: 119.60, expected_return: 0.064, volatility: 0.214, beta: 0.91, esg: 72, adv: 3600000 }
];

let universe = [];
let latest = null;

function readNumber(id){ return Number($(id).value); }
function setValues(values){ Object.entries(values).forEach(([k,v]) => { if($(k)) $(k).value = v; }); }
function reset(){ setValues(defaultValues); }

function constraintsFromForm(){
  return {
    universe: 'sample_large_cap',
    capital: readNumber('capital'),
    objective: { type: 'mean_variance', risk_aversion: 0.70, transaction_cost_penalty: 0.20 },
    constraints: {
      cardinality: { exactly: Math.round(readNumber('cardinality')) },
      weights: { min_if_selected: readNumber('minWeight'), max_if_selected: readNumber('maxWeight') },
      sectors: {
        Technology: { max_weight: readNumber('techMax') },
        Healthcare: { max_weight: readNumber('healthMax') },
        Energy: { max_weight: readNumber('energyMax') },
        Utilities: { min_weight: readNumber('utilitiesMin') },
        'Consumer Staples': { min_weight: readNumber('staplesMin') }
      },
      risk: {
        beta: { min: readNumber('betaMin'), max: readNumber('betaMax') },
        volatility: { max: readNumber('volMax') }
      },
      liquidity: { min_average_daily_volume: readNumber('liqMin') },
      esg: { min_score: readNumber('esgMin') },
      defensive: { min_count: 4 },
      turnover: { max: 0.25 },
      logic: [
        { if_selected: 'TSLA', then_not_selected: 'F' },
        { forbid_pair: ['V','MA'], reason: 'redundant payment network exposure' }
      ],
      correlation: { forbid_pair_above: readNumber('corrMax') }
    }
  };
}

async function api(path, options={}){
  const res = await fetch(path, { headers:{'Content-Type':'application/json'}, ...options });
  if(!res.ok){
    let detail; try{ detail = await res.json(); }catch{ detail = await res.text(); }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail.detail || detail));
  }
  return res.json();
}

async function checkApi(){
  const pill = $('apiStatus');
  try{
    await api('/api/health');
    pill.className = 'status-pill ok';
    pill.innerHTML = '<span></span> API online';
  }catch(e){
    pill.className = 'status-pill bad';
    pill.innerHTML = '<span></span> API offline';
  }
}

async function loadAssets(){
  try{
    universe = await api('/api/assets');
    renderUniverse();
  }catch(e){
    renderUniverse(STATIC_UNIVERSE);
    setApiStatus('Static demo mode', false);
  }
}

function renderUniverse(){
  const q = ($('assetSearch').value || '').trim().toLowerCase();
  const rows = universe.filter(a => !q || a.ticker.toLowerCase().includes(q) || a.sector.toLowerCase().includes(q))
    .map(a => `<tr>
      <td><strong>${a.ticker}</strong></td><td>${a.sector}</td><td>${fmtMoney(a.price)}</td>
      <td>${fmtPct(a.expected_return)}</td><td>${fmtPct(a.volatility)}</td><td>${fmtNum(a.beta,2)}</td>
      <td>${fmtNum(a.esg,1)}</td><td>${fmtMoney(a.adv)}</td>
    </tr>`).join('');
  $('assetRows').innerHTML = rows || `<tr><td colspan="8">No matching assets.</td></tr>`;
}

function renderSolution(data){
  latest = data;
  $('kpiStatus').textContent = data.status || '—';
  $('kpiBackend').textContent = `backend: ${data.backend || data.diagnostics?.backend || 'auto'}`;
  $('kpiReturn').textContent = fmtPct(data.metrics?.expected_return, 2);
  $('kpiVol').textContent = fmtPct(data.metrics?.volatility, 2);
  $('kpiSharpe').textContent = fmtNum(data.metrics?.sharpe, 2);
  $('holdingCount').textContent = `${data.holdings?.length || 0} assets`;

  const checkRows = (data.checks || []).map(c => `<li class="${c.ok ? '' : 'fail'}"><b>${c.ok ? '✓' : '×'}</b><span>${c.label}<br><small>${typeof c.value === 'number' && c.value < 2 ? fmtPct(c.value, 2) : c.value}</small></span></li>`).join('');
  const violations = (data.violations || []).map(v => `<li class="fail"><b>!</b><span>${v}</span></li>`).join('');
  $('checks').innerHTML = checkRows + violations || '<li><b>—</b><span>No checks returned.</span></li>';

  const sectors = Object.entries(data.sector_weights || {}).sort((a,b)=>b[1]-a[1]);
  $('sectorBars').innerHTML = sectors.map(([name,w]) => `<div class="bar-row"><span>${name}</span><div class="bar-track"><div class="bar-fill" style="--w:${Math.min(w*100,100)}%"></div></div><b>${fmtPct(w,1)}</b></div>`).join('') || '<p>No sector data.</p>';

  $('holdings').innerHTML = (data.holdings || []).map(h => `<tr>
    <td><strong>${h.ticker}</strong> ${h.defensive ? '<span class="pill">DEF</span>' : ''}</td>
    <td>${h.sector}</td><td><strong>${fmtPct(h.weight,2)}</strong></td><td>${h.shares.toLocaleString()}</td>
    <td>${fmtPct(h.expected_return)}</td><td>${fmtPct(h.volatility)}</td><td>${fmtNum(h.beta,2)}</td><td>${fmtNum(h.esg,1)}</td>
  </tr>`).join('') || '<tr><td colspan="8">No holdings. The mandate may be infeasible.</td></tr>';

  $('whyNotText').textContent = data.why_not || 'No why-not ticker requested.';
}

async function solve(){
  const start = performance.now();
  $('solveBtn').disabled = true;
  $('solveBtn').textContent = 'Solving…';
  $('solveTime').textContent = 'compiling mandate';

  try{
    const payload = {
      backend: $('backend').value,
      capital: readNumber('capital'),
      constraints: constraintsFromForm(),
      why_not: ($('whyNot').value || '').trim().toUpperCase() || null
    };

    const data = await api('/api/solve', {
      method:'POST',
      body: JSON.stringify(payload)
    });

    renderSolution(data);
    $('solveTime').textContent = `${Math.round(performance.now()-start)} ms`;
  }catch(e){
    const data = staticDemoSolve();
    renderSolution(data);

    $('kpiStatus').textContent = 'STATIC DEMO';
    $('solveTime').textContent = `${Math.round(performance.now()-start)} ms`;
    $('whyNotText').textContent =
      data.why_not ||
      'GitHub Pages cannot run the FastAPI solver, so this portfolio was generated from the embedded static universe.';
  }finally{
    $('solveBtn').disabled = false;
    $('solveBtn').textContent = 'Solve Portfolio';
  }
}

function loadStress(){
  setValues({ ...defaultValues, cardinality:30, esgMin:90, liqMin:100000000, volMax:0.12, techMax:0.10, maxWeight:0.05, minWeight:0.02, whyNot:'NVDA' });
  document.querySelector('#solver').scrollIntoView({ behavior:'smooth' });
}

async function loadUniverse() {
  try {
    const response = await fetch(`${API_BASE}/api/assets`);

    if (!response.ok) {
      throw new Error("API offline");
    }

    const assets = await response.json();
    setApiStatus("API online", true);
    renderUniverse(assets);
  } catch (error) {
    setApiStatus("Static demo mode", false);
    renderUniverse(STATIC_UNIVERSE);
  }
}

function setApiStatus(text, online) {
  const apiStatus = document.querySelector("#apiStatus");
  if (!apiStatus) return;

  apiStatus.textContent = text;

  if (online) {
    apiStatus.classList.add("online");
    apiStatus.classList.remove("offline");
  } else {
    apiStatus.classList.add("offline");
    apiStatus.classList.remove("online");
  }
}

function renderUniverse(assets) {
  const tbody =
    document.querySelector("#universeTableBody") ||
    document.querySelector("#universe tbody") ||
    document.querySelector("tbody");

  if (!tbody) return;

  tbody.innerHTML = assets.map(asset => `
    <tr>
      <td>${asset.ticker}</td>
      <td>${asset.sector}</td>
      <td>$${Number(asset.price || 0).toFixed(2)}</td>
      <td>${(Number(asset.expected_return || 0) * 100).toFixed(1)}%</td>
      <td>${(Number(asset.volatility || 0) * 100).toFixed(1)}%</td>
      <td>${Number(asset.beta || 0).toFixed(2)}</td>
      <td>${asset.esg ?? "—"}</td>
      <td>${Number(asset.adv || 0).toLocaleString()}</td>
    </tr>
  `).join("");
}

function solveStaticDemo() {
  const selected = STATIC_UNIVERSE
    .filter(asset =>
      asset.esg >= 58 &&
      asset.adv >= 8000000 &&
      asset.volatility <= 0.30 &&
      asset.beta >= 0.80 &&
      asset.beta <= 1.15
    )
    .slice(0, 18);

  const weight = 1 / selected.length;

  const holdings = selected.map(asset => ({
    ...asset,
    weight,
    shares: Math.floor((1000000 * weight) / asset.price)
  }));

  function renderPortfolio(result) {
  const holdingsBody =
    document.querySelector("#holdingsTableBody") ||
    document.querySelector("#portfolioTableBody");

  const checksBox = document.querySelector("#checks");
  const whyNotBox = document.querySelector("#whyNotExplanation");

  if (holdingsBody) {
    holdingsBody.innerHTML = result.holdings.map(asset => `
      <tr>
        <td>${asset.ticker}</td>
        <td>${asset.sector}</td>
        <td>${(asset.weight * 100).toFixed(2)}%</td>
        <td>${asset.shares.toLocaleString()}</td>
        <td>${(asset.expected_return * 100).toFixed(1)}%</td>
        <td>${(asset.volatility * 100).toFixed(1)}%</td>
        <td>${asset.beta.toFixed(2)}</td>
        <td>${asset.esg}</td>
      </tr>
    `).join("");
  }

  if (checksBox) {
    checksBox.innerHTML = result.checks.map(check => `
      <div class="check-item">✓ ${check}</div>
    `).join("");
  }

  if (whyNotBox) {
    whyNotBox.textContent = result.why_not;
  }
}
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

// Background constellation
const canvas = $('constellation');
const ctx = canvas.getContext('2d');
let w, h, particles;
function resize(){
  w = canvas.width = innerWidth * devicePixelRatio;
  h = canvas.height = innerHeight * devicePixelRatio;
  canvas.style.width = innerWidth+'px'; canvas.style.height = innerHeight+'px';
  particles = Array.from({length: Math.min(180, Math.floor(innerWidth/7))}, () => ({
    x:Math.random()*w, y:Math.random()*h, vx:(Math.random()-.5)*.18, vy:(Math.random()-.5)*.18, r:Math.random()*1.7+.4
  }));
}
addEventListener('resize', resize); resize();
function tick(){
  ctx.clearRect(0,0,w,h);
  const g = ctx.createRadialGradient(w*.6,h*.25,0,w*.6,h*.25,w*.8);
  g.addColorStop(0,'rgba(134,247,255,.12)'); g.addColorStop(.42,'rgba(185,146,255,.08)'); g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0,0,w,h);
  for(const p of particles){
    p.x += p.vx*devicePixelRatio; p.y += p.vy*devicePixelRatio;
    if(p.x<0 || p.x>w) p.vx *= -1; if(p.y<0 || p.y>h) p.vy *= -1;
  }
  for(let i=0;i<particles.length;i++){
    const a = particles[i];
    ctx.beginPath(); ctx.arc(a.x,a.y,a.r*devicePixelRatio,0,Math.PI*2); ctx.fillStyle='rgba(255,255,255,.7)'; ctx.fill();
    for(let j=i+1;j<particles.length;j++){
      const b = particles[j], dx=a.x-b.x, dy=a.y-b.y, d=Math.hypot(dx,dy), lim=135*devicePixelRatio;
      if(d<lim){ ctx.strokeStyle=`rgba(134,247,255,${(1-d/lim)*.17})`; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }
    }
  }
  requestAnimationFrame(tick);
}
tick();

document.addEventListener("DOMContentLoaded", () => {
  loadUniverse();
});

$('solveBtn').addEventListener('click', solve);
$('resetBtn').addEventListener('click', () => { reset(); solve(); });
$('loadStrict').addEventListener('click', loadStress);
$('assetSearch').addEventListener('input', renderUniverse);

reset();
checkApi();
loadAssets();
solve();
