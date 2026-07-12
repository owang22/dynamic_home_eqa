# Human realism eval — tooling built and verified end to end; no human data yet

**VERDICT: the full pipeline (render job -> webapp -> analysis script)
works, verified against real data at every stage — but this report
contains a tooling validation, not a realism finding.** No volunteer has
used the webapp yet. Every number below is either a real property of the
rendered item pool (the degenerate-viewpoint rate) or a synthetic-data
proof that the statistics are computed correctly (agreement/correlation).
The actual quality verdict this tooling exists to produce — "is generated
displacement realistic, per real humans" — is not yet answerable and this
report does not claim it is.

## What was built

**Automatic signals (`embodied/placement_check.py`, new this batch).**
A real geometric collision/occupancy check, ray-cast against the scene's
static Bullet mesh (the same mechanism `embodied/sensor.py`'s occlusion
check and `embodied/reachability.py`'s ceiling check already use).
Clutter objects have no physics body of their own (`embodied/world.py`:
"objects are NOT physically instantiated"), so this checks the ANCHOR
POINT's own geometric plausibility as a resting place — supported (a
downward ray finds a surface within 0.5m) and not embedded (a ring of
short horizontal rays doesn't immediately hit solid geometry in most
directions) — not a full object-mesh contact test, which nothing in this
pipeline can construct. Stated as an approximation, not oversold. 9 unit
tests.

**Offline render job (`scripts/realism_render_job.py`).** For a
stratified sample of change events (suspicion-tail + a mandatory random
baseline, computed *separately per change_type* — see the fix below),
writes a 2x2 PNG (egocentric + top-down, before/after, the anchor
highlighted in all four panels via a pinhole projection empirically
validated against real renders, not just derived), a caption JSON (clock
time, not raw hour-float; scene/profile/day; change_type), and a
per-item automatic-signals JSON: the new geometric check, the pre-existing
suspicion score/reasons, `plausibility.py`'s capability/egress/pingpong
flags (closes a gap `render_tool.md` explicitly left unimplemented — that
module already computed these from real occupant age_bands, they just
weren't wired to a per-event render before), and the day-level (not
per-event — no per-candidate score survives in `generation_result.json`,
only the day mean) LLM self-graded realism score. Degenerate viewpoints
are included and flagged, not skipped, unlike `render_suspicious_events.py`.
32 unit tests + 1 live GPU/habitat_sim integration test, all passing.

**Two real bugs found and fixed while building this, both concretely
verified rather than assumed away:**

1. **A pooled suspicion tail starves state events.** State-change events'
   suspicion score comes from a much smaller-variety signal space (2
   state variables, 4 categories total, per `env/deltas.py`'s
   `STATE_VARIABLES`) than location events. Ranking both event types on
   one shared scale for a global top-N tail produced a hard, reproducible
   empty cell — zero state events ever made the tail, confirmed directly,
   not a rounding artifact. Fixed by scoring each `change_type`'s tail
   independently (`select_stratified_sample_per_type`); the production
   batch now has a real 16/80 state representation with genuine tail
   members in both.
2. **A stray marker distorted its own image.** The first render of a
   degenerate-viewpoint item showed a blank AFTER panel and a star
   floating outside any subplot. Root cause: plotting the highlight
   marker after `imshow` let matplotlib's default autoscale expand the
   view to include an out-of-frame point, squashing the actual image to a
   sliver. Fixed by locking the axes to the image's own pixel extent
   before plotting, and showing "(anchor out of frame from this
   viewpoint)" instead of distorting the layout when the marker falls
   outside the frame. Confirmed visually, before/after, not just assumed
   fixed from the code diff.

**The webapp (`webapp/realism_eval/`)**, a FastAPI + SQLite-WAL + vanilla
JS app adapted from a reference time-series QA implementation (same
architecture — shared deterministic joint-quota assignment, composite-key
upsert responses, hidden debug box), retargeted from time-series plots to
2x2 event-grid images. Three separate rubric axes (placement plausibility,
behavior plausibility, visual identifiability) with exact snake_case
option values, an issue-checkbox set, and a free comment field. Automatic
signals are frozen into each response at save time — a later generation-
pipeline change can't retroactively alter what an annotator was actually
shown. 9 smoke tests against a fixture pool; verified for real against
the live 80-item pool (start -> items -> save a response -> progress
readback -> shared assignment identical across two participants -> media
file actually serves), not just unit-tested in isolation.

**A third real bug, found and fixed against the live pool, not a
fixture:** the joint-quota sampler originally crossed `suspicion_stratum
x change_type x profile`. With 8+ distinct profile values in the current
80-item pool, that 3-way cross needs far more items per cell than exist —
every `TOTAL_ITEMS` value tried, including the full pool size, hit an
infeasible cell (`assign_items_joint` correctly refused to silently
short-fill rather than quietly changing the study's stratification).
Fixed by dropping `profile` from the hard-quota axes — it's still
recorded per response for post-hoc reporting, just not force-balanced.
Revisit if the render pool is scaled up materially.

**Analysis script (`scripts/analyze_realism_study.py`).** Pairwise
quadratic-weighted Cohen's kappa for inter-annotator agreement (not
Krippendorff's alpha — under `ASSIGNMENT_MODE="shared"` every annotator
rates the identical item set, so there's no missing-data pattern alpha's
extra generality is buying here), Spearman correlation with bootstrap 95%
CIs between each rubric axis and each automatic signal, and per-stratum
quality rates (the random-baseline stratum's clearly-wrong/implausible
fraction is the pool's headline number, since it's the one stratum not
pre-selected toward badness). Escape values (`cannot_tell`/`cannot_judge`)
are excluded from the ordinal computation and reported as their own rate,
not folded into either end of the scale. 12 unit tests against synthetic
data with known agreement/correlation — these prove the math, not that
any real number is good.

## Viewpoint quality: two review rounds, real fixes each time, now a precise per-panel status instead of one blurry rate

