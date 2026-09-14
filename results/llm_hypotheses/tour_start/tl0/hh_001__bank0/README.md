# hh_001, timeline seed 0, bank seed 0 — graph arm vs flat arm vs baselines

Run 2026-09-13 on the re-realized world (owner-room drift + per-resident
forgetfulness) with the re-exported bank and a re-realized oracle ensemble.
Model: Qwen/Qwen3.8-27B served locally. Scoring merges ON_PERSON with
OUT_OF_HOUSE. 2472 questions per arm.

## Layout

- `figures/` — everything to look at. `tables.md` holds every number with
  standard errors and paired bootstrap CIs.
- `arms/<protocol>__<belief>[__<condition>][__f<frac>][__b<beta>]/` — one
  folder per arm: `per_question.jsonl.gz` (truth, mixture distribution, each
  particle's distribution, senses), `diagnostics.json` (re-ask events, graph
  traces, final weights, assumption recovery), `provenance.json`, and for
  re-asking arms `revisions/` with every LLM exchange.

Arm-name tokens: `passive` = fixed patrol, no sensing; `active` = the robot
senses under a value-of-information policy with a 24-sense daily budget.
`llm` / `graph` = re-asking (LLM called mid-episode); `llm_fixed` /
`graph_fixed` = the tour-elicited set is never revised, though weights and
per-hypothesis numbers still update from sightings. `f0` = myopic VoI;
`f0.1` = 10% of the budget spent on random senses; `b<beta>` = the
assumption-targeted policy at that beta (`f` is ignored; `b0` equals `f0`
up to the RNG stream). `mostfreq72` is the no-LLM comparison arm and the
mixture's own statistical particle.

## Headline (top-1, ± one SE ≈ 0.009 passive, 0.008 active)

| arm | passive | active f0 |
|---|---|---|
| most-frequent 72 h (no LLM) | 0.721 | 0.784 |
| oracle (routine posterior, re-realized) | 0.758 | 0.797 |
| flat LLM, fixed set | 0.715 | 0.777 |
| flat LLM, re-asking | 0.701 | 0.776 |
| graph LLM, fixed set | 0.713 | 0.809 |
| graph LLM, re-asking | 0.728 | 0.811 |

Late-discovered objects (first sighted after day 0; 698 questions) are the
stratum that separates the arms: passive graph re-asking 0.532 vs flat
re-asking 0.476 vs most-frequent 0.477 vs oracle 0.632; active graph 0.66
vs flat 0.55–0.58. Tour-visible objects sit at 0.80–0.87 for everyone.

## What happened in the graph arm

- Named elicitation: 3 assumptions (weekday presence, weekend activity,
  suitcase status), 8 leaves, no repair round, 895 s. Anonymized: household
  size, weekday presence, evening meal; 8 leaves; 925 s.
- Re-asking fired only on the scheduled days 3 and 7 (the uncovered-bank
  trigger never fired: every new class was already modeled). On day 3 the
  model dropped the four `home_desk` leaves; on day 7 it dropped three more,
  leaving ONE leaf for the remaining three weeks. Weekday presence was
  settled by sightings; the other two assumptions were settled by deletion,
  not by evidence. Automatic pruning and value births never ran.
- The assumption-targeted policies (`b0.5`, `b2`) are therefore untested in
  practice: run on the fixed set, they had eight live leaves but the
  relevance-weighted bonus barely moved decisions (0.802–0.804 vs 0.802 at
  `b0`).
- Assumption recovery: work pattern recovered in every graph arm
  (`weekday_presence=out`); composition recovered only in the anonymized
  graph (`household_size=one_adult`). Flat arms score 0 by construction.

## Timing (generation seconds, live)

| | graph LLM | flat LLM |
|---|---|---|
| elicitation named / anonymized | 895 / 925 | 612 / 384 |
| passive re-asking episode | 849 (2 calls) | 1591 (3 calls) |
| active re-asking episode (f0) | 923 (2 calls) | 1863 (3 calls) |
| fixed-set episode passive / active | 6 / 33 | 6 / 38 |

## Caveats

- One household, one seed: every LLM-vs-LLM gap in the passive block is
  inside two standard errors; only the active graph arms and the
  late-discovery stratum separate clearly.
- The flat arm's re-asking now includes the uncovered-bank trigger (fired
  on day 0 in every flat arm); pass `--no-new-class-trigger` to reproduce
  the older trigger set.
- `mug_shared_1` sits in the dish rack 69% of the episode because the
  program attaches it to no daily kitchen activity and the one put-away on
  day 5 drew the 10% "left in the rack" branch. The oracle disagrees with
  that world by design (19% of realizations share it).
