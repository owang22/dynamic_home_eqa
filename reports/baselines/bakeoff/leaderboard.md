# Passive belief bake-off — horizon-controlled protocol

Frozen panel + candidate slate, evaluated with NO sensing: per checkpoint day D the belief sees the tour plus sightings from days before D only, and answers questions at forecast horizons h days past D. Cells are never pooled across h. The household is the unit of analysis throughout. (The old per-day passive curve is descriptive-only — it conflates history, recency, and horizon; this protocol replaces it for any learning-curve claim.)

## Headline cell D=7,h=1

Cell `D=7,h=1`: 20 households, 1661 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.476 [0.438, 0.517] | 0.349..0.629 | 3.244 [3.028, 3.430] | 2.280..4.022 |
| SmoothedRecency(hl=6h,freq=24h) | 0.469 [0.425, 0.517] | 0.276..0.663 | 3.363 [3.101, 3.594] | 2.235..4.319 |
| LastObservation | 0.467 [0.424, 0.513] | 0.318..0.663 | 3.567 [3.287, 3.832] | 2.328..4.503 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.460 [0.418, 0.506] | 0.276..0.629 | 3.312 [3.078, 3.519] | 2.258..4.155 |
| Markov1(a=1,cut=24h,hl=24h) | 0.452 [0.412, 0.493] | 0.264..0.629 | 3.441 [3.291, 3.561] | 2.792..3.959 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.451 [0.410, 0.497] | 0.276..0.629 | 3.104 [2.925, 3.250] | 2.284..3.698 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.450 [0.410, 0.489] | 0.325..0.607 | 3.387 [3.165, 3.577] | 2.390..4.117 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.446 [0.405, 0.496] | 0.318..0.652 | 3.259 [3.058, 3.434] | 2.310..3.914 |

## Recency stratification (pooled over checkpoints)

Accuracy binned by time since the belief's last sighting of the queried object — how fast each model's information decays (`recency_curves.png` plots this). Values are per-household means; n = questions pooled over the households that have the bin.

| model | [1h,6h) | [6h,24h) | [24h,72h) | [72h,inf) |
|---|---|---|---|---|
| LastObservation | 0.884 (n=79) | 0.560 (n=3982) | 0.445 (n=17191) | 0.387 (n=50748) |
| MostFrequentLocation(hl=24h) | 0.871 (n=79) | 0.557 (n=3982) | 0.453 (n=17191) | 0.397 (n=50748) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.743 (n=79) | 0.522 (n=3982) | 0.428 (n=17191) | 0.378 (n=50748) |
| Markov1(a=1,cut=24h,hl=24h) | 0.817 (n=79) | 0.517 (n=3982) | 0.451 (n=17191) | 0.394 (n=50748) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.884 (n=79) | 0.562 (n=3982) | 0.447 (n=17191) | 0.389 (n=50748) |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.794 (n=79) | 0.533 (n=3982) | 0.447 (n=17191) | 0.392 (n=50748) |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.871 (n=79) | 0.558 (n=3982) | 0.449 (n=17191) | 0.398 (n=50748) |
| SmoothedRecency(hl=6h,freq=24h) | 0.884 (n=79) | 0.562 (n=3982) | 0.449 (n=17191) | 0.394 (n=50748) |

Per-household winners at `D=7,h=1` (a model that only wins on one household type is still informative):

