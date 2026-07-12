# Receptacle Infrastructure Investigation

**Investigation round, not a build.** No changes were made to the builder, generator, render job, or
any artifact. All new code lives in `scripts/investigations/` (disposable, see Cleanup at the end).
Pool-wide realized-day build stays gated pending owner review of this report.

## Bottom line

**GO, with a clear boundary.** habitat-lab's Receptacle + snap_down machinery is real, already present
in our own dataset copy (no second HSSD checkout needed), and directly fixes a real, confirmed defect
in our hand-built placement stack: it successfully placed two objects our own builder rejected as
`SURFACE_FULL`, using the exact same table, in under 3 samples each. It covers **INSTANCE anchors
only** (on-surface / in-container placement) — it has no bearing on REGION anchors (open-floor
placement, ~74 of our anchor instances across the qualified pool, all our `PLACEMENT_INFEASIBLE`
failures observed this round were region anchors). See "What gets replaced" below for the precise
boundary.

## Environment

New conda env `habitat_lab_recept` (python 3.9.2, `habitat-sim=0.3.3` via conda-forge/aihabitat,
`habitat-lab` core installed editable from `third_party/habitat-lab` — **not** `habitat-baselines`,
which none of the investigated APIs need). `explore-eqa` (the env every other part of this project
uses) was not touched. The `third_party/habitat-lab` git submodule was initialized (was previously
empty on disk). Total setup: ~15 minutes, no failures, one pillow version pin fix
(`habitat-lab`'s pip install wants pillow 11.x, `habitat-sim` 0.3.3 wants 10.4.0 — pinned to 10.4.0,
harmless).

## 1. Receptacle coverage inventory

Ran `find_receptacles(sim)` (habitat-lab) + each scene's `.rec_filter.json` (active/inactive split,
already present in our existing HSSD dataset copy at
`scene_datasets/hssd-hab/scene_filter_files/<scene_id>.rec_filter.json` — **no second dataset
checkout was needed**; this directly resolves the round's own "verify ours first" gate) against all
21 scenes in the qualified pool (`generation_out/_expand_scene_pool_state.json`, `reachable=True`),
loaded via the exact `hssd-hab-uncluttered.scene_dataset_config.json` our own pipeline already uses.

| scene | raw receptacles | active | distinct furniture (active) | our instance anchors: with receptacle | without | region (n/a) |
|---|---|---|---|---|---|---|
| 102343992 | 304 | 174 | 93 | 10 | 6 | 3 |
| 102344049 | 111 | 55 | 34 | 11 | 7 | 3 |
| 102344094 | 78 | 33 | 21 | 9 | 6 | 3 |
| 102344115 | 49 | 17 | 12 | 7 | 9 | 3 |
| 102344193 | 52 | 31 | 21 | 13 | 5 | 3 |
| 102344250 | 169 | 98 | 63 | 12 | 6 | 3 |
| 102344280 | 160 | 80 | 44 | 13 | 2 | 3 |
| 102344307 | 93 | 53 | 39 | 11 | 7 | 3 |
| 102344403 | 385 | 166 | 94 | 14 | 2 | 3 |
| 102344439 | 225 | 115 | 57 | 12 | 4 | 3 |
| 102344529 | 121 | 53 | 34 | 12 | 3 | 3 |
| 102815835 | 132 | 65 | 34 | 15 | 3 | 3 |
| 102815859 | 84 | 35 | 29 | 14 | 1 | 3 |
| 102816009 | 327 | 124 | 90 | 12 | 5 | 3 |
| 102816036 | 553 | 195 | 101 | 12 | 5 | 2 |
| 102816051 | 85 | 45 | 24 | 11 | 3 | 3 |
| 102816114 | 129 | 57 | 38 | 13 | 2 | 2 |
| 102816216 | 111 | 43 | 31 | 13 | 3 | 3 |
| 102816615 | 129 | 49 | 32 | 9 | 7 | 3 |
| 102816627 | 174 | 54 | 30 | 13 | 4 | 3 |
| 102816729 | 137 | 62 | 43 | 8 | 10 | 3 |
| **total** | | | | **244** | **100** | **61** |

