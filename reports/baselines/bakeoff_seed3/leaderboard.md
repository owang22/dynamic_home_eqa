# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 20 households, 1657 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.492 [0.452, 0.534] | 0.329..0.678 | 3.180 [2.957, 3.406] | 2.311..4.241 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.482 [0.436, 0.528] | 0.278..0.678 | 3.272 [3.032, 3.521] | 2.278..4.432 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.476 [0.434, 0.521] | 0.329..0.678 | 2.996 [2.812, 3.195] | 2.389..4.041 |
| SmoothedRecency(hl=6h,freq=24h) | 0.476 [0.441, 0.516] | 0.329..0.678 | 3.331 [3.055, 3.595] | 2.194..4.458 |
| LastObservation | 0.475 [0.440, 0.516] | 0.329..0.678 | 3.533 [3.251, 3.818] | 2.223..4.669 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.467 [0.432, 0.507] | 0.329..0.650 | 3.209 [2.989, 3.438] | 2.333..4.136 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.455 [0.419, 0.494] | 0.329..0.621 | 3.349 [3.123, 3.579] | 2.362..4.327 |
| Markov1(a=1,cut=24h,hl=24h) | 0.452 [0.415, 0.490] | 0.266..0.644 | 3.374 [3.193, 3.561] | 2.763..4.260 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.902 (n=77) | 0.574 (n=3976) | 0.461 (n=17295) | 0.394 (n=50652) |
| MostFrequentLocation(hl=24h) | 0.905 (n=77) | 0.571 (n=3976) | 0.466 (n=17295) | 0.405 (n=50652) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.753 (n=77) | 0.535 (n=3976) | 0.445 (n=17295) | 0.390 (n=50652) |
| Markov1(a=1,cut=24h,hl=24h) | 0.772 (n=77) | 0.534 (n=3976) | 0.465 (n=17295) | 0.402 (n=50652) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.902 (n=77) | 0.573 (n=3976) | 0.462 (n=17295) | 0.397 (n=50652) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.808 (n=77) | 0.555 (n=3976) | 0.466 (n=17295) | 0.407 (n=50652) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.905 (n=77) | 0.571 (n=3976) | 0.464 (n=17295) | 0.401 (n=50652) |
| SmoothedRecency(hl=6h,freq=24h) | 0.902 (n=77) | 0.574 (n=3976) | 0.463 (n=17295) | 0.399 (n=50652) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| households__generated__gpt-5.6-terra__hh_001__seed3 | Markov1(a=1,cut=24h,hl=24h) (0.451) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.697) |
| households__generated__gpt-5.6-terra__hh_002__seed3 | LastObservation (0.329) | HierarchyBackoff(po=5,pc=5,hl=24h) (4.041) |
| households__generated__gpt-5.6-terra__hh_003__seed3 | MostFrequentLocation(hl=24h) (0.539) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.906) |
| households__generated__gpt-5.6-terra__hh_004__seed3 | HierarchyBackoff(po=5,pc=5,hl=24h) (0.507) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.812) |
| households__generated__gpt-5.6-terra__hh_005__seed3 | LastObservation (0.487) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.122) |
| households__generated__gpt-5.6-terra__hh_006__seed3 | MostFrequentLocation(hl=24h) (0.607) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.571) |
| households__generated__gpt-5.6-terra__hh_007__seed3 | LastObservation (0.463) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.252) |
| households__generated__gpt-5.6-terra__hh_008__seed3 | MostFrequentLocation(hl=24h) (0.372) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.295) |
| households__generated__gpt-5.6-terra__hh_009__seed3 | Markov1(a=1,cut=24h,hl=24h) (0.405) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.242) |
| households__generated__gpt-5.6-terra__hh_010__seed3 | LastObservation (0.412) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.172) |
| households__generated__gpt-5.6-terra__hh_011__seed3 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.650) | SmoothedRecency(hl=6h,freq=24h) (2.194) |
| households__generated__gpt-5.6-terra__hh_012__seed3 | Markov1(a=1,cut=24h,hl=24h) (0.529) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.759) |
| households__generated__gpt-5.6-terra__hh_013__seed3 | LastObservation (0.541) | SmoothedRecency(hl=6h,freq=24h) (3.085) |
| households__generated__gpt-5.6-terra__hh_014__seed3 | LastObservation (0.471) | LastObservation (3.657) |
| households__generated__gpt-5.6-terra__hh_015__seed3 | LastObservation (0.500) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.796) |
| households__generated__gpt-5.6-terra__hh_016__seed3 | LastObservation (0.678) | LastObservation (2.223) |
| households__generated__gpt-5.6-terra__hh_017__seed3 | HierarchyBackoff(po=5,pc=5,hl=24h) (0.511) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.859) |
| households__generated__gpt-5.6-terra__hh_018__seed3 | LastObservation (0.439) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.255) |
| households__generated__gpt-5.6-terra__hh_019__seed3 | MostFrequentLocation(hl=24h) (0.522) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.838) |
| households__generated__gpt-5.6-terra__hh_020__seed3 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.625) | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (2.549) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 20 households, 1800 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.413 [0.381, 0.445] | 0.311..0.578 | 3.710 [3.503, 3.929] | 2.566..4.773 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.409 [0.377, 0.444] | 0.300..0.556 | 3.762 [3.554, 3.988] | 2.655..4.773 |
| LastObservation | 0.407 [0.380, 0.436] | 0.300..0.556 | 3.932 [3.721, 4.136] | 2.894..4.759 |
| Markov1(a=1,cut=24h,hl=24h) | 0.402 [0.358, 0.447] | 0.189..0.578 | 3.710 [3.503, 3.929] | 2.566..4.773 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.401 [0.360, 0.439] | 0.189..0.578 | 3.710 [3.502, 3.929] | 2.566..4.773 |
| SmoothedRecency(hl=6h,freq=24h) | 0.399 [0.357, 0.441] | 0.189..0.611 | 3.750 [3.541, 3.973] | 2.637..4.759 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.397 [0.355, 0.438] | 0.189..0.578 | 3.622 [3.400, 3.852] | 2.437..4.706 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.386 [0.346, 0.423] | 0.189..0.567 | 3.746 [3.535, 3.973] | 2.597..4.773 |

