# Per-household passive analysis

20 households x 2 seeds (0, 1), 7 belief models + the routine oracle. Seeds of one home are pooled (equal question counts, so this is the seed mean); the last column of the overview is the largest across-seed range any model showed on that home, the noise floor for reading its row. Commit `f78a418bc019`, run 2026-09-05T01:28:51.

Two evaluation modes over the same questions:

- **kept current** (continuous): the belief is updated with every sighting strictly before each query and answers about now. Query day is the history length; the age of the object's last sighting is recorded per question.
- **frozen forecast**: the bake-off protocol. The belief is frozen at day D and answers questions up to 7 days later, bucketed by horizon; the headline cell is D=7, h=1 (questions 6-24h after the freeze).

The routine oracle predicts from the household's authored rules re-realized under many seeds, with no observations: routine knowledge alone. Not a hard ceiling; a fresh sighting beats it.

## Which homes separate the models (belief kept current)

Sorted by the oracle within resident group, so the most routine-predictable home of each group comes first.

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.576 | 0.530 | 0.519 | 0.576 | 0.506 | 0.522 | 0.520 | 0.737 | LastObs | 0.054 | 0.000 | 0.162 | 0.059 | +0.000 (0/2) |
| hh_012 | researcher_household | 1 | 0.496 | 0.495 | 0.447 | 0.487 | 0.456 | 0.468 | 0.466 | 0.730 | LastObs | 0.028 | 0.000 | 0.234 | 0.094 | +0.000 (0/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.506 | 0.569 | 0.548 | 0.537 | 0.484 | 0.502 | 0.495 | 0.729 | Periodic | 0.063 | 0.063 | 0.160 | 0.072 | +0.063 (2/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.436 | 0.472 | 0.485 | 0.474 | 0.441 | 0.470 | 0.464 | 0.719 | DaytypeMix | 0.015 | 0.050 | 0.234 | 0.071 | +0.050 (2/2) |
| hh_019 | working_professional_solo | 1 | 0.530 | 0.528 | 0.508 | 0.484 | 0.481 | 0.488 | 0.486 | 0.713 | LastObs | 0.041 | 0.000 | 0.183 | 0.097 | +0.000 (0/2) |
| hh_014 | single_adult_wfh | 1 | 0.658 | 0.659 | 0.632 | 0.663 | 0.598 | 0.621 | 0.615 | 0.710 | SmoothedRec | 0.031 | 0.005 | 0.048 | 0.018 | +0.005 (2/2) |
| hh_016 | single_senior_solo | 1 | 0.627 | 0.628 | 0.602 | 0.626 | 0.578 | 0.592 | 0.588 | 0.684 | Periodic | 0.026 | 0.001 | 0.056 | 0.022 | +0.001 (1/2) |
| **1-resident mean** |  | 7 | 0.547 | 0.555 | 0.534 | 0.549 | 0.506 | 0.523 | 0.519 | 0.717 |  | 0.037 | 0.017 | 0.154 |  |  |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.512 | 0.490 | 0.507 | 0.491 | 0.531 | 0.545 | 0.539 | 0.776 | PerpetuaStar | 0.033 | 0.033 | 0.230 | 0.055 | +0.033 (2/2) |
| hh_018 | working_couple_no_children | 2 | 0.508 | 0.507 | 0.592 | 0.507 | 0.506 | 0.527 | 0.525 | 0.753 | DaytypeMix | 0.084 | 0.084 | 0.161 | 0.012 | +0.084 (2/2) |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.488 | 0.442 | 0.433 | 0.442 | 0.409 | 0.427 | 0.423 | 0.728 | LastObs | 0.055 | 0.000 | 0.241 | 0.010 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.551 | 0.477 | 0.465 | 0.514 | 0.473 | 0.493 | 0.489 | 0.712 | LastObs | 0.062 | 0.000 | 0.161 | 0.095 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.555 | 0.555 | 0.547 | 0.553 | 0.539 | 0.555 | 0.548 | 0.678 | Periodic | 0.002 | 0.000 | 0.123 | 0.020 | +0.000 (1/2) |
| hh_011 | remote_worker_couple | 2 | 0.593 | 0.592 | 0.574 | 0.593 | 0.561 | 0.567 | 0.562 | 0.660 | LastObs | 0.020 | 0.000 | 0.067 | 0.042 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.534 | 0.511 | 0.520 | 0.517 | 0.503 | 0.519 | 0.514 | 0.718 |  | 0.043 | 0.020 | 0.164 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.426 | 0.440 | 0.416 | 0.383 | 0.444 | 0.458 | 0.454 | 0.752 | PerpetuaStar | 0.018 | 0.031 | 0.295 | 0.108 | +0.031 (1/2) |
| hh_007 | college_roommates | 3 | 0.473 | 0.436 | 0.424 | 0.401 | 0.419 | 0.444 | 0.441 | 0.723 | LastObs | 0.037 | 0.000 | 0.250 | 0.072 | +0.000 (0/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.571 | 0.591 | 0.564 | 0.591 | 0.537 | 0.563 | 0.546 | 0.712 | Periodic | 0.026 | 0.019 | 0.121 | 0.036 | +0.019 (1/2) |
| hh_002 | multigenerational_family | 5 | 0.474 | 0.474 | 0.433 | 0.451 | 0.416 | 0.443 | 0.443 | 0.695 | LastObs | 0.031 | 0.000 | 0.221 | 0.066 | +0.000 (0/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.513 | 0.491 | 0.511 | 0.508 | 0.488 | 0.504 | 0.496 | 0.695 | LastObs | 0.009 | 0.000 | 0.182 | 0.080 | +0.000 (0/2) |
| hh_015 | single_parent_teens | 3 | 0.407 | 0.482 | 0.426 | 0.483 | 0.436 | 0.441 | 0.430 | 0.694 | SmoothedRec | 0.047 | 0.076 | 0.212 | 0.051 | +0.076 (2/2) |
| hh_009 | couple_with_toddler | 3 | 0.492 | 0.494 | 0.480 | 0.509 | 0.483 | 0.502 | 0.501 | 0.682 | SmoothedRec | 0.016 | 0.017 | 0.172 | 0.076 | +0.017 (1/2) |
| **3+-resident mean** |  | 7 | 0.480 | 0.487 | 0.465 | 0.475 | 0.460 | 0.479 | 0.473 | 0.708 |  | 0.026 | 0.020 | 0.208 |  |  |

![](separation_by_home.png)

## Same homes under the frozen forecast (D=7, h=1)

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_012 | researcher_household | 1 | 0.514 | 0.514 | 0.497 | 0.514 | 0.577 | 0.571 | 0.571 | 0.760 | Perpetua | 0.063 | 0.063 | 0.183 | 0.166 | +0.063 (2/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.475 | 0.475 | 0.469 | 0.486 | 0.373 | 0.339 | 0.339 | 0.746 | SmoothedRec | 0.017 | 0.011 | 0.260 | 0.086 | +0.011 (1/2) |
| hh_001 | working_professional_solo | 1 | 0.384 | 0.384 | 0.421 | 0.415 | 0.348 | 0.348 | 0.348 | 0.738 | DaytypeMix | 0.037 | 0.037 | 0.317 | 0.144 | +0.036 (1/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.385 | 0.408 | 0.466 | 0.385 | 0.270 | 0.328 | 0.322 | 0.718 | DaytypeMix | 0.080 | 0.080 | 0.253 | 0.149 | +0.080 (2/2) |
| hh_014 | single_adult_wfh | 1 | 0.449 | 0.449 | 0.442 | 0.449 | 0.474 | 0.500 | 0.481 | 0.692 | PerpetuaStar | 0.051 | 0.051 | 0.192 | 0.092 | +0.048 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.358 | 0.409 | 0.386 | 0.409 | 0.261 | 0.261 | 0.267 | 0.676 | Periodic | 0.051 | 0.051 | 0.267 | 0.097 | +0.051 (2/2) |
| hh_016 | single_senior_solo | 1 | 0.539 | 0.539 | 0.489 | 0.539 | 0.393 | 0.427 | 0.427 | 0.663 | LastObs | 0.051 | 0.000 | 0.124 | 0.090 | +0.000 (0/2) |
| **1-resident mean** |  | 7 | 0.443 | 0.454 | 0.453 | 0.457 | 0.385 | 0.396 | 0.394 | 0.713 |  | 0.050 | 0.042 | 0.228 |  |  |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.420 | 0.384 | 0.370 | 0.420 | 0.304 | 0.319 | 0.312 | 0.790 | LastObs | 0.051 | 0.000 | 0.370 | 0.269 | +0.000 (0/2) |
| hh_018 | working_couple_no_children | 2 | 0.415 | 0.415 | 0.478 | 0.478 | 0.352 | 0.365 | 0.352 | 0.774 | DaytypeMix | 0.063 | 0.063 | 0.296 | 0.119 | +0.063 (2/2) |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.511 | 0.504 | 0.504 | 0.511 | 0.460 | 0.496 | 0.482 | 0.748 | LastObs | 0.007 | 0.000 | 0.237 | 0.310 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.392 | 0.363 | 0.386 | 0.392 | 0.339 | 0.310 | 0.316 | 0.737 | LastObs | 0.029 | 0.000 | 0.345 | 0.053 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.506 | 0.506 | 0.494 | 0.494 | 0.459 | 0.482 | 0.482 | 0.682 | LastObs | 0.012 | 0.000 | 0.176 | 0.083 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.361 | 0.361 | 0.361 | 0.361 | 0.408 | 0.444 | 0.432 | 0.651 | PerpetuaStar | 0.083 | 0.083 | 0.207 | 0.180 | +0.083 (2/2) |
| **2-resident mean** |  | 6 | 0.434 | 0.422 | 0.432 | 0.443 | 0.387 | 0.403 | 0.396 | 0.730 |  | 0.041 | 0.024 | 0.272 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.331 | 0.361 | 0.367 | 0.331 | 0.349 | 0.343 | 0.337 | 0.777 | DaytypeMix | 0.024 | 0.036 | 0.410 | 0.120 | +0.036 (2/2) |
| hh_007 | college_roommates | 3 | 0.406 | 0.370 | 0.364 | 0.388 | 0.273 | 0.309 | 0.303 | 0.758 | LastObs | 0.042 | 0.000 | 0.352 | 0.146 | +0.000 (0/2) |
| hh_009 | couple_with_toddler | 3 | 0.439 | 0.433 | 0.398 | 0.439 | 0.374 | 0.368 | 0.374 | 0.743 | LastObs | 0.041 | 0.000 | 0.304 | 0.126 | +0.000 (0/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.427 | 0.452 | 0.414 | 0.427 | 0.344 | 0.376 | 0.350 | 0.726 | Periodic | 0.038 | 0.025 | 0.274 | 0.153 | +0.027 (1/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.457 | 0.451 | 0.468 | 0.445 | 0.462 | 0.509 | 0.497 | 0.676 | PerpetuaStar | 0.046 | 0.052 | 0.168 | 0.126 | +0.053 (2/2) |
| hh_015 | single_parent_teens | 3 | 0.352 | 0.369 | 0.386 | 0.375 | 0.381 | 0.369 | 0.369 | 0.676 | DaytypeMix | 0.017 | 0.034 | 0.290 | 0.102 | +0.034 (2/2) |
| hh_002 | multigenerational_family | 5 | 0.377 | 0.293 | 0.287 | 0.293 | 0.353 | 0.317 | 0.317 | 0.659 | LastObs | 0.060 | 0.000 | 0.281 | 0.148 | +0.000 (0/2) |
| **3+-resident mean** |  | 7 | 0.398 | 0.390 | 0.384 | 0.385 | 0.362 | 0.370 | 0.364 | 0.716 |  | 0.038 | 0.021 | 0.297 |  |  |

## Age of the last sighting

All homes pooled:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 557 | 0.991 | 0.991 | 0.991 | 0.991 | 0.946 | 0.975 | 0.968 | 0.680 |
| 15m-1h | 1692 | 0.953 | 0.953 | 0.939 | 0.953 | 0.914 | 0.937 | 0.936 | 0.673 |
| 1-3h | 4253 | 0.883 | 0.883 | 0.862 | 0.883 | 0.840 | 0.866 | 0.863 | 0.688 |
| 3-6h | 4514 | 0.753 | 0.752 | 0.723 | 0.753 | 0.715 | 0.732 | 0.727 | 0.699 |
| 6-12h | 8947 | 0.671 | 0.671 | 0.630 | 0.671 | 0.633 | 0.646 | 0.644 | 0.701 |
| 12-24h | 18360 | 0.597 | 0.597 | 0.569 | 0.597 | 0.486 | 0.505 | 0.498 | 0.713 |
| 1-2d | 29916 | 0.533 | 0.535 | 0.527 | 0.534 | 0.436 | 0.460 | 0.454 | 0.713 |
| 2-3d | 9241 | 0.270 | 0.262 | 0.273 | 0.254 | 0.353 | 0.358 | 0.355 | 0.705 |
| 3d+ | 12520 | 0.161 | 0.150 | 0.164 | 0.129 | 0.343 | 0.347 | 0.343 | 0.756 |

1-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 266 | 0.985 | 0.985 | 0.985 | 0.985 | 0.944 | 0.974 | 0.962 | 0.680 |
| 15m-1h | 741 | 0.964 | 0.964 | 0.947 | 0.964 | 0.938 | 0.947 | 0.945 | 0.682 |
| 1-3h | 1774 | 0.902 | 0.901 | 0.874 | 0.902 | 0.861 | 0.886 | 0.883 | 0.698 |
| 3-6h | 1792 | 0.804 | 0.802 | 0.766 | 0.804 | 0.756 | 0.777 | 0.770 | 0.699 |
| 6-12h | 3154 | 0.734 | 0.733 | 0.683 | 0.734 | 0.688 | 0.701 | 0.701 | 0.694 |
| 12-24h | 7434 | 0.612 | 0.611 | 0.580 | 0.612 | 0.485 | 0.502 | 0.494 | 0.715 |
| 1-2d | 10161 | 0.533 | 0.538 | 0.531 | 0.536 | 0.427 | 0.453 | 0.450 | 0.714 |
| 2-3d | 2643 | 0.132 | 0.170 | 0.168 | 0.138 | 0.323 | 0.319 | 0.318 | 0.740 |
| 3d+ | 3535 | 0.164 | 0.192 | 0.182 | 0.174 | 0.328 | 0.330 | 0.327 | 0.767 |

2-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 147 | 1.000 | 1.000 | 1.000 | 1.000 | 0.973 | 0.973 | 0.973 | 0.680 |
| 15m-1h | 498 | 0.944 | 0.944 | 0.934 | 0.944 | 0.900 | 0.928 | 0.932 | 0.687 |
| 1-3h | 1250 | 0.877 | 0.877 | 0.863 | 0.877 | 0.829 | 0.853 | 0.851 | 0.688 |
| 3-6h | 1389 | 0.704 | 0.703 | 0.689 | 0.704 | 0.665 | 0.690 | 0.686 | 0.697 |
| 6-12h | 3080 | 0.624 | 0.624 | 0.596 | 0.624 | 0.586 | 0.601 | 0.598 | 0.698 |
| 12-24h | 5580 | 0.616 | 0.615 | 0.605 | 0.616 | 0.527 | 0.546 | 0.540 | 0.726 |
| 1-2d | 10068 | 0.547 | 0.547 | 0.541 | 0.547 | 0.453 | 0.476 | 0.470 | 0.722 |
| 2-3d | 1827 | 0.202 | 0.093 | 0.153 | 0.117 | 0.347 | 0.327 | 0.323 | 0.681 |
| 3d+ | 3161 | 0.157 | 0.021 | 0.140 | 0.058 | 0.348 | 0.346 | 0.344 | 0.757 |

3+-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 144 | 0.993 | 0.993 | 0.993 | 0.993 | 0.924 | 0.979 | 0.972 | 0.681 |
| 15m-1h | 453 | 0.945 | 0.945 | 0.932 | 0.945 | 0.892 | 0.932 | 0.925 | 0.642 |
| 1-3h | 1229 | 0.862 | 0.862 | 0.843 | 0.862 | 0.821 | 0.850 | 0.845 | 0.675 |
| 3-6h | 1333 | 0.737 | 0.736 | 0.701 | 0.737 | 0.712 | 0.715 | 0.710 | 0.701 |
| 6-12h | 2713 | 0.651 | 0.652 | 0.609 | 0.651 | 0.621 | 0.635 | 0.631 | 0.710 |
| 12-24h | 5346 | 0.557 | 0.557 | 0.517 | 0.557 | 0.446 | 0.467 | 0.458 | 0.698 |
| 1-2d | 9687 | 0.520 | 0.520 | 0.509 | 0.520 | 0.426 | 0.450 | 0.443 | 0.703 |
| 2-3d | 4771 | 0.373 | 0.378 | 0.377 | 0.370 | 0.372 | 0.393 | 0.388 | 0.695 |
| 3d+ | 5824 | 0.160 | 0.195 | 0.166 | 0.139 | 0.349 | 0.357 | 0.352 | 0.747 |

![](age_by_group.png)

Kept current versus frozen forecast at matched ages, LastObs and the best routine model per group:

![](modes_by_group.png)

Every model here uses recent sightings, so at short ages they all sit on LastObs; the informative comparison is at a day or more, against the oracle:

| home | type | res | LastObs 12-24h | LastObs 1-2d | best model 1-2d | oracle 1-2d | LastObs 3d+ | best model 3d+ | oracle 3d+ | routine > LastObs by 0.02 from |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.561 | 0.576 | 0.576 (SmoothedRec, n=1424) | 0.716 | 0.359 | 0.359 (SmoothedRec, n=746) | 0.799 | never |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.538 | 0.446 | 0.483 (DaytypeMix, n=1353) | 0.695 | 0.061 | 0.343 (PerpetuaStar, n=721) | 0.775 | 1-2d |
| hh_012 | researcher_household | 1 | 0.536 | 0.491 | 0.493 (SmoothedRec, n=1407) | 0.733 | 0.198 | 0.265 (PerpStarFlat, n=742) | 0.730 | never |
| hh_014 | single_adult_wfh | 1 | 0.735 | 0.633 | 0.633 (LastObs, n=1539) | 0.710 | 0.071 | 0.408 (Perpetua, n=211) | 0.744 | 2-3d |
| hh_016 | single_senior_solo | 1 | 0.675 | 0.576 | 0.577 (Periodic, n=1616) | 0.703 | 0.000 | 0.517 (Perpetua, n=116) | 0.664 | never |
| hh_019 | working_professional_solo | 1 | 0.582 | 0.516 | 0.516 (LastObs, n=1365) | 0.719 | 0.170 | 0.308 (PerpetuaStar, n=623) | 0.806 | 3d+ |
| hh_020 | working_professional_solo__night_shift | 1 | 0.616 | 0.473 | 0.527 (DaytypeMix, n=1457) | 0.722 | 0.003 | 0.383 (Perpetua, n=376) | 0.745 | 1-2d |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.551 | 0.548 | 0.549 (SmoothedRec, n=1713) | 0.778 | 0.157 | 0.487 (Perpetua, n=503) | 0.809 | never |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.558 | 0.477 | 0.477 (LastObs, n=1643) | 0.719 | 0.256 | 0.310 (Perpetua, n=484) | 0.769 | never |
| hh_011 | remote_worker_couple | 2 | 0.723 | 0.603 | 0.603 (Periodic, n=1696) | 0.680 | 0.045 | 0.397 (Perpetua, n=312) | 0.638 | never |
| hh_013 | retired_couple | 2 | 0.636 | 0.537 | 0.538 (DaytypeMix, n=1852) | 0.679 | 0.026 | 0.503 (Perpetua, n=195) | 0.626 | never |
| hh_017 | working_couple_no_children | 2 | 0.593 | 0.569 | 0.569 (SmoothedRec, n=1503) | 0.741 | 0.290 | 0.302 (PerpetuaStar, n=945) | 0.738 | never |
| hh_018 | working_couple_no_children | 2 | 0.644 | 0.551 | 0.551 (LastObs, n=1661) | 0.741 | 0.001 | 0.422 (DaytypeMix, n=722) | 0.827 | 2-3d |
| hh_002 | multigenerational_family | 5 | 0.573 | 0.481 | 0.481 (SmoothedRec, n=1265) | 0.696 | 0.229 | 0.324 (Perpetua, n=1057) | 0.693 | never |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.641 | 0.629 | 0.629 (LastObs, n=1479) | 0.698 | 0.131 | 0.424 (PerpetuaStar, n=642) | 0.771 | 2-3d |
| hh_007 | college_roommates | 3 | 0.550 | 0.463 | 0.464 (SmoothedRec, n=1308) | 0.720 | 0.284 | 0.375 (PerpStarFlat, n=950) | 0.739 | never |
| hh_008 | college_roommates__irregular_gig | 3 | 0.594 | 0.562 | 0.562 (Periodic, n=1460) | 0.686 | 0.133 | 0.396 (Perpetua, n=618) | 0.759 | 2-3d |
| hh_009 | couple_with_toddler | 3 | 0.530 | 0.488 | 0.488 (Periodic, n=1633) | 0.690 | 0.101 | 0.369 (PerpStarFlat, n=426) | 0.718 | never |
| hh_010 | family_teen_and_child | 4 | 0.481 | 0.510 | 0.513 (Periodic, n=1233) | 0.764 | 0.172 | 0.343 (PerpetuaStar, n=1225) | 0.787 | 2-3d |
| hh_015 | single_parent_teens | 3 | 0.529 | 0.491 | 0.491 (SmoothedRec, n=1309) | 0.678 | 0.001 | 0.353 (Perpetua, n=906) | 0.756 | 2-3d |

![](age_by_home.png)

Age is not exogenous. An object the patrol has not seen for days is one it could not see — the share of questions whose true location is out of the house or on a person rises with age (seed-0 banks, all homes pooled):

| age of last sighting | n | ordinary receptacle | out of house | on a person |
|---|---|---|---|---|
| <15m | 525 | 100% | 0% | 0% |
| 15m-1h | 1734 | 98% | 1% | 0% |
| 1-3h | 3993 | 95% | 5% | 0% |
| 3-6h | 4827 | 93% | 7% | 0% |
| 6-12h | 8022 | 88% | 12% | 0% |
| 12-24h | 15691 | 85% | 14% | 1% |
| 1-2d | 6470 | 76% | 21% | 3% |
| 2-3d | 1971 | 67% | 29% | 4% |
| 3d+ | 1767 | 64% | 31% | 5% |

## History: accuracy by query day

`sep` is best model minus the median model over that day window; `95%-of-peak day` is when the best model's 3-day rolling accuracy first reaches 95% of its own peak.

| home | type | res | best model | best d3-5 | best d20+ | sep d3-5 | sep d20+ | LastObs d20+ | oracle d20+ | 95%-of-peak day |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | LastObs | 0.552 | 0.549 | 0.000 | 0.043 | 0.549 | 0.755 | 10 |
| hh_006 | working_professional_solo__irregular_gig | 1 | SmoothedRec | 0.402 | 0.494 | -0.017 | 0.021 | 0.470 | 0.726 | 12 |
| hh_012 | researcher_household | 1 | LastObs | 0.504 | 0.472 | 0.000 | 0.033 | 0.472 | 0.740 | 7 |
| hh_014 | single_adult_wfh | 1 | SmoothedRec | 0.650 | 0.664 | 0.013 | 0.022 | 0.649 | 0.718 | 3 |
| hh_016 | single_senior_solo | 1 | PerpetuaStar | 0.593 | 0.596 | -0.076 | 0.011 | 0.585 | 0.667 | 7 |
| hh_019 | working_professional_solo | 1 | Periodic | 0.544 | 0.547 | 0.000 | 0.038 | 0.542 | 0.751 | 6 |
| hh_020 | working_professional_solo__night_shift | 1 | Periodic | 0.533 | 0.559 | 0.054 | 0.049 | 0.502 | 0.758 | 9 |
| hh_004 | working_couple_no_children__night_shift | 2 | PerpetuaStar | 0.517 | 0.568 | 0.000 | 0.054 | 0.514 | 0.798 | 20 |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | LastObs | 0.478 | 0.493 | 0.050 | 0.053 | 0.493 | 0.735 | 7 |
| hh_011 | remote_worker_couple | 2 | LastObs | 0.615 | 0.584 | 0.004 | 0.024 | 0.584 | 0.655 | 3 |
| hh_013 | retired_couple | 2 | Periodic | 0.544 | 0.519 | 0.000 | 0.004 | 0.519 | 0.664 | 9 |
| hh_017 | working_couple_no_children | 2 | LastObs | 0.526 | 0.575 | 0.002 | 0.083 | 0.575 | 0.703 | 17 |
| hh_018 | working_couple_no_children | 2 | DaytypeMix | 0.594 | 0.594 | 0.050 | 0.088 | 0.506 | 0.753 | 11 |
| hh_002 | multigenerational_family | 5 | LastObs | 0.407 | 0.503 | 0.000 | 0.039 | 0.503 | 0.719 | 9 |
| hh_003 | single_parent_teens__rotating_shift | 3 | Periodic | 0.585 | 0.584 | 0.000 | 0.026 | 0.565 | 0.706 | 12 |
| hh_007 | college_roommates | 3 | LastObs | 0.474 | 0.477 | 0.030 | 0.053 | 0.477 | 0.724 | 12 |
| hh_008 | college_roommates__irregular_gig | 3 | LastObs | 0.504 | 0.534 | -0.002 | 0.015 | 0.534 | 0.722 | 10 |
| hh_009 | couple_with_toddler | 3 | PerpStarFlat | 0.533 | 0.512 | 0.011 | 0.018 | 0.494 | 0.698 | 3 |
| hh_010 | family_teen_and_child | 4 | PerpetuaStar | 0.556 | 0.463 | 0.074 | 0.022 | 0.438 | 0.740 | 6 |
| hh_015 | single_parent_teens | 3 | Periodic | 0.502 | 0.474 | 0.030 | 0.045 | 0.394 | 0.729 | 3 |

![](history_by_home.png)

## Perpetua and Perpetua*: survival models vs frequency

The three survival models against the two frequency comparators the question is about, one panel per home. Homes are never pooled: a fleet mean would hide which homes the survival machinery helps.

![](perpetua_by_home.png)

The same comparison as a per-home difference at the three long-age bins, where the models actually diverge:

![](perpetua_long_age_delta.png)

### Absence signal, fallback, training data

Absence signal (kept current, every home and seed): mean of the largest per-edge presence belief, split by where the object really was. A usable not-in-the-house threshold needs the out-of-house column well below the ordinary one. `n` counts questions; `fallback` is the share of predictions with at least one edge still on the fallback prior.

| model | age of last sighting | n | max belief, ordinary receptacle | max belief, out of house | max belief, on a person | fallback |
|---|---|---|---|---|---|---|
| Perpetua | <15m | 557 | 0.913 (556) | 0.008 (1) | - | 0.92 |
| Perpetua | 15m-1h | 1692 | 0.932 (1668) | 0.931 (24) | - | 0.94 |
| Perpetua | 1-3h | 4253 | 0.901 (4070) | 0.915 (177) | 0.966 (6) | 0.95 |
| Perpetua | 3-6h | 4514 | 0.829 (4140) | 0.803 (365) | 0.878 (9) | 0.95 |
| Perpetua | 6-12h | 8947 | 0.712 (8081) | 0.672 (841) | 0.613 (25) | 0.94 |
| Perpetua | 12-24h | 18360 | 0.645 (16050) | 0.592 (2252) | 0.527 (58) | 0.93 |
| Perpetua | 1-2d | 29916 | 0.627 (26143) | 0.518 (3475) | 0.527 (298) | 0.93 |
| Perpetua | 2-3d | 9241 | 0.584 (7247) | 0.511 (1767) | 0.517 (227) | 0.91 |
| Perpetua | 3d+ | 12520 | 0.615 (8601) | 0.553 (3522) | 0.540 (397) | 0.90 |
| PerpetuaStar | <15m | 557 | 0.941 (556) | 0.020 (1) | - | 0.92 |
| PerpetuaStar | 15m-1h | 1692 | 0.940 (1668) | 0.925 (24) | - | 0.94 |
| PerpetuaStar | 1-3h | 4253 | 0.915 (4070) | 0.909 (177) | 0.950 (6) | 0.95 |
| PerpetuaStar | 3-6h | 4514 | 0.855 (4140) | 0.830 (365) | 0.815 (9) | 0.95 |
| PerpetuaStar | 6-12h | 8947 | 0.746 (8081) | 0.703 (841) | 0.619 (25) | 0.94 |
| PerpetuaStar | 12-24h | 18360 | 0.694 (16050) | 0.608 (2252) | 0.556 (58) | 0.93 |
| PerpetuaStar | 1-2d | 29916 | 0.679 (26143) | 0.532 (3475) | 0.489 (298) | 0.93 |
| PerpetuaStar | 2-3d | 9241 | 0.566 (7247) | 0.467 (1767) | 0.446 (227) | 0.91 |
| PerpetuaStar | 3d+ | 12520 | 0.530 (8601) | 0.461 (3522) | 0.443 (397) | 0.90 |
| PerpStarFlat | <15m | 557 | 0.936 (556) | 0.010 (1) | - | 0.92 |
| PerpStarFlat | 15m-1h | 1692 | 0.934 (1668) | 0.897 (24) | - | 0.94 |
| PerpStarFlat | 1-3h | 4253 | 0.909 (4070) | 0.878 (177) | 0.955 (6) | 0.95 |
| PerpStarFlat | 3-6h | 4514 | 0.849 (4140) | 0.797 (365) | 0.811 (9) | 0.95 |
| PerpStarFlat | 6-12h | 8947 | 0.734 (8081) | 0.691 (841) | 0.569 (25) | 0.94 |
| PerpStarFlat | 12-24h | 18360 | 0.681 (16050) | 0.594 (2252) | 0.550 (58) | 0.93 |
| PerpStarFlat | 1-2d | 29916 | 0.668 (26143) | 0.521 (3475) | 0.498 (298) | 0.93 |
| PerpStarFlat | 2-3d | 9241 | 0.561 (7247) | 0.462 (1767) | 0.443 (227) | 0.91 |
| PerpStarFlat | 3d+ | 12520 | 0.524 (8601) | 0.454 (3522) | 0.433 (397) | 0.90 |

Fallback use by query day: share of edge beliefs computed from the fallback single-component prior rather than a fitted mixture.

| model | day 3 | day 6 | day 9 | day 12 | day 15 | day 18 | day 21 | day 24 | day 27 |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua | 1.00 | 0.99 | 0.95 | 0.86 | 0.78 | 0.71 | 0.66 | 0.63 | 0.61 |
| PerpetuaStar | 1.00 | 0.99 | 0.95 | 0.86 | 0.78 | 0.71 | 0.66 | 0.63 | 0.61 |
| PerpStarFlat | 1.00 | 0.99 | 0.95 | 0.86 | 0.78 | 0.71 | 0.66 | 0.63 | 0.61 |

Training data per edge at the end of the kept-current run: completed segments are what the EM fits on; an edge needs 2 of a kind to leave the fallback prior for that filter.

| model | edges | median persistence segs | median emergence segs | share < 2 persistence | share < 2 emergence | median resets | mean K persistence |
|---|---|---|---|---|---|---|---|
| Perpetua | 4759 | 2 | 1 | 0.48 | 0.61 | 3 | 1.04 |
| PerpetuaStar | 4759 | 2 | 1 | 0.48 | 0.61 | 3 | 1.04 |
| PerpStarFlat | 4759 | 2 | 1 | 0.48 | 0.61 | 3 | 1.04 |


Figures are static; every plotted value appears in the tables above, which are the table view.
