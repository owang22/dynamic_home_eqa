# Value-of-information policies on the representative grid

Inputs: the 10 test households of `results/conformal_sweep_v2/` (split seed 0), budgets 24 and 90 senses per day, beliefs LastObservation, PeriodicPersistence, PerpetuaStar. VoIThresholdSense senses the argmax-voi receptacle while max voi >= lambda (`policies/voi_sense.py`; one-step lookahead, arithmetic on the belief's distribution), in fixed-budget mode (the cap binds) and soft-budget mode (cap disabled; the price alone sets the spend). VoIBudgetPriceSense starts at lambda 0.05 and moves it by gamma * (spend rate - budget rate) after every question, clipped to [0.001, 0.5]. Comparators: ResolvableMassSense and ConformalSense(global) at the reference sweep's best configuration for that belief and budget (`comparators.json`; a belief the reference sweep did not run gets the configuration most of its beliefs preferred at that budget, marked 'consensus' below). Produced by `python -m baselines.voi_study`; per-day accuracy per cell in `accuracy_by_day.csv`. Every cell is 22 500 questions, so the 95% Wilson interval on an accuracy is about +/-0.006 and differences below about 0.01 are noise; the tables below are raw numbers, the figures carry the intervals. Figures: `frontier.png` (accuracy against cost per belief and budget, with the cap-removed price frontier) and `budget_reallocation.png` (senses per question by how sure the belief was before sensing).

- LLMBelief cells skipped: the cached completions leave 49%-58% of a passive replay's queried predictions unanswered per test household, and sensing changes the prompts further; every cell would need new LLM calls.
- OracleBelief cells not run: the oracle-posterior study stopped at its ESS gate (fleet median ESS 1.00; `results/oracle_program_posterior/`).

## 1. VoI policies against the two comparators, per (belief, budget)

Task accuracy (senses per question); delta = VoI policy minus comparator, raw.

### LastObservation, budget 24

Comparators: ResolvableMassSense(alpha=0.3,tau=0.8,global) 0.655 (0.24 senses/q); ConformalSense(alpha=0.4,global) 0.654 (0.24). NeverSense 0.587, SequentialSearch 0.642 (0.27).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.650 | 0.25 | -0.005 | -0.004 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.649 | 0.25 | -0.006 | -0.005 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.650 | 0.25 | -0.005 | -0.004 |
| VoIThresholdSense(lambda=0.01) | 0.631 | 0.20 | -0.024 | -0.023 |
| VoIThresholdSense(lambda=0.02) | 0.623 | 0.14 | -0.033 | -0.031 |
| VoIThresholdSense(lambda=0.05) | 0.596 | 0.04 | -0.059 | -0.058 |
| VoIThresholdSense(lambda=0.1) | 0.587 | 0.00 | -0.068 | -0.066 |
| VoIThresholdSense(lambda=0.2) | 0.587 | 0.00 | -0.068 | -0.067 |
| VoIThresholdSense(lambda=0.3) | 0.587 | 0.00 | -0.068 | -0.067 |

### LastObservation, budget 90

Comparators: ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.806 (0.78 senses/q); ConformalSense(alpha=0.5,global) 0.784 (0.70). NeverSense 0.587, SequentialSearch 0.706 (1.00).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.704 | 0.83 | -0.102 | -0.080 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.705 | 0.81 | -0.101 | -0.080 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.705 | 0.82 | -0.100 | -0.079 |
| VoIThresholdSense(lambda=0.01) | 0.677 | 0.59 | -0.129 | -0.108 |
| VoIThresholdSense(lambda=0.02) | 0.647 | 0.25 | -0.159 | -0.138 |
| VoIThresholdSense(lambda=0.05) | 0.597 | 0.04 | -0.209 | -0.188 |
| VoIThresholdSense(lambda=0.1) | 0.587 | 0.00 | -0.218 | -0.197 |
| VoIThresholdSense(lambda=0.2) | 0.587 | 0.00 | -0.219 | -0.197 |
| VoIThresholdSense(lambda=0.3) | 0.587 | 0.00 | -0.219 | -0.198 |

### LastObservation, soft budget (cap disabled)

| lambda | accuracy | senses/q | senses/day |
|---|---|---|---|
| 0.2 | 0.587 | 0.00 | 0.0 |
| 0.3 | 0.587 | 0.00 | 0.0 |
| 0.1 | 0.587 | 0.00 | 0.1 |
| 0.05 | 0.597 | 0.04 | 3.7 |
| 0.02 | 0.653 | 0.27 | 24.4 |
| 0.01 | 0.746 | 1.22 | 110.2 |

### PeriodicPersistence, budget 24

Comparators: ResolvableMassSense(alpha=0.3,tau=0.4,global) 0.690 (0.21 senses/q); ConformalSense(alpha=0.3,global) 0.688 (0.22). NeverSense 0.592, SequentialSearch 0.654 (0.27).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.666 | 0.26 | -0.024 | -0.022 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.665 | 0.26 | -0.025 | -0.023 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.668 | 0.26 | -0.022 | -0.020 |
| VoIThresholdSense(lambda=0.01) | 0.665 | 0.27 | -0.025 | -0.023 |
| VoIThresholdSense(lambda=0.02) | 0.669 | 0.27 | -0.022 | -0.020 |
| VoIThresholdSense(lambda=0.05) | 0.681 | 0.24 | -0.009 | -0.007 |
| VoIThresholdSense(lambda=0.1) | 0.675 | 0.15 | -0.015 | -0.013 |
| VoIThresholdSense(lambda=0.2) | 0.641 | 0.08 | -0.050 | -0.048 |
| VoIThresholdSense(lambda=0.3) | 0.616 | 0.04 | -0.075 | -0.072 |

### PeriodicPersistence, budget 90

Comparators: ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.853 (0.96 senses/q); ConformalSense(alpha=0.5,global) 0.848 (0.70). NeverSense 0.592, SequentialSearch 0.720 (1.00).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.739 | 0.97 | -0.114 | -0.109 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.751 | 0.98 | -0.102 | -0.098 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.752 | 0.98 | -0.101 | -0.096 |
| VoIThresholdSense(lambda=0.01) | 0.752 | 0.94 | -0.101 | -0.097 |
| VoIThresholdSense(lambda=0.02) | 0.776 | 0.85 | -0.076 | -0.072 |
| VoIThresholdSense(lambda=0.05) | 0.744 | 0.42 | -0.109 | -0.105 |
| VoIThresholdSense(lambda=0.1) | 0.676 | 0.15 | -0.177 | -0.173 |
| VoIThresholdSense(lambda=0.2) | 0.641 | 0.08 | -0.212 | -0.208 |
| VoIThresholdSense(lambda=0.3) | 0.616 | 0.04 | -0.237 | -0.232 |

### PeriodicPersistence, soft budget (cap disabled)

| lambda | accuracy | senses/q | senses/day |
|---|---|---|---|
| 0.3 | 0.616 | 0.04 | 3.3 |
| 0.2 | 0.641 | 0.08 | 6.9 |
| 0.1 | 0.676 | 0.15 | 13.9 |
| 0.05 | 0.745 | 0.43 | 38.4 |
| 0.02 | 0.872 | 1.36 | 122.5 |
| 0.01 | 0.929 | 2.56 | 230.5 |

### PerpetuaStar, budget 24 (consensus config)

Comparators: ResolvableMassSense(alpha=0.3,tau=0.4,global) 0.617 (0.27 senses/q); ConformalSense(alpha=0.3,global) 0.622 (0.27). NeverSense 0.532, SequentialSearch 0.601 (0.27).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.631 | 0.26 | +0.014 | +0.009 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.621 | 0.26 | +0.004 | -0.001 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.626 | 0.26 | +0.009 | +0.004 |
| VoIThresholdSense(lambda=0.01) | 0.596 | 0.27 | -0.021 | -0.027 |
| VoIThresholdSense(lambda=0.02) | 0.598 | 0.27 | -0.019 | -0.024 |
| VoIThresholdSense(lambda=0.05) | 0.610 | 0.27 | -0.007 | -0.012 |
| VoIThresholdSense(lambda=0.1) | 0.613 | 0.27 | -0.004 | -0.009 |
| VoIThresholdSense(lambda=0.2) | 0.631 | 0.26 | +0.014 | +0.009 |
| VoIThresholdSense(lambda=0.3) | 0.623 | 0.16 | +0.006 | +0.001 |

### PerpetuaStar, budget 90 (consensus config)

Comparators: ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.681 (0.99 senses/q); ConformalSense(alpha=0.5,global) 0.642 (0.23). NeverSense 0.532, SequentialSearch 0.644 (1.00).

| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |
|---|---|---|---|---|
| VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) | 0.700 | 0.99 | +0.019 | +0.058 |
| VoIBudgetPriceSense(gamma=0.05,lambda0=0.05) | 0.705 | 0.99 | +0.025 | +0.064 |
| VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 0.706 | 0.99 | +0.025 | +0.064 |
| VoIThresholdSense(lambda=0.01) | 0.698 | 0.98 | +0.018 | +0.057 |
| VoIThresholdSense(lambda=0.02) | 0.709 | 0.96 | +0.029 | +0.068 |
| VoIThresholdSense(lambda=0.05) | 0.719 | 0.84 | +0.038 | +0.077 |
| VoIThresholdSense(lambda=0.1) | 0.710 | 0.65 | +0.030 | +0.069 |
| VoIThresholdSense(lambda=0.2) | 0.669 | 0.34 | -0.011 | +0.028 |
| VoIThresholdSense(lambda=0.3) | 0.623 | 0.16 | -0.057 | -0.018 |

