"""Patrol notes filed by where things rest, merged across overlapping cameras.

The present notes (search.py 'vlm') list what the model sees in each patrol picture under the
furniture the camera points at. About 4 in 10 things in those pictures rest on other furniture,
and overlapping cameras list one thing several times. Here:

  1. detect   the model lists every object in each patrol picture with a box (bbox_2d, 0-1000)
  2. place    the box's bottom strip is looked up in the view's furniture map (render/place_map.py:
              which furniture of the EMPTY home each pixel shows, from the known camera pose), so
              each object is filed under the furniture it rests on
  3. merge    per patrol, names are pooled over all cameras: one entry per name per furniture
  4. notes    the same day-by-day text as search.py; furniture that some patrol picture shows
              (>= SEEN_PX pixels of it) with nothing on it is written 'nothing seen'

Arms (model ranking, perfect looks, as the 84% arm 'llm:vlm:truth'):
  camera   the new detections, filed under the camera's furniture (the present rule)
  placed   the new detections, filed by where they rest
so 'camera' vs 'placed' isolates the filing, and 'camera' vs the 84% arm the new listing prompt.

    python placed_notes.py detect [N]     detect N random patrol pictures (all when omitted)
    python placed_notes.py check          placement accuracy and duplicates (truth used to SCORE only)
    python placed_notes.py run camera placed
    python placed_notes.py report
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import json
import pathlib
import random
import sys

import numpy as np

import search
import vlm
from world import World

HERE = pathlib.Path(__file__).parent
OUT = HERE / "placed"
MAPS = OUT / "maps"
SEEN_PX = 2000
W_, H_ = 640, 480

PROMPT = ("This picture was taken by a home robot. List the separate objects you can see lying on or in "
          "furniture or on the floor (not furniture, not things built into the room). Use short everyday "
          "names. For each give its bounding box as bbox_2d [x1, y1, x2, y2] in coordinates from 0 to 1000 "
          "relative to the picture width and height.")
SCHEMA = {"type": "object", "properties": {"objects": {"type": "array", "maxItems": 25, "items": {
    "type": "object", "properties": {
        "name": {"type": "string", "maxLength": 40},
        "bbox_2d": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "minItems": 4, "maxItems": 4}},
    "required": ["name", "bbox_2d"]}}}, "required": ["objects"]}


def patrol_pictures(W):
    out = []
    for day, t, rooms in W.patrol_plan():
        if not W.rendered(day, t):
            continue
        for f, spots in W.furniture.items():
            if W.places[spots[0]]["room"] in rooms:
                out += [(day, t, s) for s in spots]
    return out


def detect_one(W, day, t, s):
    text, info = vlm.ask(PROMPT, [W.picture(day, t, s)], schema=SCHEMA, max_tokens=1500)
    try:
        objs = json.loads(text)["objects"]
    except Exception:  # noqa: BLE001
        return None
    seen, out = set(), []
    for o in objs:
        name = o["name"].strip(" -*•.").lower()
        b = o["bbox_2d"]
        box = (b[0] * W_ / 1000, b[1] * H_ / 1000, b[2] * W_ / 1000, b[3] * H_ / 1000)
        if not name or box[2] <= box[0] or box[3] <= box[1] or (name, tuple(b)) in seen:
            continue
        seen.add((name, tuple(b)))
        out.append({"name": name, "box": [round(v, 1) for v in box]})
    return out


_maps = {}


def furniture_map(spot):
    if spot not in _maps:
        z = np.load(MAPS / f"{spot}.npz")
        _maps[spot] = (z["label"], [str(k) for k in z["keys"]])
    return _maps[spot]


def rests_on(spot, box):
    """Furniture key under the bottom of the box: the commonest label in the box's bottom strip
    (middle half of its width, lowest 15% of its height), else the first label straight below."""
    label, keys = furniture_map(spot)
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    c0, c1 = int(max(0, x1 + w / 4)), int(min(W_, max(x1 + 3 * w / 4, x1 + w / 4 + 1)))
    r0, r1 = int(max(0, y2 - max(4, 0.15 * h))), int(min(H_, y2 + 1))
    strip = label[r0:r1, c0:c1].ravel()
    strip = strip[strip >= 0]
    if len(strip):
        return keys[collections.Counter(strip.tolist()).most_common(1)[0][0]]
    col = int(min(W_ - 1, max(0, (x1 + x2) / 2)))
    for r in range(int(min(H_ - 1, y2)), int(min(H_, y2 + 40))):
        if label[r, col] >= 0:
            return keys[label[r, col]]
    return None


def seen_furniture(spot):
    label, keys = furniture_map(spot)
    ids, n = np.unique(label[label >= 0], return_counts=True)
    return {keys[i] for i, c in zip(ids, n) if c >= SEEN_PX}


def build_notes(W, dets, filing):
    """[(day, hhmm, rooms, {furniture key: [names]})] in the search.py notes format, plus counts."""
    stats = collections.Counter()
    out = []
    for day, t, rooms in W.patrol_plan():
        if not W.rendered(day, t):
            continue
        notes = collections.defaultdict(list)
        pics = [(s, f) for f, spots in W.furniture.items() if W.places[spots[0]]["room"] in rooms for s in spots]
        if filing == "camera":
            for s, f in pics:
                notes[f] += []
                for o in dets.get(f"{day}|{t}|{s}") or []:
                    notes[f].append(o["name"])
                    stats["listed"] += 1
        else:
            for s, f in pics:
                for k in seen_furniture(s):
                    if k in W.furniture:
                        notes[k] += []
                for o in dets.get(f"{day}|{t}|{s}") or []:
                    stats["listed"] += 1
                    k = rests_on(s, o["box"])
                    if k is None:
                        stats["no furniture under it"] += 1
                    elif k not in W.furniture:
                        stats["on furniture with no view (dropped)"] += 1
                    else:
                        notes[k].append(o["name"])
                        stats["filed"] += 1
                        stats["filed elsewhere than the camera's furniture"] += k != f
        merged = {k: list(dict.fromkeys(v))[:15] for k, v in notes.items()}
        stats["entries after merging"] += sum(len(v) for v in merged.values())
        out.append((day, t, rooms, merged))
    return out, stats


def load_dets():
    p = OUT / "detections.json"
    return json.loads(p.read_text()) if p.exists() else {}


def cmd_detect(W, n=None):
    OUT.mkdir(exist_ok=True)
    pics = patrol_pictures(W)
    if n:
        pics = random.Random(0).sample(pics, n)
    have = load_dets()
    todo = [p for p in pics if f"{p[0]}|{p[1]}|{p[2]}" not in have]
    print(f"{len(pics)} pictures, {len(todo)} to detect", flush=True)
    with cf.ThreadPoolExecutor(8) as ex:
        for i, (p, r) in enumerate(zip(todo, ex.map(lambda p: detect_one(W, *p), todo))):
            have[f"{p[0]}|{p[1]}|{p[2]}"] = r
            if i % 100 == 0:
                (OUT / "detections.json").write_text(json.dumps(have))
                print(f"  {i}/{len(todo)}", flush=True)
    (OUT / "detections.json").write_text(json.dumps(have))
    print("unparsed:", sum(v is None for v in have.values()), "of", len(have))


def cmd_check(W):
    """Placement scored with the truth ids (scoring only): the object id under most of the box's
    bottom strip in the snapshot's own id picture, and the furniture that object rests on."""
    from PIL import Image
    dets = load_dets()
    res = collections.Counter()
    for key, objs in dets.items():
        if not objs:
            continue
        day, t, s = key.split("|")
        day = int(day)
        p = W.picture(day, t, s)
        raw = json.loads((p.parent / "truth.json").read_text())["pictures"][s]["objects"]
        by_sid = {o["semantic_id"]: o["object"] for o in raw}
        ids = np.array(Image.open(p.with_name(f"{s}_ids.png")))
        st = W.states[(day, t)]["objects"]
        for o in objs:
            x1, y1, x2, y2 = [int(v) for v in o["box"]]
            reg = ids[max(0, y1):min(H_, y2 + 1), max(0, x1):min(W_, x2 + 1)].ravel()
            reg = [v for v in reg.tolist() if v in by_sid]
            if not reg:
                res["box shows no snapshot object"] += 1
                continue
            oid = by_sid[collections.Counter(reg).most_common(1)[0][0]]
            place = st[oid].get("place")
            if place not in W.places:
                res["object not on a place"] += 1
                continue
            true_f = W.fkey(place)
            res["scored"] += 1
            res["camera's furniture right"] += W.fkey(s) == true_f
            res["placed furniture right"] += rests_on(s, o["box"]) == true_f
            res["placed: none found"] += rests_on(s, o["box"]) is None
    print(json.dumps(res, indent=1))
    (OUT / "check.json").write_text(json.dumps(res, indent=1))
    for filing in ["camera", "placed"]:
        notes, stats = build_notes(W, dets, filing)
        print(filing, dict(stats))


