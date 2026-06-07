from __future__ import annotations

import argparse
from logicwealth.data_loader import load_assets, load_correlations
from logicwealth.dsl.parser import load_constraint_file
from logicwealth.solvers.engine import solve
from logicwealth.explain.report import constraint_report, why_not_asset


def main():
    p=argparse.ArgumentParser(description="LogicWealth portfolio constraint solver")
    p.add_argument("--assets", default="data/sample_assets.csv")
    p.add_argument("--constraints", default="examples/growth_balanced.yaml")
    p.add_argument("--correlations", default="data/sample_correlations.csv")
    p.add_argument("--backend", default="auto", choices=["auto","z3","greedy"])
    p.add_argument("--why-not", default=None)
    args=p.parse_args()
    pi=load_assets(args.assets)
    pi.correlations=load_correlations(args.correlations)
    spec=load_constraint_file(args.constraints)
    sol=solve(pi,spec,args.backend)
    print(constraint_report(pi,spec,sol))
    if args.why_not:
        print("\n" + why_not_asset(pi,spec,sol,args.why_not))

if __name__ == "__main__":
    main()
