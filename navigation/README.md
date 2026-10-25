# navigation/

**Owner: the control-PC agent (Claude Code on Z690, `nesl-Z690-CLASSIFIED`, 172.17.40.64).** Only that agent
edits this folder and pushes it. Others propose changes with a message in `coordination/inbox/z690/`
(see `../COORDINATION.md`).

The code that runs the dog from the control PC: the console (port 8080), its agent API, the map and
localization, the route planner, gait, markers, labelling and the camera-frame trail.

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

Base `http://172.17.40.64:8080`. A person at the console always wins; one agent owner at a time, 60 s lease.

| endpoint | what |
|---|---|
| `GET /state.json`, `GET /events` | one snapshot / live stream: odom, `map` (`mode`, `status`, `room_deg`), `map_pose`, `nav.path`, `agents.owner`, `loc`, `markers`, `battery`, `obstacle` (the dog's own obstacle ranges F/B/L/R) |
| `GET /frame.jpg` | latest camera frame, header `X-Frame-Age` |
| `GET /map.png`, `/map/layer.png`, `/map/objects`, `/map/proposals` | map image, height layers, object labels, proposed objects |
| `POST /map {action}` | `new`, `extend`, `save`, `stop`, `align`, `localize_at {x, y, yaw_deg}`, `frame {T}` |
| `GET/POST /places`, `/places/move`, `/places/delete`, `/places/<id>.jpg` | saved places: stand spot `x, y, yaw_deg`, `target {x, y}` |
| `GET /nav/plan?place=<id>` or `?x=&y=` | route preview without moving; may carry `tight` or `squeeze`, `squeeze_at`, `squeeze_along_m` |
| `GET /trail/near`, `/trail/since`, `/trail/coverage`, `/trail/<day>/<ms>.jpg` | camera frames with map poses |
| `GET /markers` | live ArUco detections: id, label, distance `z`, bearing |
| `/label/detect`, `/label/example(s)`, `/label/remove` | labelling by example |
| `POST /agent/<call>` | `claim`, `release`, `stop`, `say`, `status`, `move {m}`, `turn {deg}`, `look {deg}`, `photo`, `look_around {n}`, `go_to {place \| x, y}`; body needs `client` |
| `GET /agent/status?client=<you>` | owner, running tool, `safe`, `battery`, notes, `localization_notice` |

- Results: `done`, `blocked`, `timeout`, `aborted`, `error`, `no_route`, `refused`; `no_route` and `blocked`
  carry `why`.
- `loc`: `{status, seq, fit, runner_up, unsure, events, track}`; event kinds `hand_placement`, `auto_align`,
  `session_restore`, `new_map`, `drift_correction`, `unknown`.
- Qwen3-VL-8B: `POST http://172.17.40.64:8000/v1/chat/completions`, model `qwen3-vl-8b` (Docker `go2_vlm`,
  GPU 1), lab LAN only.
- Requested, not built yet: `POST /agent/posture`, `POST /agent/relocalize` and `loc.lost`
  (`coordination/inbox/z690/`).

Full board history: `../coordination/board_archive_2026-10-23.md`.
