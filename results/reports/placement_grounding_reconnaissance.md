# Placement/grounding reconnaissance — read-only pass, no code changes

Gathered against the three scenes with existing anchor-admission caches (used as
the comparison set throughout this pass): **102343992**, **102344022**, **102344049**,
household profile `family_with_kids`. All numbers below are from real code execution
against real scene data, not estimated.

Side task done alongside this: `scripts/realism_render_job.py`'s `--n-location`/`--n-state`
defaults halved (64→32, 16→8, ~80→~40 total) so the webapp sample pool lands close to the
requested ~30.

---

## Strategy 1 — Eliminate coarse targets from the output language

### 1.1 — Actual schema output + relationship vocabulary

`PARTNR_RELATIONSHIPS` (after `grounding.py`'s import-time extension from PARTNR's own
registry): `{in_region, inside, near, next_to, on, on_top, within}`. Only `in_region` is
room/region-targeted (`REGION_ONLY_RELATIONSHIPS = {"in_region"}`); the other six all target
a **furniture category**, not a receptacle instance.

Real `build_displacement_schema` output for scene 102343992, `location="kitchen"`:

```json
"target_anchor": { "enum": ["fridge", "range_hood"] }   // furniture-relation branch
"target_anchor": { "enum": ["kitchen"] }                 // in_region branch
```

For `location="bedroom"`: `["bed", "wardrobe"]`. For `location="living_room"`:
`["bench", "couch", "tv"]`. Every `target_anchor` enum entry is a **bare category name**
(`"table"`, `"fridge"`), never a room-qualified or instance-level string — confirms the
premise directly. Full schema JSON captured during this pass, available on request.

Notable gap already visible here: the kitchen vocabulary is `[fridge, range_hood]` only —
no `counter`, despite `counter` genuinely existing in this scene's furniture (see 1.3/1.4).

### 1.2 — Where `in_region` becomes a floor placement

Not in `grounding.py` — `grounding.py`'s `in_region` handling is a **point-in-volume
validation** only (`_ground_in_region_by_geometry`), it never picks a position. The actual
placement happens at the **build** stage, `scripts/build_realized_day.py`:

- `classify_anchor()` (line 280): any anchor equal to a bare `CANONICAL_ROOMS` name — i.e.
  every `in_region` target — classifies as `"region"`.
- `resolve_anchor_position()` (line 345): a `"region"` anchor's position is that room's
  **centroid, navmesh-snapped at floor height** (`world.snap_to_navmesh((cx, 0.0, cz))` —
  the `0.0` is literal).
- `compliance_place_region()` (line 508): does a `snap_down(sim, obj)` call with the
  **default `support_obj_ids=[stage_id]`** — explicitly commented "the real floor/stage
  mesh." This is the floor-bowl mechanism, located precisely: object lands on the room's
  floor mesh, not any furniture surface, because a region anchor by construction has no
  single furniture instance to bind to.

