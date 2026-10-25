"""The lab agent's picture memory: every picture the dog has taken, with when, where and what is in it.

    python3 go2/lab_agent/memory.py index            # fetch new console trail frames, describe every new picture
    python3 go2/lab_agent/memory.py watch            # the same every 2 minutes (web.py runs this for you)
    python3 go2/lab_agent/memory.py search "grey backpack" [--since 14:00] [--place desk_kang]
    python3 go2/lab_agent/memory.py stats

Pictures come from two places: the console's camera trail (frames it stores while the dog walks, with map poses;
GET /trail/coverage + /trail/near) and photos the agent takes (server.py adds them as they are taken). Each
picture is described once by the local vision model (Qwen3.8-27B on vLLM, 127.0.0.1:8300): the objects a person
might ask about, with colour and where they are in the picture; how many people; and states worth noticing
(a light on, a door open). Search is word matching over those descriptions; the agent then looks at the pictures
themselves before it answers, so a description only has to be good enough to find the right pictures.

Stored in go2/data/lab_agent/: pictures/ (copies), index.jsonl (one line per picture), places.json (last copy of
the console's places, for naming where a picture was taken when the console is off).
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "lab_agent"
PICS = DATA / "pictures"
INDEX = DATA / "index.jsonl"
PLACES = DATA / "places.json"
TRAIL_CACHE = ROOT / "data" / "trail_cache"            # anchors.py --fetch keeps its copies here
CONSOLE = "http://172.17.40.64:8080"
VLM = "http://127.0.0.1:8300/v1/chat/completions"
HFOV = 73.0                                            # Go2 front camera, 720p calibration

DESCRIBE_SCHEMA = {"type": "object", "properties": {
    "summary": {"type": "string", "maxLength": 300},
    "objects": {"type": "array", "maxItems": 30, "items": {"type": "object", "properties": {
        "name": {"type": "string", "maxLength": 60},
        "colour": {"type": "string", "maxLength": 30},
        "on": {"type": "string", "maxLength": 40},
        "across": {"type": "number", "minimum": 0, "maximum": 1}},
        "required": ["name", "colour", "on", "across"]}},
    "people": {"type": "integer", "minimum": 0, "maximum": 30},
    "people_notes": {"type": "string", "maxLength": 200},
    "states": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 80}}},
    "required": ["summary", "objects", "people", "people_notes", "states"]}
# 30 objects x ~45 tokens + summary/notes/states ~250 tokens: 2000 leaves room, so the schema caps bind first.
DESCRIBE_MAX_TOKENS = 2000

DESCRIBE_ASK = ("A picture from a robot dog's camera, about 0.4 m above the floor, in a university robotics lab. "
                "Describe it so that someone can later find things in it by searching words.\n"
                "- summary: one or two sentences: what part of the lab this is and what stands out.\n"
                "- objects: every object a person might later ask about: bags and backpacks, bottles, cups, laptops, "
                "phones, keys, tools, screws and parts, boxes, jackets, papers, robots, chairs, desks, monitors, "
                "appliances. Use plain names ('backpack', not 'bag-like item'). colour: its main colour. on: what it "
                "sits on or where (floor, desk, chair, shelf, wall). across: where its centre is across the picture, "
                "0 = left edge, 1 = right edge. Skip things too blurred to name.\n"
                "- people: how many people are in view (count a person even if only legs or part of the body show). "
                "people_notes: what they are doing or wearing, briefly.\n"
                "- states: anything in a state worth noticing: a light or screen on, a door open, an indicator lit, "
                "something spilled or fallen.")


def now_s():
    return time.time()


def clock(t):
    return datetime.fromtimestamp(t).strftime("%a %Y-%m-%d %H:%M")


def get_json(path, timeout=10):
    with urllib.request.urlopen(CONSOLE + path, timeout=timeout) as r:
        return json.load(r)


def get_bytes(path, timeout=15):
    with urllib.request.urlopen(CONSOLE + path, timeout=timeout) as r:
        return r.read()


def places():
    """The console's places; the saved copy when the console is off."""
    try:
        p = get_json("/places", timeout=5)
        DATA.mkdir(parents=True, exist_ok=True)
        PLACES.write_text(json.dumps(p))
        return p
    except Exception:  # noqa: BLE001
        return json.loads(PLACES.read_text()) if PLACES.exists() else {}


