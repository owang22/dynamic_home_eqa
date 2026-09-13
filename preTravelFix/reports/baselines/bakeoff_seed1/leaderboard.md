# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 20 households, 1660 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.485 [0.444, 0.524] | 0.325..0.611 | 3.023 [2.854, 3.200] | 2.370..4.023 |
| LastObservation | 0.482 [0.447, 0.521] | 0.382..0.644 | 3.480 [3.224, 3.717] | 2.456..4.197 |
| MostFrequentLocation(hl=24h) | 0.480 [0.448, 0.518] | 0.365..0.611 | 3.202 [2.984, 3.413] | 2.396..4.116 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.475 [0.444, 0.510] | 0.393..0.633 | 3.230 [3.034, 3.426] | 2.504..4.162 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.473 [0.432, 0.515] | 0.318..0.644 | 3.273 [3.038, 3.499] | 2.354..4.090 |
| SmoothedRecency(hl=6h,freq=24h) | 0.470 [0.431, 0.512] | 0.330..0.633 | 3.354 [3.104, 3.577] | 2.342..4.077 |
| Markov1(a=1,cut=24h,hl=24h) | 0.457 [0.432, 0.484] | 0.368..0.568 | 3.441 [3.273, 3.617] | 2.763..4.442 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.457 [0.417, 0.496] | 0.295..0.602 | 3.328 [3.130, 3.531] | 2.561..4.219 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.816 (n=69) | 0.581 (n=4007) | 0.447 (n=17193) | 0.400 (n=50731) |
| MostFrequentLocation(hl=24h) | 0.883 (n=69) | 0.578 (n=4007) | 0.454 (n=17193) | 0.407 (n=50731) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.807 (n=69) | 0.542 (n=4007) | 0.437 (n=17193) | 0.390 (n=50731) |
| Markov1(a=1,cut=24h,hl=24h) | 0.780 (n=69) | 0.536 (n=4007) | 0.452 (n=17193) | 0.403 (n=50731) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.816 (n=69) | 0.582 (n=4007) | 0.451 (n=17193) | 0.401 (n=50731) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.852 (n=69) | 0.563 (n=4007) | 0.455 (n=17193) | 0.402 (n=50731) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.883 (n=69) | 0.578 (n=4007) | 0.452 (n=17193) | 0.402 (n=50731) |
| SmoothedRecency(hl=6h,freq=24h) | 0.816 (n=69) | 0.579 (n=4007) | 0.450 (n=17193) | 0.404 (n=50731) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| households__generated__gpt-5.6-terra__hh_001__seed1 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.444) | Markov1(a=1,cut=24h,hl=24h) (2.822) |
| households__generated__gpt-5.6-terra__hh_002__seed1 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.425) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.414) |
| households__generated__gpt-5.6-terra__hh_003__seed1 | HierarchyBackoff(po=5,pc=5,hl=24h) (0.554) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.892) |
| households__generated__gpt-5.6-terra__hh_004__seed1 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.554) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.923) |
| households__generated__gpt-5.6-terra__hh_005__seed1 | TimetableLookup(bin=1h,days=all,hl=24h) (0.507) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.057) |
| households__generated__gpt-5.6-terra__hh_006__seed1 | LastObservation (0.460) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.239) |
| households__generated__gpt-5.6-terra__hh_007__seed1 | LastObservation (0.424) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.527) |
| households__generated__gpt-5.6-terra__hh_008__seed1 | LastObservation (0.439) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.469) |
| households__generated__gpt-5.6-terra__hh_009__seed1 | LastObservation (0.425) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.115) |
| households__generated__gpt-5.6-terra__hh_010__seed1 | MostFrequentLocation(hl=24h) (0.422) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.012) |
| households__generated__gpt-5.6-terra__hh_011__seed1 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.586) | SmoothedRecency(hl=6h,freq=24h) (2.674) |
| households__generated__gpt-5.6-terra__hh_012__seed1 | LastObservation (0.636) | SmoothedRecency(hl=6h,freq=24h) (2.363) |
| households__generated__gpt-5.6-terra__hh_013__seed1 | LastObservation (0.593) | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (2.753) |
| households__generated__gpt-5.6-terra__hh_014__seed1 | LastObservation (0.413) | HierarchyBackoff(po=5,pc=5,hl=24h) (4.023) |
| households__generated__gpt-5.6-terra__hh_015__seed1 | Markov1(a=1,cut=24h,hl=24h) (0.420) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.391) |
| households__generated__gpt-5.6-terra__hh_016__seed1 | LastObservation (0.562) | MostFrequentLocation(hl=24h) (2.832) |
| households__generated__gpt-5.6-terra__hh_017__seed1 | MostFrequentLocation(hl=24h) (0.533) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.669) |
| households__generated__gpt-5.6-terra__hh_018__seed1 | MostFrequentLocation(hl=24h) (0.564) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.458) |
| households__generated__gpt-5.6-terra__hh_019__seed1 | MostFrequentLocation(hl=24h) (0.472) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.056) |
| households__generated__gpt-5.6-terra__hh_020__seed1 | LastObservation (0.644) | SmoothedRecency(hl=6h,freq=24h) (2.342) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 20 households, 1800 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.374 [0.336, 0.417] | 0.222..0.533 | 4.029 [3.762, 4.314] | 3.043..5.054 |
| SmoothedRecency(hl=6h,freq=24h) | 0.373 [0.333, 0.412] | 0.211..0.533 | 4.067 [3.791, 4.369] | 3.051..5.191 |
| MostFrequentLocation(hl=24h) | 0.372 [0.332, 0.413] | 0.222..0.533 | 4.007 [3.738, 4.294] | 2.982..5.063 |
| LastObservation | 0.369 [0.331, 0.405] | 0.222..0.511 | 4.211 [3.954, 4.486] | 3.377..5.380 |
| Markov1(a=1,cut=24h,hl=24h) | 0.368 [0.329, 0.409] | 0.222..0.533 | 4.007 [3.738, 4.294] | 2.982..5.063 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.367 [0.322, 0.409] | 0.144..0.533 | 4.009 [3.740, 4.296] | 2.982..5.063 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.366 [0.319, 0.410] | 0.144..0.533 | 3.844 [3.585, 4.137] | 2.915..4.944 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.354 [0.309, 0.399] | 0.144..0.533 | 4.040 [3.773, 4.325] | 3.078..5.054 |

