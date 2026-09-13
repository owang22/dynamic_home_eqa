# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 20 households, 1635 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.504 [0.466, 0.548] | 0.356..0.730 | 3.193 [2.882, 3.480] | 1.446..4.063 |
| LastObservation | 0.503 [0.463, 0.547] | 0.378..0.730 | 3.396 [3.107, 3.662] | 1.863..4.277 |
| MostFrequentLocation(hl=24h) | 0.497 [0.463, 0.537] | 0.356..0.697 | 3.077 [2.801, 3.314] | 1.503..3.763 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.495 [0.456, 0.537] | 0.329..0.730 | 2.873 [2.654, 3.056] | 1.516..3.377 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.486 [0.446, 0.532] | 0.329..0.697 | 3.155 [2.850, 3.418] | 1.460..3.896 |
| Markov1(a=1,cut=24h,hl=24h) | 0.485 [0.448, 0.523] | 0.341..0.708 | 3.308 [3.132, 3.462] | 2.346..3.937 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.480 [0.437, 0.525] | 0.318..0.708 | 3.109 [2.841, 3.339] | 1.559..3.716 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.468 [0.431, 0.513] | 0.294..0.674 | 3.226 [2.945, 3.465] | 1.580..3.988 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.930 (n=85) | 0.586 (n=3976) | 0.452 (n=17197) | 0.395 (n=50741) |
| MostFrequentLocation(hl=24h) | 0.899 (n=85) | 0.582 (n=3976) | 0.456 (n=17197) | 0.404 (n=50741) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.646 (n=85) | 0.551 (n=3976) | 0.438 (n=17197) | 0.393 (n=50741) |
| Markov1(a=1,cut=24h,hl=24h) | 0.861 (n=85) | 0.530 (n=3976) | 0.455 (n=17197) | 0.404 (n=50741) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.922 (n=85) | 0.585 (n=3976) | 0.452 (n=17197) | 0.401 (n=50741) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.876 (n=85) | 0.562 (n=3976) | 0.455 (n=17197) | 0.407 (n=50741) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.896 (n=85) | 0.583 (n=3976) | 0.455 (n=17197) | 0.401 (n=50741) |
| SmoothedRecency(hl=6h,freq=24h) | 0.930 (n=85) | 0.587 (n=3976) | 0.454 (n=17197) | 0.397 (n=50741) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| households__generated__gpt-5.6-terra__hh_001__seed4 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.476) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.007) |
| households__generated__gpt-5.6-terra__hh_002__seed4 | MostFrequentLocation(hl=24h) (0.439) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.377) |
| households__generated__gpt-5.6-terra__hh_003__seed4 | MostFrequentLocation(hl=24h) (0.483) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.278) |
| households__generated__gpt-5.6-terra__hh_004__seed4 | LastObservation (0.413) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.296) |
| households__generated__gpt-5.6-terra__hh_005__seed4 | LastObservation (0.493) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.325) |
| households__generated__gpt-5.6-terra__hh_006__seed4 | LastObservation (0.388) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.197) |
| households__generated__gpt-5.6-terra__hh_007__seed4 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.529) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.868) |
| households__generated__gpt-5.6-terra__hh_008__seed4 | TimetableLookup(bin=1h,days=all,hl=24h) (0.519) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.781) |
| households__generated__gpt-5.6-terra__hh_009__seed4 | Markov1(a=1,cut=24h,hl=24h) (0.549) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.609) |
| households__generated__gpt-5.6-terra__hh_010__seed4 | LastObservation (0.384) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.204) |
| households__generated__gpt-5.6-terra__hh_011__seed4 | LastObservation (0.643) | SmoothedRecency(hl=6h,freq=24h) (2.348) |
| households__generated__gpt-5.6-terra__hh_012__seed4 | LastObservation (0.528) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.658) |
| households__generated__gpt-5.6-terra__hh_013__seed4 | LastObservation (0.532) | MostFrequentLocation(hl=24h) (3.148) |
| households__generated__gpt-5.6-terra__hh_014__seed4 | Markov1(a=1,cut=24h,hl=24h) (0.600) | SmoothedRecency(hl=6h,freq=24h) (2.681) |
| households__generated__gpt-5.6-terra__hh_015__seed4 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.548) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.833) |
| households__generated__gpt-5.6-terra__hh_016__seed4 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.683) | SmoothedRecency(hl=6h,freq=24h) (2.027) |
| households__generated__gpt-5.6-terra__hh_017__seed4 | Markov1(a=1,cut=24h,hl=24h) (0.461) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.206) |
| households__generated__gpt-5.6-terra__hh_018__seed4 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.528) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.760) |
| households__generated__gpt-5.6-terra__hh_019__seed4 | Markov1(a=1,cut=24h,hl=24h) (0.466) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.047) |
| households__generated__gpt-5.6-terra__hh_020__seed4 | LastObservation (0.730) | SmoothedRecency(hl=6h,freq=24h) (1.446) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 20 households, 1800 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.397 [0.358, 0.435] | 0.244..0.600 | 3.813 [3.564, 4.057] | 2.418..4.652 |
| SmoothedRecency(hl=6h,freq=24h) | 0.392 [0.349, 0.437] | 0.211..0.600 | 3.841 [3.604, 4.086] | 2.514..4.721 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.389 [0.354, 0.430] | 0.244..0.600 | 3.830 [3.580, 4.078] | 2.479..4.710 |
| MostFrequentLocation(hl=24h) | 0.388 [0.343, 0.436] | 0.211..0.600 | 3.813 [3.564, 4.057] | 2.418..4.652 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.384 [0.342, 0.432] | 0.211..0.600 | 3.648 [3.445, 3.836] | 2.506..4.283 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.381 [0.338, 0.425] | 0.211..0.600 | 3.840 [3.584, 4.082] | 2.479..4.756 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.373 [0.323, 0.422] | 0.178..0.600 | 3.815 [3.571, 4.055] | 2.479..4.652 |
| LastObservation | 0.368 [0.319, 0.418] | 0.178..0.600 | 4.043 [3.781, 4.310] | 2.763..5.004 |

