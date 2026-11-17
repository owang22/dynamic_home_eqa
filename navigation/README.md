# navigation/

**Owner: the control-PC agent (Claude Code on Z690, `nesl-Z690-CLASSIFIED`, 172.17.40.64).** Only that agent
edits this folder and pushes it. Others propose changes with a message in `coordination/inbox/z690/`
(see `../COORDINATION.md`).

The code that runs the dog from the control PC: the console (port 8080), its agent API, the map and
localization, the route planner, gait, markers, labelling and the camera-frame trail.

Localization notes and studies are in `localization/`. Route-planning notes, failure summaries and offline
studies are in `route_planning/` (the planner code itself
stays flat here, see below). High-level decisions (where to go and why) are cheetah's `../planning/`.

## Where it runs

The live copy is `~/oliver/` on Z690. `run_go2_keys.sh` starts the ROS 2 driver container `go2_test` (image
`rosrobot`, `ROS_DOMAIN_ID=78`) and copies the console files into its `/root`. This folder is a snapshot of
that code: `./sync_from_oliver.sh` copies it here (code only), and the Z690 agent commits after each change it
deploys. Robot data (maps in `~/oliver/go2_maps`, recordings, trail frames, the remote connector's `secret`)
stays on Z690 and is never committed.

Restarting the console (clears the agent-call log and drops the agent owner):

```
docker cp go2_dashboard.py go2_test:/root/   # and any other changed module
docker exec go2_test pkill -f '[g]o2_dashboard.py'
docker exec -d go2_test bash -c "source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash \
  && exec python3 /root/go2_dashboard.py 8080 > /tmp/dash.log 2>&1"
```

## Automatic run recording

Since 2026-11-15 the console records every session with the dog by itself (Oliver's request, board #50). It starts
when the console has both `/go2_states` and camera frames after a connect, and stops when the dog disconnects (no
state for 15 s), after 4 min with no motion and no commands (standing or lying; `GO2_AUTO_REC_IDLE_S`), or cleanly
when free disk falls below 45 GB (it won't start below 50 GB). Activity or a reconnect starts a new session.
Each session is `~/oliver/go2_recordings/auto_YYYYMMDD_HHMMSS/` with `bag/` (camera as full-size JPEG on
`/camera/image_raw/compressed`, `/camera/camera_info`, `/point_cloud2`, `/odom`, `/imu`, `/tf`, `/tf_static`,
`/joint_states`, `/go2_states`; zstd per message, about 4 GB/hour) and `events.jsonl` (console state once a second,
line-up events, agent calls; no driver identity). `auto_index.jsonl` in that folder has one line per session
(start, end, reason, bytes). The page shows **auto recording** in its header; `/state.json` has `rec.auto`.
Stop recording during an auto session ends it and pauses auto recording until the dog reconnects; Record is
refused while an auto session runs. Off switch: start the console with `docker exec -e GO2_AUTO_REC=0 ...`.

Since 2026-11-16 auto sessions also record the RealSense L515 when its bridge (`~/oliver/l515_go2_pi4_bridge`) is
publishing: `/go2/l515/color/image_raw/compressed`, `/go2/l515/color/camera_info`, `/go2/l515/depth/image_raw` (raw
16-bit mm) and `/go2/l515/depth/camera_info` (not `/go2/l515/points` or the raw colour image: both rebuild from these).
The topics are always listed; `ros2 bag record` picks each up when it appears, so an L515 that is off (or starts
mid-session) neither blocks nor delays the Go2 topics, and is simply absent from the bag. Measured: depth 614 KB ->
~207 KB per frame with zstd at ~8 Hz, colour ~46 KB: about +7.6 GB/hour, so ~12 GB/hour per session with the L515
(~13 at its 10 Hz max). Each `auto_index.jsonl` line now also has `topics_recorded`, `msg_counts` (from the bag's
metadata) and `l515` (true if any L515 message was saved). The manual Record settings have an L515 group.
The page has an **L515 depth camera** panel (colour + colourised depth at ~4 Hz, fps and frame age, "L515 offline"
when the bridge or Pi is off), proxied through the console (`/l515/color.jpg`, `/l515/depth.jpg`) so port 8080 is
enough; `/state.json` has `l515 {online, fps, age_s, bridge}`.

**Line up again uses a marker first** (2026-11-16, Oliver: localization fixes must use vision). If a surveyed marker
is in the detector's latest frame (< 2 s old; fix_ok, not held, ambig < 0.5, <= 30° off face-on, <= 2.5 m), the dog's
map pose comes from the best one (most face-on, then nearest; median of several, spread reported): heading = facing
- 180° + yaw_deg (sign checked on 185 logged tag-A sightings). The lidar then refines within 0.5 m / 10° of it; if it
can't confirm there (no map, low score, worse fit), the marker pose is applied as is and the status says so. With no
usable marker it falls back to the whole-map lidar line-up and the status says why (`no marker in view`, or per tag:
unsurveyed, oblique, far, ambiguous, unsteady). Events: `marker_lineup` (`via: "marker"`, `marker`, `marker_id`,
`fit_before`, `fit_marker`, `fit_after`, `lidar_refined`, `lidar_note`) or `auto_align` with `via: "lidar"`.
**Set dog position uses markers too** (2026-11-16): the click only narrows the region. With a usable marker in view
the marker line-up above runs; if it puts the dog more than 1.5 m from the click (or > 45° from a dragged arrow) it is
still used and the status leads with the conflict ("tag B puts the dog 2.3 m from your click; used tag B"). Without one,
the lidar's line-ups within 0.75 m of the click are filtered to good-enough fits (score >= 0.3 and within 0.10 of the
best there; inside the arrow's ±45°) and the one closest to the click (+0.5 m per rad off the arrow) is applied; if none
passes, the position is left unchanged and the status says so. Events: `marker_lineup` with `clicked`, `click_dist_m`,
`click_conflict`, or `hand_placement` with `via: "lidar"`, `click_dist_m`, `score`, `best_score`, `n_good`.

## Files

| file | what |
|---|---|
| `go2_dashboard.py` | the console: web page, ROS node, HTTP API, recording, places, map control, agent ownership |
| `go2_agent.py` | the agent tools (`move`, `turn`, `look`, `photo`, `look_around`, `go_to`), gait (rocking turns, re-plant step, shuffle-and-retry), `go_to` leg following and replans, squeeze routes |
| `go2_nav.py` | route planner: A* on 10 cm cells, 0.28 m clearance, 0.20 m `tight` retry, 0.12 m `squeeze` retry beyond 1.5 m (the dog walks up and re-plans with live lidar), graded cost, live-lidar overlay within 3 m, speck filter (obstacle blobs of 1–2 cells ignored) |
| `go2_mapper.py` | the occupancy map (5 cm, height layers), saving and loading, line-up (`localize_at`, auto line-up, session restore) and drift tracking (`track()`, ±20 cm / ±2°) |
| `go2_trail.py` | camera frames kept every 0.3 m or 20° with their map pose, 14 days |
| `go2_markers.py` | ArUco 4x4_50 detection (ids 0–3 = A–D, 18 cm). Known issue: often reports no markers while some are in view |
| `go2_examples.py`, `go2_label.py` | labelling objects from boxes in trail frames; Qwen3-VL-8B suggestions |
| `go2_tidy.py` | place tidying and map object cleanup |
| `go2_floor.py`, `go2_straighten.py` | offline map building: floor plane, desk-top layer, straightening a map to the room axes |
| `go2_keys.py`, `run_go2_keys.sh` | driver container start and keyboard driving |
| `go2_map.sh`, `go2_goto.sh` | command-line map control and go-to |
| `go2_claude.sh`, `go2_claude/` | the control PC's own Claude driver (MCP tools over the console API) |
| `go2_remote/` | remote-page connector through a cloudflared tunnel (the secret path is generated locally, never committed) |
| `patch_driver_*.sh` | patches to the driver inside the container, run by Oliver (`--undo` puts the original back) |
| `markers/make_markers.py` | prints the ArUco marker sheets |
| `watch_notes.sh` | a cheap watcher the Z690 agent uses to notice new `/agent/say` notes |

## Console API

Base `http://172.17.40.64:8080`. A person at the console always wins; one agent owner at a time, 60 s lease (`AGENT_LEASE_S`), refreshed by `claim` and tool calls, not by `say`.

| endpoint | what |
|---|---|
| `GET /state.json`, `GET /events` | one snapshot / live stream: odom, `map` (`mode`, `status`, `room_deg`), `map_pose`, `nav.path`, `agents.owner`, `loc`, `markers`, `battery`; `state.obstacle` is the dog's own 4 obstacle ranges (order assumed F/B/L/R, unverified) |
| `GET /frame.jpg` | latest camera frame, header `X-Frame-Age` |
| `GET /map.png`, `/map/layer.png`, `/map/objects`, `/map/proposals` | map image, height layers, object labels, proposed objects |
| `POST /map {action}` | people only: `start`, `new`, `extend`, `stop`, `save`, `revert`, `clear`, `frame {T}`, `align`, `localize_at {x, y, yaw_deg}` |
| `GET/POST /places`, `/places/move`, `/places/delete`, `/places/<id>.jpg` | saved places: stand spot `x, y, yaw_deg`, `target {x, y}` |
| `GET /nav/plan?place=<id>` or `?x=&y=` | route preview without moving; may carry `tight` or `squeeze`, `squeeze_at`, `squeeze_along_m`, and `fallback: live_noblocks` when it only worked by ignoring the 120 s stall blocks |
| `GET /trail/near`, `/trail/since`, `/trail/coverage`, `/trail/<day>/<ms>.jpg` | camera frames with map poses |
| `GET /markers` | live ArUco detections: `id`, `mark` (A–D), `z`, `x`, `bearing_deg` (+ = right), `dist`, `view_deg`, `fix_ok`/`why`, `held` (kept 0.5 s after the last sighting), and more; see `AGENT_API.md` |
| `/label/detect`, `/label/example(s)`, `/label/remove` | labelling by example |
| `POST /agent/<call>` | `claim`, `release`, `stop`, `say`, `status`, `move {m}`, `turn {deg}`, `look {deg}`, `photo`, `look_around {n}`, `go_to {place \| x, y}`, `posture`, `relocalize`; body needs `client` |
| `POST /agent/posture {pose}` | `stand` or `lie`, as the console's buttons do; waits until `/go2_states` body height shows it (stand at 0.24 m or more, lie under 0.18 m; thresholds not yet checked on the dog) and returns `body_height`. `crouch` / `body_height` are not supported yet. While lying, `move`, `turn` and `go_to` fail with `not_standing` |
| `POST /agent/relocalize {mode}` | `search` (around the current pose or `x, y`, `radius_m` 3, clamped 0.5–10) or `global`: the top `top` (5) line-ups of the recent lidar views with the saved map, `[{x, y, yaw, yaw_deg, score, fit}]`, not applied; takes about 4–9 s. `set {x, y, yaw \| yaw_deg, force?}`: applies that pose exactly; refused if its `fit` is more than 0.02 below the current one unless `force`; logs a `loc` event `agent_relocalize`. Search replies and refusals carry `current {pose, fit, lost, lost_since}`; a successful `set` returns `fit_before`, `fit_after` and `pose` |
| `GET /history?keys=&since=&until=&step=&limit=` | state once a second over the last 4 h (also kept in `/maps/lab_history/<day>.jsonl` across restarts): `odom.*`, `map_pose.*`, `loc.track_fit`, `loc.lost`, `loc.fit`, `loc.seq`, `obstacle`, `body_height`, `mode`, `roll`, `pitch`, `owner`, `owner_kind`, `call`, `battery`, `markers`, `age.*`; `keys` takes prefixes (`map_pose`). Also returns `loc_events` and `agent_calls` in the window |
| `GET /agent/status?client=<you>` | owner, running tool, `safe`, `battery`, notes, `localization_notice` |

- Results: `done`, `blocked`, `timeout`, `aborted`, `error`, `no_route`, `refused`. A failed plan carries `why`
  (whether the saved map alone had a route); a `go_to` blocked while driving carries `at [x, y]` instead.
- Every tool result also has `stop_reason`, one word to branch on: `arrived` (move, turn, go_to finished), `done`
  (other tools), `obstacle`, `stuck` (no progress), `no_route`, `timeout`, `stop` (STOP or an agent's stop),
  `person` (a person took over), `lost`, `not_standing`, `fallen`, `stale_sensors`, `refused`, `busy`, `bad_arguments`, `error` (the last three also on 409/400 replies). Also `fit`
  (`loc.track_fit` at the end), `lost`, and the final `map_pose` and `odom`; `move` and `go_to` give `moved_m`, `turn`
  gives `turned_deg`.
- `go_to` stops with `stop_reason: lost` when `loc.lost` comes on, or at the start if it's already on
  (`GO_TO_STOP_WHEN_LOST`): relocalize first. `move` and `turn` work on odometry and don't check it.
- `loc`: `{status, seq, fit, runner_up, unsure, lost, lost_since, track_fit, events, track}`; event kinds
  `hand_placement`, `auto_align`, `session_restore`, `new_map`, `drift_correction`, `agent_relocalize`, `unknown`.
  - `fit` / `runner_up` / `unsure` describe the last line-up only (`unsure`: score under 0.3, or less than 0.05
    ahead of the best different heading).
  - `track_fit` is the drift tracker's latest fit: mean wall likelihood of the lidar view, about 0.75–0.9 when
    placed right. Relocalize's `fit` is the same measure.
  - `lost` turns on when `track_fit` stays under 0.65 for 10 s while the dog walks at least 0.3 m. It clears at
    0.70 or on any new placement or line-up. A gap over 5 s between judged views (the dog stood) restarts the timer.
  - `fresh_fit`, `suspect`, `suspect_since` (advisory, never stops anything): the fit of voxels placed in the last
    10 s at the current pose; `suspect` when under 0.65 for 10 s while walking 0.3 m. It can't tell a wrong pose
    from a changed room (10-24: a well-placed dog sat at 0.63-0.72), so on `suspect` take a marker fix or run
    `relocalize search` before a long `go_to`.
- Qwen3-VL-8B: `POST http://172.17.40.64:8000/v1/chat/completions`, model `qwen3-vl-8b` (Docker `go2_vlm`,
  GPU 1), lab LAN only.

Full board history: `../coordination/board_archive_2026-10-23.md`.