### PerpetuaStar, soft budget (cap disabled)

| lambda | accuracy | senses/q | senses/day |
|---|---|---|---|
| 0.3 | 0.623 | 0.16 | 14.5 |
| 0.2 | 0.669 | 0.34 | 30.7 |
| 0.1 | 0.712 | 0.65 | 58.9 |
| 0.05 | 0.733 | 0.92 | 82.4 |
| 0.02 | 0.750 | 1.17 | 105.4 |
| 0.01 | 0.757 | 1.31 | 117.8 |

### Summary: best VoI policy per cell vs the better comparator

| belief | budget | best VoI (accuracy, senses/q) | better comparator | delta |
|---|---|---|---|---|
| LastObservation | 24 | VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) (0.650, 0.25) | ResolvableMassSense(alpha=0.3,tau=0.8,global) (0.655, 0.24) | -0.005 |
| LastObservation | 90 | VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) (0.705, 0.82) | ResolvableMassSense(alpha=0.2,tau=0.6,global) (0.806, 0.78) | -0.100 |
| PeriodicPersistence | 24 | VoIThresholdSense(lambda=0.05) (0.681, 0.24) | ResolvableMassSense(alpha=0.3,tau=0.4,global) (0.690, 0.21) | -0.009 |
| PeriodicPersistence | 90 | VoIThresholdSense(lambda=0.02) (0.776, 0.85) | ResolvableMassSense(alpha=0.2,tau=0.6,global) (0.853, 0.96) | -0.076 |
| PerpetuaStar | 24 | VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) (0.631, 0.26) | ConformalSense(alpha=0.3,global) (0.622, 0.27) | +0.009 |
| PerpetuaStar | 90 | VoIThresholdSense(lambda=0.05) (0.719, 0.84) | ResolvableMassSense(alpha=0.2,tau=0.6,global) (0.681, 0.99) | +0.038 |

