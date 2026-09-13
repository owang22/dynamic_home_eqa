# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 12 households, 1025 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.476 [0.411, 0.528] | 0.232..0.593 | 3.620 [3.264, 4.069] | 2.810..5.307 |
| MostFrequentLocation(hl=24h) | 0.473 [0.410, 0.529] | 0.232..0.622 | 3.121 [2.647, 3.634] | 1.804..4.917 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.472 [0.410, 0.526] | 0.244..0.611 | 3.214 [2.784, 3.681] | 1.851..4.879 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.469 [0.408, 0.523] | 0.232..0.589 | 3.164 [2.704, 3.663] | 1.864..4.928 |
| Markov1(a=1,cut=24h,hl=24h) | 0.468 [0.404, 0.524] | 0.232..0.622 | 3.194 [2.748, 3.648] | 1.934..4.750 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.390, 0.509] | 0.232..0.614 | 3.043 [2.540, 3.536] | 1.727..4.649 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.439 [0.378, 0.493] | 0.232..0.578 | 2.680 [2.246, 3.175] | 1.539..4.192 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [0h,1h) | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|---|
| LastObservation | 1.000 (n=1) | 0.988 (n=22) | 0.595 (n=673) | 0.480 (n=4509) | 0.457 (n=37995) |
| MostFrequentLocation(hl=24h) | 1.000 (n=1) | 0.988 (n=22) | 0.591 (n=673) | 0.483 (n=4509) | 0.456 (n=37995) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 1.000 (n=1) | 0.750 (n=22) | 0.579 (n=673) | 0.481 (n=4509) | 0.458 (n=37995) |
| Markov1(a=1,cut=24h,hl=24h) | 1.000 (n=1) | 0.950 (n=22) | 0.538 (n=673) | 0.483 (n=4509) | 0.456 (n=37995) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 1.000 (n=1) | 0.988 (n=22) | 0.595 (n=673) | 0.483 (n=4509) | 0.458 (n=37995) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 1.000 (n=1) | 0.592 (n=22) | 0.526 (n=673) | 0.469 (n=4509) | 0.460 (n=37995) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 1.000 (n=1) | 0.988 (n=22) | 0.591 (n=673) | 0.481 (n=4509) | 0.432 (n=37995) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| revamp_v1__claude-fable-5__hh1 | LastObservation (0.593) | HierarchyBackoff(po=5,pc=5,hl=24h) (1.756) |
| revamp_v1__claude-fable-5__hh3 | MostFrequentLocation(hl=24h) (0.622) | DaytypeMixture(K=3,bin=2h,hl=24h) (1.727) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh1 | LastObservation (0.416) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.313) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh10 | LastObservation (0.500) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.640) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh2 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.511) | DaytypeMixture(K=3,bin=2h,hl=24h) (2.963) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh3 | LastObservation (0.456) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.705) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh4 | LastObservation (0.398) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.679) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh5 | LastObservation (0.414) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.739) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh6 | TimetableLookup(bin=1h,days=all,hl=24h) (0.244) | HierarchyBackoff(po=5,pc=5,hl=24h) (4.192) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh7 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.614) | HierarchyBackoff(po=5,pc=5,hl=24h) (1.539) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh8 | LastObservation (0.511) | HierarchyBackoff(po=5,pc=5,hl=24h) (1.890) |
| revamp_v2__storyfirst__gpt-5.6-terra__hh9 | LastObservation (0.584) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.777) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 12 households, 1080 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.508 [0.452, 0.563] | 0.333..0.700 | 3.396 [3.025, 3.793] | 2.072..4.605 |
| MostFrequentLocation(hl=24h) | 0.506 [0.450, 0.559] | 0.333..0.700 | 3.314 [2.931, 3.747] | 1.951..4.620 |
| Markov1(a=1,cut=24h,hl=24h) | 0.506 [0.450, 0.559] | 0.333..0.700 | 3.314 [2.931, 3.747] | 1.951..4.620 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.506 [0.450, 0.559] | 0.333..0.700 | 3.314 [2.931, 3.747] | 1.951..4.620 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.503 [0.447, 0.557] | 0.333..0.700 | 3.353 [2.964, 3.779] | 1.951..4.614 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.503 [0.447, 0.557] | 0.333..0.700 | 3.353 [2.964, 3.779] | 1.951..4.614 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.493 [0.437, 0.544] | 0.311..0.667 | 3.125 [2.793, 3.502] | 2.140..4.292 |

