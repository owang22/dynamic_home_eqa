# Fleet health run

One shared config (`src/baselines/configs/cold_start.yaml`, hash `ce8494300439…`), seed 0, commit `4a1e59dc43c3` (dirty tree), run 2026-09-17T00:21:01.103721+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 672 | `S...D.` | 2 | 0.043 | 0.042 | 0.040 | 0.549 | 0.612/0.671 | 38.6 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 672 | `....D.` | 1 | 0.028 | 0.033 | 0.024 | 0.399 | 0.536/0.494 | 127.7 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 672 | `S...D.` | 2 | 0.028 | 0.034 | 0.036 | 0.330 | 0.633/0.543 | 71.8 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 672 | `....D.` | 1 | 0.033 | 0.042 | 0.036 | 0.473 | 0.568/0.562 | 101.8 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 672 | `....D.` | 1 | 0.040 | 0.037 | 0.037 | 0.479 | 0.502/0.503 | 69.0 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 672 | `....D.` | 1 | 0.045 | 0.043 | 0.042 | 0.571 | 0.557/0.646 | 32.1 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 672 | `....D.` | 1 | 0.043 | 0.040 | 0.039 | 0.455 | 0.596/0.494 | 84.7 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 672 | `....D.` | 1 | 0.040 | 0.025 | 0.024 | 0.374 | 0.557/0.427 | 99.3 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 672 | `....D.` | 1 | 0.036 | 0.031 | 0.024 | 0.356 | 0.547/0.527 | 103.6 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 672 | `....D.` | 1 | 0.040 | 0.033 | 0.030 | 0.439 | 0.534/0.537 | 124.7 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 672 | `S...D.` | 2 | 0.037 | 0.040 | 0.028 | 0.515 | 0.618/0.552 | 65.0 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 672 | `....D.` | 1 | 0.048 | 0.042 | 0.039 | 0.426 | 0.521/0.366 | 41.2 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 672 | `S...D.` | 2 | 0.033 | 0.034 | 0.025 | 0.488 | 0.607/0.507 | 100.0 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 672 | `S...D.` | 2 | 0.051 | 0.060 | 0.040 | 0.327 | 0.674/0.548 | 35.4 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 672 | `....D.` | 1 | 0.028 | 0.025 | 0.028 | 0.455 | 0.531/0.443 | 74.4 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 672 | `S...D.` | 2 | 0.042 | 0.040 | 0.049 | 0.478 | 0.611/0.435 | 47.8 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 672 | `....D.` | 1 | 0.039 | 0.034 | 0.031 | 0.473 | 0.581/0.472 | 72.9 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 672 | `S...D.` | 2 | 0.043 | 0.025 | 0.045 | 0.518 | 0.608/0.490 | 71.0 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 672 | `....D.` | 1 | 0.051 | 0.068 | 0.052 | 0.308 | 0.576/0.543 | 53.9 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 672 | `S...D.` | 2 | 0.030 | 0.049 | 0.036 | 0.500 | 0.604/0.463 | 40.4 |