## 2. Does VoIBudgetPriceSense move budget toward hard questions?

Senses per question by the belief's confidence at the question's first decision (max p before any sense), VoIBudgetPriceSense (gamma 0.05) against SequentialSearch's flat spending, with accuracy in the bin. n per bin in parentheses.

### LastObservation, budget 24

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 84 | 2.24 (0.190) | 4.66 (0.338) |
| [0.5, 0.8) | 295 | 0.67 (0.119) | 2.37 (0.200) |
| [0.8, 0.95) | 1221 | 0.23 (0.195) | 1.37 (0.241) |
| [0.95, 1] | 20900 | 0.26 (0.677) | 0.16 (0.675) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 8.77, VoIBudgetPrice 30.03.

### LastObservation, budget 90

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 91 | 10.80 (0.637) | 13.00 (0.716) |
| [0.5, 0.8) | 263 | 7.72 (0.490) | 11.21 (0.762) |
| [0.8, 0.95) | 1124 | 3.50 (0.319) | 8.06 (0.512) |
| [0.95, 1] | 21022 | 0.74 (0.729) | 0.33 (0.713) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 14.61, VoIBudgetPrice 39.36.

### PeriodicPersistence, budget 24

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 282 | 0.92 (0.220) | 1.58 (0.302) |
| [0.5, 0.8) | 2007 | 0.43 (0.333) | 0.70 (0.369) |
| [0.8, 0.95) | 4070 | 0.29 (0.487) | 0.45 (0.509) |
| [0.95, 1] | 16141 | 0.23 (0.744) | 0.14 (0.746) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 4.01, VoIBudgetPrice 11.47.

