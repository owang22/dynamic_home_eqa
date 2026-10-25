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

## Open-model answerer: `llm.py`

```
python -m simulation.lab_history.baselines.llm --per-length 100 --workers 3   # needs :8302 (Qwen3.6-35B-A3B-FP8)
```

Qwen3.6-35B-A3B-FP8 (thinking off, temperature 0), answering one of the 16 places or "not in the lab"
(json_schema enum), on a stratified sample: 100 questions per history length, 300 in all, pooled over seeds.
- **flat:** the event lines up to the question's time, the most recent ~11k tokens of them (mean prompt 10.9k
  tokens; 30-day histories mostly fit, 60/90-day ones are cut).
- **table:** per object and person: last seen, the three most frequent places, the most frequent place per
  weekday, and when each place was last looked at (mean prompt 2.7k tokens).

The rules are scored on the same sample (`llm_results.json`, `by_stratum` and `by_stratum_days`):

| stratum (n) | LLM, flat | LLM, table | last seen | recency vote | claims |
|---|---|---|---|---|---|
| where_now fresh (90) | 0.78 | 0.82 | **0.98** | 0.83 | 0.88 |
| where_now stale (90) | 0.20 | 0.16 | 0.01 | 0.08 | **0.33** |
| where_now, gold "not in the lab" (45) | 0 | 0 | 0 | 0 | 0 |
| usual_place (45) | 0.64 | 0.67 | | | **0.78** (weekday, 4 weeks, or away) |
| last_in_lab (15, thin) | 0.80 | 1.00 | 1.00 | 1.00 | 0.20 |
| desk_now (15, thin) | 0.80 | 0.87 | 1.00 | 1.00 | 0.80 |

**What this says:**
- **The open model beats no rule** on any stratum. On fresh questions it loses to last seen (0.78-0.82 vs 0.98).
  On stale ones it beats last seen but not claims (0.16-0.20 vs 0.33 on this sample; claims was 0.18 on all 529
  stale questions, so the sample's claims number is on the high side).
- **It almost never says "not in the lab"** (5 of 600 answers), so it scores 0 there too, like the rules.
- **The table is no better than the raw history** (overall 0.49 vs 0.47), at a quarter of the tokens.

## Before and after routine shifts: `runs_preshift/`

cheetah asked for questions from before the first shift. `generate.py --questions-from 3` lets questions start on day
3. Every question now has a `phase`: `before_first_shift`, `0-7d_after_shift` or `7d+_after_shift`.
`../runs_preshift/` holds the same 9 histories as `../runs/` (identical events and truth) with questions drawn from
day 3 on, about 30% of them before the first shift. Regenerating `../runs/` only added the `phase` field; no question
or answer changed.

```
python -m simulation.lab_history.baselines.rules --runs runs_preshift    # -> rules_results_preshift.json
```

| where_now, by phase (n) | last seen | recency vote | claims |
|---|---|---|---|
| before the first shift (576) | 0.71 | 0.64 | 0.69 |
| first week after a shift (575) | 0.72 | 0.67 | 0.63 |
| later (740) | 0.70 | 0.65 | 0.61 |
| stale only: before / first week / later (156 / 155 / 214) | 0 / 0 / 0 | | 0.24 / **0.12** / 0.21 |

usual_place (weekday, 4 weeks, or away): 0.81 before, 0.77 in the first week after a shift, 0.88 later.

**What this says:**
- **Shifts barely move the overall numbers.** Each shift changes one person's desk and two objects' routines, out
  of 25 tracked people and objects, so most questions aren't about a shifted thing.
- **The visible effect is on stale questions:** claims halves in the week after a shift (0.24 to 0.12), because its
  fallback, the usual place, is the old one.
- To measure shifts directly, questions should target the shifted people and objects. This would be a generator
  option, not done yet.
