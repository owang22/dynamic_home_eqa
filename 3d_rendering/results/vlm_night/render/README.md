# Household A pictures at fixed robot viewpoints

Pictures of household A's simulated home (HSSD scene `107734254_176000121`, habitat-sim) at
every snapshot of the 14-day run (`lived_home/hssd_a/day_XX/positions_HHMM.json`, 8 times a day,
08:00 to 22:00). Each spot is always photographed from the same place, so pictures of one spot
on different days differ only in what lies there. Every picture comes with the objects it shows
and how many pixels each one covers.

The 3D placement is the committed renderer in
`3d_rendering/results/render_methods/habitat_hssd/scripts/` (read its `REPORT.md`). It is imported,
not edited; `lib.py` subclasses its `Home` with four changes listed under "Changes to placement".

## Picture sets and the code that made each

All pictures are outside the repo, under `/mnt/nvme/oliver/robot/render_methods/vlm_night/`.
Each set has the same folder layout and truth.json format (below).

| set | snapshots | eye | placement | code | used by |
|---|---|---|---|---|---|
| `hssd_a` | all 112 | 1.0 m | v1 (`lib.SnapshotHome`) | `choose_views.py`, `render_snapshot.py`, `run_all.py` | every result in `../NIGHT_2026-10-13.md` and `../questions/` |
| `hssd_a_1p4` | 44 (days 4-14, 10/14/18/22 h) | 1.4 m | v1 | `*_1p4.py`, `README_1p4.md` | camera-height bench in the night notes |
| `hssd_a_0p4` | 40 (days 3-7, every 2 h) | 0.4 m | v1 | `*_0p4.py` (2026-10-19) | `go2/evidence_memory/` |
| `hssd_a_v2` | all 112 | 1.0 m | v2 (`lib.SnapshotHomeV2`) | `*_v2.py`, `placement_check.py`, `before_after.py` | superseded by v3 |
| `hssd_a_v3` | 5 (check snapshots) | 1.0 m | v3 (`lib_v3.SnapshotHomeV3`) | `*_v3.py`, `typical_sizes.py` | checks only |
| `hssd_a2_v3` | all 112 of run `hssd_a2` | 1.0 m | v3 | `run_all_v3.py` with `RUN_V3` (below) | newest set; no question trial has used it yet |

For new pictures use v3. `place_map.py` (which furniture each pixel of a view shows, from the
empty home) is used by `../questions/placed_notes.py`. Logs: `logs/` (v1), `run_1p4/`, `run_0p4/`,
`run_v2/`, `run_v3/`.

## How to run

Python: `~/miniconda3/envs/dynamic_eqa/bin/python` (has habitat_sim). Run from this folder.

```
python choose_views.py              # once: one camera stand per spot -> spot_views.json (about 1 min)
python render_snapshot.py 7 1800    # one snapshot (about 22 s; --force to redo)
python run_all.py --workers 2       # every snapshot; skips those with a truth.json; resumable
python outline.py 7 1800 <spot>     # check copy: each counted object outlined and numbered
python contact_sheet.py out.jpg a.jpg b.jpg ...   # several pictures on one sheet
```

Logs: `logs/run_all.log` (one line per snapshot), `logs/render_times.jsonl` (timings and counts
per snapshot), `logs/snapshots/day_XX_HHMM.log` (habitat output), `logs/choose_views.log`.

## Output layout

Large files live outside the repo, under `/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a/`:

```
spot_views.json                       copy of this folder's spot_views.json
spot_views/<spot>.jpg                 the view of the empty home (no snapshot objects)
spot_views/<spot>_points.jpg          same, with the surface test points (green seen, red not)
day_XX/HHMM/<spot>.jpg                the picture: 640x480, 75 deg horizontal lens, eye 1.0 m
day_XX/HHMM/<spot>_ids.png            16-bit object-id picture (pixel value = semantic_id)
day_XX/HHMM/truth.json                ground truth for the snapshot (below)
checks/                               outlined copies made by outline.py
```