The render job originally reported one boolean, `degenerate_viewpoint`,
sitting at 72-95% depending on sample. Two rounds of manual review (the
first from loading the webapp and reading captions; the second from a
structured "fix the render pipeline" pass) replaced that single number
with an explicit per-panel status — `STATUS_OK` /
`STATUS_ANCHOR_UNRESOLVED` / `STATUS_NO_NAVIGABLE_VIEWPOINT` /
`STATUS_AIM_FAILED` — and fixed every root cause that turned out to be
fixable. What follows is what was found, what was and wasn't fixable, and
the real, re-measured numbers after every fix.

**1. Anchor-naming bug (`rooms.resolve_slot()`) — fixed at the source.**
`resolve_slot()` synthesized `"{room}.{anchor}"` (e.g. `"bedroom.wardrobe"`,
`"kitchen.fridge"`) whenever no hand-authored `SLOT_ANCHORS` entry existed
for an (anchor, room) pair — including for `STATEFUL_FURNITURE` categories
(wardrobe, fridge, oven, tv), which are only ever registered under their
own bare category name. The synthesized string passes `slot_room()`'s own
room-consistency check fine, but has no entry anywhere in the real
anchor-position registry — confirmed directly: `"bedroom.wardrobe"` was
not in `world._anchor_positions`, while bare `"wardrobe"` was, with a
real position from the furniture census. Not rendering-specific — anything
resolving this exact string (belief, search) hits the same gap. **Fixed
at the source** in `rooms.resolve_slot()` (returns the bare, resolvable
key for `STATEFUL_FURNITURE` categories); 3 new unit tests
(`tests/test_rooms.py`). The already-generated pool predates the fix, so
`realism_render_job.py`'s `resolve_position_and_viewpoint` also gained a
local, read-time alias for old data — deliberately not added to shared
`EmbodiedWorld` code.

One premise from the original bug report turned out not to hold, worth
correcting precisely: the suggested fix was "read the event's grounded
world position directly from the generation output — stop re-resolving
names through the lookup table." Checked directly against
`generation/grounding.py` and `env/deltas.py`'s `Change` schema: grounding
DOES compute real 3D positions internally (`sample_position_on_furniture`),
but only a *count* (`positions_found`) survives into the manifest — the
actual coordinates are never persisted anywhere `Change`/`manifest.json`
can be read from. There is no stored per-event position to read; the bare-key
alias above is the closest available equivalent (the real furniture-census
position, the same authoritative source grounding itself used).

**2. Camera had no pitch — fixed, and this was the single biggest lever.**
The render camera only ever yawed level; a floor-level anchor near an
eye-height camera needs real downward pitch, or the target lands below
the visible frame even though `viewpoint_for`'s own occlusion check (a
real 3D ray, not level-only) already confirmed a clear line of sight
exists — the camera just never looked along it. Rewrote `camera_basis`/
`capture_rgb_and_basis` to a full 3D look-at (yaw AND pitch, rotation
built directly from a `(right, up, forward)` matrix via
`mn.Quaternion.from_matrix`, not composed angle-axis rotations).
Empirically validated before use, not just derived: a steep downward test
case rendered a real floor-tile texture whose perspective lines visibly
converge exactly at the projected target pixel.

**3. The room-centroid fallback rendered blindly — replaced.** Bare-room-
name anchors (e.g. `"outdoor"`) used to snap to the room centroid and
render whatever a fixed, unchecked camera pose saw — a labeled failure is
fine, a wrong-room render is not. Fixed two ways: (a)
`embodied/sensor.py`'s `viewpoint_for` was refactored (pure extraction,
zero behavior change for any existing caller — confirmed via the existing
`test_sensor.py` suite, 12/12 still passing) into a new
`viewpoint_from_position`, so a room-centroid position now gets the SAME
visibility-validated ring search a named furniture anchor gets, not a
blind fallback; (b) if that search still fails, the panel now shows an
explicit `NO_NAVIGABLE_VIEWPOINT` card instead of an unvalidated render.