**70.9% (244/344) of our INSTANCE-classified anchor instances have a real, curated (`active`),
matching receptacle** within 0.6m of our own anchor's resolved position (raw JSON:
`receptacle_investigation_media/receptacle_coverage_by_scene.json`, includes the full per-anchor
detail this table summarizes). The 29.1% without a match is a **methodology floor, not necessarily a
real gap**: matching was done by simple XZ-proximity between our anchor's resolved point and each
active receptacle's parent object's live translation — this misses receptacles on **articulated
links** (a fridge shelf sitting well away from the fridge body's own root translation, for instance;
`fridge` and `wardrobe` both showed "no match" in every scene and are prime suspects for exactly this
methodology gap, not a real annotation absence — not verified further this round, flagged as a
follow-up if this proceeds to GO). 287 of our anchor instances are `unbacked` in our own system
already (a pre-existing gap unrelated to receptacles, skipped from this table).

**Dataset version**: no delta found. Our copy already carries the same `scene_filter_files` used
in production (confirmed further in Section 2: OVMM's own episode files load
`hssd-hab-uncluttered.scene_dataset_config.json` too). No second `hssd-hab` checkout was pulled — the
"verify ours first" branch resolved cleanly without needing it.

## 2. OVMM overlap check

Fetched `ai-habitat/OVMM_episodes`' file listing + the small `train/episodes.json.gz` /
`minival/episodes.json.gz` index files (metadata only, no mesh/episode-content LFS blobs pulled) —
50 distinct scenes across train (38, listed per-scene under `train/content/`) + val (12) + minival (8).

**Overlap with our 21-scene qualified pool: 8 scenes** — `102344049, 102344193, 102344250, 102344280,
102344403, 102815859, 102816009, 102816216`. Notably includes **102344280**, one of the 4 scenes this
project's render batches actively use. Our primary scene, **102343992, is NOT in OVMM's set.**

For an overlapping scene (102344280, `train/content/102344280.json.gz`, 1000 episodes), inspected a
real episode directly: `scene_dataset_config: "data/hssd-hab/hssd-hab-uncluttered.scene_dataset_config.json"`
— **the same "uncluttered" variant we use**, confirmed directly, not assumed. Its
`name_to_receptacle` mapping references receptacle unique-names in the exact same
`<parent_handle>|receptacle_mesh_<hash>.<n>` format `find_receptacles(sim)` returns for our own local
copy of the identical scene. **OVMM's episode metadata does not add receptacles or filters ours
lack** — it consumes the same underlying per-scene `.rec_filter.json`/receptacle-mesh annotations
already sitting in our dataset, it doesn't ship a superset.

## 3. Object library check

Fetched `ai-habitat/OVMM_objects`' `object_categories.csv` (2,404 objects, 108 categories — metadata
only, no mesh downloads for the bulk library).

- **`keys`: no exact match, but a real, close substitute exists — `keychain` (3 candidates, 2 with
  complete habitat-ready assets: render mesh + collision mesh + `.object_config.json`)**. Downloaded
  and spawned both (`Keychain_1`, `Keychain_2`, ~50-60KB each) directly in a real sim and measured
  real-world AABB: **0.128m and 0.130m max extent** — within 8% of our own
  `asset_candidate_acceptance._CATEGORY_TARGET_M["key"] = 0.12`, comfortably inside its 20% scale
  tolerance. Both would have PASSED the scale check that the 5 rejected Objaverse candidates failed.
  This supersedes the closed Objaverse keys finding (0/5 passed, `asset_coverage.md`) — a real,
  differently-sourced candidate exists and has not been run through the full mask-predicate
  acceptance pipeline. Per the round's constraint, **not promoted this round** — flagged for the
  normal `asset_candidate_acceptance.py` pass if this proceeds to GO.
- **`wallet`: no match at all**, in any of the 108 categories (checked directly against the category
  list, not just a name guess). The `wallet` gap stands as previously documented — OVMM does not
  change that finding.
