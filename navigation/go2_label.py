"""Semantic labels for the lab map: which obstacles are desks, the sofa, the conference table, chairs...

Offline pass over the camera trail (frames with map poses, see go2_trail.py). Each chosen frame goes to
the local vision model (Qwen3-VL via vLLM) which boxes objects from a fixed vocabulary. Each box's
horizontal extent is a bearing range; rays across it are cast over the saved occupancy grid and the
first obstacle cell along each ray gets a vote for the box's label. Poses can be off by 1-3 m and
10-20 degrees and single boxes can be wrong, so nothing is trusted alone: a cell is labelled only
with enough votes and a clear majority, and an object only when several frames agree on it.

Writes /maps/<map>_objects.json (keeps human-edited objects) and a debug PNG. Never talks to the dog.

  docker run --rm --net=host --entrypoint python3 -v /etc/localtime:/etc/localtime:ro \
      -v /home/nesl/oliver:/src -v /home/nesl/oliver/go2_maps:/maps -v /tmp/lbl:/out rosrobot \
      /src/go2_label.py --cache /out/qwen_cache.jsonl --png /out/labels.png [--dry-run] [--since ...]
"""
import argparse
import base64
import json
import math
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

RES = 0.05                  # m per cell (go2_mapper.RES); row index = y, col = x, row 0 = lowest y
OCC_SCORE, LAYER_OCC = 2, 2  # occupied: score >= 2, or mid/high layer votes >= 2 (go2_mapper)
HFOV = math.radians(79)     # front camera, tape-verified; pinhole, centred principal point
CAM_AHEAD = 0.33            # camera sits this far ahead of the pose point along yaw (m)
CAM_H = 0.30               # camera height above the floor (m), rough; from box bottoms vs ray ranges
HOST_UID = 1000
VOCAB = ["desk", "office chair", "sofa", "conference table", "table", "cabinet/drawers", "shelf/bookcase",
         "door", "wall", "box", "printer", "water cooler", "trash bin", "person", "other"]
SKIP = {"person"}           # moves around: never voted
NO_OBJECT = {"wall", "other"}   # voted (they compete for a cell, so a wall seen as a "desk" once loses)
                                # but never turned into objects
VOTE_W = {"wall": 0.3, "other": 0.5}   # wall boxes are huge and swallow what stands in front of them
SYNONYMS = {"chair": "office chair", "cabinet": "cabinet/drawers", "drawers": "cabinet/drawers",
            "shelf": "shelf/bookcase", "bookcase": "shelf/bookcase", "bookshelf": "shelf/bookcase",
            "couch": "sofa", "trash can": "trash bin", "bin": "trash bin", "boxes": "box"}
COLORS = {"desk": (40, 120, 230), "office chair": (230, 150, 30), "sofa": (150, 40, 160),
          "conference table": (30, 30, 200), "table": (90, 180, 250), "cabinet/drawers": (60, 140, 60),
          "shelf/bookcase": (40, 200, 120), "door": (120, 80, 40), "box": (40, 200, 220), "printer": (200, 200, 60),
          "water cooler": (230, 60, 60), "trash bin": (130, 130, 130)}   # BGR, for the debug PNG
PROMPT = ("Locate the furniture and objects that are clearly visible in this image of a lab. Use one label per "
          "object from: " + ", ".join(VOCAB) + ". Give each visible object once, with a tight box, at most 12 "
          "objects; do not list labels that are not in the image. Answer with JSON only: "
          '[{"bbox_2d": [x1, y1, x2, y2], "label": "..."}]')


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


# ---------- 1. frames ----------
def load_frames(maps, name, since, until, skip):
    """All trail frames [(t, x, y, yaw, path)] within [since, until) and outside the skip ranges (epoch s)."""
    root, out = os.path.join(maps, f"{name}_trail"), []
    for d in sorted(os.listdir(root)):
        try:
            with open(os.path.join(root, d, "index.jsonl")) as f:
                for line in f:
                    try:
                        p = json.loads(line)
                        out.append((p["t"], p["x"], p["y"], p["yaw"], os.path.join(root, d, p["f"])))
                    except (ValueError, KeyError):
                        pass
        except OSError:
            pass
    return [fr for fr in out if since <= fr[0] < until and not any(a <= fr[0] < b for a, b in skip)]