| household | best accuracy | best log-loss |
|---|---|---|
| households__generated__gpt-5.6-terra__hh_001 | Markov1(a=1,cut=24h,hl=24h) (0.386) | Markov1(a=1,cut=24h,hl=24h) (3.081) |
| households__generated__gpt-5.6-terra__hh_002 | LastObservation (0.494) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.086) |
| households__generated__gpt-5.6-terra__hh_003 | MostFrequentLocation(hl=24h) (0.544) | MostFrequentLocation(hl=24h) (2.981) |
| households__generated__gpt-5.6-terra__hh_004 | MostFrequentLocation(hl=24h) (0.581) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.717) |
| households__generated__gpt-5.6-terra__hh_005 | LastObservation (0.493) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.404) |
| households__generated__gpt-5.6-terra__hh_006 | LastObservation (0.448) | Markov1(a=1,cut=24h,hl=24h) (3.521) |
| households__generated__gpt-5.6-terra__hh_007 | MostFrequentLocation(hl=24h) (0.450) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.147) |
| households__generated__gpt-5.6-terra__hh_008 | LastObservation (0.453) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.150) |
| households__generated__gpt-5.6-terra__hh_009 | DaytypeMixture(K=3,bin=2h,hl=24h) (0.440) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.097) |
| households__generated__gpt-5.6-terra__hh_010 | MostFrequentLocation(hl=24h) (0.349) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.698) |
| households__generated__gpt-5.6-terra__hh_011 | LastObservation (0.573) | MostFrequentLocation(hl=24h) (2.748) |
| households__generated__gpt-5.6-terra__hh_012 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.529) | HierarchyBackoff(po=5,pc=5,hl=24h) (2.609) |
| households__generated__gpt-5.6-terra__hh_013 | LastObservation (0.607) | SmoothedRecency(hl=6h,freq=24h) (2.553) |
| households__generated__gpt-5.6-terra__hh_014 | LastObservation (0.481) | SmoothedRecency(hl=6h,freq=24h) (3.299) |
| households__generated__gpt-5.6-terra__hh_015 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.443) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.607) |
| households__generated__gpt-5.6-terra__hh_016 | LastObservation (0.663) | SmoothedRecency(hl=6h,freq=24h) (2.235) |
| households__generated__gpt-5.6-terra__hh_017 | MostFrequentLocation(hl=24h) (0.407) | Markov1(a=1,cut=24h,hl=24h) (3.301) |
| households__generated__gpt-5.6-terra__hh_018 | PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (0.407) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.412) |
| households__generated__gpt-5.6-terra__hh_019 | Markov1(a=1,cut=24h,hl=24h) (0.437) | HierarchyBackoff(po=5,pc=5,hl=24h) (3.063) |
| households__generated__gpt-5.6-terra__hh_020 | LastObservation (0.621) | LastObservation (2.620) |

## All cells

### D=1,h=3

Cell `D=1,h=3`: 20 households, 1800 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.437 [0.399, 0.472] | 0.300..0.544 | 3.539 [3.359, 3.771] | 2.912..4.964 |
| LastObservation | 0.431 [0.397, 0.465] | 0.300..0.533 | 3.826 [3.602, 4.069] | 3.142..4.835 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.431 [0.394, 0.467] | 0.300..0.544 | 3.638 [3.427, 3.874] | 2.884..4.847 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.427 [0.387, 0.468] | 0.289..0.556 | 3.633 [3.415, 3.869] | 2.889..4.847 |
| SmoothedRecency(hl=6h,freq=24h) | 0.427 [0.387, 0.469] | 0.300..0.556 | 3.679 [3.451, 3.920] | 2.982..4.847 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.427 [0.389, 0.463] | 0.300..0.556 | 3.632 [3.416, 3.869] | 2.863..4.847 |
| MostFrequentLocation(hl=24h) | 0.423 [0.387, 0.462] | 0.300..0.544 | 3.630 [3.415, 3.869] | 2.863..4.847 |
| Markov1(a=1,cut=24h,hl=24h) | 0.411 [0.377, 0.447] | 0.278..0.533 | 3.630 [3.415, 3.869] | 2.863..4.847 |

### D=1,h=7

