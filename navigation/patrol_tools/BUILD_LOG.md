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