- **`cup`: 87 candidates**, several sourced from HSSD itself (`train_val/hssd/configs/objects/
  <hash>.object_config.json` — the same asset-hash convention our own `SPAWNABLE_ASSET_BY_CATEGORY`
  uses), not just AI2-THOR/ABO/GSO. Not deep-checked for scale this round (cup already has a working,
  if sometimes `mask_too_small`, asset in our pipeline — this is a real, promising lead for that
  existing finding, not a new gap) — flagged, not resolved.

## 4. snap_down spike

**Setup**: scene 102343992, the dining table's one active receptacle (matched to our own resolved
`dining.table` anchor position). Two real, currently-failing trace events from
`102343992_family_with_kids_state`'s actual built artifact:

| label | category | our builder's real recorded status | snap_down (this investigation) |
|---|---|---|---|
| `phone_1` (t=7.501, `kitchen.range_hood -> dining.table`) | phone | `SURFACE_FULL` (no realized_pose at all — a real gray placeholder card in production today) | **succeeded on attempt 2/40**, rendered `OK` via our own spectator camera + mask predicate (1.7% frame area) |
| `cup_1` (t=7.32→ same burst window, `kitchen.range_hood -> dining.table`) | cup | `SURFACE_FULL` | **succeeded on attempt 2/40**, rendered `OK` (1.5% frame area) |

Both used the exact real asset our own `SPAWNABLE_ASSET_BY_CATEGORY` already assigns to these
categories (`phone`, the landline substitute; `cup`, the drinkware substitute — same known issues as
today, unrelated to this test), placed via `Receptacle.sample_uniform_global` + `snap_down`
(real-mesh gravity-projection + collision rejection, not our circular-footprint occupancy
approximation), then rendered and mask-checked through **our own, unmodified**
`embodied.sensor.spectator_viewpoint` + `evaluate_object_mask` — the exact functions production
would use, not a separate/parallel check. Renders: `receptacle_investigation_media/
phone_1_snap_down.png`, `cup_1_snap_down.png`. Both show a visually recognizable dining table (round
tabletop, pedestal leg, chairs in frame) — a clearer "this looks like a dining table" result than
several of the current pipeline's own OK dining.table renders reviewed earlier this session, though
that comparison is incidental, not the point of this test.

Root cause this directly confirms: our `compliance_place_on_surface`'s occupancy model is a
**cumulative, never-shrinking, whole-day list of circular footprints** (see the "dining table
clutter" discussion earlier this session — the actual finding was a generation-side burst-arrival
problem, not a placement-search bug) — `SURFACE_FULL` there reflects an accumulated, monotonic
booking list, not a real-time snapshot of what's physically on the table right now. `snap_down`
doesn't have this problem by construction: it queries the **live collision state of the actual scene
right now**, so an object whose real would-be neighbors have already moved on (even if our own
bookkeeping never freed their slot) places successfully. This is a structural advantage of the
receptacle+snap_down approach over our current occupancy list, independent of the margin/footprint
tuning question raised earlier.

**Does it handle `PLACEMENT_INFEASIBLE`?** Checked the real `PLACEMENT_INFEASIBLE` events in the same
artifact (`stool_1 -> kitchen`, `potted_plant_1 -> living_room` / `-> kitchen`) — **all of them are
REGION anchors** (open-floor placement), not instance/surface anchors. Receptacles are specifically
furniture-surface/container annotations; they have **no bearing on floor-region placement at all**.
Every `PLACEMENT_INFEASIBLE` observed this round is out of scope for a receptacle-based fix — this is
a firm boundary, not a partial-coverage caveat: `SURFACE_FULL` is receptacle territory,
`PLACEMENT_INFEASIBLE` (region anchors) is not.

## 5. gfx-replay note

