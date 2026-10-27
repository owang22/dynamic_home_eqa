# Constrained lab remap: scope (10-26, loc-research). Not built.

## Why

On 10-26 the saved map puts B's door about 0.3 m too close to the desk area. Evidence at the B stand (820–1260 s):
- the camera range to B is 2.74 m;
- the dog's own lidar range along the same bearing is 2.6–2.8 m;
- the map, from the console pose, gives 2.2–2.4 m.

Thick, smeared walls hide the offset from the tracker. A marker re-anchor on that map would put the dog inside a desk.
The odom-scale rebuild (K=1.157) is right in scale (two blind tape checks within 1%) but keeps this local error. It
came from the 10-23 mapping drive's own poses: go2_straighten fixed heading only; positions were raw odom.

## Method: a 2-D pose graph, then rebuild with the existing rebuild code

**Nodes:**
- the dog's pose every ~0.5 m or ~10° of motion, plus every still period;
- from 10-23 (the mapping drive) and 10-26 (today, 31 min, with the 7-min stand at B);
- more bags as they are recorded.

**Edges:**

| edge | measurement | noise |
|---|---|---|
| odometry, between consecutive nodes | odom increment × K (1.157) | heading σ from the gyro-drift study (~1.2°/min, wandering −4..+6) |
| lidar scan-match, between nodes ≤ 3 m apart (also across bags) | ICP / correlative match of each node's *fresh* voxels (born ≤ 20 s, each in its own odom frame, so stale ones don't enter) | from the match's curvature; degenerate directions (aisles) get near-zero information, as in the degeneracy study |
| marker, node to a marker landmark node | camera range and bearing only: marker yaw is unusable, MAD 9° | ~2% of range plus 1° bearing; gated fix_ok, ambig < 0.5, view ≤ 45° |
| tape (optional), a few pinned distances | Oliver's spans | |

- Marker landmarks A–D (and more) are free nodes. Their map positions come out of the solve, not from the old survey.
- Loop closures: cross-bag scan-matches, accepted only with a clear peak and consistent with marker edges. Today's
  bag revisits every 10-23 area.

**Solve:** robust least squares (Huber/Cauchy), then rebuild the grid by voting each node's voxels at the optimized
pose, as go2_straighten.rebuild does now (birth-pose placement, `p' = pose_birth ⊕ (p − r_birth)`).

## Tools

- **No GTSAM or g2o installed** (Python 3.11 go2 env; rosrobot has only a Ceres plugin).
- **Options:**
  - (a) `pip install gtsam` in a separate env: wheels exist for py3.11; this needs your OK to install;
  - (b) our own solver: scipy.optimize.least_squares with a sparse Jacobian and Huber loss. A 2-D graph of about
    3–5k nodes solves in seconds, needs no new dependencies, and is about 200 lines.
- **Recommendation: (b) first.** It's enough at this size. Move to GTSAM if graphs grow (many bags) or we want
  incremental iSAM2 online.
- **Scan matching:** reuse the console's wall-field correlative matcher (go2_mapper `_wall_field` / `track` search),
  widened and run on node-local submaps. Its curvature gives the information matrix (code from the degeneracy study).

## How saved things move

Each item is tied to the node(s) it was observed from and moves with them:
- **Places** are dog standing poses: exact. Map each place to the nearest node(s) in the old trajectory, then apply
  those nodes' old→new pose change (as convert_maps.py does for the scale, but with per-node transforms).
- **Objects:** labelled from views. Move them by the pose change of their observing nodes; with several observers,
  take the weighted mean. Hand-placed objects without observers move by the local displacement field (median
  voxel shift near them).
- **Markers** come straight out of the solve as landmark nodes. Write lab_markers_survey/*.json from the solve. Keep
  hand-placed marker objects; log their difference from the solve, so we learn which to trust.
- **The session file** (lab.session.json) is moved aside, so the next start does a fresh line-up.
- **Rollback:** as in scale/PROPOSAL.md, back up go2_maps/ whole.

## Effort (loc-research, offline, no robot time)

1. Node extraction plus odometry and marker edges from both extracts: ½ day.
2. Fresh-voxel scan matching with information from curvature, plus loop-closure gating: 1 day.
3. Solver (scipy, robust), sanity plots, ablations (no markers / no loops / no scale): ½ day.
4. Rebuild plus moving places, objects and markers, writing a dry-run maps folder: ½ day (reuses rebuild_scaled.py
   and convert_maps.py).
5. Validation (below): ½ day.

About 3 days of compute and analysis. Replays run 2 at a time at nice 19 while the console is live.

## Validation: decided before looking, on held-out data

- **Tape:** span A (9.93 m), A→cabinet (4.216 m), and any new spans Oliver tapes, measured on the new map. Target:
  within 2%. The current map gives 0.93 / 0.94.
- **Held-out markers:**
  - leave out all sightings from one bag, or the stand window, when solving;
  - then replay that bag on the new map and measure the camera-range residual to the solved landmarks;
  - target: |median| ≤ 5 cm in every window, including the B stand (now +35–40 cm);
  - camera range is known good to about 2% (vertical-edge check plus direct lidar ranges).
- **Direct lidar rays:** at the B stand, the first-hit range toward B against the map from the replayed pose.
  Target: within 10 cm (now +26 cm).
- **Replays:** 10-23 at +0/+4 and today, through the deployed tracker. Position and heading against the reference,
  fit, lost/suspect, and the tape-stop ratios, all no worse than now.
- **Then** the marker logging-only version (below) runs on the new map for a few drives. Its `marker_disagree` events
  should become rare before re-anchoring is switched on.

## Tracker translation limits: folded into this plan (10-26 night)

The still-dog limit ("both": translation while still only with ≥ 200 cells, at most 0.1 m per still period) is
deployed (21:00). It halved the 16:53 false shift (0.36 → 0.18 m) without regressions, but did not block it.

A per-correction limit tied to odom motion (|d| ≤ a + b·distance since the last correction) was calibrated on 10-23
(+0, +4, 3 varying-drift seeds; 288 corrections) and is not separable:
- good corrections made with almost no motion are as large as the bad ones (p95 0.14 m; steps are capped near
  0.12 m by the search anyway);
- every (a, b) tried clipped more good corrections than bad: 17 vs 5 at (0.06, 0.2), 7 vs 0 at (0.10, 0.3);
- a flat-direction (aisle) limit had only 17 degenerate cases, too few to judge.

Not tested held-out and not deployed. The false shifts come from the smeared, thick walls near B's door, not from
step size, so the remap above is the fix. After the remap, re-run this calibration: thin walls should separate good
corrections from bad by fit curvature rather than by size.

## Meanwhile: logging-only marker check (diff ready, not deployed)

`proposed_log/marker_log_only.diff`:
- `Mapper.marker_fix` with `MK_MOVE = False`. Every gated fix that would move the dog, or that the lidar disputes,
  becomes a `marker_disagree` loc event (pose, marker shift, fits, fresh cells) and raises `suspect`. The dog is
  never moved.
- The marker table comes from hand-placed objects with an aruco_id, then the survey files.
- Deploy step: copy `~/go2_overnight/markers_survey/{A,B}.json` into `/maps/lab_markers_survey/`.