def choose(frames, step_m, step_deg, per_key, occ, origin):
    """About one frame per step_m of position and step_deg of heading: at most per_key frames per
    (x, y, heading) bin, spread over different days, so pose errors of different sessions average out.
    Frames whose camera sits inside an obstacle have an obviously wrong pose and are dropped."""
    bins, bad = {}, 0
    for fr in frames:
        t, x, y, yaw, _ = fr
        cx, cy = x + CAM_AHEAD * math.cos(yaw), y + CAM_AHEAD * math.sin(yaw)
        c, r = int((cx - origin[0]) // RES), int((cy - origin[1]) // RES)
        if not (0 <= r < occ.shape[0] and 0 <= c < occ.shape[1]) or occ[r, c]:
            bad += 1
            continue
        key = (round(x / step_m), round(y / step_m), round(wrap(yaw) / math.radians(step_deg)) % round(360 / step_deg))
        bins.setdefault(key, []).append(fr)
    out = []
    for fs in bins.values():
        days, pick = set(), []
        for fr in sorted(fs, key=lambda f: f[0]):       # first one of each day, then fill up
            day = os.path.basename(os.path.dirname(fr[4]))
            if day not in days:
                days.add(day)
                pick.append(fr)
        pick += [fr for fr in fs if fr not in pick]
        out += pick[:per_key]
    return sorted(out, key=lambda f: f[0]), bad


# ---------- 2. detection ----------
def ask(url, path, timeout=60):
    """Raw model answer for one frame."""
    with open(path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    body = {"model": "qwen3-vl-8b", "temperature": 0, "max_tokens": 700, "repetition_penalty": 1.05,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img}},
                {"type": "text", "text": PROMPT}]}]}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)["choices"][0]["message"]["content"]
        except Exception as e:      # noqa: BLE001  (server busy / timeout: retry, then give up on this frame)
            err = e
            time.sleep(1 + attempt)
    print(f"  model failed on {path}: {err}")
    return None


def parse(txt):
    """[(label, x1, x2, y2, weight) with x, y in 0..1 of the image]. Pulls every {"bbox_2d": [...], "label": ...}
    out of the text (code fences, cut-off output and junk tolerated). The model sometimes repeats one
    box with many labels (it walks the vocabulary): a box with 3+ labels is dropped, with 2 each counts
    half; exact repeats count once."""
    by_box = {}
    for m in re.finditer(r"\{[^{}]*\}", txt or ""):
        try:
            d = json.loads(m.group(0))
            x1, y1, x2, y2 = [float(v) for v in d["bbox_2d"]]
            lab = str(d["label"]).strip().lower()
        except (ValueError, KeyError, TypeError):
            continue
        lab = SYNONYMS.get(lab, lab)
        if lab not in VOCAB:
            lab = "other"
        x1, x2 = sorted((min(max(x1, 0), 1000) / 1000, min(max(x2, 0), 1000) / 1000))
        if x2 - x1 < 0.01:
            continue
        by_box.setdefault((round(x1, 2), round(x2, 2), round(y1 / 20), round(y2 / 20)), set()).add(lab)
    out = []
    for (x1, x2, _, y2), labs in by_box.items():
        if len(labs) <= 2:
            out += [(lab, x1, x2, min(y2 * 20 / 1000, 1.0), 1.0 / len(labs)) for lab in labs]
    return out


# ---------- 3. projection ----------
def cast(occ, origin, cx, cy, bearings, max_r):
    """First occupied cell (r, c) along each map-frame bearing from (cx, cy), or None, plus its range."""
    d = np.arange(0.1, max_r, RES / 2)
    xs = cx + np.cos(bearings)[:, None] * d[None, :]
    ys = cy + np.sin(bearings)[:, None] * d[None, :]
    c = np.floor((xs - origin[0]) / RES).astype(np.int64)
    r = np.floor((ys - origin[1]) / RES).astype(np.int64)
    inb = (r >= 0) & (r < occ.shape[0]) & (c >= 0) & (c < occ.shape[1])
    hit = np.zeros(r.shape, bool)
    hit[inb] = occ[r[inb], c[inb]]
    k = hit.argmax(1)
    ok = hit[np.arange(len(k)), k]
    return [(r[i, k[i]], c[i, k[i]], d[k[i]]) if ok[i] else None for i in range(len(k))]


