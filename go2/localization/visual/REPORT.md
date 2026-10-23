# Relocalizing the Go2 from its camera, using what is above the clutter (offline, 2026-10-23)

This was offline only, with no console calls at all. Everything ran on the 1109 stored pictures (`lab_agent/memory.py`
`load()`) and the event logs. Scripts, figures and results are in `go2/localization/visual/`; every number is in
`NOTES.md`, and problems P1-P6 are in `problems_found.md`.

**Lead's check of P1:** the two tilted pictures are `p1792710742_11` (look +16°) and `p1792711082_3` (look −5°). Each was
compared with the level picture taken 4-6 s earlier. The best vertical alignment between each pair is a shift of 0 rows,
where a real 16° tilt would move the view by about 60 of 180 rows. The pictures are not pixel-identical (mean
difference 7.9 and 20 out of 255) but the camera did not tilt.

## Short version

1. **There are no tilted pictures (P1).** All 1109 are level, because `look` springs back before `photo` fires.
   - At 0.4 m, a level camera sees the ceiling only beyond about 5 m, as a thin top strip in about a quarter of frames.
   - So what could be tested is "localize on the upper part of a level frame", not on the ceiling.
2. **Ground truth was the hard part (P4).** Verified picture pairs show the console poses are much worse than ±0.2 m.
   - Yaw errors have a median of 8-12° and a 90th percentile of about 22°. They reach 90-128° on 10-20 around
     12:20-12:36.
   - 10-19 is shifted about 0.75 m relative to 10-20 and 10-22.
   - 10-22 is 1.5-3 m off after the 16:24 hand placements.
   - 10-22's sessions disagree with each other by 15-30°.
   - The poses were audited (`yaw_audit.py`, `pos_audit.py`) and the bad stretches left out. The clue was that
     within-day recall on 10-22 came out lower than cross-day recall.
3. **The calibration's focal length is about 10% too long for the stored frames (P3).** Image rotations come out at
   0.88× the odom turn, while odom itself is within 2% over full turns. The effective field of view is about 79°, not
   73°. Corrected here with fx × 0.90. Not yet changed in `memory.py` / `anchors.py` (`HFOV = 73`).
4. **Place recognition** (DINOv2 ViT-L with AnyLoc-style VLAD), within 1 m and 30°:
   - Recall@1 is 0.88 within a day and 0.66 across days (10-20 ↔ 10-22); at 2 m and 45° it is 0.66-0.80.
   - Across days the upper half beats the lower half by 5-12 points, but the full frame is still 3-5 points better.
   - The narrow top 30% band is clearly worse, 18 points below the upper half.
   - SigLIP is useless for this (0.12-0.17).
5. **Pose refinement** (SuperPoint + LightGlue and an essential matrix):
   - Relative yaw is good to about 2°.
   - Across days, accepting matches with 150 or more inliers gives a pose for 63% of queries (10-20 queries against
     10-22 pictures) at 93% precision. Position error has a median of about 0.3 m (90th percentile about 0.8 m), about
     the console's own noise.
   - Matching only the upper region gives 97% precision at 62% coverage. The lower region loses most of its matches
     across days, which supports the premise at the level of local features.
6. **A spin helps.** Taking the best of about 4 pictures from one turn in place lifts coverage from 0.48 to 0.86 at
   precision 1.00 (LightGlue, 150 or more inliers).
7. **VLM:** the 27B draws usable boxes around fixed and movable things, at about 22 s per picture. Masking movable
   things does not help retrieval, and keeping only fixed things hurts badly. A text list of fixed landmarks is only a
   coarse prior (cross-day recall@10 of 0.56-0.70).

## 1. What the camera sees above the clutter

Figures: `figs/task1_survey_[0-4].jpg`, `figs/task1_tilt_pair_0_vs_16.jpg`.

- **Horizon at look 0:** row about 187 of 360 by the model, about 195 measured from vanishing points (about 1° nose
  down).
- **Top and bottom edges of the view:** +25° / −23° with the calibration; +28° / −26° with the corrected focal length.
- **Ceiling:** visible only beyond about 5 m. It showed in about 7 of 30 sampled frames, as lights, tiles, a vent or a
  camera.
- **Upper band:** walls, doors and frames, the whiteboard wall, fire extinguishers, the wall TV, monitors, tall
  cabinets, shelving, the water dispenser and the far desk rows.
- **Things that intrude:** chair backs (up to about 1.1 m), standing people, and cabinet sides the dog walks past.
- **Crops used:** upper = rows 0-162, top = rows 0-108, lower = rows 198-360.

## 2. Place recognition

A match counts if it is within 1 m and 30° of the console pose. The clean set is the trusted pictures, minus those
flagged by the audit, minus 10-22 after 16:24:38. That leaves 81 / 168 / 204 pictures for 10-19 / 10-20 / 10-22. Cross-day
means 10-22 against 10-20 in both directions; 10-19 has its own map offset. Chance recall@1 is 2-7%.

