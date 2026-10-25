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
| `GET /nav/plan?place=<id>` or `?x=&y=` | route preview without moving; may carry `tight` or `squeeze`, `squeeze_at`, `squeeze_along_m` |
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
    0.70 or on any new placement or line-up.
- Qwen3-VL-8B: `POST http://172.17.40.64:8000/v1/chat/completions`, model `qwen3-vl-8b` (Docker `go2_vlm`,
  GPU 1), lab LAN only.

Full board history: `../coordination/board_archive_2026-10-23.md`.