### D=1,h=7

Cell `D=1,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.402 [0.372, 0.432] | 0.242..0.506 | 3.999 [3.821, 4.195] | 3.435..4.968 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.395 [0.358, 0.430] | 0.236..0.508 | 3.831 [3.629, 4.053] | 3.158..4.761 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.393 [0.359, 0.427] | 0.242..0.508 | 3.842 [3.638, 4.067] | 3.152..4.774 |
| Markov1(a=1,cut=24h,hl=24h) | 0.393 [0.361, 0.426] | 0.242..0.508 | 3.830 [3.628, 4.052] | 3.158..4.761 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.392 [0.352, 0.428] | 0.194..0.508 | 3.708 [3.496, 3.945] | 3.053..4.648 |
| MostFrequentLocation(hl=24h) | 0.392 [0.358, 0.425] | 0.242..0.508 | 3.830 [3.628, 4.052] | 3.158..4.761 |
| SmoothedRecency(hl=6h,freq=24h) | 0.391 [0.352, 0.424] | 0.194..0.508 | 3.855 [3.650, 4.083] | 3.195..4.887 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.389 [0.358, 0.417] | 0.231..0.506 | 3.853 [3.650, 4.074] | 3.151..4.774 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 20 households, 1620 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.484 [0.452, 0.520] | 0.323..0.644 | 3.235 [2.985, 3.453] | 2.111..4.002 |
| MostFrequentLocation(hl=24h) | 0.476 [0.439, 0.517] | 0.323..0.644 | 3.168 [2.945, 3.369] | 2.191..3.943 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.473 [0.440, 0.512] | 0.323..0.656 | 3.188 [2.958, 3.393] | 2.186..3.956 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.472 [0.441, 0.506] | 0.308..0.611 | 3.226 [2.998, 3.425] | 2.251..3.937 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.471 [0.431, 0.511] | 0.295..0.633 | 3.056 [2.888, 3.220] | 2.359..3.656 |
| LastObservation | 0.470 [0.432, 0.512] | 0.295..0.644 | 3.447 [3.215, 3.651] | 2.469..4.112 |
| Markov1(a=1,cut=24h,hl=24h) | 0.462 [0.431, 0.493] | 0.323..0.609 | 3.571 [3.424, 3.724] | 2.986..4.268 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.459 [0.423, 0.499] | 0.314..0.667 | 3.182 [2.962, 3.377] | 2.257..3.949 |

### D=3,h=3

Cell `D=3,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.423 [0.394, 0.451] | 0.272..0.528 | 3.587 [3.438, 3.741] | 2.773..4.305 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.421 [0.398, 0.442] | 0.328..0.500 | 3.541 [3.401, 3.686] | 2.911..4.314 |
| MostFrequentLocation(hl=24h) | 0.416 [0.385, 0.445] | 0.272..0.528 | 3.525 [3.379, 3.672] | 2.860..4.282 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.412 [0.384, 0.440] | 0.283..0.522 | 3.514 [3.367, 3.660] | 2.842..4.288 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.412 [0.381, 0.440] | 0.272..0.528 | 3.407 [3.293, 3.541] | 2.937..4.241 |
| Markov1(a=1,cut=24h,hl=24h) | 0.412 [0.380, 0.439] | 0.272..0.528 | 3.525 [3.379, 3.672] | 2.860..4.282 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.411 [0.385, 0.435] | 0.278..0.522 | 3.575 [3.428, 3.720] | 2.956..4.352 |
| LastObservation | 0.409 [0.382, 0.434] | 0.300..0.489 | 3.848 [3.729, 3.986] | 3.308..4.498 |

