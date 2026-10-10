# Work log (BEHAVIOR-1K / OmniGibson trial), 2026-10-10

Times are local (from `date`).

- 13:07 GPU idle (47 MiB used), / 271 GB free, /mnt/nvme 620 GB free.
- 13:08 Cloned BEHAVIOR-1K tag v3.9.3-post2 (commit a8247a8c, 2026-10-05) to
  /mnt/nvme/oliver/robot/render_methods/behavior/BEHAVIOR-1K (987 MB with git).
  That release pins Isaac Sim 5.1.0 (Kit 107.3.1), Python 3.11, torch 2.7.0+cu128.
  Isaac Sim 5.x lists RTX PRO 6000 Blackwell and driver 580 as supported, so no version change needed.
- 13:09 Started the official `setup.sh --omnigibson --bddl --dataset --accept-nvidia-eula --accept-dataset-tos`
  inside a conda env I created first at /mnt/nvme/oliver/robot/render_methods/behavior/conda_env
  (setup.sh's `--new-env` would put it in ~/miniconda3/envs on /; I made the same env by hand:
  python 3.11, pip, setuptools<81, wheel from conda-forge, then ran setup.sh without --new-env).
  The Isaac Sim wheels are downloaded by setup.sh into a mktemp dir under /tmp (on /) and deleted after.
- 13:15 setup.sh finished the pip part (torch, bddl, OmniGibson, 26 Isaac Sim 5.1.0 wheels) in about 6 minutes,
  then FAILED at the dataset step: `import omnigibson` -> `ModuleNotFoundError: No module named 'warp'`.
  Cause: in this release `omnigibson/utils/usd_utils.py` imports `warp` at the top, but `warp-lang==1.12.0`
  is only listed under the `primitives` extra in OmniGibson/setup.py. Fix: `pip install warp-lang==1.12.0`.
- 13:16 Second import failure: `pyarrow requires NumPy 2.0 or newer, found 1.26.0`. pip had pulled
  pyarrow 26.0.0 (via lerobot -> datasets), but OmniGibson and Isaac Sim pin numpy 1.26. Fix:
  `pip install pyarrow==21.0.0`. After both fixes `import omnigibson` works.
  pip also reports harmless-looking conflicts: pillow 11.3.0 (omnigibson wants ~=11.0.0),
  websockets 17.2 (isaacsim-kernel wants 12.0, setup.sh forces >=15 on purpose).
- 13:16 Ran the three dataset downloads from setup.sh by hand (download_data.sh), with
  `download_behavior_1k_assets(accept_license=True)`, i.e. accepting the BEHAVIOR Data Bundle End User
  License Agreement (revision December 8, 2022; text quoted in REPORT.md). No account or login needed.
- 13:24 Dataset download done: behavior-1k-assets 3.9.0 (31.5 GB zip -> 33 GB on disk, about 7 minutes),
  robot assets 3.8.2 (2.8 GB), 2026 challenge task instances (620 MB). Zip goes through /tmp first.
  Library: 1,829 object categories, 8,635 models; 50 scenes (+ gates_bedroom).
- 13:25 HSSD route, failure 1: HSSD-hab glbs store textures as KTX2 with Basis Universal compression
  (glTF extension KHR_texture_basisu). Isaac Sim, trimesh and OmniGibson's importer cannot read them.
  `pip install pyktx` fails to build. Workaround: Khronos KTX-Software 4.4.2 Linux binary (no login,
  GitHub release) + scripts/hssd_unbasis.py transcodes each texture to PNG and rewrites the glb.
  233 glbs of home 107734254_176000121 (792 textures) in 2 seconds, 95 MB.
- 13:26 HSSD route, failure 2: OmniGibson's importer asserts the file name starts with a letter; HSSD names
  are hex hashes. Workaround: copies named "h<hash>.glb". Doors/windows live in objects/openings/ (first
  conversion run missed 9 of them).
- 13:27 HSSD route, failure 3: the shipped example `python -m omnigibson.examples.objects.import_custom_object`
  crashes in this release: `import_og_asset_from_urdf() got an unexpected keyword argument 'keep_instanceable'`.
  Workaround: scripts/hssd_og_import.py calls generate_urdf_for_mesh + import_og_asset_from_urdf directly.
  First test: an HSSD bar stool (glb) and an HSSD articulated kitchen cabinet (HSSD's own URDF with 2 doors and
  a drawer) both import.
