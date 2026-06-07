from __future__ import annotations

from logicwealth.models import PortfolioInput, ConstraintSpec, PortfolioSolution


def solve(pi: PortfolioInput, spec: ConstraintSpec, backend: str = "auto") -> PortfolioSolution:
    if backend in {"auto", "z3"}:
        from .z3_backend import solve_z3
        return solve_z3(pi, spec)
    if backend == "greedy":
        from .greedy_backend import solve_greedy
        return solve_greedy(pi, spec)
    raise ValueError(f"Unknown backend: {backend}")
