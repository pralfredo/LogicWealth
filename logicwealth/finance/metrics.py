from __future__ import annotations

from typing import Dict, Iterable, Tuple
from logicwealth.models import Asset, PortfolioInput


def weighted(weights: Dict[str, float], assets: Iterable[Asset], field: str) -> float:
    amap = {a.ticker: a for a in assets}
    return sum(weights.get(t, 0.0) * getattr(amap[t], field) for t in weights if t in amap)


def sector_weights(weights: Dict[str, float], assets: Iterable[Asset]) -> Dict[str, float]:
    amap = {a.ticker: a for a in assets}
    out: Dict[str, float] = {}
    for t, w in weights.items():
        if t in amap:
            out[amap[t].sector] = out.get(amap[t].sector, 0.0) + w
    return out


def turnover(new: Dict[str, float], old: Dict[str, float]) -> float:
    keys = set(new) | set(old)
    return sum(abs(new.get(k, 0.0) - old.get(k, 0.0)) for k in keys)


def proxy_variance(weights: Dict[str, float], assets: Iterable[Asset], correlations: Dict[Tuple[str,str], float]) -> float:
    amap = {a.ticker: a for a in assets}
    tickers = list(weights)
    var = 0.0
    for i, a in enumerate(tickers):
        for j, b in enumerate(tickers):
            corr = 1.0 if a == b else correlations.get(tuple(sorted((a,b))), 0.25)
            var += weights[a]*weights[b]*amap[a].volatility*amap[b].volatility*corr
    return var


def summary_metrics(pi: PortfolioInput, weights: Dict[str, float]) -> Dict[str, float]:
    var = proxy_variance(weights, pi.assets, pi.correlations)
    vol = var ** 0.5
    ret = weighted(weights, pi.assets, "expected_return")
    beta = weighted(weights, pi.assets, "beta")
    esg = weighted(weights, pi.assets, "esg")
    sharpe = ret / vol if vol else 0.0
    return {
        "expected_return": ret,
        "volatility": vol,
        "beta": beta,
        "esg": esg,
        "sharpe": sharpe,
        "turnover": turnover(weights, pi.current_weights),
    }
