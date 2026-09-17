# Fleet health run

One shared config (`src/baselines/configs/cold_start.yaml`, hash `ce8494300439…`), seed 0, commit `606e2eec2464` (dirty tree), run 2026-09-17T00:52:53.691618+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 672 | `S...D.` | 2 | 0.052 | 0.046 | 0.040 | 0.586 | 0.653/0.722 | 39.1 |
| profiles/households/generated/gpt-5.6-terra/hh_002 | multigenerational_family | 672 | `....D.` | 1 | 0.027 | 0.034 | 0.022 | 0.399 | 0.559/0.472 | 124.6 |
| profiles/households/generated/gpt-5.6-terra/hh_003 | single_parent_teens__rotating_shift | 672 | `S...D.` | 2 | 0.033 | 0.021 | 0.021 | 0.515 | 0.633/0.534 | 71.6 |
| profiles/households/generated/gpt-5.6-terra/hh_004 | working_couple_no_children__night_shift | 672 | `S...D.` | 2 | 0.046 | 0.046 | 0.043 | 0.475 | 0.618/0.613 | 100.9 |
| profiles/households/generated/gpt-5.6-terra/hh_005 | working_couple_no_children__opposite_schedules | 672 | `....D.` | 1 | 0.034 | 0.040 | 0.033 | 0.510 | 0.537/0.549 | 64.0 |
| profiles/households/generated/gpt-5.6-terra/hh_006 | working_professional_solo__irregular_gig | 672 | `....D.` | 1 | 0.058 | 0.040 | 0.039 | 0.530 | 0.582/0.571 | 32.3 |
| profiles/households/generated/gpt-5.6-terra/hh_007 | college_roommates | 672 | `....D.` | 1 | 0.046 | 0.037 | 0.031 | 0.451 | 0.594/0.463 | 88.2 |
| profiles/households/generated/gpt-5.6-terra/hh_008 | college_roommates__irregular_gig | 672 | `....D.` | 1 | 0.030 | 0.042 | 0.040 | 0.359 | 0.581/0.540 | 99.8 |
| profiles/households/generated/gpt-5.6-terra/hh_009 | couple_with_toddler | 672 | `....D.` | 1 | 0.037 | 0.025 | 0.024 | 0.369 | 0.542/0.521 | 103.7 |
| profiles/households/generated/gpt-5.6-terra/hh_010 | family_teen_and_child | 672 | `....D.` | 1 | 0.034 | 0.036 | 0.028 | 0.436 | 0.536/0.507 | 128.6 |
| profiles/households/generated/gpt-5.6-terra/hh_011 | remote_worker_couple | 672 | `S...D.` | 2 | 0.031 | 0.037 | 0.042 | 0.531 | 0.669/0.493 | 67.7 |
| profiles/households/generated/gpt-5.6-terra/hh_012 | researcher_household | 672 | `....D.` | 1 | 0.043 | 0.031 | 0.034 | 0.430 | 0.519/0.351 | 41.6 |
| profiles/households/generated/gpt-5.6-terra/hh_013 | retired_couple | 672 | `S...D.` | 2 | 0.021 | 0.034 | 0.025 | 0.506 | 0.648/0.595 | 97.7 |
| profiles/households/generated/gpt-5.6-terra/hh_014 | single_adult_wfh | 672 | `S..ND.` | 3 | 0.054 | 0.062 | 0.037 | 0.199 | 0.718/0.574 | 35.6 |
| profiles/households/generated/gpt-5.6-terra/hh_015 | single_parent_teens | 672 | `....D.` | 1 | 0.028 | 0.019 | 0.034 | 0.461 | 0.554/0.449 | 76.0 |
| profiles/households/generated/gpt-5.6-terra/hh_016 | single_senior_solo | 672 | `S...D.` | 2 | 0.036 | 0.036 | 0.049 | 0.470 | 0.609/0.430 | 48.5 |
| profiles/households/generated/gpt-5.6-terra/hh_017 | working_couple_no_children | 672 | `....D.` | 1 | 0.036 | 0.027 | 0.030 | 0.451 | 0.589/0.430 | 72.3 |
| profiles/households/generated/gpt-5.6-terra/hh_018 | working_couple_no_children | 672 | `....D.` | 1 | 0.039 | 0.030 | 0.036 | 0.463 | 0.590/0.491 | 69.4 |
| profiles/households/generated/gpt-5.6-terra/hh_019 | working_professional_solo | 672 | `S...D.` | 2 | 0.051 | 0.060 | 0.055 | 0.565 | 0.615/0.659 | 52.0 |
| profiles/households/generated/gpt-5.6-terra/hh_020 | working_professional_solo__night_shift | 672 | `S...D.` | 2 | 0.028 | 0.045 | 0.042 | 0.571 | 0.603/0.418 | 40.0 |
