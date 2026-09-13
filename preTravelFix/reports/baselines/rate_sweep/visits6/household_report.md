# Per-household passive analysis

20 households x 2 seeds (0, 1), 7 belief models + the routine oracle. Seeds of one home are pooled (equal question counts, so this is the seed mean); the last column of the overview is the largest across-seed range any model showed on that home, the noise floor for reading its row. Commit `f78a418bc019`, run 2026-09-05T01:43:22.

Two evaluation modes over the same questions:

- **kept current** (continuous): the belief is updated with every sighting strictly before each query and answers about now. Query day is the history length; the age of the object's last sighting is recorded per question.
- **frozen forecast**: the bake-off protocol. The belief is frozen at day D and answers questions up to 7 days later, bucketed by horizon; the headline cell is D=7, h=1 (questions 6-24h after the freeze).

The routine oracle predicts from the household's authored rules re-realized under many seeds, with no observations: routine knowledge alone. Not a hard ceiling; a fresh sighting beats it.

## Which homes separate the models (belief kept current)

Sorted by the oracle within resident group, so the most routine-predictable home of each group comes first.

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.618 | 0.590 | 0.565 | 0.618 | 0.548 | 0.558 | 0.553 | 0.737 | LastObs | 0.053 | 0.000 | 0.119 | 0.059 | +0.000 (0/2) |
| hh_012 | researcher_household | 1 | 0.599 | 0.600 | 0.521 | 0.593 | 0.520 | 0.528 | 0.522 | 0.730 | Periodic | 0.072 | 0.000 | 0.130 | 0.100 | +0.000 (2/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.583 | 0.631 | 0.596 | 0.609 | 0.565 | 0.568 | 0.566 | 0.729 | Periodic | 0.048 | 0.048 | 0.098 | 0.075 | +0.048 (2/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.524 | 0.547 | 0.531 | 0.548 | 0.512 | 0.518 | 0.511 | 0.719 | SmoothedRec | 0.024 | 0.024 | 0.170 | 0.047 | +0.024 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.612 | 0.619 | 0.581 | 0.577 | 0.541 | 0.552 | 0.550 | 0.713 | Periodic | 0.042 | 0.007 | 0.094 | 0.080 | +0.007 (1/2) |
| hh_014 | single_adult_wfh | 1 | 0.727 | 0.729 | 0.696 | 0.733 | 0.688 | 0.704 | 0.699 | 0.710 | SmoothedRec | 0.030 | 0.006 | -0.023 | 0.029 | +0.006 (2/2) |
| hh_016 | single_senior_solo | 1 | 0.740 | 0.740 | 0.697 | 0.740 | 0.694 | 0.715 | 0.709 | 0.684 | Periodic | 0.025 | 0.000 | -0.056 | 0.026 | +0.000 (1/2) |
| **1-resident mean** |  | 7 | 0.629 | 0.636 | 0.598 | 0.631 | 0.581 | 0.592 | 0.587 | 0.717 |  | 0.042 | 0.012 | 0.076 |  |  |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.497 | 0.460 | 0.489 | 0.459 | 0.506 | 0.510 | 0.507 | 0.776 | PerpetuaStar | 0.014 | 0.014 | 0.265 | 0.067 | +0.014 (1/2) |
| hh_018 | working_couple_no_children | 2 | 0.596 | 0.595 | 0.637 | 0.596 | 0.572 | 0.590 | 0.580 | 0.753 | DaytypeMix | 0.042 | 0.042 | 0.116 | 0.017 | +0.042 (2/2) |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.573 | 0.488 | 0.464 | 0.489 | 0.491 | 0.489 | 0.486 | 0.728 | LastObs | 0.084 | 0.000 | 0.156 | 0.017 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.611 | 0.559 | 0.533 | 0.585 | 0.541 | 0.547 | 0.542 | 0.712 | LastObs | 0.065 | 0.000 | 0.100 | 0.074 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.642 | 0.641 | 0.599 | 0.640 | 0.618 | 0.624 | 0.622 | 0.678 | LastObs | 0.018 | 0.000 | 0.036 | 0.037 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.661 | 0.659 | 0.613 | 0.661 | 0.604 | 0.612 | 0.600 | 0.660 | LastObs | 0.048 | 0.000 | -0.001 | 0.018 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.597 | 0.567 | 0.556 | 0.572 | 0.555 | 0.562 | 0.556 | 0.718 |  | 0.045 | 0.009 | 0.112 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.509 | 0.516 | 0.484 | 0.472 | 0.468 | 0.480 | 0.477 | 0.752 | Periodic | 0.035 | 0.007 | 0.237 | 0.084 | +0.007 (1/2) |
| hh_007 | college_roommates | 3 | 0.560 | 0.520 | 0.508 | 0.488 | 0.509 | 0.530 | 0.520 | 0.723 | LastObs | 0.040 | 0.000 | 0.164 | 0.074 | +0.000 (0/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.656 | 0.670 | 0.625 | 0.671 | 0.602 | 0.628 | 0.621 | 0.712 | SmoothedRec | 0.043 | 0.015 | 0.040 | 0.018 | +0.015 (2/2) |
| hh_002 | multigenerational_family | 5 | 0.573 | 0.573 | 0.519 | 0.537 | 0.497 | 0.505 | 0.503 | 0.695 | LastObs | 0.054 | 0.000 | 0.122 | 0.072 | +0.000 (0/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.572 | 0.549 | 0.569 | 0.574 | 0.561 | 0.569 | 0.565 | 0.695 | SmoothedRec | 0.006 | 0.002 | 0.120 | 0.053 | +0.002 (1/2) |
| hh_015 | single_parent_teens | 3 | 0.502 | 0.573 | 0.501 | 0.574 | 0.495 | 0.515 | 0.508 | 0.694 | SmoothedRec | 0.066 | 0.072 | 0.121 | 0.058 | +0.072 (2/2) |
| hh_009 | couple_with_toddler | 3 | 0.552 | 0.554 | 0.528 | 0.573 | 0.536 | 0.544 | 0.539 | 0.682 | SmoothedRec | 0.029 | 0.021 | 0.109 | 0.058 | +0.021 (2/2) |
| **3+-resident mean** |  | 7 | 0.561 | 0.565 | 0.533 | 0.556 | 0.524 | 0.539 | 0.533 | 0.708 |  | 0.039 | 0.017 | 0.130 |  |  |

![](separation_by_home.png)

## Same homes under the frozen forecast (D=7, h=1)

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_012 | researcher_household | 1 | 0.577 | 0.577 | 0.514 | 0.560 | 0.543 | 0.560 | 0.520 | 0.760 | LastObs | 0.017 | 0.000 | 0.183 | 0.132 | +0.000 (0/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.633 | 0.633 | 0.616 | 0.627 | 0.282 | 0.260 | 0.266 | 0.746 | LastObs | 0.017 | 0.000 | 0.113 | 0.036 | +0.000 (0/2) |
| hh_001 | working_professional_solo | 1 | 0.384 | 0.384 | 0.390 | 0.396 | 0.311 | 0.305 | 0.305 | 0.738 | SmoothedRec | 0.012 | 0.012 | 0.341 | 0.154 | +0.012 (1/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.368 | 0.402 | 0.443 | 0.368 | 0.310 | 0.299 | 0.287 | 0.718 | DaytypeMix | 0.075 | 0.075 | 0.276 | 0.184 | +0.075 (1/2) |
| hh_014 | single_adult_wfh | 1 | 0.449 | 0.449 | 0.442 | 0.449 | 0.532 | 0.532 | 0.526 | 0.692 | Perpetua | 0.083 | 0.083 | 0.160 | 0.100 | +0.083 (2/2) |
| hh_019 | working_professional_solo | 1 | 0.386 | 0.420 | 0.432 | 0.455 | 0.312 | 0.341 | 0.341 | 0.676 | SmoothedRec | 0.068 | 0.068 | 0.222 | 0.087 | +0.068 (2/2) |
| hh_016 | single_senior_solo | 1 | 0.612 | 0.584 | 0.590 | 0.612 | 0.388 | 0.399 | 0.404 | 0.663 | LastObs | 0.028 | 0.000 | 0.051 | 0.124 | +0.000 (0/2) |
| **1-resident mean** |  | 7 | 0.487 | 0.493 | 0.490 | 0.495 | 0.383 | 0.385 | 0.378 | 0.713 |  | 0.043 | 0.034 | 0.192 |  |  |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.500 | 0.442 | 0.449 | 0.500 | 0.297 | 0.312 | 0.297 | 0.790 | LastObs | 0.058 | 0.000 | 0.290 | 0.127 | +0.000 (0/2) |
| hh_018 | working_couple_no_children | 2 | 0.465 | 0.465 | 0.447 | 0.484 | 0.365 | 0.377 | 0.365 | 0.774 | SmoothedRec | 0.038 | 0.019 | 0.289 | 0.206 | +0.019 (2/2) |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.561 | 0.554 | 0.547 | 0.561 | 0.482 | 0.504 | 0.496 | 0.748 | LastObs | 0.014 | 0.000 | 0.187 | 0.065 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.468 | 0.444 | 0.462 | 0.468 | 0.304 | 0.316 | 0.316 | 0.737 | LastObs | 0.023 | 0.000 | 0.269 | 0.141 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.600 | 0.600 | 0.588 | 0.600 | 0.435 | 0.512 | 0.476 | 0.682 | LastObs | 0.012 | 0.000 | 0.082 | 0.118 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.562 | 0.544 | 0.503 | 0.533 | 0.479 | 0.438 | 0.432 | 0.651 | LastObs | 0.059 | 0.000 | 0.089 | 0.057 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.526 | 0.508 | 0.499 | 0.524 | 0.394 | 0.410 | 0.397 | 0.730 |  | 0.034 | 0.003 | 0.201 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.361 | 0.367 | 0.392 | 0.367 | 0.337 | 0.349 | 0.319 | 0.777 | DaytypeMix | 0.030 | 0.030 | 0.386 | 0.145 | +0.030 (2/2) |
| hh_007 | college_roommates | 3 | 0.436 | 0.382 | 0.394 | 0.418 | 0.309 | 0.339 | 0.339 | 0.758 | LastObs | 0.055 | 0.000 | 0.321 | 0.109 | +0.000 (0/2) |
| hh_009 | couple_with_toddler | 3 | 0.433 | 0.433 | 0.409 | 0.427 | 0.333 | 0.322 | 0.327 | 0.743 | LastObs | 0.023 | 0.000 | 0.310 | 0.046 | +0.000 (0/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.433 | 0.446 | 0.382 | 0.433 | 0.363 | 0.376 | 0.369 | 0.726 | Periodic | 0.064 | 0.013 | 0.280 | 0.120 | +0.013 (1/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.509 | 0.480 | 0.532 | 0.457 | 0.428 | 0.451 | 0.434 | 0.676 | DaytypeMix | 0.075 | 0.023 | 0.145 | 0.102 | +0.021 (1/2) |
| hh_015 | single_parent_teens | 3 | 0.324 | 0.420 | 0.409 | 0.364 | 0.301 | 0.318 | 0.307 | 0.676 | Periodic | 0.097 | 0.097 | 0.256 | 0.182 | +0.097 (2/2) |
| hh_002 | multigenerational_family | 5 | 0.413 | 0.383 | 0.365 | 0.383 | 0.323 | 0.353 | 0.347 | 0.659 | LastObs | 0.048 | 0.000 | 0.246 | 0.169 | +0.000 (0/2) |
| **3+-resident mean** |  | 7 | 0.416 | 0.416 | 0.412 | 0.407 | 0.342 | 0.358 | 0.349 | 0.716 |  | 0.056 | 0.023 | 0.278 |  |  |

## Age of the last sighting

All homes pooled:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 1091 | 0.990 | 0.985 | 0.980 | 0.990 | 0.938 | 0.947 | 0.942 | 0.692 |
| 15m-1h | 3423 | 0.933 | 0.930 | 0.909 | 0.933 | 0.877 | 0.897 | 0.892 | 0.677 |
| 1-3h | 7882 | 0.857 | 0.854 | 0.783 | 0.857 | 0.798 | 0.815 | 0.810 | 0.689 |
| 3-6h | 9713 | 0.760 | 0.759 | 0.706 | 0.760 | 0.704 | 0.719 | 0.717 | 0.701 |
| 6-12h | 16019 | 0.701 | 0.700 | 0.650 | 0.701 | 0.638 | 0.649 | 0.643 | 0.721 |
| 12-24h | 31556 | 0.592 | 0.594 | 0.568 | 0.592 | 0.495 | 0.510 | 0.504 | 0.715 |
| 1-2d | 12975 | 0.296 | 0.285 | 0.288 | 0.272 | 0.350 | 0.353 | 0.347 | 0.706 |
| 2-3d | 3884 | 0.195 | 0.165 | 0.185 | 0.141 | 0.302 | 0.291 | 0.289 | 0.766 |
| 3d+ | 3457 | 0.191 | 0.141 | 0.181 | 0.123 | 0.319 | 0.309 | 0.304 | 0.785 |

1-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 450 | 0.982 | 0.976 | 0.976 | 0.982 | 0.929 | 0.936 | 0.929 | 0.682 |
| 15m-1h | 1533 | 0.928 | 0.925 | 0.894 | 0.928 | 0.856 | 0.876 | 0.874 | 0.674 |
| 1-3h | 3412 | 0.875 | 0.874 | 0.800 | 0.875 | 0.814 | 0.836 | 0.828 | 0.693 |
| 3-6h | 3966 | 0.778 | 0.778 | 0.724 | 0.778 | 0.709 | 0.731 | 0.731 | 0.701 |
| 6-12h | 6494 | 0.724 | 0.724 | 0.669 | 0.725 | 0.652 | 0.662 | 0.658 | 0.708 |
| 12-24h | 10606 | 0.594 | 0.599 | 0.575 | 0.595 | 0.492 | 0.504 | 0.500 | 0.729 |
| 1-2d | 3528 | 0.174 | 0.216 | 0.190 | 0.185 | 0.298 | 0.288 | 0.283 | 0.740 |
| 2-3d | 976 | 0.170 | 0.195 | 0.194 | 0.165 | 0.325 | 0.296 | 0.294 | 0.769 |
| 3d+ | 535 | 0.164 | 0.215 | 0.226 | 0.217 | 0.314 | 0.305 | 0.293 | 0.776 |

2-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 310 | 0.994 | 0.994 | 0.987 | 0.994 | 0.916 | 0.948 | 0.945 | 0.710 |
| 15m-1h | 945 | 0.958 | 0.954 | 0.940 | 0.958 | 0.916 | 0.927 | 0.921 | 0.703 |
| 1-3h | 2234 | 0.853 | 0.852 | 0.779 | 0.853 | 0.802 | 0.800 | 0.796 | 0.683 |
| 3-6h | 2920 | 0.765 | 0.765 | 0.718 | 0.765 | 0.708 | 0.715 | 0.712 | 0.698 |
| 6-12h | 4691 | 0.685 | 0.685 | 0.650 | 0.685 | 0.624 | 0.639 | 0.630 | 0.762 |
| 12-24h | 10739 | 0.593 | 0.592 | 0.569 | 0.592 | 0.505 | 0.518 | 0.509 | 0.710 |
| 1-2d | 2908 | 0.234 | 0.119 | 0.175 | 0.135 | 0.331 | 0.327 | 0.326 | 0.684 |
| 2-3d | 916 | 0.228 | 0.035 | 0.147 | 0.068 | 0.272 | 0.248 | 0.248 | 0.749 |
| 3d+ | 1337 | 0.209 | 0.013 | 0.133 | 0.040 | 0.318 | 0.298 | 0.298 | 0.791 |

3+-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 331 | 0.997 | 0.991 | 0.979 | 0.997 | 0.970 | 0.961 | 0.958 | 0.689 |
| 15m-1h | 945 | 0.917 | 0.914 | 0.904 | 0.917 | 0.872 | 0.899 | 0.892 | 0.656 |
| 1-3h | 2236 | 0.832 | 0.826 | 0.762 | 0.832 | 0.771 | 0.799 | 0.795 | 0.687 |
| 3-6h | 2827 | 0.728 | 0.727 | 0.669 | 0.728 | 0.695 | 0.706 | 0.704 | 0.702 |
| 6-12h | 4834 | 0.685 | 0.684 | 0.625 | 0.685 | 0.632 | 0.641 | 0.636 | 0.698 |
| 12-24h | 10211 | 0.589 | 0.590 | 0.561 | 0.590 | 0.488 | 0.508 | 0.503 | 0.706 |
| 1-2d | 6539 | 0.389 | 0.397 | 0.392 | 0.380 | 0.386 | 0.400 | 0.391 | 0.697 |
| 2-3d | 1992 | 0.192 | 0.210 | 0.199 | 0.164 | 0.304 | 0.309 | 0.306 | 0.773 |
| 3d+ | 1585 | 0.184 | 0.224 | 0.206 | 0.162 | 0.322 | 0.320 | 0.312 | 0.784 |

![](age_by_group.png)

Kept current versus frozen forecast at matched ages, LastObs and the best routine model per group:

![](modes_by_group.png)

Every model here uses recent sightings, so at short ages they all sit on LastObs; the informative comparison is at a day or more, against the oracle:

| home | type | res | LastObs 12-24h | LastObs 1-2d | best model 1-2d | oracle 1-2d | LastObs 3d+ | best model 3d+ | oracle 3d+ | routine > LastObs by 0.02 from |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.567 | 0.352 | 0.352 (SmoothedRec, n=537) | 0.791 | 0.268 | 0.403 (Perpetua, n=149) | 0.805 | never |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.470 | 0.087 | 0.322 (PerpetuaStar, n=686) | 0.730 | 0.167 | 0.250 (Perpetua, n=36) | 0.611 | 12-24h |
| hh_012 | researcher_household | 1 | 0.549 | 0.232 | 0.232 (Periodic, n=630) | 0.757 | 0.179 | 0.310 (SmoothedRec, n=145) | 0.731 | never |
| hh_014 | single_adult_wfh | 1 | 0.742 | 0.137 | 0.425 (PerpStarFlat, n=424) | 0.684 | n=24<30 | n=24<30 | n=24<30 | 1-2d |
| hh_016 | single_senior_solo | 1 | 0.670 | 0.039 | 0.337 (PerpetuaStar, n=205) | 0.629 | n=3<30 | n=3<30 | n=3<30 | never |
| hh_019 | working_professional_solo | 1 | 0.564 | 0.247 | 0.260 (Periodic, n=511) | 0.763 | 0.110 | 0.287 (Perpetua, n=136) | 0.779 | 2-3d |
| hh_020 | working_professional_solo__night_shift | 1 | 0.586 | 0.049 | 0.344 (Perpetua, n=535) | 0.744 | 0.000 | 0.452 (PerpStarFlat, n=42) | 0.810 | 12-24h |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.575 | 0.210 | 0.326 (PerpetuaStar, n=519) | 0.738 | 0.136 | 0.307 (Perpetua, n=479) | 0.743 | never |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.516 | 0.390 | 0.390 (LastObs, n=610) | 0.725 | 0.349 | 0.349 (LastObs, n=375) | 0.856 | never |
| hh_011 | remote_worker_couple | 2 | 0.671 | 0.169 | 0.379 (PerpetuaStar, n=462) | 0.608 | 0.171 | 0.195 (Perpetua, n=41) | 0.585 | never |
| hh_013 | retired_couple | 2 | 0.604 | 0.103 | 0.429 (Perpetua, n=368) | 0.549 | n=5<30 | n=5<30 | n=5<30 | never |
| hh_017 | working_couple_no_children | 2 | 0.570 | 0.288 | 0.300 (PerpetuaStar, n=527) | 0.670 | 0.322 | 0.438 (PerpStarFlat, n=233) | 0.833 | never |
| hh_018 | working_couple_no_children | 2 | 0.599 | 0.156 | 0.434 (DaytypeMix, n=422) | 0.780 | 0.005 | 0.480 (DaytypeMix, n=204) | 0.784 | 1-2d |
| hh_002 | multigenerational_family | 5 | 0.607 | 0.479 | 0.479 (LastObs, n=1104) | 0.678 | 0.299 | 0.299 (Periodic, n=425) | 0.741 | never |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.687 | 0.473 | 0.511 (SmoothedRec, n=875) | 0.721 | 0.220 | 0.370 (Perpetua, n=100) | 0.810 | 1-2d |
| hh_007 | college_roommates | 3 | 0.564 | 0.467 | 0.467 (LastObs, n=1004) | 0.721 | 0.275 | 0.379 (PerpetuaStar, n=211) | 0.791 | never |
| hh_008 | college_roommates__irregular_gig | 3 | 0.629 | 0.371 | 0.433 (DaytypeMix, n=933) | 0.687 | 0.119 | 0.409 (Perpetua, n=176) | 0.716 | 1-2d |
| hh_009 | couple_with_toddler | 3 | 0.542 | 0.238 | 0.394 (PerpetuaStar, n=667) | 0.645 | 0.088 | 0.333 (PerpetuaStar, n=114) | 0.816 | 3d+ |
| hh_010 | family_teen_and_child | 4 | 0.533 | 0.378 | 0.381 (Periodic, n=937) | 0.726 | 0.159 | 0.322 (PerpStarFlat, n=339) | 0.814 | 3d+ |
| hh_015 | single_parent_teens | 3 | 0.553 | 0.268 | 0.416 (SmoothedRec, n=1019) | 0.690 | 0.000 | 0.355 (SmoothedRec, n=220) | 0.836 | 1-2d |

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
| hh_001 | working_professional_solo | 1 | LastObs | 0.676 | 0.585 | 0.046 | 0.053 | 0.585 | 0.755 | 3 |
| hh_006 | working_professional_solo__irregular_gig | 1 | SmoothedRec | 0.491 | 0.590 | -0.004 | 0.040 | 0.561 | 0.726 | 13 |
| hh_012 | researcher_household | 1 | LastObs | 0.531 | 0.608 | 0.011 | 0.089 | 0.608 | 0.740 | 9 |
| hh_014 | single_adult_wfh | 1 | SmoothedRec | 0.724 | 0.710 | 0.007 | 0.034 | 0.697 | 0.718 | 9 |
| hh_016 | single_senior_solo | 1 | Periodic | 0.776 | 0.715 | 0.009 | 0.002 | 0.713 | 0.667 | 3 |
| hh_019 | working_professional_solo | 1 | Periodic | 0.680 | 0.622 | 0.004 | 0.038 | 0.615 | 0.751 | 3 |
| hh_020 | working_professional_solo__night_shift | 1 | Periodic | 0.598 | 0.617 | 0.017 | 0.051 | 0.574 | 0.758 | 9 |
| hh_004 | working_couple_no_children__night_shift | 2 | LastObs | 0.539 | 0.505 | 0.000 | 0.027 | 0.505 | 0.798 | 6 |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | LastObs | 0.543 | 0.578 | 0.019 | 0.094 | 0.578 | 0.735 | 13 |
| hh_011 | remote_worker_couple | 2 | SmoothedRec | 0.700 | 0.642 | 0.011 | 0.028 | 0.641 | 0.655 | 3 |
| hh_013 | retired_couple | 2 | LastObs | 0.637 | 0.630 | 0.002 | 0.015 | 0.630 | 0.664 | 7 |
| hh_017 | working_couple_no_children | 2 | LastObs | 0.587 | 0.619 | 0.030 | 0.065 | 0.619 | 0.703 | 15 |
| hh_018 | working_couple_no_children | 2 | DaytypeMix | 0.626 | 0.625 | 0.031 | 0.026 | 0.599 | 0.753 | 12 |
| hh_002 | multigenerational_family | 5 | Periodic | 0.537 | 0.581 | 0.028 | 0.063 | 0.580 | 0.719 | 15 |
| hh_003 | single_parent_teens__rotating_shift | 3 | Periodic | 0.696 | 0.676 | 0.006 | 0.036 | 0.664 | 0.706 | 6 |
| hh_007 | college_roommates | 3 | LastObs | 0.511 | 0.571 | 0.000 | 0.057 | 0.571 | 0.724 | 10 |
| hh_008 | college_roommates__irregular_gig | 3 | SmoothedRec | 0.557 | 0.579 | -0.007 | 0.009 | 0.578 | 0.722 | 9 |
| hh_009 | couple_with_toddler | 3 | SmoothedRec | 0.550 | 0.576 | 0.000 | 0.023 | 0.553 | 0.698 | 6 |
| hh_010 | family_teen_and_child | 4 | LastObs | 0.480 | 0.524 | -0.019 | 0.028 | 0.524 | 0.740 | 6 |
| hh_015 | single_parent_teens | 3 | Periodic | 0.563 | 0.554 | 0.050 | 0.055 | 0.494 | 0.729 | 3 |

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
| Perpetua | <15m | 1091 | 0.930 (1085) | 0.955 (6) | - | 0.91 |
| Perpetua | 15m-1h | 3423 | 0.915 (3360) | 0.905 (62) | 0.839 (1) | 0.92 |
| Perpetua | 1-3h | 7882 | 0.878 (7485) | 0.862 (384) | 0.929 (13) | 0.92 |
| Perpetua | 3-6h | 9713 | 0.813 (8965) | 0.782 (725) | 0.683 (23) | 0.91 |
| Perpetua | 6-12h | 16019 | 0.725 (14146) | 0.691 (1832) | 0.659 (41) | 0.91 |
| Perpetua | 12-24h | 31556 | 0.649 (26966) | 0.551 (4411) | 0.535 (179) | 0.90 |
| Perpetua | 1-2d | 12975 | 0.515 (9825) | 0.403 (2763) | 0.417 (387) | 0.88 |
| Perpetua | 2-3d | 3884 | 0.477 (2532) | 0.427 (1170) | 0.422 (182) | 0.87 |
| Perpetua | 3d+ | 3457 | 0.397 (2192) | 0.373 (1071) | 0.419 (194) | 0.89 |
| PerpetuaStar | <15m | 1091 | 0.914 (1085) | 0.943 (6) | - | 0.91 |
| PerpetuaStar | 15m-1h | 3423 | 0.915 (3360) | 0.907 (62) | 0.036 (1) | 0.92 |
| PerpetuaStar | 1-3h | 7882 | 0.886 (7485) | 0.850 (384) | 0.881 (13) | 0.92 |
| PerpetuaStar | 3-6h | 9713 | 0.821 (8965) | 0.790 (725) | 0.714 (23) | 0.91 |
| PerpetuaStar | 6-12h | 16019 | 0.746 (14146) | 0.705 (1832) | 0.629 (41) | 0.91 |
| PerpetuaStar | 12-24h | 31556 | 0.687 (26966) | 0.567 (4411) | 0.537 (179) | 0.90 |
| PerpetuaStar | 1-2d | 12975 | 0.511 (9825) | 0.377 (2763) | 0.399 (387) | 0.88 |
| PerpetuaStar | 2-3d | 3884 | 0.430 (2532) | 0.392 (1170) | 0.372 (182) | 0.87 |
| PerpetuaStar | 3d+ | 3457 | 0.320 (2192) | 0.289 (1071) | 0.293 (194) | 0.89 |
| PerpStarFlat | <15m | 1091 | 0.910 (1085) | 0.845 (6) | - | 0.91 |
| PerpStarFlat | 15m-1h | 3423 | 0.911 (3360) | 0.883 (62) | 0.026 (1) | 0.92 |
| PerpStarFlat | 1-3h | 7882 | 0.879 (7485) | 0.836 (384) | 0.884 (13) | 0.92 |
| PerpStarFlat | 3-6h | 9713 | 0.811 (8965) | 0.775 (725) | 0.715 (23) | 0.91 |
| PerpStarFlat | 6-12h | 16019 | 0.735 (14146) | 0.692 (1832) | 0.628 (41) | 0.91 |
| PerpStarFlat | 12-24h | 31556 | 0.673 (26966) | 0.555 (4411) | 0.535 (179) | 0.90 |
| PerpStarFlat | 1-2d | 12975 | 0.505 (9825) | 0.375 (2763) | 0.392 (387) | 0.88 |
| PerpStarFlat | 2-3d | 3884 | 0.427 (2532) | 0.390 (1170) | 0.379 (182) | 0.87 |
| PerpStarFlat | 3d+ | 3457 | 0.314 (2192) | 0.287 (1071) | 0.282 (194) | 0.89 |

Fallback use by query day: share of edge beliefs computed from the fallback single-component prior rather than a fitted mixture.

| model | day 3 | day 6 | day 9 | day 12 | day 15 | day 18 | day 21 | day 24 | day 27 |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua | 0.99 | 0.90 | 0.78 | 0.69 | 0.62 | 0.59 | 0.56 | 0.55 | 0.54 |
| PerpetuaStar | 0.99 | 0.90 | 0.78 | 0.69 | 0.62 | 0.59 | 0.56 | 0.55 | 0.54 |
| PerpStarFlat | 0.99 | 0.90 | 0.78 | 0.69 | 0.62 | 0.59 | 0.56 | 0.55 | 0.54 |

Training data per edge at the end of the kept-current run: completed segments are what the EM fits on; an edge needs 2 of a kind to leave the fallback prior for that filter.

| model | edges | median persistence segs | median emergence segs | share < 2 persistence | share < 2 emergence | median resets | mean K persistence |
|---|---|---|---|---|---|---|---|
| Perpetua | 5575 | 2 | 1 | 0.42 | 0.55 | 3 | 1.10 |
| PerpetuaStar | 5575 | 2 | 1 | 0.42 | 0.55 | 3 | 1.10 |
| PerpStarFlat | 5575 | 2 | 1 | 0.42 | 0.55 | 3 | 1.10 |


Figures are static; every plotted value appears in the tables above, which are the table view.