Cell `D=1,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.403 [0.365, 0.439] | 0.242..0.547 | 3.701 [3.538, 3.873] | 2.967..4.425 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.400 [0.360, 0.440] | 0.228..0.542 | 3.830 [3.653, 4.017] | 2.947..4.474 |
| MostFrequentLocation(hl=24h) | 0.397 [0.364, 0.432] | 0.272..0.547 | 3.808 [3.630, 3.993] | 2.911..4.457 |
| SmoothedRecency(hl=6h,freq=24h) | 0.397 [0.363, 0.431] | 0.289..0.547 | 3.850 [3.654, 4.049] | 2.914..4.628 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.396 [0.365, 0.428] | 0.289..0.547 | 3.813 [3.638, 3.997] | 2.911..4.457 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.395 [0.363, 0.428] | 0.269..0.542 | 3.844 [3.665, 4.030] | 2.941..4.474 |
| LastObservation | 0.395 [0.363, 0.428] | 0.272..0.539 | 4.039 [3.843, 4.244] | 3.185..4.817 |
| Markov1(a=1,cut=24h,hl=24h) | 0.394 [0.359, 0.428] | 0.242..0.547 | 3.808 [3.630, 3.993] | 2.911..4.457 |

### D=3,h=0.25

(no questions in cell D=3,h=0.25)

### D=3,h=1

Cell `D=3,h=1`: 20 households, 1623 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.494 [0.447, 0.539] | 0.322..0.693 | 3.121 [2.871, 3.368] | 1.969..4.258 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.493 [0.439, 0.541] | 0.254..0.682 | 3.036 [2.828, 3.249] | 2.025..4.147 |
| SmoothedRecency(hl=6h,freq=24h) | 0.491 [0.443, 0.535] | 0.286..0.682 | 3.176 [2.920, 3.458] | 2.030..4.177 |
| MostFrequentLocation(hl=24h) | 0.484 [0.437, 0.531] | 0.238..0.670 | 3.107 [2.858, 3.353] | 1.943..4.180 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.483 [0.447, 0.522] | 0.309..0.659 | 3.160 [2.911, 3.405] | 2.047..4.291 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.477 [0.433, 0.521] | 0.286..0.682 | 3.128 [2.880, 3.375] | 1.938..4.227 |
| LastObservation | 0.465 [0.420, 0.514] | 0.254..0.682 | 3.411 [3.168, 3.671] | 2.198..4.490 |
| Markov1(a=1,cut=24h,hl=24h) | 0.458 [0.414, 0.500] | 0.254..0.636 | 3.491 [3.283, 3.713] | 2.642..4.515 |

### D=3,h=3

Cell `D=3,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.425 [0.390, 0.459] | 0.272..0.600 | 3.554 [3.362, 3.744] | 2.420..4.222 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.417 [0.374, 0.459] | 0.217..0.644 | 3.524 [3.327, 3.711] | 2.336..4.210 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.415 [0.377, 0.450] | 0.217..0.567 | 3.439 [3.265, 3.606] | 2.457..4.197 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.414 [0.378, 0.448] | 0.278..0.583 | 3.578 [3.382, 3.773] | 2.409..4.301 |
| MostFrequentLocation(hl=24h) | 0.413 [0.372, 0.451] | 0.217..0.589 | 3.530 [3.329, 3.723] | 2.364..4.224 |
| SmoothedRecency(hl=6h,freq=24h) | 0.411 [0.369, 0.450] | 0.217..0.583 | 3.613 [3.405, 3.819] | 2.369..4.188 |
| Markov1(a=1,cut=24h,hl=24h) | 0.409 [0.366, 0.448] | 0.256..0.589 | 3.530 [3.329, 3.723] | 2.364..4.224 |
| LastObservation | 0.397 [0.362, 0.433] | 0.217..0.567 | 3.937 [3.742, 4.133] | 2.993..4.686 |

### D=3,h=7

