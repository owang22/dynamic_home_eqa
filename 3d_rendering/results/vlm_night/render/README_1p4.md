# Household A pictures with the camera eye at 1.4 m

A second picture set of the same home, same snapshots and same object placement as the 1.0 m set
(README.md), with only the camera changed: eye 1.4 m above the floor instead of 1.0 m. Made so
recognition by a vision model can be compared between the two camera heights.

## Folder

`/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_1p4/` — same layout and truth.json format
as `hssd_a/`, so a loader works by changing the folder:

```
spot_views.json, spot_views/<spot>.jpg, spot_views/<spot>_points.jpg   the 1.4 m stands (empty home)
day_XX/HHMM/<spot>.jpg, <spot>_ids.png, truth.json                     44 snapshots
```

Snapshots: days 4-14 at 10:00, 14:00, 18:00 and 22:00 only (44 of the 112). The `eye` and
`target` fields in truth.json give the 1.4 m camera.

## How it was made

No file of the 1.0 m set was edited. Four small files were added here:

- `lib_1p4.py`: imported first; sets `lib.EYE_HEIGHT = 1.4`, the picture folder to `hssd_a_1p4/`,
  the stand file to `spot_views_1p4.json`, and the log folder to `run_1p4/logs/`. Nothing else.
- `choose_views_1p4.py`: runs `choose_views.main()` unchanged (same lens 75 deg, 640x480, same
  candidate rings, tilt limits 60 deg down / 30 deg up, same score) -> `spot_views_1p4.json`.
- `render_snapshot_1p4.py`: runs `render_snapshot.main()` unchanged with the 1.4 m stands.
- `run_all_1p4.py`: the 44 snapshots, 2 at a time, resumable.

```
~/miniconda3/envs/dynamic_eqa/bin/python choose_views_1p4.py      # about 1 min
~/miniconda3/envs/dynamic_eqa/bin/python run_all_1p4.py --workers 2
```

Same placement, checked: the wrapper path, given the 1.0 m stand file, re-rendered day 7 18:00 into
a scratch folder byte-identical to `hssd_a/day_07/1800` (184 pictures, truth.json equal apart from
timings). Placement is deterministic (hash-based choices), and in all 44 snapshots every object's
placed / did-not-fit / why-not-placed / model fields agree between the two sets.

## Timing (2026-10-13)

- Choosing stands: 55 s. Rendering: 44 snapshots, 2 at a time, 496 s in all, 0 failures; per
  snapshot 21.8 s median (placing 17.2 s, 93 pictures 0.75 s). 259 MB.
- Logs: `run_1p4/logs/` (choose_views.log, run_all.log, render_times.jsonl, snapshots/).

## Stands at 1.4 m compared with 1.0 m

- 93 views, 3 skipped (bed bottom shelf, fireplace top shelf as before; the office desk shelf,
  under the desk top, is now skipped at 4% seen). The laundry-room and toilet-room sink basins,
  skipped at 1.0 m, now have views. **The spot lists differ by these three**, so a loader that
  pairs pictures by spot must take the spots both sets have (91).
- Counters, island, range, sideboards (0.8-1.2 m): tilt goes from about level (5 deg down to 8 deg up) to
  23-37 deg down; the tops are now seen from above. Surface share seen is about the same or higher,
  except the island (0.87 -> 0.77, the plant hides the far end from the new stand) and the office
  desk top (0.89 -> 0.78).
- Basins: kitchen sink 35% -> 100% seen, bathroom-2 basin 83% -> 97%.
- High shelves (1.8-2.0 m) are still seen from below: coat-rack upper shelf 23% -> 53%, bathroom-1
  upper shelf 13% -> 30%.
- Low tables (nightstands, coffee and side tables, 0.4-0.65 m): the stand moves back (0.6 -> 0.75 m)
  and the eye is 0.4 m higher, so the camera is about 1.1 m from the top instead of 0.7 m and
  things there cover about half as many pixels.
- Entryway floor: the stand moved 3 m (2.25 m away, looking along the hall -> 0.9 m away, looking
  steeply down); 94% -> 74% of the floor seen, and the door and hall are no longer in the picture.

## Pixels of things on their own spot, both sets (44 snapshots, placed and not hidden)

| kind of spot | objects | >= 300 px at 1.0 m | >= 300 px at 1.4 m | median pixel ratio 1.4 / 1.0 |
|---|---|---|---|---|
| counters etc. 0.7-1.2 m | 3161 | 2317 | 2690 | 1.35 |
| basins and openings | 443 | 111 | 257 | (most were near 0 at 1.0 m) |
| floors | 1432 | 950 | 893 | 0.75 |
| low tables and seats < 0.7 m | 1932 | 1728 | 1518 | 0.67 |
| high shelves > 1.2 m | 112 | 88 | 68 | 1.22 |
| all | 7080 | 5194 | 5426 | |

Counts are of object-snapshot pairs; an object on a spot with no view in one set counts 0 there.

## Eye check (day 4 10:00)

Flat things on counters are clearly easier to see at 1.4 m. Island: at 1.0 m the receipt, knife
and menu folder are thin white slivers or not there at all; at 1.4 m the menu folder, knife, pen
and tray are plain to see. Dining-room sideboard (1.14 m): at 1.0 m the top cannot be seen at all;
at 1.4 m the serving spoon and the mail show. Office desk: sticky notes, keyboard and mouse show
at 1.4 m. Counter by the kitchen sink: at 1.4 m the view looks down into the sink as well.
Costs: upright things on the island (eggs, yogurt, water bottle) get smaller; nightstands and
other low tables are seen from further away (everything about half the pixels, still nameable);
the bathroom-2 floor looks almost the same with things slightly smaller.