### D=3,h=7

Cell `D=3,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.408 [0.384, 0.432] | 0.308..0.519 | 3.632 [3.493, 3.783] | 3.136..4.255 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.406 [0.377, 0.432] | 0.314..0.494 | 3.567 [3.441, 3.710] | 3.201..4.192 |
| MostFrequentLocation(hl=24h) | 0.403 [0.376, 0.428] | 0.308..0.519 | 3.573 [3.446, 3.718] | 3.189..4.191 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.401 [0.376, 0.426] | 0.297..0.517 | 3.614 [3.485, 3.757] | 3.223..4.245 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.400 [0.372, 0.423] | 0.306..0.478 | 3.590 [3.465, 3.732] | 3.216..4.198 |
| Markov1(a=1,cut=24h,hl=24h) | 0.396 [0.368, 0.423] | 0.308..0.519 | 3.573 [3.446, 3.718] | 3.189..4.191 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.396 [0.369, 0.422] | 0.308..0.519 | 3.442 [3.329, 3.578] | 3.003..4.078 |
| LastObservation | 0.396 [0.367, 0.424] | 0.306..0.494 | 3.943 [3.813, 4.083] | 3.362..4.471 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 20 households, 1624 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h) | 0.451 [0.407, 0.497] | 0.287..0.637 | 3.486 [3.177, 3.765] | 2.331..4.512 |
| MostFrequentLocation(hl=24h) | 0.451 [0.408, 0.496] | 0.287..0.637 | 3.444 [3.152, 3.727] | 2.257..4.509 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.450 [0.414, 0.488] | 0.287..0.569 | 3.446 [3.148, 3.722] | 2.166..4.482 |
| LastObservation | 0.448 [0.403, 0.497] | 0.287..0.637 | 3.740 [3.436, 4.029] | 2.504..4.851 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.448 [0.404, 0.496] | 0.299..0.637 | 3.386 [3.087, 3.671] | 2.170..4.481 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.445 [0.402, 0.492] | 0.294..0.625 | 3.491 [3.185, 3.775] | 2.330..4.516 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.429 [0.388, 0.473] | 0.287..0.583 | 3.535 [3.225, 3.822] | 2.299..4.745 |
| Markov1(a=1,cut=24h,hl=24h) | 0.422 [0.385, 0.461] | 0.276..0.583 | 3.911 [3.668, 4.163] | 2.834..4.902 |

### D=5,h=3

Cell `D=5,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.408 [0.375, 0.443] | 0.261..0.533 | 3.657 [3.478, 3.849] | 2.960..4.416 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.403 [0.364, 0.440] | 0.256..0.539 | 3.550 [3.366, 3.764] | 2.906..4.438 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.398 [0.364, 0.433] | 0.256..0.533 | 3.703 [3.518, 3.902] | 2.957..4.480 |
| MostFrequentLocation(hl=24h) | 0.398 [0.356, 0.438] | 0.256..0.539 | 3.669 [3.488, 3.867] | 2.945..4.446 |
| Markov1(a=1,cut=24h,hl=24h) | 0.396 [0.359, 0.432] | 0.256..0.539 | 3.669 [3.488, 3.867] | 2.945..4.446 |
| SmoothedRecency(hl=6h,freq=24h) | 0.396 [0.355, 0.434] | 0.256..0.539 | 3.732 [3.552, 3.933] | 3.044..4.525 |
| LastObservation | 0.392 [0.351, 0.432] | 0.256..0.539 | 4.033 [3.811, 4.268] | 3.224..5.066 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.381 [0.350, 0.414] | 0.272..0.528 | 3.742 [3.562, 3.933] | 3.022..4.481 |

