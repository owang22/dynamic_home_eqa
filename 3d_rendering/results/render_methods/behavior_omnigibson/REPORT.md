# BEHAVIOR-1K / OmniGibson: report (2026-10-10)

Written by the BEHAVIOR trial agent and saved by the lead. `LOG.md` lists every failure in time
order; scripts are in `scripts/`, pictures in `pictures/`, run logs in `logs/`.

**Lead's check of the pictures:** the sink, drawer and entryway pictures match the text. One extra
fault the text does not mention: in `pictures/settle_v2_coacd_locked/entryway_floor_settled.png` a
dark object is still in mid-air in the doorway after the 2 s settle, probably one of the launched
objects. The owner's priorities changed during the trial, from the look of the pictures to
clipping and odd behaviour. That is why the first section is a physics check.

Representative pictures (under `pictures/`):
- `hssd_home/v3_living_raised_1.0m.png`: the HSSD home loaded into OmniGibson, with BEHAVIOR objects
  on the snapshot's coffee table.
- `settle_v2_coacd_locked/kitchen_kitchen_sink_cabinet_countertop_beside_the_kitchen_s_settled.png`:
  after 2 s of physics, a water bottle placed beside the sink has tipped into the basin.
- `open_close/bottom_cabinet_bamfsz_0_open.png` and `..._shut.png`: a BEHAVIOR drawer cabinet open
  with a mug inside. Closing the drawers pushed out the bowl that was also inside, onto the floor.

## Clipping and odd behaviour, on the HSSD home

