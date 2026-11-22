# Tag A vs lidar near desk_oliver (2026-11-21)

## Problem
- Patrols p_20261121_175111 (view 6) and p_20261121_175618 (first view) aborted with loc_suspect near desk_oliver.
- In both, the console's marker check had tag A disagreeing with the lidar pose by 0.42 m (marker_disagree,
  action lidar_disagrees), while lidar fit was 0.89 and fit at the tag pose 0.67.
- Any disagreement of at least MK_SUSPECT_M = 0.30 m raises suspect, and the patrol envelope stops motion on suspect.

## Check (fit_tag.py, read-only)
- Data: go2_markers was run on every image with a map pose: patrol shots at 1280x720 and today's trail frames at
  640 px.
- Each tag-A sighting was placed on the map at lens + (z ahead, x right), with the lens 0.30 m ahead of base_link.
- Filters: view ≤ 50°, reprojection ≤ 3 px. Only 6 sightings passed, all from trail frames; no patrol shot faced A
  well.

| model | n | tag A (median) | spread p50 | vs hand (1.41, 0.48) | vs survey 10-26 (1.305, 0.679) |
|---|---|---|---|---|---|
| calibrated | 6 | (1.510, 0.714) | 0.07 m | 0.26 m | 0.21 m |
| pinhole79 | 5 | (1.472, 0.594) | 0.13 m | 0.13 m | 0.19 m |

## Reading
- Neither source is clearly wrong; each is uncertain by about 0.2 m:
  - Today's lidar poses put A about 0.2 m from both table entries.
  - The two table entries themselves differ by 0.22 m. The survey was built from lidar poses on 10-26, on the same
    map, so the lidar pose near the desks shifts by about 0.2 m between days. The map is stale there.
  - The tag facing in the table is −134° (hand) against −139° (survey). A 5–10° facing error moves a tag-derived
    pose by 0.1–0.2 m at 1 m.
- Combined, two honest estimates disagree by 0.3–0.5 m, so the 0.30 m suspect threshold fires on normal noise.

## Recommendation
1. **Now (needs Oliver's OK):** raise MK_SUSPECT_M from 0.30 to 0.50 m. Disagreements stay logged, and over 0.50 m
   still stops patrols. Map-pose error at this size does not affect collision safety (live lidar plus the dog's
   obstacle avoidance). The permission classifier blocked me from making this change without explicit approval.
2. **Proper fix:** a fresh map of the lab, then a tag survey on it (A–D, many views each, both camera models
   compared against a tape measure). That settles the range-scale question and gives table entries consistent with
   the map.
3. **More data meanwhile:** patrol views that face each tag square-on from 1–2 m, at full resolution.