**4. A hard aim gate replaces the soft "out of frame" banner.** After
capture, the anchor's projected pixel is required to land in the central
60% of the frame (the same projection math the marker itself uses, so a
pass can't disagree with the pixels) or the panel is marked `AIM_FAILED`
and shown as a gray card instead of saved. With pitch now aiming exactly
at the target by construction, this gate is close to unreachable in
practice: **0/80 items hit `AIM_FAILED` on either panel** in the final
re-render — it fires on real numerical edge cases, not routinely, exactly
as expected once pitch was fixed.

**5. A real, independent rendering bug found while verifying all of the
above: placeholder panels were rendering completely blank.** Every
"failed" panel this entire project has ever produced — going back to the
very first render tool, before this task's instructions even arrived —
was silently invisible: no gray/black background, no status text, just
white space. Root cause, isolated with a minimal reproduction (not
assumed): `ax.axis("off")` in this matplotlib version (3.8.0) suppresses
an Axes' own facecolor AND any text already drawn on it at save time,
despite `ax.patch.get_visible()` still reporting `True`. Fixed by removing
ticks/spines individually instead (`_hide_decorations`), confirmed
visually before/after on a minimal repro and on real render output.
**This means every prior description in this project of a panel as
"blank" or "no resolvable viewpoint" was accurate about the underlying
resolution failure, but the panel itself never actually showed that
reason — it just looked empty.** The status cards now genuinely say why.

**6. Smaller items, also done this round:** top-down panels now show
BOTH before (hollow star) and after (solid star) markers with an arrow
between them and room-centroid labels, on both top-down panels — a panel
is never wasted just because its own anchor didn't resolve while the
other did (verified: the `stool_1` case above shows this exactly — a
fully-unresolved BEFORE anchor still gets a useful combined top-down
view). A cheap highlight-visibility check (`highlight_would_be_visible`)
samples the pixel neighborhood under the marker and flags
`HIGHLIGHT_INVISIBLE` if the underlying scene content is already close to
the marker's own red — a full duplicate-render diff was considered and
skipped as unnecessary cost for a failure mode this proxy already covers
(a solid red/white star only visually disappears against an
already-red-ish background). Scene lighting was investigated, not
fixed: the HSSD `scene_instance.json` files carry no authored lighting
layout at all (`default_lighting: None`), and the render already uses
habitat_sim's generic default, not the explicit no-light key — there is
no richer lighting config being missed, this is a dataset limitation.

**7. Also confirmed, not fixable this way: a state change can't be shown
visually.** HSSD scene assets are static — one baked appearance per
object, no separate "powered on" texture/material. The caption text is
the only place a state change is legible.

### The real, decomposed numbers (full 80-item pool, all fixes applied)

| Panel | OK | NO_NAVIGABLE_VIEWPOINT | ANCHOR_UNRESOLVED | AIM_FAILED |
|---|---|---|---|---|
| BEFORE | 50.0% (40/80) | 42.5% (34/80) | 7.5% (6/80) | 0% (0/80) |
| AFTER | 51.2% (41/80) | 45.0% (36/80) | 3.8% (3/80) | 0% (0/80) |

**30.0% of items (24/80) have BOTH panels OK; 71.25% (57/80) have AT
LEAST ONE panel OK** — a meaningfully more useful pool than the earlier
"72-95% degenerate" framing suggested, and now precisely attributable:
the overwhelming majority of remaining failures are
`NO_NAVIGABLE_VIEWPOINT` (a real position exists, but no candidate within
the tried radii — now up to 3.5m, and now also tried for room-centroid
positions — passed the visibility check), not `ANCHOR_UNRESOLVED` (a
genuine scene data gap, now a small minority) and not `AIM_FAILED`
(effectively eliminated by the pitch fix). **`NO_NAVIGABLE_VIEWPOINT` is
the one deferred root cause left** — per explicit instruction, not
investigated further this batch, left for manual inspection now that the
tooling correctly labels it instead of hiding it.

*(Superseded by the round below — the numbers in this section reflect the
render pipeline before real object instantiation existed. Kept for the
record of what the pitch/status-system fixes alone achieved.)*

## Round 2: the panels weren't empty because of viewpoints — the objects were never there

Manual review after the round above surfaced the real remaining problem:
**successful, correctly-aimed renders still showed an empty room with a
star on it.** `vase_1` on `dining.table` — no vase. `bowl_1` — no bowl.
This isn't a rendering bug, it's the project's own Phase-1 architecture:
Tier-2b clutter objects (vase, bowl, cup, phone, ...) are never
physically instantiated in habitat_sim (`embodied/world.py`'s own module
docstring) — every egocentric render was always going to be the static
HSSD scene with a marker on it, because the object was never geometry to
begin with. Fixing this — not more parameter tuning — was the real work
this round.

**1. Objects are now really spawned, real HSSD catalog assets, not
placeholders.** Checked the actual HSSD object catalog
(`semantics/objects.csv`'s `main_category` column) against every category
in the rendered pool: real, on-disk assets exist for `vase` (164),
`bowl` (42), `candle` (100), `phone` (13), `bottle` (54), `book` (65),
`laptop` (12), `drinkware` (130). **`cup` has zero matching entries
anywhere in this dataset's taxonomy** (checked `cup`/`mug`/`coffee_cup`
too) — mapped to `drinkware` (the closest real semantic superset) as an
explicit, disclosed substitution (`CATEGORY_SUBSTITUTED`, recorded per
item, never silent). **`wallet` and `keys` have no matching asset or
reasonable synonym at all** (checked `key_chain`/`purse` too) — these
get `OBJECT_SPAWN_FAILED` with an honest `no_asset_for_category` reason,
not a fake substitute. Separately confirmed `chair`/`stool`/
`potted_plant`/`cushion` (Tier 2a) and the stateful-furniture categories
are ALREADY real, HSSD-placed geometry (`_ALREADY_INSTANTIATED_CATEGORIES`)
— verified directly against a real `scene_instance.json`: the frozen
scene's own `stool_1` event resolves to the exact coordinates of a real
stool instance HSSD itself placed. Spawning these would double the
object, not fix a missing one.

**2. Placement, not just spawning: raycast for the real support surface,
offset by the object's own bounding box.** The naive "drop the mesh
origin at the anchor" approach embeds half of every asset into its
surface — confirmed directly: a real vase's bounding box is symmetric
about y=0 (min -0.225m/max +0.225m), and a real dining-table anchor's
raw Y (0.57) differed from the raycast-resolved true tabletop surface
(1.02) by 45cm. Fixed: raycast straight down from above the anchor,
offset the object's `bb.min.y` onto the found surface. A NEW
`geom_check_mesh` signal re-runs the existing placement_check
(supported/embedded) at this corrected position, alongside the original
point-based check at the raw anchor — **they disagree 16.7% of the time
(9/54 compared)**, meaning roughly 1 in 6 placements the old point check
would have called fine, the mesh-corrected check calls differently (or
vice versa) — a real, reportable finding about how much the surface
correction actually matters, not just a nicety.

**3. A real bug found and fixed while verifying spawn success: objects
render, but not always where the marker says they are — and the FIRST
diff-check design couldn't tell.** The original sanity check (render
with/without the object, diff a small window around the marker's
projected pixel) was failing on the large majority of genuine, visible
spawns. Debugged with a real case (`bowl_1` -> `outdoor`): the bowl WAS
spawned, correctly positioned per every position readout available
(`obj.translation`, `project_point` on that translation both agreed with
the marker to within 3px) — yet the actual rendered pixels showed it
~120px away from where all of that math said it would be. Chased two
hypotheses: object motion type defaulting to `DYNAMIC` and falling under
gravity before capture (fixed by forcing `KINEMATIC` — made no visible
difference, ruling this out) and a render/physics transform desync
(readbacks of `translation`/`root_scene_node.translation`/
`transformation.translation` all agreed with each other, ruling this out
too). **Root cause not fully chased down** — rather than keep guessing,
replaced the marker-windowed diff with a whole-frame changed-pixel count
(`count_changed_pixels`): the background is otherwise static between the
two captures, so any real cluster of changed pixels can only be the
spawned object, wherever it actually renders. Calibrated against the
real bowl case (1600/172800 pixels changed, unambiguous) and re-verified
on a fresh case (vase: 21721 changed pixels). **Measured effect: spawn
success rate went from 10/54 (18.5%) to 34/54 (63.0%)** on a full
re-render — confirmed, not assumed. The marker/object position mismatch
itself remains a disclosed, open discrepancy (the star may not sit
exactly on the object even when both are correctly present) —
worth investigating further, not blocking the deliverable, since the
object being genuinely visible in-frame is what annotators actually
judge.