**Setup** (`scripts/t06_hssd_settle.py`, results in `settle_v2_coacd_locked.json`):
- HSSD home `107734254_176000121`: 181 of 198 furniture pieces loaded.
  - Missing: all 16 doors and windows (their import failed), and the range/oven ("local transform
    is not orthogonal").
  - Walls and floors are visual only, so walls have no collision. A floor plane gives the floor
    collision.
- Static furniture was re-imported with CoACD convex decomposition. Doors and drawers were held shut
  with joint limits.
- 220 snapshot objects have a BEHAVIOR model; 208 were simulated.
- Objects were put at the snapshot's own spot centre and height, without samplers. Inside each
  spot's square, a ray test found where the support surface really is, and footprints were packed
  so they don't overlap.

### (1) Settle test (gravity on, 60 steps × 1/30 s = 2.0 s)

- **101 of 208 moved more than 2 cm or tilted more than 10°.** 73 moved over 10 cm, 23 moved
  2-10 cm, 5 only tilted. 49 dropped more than 10 cm.
- Run-to-run spread: the same test with an extra joint lock gave 108 of 208. The first import (one
  convex hull per piece, drawers free) gave 134.
- By the kind of spot the snapshot names:

  | spot kind | moved / total |
  |---|---|
  | flat surfaces | 51/105 |
  | closed cabinets and drawers | 23/52 |
  | floors | 13/33 |
  | cooktop | 6/6 (the range is missing) |
  | seats | 4/5 |
  | washer drums | 3/3 |
  | basins | 0/3 |
  | mattress | 1/1 |
  | on the mirrored furniture | 10/10 |

- Because walls have no collision, objects pushed out of overlaps flew through walls into other rooms:
  - shampoo, conditioner and nail clippers 7-8.5 m from the bathroom vanity;
  - wine glass 5.5 m, from the dining table to the kitchen floor;
  - laundry clothes 2-2.5 m.
- Every object, with distance, tilt and where it ended: `settle_big` and `ended` in the JSON.
  `scripts/summarise_settle.py <json> full` prints the list.

### (2) Overlap test (gravity off, 1/3 s; "pushed" means it moved more than 5 mm or turned more than 3°)

- **128 of 208 were pushed out of something.**
  - For 108 of them, the object's box overlapped a piece of furniture at placement.
  - For 20, no box overlap; they were pushed by tight contacts with each other.
- Main causes:
  - Collision shapes of drawers, compartments, piano and fireplace shelves and washer drums are solid
    where the snapshot has open space.
  - The mirrored vanity stands in the wrong place: HSSD gives it scale x = -1 and it was imported
    unmirrored.
  - Rigid cloth shells overlap their neighbours.

### (3) Ended on a different kind of surface (only objects that left their furniture)

| from (snapshot spot) | to | count |
|---|---|---|
| flat surface | floor | 29 |
| flat surface | seat | 2 (keys and a music book: piano shelf → piano stool) |
| flat surface | basin | 1 (water bottle: "countertop beside the kitchen sink" → the sink basin) |
| cooktop | floor | 4 |
| closed space | floor | 4 |
| drum | floor | 3 |
| seat | floor | 2 |
| floor | tub | 1 |
| various | no surface found | 9 |

- The snapshot itself already puts 3 objects in basins, 6 on cooktops, 6 on seats and 3 on mattresses.
- The first layout (a plain square of the spot's area) put counter objects over the sink basin. The
  ray test fixed that, except for the one bottle above.

### (4) Every change from the snapshot, with reasons (`changes` in the JSON)

- **Left out:**
  - 7 have no residents to be worn by or carried in a pocket;
  - 24 have no BEHAVIOR model (bookmark, headphones, scissors, remote control, ...);
  - 1 because its reference has no model.
- **Stand-in models:** 26 (loafer → sports shoe, jacket → wool coat, thermos → water bottle, ...).
- **Kept out of sight and not simulated:** 11 objects inside a backpack, tote bag, first-aid kit or
  jeans. BEHAVIOR's bag models are solid shells.
- **Placed overlapping or overhanging:**
  - 30 because the ray test found no surface at the spot's height. That happened on 18 spots: both
    cooktops (range missing), the mirrored vanity, piano and fireplace shelves and compartments, both
    washer drums, two chair seats, the coat-rack shelf, the clothes rail, a toilet top, the fridge
    crisper drawer and a vanity compartment.
  - 22 because no free footprint fitted on the surface.
- No retries on this route.
- **Route A** (BEHAVIOR's own samplers, BEHAVIOR's house):
  - Samplers ran with 3×4 retries; 10 placements needed the cabinet opened first (4 succeeded).
  - 34 "sampler said no".
  - 6 errors "Container object must have a fillable mesh" (desk, nightstand, piano lack Inside
    annotations).
  - 16 errors from the agent's own bug (it changed the retry count after launch; it is locked).
  - 3 skipped because their reference was not placed; 2 had no matching furniture (fireplace).
  - 8 sampled but no longer held after the 2 s settle; e.g. the thermos and sponge slid onto the
    neighbouring counter run.

### (5) Cloth

- All 21 cloth objects in the six busiest spots **fail to load as cloth** in this release:
  `'NoneType' object has no attribute 'GetPath'`. The loader looks for a single mesh directly under
  the link, and the 3.9.0 models don't have one.
- They load as rigid shells instead, each frozen in one crumpled shape. The towel "draped over the
  vanity edge" in the earlier picture is that fixed model shape, not physics.
- As rigid bodies:
  - Towels: the bath towel was launched 4 m (mirrored vanity) and the guest towel 2.3 m; the hand
    towel fell 0.8 m to the floor. The dish towel and tea towels stayed put (≤4 cm).
  - Clothes heaped on the laundry floor were launched 1-2.5 m. Clothes on the bathroom floor mostly
    stayed within 20 cm, as an interpenetrating heap by the toilet
    (`settle_v2_coacd_locked/bathroom_2_floor_settled.png`).
- The laundry-floor camera picked a bad pose (it shows a wall), so there is no usable picture of
  that floor.

### Hanging and draping relations

OmniGibson and BDDL have relations our four lack:
- **Draped:** cloth over a rigid object, with a sampler. Needs working cloth loading and GPU dynamics.
- **AttachedTo:** joins two rigid objects at "attachment" points on the models. Only 1 of 4 coat
  racks, 1 of 7 hangers and the wall nail have them; no towel rack or hall tree does.
- **Overlaid**, **Folded/Unfolded** and **Touching** also exist.
- Uses across BEHAVIOR's 1,000 activities: ontop 5,330, inside 2,639, nextto 173, under 9,
  attached 110, draped 39, overlaid 27, touching 29.

## Original questions

### 1. Did it run?

- Release v3.9.3-post2, which uses Isaac Sim 5.1; it supports Blackwell with driver 580. No Xid errors.
- Install: a prefix conda env at `/mnt/nvme/oliver/robot/render_methods/behavior/conda_env`, built
  with the official `setup.sh` (env made first, then setup.sh without `--new-env`).
- About 79 GB under `/mnt/nvme/oliver/robot/render_methods/behavior/`: env 20 GB, dataset 33 GB
  (31.5 GB zip, 7 minutes), Omniverse cache 21 GB.
- **Licences accepted:** the NVIDIA Isaac Sim EULA, and the BEHAVIOR Data Bundle EULA (revision
  December 8, 2022). Its terms: non-commercial academic research only; the data is encrypted; no
  extracting or reverse engineering; use only inside OmniGibson; no redistribution of the key or
  data. No accounts or logins anywhere.
- Fixes needed: `warp-lang` missing; pyarrow 26 needs numpy 2 (pinned to 21); the shipped
  custom-import example is broken.
- **Instance and semantic segmentation segfault Isaac Sim** whenever real content is in view
  (6 crashes, not fixed). Each object's share of the picture was measured by hiding it and
  comparing depth instead.
- Other crashes:
  - BEHAVIOR's cooking/transition rules crashed a 55-minute placement run.
  - The route-A render run segfaulted after 11 of 12 pictures, so its poses come from the log
    (`views_behavior_house_partial.json`).

### 2. Placement

**Route A** (BEHAVIOR's house `house_single_floor`, with 11 extra furniture pieces added from the
library): **159 of 220 attempted objects sampled; 151 still held their relation after 2 s.**

| relation | sampled / attempted | still held after 2 s |
|---|---|---|
| on_top | 106/128 | 98 |
| inside | 43/74 (16 not tried: agent's bug) | 43 |
| next_to (no sampler in OmniGibson; placed by hand and checked) | 10/17 | 10 |
| under | 0/1 | 0 |

- Snapshot objects marked hidden: 41 of 76 placed and still held their relation after settling.
- Placement took 40 minutes; scene load 141 s.

**Route B** (the HSSD home itself) works by computed poses (numbers above). Remaining work:
mirrored instances (27 in this home), doors and windows, the oven, wall collision, better shelf and
compartment collision.

### 3. Objects

- 162 of the snapshot's 187 types have a BEHAVIOR category; 138 of them are the same kind of thing.
- 226 of 251 objects get a model.
- Duplicates: 9 mugs → 9 different models (14 available). All 9 chargers, 3 phones and 6 towels
  share one model each. Appearance words ("cream painted stripe") are not followed.

### 4. People

None in OmniGibson or BEHAVIOR. Isaac Sim's public asset server (no login) has people; they were
loaded as static T-pose figures. Not animated.

### 5. Look and speed

An independent checker scored the pictures about 2/5 for realism: denoising blur, very dark areas,
blown-out windows. It could not find keys, pens or glasses in any picture. Rendering takes about
0.011 s per frame at 640×480 once loaded. GPU memory 7-21 GB per process.

### 6. Robot

- No quadruped in OmniGibson ("A1" there is an arm).
- The Freight base was driven through BEHAVIOR's small Rs_int house, carrying cameras at 0.37 m and
  1.0 m.
- A Unitree Go2 model from Isaac's asset server stands in the scene, with cameras placed on it. It is
  static: walking would need a gait policy that OmniGibson doesn't include.

### 7. Verdict

- BEHAVIOR gives us our four relations, samplers, and openable cabinets that really hold their
  contents. Its own houses work, with 151 of 220 attempted objects placed and holding (about 70%), at
  40 minutes per snapshot.
- The HSSD home loads, but under physics about half the objects move. The causes are import faults
  (no wall collision, mirrored furniture, missing furniture, solid compartments), cloth not loading,
  and segmentation crashing on this card.
- Usable as a renderer for our snapshots only after about a week of fixing those, and only for
  research (the licence).

**Not done:** an animated person; a walking Go2; a working views.json with full poses for route A
(the run crashed); a correct mirrored-furniture import; a laundry-floor picture from a sensible pose;
cloth simulation of any kind.
