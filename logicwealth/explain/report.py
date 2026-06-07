from __future__ import annotations

from logicwealth.models import PortfolioInput, ConstraintSpec, PortfolioSolution
from logicwealth.finance.metrics import sector_weights


def constraint_report(pi: PortfolioInput, spec: ConstraintSpec, sol: PortfolioSolution) -> str:
    lines=[]
    lines.append("# LogicWealth Optimization Report")
    lines.append("")
    lines.append(f"Status: **{sol.status}**")
    if sol.metrics:
        lines.append(f"Expected annual return: **{sol.metrics['expected_return']:.2%}**")
        lines.append(f"Expected volatility: **{sol.metrics['volatility']:.2%}**")
        lines.append(f"Sharpe proxy: **{sol.metrics['sharpe']:.2f}**")
        lines.append(f"Beta: **{sol.metrics['beta']:.2f}**")
        lines.append(f"Average ESG: **{sol.metrics['esg']:.1f}**")
    lines.append("")
    lines.append("## Selected portfolio")
    for t,w in sorted(sol.selected.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {t}: {w:.2%} ({sol.shares.get(t,0)} shares)")
    if sol.selected:
        lines.append("")
        lines.append("## Sector exposure")
        for s,w in sorted(sector_weights(sol.selected, pi.assets).items()):
            lines.append(f"- {s}: {w:.2%}")
    lines.append("")
    lines.append("## Constraint satisfaction")
    if not sol.violations:
        lines.append("- ✓ No detected violations.")
    else:
        for v in sol.violations:
            lines.append(f"- ⚠ {v}")
    return "\n".join(lines)


def why_not_asset(pi: PortfolioInput, spec: ConstraintSpec, sol: PortfolioSolution, ticker: str) -> str:
    ticker=ticker.upper()
    amap={a.ticker:a for a in pi.assets}
    if ticker in sol.selected:
        return f"{ticker} is included with weight {sol.selected[ticker]:.2%}."
    if ticker not in amap:
        return f"{ticker} is not in the current asset universe."
    a=amap[ticker]
    reasons=[]
    if spec.esg_min is not None and a.esg < spec.esg_min:
        reasons.append(f"ESG score {a.esg:.1f} is below the minimum {spec.esg_min:.1f}.")
    if spec.liquidity_min is not None and a.adv < spec.liquidity_min:
        reasons.append(f"Average daily volume {a.adv:,.0f} is below the minimum {spec.liquidity_min:,.0f}.")
    for b,wt in sol.selected.items():
        corr=pi.correlations.get(tuple(sorted((ticker,b))),0)
        if spec.correlation_forbid_above is not None and corr>spec.correlation_forbid_above:
            reasons.append(f"Correlation with selected {b} is {corr:.2f}, above {spec.correlation_forbid_above:.2f}.")
    if spec.sector_max.get(a.sector) is not None:
        from logicwealth.finance.metrics import sector_weights
        sw=sector_weights(sol.selected, pi.assets)
        if sw.get(a.sector,0)+spec.min_weight>spec.sector_max[a.sector]:
            reasons.append(f"Adding it at the minimum weight would exceed the {a.sector} sector cap.")
    if not reasons:
        reasons.append("It was eligible, but the optimizer preferred other assets under the risk-adjusted objective and active constraints.")
    return f"Why {ticker} was excluded:\n" + "\n".join(f"- {r}" for r in reasons)