### D=1,h=7

Cell `D=1,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.488 [0.450, 0.525] | 0.397..0.611 | 3.429 [3.159, 3.707] | 2.337..4.026 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.487 [0.450, 0.525] | 0.394..0.611 | 3.419 [3.154, 3.693] | 2.337..4.026 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.487 [0.450, 0.525] | 0.397..0.611 | 3.438 [3.166, 3.717] | 2.337..4.026 |
| MostFrequentLocation(hl=24h) | 0.487 [0.450, 0.524] | 0.394..0.608 | 3.420 [3.155, 3.693] | 2.344..4.026 |
| Markov1(a=1,cut=24h,hl=24h) | 0.487 [0.450, 0.524] | 0.394..0.608 | 3.420 [3.155, 3.693] | 2.344..4.026 |
| LastObservation | 0.487 [0.450, 0.524] | 0.392..0.608 | 3.543 [3.289, 3.807] | 2.706..4.202 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.475 [0.439, 0.509] | 0.381..0.578 | 3.092 [2.844, 3.349] | 2.219..3.695 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 12 households, 987 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.535 [0.466, 0.604] | 0.383..0.722 | 2.981 [2.544, 3.435] | 1.873..4.228 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.535 [0.467, 0.601] | 0.383..0.700 | 2.967 [2.536, 3.422] | 1.895..4.246 |
| Markov1(a=1,cut=24h,hl=24h) | 0.535 [0.464, 0.604] | 0.370..0.722 | 3.023 [2.595, 3.479] | 1.966..4.176 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.533 [0.466, 0.602] | 0.383..0.722 | 3.001 [2.570, 3.461] | 1.872..4.227 |
| LastObservation | 0.533 [0.460, 0.603] | 0.370..0.722 | 3.226 [2.749, 3.729] | 1.919..4.349 |
| MostFrequentLocation(hl=24h) | 0.532 [0.462, 0.601] | 0.370..0.722 | 2.980 [2.542, 3.436] | 1.872..4.243 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.501 [0.439, 0.563] | 0.358..0.678 | 2.587 [2.222, 2.970] | 1.626..3.659 |

### D=3,h=3

Cell `D=3,h=3`: 12 households, 2160 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.485 [0.452, 0.522] | 0.417..0.622 | 3.205 [2.937, 3.438] | 1.927..3.624 |
| LastObservation | 0.483 [0.448, 0.522] | 0.406..0.622 | 3.569 [3.307, 3.812] | 2.610..4.106 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.483 [0.450, 0.522] | 0.422..0.628 | 3.262 [2.973, 3.498] | 1.934..3.699 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.483 [0.448, 0.523] | 0.411..0.628 | 3.238 [2.961, 3.480] | 1.936..3.668 |
| MostFrequentLocation(hl=24h) | 0.482 [0.448, 0.520] | 0.411..0.622 | 3.232 [2.956, 3.470] | 1.942..3.648 |
| Markov1(a=1,cut=24h,hl=24h) | 0.482 [0.448, 0.520] | 0.411..0.622 | 3.232 [2.956, 3.470] | 1.942..3.648 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.457 [0.430, 0.487] | 0.383..0.567 | 2.710 [2.448, 2.973] | 1.688..3.610 |

### D=3,h=7

Cell `D=3,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.459 [0.429, 0.487] | 0.356..0.539 | 3.737 [3.547, 3.948] | 3.185..4.452 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.458 [0.424, 0.493] | 0.364..0.564 | 3.442 [3.224, 3.692] | 2.560..4.202 |
| MostFrequentLocation(hl=24h) | 0.457 [0.428, 0.485] | 0.367..0.539 | 3.462 [3.246, 3.705] | 2.591..4.212 |
| Markov1(a=1,cut=24h,hl=24h) | 0.457 [0.428, 0.485] | 0.367..0.539 | 3.462 [3.246, 3.705] | 2.591..4.212 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.457 [0.427, 0.486] | 0.361..0.544 | 3.473 [3.255, 3.719] | 2.594..4.243 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.455 [0.425, 0.485] | 0.358..0.544 | 3.507 [3.291, 3.750] | 2.609..4.273 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.434 [0.405, 0.463] | 0.358..0.525 | 2.812 [2.600, 3.039] | 2.144..3.356 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 12 households, 1031 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.523 [0.490, 0.556] | 0.427..0.619 | 2.786 [2.514, 3.066] | 1.752..3.529 |
| MostFrequentLocation(hl=24h) | 0.521 [0.487, 0.555] | 0.416..0.619 | 2.761 [2.494, 3.031] | 1.751..3.484 |
| LastObservation | 0.521 [0.488, 0.554] | 0.416..0.619 | 3.312 [3.082, 3.541] | 2.632..4.036 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.521 [0.486, 0.554] | 0.427..0.619 | 2.820 [2.553, 3.082] | 1.730..3.499 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.520 [0.481, 0.556] | 0.416..0.622 | 2.682 [2.401, 2.971] | 1.602..3.415 |
| Markov1(a=1,cut=24h,hl=24h) | 0.517 [0.481, 0.550] | 0.404..0.619 | 2.827 [2.558, 3.099] | 1.875..3.610 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.484 [0.461, 0.510] | 0.422..0.578 | 2.332 [2.119, 2.573] | 1.640..3.404 |

