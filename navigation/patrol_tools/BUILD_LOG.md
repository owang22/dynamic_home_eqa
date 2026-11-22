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

## Not buildable here (and why)
- **Live motion tests by the control PC itself:** the permission rules on Z690 block me from sending patrol or motion
  calls to the dog. Live runs come from cheetah, or from Oliver.
- **L515 depth:** the camera is not on the Pi's USB (hardware). It needs a person.

## Verification on later patrols
- **p_20261121_174120 (17:41, AUT's first patrol):** settle-until-still verified. 14 of 14 shots were still=true
  (patrol 1: 2 of 4 false), and the extra wait was at most about 0.5 s. No refusals. fresh_fit 0.66-0.84.
  Observation: facing (3-16 s per heading change, about 16 s for 180 deg) is now a cost comparable to walking.
