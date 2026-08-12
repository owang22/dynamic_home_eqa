# Baselines rundown — hh_001

Run directory: `smoke_results/baselines_hh1_21d`

## Provenance

- bank: `banks/baselines/hh1_21d_uniform.jsonl` (manifest `f8aeb6e26bf0…`)
- config: `src/baselines/configs/hh1_21d.yaml` (hash `54e7fda6d18a…`)
- git commit: `5019dd9c8a60` (dirty tree)
- seed: 0 · run at 2026-08-12T00:16:34.705013+00:00

**1620 questions** over 18 question-days, 17 distinct objects queried, budget 24/day, 9 agents.

## Headline: accuracy by agent

| agent | task accuracy | budget/question | budget/day |
|---|---|---|---|
| LastObservation+SequentialSearch | 0.754 | 0.27 | 24.00 |
| MostFrequentLocation(hl=24h)+SequentialSearch | 0.732 | 0.27 | 24.00 |
| TimetableLookup(bin=1h,days=all,hl=24h)+SequentialSearch | 0.691 | 0.27 | 24.00 |
| MostFrequentLocation(hl=24h)+FixedSchedule(k=6.0h,n_rot=4) | 0.593 | 0.04 | 3.28 |
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.584 | 0.04 | 3.28 |
| LastObservation+NeverSense | 0.580 | 0.00 | 0.00 |
| MostFrequentLocation(hl=24h)+NeverSense | 0.567 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all,hl=24h)+FixedSchedule(k=6.0h,n_rot=4) | 0.535 | 0.04 | 3.28 |
| TimetableLookup(bin=1h,days=all,hl=24h)+NeverSense | 0.528 | 0.00 | 0.00 |

## Belief × policy accuracy

| belief \ policy | SequentialSearch | FixedSchedule(k=6.0h,n_rot=4) | NeverSense |
|---|---|---|---|
| LastObservation | 0.754 | 0.584 | 0.580 |
| MostFrequentLocation(hl=24h) | 0.732 | 0.593 | 0.567 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.691 | 0.535 | 0.528 |

## Per object class, pure belief (NeverSense)

| belief \ class | blanket | book | bowl | charger | headphones | jacket | keys | medication_bottle | mug | phone | plate | remote | umbrella | wallet | water_bottle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LastObservation | 0.57 (n=97) | 0.52 (n=95) | 0.69 (n=189) | 1.00 (n=94) | 0.55 (n=97) | 0.35 (n=94) | 0.23 (n=98) | 1.00 (n=94) | 0.61 (n=191) | 0.48 (n=94) | 0.65 (n=94) | 0.48 (n=96) | 0.67 (n=96) | 0.49 (n=94) | 0.29 (n=97) |
| MostFrequentLocation(hl=24h) | 0.57 (n=97) | 0.51 (n=95) | 0.69 (n=189) | 1.00 (n=94) | 0.55 (n=97) | 0.37 (n=94) | 0.23 (n=98) | 1.00 (n=94) | 0.58 (n=191) | 0.37 (n=94) | 0.61 (n=94) | 0.48 (n=96) | 0.65 (n=96) | 0.49 (n=94) | 0.29 (n=97) |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.54 (n=97) | 0.48 (n=95) | 0.70 (n=189) | 1.00 (n=94) | 0.47 (n=97) | 0.36 (n=94) | 0.24 (n=98) | 1.00 (n=94) | 0.46 (n=191) | 0.41 (n=94) | 0.37 (n=94) | 0.46 (n=96) | 0.55 (n=96) | 0.49 (n=94) | 0.29 (n=97) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| keys_marisol | 0.36 | 882 |
| water_bottle_1 | 0.41 | 873 |
| jacket_marisol | 0.45 | 846 |
| bowl_2 | 0.46 | 837 |
| wallet_marisol | 0.49 | 846 |

## Artifacts

- per-question rows: `smoke_results/baselines_hh1_21d/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_hh1_21d/aggregate.csv`
- run log (replayable): `smoke_results/baselines_hh1_21d/run_log.jsonl`
- plots: `smoke_results/baselines_hh1_21d/accuracy_by_agent.png`, `smoke_results/baselines_hh1_21d/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
