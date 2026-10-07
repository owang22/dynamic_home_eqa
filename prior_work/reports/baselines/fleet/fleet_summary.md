# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `633502ee581f…`), seed 0, commit `ea0a371dfb3d` (dirty tree), run 2026-09-13T08:21:08.269527+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2472 | `S.NN..` | 3 | 0.736 | 0.731 | 0.647 | 0.781 | 0.602/0.593 | 40.1 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2350 | `...N..` | 1 | 0.589 | 0.589 | 0.509 | 0.646 | 0.535/0.526 | 135.1 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2398 | `S.NN..` | 3 | 0.714 | 0.703 | 0.619 | 0.767 | 0.632/0.611 | 78.0 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2505 | `S..N..` | 2 | 0.557 | 0.547 | 0.523 | 0.648 | 0.602/0.613 | 106.0 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2446 | `...N..` | 1 | 0.567 | 0.564 | 0.523 | 0.641 | 0.508/0.496 | 69.9 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2468 | `..NN..` | 2 | 0.672 | 0.672 | 0.589 | 0.740 | 0.538/0.542 | 36.0 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2441 | `...N..` | 1 | 0.648 | 0.650 | 0.572 | 0.687 | 0.547/0.533 | 92.0 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2430 | `...N..` | 1 | 0.625 | 0.626 | 0.558 | 0.671 | 0.565/0.551 | 105.5 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2424 | `...N..` | 1 | 0.588 | 0.588 | 0.521 | 0.643 | 0.524/0.510 | 106.9 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2504 | `...N..` | 1 | 0.546 | 0.555 | 0.509 | 0.626 | 0.553/0.540 | 135.9 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2496 | `..NN..` | 2 | 0.709 | 0.706 | 0.617 | 0.785 | 0.591/0.575 | 73.7 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2379 | `..NN..` | 2 | 0.661 | 0.664 | 0.605 | 0.720 | 0.530/0.520 | 45.4 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2367 | `..NN..` | 2 | 0.663 | 0.666 | 0.623 | 0.699 | 0.586/0.556 | 104.8 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2490 | `S.NN..` | 3 | 0.803 | 0.794 | 0.668 | 0.850 | 0.623/0.628 | 38.3 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2442 | `...N..` | 1 | 0.593 | 0.600 | 0.535 | 0.657 | 0.536/0.521 | 84.2 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2347 | `S.NN..` | 3 | 0.770 | 0.767 | 0.665 | 0.792 | 0.638/0.635 | 52.1 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2459 | `...N..` | 1 | 0.645 | 0.642 | 0.594 | 0.699 | 0.545/0.526 | 77.9 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2393 | `..NN..` | 2 | 0.667 | 0.659 | 0.625 | 0.716 | 0.577/0.563 | 76.0 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2343 | `..NN..` | 2 | 0.655 | 0.662 | 0.592 | 0.712 | 0.556/0.531 | 57.5 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2361 | `..NN..` | 2 | 0.703 | 0.696 | 0.589 | 0.743 | 0.521/0.513 | 43.2 |