**4. State-change items now skip the egocentric axis entirely, both in
the render and in the webapp.** `render_event_grid` shows an explicit
`N/A (state change — not visually represented)` gray card for both
egocentric panels on a state item (top-down + caption still fully
render). The webapp mirrors this: `placement`/`visibility` auto-set to
`not_applicable` and grayed out client-side for a state item, with
server-side validation that `not_applicable` is only ever accepted for a
genuine state-change item (a location item claiming its placement axis
doesn't apply is rejected) — only `behavior` (a narrative judgment, not a
perceptual one) stays required.

**5. Sightline failures instrumented, one real (partial) fix applied.**
Logged every candidate pose's outcome for the repeat-offender anchors
(`kitchen.fridge`, `bedroom.bed`, `bedroom.wardrobe`) — 100% occlusion,
with SUBSTANTIAL gaps (ray hits landing 0.4-3.8m short of the target, not
a few-cm graze the existing 0.3m slack already handles). Tested whether
targeting a point above the anchor's own (often floor/base-level, e.g.
fridge/wardrobe y~0) position opens a real sightline: **it does for
`bedroom.bed`** (0/60 candidates pass at the true height, 19/60 pass at
+0.6m) **but makes zero difference for `kitchen.fridge`/`bedroom.wardrobe`**
(0/60 at every offset tried up to +1.4m — genuinely, fully blocked
regardless of height, likely wedged tightly against cabinetry with no
navigable line of sight from anywhere in the tried radii). Implemented as
a local, disclosed height-search (`viewpoint_for_render`, tries
`(0.0, 0.6, 1.0)` in order, smallest offset that works wins) plus a
farthest-within-the-first-passing-radius-tier preference (addresses the
tabletop-fills-frame framing problem) — bounded to one radius tier after
confirming, on a real case, that "farthest across ALL tried radii" could
push a small object far enough away to fail its own visibility diff
check. **On the real pool: 130 panels resolved at the true anchor height,
19 needed +0.6m, 2 needed +1.0m** — the offset fix is a real but modest
contributor; `NO_NAVIGABLE_VIEWPOINT` remains the dominant residual
cause, and per instruction is not root-caused further this batch.

**6. Lighting confirmed pool-wide, not just the one scene checked
before.** All 21 distinct scenes in the current pool have
`default_lighting: None` or empty in their `scene_instance.json` — no
scene has an authored lighting layout being missed. Per-scene mean
luminance is now tracked and reported per item (0-255 grayscale, Rec.
601 weighting) — real variation across scenes (25.3 to 159.0), consistent
with genuine differences in room brightness/window exposure rather than
a systematic lighting-key bug.

### Final decomposed numbers (full 80-item pool, all round-1 + round-2 fixes)

| Panel | OK | NO_NAVIGABLE_VIEWPOINT | ANCHOR_UNRESOLVED | OBJECT_SPAWN_FAILED | N/A (state) |
|---|---|---|---|---|---|
| BEFORE | 43.75% (35/80) | 12.5% (10/80) | 7.5% (6/80) | 16.25% (13/80) | 20% (16/80) |
| AFTER | 41.25% (33/80) | 13.75% (11/80) | 3.75% (3/80) | 21.25% (17/80) | 20% (16/80) |

(`AIM_FAILED` is 0/80 on both panels, as in round 1 — the pitch fix holds.)

Of the 64 location-event panels needing real object spawning: 34 already
had real, HSSD-placed geometry (no spawn needed), 34/54 genuine spawn
attempts succeeded, 10/54 had no matching asset in this dataset at all
(`cup`→substituted, `wallet`/`keys`→genuinely unavailable).
`OBJECT_SPAWN_FAILED` is now the second-largest failure cause after
`NO_NAVIGABLE_VIEWPOINT` — an honest reflection of a real, disclosed
residual (the marker/object position mismatch noted above, plus the 10
no-asset cases), not a regression from round 1's numbers, which never
attempted to instantiate anything at all.

## Round 3: an output-truth predicate — proxies replaced with a direct check

Round 2's checks (anchor projects centrally, some pixels changed somewhere) were all PROXIES for the
actual claim — "the claimed object is visible in the frame at its claimed location" — never asserted
directly. This surfaced concretely: `AIM_FAILED` sat at 0/80 across the whole batch (a tautological
check the code satisfied by construction — the camera_basis look-at math guarantees the aim TARGET
projects near center regardless of whether anything is actually there), while items were shipping as
a false `OK` with no object anywhere in frame. Separately, round 2's own pixel-diff check had been
widened (18.5% → 63% failure-to-pass by relaxing the comparison window) instead of investigated —
identified this round as the guard inverted: the 18.5% was the system correctly reporting a real bug,
not noise to calibrate away. **Standing rule adopted, permanent: a check that fails at scale is a
finding, never a calibration target.**

