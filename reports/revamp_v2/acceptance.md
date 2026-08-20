# revamp_v2 acceptance report

Model slug: `qwen3.6-35b-a3b-fp8`; seed 0.

## Build (generation + the four gates)

| hh | type | status | program tries | persona tries | blocks | arcs | objects | rules | ids leak type |
|---|---|---|---|---|---|---|---|---|---|
| hh1 | night_shift_worker_solo | OK | 1 | 1 | 13 | 4 | 16 | 61 | no |
| hh2 | family_young_children | OK | 3 | 5 | 37 | 8 | 36 | 72 | YES |
| hh3 | retired_couple | OK | 1 | 1 | 20 | 5 | 18 | 32 | no |
| hh4 | college_roommates | OK | 1 | 5 | 25 | 6 | 40 | 80 | YES |
| hh5 | remote_worker_couple | OK | 1 | 5 | 15 | 6 | 15 | 50 | YES |
| hh6 | single_parent_teens | OK | 1 | 1 | 27 | 8 | 22 | 44 | no |
| hh7 | multigenerational | OK | 1 | 1 | 43 | 5 | 29 | 65 | no |
| hh8 | shift_worker_couple_opposite | OK | 1 | 1 | 13 | 4 | 19 | 86 | no |
| hh9 | grad_student_solo | OK | 1 | 1 | 9 | 6 | 10 | 25 | no |
| hh10 | frequent_traveler_couple | OK | 1 | 1 | 14 | 5 | 18 | 38 | no |

10/10 households passed every check within 5 program attempts. Leak audit (chance = 1/10): 3 household(s) could not be resampled into an inventory that hides their type — see the README on the closed object vocabulary.

## Realism panel (reporting only, never a gate)

| household | n_events | events_per_day | moves_per_object_day | hour_entropy | daily_fano | twin_pairs | never_move |
|---|---|---|---|---|---|---|---|
| hh_001 | 591 | 28.14 | 1.76 | 0.712 | 2.36 | 4 | 5/16 |
| hh_002 | 700 | 33.33 | 0.93 | 0.809 | 13.03 | 61 | 27/36 |
| hh_003 | 491 | 23.38 | 1.3 | 0.801 | 0.71 | 6 | 10/18 |
| hh_004 | 430 | 20.48 | 0.51 | 0.818 | 13.86 | 36 | 35/40 |
| hh_005 | 699 | 33.29 | 2.22 | 0.852 | 7.37 | 3 | 4/15 |
| hh_006 | 664 | 31.62 | 1.44 | 0.902 | 2.91 | 9 | 12/22 |
| hh_007 | 1089 | 51.86 | 1.79 | 0.877 | 2.06 | 6 | 9/29 |
| hh_008 | 1898 | 90.38 | 4.76 | 0.945 | 4.48 | 1 | 2/19 |
| hh_009 | 1597 | 76.05 | 7.6 | 0.871 | 20.76 | 0 | 0/10 |
| hh_010 | 686 | 32.67 | 1.81 | 0.816 | 5.57 | 0 | 2/18 |
| casas_aruba (REAL, ref) | 1027 | 48.9 | 3.26 | 0.884 | 5.09 | 1 | 1/15 |

Fano in [1, 6]: 5/10 households (expect >= 8/10); hour-entropy >= 0.75: 9/10.

