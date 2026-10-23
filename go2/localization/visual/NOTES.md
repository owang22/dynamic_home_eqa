# Camera relocalization from the upper image band: working notes (2026-10-23, offline, no dog)

Scripts and outputs live in `go2/localization/visual/`. Problems are in `problems_found.md`.
Shared loader: `vcommon.py` (records from `lab_agent/memory.py load()`, trust flags from the event logs).

## 0. Data and pose trust

- 1109 pictures: 616 trail frames on 10-19 (15:5x-17:1x), 185 on 10-20 (11:19-12:4x and 19:1x-19:5x),
  264 trail frames on 10-22 (15:3x-16:5x), plus 44 agent photos/look-arounds on 10-22.
- **Stored size:** trail frames are 640x360 (downscaled), some photos are 1280x720. K is scaled to the actual size.
- **Calibration:** `front_camera_720.yaml`, copied read-only from the go2-lab image
  (`/ros2_ws/src/nesl/go2_robot_sdk/calibration/`). fx=864.4, fy=863.7, cx=639.2, cy=373.3 at 1280x720, so the
  HFOV is 73.0 deg. Plumb-bob distortion is strong (k1=-0.355, k2=0.102). Through the distortion the top edge
  at the centre column is +24.9 deg above level, and the bottom edge is -23.1 deg.
- **Trust filter** (`vcommon.load_records`). A frame is trusted when all of these hold:
  - not 10-19 before 16:54 (Oliver's rule; this removes 526 of the 616 10-19 frames);
  - no localizer jump/start/hand event within 5 s (events from `../results/jumps_events.csv`);
  - odom turn rate under 30 deg/s at the frame time;
  - the index pose agrees with the event-log map pose within 0.3 m.
  Result: 85 trusted frames on 10-19, 184 on 10-20, 298 on 10-22 (567 in total).
- **Index pose vs event-log map pose at the same time:** median 0.5-0.7 cm, p90 4-8 cm. The 10-22 maximum is
  1.85 m / 57 deg, at a frame next to a jump. So the index stores the console pose faithfully. The pose noise is
  the console's own noise, which the lidar study puts at about 0.35 m median against its refined poses (still
  under way).

## 1. What is visible above the clutter (task 1)

I looked at 30 frames spread over the lab (farthest-point sampling over x, y, yaw), all days:
`figs/task1_survey_[0-4].jpg`. The yellow line is the computed horizon.

**The tilt question: there are no tilted frames.**
- 1107 of 1109 pictures have look_deg 0. The two that don't are photos at look 16 and look -5.
- The look-16 photo (`p1792710742_11`) and the look-0 photo taken 5 s before at the same spot
  (`p1792710737_10`) are pixel-for-pixel the same framing: `figs/task1_tilt_pair_0_vs_16.jpg`. The look -5 one
  is also the same as its look-0 neighbour.
- So the camera was level when the picture was taken. `photo` waits until the dog is still, and `look` springs
  back after about 0.5 s. **Every picture we have is a level picture.** Problem P1.

**Horizon row (level ray, centre column)**, for 640x360 pictures and nominal pitch = look_deg. Computed through
the distortion model (`vcommon.horizon_row`):

| look_deg | horizon row (of 360) | elevation at top edge | elevation at row 90 | elevation at bottom |
|---|---|---|---|---|
| -5 | 149 | +19.9 | +7.8 | -28.1 |
| 0 | 187 | +24.9 | +12.8 | -23.1 |
| 5 | 224 | +29.9 | +17.8 | -18.1 |
| 10 | 262 | +34.9 | +22.8 | -13.1 |
| 16 | 307 | +40.9 | +28.8 | -7.1 |

- **Measured horizon** (vanishing points of floor and ceiling lines in 116 undistorted level frames;
  `horizon_est.py`): median row 195 (IQR 173-226). That is a body pitch of about 1 deg nose-down, which matches
  the nominal 187 within noise. At look 0, the horizon is at **52-54 % of the image height**.

