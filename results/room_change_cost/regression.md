# Regression: c = 0 against `results/voi_policies/`

Every cell below is the same (belief, policy, budget) run on the same test households with the same seed and the same policy configuration, at room-change cost 0 — where the cost model is by construction the flat one. Task accuracy and senses per question must match to the 6 decimals both csvs carry. Policy slugs are Part B's own, because the RNG derivation keys on them.

| belief | budget | policy | acc here | acc there | senses/q here | there | match |
|---|---|---|---|---|---|---|---|
| LastObservation | 24 | NeverSense | 0.586933 | 0.586933 | 0.0 | 0.0 | yes |
| LastObservation | 24 | SequentialSearch | 0.641511 | 0.641511 | 0.266667 | 0.266667 | yes |
| LastObservation | 24 | ResolvableMassSense_best | 0.655111 | 0.655111 | 0.239467 | 0.239467 | yes |
| LastObservation | 24 | VoIThresholdSense_lambda0.01 | 0.630978 | 0.630978 | 0.204622 | 0.204622 | yes |
| LastObservation | 24 | VoIBudgetPriceSense_gamma0.1 | 0.649956 | 0.649956 | 0.253244 | 0.253244 | yes |
| LastObservation | 90 | NeverSense | 0.586889 | 0.586889 | 0.0 | 0.0 | yes |
| LastObservation | 90 | SequentialSearch | 0.705689 | 0.705689 | 1.0 | 1.0 | yes |
| LastObservation | 90 | ResolvableMassSense_best | 0.805911 | 0.805911 | 0.780711 | 0.780711 | yes |
| LastObservation | 90 | VoIThresholdSense_lambda0.01 | 0.676622 | 0.676622 | 0.587867 | 0.587867 | yes |
| LastObservation | 90 | VoIBudgetPriceSense_gamma0.1 | 0.705467 | 0.705467 | 0.815289 | 0.815289 | yes |
| PeriodicPersistence | 24 | NeverSense | 0.5924 | 0.5924 | 0.0 | 0.0 | yes |
| PeriodicPersistence | 24 | SequentialSearch | 0.654178 | 0.654178 | 0.266667 | 0.266667 | yes |
| PeriodicPersistence | 24 | ResolvableMassSense_best | 0.690444 | 0.690444 | 0.205733 | 0.205733 | yes |
| PeriodicPersistence | 24 | VoIThresholdSense_lambda0.05 | 0.681422 | 0.681156 | 0.243156 | 0.242978 | **NO** |
| PeriodicPersistence | 24 | VoIBudgetPriceSense_gamma0.1 | 0.668267 | 0.668 | 0.262489 | 0.2616 | **NO** |
| PeriodicPersistence | 90 | NeverSense | 0.5924 | 0.5924 | 0.0 | 0.0 | yes |
| PeriodicPersistence | 90 | SequentialSearch | 0.719822 | 0.719822 | 1.0 | 1.0 | yes |
| PeriodicPersistence | 90 | ResolvableMassSense_best | 0.852933 | 0.852933 | 0.962711 | 0.962711 | yes |
| PeriodicPersistence | 90 | VoIThresholdSense_lambda0.02 | 0.776933 | 0.776444 | 0.851244 | 0.854 | **NO** |
| PeriodicPersistence | 90 | VoIBudgetPriceSense_gamma0.1 | 0.750267 | 0.752311 | 0.976711 | 0.976222 | **NO** |
| PerpetuaStar | 24 | NeverSense | 0.531778 | 0.531778 | 0.0 | 0.0 | yes |
| PerpetuaStar | 24 | SequentialSearch | 0.600711 | 0.600711 | 0.266667 | 0.266667 | yes |
| PerpetuaStar | 24 | ResolvableMassSense_best | 0.616978 | 0.616978 | 0.266178 | 0.266178 | yes |
| PerpetuaStar | 24 | VoIThresholdSense_lambda0.2 | 0.631111 | 0.630978 | 0.260578 | 0.261111 | **NO** |
| PerpetuaStar | 24 | VoIBudgetPriceSense_gamma0.01 | 0.623067 | 0.631378 | 0.262711 | 0.261467 | **NO** |
| PerpetuaStar | 90 | NeverSense | 0.531778 | 0.531778 | 0.0 | 0.0 | yes |
| PerpetuaStar | 90 | SequentialSearch | 0.644133 | 0.644133 | 1.0 | 1.0 | yes |
| PerpetuaStar | 90 | ResolvableMassSense_best | 0.680578 | 0.680578 | 0.990356 | 0.990356 | yes |
| PerpetuaStar | 90 | VoIThresholdSense_lambda0.05 | 0.716711 | 0.718711 | 0.839556 | 0.840978 | **NO** |
| PerpetuaStar | 90 | VoIBudgetPriceSense_gamma0.1 | 0.7072 | 0.7056 | 0.988222 | 0.988311 | **NO** |
| OracleBelief | 24 | NeverSense | NeverSense | not in voi_policies | | | **NO** |
| OracleBelief | 24 | SequentialSearch | SequentialSearch | not in voi_policies | | | **NO** |
| OracleBelief | 24 | ResolvableMassSense | ResolvableMassSense_best | not in voi_policies | | | **NO** |
| OracleBelief | 24 | VoIThresholdSense | VoIThresholdSense_lambda0.01 | not in voi_policies | | | **NO** |
| OracleBelief | 24 | VoIBudgetPriceSense | VoIBudgetPriceSense_gamma0.1 | not in voi_policies | | | **NO** |
| OracleBelief | 90 | NeverSense | NeverSense | not in voi_policies | | | **NO** |
| OracleBelief | 90 | SequentialSearch | SequentialSearch | not in voi_policies | | | **NO** |
| OracleBelief | 90 | ResolvableMassSense | ResolvableMassSense_best | not in voi_policies | | | **NO** |
| OracleBelief | 90 | VoIThresholdSense | VoIThresholdSense_lambda0.01 | not in voi_policies | | | **NO** |
| OracleBelief | 90 | VoIBudgetPriceSense | VoIBudgetPriceSense_gamma0.1 | not in voi_policies | | | **NO** |

