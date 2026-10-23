"""Object instances from the picture memory: which physical things the dog has seen, where they are on the map,
when it saw them, and how likely each is still there.

    python3 go2/lab_agent/memory_instances.py ranges       # ask the vision model how far each object is (once per picture)
    python3 go2/lab_agent/memory_instances.py build        # sightings -> instances -> data/lab_agent/instances/instances.json
    python3 go2/lab_agent/memory_instances.py show backpack

1. Sightings. Every object in a picture's description (not clutter: memory.CLUTTER) is a sighting: its canonical
   name (memory.canon) and colour, the camera pose, the bearing from its place across the picture
   (memory.bearing_line, camera 73 deg wide) and a distance from the local vision model (asked once per picture,
   `ranges`). Bearing + distance give a rough map point for each sighting.
2. Instances. Within each day, sightings with the same name and a compatible colour are grouped greedily, oldest
   first: a sighting joins the nearest instance whose position is within JOIN_M (+ a share of the distance guess,
   which grows with range); otherwise it starts a new instance. Instances on different days are linked, not merged
   ("earlier"), because map poses shift between days and cross-day grouping mixed different things. An instance's position is the crossing of its sight lines when they
   come from directions at least 15 deg apart (as locate does), else the median of its sighting points.
3. Negative evidence. A picture "covers" an instance when the instance lies inside its field of view (73 deg,
   with a 5 deg margin cut off each edge), between 0.5 m and COVER_MAX_M, and the saved map has no wall or furniture
   on the straight line between them. A covering picture that lists no object of that name (and colour) is a miss.
4. P(still there). A persistence model (Rosen et al., ICRA 2016, simplified): with no misses, the chance an
   object is still where it was last seen decays exponentially with time since it was last seen, at a rate per
   kind of thing (HALF_LIFE_H: a backpack moves within hours, a sofa stays for months). Each later miss is
   evidence it has gone: it multiplies the odds by L = 1 - COVER_TRUE * DESCRIBE_RECALL[kind] (at most a factor
   MIN_MISS_LR; COVER_TRUE_LATER_DAY for a miss on a later day than the last sighting): a miss means little for a kind the describer often leaves out (podium, tape) and more for one it
   nearly always names (backpack, fire extinguisher). Misses within one 10-minute visit count once. Sightings
   after the misses reset the clock.
   p = prior * L^misses / (prior * L^misses + (1 - prior)), prior = 0.5^(hours since last seen / half-life).
   The half-lives are guesses, written down so they can be fitted once there are staged moves.

Map poses can be off by 1-2 m when the localizer jumps, and 2026-10-19 trail frames taken before 16:54 have worse
poses (the map was fixed then): their sightings are kept but weighted down (POSE_W) when positions are averaged.
Stored in go2/data/lab_agent/instances/: ranges.jsonl (distance guesses) and instances.json (rebuilt each time).
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import memory as M

INST = M.DATA / "instances"
RANGES = INST / "ranges.jsonl"
OUT = INST / "instances.json"
MAP_FIX_T = datetime(2026, 10, 19, 16, 54).timestamp()   # trail poses before this are worse (README)

JOIN_M = 1.5          # same thing if the points are this close (+ JOIN_FRAC of the distance guess); NOTES.md
JOIN_FRAC = 0.35
JOIN_BIG_M = 2.0
BIG = {"sofa", "bookshelf", "whiteboard", "television", "fridge", "printer", "water cooler", "appliance", "podium",
       "microwave", "workbench", "server rack"}
COVER_MIN_M, COVER_MAX_M = 0.5, 3.5
SMALL = {"phone", "cup", "key", "mouse", "bottle", "screw", "tool", "tape", "keyboard", "jug", "plant", "shoe"}
SMALL_MAX_M = 2.0     # a small thing further than this is easily missed by the description
EDGE_DEG = 5.0
# How often the describer lists a thing of this kind when it is plainly in the picture (hand-labelled search eval,
# memory_notes/search_eval/labels.json; an upper bound, the pools came partly from word search).
DESCRIBE_RECALL = {"backpack": 1.0, "computer tower": 0.95, "water cooler": 0.47, "appliance": 0.47,
                   "fire extinguisher": 0.96, "sofa": 1.0, "bucket": 0.97, "tripod": 0.97, "printer": 0.94,
                   "laptop": 0.91, "jacket": 0.97, "podium": 0.24, "television": 0.85, "whiteboard": 0.47,
                   "vacuum cleaner": 0.90, "microwave": 0.62, "fridge": 0.82, "trash can": 0.87, "shoe": 0.62,
                   "bottle": 1.0, "plant": 1.0, "broom": 1.0, "case": 1.0, "phone": 0.67, "tape": 0.12, "cup": 1.0}
DEFAULT_RECALL = 0.8
COVER_TRUE = 0.45     # chance a picture the geometry says covers the spot really shows it (pose error, occlusion
COVER_TRUE_LATER_DAY = 0.15  # by things not on the map); measured on static objects, 0.48 same day, 0.14 on a
                             # later day (map poses differ between walks), see NOTES.md
VISIT_MIN = 10
MIN_MISS_LR = 0.3     # one miss never counts for more than this (the describer and the poses both err)
POSE_W = {"good": 1.0, "pre_fix": 0.3}
MAX_PER_PICTURE = 4   # a picture listing more of one kind than this lists them along an edge, not one by one
DIST_SCALE = 0.8      # Qwen's distances run ~25% long against sight-line crossings (NOTES.md)
HALF_LIFE_H = {       # hours until P(still there) falls to 0.5 with no new evidence (guesses; see NOTES.md)
    "backpack": 8, "bag": 8, "paper bag": 8, "tote bag": 8, "plastic bag": 8, "jacket": 12, "clothing": 12,
    "laptop": 6, "phone": 2, "cup": 12, "bottle": 24, "shoe": 24, "key": 6, "mouse": 72, "keyboard": 240,
    "tool": 24, "screw": 24, "tape": 24, "camera": 48, "tripod": 72, "robot": 48, "robot arm": 720,
    "case": 72, "storage bin": 168, "basket": 168, "bucket": 168, "mop": 168, "broom": 168,
    "vacuum cleaner": 168, "trash can": 336, "plant": 720, "computer tower": 720, "printer": 2160,
    "fire extinguisher": 2160, "sofa": 2160, "bookshelf": 2160, "whiteboard": 4320, "television": 4320,
    "water cooler": 2160, "fridge": 2160, "microwave": 2160, "podium": 720, "appliance": 720}
DEFAULT_HALF_LIFE_H = 48
COLOURS = ["black", "white", "grey", "silver", "red", "orange", "yellow", "green", "teal", "blue", "purple", "pink",
           "brown", "beige", "wood", "transparent", "clear", "gold", "dark", "light", "cream"]
SAME_COLOUR = {"gray": "grey", "silver": "grey", "cream": "white", "beige": "white", "clear": "transparent",
               "wood": "brown", "wooden": "brown", "tan": "brown", "navy": "blue", "teal": "blue",
               "maroon": "red", "dark red": "red"}


# ---- 1. sightings ----

def kept(o):
    return M.canon(o["name"]) not in M.CLUTTER


def ask_ranges(r):
    """The vision model's distance to each kept object in picture r: {object index: metres, or None if it says the
    object is not really there}. One answer per object, each with a short reason first (asked together, without
    the reason, it gave every object the same distance)."""
    objs = [(i, o) for i, o in enumerate(r["seen"]["objects"]) if kept(o)]
    if not objs:
        return {}
    item = {"type": "object", "properties": {
        "where": {"type": "string", "maxLength": 120}, "visible": {"type": "boolean"},
        "metres": {"type": "number", "minimum": 0.2, "maximum": 15}}, "required": ["where", "visible", "metres"]}
    schema = {"type": "object", "properties": {f"o{i}": item for i, _ in objs}, "required": [f"o{i}" for i, _ in objs]}
    listing = "\n".join(f"o{i}: {o['colour']} {o['name']} ({o['on']}, centre at {o['across']:.2f} across)"
                        for i, o in objs)
    ask = ("A picture from a robot dog's camera, 0.4 m above the floor, about 73 degrees wide (a wide lens: things "
           "look smaller and further than they are), in a robotics lab. These objects were listed in it "
           "(across: 0 = left edge, 1 = right edge):\n" + listing +
           "\nFor each one: where: say in a few words where it is and what it stands on; visible: is it really in "
           "the picture; metres: how far it is from the camera along the floor. Objects at different depths must "
           "get different distances. Judge from where it meets the floor (lower in the picture = closer), its size, "
           "and the furniture around it (a desk is about 0.75 m tall and 0.7 m deep, an office chair 0.65 m wide).")
    a = M.ask_vlm(ask, [Path(r["path"]).read_bytes()], schema, 300 + 90 * len(objs))
    return {i: (a[f"o{i}"]["metres"] if a[f"o{i}"]["visible"] else None) for i, _ in objs}


def load_ranges():
    if not RANGES.exists():
        return {}
    out = {}
    for l in RANGES.read_text().splitlines():
        if l.strip():
            d = json.loads(l)
            out[d["id"]] = {int(k): v for k, v in d["ranges"].items()}
    return out


_W = threading.Lock()


def update_ranges(recs=None, workers=4):
    """Ask for distances in every described picture not asked yet. Returns (done, failed)."""
    have = load_ranges()
    todo = [r for r in (recs if recs is not None else M.load())
            if r.get("seen") and r["id"] not in have and r.get("x") is not None and any(kept(o) for o in r["seen"]["objects"])]
    INST.mkdir(parents=True, exist_ok=True)

    def one(r):
        for _ in range(3):
            try:
                rg = ask_ranges(r)
                with _W, RANGES.open("a") as f:
                    f.write(json.dumps({"id": r["id"], "ranges": rg}) + "\n")
                return True
            except Exception as e:  # noqa: BLE001 - model restarting: wait and retry
                err = e
                __import__("time").sleep(20)
        print(f"ranges failed for {r['id']}: {err}", file=sys.stderr, flush=True)   # stdout is the MCP channel
        return False
    with ThreadPoolExecutor(workers) as pool:
        ok = sum(pool.map(one, todo))
    return ok, len(todo) - ok


def colour_key(c):
    """The colour words of a description, coarsened: 'dark grey' -> 'grey', 'black and grey' -> 'black grey';
    '' if none is named. Two colours match when they share a word (colours_match)."""
    c = " " + c.lower().replace("-", " ").replace("/", " ") + " "
    for k, v in SAME_COLOUR.items():
        c = c.replace(f" {k} ", f" {v} ")
    found = {SAME_COLOUR.get(w, w) for w in c.split() if w in COLOURS and w not in ("dark", "light")}
    return " ".join(sorted(found))


def pose_quality(r):
    return "pre_fix" if r["source"] == "trail" and r["t"] < MAP_FIX_T else "good"


def sightings(recs=None, rng=None):
    rng = load_ranges() if rng is None else rng
    out = []
    for r in recs if recs is not None else M.load():
        if not r.get("seen") or r.get("x") is None or r.get("yaw_deg") is None:
            continue
        count = {}
        for o in r["seen"]["objects"]:
            count[M.canon(o["name"])] = count.get(M.canon(o["name"]), 0) + 1
        for i, o in enumerate(r["seen"]["objects"]):
            if not kept(o) or count[M.canon(o["name"])] > MAX_PER_PICTURE:   # "16 bottles" along an edge: an artefact
                continue
            d = rng.get(r["id"], {}).get(i, "unasked")
            if d is None:                      # the model said it is not really visible
                continue
            b = math.radians(M.bearing_line(r, o["across"]))
            s = {"id": r["id"], "key": f"{r['id']}:{i}", "t": r["t"], "name": M.canon(o["name"]), "colour": o["colour"],
                 "ckey": colour_key(o["colour"]), "on": o["on"], "across": o["across"],
                 "cx": r["x"], "cy": r["y"], "b": b, "d": None if d == "unasked" else d * DIST_SCALE,
                 "pose": pose_quality(r)}
            if s["d"] is not None:
                s["px"], s["py"] = r["x"] + s["d"] * math.cos(b), r["y"] + s["d"] * math.sin(b)
            out.append(s)
    return out


# ---- 2. instances ----

def colours_match(a, b):
    return not a or not b or bool(set(a.split()) & set(b.split()))


def crossing(ss):
    """Weighted least-squares crossing of sight lines; sightings whose line misses the point by much more than the
    others are dropped (two rounds). Returns (x, y, residuals, kept sightings) or None."""
    import numpy as np
    keep = list(ss)
    for _ in range(3):
        if len(keep) < 2:
            return None
        base = max(math.hypot(s["cx"] - t["cx"], s["cy"] - t["cy"]) for s in keep for t in keep)
        spread = max(abs(math.degrees(math.remainder(s["b"] - t["b"], 2 * math.pi))) for s in keep for t in keep)
        if base < 0.5 or spread < 15:              # cameras too close together, or lines nearly parallel
            return None
        A, v = np.zeros((2, 2)), np.zeros(2)
        for s in keep:
            u = np.array([math.cos(s["b"]), math.sin(s["b"])])
            P = np.eye(2) - np.outer(u, u)
            A += POSE_W[s["pose"]] * P
            v += POSE_W[s["pose"]] * P @ np.array([s["cx"], s["cy"]])
        if abs(np.linalg.det(A)) < 1e-3:
            return None
        p = np.linalg.solve(A, v)
        res = [abs((p[0] - s["cx"]) * math.sin(s["b"]) - (p[1] - s["cy"]) * math.cos(s["b"])) for s in keep]
        ahead = [(p[0] - s["cx"]) * math.cos(s["b"]) + (p[1] - s["cy"]) * math.sin(s["b"]) > 0.2 for s in keep]
        cut = max(0.75, 2.5 * statistics.median(res))
        bad = [s for s, r, a in zip(keep, res, ahead) if r > cut or not a]
        if not bad:
            return float(p[0]), float(p[1]), res, keep
        keep = [s for s in keep if s not in bad]
    return None


def position(ss):
    """(x, y, uncertainty m, how) from sightings: sight-line crossing if the cameras were at least 0.5 m apart and
    the directions differ by 15 deg or more, else the weighted median of the distance-guess points."""
    c = crossing(ss) if len(ss) >= 2 else None
    if c and len(c[3]) >= max(2, len(ss) // 2):
        x, y, res, kept_ = c
        unc = max(0.3, 2 * statistics.median(res))
        return x, y, round(unc, 2), f"crossing of {len(kept_)} of {len(ss)} sight lines"
    pts = [s for s in ss if s.get("px") is not None]
    if not pts:
        return None, None, None, "no distance"
    x, y = statistics.median(s["px"] for s in pts), statistics.median(s["py"] for s in pts)
    spread = statistics.median([math.hypot(s["px"] - x, s["py"] - y) for s in pts]) if len(pts) > 1 else 0
    unc = max(spread, 0.4 * statistics.median(s["d"] for s in pts))      # one direction: the distance guess dominates
    return x, y, round(unc, 2), "distance guess"


def join_radius(name, d):
    """How far a sighting's point may be from an instance's to be the same thing. Map poses differ by 1-2 m
    between walks, so this is wide; big furniture gets more (its distance guesses spread along its length)."""
    return (JOIN_BIG_M if name in BIG else JOIN_M) + JOIN_FRAC * d


def group(ss):
    """Greedy grouping, oldest first: a sighting joins the nearest instance of the same name (and a matching
    colour, except for BIG kinds, whose colour the describer names inconsistently: the sofa is black, brown or
    dark brown) within join_radius; otherwise it starts a new one. Returns a list of instances (lists of
    sightings)."""
    insts = []
    for s in sorted(ss, key=lambda s: s["t"]):
        if s.get("px") is None:
            continue
        best = None
        for inst in insts:
            h = inst["head"]
            if h["name"] != s["name"] or not (s["name"] in BIG or colours_match(h["ckey"], s["ckey"])):
                continue
            if any(t["id"] == s["id"] for t in inst["ss"]):     # two of a kind in one picture are two things
                continue
            dist = math.hypot(inst["x"] - s["px"], inst["y"] - s["py"])
            if dist <= join_radius(s["name"], s["d"]) and (best is None or dist < best[0]):
                best = (dist, inst)
        if best:
            inst = best[1]
            inst["ss"].append(s)
            if not inst["head"]["ckey"]:
                inst["head"] = s
            w = sum(POSE_W[t["pose"]] for t in inst["ss"])
            inst["x"] = sum(POSE_W[t["pose"]] * t["px"] for t in inst["ss"]) / w
            inst["y"] = sum(POSE_W[t["pose"]] * t["py"] for t in inst["ss"]) / w
        else:
            insts.append({"head": s, "ss": [s], "x": s["px"], "y": s["py"]})
    return [i["ss"] for i in insts]


# ---- 3. negative evidence ----

_GRID = {}


def grid():
    """The console's saved map (nav_proto.Grid), for line-of-sight checks and route lengths; None if unreachable.
    Only GETs /map.png and /state.json (read-only)."""
    if "g" not in _GRID:
        try:
            import io
            import sys
            import numpy as np
            from PIL import Image
            sys.path.insert(0, str(M.ROOT / "console"))
            import nav_proto as N
            png = M.get_bytes("/map.png", 10)
            meta = M.get_json("/state.json", 10)["map"]
            G = N.Grid(np.array(Image.open(io.BytesIO(png)).convert("L")), meta)
            INST.mkdir(parents=True, exist_ok=True)
            (INST / "map.png").write_bytes(png)
            (INST / "map_meta.json").write_text(json.dumps(meta))
        except Exception:  # noqa: BLE001 - console off: the last saved copy
            try:
                import sys
                import numpy as np
                from PIL import Image
                sys.path.insert(0, str(M.ROOT / "console"))
                import nav_proto as N
                G = N.Grid(np.array(Image.open(INST / "map.png").convert("L")),
                           json.loads((INST / "map_meta.json").read_text()))
            except Exception:  # noqa: BLE001
                G = None
        _GRID["g"] = G
    return _GRID["g"]


def clear_line(G, x0, y0, x1, y1):
    """No occupied map cell between the camera and the thing (the last 0.4 m, the thing and what it stands on,
    do not count)."""
    if G is None:
        return True
    n = int(math.hypot(x1 - x0, y1 - y0) / 0.05) + 1
    for k in range(n):
        f = k / max(1, n - 1)
        if math.hypot((x1 - x0) * (1 - f), (y1 - y0) * (1 - f)) < 0.4:
            return True
        i, j = G.cell(x0 + f * (x1 - x0), y0 + f * (y1 - y0))
        if 0 <= i < G.H and 0 <= j < G.W and G.occ[i, j]:
            return False
    return True


def covers(r, x, y, G=None, small=False):
    """Would picture r show a thing at map (x, y)? In the field of view, in range, nothing on the map in between."""
    if r.get("x") is None or r.get("yaw_deg") is None or abs(r.get("look_deg") or 0) > 10:
        return False
    d = math.hypot(x - r["x"], y - r["y"])
    if not COVER_MIN_M <= d <= (SMALL_MAX_M if small else COVER_MAX_M):
        return False
    off = math.degrees(math.remainder(math.atan2(y - r["y"], x - r["x"]) - math.radians(r["yaw_deg"]), 2 * math.pi))
    if abs(off) > M.HFOV / 2 - EDGE_DEG:
        return False
    return clear_line(G, r["x"], r["y"], x, y)


def same_kind(a, b):
    """'backpack' and 'bag' are the same kind for negative evidence (the describer uses both for one thing)."""
    return a == b or M.KIND.get(a) == b or M.KIND.get(b) == a or (M.KIND.get(a) and M.KIND.get(a) == M.KIND.get(b))


def lists(r, name, ckey):
    """Does picture r's description name a thing of this kind (and a compatible colour) anywhere in it?"""
    return any(same_kind(M.canon(o["name"]), name) and colours_match(ckey, colour_key(o["colour"]))
               for o in (r.get("seen") or {}).get("objects", []))


