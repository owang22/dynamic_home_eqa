"""Choose one fixed robot viewpoint per open spot of household A, from the empty home.

    ~/miniconda3/envs/dynamic_eqa/bin/python choose_views.py

Which spots: every place whose kind is "surface" or "open" (tables, counters, seats, shelves,
floors, sinks, the bathtub, the fireplace opening). Closed places (drawers, cabinets, the
washing-machine drums, compartments) are left out: their insides cannot be seen from outside.

How a stand is scored (no snapshot object is in the scene, so the choice does not depend on
what lies on the spot on any day):
  1. The spot's surface is found by the committed scanner (scene.Home.grid_for): 2 cm cells
     of the spot's furniture (or the room's floor) at the spot height, seen from above.
  2. Up to 600 of those cells become test points 4 cm above the surface, where a small object
     lying there would be. For open places (sinks, the bathtub, the fireplace opening) the
     points are 12 cm above the bottom: from 1.0 m the bottom of a basin is hidden by its near
     rim, and what can be seen is the top of what stands in it (a mug, a stack of plates).
  3. Candidate stands: walkable floor (navmesh, 0.2 m body radius), rings 0.6 m to 3.5 m (to
     6 m for floors) around the middle of the points, 0.15 m apart, 24 bearings. Eye at 1.0 m,
     75 deg horizontal lens, aimed at the middle of the points with tilt limited to 60 deg down
     and 30 deg up.
  4. A test point counts as seen when it projects inside the picture (2% margin) and nothing is
     drawn in front of it (depth picture 320x240, tolerance 2 cm + 1% of the distance).
  5. Score = mean over test points of seen x min(1, (near / distance)^2) x slant, where
     near = 1.3 m (2.5 m for floors, where things are bigger and the room matters) and
     slant = min(1, 0.25 + 0.75 sin(angle down onto the point) / sin 25 deg): the share of the
     surface seen, with far points counted less (fewer pixels) and points seen nearly edge-on
     counted less (a flat thing there shows as a sliver). A point level with or above the eye
     keeps slant 0.25, so high shelves are not ruled out.
     Near-equal scores (within 0.01) prefer a stand about 1.2 m away, so some furniture shows.
A spot is skipped when its best stand sees under 5% of its test points.

Writes spot_views.json here, and for checking, under PICS/spot_views/: the empty-home picture
of each view, and a copy with the test points drawn (green seen, red not seen).
"""
from __future__ import annotations

import math
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

import lib

SMALL_W, SMALL_H = 320, 240
OFFSET = 0.04
OFFSET_OPEN = 0.12
MAX_POINTS = 600


def walkable(home, x, z):
    q = home.sim.pathfinder.snap_point(np.array([x, 0.17, z], dtype=np.float32))
    return bool(np.isfinite(q[0]) and math.hypot(q[0] - x, q[2] - z) < 0.03 and abs(q[1] - 0.17) < 0.1)


def test_points(home, place):
    g = home.snap["places"][place]["geometry"]
    lift = OFFSET_OPEN if home.snap["places"][place]["kind"] == "open" else OFFSET
    grid = home.grid_for(place)
    ii, jj = np.nonzero(grid.valid)
    how = "scanned surface cells"
    if len(ii) >= 5:
        xs, zs = grid.x0 + (jj + 0.5) * lib.scene.CELL, grid.z0 + (ii + 0.5) * lib.scene.CELL
        ys = grid.heights[ii, jj]
        pts = np.stack([xs, ys + lift, zs], 1)
    else:
        # nothing found by the scan: a disc of the spot's area around its centre
        c, r = np.array(g["center"]), math.sqrt(max(g["area"], 0.01) / math.pi)
        a = np.linspace(0, 2 * math.pi, 24, endpoint=False)
        pts = [c + [0, lift, 0]] + [c + [rr * math.cos(t), lift, rr * math.sin(t)]
                                      for rr in (r / 2, r) for t in a]
        pts = np.array(pts)
        how = "disc around the spot centre (the scan found no surface cells)"
    if len(pts) > MAX_POINTS:
        pick = np.random.default_rng(0).choice(len(pts), MAX_POINTS, replace=False)
        pts = pts[np.sort(pick)]
    area = float(grid.valid.sum() * lib.scene.CELL ** 2)
    return pts, how, area


def seen_mask(home, pts, eye, look):
    lib.common.look_from(home.sim, eye, look)
    depth = home.shoot("v_depth")["v_depth"]
    turn = lib.camera_frame(home)
    col, row, z = lib.project(pts, eye, turn, SMALL_W, SMALL_H)
    m = 0.02
    inside = (z > 0.1) & (col >= SMALL_W * m) & (col < SMALL_W * (1 - m)) & (row >= SMALL_H * m) & (row < SMALL_H * (1 - m))
    seen = np.zeros(len(pts), bool)
    k = np.flatnonzero(inside)
    c, r = col[k].astype(int), row[k].astype(int)
    d = depth[r, c]
    seen[k] = d >= z[k] - (0.02 + 0.01 * z[k])
    enclosed = float((depth < 0.25).mean())
    return seen, enclosed