# ---------- 4. aggregation ----------
def objects(votes, hits, occ, origin, labels, a):
    """Per-cell majority label -> connected same-label groups -> rotated rectangles in map metres."""
    V = votes.copy()
    if a.smooth:            # a cell's votes include its neighbours': poses jitter by a few cells
        k = 2 * a.smooth + 1
        for i in range(len(V)):
            V[i] = cv2.boxFilter(V[i], -1, (k, k), normalize=False, borderType=cv2.BORDER_CONSTANT)
    near = cv2.dilate(occ.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    total = V.sum(0)
    best = V.argmax(0)
    bestv = V.max(0)
    frac = np.where(total > 0, bestv / np.maximum(total, 1e-9), 0)
    ok = near & (bestv >= a.min_votes) & (frac >= a.min_frac)
    cell_label = np.where(ok, best, -1)
    out = []
    for li, lab in enumerate(labels):
        if lab in NO_OBJECT:
            continue
        mask = (cell_label == li).astype(np.uint8)
        if not mask.any():
            continue
        grown = cv2.dilate(mask, np.ones((2 * a.grow + 1,) * 2, np.uint8)) if a.grow else mask
        n, comp = cv2.connectedComponents(grown, connectivity=8)
        h = hits[hits[:, 1] == li]
        hcomp = comp[h[:, 2].astype(int), h[:, 3].astype(int)] if len(h) else np.zeros(0, int)
        for k in range(1, n):
            cells = np.argwhere((comp == k) & (mask > 0))
            frames = len(set(h[hcomp == k, 0].astype(int).tolist()))
            raw = float(votes[li][cells[:, 0], cells[:, 1]].sum())
            if len(cells) < a.min_cells or frames < a.min_frames or raw < a.min_votes:
                continue
            pts = np.stack([origin[0] + (cells[:, 1] + 0.5) * RES, origin[1] + (cells[:, 0] + 0.5) * RES], 1)
            (x, y), (w, hh), ang = cv2.minAreaRect(pts.astype(np.float32))
            out.append({"label": lab, "x": round(float(x), 2), "y": round(float(y), 2),
                        "w": round(float(w) + RES, 2), "h": round(float(hh) + RES, 2),
                        "yaw": round(math.radians(ang), 3),
                        "votes": round(raw, 1),
                        "cells": int(len(cells)), "frames": frames})
    out.sort(key=lambda o: -o["votes"])
    return out, cell_label


def rect_poly(o):
    return cv2.boxPoints(((o["x"], o["y"]), (max(o["w"], RES), max(o["h"], RES)), math.degrees(o.get("yaw", 0))))


def overlap(a, b):
    """Intersection area / smaller area of two objects' rotated rectangles."""
    pa, pb = rect_poly(a), rect_poly(b)
    inter, poly = cv2.intersectConvexConvex(pa.astype(np.float32), pb.astype(np.float32))
    return inter / max(min(cv2.contourArea(pa), cv2.contourArea(pb)), 1e-6)


def merge(new, old_file):
    """Keep every human-edited object (confirmed_by or a name) exactly as it is. Its re-detection, the
    overlapping new ones with its label (or, if a person relabelled it, the most overlapping one), only
    goes into its 'detected' field. Every other new detection gets a fresh id."""
    kept = []
    try:
        with open(old_file) as f:
            kept = [o for o in json.load(f).get("objects", []) if o.get("confirmed_by") or o.get("name")]
    except (OSError, ValueError):
        pass
    absorbed = set()
    for k in kept:
        cand = [(overlap(o, k), i) for i, o in enumerate(new) if i not in absorbed]
        cand = [(ov, i) for ov, i in cand if ov > 0.3]
        same = [i for ov, i in cand if new[i]["label"] == k.get("label")]
        mine = same or [max(cand)[1]] if cand else []
        if mine:
            best = max(mine, key=lambda i: new[i]["votes"])
            k["detected"] = {f: new[best][f] for f in ("label", "x", "y", "w", "h", "yaw", "votes", "cells", "frames")}
            absorbed.update(mine)
    out, used = list(kept), {o.get("id") for o in kept}
    for i, o in enumerate(new):
        if i in absorbed:
            continue
        n, base = 1, "obj_" + re.sub(r"\W+", "_", o["label"])
        while f"{base}_{n}" in used:
            n += 1
        used.add(f"{base}_{n}")
        out.append({"id": f"{base}_{n}", "label": o["label"], "name": "", **{k: o[k] for k in o if k != "label"}})
    return out, len(kept)


# ---------- debug image ----------
def debug_png(path, occ, seen, origin, cell_label, labels, objs, places, frames, scale=4):
    known = np.argwhere(seen | occ)
    (r0, c0), (r1, c1) = known.min(0) - 10, known.max(0) + 11
    img = np.full((r1 - r0, c1 - c0, 3), 205, np.uint8)
    img[seen[r0:r1, c0:c1]] = 254
    img[occ[r0:r1, c0:c1]] = 60
    cl = cell_label[r0:r1, c0:c1]
    for li, lab in enumerate(labels):
        if lab in COLORS:
            img[cl == li] = COLORS[lab]
    img = cv2.resize(img[::-1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)   # north up
    H = img.shape[0]

    def px(x, y):
        return int(((x - origin[0]) / RES - c0) * scale), int(H - ((y - origin[1]) / RES - r0) * scale)
    for t, x, y, yaw, _ in frames:
        cv2.circle(img, px(x, y), 1, (200, 170, 170), -1)
    for o in objs:
        lab = o.get("label", "other")
        col = COLORS.get(lab, (0, 0, 0))
        pts = np.array([px(*p) for p in rect_poly(o)], np.int32)
        cv2.polylines(img, [pts], True, col, 2)
        cv2.putText(img, f"{o.get('name') or lab} {o.get('frames', '')}", px(o["x"], o["y"]), 0, 0.4, (0, 0, 0), 1)
    for name, (x, y) in places.items():
        p = px(x, y)
        cv2.drawMarker(img, p, (0, 0, 255), cv2.MARKER_CROSS, 10, 2)
        cv2.putText(img, name, (p[0] + 5, p[1] - 5), 0, 0.4, (0, 0, 200), 1)
    for i, lab in enumerate(l for l in labels if l in COLORS):    # legend
        cv2.rectangle(img, (5, 5 + 14 * i), (15, 15 + 14 * i), COLORS[lab], -1)
        cv2.putText(img, lab, (20, 15 + 14 * i), 0, 0.4, (0, 0, 0), 1)
    cv2.imwrite(path, img)


def get_places(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            pl = json.load(r)
        return {k: ((p.get("target") or p)["x"], (p.get("target") or p)["y"]) for k, p in pl.items()}
    except Exception:       # noqa: BLE001  (console down: just no markers)
        return {}


def when(s):
    """'2026-10-23' or '2026-10-23 13:30' (local time) -> epoch s."""
    s = s.strip().replace("T", " ")
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M" if " " in s else "%Y-%m-%d"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--maps", default="/maps")
    ap.add_argument("--map", default="lab")
    ap.add_argument("--since", help="only frames from this local time on: '2026-10-23' or '2026-10-23 13:30'")
    ap.add_argument("--until", help="only frames before this local time")
    ap.add_argument("--skip", action="append", default=[], help="drop frames in 'FROM,TO' (local times); repeatable")
    ap.add_argument("--step-m", type=float, default=0.4, help="frame subsampling: position bin (m)")
    ap.add_argument("--step-deg", type=float, default=20, help="frame subsampling: heading bin (deg)")
    ap.add_argument("--per-key", type=int, default=2, help="frames kept per position/heading bin (different days first)")
    ap.add_argument("--max-frames", type=int, default=0, help="cap on frames sent to the model (0 = no cap)")
    ap.add_argument("--url", default="http://localhost:8000/v1/chat/completions")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cache", help="jsonl of model answers per frame; reused on reruns (tuning is then free)")
    ap.add_argument("--max-range", type=float, default=6.0, help="ignore ray hits further than this (m)")
    ap.add_argument("--gate", type=float, default=2.0, help="range gate: hits beyond gate x (distance from the box's "
                    "bottom edge) + gate-add are ignored; 0 = off")
    ap.add_argument("--gate-add", type=float, default=0.5)
    ap.add_argument("--elevated-w", type=float, default=0.3, help="weight of boxes whose bottom is above the horizon")
    ap.add_argument("--ray-deg", type=float, default=1.0, help="one ray per this many degrees of box width")
    ap.add_argument("--shrink", type=float, default=0.1, help="trim this fraction off each side of a box")
    ap.add_argument("--wide", type=float, default=0.6, help="boxes wider than this fraction of the image...")
    ap.add_argument("--wide-w", type=float, default=0.3, help="...count this much (object right in front)")
    ap.add_argument("--smooth", type=int, default=1, help="spread votes over +-this many cells")
    ap.add_argument("--min-votes", type=float, default=4, help="cell needs this much winning vote (summed over the smoothing window)")
    ap.add_argument("--min-frac", type=float, default=0.5, help="and this share of all votes on it")
    ap.add_argument("--grow", type=int, default=1, help="dilate labelled cells by this many before grouping")
    ap.add_argument("--min-cells", type=int, default=4, help="drop objects with fewer cells")
    ap.add_argument("--min-frames", type=int, default=3, help="drop objects seen in fewer frames")
    ap.add_argument("--min-agree", type=float, default=0.25, help="second pass: drop frames whose votes on "
                    "labelled cells agree with the cell's label less than this share; 0 = off")
    ap.add_argument("--agree-min-votes", type=float, default=5, help="only judge frames with this many such votes")
    ap.add_argument("--png", default="/tmp/labels.png", help="debug image")
    ap.add_argument("--places-url", default="http://localhost:8080/places", help="known places drawn on the PNG")
    ap.add_argument("--out", help="default <maps>/<map>_objects.json")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, write only the PNG")
    a = ap.parse_args()
    t_start = time.time()

    g = np.load(os.path.join(a.maps, f"{a.map}.grid.npz"))
    origin = tuple(float(v) for v in g["origin"])
    occ = g["score"] >= OCC_SCORE
    for k in ("mid", "high"):
        if k in g.files:
            occ |= g[k] >= LAYER_OCC
    seen = g["seen"]

    skip = [tuple(when(s.strip()) for s in r.split(",")) for r in a.skip]
    allf = load_frames(a.maps, a.map, when(a.since) if a.since else 0, when(a.until) if a.until else 1e12, skip)
    frames, bad = choose(allf, a.step_m, a.step_deg, a.per_key, occ, origin)
    if a.max_frames:
        frames = frames[:: max(1, math.ceil(len(frames) / a.max_frames))]
    print(f"{len(allf)} frames in range, {bad} dropped (camera inside an obstacle), {len(frames)} used")

    cache = {}
    if a.cache and os.path.exists(a.cache):
        with open(a.cache) as f:
            for line in f:
                try:
                    d = json.loads(line)
                    cache[d["f"]] = d["txt"]
                except (ValueError, KeyError):
                    pass
    todo = [fr[4] for fr in frames if os.path.relpath(fr[4], a.maps) not in cache]
    print(f"model: {len(frames) - len(todo)} cached, {len(todo)} to ask")
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (p, txt) in enumerate(zip(todo, ex.map(lambda p: ask(a.url, p), todo))):
            if txt is None:
                continue
            key = os.path.relpath(p, a.maps)
            cache[key] = txt
            if a.cache:
                with open(a.cache, "a") as f:
                    f.write(json.dumps({"f": key, "txt": txt}) + "\n")
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(todo)} ({(time.time() - t0) / (i + 1):.2f} s/frame)")

    labels = [l for l in VOCAB if l not in SKIP]
    hits, nbox = [], 0          # (frame, label, row, col, weight)
    W, H = 640, 360
    fx = (W / 2) / math.tan(HFOV / 2)
    for fi, (t, x, y, yaw, p) in enumerate(frames):
        txt = cache.get(os.path.relpath(p, a.maps))
        if txt is None:
            continue
        cx, cy = x + CAM_AHEAD * math.cos(yaw), y + CAM_AHEAD * math.sin(yaw)
        mine = {}               # one vote per frame, label and cell (a shelf of stacked boxes is one vote)
        for lab, x1, x2, y2, w in parse(txt):
            if lab in SKIP:
                continue
            nbox += 1
            w *= VOTE_W.get(lab, 1.0) * (a.wide_w if x2 - x1 > a.wide else 1.0)
            m = (x2 - x1) * a.shrink
            u1, u2 = (x1 + m) * W, (x2 - m) * W
            b1, b2 = math.atan((W / 2 - u1) / fx), math.atan((W / 2 - u2) / fx)   # image right = negative bearing
            n = max(2, int(math.degrees(b1 - b2) / a.ray_deg) + 1)
            li = labels.index(lab)
            # range gate: a box's bottom edge is where the object meets the floor, so with a level camera
            # at CAM_H it is about CAM_H * fy / (pixels below centre) away. A ray that runs on far past
            # that went through something the (stale) map lacks and would vote for whatever is behind it.
            # Two-sided: a hit much nearer than that is something in front (e.g. boxes on a shelf seen
            # over the sofa). A box whose bottom is above the horizon doesn't stand on the floor nearby
            # (shelf contents, monitors, door frames): it rarely reaches the 0.2-0.6 m map, so it counts little.
            below = (y2 - 0.5) * H
            min_r, max_r = 0.0, a.max_range
            if a.gate and below > 0.03 * H:
                d = CAM_H * fx / below
                min_r, max_r = d / a.gate - a.gate_add, min(max_r, a.gate * d + a.gate_add)
            elif below <= 0:
                w *= a.elevated_w
            for h in cast(occ, origin, cx, cy, yaw + np.linspace(b2, b1, n), max_r):
                if h is not None and h[2] >= min_r:
                    k = (li, h[0], h[1])
                    mine[k] = max(mine.get(k, 0), w)
        hits += [(fi, li, r, c, w) for (li, r, c), w in mine.items()]
    hits = np.array(hits, np.float64).reshape(-1, 5)
    print(f"{nbox} boxes, {len(hits)} cell votes")

    def tally(h):
        v = np.zeros((len(labels),) + occ.shape, np.float32)
        np.add.at(v, (h[:, 1].astype(int), h[:, 2].astype(int), h[:, 3].astype(int)), h[:, 4])
        return v
    votes = tally(hits)
    objs, cell_label = objects(votes, hits, occ, origin, labels, a)
    # Second pass: a frame whose votes mostly disagree with the consensus was probably taken with a bad
    # pose (or the model misread it): drop it and vote again.
    if a.min_agree > 0:
        cl = cell_label[hits[:, 2].astype(int), hits[:, 3].astype(int)]
        on = cl >= 0
        fi = hits[:, 0].astype(int)
        tot = np.bincount(fi[on], hits[on, 4], len(frames))
        agree = np.bincount(fi[on], hits[on, 4] * (cl[on] == hits[on, 1]), len(frames))
        bad = (tot >= a.agree_min_votes) & (agree < a.min_agree * tot)
        if bad.any():
            days = {}
            for i in np.nonzero(bad)[0]:
                d = time.strftime("%m-%d %Hh", time.localtime(frames[i][0]))
                days[d] = days.get(d, 0) + 1
            print(f"dropping {bad.sum()} frames that disagree with the consensus (of {(tot >= a.agree_min_votes).sum()} "
                  f"checked): {days}")
            hits = hits[~bad[fi]]
            votes = tally(hits)
            objs, cell_label = objects(votes, hits, occ, origin, labels, a)
    out_path = a.out or os.path.join(a.maps, f"{a.map}_objects.json")
    final, n_kept = merge(objs, out_path)
    print(f"{len(objs)} objects detected, {n_kept} human-edited kept:")
    for o in final:
        print(f"  {o['id']:28s} {o['label']:17s} ({o['x']:6.2f},{o['y']:6.2f}) {o['w']:.2f}x{o['h']:.2f} m "
              f"votes {o.get('votes', '-')} cells {o.get('cells', '-')} frames {o.get('frames', '-')}"
              + (f"  name={o['name']!r}" if o.get("name") else ""))
    debug_png(a.png, occ, seen, origin, cell_label, labels, final, get_places(a.places_url), frames)
    print(f"debug image {a.png}; {time.time() - t_start:.0f} s total")
    if a.dry_run:
        return
    params = {k: v for k, v in vars(a).items() if k not in ("dry_run", "png", "cache", "url", "places_url", "out")}
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "params": params, "frames_used": len(frames),
           "objects": final}
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.chown(tmp, HOST_UID, HOST_UID)
    os.replace(tmp, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