| split (recall@1 / recall@5) | full | upper 45% | top 30% | lower 45% |
|---|---|---|---|---|
| within 10-20 (n = 145) | **0.88** / 0.92 | 0.84 / 0.89 | 0.70 / 0.84 | 0.80 / 0.94 |
| cross-day pooled (n = 278) | **0.66** / 0.81 | 0.63 / 0.79 | 0.45 / 0.65 | 0.58 / 0.75 |
| 10-22 queries against 10-19 + 10-20 (n = 139) | **0.61** / 0.76 | 0.56 / 0.71 | 0.37 / 0.61 | 0.45 / 0.66 |

Paired differences in recall@1 (95% bootstrap intervals):

| comparison | cross-day pooled | 10-22 against 10-19 + 10-20 |
|---|---|---|
| upper − lower | +0.05 [−0.00, +0.10] | +0.12 [+0.03, +0.19] |
| full − upper | +0.04 [−0.01, +0.08] | |
| upper − top | +0.18 [+0.12, +0.23] | |

- **Drop from within-day to cross-day:** full −25%, upper −25%, lower −28%, top −36%.
- **Other descriptors** (full frame, recall@1: within a day / 10-22 vs 10-20 / 10-20 vs 10-22): CLS 0.82 / 0.51 / 0.65,
  GeM 0.77 / 0.51 / 0.72, SigLIP 0.44 / 0.12 / 0.17.
- **Failure types** (`figs/fail_*.jpg`, `figs/xday_*.jpg`): a chair seat or cabinet face filling the frame; borderline
  cases at 1.0-1.3 m or 26-31°; repeated desk rows.
- **Coverage:** 10-20 and 10-22 covered different parts of the lab (`figs/map_pictures.png`). Only 63% of 10-22 queries
  have any 10-20 picture within 1 m and 30°.

## 3. Pose refinement

**Method** (`refine.py`, `geo.py`, `geo_lg.py`):
- retrieve the top 10, then match keypoints inside the chosen region;
- fit an essential matrix with the corrected camera matrix;
- yaw = stored picture's yaw + relative yaw;
- position = inlier-weighted mean of the verified stored pictures.

**How good the camera part is:** relative yaw against odom over 1-4 s has a median error of 1.9°. The cycle residual over
852 pairs is 0.5°.

| against console poses, correct matches only | yaw: stored pose → corrected | position median |
|---|---|---|
| within 10-20 | 10.6° → 3.8° | 0.26 m |
| cross-day | 10-12° → 5.6-8° | 0.28-0.37 m (90th percentile 0.6-0.9 m) |

- The remaining yaw error is console noise on the two pictures.
- Triangulation does not beat the weighted mean.
- The position is where the stored picture was taken. A correct match of the same cabinet corner seen from 1.5 m and
  88° away therefore comes out 1.5 m off (`figs/lg_false_match_ceiling.jpg`). A denser set of stored pictures, or
  lidar scale, fixes this.

Precision against coverage across days (`figs/refine_curves.png`; precision means within 1 m and 15° of the console):

| accept rule | 10-20 queries vs 10-22 | 10-22 queries vs 10-20 |
|---|---|---|
| SIFT full, 40+ inliers | 57% at 0.95 | 36% at 0.85 |
| SIFT upper, 40+ | 38% at 0.98 | 21% at 1.00 |
| SIFT lower, 40+ | 15% at 0.95 | 9% at 0.83 |
| LightGlue full, 150+ | 63% at 0.93 | 44% at 0.84 |
| LightGlue full, 200+ | 51% at 0.97 | 32% at 0.88 |
| LightGlue upper, 75+ | 62% at 0.97 | 41% at 0.87 |
| LightGlue lower, 75+ | 51% at 0.91 | 34% at 0.79 |

**Spin**, best of about 4 pictures (10-20 queries vs 10-22):

| matcher | single picture | best of the spin |
|---|---|---|
| SIFT, 40+ inliers | 0.43 at 1.00 | 0.81 at 0.94 |
| LightGlue, 150+ inliers | 0.48 at 1.00 | 0.86 at 1.00 |

Spins on 10-22 against 10-20 pictures reach only 0.60 at 0.72, because many are in areas 10-20 never covered.

**Prototype** `reloc.py --selftest` (29 spin sets from 10-22 against 10-20 pictures), at 0.83 s per picture:

| confidence | spin sets | within 1 m |
|---|---|---|
| high | 16 | 12 (median 0.48 m) |
| medium | 7 | 5 |
| low | 6 | 0; none had a stored picture within 1 m |

So the confidence label works as a gate.

## 4. VLM probe

