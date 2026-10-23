# Problems found while doing the offline localization study (2026-10-23, no dog)

Each item says what was seen, the evidence, and what it means. Scripts are in `go2/localization/`.

## 1. Odom yaw drifts while the dog stands still (+0.6 to +4.8 deg/min, always counter-clockwise)

- Seen in every session: in 60 s windows where odom position moves < 5 cm, odom yaw grows by a median of
  +0.6 (2026-10-20 evening) to +4.8 deg/min (2026-10-22 16:16 session). Never negative in a session median.
- It is drift in the estimate, not the dog slowly turning on the spot. Test (`scratch/still_rotation.py`): during
  a 4-12 min still period, the voxel cells that appear only at the end line up with the cells from the start
  only after rotating them by about minus the odom yaw change (for example, odom +23.5 deg, best re-alignment
  -25 deg; odom +12 deg, -17 deg; odom +2.6 deg, -4 deg). If the dog had really turned and odom had followed it,
  the new cells would line up with no rotation.
- `/state.json` shows `imu.rpy[2] == odom.yaw` (both -1.242 at 00:16 tonight), so odom yaw looks like the
  IMU's integrated yaw (no magnetometer). The IMU temperature reads 79 degC. The bias differs a lot between days
  (0.6 vs 4.8 deg/min), so a fixed bias correction will not work.
- Consequences:
  - (a) The console's map pose turns with odom while the dog stands still: median map-yaw change per still
    minute is about equal to the odom one in most sessions (table in `results/odom_yaw_drift.csv`).
  - (b) The dog's own voxel map gets smeared, because new cells are inserted with the drifted yaw. Old cells
    stay, so walls come out doubled. The 2D scan the console builds from it inherits the smear.
  - (c) The `map->odom` correction keeps growing: -60 deg over 77 min on 2026-10-20 11:19 and -93 deg over
    22 min on 2026-10-22 16:16. Against the saved map, the console's heading was still right (within 0-4 deg)
    for the first hour of 2026-10-20, so most of the console's yaw corrections are real fixes of odom drift,
    not localizer errors.
- "Trust odometry" holds for translation over seconds to minutes, but not for heading over minutes.

## 2. The cloud's height channel is capped: almost nothing is above 1.2 m

- `cloud.obs` z is the top of each 0.1 m column above the console's `floor_z` estimate. It never drops below
  0.10, it is quantised at 0.05, and desk tops come out at 0.75-0.85.
- The highest value ever logged is 1.45. The median per-cloud maximum is 1.4, but in the 2026-10-22 16:16
  session it is 1.15. The voxel map the dog sends has a limited vertical extent.
- Cells above 1.2 m: a median of 0-40 per snapshot, out of about 2,000. A "ceiling / upper wall" band
  (Roomba lesson 2) is not available from this stream. The best we can do is the 0.9-1.4 m band (top of
  cabinets, monitors, partitions, walls up to the cap).
- `floor_z` itself wanders (-0.12 / -0.08 / -0.07). In some snapshots a large patch of floor comes out as
  "obstacle" at z 0.10-0.20, a diamond of dark-blue cells around the dog. So cells below about 0.25 m are
  mostly floor noise and must not be used.

## 3. The cloud window is a 6.4 m square around the dog, not 8 m

`log_events.py` says "within 8 m of the dog". The cells actually span +-3.2 m in x and y in the odom frame. That
matches the dog's own voxel map extent. It sets the "in view" footprint used in persistence.py.

## 4. `cloud.flat` is in an unknown frame