### D=1,h=7

Cell `D=1,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.413 [0.385, 0.442] | 0.325..0.544 | 3.741 [3.566, 3.931] | 2.958..4.730 |
| SmoothedRecency(hl=6h,freq=24h) | 0.406 [0.366, 0.441] | 0.228..0.544 | 3.777 [3.597, 3.965] | 2.984..4.730 |
| MostFrequentLocation(hl=24h) | 0.399 [0.365, 0.432] | 0.228..0.544 | 3.741 [3.566, 3.931] | 2.958..4.730 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.397 [0.364, 0.429] | 0.228..0.525 | 3.756 [3.579, 3.944] | 2.980..4.730 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.393 [0.354, 0.431] | 0.228..0.544 | 3.628 [3.464, 3.805] | 2.898..4.471 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.392 [0.355, 0.427] | 0.228..0.519 | 3.768 [3.590, 3.957] | 2.994..4.730 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.389 [0.353, 0.425] | 0.228..0.544 | 3.743 [3.569, 3.933] | 2.976..4.730 |
| LastObservation | 0.384 [0.349, 0.417] | 0.228..0.528 | 3.976 [3.791, 4.155] | 3.189..4.730 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 20 households, 1637 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.467 [0.421, 0.513] | 0.287..0.691 | 3.320 [3.076, 3.538] | 2.163..3.977 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.464 [0.425, 0.509] | 0.314..0.667 | 3.332 [3.086, 3.550] | 2.242..3.988 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.462 [0.417, 0.513] | 0.333..0.691 | 3.183 [2.972, 3.391] | 2.134..4.018 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.462 [0.417, 0.508] | 0.314..0.679 | 3.341 [3.101, 3.553] | 2.259..3.957 |
| LastObservation | 0.456 [0.409, 0.506] | 0.300..0.691 | 3.527 [3.253, 3.781] | 2.141..4.621 |
| SmoothedRecency(hl=6h,freq=24h) | 0.452 [0.406, 0.501] | 0.300..0.691 | 3.341 [3.065, 3.593] | 2.005..4.144 |
| MostFrequentLocation(hl=24h) | 0.448 [0.399, 0.500] | 0.287..0.704 | 3.301 [3.046, 3.530] | 2.155..3.960 |
| Markov1(a=1,cut=24h,hl=24h) | 0.447 [0.404, 0.494] | 0.267..0.691 | 3.663 [3.494, 3.837] | 2.858..4.460 |

### D=3,h=3

Cell `D=3,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.433 [0.402, 0.466] | 0.322..0.589 | 3.516 [3.312, 3.716] | 2.890..4.396 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.432 [0.393, 0.471] | 0.217..0.594 | 3.472 [3.264, 3.678] | 2.889..4.356 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.431 [0.402, 0.463] | 0.328..0.594 | 3.336 [3.155, 3.517] | 2.777..4.115 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.427 [0.392, 0.461] | 0.250..0.528 | 3.452 [3.240, 3.658] | 2.842..4.355 |
| Markov1(a=1,cut=24h,hl=24h) | 0.426 [0.397, 0.455] | 0.278..0.533 | 3.450 [3.234, 3.656] | 2.848..4.350 |
| MostFrequentLocation(hl=24h) | 0.422 [0.382, 0.462] | 0.211..0.594 | 3.450 [3.234, 3.656] | 2.848..4.350 |
| LastObservation | 0.422 [0.390, 0.456] | 0.289..0.544 | 3.777 [3.568, 3.971] | 2.933..4.601 |
| SmoothedRecency(hl=6h,freq=24h) | 0.417 [0.379, 0.456] | 0.211..0.533 | 3.530 [3.301, 3.752] | 2.799..4.557 |