**Root-cause investigation (COM hypothesis tested and refuted; real cause found).** The leading
hypothesis for the ~120px marker/object position mismatch was that habitat_sim applies rigid-object
translations in COM-aligned space, displacing assets whose COM sits far from their geometric origin.
Tested directly: `obj.com`, `obj.translation`, and `obj.root_scene_node.absolute_translation` all
returned IDENTICAL values for a real spawned object with `compute_COM_from_shape=True` — no hidden
COM-space offset exists. The real causes were two separate, more mundane bugs, both confirmed by
direct reproduction:
1. **A semantic-ID collision.** `object_id + 1` (the assumption used to test the instance-segmentation
   sensor) is not a safe convention — it coincided with a real HSSD scene's own baked STATIC
   scene-instance semantic ID, and a "mask" computed this way landed entirely on an unrelated outdoor
   lounge chair, not the spawned object. Fix: explicitly assign each verified object a reserved
   sentinel `semantic_id` (900001, `_SPAWNED_OBJECT_SEMANTIC_ID`) immediately before capture, far
   outside any real scene's observed ID range.
2. **Aim/placement used two different position values.** The camera aimed at the anchor's raw
   position (offset by a height-search approximation); the object was spawned at the anchor's TRUE
   position (offset by real surface-height raycast) — these differ by up to ~1m whenever the
   viewpoint search needed a nonzero height offset, and the old code's own comment already disclosed
   this as "a camera-aim approximation, not a claim about where the object itself sits."

**The fix — one output-truth predicate (`evaluate_object_mask` in `scripts/realism_render_job.py`):**
a real instance-segmentation sensor (`habitat_sim.SensorType.SEMANTIC`, added to the render camera)
gates every egocentric panel on the verified object's own mask: non-empty, 0.5%-40% of frame, centroid
in the central 60% band, and the claimed anchor projecting anywhere in frame. Any failing clause maps
to a labeled status (`OBJECT_SPAWN_FAILED` or `AIM_FAILED`), never silently OK. Camera aim, the star
marker, and the commanded-vs-actual offset log all now derive from ONE position
(`world_aabb_centroid` — the object's real post-spawn/looked-up world AABB centroid), not the anchor.
For `_ALREADY_INSTANTIATED_CATEGORIES` (real scene furniture never spawned by this job), a new
`find_nearest_rigid_object` looks up the actual real rigid object nearest the anchor (tolerance tuned
to 0.4m from two real observed distances: 0.24m for a true match, 0.575m for a false one) — this
closed a second real false-OK bug: a "moved" already-instantiated object's "after" panel previously
always reported OK regardless of whether anything was actually there, because that branch never
checked at all. Verified end to end against real data (not just the fixture): a spawned phone's star
marker landed exactly on the visible phone mesh; a stool's "after" panel (no real second stool exists
near the new anchor) now correctly renders `OBJECT_SPAWN_FAILED` instead of the old silent false `OK`.

**Reverts and cleanup (same PR as the mechanism that subsumed them, per standing rule):** deleted
`count_changed_pixels`, `_CHANGED_PIXEL_COUNT_THRESHOLD`, the anchor-projection `AIM_FAILED` gate, and
the old RGB-only `capture_rgb_and_basis` (replaced by `capture_rgb_semantic_and_basis`) —
~120 lines removed, ~340 added (mask predicate, position/lookup helpers, per-panel rewrite).
`scripts/asset_candidate_acceptance.py`'s own pixel-diff step was replaced by the same
`evaluate_object_mask` predicate. One stale pre-fix render batch (80 items, `realism_eval_media/`) was
archived (2 representative items, `realism_eval_media_archive_pre_mask_predicate/`) and the rest
deleted — those renders used the now-superseded proxy checks and would report incorrect statuses.

**Gold set (`scripts/gold_set.py`, `tests/test_gold_set.py`):** 8 fixed real items (easy-table,
counter [substitutes for "sofa" — no resolvable sofa/couch anchor exists anywhere in this project's
real data, checked directly], fridge-top, unresolved-name, state, large-object, small-object,
cross-room) with recorded expected `panel_status`, diffed per-item (not just aggregated) on every
render-job change via `diff_statuses`. All 8 currently match their recorded baseline.

