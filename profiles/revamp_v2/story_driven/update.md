# Story-driven generation — status update (2026-08-19)

Runs of `src/revamp_v2/story_driven.py` (21 days, hh1–3, seed 0) via the
scratchpad `story_driven_run.sh` / `story_both.sh` drivers: vLLM on
:8300, TP=1, xgrammar structured outputs (movement pass only — the story
stage is thinking-mode, no grammar).

## Run outcomes

### deepseek-v4-flash — finished (exit 0, 211 min gen + 80 s server)
Viewer configs + spatialize OK for all three households.

| hh | residents.jsonl | events | failed weeks | failed days | story acts | verdict |
|----|----------------|--------|--------------|-------------|-----------|---------|
| hh1 | 198 | 509 | 0/3 | 1 | 23 | good |
| hh2 | **0** | 455 | **3/3** | **30** | **0** | **NOT story-driven** |
| hh3 | 357 | 733 | 1/3 | 10 | 26 | usable |

**hh2 is fallback data wearing a story-driven label.** All three story
weeks failed, so every day ran the `(story missing)` fallback path in the
movement loop. It spatialized "OK" and looks healthy downstream — do not
use it as story-driven data.

hh2 failure modes (per `meta.json` `failed_weeks`):
- week 0: invented resident name `Sam` instead of `resident_N` → jsonschema kill
- week 1: block-array shape drift → jsonschema kill
- week 2: `JSONDecodeError` — unterminated JSON at ~27 KB (likely length truncation)

### qwen3.8-27b — killed mid-run (~1h45m in, hh1 day 18/21 of movement pass)
Weeks 0 and 1 of hh1's story both failed with
`Expecting value: line 1 column 1` — the payload was raw reasoning prose
("We need answer user's request…"), not JSON. Only week 2 survived; days
0–13 had no story (days 0–1 recorded 0 movements). Killed rather than
spend ~4.5 h producing three mostly-fallback households.

Leftover partial output at `story_driven/qwen3.8-27b/hh1/` (story.yaml,
persona/program/motions copies, residents.jsonl; **no** events.jsonl /
hourly.csv / meta.json). Safe to delete.

## Root cause (qwen failures)

1. **Story stage is thinking-mode with no grammar** — by design:
   `generate_json_thinking` → `generate_thinking` (llm_client.py), because
   on this vLLM the JSON grammar suppresses the think block outright. The
   payload extractor splits on `</think>` and falls back to the *entire
   raw text* when the tag is absent.
2. **The think block never closed — token-cap truncation.** vLLM metrics
   showed `finished_reason="length"` = 2, exactly the 2 failed weeks.
   `STORY_MAX_TOKENS = 24000` wasn't enough for a whole-week story;
   Qwen3.8-27B burned the budget still reasoning, truncated before
   `</think>`, parser got prose → JSONDecodeError at char 0.
3. **`max_retries=1`** on the story call (story_driven.py:195) — one bad
   sample permanently loses a whole week, no reroll at a shifted seed.

The deepseek hh2 failures are the complementary mode: think blocks closed
fine but *content* drifted (invented names, shape drift) — the known
prose-constraints-don't-bind failure; only grammar-enforced stages hold
the vocabulary. Plus one probable length truncation.

## Proposed fixes (not yet applied)

- Truncation guard: raise `STORY_MAX_TOKENS`; better, detect
  `finish_reason == "length"` / missing `</think>` and retry instead of
  parsing garbage.
- `max_retries=3` for the story stage — failures are seed-sensitive; a
  reroll would likely have recovered all five failed weeks across both runs.
- Shrink the ask: per-day (or per-resident) story calls instead of
  whole-week, so thinking fits in budget and one bad sample loses a day.
- Refuse-to-ship: if all weeks fail, error out instead of writing a
  fallback-only household that looks healthy downstream (the hh2 trap).