# ---- 4. P(still there) ----

def miss_lr(name, later_day=False):
    """Odds factor for one miss: P(not listed | still there) / P(not listed | gone) = 1 - cover * recall."""
    cover = COVER_TRUE_LATER_DAY if later_day else COVER_TRUE
    return max(MIN_MISS_LR, 1 - cover * DESCRIBE_RECALL.get(name, DEFAULT_RECALL))


def p_still(name, hours_since_seen, misses_since, later_day_misses=0):
    """P(still where it was last seen): time decay times the evidence of the misses since then."""
    hl = HALF_LIFE_H.get(name, DEFAULT_HALF_LIFE_H)
    prior = 0.5 ** (max(0.0, hours_since_seen) / hl)
    odds = prior / max(1e-9, 1 - prior)
    odds *= miss_lr(name) ** (misses_since - later_day_misses) * miss_lr(name, True) ** later_day_misses
    return odds / (1 + odds)


def day(t):
    return datetime.fromtimestamp(t).date()


def visit(t):
    """Misses within one VISIT_MIN-minute window count once: pictures from one pass share the same pose error and
    the same view, so they are not independent evidence."""
    return day(t), int(t // (VISIT_MIN * 60))


def build(recs=None, now=None, save=True):
    recs = recs if recs is not None else M.load()
    now = now or __import__("time").time()
    G = grid()
    by = {r["id"]: r for r in recs}
    ss = sightings(recs)
    groups = [g for d in sorted({day(s["t"]) for s in ss}) for g in group([s for s in ss if day(s["t"]) == d])]
    described = sorted((r for r in recs if r.get("seen")), key=lambda r: r["t"])
    P = M.places()
    out = []
    for k, g in enumerate(groups):
        x, y, unc, how = position(g)
        if x is None:
            continue
        head = max(g, key=lambda s: bool(s["ckey"]))
        name, ckey = head["name"], head["ckey"]
        ids = sorted({s["id"] for s in g}, key=lambda i: by[i]["t"])
        first, last = by[ids[0]]["t"], by[ids[-1]]["t"]
        seen_ids = set(ids)
        cov = [r for r in described if r["id"] not in seen_ids and covers(r, x, y, G, name in SMALL)]
        miss = [r for r in cov if not lists(r, name, ckey)]
        miss_after = [r for r in miss if r["t"] > last]
        visits = sorted({visit(r["t"]) for r in miss_after})
        later = sum(v[0] != day(last) for v in visits)
        p = p_still(name, (now - last) / 3600, len(visits), later)
        colours = sorted({s["colour"] for s in g}, key=lambda c: -sum(s["colour"] == c for s in g))
        near = M.nearest_place(x, y, P)
        out.append({"key": f"{name.replace(' ', '_')}_{k}", "name": name, "colour": colours[0], "colours": colours[:4],
                    "on": statistics.mode([s["on"] for s in g]), "x": round(x, 2), "y": round(y, 2),
                    "uncertainty_m": unc, "how": how, "near_place": near[0], "near_place_m": near[1],
                    "first_seen": first, "last_seen": last, "first_time": M.clock(first), "last_time": M.clock(last),
                    "n_sightings": len(g), "n_pictures": len(ids), "pictures": ids,
                    "pose_quality": f"{sum(s['pose'] == 'good' for s in g)}/{len(g)} good",
                    "n_covered": len(cov), "n_missed": len(miss), "missed_after_last_seen": [r["id"] for r in miss_after],
                    "missed_visits": len(visits),
                    "p_still": round(p, 2)})
    link_days(out)
    out.sort(key=lambda i: (i["name"], -i["n_pictures"]))
    if save:
        INST.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"built": now, "built_time": M.clock(now), "n_pictures": len(recs),
                                   "n_sightings": len(ss), "instances": out}, indent=0))
    return out