- 13:30 First scene load (house_single_floor, 595 objects): 254 s cold, 143 s warm. Renders fine.
  CRASH: one camera pose (closet_1, camera placed inside the wardrobe's box) segfaults Isaac Sim in
  omni.syntheticdata's post-process every time (3 of 3 runs). Workaround: never put a camera inside an
  object's box.
- 13:39-13:45 Whole HSSD home imported with OmniGibson's tools: 109 of 109 static furniture models and 14 of
  14 articulated ones, 5.0 minutes. Doors/windows (9) failed: 7 from a naming bug of mine, then all 9
  with `RuntimeError('Accessed invalid null prim')`. Stage (walls, floors) imported as visual-only, 10 s.
- 13:47 Placement run 1 stopped: added furniture made with fixed_base=True cannot be sampled
  (`'RigidKinematicPrim' object has no attribute 'get_linear_velocity'`). Restarted without fixed_base.
- 13:50-14:05 CRASH, the big one: Isaac Sim 5.1 segfaults (omni.syntheticdata `_post_process_graph_tick`) whenever a
  camera with instance segmentation (`seg_instance` or `seg_instance_id`) or semantic segmentation looks at real
  content. Repeated in both homes, 6 crashes. rgb + depth never crashed (hundreds of pictures). Tests that seemed to
  clear semantic segmentation were looking at empty space (a check that could not fail). Workaround: no segmentation
  at all; the share of the picture each object fills is measured by hiding it and seeing which pixels' depth changes
  (og_common.visible_share), and camera directions are chosen with a one-depth-picture test of each box centre.
- 14:05 HSSD home: articulated furniture came out lying on its side. OmniGibson drops the HSSD URDF's empty root
  link and its -90 degree x turn. Fix: an extra +90 degree x turn on articulated instances (checked by box heights:
  fridge top 1.78 m, sink cabinet top 0.93 m). Each articulated object's box also contains a 1 m cube around its
  origin (bottom at -0.49 m), so box-based sampling on them is unreliable. The HSSD oven fails to load
  ("local transform is not orthogonal"); 181 of 198 furniture instances load (16 doors/windows + the oven missing).
- 14:10 HSSD home: OmniGibson's OnTop sampler on HSSD furniture placed 6 of 12 kitchen objects, and the rest fell
  to the floor once physics ran. Switched the HSSD route to computed poses: the snapshot's spot centre and height,
  objects in rows around it, no physics. All 6 views rendered.
- 14:15 Placement run 2 (BEHAVIOR house) far too slow: up to 9 minutes for one failed Inside. Two causes:
  (1) objects waiting to be placed were parked in mid-air far away, as BEHAVIOR's own task sampler does, and fell
  forever; (2) every sampling retry reloads the whole scene state (830 objects), 10 x 10 retries for Inside.
  Fix: park on the lawn north of the house; 4 x 6 retries; 1 x 3 for Inside another object.
- 14:20 t04: OmniGibson's Freight base driven through Rs_int, two cameras carried on it (pose set from the base
  each step). Unitree Go2 USD and two Isaac Sim people loaded straight from NVIDIA's public asset server (no login).
- 14:29 Hide-and-compare bug of mine: it made hidden objects visible again for the next picture (apron inside the
  backpack showed in the entryway). Fixed; HSSD views rerun.
- 14:35 Hide-and-compare bug 2: with 2 frames per change the depth picture lags one change behind, so each
  object got the previous object's share (caught because the big flour sack scored less than a small tin and the
  counter it stands on scored 0.02%). With 5 frames per change the numbers line up (counter 22-25%, flour sack
  largest). All share numbers in the report come from runs with 5 frames.
- 14:33 Go2 model and a resident figure standing in Rs_int (t04b), with the two cameras placed on the Go2 model.
  Needed `og.sim.editing_usd()` around plain USD edits, or OmniGibson raises "USD edit detected outside".
- 15:27 Placement run 4 CRASHED after 55 minutes and 214 of 226 objects (segfault): BEHAVIOR's transition rules
  (cooking/mixing recipes) fired during a physics step while things sat on the cutting board by the burner, and
  Isaac Sim crashed making particles (`RuntimeError: Accessed invalid null prim` in micro_particle_system, then
  segfault). The placement record was only written at the end, so it was lost (my fault: no checkpoint).
  Run 5 (15:28): transition rules off (`gm.ENABLE_TRANSITION_RULES = False`), record saved every 10 objects,
  retries 3 x 4 (1 x 3 for Inside another object) to finish in reasonable time. Fewer retries lower the success
  rate somewhat; BEHAVIOR's default is 10 x 10.
- 16:00 Coordinator relayed a change of priorities from the owner (not heard from him directly): look, lighting and
  Go2-camera views no longer matter; what matters is objects clipping into things or behaving oddly. Added
  scripts/t06_hssd_settle.py: whole snapshot on the HSSD home by computed pose, overlap test (gravity off),
  settle test (2 s), where each thing ended up, every change from the snapshot with its reason.
- 16:05 Settle run 1 (HSSD as first imported: static furniture with one convex hull each, articulated doors and
  drawers free): 141 of 208 objects pushed with gravity off, 134 of 208 moved >2 cm or tilted >10 degrees, 81
  dropped more than 10 cm. Causes seen in the pictures: drawers sliding open under load (joints free), the mirrored
  bathroom vanity standing in the wrong place (HSSD gives it scale x = -1; imported unmirrored), and single convex
  hulls filling basins, tubs, shelves and drawers. Run 2: doors and drawers held shut by stiff position drives.
  Run 3: also static furniture re-imported with CoACD convex decomposition (109 of 109 ok, 19 min of import spread
  over 4 processes, dataset hssd-assets-coacd).
- 16:30 Route A placement run 5 finished (40 min of sampling): 159 of 220 attempted objects sampled, 151 still holding
  their relation after 60 physics steps. 18 "inside another object" placements errored because of my bug (changing
  the retry count after launch is refused: macros are locked). Scene saved.
- 16:35 Route A pictures (t03): reloading the saved scene needs GPU dynamics (it holds a "sludge" particle system);
  then 11 of 12 pictures rendered and the run segfaulted with no Python frame before writing views.json. Poses
  parsed from the log into views_behavior_house_partial.json. The open-cabinet demo moved to t07 (Rs_int).
- 16:40 Cloth: all 21 cloth objects of the six busiest spots fail to load as cloth in this release
  (`'NoneType' object has no attribute 'GetPath'`: OmniGibson looks for a single mesh directly under the link and
  the 3.9.0 models do not have one). They load as rigid shells in one fixed crumpled shape.
- 16:45 t07: Rs_int kitchen cabinet; mug and bowl sampled Inside with the drawers open (both ok); on closing,
  the bowl was pushed out onto the floor, the mug stayed inside (0% of the picture shut, 0.15% open).
