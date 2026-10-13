# Household A pictures at fixed robot viewpoints

Pictures of household A's simulated home (HSSD scene `107734254_176000121`, habitat-sim) at
every snapshot of the 14-day run (`lived_home/hssd_a/day_XX/positions_HHMM.json`, 8 times a day,
08:00 to 22:00). Each spot is always photographed from the same place, so pictures of one spot
on different days differ only in what lies there. Every picture comes with the objects it shows
and how many pixels each one covers.

The 3D placement is the committed renderer in
`3d_rendering/results/render_methods/habitat_hssd/scripts/` (read its `REPORT.md`). It is imported,
not edited; `lib.py` subclasses its `Home` with three changes listed under "Changes to placement".

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

The first full run (moved to `/mnt/nvme/oliver/robot/render_methods/vlm_night/old_v1/`, delete
when no longer wanted) had only changes 1-3; change 4 was found in the eye check and everything
was rendered again.

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
