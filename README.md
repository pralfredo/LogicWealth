# LogicWealth

## SMT-Based Portfolio Construction Under Real-World Constraints

**LogicWealth** is a formal-methods-inspired quantitative finance project for building portfolios under messy, realistic, discrete, conditional, and compliance-heavy constraints. It treats portfolio construction not as a clean textbook optimization problem, but as a formal reasoning problem: a portfolio is acceptable only if it satisfies a set of logical and arithmetic rules, and among the acceptable portfolios the system searches for the best risk-adjusted allocation.

The central idea is simple but powerful: real investment mandates are full of logic. A fund manager does not merely say, “maximize return for a given level of variance.” They say things like: hold exactly thirty securities, keep technology below twenty-five percent, never hold two securities from a restricted pair, maintain beta near one, avoid illiquid names, keep turnover below fifteen percent, include defensive exposure, use integer shares, and explain why a candidate security was excluded. These requirements are not just numerical preferences. They are formal constraints.

LogicWealth converts those requirements into a solver-readable model. It introduces Boolean variables for asset selection, real variables for portfolio weights, integer-like quantities for shares, and implication rules for conditional mandates. The project includes a data model, constraint parser, solver engine, explanation layer, command-line interface, sample asset universe, dashboard mockup, tests, and a research-style project brief. The result is a serious prototype of a system that sits at the intersection of formal logic, satisfiability modulo theories, quantitative finance, optimization, programming language design, and explainable decision systems.