def link_days(insts):
    """Instances are grouped within one day (map poses shift between walks and days, and grouping across days
    mixed different things: NOTES.md). Each is then linked to the nearest instance of the same name and colour
    on an earlier day within the join radius: probably the same thing, seen again. Adds "earlier"/"later" (keys),
    "chain" (the first instance's key) and "chain_first_time" (when the chain was first seen)."""
    by_t = sorted(insts, key=lambda i: i["first_seen"])
    for n, i in enumerate(by_t):
        best = None
        for j in by_t[:n]:
            if day(j["last_seen"]) >= day(i["first_seen"]) or j["name"] != i["name"]:
                continue
            if not (i["name"] in BIG or colours_match(colour_key(i["colour"]), colour_key(j["colour"]))):
                continue
            dist = math.hypot(i["x"] - j["x"], i["y"] - j["y"])
            if dist <= join_radius(i["name"], 1.0) and (best is None or (j["last_seen"], -dist) > best[0]):
                best = ((j["last_seen"], -dist), j)
        i["earlier"] = best[1]["key"] if best else None
        i["chain_first_time"] = best[1]["chain_first_time"] if best else i["first_time"]
        i["chain"] = best[1]["chain"] if best else i["key"]
        i["later"] = None
    keys = {i["key"]: i for i in insts}
    for i in by_t:
        if i["earlier"]:
            keys[i["earlier"]]["later"] = i["key"]       # the newest link wins: a chain is the latest per day
    days = {}
    for i in insts:
        days.setdefault(i["chain"], set()).add(day(i["last_seen"]))
    for i in insts:
        i["chain_days"] = [d.strftime("%a %m-%d") for d in sorted(days[i["chain"]])]


