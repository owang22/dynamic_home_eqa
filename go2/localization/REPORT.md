# Go2 localization: what a Roomba-style approach would give us (offline, 2026-10-23, no dog)

Data: 21 event logs from 10-14 to 10-22, 370 min with a map pose. Each has 10 Hz odometry and the console's map pose,
plus a snapshot of the dog's voxel map every 1-2 s (`cloud.obs`): the obstacle cells (0.1 m) of a 6.4 m square around
the dog, in the odom frame, with column-top heights. Also used: the saved map, `places.json` and the trail pictures.
Only `GET /state.json` and `GET /map.png` were read from the console (copies in `console_snapshot/`). Item numbers
refer to `problems_found.md`.

The reference for accuracy is an offline pose graph built from the logs, not a surveyed one. It is checked only on
revisits it never saw. Its absolute heading is uncertain by several degrees (item 9).

**Lead's check:** the lead session measured odom yaw drift independently with a separate script. In windows of 1-17
min where the dog didn't move (xy within 3 cm, no single step over 0.5°), yaw drifted +0.3 to +4.7°/min, always
counter-clockwise: 3.7-4.7°/min on 10-22, 0.3-0.9°/min on the 10-20 evening logs.

## 1. Short version

1. **Heading is the root problem.**
   - Odom yaw drifts +0.6 to +4.8°/min while the dog stands still, always counter-clockwise, at a different rate each
     day.
   - It is estimate drift, not real turning: cells added to the dog's voxel map while still line up with older cells
     only after rotating them back by the odom yaw change.
   - The console follows this drift. Its map-to-odom yaw changes by 60-90° per session (`figs/fig1_yaw_drift.png`).
   - So Roomba lesson 4 ("trust odometry") holds for position, not for heading over minutes.
2. **The console rarely jumps. Mostly it is slightly wrong.**
   - 2 real jumps in 370 min: 1.32 m / 25° while turning at 10-22 16:11:10, and 10.6° at 10-20 16:13:42.
   - 4 probable hand placements: 15:51:08 and the 16:24 cluster on 10-22 (0.45, 1.84 and 0.96 m).
   - 265 twitches, about 1 per still minute, median 0.12 m. These are treated as the console's drift correction (board
     #12). Their rate rises with yaw drift (Pearson r = 0.67, n = 9; Spearman 0.57, not significant).
   - On 2,186 revisit pairs, the console gives the same pose within 0.3 m / 5° only 49% of the time: 61% within a
     session, 42% across sessions, 18-21% on 10-22.
3. **Localizing on structure above the clutter is impossible with this lidar stream.**
   - Column heights stop near 1.4 m (highest logged 1.45 m), and a snapshot has 0-40 cells above 1.2 m out of about
     2,000.
   - A map of cells 0.9 m and higher was the worst reference: 18% tracking agreement, 8% global success.
   - The ceiling has to come from the camera.
4. **A map learned across days is the main gain.**
   - A multi-session pose graph links 1,305 keyframes with the 2,186 revisit matches plus odometry.
   - On held-out revisits it agrees within 0.3 m / 5° 84% of the time, against 45% for the console. Medians are 0.05 m
     / 0.8° against 0.18 m / 4.6°.
   - "What stays put", computed from its poses, is crisp: desks and drawer cabinets are static; chairs, boxes and
     people move. The trail pictures confirm it.
   - A consensus map built from it, leaving out the test day, is the best reference: tracking 57% vs 33% for the
     console, revisits 62% vs 49%, global relocalization 53% vs 21% on the saved map.
5. **Finding the pose from scratch works about half the time.**
   - One snapshot against the consensus map: 53% correct, and the right pose is among the top 8 candidates 80% of the
     time.
   - Accepting only clear wins (runner-up at most 0.95 of the best score) accepts 37% at 86% precision. The median
     runner-up/best ratio is 0.96, the same kind of ambiguity as the console's 21% vs 18%.
   - Pooling 60 s of snapshots did not help, and neither did two-view agreement: wrong answers repeat, so agreement
     gave 30% accepted at 70% precision.