## spot_views.json

`views` (one per spot with a view):
- `spot`: place id from the snapshot; `room`; `spot_name`: readable name, e.g.
  "top of the nightstand (nightstand by the main bed, bedroom 1)"; `furniture`, `place_name`, `kind`
- `eye`, `target`: habitat world coordinates (metres, y up, floor at y = 0). The camera stands at
  `eye` and looks at `target` with +y up (`common.look_from`).
- `yaw_deg`, `pitch_deg`, `metres_from_middle` (horizontal distance to the middle of the surface)
- `surface_share_seen`: share of the surface's test points this stand sees; `score` (rule below)
- `scanned_area_m2` (surface found by the scan) and `snapshot_area_m2`; `test_points`, `stands_tried`

`skipped`: spots with no usable stand, with the reason. `closed_places_not_viewed`: the 91
closed places (drawers, cabinets, compartments, washing-machine drums, the toilet bowl).

**How a stand is chosen** (full text in `choose_views.py`): the empty home, so no day's objects
affect it. The committed surface scanner finds the spot's surface; up to 600 surface cells become
test points 4 cm above it (12 cm for sinks, the bathtub and the fireplace opening). Candidate
stands: walkable floor, rings 0.6-3.5 m out (6 m for floors), 24 bearings, eye 1.0 m, aimed at the
middle of the points, tilt limited to 60 deg down and 30 deg up. A point counts as seen when it is
in the frame and nothing is drawn in front of it. Score = mean of seen x distance weight x
slant weight (far points and points seen nearly edge-on count less). Skipped when the best stand
sees under 5% of the points.

## truth.json (one per snapshot)