Each cloud also has `flat` (300-1650 xy points, 700 in tonight's state.json, the same as `map.track.points`). It
is not in the odom frame: 0% of its cells coincide with `obs` cells. Treated as robot-frame points, it fits
`obs` in only some snapshots. Treated as map-frame points, 18-72% of them lie within 0.1 m of a map wall.
Probably the console's tracking scan, taken at a different time or in a different frame. Not used here. Worth
asking the control PC owner what it is.

## 5. The map pose is refreshed at 5 Hz, but logged at 10 Hz

`map_pose` repeats on every other row (`age.map_pose` alternates about 0.02 / 0.12 s). Differencing raw rows
against odom makes fake +-1-5 deg yaw residuals while turning. The fix in `jumps.py`: evaluate odom at each
row's `t - age.map_pose`, using odom samples timed at `t - age.odom`. After this the estimated map/odom lag is
about 0 (between -0.05 and +0.05 s in most sessions).

## 6. Earlier "jumps" were mostly a sampling artefact

With raw rows, my first pass found 16 "jumps" of 0.3-0.7 m while walking. With per-sample timing (item 5), and
with consecutive corrections merged only within 0.5 s, only 2 localizer jumps remain in 370 min of logs:
2026-10-22 16:11:10, 1.32 m / 25 deg while turning, and a 10.6 deg yaw step at 2026-10-20 16:13:42. There are
also 4 probable hand placements (2026-10-22 15:51:08 and three at 16:24). Corrections that are spread over
several seconds are counted separately, as "slides" (net > 0.3 m or > 10 deg in a 10 s window): 21 out of 1,956
windows.

## 7. Not every session is in the saved map's frame

The saved map is dated `2026-10-19 16:54:17`. I checked each session's console poses against the saved map
(`scratch/session_frame_check.py`): the share of cloud cells landing on map walls at the console pose, compared
with the same at poses shifted by 0.6 m or turned by 20 deg.
- 2026-10-14, 2026-10-15 and 2026-10-19 16:29: ratio 0.95-1.07. These are not in this map's frame (older map or
  mapping). They are excluded from persistence and from map metrics.
- 2026-10-19 15:52 and later: ratio 1.12-1.61, so they are used.
- 2026-10-19 15:50, 2026-10-20 12:37 and 2026-10-20 18:47 have no map pose at all.

## 8. The console's heading is the weak part; revisits disagree by a median 5 deg

The same place was registered directly from cloud to cloud (2,186 confident pairs; 158 checked triangles close to
0.03 m / 0.1 deg). On these pairs the console's poses agree within 0.3 m and 5 deg in only 49% of cases:
- 61% of pairs within a session.
- 42% of pairs across sessions.
- 18-21% of pairs involving 2026-10-22.
That fits item 1: the console's heading follows the gyro drift between corrections.

## 9. The saved map is probably bent (not proven)

The evidence is indirect:
- (a) Single snapshots fit the saved map only weakly. The best score is about 0.70, with the runner-up 0.68.
- (b) A rigid fit of each session's pooled cells onto the saved map wants -25 to +16 deg depending on the session.
- (c) The pose-graph map's walls form a clean rectangle, with a dominant direction of 39.5 deg (mod 90, contrast
  1.46). The saved map's dominant direction is 25 deg with a weak contrast of 1.16. Its lower-left walls run at
  about 45 deg, while its top walls run at about 23 deg.

The map was built while the gyro drifted, so bending is plausible. Settle it tomorrow by checking one long wall's
direction against the map.

## 10. Bugs of my own, found and fixed (outputs of the wrong versions moved to `results/v*_...`)

- Matcher pivot half-cell offset, and a cell-corner field origin: synthetic offsets were wrong by 3-5 cm.
- Unbounded hill-climb refinement: it could walk 18 deg out of a +-4 deg window and defeat the jump gate.
  Now bounded to 1 grid step.
- Pose graph with a robust loss on every residual: it broke odometry (jumps up to 1.4 m within 30 s between
  keyframes). Now the robust weights (IRLS) apply only to revisit and console terms. 8 of 1,266 consecutive
  keyframe steps are still > 0.3 m / 5 deg (max 0.38 m / 14 deg).
- Persistence v1 used every calm snapshot. Long still periods dominated, carrying the smear from item 1, and the
  "dynamic" rule fired on any intermediate frequency. Now it uses only "fresh" snapshots (the dog moved
  >= 0.3 m or turned >= 20 deg in the last 30 s), a 0.1 m occupancy tolerance and day-pooled classes.
- Consensus refinement (`refine_poses.py`) without an anchor drifted away from the map. With an anchor it still
  did not beat the console on revisits (50% vs 49%). It is superseded by `pgo.py` and kept for the record.

## 11. Cloud timing is not an issue for map-frame placement

The cells are already in the odom frame. Taking map->odom 1.5 s earlier moves the median cell by 1 mm (p90 3 cm)
in calm periods, and by 2 mm (p90 10 cm) otherwise. `age.cloud` at the logged cloud rows is about 0.05 s.

## 12. A 360 deg turn in place does not give a 360 deg view; the snapshot already has one

The L1 window is 360 deg. After a >= 300 deg turn in place, a median of 24% of the cells are new (44 turns).
Part of that is filled body blind spots, and part is yaw-drift smear. Pooling 60 s of snapshots did not improve
global relocalization (consensus map: 53% from a single snapshot vs 56% pooled).