def load_instances():
    return json.loads(OUT.read_text())["instances"] if OUT.exists() else []


_BG = {}


def fresh_instances(wait_new=8):
    """Instances, rebuilt first if pictures were described since the last build. Distances for at most wait_new of
    the newest unranged pictures are asked for now (about 25 s); the rest are asked in a background thread and
    count from the next call on."""
    recs = M.load()
    newest = max((r["t"] for r in recs if r.get("seen")), default=0)
    built = json.loads(OUT.read_text())["built"] if OUT.exists() else 0
    have = load_ranges()
    new = sorted((r for r in recs if r.get("seen") and r["id"] not in have and r.get("x") is not None
                  and any(kept(o) for o in r["seen"]["objects"])), key=lambda r: r["t"])
    if new:
        update_ranges(new[-wait_new:])
        rest = new[:-wait_new]
        if rest and not (_BG.get("t") and _BG["t"].is_alive()):
            _BG["t"] = threading.Thread(target=update_ranges, args=(rest,), daemon=True)
            _BG["t"].start()
    if new or newest > built:
        return build(recs)
    return load_instances()


def match(thing, insts):
    """Instances a request like 'grey backpack' or 'bag' could mean, newest of each chain only (an older day's
    instance linked to a newer one is the same thing seen before): (same colour, other colour). A name match
    ('backpack', 'tower') wins; the broader kind ('bag', 'computer') is used only when no name matches."""
    insts = [i for i in insts if not i.get("later")]
    q = set(M.words(thing))
    want = colour_key(thing)

    def by_name(i):
        nw = M.words(i["name"])
        return set(nw) <= q or nw[-1] in q

    hits = [i for i in insts if by_name(i)] or [i for i in insts if set(M.words(M.KIND.get(i["name"], "-"))) & q]
    same = [i for i in hits if colours_match(want, colour_key(i["colour"]))]
    other = [i for i in hits if i not in same]
    order = lambda i: (-day(i["last_seen"]).toordinal(), -i["n_pictures"])   # noqa: E731 - newest day, then most seen
    return sorted(same, key=order), sorted(other, key=order)


