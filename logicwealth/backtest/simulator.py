from __future__ import annotations

from typing import Dict, List
from logicwealth.models import PortfolioInput, ConstraintSpec
from logicwealth.solvers.engine import solve


def single_period_demo(pi: PortfolioInput, spec: ConstraintSpec, backend: str = "auto") -> Dict[str, float]:
    sol = solve(pi, spec, backend=backend)
    return sol.metrics


def constraint_shadow_cost(pi: PortfolioInput, spec: ConstraintSpec) -> List[Dict[str, str]]:
    """Simple ablation: remove one constraint group at a time and compare Sharpe."""
    base = solve(pi, spec)
    base_sharpe = base.metrics.get("sharpe", 0.0) if base.metrics else 0.0
    rows=[]
    import copy
    for name in ["sector_max", "esg_min", "liquidity_min", "correlation_forbid_above", "beta_bounds"]:
        s=copy.deepcopy(spec)
        if name == "sector_max": s.sector_max={}
        elif name == "esg_min": s.esg_min=None
        elif name == "liquidity_min": s.liquidity_min=None
        elif name == "correlation_forbid_above": s.correlation_forbid_above=None
        elif name == "beta_bounds": s.beta_min=s.beta_max=None
        sol=solve(pi,s)
        sh=sol.metrics.get("sharpe", 0.0) if sol.metrics else 0.0
        rows.append({"removed_constraint": name, "base_sharpe": f"{base_sharpe:.3f}", "relaxed_sharpe": f"{sh:.3f}", "shadow_cost": f"{sh-base_sharpe:.3f}"})
    return rows