### D=3,h=7

Cell `D=3,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.392 [0.354, 0.425] | 0.217..0.525 | 3.733 [3.572, 3.891] | 2.816..4.413 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.389 [0.360, 0.416] | 0.222..0.486 | 3.769 [3.615, 3.927] | 2.907..4.417 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.384 [0.364, 0.404] | 0.292..0.483 | 3.611 [3.468, 3.765] | 2.831..4.261 |
| Markov1(a=1,cut=24h,hl=24h) | 0.384 [0.358, 0.409] | 0.256..0.489 | 3.738 [3.573, 3.902] | 2.799..4.417 |
| LastObservation | 0.380 [0.350, 0.410] | 0.256..0.467 | 4.124 [3.961, 4.304] | 3.581..4.893 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.380 [0.352, 0.404] | 0.219..0.478 | 3.789 [3.638, 3.946] | 2.950..4.452 |
| MostFrequentLocation(hl=24h) | 0.376 [0.344, 0.405] | 0.217..0.489 | 3.738 [3.573, 3.902] | 2.799..4.417 |
| SmoothedRecency(hl=6h,freq=24h) | 0.372 [0.337, 0.401] | 0.217..0.489 | 3.812 [3.628, 3.997] | 2.748..4.489 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 20 households, 1632 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.460 [0.409, 0.509] | 0.267..0.633 | 3.440 [3.130, 3.757] | 2.277..4.591 |
| SmoothedRecency(hl=6h,freq=24h) | 0.457 [0.404, 0.509] | 0.241..0.653 | 3.446 [3.138, 3.764] | 2.245..4.545 |
| MostFrequentLocation(hl=24h) | 0.456 [0.404, 0.509] | 0.267..0.633 | 3.415 [3.105, 3.733] | 2.304..4.577 |
| LastObservation | 0.455 [0.404, 0.509] | 0.241..0.640 | 3.615 [3.288, 3.945] | 2.413..4.891 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.453 [0.399, 0.507] | 0.241..0.633 | 3.392 [3.083, 3.709] | 2.306..4.589 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.406, 0.496] | 0.244..0.629 | 3.430 [3.123, 3.747] | 2.281..4.654 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.447 [0.394, 0.497] | 0.220..0.622 | 3.501 [3.192, 3.818] | 2.309..4.824 |
| Markov1(a=1,cut=24h,hl=24h) | 0.422 [0.376, 0.469] | 0.253..0.607 | 3.906 [3.662, 4.161] | 2.893..5.069 |

### D=5,h=3

Cell `D=5,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.409 [0.370, 0.443] | 0.244..0.528 | 3.689 [3.490, 3.911] | 2.745..4.537 |
| MostFrequentLocation(hl=24h) | 0.404 [0.363, 0.442] | 0.233..0.572 | 3.702 [3.499, 3.924] | 2.717..4.546 |
| LastObservation | 0.396 [0.355, 0.435] | 0.183..0.594 | 4.023 [3.785, 4.285] | 2.852..4.985 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.392 [0.345, 0.433] | 0.211..0.594 | 3.741 [3.532, 3.965] | 2.715..4.645 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.389 [0.349, 0.430] | 0.183..0.533 | 3.629 [3.435, 3.837] | 2.764..4.474 |
| Markov1(a=1,cut=24h,hl=24h) | 0.386 [0.338, 0.430] | 0.183..0.572 | 3.702 [3.499, 3.924] | 2.717..4.546 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.381 [0.339, 0.421] | 0.200..0.567 | 3.765 [3.566, 3.988] | 2.753..4.620 |
| SmoothedRecency(hl=6h,freq=24h) | 0.381 [0.334, 0.423] | 0.183..0.533 | 3.749 [3.550, 3.982] | 2.824..4.539 |

