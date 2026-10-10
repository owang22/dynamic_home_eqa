# Habitat-sim with HSSD: report (2026-10-10)

Written by the Habitat trial agent and saved by the lead. **Lead's check of the pictures:** the
coffee table, kitchen counter, dining table and open drawer pictures match the text below. One
correction: the "vase" in the 0.37 m dining-table picture is the table's own pedestal base. That
picture shows only the table's underside, its base and chair legs.

The snapshot `lived_home/hssd_a/day_07/positions_1800.json` (household A, day 7, 18:00) is placed
into its own HSSD home `107734254_176000121`, articulated version. That is the version the
household's places were built from, so no mapping onto another scene was needed.

All files were made by the scripts in `scripts/`. They run with
`~/miniconda3/envs/dynamic_eqa/bin/python`, except `resolve_models.py`, which needs
`~/miniconda3/bin/python` for the `objaverse` package.
- Camera pose of every picture: `views.json`
- Where every object went and why: `checks/placement.json`
- Pictures: `pictures/`; copies with each object of the spot outlined in yellow: `pictures/checks/`
- Model contact sheets: `checks/model_sheet_1..6.jpg`; verdicts by eye: `checks/model_verdicts.json`;
  rejected models: `checks/rejected_models.json`

## 1. Did it run?

Yes. Nothing new was installed: habitat-sim 0.3.3 (headless) and HSSD were already on the machine.
Opening the articulated home takes 3.0 s from a warm disk cache.

Set up outside the repo: 287 Objaverse models (626 MB) in
`/mnt/nvme/oliver/robot/render_methods/habitat_hssd/objaverse/hf-objaverse-v1/glbs/`, fetched in
34 s. The index files are links to the existing cache at `/mnt/nvme/oliver/robot/objaverse_cache`.

Licences: none accepted. The Objaverse models carry their authors' licences; of the 342 picks,
306 are CC-BY, 9 CC-BY-NC, 7 CC-BY-NC-SA, 4 CC-BY-SA and 1 CC0 (per model in
`checks/lvis_to_download.json`). HSSD's terms were not re-checked.

Failures along the way, all fixed:
- **No standing points found.** This navmesh sits at y = 0.17, so a test at floor height found
  nowhere to stand. It now snaps points to the navmesh.
- **No surfaces on cabinets, desks or the sideboard.** An articulated object's own box is empty in
  habitat-sim; the box is now built from its parts.
- **Matrix maths.** Magnum matrices multiply with `@`, not `*`.
- **A figure sank 0.25 m into the sofa.** habitat-sim positions an object by its centre of mass,
  not its mesh origin. Figures are now placed by their box.
- **A packet floated 20 cm above the counter.** The resting-height check counted walls seen at a
  slant. It now counts only the spot's furniture, placed objects and the floor.
- **A towel poked out through a cabinet's side panel.** Drawers are now pulled out, scanned, filled
  and shut.

## 2. Placement

219 of 251 objects are in the 3D scene.

| relation | in snapshot | placed | not placed, and why |
|---|---|---|---|
| on_top | 140 | 127 | 13 have no model |
| inside | 84 | 73 | 6 have no model; 5 are bigger than the box of the closed bag or kit they are in |
| next_to | 19 | 18 | 1 has no model (shoehorn) |
| under | 1 | 1 | |
| worn_by | 4 | 0 | figures are single fixed meshes |
| in_pocket_of | 3 | 0 | same |

19 of the 219 placed objects did not fit and overlap something or hang over an edge
(`did_not_fit` in `checks/placement.json`). Most are on small or crowded spots: 5 of 7 in one
kitchen drawer, 4 on the toilet-room vanity, 3 hand towels on small shelves.

**How each relation became a 3D position** (full rules in `scripts/scene.py`)
- **Finding a spot's surface:** small cameras look straight down from 25 cm above the spot height.
  - A 2 cm cell counts when the first thing drawn there is the spot's furniture (for a floor, the
    floor inside the room) and lies within 3 cm of the spot height.
  - Anything drawn above blocks the cell, such as an upper cabinet over a counter.
  - Only cells joined to the spot centre count. A lower shelf is scanned again from 8 cm.
- **on_top a place:** the object goes on a free cell.
  - At least 60% of its footprint must lie on free cells.
  - It rests on the highest drawn point under it, so it sits on a cushion rather than in it.
  - It is lined up with the furniture, a quarter turn either way, with up to ±15° of wobble.
- **on_top an object:** its centre goes inside the reference's footprint, shrunk by 20%. It rests
  on what is drawn there, such as a board's face or a thermos lid.
- **next_to:** on the reference's surface, with the footprints 1-15 cm apart. In the 4 cases where
  the reference is the place itself, the object goes on that place.
- **under** (one case, a coaster under a mug): the coaster takes the mug's spot and the mug sits
  on it.
- **inside a drawer:** the drawer is pulled out in the simulator, its bottom is scanned, the
  objects are placed, and the drawer is shut. The objects move with it (20 objects in 8 drawers).