Cell `D=3,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.389 [0.359, 0.420] | 0.264..0.567 | 3.783 [3.640, 3.920] | 2.953..4.228 |
| SmoothedRecency(hl=6h,freq=24h) | 0.383 [0.348, 0.418] | 0.233..0.561 | 3.838 [3.672, 3.994] | 2.835..4.312 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.383 [0.352, 0.415] | 0.267..0.556 | 3.743 [3.606, 3.876] | 2.955..4.194 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.382 [0.349, 0.413] | 0.264..0.550 | 3.620 [3.491, 3.738] | 2.930..4.043 |
| MostFrequentLocation(hl=24h) | 0.380 [0.349, 0.414] | 0.264..0.561 | 3.745 [3.600, 3.885] | 2.885..4.206 |
| LastObservation | 0.375 [0.346, 0.405] | 0.264..0.550 | 4.141 [3.965, 4.308] | 3.108..4.663 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.375 [0.348, 0.404] | 0.261..0.542 | 3.814 [3.671, 3.951] | 2.964..4.248 |
| Markov1(a=1,cut=24h,hl=24h) | 0.375 [0.342, 0.407] | 0.233..0.561 | 3.745 [3.600, 3.885] | 2.885..4.206 |

### D=5,h=0.25

(no questions in cell D=5,h=0.25)

### D=5,h=1

Cell `D=5,h=1`: 20 households, 1605 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| LastObservation | 0.475 [0.429, 0.518] | 0.313..0.635 | 3.535 [3.261, 3.826] | 2.519..4.449 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.474 [0.429, 0.516] | 0.322..0.635 | 3.295 [3.041, 3.557] | 2.483..4.299 |
| SmoothedRecency(hl=6h,freq=24h) | 0.472 [0.427, 0.515] | 0.313..0.635 | 3.326 [3.069, 3.608] | 2.367..4.374 |
| MostFrequentLocation(hl=24h) | 0.470 [0.426, 0.512] | 0.313..0.635 | 3.312 [3.068, 3.574] | 2.434..4.286 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.469 [0.426, 0.510] | 0.322..0.612 | 3.302 [3.064, 3.557] | 2.504..4.290 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.462 [0.416, 0.505] | 0.313..0.635 | 3.337 [3.089, 3.604] | 2.451..4.294 |
| Markov1(a=1,cut=24h,hl=24h) | 0.449 [0.406, 0.488] | 0.311..0.600 | 3.766 [3.523, 4.005] | 2.905..4.843 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.444 [0.397, 0.487] | 0.289..0.589 | 3.407 [3.163, 3.672] | 2.627..4.386 |

### D=5,h=3

Cell `D=5,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.416 [0.381, 0.451] | 0.322..0.572 | 3.658 [3.442, 3.869] | 2.622..4.330 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.411 [0.368, 0.452] | 0.217..0.572 | 3.569 [3.361, 3.767] | 2.650..4.229 |
| LastObservation | 0.410 [0.372, 0.450] | 0.261..0.600 | 3.958 [3.710, 4.191] | 2.763..4.540 |
| SmoothedRecency(hl=6h,freq=24h) | 0.409 [0.371, 0.447] | 0.267..0.572 | 3.703 [3.478, 3.922] | 2.576..4.381 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.408 [0.366, 0.449] | 0.217..0.578 | 3.651 [3.435, 3.869] | 2.664..4.342 |
| MostFrequentLocation(hl=24h) | 0.406 [0.368, 0.445] | 0.272..0.572 | 3.658 [3.442, 3.869] | 2.622..4.330 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.395 [0.351, 0.436] | 0.217..0.583 | 3.707 [3.490, 3.923] | 2.689..4.324 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.383 [0.340, 0.423] | 0.211..0.550 | 3.751 [3.534, 3.960] | 2.776..4.342 |

### D=5,h=7