### PeriodicPersistence, budget 90

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 232 | 4.05 (0.474) | 4.55 (0.576) |
| [0.5, 0.8) | 1833 | 1.99 (0.399) | 2.55 (0.494) |
| [0.8, 0.95) | 4081 | 1.40 (0.498) | 2.03 (0.576) |
| [0.95, 1] | 16354 | 0.74 (0.815) | 0.48 (0.826) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 5.44, VoIBudgetPrice 9.44.

### PerpetuaStar, budget 24

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 2782 | 0.29 (0.343) | 0.87 (0.382) |
| [0.5, 0.8) | 7708 | 0.26 (0.508) | 0.48 (0.539) |
| [0.8, 0.95) | 6110 | 0.21 (0.690) | 0.08 (0.686) |
| [0.95, 1] | 5900 | 0.33 (0.752) | 0.02 (0.720) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 0.88, VoIBudgetPrice 43.93.

### PerpetuaStar, budget 90

| first-decision confidence | n | SequentialSearch senses/q (acc) | VoIBudgetPrice senses/q (acc) |
|---|---|---|---|
| [0, 0.5) | 3283 | 0.95 (0.336) | 1.81 (0.413) |
| [0.5, 0.8) | 7222 | 0.98 (0.538) | 1.34 (0.565) |
| [0.8, 0.95) | 5864 | 0.92 (0.774) | 1.05 (0.805) |
| [0.95, 1] | 6131 | 1.13 (0.809) | 0.46 (0.796) |

Hard-to-easy spend ratio (bin [0, 0.5) over bin [0.95, 1]): SequentialSearch 0.84, VoIBudgetPrice 3.94.

## 3. On OracleBelief, do VoI policies reach the ceiling with fewer senses?

Not answerable: OracleBelief is not in this grid (the oracle-posterior study stopped at its ESS gate, `results/oracle_program_posterior/findings.md`).


## Summary

Against the better of the two comparators in each cell, at the 0.01 resolution 22 500 questions support:

- **VoI ahead**: PerpetuaStar at 90/day (+0.038: VoIThresholdSense(lambda=0.05) 0.719 at 0.84 senses/q vs ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.681 at 0.99).
- **VoI behind**: LastObservation at 90/day (-0.100: VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) 0.705 at 0.82 senses/q vs ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.806 at 0.78); PeriodicPersistence at 90/day (-0.076: VoIThresholdSense(lambda=0.02) 0.776 at 0.85 senses/q vs ResolvableMassSense(alpha=0.2,tau=0.6,global) 0.853 at 0.96).
- **within noise**: LastObservation at 24/day (-0.005: VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) 0.650 at 0.25 senses/q vs ResolvableMassSense(alpha=0.3,tau=0.8,global) 0.655 at 0.24); PeriodicPersistence at 24/day (-0.009: VoIThresholdSense(lambda=0.05) 0.681 at 0.24 senses/q vs ResolvableMassSense(alpha=0.3,tau=0.4,global) 0.690 at 0.21); PerpetuaStar at 24/day (+0.009: VoIBudgetPriceSense(gamma=0.01,lambda0=0.05) 0.631 at 0.26 senses/q vs ConformalSense(alpha=0.3,global) 0.622 at 0.27).
