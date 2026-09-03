# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 20 households, 1656 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.476 [0.447, 0.510] | 0.344..0.636 | 3.292 [3.100, 3.468] | 2.294..4.172 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.474 [0.443, 0.508] | 0.344..0.636 | 3.031 [2.866, 3.184] | 2.233..3.849 |
| SmoothedRecency(hl=6h,freq=24h) | 0.471 [0.441, 0.505] | 0.372..0.636 | 3.352 [3.132, 3.552] | 2.162..4.282 |
| LastObservation | 0.469 [0.440, 0.502] | 0.366..0.636 | 3.613 [3.388, 3.821] | 2.512..4.339 |
| MostFrequentLocation(hl=24h) | 0.466 [0.437, 0.500] | 0.344..0.636 | 3.195 [3.010, 3.373] | 2.222..4.088 |
| Markov1(a=1,cut=24h,hl=24h) | 0.459 [0.433, 0.489] | 0.344..0.636 | 3.419 [3.185, 3.638] | 2.170..4.278 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.456 [0.424, 0.495] | 0.328..0.648 | 3.233 [3.063, 3.400] | 2.326..4.073 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.431 [0.401, 0.465] | 0.328..0.568 | 3.375 [3.211, 3.531] | 2.605..4.126 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.922 (n=96) | 0.574 (n=4008) | 0.446 (n=17363) | 0.392 (n=50533) |
| MostFrequentLocation(hl=24h) | 0.925 (n=96) | 0.575 (n=4008) | 0.450 (n=17363) | 0.398 (n=50533) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.719 (n=96) | 0.534 (n=4008) | 0.428 (n=17363) | 0.391 (n=50533) |
| Markov1(a=1,cut=24h,hl=24h) | 0.740 (n=96) | 0.525 (n=4008) | 0.446 (n=17363) | 0.394 (n=50533) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.925 (n=96) | 0.574 (n=4008) | 0.447 (n=17363) | 0.400 (n=50533) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.837 (n=96) | 0.555 (n=4008) | 0.450 (n=17363) | 0.402 (n=50533) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.925 (n=96) | 0.575 (n=4008) | 0.451 (n=17363) | 0.401 (n=50533) |
| SmoothedRecency(hl=6h,freq=24h) | 0.922 (n=96) | 0.577 (n=4008) | 0.449 (n=17363) | 0.397 (n=50533) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| households__generated__gpt-5.6-terra__hh_001__seed2 | Markov1(a=1,cut=24h,hl=24h) (0.523) | Markov1(a=1,cut=24h,hl=24h) (2.170) |
| households__generated__gpt-5.6-terra__hh_002__seed2 | MostFrequentLocation(hl=24h) (0.487) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.895) |
| households__generated__gpt-5.6-terra__hh_003__seed2 | HierarchyBackoff(po=5,pc=5,hl=24h) (0.524) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.941) |
| households__generated__gpt-5.6-terra__hh_004__seed2 | LastObservation (0.538) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.866) |
| households__generated__gpt-5.6-terra__hh_005__seed2 | LastObservation (0.375) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.643) |
| households__generated__gpt-5.6-terra__hh_006__seed2 | LastObservation (0.483) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.792) |
| households__generated__gpt-5.6-terra__hh_007__seed2 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.453) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.497) |
| households__generated__gpt-5.6-terra__hh_008__seed2 | LastObservation (0.388) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.207) |
| households__generated__gpt-5.6-terra__hh_009__seed2 | MostFrequentLocation(hl=24h) (0.500) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.856) |
| households__generated__gpt-5.6-terra__hh_010__seed2 | HierarchyBackoff(po=5,pc=5,hl=24h) (0.390) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.227) |
| households__generated__gpt-5.6-terra__hh_011__seed2 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.494) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.133) |
| households__generated__gpt-5.6-terra__hh_012__seed2 | Markov1(a=1,cut=24h,hl=24h) (0.512) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.862) |
| households__generated__gpt-5.6-terra__hh_013__seed2 | LastObservation (0.542) | SmoothedRecency(hl=6h,freq=24h) (3.007) |
| households__generated__gpt-5.6-terra__hh_014__seed2 | LastObservation (0.443) | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (3.814) |
| households__generated__gpt-5.6-terra__hh_015__seed2 | Markov1(a=1,cut=24h,hl=24h) (0.447) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.298) |
| households__generated__gpt-5.6-terra__hh_016__seed2 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.648) | SmoothedRecency(hl=6h,freq=24h) (2.162) |
| households__generated__gpt-5.6-terra__hh_017__seed2 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.523) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.017) |
| households__generated__gpt-5.6-terra__hh_018__seed2 | LastObservation (0.500) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.921) |
| households__generated__gpt-5.6-terra__hh_019__seed2 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.456) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.048) |
| households__generated__gpt-5.6-terra__hh_020__seed2 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.584) | SmoothedRecency(hl=6h,freq=24h) (2.681) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 20 households, 1800 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.415 [0.375, 0.456] | 0.267..0.633 | 3.784 [3.502, 4.059] | 2.253..4.989 |
| MostFrequentLocation(hl=24h) | 0.409 [0.372, 0.454] | 0.267..0.633 | 3.719 [3.457, 3.990] | 2.259..5.004 |
| LastObservation | 0.405 [0.366, 0.449] | 0.267..0.633 | 3.948 [3.678, 4.207] | 2.533..4.989 |
| Markov1(a=1,cut=24h,hl=24h) | 0.398 [0.363, 0.441] | 0.267..0.633 | 3.719 [3.457, 3.990] | 2.259..5.004 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.398 [0.358, 0.443] | 0.267..0.633 | 3.726 [3.462, 3.996] | 2.259..5.004 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.394 [0.358, 0.436] | 0.267..0.633 | 3.561 [3.309, 3.850] | 2.238..5.023 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.389 [0.351, 0.432] | 0.267..0.633 | 3.756 [3.499, 4.013] | 2.259..5.004 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.383 [0.346, 0.427] | 0.267..0.633 | 3.747 [3.483, 4.012] | 2.259..5.004 |

