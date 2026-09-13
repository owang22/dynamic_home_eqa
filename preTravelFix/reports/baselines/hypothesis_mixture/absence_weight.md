# Setting the absence weight

Passive diet, no sensing. `spread` is max-minus-min of the cumulative log likelihood each half of the scoring paid out across particles: the half with the larger spread is the one moving the weights.

## hh_001

| absence_weight | threshold | ESS | presence spread | absence spread | passive acc | LastObservation | MostFrequentLocation | TimetableLookup | Markov1 | PeriodicPersistence | HierarchyBackoff | SmoothedRecency |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2 | 5.17 | 173 | 0 | 0.630 | 0.07 | 0.25 | 0.11 | 0.04 | 0.09 | 0.28 | 0.15 |
| 0.1 | 2 | 4.95 | 173 | 35 | 0.630 | 0.05 | 0.26 | 0.10 | 0.04 | 0.10 | 0.28 | 0.18 |
| 0.25 | 2 | 4.66 | 173 | 87 | 0.632 | 0.02 | 0.28 | 0.08 | 0.03 | 0.10 | 0.27 | 0.22 |
| 0.5 | 2 | 4.21 | 173 | 173 | 0.630 | 0.01 | 0.28 | 0.06 | 0.02 | 0.09 | 0.23 | 0.30 |
| 1 | 2 | 3.08 | 173 | 347 | 0.632 | 0.00 | 0.26 | 0.02 | 0.01 | 0.08 | 0.15 | 0.48 |
| 0.25 | 0 | 4.43 | 173 | 64 | 0.632 | 0.03 | 0.25 | 0.06 | 0.02 | 0.10 | 0.30 | 0.23 |

## hh_002

| absence_weight | threshold | ESS | presence spread | absence spread | passive acc | LastObservation | MostFrequentLocation | TimetableLookup | Markov1 | PeriodicPersistence | HierarchyBackoff | SmoothedRecency |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2 | 4.76 | 293 | 0 | 0.571 | 0.25 | 0.07 | 0.06 | 0.07 | 0.21 | 0.29 | 0.04 |
| 0.1 | 2 | 4.68 | 293 | 48 | 0.571 | 0.26 | 0.07 | 0.06 | 0.07 | 0.21 | 0.29 | 0.04 |
| 0.25 | 2 | 4.57 | 293 | 119 | 0.571 | 0.28 | 0.07 | 0.06 | 0.06 | 0.22 | 0.28 | 0.04 |
| 0.5 | 2 | 4.36 | 293 | 238 | 0.573 | 0.31 | 0.06 | 0.05 | 0.05 | 0.23 | 0.27 | 0.04 |
| 1 | 2 | 3.94 | 293 | 477 | 0.571 | 0.36 | 0.05 | 0.04 | 0.03 | 0.24 | 0.25 | 0.03 |
| 0.25 | 0 | 3.62 | 293 | 74 | 0.565 | 0.35 | 0.04 | 0.03 | 0.02 | 0.19 | 0.33 | 0.03 |