- `snapshot`, `day`, `time`, `scene`, `visible_rule`
- `people`: where the snapshot puts the two residents. **People are not drawn.**
- `pictures[<spot>]`: `picture`, `ids_picture`, `spot_name`, `room`, `eye`, `target`,
  `visible_objects`, `visible_objects_on_this_spot`, `objects_on_this_spot`, and `objects`: every
  object with at least 1 pixel in the picture plus every object the snapshot puts on this spot
  (even at 0 pixels), sorted by pixels. Each entry:
  - `object`, `semantic_id`, `pixels`, `visible` (pixels >= 30), `on_this_spot`
  - from the snapshot: `type`, `looks`, `relation`, `reference`, `reference_kind`, `place`,
    `room`, `hidden_in_snapshot`
  - from the placement: `placed`, `did_not_fit` (overlaps or overhangs), `model_source`,
    `model_is_stand_in` (e.g. a crisp packet for pasta), `model_looks_like` (the model's own name)
- `objects[<id>]`: the same fields per object, plus `why_not_placed`, `max_pixels`,
  `best_picture`, `visible_in` (spots where it has >= 30 pixels)
- Lists for a question-writer:
  - `not_placed`: not in the 3D scene, with `why`: no 3D model; out of the house; with a person
    (worn, held, in a pocket, or in or on something a person has); larger than its closed
    container; no free room
  - `placed_overlapping_or_overhanging`: placed, but did not fit (overlaps or hangs over an edge)
  - `placed_not_hidden_in_no_picture`: placed, not hidden, yet under 30 pixels in every picture,
    with `max_pixels` and why (its spot has no view, or it is out of frame or blocked)
  - `hidden_in_snapshot_but_visible`: hidden by the snapshot (inside a closed place or container,
    or under something) yet 30+ pixels somewhere: a placement leak or a see-through door
- `summary`: counts of the above; `timings`

To avoid unfair questions: ask about an object in a picture only when that picture's entry has
`visible: true`, `hidden_in_snapshot: false`; prefer `model_is_stand_in: false`; and check
`not_placed` and `placed_not_hidden_in_no_picture` before asking where something is.

## Changes to placement (lib.SnapshotHome)

The first full run had only changes 1-3 (its pictures, `old_v1/`, have since been deleted);
change 4 was found in the eye check and everything was rendered again.

1. Objects whose place is None (out of the house) are not placed (the committed code would crash).
2. Objects held by a person, and anything resting on or inside something a person wears, holds or
   pockets, are not placed. The committed code only handled worn and pocketed objects themselves;
   a held object would have been put on the surface where the person is.
3. Drawers: a thing in a drawer rests at most 8 cm above the drawer bottom. The committed rule
   allowed 0.3 m, so in a full drawer the highest drawn point won and tongs from a kitchen
   drawer were drawn lying on the counter above it.
4. Resting height on every spot: a point of the spot's furniture counts only up to 10 cm above
   the spot height, and a placed thing counts only if the snapshot puts it on the same spot.
   The committed rule took the highest drawn point under the footprint, so things meant for the
   office desk shelf (0.65 m, under the desk top) were drawn lying on the desk top (0.79 m), on
   top of the desk-top things, and keys meant for the piano's middle shelf sat on its top shelf.

## Results of the run (2026-10-13)

- 96 open spots; 92 have a view, 4 skipped (`skipped` in spot_views.json): the bed's bottom
  shelf (under the mattress), the fireplace top shelf, and the laundry-room and toilet-room sink
  basins (deep basins; their near rim hides them from 1.0 m). Of these only the bed's bottom shelf
  is ever used with a model present (its sleep mask has no model anyway), and the laundry-room
  basin's soap shows in the vanity-top view.
- All 112 snapshots (14 days x 08:00-22:00 every 2 h) rendered, 0 failures. 19.6 s per snapshot
  (place 15-18 s, 92 pictures under 1 s); 3 in parallel took 769 s in all. 631 MB.
- Per snapshot: about 215 of 251 objects placed; 36 not placed (no model 19, out of the house
  about 10, with a person about 4, too big for their closed bag about 3); 21 overlapping;
  14 placed and not hidden but in no picture; 7 hidden by the snapshot yet visible (leaks).
- Of placed, not hidden objects on a viewed spot, 84% reach 30 pixels in that spot's picture.
- `summary.json` (in the picture folder, made by `summarize.py`) has the counts per snapshot.

## Known faults

- **30 pixels is far too low to mean "a person could name it".** In the eye check, things under
  about 300 pixels were not nameable: a 152 px pen looked like a carrot, keys at 44 px, a
  newspaper at 169 px, a wallet at 327 px seen edge-on. A chair-seat picture counted 23 kitchen
  objects in a far strip at the top of the picture as "visible". 47% of visible objects that are
  not on the picture's own spot are under 300 px (11% of those on the spot). For questions, use
  `on_this_spot` and a higher pixel bar (500-1000).
- **Counters are seen nearly edge-on.** Counters, the island, the range and sideboards are
  0.9-1.1 m high and the eye is at 1.0 m, so flat things there (phones, papers, cutlery) show as
  slivers. High shelves (bathroom 1 upper shelf 1.92 m, coat-rack upper shelf 1.79 m, piano top
  shelf 1.15 m) are seen from below: 13-24% of the surface, and the piano's music notebook shows
  as 55 px of edge.
- **One view per floor sees only part of a room**: bedroom 1 floor 24%, bathroom 1 48%, kitchen
  57%. Things elsewhere on the floor are in `placed_not_hidden_in_no_picture`.
- **Kitchen sink basin**: 35% seen; plates, bowls and forks lying flat in it are usually hidden
  by the rim (most of the never-seen list).
- **Leaks**: 29 object/place pairs are hidden by the snapshot but drawn visible, listed per
  snapshot in `hidden_in_snapshot_but_visible`. Five in every snapshot: a coaster under a mug
  (shows, as it would in life), a first-aid kit through the bathroom-1 vanity, a flashlight from
  the fireplace's lower compartment, a kitchen towel through the washing machine's glass door, a
  serving platter sticking out of the sideboard. Also the milk carton through the fridge door
  (59 snapshots), and things poking out of closed bags on floors (phones, keys, water bottles).
  Closed-cabinet contents are set in rows at the spot centre and never checked for fit.
- **Models** (from the committed renderer): 20 types have no model; stand-ins are obvious (a
  crisp packet for pasta, red All Stars for every pair of shoes, a wooden chest for a parcel, a
  white box for the laptop, a beige board for a cloth napkin that overhangs the dining table);
  colours do not follow the snapshot (a "charcoal" sleep shirt is white); some sizes are off (the
  bathroom-2 toothbrush holder is bigger than the shampoo).
- **Bathroom 1 "vanity by the toilet" top** (0.45 m) is the area over the wall-hung toilet:
  tissues and soap stand on the toilet, which a question-writer may find odd.
- **Crowded spots stack**: when a spot is full, things rest on their neighbours (a towel across
  the bathroom-2 basin on a shampoo bottle, the shampoo on the toothbrush holder).
- **People are not drawn**, and nothing worn, held or pocketed is drawn.
- Lighting is flat with no shadows; dark things on dark wood lose their shape.

## Second placement (hssd_a_v2, 2026-10-13)

The same 112 snapshots, views, lens and file layout, placed again by `lib.SnapshotHomeV2`
(a subclass of `SnapshotHome`; `scene.py` and `common.py` are still not edited). Pictures:
`/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v2/`. The `hssd_a` pictures are untouched.

```
python render_snapshot_v2.py 7 1800          # one snapshot into hssd_a_v2 (about 28 s)
python run_all_v2.py --workers 2             # all 112; resumable; logs in run_v2/logs/
python placement_check.py 7 1800 v1|v2       # counts for one placement, no pictures -> run_v2/checks/
python before_after.py 7 1800                # hssd_a next to hssd_a_v2 -> hssd_a_v2/checks/
```

What changed (each rule is described in its method's docstring in `lib.py`):

1. **Open containers** (laundry basket, bowl, tray) and **open places** (sinks, bathtub, fireplace
   opening): the first placement dropped every content at the centre and each rested on the one
   before, so contents stood in towers. Now the inside of a container is measured from above
   (cells of its own mesh below its rim); each content goes on a free part of it, as low as it
   goes, and rests on another content only when no free part fits. Cloth wider than the inside is
   folded (footprint scaled down, thickness up by the same factor; a `folded_to_fit` repair) and,
   when stacked, sinks 40% into the cloth below. In open places the flattest things go first
   (plates at the bottom of a full sink), and the lower walls of a basin count as bottom.
   Closed containers (bags, pockets): contents spread over the box bottom; one that would stick
   out of the top is left out (`not_placed`, "no room left in its closed container").
2. **Thing on thing**: the base's real upper surface is measured from above; the thing's centre
   goes over it, where it rests lowest. A thing on a tray lies in the tray. When the base is much
   smaller (its top under a quarter of the thing's footprint, a tenth for cloth, or a tall thing
   on a narrower top), the thing goes beside the base on the same surface (`beside_small_base`).
3. **Crowded surfaces**: when no spot keeps a thing's whole box on free cells, the thing is also
   tried turned (30-150 degrees), and its resting height is worked out from its underside (seen
   from below) against the surface and the boxes of things already there, so a vacuum cleaner's
   hose may pass over the laundry basket instead of the cleaner standing on it. Spots where it
   rests within 3 cm of the surface come first, then (next_to) within 15 cm of the reference.
4. **Repairs are recorded.** `truth.json` gains `repairs` (one entry per change: `object`,
   `kind`, `what`, `from` = what the snapshot asked, `to` = what was drawn), `objects[<id>].repairs`,
   and in `summary`: `repairs`, `objects_repaired`, `repairs_by_kind`. Kinds: `overlap` /
   `overhang` (no free room: overlaps neighbours, or hangs over the edge or blocked cells),
   `next_to_a_place` (next_to names a place: put on it), `reference_not_drawn` (next to / on a
   thing with no model or not drawn: put on the place), `far_from_reference`,
   `beside_small_base`, `small_base_kept`, `on_neighbours`, `base_not_seen` (old box-top rule
   used), `stacked_in_container`, `wider_than_container`, `sticks_out_of_container`,
   `folded_to_fit`, `open_place_crowded`, `open_place_bottom_not_found`.
5. **Not drawn, listed plainly.** Each `not_placed` entry has `reason` and `has_model`; `summary`
   has `not_placed_by_reason`, `no_3d_model` (object, type) and `with_a_person_not_drawn`
   (object, type, why: worn, held, pocketed, or in or on something a person has).

`placement_check.py` counts per snapshot (definitions in its docstring): things more than 3 cm
above anything under them (`floating`), more than 3 cm above what they are meant to rest on
(`off_its_support`), contents more than 10 cm above their container's rim, and box overlaps.
Box overlaps over-count where a hose or a handle passes over another thing, and clothes sunk
into each other in the basket count as overlaps by design.

## Third version (hssd_a_v3, hssd_a2_v3, 2026-10-13)

Sharper pictures, corrected model sizes and kinds, garments as folded cloth, things spread out
instead of stacked, and every thing on a surface held by it. All in new files; the v1/v2 code
paths and pictures are not changed (`lib.py`, `render_snapshot.py`, `run_all_v2.py`,
`placement_check.py`, `before_after.py` are as they were). Revised the same evening after an
independent visual audit of 56 v3 pictures (clothes as hollow shells, overhangs, wrong kinds,
moves to other furniture).

```
python typical_sizes.py                       # typical size per type (local Qwen, cached) -> typical_sizes_v3.json
python make_meshes_v3.py                      # tinted folded cloth, groups, laid-flat models -> models_v3_built.json
python model_sizes_v3.py v2|v3                # size check -> run_v3/size_check_<v>.json/.md
python model_check_v3.py v2|v3 [--ask]        # every model alone, 2 views, Qwen verdict -> run_v3/model_check/<v>/
python render_snapshot_v3.py 4 1000           # one snapshot into hssd_a_v3 (about 31 s)
python run_all_v3.py --workers 2              # all snapshots; resumable; logs in run_v3/<run>/logs/
python placement_check_v3.py 4 1000 v2|v3     # counts, what each thing rests on, overhangs -> run_v3/checks/<run>/
python before_after_v3.py 4 1000 [7 1800 ..]  # v2 next to v3 -> hssd_a_v3/checks/v2_v3_day_XX_HHMM_<n>.jpg
# household A2 (same residents, objects and home; re-run generator):
RUN_V3=.../lived_home/hssd_a2 PICS_V3=/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a2_v3 \
  RUN_V3_LOGS=hssd_a2 python run_all_v3.py --workers 2      # same env for placement_check_v3.py
```

Settings live in `lib_v3.py` (imported first; it sets lib.W/H, lib.VISIBLE_PX, lib.PICS, lib.RUN,
lib.CODE and lib.HOME_CLASS in that process only). Derived meshes are in
`/mnt/nvme/oliver/robot/render_methods/vlm_night/meshes_v3/`.

1. **Pictures 1280x960** (was 640x480), same 75 deg lens, same camera stands (`spot_views.json`).
   The colour picture is drawn at 2560x1920 and reduced 2x2 -> 1 (smooth edges); the id picture is
   drawn at 1280x960. Habitat's ambient occlusion (`enable_hbao`) is on. Lights unchanged.
   **Pixel counts in truth.json are at 1280x960, 4x the old counts. "visible" is now >= 120 px
   (= 30 px at 640x480).** truth.json records `image_size`, `visible_px_threshold`, `pixel_note`.
   The eye-check bar of 300-1000 px at 640x480 becomes 1200-4000 px.
   About 31 s per snapshot (v2 21 s on the same machine): placing 21-24 s, drawing 0.9 s (v2 0.4 s),
   the rest writing the larger pictures. 15 MB per snapshot (v2 5.7 MB).
2. **Models.** `models_v3.json` (by hand) and `models_v3_built.json` (make_meshes_v3.py) give, per
   object, per type|model id or per type, a new longest side (rescale) or another model (scaled to a
   longest side), each with the reason; table with old and new sizes: `run_v3/model_fixes_v3.md`.
   - Size check: typical sizes from the local Qwen (`typical_sizes_v3.json`; four set by hand where
     Qwen was wrong, each with why); a model is flagged when its longest or middle side is over
     1.8x or under 1/1.8 of typical.
   - Garments, napkins, pillowcase and throw are all one generic folded-cloth model (the plain
     folded towel) with its texture recoloured to the object's `color` (garment meshes stood up as
     stiff hollow shells). Several-in-one objects are one model holding several copies (three
     lemons, three tins, a bunch of four carrots). Gloves and pruning shears are laid flat.
   - Wrong kinds replaced (dish soap, cleaning spray, stain remover, magazine, kitchen roll,
     candle, clogs, loafers, hand cream, sticky notes, plasters, serving platter, coffee, rice,
     pasta, phones, knives, tongs, spatula, rolling pin, salt cellar, egg carton, honey bear,
     umbrella, parcel, trays, sketchbook, shopping bags, herbs, laundry soap, water bottle).
   truth.json gives each changed object `model_change` and `summary.models_changed`.
3. **Where things go** (`SnapshotHomeV3`). A thing on a surface must have its box centre over the
   surface, at least 80% of its own outline (seen from below, not its box) over the surface, and
   its outline must not overlap another thing's turned rectangle. It rests on the scanned surface
   under its outline (so a back cushion or a basin rim does not lift it). When v2's spot fails
   this (overhang, or overlap when the surface was full), or when the snapshot puts it on top of a
   thing that is not a carrier for it (`lib_v3.CARRIERS`, also in truth.json `stack_rule`: cloth on
   cloth; anything on a tray, board, platter or in the laundry basket; plates, bowls, cutlery,
   loose food or a napkin on a plate; bowls, cutlery or loose food in a bowl; books and papers on
   a book; a cup on a coaster; cutlery on a napkin), a new spot is searched in this order:
   its own place (near its base when it has one; repair `beside_not_a_carrier` or
   `respaced_on_its_place`); another place of the same furniture (`moved_on_same_furniture`);
   the nearest other furniture of the same room (`moved_to_other_furniture`, last resort; never a
   floor unless the thing was on a floor; never into a sink). If nothing fits, the thing stays as
   v2 put it. A thing more than 3 cm above its surface with nothing under it is set down
   (`lowered_onto_surface`). Cloth overlapping only cloth (a heap of clothes) and piles in a sink
   are left. On furniture tops v3 packs things against the edges and each other (v2 scattered
   them over the middle). **When `drawn_on` is set, the thing is drawn on that place, not its
   snapshot place; `summary.moved_to_other_furniture` lists these per snapshot.**
4. `placement_check_v3.py` = placement_check.py plus, from the same 25 down samples per thing:
   what it rests on (`resting_on_a_surface`, `resting_on_a_thing`, split into carrier pairs and the
   rest) and overhang (centre sample not held, or under 80% of samples held within 3 cm of its
   bottom). Pans on cooktop grates count as overhangs (samples fall between the bars).
   `off_its_support` counts the things drawn on another place (gap null) as off support.

Known faults left (not fixed): stand-in colours often differ from the snapshot (a blue thermos jug
for a red thermos, a yellow washing-up bottle for a green pump, a red closed umbrella for a navy
folding one); receipts and mail are scattered paper strips; untextured black pans and binders;
book covers blurred at source; low-resolution rugs; glasses are opaque everywhere (habitat draws
these materials opaque); some spot names do not describe what the camera sees
(`laundryroom_toilet_by_the_bathroom_vanity_top` shows a laundry sink; the names come from the
household's place list, not from the renderer); labels are not readable.
