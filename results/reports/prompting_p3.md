# Prompting Infrastructure — Phase 3 (sequential state threading + despawn)

Phase 3 replaces batch, independent-per-window generation with a
**chronological, stateful loop**. Windows (one per occupant-activity) are
sorted by start time and processed in order; after each window's moves are
selected they are *applied* to a running `{instance: location}` state, and the
next window's proposer **and** judge see the authoritative current state
instead of the proposer's `assumed_from` guess.

Measured against the same 3-scene comparison set (`generation_out_labelset/`,
`family_with_kids`) and pre-Phase-3 baseline (reason-first + tv_room, winning
`strict_ctx_fs` judge). EXEMPLAR pool held out as before.

## What changed

**1. Running state threaded through the day** (`generation/running_state.py`).
`RunningState` tracks each owned Tier-3 item's current location (or `None` =
put away / not out yet), everything already moved today, and a per-anchor use
counter. The pipeline (`generate_for_scene`) now:

- builds the window list, sorts it chronologically (tie-break by occupant),
- for each window: `generate → ground → judge → select → state.apply`,
- feeds the acting occupant's **current object state** block into both the
  displacement prompt and the realism judge,
- makes `surface_occupancy` **live** — it reads the running state
  (`anchors_in_use`) so the proposer sees what is *currently* on each anchor in
  the room, not the start-of-day inventory,
- **down-weights repeat anchors** in selection (`anchor_uses`), so a day's
  moves spread across surfaces instead of piling onto one.

**2. `assumed_from` is now diagnostic-only, and reason-first.** The proposer's
guess about where an item came from (`assumed_from`) was never authoritative;
Phase 3 gives it the real answer via the state block, and the manifest's
`from_semantic` comes from chronological replay (as before). `reason` is now
the **first** schema property (pre-Phase-3 change), so the model reasons
*before* committing to a placement rather than rationalizing after.

**3. Despawn / put-away** (the night mechanic). Tier-3 items that get put away
at night should *disappear* — we don't model where they go, only that they're
no longer placed anywhere.

- Schema: a `put_away` anchor option, offered **only** when the acting
  occupant actually has a carried item currently out (`include_put_away`,
  gated on live state) — the model can't put away something that isn't out.
- Pipeline: `put_away` proposals are split off, **bypass grounding** (a
  put-away is always feasible), are still judged/selected, and marked
  `_despawn`.