- **inside a closed cabinet, compartment or drum** (37 objects): set in rows around the spot centre
  inside a square of the spot's area. Not checked by eye.
- **inside an open place** (sink, fireplace opening) **or open container** (bowl, basket, tray):
  dropped onto the bottom at the centre. A second object lands on the first.
- **inside a closed bag or kit:** set at the container's centre if it fits in the container's box;
  otherwise left out (5 cases).

**Stacking and capacity**
- Stacking comes from the resting-height rule: an object put where another already is rests on
  top of it.
- Capacity is not checked against the snapshot. When free cells run out, the next object overlaps.
- The snapshot asks for 4 stacks that are unlikely in real life, and they are placed as written:
  a water bottle on a thermos, herbs in a glass on the same thermos, a dish towel on a sponge, a
  wooden tray on a mixing bowl.
- Scanned areas compared with the snapshot's areas:
  - coffee table: 0.85 m² against 0.88
  - dining table: 1.34 m² against 2.55
  - laundry room floor: 0.89 m² against 7.29 (the room outline includes the floor under the machines)

**Hidden objects:** 65 of 76 are in the scene at their real position.
- Shut drawer: all 7 of its objects have 0 pixels in both shut pictures. Opened, 7 of 7 show at 1.0 m.
- One leak: a notebook inside the backpack shows 13 pixels through it in the 0.37 m entryway picture.

## 3. Objects

The snapshot has **187 object types**. Models were tried from four sources in order:

1. The earlier strand's picks (`asked_about_models.json`): 35 objects
2. The reviewed external_props set: 29 objects
3. HSSD's small-object library, found by WordNet label and name with a size filter: 56 objects
4. Objaverse, by LVIS category, ranked by whether the model's own name contains the type's word,
   then by likes: 111 objects

Every model was photographed alone and checked by eye. 36 Objaverse models were rejected because
they were not the thing: a pistol for a hair clip, SpongeBob for a sponge, rocks for earplugs,
character figures for pyjamas, a skateboard for a bookmark, an octopus tentacle for nail clippers,
cheese for butter.

| verdict by eye | types | objects |
|---|---|---|
| the right kind of thing | 114 | 169 |
| near stand-in (crisp packet for pasta, cleaver for a table knife, All Stars for loafers, one carrot for a bunch) | 53 | 62 |
| no model | 20 | 20 |

Before this work, 64 types had a candidate on disk, 115 needed Objaverse and 8 had no source at all
(metronome, sleep mask, garment bag, dental floss, delicates bag, lint roller, sewing kit,
shoehorn). After rejection, 12 more have none: whisk, apron, binder clips, bookmark, earplugs,
fabric samples, nail clippers, sponge, hair clip, corkscrew, butter, wool dryer balls.

**Cheapest way to cover the rest**
- **Objaverse is cheap to fetch but costly to check.** 287 models took 34 s, but only 244 of 342
  picks had the type's word in their own name. About 1 type in 3 needed a person to look.
- **Clothing is the weakest group.** Objaverse clothes are modelled on a body or a hanger, and laid
  flat they look like gloves or blobs.
- **HSSD's library is the best value.** It renders in the same style and at true size, but has
  little food, tools, clothing or small personal items.
- Suggested order:
  1. More HSSD name searches.
  2. A hand-picked list (Objaverse-XL or Sketchfab) for about 20 small personal items.
  3. Simple generated models for flat things: folded cloth, paper, envelopes, folders.

**Same type, different look:** partly. Different models are given out in turn within a type.

| type | objects | different models |
|---|---|---|
| mugs | 9 | 6 |
| paperback books | 9 | 8 |
| towels | 6 | 6 |
| water glasses | 6 | 5 |
| phone chargers | 9 | 2, alternating |
| reading glasses | 2 | 1 |

Models do not follow the snapshot's colour words (the "black braided" charger is white).
habitat-sim has no per-object colour change, so this would need edited copies of the model files.

## 4. People

Static figures only, from HSSD's posed figures:
- **Mara:** "People Mary sitting", on her barstool facing the island
  (`pictures/resident_mara_high_1.00m.jpg`). The figure does not match her description.
- **Julian:** "Alberto seated", on the sectional seat nearest the coffee table, facing away from
  the backrest (`pictures/resident_julian_high_1.00m.jpg`). His feet are partly inside the sofa's
  front.

There is no animation, and nothing can be worn or carried.

## 5. Look

12 test pictures (640x480), plus 4 drawer pictures and 2 resident pictures.

Spot objects showing with at least 20 pixels (hidden ones not counted):

| spot | 0.37 m, 100° | 1.0 m, 75° |
|---|---|---|
| kitchen counter by the range (12, 11 placed) | 2 | 10 |
| dining table (6) | 0 | 6 |
| coffee table (8, 7 placed) | 3 | 7 |
| nightstand (5) | 3 | 5 |
| bathroom 2 vanity (8, 6 placed) | 4 | 6 |
| entryway floor (8 visible, 7 placed) | 6 | 7 |