### D=5,h=3

Cell `D=5,h=3`: 12 households, 2160 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.481 [0.444, 0.519] | 0.389..0.600 | 3.098 [2.831, 3.398] | 2.097..3.921 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.481 [0.433, 0.525] | 0.350..0.611 | 2.975 [2.699, 3.294] | 1.959..3.849 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.481 [0.442, 0.519] | 0.383..0.600 | 3.122 [2.842, 3.424] | 2.120..3.946 |
| MostFrequentLocation(hl=24h) | 0.479 [0.442, 0.516] | 0.389..0.600 | 3.063 [2.799, 3.360] | 2.118..3.894 |
| Markov1(a=1,cut=24h,hl=24h) | 0.479 [0.442, 0.516] | 0.389..0.600 | 3.063 [2.799, 3.360] | 2.118..3.894 |
| LastObservation | 0.477 [0.436, 0.517] | 0.372..0.600 | 3.614 [3.345, 3.895] | 2.763..4.337 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.444 [0.420, 0.468] | 0.367..0.506 | 2.534 [2.289, 2.772] | 1.821..3.092 |

### D=5,h=7

Cell `D=5,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.429 [0.393, 0.464] | 0.342..0.569 | 3.430 [3.126, 3.706] | 2.144..4.055 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.419 [0.386, 0.454] | 0.344..0.553 | 3.526 [3.245, 3.788] | 2.283..4.130 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.419 [0.386, 0.453] | 0.344..0.553 | 3.570 [3.282, 3.825] | 2.311..4.149 |
| MostFrequentLocation(hl=24h) | 0.417 [0.384, 0.452] | 0.344..0.553 | 3.486 [3.191, 3.757] | 2.230..4.107 |
| Markov1(a=1,cut=24h,hl=24h) | 0.417 [0.384, 0.452] | 0.344..0.553 | 3.486 [3.191, 3.757] | 2.230..4.107 |
| LastObservation | 0.416 [0.385, 0.450] | 0.342..0.553 | 4.031 [3.802, 4.253] | 3.089..4.548 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.394 [0.368, 0.419] | 0.325..0.489 | 2.895 [2.620, 3.177] | 1.963..3.809 |

### D=7,h=0.25

(no questions in cell D=7,h=0.25)

### D=7,h=1

Cell `D=7,h=1`: 12 households, 1025 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.476 [0.411, 0.528] | 0.232..0.593 | 3.620 [3.264, 4.069] | 2.810..5.307 |
| MostFrequentLocation(hl=24h) | 0.473 [0.410, 0.529] | 0.232..0.622 | 3.121 [2.647, 3.634] | 1.804..4.917 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.472 [0.410, 0.526] | 0.244..0.611 | 3.214 [2.784, 3.681] | 1.851..4.879 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.469 [0.408, 0.523] | 0.232..0.589 | 3.164 [2.704, 3.663] | 1.864..4.928 |
| Markov1(a=1,cut=24h,hl=24h) | 0.468 [0.404, 0.524] | 0.232..0.622 | 3.194 [2.748, 3.648] | 1.934..4.750 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.390, 0.509] | 0.232..0.614 | 3.043 [2.540, 3.536] | 1.727..4.649 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.439 [0.378, 0.493] | 0.232..0.578 | 2.680 [2.246, 3.175] | 1.539..4.192 |

### D=7,h=3

Cell `D=7,h=3`: 12 households, 2160 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.431 [0.391, 0.471] | 0.333..0.544 | 3.436 [3.166, 3.717] | 2.653..4.230 |
| LastObservation | 0.431 [0.392, 0.468] | 0.328..0.528 | 3.934 [3.678, 4.205] | 3.262..4.644 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.429 [0.390, 0.474] | 0.328..0.583 | 3.293 [3.002, 3.582] | 2.324..4.043 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.427 [0.388, 0.468] | 0.328..0.539 | 3.485 [3.221, 3.755] | 2.650..4.247 |
| MostFrequentLocation(hl=24h) | 0.423 [0.384, 0.460] | 0.328..0.528 | 3.394 [3.111, 3.683] | 2.551..4.192 |
| Markov1(a=1,cut=24h,hl=24h) | 0.423 [0.384, 0.460] | 0.328..0.528 | 3.394 [3.111, 3.683] | 2.551..4.192 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.395 [0.361, 0.431] | 0.256..0.494 | 2.867 [2.579, 3.143] | 2.082..3.404 |

### D=7,h=7

Cell `D=7,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.460 [0.431, 0.486] | 0.356..0.544 | 2.999 [2.756, 3.266] | 2.204..4.056 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.460 [0.427, 0.488] | 0.336..0.558 | 3.171 [2.924, 3.424] | 2.361..4.129 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.459 [0.428, 0.487] | 0.336..0.564 | 3.222 [2.979, 3.464] | 2.372..4.145 |
| LastObservation | 0.459 [0.433, 0.481] | 0.369..0.533 | 3.740 [3.583, 3.918] | 3.224..4.356 |
| MostFrequentLocation(hl=24h) | 0.458 [0.426, 0.485] | 0.336..0.542 | 3.136 [2.889, 3.393] | 2.349..4.096 |
| Markov1(a=1,cut=24h,hl=24h) | 0.458 [0.426, 0.485] | 0.336..0.542 | 3.136 [2.889, 3.393] | 2.349..4.096 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.431 [0.394, 0.466] | 0.336..0.519 | 2.585 [2.347, 2.836] | 1.905..3.455 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 12 households, 997 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.473 [0.406, 0.536] | 0.317..0.689 | 3.640 [3.214, 4.105] | 2.149..4.717 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.471 [0.405, 0.535] | 0.317..0.700 | 3.141 [2.656, 3.628] | 1.389..4.382 |
| MostFrequentLocation(hl=24h) | 0.469 [0.401, 0.536] | 0.305..0.711 | 3.086 [2.616, 3.558] | 1.347..4.229 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.466 [0.401, 0.529] | 0.305..0.700 | 3.196 [2.729, 3.672] | 1.406..4.386 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.463 [0.389, 0.537] | 0.300..0.711 | 2.630 [2.172, 3.108] | 1.440..3.831 |
| Markov1(a=1,cut=24h,hl=24h) | 0.454 [0.394, 0.509] | 0.305..0.656 | 3.251 [2.862, 3.653] | 1.718..4.322 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.444 [0.389, 0.503] | 0.311..0.689 | 2.934 [2.478, 3.394] | 1.177..4.222 |

