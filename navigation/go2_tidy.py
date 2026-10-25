"""Tidy the lab map automatically: propose corrected positions for saved places and labelled objects.

Oliver, 10-23: "i'd rather not have to do this by hand ... use the vision knowledge and camera views as
well as world knowledge common sense" (e.g. "the door should be lined up with the corners of the room").

Offline. Reads the map, the places, the objects and the camera trail of the mapping drive; writes only a
proposals file that a person accepts or rejects (never edits places/objects, never talks to the dog):

  1. room structure: in the room frame (map rotated by room_deg, so walls are axis-parallel) the
     dominant wall lines are projection-histogram peaks of the occupied cells whose 3-cell band holds long
     runs; the outermost long line on each side is an outer wall, the rest interior lines. Corners are
     where outer walls meet; gaps are wall-free stretches 0.6-2.2 m long (candidate doorways).
  2. poses: trail poses of the drive were logged before straightening; each frame's pose is corrected
     with the straightening model (delta(t) from <map>_straightened.info.json, odom from the pose log,
     re-integrated exactly like go2_straighten.corrected_poses).
  3. vision: each drive frame goes to Qwen3-VL once (answers cached). Door boxes: the centre and edge
     bearings are intersected with the fitted wall lines (the wall chosen by the box bottom's ground
     distance: camera CAM_H above the floor, level), then clustered along each wall over frames and
     snapped to a nearby corner (door edge DOOR_JAMB from the corner) or gap. Furniture boxes: rays
     across the box are cast over the occupied+mid cells (range-gated by the ground distance) and vote.
  4. furniture: for each place, a rectangle squared to the room axes with class size limits is fitted
     around its current target: score = filled cells - ALPHA * free cells + BETA * class votes
     - GAMMA * distance from the current target - overlap with rectangles already chosen. The stand spot
     is 0.8-1.0 m in front of a face, on free floor (planner clearance >= ROBOT_R), nearest to where the
     person put it; heading faces the target.
  5. checks: own rules (stand on free floor, doors on walls, nothing through the outer walls, no stand
     inside furniture) and a common-sense look by Qwen at a rendered room-frame map with the proposals.

  docker run --rm --net=host --entrypoint python3 -v /etc/localtime:/etc/localtime:ro \
      -v /home/nesl/oliver:/src -v /home/nesl/oliver/go2_maps:/maps -v <pics>:/out rosrobot \
      /src/go2_tidy.py --pics /out [--map /maps/lab_clean.grid.npz] [--dry-run]
"""
import argparse
import base64
import json
import math
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from go2_label import cast  # noqa: E402  (first occupied cell along map-frame bearings)

RES = 0.05                    # go2_mapper grid: m per cell, rows = y, origin = map xy of cell (0, 0)
OCC_SCORE, MID_OCC = 2, 3     # occupied: score >= 2; desk/table-top layer: mid >= 3
HFOV = math.radians(79)       # front camera: pinhole, centred, level
CAM_AHEAD, CAM_H = 0.33, 0.36  # camera ahead of the pose point / above the floor (m)
ROBOT_R, ROBOT_R_TIGHT = 0.28, 0.20   # planner clearance and its fallback (go2_nav)
HOST_UID = 1000
HOST_MAPS = "/home/nesl/oliver/go2_maps"

# walls
WALL_BAND = 1                 # cells each side of a line counted as the line
WALL_GAP_CLOSE = 0.25         # m: holes this short inside a run are closed
WALL_RUN_MIN = 0.6            # m: runs shorter than this don't count
WALL_LINE_MIN = 1.5           # m: a line needs this much run length in total
WALL_NMS = 0.35               # m: peaks closer than this are one line
OUTER_FRAC = 0.30             # outer wall: a line covering at least this share of the room's span
INNER_MIN, INNER_DENS = 2.5, 0.55   # interior line: at least this long (m) and this dense
GAP_RANGE = (0.6, 2.2)        # m: wall-free stretch that could be a doorway
# doors
DOOR_SNAP = 0.8               # m: allowed |ray length - ground distance| (plus 35 % of it)
DOOR_CLUSTER = 0.6            # m: along-wall clustering radius
DOOR_MIN_FRAMES = 2
DOOR_W = (0.8, 1.0)           # m: single door leaf width (doubles: 1.5-1.9)
DOOR_JAMB = 0.10              # m: door edge sits this far from a room corner
CORNER_SNAP = 1.2             # m: a door this near a corner (along the wall) gets lined up with it
STAND_DOOR = 0.8              # m in front of a door
# furniture: class -> (long side range, short side range) in m
SIZES = {"desk": ((1.2, 1.8), (0.6, 0.8)), "conference table": ((2.4, 4.0), (1.0, 1.5)),
         "sofa": ((1.6, 2.2), (0.8, 1.0)), "water cooler": ((0.3, 0.45), (0.3, 0.45)),
         "workbench": ((1.5, 2.4), (0.6, 0.9)), "podium": ((0.5, 0.9), (0.4, 0.7)),
         "cabinet": ((0.4, 1.2), (0.4, 0.6)), "table": ((0.8, 1.8), (0.6, 1.0)), "shelf": ((0.6, 1.8), (0.3, 0.5))}
BIG = {"conference table", "sofa", "workbench"}          # target = centre of the face the dog stands at
ALPHA = 1.0                   # rectangle score: free-floor share inside counts against it...
DELTA = 0.6                   # ...free floor in front of its best face counts for it...
FRONT_STRIP = (0.4, 1.0)      # ...in this strip beyond the face (m; chairs stand in the first 0.4 m)
BETA, VNORM = 0.4, 2.0        # camera votes for the class: bonus, saturating at VNORM per cell (3x3 summed)
GAMMA = 0.35                  # per metre from the saved target
KAPPA = 2.0                   # per share of cells already taken by another place's rectangle
MAX_SHARED = 0.10             # and no more than this share at all
SIZE_K = 0.15                 # per (relative) deviation from the middle of the class size range
SEARCH_R = 1.2                # m around the seed (saved places are 0.5-1 m off)
UNIQUE = {"sofa": 2.0, "conference table": 2.0, "water cooler": 2.0, "podium": 2.0, "workbench": 1.6}
UNIQUE_BETA = 1.2             # one-of-a-kind things the map can't tell apart: search wider, trust the camera more,
NOVOTE_PEN = 0.5              # and count it against a spot that no camera frame called that
STAND_D = (0.8, 0.9, 1.0)     # m in front of a face
MOVE_MIN = 0.15               # m: smaller changes are not proposed
# vision
VOCAB = ["door", "desk", "conference table", "table", "sofa", "cabinet", "shelf", "water cooler",
         "office chair", "whiteboard", "podium", "workbench", "person"]
SYN = {"couch": "sofa", "chair": "office chair", "drawers": "cabinet", "cabinet/drawers": "cabinet",
       "bookcase": "shelf", "bookshelf": "shelf", "shelf/bookcase": "shelf", "doorway": "door", "lectern": "podium",
       "work bench": "workbench", "dispenser": "water cooler", "water dispenser": "water cooler"}
SPECIFIC = ["conference table", "sofa", "water cooler", "podium", "workbench", "door", "cabinet", "shelf", "desk",
            "table", "whiteboard", "office chair", "person"]     # most specific first
VOTED = ["desk", "conference table", "table", "sofa", "cabinet", "shelf", "water cooler", "podium", "workbench"]
PROMPT = ("Photo from a small robot's camera, 0.36 m above the floor, in a university lab. Locate the "
          "following if clearly visible: door (a door leaf or an open doorway; box the whole door from its top "
          "down to where it meets the floor), desk, conference table, table, sofa, cabinet, shelf, water cooler, "
          "office chair, whiteboard, podium, workbench, person. One label per object, each object once, tight "
          "boxes, at most 12; do not list things that are not in the image. Answer with JSON only: "
          '[{"bbox_2d": [x1, y1, x2, y2], "label": "..."}]')
PROMPT_TAG = "tidy1"
# which class a place is, from its id / description
PLACE_CLASS = [("door", "door"), ("desk", "desk"), ("sofa", "sofa"), ("couch", "sofa"),
               ("conference", "conference table"), ("water", "water cooler"), ("cooler", "water cooler"),
               ("workbench", "workbench"), ("bench", "workbench"), ("podium", "podium"), ("cabinet", "cabinet"),
               ("table", "table")]
COL = {"desk": (40, 120, 230), "conference table": (30, 30, 200), "sofa": (150, 40, 160), "water cooler": (230, 60, 60),
       "workbench": (0, 150, 150), "podium": (0, 120, 0), "cabinet": (60, 140, 60), "table": (90, 180, 250),
       "shelf": (40, 200, 120), "door": (20, 60, 140)}


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def host_path(p):
    return HOST_MAPS + p[len("/maps"):] if p.startswith("/maps/") else p


# ---------------------------------------------------------------- map and room frame
def room_deg(score):
    """go2_mapper.Mapper.room_deg: the angle (mod 90, deg) at which occupied cells' projections are sharpest."""
    rc = np.argwhere(score >= OCC_SCORE)
    pts = (rc[:, ::-1] + np.random.default_rng(0).uniform(0, 1, rc.shape)) * RES
    best = None
    for d in np.arange(-45.0, 45.0, 0.5):
        a = math.radians(d)
        u = pts[:, 0] * math.cos(a) + pts[:, 1] * math.sin(a)
        v = -pts[:, 0] * math.sin(a) + pts[:, 1] * math.cos(a)
        sharp = sum(float((np.bincount(np.floor((w - w.min()) / RES).astype(int)) ** 2).sum()) for w in (u, v))
        if best is None or sharp > best[0]:
            best = (sharp, float(d))
    return best[1]


