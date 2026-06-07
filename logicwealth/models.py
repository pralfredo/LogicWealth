from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


@dataclass(frozen=True)
class Asset:
    ticker: str
    sector: str
    industry: str
    price: float
    expected_return: float
    volatility: float
    beta: float
    esg: float
    adv: float
    defensive: bool = False
    quality: float = 0.0
    momentum: float = 0.0


@dataclass
class PortfolioInput:
    capital: float
    assets: List[Asset]
    current_weights: Dict[str, float] = field(default_factory=dict)
    correlations: Dict[Tuple[str, str], float] = field(default_factory=dict)


@dataclass
class PortfolioSolution:
    status: str
    selected: Dict[str, float]
    shares: Dict[str, int]
    metrics: Dict[str, float]
    report: List[str]
    violations: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintSpec:
    cardinality: Optional[int] = None
    min_weight: float = 0.0
    max_weight: float = 1.0
    sector_max: Dict[str, float] = field(default_factory=dict)
    sector_min: Dict[str, float] = field(default_factory=dict)
    beta_min: Optional[float] = None
    beta_max: Optional[float] = None
    volatility_max: Optional[float] = None
    turnover_max: Optional[float] = None
    esg_min: Optional[float] = None
    liquidity_min: Optional[float] = None
    defensive_min_count: Optional[int] = None
    forbid_pairs: List[Tuple[str, str, str]] = field(default_factory=list)  # (a,b,reason)
    implications: List[Tuple[str, str, bool]] = field(default_factory=list)  # if a selected, b selected? bool
    correlation_forbid_above: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict)