### D=1,h=7

Cell `D=1,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.416 [0.381, 0.454] | 0.283..0.594 | 3.740 [3.543, 3.923] | 2.657..4.234 |
| SmoothedRecency(hl=6h,freq=24h) | 0.414 [0.380, 0.452] | 0.269..0.597 | 3.775 [3.561, 3.975] | 2.615..4.451 |
| MostFrequentLocation(hl=24h) | 0.413 [0.378, 0.451] | 0.281..0.597 | 3.737 [3.539, 3.921] | 2.641..4.234 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.409 [0.376, 0.447] | 0.283..0.589 | 3.624 [3.446, 3.788] | 2.749..4.165 |
| LastObservation | 0.407 [0.371, 0.447] | 0.269..0.597 | 3.949 [3.731, 4.160] | 2.782..4.624 |
| Markov1(a=1,cut=24h,hl=24h) | 0.403 [0.366, 0.444] | 0.269..0.597 | 3.737 [3.539, 3.921] | 2.641..4.234 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.402 [0.366, 0.441] | 0.275..0.594 | 3.780 [3.584, 3.966] | 2.695..4.301 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.400 [0.364, 0.439] | 0.275..0.597 | 3.761 [3.562, 3.947] | 2.669..4.285 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 20 households, 1616 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.468 [0.421, 0.517] | 0.274..0.691 | 3.267 [2.979, 3.549] | 2.118..4.521 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.466 [0.422, 0.504] | 0.274..0.625 | 3.291 [3.009, 3.562] | 2.200..4.515 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.465 [0.415, 0.521] | 0.274..0.691 | 3.143 [2.917, 3.373] | 2.188..3.998 |
| LastObservation | 0.464 [0.410, 0.520] | 0.250..0.691 | 3.547 [3.247, 3.834] | 2.215..4.815 |
| SmoothedRecency(hl=6h,freq=24h) | 0.464 [0.420, 0.510] | 0.274..0.670 | 3.334 [3.030, 3.629] | 2.124..4.644 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.459 [0.417, 0.497] | 0.265..0.614 | 3.330 [3.044, 3.607] | 2.185..4.614 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.455 [0.402, 0.509] | 0.274..0.691 | 3.288 [2.996, 3.571] | 2.169..4.540 |
| Markov1(a=1,cut=24h,hl=24h) | 0.439 [0.391, 0.492] | 0.274..0.662 | 3.702 [3.494, 3.920] | 2.932..4.489 |

### D=3,h=3

Cell `D=3,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.406 [0.367, 0.449] | 0.233..0.600 | 3.567 [3.327, 3.762] | 2.200..4.276 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.404 [0.369, 0.441] | 0.233..0.606 | 3.572 [3.334, 3.769] | 2.202..4.285 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.404 [0.374, 0.437] | 0.306..0.578 | 3.630 [3.394, 3.821] | 2.309..4.278 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.403 [0.368, 0.444] | 0.256..0.606 | 3.590 [3.353, 3.789] | 2.248..4.278 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.402 [0.367, 0.441] | 0.233..0.556 | 3.443 [3.229, 3.611] | 2.304..3.993 |
| LastObservation | 0.392 [0.353, 0.432] | 0.233..0.556 | 3.957 [3.748, 4.140] | 3.070..4.797 |
| SmoothedRecency(hl=6h,freq=24h) | 0.391 [0.357, 0.426] | 0.233..0.589 | 3.642 [3.389, 3.849] | 2.163..4.357 |
| Markov1(a=1,cut=24h,hl=24h) | 0.389 [0.351, 0.432] | 0.233..0.600 | 3.567 [3.327, 3.762] | 2.200..4.276 |

