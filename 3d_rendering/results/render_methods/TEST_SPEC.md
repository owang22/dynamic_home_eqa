# Rendering methods: shared test (2026-10-10)

Oliver asked for three ways of rendering to be tried and compared, one agent each:
Habitat-sim with HSSD (known to work), BEHAVIOR-1K / OmniGibson (StanfordVL), and EnvDreamer
(arXiv 2610.04301, MIT, Unreal Engine 5). Every method renders the same test so the reports can
be compared side by side.

## What the renders are for

The robot's job is to find objects in a home whose residents move things. The household
generator (`3d_rendering/src/lived_home`) writes a snapshot of where every object is, every two
hours. A renderer must turn one snapshot into the pictures a robot camera would take, so search
methods can be run on pictures instead of on text. Later the same methods run on a real Unitree
Go2 Pro in a lab, so how close the pictures look to real camera photos matters.

## The test snapshot

`3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json`: household A (Mara and
Julian), HSSD scene `107734254_176000121`, day 7 at 18:00. It holds 187 places and 251 objects.
Each object has a type, a plain appearance ("black glass"), colour, material, size, a place, and
one of four relations to a reference (`inside`, `on_top`, `under`, `next_to`; also `worn_by` and
`in_pocket_of` for people). Each place has the HSSD furniture instance, its position and
rotation, a spot centre and height, and whether it is articulated. 76 objects are hidden: under
something, or inside a closed container. Mara is on a barstool in the kitchen and Julian is on
the sectional in the living room.

## Six test views

Frame each of these spots so that the spot and what is on it fill a good part of the picture:

1. `kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range` (12 objects)
2. `dining_room_dining_table_tabletop` (6)
3. `living_room_living_room_coffee_table_top` (8)
4. `bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand` (5)
5. `bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top` (8)
6. `entryway_floor` (8, floor clutter)

Render each view at two camera heights: **0.37 m** (the Go2's built-in camera, about 100-degree
lens, up to 15 degrees of downward tilt) and **1.0 m** (a raised camera, 75-degree lens). Use
640x480 or larger. Write down the camera pose of every picture in a `views.json`.

If a method cannot use this HSSD home (for example BEHAVIOR's own scenes), map the snapshot onto
the closest scene the method has: the same objects with the same relations onto furniture of the
same kind. Say exactly what was mapped and how.

## What every report must cover

Put each method's work in `3d_rendering/results/render_methods/<method>/`, with a `REPORT.md`,
the pictures, and the scripts that made them. If you set something up outside the repo, list
the paths. The report must cover:

1. **Did it run?** What was installed, where, how big, how long it took, any licence accepted,
   and every failure along the way.
2. **Placement:** how many of the 251 objects and 4 relations could be placed as the snapshot
   says. Count per relation. Say what happens to hidden objects, and whether drawers and doors
   can be shown open or shut.
3. **Objects:** where the 3D models came from, how many of the snapshot's 187 object types have a
   model, and whether two objects of the same type can look different (the snapshot often has
   several mugs, chargers or books).
4. **People:** can a resident be shown in the scene (static figure, animated, or not at all)?
5. **Look:** the pictures themselves. Lighting, textures, how believable they are next to a real
   photo, and whether small things (pens, keys, glasses) can be made out at 0.37 m and at 1.0 m.
6. **Speed:** seconds per picture once loaded, load time per scene, GPU memory used.
7. **Robot:** is there a Go2 or similar quadruped model, and can the camera be moved and the
   robot driven?
8. **Effort to make this the main renderer:** what would have to be built, as a list of tasks.
9. **Verdict** in three lines.

## Rules for all three agents

- Look at every picture before describing it (open the image file). A model can load without
  error and draw nothing: check how much of the picture each object fills.
- The machine has one GPU (RTX PRO 6000 Blackwell, 96 GB, driver 580) shared by the three
  trials. Check `nvidia-smi` before a large job and keep peak use under about 40 GB. The card has
  fallen off the bus before (Xid 79). If `nvidia-smi` stops answering, stop GPU work and report
  it. Do not try to reset the card.
- Disk: `/` has about 270 GB free and `/mnt/nvme` about 620 GB. Put large installs and datasets
  under `/mnt/nvme/oliver/robot/render_methods/<method>/`.
- Do not modify `3d_rendering/src/lived_home` or any results outside your own folder.
- Do not spend money on hosted models (no Luna or Terra calls), and do not commit to git: the
  lead reviews and commits.
- Use plain words in the report. Name things by what they are.
