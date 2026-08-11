# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh001`

## Provenance

- bank: `banks/baselines/hh_001_seed0_bank.jsonl` (manifest `0d8a4e365a2e…`)
- config: `src/baselines/configs/hh_001.yaml` (hash `458c8ae5d205…`)
- git commit: `b595fd7fee91` (dirty tree)
- seed: 0 · run at 2026-08-11T02:19:40.706115+00:00

**44 questions** over 11 question-days, 17 distinct objects queried, budget 2/day, 9 agents.

## Headline: accuracy by agent

| agent | task accuracy | budget/question | budget/day |
|---|---|---|---|
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.659 | 0.45 | 1.82 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.636 | 0.45 | 1.82 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.636 | 0.45 | 1.82 |
| LastObservation+SequentialSearch | 0.614 | 0.50 | 2.00 |
| MostFrequentLocation+SequentialSearch | 0.591 | 0.50 | 2.00 |
| LastObservation+NeverSense | 0.545 | 0.00 | 0.00 |
| MostFrequentLocation+NeverSense | 0.545 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.545 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.545 | 0.50 | 2.00 |

## Belief × policy accuracy

| belief \ policy | FixedSchedule(k=6.0h,n_rot=4) | SequentialSearch | NeverSense |
|---|---|---|---|
| LastObservation | 0.659 | 0.614 | 0.545 |
| MostFrequentLocation | 0.636 | 0.591 | 0.545 |
| TimetableLookup(bin=1h,days=all) | 0.636 | 0.545 | 0.545 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | charger | headphones | jacket | keys | medication_bottle | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LastObservation | 0.50 (n=2) | 0.33 (n=3) | 0.58 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |
| MostFrequentLocation | 0.50 (n=2) | 0.33 (n=3) | 0.58 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |
| TimetableLookup(bin=1h,days=all) | 0.50 (n=2) | 0.33 (n=3) | 0.58 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| plate_1 | 0.00 | 9 |
| mug_1 | 0.00 | 9 |
| book_1 | 0.26 | 27 |
| headphones_1 | 0.31 | 36 |
| jacket_marisol | 0.33 | 27 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh001/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh001/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh001/run_log.jsonl`
- plots: `smoke_results/baselines_hh001/accuracy_by_agent.png`, `smoke_results/baselines_hh001/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