habitat-sim's `gfx_replay_manager` (`sim.gfx_replay_manager.add_user_transform_to_keyframe` /
`extract_keyframe()`, used by habitat-lab's `rearrange_sim.py`/`utils.py:write_gfx_replay`) records a
scene-graph keyframe — object transforms/visibility at a point in time — to a serializable
`.replay.json`, replayable later via a `ReplayRenderer` without needing the full physics/object-
management state reconstructed. This maps cleanly onto our own build/render split in principle: the
builder could record a keyframe per realized event instead of (or alongside) writing `realized_pose`
tuples, and the render job would replay+render instead of re-materializing objects into a live sim.
**Cost/benefit is not favorable enough to pursue now**: our `RealizedPose` (a plain (x,y,z) + identity
rotation, per event) is already a complete, human-readable, diffable record of the one thing we
actually need (final resting pose) — a gfx-replay keyframe would carry substantially more state
(full scene-graph transforms, asset references) for no capability our render job is currently missing
(materialization from a plain pose tuple already works, per this session's own BIND-relocation fix).
It would matter if this project ever needed multi-frame animation replay (an object's full motion
path, not just before/after snapshots) — not a current requirement. **No implementation, this round
or recommended immediately** — worth a second look only if animated (not snapshot) rendering becomes
a real requirement.

## What gets replaced (if GO is acted on)

- **Placement internals**: `build_realized_day.py`'s `compliance_place_on_surface` (INSTANCE anchors
  only — `compliance_place_region`, for REGION anchors, is untouched, receptacles don't apply there)
  would be replaced by `Receptacle.sample_uniform_global` + `snap_down`, with our existing
  `_SURFACE_EDGE_MARGIN_M`/`_PACKING_MARGIN_M`/occupancy-list bookkeeping retired in favor of live
  collision state. The `PLACEMENT_OK` / `PLACEMENT_SURFACE_FULL` outcome vocabulary stays (snap_down's
  own True/False maps directly onto it) — no artifact schema change.
- **Anchor vocabulary aliasing**: `classify_anchor`'s "instance" branch would need a per-anchor
  receptacle lookup (this round's `find_active_receptacles_for_anchor` pattern) alongside the
  existing SLOT_ANCHORS/STATEFUL_FURNITURE resolution — additive, not a replacement of the anchor
  strings themselves (anchor names like `"dining.table"` stay the semantic vocabulary; only how a
  concrete (x,y,z) gets resolved for them changes).
- **Replay path**: no change recommended (see Section 5) — render job keeps reading plain
  `RealizedPose` tuples from the artifact.
- **What regenerates under a new fingerprint**: every already-built `realized_day.json` artifact
  (`data/realized_days/*.json`) — placement outcomes would shift for real (this round's own spike
  demonstrates real events flipping `SURFACE_FULL -> OK`), so `_BUILDER_VERSION`/`_code_hash()` must
  bump and every folder rebuilds. No manifest/generation-side regeneration needed — the trace events
  themselves are untouched.
- **Rough effort**: 2-3 focused sessions. Swapping `compliance_place_on_surface`'s internals is
  contained (one function, well-covered by existing tests + the gold set); the larger cost is
  re-running the pool-wide build and re-verifying the gold set/attribution table against the new
  placement outcomes, plus resolving the fridge/wardrobe articulated-receptacle question flagged in
  Section 1 before trusting STATEFUL_FURNITURE anchors specifically.

## Cleanup

`scripts/investigations/` (this round's `receptacle_probe.py`, `receptacle_coverage.py`,
`snap_down_spike.py`, `run_snap_down_spike.py`) is disposable per the round's own constraint. Left in
place pending owner review of this report — the raw per-scene JSON and both spike renders it produced
are the evidence this report cites, so deleting the scripts now (while keeping only prose) would make
the numbers above unverifiable without re-running from scratch. Delete after this report is reviewed,
or move under a permanent path (e.g. `scripts/` proper) if GO is acted on and the placement-internals
swap begins for real. The `habitat_lab_recept` conda env and the now-initialized `third_party/
habitat-lab` submodule are likewise left in place — needed again immediately if GO proceeds, cheap to
remove (`conda env remove -n habitat_lab_recept`; the submodule can be deinitialized) if NO-GO.