**What a level camera at 0.4 m can see:**
- **Ceiling (assume ~2.7-3.0 m, i.e. 2.3-2.6 m above the camera):** it enters the top edge (+24.9 deg) only beyond
  about 5 m, and the top corners only a bit closer.
  - In the sample it shows in about 7 of 30 frames, always as a thin strip (top 5-15 %): troffer lights, ceiling
    tiles, one vent, a security camera / smoke detector. All of these were views down the long open axis of
    the lab.
  - The VLM descriptions list a ceiling object in only 62 / 1109 frames (it was asked for findable objects,
    so this undercounts, but it agrees).
  - At look +16 (if a tilted frame could be captured) the ceiling would enter the frame beyond about 2.8 m, and
    the top 40 % of the frame would be above +16 deg.
- **Desk height (0.75 m, 0.35 m above the camera):** +10 deg at 2 m (row ~110), +4 deg at 5 m (row ~160). So
  everything in the top ~30 % of a level frame is above desk height out to ~2 m, and above ~1.4 m at 5 m.
- **Stable things that do appear in the upper band:**
  - lavender upper walls and wall corners;
  - wooden doors with frames and kick plates;
  - the whiteboard wall;
  - fire extinguishers (VLM: 93 frames);
  - a wall TV / monitors on desks;
  - tall light-wood cabinets and wardrobes, metal shelves (with boxes);
  - the black water dispenser, the far desk rows with their monitors, ceiling lights.
  - Monitors are "quasi-static": they rarely move, but their screen content changes.
- **What crowds the upper band near the dog:**
  - office-chair backs (seat backs reach ~1.1 m, well above the horizon at 0.4 m), people (standing people fill
    the whole frame height), and the sides of the cabinets and desks the dog walks along;
  - jackets on chairs, backpacks on desks, cardboard boxes stacked on cabinets (the "CyberPower" boxes).
  - In about half the sampled frames the nearest metre is a chair or a cabinet side that covers most of the
    upper half.
- **Takeaway:** "above the clutter" for this camera is not "the ceiling". At tilt 0 it is the band between
  about desk height and the top edge, at 2-8 m range: walls, doors, tall furniture, far desk rows, and
  occasionally the ceiling. Chairs and people still intrude.

**Crops chosen for task 2** (rows of the 640x360 level frame; the horizon is at ~190):
- `full`: rows 0-360.
- `upper`: rows 0-162 (top 45 %; above about +3.5 deg; everything above the camera, up to ~0.7 m at 4 m range).
- `top`: rows 0-108 (top 30 %; above about +11 deg, i.e. above desk height out to ~2 m and above ~1.4 m at
  5 m). This is the "above the clutter" band.
- `lower`: rows 198-360 (bottom 45 %; below the horizon: floor, chair bases, boxes, desk fronts).

## 2. Ground truth is the weak link: what the pictures say about the console poses

Before trusting any recall number I checked the console poses against the pictures themselves:
SIFT + essential matrix between pictures of the same place.

**(a) The calibrated focal length under-reads rotations by ~12 %**
- Rotations over 1-4 s between consecutive trail frames, from the images with the 720p K, are 0.878x the odom
  yaw change (250 pairs).
- Is odom yaw itself right? Checked independently (`yaw_scale_check.py`): 31 pairs of frames at the same spot,
  one full turn apart. Odom gives 360 + residual within **+1.8 %** (IQR 0.5-2.6 %), and part of that is drift.
- So the camera model is off. With fx, fy x 0.90 the image rotations match odom (slope 1.003, median
  |diff| 1.9 deg; `scratch_fx_sweep.py`, `results/fx_sweep.json`). The effective HFOV of the stored frames is
  about **79 deg, not 73**.
- `vcommon.FX_SCALE = 0.90` is used for all geometry from here on. Problem P3.

**(b) Console yaw errors** (`pose_consistency.py`, `yaw_audit.py`)
- Data: 852 verified pairs (>= 60 inliers, within 1.5 m) among 342 trusted pictures.
- Rotation averaging (IRLS) fits all pairwise image rotations with residual median 0.5 deg, p90 1.8 deg. So the
  image rotations are cycle-consistent.
- The console yaw error per picture that comes out of it:

