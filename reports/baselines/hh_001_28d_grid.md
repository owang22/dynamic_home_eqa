# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh001_28d`

## Provenance

- bank: `banks/baselines/hh_001_28d_uniform.jsonl` (manifest `5521a356974b…`)
- config: `src/baselines/configs/hh_001_28d.yaml` (hash `d00a6acd8ea0…`)
- git commit: `c01cfc4b75a1` (dirty tree)
- seed: 0 · run at 2026-08-11T19:52:53.826358+00:00

**2250 questions** over 25 question-days, 17 distinct objects queried, budget 16/day, 9 agents.

## Headline: accuracy by agent

| agent | task accuracy | budget/question | budget/day |
|---|---|---|---|
| LastObservation+SequentialSearch | 0.811 | 0.18 | 16.00 |
| MostFrequentLocation+SequentialSearch | 0.740 | 0.18 | 16.00 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.692 | 0.18 | 16.00 |
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.673 | 0.03 | 3.00 |
| LastObservation+NeverSense | 0.630 | 0.00 | 0.00 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.630 | 0.03 | 3.00 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.592 | 0.03 | 3.00 |
| MostFrequentLocation+NeverSense | 0.585 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.569 | 0.00 | 0.00 |

## Belief × policy accuracy

| belief \ policy | SequentialSearch | FixedSchedule(k=6.0h,n_rot=4) | NeverSense |
|---|---|---|---|
| LastObservation | 0.811 | 0.673 | 0.630 |
| MostFrequentLocation | 0.740 | 0.630 | 0.585 |
| TimetableLookup(bin=1h,days=all) | 0.692 | 0.592 | 0.569 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | charger | headphones | jacket | keys | medication_bottle | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LastObservation | 0.36 (n=132) | 0.43 (n=137) | 0.84 (n=267) | 0.57 (n=135) | 0.42 (n=128) | 0.76 (n=133) | 0.75 (n=130) | 1.00 (n=130) | 0.51 (n=261) | 0.73 (n=138) | 0.48 (n=134) | 0.56 (n=133) | 0.78 (n=131) | 0.81 (n=127) | 0.39 (n=134) |
| MostFrequentLocation | 0.33 (n=132) | 0.47 (n=137) | 0.75 (n=267) | 0.56 (n=135) | 0.30 (n=128) | 0.66 (n=133) | 0.69 (n=130) | 1.00 (n=130) | 0.42 (n=261) | 0.74 (n=138) | 0.43 (n=134) | 0.49 (n=133) | 0.73 (n=131) | 0.81 (n=127) | 0.39 (n=134) |
| TimetableLookup(bin=1h,days=all) | 0.34 (n=132) | 0.45 (n=137) | 0.74 (n=267) | 0.52 (n=135) | 0.28 (n=128) | 0.62 (n=133) | 0.72 (n=130) | 1.00 (n=130) | 0.38 (n=261) | 0.67 (n=138) | 0.49 (n=134) | 0.48 (n=133) | 0.70 (n=131) | 0.78 (n=127) | 0.39 (n=134) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| book_1 | 0.44 | 1233 |
| headphones_1 | 0.45 | 1152 |
| water_bottle_1 | 0.50 | 1206 |
| blanket_1 | 0.51 | 1188 |
| mug_1 | 0.52 | 1188 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh001_28d/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh001_28d/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh001_28d/run_log.jsonl`
- plots: `smoke_results/baselines_hh001_28d/accuracy_by_agent.png`, `smoke_results/baselines_hh001_28d/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
