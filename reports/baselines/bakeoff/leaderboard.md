# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 1 households, 59 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.593 | 0.593..0.593 | 2.810 | 2.810..2.810 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.559 | 0.559..0.559 | 2.224 | 2.224..2.224 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.542 | 0.542..0.542 | 2.535 | 2.535..2.535 |
| MostFrequentLocation(hl=24h) | 0.525 | 0.525..0.525 | 2.049 | 2.049..2.049 |
| Markov1(a=1,cut=24h,hl=24h) | 0.525 | 0.525..0.525 | 1.934 | 1.934..1.934 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.525 | 0.525..0.525 | 1.756 | 1.756..1.756 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.508 | 0.508..0.508 | 1.851 | 1.851..1.851 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.938 (n=16) | 0.538 (n=91) | 0.506 (n=616) | 0.480 (n=2877) |
| MostFrequentLocation(hl=24h) | 0.938 (n=16) | 0.538 (n=91) | 0.497 (n=616) | 0.487 (n=2877) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.750 (n=16) | 0.516 (n=91) | 0.477 (n=616) | 0.475 (n=2877) |
| Markov1(a=1,cut=24h,hl=24h) | 0.750 (n=16) | 0.505 (n=91) | 0.497 (n=616) | 0.487 (n=2877) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.938 (n=16) | 0.538 (n=91) | 0.500 (n=616) | 0.477 (n=2877) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.625 (n=16) | 0.451 (n=91) | 0.492 (n=616) | 0.461 (n=2877) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.938 (n=16) | 0.538 (n=91) | 0.492 (n=616) | 0.482 (n=2877) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| revamp_v1__claude-fable-5__hh1 | LastObservation (0.593) | HierarchyBackoff(po=5,pc=5,hl=24h) (1.756) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 1 households, 90 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.544 | 0.544..0.544 | 3.147 | 3.147..3.147 |
| MostFrequentLocation(hl=24h) | 0.544 | 0.544..0.544 | 2.980 | 2.980..2.980 |
| Markov1(a=1,cut=24h,hl=24h) | 0.544 | 0.544..0.544 | 2.980 | 2.980..2.980 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.544 | 0.544..0.544 | 2.980 | 2.980..2.980 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.544 | 0.544..0.544 | 2.845 | 2.845..2.845 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.522 | 0.522..0.522 | 3.124 | 3.124..3.124 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.522 | 0.522..0.522 | 3.124 | 3.124..3.124 |

### D=1,h=7

Cell `D=1,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.458 | 0.458..0.458 | 3.742 | 3.742..3.742 |
| MostFrequentLocation(hl=24h) | 0.458 | 0.458..0.458 | 3.642 | 3.642..3.642 |
| Markov1(a=1,cut=24h,hl=24h) | 0.458 | 0.458..0.458 | 3.642 | 3.642..3.642 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.458 | 0.458..0.458 | 3.642 | 3.642..3.642 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.458 | 0.458..0.458 | 2.744 | 2.744..2.744 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.456 | 0.456..0.456 | 3.688 | 3.688..3.688 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.450 | 0.450..0.450 | 3.723 | 3.723..3.723 |

### D=3,h=0.25

Cell `D=3,h=0.25`: 1 households, 30 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.533 | 0.533..0.533 | 3.224 | 3.224..3.224 |
| MostFrequentLocation(hl=24h) | 0.533 | 0.533..0.533 | 3.261 | 3.261..3.261 |
| Markov1(a=1,cut=24h,hl=24h) | 0.533 | 0.533..0.533 | 3.898 | 3.898..3.898 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.533 | 0.533..0.533 | 3.258 | 3.258..3.258 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.500 | 0.500..0.500 | 3.311 | 3.311..3.311 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.500 | 0.500..0.500 | 3.152 | 3.152..3.152 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.467 | 0.467..0.467 | 3.704 | 3.704..3.704 |

### D=3,h=1

Cell `D=3,h=1`: 1 households, 60 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.700 | 0.700..0.700 | 2.072 | 2.072..2.072 |
| MostFrequentLocation(hl=24h) | 0.700 | 0.700..0.700 | 2.025 | 2.025..2.025 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.700 | 0.700..0.700 | 2.023 | 2.023..2.023 |
| Markov1(a=1,cut=24h,hl=24h) | 0.700 | 0.700..0.700 | 2.077 | 2.077..2.077 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.700 | 0.700..0.700 | 2.022 | 2.022..2.022 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.700 | 0.700..0.700 | 2.044 | 2.044..2.044 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.667 | 0.667..0.667 | 2.071 | 2.071..2.071 |

### D=3,h=3

Cell `D=3,h=3`: 1 households, 180 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.472 | 0.472..0.472 | 3.646 | 3.646..3.646 |
| MostFrequentLocation(hl=24h) | 0.472 | 0.472..0.472 | 3.413 | 3.413..3.413 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.472 | 0.472..0.472 | 3.439 | 3.439..3.439 |
| Markov1(a=1,cut=24h,hl=24h) | 0.472 | 0.472..0.472 | 3.413 | 3.413..3.413 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.472 | 0.472..0.472 | 3.403 | 3.403..3.403 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.467 | 0.467..0.467 | 3.425 | 3.425..3.425 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.461 | 0.461..0.461 | 2.847 | 2.847..2.847 |

### D=3,h=7

Cell `D=3,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.461 | 0.461..0.461 | 3.723 | 3.723..3.723 |
| MostFrequentLocation(hl=24h) | 0.461 | 0.461..0.461 | 3.406 | 3.406..3.406 |
| Markov1(a=1,cut=24h,hl=24h) | 0.461 | 0.461..0.461 | 3.406 | 3.406..3.406 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.461 | 0.461..0.461 | 3.433 | 3.433..3.433 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.456 | 0.456..0.456 | 3.379 | 3.379..3.379 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.439 | 0.439..0.439 | 3.606 | 3.606..3.606 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.431 | 0.431..0.431 | 2.637 | 2.637..2.637 |