This is not a bug so much as the documented, designed behavior for a target language that
can't express "which surface" — exactly the diagnosis in the prompt. Deleting `in_region`
from the emittable vocabulary (Strategy 1's proposal) removes the only code path that reaches
this function.

### 1.3 — Room-tagging coverage (the caveat that gates this whole strategy)

Two **independent** room-tagging implementations exist, feeding different consumers, with
very different real coverage:

**`topdown_map.instance_room_positions`** (feeds `resolve_slot`'s validation fallback,
`room_instance_categories` in `pipeline.py`) — sourced from `load_furniture_census` (full
Tier-1 census) + Tier-2a native clutter positions:

| scene | positions checked | room-tagged OK | no region volume | geometry↔tag mismatch | no CANONICAL_ROOMS match |
|---|---|---|---|---|---|
| 102343992 | 106 | 41 (38.7%) | 12 | 52 | 1 |
| 102344022 | 78 | 55 (70.5%) | 19 | 4 | 0 |
| 102344049 | 52 | 40 (76.9%) | 1 | 11 | 0 |

The fixture scene (102343992) is the worst of the three, and the dominant failure mode
there is **geometry↔foundIn-tag disagreement** (49% of all positions), not missing region
volumes — e.g. a real `table` sits in a region geometrically classified `garage`/`other_room`,
which the hand-authored `found_in_rooms("table")` tag list doesn't include, so the instance
is silently dropped rather than trusted either way.

**`generation/inventory.py`'s `room_inventory_from_scene_state`** (the one that actually
feeds `generate_displacements`'s prompt/schema) — sourced from `load_scene_state`, which by
its own docstring only returns **Tier-2a native clutter + one instance per `STATEFUL_FURNITURE`
category** (fridge, wardrobe, oven, tv):

| scene | instances checked | geometric match + tag OK | recovered via slot-prefix fallback | dropped: tag mismatch |
|---|---|---|---|---|
| 102343992 | 17 | 13 (76.5%) | 1 (5.9%) | 3 (17.6%) |
| 102344022 | 32 | 23 (71.9%) | 6 (18.8%) | 3 (9.4%) |
| 102344049 | 16 | 13 (81.2%) | 0 (0%) | 3 (18.8%) |

Effective coverage here is actually decent (82–91%) — **but the population it's measuring
is tiny and structurally excludes almost every static Tier-1 fixture**: table, counter,
cabinet, shelves, bench, stand, bed, wardrobe, couch, etc. never enter `load_scene_state`
at all, because that function was built to seed only the "tracked, potentially-moving"
instance set, not the full furniture census.

**Direct confirmation, scene 102343992**: `room_inventory_from_scene_state` returns
categories `{chair, potted_plant, stool}` — literally nothing else, in any room, ever.
Every other anchor-capable category (`bathtub, bed, bench, cabinet, couch, counter, fridge,
range_hood, shelves, stand, table, toilet, trashcan, tv, wardrobe, washer_dryer` — all 16 of
the remaining `anchor_inventory` categories) **never appears in `room_inventory`, in any
room, at all.**

**This is why 1.1's kitchen enum showed `[fridge, range_hood]`**: `anchors_in_room()`'s real
room_inventory∩anchor_inventory intersection is empty for every category, so it falls through
to a **third, separate mechanism** — `rooms.CATEGORY_ROOM_HINT`, an 18-entry hand-authored
static table (`fridge→kitchen`, `bed→bedroom`, `tv→living_room`, ...). That table is where
`[fridge, range_hood]` actually came from, not real per-scene geometry.

`CATEGORY_ROOM_HINT` itself **omits** `cabinet, counter, shelves, stand, table, trashcan` —
for those six categories there is no room-scoping mechanism at all, geometric or static, so
`generate_displacements`'s outer fallback (`anchor_inventory.keys()`, scene-wide, no room
filter) kicks in and offers them in **every room, for every activity, regardless of the
occupant's actual location.** This is almost certainly the literal mechanism behind the
"outdoor dining table" class of bug named in the prompt.

