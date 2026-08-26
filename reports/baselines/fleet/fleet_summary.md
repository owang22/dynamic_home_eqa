# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `78b408e9e529…`), seed 0, commit `27ae5272a275` (dirty tree), run 2026-08-25T21:22:22.327590+00:00.

`gates` = the six healthcheck gates in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered. NeverSense columns are passive task accuracy for the frozen panel beliefs. Failing banks are diagnosed in `failures.md`.

| household | type | questions | gates | pass | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/revamp_v1/claude-fable-5/hh1 | night_shift_solo | 1620 | `PPPPPP` | PASS | 0.580 | 0.567 | 0.528 | 0.754 | 0.573/0.525 | 25.4 |
| profiles/revamp_v1/claude-fable-5/hh3 | retired_couple | 1620 | `FPPFFP` | FAIL | 0.614 | 0.614 | 0.619 | 0.631 | 0.685/0.654 | 55.2 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh1 | working_professional_solo | 1620 | `FPPFFP` | FAIL | 0.517 | 0.503 | 0.495 | 0.652 | 0.622/0.596 | 54.9 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh10 | night_shift_worker_solo | 1620 | `PPPPFP` | FAIL | 0.479 | 0.478 | 0.479 | 0.694 | 0.582/0.549 | 51.9 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh2 | working_couple_no_children | 1620 | `PPPFFP` | FAIL | 0.486 | 0.486 | 0.480 | 0.565 | 0.555/0.522 | 105.4 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh3 | retired_couple | 1620 | `FPPFFP` | FAIL | 0.506 | 0.507 | 0.494 | 0.588 | 0.613/0.598 | 105.4 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh4 | family_teen_and_child | 1620 | `PPPFFP` | FAIL | 0.452 | 0.452 | 0.449 | 0.505 | 0.538/0.515 | 210.8 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh5 | couple_with_toddler | 1620 | `PPPFFP` | FAIL | 0.395 | 0.398 | 0.401 | 0.497 | 0.543/0.531 | 118.3 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh6 | single_parent_teens | 1620 | `PPPFFP` | FAIL | 0.419 | 0.419 | 0.423 | 0.456 | 0.513/0.468 | 195.5 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh7 | single_adult_wfh | 1620 | `FPPFFP` | FAIL | 0.591 | 0.594 | 0.578 | 0.717 | 0.668/0.641 | 51.1 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh8 | remote_worker_couple | 1620 | `FPPFFP` | FAIL | 0.538 | 0.541 | 0.531 | 0.678 | 0.623/0.622 | 98.6 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh9 | college_roommates | 1620 | `FPPFFP` | FAIL | 0.567 | 0.567 | 0.563 | 0.660 | 0.653/0.625 | 129.9 |