This repository is designed to look and feel like something a strong graduate applicant in logic, computer science, or quantitative finance could present as a flagship project. It is intentionally broader than a small script. It has a research thesis, an engineering architecture, a solver-backed core, an explanation layer, and a clear roadmap for turning the prototype into a deeper research platform.

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Why Logic Belongs in Portfolio Construction](#why-logic-belongs-in-portfolio-construction)
3. [What the System Does](#what-the-system-does)
4. [Core Mathematical Model](#core-mathematical-model)
5. [Constraint Types](#constraint-types)
6. [Solver Architecture](#solver-architecture)
7. [Repository Structure](#repository-structure)
8. [Installation](#installation)
9. [Quick Start](#quick-start)
10. [Example Mandate](#example-mandate)
11. [The PortLogic Design Philosophy](#the-portlogic-design-philosophy)
12. [Explanation and Auditability](#explanation-and-auditability)
13. [Dashboard Concept](#dashboard-concept)
14. [Testing](#testing)
15. [Research Framing](#research-framing)
16. [Roadmap](#roadmap)
17. [Resume and Portfolio Positioning](#resume-and-portfolio-positioning)
18. [Limitations](#limitations)
19. [License and Disclaimer](#license-and-disclaimer)

---

## Project Vision

LogicWealth asks a direct question:

> Can real-world portfolio construction be modeled as a satisfiability and optimization problem, where investment policy, risk management, compliance, and execution constraints are represented as formal logical conditions?

The project starts from the observation that the cleanest mathematical version of portfolio optimization is rarely the version used in practice. Textbook mean-variance optimization assumes a continuous allocation over assets, usually with a small set of elegant constraints. A real portfolio is less elegant. It is constrained by sector rules, liquidity rules, client mandates, turnover limits, tax concerns, position limits, risk budgets, factor exposures, and operational requirements. These rules interact in ways that are naturally logical.

For example, a realistic mandate might say:

```text
Select exactly 30 assets.
Every selected asset must have weight between 1% and 7%.
Technology exposure must be no more than 25%.
Utilities exposure must be at least 4%.
Portfolio beta must remain between 0.80 and 1.15.
No selected asset may have ESG score below 58.
No selected asset may have average daily volume below 8 million shares.
If TSLA is selected, F must not be selected.
No pair of selected assets may have correlation above 0.90.
```

A system that can handle these rules needs more than matrix algebra. It needs a language for constraints, a compiler from that language into solver conditions, and a reporting layer that can explain whether the rules were satisfied. LogicWealth is a prototype of that system.

The long-term vision is an institutional-grade research tool where a user can write an investment policy statement in a structured constraint language, choose a solver backend, run a portfolio optimization, inspect the result, diagnose infeasibility, measure the cost of each constraint, and backtest the mandate across time. The current project implements the foundation and gives a clear path toward that larger system.

---


## Repository Structure

The repository is organized as follows:

```text
LogicWealth/
├── logicwealth/
│   ├── dsl/
│   │   ├── parser.py
│   │   └── __init__.py
│   ├── finance/
│   │   ├── metrics.py
│   │   └── __init__.py
│   ├── solvers/
│   │   ├── engine.py
│   │   ├── greedy_backend.py
│   │   ├── z3_backend.py
│   │   └── __init__.py
│   ├── explain/
│   │   ├── report.py
│   │   └── __init__.py
│   ├── backtest/
│   │   ├── simulator.py
│   │   └── __init__.py
│   ├── api/
│   │   └── app.py
│   ├── data_loader.py
│   ├── models.py
│   └── __init__.py
├── dashboard/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/
│   ├── sample_assets.csv
│   └── sample_correlations.csv
├── examples/
│   ├── growth_balanced.yaml
│   └── portlogic_example.plogic
├── paper/
│   └── LogicWealth_Project_Brief.md
├── tests/
│   ├── test_parser.py
│   └── test_solver.py
├── logicwealth_cli.py
├── requirements.txt
├── pyproject.toml
├── DEMO_OUTPUT.md
└── README.md
```

Each folder has a specific purpose. The `logicwealth` package contains the actual system logic. The `data` folder contains the sample investment universe. The `examples` folder contains mandates and DSL examples. The `dashboard` folder contains a polished static visual demo. The `paper` folder frames the project as a research artifact. The `tests` folder verifies the core parser and solver behavior.

---

## Why Logic Belongs in Portfolio Construction

Classical portfolio optimization is usually introduced through the Markowitz framework. Given expected returns, a covariance matrix, and a risk-aversion parameter, one chooses weights that optimize a risk-return tradeoff. A simplified objective might look like this:

```text
maximize expected_return - lambda * variance
```

with constraints such as:

```text
sum(weights) = 1
weights >= 0
```

This formulation is elegant, but it hides much of the complexity of actual portfolio design. Real mandates often include rules that are conditional, combinatorial, discrete, or categorical. These rules are logical in structure.

A cardinality rule such as “choose exactly 30 assets” requires binary selection variables. A rule such as “if AAPL is selected, then MSFT cannot be selected” is an implication. A rule such as “at least three defensive stocks must be included” is a counting constraint over a category. A rule such as “if volatility is high, reduce maximum equity exposure” is a conditional arithmetic constraint. A rule such as “forbid pairs with correlation above 0.90” is a graph constraint over selected assets.

LogicWealth makes this structure explicit. For each asset `i`, the system can reason with:

```text
x_i ∈ {0,1}       asset selection variable
w_i ∈ R_≥0        portfolio weight variable
q_i ∈ Z_≥0        share quantity variable
```

The Boolean variable `x_i` tells the solver whether asset `i` is included. The weight variable `w_i` tells the solver how much capital is assigned to that asset. The share quantity variable `q_i` supports execution-aware extensions in which the resulting allocation must be translated into integer shares.

Logical constraints become precise formulas. For example:

```text
x_AAPL + x_MSFT <= 1
```

means that AAPL and MSFT cannot both be selected.

```text
x_i = 1 => 0.01 <= w_i <= 0.07
```

means that a selected asset must receive between one and seven percent of the portfolio.

```text
sum(w_i for i in Technology) <= 0.25
```

means that the total technology allocation cannot exceed twenty-five percent.

This is where SAT and SMT become relevant. SAT is designed for Boolean satisfiability. SMT extends satisfiability solving with background theories such as linear arithmetic, integer arithmetic, and real arithmetic. Portfolio construction with selection rules, weight bounds, sector constraints, and conditional requirements naturally lives in this mixed world.

The goal is not to claim that SMT replaces all traditional optimization. In production finance, mixed-integer programming, quadratic programming, and convex optimization remain essential. The point is that a formal logic layer gives a principled way to represent realistic mandates, compile them into multiple solver backends, and explain the resulting decisions.

---

## What the System Does

LogicWealth currently implements a compact but extensible version of the full system. It loads a sample asset universe, reads a portfolio mandate, applies logical and arithmetic constraints, chooses a feasible set of assets, assigns weights, computes risk and portfolio statistics, and generates a readable report.

At a high level, the workflow is:

```text
Asset universe
    ↓
Mandate file
    ↓
Constraint parser
    ↓
Solver backend
    ↓
Portfolio result
    ↓
Risk metrics and explanation report
```

The project supports two styles of constraint definition. The first is a YAML mandate file, which is practical and readable. The second is a small line-oriented DSL concept called PortLogic, included as a design direction and example. The YAML path is currently the main execution path because it is easy to parse and easy to edit.

The system can model constraints such as:

- exact number of selected assets
- minimum and maximum weight for selected positions
- sector exposure caps
- sector exposure floors
- beta lower and upper bounds
- minimum ESG score
- minimum liquidity
- conditional exclusions
- forbidden correlated pairs
- simple objective scoring
- integer share estimation
- why-not explanations for excluded assets

The command-line interface produces a report that includes selected assets, weights, share counts, return estimates, volatility estimates, beta, ESG average, liquidity checks, sector exposures, and detected constraint violations. The explanation layer can also answer why a given asset was not selected, based on the constraints and the chosen portfolio.

This is not intended to be a live trading system. It is a research engineering prototype. The emphasis is on formal modeling, constraint compilation, explainability, and architecture. That makes it suitable as a graduate-school-facing project, because it demonstrates mathematical maturity and systems thinking rather than just API usage.

---

## Core Mathematical Model

Let there be `n` candidate assets in the investment universe. For each asset `i`, LogicWealth associates several quantities:

```text
mu_i       expected return estimate
sigma_i    volatility estimate
beta_i     market beta estimate
sector_i   categorical sector label
esg_i      ESG or quality score
liq_i      average daily liquidity estimate
price_i    current price
```

The decision variables are:

```text
x_i        binary selection variable
w_i        portfolio weight
q_i        share quantity
```

The selection variable is Boolean or binary:

```text
x_i ∈ {0,1}
```

The portfolio weight is nonnegative:

```text
w_i >= 0
```

The portfolio must allocate all available capital:

```text
sum_i w_i = 1
```

The relationship between selection and weight is encoded with lower and upper bounds:

```text
w_i <= max_weight * x_i
w_i >= min_weight * x_i
```

If `x_i = 0`, then `w_i` must be zero. If `x_i = 1`, then `w_i` must lie between the minimum and maximum selected-asset weights.

A cardinality constraint is:

```text
sum_i x_i = K
```

where `K` is the required number of assets.

Sector exposure constraints have the form:

```text
sum_{i in sector S} w_i <= cap_S
sum_{i in sector S} w_i >= floor_S
```

Portfolio beta is computed as a weighted average:

```text
beta_p = sum_i beta_i * w_i
```

with bounds:

```text
beta_min <= beta_p <= beta_max
```

Expected portfolio return is:

```text
R_p = sum_i mu_i * w_i
```

A simple volatility proxy can be computed from weighted asset volatilities, while a more advanced version would use the covariance matrix:

```text
variance_p = w^T Sigma w
```

The current prototype keeps the implementation lightweight, but the architecture is designed so that a mixed-integer quadratic backend can be added later for full covariance-aware optimization.

Conditional rules are encoded as implications. For example:

```text
if selected(TSLA) then not selected(F)
```

can be represented as:

```text
x_TSLA => not x_F
```

or equivalently:

```text
x_TSLA + x_F <= 1
```

Correlation exclusions are represented similarly. If assets `i` and `j` have correlation above a threshold, the system adds:

```text
x_i + x_j <= 1
```

This turns the asset universe into a graph: assets are nodes, forbidden co-holdings are edges, and the solver must choose a feasible independent-like subset while still satisfying financial constraints.

---

## Constraint Types

LogicWealth is organized around the idea that constraints should be explicit, auditable, and extensible. The current prototype supports a focused set of constraints that demonstrate the formal architecture.

### Cardinality

Cardinality controls how many assets are selected. This is common in real portfolios because portfolio managers often want diversification without over-fragmentation.

```yaml
cardinality:
  exactly: 18
```

This is encoded as a sum over binary selection variables.

### Weight Bounds

Weight bounds prevent the optimizer from placing too much or too little capital in a selected asset.

```yaml
weights:
  min_if_selected: 0.025
  max_if_selected: 0.095
```

This prevents tiny meaningless positions and overly concentrated positions.

### Sector Caps and Floors

Sector constraints control diversification across economic categories.

```yaml
sectors:
  Technology:
    max_weight: 0.26
  Healthcare:
    max_weight: 0.22
  Utilities:
    min_weight: 0.04
```

This makes the portfolio more realistic than a pure return optimizer, which might over-concentrate in a high-scoring sector.

### Beta Bounds

Beta constraints control market sensitivity.

```yaml
risk:
  beta:
    min: 0.80
    max: 1.15
```

A portfolio with beta far above one may behave too aggressively relative to the market. A portfolio with beta far below one may not match an equity mandate. The bounds let the user formalize the desired market exposure.

### ESG and Liquidity Screens

ESG and liquidity screens are examples of asset-level filters.

```yaml
esg:
  min_score: 58

liquidity:
  min_average_daily_volume: 8000000
```

The exact interpretation of ESG is deliberately generic in this prototype. It can be replaced by quality score, governance score, compliance score, or any user-defined asset score.

### Conditional Rules

Conditional rules are one of the most logic-centered parts of the project.

```yaml
logic:
  - if_selected: TSLA
    then_not_selected: F
```

This says that if Tesla is selected, Ford cannot be selected. The same pattern could represent compliance rules, correlated business exposure rules, client restrictions, or thematic exclusions.

### Correlation Exclusions

Highly correlated positions can reduce diversification. LogicWealth supports pairwise exclusion above a threshold.

```yaml
correlation:
  forbid_pair_above: 0.90
```

When a pair exceeds the threshold, both cannot be selected simultaneously. This is a discrete diversification rule, not merely a continuous penalty.

### Integer Share Output

The project can translate weights into approximate share quantities given a capital base and price data. This is important because real portfolios are executed in shares, not abstract weights. The current version treats this as a reporting layer, but future versions can make integer shares part of the solver itself.

---

## Solver Architecture

LogicWealth is designed around solver backends. The project currently includes a Z3-oriented backend and a dependency-free greedy backend. The greedy backend exists to make the project runnable even when a user has not installed the optional solver dependencies. The Z3 backend is the more logic-focused component.

The architecture is intentionally modular:

```text
Mandate
  ↓
Parsed constraints
  ↓
Internal portfolio model
  ↓
Backend-specific encoding
  ↓
Solver result
  ↓
Normalized portfolio object
```

A backend receives the asset universe and the parsed mandate. It then constructs a feasible solution according to its own method. The result is normalized into a common portfolio representation so that the reporting layer does not need to know which solver was used.

### Z3 Backend

The Z3 backend represents selection decisions using Boolean variables and expresses constraints through logical and arithmetic formulas. It is the natural home for implication, exclusion, cardinality, and linear arithmetic rules.

The Z3 style is especially useful for future extensions such as:

- named constraints
- unsatisfiable core extraction
- hard and soft constraints
- MaxSMT relaxation
- conditional arithmetic rules
- formal verification of mandate satisfaction

### Greedy Backend

The greedy backend is deliberately simple. It ranks assets using a practical score, filters out assets that violate hard screens, selects a feasible set while respecting major categorical restrictions, and assigns weights in a transparent way. It is not meant to be mathematically optimal. It is meant to provide a robust fallback and a baseline for comparing solver-backed results.

This is useful pedagogically. A strong project should show not only the advanced method, but also the baseline method it improves upon. The greedy backend makes it easy to run the repository immediately, inspect outputs, and test the reporting layer.

### Future Backends

The most ambitious extension is a multi-solver system:

```text
Z3          for SMT and formal logic constraints
OR-Tools    for CP-SAT and combinatorial optimization
Pyomo       for mathematical programming
CVXPY       for continuous relaxations
Gurobi      for production-grade MIQP, if available
SCIP/HiGHS  for open-source optimization paths
```

A serious research version would compare these backends on scalability, solve time, objective quality, and constraint expressiveness. That comparison would make the project much stronger than a single-solver demo.

---

## Installation

Clone or unzip the repository, then enter the project directory:

```bash
cd LogicWealth
```

The project is designed to run with minimal dependencies. For the dependency-free backend, Python is enough for the core demo. For YAML parsing and Z3 support, install the requirements:

```bash
pip install -r requirements.txt
```

The main dependencies are intentionally light:

```text
z3-solver
pyyaml
```

If Z3 is unavailable, use the greedy backend:

```bash
python logicwealth_cli.py --backend greedy
```

If Z3 is installed, use:

```bash
python logicwealth_cli.py --backend z3
```

For development, install test tooling if needed:

```bash
pip install pytest
pytest
```

---

## Quick Start

Run the default optimization using the included sample mandate:

```bash
python logicwealth_cli.py --backend greedy
```

Run with the Z3 backend:

```bash
python logicwealth_cli.py --backend z3
```

Ask why a particular ticker was excluded:

```bash
python logicwealth_cli.py --backend greedy --why-not NVDA
```

Use a specific mandate file:

```bash
python logicwealth_cli.py --mandate examples/growth_balanced.yaml --backend greedy
```

Open the dashboard mockup:

```bash
open dashboard/index.html
```

On Linux, use:

```bash
xdg-open dashboard/index.html
```

On Windows, open the file manually in a browser or use:

```powershell
start dashboard/index.html
```

The expected output is a readable optimization report. It shows the chosen holdings, weights, estimated shares, return and risk summaries, sector exposures, and a constraint audit.

---

## Example Mandate

The included YAML mandate describes a growth-balanced portfolio with sector limits, risk limits, ESG screens, liquidity filters, logical exclusions, and correlation restrictions.

```yaml
universe: sample_large_cap
capital: 1000000
rebalance_frequency: monthly

objective:
  type: score
  return_weight: 0.55
  risk_weight: 0.25
  esg_weight: 0.10
  liquidity_weight: 0.10

constraints:
  cardinality:
    exactly: 18

  weights:
    min_if_selected: 0.025
    max_if_selected: 0.095

  sectors:
    Technology:
      max_weight: 0.26
    Healthcare:
      max_weight: 0.22
    Utilities:
      min_weight: 0.04

  risk:
    beta:
      min: 0.80
      max: 1.15

  liquidity:
    min_average_daily_volume: 8000000

  esg:
    min_score: 58

  logic:
    - if_selected: TSLA
      then_not_selected: F

  correlation:
    forbid_pair_above: 0.90
```

This mandate is intentionally realistic. It does not merely optimize a score. It forces the optimizer to respect structural rules that resemble an investment policy statement.

---

## The PortLogic Design Philosophy

The project includes a prototype DSL concept called PortLogic. The point of PortLogic is to make investment constraints look like a small formal language rather than scattered Python conditionals.

A possible PortLogic file might look like this:

```text
portfolio GrowthBalanced:
    universe sample_large_cap
    capital 1000000

    objective maximize score

    exactly 18 assets
    selected weight between 0.025 and 0.095
    sector Technology max 0.26
    sector Healthcare max 0.22
    sector Utilities min 0.04
    beta between 0.80 and 1.15
    esg at least 58
    liquidity at least 8000000
    if selected TSLA then not selected F
    forbid pair if correlation above 0.90
```

The long-term purpose of this DSL is to support a formal compiler pipeline:

```text
Text constraint
  ↓
Lexer
  ↓
Parser
  ↓
Abstract syntax tree
  ↓
Type checker
  ↓
Constraint normalizer
  ↓
Solver encoding
  ↓
Result explanation
```

This is what makes LogicWealth more than a finance script. It becomes a programming languages and formal methods project. The user writes rules in a domain-specific language; the system interprets those rules as mathematical formulas; the solver checks satisfiability and searches for a good portfolio.

A strong future version should define a formal grammar and semantics. For example:

```text
Constraint ::= Cardinality | WeightBound | SectorRule | RiskRule | Implication | PairExclusion
Implication ::= IF Condition THEN Constraint
Condition ::= Selected(Ticker) | Metric Comparator Value
```

The denotational semantics would map each syntactic construct to a formula over decision variables. That gives the project academic depth and makes it suitable for a research-style writeup.

---

## Explanation and Auditability

One of the most important design goals is explainability. A portfolio optimizer that returns a list of weights is not enough. A serious constraint solver should explain why the solution is feasible, why certain assets were selected, and why others were excluded.

LogicWealth’s reporting layer produces a constraint satisfaction audit. A typical report includes checks such as:

```text
[✓] Exactly 18 assets selected
[✓] Every selected asset satisfies ESG minimum
[✓] Every selected asset satisfies liquidity minimum
[✓] Technology exposure is below the cap
[✓] Healthcare exposure is below the cap
[✓] Utilities exposure is above the floor
[✓] Portfolio beta lies within the target interval
[✓] Forbidden conditional pair rule satisfied
[✓] Correlation exclusion rule satisfied
```

This audit matters because a quant system should not only optimize; it should be inspectable. In institutional settings, a portfolio decision may need to be justified to risk managers, compliance officers, clients, or future researchers. A formal report gives the system credibility.

The `--why-not` feature is an early version of local explanation. For example:

```bash
python logicwealth_cli.py --backend greedy --why-not NVDA
```

The system can explain whether the asset was excluded because of score ranking, sector pressure, risk limits, ESG, liquidity, correlation rules, or conditional conflicts. A future version should make this deeper by computing counterfactual explanations:

```text
NVDA was not selected because including it would have forced Technology exposure above 26% unless another Technology position was removed. It was also involved in a correlation conflict with AMD under the 0.90 threshold.
```

The most ambitious explanation feature is an infeasibility debugger. If the mandate is impossible, the system should not merely return `UNSAT`. It should identify a small conflicting set of constraints. For example:

```text
No feasible portfolio found.

Minimal conflicting set:
1. exactly 30 assets
2. ESG score at least 90
3. liquidity at least 100,000,000
4. volatility below 10%

Only 12 assets satisfy constraints 2-4, but the mandate requires 30.
```

Z3 supports named constraints and unsat-core extraction, which makes this a natural next step. A MaxSMT version could go further by suggesting the smallest relaxation required to restore feasibility.

---

## Dashboard Concept

The included dashboard is a static visual prototype. Its purpose is to show how LogicWealth could look as a polished quant terminal. A production dashboard would connect to the solver API, allow live mandate editing, and render portfolio diagnostics interactively.

A strong dashboard should include several panels:

### Portfolio Composition

This panel shows selected assets, weights, share counts, sectors, and scores. It should make the final allocation easy to inspect.

### Constraint Satisfaction

This panel shows each rule with a pass or fail marker. It should be possible to click a constraint and see the mathematical expression behind it.

### Sector Exposure

This panel shows sector weights relative to caps and floors. A cap should be visually distinct from an actual exposure.

### Risk Summary

This panel shows expected return, volatility, beta, Sharpe-like score, ESG average, liquidity, and turnover.

### Forbidden-Pair Graph

This would be the most visually distinctive feature. Assets are nodes. Correlation or compliance conflicts are edges. Selected assets glow. Forbidden co-holdings are visible as a graph. This makes the logic structure of the portfolio visible.

### Efficient Frontier

A future dashboard should compare the unconstrained efficient frontier with the constrained frontier. This would show the cost of real-world rules.

### Infeasibility View

If the mandate is impossible, the dashboard should show conflicting constraints as a graph or dependency tree. This would turn a technical solver failure into an understandable diagnostic.

The aesthetic direction should be serious rather than gimmicky: dark glass panels, precise typography, clean charts, strong spacing, and high-contrast constraint states. The project should feel like a formal quant terminal, not a trading-game UI.

---

## Testing

The repository includes tests for the parser and solver behavior. Run them with:

```bash
pytest
```

Testing is important because constraint systems can fail silently if a rule is encoded incorrectly. For example, a sector cap written with the wrong inequality could produce portfolios that look reasonable but violate the mandate. A serious solver project needs tests for each constraint type.

Recommended future tests include:

- parser tests for every DSL construct
- YAML validation tests
- sector cap tests
- sector floor tests
- cardinality tests
- beta bound tests
- ESG and liquidity screen tests
- implication rule tests
- correlation exclusion tests
- infeasible mandate tests
- solver equivalence tests across backends
- regression tests for known mandates
- property-based tests generating random feasible and infeasible universes

A strong property-based test would randomly generate small asset universes and random constraints, then verify that the returned portfolio satisfies every encoded rule. This is particularly appropriate because the project is about formal correctness.

---

## Research Framing

LogicWealth can be framed as a research project in several ways.

### Formal Methods for Finance

The central framing is that investment mandates are formal specifications. A portfolio is a model of the specification if it satisfies all constraints. This mirrors the logic relation between formulas and models.

```text
Portfolio P satisfies mandate M
```

can be written conceptually as:

```text
P ⊨ M
```

The solver searches for a portfolio `P` such that the mandate is true, and then optimizes an objective over the satisfying portfolios.

### Constraint-Rich Optimization

The project also fits into constraint-rich optimization. The key problem is not just continuous risk-return optimization; it is optimization under a mixture of Boolean, integer, categorical, and real-valued constraints.

### Explainable Quantitative Systems

LogicWealth is interpretable by design. The constraints are explicit, the solution can be audited, and excluded assets can be explained. This contrasts with black-box portfolio systems where the reason for a weight may be opaque.

### Programming Languages for Finance

The DSL direction makes the project relevant to programming languages. An investment policy statement becomes a formal program. The compiler translates that program into solver constraints. The type checker can catch malformed rules before optimization.

### Solver Benchmarking

A mature research version would compare Z3, OR-Tools, Pyomo, CVXPY, and other backends. The comparison could measure expressiveness, speed, scalability, objective quality, and diagnostic capability.

A possible paper title:

> LogicWealth: A Domain-Specific Constraint Language and SMT Framework for Real-World Portfolio Construction

A possible abstract:

> Portfolio construction in practice involves discrete, conditional, and compliance-oriented constraints that are difficult to represent in standard continuous optimization frameworks. LogicWealth models investment mandates as formal logical and arithmetic specifications, compiles them into solver backends, and produces auditable portfolios with explanation reports. We demonstrate the approach on a constraint-rich equity universe involving cardinality, sector exposure, beta, ESG, liquidity, correlation, and conditional exclusion rules. The project shows how satisfiability modulo theories and domain-specific language design can make portfolio construction more expressive, inspectable, and formally grounded.

---

## Roadmap

LogicWealth is intentionally built as a prototype with a clear path toward a more ambitious system.

### Phase 1: Harden the Current Core

- improve YAML validation
- add clearer error messages
- strengthen solver tests
- separate hard constraints from scoring preferences
- improve weight assignment logic
- make reports exportable as Markdown and JSON

### Phase 2: Real SMT Diagnostics

- name every constraint
- use Z3 unsat cores
- display minimal conflicting rule sets
- implement infeasibility explanations
- add counterfactual why-not explanations

### Phase 3: Soft Constraints and MaxSMT

- allow constraints to be marked hard or soft
- assign penalties to soft constraints
- minimize total violation cost
- suggest mandate relaxations
- display the cost of each relaxation

### Phase 4: Production-Grade Optimization

- add OR-Tools CP-SAT backend
- add Pyomo backend
- add CVXPY continuous relaxation backend
- add MIQP support for covariance-aware variance minimization
- compare solve time and solution quality across backends

### Phase 5: Backtesting Lab

- monthly rebalancing
- transaction cost model
- turnover constraints over time
- benchmark comparisons
- drawdown analysis
- rolling beta and volatility
- constraint violation audit across time

### Phase 6: Factor Model

- add market, size, value, momentum, quality, and low-volatility exposures
- support factor exposure caps and floors
- add factor-neutral mandates
- compute tracking error against a benchmark

### Phase 7: Tax-Aware Rebalancing

- add tax lots
- model realized gains and losses
- constrain short-term gains
- support wash-sale-aware logic
- optimize after-tax outcomes

### Phase 8: Interactive Dashboard

- live constraint editor
- solver API integration
- portfolio visualization
- forbidden-pair graph
- efficient frontier comparison
- infeasibility graph
- report export

### Phase 9: Natural Language to Constraints

- parse investment policy statements
- translate natural language into PortLogic
- show the generated formal constraints
- require user approval before solving

This roadmap is ambitious but coherent. Each phase builds on the existing architecture rather than replacing it.

---

## Resume and Portfolio Positioning

LogicWealth is especially strong because it can be presented differently depending on the audience.

For a quant audience:

> Built a constraint-rich portfolio optimization engine combining risk-adjusted scoring with cardinality, sector exposure, beta, ESG, liquidity, correlation, and conditional compliance constraints; generated auditable allocation reports and explainable exclusion diagnostics.

For a formal methods audience:

> Designed an SMT-inspired portfolio construction system that represents investment mandates as Boolean and arithmetic formulas over asset-selection and weight variables, with a roadmap toward unsat-core diagnostics and MaxSMT relaxation.

For a programming languages audience:

> Prototyped a domain-specific language for portfolio mandates, compiling human-readable investment constraints into solver-ready representations through a parser, internal constraint model, and backend abstraction.

For a software engineering audience:

> Developed a modular Python package with solver backends, financial metrics, report generation, sample data, tests, CLI tooling, and dashboard prototype for explainable portfolio construction.

A concise resume bullet:

> Built LogicWealth, an SMT-inspired portfolio construction engine that compiles real-world investment constraints into solver models, supporting cardinality limits, sector caps, ESG/liquidity screens, beta bounds, correlation exclusions, conditional rules, integer share reports, and explainable optimization audits.

A more ambitious resume bullet:

> Designed and implemented a formal constraint framework for portfolio optimization, combining a DSL-style mandate representation, Z3-based logical encoding, fallback heuristic solver, risk metric engine, why-not explanations, and dashboard prototype for auditable quant portfolio construction.

A graduate-school project description:

> LogicWealth investigates how formal logic and satisfiability modulo theories can represent realistic portfolio mandates that combine Boolean selection, arithmetic risk bounds, categorical diversification rules, and conditional compliance constraints. The system treats a portfolio as a model of an investment specification and produces auditable allocations with solver-backed constraint satisfaction reports.

---

## Limitations

LogicWealth is a prototype, not a production trading system. It should not be used to make real investment decisions. The sample data is simplified, the expected return estimates are illustrative, and the current optimizer is designed for demonstration rather than institutional execution.

Important limitations include:

- expected return estimation is not robust enough for real capital allocation
- covariance-aware quadratic optimization is not fully implemented in the core backend
- integer shares are currently more of a reporting feature than a hard solver constraint
- transaction costs and turnover are not yet fully integrated into the optimization loop
- tax-lot modeling is only a roadmap item
- ESG scores in the sample data are illustrative
- dashboard is a static prototype rather than a live application
- solver scalability has not yet been benchmarked on large universes

These limitations are not weaknesses if they are presented honestly. They define the research frontier of the project. The valuable contribution is the architecture and formal framing: portfolio construction as satisfaction and optimization under explicit logical constraints.

---

## License and Disclaimer

This project is for educational and research purposes. It is not financial advice, investment advice, or a recommendation to buy or sell any security. The included data is sample data intended to demonstrate software architecture and formal modeling techniques. Any real investment use would require validated data, robust risk modeling, production-grade optimization, compliance review, and professional judgment.

---

## Closing Summary

LogicWealth is a portfolio construction system built around a formal idea: an investment mandate is a specification, and a portfolio is valid only if it satisfies that specification. By combining Boolean selection variables, arithmetic weight constraints, categorical exposure rules, conditional implications, solver backends, and explanation reports, the project demonstrates how logic can make quantitative finance more expressive and auditable.

The strongest version of this project is not merely an optimizer. It is a small formal language, a solver compiler, a risk engine, an explanation system, and a research platform. That combination makes it suitable for a serious portfolio, a graduate-school application, or a technically ambitious quant-facing project.

LogicWealth is therefore best understood as a bridge between three worlds:

```text
Formal logic          → constraints, implication, satisfiability
Quantitative finance  → portfolios, risk, diversification, mandates
Software engineering  → parsers, APIs, dashboards, tests, reports
```

That is the project’s identity: rigorous enough for logic, practical enough for quant finance, and polished enough to present as a flagship engineering artifact.

---

## Live Website Dashboard

LogicWealth now includes a live local website connected to the Python solver through FastAPI.

### Start the website

```bash
cd LogicWealth
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn logicwealth.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The dashboard supports live constraint editing, backend selection, portfolio solving, holdings display, sector exposure visualization, constraint certificates, why-not explanations, and asset-universe search.

### API endpoints

```text
GET  /api/health
GET  /api/assets
POST /api/solve
```

The static frontend files live in `dashboard/`. The backend app lives in `logicwealth/api/app.py`.