**Net finding for Strategy 1**: the room-scoping "system" is actually a three-tier fallback
chain (real geometry → static 18-entry hint table → unscoped scene-wide), and for most
furniture categories — including exactly the surfaces you'd want a bowl/keys/wallet/phone
placed on — it bottoms out at the last tier. Room-qualified receptacle-instance anchors
(Strategy 1's actual proposal) are **not** built on top of this chain today; they'd need a
new census (Strategy 2's territory) feeding a new vocabulary layer, not a fix to the existing
one.

### 1.4 — Enum size after the change

Using the current `room_inventory` (tiny, tag-gated) population: **13–29 room-qualified
instances per scene** — nowhere near the "hundreds" the prompt worried about; grammar
compile time is a non-issue at this scale. Using the raw Tier-1 census as the ceiling (i.e.
if 1.3's structural gap were fixed and every real furniture piece got a room-qualified
instance entry): **39–92 per scene**. Either number is comfortably small for guided
decoding — the gating concern for Strategy 1 is data coverage (1.3), not enum size.

---

## Strategy 2 — Ground placements in real receptacle geometry

### 2.1 — Receptacle annotation coverage (Tier-1 furniture, per category, per scene)

Measured directly via `habitat.datasets.rearrange.samplers.receptacle.find_receptacles(sim)`
+ each scene's `.rec_filter.json` "active" list — the exact mechanism
`build_realized_day.resolve_furniture_receptacles` already uses.

| category | 102343992 (n / raw / active) | 102344022 | 102344049 |
|---|---|---|---|
| table | 15 / 73% / 73% | 7 / 100% / 100% | 4 / 100% / 100% |
| counter | 8 / 100% / **25%** | 5 / 100% / 100% | 1 / 100% / 100% |
| cabinet | 12 / 92% / 83% | 20 / 85% / 60% | 3 / 100% / 100% |
| shelves | 14 / 100% / 79% | — | 5 / 100% / 40% |
| bench | 11 / 100% / 91% | — | 1 / 100% / 100% |
| wardrobe | 5 / 100% / **0%** | — | 2 / 100% / **0%** |
| washer_dryer | 2 / 100% / **0%** | — | 2 / 100% / 100% |
| bathtub | 1 / 100% / 100% | 1 / 100% / **0%** | — |
| **fridge** | 1 / **0%** / **0%** | 1 / **0%** / **0%** | 3 / **0%** / **0%** |
| **tv** | 3 / **0%** / **0%** | 2 / **0%** / **0%** | 3 / **0%** / **0%** |
| oven/dishwasher/fireplace | — | 0% (both) | 0% (fireplace) |

Two distinct patterns:
- **Raw annotation exists but curators filtered it all out** (wardrobe, washer_dryer in
  102343992; bathtub in 102344022) — `resolve_furniture_receptacles`'s
  `raw_had_any=True, active=[]` case, i.e. `PLACEMENT_RECEPTACLE_CURATED_OUT`, a real,
  human-authored exclusion, not a bug.
- **No receptacle authored at all, ever** (fridge, tv, oven, dishwasher, fireplace — 0%
  raw, consistently across every scene) — these categories structurally cannot use
  receptacle-based placement regardless of any fix; they need their own fallback story
  (interior-shelf receptacles for fridge specifically aren't modeled as `Receptacle`
  objects in this dataset at all).

Counter — probably the single most commonly-wanted "put it on X" surface — swings from
100% raw to 25% active in the fixture scene specifically, which matters a lot for exactly
this project's fixture-scene-heavy testing history.

### 2.2 — How the sim-backed grounding path already picks poses

`generation/grounding.py`'s `ground_proposal()` (the `ground_displacement_batch` / live-
WorldGraph path) delegates directly to **`anchor.sample_place_location(spatial_relation=...,
spatial_constraint=..., ...)`** — a PARTNR `habitat_llm.world_model` furniture-node method,
external to this project. It almost certainly does receptacle-aware sampling internally
(that's what the method is for), but this is opaque from here — no receptacle files are
touched directly by `grounding.py` (confirmed: zero occurrences of "receptacle" anywhere in
that file).

**This path is not the one actually used.** `generate_for_scene`'s own docstring: `world_graph:
... None = use standalone CSV-based inventory`, and `gen_dataset.py` (the actual CLI
entrypoint) never wires up a live WorldGraph/env/agent — every real generation run in this
pipeline goes through `ground_displacement_batch_semantic` instead, which has **no placement
sampling of any kind**, only category/anchor-existence and region point-in-volume checks (see
3.1 below for the direct consequence).

The receptacle machinery that **does** run for real, for every build, is a **separate,
independent implementation** — `build_realized_day.resolve_furniture_receptacles` +
`compliance_place_on_surface`, using habitat-lab's `find_receptacles`/`Receptacle
.sample_uniform_global` directly (the same calls 2.1's measurement script used). This
already does real occupancy-safe placement (`_other_object_collides` checks against
already-placed objects) — Strategy 2's proposed mechanism **already exists**, just only at
the build stage, three stages downstream of where the LLM's proposal was generated and
graded.

### 2.3 — Where `realized_pos` is computed

**Build stage**, not generation, not render. Confirmed at both ends:
- `generation/schemas.py`'s own module docstring: *"No geometry in any schema. Spatial
  anchors are semantic object categories, not coordinates. PARTNR resolves geometry."* —
  generation never produces a position.
- `scripts/realism_render_job.py`'s `render_event_grid` docstring: *"This function no
  longer computes placement at all; it materializes each panel's object AT its recorded
  realized_pose"* — render never computes one either.
- The actual computation is `scripts/build_realized_day.py`'s per-event loop
  (`compliance_place_on_surface` / `compliance_place_region`, both described above), a
  third, distinct pipeline stage that runs after generation+grounding and before rendering.

Real numbers from this session's own fixture-scene build (`102343992_family_with_kids`,
148 events): **anchor classification: instance=115 (77.7%), region=33 (22.3%)**; placement
method of the 120 successful placements: `snap_down=72` (this label is used by both the
region-floor path AND a `compliance_place_on_surface` fallback tier — see that function's
own docstring for the split), `surface_height=22`, `synthetic=26`. Roughly 1-in-5 anchor
resolutions in a real generated day go through the region/floor path.

---

## Strategy 3 — Second-stage resolver

### 3.1 — Rejection taxonomy from a real batch (the load-bearing number, and a surprise)

Fresh generation run (cache-bypassed-eligible, force=False so cache-hits were allowed but
none existed for this exact seed set), standalone/semantic grounding, all 3 comparison
scenes, `family_with_kids`:

| scene | total proposals | accepted | no_object | no_anchor | no_placement | bad_relation |
|---|---|---|---|---|---|---|
| 102343992 | 470 | 470 (100%) | 0 | 0 | 0 | 0 |
| 102344022 | 858 | 858 (100%) | 0 | 0 | 0 | 0 |
| 102344049 | 674 | 674 (100%) | 0 | 0 | 0 | 0 |

**Zero rejections, on any axis, across 2,002 real proposals.** This is not evidence that
generation is flawless — it's the schema doing its job *too* well: `object_category` and
`target_anchor` are guided-decoding `enum`-constrained to the real per-scene vocabulary
(1.1), so the model is **physically incapable** of emitting a value that would trip
`no_object`/`no_anchor` under the standalone path's existence-only checks. This
instrumentation is currently **blind to the actual problem** — floor-bowls and
scene-wide-fallback anchors (1.3) sail through with a 100% survival rate because "does this
category/anchor exist somewhere in the scene" is a real yes for all of them.

The taxonomy that actually captures resolution-level failure is a **different, separate**
one: `build_realized_day.py`'s own audit dict, three stages downstream. From this session's
real fixture-scene build: `ok=120, anchor_unbacked=20, infeasible=8, no_asset=0` out of 148
events (unrealized-event rate 18.9%) — that's where "good intent, bad translation" actually
shows up, not in `GroundingStats`.

**Direct implication for the sequencing question**: since generation-time grounding cannot
currently discriminate at all, a resolver stage (Strategy 3) would be the **first** point in
the pipeline capable of rejecting/redirecting a bad (category, anchor) pair before it reaches
the builder — right now nothing does. This argues for either fixing `ground_displacement_batch_semantic`
to actually check placement feasibility (which needs Strategy 2's data), or adding the
resolver, before more schema work on top of a validation stage that currently never says no.

### 3.2 — Occupancy/adjacency info in current prompts

None. Checked `_DISPLACEMENT_SYSTEM` (the full system prompt) and
`format_inventory_for_prompt` (the inventory text block) directly — the prompt gives the
model category:count pairs and a per-room top-5 breakdown, nothing about what's currently
on a given receptacle, its capacity, or spatial relationships between receptacles. Confirms
the prompt suspicion in the brief.

### 3.3 — Cache-key/seed structure for a two-call-per-proposal pattern

`generation/cache.py`'s `make_seed(household_id, day, stage, occupant_index)` is a fixed
4-tuple with **no per-proposal disambiguator**. Every existing call site folds
proposal-adjacent context into the free-form `stage` string (e.g.
`f"displacement_{activity}_{start:.2f}"`), never into a 5th positional argument.

This project has already hit and fixed exactly this class of bug once:
`generate_displacements`'s own docstring: *"start disambiguates repeat occurrences of the
same activity label within a day ... the seed used to be keyed on activity label alone, so
every recurrence collided on the same cache entry and reused byte-identical proposals."* A
resolver stage needing one call per surviving proposal (not per activity-batch) would
collide the same way unless the proposal itself contributes to the seed — either a new
index parameter on `make_seed`, or a proposal-identifying string
(`f"resolver_{activity}_{start:.2f}_{object_category}_{target_anchor}"`) folded into `stage`,
matching the existing precedent rather than inventing a new pattern.

---

## Summary for sequencing

- **Strategy 2's data foundation is real but incomplete**: receptacle geometry exists and
  already works (build stage), but ~5 categories (fridge/tv/oven/dishwasher/fireplace) have
  zero annotations by design and need a separate fallback; curator filtering removes a
  further, sometimes large, chunk of the rest (counter: 25% active in the fixture scene).
- **Strategy 1 is gated exactly as the brief predicted** — but the actual blocker isn't
  "region-tagging is somewhat noisy," it's that the vocabulary-building function
  (`room_inventory_from_scene_state`) structurally never sees most Tier-1 furniture at all,
  so room-scoping today runs almost entirely on an 18-entry static hint table with real
  gaps (counter/table/cabinet/shelves/stand/trashcan have no room-scoping mechanism
  whatsoever). Building room-qualified anchors needs a new census pulling from the full
  Tier-1 furniture population (Strategy 2's territory), not a patch to the existing chain.
- **Strategy 3's own gather item produced the most load-bearing surprise**: the rejection
  taxonomy the decision was supposed to hinge on is currently non-functional (100% survival,
  always) because guided decoding already prevents the failure modes it measures. The real
  "good intent, bad translation" signal lives in the build-stage audit instead, and by that
  measure it's substantial (~19% unrealized-event rate on the fixture scene, dominated by
  `anchor_unbacked`).

No code changes made beyond the sample-volume side task. Report only, per your request.