Cell `D=5,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.405 [0.371, 0.439] | 0.281..0.531 | 3.578 [3.417, 3.740] | 2.932..4.202 |
| Markov1(a=1,cut=24h,hl=24h) | 0.403 [0.376, 0.431] | 0.319..0.531 | 3.706 [3.541, 3.866] | 2.951..4.336 |
| SmoothedRecency(hl=6h,freq=24h) | 0.400 [0.364, 0.433] | 0.244..0.531 | 3.779 [3.604, 3.951] | 2.958..4.418 |
| MostFrequentLocation(hl=24h) | 0.394 [0.358, 0.430] | 0.244..0.531 | 3.706 [3.541, 3.866] | 2.951..4.336 |
| LastObservation | 0.393 [0.357, 0.427] | 0.233..0.522 | 3.992 [3.804, 4.188] | 3.302..4.728 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.388 [0.358, 0.418] | 0.283..0.528 | 3.707 [3.548, 3.860] | 2.954..4.309 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.375 [0.339, 0.411] | 0.250..0.531 | 3.764 [3.603, 3.923] | 3.052..4.391 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.366 [0.330, 0.401] | 0.231..0.519 | 3.795 [3.633, 3.950] | 3.095..4.409 |

### D=7,h=0.25

(no questions in cell D=7,h=0.25)

### D=7,h=1

Cell `D=7,h=1`: 20 households, 1661 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.476 [0.438, 0.517] | 0.349..0.629 | 3.244 [3.028, 3.430] | 2.280..4.022 |
| SmoothedRecency(hl=6h,freq=24h) | 0.469 [0.425, 0.517] | 0.276..0.663 | 3.363 [3.101, 3.594] | 2.235..4.319 |
| LastObservation | 0.467 [0.424, 0.513] | 0.318..0.663 | 3.567 [3.287, 3.832] | 2.328..4.503 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.460 [0.418, 0.506] | 0.276..0.629 | 3.312 [3.078, 3.519] | 2.258..4.155 |
| Markov1(a=1,cut=24h,hl=24h) | 0.452 [0.412, 0.493] | 0.264..0.629 | 3.441 [3.291, 3.561] | 2.792..3.959 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.451 [0.410, 0.497] | 0.276..0.629 | 3.104 [2.925, 3.250] | 2.284..3.698 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.450 [0.410, 0.489] | 0.325..0.607 | 3.387 [3.165, 3.577] | 2.390..4.117 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.446 [0.405, 0.496] | 0.318..0.652 | 3.259 [3.058, 3.434] | 2.310..3.914 |

### D=7,h=3

Cell `D=7,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.428 [0.403, 0.458] | 0.306..0.589 | 3.570 [3.357, 3.748] | 2.456..4.217 |
| Markov1(a=1,cut=24h,hl=24h) | 0.414 [0.384, 0.446] | 0.261..0.589 | 3.570 [3.357, 3.748] | 2.456..4.217 |
| SmoothedRecency(hl=6h,freq=24h) | 0.409 [0.378, 0.444] | 0.261..0.594 | 3.690 [3.471, 3.880] | 2.478..4.310 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.408 [0.373, 0.444] | 0.250..0.594 | 3.640 [3.432, 3.822] | 2.499..4.288 |
| LastObservation | 0.405 [0.377, 0.441] | 0.278..0.600 | 3.931 [3.709, 4.127] | 2.763..4.920 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.404 [0.377, 0.436] | 0.306..0.583 | 3.586 [3.379, 3.761] | 2.478..4.252 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.401 [0.368, 0.435] | 0.261..0.589 | 3.402 [3.203, 3.564] | 2.476..3.937 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.396 [0.372, 0.423] | 0.283..0.544 | 3.716 [3.521, 3.900] | 2.614..4.456 |

### D=7,h=7