### D=5,h=7

Cell `D=5,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.407 [0.371, 0.445] | 0.247..0.550 | 3.587 [3.401, 3.770] | 2.933..4.448 |
| SmoothedRecency(hl=6h,freq=24h) | 0.406 [0.366, 0.445] | 0.247..0.550 | 3.671 [3.480, 3.856] | 2.972..4.538 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.403 [0.366, 0.439] | 0.247..0.550 | 3.480 [3.306, 3.657] | 2.903..4.277 |
| Markov1(a=1,cut=24h,hl=24h) | 0.398 [0.362, 0.435] | 0.256..0.547 | 3.587 [3.401, 3.770] | 2.933..4.448 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.397 [0.361, 0.434] | 0.272..0.544 | 3.574 [3.394, 3.749] | 2.944..4.388 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.394 [0.358, 0.429] | 0.258..0.544 | 3.645 [3.462, 3.830] | 2.978..4.526 |
| LastObservation | 0.393 [0.353, 0.433] | 0.256..0.564 | 3.970 [3.753, 4.179] | 3.053..4.803 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.381 [0.347, 0.412] | 0.233..0.536 | 3.667 [3.483, 3.854] | 2.992..4.558 |

### D=7,h=0.25

(no questions in cell D=7,h=0.25)

### D=7,h=1

Cell `D=7,h=1`: 20 households, 1660 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.485 [0.444, 0.524] | 0.325..0.611 | 3.023 [2.854, 3.200] | 2.370..4.023 |
| LastObservation | 0.482 [0.447, 0.521] | 0.382..0.644 | 3.480 [3.224, 3.717] | 2.456..4.197 |
| MostFrequentLocation(hl=24h) | 0.480 [0.448, 0.518] | 0.365..0.611 | 3.202 [2.984, 3.413] | 2.396..4.116 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.475 [0.444, 0.510] | 0.393..0.633 | 3.230 [3.034, 3.426] | 2.504..4.162 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.473 [0.432, 0.515] | 0.318..0.644 | 3.273 [3.038, 3.499] | 2.354..4.090 |
| SmoothedRecency(hl=6h,freq=24h) | 0.470 [0.431, 0.512] | 0.330..0.633 | 3.354 [3.104, 3.577] | 2.342..4.077 |
| Markov1(a=1,cut=24h,hl=24h) | 0.457 [0.432, 0.484] | 0.368..0.568 | 3.441 [3.273, 3.617] | 2.763..4.442 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.457 [0.417, 0.496] | 0.295..0.602 | 3.328 [3.130, 3.531] | 2.561..4.219 |

### D=7,h=3

Cell `D=7,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.444 [0.411, 0.474] | 0.239..0.528 | 3.325 [3.112, 3.541] | 2.492..4.396 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.438 [0.404, 0.470] | 0.200..0.544 | 3.464 [3.259, 3.682] | 2.779..4.604 |
| MostFrequentLocation(hl=24h) | 0.436 [0.403, 0.464] | 0.239..0.528 | 3.462 [3.263, 3.676] | 2.812..4.664 |
| Markov1(a=1,cut=24h,hl=24h) | 0.433 [0.401, 0.462] | 0.239..0.533 | 3.462 [3.263, 3.676] | 2.812..4.664 |
| LastObservation | 0.429 [0.398, 0.457] | 0.250..0.528 | 3.827 [3.653, 4.031] | 3.301..5.146 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.424 [0.394, 0.449] | 0.233..0.500 | 3.538 [3.333, 3.753] | 2.914..4.861 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.421 [0.386, 0.451] | 0.211..0.500 | 3.567 [3.354, 3.789] | 2.894..4.955 |
| SmoothedRecency(hl=6h,freq=24h) | 0.419 [0.386, 0.449] | 0.233..0.500 | 3.613 [3.431, 3.821] | 3.007..4.946 |

