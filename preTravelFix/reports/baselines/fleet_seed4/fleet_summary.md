# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `9e4120296a86` (dirty tree), run 2026-09-03T06:15:44.795587+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.607 | 0.600 | 0.556 | 0.638 | 0.571/0.547 | 62.4 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.547 | 0.548 | 0.494 | 0.584 | 0.541/0.524 | 153.2 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S..N..` | 2 | 0.638 | 0.625 | 0.564 | 0.685 | 0.613/0.597 | 97.2 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...ND.` | 2 | 0.512 | 0.512 | 0.493 | 0.592 | 0.596/0.592 | 118.6 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...ND.` | 2 | 0.513 | 0.508 | 0.491 | 0.614 | 0.477/0.486 | 93.1 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.568 | 0.557 | 0.493 | 0.649 | 0.533/0.536 | 56.2 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.527 | 0.513 | 0.471 | 0.572 | 0.581/0.548 | 132.0 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `...N..` | 1 | 0.556 | 0.552 | 0.501 | 0.596 | 0.591/0.566 | 141.1 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.589 | 0.584 | 0.540 | 0.645 | 0.575/0.557 | 122.0 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.514 | 0.521 | 0.474 | 0.553 | 0.544/0.546 | 160.0 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `..NN..` | 2 | 0.667 | 0.655 | 0.581 | 0.739 | 0.590/0.582 | 89.2 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.587 | 0.580 | 0.518 | 0.676 | 0.529/0.515 | 60.5 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S..N..` | 2 | 0.640 | 0.632 | 0.597 | 0.678 | 0.625/0.598 | 123.4 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.743 | 0.727 | 0.639 | 0.810 | 0.638/0.627 | 48.2 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.564 | 0.560 | 0.508 | 0.614 | 0.559/0.519 | 95.7 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.739 | 0.724 | 0.633 | 0.752 | 0.639/0.636 | 60.6 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...N..` | 1 | 0.595 | 0.594 | 0.560 | 0.619 | 0.569/0.559 | 101.5 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...ND.` | 2 | 0.611 | 0.610 | 0.587 | 0.680 | 0.597/0.576 | 90.1 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.639 | 0.631 | 0.568 | 0.679 | 0.593/0.559 | 69.0 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.611 | 0.596 | 0.509 | 0.709 | 0.550/0.496 | 56.2 |