- Manifest: a despawn emits **`change_type="remove"`** — the established
  "object leaves the world" contract `env/replay.py` (pops the instance from
  replayed QA/agent state) and `env/world_graph_adapter.py` (clean no-op)
  already implement, reused rather than inventing a synonym they'd each have to
  special-case. `to_semantic="away"` (ignored by the remove path),
  `from_semantic` = the item's current tracked location, `mover` = the owner
  (a carried item travels with them — no source-room attendance needed). If the
  replay has no prior placement for the item (it was never actually out in the
  manifest's own chain), the removal is dropped, not emitted from nowhere
  (`dropped_despawn_notout`).
- Re-appearance chains cleanly: bringing the item back out the next day/window
  is a `move_existing` **from `"away"`**, so the location chain stays
  consistent.

**4. `trace_validate` is remove-aware.** A removal's destination is the
symbolic `"away"` (no room), so the ordinary source/destination room-presence
check would misfire. For `change_type=="remove"` the validator instead requires
the **mover to be home** (a real, non-`"away"` activity location) at event time
— still re-derived from `traces`, so a put-away claimed while its owner is out
of the house is caught.

## Cache correctness

Later windows depend on earlier outcomes, so stale cache must never be served.
The acting occupant's state block is hashed (`state_hash`) and folded into both
the displacement and judge **stage tags**, alongside the existing prompt
content-hash. A change to any earlier window's selected moves changes the state
block, which changes the tag, which invalidates the cache for every downstream
window — automatically.

## Verification (code-level)

- `tests/test_manifest.py` — 3 new despawn unit tests: put-away emits a
  `remove`→`"away"` chaining from the item's location; a removed item reappears
  as `move_existing` from `"away"`; a put-away with no prior placement is
  dropped and counted. All 15 pass. `tests/test_replay.py` still green — the
  `"remove"` event pops the instance from replayed state.
- `tests/test_integration_fake_client.py` — new Phase 3 end-to-end test
  (`enrich_context=True`) across 3 scenes × 3 seeds runs the full per-window
  loop; the fake client randomly emits `put_away`, exercising the despawn
  split, the manifest `"away"` change, and re-appearance chaining. All hard
  trace invariants hold with despawns in the log. (Confirmed non-vacuous:
  despawn events are actually produced.)
- 76 targeted tests green (manifest + integration + trace_validate + replay).
  The only suite failures are pre-existing and unrelated (stale `llm_prior`
  collection after the owner's `llm_OLD` rename; render-mask / calibration
  tests that fail identically on `HEAD`).

## Regenerated comparison set (Phase 3)

All 3 scenes regenerated end-to-end under the sequential loop
(`generation_out_labelset/`, overwritten, `force=True`). **100% grounding
survival, all 3 trace-valid** (chain_breaks=0, re_inserts=0, no_ops=0,
unattended=0 — despawns and all).

| scene | changes (base → P3) | despawns | realism (base → P3) |
|---|---|---|---|
| 102343992 | 62 → 42 | 2 | 0.581 → 0.561 |
| 102344022 | 53 → 45 | 0 | 0.605 → 0.526 |
| 102344049 | 48 → 41 | 3 | 0.489 → 0.528 |
| **mean** | | **5 total** | **0.558 → 0.538** |

**Realism is flat** (0.558 → 0.538, within run-to-run noise). Phase 3 was not a
realism play — it's a *correctness/coherence* change (the proposer/judge now
reason against real state) plus the despawn mechanic. Selected-score level is
governed by the calibrated `strict_ctx_fs` judge, unchanged from P2.

**Despawn works in real generation.** 5 put-away events across the set, every
one trace-valid, `dropped_despawn_notout=0` (the running-state/manifest-replay
gating never disagreed). Owners put away their own carried items at night; the
items leave the tracked world (`→ "away"`) instead of being "moved from some
unknown thing", which was the artifact the owner flagged.

**The proposer's provenance guesses got more accurate — the core Phase 3
signal.** `llm_claim_divergence` counts moves where the proposer's `assumed_from`
guess disagreed with the authoritative chronological replay. As a fraction of
moves that have a provenance (changes minus `insert_new`):

| scene | baseline | Phase 3 |
|---|---|---|
| 102343992 | 46/52 = **88%** | 30/38 = **79%** |
| 102344022 | 35/48 = **73%** | 23/42 = **55%** |
| 102344049 | 28/39 = **72%** | 15/36 = **42%** |

Feeding the authoritative current-state block into the proposer cut divergence
in every scene (mean ≈ 78% → 59%). It stays high in absolute terms — the model
still guesses wrong often — which is exactly why `from_semantic` comes from
replay, never from `assumed_from`. Phase 3 both **uses** the real state and
**demonstrates** the guess was never trustworthy.

**Unchanged-good from P2:** zero fixtures moved (fridge/tv/wardrobe/counter/oven
never carried) across all 3 scenes; Tier-3 instances remain per-owner
(`emily_phone`, `david_laptop`, …), children own nothing.

## Open / parked

- **Render realization of `remove`.** State-graph consumers already handle it
  (`env/replay.py` pops the instance; `env/world_graph_adapter.py` no-ops), so
  QA/agent state is correct today. But `scripts/build_realized_day.py` (the
  render step) sets `anchor = c.to_semantic` for every non-`state_change` event
  and would classify a removal's `"away"` as an *unbacked placement* rather
  than removing the asset from that frame on. It needs a `remove` branch
  alongside its `state_change` branch. Only relevant once Phase 3 days feed the
  renderer/web server (the P2 render pool is untouched) — track then.
- **Exemplars still `family_with_kids`-flavored** (carried from P2) — re-sample
  the EXEMPLAR pool across profiles when the scene pool broadens.
- **`reason`-in-judge A/B** (carried from P2) — the judge still sees the
  proposer's `reason`; a possible over-scoring lever to test if calibration
  regresses on a broader set.