### D=1,h=7

Cell `D=1,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.415 [0.383, 0.448] | 0.303..0.628 | 3.765 [3.541, 3.995] | 2.401..4.807 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.410 [0.375, 0.446] | 0.272..0.619 | 3.802 [3.582, 4.025] | 2.453..4.807 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.401 [0.362, 0.439] | 0.211..0.625 | 3.664 [3.435, 3.899] | 2.470..4.668 |
| Markov1(a=1,cut=24h,hl=24h) | 0.400 [0.360, 0.441] | 0.211..0.628 | 3.765 [3.541, 3.995] | 2.401..4.807 |
| SmoothedRecency(hl=6h,freq=24h) | 0.397 [0.355, 0.438] | 0.211..0.628 | 3.795 [3.563, 4.020] | 2.412..4.807 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.395 [0.352, 0.437] | 0.211..0.622 | 3.771 [3.550, 3.998] | 2.434..4.807 |
| LastObservation | 0.394 [0.356, 0.431] | 0.236..0.581 | 3.992 [3.785, 4.196] | 2.897..4.849 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.393 [0.355, 0.430] | 0.211..0.622 | 3.789 [3.569, 4.014] | 2.429..4.807 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 20 households, 1614 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.485 [0.448, 0.522] | 0.337..0.671 | 3.124 [2.899, 3.374] | 2.311..4.499 |
| SmoothedRecency(hl=6h,freq=24h) | 0.482 [0.438, 0.524] | 0.286..0.686 | 3.255 [2.990, 3.538] | 2.002..4.499 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.476 [0.436, 0.515] | 0.306..0.657 | 3.248 [3.019, 3.508] | 2.264..4.456 |
| MostFrequentLocation(hl=24h) | 0.469 [0.428, 0.515] | 0.286..0.671 | 3.215 [2.977, 3.482] | 2.156..4.432 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.467 [0.422, 0.511] | 0.286..0.686 | 3.239 [2.997, 3.501] | 2.213..4.427 |
| LastObservation | 0.461 [0.417, 0.508] | 0.286..0.686 | 3.460 [3.216, 3.715] | 2.191..4.490 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.457 [0.411, 0.499] | 0.280..0.614 | 3.286 [3.056, 3.543] | 2.342..4.427 |
| Markov1(a=1,cut=24h,hl=24h) | 0.450 [0.408, 0.491] | 0.267..0.629 | 3.644 [3.452, 3.858] | 2.971..4.744 |

### D=3,h=3

Cell `D=3,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.427 [0.394, 0.464] | 0.289..0.628 | 3.610 [3.422, 3.790] | 2.491..4.252 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.417 [0.385, 0.445] | 0.278..0.550 | 3.493 [3.315, 3.671] | 2.461..4.056 |
| SmoothedRecency(hl=6h,freq=24h) | 0.409 [0.369, 0.445] | 0.239..0.550 | 3.671 [3.455, 3.867] | 2.367..4.382 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.408 [0.375, 0.440] | 0.239..0.550 | 3.649 [3.462, 3.829] | 2.569..4.269 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.405 [0.366, 0.441] | 0.239..0.561 | 3.634 [3.441, 3.816] | 2.538..4.268 |
| Markov1(a=1,cut=24h,hl=24h) | 0.403 [0.368, 0.437] | 0.239..0.567 | 3.614 [3.417, 3.799] | 2.458..4.265 |
| LastObservation | 0.399 [0.364, 0.434] | 0.239..0.550 | 3.912 [3.756, 4.069] | 3.143..4.479 |
| MostFrequentLocation(hl=24h) | 0.397 [0.361, 0.435] | 0.239..0.567 | 3.614 [3.417, 3.799] | 2.458..4.265 |