Cell `D=7,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.444 [0.414, 0.475] | 0.278..0.561 | 3.517 [3.295, 3.738] | 2.591..4.907 |
| Markov1(a=1,cut=24h,hl=24h) | 0.437 [0.401, 0.471] | 0.222..0.561 | 3.517 [3.295, 3.738] | 2.591..4.907 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.432 [0.397, 0.465] | 0.222..0.542 | 3.414 [3.195, 3.632] | 2.506..4.748 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.432 [0.403, 0.462] | 0.283..0.553 | 3.520 [3.303, 3.740] | 2.655..4.888 |
| SmoothedRecency(hl=6h,freq=24h) | 0.432 [0.396, 0.467] | 0.222..0.550 | 3.592 [3.380, 3.799] | 2.795..4.928 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.430 [0.397, 0.462] | 0.217..0.533 | 3.590 [3.377, 3.798] | 2.741..4.914 |
| LastObservation | 0.427 [0.396, 0.460] | 0.278..0.561 | 3.852 [3.646, 4.066] | 3.015..4.997 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.418 [0.390, 0.448] | 0.272..0.547 | 3.642 [3.435, 3.852] | 2.905..4.933 |

### D=10,h=0.25

(no questions in cell D=10,h=0.25)

### D=10,h=1

Cell `D=10,h=1`: 20 households, 1609 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.478 [0.445, 0.510] | 0.321..0.639 | 3.197 [2.993, 3.416] | 2.440..3.916 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.477 [0.451, 0.503] | 0.358..0.593 | 3.100 [2.912, 3.298] | 2.405..3.750 |
| SmoothedRecency(hl=6h,freq=24h) | 0.476 [0.443, 0.509] | 0.321..0.639 | 3.343 [3.128, 3.574] | 2.448..4.362 |
| LastObservation | 0.466 [0.434, 0.496] | 0.338..0.593 | 3.540 [3.347, 3.739] | 2.580..4.392 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.465 [0.427, 0.504] | 0.338..0.663 | 3.210 [3.008, 3.430] | 2.385..3.886 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.462 [0.430, 0.492] | 0.321..0.593 | 3.274 [3.078, 3.478] | 2.433..4.026 |
| Markov1(a=1,cut=24h,hl=24h) | 0.456 [0.424, 0.489] | 0.338..0.639 | 3.372 [3.155, 3.593] | 2.287..4.259 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.424 [0.398, 0.451] | 0.321..0.535 | 3.344 [3.150, 3.546] | 2.476..3.997 |

### D=10,h=3

Cell `D=10,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| MostFrequentLocation(hl=24h) | 0.426 [0.402, 0.450] | 0.350..0.539 | 3.555 [3.389, 3.731] | 2.875..4.348 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.425 [0.403, 0.447] | 0.344..0.539 | 3.451 [3.290, 3.631] | 2.873..4.324 |
| Markov1(a=1,cut=24h,hl=24h) | 0.424 [0.395, 0.453] | 0.272..0.539 | 3.555 [3.389, 3.731] | 2.875..4.348 |
| SmoothedRecency(hl=6h,freq=24h) | 0.423 [0.398, 0.449] | 0.344..0.539 | 3.637 [3.464, 3.818] | 2.876..4.308 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.420 [0.391, 0.447] | 0.283..0.528 | 3.549 [3.379, 3.729] | 2.936..4.372 |
| LastObservation | 0.416 [0.388, 0.441] | 0.272..0.539 | 3.922 [3.766, 4.075] | 3.185..4.494 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.414 [0.385, 0.441] | 0.267..0.517 | 3.624 [3.460, 3.796] | 2.952..4.334 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.391 [0.366, 0.416] | 0.267..0.489 | 3.700 [3.545, 3.866] | 3.038..4.444 |

### D=10,h=7