### D=3,h=7

Cell `D=3,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.393 [0.363, 0.426] | 0.225..0.553 | 3.726 [3.528, 3.906] | 2.635..4.406 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.385 [0.357, 0.415] | 0.239..0.528 | 3.784 [3.594, 3.960] | 2.769..4.440 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.385 [0.352, 0.417] | 0.203..0.522 | 3.581 [3.399, 3.760] | 2.632..4.254 |
| MostFrequentLocation(hl=24h) | 0.383 [0.353, 0.414] | 0.203..0.542 | 3.732 [3.529, 3.910] | 2.600..4.383 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.380 [0.349, 0.411] | 0.247..0.547 | 3.759 [3.567, 3.937] | 2.749..4.422 |
| SmoothedRecency(hl=6h,freq=24h) | 0.377 [0.343, 0.412] | 0.203..0.542 | 3.804 [3.591, 3.993] | 2.563..4.506 |
| Markov1(a=1,cut=24h,hl=24h) | 0.374 [0.340, 0.411] | 0.203..0.542 | 3.732 [3.529, 3.910] | 2.600..4.383 |
| LastObservation | 0.371 [0.334, 0.405] | 0.203..0.522 | 4.131 [3.967, 4.294] | 3.300..4.673 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 20 households, 1625 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.458 [0.420, 0.490] | 0.273..0.614 | 3.465 [3.248, 3.691] | 2.569..4.371 |
| LastObservation | 0.453 [0.413, 0.493] | 0.284..0.614 | 3.680 [3.443, 3.922] | 2.669..4.663 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.451 [0.419, 0.485] | 0.330..0.625 | 3.468 [3.247, 3.696] | 2.605..4.422 |
| MostFrequentLocation(hl=24h) | 0.449 [0.416, 0.481] | 0.330..0.614 | 3.431 [3.211, 3.664] | 2.564..4.398 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.448 [0.416, 0.481] | 0.284..0.614 | 3.422 [3.219, 3.632] | 2.532..4.211 |
| SmoothedRecency(hl=6h,freq=24h) | 0.448 [0.412, 0.485] | 0.330..0.614 | 3.452 [3.233, 3.681] | 2.578..4.396 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.439 [0.412, 0.468] | 0.330..0.602 | 3.538 [3.333, 3.754] | 2.680..4.476 |
| Markov1(a=1,cut=24h,hl=24h) | 0.411 [0.378, 0.444] | 0.284..0.625 | 3.841 [3.653, 4.028] | 2.995..4.377 |

### D=5,h=3

Cell `D=5,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.387 [0.349, 0.427] | 0.206..0.550 | 3.797 [3.574, 4.012] | 2.737..4.580 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.384 [0.345, 0.423] | 0.244..0.567 | 3.716 [3.508, 3.894] | 2.760..4.300 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.380 [0.342, 0.419] | 0.244..0.572 | 3.843 [3.614, 4.056] | 2.738..4.622 |
| LastObservation | 0.378 [0.338, 0.421] | 0.211..0.567 | 4.135 [3.879, 4.377] | 2.993..4.943 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.374 [0.339, 0.412] | 0.250..0.567 | 3.900 [3.676, 4.103] | 2.758..4.616 |
| Markov1(a=1,cut=24h,hl=24h) | 0.372 [0.333, 0.411] | 0.244..0.567 | 3.802 [3.575, 4.017] | 2.718..4.573 |
| SmoothedRecency(hl=6h,freq=24h) | 0.371 [0.333, 0.413] | 0.211..0.567 | 3.855 [3.613, 4.081] | 2.694..4.767 |
| MostFrequentLocation(hl=24h) | 0.370 [0.332, 0.411] | 0.211..0.567 | 3.802 [3.575, 4.017] | 2.718..4.573 |