### D=3,h=7

Cell `D=3,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.408 [0.380, 0.439] | 0.275..0.528 | 3.731 [3.611, 3.842] | 3.088..4.110 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.396 [0.374, 0.418] | 0.303..0.497 | 3.588 [3.461, 3.713] | 2.976..4.112 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.393 [0.363, 0.421] | 0.244..0.500 | 3.758 [3.634, 3.870] | 3.098..4.127 |
| SmoothedRecency(hl=6h,freq=24h) | 0.390 [0.359, 0.418] | 0.253..0.497 | 3.790 [3.635, 3.931] | 2.943..4.388 |
| Markov1(a=1,cut=24h,hl=24h) | 0.387 [0.358, 0.415] | 0.242..0.497 | 3.730 [3.600, 3.847] | 3.024..4.117 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.385 [0.355, 0.413] | 0.253..0.497 | 3.744 [3.618, 3.858] | 3.091..4.118 |
| LastObservation | 0.383 [0.357, 0.408] | 0.242..0.478 | 4.064 [3.942, 4.190] | 3.531..4.619 |
| MostFrequentLocation(hl=24h) | 0.381 [0.357, 0.407] | 0.242..0.478 | 3.730 [3.600, 3.847] | 3.024..4.117 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 20 households, 1651 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.456 [0.415, 0.497] | 0.310..0.619 | 3.428 [3.190, 3.658] | 2.523..4.421 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.450 [0.404, 0.498] | 0.295..0.643 | 3.384 [3.166, 3.608] | 2.492..4.253 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.450 [0.408, 0.496] | 0.293..0.643 | 3.453 [3.196, 3.707] | 2.483..4.390 |
| MostFrequentLocation(hl=24h) | 0.449 [0.408, 0.493] | 0.322..0.619 | 3.425 [3.187, 3.667] | 2.495..4.387 |
| SmoothedRecency(hl=6h,freq=24h) | 0.448 [0.404, 0.493] | 0.310..0.619 | 3.451 [3.194, 3.705] | 2.428..4.358 |
| LastObservation | 0.446 [0.397, 0.496] | 0.273..0.643 | 3.713 [3.410, 4.012] | 2.500..4.764 |
| Markov1(a=1,cut=24h,hl=24h) | 0.436 [0.396, 0.477] | 0.311..0.619 | 3.816 [3.636, 3.996] | 2.925..4.473 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.428 [0.382, 0.477] | 0.273..0.619 | 3.502 [3.247, 3.745] | 2.600..4.454 |

### D=5,h=3

Cell `D=5,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.430 [0.395, 0.467] | 0.250..0.611 | 3.518 [3.333, 3.671] | 2.473..4.095 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.429 [0.398, 0.463] | 0.283..0.606 | 3.518 [3.344, 3.665] | 2.534..4.096 |
| MostFrequentLocation(hl=24h) | 0.429 [0.391, 0.469] | 0.267..0.611 | 3.518 [3.333, 3.671] | 2.473..4.095 |
| SmoothedRecency(hl=6h,freq=24h) | 0.420 [0.381, 0.462] | 0.267..0.611 | 3.572 [3.366, 3.748] | 2.449..4.096 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.418 [0.386, 0.453] | 0.261..0.600 | 3.552 [3.360, 3.721] | 2.502..4.172 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.413 [0.374, 0.453] | 0.267..0.611 | 3.452 [3.290, 3.598] | 2.561..4.006 |
| LastObservation | 0.412 [0.369, 0.459] | 0.244..0.611 | 3.869 [3.627, 4.104] | 2.686..4.809 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.407 [0.367, 0.451] | 0.244..0.600 | 3.595 [3.406, 3.760] | 2.599..4.228 |