def nearest_place(x, y, P=None):
    P = places() if P is None else P
    best = min(((math.hypot(p["x"] - x, p["y"] - y), pid) for pid, p in P.items()), default=None)
    return (best[1], round(best[0], 2)) if best else (None, None)


# Vision model servers, tried in order (2026-10-23). The 27B on cheetah has been off since 01:50 (its GPU is gaofeng's).
# The H100 machine is the backup runner for the same 27B: its address goes in vlm_backends.json next to this file
# ({"h100": "http://<host>:<port>/v1/chat/completions"}), or env VLM_H100_URL. The 8B on the control PC takes only
# short questions (locate: one picture, a small answer), not describing every picture: it also serves watch_go_to,
# scan_for and skills, and a description takes it about 70 s.
BACKENDS_FILE = Path(__file__).with_name("vlm_backends.json")
_UP: dict[str, tuple[float, bool]] = {}          # url -> (checked at, answering)


def backends(short):
    import os
    cfg = json.loads(BACKENDS_FILE.read_text()) if BACKENDS_FILE.exists() else {}
    out = [("cheetah-27b", VLM, "Qwen/Qwen3.8-27B", True)]
    h100 = os.environ.get("VLM_H100_URL") or cfg.get("h100")
    if h100:
        out.append(("h100-27b", h100, cfg.get("h100_model", "Qwen/Qwen3.8-27B"), True))
    if short:
        out.append(("z690-8b", cfg.get("z690", "http://172.17.40.64:8000/v1/chat/completions"), "qwen3-vl-8b", False))
    return out


def answering(url):
    """Is this server up? Cached 30 s (a dead one answers 'connection refused' at once; a live one in ms)."""
    t, ok = _UP.get(url, (0.0, False))
    if time.time() - t < 30:
        return ok
    try:
        urllib.request.urlopen(url.replace("/chat/completions", "/models"), timeout=3).read()
        ok = True
    except Exception:  # noqa: BLE001
        ok = False
    _UP[url] = (time.time(), ok)
    return ok


def ask_vlm(prompt, jpgs, schema, max_tokens, fallback=False):
    """fallback=True: a short question, which may also go to the 8B if both 27Bs are down."""
    content = [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b).decode()}}
               for b in jpgs]
    content.append({"type": "text", "text": prompt})
    chain = backends(short=fallback)
    up = [b for b in chain if answering(b[1])]
    if not up:
        raise ConnectionError("no vision model server is answering (tried " + ", ".join(b[0] for b in chain) + ")")
    name, url, model, qwen38 = up[0]
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "a", "schema": schema}}}
    if qwen38:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        ch = json.loads(r.read())["choices"][0]
    if ch.get("finish_reason") == "length":
        raise RuntimeError("description cut off at max_tokens")
    return json.loads(ch["message"]["content"])


def describe(jpg):
    return ask_vlm(DESCRIBE_ASK, [jpg], DESCRIBE_SCHEMA, DESCRIBE_MAX_TOKENS)


# ---- the index ----

def load():
    if not INDEX.exists():
        return []
    by = {}
    for l in INDEX.read_text().splitlines():          # one record per picture: a frame indexed twice keeps the last
        if l.strip():
            r = json.loads(l)
            by[r["id"]] = r
    return list(by.values())


_APPEND = __import__("threading").Lock()


def append(rec):
    DATA.mkdir(parents=True, exist_ok=True)
    with _APPEND, INDEX.open("a") as f:     # one whole line per write (background describers run in threads)
        f.write(json.dumps(rec) + "\n")


def add_picture(jpg, t, x, y, yaw_deg, source, look_deg=0.0, pid=None, background=False, extra=None):
    """Save, describe and index one picture. Returns the record. The nearest place is worked out at search time
    (places can be added or moved later, and the console may be off while indexing). background=True indexes the
    picture at once without a description and writes the described record when the vision model answers (the
    record with the same id later in the file wins: load())."""
    PICS.mkdir(parents=True, exist_ok=True)
    pid = pid or f"{source[0]}{int(t * 1000)}"
    path = PICS / f"{pid}.jpg"
    path.write_bytes(jpg)
    rec = {"id": pid, "t": round(t, 2), "time": clock(t), "source": source, "path": str(path),
           "x": x, "y": y, "yaw_deg": yaw_deg, "look_deg": look_deg}
    rec.update(extra or {})     # e.g. the console's line-up state when the picture was taken (loc, loc_notices)

    def fill():
        r = dict(rec)
        try:
            r["seen"] = describe(jpg)
        except Exception as e:  # noqa: BLE001
            r["seen"], r["describe_error"] = None, str(e)[:200]
        append(r)
        return r
    if background:
        import threading
        append(dict(rec, seen=None))
        threading.Thread(target=fill).start()       # not a daemon: the server process waits for it before exiting
        return dict(rec, seen=None)
    return fill()