6. **Squaring up on walls gives heading only roughly.**
   - Dominant wall direction: 25° on the saved map (weak contrast, 1.16) but 39.5° on the pose-graph map (contrast
     1.46). The 14.5° gap is unexplained.
   - From one snapshot, wall direction gives heading (modulo 90°) within 5° 46% of the time, median error 5.6°. That is
     enough to catch 20° of drift, not to set heading precisely.
7. **The saved map is probably bent** (item 9, not proven). On its own it is a weak reference: best single-snapshot
   score about 0.70 against 0.68 for the runner-up.

## 2. Diagnostic of the current localizer (`jumps.py`)

**Method:**
- Each map pose is compared with the previous map pose plus the odom step.
- Odom is taken at `t − age.map_pose`, interpolated from samples timed at `t − age.odom`. The map pose updates at 5 Hz
  but is logged at 10 Hz; the remaining lag is ±0.05 s.
- Steps over 2 cm / 1° are merged into events (within 0.5 s, at most 2 s long) and classed:
  - **twitch:** dog still, 3-30 cm
  - **jump:** 0.3 m or 10° or more
  - **hand?:** 0.5 m or 10° or more while odom is frozen for 3 s or more and no agent call is running
  - **slide:** a slow correction, more than 0.3 m or 10° net within 10 s

Outputs: `results/jumps_sessions.csv`, `jumps_events.csv`, `odom_yaw_drift.csv`.

| session | min | twitches per still min (median size) | jumps | hand? | slides | still yaw drift °/min |
|---|---|---|---|---|---|---|
| 10-22 16:16 | 22 | 2.86 (0.13 m) | 0 | 3 | 10/128 | 4.7 |
| 10-22 16:00 | 15 | 3.33 (0.12 m) | 1 | 0 | 2/87 | 3.8 |
| 10-22 15:34 | 20 | 2.10 (0.12 m) | 0 | 1 | 2/118 | 2.4 |
| 10-20 evening (3 logs) | 39 | 0.36-0.73 | 0 | 0 | 0/230 | 0.6-0.9 |
| 10-20 15:38 | 36 | 1.70 (0.09 m) | 1 | 0 | 3/179 | 1.9 |
| 10-20 11:19 | 77 | 0.93 (0.12 m) | 0 | 0 | 3/450 | 2.7 |
| 10-19 17:08 | 13 | 0.30 (0.10 m) | 0 | 0 | 1/75 | 3.4 |
| 10-19 16:40 | 25 | 0.32 (0.13 m) | 0 | 0 | 0/100 | 1.5 |
| 10-19 15:52 | 35 | 0 | 0 | 0 | 0/167 | 1.8 |
| 10-14 (old map) | 56 | 0.07 (0.09 m) | 0 | 0 | 0/281 | 3.8 |
| **all** | **370** | **1.04 (0.12 m)** | **2** | **4** | **21/1956** | |

- Only 0-12% of twitches are undone within 15 s, so the pose isn't flipping back and forth.
- While walking, the net correction within 10 s has a 95th percentile of 0.1-0.37 m and 1-8°.
- A first pass reported 16 "jumps"; 14 were a sampling artefact (item 6).

## 3. What stays put (`persistence.py`, `revisits.py`, `pgo.py`)

**What the cloud's z means:** the column-top height above `floor_z`, in 0.05 m steps. Desk tops read 0.75-0.85 m.
Below 0.25 m it is mostly floor noise, and heights stop at about 1.4 m.

**Console poses were not good enough:** a persistence map built from them smears into swirls
(`figs/persistence_console.png`). So an offline pose graph was built instead.

- **Keyframes:** 1,305 calm snapshots taken soon after the dog moved (at least 0.3 m or 20° in the previous 30 s), at
  least 3 s apart.
