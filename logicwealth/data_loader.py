from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Tuple
from .models import Asset, PortfolioInput


def load_assets(path: str | Path, capital: float = 1_000_000) -> PortfolioInput:
    assets = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assets.append(Asset(
                ticker=row["ticker"],
                sector=row["sector"],
                industry=row.get("industry", ""),
                price=float(row["price"]),
                expected_return=float(row["expected_return"]),
                volatility=float(row["volatility"]),
                beta=float(row["beta"]),
                esg=float(row["esg"]),
                adv=float(row["adv"]),
                defensive=row.get("defensive", "false").lower() in {"1", "true", "yes"},
                quality=float(row.get("quality", 0.0)),
                momentum=float(row.get("momentum", 0.0)),
            ))
    return PortfolioInput(capital=capital, assets=assets)


def load_correlations(path: str | Path) -> Dict[Tuple[str, str], float]:
    corr = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a, b = row["a"], row["b"]
            corr[tuple(sorted((a, b)))] = float(row["correlation"])
    return corr