def path_lengths(G, start):
    """Plain route length (m) from start to every reachable cell over cells the planner may enter."""
    import heapq
    import numpy as np
    g = np.full(G.cost.shape, np.inf)
    g[start] = 0
    pq = [(0.0, start)]
    while pq:
        gc, (i, j) = heapq.heappop(pq)
        if gc > g[i, j]:
            continue
        for di, dj, L in ((-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1),
                          (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)):
            n = (i + di, j + dj)
            if G.ok(n) and gc + L * 0.05 < g[n]:
                g[n] = gc + L * 0.05
                heapq.heappush(pq, (g[n], n))
    return g


def route(x, y):
    """Where to stand to see map (x, y) and how far the dog would walk there, on the saved map, from where the
    console says the dog is now. Reads /state.json and /map.png only (no route request to the console).
    None if the console is off."""
    import sys
    import numpy as np
    G = grid()
    try:
        mp = M.get_json("/state.json", 5).get("map_pose")
    except Exception:  # noqa: BLE001
        return None
    if G is None or not mp:
        return None
    sys.path.insert(0, str(M.ROOT / "console"))
    import nav_proto as N
    start = G.nearest_ok(G.cell(mp["x"], mp["y"]))
    out = {"dog_at": {"x": round(mp["x"], 2), "y": round(mp["y"], 2)},
           "straight_m": round(math.hypot(x - mp["x"], y - mp["y"]), 1)}
    if start is None:
        return out
    stand = N.choose_stand(G, N.Grid.dijkstra(G, start), {"x": x, "y": y})
    if stand:
        L = path_lengths(G, start)[G.cell(stand["x"], stand["y"])]
        out["stand"] = {k: stand[k] for k in ("x", "y", "yaw_deg")}
        out["route_m"] = round(float(L), 1) if np.isfinite(L) else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ranges", "build", "show"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.cmd == "ranges":
        recs = M.load()
        if a.limit:
            have = load_ranges()
            recs = [r for r in recs if r["id"] not in have][: a.limit]
        print("ranges: %d asked, %d failed" % update_ranges(recs))
    elif a.cmd == "build":
        out = build()
        print(f"{len(out)} instances from {sum(i['n_sightings'] for i in out)} sightings")
    else:
        for i in load_instances():
            if not a.name or i["name"] == M.canon(a.name):
                print(f"{i['key']}: {i['colour']} {i['name']} at ({i['x']}, {i['y']}) +-{i['uncertainty_m']} ({i['how']}), "
                      f"{i['n_pictures']} pictures {i['first_time']} .. {i['last_time']}, covered {i['n_covered']}x, "
                      f"missed {i['n_missed']}x ({len(i['missed_after_last_seen'])} after), p_still {i['p_still']}")


if __name__ == "__main__":
    main()