- **Revisit pairs:** two keyframes at least 60 s apart and within 1.5 m by console pose, matched cloud to cloud with a
  correlative search (±0.8 m, ±25°).
  - Kept if the score is at least 0.55, the margin at least 0.05, and the reverse match agrees within 0.1 m / 2°.
  - 2,186 of 10,332 attempts were kept. 158 triangles of matches close to a median 0.03 m / 0.1°.
- **Pose graph:**
  - Constraints: revisits (0.05 m / 1°), odometry between consecutive keyframes (0.5° + 4°/min), and a weak console
    prior (0.5 m / 10°).
  - Solved in two stages, with robust weighting on the revisit and console terms only.
  - Anchored to the console's average frame, so `places.json` stays valid.

Held-out revisit test (30% of pairs, n = 655):

| | median | 90th percentile | within 0.3 m and 5° |
|---|---|---|---|
| Pose graph | 0.05 m / 0.8° | 0.23 m / 8.8° | 84% |
| Console | 0.18 m / 4.6° | 0.59 m / 19° | 45% |

- The pose graph differs from the console by a median 0.27 m / 6.5° (90th percentile 0.86 m / 18.9°).
- It has 8 of 1,266 consecutive keyframe steps over 0.3 m / 5°; the largest is 0.38 m / 14°.

**Persistence from pose-graph poses** (`figs/persistence_pgo.png`, `results/persistence_*_pgo`). Days are the unit
across sessions; counts are 0.1 m cells.

| column reaches | static | semi-static | dynamic | one day only | free |
|---|---|---|---|---|---|
| 0.25 m or more | 2,998 (34% of ever-occupied) | 859 (10%) | 4,318 (49%) | 669 | 2,841 |
| 0.5 m or more | 2,195 (26%) | 1,118 (13%) | 4,570 (54%) | 593 | 3,209 |
| 0.9 m or more | 222 (4%) | 1,205 (22%) | 3,718 (68%) | 333 | 6,207 |
| 1.2 m or more | 51 (2%) | 414 (20%) | 1,468 (72%) | 115 | 9,637 |

- Higher cells are less stable, not more: monitors, chair backs, people, and flicker near the 1.4 m cap.
- "Dynamic" is overcounted because "in view" is approximated without ray tracing, poses still have noise, and the
  voxel map smears (item 1). Treat the classes as a ranking.
- Checked against pictures (`figs/fig5_trail_pictures_desk_oliver_kang.jpg`): desks and cabinets are identical on
  10-19, 10-20 and 10-22, while chairs, boxes, a tripod and people move. desk_oliver is 72 static / 8 dynamic cells;
  desk_khang is 0 static / 68 dynamic.

## 4. Offline localizer (`localizer.py`, `matcher.py`, `keyframe_reloc.py`)

**Matcher:** brute-force yaw search with `cv2.matchTemplate` over x/y against a likelihood field (sigma 0.1 m), then a
bounded hill-climb.

| reference map | built from | cells used from each snapshot |
|---|---|---|
| saved | `map.png` | 0.4 m or higher |
| high | cells 0.9 m or higher, in 40% or more of views | 0.9 m or higher |
| static | persistence classes | 0.25 m or higher |
| consensus | cells 0.5 m or higher, in 50% or more of views | 0.5 m or higher |

The high, static and consensus maps are built without the test day.

**Online replay:** predict with odometry, search only ±0.3 m / ±4° (this window is the jump gate), and accept a match
only if it beats both the prediction and the runner-up by 0.01. Start from the console pose. The reference is the pose
graph at keyframes; revisit consistency, which doesn't depend on any map, is reported too.