| day | median | p90 |
|---|---|---|
| 10-19 | 11.6 | 24.1 |
| 10-20 | 8.3 | 22.0 |
| 10-22 | 8.4 | 22.8 |

- Gross cases:
  - 10-20 12:2x-12:3x: the console yaw is off by **90-128 deg**. The event-log jump detector did not catch it.
  - 10-22 15:4x: -23 deg.
- 10-22 sessions disagree with each other by 15-30 deg (153454 vs 160051: 23 deg; 160051 vs 161641: -30 deg).
  This matches the lidar study's yaw-drift finding.

**(c) Console position errors** (`pos_audit.py`)
- On the clean day, strongly matched pairs (>= 100 inliers) are within 1 m of each other 99 % of the time.
- Applying that rule:
  - 10-19 (after 16:54) poses are **shifted by about 0.75 m** (dx -0.57, dy +0.50) relative to 10-20 and 10-22
    for the same views (44 pairs, consistent direction).
  - 10-20 and 10-22 agree (mean offset 2-5 cm).
  - 10-22 16:3x pictures are 1.5-3 m off: identical pictures, with the console saying 2-3 m apart
    (`figs/fail_within_10-22_dino_vlad_full.jpg`, rows 1-3).
- Within 10-22, retrieval R@1 against the **same session** is 0.71, against **other sessions** 0.18. The 10-22
  sessions are not in one consistent frame. Problem P4.

**Ground-truth sets used below:**
- `trusted` (section 0);
- `clean` = trusted minus yaw-suspect (|e| > 20 deg) and position-suspect (|offset| > 1 m) pictures:
  81 / 168 / 267 pictures;
- `audited` = clean, with yaw corrected by the session-local (+-90 s) median audit error.

**Cross-day tests:** the main ones are **10-22 queries vs 10-20 db** and the reverse, because those two days share
a map frame. The leave-one-day-out splits that include 10-19 are reported too, but 10-19's offset makes them
pessimistic.

## 2b. Place recognition (task 2)

**Setup**
- Descriptors (`desc.py`): DINOv2 ViT-L/14-reg4 with CLS, GeM over patch tokens, and AnyLoc-style hard VLAD
  (K=32, vocabulary from 10-19/10-20 tokens); and SigLIP SO400M-384 (square windows averaged).
- The image is cropped before the network (no attention leak from the cropped-away part).
- Positive = a db frame within 1 m and 30 deg.
- Within-day excludes db frames within 60 s of the query.
- Chance R@1 is 2-7 %.
- Full tables: `results/vpr_eval*.json`. Paired bootstrap: `results/vpr_compare.json`.

**DINOv2-VLAD R@1 / R@5, clean GT:**

| split | n with positive | full | upper (top 45 %) | top (top 30 %) | lower (bottom 45 %) |
|---|---|---|---|---|---|
| within 10-20 | 145 | **0.88**/0.92 | 0.84/0.89 | 0.70/0.84 | 0.80/0.94 |
| cross-day 10-22 vs 10-20 + reverse | 321 | **0.54**/0.68 | 0.48/0.68 | 0.35/0.55 | 0.44/0.64 |
| leave-one-out, q=10-22 (db 10-19+10-20) | 184 | **0.48**/0.61 | 0.43/0.58 | 0.29/0.49 | 0.34/0.52 |
| within 10-22 (GT-limited, see P4) | 204 | 0.35/0.58 | 0.32/0.54 | 0.28/0.47 | 0.24/0.45 |

**Paired differences in R@1, cross-day pooled (95 % bootstrap CI):**

| comparison | difference |
|---|---|
| upper - lower | +0.04 [-0.01, +0.09] |
| full - upper | +0.06 [+0.02, +0.10] |
| upper - top | +0.13 [+0.08, +0.18] |
| full+upper fused - full | +0.01 [-0.02, +0.03] |

On leave-one-out q=10-22, upper - lower is +0.09 [+0.03, +0.15].

**Share of queries that have any positive:**
- 10-22 q vs 10-20 db: 62 %;
- 10-20 q vs 10-22 db: 92 %;
- 10-22 q vs 10-19+10-20 db: 70 %.

