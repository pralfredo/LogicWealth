from __future__ import annotations

from typing import Dict, List
from logicwealth.models import PortfolioInput, ConstraintSpec, PortfolioSolution
from logicwealth.finance.metrics import summary_metrics, sector_weights


def solve_z3(pi: PortfolioInput, spec: ConstraintSpec) -> PortfolioSolution:
    """SMT backend using Z3 Optimize when installed.

    This backend is intentionally linear: it optimizes expected return minus linearized
    risk penalties. For quadratic variance, use a MIQP backend in production.
    """
    try:
        from z3 import Bool, Real, If, Optimize, Sum, Implies, And, Not, sat  # type: ignore
    except Exception as e:
        from .greedy_backend import solve_greedy
        sol = solve_greedy(pi, spec)
        sol.diagnostics["z3_fallback"] = f"Z3 unavailable: {e}"
        return sol

    assets = pi.assets
    tickers = [a.ticker for a in assets]
    amap = {a.ticker:a for a in assets}
    x = {t: Bool(f"select_{t}") for t in tickers}
    w = {t: Real(f"weight_{t}") for t in tickers}
    opt = Optimize()

    for a in assets:
        opt.add(w[a.ticker] >= 0)
        opt.add(Implies(x[a.ticker], And(w[a.ticker] >= spec.min_weight, w[a.ticker] <= spec.max_weight)))
        opt.add(Implies(Not(x[a.ticker]), w[a.ticker] == 0))
        if spec.esg_min is not None and a.esg < spec.esg_min:
            opt.add(Not(x[a.ticker]))
        if spec.liquidity_min is not None and a.adv < spec.liquidity_min:
            opt.add(Not(x[a.ticker]))
    opt.add(Sum([w[t] for t in tickers]) == 1)
    if spec.cardinality is not None:
        opt.add(Sum([If(x[t], 1, 0) for t in tickers]) == spec.cardinality)
    for sector, cap in spec.sector_max.items():
        opt.add(Sum([w[a.ticker] for a in assets if a.sector == sector]) <= cap)
    for sector, floor in spec.sector_min.items():
        opt.add(Sum([w[a.ticker] for a in assets if a.sector == sector]) >= floor)
    if spec.beta_min is not None:
        opt.add(Sum([w[a.ticker]*a.beta for a in assets]) >= spec.beta_min)
    if spec.beta_max is not None:
        opt.add(Sum([w[a.ticker]*a.beta for a in assets]) <= spec.beta_max)
    if spec.defensive_min_count is not None:
        opt.add(Sum([If(x[a.ticker],1,0) for a in assets if a.defensive]) >= spec.defensive_min_count)
    for a,b,pol in spec.implications:
        if a in x and b in x:
            opt.add(Implies(x[a], x[b] if pol else Not(x[b])))
    for a,b,reason in spec.forbid_pairs:
        if a in x and b in x:
            opt.add(Not(And(x[a], x[b])))
    if spec.correlation_forbid_above is not None:
        for (a,b), corr in pi.correlations.items():
            if corr > spec.correlation_forbid_above and a in x and b in x:
                opt.add(Not(And(x[a], x[b])))

    # Linear risk-adjusted alpha objective.
    score = Sum([w[a.ticker]*(a.expected_return - 0.35*a.volatility + 0.01*a.quality + 0.01*a.momentum) for a in assets])
    opt.maximize(score)
    result = opt.check()
    if result != sat:
        return PortfolioSolution("UNSAT", {}, {}, {}, [], ["Z3 reported no satisfying portfolio."], {"backend":"z3"})
    model = opt.model()
    weights: Dict[str,float] = {}
    for t in tickers:
        val = model.eval(w[t], model_completion=True)
        try:
            num = float(val.numerator_as_long())/float(val.denominator_as_long())
        except Exception:
            num = float(str(val))
        if num > 1e-6:
            weights[t] = num
    metrics = summary_metrics(pi, weights)
    shares = {t:int((pi.capital*wt)//amap[t].price) for t,wt in weights.items()}
    report = [f"Z3 found a satisfying portfolio with {len(weights)} assets and Sharpe {metrics['sharpe']:.2f}."]
    return PortfolioSolution("OPTIMAL", weights, shares, metrics, report, [], {"backend":"z3"})
