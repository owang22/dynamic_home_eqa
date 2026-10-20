# Robot brain: perception, memory and planning for "where is X?"

> **Status 2026-10-19:** built for the ROS-side controller (`go2/run.sh search`). Since 2026-10-14 the dog is
> driven through the control PC's console instead (`go2/README.md`), and the console rounds do not call this
> service yet. The vision model it starts (`serve_vlm.sh`) is the same one the go2 studies use.

The brain tells a robot where to look and whether a picture shows what it is looking for. It never
moves the robot. The controller (`go2/`, `go2_patrol`) walks, photographs and calls this server over
HTTP.

- Model: Qwen3.8-27B with vision, served locally by vLLM (`serve_vlm.sh`, 127.0.0.1:8300). No paid API.
- The brain itself: `server.py` (HTTP, standard library), `brain.py` (logic), `client.py` (standard
  library only, Python 3.10+, for the controller).

| who | owns |
|---|---|
| `go2/` (controller session) | Wi-Fi, map, positions, walking, tilt, photographs, patrols, the search loop on the robot |
| `robot_brain/` (this) | what is in each picture, memory of past patrols, the plan of where to look, yes/no at each look |

## Start

```bash
# 1. the vision model (about 2 minutes to load; leave it running)
nohup robot_brain/serve_vlm.sh > robot_brain/vlm.log 2>&1 &
curl -s 127.0.0.1:8300/v1/models | head -c 100     # answers when ready

# 2. the brain, for the lab
python robot_brain/server.py --data robot_brain/data/lab \
    --positions go2/data/positions.yaml \
    --path-map /data=/home/oliver/robot/dynamic_home_eqa/go2/data
curl -s 127.0.0.1:8400/health
```

- The server can start before `positions.yaml` exists. It reads the file when the file first appears, and again whenever it changes (checked on every call). `/health` shows `positions_file_found`.
- `--path-map` translates paths the controller sends from inside its container (`/data/...`) into
  paths on this machine. Without it, send pictures as bytes (`image_bytes=` in the client).
- The server listens on 127.0.0.1 only. `--host 0.0.0.0` exposes it to the network with no login; use
  it only on a closed network.
- Everything the brain sees and decides is kept under `--data`:
  - `memory.jsonl`: one line per picture, with what the model listed in it;
  - `pictures/`: a copy of each picture;
  - `sessions.json`: each question, its plan and its looks;
  - `events.jsonl`: notes from the controller;
  - `places.json`.

## The loop

```python
from client import Brain                      # robot_brain/client.py
b = Brain()                                   # http://127.0.0.1:8400
b.set_places([{"id": "bench_A", "room": "lab", "description": "workbench by the window"}])   # optional, helps the model
b.ingest_patrol("/data/patrols/2026-10-14/1000")      # after each patrol

s = b.ask("where is the red mug?")
place = s["plan"][0]
while place:
    ...walk to place; if it cannot be reached:
        r = b.feedback("could not reach " + place, session=s["session"], place=place, failed=True)
        place = r["next_place"]; continue
    ...photograph...
    r = b.look(s["session"], place, image_path="/data/looks/x.jpg")      # or image_bytes=jpeg
    if r["found"]: break               # r["box"] is in pixels of the picture you sent
    place = r["next_place"]            # None when the plan is used up
```

## API

All bodies are JSON. Times are ISO 8601 (default: now). Errors come back as `{"error": "..."}`, with:
- 400 for a bad request (e.g. an unknown place id);
- 503 when the vision model is not answering;
- 500 for anything else.

| call | body | returns |
|---|---|---|
| `GET /health` | | `{ok, model_up, places, observations}` |
| `GET /places` | | `{places: [{id, x, y, room?, description?}]}` |
| `POST /places` | `{places: [{id, room?, description?}], replace?}` | the place ids. Adds or updates; `--positions` loads ids and x, y from the positions file |
| `POST /observe` | `{place, image_path \| image_b64, time?, pose?}` | `{place, time, objects: [{name, box}], ...}`. One picture into memory |
| `POST /ingest_patrol` | `{dir}`: a go2_patrol `<date>/<HHMM>` folder | `{observed: [{id, objects}], skipped: [{id, why}]}`. Only positions with `result == "photographed"`; a failed position is not read as "empty". New ids in patrol.json are added as places |
| `POST /ask` | `{question, time?}` | `{session, target, plan, ranked_by_model, answer_type, why}` (see below) |
| `POST /look` | `{session, place, image_path \| image_b64, time?, remember?}` | `{found, box, image_size, description, next_place, done, looks_left}` (see below) |
| `POST /feedback` | `{text, session?, place?, failed?}` | `{logged, next_place?, done?}` (see below) |
| `GET /memory` | | the last 500 observations and 200 events |
| `GET /session/<id>` | | a session's plan, looks, failures and result |

`POST /ask`:
- `plan` lists up to 8 place ids, most likely first. Every entry is an id from the places list: the
  output grammar allows nothing else.
- The model ranks the first `ranked_by_model`. The rest are filled nearest-first from the last
  ranked one, using the positions' x, y.
- `answer_type` is "look", "put away", "someone has it" or "not in my notes". The plan is given in
  every case.

`POST /look`:
- `found` is a yes/no forced by the output grammar.
- `box` is in pixels of the picture as sent, or null.
- With `remember` (default true), the picture is also listed into memory in the background.
- `next_place` is the next untried place in the plan, or null; `done` is true when the thing is
  found or the plan is used up.

`POST /feedback`:
- `failed: true` with a `place` marks that place as not looked at (could not reach or photograph)
  and returns the next place.
- Any text is logged and shown to the model with its notes the next time it plans.

## Known limits

- **Pictures are filed under the place the robot stood at.** A thing seen on a neighbouring bench is
  noted under the place the picture was taken from. The rendered-home study measured this: filing by
  where things rest (which needs a map of the furniture) found more. The brain does not do that for
  the lab yet.
- **Camera height.** The Go2's camera is about 0.37 m up with a 73° lens. In the rendered home only
  2 of 11 things on a counter were visible from 0.37 m, against 10 of 11 from 1.0 m. Tilting up
  helps; tables are partly visible, counters mostly not.
- **Latency.** Listing a picture takes about 2–4 s; `/ask` takes about 2–6 s; `/look` about 1–3 s.
  A patrol of 30 positions is read in about 30 s (4 at a time).
- **Repeatability.** The model runs at temperature 0, but vLLM is not exactly repeatable between runs.

## Checked against the rendered household

`sim_check.py` plays the controller using rendered household A:
- 77 positions, one per piece of furniture;
- patrol folders in the go2_patrol layout;
- where-is questions answered through HTTP with the rendered pictures.

Results on 49 where-is questions (days 3–6, memory from 24 patrols; `data/sim/sim_run3.log`):

| | count |
|---|---|
| The 8-place plan contains a place whose picture shows the thing | **44 / 49** |
| The first place shows it | 19 / 49 |
| Found (the first yes was at a place showing the thing) | 18 / 49 |
| Said yes at a place not showing it | 22 / 49 |
| With `--verify` (each yes re-asked on a close-up of its box): found | 8 / 49 |
| With `--verify`: said yes at a place not showing it | 1 / 49 |

About 15–25 s per question, with 1–8 looks.

- Planning is good. The yes/no at each look is the weak step, as in the rendered-home study.
- `--verify` removes nearly all wrong yeses but also most right ones, so it is off by default.
- For the real run, keep each look's picture; `search.json` on the controller side does. Treat a yes as "probably there" and check it by eye.