### D=7,h=7

Cell `D=7,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.444 [0.417, 0.472] | 0.314..0.544 | 3.366 [3.154, 3.559] | 2.351..4.196 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.442 [0.411, 0.473] | 0.306..0.558 | 3.477 [3.270, 3.675] | 2.466..4.289 |
| MostFrequentLocation(hl=24h) | 0.441 [0.412, 0.469] | 0.314..0.544 | 3.475 [3.278, 3.660] | 2.477..4.240 |
| Markov1(a=1,cut=24h,hl=24h) | 0.439 [0.412, 0.468] | 0.314..0.544 | 3.475 [3.278, 3.660] | 2.477..4.240 |
| SmoothedRecency(hl=6h,freq=24h) | 0.432 [0.403, 0.463] | 0.300..0.544 | 3.575 [3.391, 3.750] | 2.791..4.271 |
| LastObservation | 0.430 [0.404, 0.460] | 0.319..0.544 | 3.856 [3.688, 4.023] | 3.147..4.615 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.428 [0.399, 0.458] | 0.294..0.553 | 3.542 [3.342, 3.730] | 2.529..4.287 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.423 [0.393, 0.454] | 0.272..0.528 | 3.585 [3.374, 3.780] | 2.559..4.340 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 20 households, 1579 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.507 [0.460, 0.553] | 0.377..0.695 | 3.068 [2.790, 3.348] | 2.065..3.979 |
| LastObservation | 0.506 [0.455, 0.556] | 0.323..0.671 | 3.333 [3.034, 3.630] | 2.275..4.178 |
| MostFrequentLocation(hl=24h) | 0.504 [0.463, 0.548] | 0.378..0.671 | 2.993 [2.729, 3.258] | 2.065..3.966 |
| SmoothedRecency(hl=6h,freq=24h) | 0.499 [0.457, 0.542] | 0.357..0.671 | 3.115 [2.819, 3.414] | 1.981..4.035 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.492 [0.441, 0.546] | 0.323..0.671 | 2.884 [2.637, 3.129] | 2.069..3.805 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.487 [0.439, 0.532] | 0.333..0.671 | 3.007 [2.751, 3.250] | 2.153..3.912 |
| Markov1(a=1,cut=24h,hl=24h) | 0.483 [0.438, 0.530] | 0.333..0.683 | 3.217 [2.967, 3.466] | 2.346..4.231 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.464 [0.417, 0.513] | 0.333..0.644 | 3.141 [2.869, 3.417] | 2.260..4.102 |

### D=10,h=3

Cell `D=10,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.447 [0.415, 0.483] | 0.328..0.694 | 3.409 [3.154, 3.633] | 1.995..4.193 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.441 [0.406, 0.481] | 0.306..0.678 | 3.489 [3.240, 3.711] | 2.080..4.228 |
| MostFrequentLocation(hl=24h) | 0.439 [0.407, 0.477] | 0.317..0.683 | 3.421 [3.163, 3.650] | 1.932..4.185 |
| Markov1(a=1,cut=24h,hl=24h) | 0.439 [0.407, 0.478] | 0.317..0.683 | 3.421 [3.163, 3.650] | 1.932..4.185 |
| SmoothedRecency(hl=6h,freq=24h) | 0.438 [0.406, 0.476] | 0.300..0.683 | 3.506 [3.255, 3.736] | 2.025..4.346 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.430 [0.396, 0.471] | 0.317..0.683 | 3.324 [3.081, 3.541] | 1.902..4.154 |
| LastObservation | 0.430 [0.394, 0.471] | 0.300..0.683 | 3.836 [3.575, 4.066] | 2.187..4.548 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.412 [0.381, 0.448] | 0.317..0.611 | 3.551 [3.317, 3.767] | 2.276..4.251 |

### D=10,h=7

