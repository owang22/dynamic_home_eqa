# navigation/

**Owner: the control-PC agent (Claude Code on Z690, `nesl-Z690-CLASSIFIED`, 172.17.40.64).** Only that agent
edits this folder and pushes it. Others propose changes with a message in `coordination/inbox/z690/`
(see `../COORDINATION.md`).

What goes here: the code that runs the dog from the control PC.

- the console (`go2_dashboard.py`, port 8080) and its agent API (`go2_agent.py`);
- the map and localization: `go2_mapper.py`, `go2_map.sh`, `go2_straighten.py`, `go2_floor.py`, the drift
  tracker, line-up events, ArUco marker detection;
- the trail of camera frames (`go2_trail.py`);
- vision checks that feed navigation and localization (Oliver's call, board #31): watching a `go_to`,
  arrival checks, `scan_for`, later visual relocalization, on Qwen3-VL-8B in Docker `go2_vlm` on Z690 GPU 1;
- the control PC's own Claude driver (`go2_claude.sh`, `go2_claude/go2_tools_mcp.py`), the remote-page connector
  (`go2_remote/`) and `run_go2_keys.sh`.

As of 2026-10-23 this code lives only on Z690, in `~/oliver/` (copied into the `go2_test` container by
`run_go2_keys.sh`). None of it is in this repo yet; the Z690 agent will add it. The file names above come from
the board and may not be complete. The split between `navigation/` and `planning/` is a first guess: the Z690
agent should move things between them as it sees fit and fix this README.

Not here: cheetah's clients of the console (`go2/console/`, `go2/lab_agent/`) and cheetah's localization studies
(`go2/localization/`). Robot data (maps, bags, pictures, keys) never goes in git.

## Console API as of 2026-10-23 (from the board; the Z690 agent's code is the reference)

Base `http://172.17.40.64:8080`. A person at the console always wins; one agent owner at a time, 60 s lease.

| endpoint | what (board post) |
|---|---|
| `GET /state.json` | one snapshot of everything `/events` streams: odom, `map` (`mode`, `status`, `room_deg`), `map_pose`, `nav.path`, `agents.owner`, `loc`, `markers`, `battery` (#10a, #28, #42) |
| `GET /events` | live stream of the same |
| `GET /frame.jpg` | latest camera frame, header `X-Frame-Age` (#3, #5) |
| `GET /map.png`, `/map/objects` | current map image, object labels (#4, #42) |
| `POST /map {action}` | map control: new, extend, save, stop, align; `{action:"frame", T:[tx,ty,theta]}` sets odom to map by hand (#10, #11) |
| `GET /places`, `POST /places`, `POST /places/delete`, `/places/<id>.jpg` | saved places: stand spot `x, y, yaw_deg` and `target {x, y}` (#10a, #12) |
| `GET /nav/plan?place=<id>` or `?x=&y=` | preview a route without moving (#12) |
| `GET /trail/near?x=&y=&radius=&limit=`, `/trail/since?t=&limit=`, `/trail/coverage` | camera frames kept every 0.3 m or 20 deg, 14 days (#12, #21) |
| `GET /markers` | live ArUco 4x4_50 detections, ids 0-3 at labels A-D: distance `z`, bearing (#38, #40, #42) |
| `POST /agent/<tool>` | `claim`, `release`, `move`, `turn`, `look`, `photo`, `look_around`, `go_to`, `stop`, `say`, `status`; body needs `client` (#10a, #12) |
| `GET /agent/status?client=<you>` | owner, running tool, `safe`, `battery`, `localization_notice` (#10a, #28) |

- `loc` (#28): `{status, seq, fit, runner_up, unsure, events, track}`; event kinds `hand_placement`,
  `auto_align`, `session_restore`, `new_map`, `drift_correction`, `unknown`, and a planned `marker` kind (#38).
- `localization_notice` (#28): on every `/agent/*` response when line-up events happened since that client's
  last call.
- Results: `done`, `blocked`, `timeout`, `aborted`, `error`, `no_route`; `no_route` and `blocked` carry `why`
  (#12, #28).
- Not built yet (#42): `go_to {watch}`, `/agent/scan`, arrival checks and `visual_reloc` events in the console.
- Qwen3-VL-8B: `POST http://172.17.40.64:8000/v1/chat/completions`, model `qwen3-vl-8b`, lab LAN only (#32).

Full history: `../coordination/board_archive_2026-10-23.md`.
