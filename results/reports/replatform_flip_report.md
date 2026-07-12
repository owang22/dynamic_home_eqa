# Replatform round — flip report + corrected receptacle coverage

Enacts the GO from `receptacle_investigation.md`. Covers items 1-4 of the Replatform + Pool Build
spec. Items 5-6 (pool-wide build, chunked generation) are NOT started — this document is the gate
before item 5, same convention as the Spectator Camera round.

## Environment decision (item 1)

New dedicated conda env `habitat_lab_recept` (python 3.9.2, `habitat-sim=0.3.3`, `habitat-lab` core —
not baselines). **The builder (`scripts/build_realized_day.py`) now runs under `habitat_lab_recept`;
everything else (render job, embodied/, all tests) stays on `explore-eqa` (`habitat-sim=0.3.1`),
untouched.** Confirmed directly before committing to the split: `find_live_object_at_xz`/
`get_world_aabb` (the builder's own pre-existing functions) produce identical real-world results
under 0.3.3. The `realized_day.json` artifact is plain JSON, fully habitat_sim-version-agnostic once
written — the render job reading it back under explore-eqa is unaffected. `third_party/habitat-lab`
(a previously-uninitialized git submodule) was initialized.

## Item 1: INSTANCE-anchor placement replatform

`compliance_place_on_surface`'s circular-footprint occupancy list is retired. Placement is now
`Receptacle.sample_uniform_global` + `snap_down` against LIVE collision state, matched to the
anchor's furniture by exact `parent_object_handle` join (not the investigation's looser 0.6m
XZ-proximity heuristic — see item 3). Determinism preserved: `sample_uniform_global` draws from
Python's global `random`/`np.random`, reseeded from `sha256(label:t:receptacle_index:attempt)`
before every sample (same hash-seeding convention `_packing_candidates`/`deterministic_radial_offset`
already use elsewhere) — same (scene, day folder, builder version) still produces a byte-identical
artifact.

**Real bugs found and fixed while building this** (not assumed correct, verified live):
- **Sensor eye-offset double-counted** in the render job (unrelated to placement, found via the
  original snap_down spike's render step) — already fixed in the investigation's own spike code,
  carried forward correctly into production (render job unchanged this round).
- **BIND-category collision-vs-receptacle mesh divergence (bedroom.bed).** Real HSSD furniture ships
  TWO separate meshes per receptacle: `collision_asset` (`*.collider.glb`, what `snap_down`'s
  gravity-projection raycasts against) and the receptacle's own `filteredSupportSurface.glb` (the
  annotated placement surface). Confirmed directly by reading the real `object_config.json` and
  casting the exact failing ray: for this scene's bed, the ray from a valid receptacle-surface sample
  point passes straight through where the mattress should be and hits the floor — the bed's collider
  mesh does not extend up to cover its own annotated support surface. Every real event landing on
  `bedroom.bed` now fails `PLACEMENT_SURFACE_FULL`. **This is a real, dataset-level limitation of the
  receptacle+snap_down approach, disclosed here, not patched around** — confirmed NOT bed-specific in
  general (every receptacle-bearing HSSD object uses this same dual-mesh structure; `kitchen.counter`
  in a different scene shows the identical config pattern), but whether it actually causes a failure
  is asset-specific and unpredictable without checking each one directly.
- **A real segfault** (item 2, see below) — `sim.pathfinder.snap_point` on a build sim with no
  navmesh recomputed crashes natively (no Python traceback) rather than raising. Root-caused and
  fixed, not worked around.

## Item 2: REGION-anchor placement fix

`compliance_place_region` replatformed the same way: candidates are now navmesh-snapped (via
`world.snap_to_navmesh`, not `sim.pathfinder.snap_point` directly — see the segfault note below) and
validated via `snap_down` against the real stage/floor + live collision, replacing the same
circular-footprint occupancy list item 1 retired for instance anchors. `_ANCHOR_TOLERANCE_M`'s
distance-to-point invariant is unchanged — region placement still has to land near where the trace
actually said, that was never part of the booking-list bug.

