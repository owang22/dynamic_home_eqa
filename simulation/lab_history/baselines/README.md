# Baselines on the lab history runs

Asked for by cheetah (2026-10-25 03:03): how hard are the questions in `../runs/`, and what must a model beat?

## Rule baselines (no LLM): `rules.py`

```
python -m simulation.lab_history.baselines.rules     # from the repo root; about 10 s
```

Writes `rules_results.json` (tables below and more) and `rules_answers.jsonl` (every answer; not in git, regenerate).
Each rule sees only the events up to the question's `t`, and matches objects by their exact name, so a misnamed
sighting ("umbrella" for "red umbrella") is invisible to it. Scoring is exact match with the gold place. 2,700
questions over the 9 runs; 95% Wilson intervals in the JSON.

| kind (n) | last seen | most frequent, all | most frequent, 7 days | recency vote | claims |
|---|---|---|---|---|---|
| where_now (1,894) | **0.71** | 0.51 | 0.58 | 0.67 | 0.64 |
| where_now, fresh (1,365) | **0.98** | 0.64 | 0.76 | 0.90 | 0.81 |
| where_now, stale (529) | 0.00 | 0.17 | 0.13 | 0.05 | **0.18** |
| where_now, gold "not in the lab" (164) | 0 | 0 | 0 | 0 | 0 |
| last_in_lab (74) | 0.95 | 0.77 | 0.95 | **0.97** | 0.37 |
| desk_now (370) | **0.98** | 0.82 | 0.96 | 0.98 | 0.87 |

| usual_place (362) | weekday, most frequent, all | weekday, most frequent, 4 weeks | weekday, 4 weeks, or "away" | most frequent, all |
|---|---|---|---|---|
| accuracy | 0.75 | 0.77 | **0.84** | 0.63 |

**The rules:**
- **last seen:** the place of the latest sighting.
- **most frequent:** over all time, or over the last 7 days.
- **recency vote:** each sighting votes for its place with weight exp(-age / 3 days).
- **claims:** last seen, unless that place was looked at later without the object. Then the most frequent other
  place.
- **usual_place:** from sightings on the asked weekday. "or away" answers "not in the lab" when the object was seen
  in the last 4 weeks, but never on that weekday.

**What this says:**
- **Fresh questions are nearly free:** last seen gets 98%. Fresh means the last sighting still holds. It isn't 100%
  because the camera sometimes invents an object, and the rules believe it.
- **Stale questions are the test:** the object moved since it was last seen. The best rule is claims at 18%, and
  last seen is 0 by construction. Routine knowledge (weekday patterns, owners, put-back spots) is what could lift
  this.
- **"Not in the lab" is never answered** by any rule, so those 164 where_now questions are all wrong for every
  rule. A model that reasons about owners and away days can win there.
- **desk_now is too easy** (98%). The desk shifts are visible within a day because people sit at their desks.
- **History length barely matters:** last seen gets 0.72 / 0.68 / 0.72 on where_now for 30 / 60 / 90 days.
- **Shift phase:** every question falls after the first shift (questions come from the last two thirds of each
  run), so `by_kind_phase` only compares the first week after a shift with later. Last seen gets 0.71 in both.
  A before/after comparison would need questions from before the first shift (a generator change).

## Open-model answerer

Next: Qwen3.6-35B-A3B (already loaded on `:8302` for the vision comparison) given the flat event history, and
then a compact per-object table, on about 100 stratified questions per history length.