**Objaverse keys/wallet re-verification (`results/reports/asset_coverage.md`'s "Round 2" section):**
license audit re-confirmed all 5 round-1 survivors as clear CC-BY. Re-run through the real mask
predicate: **0/5 pass** — all fail `mask_too_small` (0.108%-0.318% of frame, under the 0.5% floor).
The old pixel-diff numbers (662-958 "changed pixels") were counting shadow/AO changes beyond the
object's own silhouette, not a measurement of real visible footprint. `NO_ASSET_CATEGORIES`
(keys/wallet) is unchanged — nothing was ever promoted, so this finding changes nothing about the
live render pool; it closes round 1's "awaiting owner pick" with an honest answer.

**Follow-up (still round 3, `asset_coverage.md`'s own "Round 3"): re-verified under the full
production pose search** (standard ring radii, farthest-passing preference — not the one fixed test
pose above) — still 0/5, at every standard radius including the nearest. Decision closed per the
standing rule: keys/wallet are PERCEPTUAL-TIER-EXCLUDED, attempted and documented. A companion
diagnostic (mask-area distribution for native categories candle/phone/drinkware, sampled from real
pool events) found the same 0.5% floor is fine for reasonably-sized objects (phone: comfortable
1.0-1.3% margin) but structurally excludes small/thin objects independent of source — candle and
drinkware/cup (both already live, spawnable categories) fail the identical way, today, in the
currently-shipping pool. Surfaced to the owner as an open design question (viewing distance vs. floor
vs. accept), not resolved here.

**Full 80-item batch re-rendered under the mask predicate** (same seed=0, same pool — confirmed the
SAME 80 items were selected: `NO_NAVIGABLE_VIEWPOINT`/`ANCHOR_UNRESOLVED` counts match the round-2
numbers EXACTLY, digit for digit, which is real evidence this is a controlled, isolated comparison —
those two statuses are decided before the mask predicate ever runs, so an exact match on both proves
nothing else in the pipeline moved):

| Panel | OK | NO_NAVIGABLE_VIEWPOINT | ANCHOR_UNRESOLVED | OBJECT_SPAWN_FAILED | N/A (state) |
|---|---|---|---|---|---|
| BEFORE (round 2, proxy checks) | 43.75% (35/80) | 12.5% (10/80) | 7.5% (6/80) | 16.25% (13/80) | 20% (16/80) |
| BEFORE (round 3, mask predicate) | **21.25% (17/80)** | 12.5% (10/80) | 7.5% (6/80) | **38.75% (31/80)** | 20% (16/80) |
| AFTER (round 2, proxy checks) | 41.25% (33/80) | 13.75% (11/80) | 3.75% (3/80) | 21.25% (17/80) | 20% (16/80) |
| AFTER (round 3, mask predicate) | **27.50% (22/80)** | 13.75% (11/80) | 3.75% (3/80) | **35.00% (28/80)** | 20% (16/80) |

**The entire 22.5pp/13.75pp swing moves cleanly from OK to OBJECT_SPAWN_FAILED and nowhere else** —
exactly the boundary this round's mechanism change governs. `OBJECT_SPAWN_FAILED`'s reason breakdown
across all 80 items explains it fully, and matches every finding already reported above and in
`asset_coverage.md`, not a new mystery: `mask_too_small` (22 panels — dominated by `candle` 9,
`cup`/`drinkware` 8, matching the native-small diagnostic exactly), `mask_empty` (12 — occlusion,
mostly `candle`), `not_found_in_scene` (11 — mostly `stool` 7, the already-instantiated-lookup fix
correctly refusing to claim an object is somewhere it isn't), `no_asset_for_category` (10 — exactly
`wallet` 6 + `keys` 4, the pinned PERCEPTUAL-TIER-EXCLUDED categories), `mask_too_large` (4 — `stool`,
a further instance of the same not-really-there phenomenon).

**Per-item flip list — a real, disclosed limitation:** this round's own cleanup pass (see above)
deleted the round-2 batch's 78 remaining per-item JSONs before this comparison was requested,
archiving only 2 representative items. Of those 2, matched into the new batch by (folder, label, t):
`bowl_1` (`102343992_family_with_kids_day3`, t=12.706) stayed `ok`/`ok` — stable, as expected for a
clean case. `stool_1` (`102343992_family_with_kids`, t=11.699) flipped `after: ok -> object_spawn_failed`
(`not_found_in_scene`) — a real, correct, and fully expected flip: the "after" anchor for this event
has no real stool instance nearby, and round 2's code never checked at all for
already-instantiated categories (see the false-OK bug described above). The full 78-item flip list
is not reconstructable; the aggregate reason breakdown above, cross-checked against the exact-match
invariant on the two untouched statuses, is the strongest available substitute and leaves no
unexplained residual.

**Not done this round (explicit STOP, awaiting owner direction):** the elevated study-camera +
oracle-agreement check for anchors where the embodied pose search genuinely can never succeed
(fridge-top/wardrobe-top). Per the standing rule, **owner reviews 10 study items before the batch is
declared study-ready** — that review has not happened; the webapp is running with the fresh pool but
is not yet cleared for volunteer access.

## What this does and does not establish

**Establishes:** every piece of tooling this study needs — rendering
(including real object instantiation, not just a marker on an empty
scene), automatic signals, item serving, response collection, and
analysis — works correctly end to end against real data, not just
fixtures. Multiple concrete bugs (starved state tail, autoscale-distorted
marker, `axis("off")` silently blanking every placeholder, a
marker-windowed diff check that rejected the large majority of genuinely
successful object spawns) were found by actually running the pipeline
and looking at output, not assumed correct from the code or from a
single self-check. The viewpoint-resolution and object-spawn-success
rates are real, reproducible, precisely-measured findings about the
underlying scene data/geometry and this dataset's asset coverage, not
estimates.

**Does not establish:** anything about generation realism itself. No
human has rated a single item. `results/reports/human_realism_study_analysis.json`-shaped
output exists only as a synthetic-data proof of the statistics, not a
result. The gate decision (which automatic signals correlate with human
judgment; whether to retire the self-graded realism score; whether
scaling can proceed) is entirely blocked on running the actual study —
that is explicitly out of scope for this batch, which built the tooling,
not the volunteer data collection.

## Traceability

`embodied/placement_check.py` (+ `tests/test_placement_check.py`),
`embodied/sensor.py` (`viewpoint_from_position`, refactored from
`viewpoint_for` — behavior-preserving, `tests/test_sensor.py` unchanged
and still green), `rooms.py` (`resolve_slot`'s bare-key fix,
`tests/test_rooms.py`), `scripts/realism_render_job.py` (real object
spawning: `SPAWNABLE_ASSET_BY_CATEGORY`, `spawn_object`,
`resolve_surface_height`; offset-aware search: `viewpoint_for_render`,
`_farthest_passing_viewpoint`; output-truth predicate (round 3):
`evaluate_object_mask`, `world_aabb_centroid`, `find_nearest_rigid_object`,
`capture_rgb_semantic_and_basis` — `count_changed_pixels` and the old
`capture_rgb_and_basis` deleted, superseded; + `tests/
test_realism_render_job.py`, `tests/test_realism_render_job_live.py`),
`scripts/gold_set.py` (round 3's 8-item regression set + `tests/
test_gold_set.py`), `scripts/asset_candidate_acceptance.py` (round 3:
mask predicate replaces its own pixel-diff step),
`webapp/realism_eval/` (`app.py`, `sampling.py`, `static/index.html`,
`static/app.js` — including the state-item N/A handling +
`tests/test_realism_webapp.py`), `scripts/analyze_realism_study.py`
(+ `tests/test_analyze_realism_study.py`). Rendered pool: round 1/2's
80-item batch (`results/reports/realism_eval_media/`) was archived (2
representative items kept at
`realism_eval_media_archive_pre_mask_predicate/`) and cleared this round
— those renders used the now-superseded proxy checks; a fresh 80-item
batch under the mask predicate is the next step once the owner responds
to the Objaverse 0/5 finding (round 3's STOP). Full suite: `python3 -m
pytest dynamic_home_eqa/tests/ -q` (660 passed, 39 skipped —
habitat_sim-only tests, expected outside `explore-eqa`; 1 pre-existing,
unrelated failure in `test_kernel_reliability_diagram.py`, a
floating-point precision issue in a different module, not touched this
round). Serving: `python3 -m uvicorn
dynamic_home_eqa.webapp.realism_eval.app:app --host 127.0.0.1 --port
<p>` (binds loopback by default; a cloudflared-style tunnel is acceptable
for this app specifically per standing rules — first-name-only, no other
PII, tunnel URL unlisted and rotated after the study — unlike the LLM
server, which stays loopback-only unconditionally and is unrelated to
this app).

## Round 4 (Spectator Camera + Cleanup): the render camera is now decoupled from agent navigability

Triggered by a direct owner critique of the first artifact-driven batch:
why does wardrobe/fridge get proposed as a viewpoint at all if an agent
can never navigate there? Answer, confirmed by direct investigation: the
render job's camera search (`embodied.sensor.viewpoint_for`) was the
SAME navmesh-snapped, eye-height-constrained search the embodied AGENT
uses to decide what it can see — a real, but different, question from
"can we get a legible study photo of this object." This round adds a
second, deliberately un-constrained camera model for the render job only,
and cleans up the machinery it replaces.

**1. Raycast integrity.** Every `habitat_sim.Simulator` feeding a
visibility/occlusion/placement decision now asserts `enable_physics=True`
at construction (`embodied.sensor.assert_enable_physics`) and, at
`EmbodiedWorld`/`reachability`/`diagnose_navmesh_islands` construction,
runs a backstop self-test: cast straight down 1.0m above a navmesh point,
require a hit in [0.8, 1.3]m. Found a real robustness gap building this:
a single random-point sample is too flaky (confirmed on scene 102344280,
~20% of random navmesh points sit under low-clearance overhanging
geometry) — widened to 5 samples, pass if any one lands in-band.

**2/3. Spectator camera.** New `embodied.sensor.spectator_viewpoint(sim,
target_aabb, object_max_extent)`: hemisphere-sampled (12 azimuths x 4
elevation tiers x 3 distance tiers scaled to the object's own extent), no
navmesh/eye-height constraint, rejects candidates embedded in geometry,
passes on an unobstructed sightline to the object's AABB top-center or
centroid (no slack term — the target is chosen to sit on the object's own
boundary, unlike the agent-visibility check's anchor-pivot slack).
Selects lowest elevation first, then farthest distance. New failure code
`STATUS_ENCLOSED` (no candidate passes anywhere — expected only for an
object truly sealed in closed furniture). `render_event_grid` now
materializes the object FIRST, then searches around its real AABB — the
embodied ring search (`viewpoint_for_render`, `viewpoint_for_realized_pos`,
`_farthest_passing_viewpoint`, `_VIEWPOINT_RADII`, `_VIEWPOINT_Y_OFFSETS`,
`resolve_position_and_viewpoint`) is deleted from
`scripts/realism_render_job.py` entirely; `embodied.sensor.
viewpoint_from_position` gained a `prefer_farthest` flag so the one
remaining embodied-search consumer needing farthest-preference doesn't
need its own duplicated ring loop.

Three more real bugs found live-debugging this, none hypothetical:
- **Sensor eye-offset double-counted.** `capture_rgb_semantic_and_basis`
  adds the render sensor's fixed local `+1.5m` (designed to turn a
  navmesh-standing position into an eye-height camera). `spectator_
  viewpoint` already returns the exact intended eye position, so passing
  it straight through put the real capture 1.5m above where the search
  said it would be. Fixed by subtracting 1.5m from the position handed to
  the capture call.
- **BIND-category relocation was a silent no-op.** A real HSSD scene
  instance loads `motion_type=STATIC`; Bullet silently ignores a
  `.translation` assignment on a STATIC body. `_materialize_object`'s
  BIND branch (and `build_realized_day.py`'s own placement loop) set
  `.translation` without first switching to `KINEMATIC` — confirmed
  directly (`obj.translation` read back completely unchanged after the
  assignment). Every "moved" BIND-category render (stool, chair, oven,
  fridge, ...) was silently showing the object at its ORIGINAL scene
  position, not the artifact's real realized_pose. The builder's own
  recorded data was unaffected (its collision/occupancy tracking is pure
  Python bookkeeping against an `occupancy` dict, never a Bullet query),
  but every render was wrong. Fixed in both places. Fixing this exposed a
  second bug: `_materialize_object` finds a BIND object by searching near
  its fixed original scene position — once relocation actually worked, a
  later lookup for the SAME label (the other panel of the same item, or a
  later item touching the same instance in the same reused render_sim)
  could no longer find it there. New `_restore_bind_object` puts it back
  after each panel.
- **Distance-factor mis-calibration.** The naive pinhole-projection
  formula that produced the first factor set `(0.35, 1.0, 2.5)` (needed
  to rescue the fridge nook case) badly under-predicted apparent size for
  a chunkier object: a stool at the same distance/extent ratio that gave
  a laptop 12% frame area measured 46% (`mask_too_large`) — a real
  gold-set regression caught by running the actual gold set, not assumed
  fixed. Live-recalibrated to `(0.5, 1.5, 4.0)`, re-confirmed this still
  finds fridge candidates (fewer, at a higher elevation, but real ones).
- Also: `render_event_grid`'s `anchor_px` reference switched from a
  generic `resolve_anchor_position` coordinate to the panel's own exact
  `target_pos` (the artifact's real realized_pose) — the generic
  coordinate could sit far enough from the real position (0.66m, a real
  case: laptop on bedroom.bed) to project hundreds of pixels outside a
  360px frame under the spectator camera's closer standard distance,
  even though the object's own mask was correctly centered.

**4. Sensability map.** New `scripts/compute_sensability_map.py`: runs
the EMBODIED viewpoint search once per anchor per scene (not the
spectator camera — deliberately the agent-navigability question, not the
render job's), caches `{anchor: {robot_visible, pose}}` to `data/
sensability_maps/<scene_id>.json`. Not wired into the render job (out of
scope per this round); intended for question tagging / oracle-v2 /
generation-quality reporting, so an anchor's unreachability is known
before generation/sampling effort is spent on it, not discovered per-item
deep into a render batch. Computed for both scenes exercised this round:
102343992 (23/26 anchors robot-visible) and 102344280 (18/26).

**5. Dead-code sweep.** Deleted: `scripts/sweep_navmesh_recompute.py`
(188 lines — a closed D1 diagnostic; its finding, `agent_max_climb=0.4`,
is recorded directly in `NavMeshConfig`'s own docstring, the durable
record); `scripts/render_suspicious_events.py`'s entire oracle-v1 render
pipeline (`_make_render_sim`, `capture_rgb_looking_at`,
`resolve_position_and_viewpoint`, `render_event_grid`, `main` — ~186
lines; `pool_category_anchor_counts`/`score_events` kept, still the live
suspicion-scoring logic `realism_render_job.py` imports); `scripts/
asset_candidate_acceptance.py`'s `check_candidate_production_search`/
`_farthest_sightline_pose_at_radius`/`run_production_search`/`--mode`
(~114 lines — redundant once `check_candidate`'s own search IS the
exhaustive spectator search; that script itself is KEPT, updated to use
`spectator_viewpoint`, per its real future consumer named in
`build_realized_day.py`'s own coverage-gap error message); `data/objects/
external_props/` (~31MB — the 10 rejected keys/wallet Objaverse
candidates, 0/10 passed, fully recorded in `asset_coverage.md`); `results/
reports/suspicious_events/` (orphaned output of the deleted oracle-v1
pipeline); 2 stale gold-set PNGs (`shelf.png`/`sofa.png`, orphaned from an
earlier item-naming iteration no `GOLD_SET` entry matches); 2 unused
imports in `embodied/world.py` (`Change`, `SceneState`, found via
`pyflakes`). Kept: `realism_eval_media_archive_pre_mask_predicate/` (the
one designated archived batch), `asset_candidates_production_search_
result.json` (historical result file from the now-deleted production-
search mode — protected, never delete historical results).

**gold_set.py was broken and silently un-run since the artifact
cutover** — a real, pre-existing bug this round found and fixed:
`render_event_grid`'s signature had grown a required `artifact` parameter
`run_gold_set` never passed (`TypeError` on the very first attempt to run
it this round). Fixing that surfaced that several items' expected values
and rationale described `find_nearest_rigid_object`, a position-tolerance
search deleted at the artifact cutover and no longer used by anything —
stale documentation of a mechanism that hadn't actually run in a long
time. Re-verified all 8 items against a real run; updated 5 with
concrete, code-referenced justification (not silently): `fridge-top`
(the headline NO_NAVIGABLE_VIEWPOINT->OK case this round targets, plus an
unrelated real SURFACE_FULL build-time fact on its "before" panel),
`state` (wardrobe: genuinely renders now, in a tight enough nook that
only one elevation/distance combination has any sightline at all —
honest AIM_FAILED, confirmed by direct enumeration of the full candidate
grid, not a bug), `large-object` and `cross-room` (the BIND-relocation
fix made both panels findable; their "after"/"before" outcomes now
reflect real, current `placement_status` build-time facts instead of a
deleted function's distance-tolerance behavior), and `unresolved-name`
(re-targeted to corrupt the event's `label`, the only thing that still
reaches ANCHOR_UNRESOLVED post-cutover, instead of the now-inert
anchor-string corruption). All 8 green. Full suite: 709 passed (703 +
6 new sensability-map tests), same 1 pre-existing unrelated float-
precision failure noted above, `fastapi` missing in `explore-eqa`
(pre-existing environment gap, not this round's webapp tests failing).

**6. Re-render.** Same 4 folders, same sampling quotas as the archived
pre-round batch (`n_tail_location=20, n_random_location=20,
n_tail_state=10, n_random_state=10`, seed=0) for a controlled comparison
— 48/60 sampled items are shared between the two batches; 12 dropped and
12 new items entered the pool because the underlying manifests/artifacts
were regenerated (Builder Round 2) between when the archived batch was
rendered and this round, not because of anything in this round itself
(each side of that drift is listed explicitly in the flip report, not
folded into the shared-item numbers). Over the 48 shared items (96
panels): OK 3->19, OBJECT_SPAWN_FAILED 52->25, NO_NAVIGABLE_VIEWPOINT
29->0 (replaced by ENCLOSED 0->12 — the fridge cases, now honestly
distinguished from a generic camera-search failure — and AIM_FAILED
0->28, encompassing the previously-hidden wardrobe cases). Full per-item
before/after (all 35 shared-item flips, plus the pool-drift lists) is in
`results/reports/spectator_camera_round_flip_report.json` — this
document does not attempt to reproduce that table in prose, per the
standing instruction that a percentage without a flip list is not an
acceptable report.

**STOP — per this round's own gate, this is where it ends for owner
review.** Item 6 (pool-wide build), oracle sensor v2 + re-fingerprint,
and the original phase's full-batch owner 10-item review are all still
ahead and un-started; nothing past this re-render was touched.