def fetch_trail():
    """New console trail frames -> [(frame_info, jpg)]. Frames already indexed are skipped."""
    have = {r["id"] for r in load()}
    frames = {}
    with ThreadPoolExecutor(8) as pool:
        for vs in pool.map(lambda c: get_json(f"/trail/near?x={c[0]}&y={c[1]}", 15).get("views", []),
                           get_json("/trail/coverage", 15)):
            for v in vs:
                frames[v["url"]] = v
    new = [v for v in frames.values() if trail_id(v) not in have]
    with ThreadPoolExecutor(8) as pool:
        jpgs = list(pool.map(lambda v: get_bytes(v["url"]), new))
    return list(zip(new, jpgs))


def trail_id(v):
    return "t" + v["url"].split("/")[-1].split(".")[0]


def index_trail(items, workers=12, background=False):
    def one(item):
        v, jpg = item
        return add_picture(jpg, v["t"], v["x"], v["y"], v["yaw_deg"], "trail", pid=trail_id(v), background=background)
    with ThreadPoolExecutor(workers) as pool:
        recs = list(pool.map(one, items))
    return recs


def retry_failed(workers=8):
    """Describe again every picture whose description failed (model down, cut off)."""
    bad = [r for r in load() if r.get("seen") is None and r.get("describe_error")]

    def one(r):
        try:
            seen = describe(Path(r["path"]).read_bytes())
            append({k: v for k, v in r.items() if k != "describe_error"} | {"seen": seen})
            return True
        except Exception:  # noqa: BLE001
            return False
    with ThreadPoolExecutor(workers) as pool:
        ok = sum(pool.map(one, bad))
    return ok, len(bad)


def watch(every_s=120, stop=None):
    """Keep indexing new console trail frames while the console is up (started by web.py, or `memory.py watch`)."""
    while not (stop and stop.is_set()):
        try:
            retry_failed()
            items = fetch_trail()
            if items:
                recs = index_trail(items)
                print(f"{clock(time.time())}: indexed {len(recs)} new trail frames", flush=True)
        except Exception as e:  # noqa: BLE001 - console off or busy: try again next round
            print(f"{clock(time.time())}: trail check skipped ({type(e).__name__}: {str(e)[:80]})", flush=True)
        time.sleep(every_s)


def cached_trail():
    """The frames anchors.py --fetch copied on 2026-10-19 (the console is not needed)."""
    idx = TRAIL_CACHE / "index.json"
    if not idx.exists():
        return []
    have = {r["id"] for r in load()}
    out = []
    for v in json.loads(idx.read_text()):
        if trail_id(v) in have:
            continue
        f = TRAIL_CACHE / v["url"].split("/")[-1]
        if f.exists():
            out.append((v, f.read_bytes()))
    return out


# ---- search ----

STOP = set("a an the of in on at to is are was were it this that there any some my his her their where what which "
           "who how many much did does do with for from and or".split())


SAME = {"gray": "grey", "colour": "color", "rucksack": "backpack", "knapsack": "backpack", "tv": "television",
        "cellphone": "phone", "mobile": "phone", "mug": "cup", "pc": "computer", "couch": "sofa",
        "refrigerator": "fridge", "sneakers": "shoe", "sneaker": "shoe", "trainers": "shoe", "dustbin": "bin",
        "garbage": "trash", "rubbish": "trash", "wastebasket": "bin", "bookcase": "bookshelf"}