### D=5,h=7

Cell `D=5,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.381 [0.352, 0.409] | 0.264..0.503 | 3.644 [3.514, 3.793] | 3.069..4.376 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.381 [0.357, 0.404] | 0.253..0.478 | 3.814 [3.686, 3.963] | 3.281..4.512 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.373 [0.343, 0.402] | 0.222..0.503 | 3.718 [3.586, 3.873] | 3.136..4.473 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.372 [0.342, 0.401] | 0.222..0.494 | 3.777 [3.646, 3.929] | 3.260..4.497 |
| MostFrequentLocation(hl=24h) | 0.366 [0.334, 0.397] | 0.222..0.489 | 3.726 [3.588, 3.880] | 3.147..4.488 |
| Markov1(a=1,cut=24h,hl=24h) | 0.362 [0.330, 0.394] | 0.222..0.489 | 3.726 [3.588, 3.880] | 3.147..4.488 |
| LastObservation | 0.362 [0.329, 0.397] | 0.233..0.483 | 4.108 [3.949, 4.270] | 3.431..4.769 |
| SmoothedRecency(hl=6h,freq=24h) | 0.356 [0.326, 0.390] | 0.233..0.494 | 3.809 [3.660, 3.969] | 3.206..4.651 |

### D=7,h=0.25

(no questions in cell D=7,h=0.25)

### D=7,h=1

Cell `D=7,h=1`: 20 households, 1656 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.476 [0.447, 0.510] | 0.344..0.636 | 3.292 [3.100, 3.468] | 2.294..4.172 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.474 [0.443, 0.508] | 0.344..0.636 | 3.031 [2.866, 3.184] | 2.233..3.849 |
| SmoothedRecency(hl=6h,freq=24h) | 0.471 [0.441, 0.505] | 0.372..0.636 | 3.352 [3.132, 3.552] | 2.162..4.282 |
| LastObservation | 0.469 [0.440, 0.502] | 0.366..0.636 | 3.613 [3.388, 3.821] | 2.512..4.339 |
| MostFrequentLocation(hl=24h) | 0.466 [0.437, 0.500] | 0.344..0.636 | 3.195 [3.010, 3.373] | 2.222..4.088 |
| Markov1(a=1,cut=24h,hl=24h) | 0.459 [0.433, 0.489] | 0.344..0.636 | 3.419 [3.185, 3.638] | 2.170..4.278 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.456 [0.424, 0.495] | 0.328..0.648 | 3.233 [3.063, 3.400] | 2.326..4.073 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.431 [0.401, 0.465] | 0.328..0.568 | 3.375 [3.211, 3.531] | 2.605..4.126 |

### D=7,h=3

Cell `D=7,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.420 [0.394, 0.450] | 0.322..0.550 | 3.713 [3.510, 3.891] | 2.684..4.707 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.415 [0.386, 0.444] | 0.239..0.528 | 3.610 [3.421, 3.775] | 2.687..4.455 |
| Markov1(a=1,cut=24h,hl=24h) | 0.414 [0.387, 0.445] | 0.306..0.550 | 3.517 [3.327, 3.687] | 2.594..4.413 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.413 [0.383, 0.444] | 0.222..0.567 | 3.500 [3.318, 3.671] | 2.599..4.371 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.412 [0.381, 0.447] | 0.244..0.550 | 3.337 [3.149, 3.509] | 2.461..4.059 |
| LastObservation | 0.411 [0.381, 0.441] | 0.306..0.550 | 4.008 [3.807, 4.185] | 3.108..4.736 |
| MostFrequentLocation(hl=24h) | 0.408 [0.378, 0.443] | 0.244..0.550 | 3.517 [3.327, 3.687] | 2.594..4.413 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.387 [0.359, 0.421] | 0.239..0.528 | 3.678 [3.508, 3.834] | 2.849..4.466 |