### D=5,h=7

Cell `D=5,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.410 [0.380, 0.440] | 0.258..0.494 | 3.585 [3.447, 3.730] | 3.118..4.136 |
| MostFrequentLocation(hl=24h) | 0.405 [0.374, 0.434] | 0.278..0.494 | 3.585 [3.447, 3.730] | 3.118..4.136 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.397 [0.365, 0.424] | 0.256..0.489 | 3.575 [3.439, 3.717] | 3.011..4.090 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.395 [0.365, 0.422] | 0.261..0.494 | 3.631 [3.497, 3.771] | 3.162..4.144 |
| SmoothedRecency(hl=6h,freq=24h) | 0.393 [0.359, 0.425] | 0.267..0.494 | 3.689 [3.522, 3.857] | 3.124..4.467 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.389 [0.358, 0.417] | 0.278..0.494 | 3.471 [3.343, 3.607] | 2.979..3.970 |
| LastObservation | 0.379 [0.345, 0.416] | 0.250..0.494 | 4.000 [3.815, 4.190] | 3.170..4.989 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.379 [0.345, 0.413] | 0.247..0.475 | 3.658 [3.523, 3.797] | 3.176..4.173 |

### D=7,h=0.25

(no questions in cell D=7,h=0.25)

### D=7,h=1

Cell `D=7,h=1`: 20 households, 1657 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.492 [0.452, 0.534] | 0.329..0.678 | 3.180 [2.957, 3.406] | 2.311..4.241 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.482 [0.436, 0.528] | 0.278..0.678 | 3.272 [3.032, 3.521] | 2.278..4.432 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.476 [0.434, 0.521] | 0.329..0.678 | 2.996 [2.812, 3.195] | 2.389..4.041 |
| SmoothedRecency(hl=6h,freq=24h) | 0.476 [0.441, 0.516] | 0.329..0.678 | 3.331 [3.055, 3.595] | 2.194..4.458 |
| LastObservation | 0.475 [0.440, 0.516] | 0.329..0.678 | 3.533 [3.251, 3.818] | 2.223..4.669 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.467 [0.432, 0.507] | 0.329..0.650 | 3.209 [2.989, 3.438] | 2.333..4.136 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.455 [0.419, 0.494] | 0.329..0.621 | 3.349 [3.123, 3.579] | 2.362..4.327 |
| Markov1(a=1,cut=24h,hl=24h) | 0.452 [0.415, 0.490] | 0.266..0.644 | 3.374 [3.193, 3.561] | 2.763..4.260 |

### D=7,h=3

Cell `D=7,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.449 [0.426, 0.475] | 0.350..0.556 | 3.434 [3.297, 3.557] | 2.703..3.961 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.439 [0.411, 0.472] | 0.328..0.561 | 3.268 [3.116, 3.415] | 2.660..3.958 |
| LastObservation | 0.435 [0.410, 0.461] | 0.328..0.556 | 3.827 [3.673, 3.965] | 3.136..4.306 |
| Markov1(a=1,cut=24h,hl=24h) | 0.435 [0.409, 0.463] | 0.328..0.550 | 3.434 [3.297, 3.557] | 2.703..3.961 |
| SmoothedRecency(hl=6h,freq=24h) | 0.434 [0.406, 0.466] | 0.328..0.561 | 3.555 [3.385, 3.698] | 2.672..4.074 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.431 [0.409, 0.455] | 0.350..0.544 | 3.501 [3.366, 3.625] | 2.804..3.982 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.427 [0.403, 0.454] | 0.300..0.533 | 3.445 [3.309, 3.566] | 2.685..3.971 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.426 [0.407, 0.447] | 0.344..0.528 | 3.556 [3.432, 3.668] | 2.879..3.993 |

