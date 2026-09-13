# Per-household passive analysis

20 households x 2 seeds (0, 1), 7 belief models + the routine oracle. Seeds of one home are pooled (equal question counts, so this is the seed mean); the last column of the overview is the largest across-seed range any model showed on that home, the noise floor for reading its row. Commit `f78a418bc019`, run 2026-09-05T02:03:43.

Two evaluation modes over the same questions:

- **kept current** (continuous): the belief is updated with every sighting strictly before each query and answers about now. Query day is the history length; the age of the object's last sighting is recorded per question.
- **frozen forecast**: the bake-off protocol. The belief is frozen at day D and answers questions up to 7 days later, bucketed by horizon; the headline cell is D=7, h=1 (questions 6-24h after the freeze).

The routine oracle predicts from the household's authored rules re-realized under many seeds, with no observations: routine knowledge alone. Not a hard ceiling; a fresh sighting beats it.

## Which homes separate the models (belief kept current)

Sorted by the oracle within resident group, so the most routine-predictable home of each group comes first.

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.728 | 0.684 | 0.641 | 0.728 | 0.610 | 0.624 | 0.621 | 0.737 | LastObs | 0.087 | 0.000 | 0.009 | 0.060 | +0.000 (0/2) |
| hh_012 | researcher_household | 1 | 0.703 | 0.702 | 0.588 | 0.694 | 0.592 | 0.595 | 0.595 | 0.730 | LastObs | 0.108 | 0.000 | 0.027 | 0.121 | +0.000 (0/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.679 | 0.754 | 0.696 | 0.716 | 0.657 | 0.658 | 0.659 | 0.729 | Periodic | 0.075 | 0.075 | -0.025 | 0.100 | +0.075 (2/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.619 | 0.659 | 0.634 | 0.661 | 0.594 | 0.603 | 0.598 | 0.719 | SmoothedRec | 0.042 | 0.042 | 0.058 | 0.085 | +0.042 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.705 | 0.702 | 0.649 | 0.657 | 0.618 | 0.632 | 0.629 | 0.713 | LastObs | 0.057 | 0.000 | 0.007 | 0.098 | +0.000 (0/2) |
| hh_014 | single_adult_wfh | 1 | 0.824 | 0.823 | 0.760 | 0.824 | 0.762 | 0.772 | 0.771 | 0.710 | LastObs | 0.053 | 0.000 | -0.114 | 0.012 | +0.000 (0/2) |
| hh_016 | single_senior_solo | 1 | 0.832 | 0.832 | 0.757 | 0.832 | 0.771 | 0.781 | 0.780 | 0.684 | SmoothedRec | 0.051 | 0.000 | -0.148 | 0.023 | +0.000 (1/2) |
| **1-resident mean** |  | 7 | 0.727 | 0.736 | 0.675 | 0.730 | 0.658 | 0.666 | 0.665 | 0.717 |  | 0.068 | 0.017 | -0.027 |  |  |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.638 | 0.600 | 0.606 | 0.600 | 0.605 | 0.618 | 0.600 | 0.776 | LastObs | 0.034 | 0.000 | 0.137 | 0.093 | +0.000 (0/2) |
| hh_018 | working_couple_no_children | 2 | 0.647 | 0.644 | 0.700 | 0.647 | 0.618 | 0.633 | 0.622 | 0.753 | DaytypeMix | 0.056 | 0.053 | 0.052 | 0.018 | +0.053 (2/2) |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.688 | 0.598 | 0.547 | 0.599 | 0.568 | 0.572 | 0.552 | 0.728 | LastObs | 0.116 | 0.000 | 0.041 | 0.028 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.705 | 0.643 | 0.589 | 0.674 | 0.610 | 0.604 | 0.598 | 0.712 | LastObs | 0.095 | 0.000 | 0.007 | 0.055 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.732 | 0.731 | 0.659 | 0.728 | 0.697 | 0.707 | 0.704 | 0.678 | LastObs | 0.025 | 0.000 | -0.054 | 0.025 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.782 | 0.780 | 0.684 | 0.780 | 0.718 | 0.731 | 0.728 | 0.660 | LastObs | 0.051 | 0.000 | -0.122 | 0.041 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.699 | 0.666 | 0.631 | 0.671 | 0.636 | 0.644 | 0.634 | 0.718 |  | 0.063 | 0.009 | 0.010 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.569 | 0.568 | 0.520 | 0.534 | 0.544 | 0.536 | 0.521 | 0.752 | LastObs | 0.032 | 0.000 | 0.184 | 0.084 | +0.000 (0/2) |
| hh_007 | college_roommates | 3 | 0.633 | 0.593 | 0.551 | 0.559 | 0.574 | 0.571 | 0.560 | 0.723 | LastObs | 0.062 | 0.000 | 0.090 | 0.079 | +0.000 (0/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.725 | 0.737 | 0.686 | 0.739 | 0.701 | 0.702 | 0.691 | 0.712 | SmoothedRec | 0.037 | 0.014 | -0.027 | 0.055 | +0.014 (1/2) |
| hh_002 | multigenerational_family | 5 | 0.637 | 0.637 | 0.556 | 0.615 | 0.550 | 0.555 | 0.547 | 0.695 | LastObs | 0.081 | 0.000 | 0.058 | 0.063 | +0.000 (0/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.653 | 0.630 | 0.623 | 0.654 | 0.619 | 0.635 | 0.630 | 0.695 | SmoothedRec | 0.024 | 0.001 | 0.041 | 0.048 | +0.001 (1/2) |
| hh_015 | single_parent_teens | 3 | 0.583 | 0.641 | 0.546 | 0.641 | 0.579 | 0.575 | 0.570 | 0.694 | SmoothedRec | 0.062 | 0.058 | 0.054 | 0.036 | +0.058 (2/2) |
| hh_009 | couple_with_toddler | 3 | 0.637 | 0.635 | 0.574 | 0.662 | 0.587 | 0.594 | 0.586 | 0.682 | SmoothedRec | 0.068 | 0.025 | 0.020 | 0.053 | +0.025 (1/2) |
| **3+-resident mean** |  | 7 | 0.634 | 0.634 | 0.579 | 0.629 | 0.593 | 0.595 | 0.586 | 0.708 |  | 0.052 | 0.014 | 0.060 |  |  |

![](separation_by_home.png)

## Same homes under the frozen forecast (D=7, h=1)

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_012 | researcher_household | 1 | 0.594 | 0.594 | 0.629 | 0.629 | 0.474 | 0.486 | 0.463 | 0.760 | DaytypeMix | 0.034 | 0.034 | 0.131 | 0.153 | +0.035 (1/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.757 | 0.757 | 0.701 | 0.774 | 0.328 | 0.294 | 0.266 | 0.746 | SmoothedRec | 0.073 | 0.017 | -0.028 | 0.125 | +0.017 (1/2) |
| hh_001 | working_professional_solo | 1 | 0.451 | 0.451 | 0.457 | 0.451 | 0.293 | 0.317 | 0.311 | 0.738 | DaytypeMix | 0.006 | 0.006 | 0.280 | 0.130 | +0.006 (1/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.448 | 0.460 | 0.408 | 0.454 | 0.425 | 0.379 | 0.391 | 0.718 | Periodic | 0.034 | 0.011 | 0.259 | 0.161 | +0.011 (1/2) |
| hh_014 | single_adult_wfh | 1 | 0.628 | 0.641 | 0.571 | 0.622 | 0.519 | 0.545 | 0.545 | 0.692 | Periodic | 0.071 | 0.013 | 0.051 | 0.079 | +0.013 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.483 | 0.511 | 0.489 | 0.517 | 0.261 | 0.267 | 0.267 | 0.676 | SmoothedRec | 0.034 | 0.034 | 0.159 | 0.074 | +0.034 (2/2) |
| hh_016 | single_senior_solo | 1 | 0.702 | 0.708 | 0.657 | 0.702 | 0.410 | 0.444 | 0.433 | 0.663 | Periodic | 0.051 | 0.006 | -0.045 | 0.034 | +0.006 (1/2) |
| **1-resident mean** |  | 7 | 0.581 | 0.589 | 0.559 | 0.593 | 0.387 | 0.390 | 0.382 | 0.713 |  | 0.043 | 0.017 | 0.115 |  |  |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.507 | 0.464 | 0.486 | 0.514 | 0.319 | 0.377 | 0.341 | 0.790 | SmoothedRec | 0.051 | 0.007 | 0.275 | 0.085 | +0.007 (1/2) |
| hh_018 | working_couple_no_children | 2 | 0.484 | 0.472 | 0.434 | 0.484 | 0.340 | 0.346 | 0.333 | 0.774 | LastObs | 0.050 | 0.000 | 0.289 | 0.180 | +0.000 (0/2) |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.583 | 0.583 | 0.561 | 0.583 | 0.453 | 0.496 | 0.460 | 0.748 | LastObs | 0.022 | 0.000 | 0.165 | 0.100 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.474 | 0.474 | 0.450 | 0.480 | 0.439 | 0.374 | 0.345 | 0.737 | SmoothedRec | 0.029 | 0.006 | 0.257 | 0.105 | +0.006 (1/2) |
| hh_013 | retired_couple | 2 | 0.676 | 0.676 | 0.629 | 0.682 | 0.424 | 0.476 | 0.447 | 0.682 | SmoothedRec | 0.053 | 0.006 | 0.000 | 0.060 | +0.006 (1/2) |
| hh_011 | remote_worker_couple | 2 | 0.704 | 0.692 | 0.615 | 0.692 | 0.473 | 0.485 | 0.467 | 0.651 | LastObs | 0.089 | 0.000 | -0.053 | 0.060 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.571 | 0.560 | 0.529 | 0.573 | 0.408 | 0.426 | 0.399 | 0.730 |  | 0.049 | 0.003 | 0.156 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.410 | 0.422 | 0.398 | 0.422 | 0.331 | 0.367 | 0.313 | 0.777 | Periodic | 0.024 | 0.012 | 0.355 | 0.133 | +0.012 (2/2) |
| hh_007 | college_roommates | 3 | 0.491 | 0.394 | 0.412 | 0.430 | 0.224 | 0.236 | 0.230 | 0.758 | LastObs | 0.097 | 0.000 | 0.267 | 0.292 | +0.000 (0/2) |
| hh_009 | couple_with_toddler | 3 | 0.462 | 0.491 | 0.468 | 0.474 | 0.339 | 0.409 | 0.368 | 0.743 | Periodic | 0.029 | 0.029 | 0.251 | 0.089 | +0.030 (2/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.465 | 0.490 | 0.427 | 0.478 | 0.331 | 0.318 | 0.293 | 0.726 | Periodic | 0.064 | 0.025 | 0.236 | 0.133 | +0.027 (1/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.607 | 0.595 | 0.578 | 0.590 | 0.462 | 0.468 | 0.457 | 0.676 | LastObs | 0.029 | 0.000 | 0.069 | 0.125 | +0.000 (0/2) |
| hh_015 | single_parent_teens | 3 | 0.403 | 0.443 | 0.438 | 0.438 | 0.312 | 0.375 | 0.324 | 0.676 | Periodic | 0.040 | 0.040 | 0.233 | 0.136 | +0.040 (2/2) |
| hh_002 | multigenerational_family | 5 | 0.425 | 0.401 | 0.389 | 0.407 | 0.305 | 0.329 | 0.305 | 0.659 | LastObs | 0.036 | 0.000 | 0.234 | 0.034 | +0.000 (0/2) |
| **3+-resident mean** |  | 7 | 0.466 | 0.462 | 0.444 | 0.463 | 0.329 | 0.358 | 0.327 | 0.716 |  | 0.046 | 0.015 | 0.235 |  |  |

## Age of the last sighting

All homes pooled:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 2272 | 0.984 | 0.982 | 0.966 | 0.984 | 0.913 | 0.939 | 0.934 | 0.665 |
| 15m-1h | 6421 | 0.945 | 0.941 | 0.888 | 0.945 | 0.873 | 0.895 | 0.891 | 0.674 |
| 1-3h | 15299 | 0.870 | 0.867 | 0.762 | 0.870 | 0.796 | 0.814 | 0.809 | 0.691 |
| 3-6h | 18415 | 0.794 | 0.794 | 0.717 | 0.794 | 0.722 | 0.730 | 0.723 | 0.710 |
| 6-12h | 23390 | 0.686 | 0.695 | 0.640 | 0.688 | 0.614 | 0.618 | 0.613 | 0.715 |
| 12-24h | 19853 | 0.428 | 0.397 | 0.400 | 0.395 | 0.386 | 0.382 | 0.372 | 0.744 |
| 1-2d | 3751 | 0.212 | 0.185 | 0.179 | 0.163 | 0.343 | 0.323 | 0.306 | 0.756 |
| 2-3d | 405 | 0.301 | 0.326 | 0.331 | 0.259 | 0.215 | 0.215 | 0.202 | 0.733 |
| 3d+ | 194 | 0.247 | 0.314 | 0.320 | 0.340 | 0.170 | 0.165 | 0.170 | 0.784 |

1-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 1069 | 0.984 | 0.982 | 0.965 | 0.984 | 0.923 | 0.949 | 0.950 | 0.661 |
| 15m-1h | 2801 | 0.948 | 0.943 | 0.888 | 0.948 | 0.876 | 0.893 | 0.890 | 0.671 |
| 1-3h | 6512 | 0.877 | 0.875 | 0.767 | 0.877 | 0.806 | 0.818 | 0.820 | 0.703 |
| 3-6h | 7513 | 0.812 | 0.814 | 0.745 | 0.813 | 0.744 | 0.751 | 0.747 | 0.710 |
| 6-12h | 6954 | 0.675 | 0.715 | 0.657 | 0.689 | 0.605 | 0.613 | 0.614 | 0.725 |
| 12-24h | 5402 | 0.439 | 0.440 | 0.418 | 0.434 | 0.355 | 0.355 | 0.353 | 0.767 |
| 1-2d | 1022 | 0.247 | 0.250 | 0.210 | 0.251 | 0.285 | 0.283 | 0.275 | 0.732 |
| 2-3d | 118 | 0.381 | 0.508 | 0.500 | 0.390 | 0.059 | 0.068 | 0.059 | 0.737 |
| 3d+ | 109 | 0.257 | 0.284 | 0.367 | 0.367 | 0.156 | 0.147 | 0.156 | 0.798 |

2-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 608 | 0.988 | 0.984 | 0.972 | 0.988 | 0.921 | 0.949 | 0.934 | 0.678 |
| 15m-1h | 1841 | 0.951 | 0.946 | 0.902 | 0.951 | 0.875 | 0.902 | 0.895 | 0.681 |
| 1-3h | 4312 | 0.879 | 0.875 | 0.773 | 0.879 | 0.798 | 0.824 | 0.812 | 0.687 |
| 3-6h | 5499 | 0.815 | 0.813 | 0.726 | 0.815 | 0.728 | 0.736 | 0.726 | 0.716 |
| 6-12h | 7856 | 0.700 | 0.696 | 0.651 | 0.696 | 0.620 | 0.625 | 0.620 | 0.726 |
| 12-24h | 6209 | 0.413 | 0.301 | 0.355 | 0.316 | 0.405 | 0.398 | 0.385 | 0.742 |
| 1-2d | 608 | 0.250 | 0.089 | 0.186 | 0.097 | 0.266 | 0.265 | 0.220 | 0.738 |
| 2-3d | 57 | 0.368 | 0.193 | 0.368 | 0.316 | 0.175 | 0.158 | 0.123 | 0.772 |
| 3d+ | 10 | 0.200 | 0.300 | 0.200 | 0.300 | 0.200 | 0.100 | 0.100 | 0.800 |

3+-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 595 | 0.980 | 0.980 | 0.961 | 0.980 | 0.887 | 0.911 | 0.906 | 0.659 |
| 15m-1h | 1779 | 0.935 | 0.932 | 0.872 | 0.935 | 0.867 | 0.891 | 0.886 | 0.672 |
| 1-3h | 4475 | 0.849 | 0.847 | 0.743 | 0.849 | 0.781 | 0.796 | 0.789 | 0.677 |
| 3-6h | 5403 | 0.747 | 0.746 | 0.669 | 0.747 | 0.685 | 0.694 | 0.688 | 0.705 |
| 6-12h | 8580 | 0.682 | 0.678 | 0.616 | 0.679 | 0.616 | 0.616 | 0.606 | 0.697 |
| 12-24h | 8242 | 0.433 | 0.441 | 0.423 | 0.430 | 0.391 | 0.386 | 0.375 | 0.731 |
| 1-2d | 2121 | 0.184 | 0.181 | 0.162 | 0.140 | 0.393 | 0.359 | 0.345 | 0.772 |
| 2-3d | 230 | 0.243 | 0.265 | 0.235 | 0.178 | 0.304 | 0.304 | 0.296 | 0.722 |
| 3d+ | 75 | 0.240 | 0.360 | 0.267 | 0.307 | 0.187 | 0.200 | 0.200 | 0.760 |

![](age_by_group.png)

Kept current versus frozen forecast at matched ages, LastObs and the best routine model per group:

![](modes_by_group.png)

Every model here uses recent sightings, so at short ages they all sit on LastObs; the informative comparison is at a day or more, against the oracle:

| home | type | res | LastObs 12-24h | LastObs 1-2d | best model 1-2d | oracle 1-2d | LastObs 3d+ | best model 3d+ | oracle 3d+ | routine > LastObs by 0.02 from |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.568 | 0.372 | 0.372 (SmoothedRec, n=226) | 0.743 | 0.295 | 0.364 (Periodic, n=44) | 0.705 | 2-3d |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.197 | 0.232 | 0.320 (Perpetua, n=194) | 0.763 | n=4<30 | n=4<30 | n=4<30 | 6-12h |
| hh_012 | researcher_household | 1 | 0.413 | 0.240 | 0.240 (Periodic, n=263) | 0.658 | 0.298 | 0.340 (SmoothedRec, n=47) | 0.830 | never |
| hh_014 | single_adult_wfh | 1 | 0.676 | 0.250 | 0.500 (SmoothedRec, n=120) | 0.825 | n=14<30 | n=14<30 | n=14<30 | 1-2d |
| hh_016 | single_senior_solo | 1 | 0.375 | n=11<30 | n=11<30 | n=11<30 | - | - | - | 12-24h |
| hh_019 | working_professional_solo | 1 | 0.459 | 0.140 | 0.340 (PerpetuaStar, n=150) | 0.760 | - | - | - | 6-12h |
| hh_020 | working_professional_solo__night_shift | 1 | 0.420 | 0.086 | 0.431 (Perpetua, n=58) | 0.655 | - | - | - | 3-6h |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.277 | 0.096 | 0.346 (PerpetuaStar, n=52) | 0.654 | - | - | - | never |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.508 | 0.385 | 0.385 (LastObs, n=192) | 0.776 | n=2<30 | n=2<30 | n=2<30 | 3d+ |
| hh_011 | remote_worker_couple | 2 | 0.617 | 0.320 | 0.347 (Periodic, n=75) | 0.800 | n=6<30 | n=6<30 | n=6<30 | 1-2d |
| hh_013 | retired_couple | 2 | 0.388 | n=9<30 | n=9<30 | n=9<30 | - | - | - | never |
| hh_017 | working_couple_no_children | 2 | 0.449 | 0.340 | 0.340 (LastObs, n=144) | 0.667 | n=2<30 | n=2<30 | n=2<30 | never |
| hh_018 | working_couple_no_children | 2 | 0.256 | 0.000 | 0.412 (DaytypeMix, n=136) | 0.772 | - | - | - | 12-24h |
| hh_002 | multigenerational_family | 5 | 0.526 | 0.302 | 0.302 (Periodic, n=477) | 0.753 | 0.277 | 0.298 (SmoothedRec, n=47) | 0.723 | never |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.501 | 0.148 | 0.522 (Perpetua, n=203) | 0.773 | n=3<30 | n=3<30 | n=3<30 | 12-24h |
| hh_007 | college_roommates | 3 | 0.508 | 0.279 | 0.444 (Perpetua, n=365) | 0.816 | n=1<30 | n=1<30 | n=1<30 | never |
| hh_008 | college_roommates__irregular_gig | 3 | 0.458 | 0.108 | 0.510 (PerpStarFlat, n=251) | 0.805 | - | - | - | 12-24h |
| hh_009 | couple_with_toddler | 3 | 0.335 | 0.175 | 0.385 (Perpetua, n=143) | 0.713 | - | - | - | never |
| hh_010 | family_teen_and_child | 4 | 0.358 | 0.156 | 0.396 (Perpetua, n=391) | 0.777 | n=20<30 | n=20<30 | n=20<30 | 1-2d |
| hh_015 | single_parent_teens | 3 | 0.352 | 0.003 | 0.392 (Perpetua, n=291) | 0.739 | n=4<30 | n=4<30 | n=4<30 | 12-24h |

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
| hh_001 | working_professional_solo | 1 | LastObs | 0.772 | 0.698 | 0.050 | 0.094 | 0.698 | 0.755 | 3 |
| hh_006 | working_professional_solo__irregular_gig | 1 | SmoothedRec | 0.635 | 0.651 | 0.022 | 0.070 | 0.619 | 0.726 | 12 |
| hh_012 | researcher_household | 1 | LastObs | 0.706 | 0.708 | 0.061 | 0.113 | 0.708 | 0.740 | 3 |
| hh_014 | single_adult_wfh | 1 | SmoothedRec | 0.793 | 0.803 | 0.013 | 0.060 | 0.797 | 0.718 | 3 |
| hh_016 | single_senior_solo | 1 | SmoothedRec | 0.830 | 0.840 | 0.039 | 0.069 | 0.838 | 0.667 | 3 |
| hh_019 | working_professional_solo | 1 | Periodic | 0.798 | 0.699 | 0.011 | 0.058 | 0.698 | 0.751 | 3 |
| hh_020 | working_professional_solo__night_shift | 1 | Periodic | 0.659 | 0.765 | 0.030 | 0.079 | 0.686 | 0.758 | 9 |
| hh_004 | working_couple_no_children__night_shift | 2 | LastObs | 0.585 | 0.659 | 0.000 | 0.036 | 0.659 | 0.798 | 8 |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | LastObs | 0.643 | 0.670 | 0.069 | 0.110 | 0.670 | 0.735 | 8 |
| hh_011 | remote_worker_couple | 2 | LastObs | 0.826 | 0.780 | 0.019 | 0.056 | 0.780 | 0.655 | 3 |
| hh_013 | retired_couple | 2 | Periodic | 0.733 | 0.699 | -0.007 | 0.017 | 0.699 | 0.664 | 4 |
| hh_017 | working_couple_no_children | 2 | LastObs | 0.693 | 0.709 | 0.070 | 0.091 | 0.709 | 0.703 | 13 |
| hh_018 | working_couple_no_children | 2 | DaytypeMix | 0.707 | 0.685 | 0.035 | 0.028 | 0.657 | 0.753 | 6 |
| hh_002 | multigenerational_family | 5 | LastObs | 0.641 | 0.654 | 0.013 | 0.098 | 0.654 | 0.719 | 6 |
| hh_003 | single_parent_teens__rotating_shift | 3 | Periodic | 0.769 | 0.743 | 0.013 | 0.026 | 0.733 | 0.706 | 6 |
| hh_007 | college_roommates | 3 | LastObs | 0.628 | 0.645 | 0.080 | 0.070 | 0.645 | 0.724 | 11 |
| hh_008 | college_roommates__irregular_gig | 3 | SmoothedRec | 0.641 | 0.654 | -0.004 | 0.023 | 0.650 | 0.722 | 9 |
| hh_009 | couple_with_toddler | 3 | SmoothedRec | 0.622 | 0.683 | 0.024 | 0.076 | 0.655 | 0.698 | 6 |
| hh_010 | family_teen_and_child | 4 | LastObs | 0.537 | 0.591 | -0.002 | 0.040 | 0.591 | 0.740 | 6 |
| hh_015 | single_parent_teens | 3 | Periodic | 0.613 | 0.643 | 0.006 | 0.074 | 0.592 | 0.729 | 11 |

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
| Perpetua | <15m | 2272 | 0.909 (2261) | 0.977 (11) | - | 0.91 |
| Perpetua | 15m-1h | 6421 | 0.894 (6317) | 0.894 (98) | 0.682 (6) | 0.89 |
| Perpetua | 1-3h | 15299 | 0.849 (14569) | 0.818 (713) | 0.915 (17) | 0.90 |
| Perpetua | 3-6h | 18415 | 0.786 (17052) | 0.690 (1332) | 0.784 (31) | 0.90 |
| Perpetua | 6-12h | 23390 | 0.697 (20082) | 0.511 (3218) | 0.515 (90) | 0.88 |
| Perpetua | 12-24h | 19853 | 0.547 (13635) | 0.376 (5911) | 0.314 (307) | 0.86 |
| Perpetua | 1-2d | 3751 | 0.446 (2412) | 0.349 (966) | 0.278 (373) | 0.85 |
| Perpetua | 2-3d | 405 | 0.365 (163) | 0.300 (114) | 0.280 (128) | 0.82 |
| Perpetua | 3d+ | 194 | 0.242 (65) | 0.237 (61) | 0.307 (68) | 0.82 |
| PerpetuaStar | <15m | 2272 | 0.916 (2261) | 0.828 (11) | - | 0.91 |
| PerpetuaStar | 15m-1h | 6421 | 0.905 (6317) | 0.896 (98) | 0.820 (6) | 0.89 |
| PerpetuaStar | 1-3h | 15299 | 0.859 (14569) | 0.820 (713) | 0.886 (17) | 0.90 |
| PerpetuaStar | 3-6h | 18415 | 0.791 (17052) | 0.698 (1332) | 0.751 (31) | 0.90 |
| PerpetuaStar | 6-12h | 23390 | 0.710 (20082) | 0.513 (3218) | 0.476 (90) | 0.88 |
| PerpetuaStar | 12-24h | 19853 | 0.557 (13635) | 0.351 (5911) | 0.302 (307) | 0.86 |
| PerpetuaStar | 1-2d | 3751 | 0.425 (2412) | 0.330 (966) | 0.266 (373) | 0.85 |
| PerpetuaStar | 2-3d | 405 | 0.352 (163) | 0.243 (114) | 0.235 (128) | 0.82 |
| PerpetuaStar | 3d+ | 194 | 0.209 (65) | 0.193 (61) | 0.197 (68) | 0.82 |
| PerpStarFlat | <15m | 2272 | 0.910 (2261) | 0.857 (11) | - | 0.91 |
| PerpStarFlat | 15m-1h | 6421 | 0.897 (6317) | 0.888 (98) | 0.818 (6) | 0.89 |
| PerpStarFlat | 1-3h | 15299 | 0.850 (14569) | 0.803 (713) | 0.879 (17) | 0.90 |
| PerpStarFlat | 3-6h | 18415 | 0.779 (17052) | 0.675 (1332) | 0.744 (31) | 0.90 |
| PerpStarFlat | 6-12h | 23390 | 0.698 (20082) | 0.494 (3218) | 0.441 (90) | 0.88 |
| PerpStarFlat | 12-24h | 19853 | 0.543 (13635) | 0.333 (5911) | 0.293 (307) | 0.86 |
| PerpStarFlat | 1-2d | 3751 | 0.404 (2412) | 0.320 (966) | 0.261 (373) | 0.85 |
| PerpStarFlat | 2-3d | 405 | 0.316 (163) | 0.238 (114) | 0.229 (128) | 0.82 |
| PerpStarFlat | 3d+ | 194 | 0.195 (65) | 0.192 (61) | 0.193 (68) | 0.82 |

Fallback use by query day: share of edge beliefs computed from the fallback single-component prior rather than a fitted mixture.

| model | day 3 | day 6 | day 9 | day 12 | day 15 | day 18 | day 21 | day 24 | day 27 |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua | 0.87 | 0.72 | 0.64 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.53 |
| PerpetuaStar | 0.87 | 0.72 | 0.64 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.53 |
| PerpStarFlat | 0.87 | 0.72 | 0.64 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.53 |

Training data per edge at the end of the kept-current run: completed segments are what the EM fits on; an edge needs 2 of a kind to leave the fallback prior for that filter.

| model | edges | median persistence segs | median emergence segs | share < 2 persistence | share < 2 emergence | median resets | mean K persistence |
|---|---|---|---|---|---|---|---|
| Perpetua | 6676 | 2 | 1 | 0.41 | 0.53 | 3 | 1.17 |
| PerpetuaStar | 6676 | 2 | 1 | 0.41 | 0.53 | 3 | 1.17 |
| PerpStarFlat | 6676 | 2 | 1 | 0.41 | 0.53 | 3 | 1.17 |


Figures are static; every plotted value appears in the tables above, which are the table view.