### D=5,h=0.25

Cell `D=5,h=0.25`: 1 households, 29 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.414 | 0.414..0.414 | 4.049 | 4.049..4.049 |
| MostFrequentLocation(hl=24h) | 0.414 | 0.414..0.414 | 3.777 | 3.777..3.777 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.414 | 0.414..0.414 | 3.777 | 3.777..3.777 |
| Markov1(a=1,cut=24h,hl=24h) | 0.414 | 0.414..0.414 | 3.204 | 3.204..3.204 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.414 | 0.414..0.414 | 3.751 | 3.751..3.751 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.414 | 0.414..0.414 | 3.765 | 3.765..3.765 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.345 | 0.345..0.345 | 3.899 | 3.899..3.899 |

### D=5,h=1

Cell `D=5,h=1`: 1 households, 61 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.525 | 0.525..0.525 | 3.284 | 3.284..3.284 |
| MostFrequentLocation(hl=24h) | 0.525 | 0.525..0.525 | 2.492 | 2.492..2.492 |
| Markov1(a=1,cut=24h,hl=24h) | 0.525 | 0.525..0.525 | 2.463 | 2.463..2.463 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.525 | 0.525..0.525 | 2.573 | 2.573..2.573 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.525 | 0.525..0.525 | 2.195 | 2.195..2.195 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.492 | 0.492..0.492 | 2.778 | 2.778..2.778 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.492 | 0.492..0.492 | 2.308 | 2.308..2.308 |

### D=5,h=3

Cell `D=5,h=3`: 1 households, 180 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.439 | 0.439..0.439 | 3.206 | 3.206..3.206 |
| LastObservation | 0.428 | 0.428..0.428 | 3.953 | 3.953..3.953 |
| MostFrequentLocation(hl=24h) | 0.428 | 0.428..0.428 | 3.029 | 3.029..3.029 |
| Markov1(a=1,cut=24h,hl=24h) | 0.428 | 0.428..0.428 | 3.029 | 3.029..3.029 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.428 | 0.428..0.428 | 2.113 | 2.113..2.113 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.422 | 0.422..0.422 | 3.380 | 3.380..3.380 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.411 | 0.411..0.411 | 2.872 | 2.872..2.872 |

### D=5,h=7

