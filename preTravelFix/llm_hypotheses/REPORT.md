# LLM hypothesis belief — first-version results (2 households)

**Scoring note (2026-09-12).** `ON_PERSON` and `OUT_OF_HOUSE` are scored as ONE location
(`baselines.passive_eval.AWAY_EQUIVALENCE`). The bank labels an object carried by a resident
inside the house `ON_PERSON` and one that has left with them `OUT_OF_HOUSE`, but the robot
never sights anything at either (0 sightings in 168 room visits per household), so no belief
can learn the difference; under exact match, which label a statistical model produced on the
15–18% of questions whose truth is "away" was decided by its floor-mass tie-break — list
order — and MostFrequent was scored wrong on 147 such questions purely for that. The first
run's exact-match results are preserved in `eval_exact_match_v1/`; every number below is
regenerated under the merged rule. Repo-wide default is still exact match (opt-in field).

Stop point per the brief: converter verified on hand-written hypotheses, benchmark run on
two households under named and anonymized conditions, plain-statistical-only comparison
included. No households added, no re-asking loop, no prompt tuning beyond valid output.

**Two households, one bank seed, one elicitation each — early, not to be read into deeply.**

## Headline (both households, 4,500 questions, paired bootstrap CIs)

| arm | top-1 | log-loss | brier | search steps | recall@3 | ECE |
|---|---|---|---|---|---|---|
| OracleBelief (ceiling) | **0.739** | **0.739** | **0.354** | **1.51** | 0.944 | — |
| LLM named (decay 0.99) | 0.592 | 1.466 | 0.586 | 2.55 | 0.901 | — |
| LLM named, decay 1.0 | 0.580 | 1.515 | 0.603 | 2.59 | — | — |
| LLM anonymized | 0.554 | 1.562 | 0.621 | 2.60 | 0.892 | — |
| MostFrequent (24 h) | 0.618 | 1.710 | 0.620 | 3.20 | 0.862 | — |
| PeriodicPersistence — the no-LLM arm | 0.604 | 2.104 | 0.706 | 3.11 | — | — |

(Full columns in `eval/metrics.csv`.)

