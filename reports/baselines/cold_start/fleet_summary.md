# Fleet health run

One shared config (`src/baselines/configs/cold_start.yaml`, hash `ce8494300439…`), seed 0, commit `de96b5b28863` (dirty tree), run 2026-09-16T06:05:58.654468+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/households/generated/gpt-5.6-terra/hh_001 | working_professional_solo | 672 | `S...D.` | 2 | 0.043 | 0.042 | 0.040 | 0.549 | 0.612/0.671 | 38.6 |
