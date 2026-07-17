# Stage 1b re-gate

targets: 36 objects (static=12, occasional=12, dynamic=12), test days [8, 10, 12], grid 60min + transition-aware fine points, cluster-bootstrap 95% CIs (n_boot=500)

## Per-stratum accuracy (B1/B2/B5) — headline = `displaced`

| tier | qtype | stratum | all | displaced | returned | stable |
|---|---|---|---|---|---|---|
| b0_lastseen | location_now | ALL | 0.777 [0.725,0.834] (n=36823) | 0.147 [0.130,0.165] (n=9617) | 1.000 [1.000,1.000] (n=1184) | 1.000 [1.000,1.000] (n=26022) |
| b0_lastseen | location_now | static | 0.988 [0.965,1.000] (n=10038) | 0.098 [0.098,0.098] (n=132) | — | 1.000 [1.000,1.000] (n=9906) |
| b0_lastseen | location_now | occasional | 0.783 [0.719,0.836] (n=11777) | 0.143 [0.118,0.160] (n=2984) | — | 1.000 [1.000,1.000] (n=8793) |
| b0_lastseen | location_now | dynamic | 0.632 [0.578,0.717] (n=15008) | 0.150 [0.127,0.175] (n=6501) | 1.000 [1.000,1.000] (n=1184) | 1.000 [1.000,1.000] (n=7323) |
| b0_lastseen | room_now | ALL | 0.765 [0.711,0.838] (n=36823) | 0.099 [0.009,0.260] (n=9617) | 1.000 [1.000,1.000] (n=1184) | 1.000 [1.000,1.000] (n=26022) |
| b0_lastseen | room_now | static | 0.987 [0.961,1.000] (n=10038) | 0.000 [0.000,0.000] (n=132) | — | 1.000 [1.000,1.000] (n=9906) |
| b0_lastseen | room_now | occasional | 0.752 [0.675,0.813] (n=11777) | 0.022 [0.000,0.065] (n=2984) | — | 1.000 [1.000,1.000] (n=8793) |
| b0_lastseen | room_now | dynamic | 0.626 [0.522,0.729] (n=15008) | 0.136 [0.008,0.349] (n=6501) | 1.000 [1.000,1.000] (n=1184) | 1.000 [1.000,1.000] (n=7323) |
| b1_longmem | location_now | ALL | 0.770 [0.720,0.828] (n=36823) | 0.346 [0.275,0.402] (n=9617) | 0.953 [0.838,1.000] (n=1184) | 0.919 [0.883,0.951] (n=26022) |
| b1_longmem | location_now | static | 0.987 [0.963,1.000] (n=10038) | 0.098 [0.098,0.098] (n=132) | — | 0.999 [0.998,1.000] (n=9906) |
| b1_longmem | location_now | occasional | 0.768 [0.684,0.825] (n=11777) | 0.268 [0.133,0.403] (n=2984) | — | 0.938 [0.891,0.970] (n=8793) |
| b1_longmem | location_now | dynamic | 0.627 [0.567,0.710] (n=15008) | 0.386 [0.306,0.458] (n=6501) | 0.953 [0.838,1.000] (n=1184) | 0.788 [0.710,0.865] (n=7323) |
| b1_longmem | room_now | ALL | 0.666 [0.583,0.769] (n=36823) | 0.115 [0.015,0.272] (n=9617) | 0.929 [0.628,1.000] (n=1184) | 0.858 [0.797,0.912] (n=26022) |
| b1_longmem | room_now | static | 0.985 [0.957,1.000] (n=10038) | 0.000 [0.000,0.000] (n=132) | — | 0.998 [0.995,1.000] (n=9906) |
| b1_longmem | room_now | occasional | 0.654 [0.538,0.754] (n=11777) | 0.000 [0.000,0.000] (n=2984) | — | 0.876 [0.798,0.937] (n=8793) |
| b1_longmem | room_now | dynamic | 0.462 [0.315,0.627] (n=15008) | 0.170 [0.024,0.373] (n=6501) | 0.929 [0.628,1.000] (n=1184) | 0.645 [0.516,0.777] (n=7323) |
| b2_classdecay | location_now | ALL | 0.830 [0.789,0.873] (n=36823) | 0.348 [0.306,0.393] (n=9617) | 0.997 [0.987,1.000] (n=1184) | 1.000 [1.000,1.000] (n=26022) |
| b2_classdecay | location_now | static | 0.993 [0.979,1.000] (n=10038) | 0.455 [0.455,0.455] (n=132) | — | 1.000 [1.000,1.000] (n=9906) |
| b2_classdecay | location_now | occasional | 0.836 [0.775,0.879] (n=11777) | 0.352 [0.232,0.475] (n=2984) | — | 1.000 [1.000,1.000] (n=8793) |
| b2_classdecay | location_now | dynamic | 0.716 [0.666,0.779] (n=15008) | 0.344 [0.303,0.383] (n=6501) | 0.997 [0.987,1.000] (n=1184) | 1.000 [1.000,1.000] (n=7323) |
| b2_classdecay | room_now | ALL | 0.766 [0.712,0.838] (n=36823) | 0.104 [0.010,0.264] (n=9617) | 0.992 [0.960,1.000] (n=1184) | 1.000 [1.000,1.000] (n=26022) |
| b2_classdecay | room_now | static | 0.987 [0.961,1.000] (n=10038) | 0.000 [0.000,0.000] (n=132) | — | 1.000 [1.000,1.000] (n=9906) |
| b2_classdecay | room_now | occasional | 0.752 [0.675,0.813] (n=11777) | 0.022 [0.000,0.065] (n=2984) | — | 1.000 [1.000,1.000] (n=8793) |
| b2_classdecay | room_now | dynamic | 0.628 [0.524,0.731] (n=15008) | 0.143 [0.009,0.353] (n=6501) | 0.992 [0.960,1.000] (n=1184) | 1.000 [1.000,1.000] (n=7323) |
| b3_perpetua_star(fremen) | location_now | ALL | 0.818 [0.774,0.868] (n=36823) | 0.387 [0.263,0.510] (n=9617) | 0.948 [0.738,1.000] (n=1184) | 0.972 [0.957,0.985] (n=26022) |
| b3_perpetua_star(fremen) | location_now | static | 0.974 [0.945,0.997] (n=10038) | 0.098 [0.098,0.098] (n=132) | — | 0.985 [0.964,1.000] (n=9906) |
| b3_perpetua_star(fremen) | location_now | occasional | 0.803 [0.750,0.841] (n=11777) | 0.293 [0.145,0.436] (n=2984) | — | 0.975 [0.963,0.990] (n=8793) |
| b3_perpetua_star(fremen) | location_now | dynamic | 0.726 [0.645,0.807] (n=15008) | 0.435 [0.274,0.606] (n=6501) | 0.948 [0.738,1.000] (n=1184) | 0.949 [0.910,0.982] (n=7323) |
| b3_perpetua_star(fremen) | room_now | ALL | 0.778 [0.716,0.850] (n=36823) | 0.283 [0.107,0.464] (n=9617) | 0.949 [0.732,1.000] (n=1184) | 0.953 [0.923,0.976] (n=26022) |
| b3_perpetua_star(fremen) | room_now | static | 0.968 [0.932,0.996] (n=10038) | 0.000 [0.000,0.000] (n=132) | — | 0.981 [0.954,1.000] (n=9906) |
| b3_perpetua_star(fremen) | room_now | occasional | 0.734 [0.663,0.795] (n=11777) | 0.077 [0.012,0.163] (n=2984) | — | 0.957 [0.934,0.982] (n=8793) |
| b3_perpetua_star(fremen) | room_now | dynamic | 0.686 [0.569,0.797] (n=15008) | 0.383 [0.146,0.600] (n=6501) | 0.949 [0.732,1.000] (n=1184) | 0.912 [0.843,0.971] (n=7323) |
| b3_perpetua_star(schedule_prior) | location_now | ALL | 0.815 [0.769,0.867] (n=36823) | 0.389 [0.266,0.515] (n=9617) | 0.937 [0.712,1.000] (n=1184) | 0.967 [0.950,0.982] (n=26022) |
| b3_perpetua_star(schedule_prior) | location_now | static | 0.972 [0.944,0.996] (n=10038) | 0.098 [0.098,0.098] (n=132) | — | 0.984 [0.960,1.000] (n=9906) |
| b3_perpetua_star(schedule_prior) | location_now | occasional | 0.796 [0.743,0.835] (n=11777) | 0.302 [0.148,0.456] (n=2984) | — | 0.963 [0.944,0.984] (n=8793) |
| b3_perpetua_star(schedule_prior) | location_now | dynamic | 0.725 [0.642,0.808] (n=15008) | 0.434 [0.275,0.601] (n=6501) | 0.937 [0.712,1.000] (n=1184) | 0.950 [0.909,0.982] (n=7323) |
| b3_perpetua_star(schedule_prior) | room_now | ALL | 0.775 [0.713,0.847] (n=36823) | 0.297 [0.119,0.470] (n=9617) | 0.949 [0.732,1.000] (n=1184) | 0.944 [0.915,0.969] (n=26022) |
| b3_perpetua_star(schedule_prior) | room_now | static | 0.964 [0.925,0.995] (n=10038) | 0.000 [0.000,0.000] (n=132) | — | 0.977 [0.944,1.000] (n=9906) |
| b3_perpetua_star(schedule_prior) | room_now | occasional | 0.724 [0.651,0.784] (n=11777) | 0.109 [0.015,0.234] (n=2984) | — | 0.932 [0.895,0.969] (n=8793) |
| b3_perpetua_star(schedule_prior) | room_now | dynamic | 0.689 [0.571,0.800] (n=15008) | 0.389 [0.152,0.596] (n=6501) | 0.949 [0.732,1.000] (n=1184) | 0.913 [0.850,0.966] (n=7323) |