| tracker | within 0.3 m / 5° | median / 90th pct error | revisits consistent | twitches of 5 cm or more per still min |
|---|---|---|---|---|
| Consensus map | 57% | 0.12 m 4.0° / 1.32 m 27° | 62% | 0.28 |
| Saved map | 39% | 0.28 m 5.9° / 1.47 m 40° | 59% | 0.45 |
| Static map | 35% | 0.27 m 5.5° / 2.71 m 72° | 31% | 0.43 |
| Console | 33% | 0.27 m 6.3° / 0.86 m 19° | 49% | about 1 (3 cm or more) |
| High map | 18% | 0.92 m 14° / 4.4 m 48° | 35% | 0.28 |

Variants:
- **Starting from the reference pose:** no change, so the failures come from tracking, not from the start.
- **Applying only 30% of each correction:** about the same.
- **Relocalizing when lost** (gated global search): the static map improves (agreement 35% to 52%, revisits 31% to
  53%), the consensus map doesn't change, and the gate accepted only 2-9 of about 300 attempts.

Every tracker, the console included, does worst on 10-22. That day has the highest drift (3.8-4.7°/min) and the hand
placements, and it is left out of its own map.

**Global relocalization** (132 random keyframes; whole map, 360° in 2° steps; success means within 0.3 m / 10° of the
pose graph):

| map | success | right pose in top 8 | accepted at gate 0.95 | precision when accepted | 60 s pooled |
|---|---|---|---|---|---|
| Consensus | 53% | 80% | 37% | 86% | 56% |
| Static | 42% | 53% | 36% | 87% | 39% |
| Saved | 21% (24% against the console) | 39% | 26% | 59% | 27% |
| High | 8% | 13% | 31% | 22% | 9% |

- A stricter gate (0.90) gives 10-12% accepted at 87-100% precision.
- Matching against stored snapshots from other days instead of a map: 45% success, and gate 0.9 gives 17% accepted at
  100% precision.
- **Versus the console's own matcher:**
  - Its board #10 test (within 6 cm / 1°, 100% against 67%) shifted real clouds by a known small amount, which is a
    local check. Our local behaviour is similar.
  - Its live attempt at 16:39 (21% against 18%, ratio 0.86) would pass our 0.95 gate; our median ratio is 0.96.

**Wall heading:** using cells 0.5 m and up, median error 5.6° and 46% within 5° (59% on high-contrast snapshots).
Using cells 0.9 m and up, median error 10.1°.

## 5. Each Roomba lesson, tested

| lesson | verdict |
|---|---|
| 1. Start from a known pose | Needed but not enough: tracking drifts off afterwards anyway. |
| 2. Localize on what is above the clutter | Not possible with this lidar stream (heights stop at 1.4 m). Use the camera. |
| 3. Walls give heading | About 5° median error; good only for catching large drift. |
| 4. Trust odometry, gate corrections | Position yes, heading no (0.6-4.8°/min). The small search window works as a jump gate. |
| 5. A map that learns across days | Yes, the main gain. A static-only map is too sparse unless paired with relocalization. |
| 6. Find the pose from scratch | About 50%, or 37% accepted at 86% precision. Needs a second cue to confirm. |

## 6. Proposal for the control PC owner

1. **Remove yaw bias while the dog is still.** When the command is zero and odom xy is steady for 2 s or more, take
   the yaw rate as bias. Subtract it before slam_toolbox and the console's tracker see odometry, and hold heading
   while still.
   - Cheap, and it removes the creep the console follows, so it should also cut the twitches.
   - It can't fix cells already smeared into the dog's own voxel map, so prefer snapshots taken soon after the dog
     moved.
2. **Jump gate:** allow at most 0.3 m / 4° per update; anything larger only through an explicit relocalization. Log
   applied and rejected corrections, and `map.track`, to `/events`.
3. **Consensus reference map** from logged clouds (`pgo.py` + `persistence.py`), rebuilt weekly: 2.5D column tops of
   0.5 m or more, occupied in 50% or more of views across days. Match the cloud's cells of 0.5 m and up against it,
   instead of the 0-10 cm slice. Keep the saved map for route planning.
