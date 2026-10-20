"""Shared paths, the patrol, the people sheet and the vision-model client for the evidence-memory study
(2026-10-19). Design and arms: DESIGN.md."""
from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import threading
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
LIFE = pathlib.Path("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a")
RENDER = pathlib.Path("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/vlm_night/render")
PICS = {"1.0": pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a"),
        "0.4": pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_0p4")}
VIEWS = {"1.0": RENDER / "spot_views.json", "0.4": RENDER / "spot_views_0p4.json"}
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

DAYS = [3, 4, 5, 6, 7]          # the robot patrols these five days
Q_DAYS = DAYS                   # questions may be about any patrol day
TIMES = ["0800", "1000", "1200", "1400", "1600", "1800", "2000", "2200"]
SEEN_PX = 300                   # an object counts as clearly in a picture at >= 300 pixels (of 640x480)

# The 16 open places with the most putting-down and picking-up over the 14 days (events.json),
# plus the piano shelf where keys get left. The robot visits each one every two hours.
PATROL = [
    "kitchen_kitchen_island_island_countertop",
    "kitchen_kitchen_sink_cabinet_kitchen_sink_basin",
    "kitchen_kitchen_sink_cabinet_countertop_beside_the_kitchen_sink",
    "kitchen_range_left_cooktop",
    "kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range",
    "living_room_living_room_coffee_table_top",
    "living_room_living_room_sideboard_countertop",
    "dining_room_dining_table_tabletop",
    "entryway_floor",
    "hallway_2_piano_middle_piano_shelf",
    "office_office_desk_desk_top",
    "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand",
    "bedroom_1_bed_in_the_main_bedroom_mattress",
    "bedroom_1_floor",
    "bathroom_1_bathroom_vanity_by_the_toilet_top",
    "bathroom_2_floor",
]

# What the robot is told about the household, the same for every method (a lab robot would be told
# whose desk is whose in the same way).
PEOPLE_SHEET = """Two people live here.
- Mara: landscape architect, works weekdays at her studio (roughly 08:30-17:30) and sometimes at the office desk at home.
  Her things include: brass house keys, a tan zippered wallet, an olive canvas tote bag, a silver slim laptop,
  a black glass phone, a green glass phone, tortoiseshell oval reading glasses, a clear steel water bottle.
- Julian: chef who owns a restaurant; on most days out at the restaurant about 09:30-14:30 and again about 16:30-23:30; cooks a lot at home.
  His things include: brass-and-steel keys, a brown leather bifold wallet, a charcoal canvas backpack, a faded denim chore
  jacket, a black glass-and-aluminum phone, a brushed steel thermos, thin bronze round reading glasses.
People are not visible in the robot's pictures (only the things they leave)."""


def hhmm(t: str) -> str:
    return f"{t[:2]}:{t[2:]}"


def load_views(height: str) -> dict:
    d = json.loads(VIEWS[height].read_text())
    return {v["spot"]: v for v in d["views"]}


def spot_name(spot: str) -> str:
    v = load_views("1.0").get(spot)
    return v["spot_name"] if v else spot.replace("_", " ")


def picture(height: str, day: int, t: str, spot: str) -> pathlib.Path | None:
    p = PICS[height] / f"day_{day:02d}" / t / f"{spot}.jpg"
    return p if p.exists() else None


def truth(height: str, day: int, t: str) -> dict:
    return json.loads((PICS[height] / f"day_{day:02d}" / t / "truth.json").read_text())


def positions(day: int, t: str) -> dict:
    return json.loads((LIFE / f"day_{day:02d}" / f"positions_{t}.json").read_text())


def events(day: int) -> list:
    return json.loads((LIFE / f"day_{day:02d}" / "events.json").read_text())


def dump(obj, path):
    path = pathlib.Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    tmp.replace(path)


# ---------------------------------------------------------------- vision model (local Qwen3.8-27B)

URL = "http://127.0.0.1:8300/v1/chat/completions"
MODEL = "Qwen/Qwen3.8-27B"
import os
# EM_RERUN=<name> sends calls to a separate cache, so a rerun makes fresh calls (the rerun noise floor)
CACHE = HERE / (f"cache_rerun_{os.environ['EM_RERUN']}" if os.environ.get("EM_RERUN") else "cache")
CACHE.mkdir(exist_ok=True)
_stats = {"calls": 0, "cached": 0, "failed_parse": 0, "seconds": 0.0}
_lock = threading.Lock()


class ServerDown(RuntimeError):
    pass


def _img(path) -> dict:
    data = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}}


def ask(prompt: str, images=(), captions=None, schema: dict | None = None, system: str | None = None,
        max_tokens: int = 1500, prefix: str | None = None):
    """One call. `prefix` is text put before the pictures (long memory text goes there so the server
    can reuse it across questions). Returns (parsed JSON or text, info). Cached on disk by request."""
    content = []
    if prefix:
        content.append({"type": "text", "text": prefix})
    for i, p in enumerate(images):
        if captions:
            content.append({"type": "text", "text": captions[i]})
        content.append(_img(p))
    content.append({"type": "text", "text": prompt})
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": content}]
    body = {"model": MODEL, "messages": msgs, "temperature": 0.0, "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False}}
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
    key_src = json.dumps([prefix, prompt, captions, schema, system, max_tokens,
                          [(str(p), pathlib.Path(p).stat().st_size) for p in images]])
    key = hashlib.sha256(key_src.encode()).hexdigest()[:24]
    f = CACHE / f"{key}.json"
    if f.exists():
        r = json.loads(f.read_text())
        with _lock:
            _stats["cached"] += 1
        return r["out"], r["info"]
    t0 = time.time()
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(6):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=1800).read())
            break
        except urllib.error.HTTPError as e:  # a bad request will not get better: stop
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:500]!r}") from e
        except Exception as e:  # noqa: BLE001 - server busy or restarting
            if attempt == 5:
                raise ServerDown(repr(e)) from e
            time.sleep(10 * (attempt + 1))
    ch = out["choices"][0]
    text = ch["message"].get("content") or ""
    info = {"seconds": round(time.time() - t0, 1), "usage": out.get("usage"), "finish": ch.get("finish_reason")}
    res = text
    if schema:
        try:
            res = json.loads(text)
        except Exception:  # noqa: BLE001
            info["bad_text"] = text[:1500]
            res = None
            with _lock:
                _stats["failed_parse"] += 1
    with _lock:
        _stats["calls"] += 1
        _stats["seconds"] += info["seconds"]
    if res is not None:          # a failed parse is not cached, so a rerun retries it
        f.write_text(json.dumps({"out": res, "info": info}))
    return res, info


def stats():
    with _lock:
        return dict(_stats)