def choose(home, place, pts):
    centre = pts.mean(0)
    floor = home.snap["places"][place]["furniture"] == "floor"
    far = 6.0 if floor else 3.5
    near = 2.5 if floor else 1.3     # floors: things there are bigger (shoes, bags, baskets)
    best, tried = None, 0
    for d in np.arange(0.6, far + 0.01, 0.15):
        for b in np.arange(0, 2 * math.pi, math.pi / 12):
            x, z = centre[0] + d * math.sin(b), centre[2] + d * math.cos(b)
            if not walkable(home, x, z):
                continue
            eye = np.array([x, lib.EYE_HEIGHT, z])
            look, yaw, pitch = lib.aim(eye, centre)
            seen, enclosed = seen_mask(home, pts, eye, look)
            tried += 1
            if enclosed > 0.3:
                continue
            dist = np.linalg.norm(pts - eye, axis=1)
            elev = np.clip((eye[1] - pts[:, 1]) / dist, 0.0, 1.0)     # sine of the angle down onto the surface
            score = float(np.mean(seen * np.minimum(1.0, (near / dist) ** 2)
                                  * np.minimum(1.0, 0.25 + 0.75 * elev / math.sin(math.radians(25)))))
            key = (round(score, 2), -abs(d - 1.2))
            if best is None or key > best["key"]:
                best = dict(key=key, score=score, seen_share=float(seen.mean()), eye=eye, look=look,
                            yaw=yaw, pitch=pitch, d=float(d), seen=seen)
    return best, tried, centre


def main():
    t0 = time.time()
    cams = [dict(uuid="v_depth", kind="depth", width=SMALL_W, height=SMALL_H, hfov=lib.HFOV),
            dict(uuid="v_colour", kind="colour", width=lib.W, height=lib.H, hfov=lib.HFOV)]
    home = lib.open_home(lib.snapshot_path(7, "1800"), cams)
    out_pics = lib.PICS / "spot_views"
    out_pics.mkdir(parents=True, exist_ok=True)
    places = home.snap["places"]
    spots = sorted(p for p, v in places.items() if v["kind"] in ("surface", "open"))
    closed = sorted(p for p, v in places.items() if v["kind"] not in ("surface", "open"))
    views, skipped = [], []
    for n, place in enumerate(spots):
        p = places[place]
        t1 = time.time()
        pts, how, area = test_points(home, place)
        best, tried, centre = choose(home, place, pts)
        if best is None or best["seen_share"] < 0.05:
            skipped.append({"spot": place, "room": p["room"], "spot_name": lib.spot_title(p),
                            "reason": "no walkable stand at 1.0 m sees the surface" if best is None else
                            f"best stand sees only {best['seen_share']:.0%} of the surface's test points",
                            "test_points": len(pts), "stands_tried": tried, "test_points_from": how})
            print(f"[{n + 1}/{len(spots)}] SKIP {place}: {skipped[-1]['reason']}", flush=True)
            continue
        lib.common.look_from(home.sim, best["eye"], best["look"])
        colour = home.shoot("v_colour")["v_colour"][:, :, :3]
        Image.fromarray(colour).save(out_pics / f"{place}.jpg", quality=90)
        turn = lib.camera_frame(home)
        col, row, z = lib.project(pts, best["eye"], turn, lib.W, lib.H)
        im = Image.fromarray(colour.copy())
        dr = ImageDraw.Draw(im)
        for c, r, zz, s in zip(col, row, z, best["seen"]):
            if zz > 0 and 0 <= c < lib.W and 0 <= r < lib.H:
                dr.ellipse([c - 2, r - 2, c + 2, r + 2], fill=(40, 220, 40) if s else (230, 30, 30))
        im.save(out_pics / f"{place}_points.jpg", quality=85)
        views.append({
            "spot": place, "room": p["room"], "spot_name": lib.spot_title(p),
            "furniture": p["furniture"], "place_name": p["name"], "kind": p["kind"],
            "eye": [round(float(v), 3) for v in best["eye"]],
            "target": [round(float(v), 3) for v in best["look"]],
            "middle_of_surface": [round(float(v), 3) for v in centre],
            "yaw_deg": round(best["yaw"], 1), "pitch_deg": round(best["pitch"], 1),
            "metres_from_middle": round(best["d"], 2),
            "surface_share_seen": round(best["seen_share"], 3), "score": round(best["score"], 3),
            "scanned_area_m2": round(area, 3), "snapshot_area_m2": p["geometry"]["area"],
            "test_points": len(pts), "test_points_from": how, "stands_tried": tried,
            "test_point_height_above_surface_m": OFFSET_OPEN if p["kind"] == "open" else OFFSET,
        })
        print(f"[{n + 1}/{len(spots)}] {place}: seen {best['seen_share']:.0%} score {best['score']:.2f} "
              f"d {best['d']:.2f} pitch {best['pitch']:.0f} ({time.time() - t1:.1f}s)", flush=True)
    out = {
        "scene": lib.common.SCENE,
        "coordinates": "habitat world: y up, metres; floors at y = 0",
        "camera": {"width": lib.W, "height": lib.H, "hfov_deg": lib.HFOV, "eye_height_m": lib.EYE_HEIGHT,
                   "how_to_aim": "habitat_sim agent at eye, looking at target, up = +y (common.look_from)"},
        "rule": __doc__,
        "views": views,
        "skipped": skipped,
        "closed_places_not_viewed": closed,
        "seconds": round(time.time() - t0, 1),
    }
    lib.json_dump(out, lib.SPOT_VIEWS)
    lib.json_dump(out, lib.PICS / "spot_views.json")
    print(f"{len(views)} views, {len(skipped)} skipped, {len(closed)} closed places, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