## Transition-conditioned partition (B3, location_now)

| tier | bin | v |
|---|---|---|
| b0_lastseen | 0 transitions in interval | 1.000 [1.000,1.000] (n=26022) |
| b0_lastseen | >=1 transition in interval | 0.241 [0.170,0.337] (n=10801) |
| b0_lastseen | displaced, 1 transition | 0.143 [0.125,0.162] (n=8280) |
| b0_lastseen | displaced, >=2 transitions | 0.172 [0.146,0.202] (n=1337) |
| b0_lastseen | displaced, last trans <60min before query | 0.154 [0.134,0.173] (n=3059) |
| b0_lastseen | displaced, last trans >=240min before query | 0.145 [0.127,0.166] (n=3850) |
| b1_longmem | 0 transitions in interval | 0.919 [0.883,0.951] (n=26022) |
| b1_longmem | >=1 transition in interval | 0.412 [0.312,0.497] (n=10801) |
| b1_longmem | displaced, 1 transition | 0.353 [0.282,0.405] (n=8280) |
| b1_longmem | displaced, >=2 transitions | 0.304 [0.160,0.519] (n=1337) |
| b1_longmem | displaced, last trans <60min before query | 0.342 [0.286,0.395] (n=3059) |
| b1_longmem | displaced, last trans >=240min before query | 0.354 [0.259,0.446] (n=3850) |
| b2_classdecay | 0 transitions in interval | 1.000 [1.000,1.000] (n=26022) |
| b2_classdecay | >=1 transition in interval | 0.419 [0.347,0.498] (n=10801) |
| b2_classdecay | displaced, 1 transition | 0.353 [0.313,0.391] (n=8280) |
| b2_classdecay | displaced, >=2 transitions | 0.317 [0.198,0.511] (n=1337) |
| b2_classdecay | displaced, last trans <60min before query | 0.349 [0.309,0.396] (n=3059) |
| b2_classdecay | displaced, last trans >=240min before query | 0.354 [0.292,0.418] (n=3850) |
| b3_perpetua_star(fremen) | 0 transitions in interval | 0.972 [0.957,0.985] (n=26022) |
| b3_perpetua_star(fremen) | >=1 transition in interval | 0.448 [0.322,0.569] (n=10801) |
| b3_perpetua_star(fremen) | displaced, 1 transition | 0.389 [0.255,0.522] (n=8280) |
| b3_perpetua_star(fremen) | displaced, >=2 transitions | 0.369 [0.230,0.594] (n=1337) |
| b3_perpetua_star(fremen) | displaced, last trans <60min before query | 0.336 [0.267,0.410] (n=3059) |
| b3_perpetua_star(fremen) | displaced, last trans >=240min before query | 0.476 [0.304,0.646] (n=3850) |
| b3_perpetua_star(schedule_prior) | 0 transitions in interval | 0.967 [0.950,0.982] (n=26022) |
| b3_perpetua_star(schedule_prior) | >=1 transition in interval | 0.449 [0.322,0.569] (n=10801) |
| b3_perpetua_star(schedule_prior) | displaced, 1 transition | 0.391 [0.258,0.524] (n=8280) |
| b3_perpetua_star(schedule_prior) | displaced, >=2 transitions | 0.372 [0.231,0.602] (n=1337) |
| b3_perpetua_star(schedule_prior) | displaced, last trans <60min before query | 0.332 [0.265,0.406] (n=3059) |
| b3_perpetua_star(schedule_prior) | displaced, last trans >=240min before query | 0.481 [0.308,0.650] (n=3850) |

