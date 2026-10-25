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
| `0d6dc6d3` | After a turn in place over 45 deg, the next 3 lidar views search heading ±5 deg instead of ±2. The tracker had lagged 7-10 deg after turns when drift was high. Tool replies now carry `suspect` |
| `b4c9bccf` | (nav-planner) The live view now sees office chairs and things under desk tops; before, it dropped any cell topped at 0.6-1.0 m. Those are hard obstacles; open floor under a desk top gets an extra cost instead of a block. In the 10-23 replay, routes crossing hidden obstacles went from 7 to 0 |

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

## Morning test plan

Everything below is untested on the dog. Before you start, turn on **Record** in the console, so `/point_cloud2` +
odom are saved for later replays. `GET /history?keys=loc,map_pose,odom&since=<unix t>` returns the once-a-second
log for any window, with `loc_events` and `agent_calls`; note the start time of each step.

1. **Distance scale (5 min).** Lay a tape 3 m straight. Note odom `x, y` from `/state.json`, walk the dog along the
   tape at normal speed, note them again, then repeat the other way.
   - *Look at:* the odom distance. About 2.6 m (scale 0.86) confirms that odom reads ~14% short; 3.0 m means it's fine.
2. **Marker range (5 min).** Dog standing still; marker A at 1, 2 and 3 m, straight ahead and then ~30 deg to the
   side. Measure the printed black square (should be 18.0 cm).
   - *Look at:* `/markers` `dist` and `fix_ok` against the tape. The two camera models differ by 9%.
3. **Line-up and a short drive (5 min).** Start the console and let it line up, or place the dog by hand. Drive
   about 10 m with a couple of turns.
   - *Look at:* `loc.track_fit` (around 0.8-0.9 when placed right) and `loc.fresh_fit` on the console.
   - In `/history`, `loc.lost` should stay off. Compare the map arrow with the camera.
4. **Turns in place (5 min).** Turn 90 deg in place four times, pausing between turns, then walk 2 m.
   - *Look at:* `loc.track` entries with `"wide": true` right after each turn, and whether the map arrow lines up
     with the walls within a few seconds. Check for `loc.suspect` coming on.
5. **door_outside (5 min).** `go_to` into `door_outside`, then `go_to` back out to any place.
   - *Look at:* it should now plan out; it used to say `no_route`.
   - The reply has `fallback` if the stall-block retry was used. `stop_reason` tells why a drive stopped.
6. **Chairs and desks (10 min).** `go_to` a place across the desk rows, with chairs pushed out into the aisle.
   - *Look at:* the route on the map should go around the chairs, not under a desk.
   - Watch the dog's own avoidance. If it stalls, note `stop_reason` and the time.
7. **Long drive with suspect on screen (10+ min).** Several places in a row, one stop of a few minutes.
   - *Look at:* when `suspect` comes on (tool replies, or `loc.suspect` on the console). Check against the camera
     or a marker whether the dog was really off.
   - Note what was in view: a moved object, or right after a turn.
8. **Relocalize (5 min).** Place the dog wrong by hand by about 1.5 m, then call `/agent/relocalize`.
   - *Look at:* whether it puts the dog back on the right spot, and the candidates' scores.
   - In replays the right pose came first in 31-36 of 36 tries.

Afterwards, stop recording and note the bag name. That recording is what lets us re-tune `suspect` and check the
chair/under-desk change against real data.