class Room:
    """Map arrays resampled into the room frame: u = x cos a + y sin a, v = -x sin a + y cos a (a = room_deg).
    Raster row i <-> v = v0 + (i + 0.5) RES, column j <-> u = u0 + (j + 0.5) RES."""

    def __init__(self, g, deg):
        self.a = math.radians(deg)
        self.origin = np.array(g["origin"], float)
        self.ca, self.sa = math.cos(self.a), math.sin(self.a)
        r, c = np.nonzero(g["seen"])
        u, v = self.to_room(self.origin[0] + (c + 0.5) * RES, self.origin[1] + (r + 0.5) * RES)
        self.u0, self.v0 = u.min() - 1.0, v.min() - 1.0
        self.nu, self.nv = int((u.max() + 1 - self.u0) / RES) + 1, int((v.max() + 1 - self.v0) / RES) + 1
        jj, ii = np.meshgrid(np.arange(self.nu), np.arange(self.nv))
        x, y = self.to_map(self.u0 + (jj + 0.5) * RES, self.v0 + (ii + 0.5) * RES)
        C = np.floor((x - self.origin[0]) / RES).astype(int)
        R = np.floor((y - self.origin[1]) / RES).astype(int)
        S = g["score"].shape
        self.ok = (R >= 0) & (R < S[0]) & (C >= 0) & (C < S[1])
        self.R, self.C = np.clip(R, 0, S[0] - 1), np.clip(C, 0, S[1] - 1)

    def to_room(self, x, y):
        return x * self.ca + y * self.sa, -x * self.sa + y * self.ca

    def to_map(self, u, v):
        return u * self.ca - v * self.sa, u * self.sa + v * self.ca

    def rot(self, arr):
        return np.where(self.ok, arr[self.R, self.C], 0).astype(arr.dtype)

    def ij(self, u, v):
        return int((v - self.v0) // RES), int((u - self.u0) // RES)

    def at(self, arr, u, v, default=0):
        i, j = self.ij(u, v)
        return arr[i, j] if 0 <= i < arr.shape[0] and 0 <= j < arr.shape[1] else default


def planner_clearance(occ5, seen5, k=2):
    """go2_nav._grid on the saved map alone: 0.1 m cells (any 5 cm cell occupied / seen), lone cells dropped,
    unknown blocks; distance (m) to the nearest blocked cell, returned on the 5 cm grid."""
    h, w = occ5.shape[0] // k, occ5.shape[1] // k
    occ = occ5[:h * k, :w * k].reshape(h, k, w, k).any(axis=(1, 3))
    known = seen5[:h * k, :w * k].reshape(h, k, w, k).any(axis=(1, 3))
    nb = cv2.filter2D(occ.astype(np.uint8), -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT)
    occ &= nb > 1
    d = cv2.distanceTransform((~(occ | ~known)).astype(np.uint8), cv2.DIST_L2, 5) * (k * RES)
    return np.repeat(np.repeat(d, k, 0), k, 1).astype(np.float32)


# ---------------------------------------------------------------- 1. walls
def runs_of(b, close, minlen):
    """[(start, end)] (cell index, end exclusive) of True runs after closing holes <= close cells."""
    b = b.copy()
    idx = np.flatnonzero(b)
    if len(idx) > 1:
        for p, q in zip(idx[:-1], idx[1:]):
            if 1 < q - p <= close + 1:
                b[p:q] = True
    out, k, n = [], 0, len(b)
    while k < n:
        if b[k]:
            j = k
            while j < n and b[j]:
                j += 1
            if j - k >= minlen:
                out.append((k, j))
            k = j
        else:
            k += 1
    return out


def fit_walls(rm, occ, seen):
    """Wall lines in the room frame: {axis 'u' (u = c, runs along v) or 'v' (v = c, runs along u), c, runs [(lo, hi)]
    in metres, len, lo, hi, outer: 'W'/'E'/'S'/'N' or None}."""
    lines = []
    for axis in ("u", "v"):
        O = occ if axis == "u" else occ.T            # columns of O = positions along the constant coordinate
        prof = cv2.GaussianBlur(O.sum(0).astype(np.float32).reshape(1, -1), (0, 0), 1.0).ravel()
        base = rm.u0 if axis == "u" else rm.v0
        along0 = rm.v0 if axis == "u" else rm.u0
        cand = []
        for k in range(1, len(prof) - 1):
            if prof[k] >= prof[k - 1] and prof[k] >= prof[k + 1] and prof[k] > 5:
                band = O[:, max(0, k - WALL_BAND):k + WALL_BAND + 1].any(1)
                rr = runs_of(band, int(WALL_GAP_CLOSE / RES), int(WALL_RUN_MIN / RES))
                tot = sum(b - a for a, b in rr) * RES
                # density: share of the run length where the line's own column is occupied
                dens = sum(O[a:b, k].sum() for a, b in rr) / max(1, sum(b - a for a, b in rr))
                if tot >= WALL_LINE_MIN:
                    cand.append((tot, k, rr, dens))
        cand.sort(key=lambda t: -t[0] * t[3])
        kept = []
        for tot, k, rr, dens in cand:
            if all(abs(k - k2) * RES >= WALL_NMS for _, k2, _, _ in kept):
                kept.append((tot, k, rr, dens))
        for tot, k, rr, dens in kept:
            runs = [(along0 + a * RES, along0 + b * RES) for a, b in rr]
            lines.append({"axis": axis, "c": base + (k + 0.5) * RES, "runs": runs, "len": tot, "dens": dens,
                          "lo": runs[0][0], "hi": runs[-1][1], "outer": None})
    # outer walls: the outermost long line on each side, among lines of the seen extent
    sv, su = np.nonzero(seen)
    span = {"u": (rm.u0 + su.min() * RES, rm.u0 + su.max() * RES), "v": (rm.v0 + sv.min() * RES, rm.v0 + sv.max() * RES)}
    for axis, (lo_s, hi_s) in (("u", ("W", "E")), ("v", ("S", "N"))):
        other = "v" if axis == "u" else "u"
        L = [ln for ln in lines if ln["axis"] == axis and ln["len"] >= OUTER_FRAC * (span[other][1] - span[other][0])]
        if L:
            min(L, key=lambda ln: ln["c"])["outer"] = lo_s
            max(L, key=lambda ln: ln["c"])["outer"] = hi_s
    # interior lines: only long, dense ones (desk rows and clutter make many weak ones)
    lines = [ln for ln in lines if ln["outer"] or (ln["len"] >= INNER_MIN and ln["dens"] >= INNER_DENS)]
    return lines, span


def room_box(lines):
    o = {ln["outer"]: ln["c"] for ln in lines if ln["outer"]}
    return o.get("W"), o.get("E"), o.get("S"), o.get("N")


def corners_and_gaps(lines, occ, rm):
    W, E, S, N = room_box(lines)
    corners = []
    for cu, nu_ in ((W, "W"), (E, "E")):
        for cv, nv_ in ((S, "S"), (N, "N")):
            if cu is not None and cv is not None:
                corners.append({"u": cu, "v": cv, "name": nv_ + nu_, "kind": "outer"})
    # interior lines meeting an outer wall make corners too (partition ends)
    for ln in lines:
        if ln["outer"]:
            continue
        for end in (ln["lo"], ln["hi"]):
            for o in lines:
                if o["outer"] and o["axis"] != ln["axis"] and abs(o["c"] - end) < 0.4 and o["lo"] - 0.3 <= ln["c"] <= o["hi"] + 0.3:
                    u, v = (ln["c"], o["c"]) if ln["axis"] == "u" else (o["c"], ln["c"])
                    corners.append({"u": u, "v": v, "name": "partition", "kind": "inner"})
    gaps = []
    for ln in lines:
        if not ln["outer"]:
            continue
        rs = ln["runs"]
        ext = (ln["lo"], ln["hi"])
        if ln["axis"] == "u":
            ext = (S if S is not None else ext[0], N if N is not None else ext[1])
        else:
            ext = (W if W is not None else ext[0], E if E is not None else ext[1])
        edges = [ext[0]] + [x for r in rs for x in r] + [ext[1]]
        for a, b in zip(edges[0::2], edges[1::2]):
            if GAP_RANGE[0] <= b - a <= GAP_RANGE[1]:
                gaps.append({"line": ln, "lo": a, "hi": b})
    return corners, gaps


# ---------------------------------------------------------------- 2. corrected poses of the drive frames
def drive_frames(maps, name, since, until):
    out = []
    root = os.path.join(maps, f"{name}_trail")
    for d in sorted(os.listdir(root)):
        try:
            with open(os.path.join(root, d, "index.jsonl")) as f:
                for line in f:
                    try:
                        p = json.loads(line)
                    except ValueError:
                        continue
                    if since <= p["t"] <= until:
                        out.append({"t": p["t"], "x": p["x"], "y": p["y"], "yaw": p["yaw"], "path": os.path.join(root, d, p["f"]),
                                    "url": f"/trail/{d}/{p['f']}"})
        except OSError:
            pass
    return sorted(out, key=lambda f: f["t"])


def correct_poses(frames, info_path, poselog, t0):
    """Each frame's pose moved like go2_straighten moved the track: delta(t) (deg, relative to the drive start t0)
    from the info file; odom from the pose log, increments rotated by -delta and re-integrated; the map pose of
    the frame shifts by (corrected - logged) track position at its time and turns by -delta."""
    info = json.load(open(info_path))
    tg = t0 + np.array(info["delta_deg"]["t"])
    dg = np.array(info["delta_deg"]["delta"])
    T = info["T"]
    L = [json.loads(s) for s in open(poselog)]
    L = [x for x in L if x.get("mapping") and x.get("odom") and t0 - 1 <= x["t"] <= frames[-1]["t"] + 2]
    ot = np.array([x["t"] for x in L])
    od = np.array([x["odom"] for x in L], float)
    ox, oy = od[:, 0], od[:, 1]
    delta = np.radians(np.interp(ot, tg, dg))
    dm = 0.5 * (delta[1:] + delta[:-1])
    dx, dy = np.diff(ox), np.diff(oy)
    cx = ox[0] + np.r_[0, np.cumsum(np.cos(-dm) * dx - np.sin(-dm) * dy)]
    cy = oy[0] + np.r_[0, np.cumsum(np.sin(-dm) * dx + np.cos(-dm) * dy)]
    c, s = math.cos(T[2]), math.sin(T[2])
    mox, moy = T[0] + c * ox - s * oy, T[1] + s * ox + c * oy
    mcx, mcy = T[0] + c * cx - s * cy, T[1] + s * cx + c * cy
    for f in frames:
        f["x0"], f["y0"], f["yaw0"] = f["x"], f["y"], f["yaw"]
        f["x"] += float(np.interp(f["t"], ot, mcx - mox))
        f["y"] += float(np.interp(f["t"], ot, mcy - moy))
        f["yaw"] = wrap(f["yaw"] - math.radians(float(np.interp(f["t"], tg, dg))))
        f["cx"], f["cy"] = f["x"] + CAM_AHEAD * math.cos(f["yaw"]), f["y"] + CAM_AHEAD * math.sin(f["yaw"])
    return (mcx, mcy), (mox, moy)


# ---------------------------------------------------------------- 3. vision
def ask(url, path, prompt, timeout=90, max_tokens=700, extra_images=()):
    imgs = [path] + list(extra_images)
    content = []
    for p in imgs:
        with open(p, "rb") as f:
            content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()}})
    content.append({"type": "text", "text": prompt})
    body = {"model": "qwen3-vl-8b", "temperature": 0, "max_tokens": max_tokens, "repetition_penalty": 1.05,
            "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(1 + attempt)
    print(f"  model failed on {path}: {err}")
    return None


def parse(txt):
    """[(label, x1, y1, x2, y2, weight)] in 0..1; boxes given 3+ labels dropped, 2 labels count half."""
    by_box = {}
    for m in re.finditer(r"\{[^{}]*\}", txt or ""):
        try:
            d = json.loads(m.group(0))
            x1, y1, x2, y2 = [min(max(float(v), 0), 1000) / 1000 for v in d["bbox_2d"]]
            lab = str(d["label"]).strip().lower()
        except (ValueError, KeyError, TypeError):
            continue
        lab = SYN.get(lab, lab)
        if lab not in VOCAB:
            continue
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        if x2 - x1 < 0.01 or y2 - y1 < 0.01:
            continue
        by_box.setdefault((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)), set()).add(lab)
    out = []
    for (x1, y1, x2, y2), labs in by_box.items():
        if len(labs) <= 2:
            out += [(lab, x1, y1, x2, y2, 1.0 / len(labs)) for lab in labs]
        else:   # the model walked the vocabulary on one box: keep its most specific label, weakly
            out.append((min(labs, key=SPECIFIC.index), x1, y1, x2, y2, 0.3))
    return out