### D=10,h=3

Cell `D=10,h=3`: 12 households, 2160 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.458 [0.427, 0.486] | 0.350..0.517 | 3.223 [3.031, 3.404] | 2.649..3.800 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.454 [0.425, 0.482] | 0.356..0.522 | 3.170 [2.969, 3.359] | 2.568..3.744 |
| MostFrequentLocation(hl=24h) | 0.454 [0.424, 0.483] | 0.361..0.517 | 3.097 [2.872, 3.302] | 2.304..3.708 |
| Markov1(a=1,cut=24h,hl=24h) | 0.454 [0.424, 0.483] | 0.361..0.517 | 3.097 [2.872, 3.302] | 2.304..3.708 |
| LastObservation | 0.452 [0.424, 0.478] | 0.361..0.517 | 3.786 [3.607, 3.982] | 3.339..4.413 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.449 [0.419, 0.473] | 0.350..0.511 | 2.826 [2.597, 3.033] | 2.048..3.359 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.431 [0.397, 0.468] | 0.339..0.533 | 2.587 [2.352, 2.838] | 1.885..3.314 |

### D=10,h=7

Cell `D=10,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.451 [0.405, 0.494] | 0.331..0.539 | 3.236 [2.903, 3.571] | 2.283..3.973 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.451 [0.405, 0.490] | 0.325..0.553 | 2.900 [2.514, 3.282] | 1.766..3.776 |
| LastObservation | 0.450 [0.401, 0.494] | 0.336..0.569 | 3.802 [3.503, 4.140] | 2.974..4.586 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.449 [0.404, 0.488] | 0.331..0.531 | 3.169 [2.811, 3.532] | 2.230..3.958 |
| MostFrequentLocation(hl=24h) | 0.449 [0.400, 0.496] | 0.325..0.567 | 3.110 [2.730, 3.499] | 1.930..3.933 |
| Markov1(a=1,cut=24h,hl=24h) | 0.449 [0.400, 0.496] | 0.325..0.567 | 3.110 [2.730, 3.499] | 1.930..3.933 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.430 [0.373, 0.484] | 0.275..0.567 | 2.607 [2.302, 2.938] | 1.801..3.496 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 12 households, 1027 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.477 [0.401, 0.543] | 0.294..0.672 | 3.615 [3.158, 4.142] | 2.263..4.876 |
| MostFrequentLocation(hl=24h) | 0.476 [0.401, 0.543] | 0.294..0.672 | 3.046 [2.572, 3.556] | 1.502..4.220 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.475 [0.406, 0.537] | 0.310..0.655 | 3.146 [2.699, 3.641] | 1.789..4.324 |
| Markov1(a=1,cut=24h,hl=24h) | 0.466 [0.394, 0.533] | 0.276..0.672 | 3.095 [2.617, 3.569] | 1.253..4.053 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.466 [0.397, 0.524] | 0.299..0.638 | 3.249 [2.865, 3.685] | 2.089..4.367 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.460 [0.386, 0.528] | 0.271..0.672 | 2.612 [2.203, 3.044] | 1.436..3.501 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.439 [0.373, 0.501] | 0.287..0.638 | 2.880 [2.449, 3.342] | 1.633..4.000 |

### D=14,h=3

Cell `D=14,h=3`: 12 households, 2160 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.448 [0.388, 0.501] | 0.289..0.606 | 2.920 [2.510, 3.389] | 1.737..3.915 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.439 [0.388, 0.486] | 0.317..0.578 | 3.363 [3.010, 3.763] | 2.200..4.206 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.435 [0.379, 0.483] | 0.300..0.572 | 3.300 [2.916, 3.735] | 2.188..4.248 |
| LastObservation | 0.431 [0.374, 0.484] | 0.300..0.578 | 3.927 [3.566, 4.327] | 2.917..4.835 |
| MostFrequentLocation(hl=24h) | 0.431 [0.375, 0.483] | 0.300..0.578 | 3.228 [2.811, 3.662] | 2.033..4.208 |
| Markov1(a=1,cut=24h,hl=24h) | 0.431 [0.375, 0.483] | 0.300..0.578 | 3.228 [2.811, 3.662] | 2.033..4.208 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.419 [0.362, 0.473] | 0.283..0.578 | 2.763 [2.381, 3.176] | 1.772..3.729 |

### D=14,h=7

Cell `D=14,h=7`: 12 households, 4320 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.472 [0.433, 0.513] | 0.350..0.597 | 3.064 [2.854, 3.270] | 2.375..3.682 |
| LastObservation | 0.472 [0.433, 0.512] | 0.342..0.603 | 3.647 [3.372, 3.916] | 2.744..4.548 |
| MostFrequentLocation(hl=24h) | 0.472 [0.434, 0.512] | 0.342..0.603 | 2.981 [2.773, 3.181] | 2.341..3.576 |
| Markov1(a=1,cut=24h,hl=24h) | 0.472 [0.434, 0.512] | 0.342..0.603 | 2.981 [2.773, 3.181] | 2.341..3.576 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.472 [0.434, 0.510] | 0.353..0.589 | 3.143 [2.939, 3.343] | 2.508..3.706 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.471 [0.439, 0.504] | 0.389..0.567 | 2.669 [2.474, 2.858] | 1.949..3.097 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.449 [0.411, 0.490] | 0.336..0.603 | 2.565 [2.357, 2.770] | 1.912..3.062 |
