# Stage 1c — generator reproducibility & predictability-knob audit (A3)

## Seed determinism: YES, with one documented caveat

Every LLM call in the pipeline carries a derived seed
(`make_seed(household_id, day, stage_tag, occupant_index)`), and the endpoint
client sends it as the vLLM per-request `seed` (`llm_client.py`, masked to
signed-int64). Everything downstream of the LLM is seeded too: Poisson
selection (`selection.py`), clutter seeding, asset-pool draws
(`AssetAllocator`), day scenarios, and the day plan. Two reproducibility tiers:

1. **Bit-exact replay** — the response cache (`--cache-dir`) is keyed by seed;
   re-running the same (seed + config) replays every LLM response byte-for-byte.
   The stage1c cache lives at `/tmp/dynamic-home-eqa-gen-cache-stage1c`; copy it
   somewhere durable if long-term re-runs matter.
2. **Fresh regeneration** — vLLM seeded sampling is deterministic for a fixed
   engine version + kernel config. Across vLLM upgrades or different GPUs,
   sampling may drift. So (seed + config) A/B comparisons are valid when run
   against the same serving stack, which is the intended B6 usage.

Verdict: the A/B precondition for the causal predictability experiment is met —
same seed + same layout + same serving stack differ only by the knob under test.

## Knob status

| knob | status | notes |
|---|---|---|
| `n_days`, `seed`, `n_persona_types` | EXISTS | `--n-days`, seeds derived from household id, `--n-variants` / `--profile` |
| calendar day types | **IMPLEMENTED this round** | `--calendar-days`: day 0 = Monday, days 5/6 weekend; day-of-week shown to the planner ("weekday (Tuesday)"); cache-tag separated from pool-draw mode. Without it, day_type was a seeded pool draw — day 5 was NOT Saturday and generated data contained no weekly periodicity at all. |
| `schedule_jitter_min` | NOT IMPLEMENTED (flagged) | The primary predictability knob. Feasible as a seeded truncated-normal shift on each selected displacement's time within its activity window, applied BEFORE the replay-gate preflight (pipeline.py, between judge selection and `_preflight_replay_gates`) so gates re-validate jittered times. Does not touch LLM sampling. |
| `destination_entropy` | NOT IMPLEMENTED (flagged) | Requires the human-authored frozen per-(activity, object) destination categorical first (LLM may seed the table once; then it is inspected and frozen under `data/`). Temperature is then applied at manifest build in place of the LLM's destination choice. Largest of the three; do not approximate it with LLM sampling temperature (unreproducible across model versions — brief's explicit warning). |
| `activity_dropout_p` | NOT IMPLEMENTED (flagged) | Cheap: seeded per-(occupant, day, activity) Bernoulli drop applied to the accepted activity trace before displacement proposal. Occurrence-irregularity knob, orthogonal to timing jitter. |

## Stage1c data expansion actually launched

4 households / 3 scenes / 3 persona types × 35 calendar days each (5 full
weeks → 5 instances of every day-of-week, satisfying the weekly-component
gate of ≥4):

| scene | profile |
|---|---|
| 102344049 | family_with_kids |
| 102344049 | retired_couple |
| 102343992 | single_parent_young_kids |
| 102344022 | roommates_shared_house |

Protocol held fixed to stage1b: Qwen/Qwen3.6-35B-A3B via endpoint,
`--judge-style strict`, default activity scale; the ONLY generation-behavior
change is `--calendar-days` (required for Section C to be meaningful).
Manifests land in `generation_out_stage1c/<scene>_<profile>[_dayN]/`
(`manifest.json` + `generation_result.json` per day).
