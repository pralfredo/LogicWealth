from __future__ import annotations

from typing import Dict, List, Tuple
from logicwealth.models import PortfolioInput, ConstraintSpec, PortfolioSolution, Asset
from logicwealth.finance.metrics import summary_metrics, sector_weights


def _eligible(asset: Asset, spec: ConstraintSpec) -> bool:
    if spec.esg_min is not None and asset.esg < spec.esg_min: return False
    if spec.liquidity_min is not None and asset.adv < spec.liquidity_min: return False
    return True


def _violations(pi: PortfolioInput, spec: ConstraintSpec, weights: Dict[str, float]) -> List[str]:
    assets = {a.ticker: a for a in pi.assets}
    selected = set(weights)
    v=[]
    if spec.cardinality is not None and len(selected) != spec.cardinality:
        v.append(f"cardinality {len(selected)} != {spec.cardinality}")
    for t,w in weights.items():
        if w < spec.min_weight - 1e-9: v.append(f"{t} below min weight")
        if w > spec.max_weight + 1e-9: v.append(f"{t} above max weight")
    sw = sector_weights(weights, pi.assets)
    for s,m in spec.sector_max.items():
        if sw.get(s,0)>m+1e-9: v.append(f"sector {s} {sw.get(s,0):.2%} > {m:.2%}")
    for s,m in spec.sector_min.items():
        if sw.get(s,0)<m-1e-9: v.append(f"sector {s} {sw.get(s,0):.2%} < {m:.2%}")
    met=summary_metrics(pi, weights)
    if spec.beta_min is not None and met['beta']<spec.beta_min: v.append("beta below min")
    if spec.beta_max is not None and met['beta']>spec.beta_max: v.append("beta above max")
    if spec.volatility_max is not None and met['volatility']>spec.volatility_max: v.append("volatility above max")
    if pi.current_weights and spec.turnover_max is not None and met['turnover']>spec.turnover_max: v.append("turnover above max")
    for a,b,reason in spec.forbid_pairs:
        if a in selected and b in selected: v.append(f"forbidden pair {a}/{b}: {reason}")
    for a,b,pol in spec.implications:
        if a in selected and ((b in selected) != pol):
            v.append(f"implication failed: if {a} then {'select' if pol else 'exclude'} {b}")
    if spec.correlation_forbid_above is not None:
        for (a,b),corr in pi.correlations.items():
            if corr>spec.correlation_forbid_above and a in selected and b in selected:
                v.append(f"correlation pair {a}/{b} {corr:.2f} > {spec.correlation_forbid_above:.2f}")
    return v


def solve_greedy(pi: PortfolioInput, spec: ConstraintSpec, risk_aversion: float = 0.7) -> PortfolioSolution:
    """Dependency-free heuristic backend. Z3/OR-Tools backends can replace this in production."""
    eligible = [a for a in pi.assets if _eligible(a, spec)]
    if not eligible:
        return PortfolioSolution("UNSAT", {}, {}, {}, [], ["No eligible assets after hard filters"], {})
    k = spec.cardinality or min(20, len(eligible))
    # Composite alpha: expected return + quality/momentum - risk penalty.
    scored = sorted(eligible, key=lambda a: (a.expected_return + 0.025*a.quality + 0.02*a.momentum - risk_aversion*a.volatility), reverse=True)
    selected: List[Asset] = []
    sector_counts: Dict[str,int] = {}
    for a in scored:
        if len(selected) >= k: break
        # Avoid explicit logical conflicts.
        if any((a.ticker == b and aa.ticker in [x.ticker for x in selected] and not pol) or (a.ticker == aa and b in [x.ticker for x in selected] and not pol) for aa,b,pol in spec.implications):
            continue
        if spec.correlation_forbid_above is not None:
            too_corr = False
            for s in selected:
                if pi.correlations.get(tuple(sorted((a.ticker, s.ticker))), 0) > spec.correlation_forbid_above:
                    too_corr=True; break
            if too_corr: continue
        selected.append(a)
    if len(selected) < k:
        return PortfolioSolution("UNSAT", {}, {}, {}, [], [f"Only {len(selected)} assets can be selected under hard pair/filter rules; required {k}."], {"eligible": len(eligible)})
    # Start with risk-adjusted proportional weights.
    raw={a.ticker: max(0.001, a.expected_return / max(a.volatility,0.001)) for a in selected}
    total=sum(raw.values())
    weights={t:v/total for t,v in raw.items()}
    # Clip to min/max and renormalize iteratively.
    for _ in range(12):
        for t in list(weights):
            weights[t]=min(spec.max_weight, max(spec.min_weight, weights[t]))
        total=sum(weights.values())
        weights={t:v/total for t,v in weights.items()}
    # Simple sector cap/floor repair by shifting excess across selected assets.
    for _ in range(30):
        sw=sector_weights(weights, pi.assets)
        changed=False
        # satisfy sector floors first
        for sector, floor in spec.sector_min.items():
            deficit=floor-sw.get(sector,0)
            if deficit>1e-6:
                receivers=[a.ticker for a in selected if a.sector==sector and weights[a.ticker]<spec.max_weight]
                donors=[a.ticker for a in selected if a.sector!=sector and weights[a.ticker]>spec.min_weight]
                if not receivers or not donors: continue
                for r in receivers:
                    add=min(deficit/len(receivers), spec.max_weight-weights[r])
                    per=add/len(donors)
                    for d in donors:
                        take=min(per, weights[d]-spec.min_weight)
                        weights[d]-=take
                        weights[r]+=take
                    changed=True
        sw=sector_weights(weights, pi.assets)
        for sector, cap in spec.sector_max.items():
            excess=sw.get(sector,0)-cap
            if excess>1e-6:
                donors=[a.ticker for a in selected if a.sector==sector and weights[a.ticker]>spec.min_weight]
                receivers=[a.ticker for a in selected if a.sector!=sector and weights[a.ticker]<spec.max_weight]
                if not donors or not receivers: continue
                for d in donors:
                    take=min(excess/len(donors), weights[d]-spec.min_weight)
                    weights[d]-=take
                    per=take/len(receivers)
                    for r in receivers: weights[r]=min(spec.max_weight, weights[r]+per)
                    changed=True
        if not changed: break
    metrics=summary_metrics(pi, weights)
    shares={}
    amap={a.ticker:a for a in pi.assets}
    for t,w in weights.items():
        shares[t]=int((pi.capital*w)//amap[t].price)
    violations=_violations(pi, spec, weights)
    report=[]
    report.append(f"Selected {len(weights)} assets with expected return {metrics['expected_return']:.2%}, volatility {metrics['volatility']:.2%}, Sharpe {metrics['sharpe']:.2f}.")
    report.append(f"Beta {metrics['beta']:.2f}; average ESG {metrics['esg']:.1f}; turnover {metrics['turnover']:.2%}.")
    return PortfolioSolution("OPTIMAL_HEURISTIC" if not violations else "FEASIBLE_WITH_WARNINGS", weights, shares, metrics, report, violations, {"backend":"greedy"})