### D=7,h=7

Cell `D=7,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.452 [0.427, 0.482] | 0.356..0.597 | 3.364 [3.179, 3.533] | 2.401..4.153 |
| SmoothedRecency(hl=6h,freq=24h) | 0.450 [0.422, 0.482] | 0.319..0.611 | 3.456 [3.248, 3.626] | 2.385..4.112 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.450 [0.425, 0.480] | 0.353..0.597 | 3.434 [3.246, 3.600] | 2.441..4.154 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.447 [0.419, 0.482] | 0.319..0.622 | 3.258 [3.062, 3.435] | 2.263..4.106 |
| MostFrequentLocation(hl=24h) | 0.447 [0.420, 0.480] | 0.353..0.611 | 3.354 [3.165, 3.523] | 2.307..4.127 |
| Markov1(a=1,cut=24h,hl=24h) | 0.447 [0.418, 0.481] | 0.319..0.611 | 3.354 [3.165, 3.523] | 2.307..4.127 |
| LastObservation | 0.442 [0.414, 0.476] | 0.319..0.611 | 3.805 [3.582, 3.988] | 2.617..4.473 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.429 [0.402, 0.462] | 0.339..0.589 | 3.488 [3.306, 3.653] | 2.566..4.233 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 20 households, 1603 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.514 [0.461, 0.564] | 0.244..0.729 | 3.012 [2.672, 3.369] | 1.463..4.710 |
| MostFrequentLocation(hl=24h) | 0.506 [0.455, 0.554] | 0.282..0.729 | 2.907 [2.608, 3.225] | 1.503..4.444 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.505 [0.453, 0.555] | 0.244..0.729 | 2.845 [2.575, 3.135] | 1.550..4.342 |
| LastObservation | 0.498 [0.441, 0.551] | 0.282..0.729 | 3.258 [2.949, 3.586] | 1.869..4.986 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.495 [0.444, 0.546] | 0.282..0.718 | 3.000 [2.709, 3.313] | 1.586..4.425 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.486 [0.430, 0.540] | 0.269..0.706 | 2.961 [2.684, 3.265] | 1.687..4.459 |
| Markov1(a=1,cut=24h,hl=24h) | 0.480 [0.424, 0.533] | 0.269..0.729 | 3.232 [3.005, 3.485] | 2.522..4.660 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.474 [0.427, 0.515] | 0.273..0.659 | 3.101 [2.846, 3.369] | 1.842..4.503 |

### D=10,h=3

Cell `D=10,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.440 [0.403, 0.478] | 0.294..0.628 | 3.379 [3.126, 3.638] | 2.039..4.607 |
| SmoothedRecency(hl=6h,freq=24h) | 0.439 [0.402, 0.476] | 0.300..0.628 | 3.465 [3.212, 3.727] | 2.096..4.598 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.438 [0.399, 0.479] | 0.289..0.650 | 3.393 [3.135, 3.649] | 2.065..4.632 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.437 [0.399, 0.474] | 0.272..0.633 | 3.480 [3.235, 3.733] | 2.232..4.666 |
| Markov1(a=1,cut=24h,hl=24h) | 0.435 [0.397, 0.475] | 0.283..0.628 | 3.379 [3.126, 3.638] | 2.039..4.607 |
| LastObservation | 0.434 [0.393, 0.474] | 0.283..0.628 | 3.830 [3.572, 4.093] | 2.571..4.974 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.432 [0.395, 0.469] | 0.300..0.628 | 3.308 [3.059, 3.565] | 2.009..4.581 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.416 [0.383, 0.447] | 0.272..0.567 | 3.558 [3.330, 3.796] | 2.440..4.794 |

### D=10,h=7

