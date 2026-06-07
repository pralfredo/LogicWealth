const $ = (id) => document.getElementById(id);
const fmtPct = (x, d=1) => Number.isFinite(x) ? `${(x*100).toFixed(d)}%` : '—';
const fmtNum = (x, d=2) => Number.isFinite(x) ? x.toFixed(d) : '—';
const fmtMoney = (x) => Number.isFinite(x) ? `$${Math.round(x).toLocaleString()}` : '—';

const defaultValues = {
  backend:'auto', capital:1000000, cardinality:18, minWeight:0.025, maxWeight:0.095,
  esgMin:58, liqMin:8000000, corrMax:0.90, betaMin:0.80, betaMax:1.15, volMax:0.26,
  whyNot:'NVDA', techMax:0.26, healthMax:0.22, energyMax:0.12, utilitiesMin:0.04, staplesMin:0.05
};

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
    $('assetRows').innerHTML = `<tr><td colspan="8" class="bad-text">Could not load universe. Start the FastAPI server.</td></tr>`;
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
    const data = await api('/api/solve', { method:'POST', body: JSON.stringify(payload) });
    renderSolution(data);
    $('solveTime').textContent = `${Math.round(performance.now()-start)} ms`;
  }catch(e){
    $('whyNotText').textContent = `Solver error:\n${e.message}`;
    $('kpiStatus').textContent = 'ERROR';
    $('solveTime').textContent = 'failed';
  }finally{
    $('solveBtn').disabled = false;
    $('solveBtn').textContent = 'Solve Portfolio';
  }
}

function loadStress(){
  setValues({ ...defaultValues, cardinality:30, esgMin:90, liqMin:100000000, volMax:0.12, techMax:0.10, maxWeight:0.05, minWeight:0.02, whyNot:'NVDA' });
  document.querySelector('#solver').scrollIntoView({ behavior:'smooth' });
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

$('solveBtn').addEventListener('click', solve);
$('resetBtn').addEventListener('click', () => { reset(); solve(); });
$('loadStrict').addEventListener('click', loadStress);
$('assetSearch').addEventListener('input', renderUniverse);

reset();
checkApi();
loadAssets();
solve();
