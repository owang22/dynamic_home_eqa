# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh001_uniform`

## Provenance

- bank: `banks/baselines/hh_001_14d_uniform.jsonl` (manifest `15c5719aaeab…`)
- config: `src/baselines/configs/hh_001_uniform.yaml` (hash `196d6cdb6b7e…`)
- git commit: `b595fd7fee91` (dirty tree)
- seed: 0 · run at 2026-08-11T02:19:42.436536+00:00

**308 questions** over 11 question-days, 17 distinct objects queried, budget 2/day, 9 agents.

## Headline: accuracy by agent

| agent | task accuracy | budget/question | budget/day |
|---|---|---|---|
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.769 | 0.07 | 2.00 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.766 | 0.07 | 2.00 |
| MostFrequentLocation+SequentialSearch | 0.750 | 0.07 | 2.00 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.740 | 0.07 | 2.00 |
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.734 | 0.07 | 2.00 |
| LastObservation+NeverSense | 0.724 | 0.00 | 0.00 |
| MostFrequentLocation+NeverSense | 0.724 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.724 | 0.00 | 0.00 |
| LastObservation+SequentialSearch | 0.688 | 0.07 | 2.00 |

## Belief × policy accuracy

| belief \ policy | FixedSchedule(k=6.0h,n_rot=4) | SequentialSearch | NeverSense |
|---|---|---|---|
| MostFrequentLocation | 0.769 | 0.750 | 0.724 |
| TimetableLookup(bin=1h,days=all) | 0.766 | 0.740 | 0.724 |
| LastObservation | 0.734 | 0.688 | 0.724 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | charger | headphones | jacket | keys | medication_bottle | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MostFrequentLocation | 1.00 (n=13) | 0.62 (n=16) | 0.90 (n=30) | 1.00 (n=14) | 0.55 (n=29) | 0.81 (n=21) | 1.00 (n=16) | 1.00 (n=20) | 0.32 (n=34) | 0.94 (n=16) | 0.58 (n=19) | 0.24 (n=17) | 1.00 (n=20) | 1.00 (n=26) | 0.18 (n=17) |
| TimetableLookup(bin=1h,days=all) | 1.00 (n=13) | 0.62 (n=16) | 0.90 (n=30) | 1.00 (n=14) | 0.55 (n=29) | 0.81 (n=21) | 1.00 (n=16) | 1.00 (n=20) | 0.32 (n=34) | 0.94 (n=16) | 0.58 (n=19) | 0.24 (n=17) | 1.00 (n=20) | 1.00 (n=26) | 0.18 (n=17) |
| LastObservation | 1.00 (n=13) | 0.62 (n=16) | 0.90 (n=30) | 1.00 (n=14) | 0.55 (n=29) | 0.81 (n=21) | 1.00 (n=16) | 1.00 (n=20) | 0.32 (n=34) | 0.94 (n=16) | 0.58 (n=19) | 0.24 (n=17) | 1.00 (n=20) | 1.00 (n=26) | 0.18 (n=17) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| mug_1 | 0.16 | 153 |
| water_bottle_1 | 0.22 | 153 |
| remote_1 | 0.45 | 153 |
| bowl_2 | 0.51 | 72 |
| headphones_1 | 0.54 | 261 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh001_uniform/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh001_uniform/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh001_uniform/run_log.jsonl`
- plots: `smoke_results/baselines_hh001_uniform/accuracy_by_agent.png`, `smoke_results/baselines_hh001_uniform/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
