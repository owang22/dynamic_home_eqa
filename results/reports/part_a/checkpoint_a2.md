# Checkpoint A2 — Realizable-Anchor Vocabulary (Part A), regeneration report

Comparison set: 102343992 / 102344022 / 102344049, `family_with_kids`, standalone
(semantic-grounding) pipeline, Qwen3-32B. STOPPED here per instructions — awaiting the
human webapp check.

## What changed (1.2 + 1.3, all landed)

- `target_anchor` enums are now room-qualified census instance labels
  (`kitchen.counter_2`, `bedroom_1.bed_1`) from `env/anchor_census.py`, split
  surface-vs-proximity by active-receptacle backing, scoped to the occupant's current
  room only. `in_region` is no longer emittable (no schema branch); the builder's
  `compliance_place_region` stays for replaying old manifests. `CATEGORY_ROOM_HINT` and
  the scene-wide `anchor_inventory` fallback are retired from this schema path (both
  survive for the census-less legacy fallback, which logs a loud warning).
- Every anchor enum carries an explicit `"none"` abstain entry; abstained proposals are
  dropped before grounding with counters (`abstained_proposals`/`abstained_clutter` in
  generation_result, `abstained_upstream` in the build audit).
- Semantic grounding checks census membership (and active-receptacle backing for surface
  relations) — generation and grounding read the same census views.
- Builder: census labels resolve by direct census lookup to the exact instance
  (`resolve_anchor_position` → census position → `find_live_object_at_xz` on that exact
  position), no category→nearest-instance guessing. New audit fields:
  `anchor_resolutions` (chosen label vs resolved live handle, per event),
  `proximity_floor_placements`, `abstained_upstream`.
- **New realization rule (flagging explicitly — not in the instructions, but forced by
  them)**: a census anchor with 0 active receptacles (fridge/tv — nothing authored — or
  curated-out wardrobe/washer_dryer) can only be targeted by near/next_to under the new
  schema, but the manifest doesn't carry the relation, and the builder's old
  synthetic-AABB-top fallback would have placed objects ON fridge/tv tops (the exact
  fridge-top-bowl class). These anchors now get a floor placement BESIDE the instance
  (reusing `compliance_place_region`'s navmesh-snap + live snap_down machinery). Legacy
  bare-category anchors (old manifests, gold set) never hit this branch.

## Cache behavior (checked, as instructed)

`generation/cache.py`'s key is the seed alone — `make_seed(household_id, day, stage,
occupant_index)` — and does NOT incorporate prompt or schema. A same-seed rerun would
have replayed pre-Part-A responses byte-for-byte. **A fresh cache dir was used:**
`/tmp/dynamic-home-eqa-gen-cache-partA`.

## Generation results

| scene | proposals (post-abstain) | survived grounding | abstained (displacement+clutter) | selected | manifest changes |
|---|---|---|---|---|---|
| 102343992 | 243 | 222 (91.4%) | 52 + 0 | 56 | 38 |
| 102344022 | 308 | 308 (100%) | 109 + 0 | ~— | 53 |
| 102344049 | 436 | 436 (100%) | 117 + 0 | ~— | 70 |

### The 21 grounding rejections (992) — investigated, root cause partially confirmed

All 21 are **hallucinated labels not in any enum** (`bedroom_1.stand_1` x20,
`bedroom_1.wardrobe_1` x1), exclusively from bedroom-location calls in 992 (9 distinct
LLM calls; the same responses also contain valid labels like `bedroom_1.bed_1`). Under
guided decoding an out-of-enum string should be unemittable, so grammar enforcement
failed for exactly this scene's bedroom schema. vLLM runs with
`disable_fallback=False` (visible in the engine config), which silently degrades to
unconstrained generation on grammar trouble; no warning appears in the log, so the
precise trigger is unconfirmed. **The census grounding gate caught all 21** — this is
the defense-in-depth working, but "consistent by construction" has this one hole.
→ Carry into Part 2.0 prerequisite work: set/inspect `disable_fallback`, verify grammar
compile per schema (the same wiring pass that handles the reasoning parser).

## Build audit — before (pre-Part-A baseline, same code-vintage rebuild) vs after

| metric | 992 before → after | 022 before → after | 049 before → after |
|---|---|---|---|
| events | 148 → 38 | 92 → 53 | 50 → 70 |
| ok | 120 → **38 (100%)** | 53 → **53 (100%)** | 47 → **70 (100%)** |
| region-path placements | 33 → **0** | 40 → **0** | 20 → **0** |
| anchor_unbacked | 20 → **0** | 0 → 0 | 0 → 0 |
| placement_infeasible | 8 → 0 | 7 → 0 | 0 → 0 |
| surface_full | 0 → 0 | 18 → **0** | 0 → 0 |
| receptacle_curated_out | 0 → 0 | 13 → **0** | 2 → 0 |
| unrealized-event rate | 18.9% → **0.0%** | 42.4% → **0.0%** | 6.0% → **0.0%** |

Every event in every scene now realizes. `region=0` everywhere (the floor-snap path is
unreachable, as specified). `anchor_unbacked=0` (the census resolved every label — no
census bugs surfaced).

## Move volume (flagging per instructions)

992's event count dropped 148 → 38 (−74%); 022 92 → 53 (−42%); 049 went UP 50 → 70.
Abstain rates are substantial (52/109/117 across the three scenes — roughly 18–27% of
raw proposals). Note the before/after aren't the same LLM outputs (new prompt + schema =
new responses even at the same seeds), so part of the delta is ordinary regeneration
variance — but the direction in the two shrinking scenes is consistent with the
tighter vocabulary + abstention doing what it's designed to do. Whether 992's floor is
too aggressive is a curation-coverage conversation (its census has several curated-out
counters and proximity-only anchors), not something fixed silently here.

## Census/data quirks to know about during the webapp check

- `rec/game.toilet_1` appears in the **living_room** vocabulary (the "rec/game" region
  aliases to living_room in `rooms._ALIASES`, and HSSD authored a toilet there with an
  active receptacle). If a living-room placement lands on a toilet, that's this.
- `bathroom_1.table_1` etc. are real HSSD-authored tables in bathrooms — legitimate.
- 992's five bedrooms include the three bed-rule conversions (HSSD labeled them
  "office") and one "other_room" — labels `bedroom_1..5`, numbering by region index.
- Gold set (`scripts/gold_set.py`): its pinned items reference the OLD 992 manifest
  (specific labels/timestamps that no longer exist after regeneration). It needs
  re-pinning after Part A settles — expected, not done silently here.

## Artifacts

- Census tables (A1): `results/reports/anchor_census/<scene>_anchor_census.md`
- Anchor-choice histogram (doubles as Part 2 Arm 0 baseline):
  `results/reports/part_a/anchor_choice_histogram.md`
- Build audits: `results/reports/realized_day_build_log.json` (after);
  before-baseline preserved in the report table above.
- Renders: full-size (64/16) batch for all 3 folders in
  `results/reports/realism_eval_media/` — serve the webapp as usual to review.

## Human webapp checklist (from the instructions)

- No floor-level bowls (region path is gone; `region=0` confirms mechanically, the
  renders confirm visually).
- No outdoor furniture targeted by indoor activities (outdoor anchors only offered for
  location=outdoor).
- Kitchen placements use counters/tables/cabinets.
- fridge/tv never used as surfaces (proximity-floor rule; `proximity_floor_placements`
  in the audit counts these).
- Overall move volume: see the volume section above — 992's −74% is the number to react
  to if it feels gutted.
