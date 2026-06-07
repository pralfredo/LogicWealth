from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from logicwealth.data_loader import load_assets, load_correlations
from logicwealth.dsl.parser import spec_from_dict
from logicwealth.solvers.engine import solve
from logicwealth.explain.report import why_not_asset
from logicwealth.finance.metrics import sector_weights

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DASHBOARD_DIR = ROOT / "dashboard"

app = FastAPI(
    title="LogicWealth API",
    description="SMT/heuristic portfolio construction API for the LogicWealth dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolveRequest(BaseModel):
    backend: str = Field("auto", description="auto, z3, or greedy")
    capital: float = Field(1_000_000, ge=1_000)
    constraints: Dict[str, Any]
    why_not: Optional[str] = None


def _load_input(capital: float):
    pi = load_assets(DATA_DIR / "sample_assets.csv", capital=capital)
    corr_path = DATA_DIR / "sample_correlations.csv"
    if corr_path.exists():
        pi.correlations = load_correlations(corr_path)
    return pi


def _asset_map(pi):
    return {a.ticker: a for a in pi.assets}


def _solution_payload(pi, spec, sol, why_not: Optional[str] = None) -> Dict[str, Any]:
    amap = _asset_map(pi)
    sectors = sector_weights(sol.selected, pi.assets) if sol.selected else {}
    holdings = []
    for ticker, weight in sorted(sol.selected.items(), key=lambda kv: -kv[1]):
        a = amap[ticker]
        holdings.append({
            "ticker": ticker,
            "weight": weight,
            "shares": sol.shares.get(ticker, 0),
            "sector": a.sector,
            "industry": a.industry,
            "expected_return": a.expected_return,
            "volatility": a.volatility,
            "beta": a.beta,
            "esg": a.esg,
            "adv": a.adv,
            "price": a.price,
            "defensive": a.defensive,
        })
    checks = []
    if spec.cardinality is not None:
        ok = len(sol.selected) == spec.cardinality
        checks.append({"label": f"Exactly {spec.cardinality} assets selected", "ok": ok, "value": len(sol.selected)})
    for sector, cap in spec.sector_max.items():
        value = sectors.get(sector, 0)
        checks.append({"label": f"{sector} exposure ≤ {cap:.1%}", "ok": value <= cap + 1e-9, "value": value})
    for sector, floor in spec.sector_min.items():
        value = sectors.get(sector, 0)
        checks.append({"label": f"{sector} exposure ≥ {floor:.1%}", "ok": value >= floor - 1e-9, "value": value})
    if sol.metrics:
        if spec.beta_min is not None or spec.beta_max is not None:
            lo = spec.beta_min if spec.beta_min is not None else float("-inf")
            hi = spec.beta_max if spec.beta_max is not None else float("inf")
            value = sol.metrics.get("beta", 0)
            checks.append({"label": f"Beta in [{lo:.2f}, {hi:.2f}]", "ok": lo <= value <= hi, "value": value})
        if spec.volatility_max is not None:
            value = sol.metrics.get("volatility", 0)
            checks.append({"label": f"Volatility ≤ {spec.volatility_max:.1%}", "ok": value <= spec.volatility_max + 1e-9, "value": value})
        if spec.turnover_max is not None:
            value = sol.metrics.get("turnover", 0)
            checks.append({"label": f"Turnover ≤ {spec.turnover_max:.1%}", "ok": value <= spec.turnover_max + 1e-9, "value": value})
    if spec.esg_min is not None:
        checks.append({"label": f"All selected ESG scores ≥ {spec.esg_min:.0f}", "ok": not any(amap[t].esg < spec.esg_min for t in sol.selected), "value": spec.esg_min})
    if spec.liquidity_min is not None:
        checks.append({"label": f"All selected ADV ≥ ${spec.liquidity_min:,.0f}", "ok": not any(amap[t].adv < spec.liquidity_min for t in sol.selected), "value": spec.liquidity_min})
    if spec.correlation_forbid_above is not None:
        bad_pairs = []
        for (a,b), corr in pi.correlations.items():
            if corr > spec.correlation_forbid_above and a in sol.selected and b in sol.selected:
                bad_pairs.append([a,b,corr])
        checks.append({"label": f"No selected pair correlation > {spec.correlation_forbid_above:.2f}", "ok": not bad_pairs, "value": len(bad_pairs)})

    explanation = None
    if why_not:
        explanation = why_not_asset(pi, spec, sol, why_not)

    return {
        "status": sol.status,
        "backend": sol.diagnostics.get("backend", "auto"),
        "diagnostics": sol.diagnostics,
        "metrics": sol.metrics,
        "holdings": holdings,
        "sector_weights": sectors,
        "checks": checks,
        "violations": sol.violations,
        "report_lines": sol.report,
        "why_not": explanation,
        "universe_size": len(pi.assets),
    }


@app.get("/api/health")
def health():
    return {"ok": True, "project": "LogicWealth", "dashboard": DASHBOARD_DIR.exists()}


@app.get("/api/assets")
def assets():
    pi = _load_input(1_000_000)
    return [{
        "ticker": a.ticker,
        "sector": a.sector,
        "industry": a.industry,
        "price": a.price,
        "expected_return": a.expected_return,
        "volatility": a.volatility,
        "beta": a.beta,
        "esg": a.esg,
        "adv": a.adv,
        "defensive": a.defensive,
        "quality": a.quality,
        "momentum": a.momentum,
    } for a in pi.assets]


@app.post("/api/solve")
def solve_portfolio(req: SolveRequest):
    try:
        pi = _load_input(req.capital)
        spec = spec_from_dict(req.constraints)
        sol = solve(pi, spec, backend=req.backend)
        return _solution_payload(pi, spec, sol, req.why_not)
    except Exception as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc), "trace": traceback.format_exc(limit=6)})


@app.get("/")
def index():
    return FileResponse(DASHBOARD_DIR / "index.html")


app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR), name="dashboard")
