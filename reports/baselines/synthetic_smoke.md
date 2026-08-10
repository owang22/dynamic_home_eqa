# Baselines rundown — synthetic_hh

Run directory: `smoke_results/baselines_smoke`

## Provenance

- bank: `smoke_results/baselines_smoke/synthetic_bank.jsonl` (manifest `dc3ae19450db…`)
- config: `src/baselines/configs/smoke.yaml` (hash `e47b727f8bf7…`)
- git commit: `0b42c6430e3e` (dirty tree)
- seed: 0 · run at 2026-08-10T05:22:46.721685+00:00

**12 questions** over 3 question-days, 3 distinct objects queried, budget 2/day, 9 agents.

## Headline: accuracy by agent

| agent | accuracy | budget/question | budget/day |
|---|---|---|---|
| LastObservation+AlwaysSense | 0.750 | 0.50 | 2.00 |
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.750 | 0.50 | 2.00 |
| LastObservation+NeverSense | 0.750 | 0.00 | 0.00 |
| TimetableLookup(bin=1h,days=all)+AlwaysSense | 0.750 | 0.50 | 2.00 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.750 | 0.50 | 2.00 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.750 | 0.00 | 0.00 |
| MostFrequentLocation+AlwaysSense | 0.500 | 0.50 | 2.00 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.500 | 0.50 | 2.00 |
| MostFrequentLocation+NeverSense | 0.500 | 0.00 | 0.00 |

## Belief × policy accuracy

| belief \ policy | AlwaysSense | FixedSchedule(k=6.0h,n_rot=4) | NeverSense |
|---|---|---|---|
| LastObservation | 0.750 | 0.750 | 0.750 |
| TimetableLookup(bin=1h,days=all) | 0.750 | 0.750 | 0.750 |
| MostFrequentLocation | 0.500 | 0.500 | 0.500 |

## Per object class, pure belief (NeverSense)

| belief \ class | keys | laptop | mug |
|---|---|---|---|
| LastObservation | 0.50 (n=6) | 1.00 (n=3) | 1.00 (n=3) |
| TimetableLookup(bin=1h,days=all) | 1.00 (n=6) | 0.00 (n=3) | 1.00 (n=3) |
| MostFrequentLocation | 0.50 (n=6) | 0.00 (n=3) | 1.00 (n=3) |

## Hardest objects (accuracy across all agents)

| object | accuracy | answers |
|---|---|---|
| laptop_mover | 0.33 | 27 |
| keys_periodic | 0.67 | 54 |
| mug_static | 1.00 | 27 |

## Artifacts

- per-question rows: `smoke_results/baselines_smoke/questions.csv`
- aggregates (incl. per-day strata): `smoke_results/baselines_smoke/aggregate.csv`
- run log (replayable): `smoke_results/baselines_smoke/run_log.jsonl`
- plots: `smoke_results/baselines_smoke/accuracy_by_agent.png`, `smoke_results/baselines_smoke/accuracy_by_day.png`
- interactive: `/visualization/viewer/beliefs.html` (belief-vs-truth overlay on the household map)