Cell `D=10,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.388 [0.355, 0.415] | 0.172..0.503 | 3.537 [3.403, 3.687] | 3.036..4.379 |
| MostFrequentLocation(hl=24h) | 0.386 [0.358, 0.414] | 0.256..0.525 | 3.681 [3.538, 3.826] | 3.079..4.418 |
| Markov1(a=1,cut=24h,hl=24h) | 0.380 [0.353, 0.409] | 0.256..0.525 | 3.681 [3.538, 3.826] | 3.079..4.418 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.380 [0.343, 0.416] | 0.194..0.531 | 3.644 [3.498, 3.786] | 3.048..4.337 |
| SmoothedRecency(hl=6h,freq=24h) | 0.379 [0.345, 0.412] | 0.172..0.525 | 3.837 [3.680, 3.996] | 3.121..4.472 |
| LastObservation | 0.372 [0.347, 0.397] | 0.256..0.483 | 4.152 [3.989, 4.308] | 3.327..4.868 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.371 [0.343, 0.401] | 0.256..0.511 | 3.776 [3.628, 3.919] | 3.115..4.449 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.353 [0.329, 0.377] | 0.247..0.472 | 3.820 [3.678, 3.957] | 3.144..4.450 |

### D=14,h=0.25

(no questions in cell D=14,h=0.25)

### D=14,h=1

Cell `D=14,h=1`: 20 households, 1656 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.485 [0.451, 0.524] | 0.349..0.644 | 2.992 [2.816, 3.149] | 2.210..3.697 |
| SmoothedRecency(hl=6h,freq=24h) | 0.482 [0.442, 0.522] | 0.313..0.621 | 3.301 [3.045, 3.545] | 2.148..4.284 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.480 [0.444, 0.521] | 0.349..0.632 | 3.261 [3.034, 3.469] | 2.260..4.081 |
| MostFrequentLocation(hl=24h) | 0.479 [0.444, 0.521] | 0.349..0.644 | 3.144 [2.935, 3.335] | 2.182..3.950 |
| LastObservation | 0.477 [0.440, 0.519] | 0.333..0.643 | 3.525 [3.277, 3.763] | 2.484..4.531 |
| Markov1(a=1,cut=24h,hl=24h) | 0.467 [0.434, 0.507] | 0.345..0.644 | 3.327 [3.178, 3.462] | 2.508..3.844 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.457 [0.420, 0.501] | 0.325..0.701 | 3.219 [3.027, 3.389] | 2.160..3.788 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.448 [0.415, 0.487] | 0.313..0.609 | 3.372 [3.146, 3.568] | 2.356..4.101 |

### D=14,h=3

Cell `D=14,h=3`: 20 households, 3600 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.408 [0.372, 0.449] | 0.261..0.572 | 3.559 [3.362, 3.751] | 2.610..4.389 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.408 [0.375, 0.444] | 0.261..0.567 | 3.399 [3.219, 3.583] | 2.559..4.197 |
| MostFrequentLocation(hl=24h) | 0.408 [0.374, 0.445] | 0.289..0.567 | 3.559 [3.362, 3.751] | 2.610..4.389 |
| SmoothedRecency(hl=6h,freq=24h) | 0.405 [0.366, 0.447] | 0.261..0.567 | 3.791 [3.533, 4.024] | 2.638..4.903 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.404 [0.372, 0.438] | 0.278..0.550 | 3.689 [3.483, 3.893] | 2.672..4.447 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.397 [0.362, 0.435] | 0.272..0.567 | 3.571 [3.395, 3.743] | 2.615..4.369 |
| LastObservation | 0.396 [0.362, 0.432] | 0.256..0.539 | 4.042 [3.782, 4.289] | 3.189..4.970 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.378 [0.345, 0.414] | 0.233..0.567 | 3.745 [3.561, 3.925] | 2.667..4.439 |

### D=14,h=7

Cell `D=14,h=7`: 20 households, 7200 questions total. Accuracy/log-loss are unweighted per-household means; brackets are the 95% bootstrap interval over households; per-household spread is min..max.

| model | top-1 accuracy | acc spread | mean log-loss | loss spread |
|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h) | 0.442 [0.416, 0.469] | 0.336..0.569 | 3.401 [3.240, 3.564] | 2.577..4.057 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.442 [0.418, 0.468] | 0.356..0.561 | 3.295 [3.137, 3.464] | 2.527..3.972 |
| MostFrequentLocation(hl=24h) | 0.442 [0.415, 0.470] | 0.322..0.569 | 3.401 [3.240, 3.564] | 2.577..4.057 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.440 [0.412, 0.466] | 0.325..0.567 | 3.422 [3.277, 3.570] | 2.721..4.031 |
| SmoothedRecency(hl=6h,freq=24h) | 0.438 [0.409, 0.468] | 0.322..0.569 | 3.542 [3.366, 3.708] | 2.637..4.246 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.433 [0.407, 0.461] | 0.306..0.569 | 3.528 [3.369, 3.692] | 2.738..4.141 |
| LastObservation | 0.427 [0.399, 0.456] | 0.333..0.575 | 3.870 [3.682, 4.051] | 2.892..4.609 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.412 [0.389, 0.436] | 0.314..0.528 | 3.604 [3.456, 3.760] | 2.940..4.207 |