Cell `D=5,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.458 | 0.458..0.458 | 3.051 | 3.051..3.051 |
| LastObservation | 0.444 | 0.444..0.444 | 3.838 | 3.838..3.838 |
| MostFrequentLocation(hl=24h) | 0.444 | 0.444..0.444 | 3.063 | 3.063..3.063 |
| Markov1(a=1,cut=24h,hl=24h) | 0.444 | 0.444..0.444 | 3.063 | 3.063..3.063 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.444 | 0.444..0.444 | 2.820 | 2.820..2.820 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.439 | 0.439..0.439 | 3.259 | 3.259..3.259 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.436 | 0.436..0.436 | 3.315 | 3.315..3.315 |

### D=7,h=0.25

Cell `D=7,h=0.25`: 1 households, 31 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.484 | 0.484..0.484 | 3.565 | 3.565..3.565 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.484 | 0.484..0.484 | 3.304 | 3.304..3.304 |
| MostFrequentLocation(hl=24h) | 0.452 | 0.452..0.452 | 3.212 | 3.212..3.212 |
| Markov1(a=1,cut=24h,hl=24h) | 0.452 | 0.452..0.452 | 3.463 | 3.463..3.463 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.452 | 0.452..0.452 | 1.825 | 1.825..1.825 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.355 | 0.355..0.355 | 3.862 | 3.862..3.862 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.258 | 0.258..0.258 | 3.397 | 3.397..3.397 |

### D=7,h=1

Cell `D=7,h=1`: 1 households, 59 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.593 | 0.593..0.593 | 2.810 | 2.810..2.810 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.559 | 0.559..0.559 | 2.224 | 2.224..2.224 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.542 | 0.542..0.542 | 2.535 | 2.535..2.535 |
| MostFrequentLocation(hl=24h) | 0.525 | 0.525..0.525 | 2.049 | 2.049..2.049 |
| Markov1(a=1,cut=24h,hl=24h) | 0.525 | 0.525..0.525 | 1.934 | 1.934..1.934 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.525 | 0.525..0.525 | 1.756 | 1.756..1.756 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.508 | 0.508..0.508 | 1.851 | 1.851..1.851 |

### D=7,h=3

Cell `D=7,h=3`: 1 households, 180 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.433 | 0.433..0.433 | 3.914 | 3.914..3.914 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.417 | 0.417..0.417 | 3.367 | 3.367..3.367 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.417 | 0.417..0.417 | 3.291 | 3.291..3.291 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.383 | 0.383..0.383 | 3.519 | 3.519..3.519 |
| MostFrequentLocation(hl=24h) | 0.372 | 0.372..0.372 | 3.258 | 3.258..3.258 |
| Markov1(a=1,cut=24h,hl=24h) | 0.372 | 0.372..0.372 | 3.258 | 3.258..3.258 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.372 | 0.372..0.372 | 3.077 | 3.077..3.077 |

### D=7,h=7

Cell `D=7,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.497 | 0.497..0.497 | 2.579 | 2.579..2.579 |
| Markov1(a=1,cut=24h,hl=24h) | 0.497 | 0.497..0.497 | 2.579 | 2.579..2.579 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.497 | 0.497..0.497 | 2.251 | 2.251..2.251 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.494 | 0.494..0.494 | 2.758 | 2.758..2.758 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.494 | 0.494..0.494 | 2.702 | 2.702..2.702 |
| LastObservation | 0.469 | 0.469..0.469 | 3.665 | 3.665..3.665 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.456 | 0.456..0.456 | 2.504 | 2.504..2.504 |

### D=10,h=0.25

Cell `D=10,h=0.25`: 1 households, 21 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.381 | 0.381..0.381 | 4.276 | 4.276..4.276 |
| MostFrequentLocation(hl=24h) | 0.381 | 0.381..0.381 | 3.442 | 3.442..3.442 |
| Markov1(a=1,cut=24h,hl=24h) | 0.381 | 0.381..0.381 | 2.970 | 2.970..2.970 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.381 | 0.381..0.381 | 3.877 | 3.877..3.877 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.381 | 0.381..0.381 | 3.341 | 3.341..3.341 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.381 | 0.381..0.381 | 3.439 | 3.439..3.439 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.286 | 0.286..0.286 | 4.292 | 4.292..4.292 |

### D=10,h=1

Cell `D=10,h=1`: 1 households, 69 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.464 | 0.464..0.464 | 2.608 | 2.608..2.608 |
| LastObservation | 0.406 | 0.406..0.406 | 4.105 | 4.105..4.105 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.406 | 0.406..0.406 | 3.167 | 3.167..3.167 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.391 | 0.391..0.391 | 3.108 | 3.108..3.108 |
| MostFrequentLocation(hl=24h) | 0.377 | 0.377..0.377 | 3.112 | 3.112..3.112 |
| Markov1(a=1,cut=24h,hl=24h) | 0.377 | 0.377..0.377 | 3.004 | 3.004..3.004 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.377 | 0.377..0.377 | 3.033 | 3.033..3.033 |