Cell `D=10,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.422 [0.390, 0.459] | 0.283..0.631 | 3.438 [3.223, 3.618] | 2.313..4.115 |
| SmoothedRecency(hl=6h,freq=24h) | 0.415 [0.383, 0.450] | 0.269..0.572 | 3.586 [3.329, 3.790] | 2.344..4.274 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.412 [0.377, 0.451] | 0.269..0.572 | 3.348 [3.140, 3.527] | 2.328..4.080 |
| Markov1(a=1,cut=24h,hl=24h) | 0.409 [0.377, 0.444] | 0.269..0.572 | 3.466 [3.244, 3.649] | 2.365..4.140 |
| MostFrequentLocation(hl=24h) | 0.407 [0.382, 0.439] | 0.286..0.572 | 3.466 [3.244, 3.649] | 2.365..4.140 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.404 [0.376, 0.438] | 0.283..0.589 | 3.543 [3.323, 3.722] | 2.477..4.170 |
| LastObservation | 0.402 [0.371, 0.437] | 0.269..0.572 | 3.941 [3.720, 4.124] | 2.955..4.548 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.399 [0.372, 0.430] | 0.264..0.561 | 3.577 [3.369, 3.750] | 2.506..4.185 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 20 households, 1664 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.516 [0.473, 0.562] | 0.361..0.765 | 2.783 [2.533, 3.018] | 1.392..3.759 |
| MostFrequentLocation(hl=24h) | 0.510 [0.468, 0.560] | 0.361..0.765 | 2.939 [2.646, 3.212] | 1.363..3.909 |
| LastObservation | 0.508 [0.462, 0.557] | 0.311..0.765 | 3.339 [3.033, 3.635] | 1.625..4.451 |
| SmoothedRecency(hl=6h,freq=24h) | 0.508 [0.460, 0.557] | 0.311..0.765 | 3.100 [2.748, 3.437] | 1.333..4.301 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.507 [0.465, 0.552] | 0.361..0.753 | 3.060 [2.764, 3.340] | 1.414..4.251 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.485 [0.442, 0.532] | 0.361..0.659 | 2.952 [2.692, 3.193] | 1.629..3.785 |
| Markov1(a=1,cut=24h,hl=24h) | 0.480 [0.439, 0.526] | 0.361..0.659 | 3.131 [2.926, 3.326] | 2.315..3.815 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.463 [0.424, 0.506] | 0.311..0.635 | 3.166 [2.901, 3.409] | 1.885..4.090 |

### D=14,h=3

Cell `D=14,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.442 [0.402, 0.488] | 0.294..0.650 | 3.180 [2.967, 3.368] | 2.239..3.832 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.439 [0.400, 0.484] | 0.311..0.639 | 3.451 [3.198, 3.681] | 2.250..4.294 |
| MostFrequentLocation(hl=24h) | 0.436 [0.393, 0.485] | 0.294..0.650 | 3.334 [3.098, 3.550] | 2.231..4.056 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.435 [0.397, 0.477] | 0.322..0.656 | 3.325 [3.100, 3.531] | 2.226..4.110 |
| Markov1(a=1,cut=24h,hl=24h) | 0.434 [0.391, 0.482] | 0.294..0.650 | 3.334 [3.098, 3.550] | 2.231..4.056 |
| SmoothedRecency(hl=6h,freq=24h) | 0.433 [0.391, 0.481] | 0.278..0.650 | 3.549 [3.260, 3.808] | 2.220..4.379 |
| LastObservation | 0.433 [0.393, 0.481] | 0.278..0.639 | 3.855 [3.558, 4.120] | 2.494..4.678 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.412 [0.374, 0.454] | 0.272..0.611 | 3.501 [3.263, 3.716] | 2.316..4.251 |

### D=14,h=7

Cell `D=14,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.452 [0.422, 0.483] | 0.303..0.578 | 3.228 [3.060, 3.395] | 2.636..4.040 |
| MostFrequentLocation(hl=24h) | 0.448 [0.419, 0.481] | 0.303..0.575 | 3.340 [3.162, 3.510] | 2.719..4.216 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.447 [0.423, 0.476] | 0.353..0.553 | 3.325 [3.158, 3.486] | 2.727..4.131 |
| Markov1(a=1,cut=24h,hl=24h) | 0.447 [0.416, 0.481] | 0.303..0.578 | 3.340 [3.162, 3.510] | 2.719..4.216 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.447 [0.421, 0.474] | 0.317..0.561 | 3.462 [3.283, 3.630] | 2.789..4.378 |
| SmoothedRecency(hl=6h,freq=24h) | 0.445 [0.414, 0.477] | 0.303..0.575 | 3.479 [3.290, 3.658] | 2.902..4.396 |
| LastObservation | 0.437 [0.410, 0.466] | 0.303..0.531 | 3.837 [3.639, 4.030] | 3.210..4.816 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.420 [0.393, 0.450] | 0.269..0.542 | 3.515 [3.340, 3.680] | 2.832..4.431 |
