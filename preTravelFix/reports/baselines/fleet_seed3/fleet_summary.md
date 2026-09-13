# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `9e4120296a86` (dirty tree), run 2026-09-03T06:06:16.946578+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.599 | 0.593 | 0.541 | 0.635 | 0.562/0.549 | 64.9 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.559 | 0.560 | 0.515 | 0.604 | 0.567/0.546 | 153.6 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S.NN..` | 3 | 0.660 | 0.649 | 0.580 | 0.710 | 0.629/0.625 | 95.7 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...ND.` | 2 | 0.490 | 0.493 | 0.466 | 0.580 | 0.575/0.575 | 118.9 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...ND.` | 2 | 0.527 | 0.526 | 0.506 | 0.631 | 0.505/0.512 | 91.4 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.571 | 0.558 | 0.498 | 0.629 | 0.522/0.508 | 56.3 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.529 | 0.515 | 0.471 | 0.578 | 0.593/0.549 | 129.7 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `S..N..` | 2 | 0.592 | 0.582 | 0.535 | 0.638 | 0.605/0.592 | 139.4 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.564 | 0.556 | 0.504 | 0.631 | 0.542/0.524 | 121.4 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.515 | 0.506 | 0.472 | 0.558 | 0.534/0.510 | 157.9 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `..NN..` | 2 | 0.680 | 0.668 | 0.588 | 0.752 | 0.591/0.573 | 87.4 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.585 | 0.576 | 0.519 | 0.680 | 0.544/0.517 | 61.1 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S..N..` | 2 | 0.641 | 0.634 | 0.599 | 0.686 | 0.644/0.650 | 121.9 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.750 | 0.744 | 0.654 | 0.820 | 0.665/0.671 | 48.2 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.546 | 0.537 | 0.477 | 0.609 | 0.553/0.543 | 95.1 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.752 | 0.740 | 0.647 | 0.775 | 0.652/0.660 | 62.1 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...N..` | 1 | 0.583 | 0.586 | 0.548 | 0.598 | 0.575/0.568 | 102.2 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...N..` | 1 | 0.609 | 0.605 | 0.572 | 0.652 | 0.573/0.544 | 90.2 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.615 | 0.606 | 0.523 | 0.670 | 0.562/0.527 | 68.6 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.623 | 0.608 | 0.550 | 0.712 | 0.572/0.544 | 56.9 |