### D=10,h=3

Cell `D=10,h=3`: 1 households, 180 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.517 | 0.517..0.517 | 2.304 | 2.304..2.304 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.517 | 0.517..0.517 | 2.649 | 2.649..2.649 |
| Markov1(a=1,cut=24h,hl=24h) | 0.517 | 0.517..0.517 | 2.304 | 2.304..2.304 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.517 | 0.517..0.517 | 2.187 | 2.187..2.187 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.483 | 0.483..0.483 | 2.568 | 2.568..2.568 |
| LastObservation | 0.472 | 0.472..0.472 | 3.646 | 3.646..3.646 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.461 | 0.461..0.461 | 2.048 | 2.048..2.048 |

### D=10,h=7

Cell `D=10,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.567 | 0.567..0.567 | 1.930 | 1.930..1.930 |
| Markov1(a=1,cut=24h,hl=24h) | 0.567 | 0.567..0.567 | 1.930 | 1.930..1.930 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.567 | 0.567..0.567 | 1.838 | 1.838..1.838 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.539 | 0.539..0.539 | 2.399 | 2.399..2.399 |
| LastObservation | 0.531 | 0.531..0.531 | 3.243 | 3.243..3.243 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.508 | 0.508..0.508 | 2.230 | 2.230..2.230 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.478 | 0.478..0.478 | 1.799 | 1.799..1.799 |

### D=14,h=0.25

Cell `D=14,h=0.25`: 1 households, 32 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.875 | 0.875..0.875 | 0.863 | 0.863..0.863 |
| MostFrequentLocation(hl=24h) | 0.875 | 0.875..0.875 | 0.700 | 0.700..0.700 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.875 | 0.875..0.875 | 0.740 | 0.740..0.740 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.875 | 0.875..0.875 | 0.530 | 0.530..0.530 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.719 | 0.719..0.719 | 1.419 | 1.419..1.419 |
| Markov1(a=1,cut=24h,hl=24h) | 0.688 | 0.688..0.688 | 1.564 | 1.564..1.564 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.688 | 0.688..0.688 | 0.904 | 0.904..0.904 |

### D=14,h=1

Cell `D=14,h=1`: 1 households, 58 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.672 | 0.672..0.672 | 2.263 | 2.263..2.263 |
| MostFrequentLocation(hl=24h) | 0.672 | 0.672..0.672 | 1.502 | 1.502..1.502 |
| Markov1(a=1,cut=24h,hl=24h) | 0.672 | 0.672..0.672 | 1.253 | 1.253..1.253 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.672 | 0.672..0.672 | 1.436 | 1.436..1.436 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.655 | 0.655..0.655 | 1.789 | 1.789..1.789 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.638 | 0.638..0.638 | 2.089 | 2.089..2.089 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.638 | 0.638..0.638 | 1.633 | 1.633..1.633 |

### D=14,h=3

Cell `D=14,h=3`: 1 households, 180 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.578 | 0.578..0.578 | 2.917 | 2.917..2.917 |
| MostFrequentLocation(hl=24h) | 0.578 | 0.578..0.578 | 2.033 | 2.033..2.033 |
| Markov1(a=1,cut=24h,hl=24h) | 0.578 | 0.578..0.578 | 2.033 | 2.033..2.033 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.578 | 0.578..0.578 | 1.957 | 1.957..1.957 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.544 | 0.544..0.544 | 2.367 | 2.367..2.367 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.533 | 0.533..0.533 | 2.616 | 2.616..2.616 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.522 | 0.522..0.522 | 2.121 | 2.121..2.121 |

### D=14,h=7

Cell `D=14,h=7`: 1 households, 360 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.481 | 0.481..0.481 | 3.588 | 3.588..3.588 |
| MostFrequentLocation(hl=24h) | 0.481 | 0.481..0.481 | 2.808 | 2.808..2.808 |
| Markov1(a=1,cut=24h,hl=24h) | 0.481 | 0.481..0.481 | 2.808 | 2.808..2.808 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.481 | 0.481..0.481 | 2.772 | 2.772..2.772 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.472 | 0.472..0.472 | 3.040 | 3.040..3.040 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.469 | 0.469..0.469 | 3.184 | 3.184..3.184 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.444 | 0.444..0.444 | 2.668 | 2.668..2.668 |