**Real segfault found and fixed**: the build sim (`_make_render_sim`, reused from the render job)
never calls `recompute_navmesh` — confirmed already known for this project (scene 102343992 ships no
baked navmesh at all, see `embodied/world.py`'s own module docstring). Calling
`sim.pathfinder.snap_point` on that uninitialized pathfinder crashes the process natively (`Fatal
Python error: Segmentation fault`, confirmed via `faulthandler` — no catchable Python exception).
Fixed by routing navmesh snapping through `world.snap_to_navmesh` instead — `world`'s own separate
sim is already correctly `recompute_navmesh`'d with this project's real `NavMeshConfig` (see
`world.py`). The two sims load the same scene/coordinate system, so a position `world` resolves is
equally valid hand-off to the build sim's own object/collision state afterward.

Residual `PLACEMENT_INFEASIBLE` rate after the fix, this round's 3 rebuilt folders: 15/312 shared
events (down from 20 pre-replatform) — but NOT uniformly better: 102343992 and 102344049 dropped to
zero; 102344022 (more region-heavy: 40 of its 84 instance+region anchors are REGION) went from 10 to
15. `living_room.open_floor` shows real churn in both directions (4 ok→infeasible, 5 ok→surface_full,
1 infeasible→ok) — expected: navmesh-snapping is a stricter, more honest walkability bar than the old
"raycast finds some surface" check, so some previously-accepted candidates that were never really
walkable now correctly fail, while some previously-rejected ones (blocked only by the retired booking
list) now succeed.

## Item 3: corrected receptacle coverage

The investigation's Section 1 table (70.9%, 244/344) used a 0.6m XZ-proximity heuristic — looser than
what production actually does (exact `parent_object_handle` join). Re-ran coverage with the EXACT
production method across all 21 qualified scenes:

**Corrected coverage: 60.1% (200/333 instance anchors)** — a real, honest DOWNWARD correction (the
looser heuristic was producing false positives, e.g. it originally reported `fridge` as having a
receptacle in the anchor's own scene; the exact join shows zero). Full per-scene breakdown:
`receptacle_investigation_media/receptacle_coverage_exact_match.json`.

The investigation's own hypothesis for the uncorrected gap ("articulated-link receptacles missed by
root-transform matching") is **not the actual cause** — confirmed directly: this dataset variant has
**zero articulated objects** (`sim.get_articulated_object_manager().get_num_objects() == 0` for scene
102343992). The real reasons, checked concretely for the two prime suspects:
- **fridge**: zero receptacles authored anywhere in this dataset for this furniture instance —
  confirmed by an exact-handle join against the raw, unfiltered receptacle set (not just the active
  one). A genuine annotation gap, not a matching bug.
- **wardrobe**: one receptacle DOES exist (confirmed in the raw set), but it is explicitly
  `manually_filtered` in the scene's own `.rec_filter.json` — a deliberate human-curator exclusion
  (likely the wardrobe's top surface, not its interior). Also not a matching bug.

11 additional "instance" anchors (across all 21 scenes) have NO live furniture object at all
(`find_live_object_at_xz` finds nothing near the resolved position) — a different, more severe gap
than "furniture exists but has no receptacle," handled the same way `PLACEMENT_ANCHOR_UNBACKED`
already does elsewhere in this pipeline.

## Item 4: asset follow-ups

- **keys → `keychain`**: real, close, not yet passing (fails `mask_off_center`, not scale/support).
  `NO_ASSET_CATEGORIES` unchanged.
- **wallet**: FINAL. Checked against OVMM's full 108 categories, no match. Combined with the closed
  Objaverse finding, two independent sources checked, nothing found either time.
- **cup**: PROMOTED. `SPAWNABLE_ASSET_BY_CATEGORY["cup"]` now points to a genuine HSSD-native mug
  asset (`547c0a77b74f52c4e6c4a0a52f14f6c9c7a57b49`, already in our local dataset, no download) —
  measured 5.7% frame area vs. the old drinkware substitution's 0.94%, both technically passing but
  the new one far more legible. `CATEGORY_SUBSTITUTED` is now empty.

Full detail + concrete numbers for all three: `asset_coverage.md`'s new "Round 4" section.

## Final aggregate (3 rebuilt location folders, all of items 1+2+4 applied, shared events only)

| status | before (v1) | after (v2 replatform) |
|---|---|---|
| ok | 147 | 108 |
| surface_full | 50 | 94 |
| placement_infeasible | 20 | 15 |
| anchor_unbacked | 40 | 40 |
| no_asset_for_category | 33 | 33 |

123 flips total. Per-anchor (all flips, not just net): `bedroom.bed` 31 (all ok→surface_full, the
diagnosed collision-mesh gap), `fridge` 18 (all ok→surface_full, the confirmed real annotation gap),
`dining.table` 15 (13 surface_full→ok, 2 ok→surface_full — net real win, the investigation's own
headline case), `kitchen` 12 (region anchor: 5 infeasible→ok + 7 surface_full→ok, all wins),
`office.desk` 10 (9 surface_full→ok, 1 ok→surface_full — net win), `living_room.open_floor` 10 (mixed,
see item 2), `kitchen.counter` 10 (all ok→surface_full — same collision/receptacle-mesh-divergence
class as bedroom.bed, not yet individually root-caused), `bedroom`/`living_room`/`dining_room`/
`outdoor`/`bedroom.nightstand`/`living_room.shelf` (≤6 each, mixed or small).

**Net honest read**: this is not a uniform win. Real anchors with good receptacle/collision-mesh
alignment (dining.table, office.desk, kitchen) genuinely improved and are more trustworthy than the
old booking-list system ever was (live collision, not a leaky accumulator). Real anchors with a
collision/receptacle-mesh gap (bedroom.bed, and apparently kitchen.counter — not yet individually
confirmed via the same direct raycast diagnosis bedroom.bed got) or no annotation at all (fridge)
regressed to an honest failure instead of the old system's permissive-but-physically-ungrounded
success. Per the standing rule, this is reported as a real trade-off, not smoothed over.

## Verification

- Gold set: all 8 items green (4 items' expected values updated with the specific root cause each
  traces to — bedroom.bed collision-mesh gap or fridge's real annotation gap — documented inline in
  `gold_set.py`, not silently accepted).
- Full suite (explore-eqa): 702 passed, 1 skipped (the one live test requiring habitat-lab, which now
  correctly skips under explore-eqa and passes under habitat_lab_recept — confirmed both ways).
- All 4 folders (`102343992_family_with_kids[_state]`, `102344022_family_with_kids`,
  `102344049_family_with_kids`) rebuilt under the new `_BUILDER_VERSION`
  (`realized_day_v2_receptacle`) + updated code hash.

## Cleanup

`scripts/investigations/receptacle_probe.py`, `receptacle_coverage.py`, `snap_down_spike.py`,
`run_snap_down_spike.py`, `receptacle_coverage_exact.py` are disposable per the round's own
constraint — kept for now since this report's numbers cite their raw output directly
(`receptacle_investigation_media/`); `resolve_furniture_receptacles` (the one piece that mattered)
is already promoted into `build_realized_day.py` proper. Delete the investigation scripts once this
report is reviewed. `habitat_lab_recept` env + the now-initialized `third_party/habitat-lab`
submodule are kept — required again for every future build.

## Stop

Per the spec's own gate: this is where item 1-4 work ends for owner review before item 5 (pool-wide
build). Items 5 (pool-wide build + full render batch + owner 10-item review) and 6 (chunked
LLM-in-the-loop generation) are untouched.