Cell `D=10,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.416 [0.378, 0.452] | 0.242..0.603 | 3.576 [3.389, 3.758] | 2.516..4.236 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.413 [0.380, 0.451] | 0.294..0.597 | 3.643 [3.460, 3.822] | 2.616..4.282 |
| SmoothedRecency(hl=6h,freq=24h) | 0.412 [0.381, 0.447] | 0.303..0.603 | 3.695 [3.486, 3.894] | 2.564..4.420 |
| LastObservation | 0.412 [0.375, 0.453] | 0.261..0.603 | 3.976 [3.733, 4.203] | 2.744..4.816 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.406 [0.374, 0.441] | 0.281..0.603 | 3.553 [3.376, 3.721] | 2.593..4.161 |
| Markov1(a=1,cut=24h,hl=24h) | 0.401 [0.363, 0.440] | 0.242..0.603 | 3.576 [3.389, 3.758] | 2.516..4.236 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.397 [0.356, 0.440] | 0.242..0.603 | 3.464 [3.288, 3.636] | 2.513..4.059 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.389 [0.353, 0.428] | 0.236..0.553 | 3.681 [3.499, 3.857] | 2.699..4.287 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 20 households, 1663 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.483 [0.435, 0.533] | 0.297..0.742 | 3.096 [2.822, 3.365] | 1.828..4.318 |
| SmoothedRecency(hl=6h,freq=24h) | 0.478 [0.427, 0.532] | 0.270..0.742 | 3.273 [2.930, 3.610] | 1.747..4.653 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.478 [0.429, 0.530] | 0.284..0.742 | 3.225 [2.920, 3.523] | 1.757..4.558 |
| Markov1(a=1,cut=24h,hl=24h) | 0.475 [0.428, 0.523] | 0.284..0.719 | 3.207 [3.025, 3.381] | 2.453..3.955 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.472 [0.425, 0.522] | 0.284..0.742 | 2.929 [2.693, 3.165] | 1.857..4.171 |
| LastObservation | 0.471 [0.420, 0.524] | 0.270..0.742 | 3.517 [3.187, 3.839] | 1.785..4.957 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.462 [0.414, 0.510] | 0.270..0.674 | 3.100 [2.854, 3.347] | 2.086..4.324 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.436 [0.394, 0.478] | 0.291..0.573 | 3.292 [3.044, 3.533] | 2.301..4.326 |

### D=14,h=3

Cell `D=14,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.434 [0.405, 0.462] | 0.283..0.550 | 3.462 [3.307, 3.619] | 2.952..4.126 |
| MostFrequentLocation(hl=24h) | 0.428 [0.399, 0.458] | 0.283..0.550 | 3.462 [3.307, 3.619] | 2.952..4.126 |
| SmoothedRecency(hl=6h,freq=24h) | 0.422 [0.391, 0.456] | 0.283..0.544 | 3.652 [3.442, 3.880] | 2.850..4.866 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.422 [0.392, 0.454] | 0.283..0.550 | 3.294 [3.155, 3.439] | 2.840..3.908 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.421 [0.387, 0.456] | 0.256..0.556 | 3.562 [3.393, 3.745] | 2.995..4.422 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.419 [0.382, 0.457] | 0.256..0.539 | 3.433 [3.263, 3.611] | 2.909..4.232 |
| LastObservation | 0.413 [0.379, 0.449] | 0.267..0.550 | 3.925 [3.716, 4.146] | 3.112..5.066 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.408 [0.379, 0.437] | 0.278..0.517 | 3.602 [3.444, 3.773] | 3.103..4.395 |

### D=14,h=7

Cell `D=14,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.460 [0.435, 0.487] | 0.364..0.589 | 3.332 [3.173, 3.484] | 2.547..4.004 |
| MostFrequentLocation(hl=24h) | 0.460 [0.433, 0.488] | 0.325..0.589 | 3.332 [3.173, 3.484] | 2.547..4.004 |
| SmoothedRecency(hl=6h,freq=24h) | 0.451 [0.420, 0.483] | 0.325..0.589 | 3.458 [3.286, 3.634] | 2.768..4.119 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.451 [0.420, 0.482] | 0.325..0.589 | 3.232 [3.073, 3.386] | 2.392..3.940 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.425, 0.479] | 0.353..0.597 | 3.330 [3.176, 3.484] | 2.467..4.026 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.444 [0.416, 0.474] | 0.319..0.586 | 3.434 [3.276, 3.586] | 2.648..4.094 |
| LastObservation | 0.442 [0.411, 0.474] | 0.325..0.589 | 3.759 [3.553, 3.962] | 2.840..4.509 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.425 [0.400, 0.452] | 0.308..0.556 | 3.500 [3.345, 3.653] | 2.686..4.218 |