# Object names the vision model gave (162 names over 1,107 pictures on 2026-10-23), mapped to one name per kind of
# thing. Built from the name counts and checked by eye on sample pictures (memory_notes/NOTES.md): "bin" is the
# small white waste bins under the desks; "appliance" is mostly the black water cooler, so it is left alone.
CANON = {"office chair": "chair", "chairs": "chair", "recliner": "chair",
         "cardboard box": "box", "boxes": "box",
         "file cabinet": "filing cabinet", "wooden cabinet": "cabinet", "black cabinet": "cabinet",
         "white cabinet": "cabinet", "drawers": "drawer unit",
         "pc tower": "computer tower", "computer case": "computer tower", "tower": "computer tower",
         "computer monitor": "monitor", "tv": "television",
         "bin": "trash can", "trash bin": "trash can",
         "mop bucket": "bucket", "mop head": "mop", "mop handle": "mop",
         "water bottle": "bottle", "thermos": "bottle", "water jug": "jug",
         "glass": "cup", "mug": "cup", "shoes": "shoe", "sneakers": "shoe", "books": "book", "papers": "paper",
         "cables": "cable", "wire": "cable", "ceiling light": "light", "couch": "sofa",
         "refrigerator": "fridge", "mini-fridge": "fridge", "water dispenser": "water cooler",
         "robotic arm": "robot arm", "robot dog": "robot",
         "equipment case": "case", "plastic case": "case", "storage case": "case",
         "plastic storage bin": "storage bin", "plastic bin": "storage bin", "plastic container": "storage bin",
         "electrical outlet": "outlet", "door handle": "handle", "drawer handle": "handle",
         "keys": "key", "rug": "mat", "cushion": "pillow", "sweater": "jacket", "shirt": "clothing",
         "pants": "clothing"}
# Broader words a search for the kind should also find ("bag" finds backpacks, "computer" finds towers).
KIND = {"backpack": "bag", "paper bag": "bag", "tote bag": "bag", "plastic bag": "bag",
        "filing cabinet": "cabinet", "drawer unit": "cabinet", "bookshelf": "shelf",
        "computer tower": "computer", "laptop": "computer", "monitor": "screen", "television": "screen",
        "robot arm": "robot", "jacket": "clothing", "jug": "bottle", "storage bin": "container",
        "bucket": "container", "trash can": "bin", "broom": "cleaning", "mop": "cleaning",
        "vacuum cleaner": "cleaning", "dustpan": "cleaning", "fridge": "appliance", "microwave": "appliance",
        "water cooler": "appliance", "workbench": "table", "desk": "table", "tool": "tools",
        "screw": "tools", "tape": "tools"}
# Things that are everywhere and rarely asked about: kept in pictures, never made into object instances.
CLUTTER = {"box", "cable", "light", "door", "desk", "chair", "monitor", "cabinet", "drawer", "drawer unit", "shelf",
           "handle", "outlet", "power strip", "paper", "book", "wall", "floor", "door frame", "keyhole", "hinge",
           "kickplate", "label", "sticker", "panel", "wooden panel", "metal frame", "metal base", "pole", "chair leg",
           "object", "white object", "green object", "wooden object", "white curved object", "equipment",
           "electronic device", "part", "cylinder", "partition", "filing cabinet", "person", "mat", "table"}


def canon(name):
    """One name per kind of thing: 'office chair' -> 'chair', 'cardboard box' -> 'box'."""
    n = " ".join(name.lower().replace("_", " ").split())
    return CANON.get(n, CANON.get(n.replace(" ", "_"), n))


def object_words(o):
    """The words an object answers to: its colour, the name the vision model gave, its canonical name, its kind."""
    c = canon(o["name"])
    return set(words(f"{o['colour']} {o['name']} {c} {KIND.get(c, '')}"))


def words(s):
    w = [SAME.get(x, x) for x in re.findall(r"[a-z0-9]+", s.lower()) if x not in STOP]
    return [x[:-1] if len(x) > 3 and x.endswith("s") and not x.endswith("ss") else x for x in w]


def record_text(r):
    s = r.get("seen") or {}
    parts = [s.get("summary", ""), s.get("people_notes", ""), " ".join(s.get("states", []))]
    parts += [f"{o['colour']} {o['name']} on {o['on']}" for o in s.get("objects", [])]
    return " ".join(parts)


def with_places(recs, P=None):
    P = places() if P is None else P
    for r in recs:
        r["near_place"], r["near_place_m"] = nearest_place(r["x"], r["y"], P) if r.get("x") is not None else (None, None)
    return recs


def word_hits(query, recs, synonyms=True):
    """[(score, t, record, best object)] for the pictures whose description shares query words (an object's name
    and colour count most). synonyms=False is the word matching of 2026-10-22 (names as the vision model gave them)."""
    q = set(words(query))
    out = []
    for r in recs:
        if not r.get("seen"):
            continue
        best_obj, hits = None, 0.0
        for o in r["seen"].get("objects", []):
            ow = object_words(o) if synonyms else set(words(f"{o['colour']} {o['name']}"))
            h = len(q & ow)
            if h > hits:
                best_obj, hits = o, h
        rest = len(q & set(words(record_text(r))))
        score = 2 * hits + rest
        if score > 0:
            out.append((score, r["t"], r, best_obj))
    out.sort(key=lambda z: (-z[0], -z[1]))
    return out


