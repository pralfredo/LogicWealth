# LogicWealth: SMT-Based Portfolio Construction Under Real-World Constraints

## Abstract

Real-world portfolio construction is not merely a continuous optimization problem. Institutional mandates impose discrete, conditional, operational, and compliance-driven constraints: exact cardinality, sector limits, ESG screens, turnover caps, liquidity filters, integer lot sizes, factor exposure bounds, and conditional exclusions. LogicWealth models these requirements as a satisfiability modulo theories problem. The system introduces a small portfolio constraint language, compiles investment mandates into solver constraints, optimizes risk-adjusted return, and returns proof-style reports explaining why a portfolio satisfies or violates a given mandate.

## Core contribution

The project demonstrates that formal logic provides a natural representation layer for portfolio construction. Boolean selection variables encode inclusion decisions, real-valued variables encode weights, and integer variables encode shares. Logical implication and exclusion rules encode compliance and mandate-specific conditions. Solver backends then search the feasible region under all rules simultaneously.

## Mathematical formulation

Let `x_i` indicate whether asset `i` is selected, `w_i` its weight, and `q_i` its integer share count. The basic model is:

```text
x_i ∈ {0,1}
w_i ∈ R_≥0
q_i ∈ Z_≥0
Σ_i w_i = 1
```

Selection-weight consistency:

```text
w_i <= w_max x_i
w_i >= w_min x_i
```

Cardinality:

```text
Σ_i x_i = K
```

Sector exposure:

```text
Σ_{i in sector s} w_i <= cap_s
```

Beta bounds:

```text
β_min <= Σ_i β_i w_i <= β_max
```

Forbidden pairs:

```text
x_i + x_j <= 1
```

Conditional mandate:

```text
x_A ⇒ ¬x_B
```

Optimization objective:

```text
maximize μᵀw - λ wᵀΣw - γ transaction_cost(w,w_old)
```

The bundled Z3 backend uses a linearized risk-adjusted objective; a production extension would use MIQP for quadratic covariance risk.

## System architecture

```text
Mandate file / DSL
    ↓
Parser
    ↓
ConstraintSpec AST
    ↓
Solver backend
    ↓
Portfolio solution
    ↓
Constraint report + explanation engine
```

## Evaluation plan

The strongest evaluation would compare LogicWealth against:

1. equal-weight benchmark
2. unconstrained Markowitz portfolio
3. sector-neutral portfolio
4. minimum-variance portfolio
5. classical mean-variance portfolio with relaxed constraints

Metrics:

- annualized return
- volatility
- Sharpe ratio
- beta
- turnover
- transaction cost
- max drawdown
- constraint violations
- solve time
- infeasibility rate

## Why it is graduate-school worthy

The project connects formal methods to applied quantitative decision-making. It contains a formal language, semantics, solver compilation, optimization, and explanation. It can be developed into a research paper on constraint-rich optimization systems, or into an engineering artifact useful for systematic investing and risk management.
