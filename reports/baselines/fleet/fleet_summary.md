# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `230a2701c4d8` (dirty tree), run 2026-09-09T22:20:18.774883+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 2250 | `...N..` | 1 | 0.611 | 0.612 | 0.534 | 0.660 | 0.539/0.541 | 65.7 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 2250 | `...N..` | 1 | 0.572 | 0.575 | 0.516 | 0.632 | 0.536/0.522 | 154.1 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 2250 | `S.NN..` | 3 | 0.678 | 0.685 | 0.604 | 0.743 | 0.624/0.615 | 95.9 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 2250 | `...ND.` | 2 | 0.528 | 0.537 | 0.516 | 0.632 | 0.591/0.588 | 118.6 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 2250 | `...ND.` | 2 | 0.558 | 0.568 | 0.542 | 0.633 | 0.497/0.505 | 91.2 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 2250 | `...N..` | 1 | 0.573 | 0.577 | 0.487 | 0.621 | 0.510/0.491 | 55.8 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 2250 | `...N..` | 1 | 0.574 | 0.574 | 0.524 | 0.602 | 0.592/0.550 | 130.0 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 2250 | `...N..` | 1 | 0.625 | 0.634 | 0.586 | 0.672 | 0.587/0.566 | 139.0 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 2250 | `...N..` | 1 | 0.586 | 0.590 | 0.532 | 0.647 | 0.564/0.551 | 122.3 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 2250 | `...N..` | 1 | 0.542 | 0.551 | 0.515 | 0.591 | 0.543/0.521 | 158.6 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 2250 | `..NN..` | 2 | 0.681 | 0.679 | 0.587 | 0.770 | 0.595/0.575 | 89.1 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 2250 | `...N..` | 1 | 0.599 | 0.594 | 0.529 | 0.653 | 0.516/0.516 | 61.6 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 2250 | `S.NN..` | 3 | 0.677 | 0.681 | 0.644 | 0.715 | 0.614/0.601 | 119.1 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 2250 | `S.NN..` | 3 | 0.768 | 0.765 | 0.647 | 0.837 | 0.637/0.632 | 48.8 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 2250 | `...N..` | 1 | 0.556 | 0.561 | 0.520 | 0.622 | 0.549/0.512 | 95.6 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 2250 | `S.NN..` | 3 | 0.752 | 0.755 | 0.659 | 0.776 | 0.640/0.636 | 62.0 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 2250 | `...N..` | 1 | 0.604 | 0.611 | 0.580 | 0.646 | 0.559/0.543 | 103.7 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 2250 | `...ND.` | 2 | 0.626 | 0.631 | 0.606 | 0.689 | 0.573/0.564 | 92.0 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 2250 | `...N..` | 1 | 0.632 | 0.630 | 0.550 | 0.669 | 0.554/0.523 | 70.0 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 2250 | `...N..` | 1 | 0.624 | 0.631 | 0.528 | 0.671 | 0.555/0.538 | 56.8 |