def detect(frames, a):
    cache = {}
    if os.path.exists(a.cache):
        for line in open(a.cache):
            try:
                d = json.loads(line)
                cache[d["k"]] = d["txt"]
            except (ValueError, KeyError):
                pass
    key = lambda f: PROMPT_TAG + ":" + f["url"]
    todo = [f for f in frames if key(f) not in cache]
    print(f"vision: {len(frames) - len(todo)} frames cached, {len(todo)} to ask")
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (f, txt) in enumerate(zip(todo, ex.map(lambda f: ask(a.url, f["path"], PROMPT), todo))):
            if txt is None:
                continue
            cache[key(f)] = txt
            with open(a.cache, "a") as fh:
                fh.write(json.dumps({"k": key(f), "txt": txt}) + "\n")
            if (i + 1) % 40 == 0:
                print(f"  {i + 1}/{len(todo)} ({(time.time() - t0) / (i + 1):.2f} s/frame)")
    for f in frames:
        f["boxes"] = parse(cache.get(key(f)))


def cam_geom(W=640, H=360):
    fx = (W / 2) / math.tan(HFOV / 2)
    return W, H, fx


def bearing(xn, W, fx):
    """image x (0..1) -> bearing from the camera axis (rad, + = left)"""
    return math.atan((W / 2 - xn * W) / fx)


def ground_dist(yn, H, fx):
    """image row (0..1) of a floor point -> distance along the camera axis, or None above / at the horizon."""
    below = (yn - 0.5) * H
    return CAM_H * fx / below if below > 4 else None


# ---------------------------------------------------------------- doors
def ray_line(rm, cu, cv, du, dv, ln):
    """distance along the (room-frame) ray to the wall line, and the along-coordinate of the hit, or None."""
    if ln["axis"] == "u":
        if abs(du) < 1e-6:
            return None
        t = (ln["c"] - cu) / du
        along = cv + t * dv
    else:
        if abs(dv) < 1e-6:
            return None
        t = (ln["c"] - cv) / dv
        along = cu + t * du
    if t <= 0.3 or not (ln["lo"] - 0.4 <= along <= ln["hi"] + 0.4):
        return None
    return t, along


def door_observations(frames, rm, lines, occ_map, origin):
    W, H, fx = cam_geom()
    obs = []
    for fi, f in enumerate(frames):
        for lab, x1, y1, x2, y2, w in f["boxes"]:
            if lab != "door" or (y2 - y1) < 0.25:
                continue
            clipped = x1 < 0.02 or x2 > 0.98
            bc = bearing(0.5 * (x1 + x2), W, fx)
            yaw = f["yaw"] + bc
            cu, cv = rm.to_room(f["cx"], f["cy"])
            du, dv = rm.to_room(math.cos(yaw), math.sin(yaw))
            z = ground_dist(y2, H, fx) if y2 < 0.97 else None
            rg = z / math.cos(bc) if z else None
            hits = [(h, ln) for ln in lines for h in [ray_line(rm, cu, cv, du, dv, ln)] if h]
            if not hits:
                continue
            if rg:
                (t, along), ln = min(hits, key=lambda h: abs(h[0][0] - rg))
                if abs(t - rg) > DOOR_SNAP + 0.35 * rg:
                    continue
                how = "ground"
            else:
                # bottom not visible: the first obstacle along the ray, then the wall line nearest that hit
                hit = cast(occ_map, origin, f["cx"], f["cy"], np.array([yaw]), 6.0)[0]
                if hit is None:
                    continue
                rh = hit[2]
                (t, along), ln = min(hits, key=lambda h: abs(h[0][0] - rh))
                if abs(t - rh) > 0.6:
                    continue
                how = "raycast"
            width = None
            if not clipped:
                e = []
                for xn in (x1, x2):
                    yy = f["yaw"] + bearing(xn, W, fx)
                    eu, ev = rm.to_room(math.cos(yy), math.sin(yy))
                    h = ray_line(rm, cu, cv, eu, ev, dict(ln, lo=-1e9, hi=1e9))
                    if h:
                        e.append(h[1])
                if len(e) == 2:
                    width = abs(e[1] - e[0])
            # oblique views of a wall smear: weight by how square-on the ray meets the wall
            inc = abs(du) if ln["axis"] == "u" else abs(dv)
            obs.append({"frame": fi, "line": ln, "along": along, "t": t, "width": width, "how": how,
                        "w": w * (0.5 if clipped else 1.0) * (0.4 + 0.6 * inc) * (1.0 if how == "ground" else 0.6),
                        "box": (x1, y1, x2, y2)})
    return obs


def cluster_doors(obs, lines, corners, gaps, rm):
    doors = []
    for li, ln in enumerate(lines):
        O = [o for o in obs if o["line"] is ln]
        while O:
            # densest point (weighted count within DOOR_CLUSTER), then its members
            dens = [sum(p["w"] for p in O if abs(p["along"] - o["along"]) <= DOOR_CLUSTER) for o in O]
            seed = O[int(np.argmax(dens))]["along"]
            mem = [p for p in O if abs(p["along"] - seed) <= DOOR_CLUSTER]
            O = [p for p in O if p not in mem]
            frames = {p["frame"] for p in mem}
            if len(frames) < DOOR_MIN_FRAMES:
                continue
            wts = np.array([p["w"] for p in mem])
            al = np.array([p["along"] for p in mem])
            along = float(np.sum(wts * al) / wts.sum())
            wid = [p["width"] for p in mem if p["width"]]
            width = float(np.median(wid)) if wid else 0.9
            width = min(max(width, DOOR_W[0]), DOOR_W[1]) if width < 1.3 else min(max(width, 1.5), 1.9)
            d = {"line": ln, "along_meas": along, "along": along, "width": width, "frames": sorted(frames),
                 "obs": mem, "votes": float(wts.sum()), "spread": float(np.sqrt(np.sum(wts * (al - along) ** 2) / wts.sum())),
                 "snap": "measured"}
            # line up with a corner on this wall, or a gap in it
            best = None
            for c in corners:
                pc = c["v"] if ln["axis"] == "u" else c["u"]
                qc = c["u"] if ln["axis"] == "u" else c["v"]
                if abs(qc - ln["c"]) > 0.4:
                    continue
                if abs(along - pc) <= CORNER_SNAP:
                    sgn = 1.0 if along >= pc else -1.0
                    snapped = pc + sgn * (DOOR_JAMB + width / 2)
                    if best is None or abs(snapped - along) < abs(best[0] - along):
                        best = (snapped, c)
            for gp in gaps:
                if gp["line"] is ln and gp["lo"] - 0.3 <= along <= gp["hi"] + 0.3:
                    best = (0.5 * (gp["lo"] + gp["hi"]), {"name": "gap", "kind": "gap"})
                    d["width"] = min(max(gp["hi"] - gp["lo"], DOOR_W[0]), DOOR_W[1] if d["width"] < 1.3 else 1.9)
            if best is not None and abs(best[0] - along) < 1.0:
                d["along"] = best[0]
                d["snap"] = best[1]["kind"] + ":" + best[1]["name"]
            doors.append(d)
    # the same door seen on two near-parallel lines (thick walls): keep the stronger
    doors.sort(key=lambda d: -d["votes"])
    out = []
    for d in doors:
        u, v = door_uv(d)
        if all(math.hypot(u - door_uv(e)[0], v - door_uv(e)[1]) > 1.0 for e in out):
            out.append(d)
    return out


