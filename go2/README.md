# go2: the lab's Unitree Go2 Pro, driven from cheetah

Code for getting the lab's Go2 to walk to places, photograph them and remember what it saw, plus the two
studies that decide how its memory should work.

| folder | what |
|---|---|
| `lab_agent/` | **current**: talk to the dog (phone page or terminal): Opus answers from the picture memory or drives the dog |
| `console/` | clients of the control PC's console API (rounds, viewpoints, object anchors, logger) |
| `evidence_memory/` | which memory keeps the right scenes and can look back at them; simulation + the lab tool `lab.py` |
| `lab_routine_sim/` | can a model learn the lab's hidden routines (simulation, 2026-10-17) |
| `go2_patrol/`, `docker/`, `patches/`, `run.sh`, `check_connection.py`, `tests/` | the earlier route: the lab's ROS driver in Docker on cheetah (not used since 2026-10-14; see the end) |
| `data/` | robot data, not in git: event logs, trail frames, patrol pictures, anchors |

## How the dog is reached (since 2026-10-14)

- **The dog** is on lab Wi-Fi at `172.17.39.82`. It accepts one connection.
- **The control PC** (`nesl-Z690-CLASSIFIED`, `172.17.40.64`) holds that connection and runs the web console at
  `http://172.17.40.64:8080`: map, places, route planning, the camera trail and an agent API. Its code lives on the
  control PC (`~/oliver/go2_*.py`); the Claude Code session there owns it.
- **cheetah** (this machine) reaches the console over the wired network and runs everything that calls it:
  rounds, perception, memory. The split was agreed on the board (Oliver's doc "Go2 Robot Dog Lab Guide", tab "Agent
  chat", message #15). Requests for console changes go on that board.

### The agent API, as used here

`POST /agent/<tool>` with JSON including `client`; moves block until done. `claim` takes the dog (lapses after
60 s with no call), `release` gives it back, `stop` is always allowed. A person driving from the console, pressing
Take over or STOP always wins; while they have control, drive calls get 409.

| tool | notes from use on 2026-10-19 |
|---|---|
| `go_to {place}` or `{x, y, yaw_deg}` | plans on the map (A*, 10 cm grid, 28 cm clearance). Near furniture it often has no route or stops short; see board #17-#18 |
| `turn {deg}`, `move {m}` | positive turn = left |
| `look {deg}` | camera tilt: up to about +16, down about -5; springs back to level after about 0.5 s |
| `photo` | waits until the dog is still; the JPEG URL is in `photo.url` |
| `GET /nav/plan?place=` / `?x=&y=` | route preview without moving |
| `GET /places`, `/places/<id>.jpg` | saved places (stand + target) and their preview pictures |
| `GET /trail/coverage`, `/trail/near?x=&y=` | stored camera frames with poses (at most 12 within 0.35 m per query) |
| `GET /state.json`, `/events`, `/map.png`, `/frame.jpg` | state, a 10 Hz event stream, the map, the live picture |

Before driving: `GET /agent/status` (no human owner, `safe: ok`) and `map.mode == "localized"` in `/state.json`.
Home for rounds is `desk_oliver`.

## console/

| file | does | tested on the dog |
|---|---|---|
| `lab_round.py` | one patrol round; `--views` drives to ranked viewpoints until a photo clearly shows each thing | place mode yes (stops in wrong spots near furniture); viewpoint mode not yet |
| `view_plan.py` | ranks camera positions around a thing (distance from its size, clearance, map line of sight) | offline only |
| `view_targets.json` | per place: what the picture must show, the thing's size, and position overrides | - |
| `nav_proto.py` | graded-cost grid + stand choice on the saved map: the planner changes proposed on the board (#18) | offline only |
| `anchors.py` | where a thing is on the map, from trail frames: vision-model sightings -> bearing lines -> intersection | offline only |
| `log_events.py` + `go2-logger.service` | logs `/events` while the dog is on, to `data/event_logs/` | yes |

The logger: `systemctl --user status go2-logger`; test with `bash tests/test_logger.sh`.

## Safety rules (Oliver's)

No one needs to stay next to the dog (Oliver's call, 2026-10-22, replacing his earlier rule). Obstacle avoidance stays on (the console turns it on at start).
Nothing stays connected while the dog is off. Never handle the Unitree account password.

## The earlier route: the ROS driver in Docker on cheetah (2026-10-13)

Built before the control PC took the connection; kept because it works without the console. **Do not start it
while the console is connected**: `./run.sh robot` would try a second connection, and this machine's containers use
`ROS_DOMAIN_ID=42` precisely because the control PC's driver uses 78 and host networking would carry commands to the
real dog.

- `check_connection.py`: first contact over WebRTC (`conda activate go2`); says whether firmware 1.1.15+ needs the
  per-dog key (`unitree-fetch-aes-key`, run by Oliver; the key goes in `robot.env`, not committed).
- `docker/Dockerfile` builds the lab driver [nesl/Go2Controller](https://github.com/nesl/Go2Controller) at
  `f7898ac` with two patches: `0001` decodes the newer firmware handshakes; `0002` picks the SLAM map from an
  environment variable and turns off a 10 s point-cloud dump.
- `run.sh`: `robot [mapping|lab_map]`, `keyboard`, `save_map`, `record` (name positions), `patrol`, `search`
  (with `robot_brain/`), `bag`. Patrol output: `data/patrols/<date>/<HHMM>/<id>.jpg` + `patrol.json`.
- `tests/test_patrol.sh`, `tests/test_search.sh`: run against `tests/fake_robot.py` / `fake_brain.py`, no dog.
- Camera: use the 720p calibration (horizontal field of view about 73 deg; the 1080p file has a wrong matrix).
- cheetah's own Wi-Fi card (MediaTek MT7925) has no driver on kernel 5.15; the wired route to the console avoids it.
