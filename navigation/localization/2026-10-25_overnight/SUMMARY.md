# Overnight 10-25: what we found, what changed, what to test this morning

For Oliver. The work was offline: recorded bags, pose logs and the failure log. Nothing drove the dog. Details are in
`REPORT.md` and `markers.md` (this folder) and in `../../route_planning/2026-10-25_go_to_failures/`.

## What we measured

- **The lidar data is the dog's own map, not raw scans.** Over WebRTC we get `voxel_map_compressed`: a 5 cm voxel
  map of about 6 x 6 m around the dog, in its drifting odom frame. In any view, the median voxel was placed **72 s**
  earlier, and 35% are over 2 min old. Each sits where the dog put it with the heading it had *then*. So the
  drift tracker was matching a smear of past headings. (Raw L1 scans and Point-LIO, as the research doc suggests,
  aren't available over WebRTC.)
- **Heading drifts with a gyro bias that wanders.** While the dog stands still, odom heading drifts a median
  **+1.2 deg/min** (pose logs 10-23 to 10-25, 95 still periods). It was +2.5 on 10-24, and single periods ranged
  from -4 to +6.
- **Odom under-reports distance by about 9-13%.** Two independent checks agree:
  - markers: odom distance / camera-measured distance = 0.865;
  - lidar: walls re-seen after a straight walk land 0.10 m back per ~1.1 m walked, giving a scale of 0.91.

  This needs your tape check (below).
- **Replays.** We replayed the 10-23 drive through the console's own localization code against the straightened
  path.
  - The old tracker held up at today's drift, but at +4 to +6 deg/min of extra drift it ended **1.4-2.0 m and
    20-25 deg off**.
  - Matching only voxels placed in the last 20 s held 0.07-0.10 m in every case.
- **Relocalize works on this map.** A whole-map search from recent lidar found the true pose first in 31-36 of 36
  tries, even when started 1.5 m and 30 deg off.
- **go_to failures.** The 90 logged failures are 46 episodes. The causes since the 10-23 planner change:
  - 15 records with the pose lost (the 10-24 16:23 period);
  - 11 stuck at `door_outside`;
  - 11 stall "blocks" closing an aisle the map has open;
  - 8 live lidar cells.

  The casebook is `../../route_planning/casebook.json`.

## Markers

- **Not a code bug.** Through the live code, nothing is shown while a marker is in view 7.2% of the time. With the new
  detector and a 0.5 s hold, that's 2.4%. A printer panel used to read as "D" upside down.
- **What makes a marker unreadable is its own brightness:**

  | marker patch brightness | read |
  |---|---|
  | under 150 | 94% |
  | 150-200 | 84% |
  | 200-230 | 70% |
  | 230-245 | 36% |
  | 245 and up | 0% |

  Whole-frame brightness doesn't predict misses: the lab is bright everywhere.
- **10-24 "marker A visible but never read".** The dog was under a desk with someone sitting there. The camera
  exposed for the dark foreground, so the bright room behind, with A in it, was blown out (A's black squares came
  out light grey). The driver has no exposure control. **Advice:** read markers from open floor, not from under or
  next to dark furniture, and keep markers away from windows and lamps in the camera's view.
- **Bearing sign is fine.** `/markers` uses + = right. `/trail/near` uses + = left, which caused the confusion.
- **Keep markers upright.** The new detector rejects upside-down decodes, so ids 4-11 must be mounted the same way.

## Deployed tonight (by the coordinator after review)

| commit | what |
|---|---|
| `b2bf76ab` | Drift tracker matches only voxels placed in the last 20 s (`TRACK_FRESH_S`; 0 turns it off) |
| `243ec2ce` | Marker detector: rejects false and tiny decodes, keeps both pose solutions, 0.5 s hold, `fix_ok` gate |
| `f0cc8b4a` | `go_to` stops with `stop_reason: "lost"` when `loc.lost` is set (coordinator) |
| `b458894e` | Planner fallback: if no route, try again ignoring stall blocks (live obstacles keep full clearance); the dog may leave a narrow spot the way it came in. Also: `loc.fresh_fit` + `loc.suspect` (advice only), and a fix so a long stand doesn't make the lost timer fire at once |

Replay and offline checks on the deployed code:
- 21 of the 30 recent failures not caused by a lost pose now plan;
- 0 of 480 normal routes changed;
- no routes are planned while lost;
- `door_outside -> anywhere` goes from 0/15 to 15/15.

## Rejected, and why

- **Heading hold** (cancel heading change while standing still): it won only when the test drift was constant. With
  real, wandering drift it gained about 0.5 deg and nothing in position, so it was dropped.
- **Squeezing past live obstacles at ~0.1 m** (would fix 5 more failures): the camera frames at those spots show a
  real wooden panel and boxes, not lidar noise. It stays off.
- **A stricter "lost" rule** based on the fresh-voxel fit: it caught bad poses fast, but on 10-24 (a changed room) a
  well-placed dog sat right at its threshold. It ships as the advisory `loc.suspect` instead. On suspect, take a
  marker fix or run a relocalize search before a long go_to.
- **"Overexposed" flag on markers:** the data doesn't support one (see the table above).

## Known open issue

After a turn in place the tracker can lag 7-10 deg in heading for ~30 s, because it skips views while turning and
then corrects at most ~1 deg per view. Being tested now; see the next commit if it pans out.

## What to test on the dog this morning

1. **Distance scale (5 min).**
   - Lay a tape measure on the floor, 3 m straight.
   - Note `/state.json` odom x, y, walk the dog along the tape at normal speed, and note them again.
   - Repeat both ways. If odom reads about 2.6-2.7 m, the ~10% scale is real.
2. **Marker range (5 min).** With the dog still, put marker A at 1, 2 and 3 m, centred and then about 30 deg to the
   side. Note `/markers` `dist` each time. Also measure the printed black square (should be 18.0 cm). This settles
   which camera model is right; they differ by 9%, about 27 cm at 3 m.
3. **Record lidar every session.** Turn on Record so `/point_cloud2` + odom are saved. Only 13 minutes of lidar exist
   after the map was made, and changed-room days are exactly what we lack.
4. **door_outside.** `go_to` into `door_outside`, then `go_to` back out to any place. It should now plan out (it
   used to report `no_route`).
5. **A long drive with `loc` on screen.** Drive 10+ min, including several turns in place and a stop of a few
   minutes. Watch `loc.track_fit`, `loc.fresh_fit` and `loc.suspect`. Note the times when suspect comes on, and
   whether the dog was really off: check against a marker or the camera.
6. **Relocalize.** Once, place the dog wrong by hand by about 1.5 m, then call `/agent/relocalize` and see if it
   finds the right spot.
