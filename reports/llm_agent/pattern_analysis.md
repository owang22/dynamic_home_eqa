# Pattern Analysis — when do the models get room-location right/wrong

Based on existing data (Qwen3.6 + gpt-5.4-mini main banks, moved bank). Two structural
issues surfaced; both change how the metric must be read and reported.

## Issue A — all memory last-seen times are 08:00 (by design, and it's a confound)

The single-decision episode injects ONE observation: a full wake-up snapshot at 08:00.
So every object's memory entry reads "last seen 08:00", and the only thing that varies is
the query time (Δt). Consequences:
- Per-object staleness heterogeneity is untested — every object has identical age within
  an episode.
- Age is perfectly confounded with query-time-of-day and with Δt.
This is fine for the age *dose-response* (vary Δt, hold content) but it is NOT a realistic
memory. The multi-step ReAct loop (where earlier sensing sets per-object last-seen at
different times) is what tests heterogeneous staleness; the single-decision form cannot.

## Issue B — aggregate accuracy (0.924) is the base rate of non-movement, not capability

A2, both models, main bank (n=288):
- **92.4% of episodes the object never changed room** → accuracy **1.000** (trivial parroting).
- **7.6% the object did change room** → accuracy **0.000** (every single one wrong, both models).

The 0.924 headline is just P(object didn't move). It measures object stasis, not the model.
On the moved-object bank (objects that genuinely changed room), answer-only accuracy is
**0.06** (Qwen A2 0.068, and 0.063 pooled); when something moves, the models cannot say
where — they lack a routine model — and they hedge to "elsewhere" 47.5% of the time.

## Issue C — the chair hypothesis is correct, and stronger than stated

Per-class ROOM-change rate (measured on the sim over same-day windows; distinct from the
receptacle-level static/occasional/dynamic stratum):

| room_change_rate | classes |
|---|---|
| **< 0.02 (fixture-like — demote for room questions)** | fridge, oven, **stool** (0.000), tv, wardrobe, **potted_plant** (0.007), sunglasses (0.015) |
| 0.02–0.05 (near-static) | **chair (0.026)**, wallet (0.028), teapot (0.045) |
| **> 0.05 (genuinely room-mobile)** | keys, remote_control, vase, bowl, newspaper, laptop, backpack, toy, candle, headphones, **phone (0.237)**, bottle (0.273), **cup (0.288)** |

- In the current target set, **chair (40) + potted_plant (40) = 28% of episodes**, both
  effectively room-static → trivially correct → inflating everything.
- The volatility stratum is receptacle-level and **mismatches** room granularity: a
  "dynamic" chair (tucked under different tables in the same room) never changes ROOM.
  Stratum-vs-room-change: static 0.000 / occasional 0.042 / dynamic 0.188 — even the
  "dynamic" tercile only changes room 19% of the time.

## Issue D — the dining/dining_room census alias is still leaking

The chair moved-bank cell (0.833 accuracy) is **15/15 phantom moves**: `dining` →
`dining_room` synonym transitions (scene 102344022's census carries both as distinct room
labels). `moved_since_snap` uses a raw string compare, so these register as "moved" even
though nothing changed. Alias-tolerant scoring rescues the answer, but the *episode
selection* into the moved bank is polluted. Fix at the source: normalize census room labels
when logging episodes (one alias map), so `dining`/`dining_room` are one room everywhere.

## Recommendations (for decision — not yet implemented)

1. **Always report accuracy split by moved-vs-not** (aggregate is a base-rate metric). The
   moved-object effective accuracy is the real capability number.
2. **Room-level volatility relabel** for room-location questions: sample/weight targets by
   the room_change_rate table above, not the receptacle stratum. Demote < 0.02 classes
   (drop or heavily downweight chair/stool/potted_plant/fixtures) so they stop dominating.
   Keep a few as a stable control, but not 28% of the bank.
3. **Fix the census alias** (dining/dining_room) at episode-logging time.
4. Consider a **different question type for fixtures** (state/presence rather than
   room-location) since "which room is the fridge in" is trivial by construction.

Net: the capability-ladder story (Qwen/mini age-blind, flagship age-sensitive) stands —
it lives in the *resense decision* and the *moved-object* subset, both of which are robust
to A–D. But the headline accuracy number and the target-class mix need the fixes above
before the bank is frozen for the paid frontier runs.