Paired differences, LLM named − PeriodicPersistence (the mixture's statistical particle alone):

| metric | difference | 95% CI |
|---|---|---|
| top-1 | −0.012 | [−0.025, +0.002] — not significant |
| log-loss | −0.638 nats | [−0.691, −0.585] |

LLM named − MostFrequent: top-1 −0.026 [−0.039, −0.012]; log-loss −0.244 [−0.273, −0.214].

## What the LLM contributed

**A much better distribution; no detectable argmax gain, and a real argmax loss to MostFrequent.**
The LLM mixture cuts log-loss by 0.64 nats against the no-LLM arm, takes expected search cost
from 3.1 to 2.55 receptacles, and lifts recall@3 from 0.86 (MostFreq) to 0.90. On top-1 it is
indistinguishable from Periodic and 2.6 points behind MostFrequent, which is the best top-1
arm at 0.618. The mixture averages over hypotheses that disagree — that is what makes its
tail honest, and it costs at the mode.

**The statistical particle never carries weight.** `periodic_persistence` holds 0.000 weight
in every run, every week (`weight_trajectories.png` — unchanged by the scoring fix, since
weights depend on sighting likelihood, not on question scoring). On sighting likelihood the
LLM descriptions beat the statistical model outright.

**The ceiling is far away.** OracleBelief leads by 14.6 top-1 points and 0.73 nats.

## Named vs anonymized — no clean evidence that names help

Pooled, named beats anonymized by +3.8 top-1 points and 0.096 nats, CIs excluding zero. But:

- **hh_001** (both conditions elicited through the same thinking path): +0.3 points, CI
  [−1.0, +1.6]; log-loss CI [−0.04, +0.02]. **A wash.**
- **hh_002** (+7.3 points): the anonymized hypotheses came from the **salvage path** —
  three thinking calls failed to serialize valid JSON and the guided-JSON, no-thinking
  fallback produced them. Named vs anonymized on hh_002 is confounded with thinking vs
  no-thinking elicitation.

A mechanism the recapture exposed: the anonymized hypotheses almost never send anything out
of the house (3 `OUT_OF_HOUSE` moves on hh_001, zero on hh_002, vs 51 and 64 named). Under
anonymization the model has no semantic reason to believe `object_7` leaves with a person.
That is real knowledge the names carry — but on hh_002 it is inseparable from the path
confound. Measuring this properly needs hh_002 anonymized through the same path as named.

## Decay — the hedge pays, and the mechanism is visible

Tempered 0.99 beats the pure posterior 1.0 on every metric, on both households, CIs
excluding zero (+1.2 top-1 points, −0.049 nats pooled). `weight_trajectories.png` shows why:
at decay 1.0 hh_001 locks onto h1 by day 6 and never moves; at 0.99 the same mixture hands
over to h5 in week 4 when the household's routine shifts.

## Learning curve

Every non-oracle arm degrades over the episode (the households drift: hh_001 has a scripted
sick week and visitor arc). The LLM named arm holds log-loss flat (~1.5) while Periodic's
climbs; on top-1 it trails the statistical baselines in every history bucket, including the
first. No early-history advantage at the argmax. `accuracy_over_time.png` (95% CI bands on
each 3-day window: the top-1 bands of the LLM and statistical arms overlap almost
everywhere), `learning_curve.md`.

## Hypotheses produced

20/20 valid across 4 conditions, 0 dropped, 0 ID-repair rounds. The vocabulary-table
scaffolding held. hh_001 named produced five genuinely competing accounts (works from
kitchen table / commutes out / works in living room / everything-returned / mostly absent),
each with a concrete distinguishing prediction and full 35-object rest coverage. The
mixture picked h1 (kitchen-table WFH) — which is *more right about the laptop* than the
commute hypotheses, since Mara's laptop stays home; the LLM's commute hypotheses wrongly
took it out with her. Sightings settled it.

## Cost — Qwen3.8-27B on vllm, single stream ~28 tok/s

| condition | calls | output tokens | generation | per hypothesis |
|---|---|---|---|---|
| hh_001 named | 1 | 20,323 | 728 s | 146 s |
| hh_001 anonymized | 1 | 29,760 | 1,072 s | 214 s |
| hh_002 named | 1 | 39,084 | 1,416 s | 283 s |
| hh_002 anonymized | 4 (3 failed + salvage) | 126,455 | 4,581 s | 916 s |

6 live calls, 7,068 s. Anonymized runs reason ~46% longer than named on the same household.
The 60-object household is at the edge of one-pass serialization: two of hh_002 anonymized's
failures were `finish_reason=stop` with the JSON cut off mid-object.

Generation settings that mattered: `max_tokens` 40,000 with the server at 65,536 context.
`reasoning_effort` (medium vs low) barely changed output volume (73.9k vs 77.2k chars).

## Files

- `eval/` — regenerated under merged scoring: `metrics.csv`, `summary.md`, `learning_curve.{csv,md}`, `per_question.csv.gz`, `provenance.json` (records the rule)
- `eval_exact_match_v1/` — the first run, exact-match scoring, kept for comparison (+ `per_question_dists.jsonl.gz`, every arm's full per-question distribution)
- `eval/accuracy_over_time.png`, `eval/weight_trajectories.png` (+ `weight_trajectories.json`)
- `eval/scores_by_model.png`, `eval/recall_at_k.png`, `eval/calibration.png` (standard benchmark outputs)
- `hypotheses/{named,anonymized}/hh_00{1,2}.json` — what the beliefs loaded
- `logs/{named,anonymized}/hh_00{1,2}.json` — prompts, think traces, raw payloads, per-call timing
- `anonymization/hh_00{1,2}.{md,json}` — token ↔ real-id cross-reference
- `generation_cost.json`

## Viewer

`python visualization/serve.py` → belief-vs-truth at http://127.0.0.1:8711/ ; hh_001 and hh_002
traces include `LLMHyp(named)`, `LLMHyp(anonymized)`, `LLMHyp(named,decay=1.0)` and
`OracleBelief` next to the statistical panel. The viewer's correctness check applies the same
`ON_PERSON ≡ OUT_OF_HOUSE` rule.

## Not done (per the brief's stop point)

More households; re-asking when descriptions stop matching; resident personas; prompt tuning.
Recommended next before any of those: make the anonymized condition elicit through the same
path as named on hh_002 so the naming measurement is clean.