WORD_BOOST = 0.05   # fused score = SigLIP cosine + WORD_BOOST * (word score / best word score); memory_notes/NOTES.md


def search(query, since=None, until=None, place=None, source=None, k=12, recs=None, mode="fused", synonyms=True):
    """Pictures that match the query, best first. since/until: epoch seconds.
    mode="words": shared words with the description (newest first among equals; synonyms=False is the old search).
    mode="images": SigLIP text-to-picture similarity, so pictures whose description missed the thing count too.
    mode="fused": the picture similarity, nudged up by the word score (falls back to words if embeddings fail).
    Picture scores are cosines, about 0.05 (unrelated) to 0.2 (clearly there)."""
    pool = []
    for r in with_places(recs if recs is not None else load()):
        if since and r["t"] < since or until and r["t"] > until:
            continue
        if place and r.get("near_place") != place or source and r["source"] != source:
            continue
        pool.append(r)
    wh = word_hits(query, pool, synonyms) if mode != "images" else []
    if mode == "words":
        return [brief(r, obj, score) for score, _, r, obj in wh[:k]]
    try:
        import embeddings as E
        if not E.server_up():                    # the embedding server embeds new pictures itself, once
            E.update(pool)
        img = E.scores(query, [r["id"] for r in pool])
    except Exception as e:  # noqa: BLE001 - no GPU/torch: the word search still works
        if mode == "images":
            raise
        print(f"picture search unavailable ({type(e).__name__}: {e}); words only", file=__import__("sys").stderr)
        return [brief(r, obj, score) for score, _, r, obj in wh[:k]]
    by = {r["id"]: r for r in pool}
    best = max((s for s, *_ in wh), default=1)
    wscore = {r["id"]: (s, obj) for s, _, r, obj in wh}
    fused = {i: v + (WORD_BOOST * wscore[i][0] / best if i in wscore else 0) for i, v in img.items()}
    top = sorted(fused, key=lambda i: (-fused[i], -by[i]["t"]))[:k]
    return [dict(brief(by[i], wscore.get(i, (0, None))[1], round(fused[i], 3)), image_score=round(img[i], 3),
                 word_score=wscore.get(i, (0,))[0]) for i in top]


def brief(r, obj=None, score=None):
    s = r.get("seen") or {}
    b = {"id": r["id"], "time": r["time"], "source": r["source"], "near_place": r.get("near_place"),
         "pose": None if r.get("x") is None else {"x": r["x"], "y": r["y"], "yaw_deg": r["yaw_deg"]},
         "summary": s.get("summary"), "people": s.get("people")}
    if obj:
        b["match"] = obj
    if score is not None:
        b["score"] = score
    return b


def bearing_line(r, across):
    """The map direction of a thing seen at `across` (0 = left edge, 1 = right edge) in picture r."""
    return r["yaw_deg"] + (0.5 - across) * HFOV       # left of centre = positive (map yaw is counter-clockwise)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["index", "watch", "search", "stats"])
    ap.add_argument("query", nargs="?")
    ap.add_argument("--since")
    ap.add_argument("--place")
    ap.add_argument("--cached", action="store_true", help="index the 2026-10-19 trail copy instead of the console")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.cmd == "index":
        items = cached_trail() if a.cached else fetch_trail()
        items = items[: a.limit] if a.limit else items
        t0 = time.time()
        recs = index_trail(items)
        bad = sum(r.get("seen") is None for r in recs)
        print(f"indexed {len(recs)} pictures in {time.time() - t0:.0f} s; {bad} without a description")
    elif a.cmd == "watch":
        watch()
    elif a.cmd == "search":
        since = None
        if a.since:
            h, m = map(int, a.since.split(":"))
            since = datetime.now().replace(hour=h, minute=m, second=0).timestamp()
        for b in search(a.query, since=since, place=a.place):
            print(json.dumps(b))
    else:
        recs = load()
        print(len(recs), "pictures;", sum(r.get("seen") is None for r in recs), "without a description")
        by = {}
        for r in recs:
            by.setdefault(r["source"], 0)
            by[r["source"]] += 1
        print(by)


if __name__ == "__main__":
    main()