**What this says:**
- The upper half does beat the lower half across days, as expected: +4 to +9 points, and significant on the
  leave-one-out split.
- But the full frame beats the upper half everywhere, by 3-6 points.
- The narrow "above-the-clutter" band (top 30 %) is clearly worst: -13 points against upper.
- Relative drop from within-day to cross-day: full -39 %, upper -43 %, lower -45 %, top -50 %. So no crop
  "holds up better" in relative terms. Level frames from 0.4 m simply have too little above the clutter. The
  top 30 % is often blank wall, ceiling glare or the top of a chair back.
- Fusing full + upper adds nothing.
- SigLIP is poor at place recognition (R@1 0.08-0.17 cross-day, 0.44 within): it encodes "office with chairs",
  not "this office corner".
- AnyLoc-VLAD > GeM ~ CLS for DINOv2, by about 5 points.

**Failure cases** (`figs/fail_*.jpg`: query | top-1 | the true neighbour by console pose):
- (1) Occluded queries. A chair seat or a cabinet face fills the frame (about a third of the failures look like
  this). Their "true" neighbours are often blurred or occluded too.
- (2) Same scene but console poses 2-3 m apart: 28-49 % of failures pass geometric verification with >= 40
  inliers. Most of these are pose errors (P4) or views of a distant wall from 1.5-3 m further along the line of
  sight.
- (3) Genuinely confusable repeated desk rows with identical chairs and drawers.

**After cutting 10-22 from 16:24:38 on** (the three hand placements; P4). This is the final `clean` set:
81 / 168 / 204 pictures. The tables above were computed before the cut and are kept in
`results/v1_before_1624_cut/`. With the cut, DINOv2-VLAD R@1 / R@5:

| split | full | upper | top | lower |
|---|---|---|---|---|
| within 10-20 (n=145) | **0.88**/0.92 | 0.84/0.89 | 0.70/0.84 | 0.80/0.94 |
| cross-day pooled, 10-22 vs 10-20 + reverse (n=278) | **0.66**/0.81 | 0.63/0.79 | 0.45/0.65 | 0.58/0.75 |
| leave-one-out q=10-22 (n=139) | **0.61**/0.76 | 0.56/0.71 | 0.37/0.61 | 0.45/0.66 |
| within 10-22 (n=146) | **0.48**/0.70 | 0.40/0.66 | 0.38/0.57 | 0.32/0.54 |

- At 2 m / 45 deg, cross-day R@1 is full 0.66-0.80 and upper 0.57-0.78.
- **Paired differences in R@1** (95 % bootstrap CI):

| comparison | cross-day pooled | leave-one-out q=10-22 |
|---|---|---|
| upper - lower | +0.05 [-0.00, +0.10] | +0.12 [+0.03, +0.19] |
| full - upper | +0.04 [-0.01, +0.08] | |
| upper - top | +0.18 [+0.12, +0.23] | |

- **Drop from within-day (10-20) to cross-day:** full -25 %, upper -25 %, lower -28 %, top -36 %.
- **Conclusion for retrieval:**
  - The upper half is as robust across days as the full frame and somewhat better than the lower half.
  - The full frame is still a little better in absolute terms.
  - The narrow top band is clearly worse: at a 0.4 m level camera it holds too little.
- **The cut fixed most cross-day failures:** only 9-15 % of the remaining cross-day failures pass geometric
  verification (before the cut: 28-49 %).
- **Many remaining "failures" are borderline:** 1.0-1.3 m or 26-31 deg (`figs/xday_both_wrong.jpg`).
- **Coverage limits cross-day recall:** 10-20 and 10-22 covered different parts of the lab
  (`figs/map_pictures.png`). Only 63 % of 10-22 queries have any 10-20 picture within 1 m / 30 deg.
- Example montages: `figs/xday_{both_right,only_upper_right,only_full_right,both_wrong}.jpg`. In the
  'only upper right' cases, chairs moved in front of the camera between days.

## 3. Pose refinement (task 3)