### D=7,h=7

Cell `D=7,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.440 [0.418, 0.463] | 0.367..0.528 | 3.502 [3.357, 3.660] | 2.981..4.121 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.435 [0.411, 0.459] | 0.339..0.528 | 3.381 [3.216, 3.559] | 2.672..4.069 |
| Markov1(a=1,cut=24h,hl=24h) | 0.434 [0.409, 0.459] | 0.333..0.531 | 3.502 [3.357, 3.660] | 2.981..4.121 |
| SmoothedRecency(hl=6h,freq=24h) | 0.433 [0.412, 0.456] | 0.353..0.531 | 3.591 [3.456, 3.732] | 3.116..4.135 |
| LastObservation | 0.432 [0.408, 0.456] | 0.342..0.531 | 3.870 [3.699, 4.034] | 3.214..4.567 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.431 [0.407, 0.456] | 0.339..0.531 | 3.556 [3.403, 3.717] | 3.043..4.172 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.429 [0.407, 0.453] | 0.356..0.525 | 3.506 [3.359, 3.665] | 3.005..4.132 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.427 [0.404, 0.451] | 0.353..0.528 | 3.592 [3.439, 3.756] | 3.041..4.196 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 20 households, 1622 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.499 [0.453, 0.545] | 0.273..0.750 | 2.997 [2.765, 3.226] | 1.706..4.027 |
| Markov1(a=1,cut=24h,hl=24h) | 0.496 [0.453, 0.536] | 0.295..0.714 | 3.309 [3.138, 3.485] | 2.408..4.215 |
| MostFrequentLocation(hl=24h) | 0.496 [0.445, 0.545] | 0.216..0.750 | 3.100 [2.852, 3.348] | 1.659..4.107 |
| LastObservation | 0.494 [0.448, 0.541] | 0.239..0.714 | 3.369 [3.080, 3.680] | 1.974..4.906 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.492 [0.442, 0.542] | 0.239..0.714 | 3.177 [2.917, 3.441] | 1.788..4.369 |
| SmoothedRecency(hl=6h,freq=24h) | 0.487 [0.435, 0.536] | 0.216..0.750 | 3.226 [2.910, 3.546] | 1.612..4.930 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.467 [0.420, 0.513] | 0.239..0.702 | 3.140 [2.899, 3.377] | 1.874..4.160 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.451 [0.409, 0.492] | 0.216..0.595 | 3.272 [3.057, 3.485] | 2.186..4.182 |

### D=10,h=3

Cell `D=10,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.442 [0.409, 0.476] | 0.261..0.611 | 3.471 [3.268, 3.672] | 2.517..4.552 |
| Markov1(a=1,cut=24h,hl=24h) | 0.441 [0.412, 0.473] | 0.278..0.589 | 3.477 [3.270, 3.674] | 2.457..4.541 |
| SmoothedRecency(hl=6h,freq=24h) | 0.437 [0.412, 0.466] | 0.317..0.589 | 3.582 [3.368, 3.769] | 2.581..4.552 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.435 [0.408, 0.466] | 0.317..0.589 | 3.382 [3.184, 3.574] | 2.438..4.404 |
| LastObservation | 0.432 [0.402, 0.463] | 0.272..0.583 | 3.817 [3.613, 4.010] | 2.802..4.786 |
| MostFrequentLocation(hl=24h) | 0.430 [0.402, 0.463] | 0.278..0.589 | 3.477 [3.270, 3.674] | 2.457..4.541 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.429 [0.398, 0.461] | 0.283..0.589 | 3.551 [3.348, 3.740] | 2.539..4.609 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.408 [0.382, 0.436] | 0.267..0.533 | 3.604 [3.408, 3.788] | 2.605..4.667 |

### D=10,h=7

