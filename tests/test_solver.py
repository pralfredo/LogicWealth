from pathlib import Path
from logicwealth.data_loader import load_assets, load_correlations
from logicwealth.dsl.parser import load_constraint_file
from logicwealth.solvers.engine import solve


def test_demo_solves():
    root = Path(__file__).resolve().parents[1]
    pi = load_assets(root/"data"/"sample_assets.csv")
    pi.correlations = load_correlations(root/"data"/"sample_correlations.csv")
    spec = load_constraint_file(root/"examples"/"growth_balanced.yaml")
    sol = solve(pi, spec, backend="greedy")
    assert sol.selected
    assert len(sol.selected) <= spec.cardinality