**Method** (`refine.py`; SIFT is `geo.py`, SuperPoint+LightGlue is `geo_lg.py`):
- Retrieve the top-10 by full-frame DINOv2-VLAD.
- Match local features restricted to a region (full / upper rows < 162 / lower rows >= 198).
- Essential matrix with the effective K, then relative yaw and the bearing to the query's camera centre.
- Pose:
  - yaw = db yaw + relative yaw;
  - position = inlier-weighted mean of up to 3 verified db pictures within 1.5 m of the best one;
  - or bearing triangulation when the rays cross at >= 20 deg (used for 35-50 % of queries).

**How accurate the camera part is:**
- Relative yaw between two pictures: 1.9 deg median against odom over 1-4 s (P3 fix applied).
- Cycle consistency across 852 pairs: 0.5 deg median residual.
- So the yaw error of a relocalized pose is essentially the yaw error of the db picture's console pose.

**Results on correctly matched queries** (top-1 db pose and the corrected pose, both measured against the
query's console pose):

| split | matcher | yaw: db pose -> corrected (median) | position (median) | p90 |
|---|---|---|---|---|
| within 10-20 | SIFT | 10.6 -> 3.8 deg | 0.26 m | ~0.7 m |
| cross-day 10-20 vs 10-22 | SIFT | 10.2 -> 5.6 deg | 0.28 m | 0.6-0.8 m |
| cross-day 10-22 vs 10-20 | SIFT | 11.5 -> 7.0 deg | 0.31 m | |
| cross-day | LightGlue | 6.4-8.2 deg | 0.36-0.37 m | |

- The position error is about the size of the console's own noise. Triangulation does not beat the weighted
  mean (0.24 vs 0.26 m): db poses are too noisy for triangulation to help.

**Precision vs coverage** (`refine_curves.py`, `figs/refine_curves.png`). Accept when the best match has
>= T inliers. Precision = position within 1 m and yaw within 15 deg of the console. Coverage = share of
queries that have a true neighbour.

| matcher, region | 10-20 q vs 10-22 db | 10-22 q vs 10-20 db |
|---|---|---|
| SIFT, full, T=40 | 57 % at 0.95 | 36 % at 0.85 |
| SIFT, upper, T=40 | 38 % at 0.98 | 21 % at 1.00 |
| SIFT, lower, T=40 | 15 % at 0.95 | 9 % at 0.83 |
| LightGlue, full, T=150 | 63 % at 0.93 | 44 % at 0.84 |
| LightGlue, full, T=200 | 51 % at 0.97 | 32 % at 0.88 |
| LightGlue, upper, T=75 | 62 % at 0.97 | 41 % at 0.87 |
| LightGlue, upper, T=100 | 45 % at 0.99 | 30 % at 0.87 |
| LightGlue, lower, T=75 | 51 % at 0.91 | 34 % at 0.79 |

- **Within 10-20** precision saturates at 0.80-0.90. The misses are console yaw errors (10-20 12:2x-12:3x),
  not matching errors.
- **Upper-region matching reaches high precision with fewer inliers:** at the same coverage it is equal or
  better than full-frame matching (0.97 vs 0.93 at ~62 % coverage on 10-20 vs 10-22).
- **The lower region is worst across days** (furniture and chairs moved), which supports Oliver's premise at
  the local-feature level.
- **LightGlue verifies far more than SIFT** (93-97 % of queries reach 25 inliers vs 43-71 %). It needs higher
  thresholds, and at matched precision it gives +5-15 points of coverage.

**Spin sets** (`spin_sim.py`): consecutive query pictures of one turn in place (same session, < 40 s,
< 0.4 m moved; 21-30 sets of ~4 pictures).
- Taking the picture with the most inliers raises coverage from single-picture 0.43 to 0.81 at precision 0.94
  (SIFT T=40, 10-20 vs 10-22).
- Voting (>= 2 agreeing pictures) gives 0.71 at 1.00.
- 10-22 vs 10-20: best-of-N gives 0.47 at 0.71 (many 10-22 spins are in places 10-20 never covered).

- **Prototype** (`reloc.py --selftest`; 29 spin sets of 10-22 against a 168-picture 10-20 database):
  - 0.83 s per picture on the GPU (DINOv2-L, 10 LightGlue matches, essential matrix);
  - high confidence: 16 sets, 12 within 1 m, median 0.48 m;
  - medium: 7 sets, 5 within 1 m;
  - low: 6 sets, 0 within 1 m, and none of the 6 has a database picture within 1 m.
- **Remaining high-inlier mistakes** (`figs/lg_highinlier_wrong_x22v20.jpg`, `figs/lg_false_match_ceiling.jpg`):
  - real matches of the same object seen from 1-1.5 m and up to 88 deg away. The position copied from the db
    picture is then off by that much.
  - Fixes: a denser database, or metric scale from the lidar.

## 4. VLM probe (task 4)

**Permanence boxes** (`vlm_probe.py`, `vlm_viz.py`, `figs/vlm_boxes_27b_{a,b}.jpg`)
- The 27B with a JSON schema returns ~13 items per picture as fixed / rarely_moved / movable / person, with
  boxes on a 0-1000 scale.
- The boxes are coarse but in the right places: chairs, boxes, people and tripods are found reliably.
- **Latency:** median 22 s per picture (p90 35 s) at concurrency 2 on the shared GPU.
- **The 8B** on the same 20 pictures: 16.6 s, ~25 items per picture (labels many more things movable).
  Movable-mask IoU with the 27B is 0.68.

**The run was cut short**
- At 01:50 both of our vLLM servers went away (HTTP 500, then connection refused), and another user's vLLM
  (gaofeng, Qwen3.6-35B, port 8036) took the GPU.
- 214 of 372 requests failed. They were moved to `cache/vlm_27b_errors_v1/`; the first masking numbers that
  included them are in `results/v1_vlm_with_errors/` (invalid). I did not restart the shared servers.
- 158 labelled pictures remain: 146 of 10-20, 12 of 10-22. That is too few on 10-22 for a cross-day test.

**Masking test, done within 10-20 instead** (`vlm_mask_eval2.py`)
- Queries against pictures from *other sessions* of the same day (11:xx vs 19:xx, ~7 h apart; chairs, bags and
  people moved).
- Two masks:
  - **movable**: movable and person boxes greyed out and their tokens dropped; removes 36 % of pixels;
  - **fixed-only**: rarely_moved removed as well; removes 66 % of pixels.
- DINOv2-VLAD R@1:

| crop | db | unmasked | movable masked | fixed only |
|---|---|---|---|---|
| full | other session | 0.77 | 0.76 (-0.01 [-0.06, +0.04]) | 0.55 (-0.21) |
| full | any picture > 60 s away | 0.89 | 0.82 (-0.07 [-0.12, -0.02]) | 0.56 (-0.33) |
| upper | other session | 0.75 | 0.71 (-0.04 [-0.08, +0.01]) | 0.55 (-0.20) |

- **Masking does not help**, and keeping only fixed things hurts a lot. The "movable" things (chairs, boxes,
  monitors, tripods) carry most of the place identity over hours to days, and box masks cut away far more than
  the object.
- The VLM labels the *upper* band as slightly more movable than the lower one (pixels kept 63.5 % vs 67.4 %):
  chair backs and stacked boxes.
- Untested: pixel-accurate masks of **people only**. That is the case most likely to help.

**Text fingerprint as a coarse prior** (`text_fp.py`; TF-IDF over '<colour> <name>' phrases)

| fingerprint | cross-day R@1 | cross-day R@10 | within 10-20 R@1 | within 10-20 R@10 |
|---|---|---|---|---|
| all objects from the stored descriptions | 0.20-0.30 | 0.56-0.70 | 0.41 | 0.86 |
| "static" vocabulary only (doors, cabinets, desks, lights, wall/ceiling objects) | 0.10-0.16 | | 0.23 | |
| 27B fixed + rarely_moved names | | | 0.39 | 0.77 |

- At 2 m / 45 deg, within 10-20 with all objects: R@1 0.56, R@10 0.95.
- DINOv2 gets R@1 0.88 within and 0.57-0.74 across days. So text is at best a coarse prior for a lost robot
  (top-10 places), not a localizer, and the permanence filter does not make it better.
- The text costs nothing: the descriptions already exist for every picture.
