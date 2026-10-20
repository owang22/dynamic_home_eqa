"""Where a thing is on the lab map, from the console's stored camera frames ("object anchors").

    python3 go2/console/anchors.py --fetch            # copy the trail frames + poses to go2/data/trail_cache/ (once)
    python3 go2/console/anchors.py "water cooler=a tall black water dispenser with taps" "sofa=a dark leather sofa"

1. For every trail frame, the local vision model (Qwen3.8-27B, vLLM on 127.0.0.1:8300) says whether the thing is
   in the picture, where its centre is across the picture (0 = left edge, 1 = right edge), and whether it is cut
   off at a side. Cut-off sightings are not used.
2. Each sighting is a line on the map: from the frame's pose, at yaw + (0.5 - centre) x 73 deg (horizontal field
   of view of the Go2 camera, 720p calibration).
3. Position: RANSAC over pairs of lines (crossing 0.3-5 m in front of both, at least 15 deg apart), inliers =
   lines passing within 0.25 m, then the least-squares point of the inliers.
Writes go2/data/anchors.json. Nothing is written to the console: positions are reported on the board for Oliver
to accept (POST /places with a target) or correct.

Results 2026-10-19 (615 frames, 15:58-17:18): the sofa lands within 10 cm of Oliver's mark in every run; the
conference table at (-0.89, 2.92); the water cooler at (1.35, 0.40) from 20 agreeing views, not yet trusted
because 80% of the frames were taken before the 16:54 map fix, when map poses drifted; "workbench" is reported
in 459 of 615 frames (desks look like workbenches), so it needs a better description. Tried first and dropped:
OWLv2 boxes checked by the vision model. OWLv2 never boxed the real black cooler; its candidates were a bucket,
water jugs and a fire extinguisher by the outside door.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import random
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "trail_cache"
CONSOLE = "http://172.17.40.64:8080"
VLM = "http://127.0.0.1:8300/v1/chat/completions"
HFOV = 73.0

SCHEMA = {"type": "object", "properties": {
    "why": {"type": "string", "maxLength": 160},
    "present": {"type": "string", "enum": ["yes", "no"]},
    "centre_x": {"type": "number", "minimum": 0, "maximum": 1},
    "cut_off_at_edge": {"type": "string", "enum": ["yes", "no"]}},
    "required": ["why", "present", "centre_x", "cut_off_at_edge"]}


def fetch():
    """/trail/near returns at most 12 frames within 0.35 m of a point, so query every coverage cell."""
    get = lambda p: json.load(urllib.request.urlopen(CONSOLE + p, timeout=15))
    frames = {}
    with ThreadPoolExecutor(8) as pool:
        for vs in pool.map(lambda c: get(f"/trail/near?x={c[0]}&y={c[1]}").get("views", []), get("/trail/coverage")):
            for v in vs:
                frames[v["url"]] = v
    CACHE.mkdir(parents=True, exist_ok=True)

    def save(v):
        f = CACHE / v["url"].split("/")[-1]
        if not f.exists():
            f.write_bytes(urllib.request.urlopen(CONSOLE + v["url"], timeout=15).read())
    with ThreadPoolExecutor(8) as pool:
        list(pool.map(save, frames.values()))
    (CACHE / "index.json").write_text(json.dumps(list(frames.values())))
    print(f"{len(frames)} frames in {CACHE}")


def look(frame, desc):
    jpg = (CACHE / frame["url"].split("/")[-1]).read_bytes()
    body = {"model": "Qwen/Qwen3.8-27B", "temperature": 0, "max_tokens": 200,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "a", "schema": SCHEMA}},
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpg).decode()}},
                {"type": "text", "text": f"A low robot camera in a university lab. Is {desc} in this picture (not a bucket, "
                                         f"jug or something else that only resembles it)? If yes: where is its centre "
                                         f"across the picture, 0 = left edge, 1 = right edge, and is it cut off at the "
                                         f"left or right edge? If no, give centre_x 0.5. Reason first."}]}]}
    req = urllib.request.Request(VLM, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(json.loads(urllib.request.urlopen(req, timeout=120).read())["choices"][0]["message"]["content"])


def line(d):
    x, y, yaw = d["pose"]
    ang = math.radians(yaw + (0.5 - d["cx"]) * HFOV)        # left of centre = positive (map yaw is counter-clockwise)
    return np.array([x, y]), np.array([math.cos(ang), math.sin(ang)]), ang


def intersect(a, b):
    (p, u, _), (q, v, _) = a, b
    M = np.array([u, -v]).T
    if abs(np.linalg.det(M)) < 1e-3:
        return None
    t, s = np.linalg.solve(M, q - p)
    return p + t * u if (0.3 < t < 5 and 0.3 < s < 5) else None


def dist_to_line(pt, L):
    p, u, _ = L
    w = pt - p
    return abs(u[0] * w[1] - u[1] * w[0]) if w @ u > 0.2 else 1e9


def locate(dets, iters=3000, tol=0.25):
    Ls = [line(d) for d in dets]
    if len(Ls) < 3:
        return None
    rng, best = random.Random(0), None
    for _ in range(iters):
        a, b = rng.sample(range(len(Ls)), 2)
        if abs(math.remainder(Ls[a][2] - Ls[b][2], 2 * math.pi)) < math.radians(15):
            continue
        pt = intersect(Ls[a], Ls[b])
        if pt is None:
            continue
        inl = [i for i, L in enumerate(Ls) if dist_to_line(pt, L) < tol]
        if best is None or len(inl) > len(best):
            best = inl
    if not best:
        return None
    A, bvec = np.zeros((2, 2)), np.zeros(2)
    for i in best:
        p, u, _ = Ls[i]
        P = np.eye(2) - np.outer(u, u)
        A += P
        bvec += P @ p
    pt = np.linalg.solve(A, bvec)
    angs = [Ls[i][2] for i in best]
    return {"x": round(float(pt[0]), 2), "y": round(float(pt[1]), 2), "inliers": len(best), "sightings": len(dets),
            "view_spread_deg": round(math.degrees(max(abs(math.remainder(x - y, 2 * math.pi)) for x in angs for y in angs))),
            "median_miss_m": round(float(np.median([dist_to_line(pt, Ls[i]) for i in best])), 3),
            "inlier_urls": [dets[i]["url"] for i in best]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("things", nargs="*", help='"name=what it looks like"')
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    if a.fetch:
        fetch()
    if not a.things:
        return
    frames = json.loads((CACHE / "index.json").read_text())
    out = {}
    for t in a.things:
        name, desc = t.split("=", 1) if "=" in t else (t, f"a {t}")
        with ThreadPoolExecutor(16) as pool:
            ans = list(pool.map(lambda f: look(f, desc), frames))
        dets = [{"url": f["url"], "cx": r["centre_x"], "pose": [f["x"], f["y"], f["yaw_deg"]], "why": r["why"]}
                for f, r in zip(frames, ans) if r["present"] == "yes" and r["cut_off_at_edge"] == "no"]
        pos = locate(dets)
        out[name] = {"description": desc, "frames_with_it": sum(r["present"] == "yes" for r in ans),
                     "frames": len(frames), "position": pos, "sightings": dets}
        print(name, {k: v for k, v in (pos or {}).items() if k != "inlier_urls"}, flush=True)
    (ROOT / "data" / "anchors.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
