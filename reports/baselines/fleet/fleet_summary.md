# Fleet health run

One shared config (`src/baselines/configs/fleet.yaml`, hash `7ba2efcf3915…`), seed 0, commit `d57e83fe7342` (dirty tree), run 2026-08-27T00:31:34.529769+00:00.

`diagnostics` = flags in order: stationarity / solvable / not_trivial / not_impossible / discriminative / powered (`.` = not flagged, letter = flagged; flags are advisory, nothing disqualifies). NeverSense columns are passive task accuracy for the frozen panel beliefs.

| household | type | questions | diagnostics | flags | NS last_obs | NS most_freq | NS timetable | search@budget | modal share (time/query) | moves/day |
|---|---|---|---|---|---|---|---|---|---|---|
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh1 | working_professional_solo | 1620 | `S.NN..` | 3 | 0.669 | 0.647 | 0.559 | 0.696 | 0.622/0.596 | 54.9 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh10 | night_shift_worker_solo | 1620 | `..NN..` | 2 | 0.681 | 0.683 | 0.600 | 0.746 | 0.582/0.549 | 51.9 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh2 | working_couple_no_children | 1620 | `...ND.` | 2 | 0.543 | 0.545 | 0.523 | 0.580 | 0.555/0.522 | 105.4 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh3 | retired_couple | 1620 | `S..N..` | 2 | 0.620 | 0.619 | 0.581 | 0.666 | 0.613/0.598 | 105.4 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh4 | family_teen_and_child | 1620 | `...N..` | 1 | 0.493 | 0.485 | 0.438 | 0.531 | 0.538/0.515 | 210.8 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh5 | couple_with_toddler | 1620 | `...N..` | 1 | 0.551 | 0.543 | 0.514 | 0.586 | 0.543/0.531 | 118.3 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh6 | single_parent_teens | 1620 | `...N..` | 1 | 0.499 | 0.494 | 0.433 | 0.543 | 0.513/0.468 | 195.5 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh7 | single_adult_wfh | 1620 | `S.NN..` | 3 | 0.726 | 0.711 | 0.607 | 0.783 | 0.668/0.641 | 51.1 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh8 | remote_worker_couple | 1620 | `S.NN..` | 3 | 0.681 | 0.670 | 0.637 | 0.713 | 0.623/0.622 | 98.6 |
| profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh9 | college_roommates | 1620 | `S..N..` | 2 | 0.643 | 0.636 | 0.597 | 0.686 | 0.653/0.625 | 129.9 |
