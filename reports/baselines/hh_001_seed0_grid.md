# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh001`

## Provenance

- bank: `banks/baselines/hh_001_seed0_bank.jsonl` (manifest `0d8a4e365a2e…`)
- config: `src/baselines/configs/hh_001.yaml` (hash `e28f5eb8e389…`)
- git commit: `0b42c6430e3e` (dirty tree)
- seed: 0 · run at 2026-08-10T07:28:03.399769+00:00

**44 questions** over 11 question-days, 17 distinct objects queried, budget 2/day, 9 agents.

## Headline: accuracy by agent

| agent | accuracy | budget/question | budget/day |
|---|---|---|---|
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.705 | 0.45 | 1.82 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.659 | 0.45 | 1.82 |
| TimetableLookup(bin=2h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.659 | 0.45 | 1.82 |
| LastObservation+AlwaysSense | 0.614 | 0.50 | 2.00 |
| MostFrequentLocation+AlwaysSense | 0.568 | 0.50 | 2.00 |
| LastObservation+NeverSense | 0.545 | 0.00 | 0.00 |
| MostFrequentLocation+NeverSense | 0.545 | 0.00 | 0.00 |
| TimetableLookup(bin=2h,days=all)+AlwaysSense | 0.545 | 0.50 | 2.00 |
| TimetableLookup(bin=2h,days=all)+NeverSense | 0.523 | 0.00 | 0.00 |

## Belief × policy accuracy

| belief \ policy | FixedSchedule(k=6.0h,n_rot=4) | AlwaysSense | NeverSense |
|---|---|---|---|
| LastObservation | 0.705 | 0.614 | 0.545 |
| MostFrequentLocation | 0.659 | 0.568 | 0.545 |
| TimetableLookup(bin=2h,days=all) | 0.659 | 0.545 | 0.523 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | charger | headphones | jacket | keys | medication_bottle | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LastObservation | 0.50 (n=2) | 0.33 (n=3) | 0.58 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |
| MostFrequentLocation | 0.50 (n=2) | 0.33 (n=3) | 0.58 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |
| TimetableLookup(bin=2h,days=all) | 0.50 (n=2) | 0.33 (n=3) | 0.50 (n=12) | 1.00 (n=1) | 0.25 (n=4) | 0.33 (n=3) | 1.00 (n=3) | 1.00 (n=3) | 0.00 (n=3) | 0.00 (n=1) | 0.00 (n=1) | 0.50 (n=4) | 1.00 (n=1) | 1.00 (n=1) | 1.00 (n=2) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| plate_1 | 0.00 | 9 |
| mug_1 | 0.00 | 9 |
| bowl_2 | 0.24 | 63 |
| book_1 | 0.33 | 27 |
| jacket_marisol | 0.33 | 27 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh001/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh001/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh001/run_log.jsonl`
- plots: `smoke_results/baselines_hh001/accuracy_by_agent.png`, `smoke_results/baselines_hh001/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