def cmd_run(W, arms):
    qs = json.loads((search.OUT / "questions.json").read_text())
    dets = load_dets()
    for filing in arms:
        notes, stats = build_notes(W, dets, filing)

        def one(q):
            order, info = search.llm_order(W, q, notes, "vlm")
            order += [f for f in search.nearest_order(W, W.furniture_xz()[order[-1]] if order else search.entry_xy(W), order)]
            order = order[:search.MAX_LOOKS]
            looks, result = [], "not found"
            for f in order:
                yes = search.judge_truth(W, q, f)
                looks.append({"f": f, "said": yes, "there": search.present(W, q, f)})
                if yes:
                    result = "found" if search.present(W, q, f) else "false find"
                    break
            return {"id": q["id"], "result": result, "looks": len(looks), "trace": looks, "order": order}
        with cf.ThreadPoolExecutor(8) as ex:
            rows = list(ex.map(one, qs))
        (OUT / f"run_{filing}.json").write_text(json.dumps(rows, indent=1))
        print(filing, dict(stats), json.dumps(search.summarise(qs, rows)["all"]), flush=True)


def cmd_report():
    qs = json.loads((search.OUT / "questions.json").read_text())
    base = {r["id"]: r for r in json.loads((search.OUT / "run_llm__vlm__truth.json").read_text())}
    perfect = {r["id"]: r for r in json.loads((search.OUT / "run_llm__truth__truth.json").read_text())}
    arms = {"own notes (84% arm)": base, "complete notes": perfect}
    for f in sorted(OUT.glob("run_*.json")):
        arms[f.stem[4:]] = {r["id"]: r for r in json.loads(f.read_text())}
    cats = ["all", "moved since", "at last sighting", "never seen"]
    print("| notes | " + " | ".join(cats) + " |")
    for name, rows in arms.items():
        cells = []
        for c in cats:
            ids = [q["id"] for q in qs if c == "all" or q["category"] == c]
            cells.append(f"{sum(rows[i]['result'] == 'found' for i in ids)}/{len(ids)}")
        print(f"| {name} | " + " | ".join(cells) + " |")
    from math import comb
    def mcnemar(a, b):
        n = a + b
        return min(1.0, 2 * sum(comb(n, k) for k in range(0, min(a, b) + 1)) / 2 ** n) if n else 1.0
    for x, y in [("placed", "camera"), ("placed", "own notes (84% arm)"), ("camera", "own notes (84% arm)")]:
        if x in arms and y in arms:
            a = sum(arms[x][i]["result"] == "found" and arms[y][i]["result"] != "found" for i in arms[x])
            b = sum(arms[y][i]["result"] == "found" and arms[x][i]["result"] != "found" for i in arms[x])
            print(f"{x} vs {y}: {a} vs {b}, p = {mcnemar(a, b):.3f}")


if __name__ == "__main__":
    W = World()
    cmd = sys.argv[1]
    if cmd == "detect":
        cmd_detect(W, int(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif cmd == "check":
        cmd_check(W)
    elif cmd == "run":
        cmd_run(W, sys.argv[2:])
    elif cmd == "report":
        cmd_report()