- **The 0.37 m camera** cannot see the top of anything higher than about 0.5 m when tilt is
  limited to 0-15° down. It sees only what stands up past the edge. The dining-table picture shows
  the underside of the table, its pedestal base and chair legs.
- **Small things:**
  - keys on the entryway floor: 1 pixel at 0.37 m (1.35 m away), 201 pixels at 1.0 m (1.5 m away)
  - on the nightstand at 1.0 m (0.6 m away): chargers 809 and 1274 pixels, phone 1809
  - paring knife on the cutting board at 1.0 m: 1023 pixels
  - pens, nail clippers, earplugs and the hair clip are not in these views with a model
- **Lighting:** six fixed directional lights, no shadows. Mean brightness is 76-159 of 255. The
  pictures look flat and slightly plastic, and dark objects on dark wood (wallets, a watch, a
  cast-iron pan) lose their shape.
- **Textures:** HSSD models look clean and plausible. Many Objaverse models are sharper or
  cartoon-like (a lime-green child's backpack, a cartoon shampoo bottle), so the mix of styles shows.
- **Next to a real photo:** clearly rendered. There are no shadows, no contact shading where things
  meet surfaces, and no clutter beyond the snapshot's objects.
- **Visible faults:**
  - a towel lies across the vanity basin, resting on a shampoo bottle
  - the magazine is an upright stack of magazines
  - the sketchbook looks like a vinyl record
  - both pairs of entryway shoes are the same red All Stars

## 6. Speed

- Open the home: 3.0 s
- Load the 251 models: 4.2 s
- Place everything, including the people: 15.3 s (mostly the downward scans)
- Ready scene in total: 18.4 s
- One 640x480 colour picture: 2.2 ms; colour, ids and depth together: 6.3 ms
- Choosing a camera position tries 100-300 positions at 160x120 per view, under a second per view
- Peak GPU memory for this process: 4.46 GB (from the nvidia-smi process table)

## 7. Robot

There is no Go2 or other quadruped model. The camera can be put at any pose. The navmesh (0.2 m
body radius) gives walkable floor and paths, and every camera in `views.json` stands on it.
Driving would mean moving the camera along navmesh paths. habitat-sim loads URDFs, as the cabinets
show, so a robot body could be added; that is untested.

## 8. Effort to make this the main renderer

1. **Run over every snapshot.** Write pictures and `views.json` per snapshot, reusing one loaded
   scene. About 20 s each; mostly done.
2. **Fill the model gaps.** Find models for the 20 types with none and replace the worst 20 or so
   stand-ins (clothing, folders, cutlery, food bags). About a day by hand.
3. **Per-object colour.** Write recoloured copies of a model's material, so several chargers or
   mugs differ and match the snapshot's colours.
4. **Folded or crumpled clothing,** from generated cloth or ready-draped models.
5. **Capacity check.** Feed overflows back to the household generator (19 objects did not fit), and
   add a rule against unlikely stacks.
6. **Shelves behind doors.** Open the door, scan the shelf and place contents, as is done for drawers.
7. **Worn and pocketed objects.** Show them with the person, or mark them as not visible in the data.
8. **Lighting.** Add shadows or ambient occlusion, or post-processing, then compare against real
   Go2 photos.
9. **Go2 body and camera.** Add a Go2 model or footprint, and check the camera against the real one
   (0.37 m, about 100°, 0-15° tilt).
10. **Low-camera scoring.** Decide how low views are scored, since a fixed 0-15° tilt sees almost
    no tabletop.

## 9. Verdict

- **Works today on the household's own home:** 219 of 251 objects placed by rule, drawers that open
  with their contents, seated residents, and a picture in milliseconds.
- **Weak points:** object models (20 types missing, 62 objects with stand-ins, clothing poor) and
  the flat, shadowless look.
- **Recommendation:** it is the cheapest main renderer to adopt now; measure the realism gap
  against Go2 photos before committing.

## Questions asked of this method

**Can articulated furniture move, and be shown open?** Yes. All 33 articulated pieces in this home
load from URDF as moving parts in habitat-sim 0.3.3: kitchen cabinets, drawer units, the fridge,
desks, nightstands and the sideboard. Drawers slide and doors hinge (for example 0 to 2.36 rad for
the upper kitchen cabinet doors), and setting the joint value opens them.
- Rendered: the bottom drawer of the kitchen drawer cabinet, pulled out 0.43 m with its 7 objects
  (`pictures/drawer_open_high_1.00m.jpg`), and the same drawer shut with nothing showing
  (`pictures/drawer_shut_high_1.00m.jpg`).
- Not rendered: an open door. The same call works on doors, but their shelf contents are not placed
  by scanning yet.

**How the four relations became 3D positions, and what happened to stacking and capacity:** section 2.

**Types without a model, and the cheapest cover:** section 3. Of 187 types, 123 had no candidate on
the machine before this work. After downloading and checking by eye, 20 still have none.