### D=5,h=7

Cell `D=5,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.400 [0.367, 0.434] | 0.236..0.544 | 3.696 [3.518, 3.899] | 3.000..4.809 |
| MostFrequentLocation(hl=24h) | 0.395 [0.360, 0.431] | 0.236..0.556 | 3.707 [3.523, 3.920] | 2.964..4.877 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.391 [0.348, 0.430] | 0.156..0.553 | 3.748 [3.564, 3.957] | 3.010..4.883 |
| LastObservation | 0.381 [0.343, 0.423] | 0.214..0.556 | 4.058 [3.827, 4.295] | 3.070..5.242 |
| Markov1(a=1,cut=24h,hl=24h) | 0.378 [0.335, 0.418] | 0.214..0.556 | 3.707 [3.523, 3.920] | 2.964..4.877 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.371 [0.332, 0.411] | 0.214..0.542 | 3.763 [3.582, 3.975] | 3.017..4.876 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.366 [0.328, 0.407] | 0.214..0.556 | 3.605 [3.426, 3.817] | 2.974..4.797 |
| SmoothedRecency(hl=6h,freq=24h) | 0.365 [0.326, 0.406] | 0.153..0.556 | 3.798 [3.591, 4.029] | 2.955..5.082 |

### D=7,h=0.25

Cell `D=7,h=0.25`: 20 households, 165 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.792 [0.696, 0.892] | 0.370..1.000 | 1.457 [0.794, 2.121] | 0.000..4.349 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.789 [0.696, 0.887] | 0.370..1.000 | 1.657 [1.094, 2.195] | 0.185..3.680 |
| SmoothedRecency(hl=6h,freq=24h) | 0.776 [0.683, 0.869] | 0.370..1.000 | 1.440 [0.790, 2.073] | 0.000..4.168 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.775 [0.679, 0.876] | 0.370..1.000 | 1.479 [0.851, 2.117] | 0.000..4.118 |
| MostFrequentLocation(hl=24h) | 0.773 [0.679, 0.867] | 0.370..1.000 | 1.577 [0.991, 2.151] | 0.000..3.984 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.748 [0.648, 0.855] | 0.370..1.000 | 1.734 [1.138, 2.300] | 0.000..3.881 |
| Markov1(a=1,cut=24h,hl=24h) | 0.682 [0.567, 0.805] | 0.000..1.000 | 2.968 [2.531, 3.354] | 1.450..4.725 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.659 [0.540, 0.774] | 0.000..1.000 | 1.973 [1.341, 2.526] | 0.000..4.235 |

### D=7,h=1

Cell `D=7,h=1`: 20 households, 1635 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.504 [0.466, 0.548] | 0.356..0.730 | 3.193 [2.882, 3.480] | 1.446..4.063 |
| LastObservation | 0.503 [0.463, 0.547] | 0.378..0.730 | 3.396 [3.107, 3.662] | 1.863..4.277 |
| MostFrequentLocation(hl=24h) | 0.497 [0.463, 0.537] | 0.356..0.697 | 3.077 [2.801, 3.314] | 1.503..3.763 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.495 [0.456, 0.537] | 0.329..0.730 | 2.873 [2.654, 3.056] | 1.516..3.377 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.486 [0.446, 0.532] | 0.329..0.697 | 3.155 [2.850, 3.418] | 1.460..3.896 |
| Markov1(a=1,cut=24h,hl=24h) | 0.485 [0.448, 0.523] | 0.341..0.708 | 3.308 [3.132, 3.462] | 2.346..3.937 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.480 [0.437, 0.525] | 0.318..0.708 | 3.109 [2.841, 3.339] | 1.559..3.716 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.468 [0.431, 0.513] | 0.294..0.674 | 3.226 [2.945, 3.465] | 1.580..3.988 |

### D=7,h=3

Cell `D=7,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.454 [0.423, 0.491] | 0.333..0.650 | 3.141 [2.942, 3.320] | 2.145..3.935 |
| Markov1(a=1,cut=24h,hl=24h) | 0.453 [0.418, 0.489] | 0.328..0.650 | 3.315 [3.094, 3.513] | 2.136..4.171 |
| LastObservation | 0.452 [0.416, 0.489] | 0.306..0.650 | 3.721 [3.468, 3.944] | 2.418..4.663 |
| SmoothedRecency(hl=6h,freq=24h) | 0.451 [0.414, 0.488] | 0.322..0.650 | 3.451 [3.202, 3.672] | 2.103..4.334 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.412, 0.489] | 0.261..0.644 | 3.309 [3.100, 3.497] | 2.132..4.051 |
| MostFrequentLocation(hl=24h) | 0.450 [0.416, 0.485] | 0.328..0.650 | 3.315 [3.094, 3.513] | 2.136..4.171 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.446 [0.411, 0.484] | 0.283..0.644 | 3.403 [3.181, 3.596] | 2.240..4.277 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.431 [0.396, 0.467] | 0.311..0.628 | 3.441 [3.240, 3.622] | 2.403..4.230 |