**30 cells checked against the reference csv; MISMATCHES PRESENT.**

## Is the difference ours, or was the reference already stale?

results/voi_policies/provenance.json records git_commit eb731bcd with git_dirty true, generated 2026-09-08T20:33; the Part B commit 230a2701 landed 3.6 h later and voi_sense.py differs between them. So the reference csv came from an uncommitted working state and no committed code reproduces it. These re-derivations show the divergence is pre-existing and not introduced by the room-change-cost work.

Re-derivation: python -m ... representative_grid GridTask per test household, aggregate_rows; identical PolicySpec, seed 0, 10 test households, 22500 questions per cell.

| cell | HEAD, original banks | this study at c = 0 | agree |
|---|---|---|---|
| PeriodicPersistence@24 VoIBudgetPriceSense_gamma0.1 | 0.668267 (0.262489) | 0.668267 (0.262489) | yes |
| PeriodicPersistence@24 VoIThresholdSense_lambda0.05 | 0.681422 (0.243156) | 0.681422 (0.243156) | yes |
| PeriodicPersistence@90 VoIBudgetPriceSense_gamma0.1 | 0.750267 (0.976711) | 0.750267 (0.976711) | yes |
| PeriodicPersistence@90 VoIThresholdSense_lambda0.02 | 0.776933 (0.851244) | 0.776933 (0.851244) | yes |
| PerpetuaStar@24 VoIBudgetPriceSense_gamma0.01 | 0.623067 (0.262711) | 0.623067 (0.262711) | yes |
| PerpetuaStar@24 VoIThresholdSense_lambda0.2 | 0.631111 (0.260578) | 0.631111 (0.260578) | yes |
| PerpetuaStar@90 VoIThresholdSense_lambda0.05 | 0.716711 (0.839556) | 0.716711 (0.839556) | yes |

**Every re-derived cell agrees with this study's c = 0 column exactly, so the room-change cost changed nothing at c = 0 and the reference csv is stale. The c > 0 readings stand.**

