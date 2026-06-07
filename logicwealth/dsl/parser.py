from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict
from logicwealth.models import ConstraintSpec


def _simple_yaml(text: str) -> Dict[str, Any]:
    """Tiny YAML-ish parser for the bundled examples. Uses PyYAML if available; otherwise JSON."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        # The examples also ship in JSON-compatible form if users remove comments.
        return json.loads(text)


def load_constraint_file(path: str | Path) -> ConstraintSpec:
    data = _simple_yaml(Path(path).read_text())
    return spec_from_dict(data)


def spec_from_dict(data: Dict[str, Any]) -> ConstraintSpec:
    c = data.get("constraints", data)
    spec = ConstraintSpec(raw=data)

    card = c.get("cardinality", {})
    if isinstance(card, dict):
        spec.cardinality = card.get("exactly")
    elif isinstance(card, int):
        spec.cardinality = card

    weights = c.get("weights", {})
    spec.min_weight = float(weights.get("min_if_selected", weights.get("min", 0.0)))
    spec.max_weight = float(weights.get("max_if_selected", weights.get("max", 1.0)))

    for sector, rule in c.get("sectors", {}).items():
        if "max_weight" in rule:
            spec.sector_max[sector] = float(rule["max_weight"])
        if "min_weight" in rule:
            spec.sector_min[sector] = float(rule["min_weight"])

    risk = c.get("risk", {})
    beta = risk.get("beta", {})
    if beta:
        spec.beta_min = float(beta.get("min")) if beta.get("min") is not None else None
        spec.beta_max = float(beta.get("max")) if beta.get("max") is not None else None
    if risk.get("volatility", {}).get("max") is not None:
        spec.volatility_max = float(risk["volatility"]["max"])

    if c.get("turnover", {}).get("max") is not None:
        spec.turnover_max = float(c["turnover"]["max"])
    if c.get("esg", {}).get("min_score") is not None:
        spec.esg_min = float(c["esg"]["min_score"])
    if c.get("liquidity", {}).get("min_average_daily_volume") is not None:
        spec.liquidity_min = float(c["liquidity"]["min_average_daily_volume"])
    if c.get("defensive", {}).get("min_count") is not None:
        spec.defensive_min_count = int(c["defensive"]["min_count"])

    corr = c.get("correlation", {})
    if corr.get("forbid_pair_above") is not None:
        spec.correlation_forbid_above = float(corr["forbid_pair_above"])

    for rule in c.get("logic", []):
        if "if_selected" in rule and "then_not_selected" in rule:
            spec.implications.append((rule["if_selected"], rule["then_not_selected"], False))
        if "if_selected" in rule and "then_selected" in rule:
            spec.implications.append((rule["if_selected"], rule["then_selected"], True))
        if "forbid_pair" in rule:
            a, b = rule["forbid_pair"]
            spec.forbid_pairs.append((a, b, rule.get("reason", "manual exclusion")))
    return spec


def parse_portlogic(text: str) -> ConstraintSpec:
    """A deliberately small line-oriented DSL for demos and tests."""
    spec = ConstraintSpec(raw={"source": "portlogic"})
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"EXACTLY\s+(\d+)\s+ASSETS", line, re.I)
        if m:
            spec.cardinality = int(m.group(1)); continue
        m = re.match(r"WEIGHT\s+BETWEEN\s+([0-9.]+)\s+AND\s+([0-9.]+)", line, re.I)
        if m:
            spec.min_weight=float(m.group(1)); spec.max_weight=float(m.group(2)); continue
        m = re.match(r"SECTOR\s+(.+?)\s+<=\s+([0-9.]+)", line, re.I)
        if m:
            spec.sector_max[m.group(1)] = float(m.group(2)); continue
        m = re.match(r"BETA\s+BETWEEN\s+([0-9.]+)\s+AND\s+([0-9.]+)", line, re.I)
        if m:
            spec.beta_min=float(m.group(1)); spec.beta_max=float(m.group(2)); continue
        m = re.match(r"ESG\s+>=\s+([0-9.]+)", line, re.I)
        if m:
            spec.esg_min=float(m.group(1)); continue
        m = re.match(r"LIQUIDITY\s+>=\s+([0-9.]+)", line, re.I)
        if m:
            spec.liquidity_min=float(m.group(1)); continue
        m = re.match(r"IF\s+SELECTED\((.+?)\)\s+THEN\s+NOT\s+SELECTED\((.+?)\)", line, re.I)
        if m:
            spec.implications.append((m.group(1), m.group(2), False)); continue
        raise ValueError(f"Cannot parse constraint line: {line}")
    return spec
