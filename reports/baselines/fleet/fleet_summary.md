# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `9e4120296a86` (dirty tree), run 2026-08-30T00:30:10.677891+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.592 | 0.585 | 0.510 | 0.630 | 0.539/0.541 | 65.7 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.549 | 0.544 | 0.480 | 0.591 | 0.536/0.522 | 154.1 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S..N..` | 2 | 0.648 | 0.644 | 0.568 | 0.716 | 0.624/0.615 | 95.9 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...ND.` | 2 | 0.491 | 0.491 | 0.472 | 0.572 | 0.591/0.588 | 118.6 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...ND.` | 2 | 0.529 | 0.525 | 0.507 | 0.629 | 0.497/0.505 | 91.2 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.549 | 0.544 | 0.473 | 0.629 | 0.510/0.491 | 55.8 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.524 | 0.525 | 0.480 | 0.575 | 0.592/0.550 | 130.0 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `...N..` | 1 | 0.575 | 0.571 | 0.527 | 0.620 | 0.587/0.566 | 139.0 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.552 | 0.545 | 0.497 | 0.601 | 0.564/0.551 | 122.3 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.511 | 0.518 | 0.482 | 0.545 | 0.543/0.521 | 158.6 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `..NN..` | 2 | 0.661 | 0.648 | 0.573 | 0.740 | 0.595/0.575 | 89.1 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.585 | 0.569 | 0.519 | 0.673 | 0.516/0.516 | 61.6 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S.NN..` | 3 | 0.655 | 0.649 | 0.620 | 0.682 | 0.614/0.601 | 119.1 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.741 | 0.728 | 0.624 | 0.812 | 0.637/0.632 | 48.8 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.529 | 0.524 | 0.472 | 0.595 | 0.549/0.512 | 95.6 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.740 | 0.728 | 0.643 | 0.764 | 0.640/0.636 | 62.0 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...ND.` | 2 | 0.568 | 0.573 | 0.545 | 0.600 | 0.559/0.543 | 103.7 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...N..` | 1 | 0.623 | 0.616 | 0.591 | 0.662 | 0.573/0.564 | 92.0 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.619 | 0.607 | 0.532 | 0.664 | 0.554/0.523 | 70.0 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.598 | 0.578 | 0.497 | 0.704 | 0.555/0.538 | 56.8 |
