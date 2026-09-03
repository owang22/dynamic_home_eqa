# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `9e4120296a86` (dirty tree), run 2026-09-03T05:40:12.639099+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.590 | 0.585 | 0.525 | 0.624 | 0.591/0.556 | 63.7 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.529 | 0.535 | 0.488 | 0.571 | 0.560/0.561 | 152.2 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S.NN..` | 3 | 0.668 | 0.657 | 0.591 | 0.712 | 0.625/0.607 | 96.2 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...N..` | 1 | 0.499 | 0.509 | 0.476 | 0.576 | 0.580/0.595 | 119.3 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...N..` | 1 | 0.535 | 0.526 | 0.503 | 0.632 | 0.508/0.506 | 91.4 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.544 | 0.532 | 0.468 | 0.601 | 0.529/0.512 | 56.1 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.526 | 0.519 | 0.482 | 0.588 | 0.599/0.556 | 130.4 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `...N..` | 1 | 0.571 | 0.569 | 0.531 | 0.623 | 0.595/0.587 | 138.3 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.555 | 0.543 | 0.512 | 0.635 | 0.579/0.558 | 122.0 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.516 | 0.508 | 0.474 | 0.554 | 0.554/0.536 | 158.7 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `S.NN..` | 3 | 0.659 | 0.648 | 0.577 | 0.734 | 0.606/0.588 | 88.2 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.607 | 0.598 | 0.540 | 0.689 | 0.534/0.531 | 60.5 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S..N..` | 2 | 0.622 | 0.619 | 0.592 | 0.663 | 0.650/0.623 | 120.4 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.717 | 0.704 | 0.610 | 0.796 | 0.643/0.634 | 49.0 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.546 | 0.544 | 0.488 | 0.609 | 0.531/0.517 | 94.8 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.741 | 0.728 | 0.619 | 0.767 | 0.628/0.614 | 62.2 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...N..` | 1 | 0.597 | 0.593 | 0.564 | 0.631 | 0.562/0.529 | 101.5 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...N..` | 1 | 0.633 | 0.626 | 0.592 | 0.678 | 0.582/0.590 | 89.2 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.612 | 0.610 | 0.547 | 0.677 | 0.570/0.537 | 68.2 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.621 | 0.612 | 0.518 | 0.733 | 0.571/0.552 | 56.2 |
