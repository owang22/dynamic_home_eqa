# Bake-off across 5 realizations (seeds 0, 1, 2, 3, 4)

Headline cell D=7,h=1. Each seed re-runs the SAME households through the seeded simulator: same personas, stories and object rules, different jitter and misplacement draws. Accuracy is the mean over realizations; +/- is half the seed range, so it is the spread a single-seed number hides, not a bootstrap interval.

| model | accuracy (mean +/- half-range) | per-seed | mean log-loss |
|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.482 +/- 0.015 | 0.476 / 0.480 / 0.466 / 0.492 / 0.497 | 3.180 |
| LastObservation | 0.479 +/- 0.018 | 0.467 / 0.482 / 0.469 / 0.475 / 0.503 | 3.518 |
| SmoothedRecency(hl=6h,freq=24h) | 0.478 +/- 0.018 | 0.469 / 0.470 / 0.471 / 0.476 / 0.504 | 3.319 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.476 +/- 0.022 | 0.451 / 0.485 / 0.474 / 0.476 / 0.495 | 3.005 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.475 +/- 0.013 | 0.460 / 0.473 / 0.476 / 0.482 / 0.486 | 3.261 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.465 +/- 0.017 | 0.446 / 0.475 / 0.456 / 0.467 / 0.480 | 3.208 |
| Markov1(a=1,cut=24h,hl=24h) | 0.461 +/- 0.016 | 0.452 / 0.457 / 0.459 / 0.452 / 0.485 | 3.397 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.452 +/- 0.019 | 0.450 / 0.457 / 0.431 / 0.455 / 0.468 | 3.333 |

## Which model wins, per seed

- seed 0: MostFrequentLocation(hl=24h) (0.476)
- seed 1: HierarchyBackoff(po=5,pc=5,hl=24h) (0.485)
- seed 2: PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.476)
- seed 3: MostFrequentLocation(hl=24h) (0.492)
- seed 4: SmoothedRecency(hl=6h,freq=24h) (0.504)

4 distinct winners across 5 seeds. Model spread within a seed: 0.045. Seed spread within a model (max): 0.044.

A ranking claim is only safe when the gap between two models exceeds the seed spread above.
