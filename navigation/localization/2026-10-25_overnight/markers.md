# ArUco markers: why they are missed, a fixed detector, and gating for position fixes (2026-10-25 overnight)

Offline only (subagent of the loc-research session; full scripts in `~/go2_overnight/markers/` on Z690; saved by that session from the agent's final report, with
two claims re-checked in code: the bearing conventions and the launcher copy list). Nothing in `~/oliver` was
changed, nothing was sent to the robot.

## Root cause of "no markers in view while they're visible"

No logic bug in the live pipeline: `/root/go2_markers.py` in `go2_test` matches `~/oliver/go2_markers.py`, the
container has cv2 4.11.0 and the code uses its `ArucoDetector` API correctly, on the full 1280x720 bgr8 frame in
grayscale, ~14 ms per frame at ~10 Hz. Replaying all 7447 raw `/camera/image_raw` frames of the 10-23 bag through
the exact live code: while a marker is in view, the console would show nothing in **7.2%** of 10 Hz updates.

Causes, largest first:
1. **Overexposure.** In the 10-24 17:06 bag 48% of pixels are saturated and marker A, plainly visible, is
   detected in 1 frame of 432: its black square renders light grey. No detector setting or preprocessing
   (gamma, CLAHE) recovers it. On 10-23, 29% of frames have >30% saturated pixels. Needs a camera-side fix.
2. **No hold:** each frame's result replaces the last, so one missed frame shows "no markers in view".
3. **Image edge** (strong barrel distortion, k1 = -0.35): 88 of 145 misses next to hits.
4. **Motion blur:** 31 of 145.
5. **Cell-border sampling:** default `perspectiveRemoveIgnoredMarginPerCell` 0.13; 53 of 145 misses decode at 0.30
   (mostly A).

False positive: a printer control panel decodes as id 3 (D), upside down, in 16 frames on 10-23.
The detector thread catches only `cv2.error`; any other exception would stop detection silently (no sign it
happened).