4. **Relocalize behaviour:**
   - Search the whole consensus map; accept only if the runner-up is at most 0.95 of the best.
   - Otherwise move 0.5-1 m and retry, up to 4 times. Expect about 37% acceptance at about 86% precision per attempt.
   - Confirm an accepted pose with a different cue: the camera against stored trail pictures, or an AprilTag. Hand
     placement stays the fallback.
   - Spinning in place adds little: the snapshot already covers 360°, and a turn changes about 24% of cells, partly
     smear.
5. **AprilTags** at 3-4 spots, for ground truth and absolute heading. Oliver has none yet; the camera study looks at
   fixed things up high instead.

## 7. Camera relocalization

Full study: `visual/REPORT.md`.

- **No ceiling yet.** Every stored picture is level: `look` springs back before `photo`.
- **Upper part of the frame:** survives a day of furniture changes better than the lower part, but not better than the
  whole frame.
- **Matching against stored pictures across days:** 63% of queries get a pose at 93% precision, with a position median
  of about 0.3 m and relative yaw to about 2°.
- **Combined with a spin** (best of about 4 frames from one turn in place): 86% coverage at precision 1.00.
- **Masking movable things with the VLM** did not help.
- **Use it as the second cue that confirms a lidar global match** (section 6, item 4). The camera says which place and
  which way the dog is facing; the lidar does the last 0.3 m.
- **The poses on the stored pictures are noisy too** (yaw errors 8-12° median), so a survey walk with no hand placement
  is needed to build a clean set of stored pictures.

## 8. Needs the dog (about 1 hour)

1. **Still test:** 10 min on a taped mark facing a fixed landmark, with photos at the start and end. Expect odom yaw to
   change by +1 to +5° while the picture doesn't. Repeat after the dog lies down and stands up, and note `imu.temp`.
2. **Three taped marks with known heading.** At each: 1 min still, a 360° turn, 1 min still. This gives a reference
   for the console, the consensus localizer, the global search and wall heading. Also check one long wall's direction
   against the saved map (the possible bend).
3. **One slow, quiet mapping walk** of the whole lab (about 5 min), to add pose-graph links in corners the dog rarely
   visits.
4. **Questions for the control PC owner:**
   - What is `cloud.flat`?
   - Can `map.track` go into `/events`?
   - Is odom yaw the IMU yaw? (`imu.rpy[2] == odom.yaw` tonight.)
   - Can a still-time yaw-bias correction go where odom is republished?

## 9. Caveats

- The reference is the offline pose graph, checked only on held-out revisits. Its absolute frame is the console's
  average frame, so absolute heading is uncertain by several degrees.
- Everything is a replay of logged data; nothing ran on the dog.

## Files (`go2/localization/`)

- **Code:** `common.py`, `jumps.py`, `persistence.py`, `revisits.py`, `pgo.py`, `refine_poses.py` (superseded),
  `matcher.py`, `localizer.py` (online / global / global2 / walls modes), `keyframe_reloc.py`, `walls.py`,
  `make_figures.py`.
- **Figures (`figs/`):** `fig1_yaw_drift.png`, `fig2_online.png`, `fig3_global.png`,
  `fig4_odom_mosaics_on_saved_map.png`, `fig5_trail_pictures_desk_oliver_kang.jpg`, `persistence_pgo.png`,
  `persistence_console.png`.
- **Results (`results/`):** `jumps_sessions.csv`, `jumps_events.csv`, `odom_yaw_drift.csv`, `revisit_pairs.npz`,
  `pgo_poses/`, `pgo_eval_*.json`, `persistence_*.npz/json`, `online_metrics*.json`, `online_logs*/`,
  `global_summary.json`, `global_results.json`, `global_two_view.json`, `keyframe_reloc.json`, `walls.json`.
- **Other:** `problems_found.md`, `console_snapshot/` (saved map and state read at 00:16), `scratch/` (one-off
  checks), `cache/` (parsed logs, 113 MB, can be regenerated).
- **Superseded runs:** kept as `results/v*_*` and `figs/v*_*`.