### D=7,h=7

Cell `D=7,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.464 [0.434, 0.497] | 0.356..0.594 | 3.281 [3.107, 3.435] | 2.579..3.714 |
| LastObservation | 0.463 [0.433, 0.496] | 0.339..0.594 | 3.656 [3.453, 3.851] | 2.798..4.567 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.463 [0.436, 0.493] | 0.339..0.594 | 3.158 [2.969, 3.322] | 2.349..3.706 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.463 [0.434, 0.496] | 0.347..0.600 | 3.306 [3.132, 3.463] | 2.600..3.798 |
| MostFrequentLocation(hl=24h) | 0.462 [0.432, 0.495] | 0.356..0.594 | 3.281 [3.107, 3.435] | 2.579..3.714 |
| SmoothedRecency(hl=6h,freq=24h) | 0.462 [0.431, 0.495] | 0.356..0.589 | 3.377 [3.203, 3.533] | 2.691..3.807 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.457 [0.428, 0.490] | 0.336..0.594 | 3.368 [3.190, 3.522] | 2.631..3.777 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.444 [0.414, 0.480] | 0.328..0.581 | 3.409 [3.228, 3.570] | 2.641..3.862 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 20 households, 1626 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.485 [0.435, 0.540] | 0.258..0.759 | 2.968 [2.663, 3.278] | 1.548..4.743 |
| MostFrequentLocation(hl=24h) | 0.484 [0.434, 0.536] | 0.242..0.759 | 3.068 [2.738, 3.392] | 1.452..4.904 |
| SmoothedRecency(hl=6h,freq=24h) | 0.482 [0.432, 0.535] | 0.242..0.759 | 3.220 [2.842, 3.568] | 1.392..4.915 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.479 [0.426, 0.538] | 0.242..0.770 | 3.175 [2.826, 3.505] | 1.469..4.913 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.475 [0.426, 0.527] | 0.242..0.711 | 3.096 [2.797, 3.393] | 1.678..4.877 |
| LastObservation | 0.474 [0.421, 0.535] | 0.242..0.770 | 3.416 [3.038, 3.758] | 1.604..4.972 |
| Markov1(a=1,cut=24h,hl=24h) | 0.473 [0.422, 0.528] | 0.258..0.759 | 3.297 [3.047, 3.577] | 2.346..4.800 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.460 [0.410, 0.516] | 0.242..0.759 | 3.219 [2.920, 3.522] | 1.687..4.937 |

### D=10,h=3

Cell `D=10,h=3`: 20 households, 3599 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.434 [0.402, 0.470] | 0.317..0.656 | 3.492 [3.263, 3.730] | 2.410..4.457 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.433 [0.401, 0.467] | 0.306..0.633 | 3.495 [3.266, 3.742] | 2.375..4.444 |
| SmoothedRecency(hl=6h,freq=24h) | 0.431 [0.398, 0.467] | 0.317..0.644 | 3.594 [3.349, 3.840] | 2.321..4.497 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.429 [0.397, 0.461] | 0.328..0.622 | 3.375 [3.152, 3.614] | 2.364..4.426 |
| Markov1(a=1,cut=24h,hl=24h) | 0.428 [0.396, 0.463] | 0.328..0.656 | 3.492 [3.263, 3.730] | 2.410..4.457 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.427 [0.393, 0.461] | 0.311..0.622 | 3.564 [3.339, 3.797] | 2.523..4.494 |
| LastObservation | 0.424 [0.392, 0.460] | 0.317..0.622 | 3.864 [3.650, 4.077] | 2.610..4.559 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.410 [0.379, 0.443] | 0.306..0.594 | 3.636 [3.413, 3.870] | 2.581..4.620 |

### D=10,h=7

Cell `D=10,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.418 [0.387, 0.449] | 0.286..0.569 | 3.553 [3.373, 3.722] | 2.709..4.203 |
| Markov1(a=1,cut=24h,hl=24h) | 0.409 [0.377, 0.445] | 0.272..0.544 | 3.579 [3.399, 3.750] | 2.681..4.239 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.407 [0.370, 0.443] | 0.247..0.544 | 3.456 [3.288, 3.628] | 2.665..4.055 |
| MostFrequentLocation(hl=24h) | 0.405 [0.376, 0.438] | 0.269..0.544 | 3.579 [3.399, 3.750] | 2.681..4.239 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.403 [0.376, 0.436] | 0.306..0.547 | 3.689 [3.523, 3.849] | 2.900..4.315 |
| SmoothedRecency(hl=6h,freq=24h) | 0.395 [0.362, 0.431] | 0.247..0.544 | 3.708 [3.507, 3.891] | 2.712..4.420 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.395 [0.362, 0.426] | 0.261..0.558 | 3.651 [3.483, 3.811] | 2.856..4.307 |
| LastObservation | 0.391 [0.356, 0.426] | 0.244..0.544 | 3.991 [3.803, 4.165] | 3.147..4.695 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 20 households, 1647 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.502 [0.464, 0.547] | 0.390..0.700 | 3.083 [2.827, 3.297] | 1.900..3.873 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.494 [0.452, 0.541] | 0.342..0.700 | 2.942 [2.720, 3.127] | 1.918..3.646 |
| SmoothedRecency(hl=6h,freq=24h) | 0.493 [0.449, 0.540] | 0.342..0.711 | 3.207 [2.903, 3.478] | 1.858..4.009 |
| LastObservation | 0.493 [0.457, 0.535] | 0.366..0.671 | 3.456 [3.169, 3.703] | 2.275..4.406 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.491 [0.451, 0.535] | 0.329..0.683 | 3.211 [2.931, 3.463] | 1.940..4.095 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.471 [0.427, 0.519] | 0.310..0.644 | 3.173 [2.923, 3.394] | 2.007..4.041 |
| Markov1(a=1,cut=24h,hl=24h) | 0.461 [0.417, 0.508] | 0.329..0.671 | 3.306 [3.120, 3.466] | 2.444..3.774 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.455 [0.417, 0.498] | 0.345..0.656 | 3.333 [3.078, 3.567] | 2.070..4.110 |