def door_uv(d):
    ln = d["line"]
    return (ln["c"], d["along"]) if ln["axis"] == "u" else (d["along"], ln["c"])


def inward_normal(ln, centre_uv, ref_uv=None):
    """unit normal (room frame) pointing from the wall line into the room (towards ref, else the room centre)."""
    ref = ref_uv if ref_uv is not None else centre_uv
    if ln["axis"] == "u":
        return (1.0 if ref[0] > ln["c"] else -1.0, 0.0)
    return (0.0, 1.0 if ref[1] > ln["c"] else -1.0)


# ---------------------------------------------------------------- furniture votes
def furniture_votes(frames, occ_map, origin, shape):
    W, H, fx = cam_geom()
    votes = np.zeros((len(VOTED),) + shape, np.float32)
    hits = []          # (frame, label index, row, col, w)
    for fi, f in enumerate(frames):
        mine = {}
        for lab, x1, y1, x2, y2, w in f["boxes"]:
            if lab not in VOTED:
                continue
            li = VOTED.index(lab)
            if x2 - x1 > 0.6:
                w *= 0.3                 # right in front: everything behind it votes too
            m = (x2 - x1) * 0.1
            b1, b2 = bearing(x1 + m, W, fx), bearing(x2 - m, W, fx)
            n = max(2, int(math.degrees(b1 - b2)) + 1)
            min_r, max_r = 0.0, 6.0
            z = ground_dist(y2, H, fx) if y2 < 0.97 else None
            if z:
                min_r, max_r = z / 2 - 0.5, min(max_r, 2 * z + 0.5)
            elif y2 <= 0.5:
                w *= 0.3
            for h in cast(occ_map, origin, f["cx"], f["cy"], f["yaw"] + np.linspace(b2, b1, n), max_r):
                if h is not None and h[2] >= min_r:
                    k = (li, h[0], h[1])
                    mine[k] = max(mine.get(k, 0), w)
        for (li, r, c), w in mine.items():
            votes[li, r, c] += w
            hits.append((fi, li, r, c, w))
    return votes, np.array(hits, np.float64).reshape(-1, 5)


# ---------------------------------------------------------------- 4. rectangles
def integral(a):
    return np.pad(a.astype(np.float64), ((1, 0), (1, 0))).cumsum(0).cumsum(1)


def box_sums(I, h, w):
    """sum over every h x w window (top-left anchored): array (nv - h + 1, nu - w + 1)"""
    return I[h:, w:] - I[:-h, w:] - I[h:, :-w] + I[:-h, :-w]


def rsum(I, i0, j0, h, w):
    """sums of h x w windows with top-left (i0, j0) (arrays), clipped to the raster; I from integral()."""
    N, M = I.shape[0] - 1, I.shape[1] - 1
    a, b = np.clip(i0, 0, N), np.clip(i0 + h, 0, N)
    c, d = np.clip(j0, 0, M), np.clip(j0 + w, 0, M)
    return I[b, d] - I[a, d] - I[b, c] + I[a, c]


def fit_rect(cls, seeds, rm, F, E, Vcls, taken, allowed):
    """best over several seeds (the saved target, and a person-confirmed object of the same name)"""
    fits = [fit_rect1(cls, sd, rm, F, E, Vcls, taken, allowed) for sd in seeds]
    fits = [f for f in fits if f]
    return max(fits, key=lambda f: f["score"]) if fits else None