- **Boxes around fixed and movable things:** the 27B returns about 13 items per picture (fixed / rarely moved /
  movable / person, boxes on a 0-1000 scale) in a median 22 s (90th percentile 35 s); `figs/vlm_boxes_27b_{a,b}.jpg`.
  The 8B on the same 20 pictures takes 16.6 s and labels more things movable; its movable-area overlap with the 27B is
  0.68.
- **The run was cut short:** both shared vision servers received SIGTERM at 01:50 (P5), and 214 of 372 requests failed.
  146 labelled pictures from 10-20 remain, so masking was tested within 10-20 against pictures from other sessions
  about 7 h apart.

**Masking test** (DINOv2-VLAD recall@1):

| crop | compared against | unmasked | movable masked (36% of pixels) | fixed only (66% of pixels) |
|---|---|---|---|---|
| full | other session | 0.77 | 0.76 (−0.01 [−0.06, +0.04]) | 0.55 (−0.21) |
| full | any picture over 60 s away | 0.89 | 0.82 (−0.07) | 0.56 (−0.33) |
| upper | other session | 0.75 | 0.71 (−0.04) | 0.55 (−0.20) |

"Movable" things carry much of what identifies a place over hours to days, and box masks remove too much. Masks of
people only, at pixel level, are untested.

**Text fingerprint** (TF-IDF over the stored descriptions):

| fingerprint | cross-day recall@1 | cross-day recall@10 | within 10-20 (recall@1 / @10) |
|---|---|---|---|
| all objects | 0.20-0.30 | 0.56-0.70 | 0.41 / 0.86 |
| "static" words only | 0.10-0.16 | | 0.23 / – |
| 27B fixed and rarely-moved names | | | 0.39 / 0.77 |

## 5. Proposal

### (a) What to record with the dog (about 1.5 h)

1. **Tilt.** Capture with `look 16`, then `/frame.jpg` within 0.3 s. The horizon should move from row about 190 to about
   300 of 360. If it doesn't, ask the console owner for a `photo {look_deg}` that holds the pitch. Store the actual IMU
   pitch with each picture, not the requested look.
2. **Checkerboard calibration:** about 30 `/frame.jpg` grabs at 1280×720, to confirm or replace fx × 0.90.
3. **Floor marks for ground truth:** 8-10 tape crosses at measured map positions, with heading lines, in both the 10-20
   area (south-east) and the 10-22 area (north).
4. **Survey walk with no hand placement:** stands about 1 m apart, 8 headings each, level and at maximum tilt, dog
   still, events logged. Check poses at the marks and with the camera audit.
5. **360° turns at 3 marks,** a frame every 10° or so.
6. **The next day, after the lab has changed:** repeat steps 4 and 5 at about 10 marks.

### (b) Relocalize from camera

1. **Trigger:** lost, a jump (over 0.3 m or 10°), a planner failure near furniture, or on request.
2. **Spin:** 8 steps of 45°. Wait until still at each, grab a level frame (plus maximum tilt once it works), and record
   the odom yaw. About 25 s.
3. **Each frame:** DINOv2-VLAD top 10, then LightGlue (upper region first; the full frame if under 75 inliers), then the
   essential matrix, giving a yaw and position.
4. **Combine:** take the frame with the most inliers. Other frames support it if their estimate is within 0.75 m and
   their yaw agrees within 15° once the odom turn is removed.
5. **Confidence:**
   - **high:** 200+ inliers, or 150+ with a supporting frame;
   - **medium:** 100+;
   - **low:** anything less.

   Report the best match more than 2 m away as the margin.
6. **Hand off to the lidar:**
   - **high:** seed the lidar matcher at the proposed pose with a ±0.5 m / ±10° window;
   - **medium:** give it the 2-3 best hypotheses to score;
   - **low:** run a global lidar search or ask a person.

   Never publish a camera pose the lidar has not confirmed.
7. **Cost:** about 7 s of compute for 8 frames, about 35 s in all. Prototype: `reloc.py`.
8. **Side use:** the same matcher audits stored poses, and found errors the jump detector missed.

### (c) Expected accuracy

- **Measured** (cross-day, against stored pictures posed by the console):
  - recall@1 is 0.66 where stored pictures cover the place;
  - high-confidence poses are within 1 m in 75-95% of cases;
  - position median is 0.3-0.5 m;
  - yaw is about 2° relative to the stored picture, but about 8-10° absolute because of console noise.
- **With a survey set of stored pictures** (an extrapolation, not measured): yaw 2-3°, position about 0.3 m (limited by
  stand spacing until lidar scale is used), coverage above 80% of the open floor.
- **What the camera will not do:** sub-decimetre position on its own. Use it for "which place, and which way am I
  facing", and let the lidar do the last 0.3 m.
- **Untested:** tilted ceiling views. Repeated light panels are a likely look-alike hazard.