### D=14,h=3

Cell `D=14,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.411 [0.386, 0.442] | 0.322..0.578 | 3.551 [3.361, 3.721] | 2.331..4.328 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.411 [0.383, 0.443] | 0.294..0.578 | 3.370 [3.191, 3.538] | 2.325..4.088 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.408 [0.380, 0.442] | 0.322..0.628 | 3.667 [3.470, 3.843] | 2.382..4.415 |
| SmoothedRecency(hl=6h,freq=24h) | 0.407 [0.374, 0.443] | 0.244..0.611 | 3.790 [3.554, 3.996] | 2.415..4.548 |
| LastObservation | 0.403 [0.372, 0.440] | 0.244..0.600 | 4.073 [3.848, 4.257] | 2.786..4.705 |
| Markov1(a=1,cut=24h,hl=24h) | 0.402 [0.368, 0.439] | 0.244..0.611 | 3.551 [3.361, 3.721] | 2.331..4.328 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.400 [0.367, 0.436] | 0.228..0.611 | 3.522 [3.329, 3.691] | 2.349..4.298 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.383 [0.355, 0.415] | 0.250..0.556 | 3.710 [3.528, 3.866] | 2.476..4.386 |

### D=14,h=7

Cell `D=14,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.463 [0.441, 0.490] | 0.356..0.572 | 3.290 [3.141, 3.438] | 2.753..4.014 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.463 [0.440, 0.490] | 0.347..0.572 | 3.176 [3.033, 3.314] | 2.730..3.779 |
| SmoothedRecency(hl=6h,freq=24h) | 0.460 [0.436, 0.488] | 0.356..0.558 | 3.409 [3.238, 3.572] | 2.700..4.099 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.459 [0.435, 0.484] | 0.372..0.569 | 3.292 [3.153, 3.428] | 2.798..3.984 |
| Markov1(a=1,cut=24h,hl=24h) | 0.458 [0.433, 0.485] | 0.347..0.558 | 3.290 [3.141, 3.438] | 2.753..4.014 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.457 [0.436, 0.480] | 0.369..0.547 | 3.398 [3.263, 3.535] | 2.861..4.093 |
| LastObservation | 0.448 [0.424, 0.472] | 0.339..0.533 | 3.765 [3.613, 3.917] | 3.195..4.573 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.435 [0.411, 0.461] | 0.333..0.528 | 3.453 [3.320, 3.589] | 2.959..4.161 |
