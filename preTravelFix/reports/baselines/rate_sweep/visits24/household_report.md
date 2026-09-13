# Per-household passive analysis

20 households x 2 seeds (0, 1), 7 belief models + the routine oracle. Seeds of one home are pooled (equal question counts, so this is the seed mean); the last column of the overview is the largest across-seed range any model showed on that home, the noise floor for reading its row. Commit `f78a418bc019`, run 2026-09-05T02:22:47.

Two evaluation modes over the same questions:

- **kept current** (continuous): the belief is updated with every sighting strictly before each query and answers about now. Query day is the history length; the age of the object's last sighting is recorded per question.
- **frozen forecast**: the bake-off protocol. The belief is frozen at day D and answers questions up to 7 days later, bucketed by horizon; the headline cell is D=7, h=1 (questions 6-24h after the freeze).

The routine oracle predicts from the household's authored rules re-realized under many seeds, with no observations: routine knowledge alone. Not a hard ceiling; a fresh sighting beats it.

## Which homes separate the models (belief kept current)

Sorted by the oracle within resident group, so the most routine-predictable home of each group comes first.

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.826 | 0.767 | 0.726 | 0.826 | 0.654 | 0.666 | 0.664 | 0.737 | LastObs | 0.099 | 0.000 | -0.088 | 0.103 | +0.000 (0/2) |
| hh_012 | researcher_household | 1 | 0.782 | 0.781 | 0.643 | 0.775 | 0.649 | 0.657 | 0.657 | 0.730 | LastObs | 0.125 | 0.000 | -0.052 | 0.148 | +0.000 (0/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.754 | 0.854 | 0.788 | 0.804 | 0.696 | 0.713 | 0.714 | 0.729 | Periodic | 0.100 | 0.100 | -0.124 | 0.109 | +0.100 (2/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.709 | 0.770 | 0.738 | 0.771 | 0.642 | 0.651 | 0.651 | 0.719 | SmoothedRec | 0.062 | 0.062 | -0.052 | 0.104 | +0.062 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.793 | 0.793 | 0.740 | 0.733 | 0.670 | 0.686 | 0.685 | 0.713 | LastObs | 0.060 | 0.000 | -0.080 | 0.132 | +0.000 (0/2) |
| hh_014 | single_adult_wfh | 1 | 0.884 | 0.881 | 0.820 | 0.884 | 0.812 | 0.816 | 0.818 | 0.710 | LastObs | 0.064 | 0.000 | -0.174 | 0.008 | +0.000 (0/2) |
| hh_016 | single_senior_solo | 1 | 0.884 | 0.887 | 0.794 | 0.883 | 0.818 | 0.830 | 0.830 | 0.684 | Periodic | 0.058 | 0.003 | -0.203 | 0.022 | +0.003 (1/2) |
| **1-resident mean** |  | 7 | 0.805 | 0.819 | 0.750 | 0.811 | 0.706 | 0.717 | 0.717 | 0.717 |  | 0.081 | 0.024 | -0.111 |  |  |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.724 | 0.666 | 0.662 | 0.666 | 0.634 | 0.646 | 0.643 | 0.776 | LastObs | 0.062 | 0.000 | 0.051 | 0.115 | +0.000 (0/2) |
| hh_018 | working_couple_no_children | 2 | 0.715 | 0.713 | 0.786 | 0.715 | 0.658 | 0.678 | 0.682 | 0.753 | DaytypeMix | 0.073 | 0.071 | -0.033 | 0.014 | +0.071 (2/2) |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.796 | 0.673 | 0.593 | 0.674 | 0.619 | 0.637 | 0.633 | 0.728 | LastObs | 0.159 | 0.000 | -0.068 | 0.036 | +0.000 (0/2) |
| hh_017 | working_couple_no_children | 2 | 0.819 | 0.708 | 0.620 | 0.767 | 0.638 | 0.648 | 0.648 | 0.712 | LastObs | 0.170 | 0.000 | -0.107 | 0.116 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.795 | 0.794 | 0.682 | 0.791 | 0.729 | 0.736 | 0.735 | 0.678 | LastObs | 0.059 | 0.000 | -0.117 | 0.040 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.847 | 0.844 | 0.730 | 0.845 | 0.785 | 0.789 | 0.790 | 0.660 | LastObs | 0.057 | 0.000 | -0.187 | 0.036 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.783 | 0.733 | 0.679 | 0.743 | 0.677 | 0.689 | 0.688 | 0.718 |  | 0.097 | 0.012 | -0.077 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.692 | 0.695 | 0.624 | 0.635 | 0.594 | 0.600 | 0.600 | 0.752 | Periodic | 0.072 | 0.003 | 0.057 | 0.126 | +0.003 (1/2) |
| hh_007 | college_roommates | 3 | 0.782 | 0.718 | 0.667 | 0.664 | 0.638 | 0.646 | 0.645 | 0.723 | LastObs | 0.118 | 0.000 | -0.059 | 0.132 | +0.000 (0/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.813 | 0.837 | 0.776 | 0.840 | 0.734 | 0.750 | 0.749 | 0.712 | SmoothedRec | 0.064 | 0.027 | -0.128 | 0.062 | +0.027 (1/2) |
| hh_002 | multigenerational_family | 5 | 0.766 | 0.766 | 0.654 | 0.724 | 0.606 | 0.618 | 0.612 | 0.695 | Periodic | 0.112 | 0.000 | -0.071 | 0.084 | +0.000 (1/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.743 | 0.705 | 0.696 | 0.741 | 0.686 | 0.693 | 0.692 | 0.695 | LastObs | 0.046 | 0.000 | -0.048 | 0.081 | +0.000 (0/2) |
| hh_015 | single_parent_teens | 3 | 0.682 | 0.780 | 0.651 | 0.781 | 0.632 | 0.642 | 0.641 | 0.694 | SmoothedRec | 0.130 | 0.100 | -0.087 | 0.075 | +0.100 (2/2) |
| hh_009 | couple_with_toddler | 3 | 0.755 | 0.748 | 0.651 | 0.792 | 0.651 | 0.669 | 0.665 | 0.682 | SmoothedRec | 0.124 | 0.037 | -0.111 | 0.085 | +0.037 (1/2) |
| **3+-resident mean** |  | 7 | 0.748 | 0.750 | 0.674 | 0.740 | 0.649 | 0.660 | 0.658 | 0.708 |  | 0.095 | 0.024 | -0.064 |  |  |

![](separation_by_home.png)

## Same homes under the frozen forecast (D=7, h=1)

| home | type | res | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle | best | best-median | best-LastObs | oracle-best | seed range | paired best-LastObs (seeds>0) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_012 | researcher_household | 1 | 0.669 | 0.657 | 0.646 | 0.674 | 0.606 | 0.560 | 0.560 | 0.760 | SmoothedRec | 0.029 | 0.006 | 0.086 | 0.210 | +0.006 (1/2) |
| hh_020 | working_professional_solo__night_shift | 1 | 0.757 | 0.751 | 0.689 | 0.768 | 0.254 | 0.243 | 0.237 | 0.746 | SmoothedRec | 0.079 | 0.011 | -0.023 | 0.116 | +0.011 (1/2) |
| hh_001 | working_professional_solo | 1 | 0.470 | 0.470 | 0.488 | 0.476 | 0.305 | 0.287 | 0.287 | 0.738 | DaytypeMix | 0.018 | 0.018 | 0.250 | 0.141 | +0.018 (2/2) |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.437 | 0.483 | 0.443 | 0.466 | 0.362 | 0.345 | 0.339 | 0.718 | Periodic | 0.046 | 0.046 | 0.236 | 0.138 | +0.046 (2/2) |
| hh_014 | single_adult_wfh | 1 | 0.712 | 0.718 | 0.679 | 0.705 | 0.526 | 0.513 | 0.551 | 0.692 | Periodic | 0.038 | 0.006 | -0.026 | 0.120 | +0.006 (1/2) |
| hh_019 | working_professional_solo | 1 | 0.511 | 0.517 | 0.477 | 0.511 | 0.273 | 0.273 | 0.267 | 0.676 | Periodic | 0.040 | 0.006 | 0.159 | 0.034 | +0.006 (1/2) |
| hh_016 | single_senior_solo | 1 | 0.702 | 0.713 | 0.663 | 0.702 | 0.506 | 0.483 | 0.466 | 0.663 | Periodic | 0.051 | 0.011 | -0.051 | 0.067 | +0.011 (2/2) |
| **1-resident mean** |  | 7 | 0.608 | 0.616 | 0.584 | 0.615 | 0.404 | 0.386 | 0.387 | 0.713 |  | 0.043 | 0.015 | 0.090 |  |  |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.507 | 0.435 | 0.449 | 0.514 | 0.333 | 0.391 | 0.341 | 0.790 | SmoothedRec | 0.080 | 0.007 | 0.275 | 0.170 | +0.007 (1/2) |
| hh_018 | working_couple_no_children | 2 | 0.491 | 0.491 | 0.459 | 0.484 | 0.352 | 0.409 | 0.384 | 0.774 | LastObs | 0.031 | 0.000 | 0.283 | 0.164 | +0.000 (0/2) |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.576 | 0.576 | 0.583 | 0.576 | 0.424 | 0.439 | 0.367 | 0.748 | DaytypeMix | 0.007 | 0.007 | 0.165 | 0.162 | +0.007 (1/2) |
| hh_017 | working_couple_no_children | 2 | 0.491 | 0.480 | 0.456 | 0.485 | 0.298 | 0.345 | 0.333 | 0.737 | LastObs | 0.035 | 0.000 | 0.246 | 0.093 | +0.000 (0/2) |
| hh_013 | retired_couple | 2 | 0.671 | 0.665 | 0.588 | 0.671 | 0.559 | 0.482 | 0.494 | 0.682 | LastObs | 0.082 | 0.000 | 0.012 | 0.106 | +0.000 (0/2) |
| hh_011 | remote_worker_couple | 2 | 0.716 | 0.716 | 0.592 | 0.710 | 0.473 | 0.420 | 0.426 | 0.651 | LastObs | 0.124 | 0.000 | -0.065 | 0.066 | +0.000 (0/2) |
| **2-resident mean** |  | 6 | 0.575 | 0.560 | 0.521 | 0.573 | 0.407 | 0.414 | 0.391 | 0.730 |  | 0.060 | 0.002 | 0.153 |  |  |
| hh_010 | family_teen_and_child | 4 | 0.422 | 0.440 | 0.410 | 0.428 | 0.319 | 0.331 | 0.319 | 0.777 | Periodic | 0.030 | 0.018 | 0.337 | 0.084 | +0.018 (2/2) |
| hh_007 | college_roommates | 3 | 0.503 | 0.406 | 0.424 | 0.442 | 0.248 | 0.309 | 0.303 | 0.758 | LastObs | 0.097 | 0.000 | 0.255 | 0.220 | +0.000 (0/2) |
| hh_009 | couple_with_toddler | 3 | 0.491 | 0.491 | 0.444 | 0.497 | 0.327 | 0.345 | 0.333 | 0.743 | SmoothedRec | 0.053 | 0.006 | 0.246 | 0.101 | +0.006 (1/2) |
| hh_008 | college_roommates__irregular_gig | 3 | 0.503 | 0.497 | 0.484 | 0.503 | 0.287 | 0.357 | 0.369 | 0.726 | LastObs | 0.019 | 0.000 | 0.223 | 0.171 | +0.000 (0/2) |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.601 | 0.590 | 0.578 | 0.572 | 0.491 | 0.486 | 0.480 | 0.676 | LastObs | 0.029 | 0.000 | 0.075 | 0.123 | +0.000 (0/2) |
| hh_015 | single_parent_teens | 3 | 0.449 | 0.489 | 0.460 | 0.460 | 0.381 | 0.415 | 0.420 | 0.676 | Periodic | 0.040 | 0.040 | 0.188 | 0.159 | +0.040 (1/2) |
| hh_002 | multigenerational_family | 5 | 0.485 | 0.467 | 0.425 | 0.461 | 0.281 | 0.281 | 0.251 | 0.659 | LastObs | 0.060 | 0.000 | 0.174 | 0.091 | +0.000 (0/2) |
| **3+-resident mean** |  | 7 | 0.493 | 0.483 | 0.461 | 0.481 | 0.334 | 0.361 | 0.354 | 0.716 |  | 0.047 | 0.009 | 0.214 |  |  |

## Age of the last sighting

All homes pooled:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 4607 | 0.985 | 0.979 | 0.947 | 0.985 | 0.916 | 0.937 | 0.934 | 0.676 |
| 15m-1h | 12848 | 0.943 | 0.940 | 0.862 | 0.943 | 0.861 | 0.888 | 0.888 | 0.683 |
| 1-3h | 29363 | 0.874 | 0.873 | 0.755 | 0.874 | 0.794 | 0.807 | 0.807 | 0.697 |
| 3-6h | 20302 | 0.763 | 0.772 | 0.711 | 0.765 | 0.681 | 0.690 | 0.689 | 0.711 |
| 6-12h | 14346 | 0.640 | 0.594 | 0.577 | 0.583 | 0.458 | 0.461 | 0.460 | 0.744 |
| 12-24h | 7427 | 0.356 | 0.323 | 0.327 | 0.306 | 0.249 | 0.239 | 0.236 | 0.807 |
| 1-2d | 812 | 0.392 | 0.367 | 0.389 | 0.366 | 0.129 | 0.126 | 0.127 | 0.733 |
| 2-3d | 198 | 0.369 | 0.449 | 0.470 | 0.434 | 0.056 | 0.051 | 0.051 | 0.783 |
| 3d+ | 97 | 0.268 | 0.268 | 0.381 | 0.381 | 0.103 | 0.093 | 0.113 | 0.794 |

1-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 2113 | 0.992 | 0.987 | 0.960 | 0.992 | 0.930 | 0.951 | 0.948 | 0.690 |
| 15m-1h | 5669 | 0.953 | 0.950 | 0.879 | 0.953 | 0.877 | 0.898 | 0.900 | 0.692 |
| 1-3h | 12254 | 0.882 | 0.882 | 0.788 | 0.882 | 0.804 | 0.815 | 0.816 | 0.703 |
| 3-6h | 4469 | 0.716 | 0.766 | 0.719 | 0.728 | 0.626 | 0.630 | 0.629 | 0.731 |
| 6-12h | 4508 | 0.640 | 0.685 | 0.630 | 0.661 | 0.492 | 0.497 | 0.497 | 0.742 |
| 12-24h | 1915 | 0.384 | 0.408 | 0.340 | 0.389 | 0.194 | 0.193 | 0.190 | 0.820 |
| 1-2d | 405 | 0.402 | 0.390 | 0.407 | 0.427 | 0.114 | 0.121 | 0.121 | 0.723 |
| 2-3d | 104 | 0.356 | 0.462 | 0.538 | 0.423 | 0.067 | 0.058 | 0.058 | 0.779 |
| 3d+ | 63 | 0.222 | 0.270 | 0.413 | 0.460 | 0.127 | 0.095 | 0.127 | 0.841 |

2-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 1220 | 0.978 | 0.976 | 0.931 | 0.978 | 0.902 | 0.926 | 0.921 | 0.663 |
| 15m-1h | 3603 | 0.936 | 0.933 | 0.843 | 0.936 | 0.849 | 0.881 | 0.881 | 0.686 |
| 1-3h | 8639 | 0.872 | 0.870 | 0.728 | 0.872 | 0.787 | 0.804 | 0.804 | 0.697 |
| 3-6h | 7162 | 0.784 | 0.776 | 0.720 | 0.778 | 0.707 | 0.715 | 0.716 | 0.721 |
| 6-12h | 4084 | 0.657 | 0.461 | 0.506 | 0.482 | 0.407 | 0.407 | 0.405 | 0.764 |
| 12-24h | 2127 | 0.314 | 0.105 | 0.270 | 0.163 | 0.276 | 0.263 | 0.260 | 0.783 |
| 1-2d | 125 | 0.376 | 0.352 | 0.408 | 0.368 | 0.096 | 0.088 | 0.096 | 0.744 |
| 2-3d | 32 | 0.562 | 0.375 | 0.531 | 0.531 | 0.031 | 0.031 | 0.031 | 0.812 |
| 3d+ | 8 | 0.375 | 0.125 | 0.125 | 0.250 | 0.000 | 0.125 | 0.125 | 0.625 |

3+-resident homes:

| age of last sighting | n | LastObs | Periodic | DaytypeMix | SmoothedRec | Perpetua | PerpetuaStar | PerpStarFlat | oracle |
|---|---|---|---|---|---|---|---|---|---|
| <15m | 1274 | 0.979 | 0.969 | 0.940 | 0.979 | 0.904 | 0.923 | 0.924 | 0.666 |
| 15m-1h | 3576 | 0.935 | 0.931 | 0.853 | 0.935 | 0.846 | 0.878 | 0.877 | 0.664 |
| 1-3h | 8470 | 0.863 | 0.862 | 0.736 | 0.863 | 0.786 | 0.800 | 0.798 | 0.688 |
| 3-6h | 8671 | 0.769 | 0.771 | 0.698 | 0.772 | 0.688 | 0.701 | 0.699 | 0.692 |
| 6-12h | 5754 | 0.627 | 0.617 | 0.585 | 0.593 | 0.468 | 0.472 | 0.469 | 0.731 |
| 12-24h | 3385 | 0.366 | 0.412 | 0.355 | 0.349 | 0.264 | 0.250 | 0.247 | 0.814 |
| 1-2d | 282 | 0.383 | 0.340 | 0.355 | 0.277 | 0.167 | 0.149 | 0.149 | 0.741 |
| 2-3d | 62 | 0.290 | 0.468 | 0.323 | 0.403 | 0.048 | 0.048 | 0.048 | 0.774 |
| 3d+ | 26 | 0.346 | 0.308 | 0.385 | 0.231 | 0.077 | 0.077 | 0.077 | 0.731 |

![](age_by_group.png)

Kept current versus frozen forecast at matched ages, LastObs and the best routine model per group:

![](modes_by_group.png)

Every model here uses recent sightings, so at short ages they all sit on LastObs; the informative comparison is at a day or more, against the oracle:

| home | type | res | LastObs 12-24h | LastObs 1-2d | best model 1-2d | oracle 1-2d | LastObs 3d+ | best model 3d+ | oracle 3d+ | routine > LastObs by 0.02 from |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_001 | working_professional_solo | 1 | 0.557 | 0.500 | 0.500 (SmoothedRec, n=140) | 0.743 | n=27<30 | n=27<30 | n=27<30 | 2-3d |
| hh_006 | working_professional_solo__irregular_gig | 1 | 0.104 | 0.587 | 0.587 (LastObs, n=63) | 0.857 | n=1<30 | n=1<30 | n=1<30 | 3-6h |
| hh_012 | researcher_household | 1 | 0.436 | 0.286 | 0.338 (DaytypeMix, n=77) | 0.519 | n=24<30 | n=24<30 | n=24<30 | 1-2d |
| hh_014 | single_adult_wfh | 1 | 0.609 | 0.221 | 0.676 (SmoothedRec, n=68) | 0.779 | n=11<30 | n=11<30 | n=11<30 | 12-24h |
| hh_016 | single_senior_solo | 1 | 0.081 | n=5<30 | n=5<30 | n=5<30 | - | - | - | never |
| hh_019 | working_professional_solo | 1 | 0.442 | 0.319 | 0.319 (LastObs, n=47) | 0.745 | - | - | - | 2-3d |
| hh_020 | working_professional_solo__night_shift | 1 | 0.153 | n=5<30 | n=5<30 | n=5<30 | - | - | - | 3-6h |
| hh_004 | working_couple_no_children__night_shift | 2 | 0.101 | - | - | - | - | - | - | never |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | 0.456 | n=19<30 | n=19<30 | n=19<30 | n=3<30 | n=3<30 | n=3<30 | 1-2d |
| hh_011 | remote_worker_couple | 2 | 0.505 | 0.479 | 0.479 (SmoothedRec, n=48) | 0.896 | n=4<30 | n=4<30 | n=4<30 | 12-24h |
| hh_013 | retired_couple | 2 | 0.125 | - | - | - | - | - | - | never |
| hh_017 | working_couple_no_children | 2 | 0.573 | 0.487 | 0.487 (LastObs, n=39) | 0.538 | n=1<30 | n=1<30 | n=1<30 | never |
| hh_018 | working_couple_no_children | 2 | 0.035 | n=19<30 | n=19<30 | n=19<30 | - | - | - | 6-12h |
| hh_002 | multigenerational_family | 5 | 0.570 | 0.327 | 0.416 (DaytypeMix, n=113) | 0.628 | n=14<30 | n=14<30 | n=14<30 | 1-2d |
| hh_003 | single_parent_teens__rotating_shift | 3 | 0.373 | n=18<30 | n=18<30 | n=18<30 | n=2<30 | n=2<30 | n=2<30 | 6-12h |
| hh_007 | college_roommates | 3 | 0.561 | 0.745 | 0.745 (LastObs, n=51) | 0.902 | - | - | - | never |
| hh_008 | college_roommates__irregular_gig | 3 | 0.232 | n=19<30 | n=19<30 | n=19<30 | - | - | - | 6-12h |
| hh_009 | couple_with_toddler | 3 | 0.361 | n=12<30 | n=12<30 | n=12<30 | - | - | - | never |
| hh_010 | family_teen_and_child | 4 | 0.272 | 0.339 | 0.559 (Periodic, n=59) | 0.797 | n=10<30 | n=10<30 | n=10<30 | 1-2d |
| hh_015 | single_parent_teens | 3 | 0.047 | n=10<30 | n=10<30 | n=10<30 | - | - | - | 3-6h |

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
| hh_001 | working_professional_solo | 1 | LastObs | 0.846 | 0.802 | 0.052 | 0.119 | 0.802 | 0.755 | 3 |
| hh_006 | working_professional_solo__irregular_gig | 1 | Periodic | 0.717 | 0.762 | 0.063 | 0.062 | 0.703 | 0.726 | 8 |
| hh_012 | researcher_household | 1 | LastObs | 0.781 | 0.781 | 0.102 | 0.119 | 0.781 | 0.740 | 3 |
| hh_014 | single_adult_wfh | 1 | SmoothedRec | 0.854 | 0.860 | 0.007 | 0.061 | 0.849 | 0.718 | 3 |
| hh_016 | single_senior_solo | 1 | Periodic | 0.883 | 0.893 | 0.033 | 0.069 | 0.892 | 0.667 | 4 |
| hh_019 | working_professional_solo | 1 | Periodic | 0.865 | 0.792 | 0.020 | 0.071 | 0.786 | 0.751 | 3 |
| hh_020 | working_professional_solo__night_shift | 1 | Periodic | 0.837 | 0.862 | 0.126 | 0.093 | 0.769 | 0.758 | 9 |
| hh_004 | working_couple_no_children__night_shift | 2 | LastObs | 0.724 | 0.723 | 0.065 | 0.074 | 0.723 | 0.798 | 3 |
| hh_005 | working_couple_no_children__opposite_schedules | 2 | LastObs | 0.750 | 0.792 | 0.122 | 0.167 | 0.792 | 0.735 | 8 |
| hh_011 | remote_worker_couple | 2 | LastObs | 0.867 | 0.829 | 0.011 | 0.037 | 0.829 | 0.655 | 3 |
| hh_013 | retired_couple | 2 | LastObs | 0.772 | 0.785 | 0.041 | 0.051 | 0.785 | 0.664 | 6 |
| hh_017 | working_couple_no_children | 2 | LastObs | 0.811 | 0.831 | 0.131 | 0.167 | 0.831 | 0.703 | 5 |
| hh_018 | working_couple_no_children | 2 | DaytypeMix | 0.819 | 0.763 | 0.104 | 0.035 | 0.728 | 0.753 | 3 |
| hh_002 | multigenerational_family | 5 | LastObs | 0.739 | 0.766 | 0.028 | 0.134 | 0.766 | 0.719 | 6 |
| hh_003 | single_parent_teens__rotating_shift | 3 | Periodic | 0.863 | 0.843 | 0.015 | 0.090 | 0.817 | 0.706 | 3 |
| hh_007 | college_roommates | 3 | LastObs | 0.793 | 0.788 | 0.137 | 0.144 | 0.788 | 0.724 | 5 |
| hh_008 | college_roommates__irregular_gig | 3 | LastObs | 0.765 | 0.741 | 0.043 | 0.071 | 0.741 | 0.722 | 5 |
| hh_009 | couple_with_toddler | 3 | SmoothedRec | 0.757 | 0.810 | 0.080 | 0.121 | 0.768 | 0.698 | 4 |
| hh_010 | family_teen_and_child | 4 | LastObs | 0.680 | 0.708 | 0.039 | 0.098 | 0.708 | 0.740 | 6 |
| hh_015 | single_parent_teens | 3 | SmoothedRec | 0.772 | 0.776 | 0.113 | 0.117 | 0.687 | 0.729 | 19 |

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
| Perpetua | <15m | 4607 | 0.907 (4590) | 0.737 (16) | 0.970 (1) | 0.90 |
| Perpetua | 15m-1h | 12848 | 0.878 (12591) | 0.829 (250) | 0.947 (7) | 0.90 |
| Perpetua | 1-3h | 29363 | 0.842 (27917) | 0.752 (1412) | 0.698 (34) | 0.90 |
| Perpetua | 3-6h | 20302 | 0.772 (17935) | 0.466 (2310) | 0.522 (57) | 0.89 |
| Perpetua | 6-12h | 14346 | 0.627 (9756) | 0.312 (4461) | 0.316 (129) | 0.89 |
| Perpetua | 12-24h | 7427 | 0.440 (3490) | 0.269 (3612) | 0.252 (325) | 0.87 |
| Perpetua | 1-2d | 812 | 0.317 (232) | 0.207 (267) | 0.233 (313) | 0.83 |
| Perpetua | 2-3d | 198 | 0.235 (24) | 0.241 (65) | 0.189 (109) | 0.79 |
| Perpetua | 3d+ | 97 | 0.165 (21) | 0.140 (31) | 0.133 (45) | 0.74 |
| PerpetuaStar | <15m | 4607 | 0.927 (4590) | 0.802 (16) | 0.976 (1) | 0.90 |
| PerpetuaStar | 15m-1h | 12848 | 0.896 (12591) | 0.906 (250) | 0.952 (7) | 0.90 |
| PerpetuaStar | 1-3h | 29363 | 0.852 (27917) | 0.756 (1412) | 0.741 (34) | 0.90 |
| PerpetuaStar | 3-6h | 20302 | 0.780 (17935) | 0.440 (2310) | 0.526 (57) | 0.89 |
| PerpetuaStar | 6-12h | 14346 | 0.637 (9756) | 0.263 (4461) | 0.271 (129) | 0.89 |
| PerpetuaStar | 12-24h | 7427 | 0.395 (3490) | 0.205 (3612) | 0.217 (325) | 0.87 |
| PerpetuaStar | 1-2d | 812 | 0.321 (232) | 0.161 (267) | 0.199 (313) | 0.83 |
| PerpetuaStar | 2-3d | 198 | 0.122 (24) | 0.107 (65) | 0.161 (109) | 0.79 |
| PerpetuaStar | 3d+ | 97 | 0.132 (21) | 0.084 (31) | 0.096 (45) | 0.74 |
| PerpStarFlat | <15m | 4607 | 0.928 (4590) | 0.800 (16) | 0.973 (1) | 0.90 |
| PerpStarFlat | 15m-1h | 12848 | 0.896 (12591) | 0.906 (250) | 0.955 (7) | 0.90 |
| PerpStarFlat | 1-3h | 29363 | 0.851 (27917) | 0.757 (1412) | 0.738 (34) | 0.90 |
| PerpStarFlat | 3-6h | 20302 | 0.779 (17935) | 0.437 (2310) | 0.527 (57) | 0.89 |
| PerpStarFlat | 6-12h | 14346 | 0.633 (9756) | 0.264 (4461) | 0.271 (129) | 0.89 |
| PerpStarFlat | 12-24h | 7427 | 0.394 (3490) | 0.201 (3612) | 0.210 (325) | 0.87 |
| PerpStarFlat | 1-2d | 812 | 0.318 (232) | 0.170 (267) | 0.202 (313) | 0.83 |
| PerpStarFlat | 2-3d | 198 | 0.122 (24) | 0.108 (65) | 0.161 (109) | 0.79 |
| PerpStarFlat | 3d+ | 97 | 0.132 (21) | 0.083 (31) | 0.096 (45) | 0.74 |

Fallback use by query day: share of edge beliefs computed from the fallback single-component prior rather than a fitted mixture.

| model | day 3 | day 6 | day 9 | day 12 | day 15 | day 18 | day 21 | day 24 | day 27 |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua | 0.79 | 0.67 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.52 | 0.52 |
| PerpetuaStar | 0.79 | 0.67 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.52 | 0.52 |
| PerpStarFlat | 0.79 | 0.67 | 0.60 | 0.57 | 0.55 | 0.54 | 0.53 | 0.52 | 0.52 |

Training data per edge at the end of the kept-current run: completed segments are what the EM fits on; an edge needs 2 of a kind to leave the fallback prior for that filter.

| model | edges | median persistence segs | median emergence segs | share < 2 persistence | share < 2 emergence | median resets | mean K persistence |
|---|---|---|---|---|---|---|---|
| Perpetua | 7315 | 2 | 1 | 0.39 | 0.53 | 3 | 1.32 |
| PerpetuaStar | 7315 | 2 | 1 | 0.39 | 0.53 | 3 | 1.32 |
| PerpStarFlat | 7315 | 2 | 1 | 0.39 | 0.53 | 3 | 1.32 |


Figures are static; every plotted value appears in the tables above, which are the table view.