Cell `D=10,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.421 [0.400, 0.445] | 0.344..0.536 | 3.409 [3.267, 3.564] | 2.815..4.234 |
| Markov1(a=1,cut=24h,hl=24h) | 0.419 [0.390, 0.446] | 0.267..0.536 | 3.518 [3.384, 3.667] | 2.928..4.298 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.418 [0.382, 0.450] | 0.247..0.556 | 3.495 [3.363, 3.649] | 2.950..4.283 |
| SmoothedRecency(hl=6h,freq=24h) | 0.415 [0.393, 0.438] | 0.336..0.536 | 3.633 [3.498, 3.784] | 2.964..4.334 |
| MostFrequentLocation(hl=24h) | 0.414 [0.385, 0.443] | 0.267..0.536 | 3.518 [3.384, 3.667] | 2.928..4.298 |
| LastObservation | 0.408 [0.377, 0.436] | 0.253..0.508 | 3.983 [3.843, 4.133] | 3.396..4.626 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.408 [0.374, 0.439] | 0.247..0.533 | 3.605 [3.476, 3.754] | 3.026..4.366 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.395 [0.367, 0.423] | 0.247..0.494 | 3.640 [3.510, 3.786] | 3.075..4.452 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 20 households, 1633 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.500 [0.455, 0.543] | 0.309..0.632 | 3.450 [3.146, 3.759] | 2.557..4.810 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.496 [0.451, 0.541] | 0.309..0.627 | 3.194 [2.896, 3.478] | 2.033..4.482 |
| MostFrequentLocation(hl=24h) | 0.496 [0.448, 0.544] | 0.259..0.655 | 3.050 [2.779, 3.319] | 1.948..4.369 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.495 [0.449, 0.542] | 0.309..0.723 | 3.086 [2.844, 3.316] | 1.978..4.215 |
| SmoothedRecency(hl=6h,freq=24h) | 0.491 [0.445, 0.538] | 0.309..0.651 | 3.200 [2.855, 3.521] | 1.838..4.673 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.482 [0.437, 0.529] | 0.309..0.651 | 2.914 [2.689, 3.147] | 1.926..4.071 |
| Markov1(a=1,cut=24h,hl=24h) | 0.478 [0.437, 0.523] | 0.309..0.655 | 3.230 [3.034, 3.429] | 2.449..4.195 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.462 [0.420, 0.505] | 0.259..0.632 | 3.257 [3.002, 3.515] | 2.246..4.467 |

### D=14,h=3

Cell `D=14,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.440 [0.406, 0.478] | 0.322..0.628 | 3.336 [3.117, 3.531] | 2.345..3.999 |
| MostFrequentLocation(hl=24h) | 0.439 [0.403, 0.479] | 0.322..0.639 | 3.360 [3.129, 3.572] | 2.213..4.155 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.437 [0.403, 0.476] | 0.278..0.633 | 3.489 [3.231, 3.710] | 2.198..4.274 |
| LastObservation | 0.434 [0.401, 0.473] | 0.344..0.650 | 3.895 [3.629, 4.127] | 2.425..4.544 |
| Markov1(a=1,cut=24h,hl=24h) | 0.432 [0.395, 0.475] | 0.272..0.650 | 3.360 [3.129, 3.572] | 2.213..4.155 |
| SmoothedRecency(hl=6h,freq=24h) | 0.431 [0.394, 0.472] | 0.272..0.639 | 3.590 [3.330, 3.830] | 2.220..4.423 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.429 [0.392, 0.473] | 0.272..0.650 | 3.200 [2.975, 3.401] | 2.253..3.897 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.411 [0.377, 0.448] | 0.317..0.606 | 3.548 [3.314, 3.752] | 2.400..4.203 |

### D=14,h=7

Cell `D=14,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.446 [0.410, 0.486] | 0.297..0.647 | 3.375 [3.151, 3.600] | 2.431..4.243 |
| MostFrequentLocation(hl=24h) | 0.443 [0.406, 0.480] | 0.308..0.614 | 3.391 [3.157, 3.608] | 2.441..4.353 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.442 [0.404, 0.484] | 0.250..0.614 | 3.482 [3.241, 3.703] | 2.475..4.446 |
| LastObservation | 0.438 [0.404, 0.478] | 0.308..0.619 | 3.871 [3.605, 4.115] | 2.602..4.820 |
| Markov1(a=1,cut=24h,hl=24h) | 0.438 [0.402, 0.478] | 0.247..0.619 | 3.391 [3.157, 3.608] | 2.441..4.353 |
| SmoothedRecency(hl=6h,freq=24h) | 0.436 [0.399, 0.476] | 0.247..0.614 | 3.531 [3.289, 3.756] | 2.466..4.564 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.434 [0.398, 0.474] | 0.247..0.614 | 3.278 [3.065, 3.485] | 2.331..4.119 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.423 [0.388, 0.461] | 0.281..0.589 | 3.539 [3.296, 3.763] | 2.510..4.551 |