## C2 (b3 mass accounting, post-fix)

```json
{
 "b3_perpetua_star(fremen)": {
  "mean_p_elsewhere": 0.2746,
  "mean_p_true": 0.5768
 },
 "b3_perpetua_star(schedule_prior)": {
  "mean_p_elsewhere": 0.2753,
  "mean_p_true": 0.5776
 }
}
```

## C3 (Δt hygiene + nested time-of-day test)

```json
{
 "b0_lastseen": {
  "delta_t_R2": 0.249,
  "nested_tod": {
   "n_cells": 6172,
   "rss_dt_only": 1344.0918,
   "rss_dt_plus_tod": 1334.3251,
   "F": 5.637,
   "p_value": 3.7559993653413647e-07,
   "tod_terms_significant": true
  }
 },
 "b1_longmem": {
  "delta_t_R2": "n/a (\u0394t not a model input)"
 },
 "b2_classdecay": {
  "delta_t_R2": 0.2187,
  "nested_tod": {
   "n_cells": 6172,
   "rss_dt_only": 1255.3941,
   "rss_dt_plus_tod": 1245.7021,
   "F": 5.992,
   "p_value": 1.0920171851336397e-07,
   "tod_terms_significant": true
  }
 },
 "b3_perpetua_star(fremen)": {
  "delta_t_R2": 0.2445,
  "nested_tod": {
   "n_cells": 6172,
   "rss_dt_only": 1293.5424,
   "rss_dt_plus_tod": 1282.8619,
   "F": 6.412,
   "p_value": 2.503362048366137e-08,
   "tod_terms_significant": true
  }
 },
 "b3_perpetua_star(schedule_prior)": {
  "delta_t_R2": 0.2493,
  "nested_tod": {
   "n_cells": 6172,
   "rss_dt_only": 1289.4643,
   "rss_dt_plus_tod": 1277.6445,
   "F": 7.125,
   "p_value": 2.003431683684308e-09,
   "tod_terms_significant": true
  }
 }
}
```