**Bearing sign (cheetah's question): not flipped.** `/markers` `bearing_deg` > 0 = right of straight ahead in all
1392 sightings (go2_markers.py:5, :65). But `/trail/near` (go2_trail.py, `near()`) uses the opposite convention,
+ = left, which is the likely source of the confusion.

## Current code: frames with at least one detection

| frames | n | A | B | C | D | other ids |
|---|---|---|---|---|---|---|
| raw 10-23 bag | 7447 | 388 | 497 | 142 | 357 (16 printer FP) | 17 x30, 37 x18 |
| raw 10-24 bag | 432 | 1 | 0 | 0 | 0 | 17 x3 |
| trail (640x360) | 3202 | 97 | 99 | 32 | 60 | |

Parameter sweep (total detections, raw 10-23): default 1384; margin 0.25-0.35: 1424; errorCorrectionRate 1.0: +44
but 670 junk-id frames; gamma/CLAHE/sharpen/1.5x upscale: within +-10; undistorting first: -7%. Parameters are
not the main lever.

## The fixed detector: `go2_markers_fixed.py` (drop-in, same class, `detect()`, `snapshot()`)

- cell margin 0.30, subpixel corners (pose only);
- rejects markers that aren't upright, shortest side < 15 px, non-convex quads;
- pose by `solvePnPGeneric` IPPE_SQUARE on undistorted corners, both solutions kept;
- new keys: `dist, view_deg, yaw_deg, reproj_px, ambig, alt, min_side_px, edge, fix_ok, why`;
- `snapshot()` holds a marker 0.5 s after its last sighting (flagged `held`, never `fix_ok`);
- the thread catches every exception; the last one is in `latest.err`.

| frames | before A/B/C/D | after |
|---|---|---|
| raw 10-23 | 388/497/142/357 | 403/504/142/343 (D: 16 printer false positives removed; the rest of the drop are real but tiny D sightings under 15 px) |
| trail | 97/99/32/60 | 101/102/32/57 (D: 3 real sightings 5-7 px wide at 640 px, 3-4.5 m, dropped by MIN_SIDE_PX; not false positives) |
| 10-24 | 1 | 1 |

"Nothing shown while in view" (raw 10-23): 7.2% -> 5.8% (no hold) -> **2.4%** (with the 0.5 s hold).
Median 15 ms per frame; a threaded smoke test gave no errors.

## Pose quality (1392 sightings, raw 10-23)

| range | n | reproj best/2nd (px) | ambiguous (ratio > 0.5) | range jitter frame to frame, median/p90 |
|---|---|---|---|---|
| 0-1 m | 223 | 0.93 / 12.5 | 4% | 0.5 / 2.1 cm |
| 1-2 m | 451 | 0.46 / 4.1 | 6% | 0.7 / 2.9 cm |
| 2-3 m | 417 | 0.20 / 2.1 | 12% | 1.4 / 6.3 cm |
| 3-4 m | 115 | 0.10 / 0.37 | 21% | 1.7 / 8.3 cm |
| > 4 m | 185 | 0.15 / 0.20 | 83% | 4.0 / 11.5 cm |

- The two IPPE solutions differ by <= 1 cm in position: a flip changes only the marker's orientation, so a
  range + bearing fix is barely affected. Orientation is unusable for front-on (< 15 deg: 41% ambiguous) or far views.
- **The real risk at ~3 m is range scale, not noise:** the bag's calibration (fx 864) vs the tape-checked 79 deg
  pinhole (fx ~776) differ by 9%, about 27 cm at 3 m; pinhole ranges also read 5-7% long at 30-45 deg off-axis.
  A lidar cross-check was inconclusive (unknown ~0.1 m offset). The fix keeps the tape-checked model.
  **Needs a tape check at 1, 2, 3 m, centred and ~30 deg off-axis, and a measurement of the printed square.**

## Gate for using a sighting as a position fix (implemented as `fix_ok`)

dist <= 3.0 m, view angle <= 60 deg, smallest side >= 30 px, not at the image edge (edge <= 0.85), reprojection
<= 2 px, same id in 2 of the last 3 frames within 1 s with range within 15%; use range + bearing only (orientation
only if ambig < 0.5 and view > 15 deg). For the localizer (not built): reject fixes implying a jump > ~1 m or
15 deg, sigma ~ 0.15 m + 5% of range, don't fuse B or D until surveyed. 581 of 1392 sightings pass.

## Survey from trail frames (cross-check only; Oliver's tape survey should replace it)

| marker | gated sightings | x, y | spread median/p90 | draft | difference |
|---|---|---|---|---|---|
| A | 49 | 1.21, 0.91 | 0.17/0.32 m | 1.65, 0.89 | 0.44 m |
| B | 39 | -0.63, -3.95 | 0.31/0.56 m | -0.67, -3.83 | 0.13 m |
| C | 30 | -5.70, 0.88 | 0.31/1.08 m | -5.89, 0.91 | 0.20 m |
| D | 46 | 0.52, 2.48 | 0.63/1.72 m | 0.36, 2.47 | 0.16 m |

Spread does not grow with range, so it is trail map-pose error (some trail poses are up to 2 m off).

## Deploy (not done)

1. Copy `go2_markers_fixed.py` to `~/oliver/go2_markers.py` (`markers_fixed.diff` here).
2. `run_go2_keys.sh` does **not** copy `go2_markers.py` into the container (it copies keys, dashboard, agent,
   mapper, trail, nav): `docker cp` it by hand or apply the launcher part of
   `deploy/optional_dashboard_and_launcher.diff`.
3. Restart the dashboard process. Optional dashboard diff tags held markers "(just lost)".
4. Consumers of `/markers` should skip items with `held` set.

Untested live (load, DDS drops). The upright rule rejects markers mounted rotated; min side 15 px drops sightings
beyond ~9 m.
