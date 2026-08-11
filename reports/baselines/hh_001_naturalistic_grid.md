# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh001_naturalistic`

## Provenance

- bank: `banks/baselines/hh_001_14d_naturalistic.jsonl` (manifest `c8d71c3867b8…`)
- config: `src/baselines/configs/hh_001_naturalistic.yaml` (hash `5e437cea8339…`)
- git commit: `b595fd7fee91` (dirty tree)
- seed: 0 · run at 2026-08-11T02:19:44.150372+00:00

**308 questions** over 11 question-days, 14 distinct objects queried, budget 2/day, 9 agents.

## Headline: accuracy by agent

| agent | task accuracy | budget/question | budget/day |
|---|---|---|---|
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.614 | 0.07 | 2.00 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.581 | 0.07 | 2.00 |
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.555 | 0.07 | 2.00 |
| LastObservation+SequentialSearch | 0.542 | 0.07 | 2.00 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.542 | 0.07 | 2.00 |
| MostFrequentLocation+SequentialSearch | 0.529 | 0.07 | 2.00 |
| LastObservation+NeverSense | 0.500 | 0.00 | 0.00 |
| MostFrequentLocation+NeverSense | 0.500 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.497 | 0.00 | 0.00 |

## Belief × policy accuracy

| belief \ policy | FixedSchedule(k=6.0h,n_rot=4) | SequentialSearch | NeverSense |
|---|---|---|---|
| MostFrequentLocation | 0.614 | 0.529 | 0.500 |
| TimetableLookup(bin=1h,days=all) | 0.581 | 0.542 | 0.497 |
| LastObservation | 0.555 | 0.542 | 0.500 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | headphones | jacket | keys | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MostFrequentLocation | 1.00 (n=2) | 0.61 (n=36) | 0.65 (n=26) | 0.65 (n=26) | 0.71 (n=28) | 1.00 (n=18) | 0.21 (n=62) | 0.62 (n=16) | 0.21 (n=24) | 0.22 (n=9) | 1.00 (n=1) | 1.00 (n=12) | 0.31 (n=48) |
| TimetableLookup(bin=1h,days=all) | 1.00 (n=2) | 0.64 (n=36) | 0.65 (n=26) | 0.65 (n=26) | 0.71 (n=28) | 1.00 (n=18) | 0.18 (n=62) | 0.62 (n=16) | 0.21 (n=24) | 0.22 (n=9) | 1.00 (n=1) | 1.00 (n=12) | 0.31 (n=48) |
| LastObservation | 1.00 (n=2) | 0.61 (n=36) | 0.65 (n=26) | 0.65 (n=26) | 0.71 (n=28) | 1.00 (n=18) | 0.21 (n=62) | 0.62 (n=16) | 0.21 (n=24) | 0.22 (n=9) | 1.00 (n=1) | 1.00 (n=12) | 0.31 (n=48) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| plate_1 | 0.21 | 216 |
| mug_1 | 0.23 | 324 |
| remote_1 | 0.35 | 81 |
| water_bottle_1 | 0.36 | 432 |
| bowl_2 | 0.58 | 234 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh001_naturalistic/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh001_naturalistic/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh001_naturalistic/run_log.jsonl`
- plots: `smoke_results/baselines_hh001_naturalistic/accuracy_by_agent.png`, `smoke_results/baselines_hh001_naturalistic/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