## D1 ECE (p_chosen)

```json
{
 "b0_lastseen__location_now": 0.1491,
 "b0_lastseen__room_now": 0.2327,
 "b1_longmem__location_now": 0.1303,
 "b1_longmem__room_now": 0.1853,
 "b2_classdecay__location_now": 0.1591,
 "b2_classdecay__room_now": 0.1858,
 "b3_perpetua_star(fremen)__location_now": 0.185,
 "b3_perpetua_star(fremen)__room_now": 0.0715,
 "b3_perpetua_star(schedule_prior)__location_now": 0.1835,
 "b3_perpetua_star(schedule_prior)__room_now": 0.0695
}
```

## D2 temperature hook (fit day 8, evaluated on the others; NOT applied to gate numbers)

```json
{
 "b0_lastseen": {
  "T": 4.0,
  "ece_p_true_pre": 0.0377,
  "ece_p_true_post": 0.0525
 },
 "b1_longmem": {
  "T": 1.4,
  "ece_p_true_pre": 0.1668,
  "ece_p_true_post": 0.1916
 },
 "b2_classdecay": {
  "T": 2.15,
  "ece_p_true_pre": 0.1076,
  "ece_p_true_post": 0.1576
 },
 "b3_perpetua_star(fremen)": {
  "T": 1.2,
  "ece_p_true_pre": 0.2428,
  "ece_p_true_post": 0.257
 },
 "b3_perpetua_star(schedule_prior)": {
  "T": 1.2,
  "ece_p_true_pre": 0.2377,
  "ece_p_true_post": 0.2517
 }
}
```

## E1 two-anchor diagnostic (dynamic stratum, displaced)

```json
{
 "b3_perpetua_star(fremen)": {
  "displaced_acc_1anchor": "0.435 [0.274,0.606] (n=6501)",
  "displaced_acc_2anchor": "0.644 [0.554,0.740] (n=6501)"
 },
 "b3_perpetua_star(schedule_prior)": {
  "displaced_acc_1anchor": "0.434 [0.275,0.601] (n=6501)",
  "displaced_acc_2anchor": "0.644 [0.553,0.739] (n=6501)"
 }
}
```

## C1 room_now distinctness

```json
{
 "n_room_now_checked": 324,
 "n_with_duplicate_rooms": 0,
 "index_balance": [
  0.2808641975308642,
  0.29012345679012347,
  0.20679012345679013,
  0.2222222222222222
 ]
}
```
