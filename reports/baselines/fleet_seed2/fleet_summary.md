# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `9e4120296a86` (dirty tree), run 2026-09-03T05:49:36.877737+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.586 | 0.580 | 0.528 | 0.640 | 0.563/0.547 | 64.4 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.549 | 0.553 | 0.497 | 0.588 | 0.543/0.525 | 152.8 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S.NN..` | 3 | 0.653 | 0.650 | 0.578 | 0.702 | 0.630/0.615 | 93.9 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...ND.` | 2 | 0.492 | 0.500 | 0.475 | 0.569 | 0.584/0.605 | 118.8 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...N..` | 1 | 0.511 | 0.512 | 0.474 | 0.618 | 0.499/0.499 | 91.0 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.548 | 0.532 | 0.464 | 0.619 | 0.527/0.505 | 55.6 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.522 | 0.508 | 0.473 | 0.591 | 0.564/0.524 | 130.6 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `...N..` | 1 | 0.592 | 0.587 | 0.521 | 0.633 | 0.588/0.585 | 138.8 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.584 | 0.576 | 0.528 | 0.640 | 0.553/0.522 | 120.0 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.517 | 0.513 | 0.470 | 0.549 | 0.539/0.516 | 157.8 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `..NN..` | 2 | 0.674 | 0.663 | 0.580 | 0.752 | 0.580/0.558 | 88.2 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.582 | 0.564 | 0.512 | 0.675 | 0.531/0.511 | 61.8 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S..N..` | 2 | 0.629 | 0.624 | 0.594 | 0.663 | 0.641/0.635 | 120.6 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.756 | 0.732 | 0.639 | 0.824 | 0.658/0.651 | 49.2 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.563 | 0.550 | 0.506 | 0.603 | 0.559/0.543 | 94.6 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.728 | 0.717 | 0.624 | 0.752 | 0.633/0.617 | 61.7 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...N..` | 1 | 0.568 | 0.566 | 0.534 | 0.599 | 0.567/0.545 | 102.0 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...N..` | 1 | 0.619 | 0.616 | 0.579 | 0.672 | 0.561/0.536 | 89.1 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.621 | 0.613 | 0.520 | 0.681 | 0.577/0.538 | 68.7 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.616 | 0.604 | 0.516 | 0.733 | 0.545/0.497 | 57.9 |
