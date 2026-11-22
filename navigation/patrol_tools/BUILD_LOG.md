# Patrol tools build log (Z690, console side)

What the control PC built for the patrol agent, when, and which ask or traced failure each build answers. It's
part of the self-improvement study record (cheetah's planning/patrol_brain/study/). Times are PT, 2026-11-21.
Code is in `../` (go2_patrol.py, go2_dashboard.py, go2_agent.py, go2_watchdog.py, go2_keys.py).

| time | build (commit) | answers |
|---|---|---|
| 16:05 | Driving prior: Oliver's hand driving mined offline (speed, reverse, clearance, dwell spots) → ~/go2_overnight/prior | Oliver's request: learn from how he drives; sets the envelope limits |
| 16:11 | `/map/grid.json` + map_id, keep-out zones, `POST /patrol/check` dry run, pose quality (`loc`) on trail frames (355c8ee4f7) | cheetah's ask (inbox 16:06): coverage from a map export, batched check without motion, pose weights |
| 16:22 | go2_keys follows the console speed preset and the 0.25 m/s reverse cap; podium keep-out dropped (5228690c7a) | the prior found keyboard reversals at 0.38 m/s; Oliver said the podium and door are not hazards |
| 16:50 | The patrol envelope (`patrol/start|stop`), `/agent/view` with views on disk, est_s refit on 17 past go_tos (8723ebb7f2) | cheetah's ask (inbox 16:06): persistence + metadata, machine-readable why, lease and stand rules; Oliver's safety goal |
| 17:29 | Automatic tag line-up when not lined up, `relocalize {mode: tag}` (db5f24a983) | traced failure, patrol 1 pre-start: about 3 min of ambiguous lidar line-up and a mirror pose, while tag A was in view; Oliver asked why vision wasn't used |
| 17:29 | `/agent/view` waits for stillness before the shutter (92b1ab9e68) | traced failure, patrol 1: 2 of 4 shots still=false (cheetah's note 17:27) |
| 17:29 | `GET /patrol/views` candidates (seen counts, walk length), `GET /patrol/prior` (4c0c93a79f) | agreed plan step 4-5 (inbox 16:25) |
| 17:34 | Watchdog detects an L515 missing from the Pi's USB instead of restarting the bridge every 2 min (402d19b77e) | ahead of the expected "L515 back online" ask: the root cause is hardware (unplugged); Oliver asked to reconnect it |
| 17:48 | est_s depends on the speed preset (slow 3.4 s + m/0.12; normal as before); per-heading cost measured (8fb8378f58) | AUT trace, patrol 2: est_s 1.3-1.7x optimistic; draft per-heading ask (as data, no new API) |
| 17:59 | Shot `clearance` (front_clear_m, ranges_deg_m from the live lidar) (7aab51a8fe) | AUT ask 17:47: v003 h1 faced a cable bundle 0.3 m from the lens (patrol 2) |
| 17:59 | `relocalize tag` refusal lists each tag's stand pose and viewable_from_here / turn (7aab51a8fe) | AUT ask 17:52 (offer b): spun 360 deg near the sofa where tag D faces away (patrol 2) |
| 17:59 | `/patrol/check` yaw lists → per-heading est_face_s; shots log face_s (7aab51a8fe) | AUT ask 17:52: flat 6.9 s per heading over-bought big turns |
| 17:59 | loc_suspect says what raised it (`suspect_why`: lidar_fit or tag + shift) (7aab51a8fe) | traced failure, patrol 3: the abort said "lidar looks shifted", but tag A disagreed with the lidar by 0.42 m; the AUT blamed the stale map |
| 18:35 | Turning sweep check (turn_blocked within 0.42 m of centre), no re-plant or shuffle in the sweep, no backward rock in patrols; avoid API mode re-asserted before manual moves (0866f0c19d) | Collision p_20261121_182815 (Oliver stopped it: chair hit by the front while turning and by the back legs while backing); Oliver: manual driving only worked with avoidance off |
| 18:40 | /patrol/check `turn_clear_m` + `ok_to_turn`; /agent/view refuses multi-heading views at stands too tight to turn (turn_clearance) (8cc12ba0f5) | AUT ask 18:34 after the chair collision |
| 18:55 | `GET /agent/surround` (36 x 10 deg nearest live cells, footprint margins, cloud age, pose; no claim) (b702a90fa7) | AUT ask 18:50, item 1 (after Oliver: the agent should plan its own exits) |
| 19:08 | Oliver's tight-spot exits: 261 episodes (125 strict) from his recorded drives, JSON (~/go2_overnight/exits on Z690) | AUT ask 18:50, item 3 |
| 19:14 | `POST /agent/arc` (+ `dry`), swept-footprint check, margin 0.08 m; walls/tall cells now count in the turn sweep and surround (52ec3ce158) | AUT ask 18:50, item 2 |
| 19:45 | Dwell spots (78 candidates + all prior buckets, 244 records) converted to the 19:29 map by the remap's per-node correction; /patrol/views and /patrol/prior serve them | AUT ask 19:36 |

## Not buildable here (and why)
- **Live motion tests by the control PC itself:** the permission rules on Z690 block me from sending patrol or motion
  calls to the dog. Live runs come from cheetah, or from Oliver.
- **L515 depth:** the camera is not on the Pi's USB (hardware). It needs a person.

## Verification on later patrols
Patrols are keyed by patrol_id. The AUT numbers only its own runs; p_20261121_172507 was the experimenter's
baseline. AUT 1 = p_..._174120 (v0), 2 = _175111 (v2), 3 = _175618 (v3), 4 = _180517 (v4), 5 = _180630 (v5),
6 = _181112 (v6). Earlier commit messages here said "patrol 2/6/7" by the experimenter's count; this list is right.
- **p_20261121_174120 (17:41, AUT's first patrol):** settle-until-still verified. 14 of 14 shots were still=true
  (patrol 1: 2 of 4 false), and the extra wait was at most about 0.5 s. No refusals. fresh_fit 0.66-0.84.
  Observation: facing (3-16 s per heading change, about 16 s for 180 deg) is now a cost comparable to walking.
- **p_20261121_180630 (18:06, brain v5):** shot clearance verified live. h0 front_clear_m 0.22 m to a chair seat
  (matches the photo), h1 0.63 m. The brain dropped the blocked heading's credit (46 → 5 cells). The patrol ended
  because of the AUT's own NameError; its finally block stopped the patrol and lay the dog down.
- **p_20261121_181112 (18:11, AUT brain v6):** suspect threshold 0.50 m verified. No tag-A suspect while working at
  desk_oliver (patrols 3-5 had aborted there at 0.30 m). 10 views, 0 refusals.
- **p_20261121_182117 (18:21):** first live L515 capture in /agent/view: colour + 16-bit depth (640x480, 58% valid)
  + camera_infos, dt_to_dog_s -0.014 s. L515 centre-patch median 0.84 m vs lidar front_clear_m 1.06 m (not the same
  quantity: patch vs nearest in ±40°, different mount).
  Correction (18:29, after the AUT's question): L515 depth PNGs are in mm (receiver converts). The 0.84 m above was
  wrong (camera scale applied twice). The centre patch is 3.4-4.3 m and sparse, consistent with the lidar's nearest
  cell at 1.06 m within ±40°.
- **p_20261121_184002 (18:40):** turn_blocked verified live. The dog was lying in the collision pocket (map
  clearance 0.14 m); the first view's go_to refused to turn (obstacle 0.39 m from centre, inside the 0.42 m sweep),
  walked 0 m, and the AUT stopped and lay down.

## 2026-11-22 14:30 — AUT ask 1416 (arrival heading, view without final turn)
1. `/patrol/check` results now carry `arrival_heading_deg`, the heading of the route's last segment (>= 5 cm), and
   `in_place_turns` [{x, y, deg}]. These are the places on the route where the heading changes by more than 45° (start
   included); there the follower stops and turns in place, so the turn-sweep check applies.
2. `/agent/view {x, y, face: "arrival"}` makes no turn at all. It settles and shoots at the arrival heading, then
   reports `arrived_yaw_deg` (also in view.json, and `goal.face`). Giving `face: "arrival"` together with `yaw_deg`
   returns 400. Omitting `yaw_deg` already behaved this way; now it is explicit and reported.
3. Small-turn rule (unchanged, answered): a view turns only when the heading error is over 3° (FACE_TOL_DEG). A
   go_to's final face turns only when it is over 5°. While walking a route, heading errors up to 45° are steered
   without stopping, and only the forward check applies. Any in-place turn, however small, runs the sweep check
   (SWEEP_R 0.42 m) every tick, so there is no small-turn exemption. Loosening that is a safety change and needs Oliver.
4. Reverse `/agent/arc` dry runs now return `rear_unverified: true` + `rear_note`. The dry run cannot see what the
   dog's own avoidance sees behind it.
Tests: test_view 78/78 (4 new), test_patrol 71/71, test_arc 77/78 (1 new). The failing test, "reverse arc from START
stopped mid-arc", fails the same way on the old code: the fixture START is in the old map frame, and the 19:29 map
has an obstacle 0.65 m behind it. go2_wake.sh: the L515 tunnel no longer inherits the wake lock (it blocked every
wake after 11-21 15:52).

## 2026-11-22 15:0x — Oliver: margins too strict; agent may lower them (ask 1430 answered)
- **Stand fix (cause of every "dry clear, moved 0.00" stall today, including Oliver's 14:18 avoid-on drive):**
  - The cause: the console's stand sent BalanceStand 0.2 s after StandUp, while the dog was still rising. The dog
    dropped it and stayed in its locked stand-up pose (body 0.329 m), which ignores walking.
  - Evidence: 14:15:31 arc (avoid on), 14:18:28 Oliver (avoid on), 14:26:36 arc (**avoid off**). In all three, body
    height was 0.329 and there was no motion; it moved once height dropped to about 0.31.
  - The fix: Collector.action("stand") sends StandUp, waits up to 4 s for the height to stop rising (>= 0.28 m and
    steady), then sends BalanceStand twice.
- Stall replies (move, arc, go_to) now carry `stall` / `stall_info`: {dog_avoid_on, body_height, locked_stand_suspect,
  hint}.
- **In-place turn check = the body rectangle swept through the turn still to go** (+10° coast), inflated by the
  turn margin. It used to be a full circle of SWEEP_R 0.42 m.
  - The default margin of 0.03 m keeps a full turn at about 0.42 m. Small turns now need much less.
- **`/agent/margins {client, turn_margin_m?, arc_margin_m?, why?}`**: the agent's own margins.
  - Range 0..0.20 m; `get: true` reads them, `reset: true` restores the defaults.
  - They apply while that client owns the dog and are reset by a console restart.
  - /patrol/check `turn_need_m` / `ok_to_turn` and the turn_clearance refusal use the owner's turn margin.
- **`GET /patrol/human_turns?x=&y=&r=&min_turn_deg=`**: Oliver's 389 in-place turns from his recorded drives.
  - Fields: pose (19:29 map, converted), turn_deg, min_clearance_m (live lidar then) and min_body_gap_m.
  - Source: patrol_tools/human_turns/human_turns.py; data in /maps/lab_prior/human_turns.json, not in git.
  - Near tag B he turned 190° at (0.08, -3.78) with 0.46 m clearance.
  - Overall p5 clearance is 0.28 m, and 118/389 turns were below 0.42 m.
- Tests: test_margins 22/22 (new), test_view 78/78, test_patrol 71/71, test_arc 77/78 (the same old-map fixture failure).

## 2026-11-22 15:1x — AUT asks 1450 + 1452 (Oliver-approved exceptions)
- **1452:** reverse `/agent/arc` rear check now runs along the arc. The saved map's occupied cells behind the dog's
  centre are checked against the body rectangle swept along the arc (+ coast) at the arc margin (`source:
  saved_map_swept`).
  - It runs both before and during the arc. The live cells were already swept by `_arc_sweep`.
  - The straight-back raycast and live rear box are no longer used for arcs; `/agent/move` still uses them.
  - Arc replies carry `stopped_by`: lidar_sweep | rear_map_sweep | progress (with stall_info).
- **1450:** `/agent/move {lateral_m}` strafes (+ left), at most 0.5 m per call at 0.15 m/s, with heading held.
  - It is refused or stopped when the live side gap beyond the body side (within the body length + margin) would
    fall below the arc margin, and it has stall detection.
  - `/agent/surround` gains `bins_detail` per bin: {d_m, kind band|tall|under, z_min_m, z_max_m, kinds_near}.
- Tests: test_arc 78/78 (rear tests rewritten for the swept check; the old fixture failure is gone), test_margins
  27/27 (strafe + surround), test_view 78/78, test_patrol 71/71. The harness sim now integrates lateral velocity.

## 2026-11-22 15:3x — AUT asks 1507 + 1510
- **1507:** the patrol envelope's move pre-check read `m` and returned 400 for `lateral_m`. Strafes now pass through
  it, and they never count against the reverse budget: all strafe replies carry `lateral: true`.
  - `_side_gap` treated an empty live cloud (nothing near) as stale. Fixed.
  - Arc progress stops now carry `stall_info` (as well as `stall`), with `odom_vel` added.
- **1510:** measured with the dog lying: **no /point_cloud2 at all** (12 s, ROS domain 78). The lidar really stops
  while lying.
  - A switch command (rt/utlidar/switch) exists, but the driver's webrtc_req path cannot send a plain publish. It
    would need a driver patch, and whether the firmware streams while lying is unknown.
  - After a stand-up, the dog's voxel map restarts with ~1.3k cells (normally 45-80k) and takes about 10 s to rebuild.
  - Built instead: the **held cloud** (Agents._hold_cloud). The latest standing cloud is kept; while the dog stays
    within 0.05 m / 5° of where it was, it is used when lying (lidar off) and merged into the sparse live map for
    15 s after a stand-up.
  - Flagged as `cloud["held"]` = {age_s, why, n_held, n_live}, shown in /agent/surround `cloud_held`.
  - Standing with no live cloud is still a sensor fault (never held). Long after a stand-up, the live map is used as
    is (no ghosts).
  - Effect: dry runs, surround, /patrol/check at the dog and the turn sweep work while lying. Motion still needs a
    stand (check_safe).
- The held cloud is saved to /maps/held_cloud.json on lie-down and reloaded once after a console restart (deploys happen while lying). Tests use a temp file.
- Tests: test_margins 38/38 (patrol strafe, held cloud, reload), test_arc 78/78, test_view 78/78, test_patrol 71/71.

## 2026-11-22 15:4x — AUT ask 1528 (Oliver-approved exception)
- **Low band:** cells topped 0.10-0.18 m (the console keeps nothing below 0.10 m, OBSTACLE_MIN_H).
  - `/agent/surround` bins_detail: per-bin `low` = {d_m, z_m, kind: low}, plus `low_band_m`. They are not counted in
    `bins` or the checks.
  - Arc dry runs and strafes report `low` = {low_min_clearance_m, low_blocked, low_n_near, margin_m}.
- **Dog avoidance ranges:** not available. /go2_states range_obstacle is 0 in every row, and the driver publishes
  nothing else from the dog's avoidance.
- **One-shot `dog_avoid: false`** on `/agent/move` (m or lateral_m) and real `/agent/arc`:
  - Limits: at most 0.30 m, and |v| <= 0.10 m/s (move and strafe speeds are clamped to 0.10).
  - Refused (409) with `low_blocked` if a low cell would come within the arc margin of the body along the path, or
    with `no_live_cloud`.
  - The dog's avoidance is switched off for that call only and restored afterwards, even on an error or abort
    (`dog_avoid_restored`).
  - All the console's own checks still apply.
- Tests: test_margins 43/43, test_arc 78/78, test_view 78/78, test_patrol 71/71.