def fit_rect1(cls, seed_uv, rm, F, E, Vcls, taken, allowed):
    """Best axis-aligned rectangle (room frame) of class cls near seed. Densities (0..1), so size is set by the
    class range and its nominal size, not by how much clutter a bigger box can swallow:
      fill - ALPHA free + DELTA front + BETA votes - GAMMA dist - KAPPA taken - SIZE_K size deviation
    front = free-floor share of the strip FRONT_STRIP beyond the best face (furniture is used from an aisle)."""
    (l0, l1), (s0, s1) = SIZES[cls]
    search, beta = UNIQUE.get(cls, SEARCH_R), UNIQUE_BETA if cls in UNIQUE else BETA
    IF, IE, IV, IT, IA = integral(F), integral(E), integral(Vcls), integral(taken), integral(~allowed)
    si, sj = rm.ij(*seed_uv)
    R = int(search / RES)
    f0, f1 = int(FRONT_STRIP[0] / RES), int(FRONT_STRIP[1] / RES)
    best = None
    sizes = set()
    for L in np.arange(l0, l1 + 1e-6, 0.1):
        for S in np.arange(s0, s1 + 1e-6, 0.05):
            sizes.add((round(L, 2), round(S, 2)))
            sizes.add((round(S, 2), round(L, 2)))
    Ln, Sn = (l0 + l1) / 2, (s0 + s1) / 2
    for du, dv in sizes:
        w, h = max(1, int(round(du / RES))), max(1, int(round(dv / RES)))
        n = float(w * h)
        ii, jj = np.mgrid[si - R - h // 2:si + R - h // 2 + 1, sj - R - w // 2:sj + R - w // 2 + 1]
        cu = rm.u0 + (jj + w / 2) * RES
        cv = rm.v0 + (ii + h / 2) * RES
        dist = np.hypot(cu - seed_uv[0], cv - seed_uv[1])
        fill, free = rsum(IF, ii, jj, h, w) / n, rsum(IE, ii, jj, h, w) / n
        vote, tk, out = rsum(IV, ii, jj, h, w) / n, rsum(IT, ii, jj, h, w) / n, rsum(IA, ii, jj, h, w) / n
        sq = abs(du - dv) < 0.25
        fronts = []
        if du >= dv or sq:      # faces at v +- (long side along u)
            fronts += [rsum(IE, ii + h + f0, jj, f1 - f0, w) / (w * (f1 - f0)), rsum(IE, ii - f1, jj, f1 - f0, w) / (w * (f1 - f0))]
        if dv > du or sq:
            fronts += [rsum(IE, ii, jj + w + f0, h, f1 - f0) / (h * (f1 - f0)), rsum(IE, ii, jj - f1, h, f1 - f0) / (h * (f1 - f0))]
        front = np.max(fronts, axis=0)
        L, S = max(du, dv), min(du, dv)
        sdev = 0.5 * (abs(L - Ln) / max(l1 - l0, 0.1) + abs(S - Sn) / max(s1 - s0, 0.1))
        sc = (fill - ALPHA * free + DELTA * front + beta * np.minimum(vote / VNORM, 1.0) - GAMMA * dist - KAPPA * tk
              - SIZE_K * sdev)
        if cls in UNIQUE:
            sc = sc - NOVOTE_PEN * (vote < 0.1 * VNORM)
        sc = np.where((out > 0.05) | (dist > search) | (tk > MAX_SHARED), -1e9, sc)
        k = np.unravel_index(int(np.argmax(sc)), sc.shape)
        if best is None or sc[k] > best["score"]:
            best = {"u": float(cu[k]), "v": float(cv[k]), "du": w * RES, "dv": h * RES, "score": float(sc[k]),
                    "fill": float(fill[k]), "free": float(free[k]), "front": float(front[k]), "votes": float(vote[k]),
                    "i": int(ii[k]), "j": int(jj[k]), "h": h, "w": w, "dist": float(dist[k]), "cls": cls}
    return best


def rect_mask(shape, r):
    m = np.zeros(shape, bool)
    m[r["i"]:r["i"] + r["h"], r["j"]:r["j"] + r["w"]] = True
    return m


def choose_stand(rect, rm, clr, orig_uv, big, allowed):
    """stand spot in front of a face of the rectangle: (score, (u, v), target (u, v), clearance, normal, note).
    First try STAND_D with clearance >= ROBOT_R; then up to 1.3 m out / ROBOT_R_TIGHT (noted, flagged)."""
    hu, hv = rect["du"] / 2, rect["dv"] / 2
    for dists, need, note in ((STAND_D, ROBOT_R, ""), (STAND_D + (1.1, 1.2, 1.3), ROBOT_R_TIGHT, "tight")):
        best = None
        for n, t, half in (((1, 0), (0, 1), hv), ((-1, 0), (0, 1), hv), ((0, 1), (1, 0), hu), ((0, -1), (1, 0), hu)):
            fc = (rect["u"] + n[0] * hu, rect["v"] + n[1] * hv)
            for s in np.arange(-0.6, 0.61, 0.15):
                if abs(s) > max(half - 0.1, 0):
                    continue
                for d in dists:
                    p = (fc[0] + t[0] * s + n[0] * d, fc[1] + t[1] * s + n[1] * d)
                    c = float(rm.at(clr, *p))
                    if c < need or not rm.at(allowed, *p):
                        continue
                    score = min(c, 0.6) - 0.3 * abs(s) - 0.5 * abs(d - 0.9)
                    if orig_uv is not None:
                        score -= 0.35 * math.hypot(p[0] - orig_uv[0], p[1] - orig_uv[1])
                    tgt = (fc[0] + t[0] * s, fc[1] + t[1] * s) if big else (rect["u"], rect["v"])
                    if best is None or score > best[0]:
                        best = (score, p, tgt, c, n, note)
        if best:
            return best
    return None


# ---------------------------------------------------------------- 5. common sense
def qwen_review(a, png, items):
    lines = [f'{it["n"]}: {it["what"]}' for it in items]
    prompt = ("This is a top-down occupancy map of one rectangular university lab room, drawn so the room's walls "
              "are horizontal and vertical. Grey/black = obstacles seen by a lidar (walls, furniture); light blue = "
              "table-top height; white = free floor. Thick red lines = fitted outer walls, green = gaps in them, dark red circles = room corners. "
              "Coloured rectangles are proposed furniture, each with a number; brown bars are proposed doors; arrows "
              "show where a robot dog would stand and which way it would face (it should stand on white floor, in "
              "front of the thing, facing it). 1 m grid.\nProposals:\n" + "\n".join(lines) +
              "\nUsing common sense about how labs are laid out (doors are in outer walls, often next to a corner; "
              "desks stand in rows against walls or back to back; furniture never sits inside a wall; only one "
              "of each unique item such as a sofa), list the proposals that look implausible. Answer with JSON "
              'only: [{"n": number, "verdict": "ok" | "suspect" | "wrong", "why": "short reason"}] covering every '
              "number.")
    txt = ask(a.url, png, prompt, timeout=180, max_tokens=1500)
    out = {}
    for m in re.finditer(r"\{[^{}]*\}", txt or ""):
        try:
            d = json.loads(m.group(0))
            out[int(d["n"])] = (str(d.get("verdict", "ok")).lower(), str(d.get("why", ""))[:200])
        except (ValueError, KeyError, TypeError):
            pass
    return out, txt


# ---------------------------------------------------------------- pictures
class Canvas:
    def __init__(self, rm, occ, mid, seen, span, scale=4, pad=0.5):
        self.rm, self.s = rm, scale
        (ua, ub), (va, vb) = span["u"], span["v"]
        self.ua, self.vb = ua - pad, vb + pad
        j0, j1 = int((ua - pad - rm.u0) / RES), int((ub + pad - rm.u0) / RES)
        i0, i1 = int((va - pad - rm.v0) / RES), int((vb + pad - rm.v0) / RES)
        img = np.full((i1 - i0, j1 - j0, 3), 205, np.uint8)
        img[seen[i0:i1, j0:j1]] = 255
        img[mid[i0:i1, j0:j1]] = (235, 200, 150)
        img[occ[i0:i1, j0:j1]] = (110, 110, 110)
        self.img = cv2.resize(img[::-1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        H, W = self.img.shape[:2]
        for k in range(int(math.ceil(self.ua)), int(ub + pad) + 1):        # 1 m grid
            cv2.line(self.img, (self.px(k, 0)[0], 0), (self.px(k, 0)[0], H), (225, 225, 225), 1)
        for k in range(int(math.ceil(va - pad)), int(self.vb) + 1):
            cv2.line(self.img, (0, self.px(0, k)[1]), (W, self.px(0, k)[1]), (225, 225, 225), 1)

    def px(self, u, v):
        return int(round((u - self.ua) / RES * self.s)), int(round((self.vb - v) / RES * self.s))

    def pxm(self, x, y):
        return self.px(*self.rm.to_room(x, y))

    def line(self, p, q, col, t=1):
        cv2.line(self.img, self.px(*p), self.px(*q), col, t, cv2.LINE_AA)

    def rect(self, r, col, t=2):
        cv2.rectangle(self.img, self.px(r["u"] - r["du"] / 2, r["v"] + r["dv"] / 2),
                      self.px(r["u"] + r["du"] / 2, r["v"] - r["dv"] / 2), col, t)

    def arrow(self, uv, ang_room, col, t=2, ln=0.45):
        p = self.px(*uv)
        q = self.px(uv[0] + ln * math.cos(ang_room), uv[1] + ln * math.sin(ang_room))
        cv2.arrowedLine(self.img, p, q, col, t, cv2.LINE_AA, tipLength=0.35)

    def text(self, uv, s, col=(0, 0, 0), sc=0.45, th=1):
        p = self.px(*uv)
        cv2.putText(self.img, s, (p[0] + 4, p[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, sc, (255, 255, 255), th + 2, cv2.LINE_AA)
        cv2.putText(self.img, s, (p[0] + 4, p[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, sc, col, th, cv2.LINE_AA)


def draw_walls(cv_, lines, corners, gaps, inner=False):
    for ln in lines:
        if not (ln["outer"] or inner):
            continue
        col, t = ((0, 0, 220), 3) if ln["outer"] else ((0, 150, 255), 1)
        for a, b in ln["runs"]:
            p, q = ((ln["c"], a), (ln["c"], b)) if ln["axis"] == "u" else ((a, ln["c"]), (b, ln["c"]))
            cv_.line(p, q, col, t)
    for c in corners:
        if c["kind"] != "outer" and not inner:
            continue
        cv2.circle(cv_.img, cv_.px(c["u"], c["v"]), 6, (0, 0, 160) if c["kind"] == "outer" else (0, 120, 220), 2)
    for gp in gaps:
        ln = gp["line"]
        p, q = ((ln["c"], gp["lo"]), (ln["c"], gp["hi"])) if ln["axis"] == "u" else ((gp["lo"], ln["c"]), (gp["hi"], ln["c"]))
        cv_.line(p, q, (0, 200, 0), 3)


# ---------------------------------------------------------------- main
def when(s):
    return time.mktime(time.strptime(s.strip().replace("T", " "), "%Y-%m-%d %H:%M:%S"))


def get_json(url, path, key=None):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            d = json.load(r)
    except Exception:  # noqa: BLE001  (console down: the file)
        try:
            d = json.load(open(path))
        except (OSError, ValueError):
            d = {}
    return d.get(key, []) if key else d


def place_class(pid, desc):
    s = (pid + " " + (desc or "")).lower()
    for k, c in PLACE_CLASS:
        if k in s:
            return c
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--maps", default="/maps")
    ap.add_argument("--name", default="lab")
    ap.add_argument("--map", default=None, help="grid npz (default: <maps>/<name>_clean.grid.npz if it exists, "
                    "else <maps>/<name>.grid.npz)")
    ap.add_argument("--since", default="2026-10-23 14:31:57", help="mapping drive start (local time); also t0 of delta(t)")
    ap.add_argument("--until", default="2026-10-23 14:44:30")
    ap.add_argument("--info", default=None, help="straightening info (default <maps>/<name>_straightened.info.json)")
    ap.add_argument("--poselog", default=None, help="default <maps>/<name>_poselog/<day of --since>.jsonl")
    ap.add_argument("--url", default="http://localhost:8000/v1/chat/completions")
    ap.add_argument("--console", default="http://localhost:8080")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cache", default="/out/qwen_tidy_cache.jsonl", help="model answers per frame (jsonl)")
    ap.add_argument("--pics", default=None, help="debug pictures directory")
    ap.add_argument("--out", default=None, help="default <maps>/<name>_proposals.json")
    ap.add_argument("--inner-doors", action="store_true", help="allow doors on interior lines too")
    ap.add_argument("--no-review", action="store_true", help="skip the model's common-sense look")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, don't write the proposals")
    a = ap.parse_args()
    t_start = time.time()

    path = a.map or next(p for p in (os.path.join(a.maps, f"{a.name}_clean.grid.npz"), os.path.join(a.maps, f"{a.name}.grid.npz"))
                         if os.path.exists(p))
    g = dict(np.load(path))
    if "mid" not in g:                       # a map without the desk-top layer: borrow the live map's
        base = np.load(os.path.join(a.maps, f"{a.name}.grid.npz"))
        g["mid"] = base["mid"] if np.allclose(base["origin"], g["origin"]) else np.zeros_like(g["score"])
    origin = np.array(g["origin"], float)
    occ_m = g["score"] >= OCC_SCORE
    mid_m = g["mid"] >= MID_OCC
    seen_m = g["seen"].astype(bool) | occ_m
    deg = room_deg(g["score"])
    rm = Room({"origin": origin, "seen": seen_m, "score": g["score"]}, deg)
    occ, mid, seen = rm.rot(occ_m), rm.rot(mid_m) & ~rm.rot(occ_m), rm.rot(seen_m)
    print(f"map {path}: room_deg {deg:.1f}, room raster {rm.nu}x{rm.nv}")

    # planner-like clearance: occupied (isolated cells dropped) or unknown blocks
    clr = rm.rot(planner_clearance(occ_m, g["seen"].astype(bool)))

    # 1. walls
    lines, span = fit_walls(rm, occ, seen)
    corners, gaps = corners_and_gaps(lines, occ, rm)
    Wb, Eb, Sb, Nb = room_box(lines)
    centre_uv = ((Wb + Eb) / 2 if Wb is not None and Eb is not None else 0, (Sb + Nb) / 2 if Sb is not None and Nb is not None else 0)
    print(f"walls: {len(lines)} lines, outer W {Wb} E {Eb} S {Sb} N {Nb}; {len(corners)} corners, {len(gaps)} gaps")
    for ln in sorted(lines, key=lambda l: -l["len"]):
        print(f"  {ln['axis']}={ln['c']:6.2f}  {ln['len']:.1f} m dens {ln['dens']:.2f} over {ln['lo']:.1f}..{ln['hi']:.1f}  {ln['outer'] or ''}")
    allowed = np.zeros_like(occ)          # interior of the outer walls (rectangles must stay inside)
    jW = int((Wb - rm.u0) / RES) + 1 if Wb is not None else 0
    jE = int((Eb - rm.u0) / RES) if Eb is not None else rm.nu
    iS = int((Sb - rm.v0) / RES) + 1 if Sb is not None else 0
    iN = int((Nb - rm.v0) / RES) if Nb is not None else rm.nv
    allowed[iS:iN, jW:jE] = True

    # 2. frames with corrected poses
    t0, t1 = when(a.since), when(a.until)
    frames = drive_frames(a.maps, a.name, t0, t1)
    day = time.strftime("%Y%m%d", time.localtime(t0))
    newtrack, oldtrack = correct_poses(frames, a.info or os.path.join(a.maps, f"{a.name}_straightened.info.json"),
                                       a.poselog or os.path.join(a.maps, f"{a.name}_poselog", day + ".jsonl"), t0)
    shift = [math.hypot(f["x"] - f["x0"], f["y"] - f["y0"]) for f in frames]
    occ_any = occ_m | mid_m
    good = []
    for f in frames:
        c, r = int((f["cx"] - origin[0]) // RES), int((f["cy"] - origin[1]) // RES)
        if not occ_m[r, c]:
            good.append(f)
    print(f"frames: {len(frames)} in the drive, {len(good)} with the camera on free floor; pose correction "
          f"median {np.median(shift):.2f} m, max {max(shift):.2f} m")
    frames = good

    # 3. vision
    detect(frames, a)
    nb_lab = {}
    for f in frames:
        for b in f["boxes"]:
            nb_lab[b[0]] = nb_lab.get(b[0], 0) + 1
    print("boxes:", dict(sorted(nb_lab.items(), key=lambda kv: -kv[1])))
    obs = door_observations(frames, rm, [ln for ln in lines if ln["outer"] or a.inner_doors], occ_any, origin)
    doors = cluster_doors(obs, lines, corners, gaps, rm)
    print(f"doors: {len(obs)} observations -> {len(doors)} doors")
    votes_m, hits = furniture_votes(frames, occ_any, origin, occ_m.shape)
    votes = np.stack([cv2.boxFilter(rm.rot(v), -1, (3, 3), normalize=False) for v in votes_m])

    # 4. places and objects
    places = get_json(a.console + "/places", os.path.join(a.maps, f"{a.name}.places.json"))
    objects = get_json(a.console + "/map/objects", os.path.join(a.maps, f"{a.name}_objects.json"), "objects")
    F = (occ | mid).astype(np.float32)
    E = (seen & ~occ & ~mid).astype(np.float32)
    taken = np.zeros(occ.shape, np.float32)
    results = {}       # place id -> dict

    confirmed = {o["name"]: rm.to_room(o["x"], o["y"]) for o in objects if o.get("name") and o.get("confirmed_by")}

    def seeds_of(pid, p):
        return [seed_of(p)] + ([confirmed[pid]] if pid in confirmed else [])

    def seed_of(p):
        tg = p.get("target")
        if tg:
            return rm.to_room(tg["x"], tg["y"])
        y = math.radians(p["yaw_deg"])
        return rm.to_room(p["x"] + 0.9 * math.cos(y), p["y"] + 0.9 * math.sin(y))

    # doors first
    door_used = set()
    for pid, p in places.items():
        if place_class(pid, p.get("description")) != "door":
            continue
        su = seed_of(p)
        cand = [(math.hypot(door_uv(d)[0] - su[0], door_uv(d)[1] - su[1]) - 0.1 * min(d["votes"], 5), k)
                for k, d in enumerate(doors) if k not in door_used]
        cand = [c for c in cand if c[0] < 2.5]
        if not cand:
            results[pid] = {"cls": "door", "fail": "no door detected within 2.5 m of the saved one"}
            continue
        _, k = min(cand)
        door_used.add(k)
        d = doors[k]
        du_ = door_uv(d)
        n = inward_normal(d["line"], centre_uv)
        stand, sd = None, None
        for dd in (STAND_DOOR, 0.9, 1.0, 0.7):
            for s in (0, 0.15, -0.15, 0.3, -0.3):
                t_ = (n[1], -n[0])
                q = (du_[0] + n[0] * dd + t_[0] * s, du_[1] + n[1] * dd + t_[1] * s)
                if rm.at(clr, *q) >= ROBOT_R:
                    stand, sd = q, (dd, s)
                    break
            if stand:
                break
        flags = []
        if stand is None:
            for dd in (STAND_DOOR, 0.9, 1.0, 1.1, 1.2):
                for s in (0, 0.15, -0.15, 0.3, -0.3):
                    t_ = (n[1], -n[0])
                    q = (du_[0] + n[0] * dd + t_[0] * s, du_[1] + n[1] * dd + t_[1] * s)
                    if rm.at(clr, *q) >= ROBOT_R_TIGHT:
                        stand, sd = q, (dd, s)
                        break
                if stand:
                    break
            if stand:
                flags.append(f"tight: door stand spot clearance {rm.at(clr, *stand):.2f} m (< {ROBOT_R})")
        if stand is None:
            stand = (du_[0] + n[0] * STAND_DOOR, du_[1] + n[1] * STAND_DOOR)
            flags.append(f"stand spot has clearance {rm.at(clr, *stand):.2f} m < {ROBOT_R_TIGHT}")
        results[pid] = {"cls": "door", "door": d, "target_uv": du_, "stand_uv": stand, "normal": n, "flags": flags,
                        "stand_note": sd}

    # furniture: fit each place's rectangle; places with a stronger fit claim their cells first
    furn = [(pid, p, place_class(pid, p.get("description"))) for pid, p in places.items()]
    furn = [(pid, p, c if c in SIZES else "table") for pid, p, c in furn if c and c != "door"]
    def votes_for(cls):
        if cls == "workbench":
            return votes[VOTED.index("workbench")] + votes[VOTED.index("table")] + 0.5 * votes[VOTED.index("desk")]
        return votes[VOTED.index(cls)] if cls in VOTED else np.zeros_like(F)

    # pass 1 alone sets the order (strongest, least ambiguous fit first); pass 2 fits one at a time, each
    # rectangle's cells then counting against the later ones (desks in a pod end up side by side)
    first = {pid: fit_rect(cls, seeds_of(pid, p), rm, F, E, votes_for(cls), taken, allowed) for pid, p, cls in furn}
    for pid, p, cls in sorted(furn, key=lambda t: -(first[t[0]]["score"] if first[t[0]] else -1e9)):
        r = fit_rect(cls, seeds_of(pid, p), rm, F, E, votes_for(cls), taken, allowed)
        if r is None:
            continue
        results[pid] = {"cls": r["cls"], "rect": r}
        taken += rect_mask(occ.shape, r)

    for pid, p, cls in furn:
        res = results.get(pid)
        if not res or "rect" not in res:
            results[pid] = {"cls": cls, "fail": "no rectangle fits near the saved target"}
            continue
        r = res["rect"]
        st = choose_stand(r, rm, clr, rm.to_room(p["x"], p["y"]), cls in BIG, allowed)
        res["flags"] = []
        if st and st[5]:
            res["flags"].append(f"tight: no spot {STAND_D[0]}-{STAND_D[-1]} m out with clearance >= {ROBOT_R}; using one with "
                                f"{st[3]:.2f} m clearance, {math.hypot(st[1][0] - st[2][0], st[1][1] - st[2][1]):.1f} m from the target")
        if st is None:
            res["flags"].append("no free stand spot 0.8-1.3 m in front of any face")
            res["stand_uv"], res["target_uv"] = rm.to_room(p["x"], p["y"]), (r["u"], r["v"])
        else:
            res["stand_uv"], res["target_uv"], res["clear"], res["normal"] = st[1], st[2], st[3], st[4]
            res["clear"] = st[3]
        # evidence: frames whose votes for this class landed in the rectangle
        vi = VOTED.index(cls) if cls in VOTED else -1
        ev = {}
        if len(hits):
            hu, hv = rm.to_room(origin[0] + (hits[:, 3] + 0.5) * RES, origin[1] + (hits[:, 2] + 0.5) * RES)
            inside = (np.abs(hu - r["u"]) <= r["du"] / 2 + 0.1) & (np.abs(hv - r["v"]) <= r["dv"] / 2 + 0.1)
            for fi, li, w in hits[inside][:, [0, 1, 4]]:
                if int(li) == vi:
                    ev[int(fi)] = ev.get(int(fi), 0) + w
        res["evidence_frames"] = sorted(ev, key=lambda k: -ev[k])
        print(f"  fit {pid:17s} {cls:16s} ({r['u']:5.2f},{r['v']:5.2f}) {r['du']:.2f}x{r['dv']:.2f} score {r['score']:.2f} "
              f"fill {r['fill']:.2f} free {r['free']:.2f} front {r['front']:.2f} votes {r['votes']:.2f} dist {r['dist']:.2f}")
        res["n_frames"] = len(ev)

    # 5. rule checks
    rects = {pid: res["rect"] for pid, res in results.items() if "rect" in res}
    for pid, res in results.items():
        if "fail" in res:
            continue
        su = res["stand_uv"]
        c = float(rm.at(clr, *su))
        if c < ROBOT_R_TIGHT and not any("clearance" in f for f in res["flags"]):
            res["flags"].append(f"stand spot clearance {c:.2f} m < {ROBOT_R}")
        for q, r in rects.items():
            if abs(su[0] - r["u"]) < r["du"] / 2 + 0.15 and abs(su[1] - r["v"]) < r["dv"] / 2 + 0.15:
                res["flags"].append(f"stand spot inside or touching the {q} rectangle")
        if res["cls"] == "door":
            ln = res["door"]["line"]
            if not ln["outer"]:
                res["flags"].append("door on an interior line, not an outer wall")
            if res["door"]["spread"] > 0.5:
                res["flags"].append(f"observations spread {res['door']['spread']:.2f} m along the wall")
        if "rect" in res:
            r = res["rect"]
            if r["fill"] < 0.3:
                res["flags"].append(f"rectangle only {100 * r['fill']:.0f}% filled by map obstacles")
            for q, r2 in rects.items():
                if q == pid:
                    continue
                ou = max(0, min(r["u"] + r["du"] / 2, r2["u"] + r2["du"] / 2) - max(r["u"] - r["du"] / 2, r2["u"] - r2["du"] / 2))
                ov = max(0, min(r["v"] + r["dv"] / 2, r2["v"] + r2["dv"] / 2) - max(r["v"] - r["dv"] / 2, r2["v"] - r2["dv"] / 2))
                if ou * ov > 0.25 * min(r["du"] * r["dv"], r2["du"] * r2["dv"]):
                    res["flags"].append(f"overlaps {q}")
            if res["n_frames"] == 0:
                res["flags"].append(f"no camera frame saw a {res['cls']} here (map shape only)")

    # confidence
    for pid, res in results.items():
        if "fail" in res:
            continue
        if res["cls"] == "door":
            d = res["door"]
            c = 0.3 + 0.08 * min(len(d["frames"]), 5) + (0.15 if d["snap"] != "measured" else 0) + (0.1 if d["line"]["outer"] else 0)
        else:
            r = res["rect"]
            c = 0.2 + 0.35 * max(0.0, min(1.0, r["fill"] - r["free"])) + 0.08 * min(res["n_frames"], 4)
            c -= 0.1 * max(0.0, r["dist"] - 0.5)
        c -= 0.12 * len(res["flags"])
        res["conf"] = round(max(0.05, min(0.95, c)), 2)

    # proposals
    items = []

    def frame_urls(idx):
        return [frames[i]["url"] for i in idx[:3]]

    for pid, res in results.items():
        p = places[pid]
        if "fail" in res:
            print(f"  {pid:18s} FAILED: {res['fail']}")
            continue
        tx, ty = rm.to_map(*res["target_uv"])
        sx, sy = rm.to_map(*res["stand_uv"])
        yaw = math.degrees(math.atan2(ty - sy, tx - sx))
        old_t = p.get("target") or {"x": p["x"] + 0.9 * math.cos(math.radians(p["yaw_deg"])),
                                    "y": p["y"] + 0.9 * math.sin(math.radians(p["yaw_deg"]))}
        dt = math.hypot(tx - old_t["x"], ty - old_t["y"])
        ds = math.hypot(sx - p["x"], sy - p["y"])
        dyaw = abs(wrap(math.radians(yaw - p["yaw_deg"])))
        res.update({"map_target": (tx, ty), "map_stand": (sx, sy), "yaw_deg": yaw, "dt": dt, "ds": ds,
                    "dyaw": math.degrees(dyaw)})
        if dt < MOVE_MIN and ds < MOVE_MIN + 0.05 and math.degrees(dyaw) < 10:
            print(f"  {pid:18s} already fine (target {dt:.2f} m, stand {ds:.2f} m)")
            continue
        if res["cls"] == "door":
            d = res["door"]
            wall = d["line"]["outer"] or "interior"
            snap = {"measured": "where the camera views put it"}.get(d["snap"], "lined up with the " + d["snap"].replace("outer:", "") + " corner"
                                                                     if d["snap"].startswith(("outer", "inner")) else "centred on a wall gap")
            summary = f"move {pid} {dt:.1f} m onto the {wall} wall, {snap}"
            reason = (f"{len(d['frames'])} drive frames show a door here (rays from the camera through the door box meet the "
                      f"{wall} wall line at {d['along_meas']:.2f} m along it, spread {d['spread']:.2f} m); "
                      f"door {d['width']:.1f} m wide, {d['snap']}; stand {res['stand_note'][0] if res['stand_note'] else STAND_DOOR:.1f} m "
                      f"in front along the wall's inward normal, facing the door")
            ev = sorted({o["frame"] for o in d["obs"]}, key=lambda i: -max(o["w"] for o in d["obs"] if o["frame"] == i))
        else:
            r = res["rect"]
            summary = (f"move {pid} target {dt:.1f} m / stand {ds:.1f} m onto a {r['du']:.1f} x {r['dv']:.1f} m "
                       f"{res['cls']} squared to the room")
            reason = (f"room-aligned {res['cls']} rectangle {100 * r['fill']:.0f}% filled by map obstacles/table tops, "
                      f"{100 * r['free']:.0f}% free floor, {res['n_frames']} frames saw a {res['cls']} there; "
                      f"{r['dist']:.2f} m from the saved target; stand {res.get('clear', 0):.2f} m clear of obstacles, "
                      f"facing {'the nearest face' if res['cls'] in BIG else 'the centre'}")
            ev = res["evidence_frames"]
        items.append({"id": f"p{len(items) + 1}", "kind": "place_move", "target_id": pid, "summary": summary,
                      "reason": reason, "confidence": res["conf"],
                      "change": {"x": round(sx, 3), "y": round(sy, 3), "yaw_deg": round(yaw, 1),
                                 "target": {"x": round(tx, 3), "y": round(ty, 3)}},
                      "evidence": frame_urls(ev), "flags": list(res["flags"]), "_res": pid})

    # objects: doors and fitted furniture as objects; existing named ones moved
    def obj_change(label, name, u, v, du, dv):
        x, y = rm.to_map(u, v)
        long_u = du >= dv
        yaw = rm.a if long_u else rm.a + math.pi / 2
        return {"label": label, "name": name, "x": round(x, 3), "y": round(y, 3), "w": round(max(du, dv), 2),
                "h": round(min(du, dv), 2), "yaw": round(wrap(yaw), 3)}

    new_objs = []
    for pid, res in results.items():
        if "fail" in res:
            continue
        if res["cls"] == "door":
            d = res["door"]
            u, v = door_uv(d)
            du, dv = (0.1, d["width"]) if d["line"]["axis"] == "u" else (d["width"], 0.1)
            ev = [o["frame"] for o in d["obs"]]
            new_objs.append((pid, "door", obj_change("door", pid, u, v, du, dv), res["conf"], ev, res["flags"]))
        else:
            r = res["rect"]
            new_objs.append((pid, res["cls"], obj_change(res["cls"], pid, r["u"], r["v"], r["du"], r["dv"]), res["conf"],
                             res["evidence_frames"], res["flags"]))
    for k, d in enumerate(doors):                 # doors no place points at
        if k in door_used:
            continue
        u, v = door_uv(d)
        du, dv = (0.1, d["width"]) if d["line"]["axis"] == "u" else (d["width"], 0.1)
        conf = round(min(0.8, 0.2 + 0.08 * len(d["frames"]) + (0.1 if d["line"]["outer"] else -0.1)), 2)
        fl = [] if d["line"]["outer"] else ["on an interior line, not an outer wall"]
        new_objs.append((None, "door", obj_change("door", "", u, v, du, dv), conf, sorted({o["frame"] for o in d["obs"]}), fl))
    for pid, label, ch, conf, ev, fl in new_objs:
        # an existing object with this name (or same label close by) -> move it, else new
        match = None
        for o in objects:
            if (pid and o.get("name") == pid) or (o.get("label") == label and math.hypot(o["x"] - ch["x"], o["y"] - ch["y"]) < 0.8):
                match = o
                break
        if match is not None:
            dd = math.hypot(match["x"] - ch["x"], match["y"] - ch["y"])
            if dd < MOVE_MIN:
                continue
            kind, tid = "object_move", match.get("id")
            summary = f"move object {tid} ({match.get('name') or label}) {dd:.1f} m to the fitted {label}"
            if match.get("confirmed_by"):
                fl = fl + [f"object was confirmed by {match['confirmed_by']}"]
                conf = round(conf * 0.8, 2)
            if match.get("label") != label:
                ch = dict(ch, label=match.get("label"))
        else:
            kind, tid = "object_new", None
            summary = f"new {label} object" + (f" '{pid}'" if pid else "") + f" {ch['w']:.1f} x {ch['h']:.1f} m"
        items.append({"id": f"p{len(items) + 1}", "kind": kind, "target_id": tid, "summary": summary,
                      "reason": f"same fit as the place {pid}" if pid else f"door seen in {len(set(ev))} drive frames",
                      "confidence": conf, "change": ch, "evidence": frame_urls(ev), "flags": list(fl), "_pid": pid})

    # pictures (also the one the model reviews)
    if a.pics:
        os.makedirs(a.pics, exist_ok=True)
    pic_dir = a.pics or "/tmp"
    cvs = Canvas(rm, occ, mid, seen, span)
    draw_walls(cvs, lines, corners, gaps)
    for f in frames:
        cv2.circle(cvs.img, cvs.pxm(f["x"], f["y"]), 1, (200, 160, 160), -1)
    review_items = []
    for it in items:
        if it["kind"] == "place_move" or (it["change"].get("label") == "door" and not it["change"].get("name")):
            it["_n"] = len(review_items) + 1
        if it["kind"] == "place_move":
            res = results[it["_res"]]
            if "rect" in res:
                cvs.rect(res["rect"], COL.get(res["cls"], (0, 0, 0)))
            if res["cls"] == "door":
                d = res["door"]
                u, v = res["target_uv"]
                hw = d["width"] / 2
                p, q = ((u, v - hw), (u, v + hw)) if d["line"]["axis"] == "u" else ((u - hw, v), (u + hw, v))
                cvs.line(p, q, COL["door"], 6)
            su, tu = res["stand_uv"], res["target_uv"]
            cvs.arrow(su, math.atan2(tu[1] - su[1], tu[0] - su[0]), (0, 160, 0))
            cv2.circle(cvs.img, cvs.px(*tu), 4, (0, 0, 0), -1)
            cvs.text(tu, f"{it['_n']} {it['target_id']}", (0, 0, 0))
            review_items.append({"n": it["_n"], "what": f"{res['cls']} '{it['target_id']}' rect "
                                 f"{'%.1fx%.1f m' % (res['rect']['du'], res['rect']['dv']) if 'rect' in res else 'door %.1f m' % res['door']['width']}"
                                 f" at ({tu[0]:.1f},{tu[1]:.1f}), stand ({su[0]:.1f},{su[1]:.1f})"})
        elif it["change"]["label"] == "door" and not it["change"]["name"]:
            u, v = rm.to_room(it["change"]["x"], it["change"]["y"])
            cv2.circle(cvs.img, cvs.px(u, v), 7, COL["door"], 3)
            cvs.text((u, v), f"{it['_n']} door?", COL["door"])
            review_items.append({"n": it["_n"], "what": f"extra door at ({u:.1f},{v:.1f})"})
    review_png = os.path.join(pic_dir, "tidy_review.jpg")
    cv2.imwrite(review_png, cvs.img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    review_raw = None
    if not a.no_review and review_items:
        verdicts, review_raw = qwen_review(a, review_png, review_items)
        n_of_place = {it["target_id"]: it["_n"] for it in items if it["kind"] == "place_move"}
        for it in items:
            n = it.get("_n") or n_of_place.get(it.get("_pid"))
            v = verdicts.get(n)
            if not v:
                continue
            it["review"] = {"verdict": v[0], "why": v[1]}
            if v[0] == "wrong":
                it["confidence"] = round(it["confidence"] * 0.5, 2)
                it["flags"].append("model review: wrong - " + v[1])
            elif v[0] == "suspect":
                it["confidence"] = round(it["confidence"] * 0.8, 2)
                it["flags"].append("model review: suspect - " + v[1])
        print(f"model review: {sum(1 for v in verdicts.values() if v[0] != 'ok')} of {len(verdicts)} flagged")

    # final picture: current places grey, proposals coloured
    if a.pics:
        for pid, p in places.items():
            su = rm.to_room(p["x"], p["y"])
            cvs.arrow(su, math.radians(p["yaw_deg"]) - rm.a, (150, 150, 150), 1)
            if p.get("target"):
                tu = rm.to_room(p["target"]["x"], p["target"]["y"])
                cv2.drawMarker(cvs.img, cvs.px(*tu), (150, 150, 150), cv2.MARKER_TILTED_CROSS, 8, 1)
                cvs.line(su, tu, (190, 190, 190), 1)
        for it in items:
            if it["kind"] == "place_move":
                res = results[it["_res"]]
                p = places[it["target_id"]]
                cvs.line(rm.to_room(p["x"], p["y"]), res["stand_uv"], (0, 200, 255), 1)
        cv2.putText(cvs.img, f"room frame (map rotated {-deg:.1f} deg). red: outer walls, green: gaps, "
                    "circles: corners; grey: current places; green arrows: proposed", (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 0, 0), 1, cv2.LINE_AA)
        cv2.imwrite(os.path.join(a.pics, "tidy_map.png"), cvs.img)
        vp = Canvas(rm, occ, mid, seen, span)
        draw_walls(vp, [ln for ln in lines if ln["outer"]], [], [])
        for li, lab in enumerate(VOTED):
            vv = votes[li]
            m = vv >= VNORM * 2
            ii, jj = np.nonzero(m)
            for i, j in zip(ii, jj):
                u, v = rm.u0 + (j + 0.5) * RES, rm.v0 + (i + 0.5) * RES
                cv2.circle(vp.img, vp.px(u, v), 2, COL.get(lab, (0, 0, 0)), -1)
        for k, lab in enumerate(VOTED):
            cv2.rectangle(vp.img, (8, 30 + 16 * k), (20, 42 + 16 * k), COL.get(lab, (0, 0, 0)), -1)
            cv2.putText(vp.img, lab, (26, 41 + 16 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        for pid, p in places.items():
            tu = seed_of(p)
            cv2.drawMarker(vp.img, vp.px(*tu), (0, 0, 0), cv2.MARKER_TILTED_CROSS, 10, 2)
            vp.text(tu, pid, (0, 0, 0), 0.4)
        cv2.putText(vp.img, f"camera votes per class (cells >= {2 * VNORM:g}); x = saved targets", (8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.imwrite(os.path.join(a.pics, "tidy_votes.png"), vp.img)
        door_pictures(a.pics, doors, results, frames, rm, occ, mid, seen, span, lines, corners, gaps)

    for it in items:
        it.pop("_res", None)
        it.pop("_n", None)
        it.pop("_pid", None)
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "map": host_path(path), "room_deg": round(deg, 2),
           "params": {"ALPHA": ALPHA, "BETA": BETA, "GAMMA": GAMMA, "SEARCH_R": SEARCH_R, "CORNER_SNAP": CORNER_SNAP,
                      "DOOR_JAMB": DOOR_JAMB, "STAND_D": STAND_D, "STAND_DOOR": STAND_DOOR, "ROBOT_R": ROBOT_R,
                      "frames": len(frames)},
           "walls": [{"axis": ln["axis"], "c": round(ln["c"], 2), "lo": round(ln["lo"], 2), "hi": round(ln["hi"], 2),
                      "len": round(ln["len"], 1), "outer": ln["outer"]} for ln in lines],
           "review_raw": review_raw, "items": items}
    print(f"\n{len(items)} proposals:")
    for it in items:
        print(f"  {it['id']:4s} {it['kind']:11s} {it['confidence']:.2f}  {it['summary']}"
              + (f"   [{'; '.join(it['flags'])}]" if it["flags"] else ""))
    print(f"{time.time() - t_start:.0f} s")
    if a.dry_run:
        return
    out = a.out or os.path.join(a.maps, f"{a.name}_proposals.json")
    tmp = out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    try:
        os.chown(tmp, HOST_UID, HOST_UID)
    except PermissionError:
        pass
    os.replace(tmp, out)
    print(f"wrote {out}")


def door_pictures(pics, doors, results, frames, rm, occ, mid, seen, span, lines, corners, gaps):
    """one picture per detected door: up to 3 evidence frames with the box, and the map with the rays."""
    name_of = {id(res["door"]): pid for pid, res in results.items() if res.get("cls") == "door" and "door" in res}
    for k, d in enumerate(doors):
        name = name_of.get(id(d), f"door{k}")
        cvs = Canvas(rm, occ, mid, seen, span, scale=3)
        draw_walls(cvs, lines, corners, gaps)
        best = sorted(d["obs"], key=lambda o: -o["w"])
        for o in d["obs"]:
            f = frames[o["frame"]]
            cu = rm.to_room(f["cx"], f["cy"])
            ln = d["line"]
            hit = (ln["c"], o["along"]) if ln["axis"] == "u" else (o["along"], ln["c"])
            cvs.line(cu, hit, (255, 140, 0), 1)
            cv2.circle(cvs.img, cvs.px(*cu), 3, (255, 0, 0), -1)
        u, v = door_uv(d)
        hw = d["width"] / 2
        p, q = ((u, v - hw), (u, v + hw)) if d["line"]["axis"] == "u" else ((u - hw, v), (u + hw, v))
        cvs.line(p, q, (0, 0, 0), 7)
        if name in results and "stand_uv" in results[name]:
            su = results[name]["stand_uv"]
            cvs.arrow(su, math.atan2(v - su[1], u - su[0]), (0, 160, 0))
        cvs.text((u, v), f"{name}: {len(d['frames'])} frames, {d['snap']}", (0, 0, 0), 0.5)
        tiles, seen_f = [], set()
        for o in best:
            if o["frame"] in seen_f:
                continue
            seen_f.add(o["frame"])
            img = cv2.imread(frames[o["frame"]]["path"])
            if img is None:
                continue
            H, W = img.shape[:2]
            x1, y1, x2, y2 = o["box"]
            cv2.rectangle(img, (int(x1 * W), int(y1 * H)), (int(x2 * W), int(y2 * H)), (0, 0, 255), 2)
            cv2.putText(img, f"{os.path.basename(frames[o['frame']]['path'])} {o['how']} t={o['t']:.1f}m", (5, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            tiles.append(img)
            if len(tiles) == 3:
                break
        Wt = 640 * 3
        top = np.hstack(tiles + [np.zeros_like(tiles[0])] * (3 - len(tiles))) if tiles else np.zeros((360, Wt, 3), np.uint8)
        m = cvs.img
        sc = Wt / m.shape[1]
        m = cv2.resize(m, (Wt, int(m.shape[0] * sc)))
        cv2.imwrite(os.path.join(pics, f"door_{name}.jpg"), np.vstack([top, m]), [cv2.IMWRITE_JPEG_QUALITY, 85])


if __name__ == "__main__":
    main()
