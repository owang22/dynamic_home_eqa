"""Offline prototype of two planner changes proposed to the control PC (board #18), on the console's saved map
(no robot): a graded clearance cost instead of one hard 28 cm cut-off, and choosing where to stand from the
object's position. Its Grid class is also what view_plan.py and lab_round.py --views use.

    python3 go2/console/nav_proto.py [--map map.png --places places.json]   (default: fetch both from the console)

1. Cost grid (as in the ROS 2 Nav2 inflation layer): cells closer than LETHAL to an obstacle cannot be entered;
   between LETHAL and INFLATE the cost falls off exponentially, so the route keeps to the middle of an aisle but
   can still pass a gap only a little wider than the dog. A*, 8-connected, cost = length x (1 + weight x cost).
2. Stand selection: candidate standing spots on rings 0.6-1.4 m around the object's target point, every 15 deg;
   keep those that are enterable, have a clear straight line of sight to the target on the map, and are reachable
   from the dog; pick the one with the lowest (route cost + a penalty for low clearance + distance from 1.0 m).
   The dog stands there facing the target.
Writes go2/data/nav_proto/nav_proto.png (map, saved stands, chosen stands) and nav_proto.json.
Result on the 16:54 map: 12 of 16 saved stands reachable from desk_oliver (the 28 cm rule blocks most of them).
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

BASE = "http://172.17.40.64:8080"
RES = 0.05
LETHAL = 0.20       # Go2 half-width ~0.155 m + 4.5 cm margin: closer than this the body would touch
INFLATE = 0.55      # beyond this, no extra cost
DECAY = 6.0         # cost = exp(-DECAY * (d - LETHAL)) between LETHAL and INFLATE
WEIGHT = 3.0


def load(args):
    if args.map:
        im = np.array(Image.open(args.map).convert("L"))
        places = json.loads(Path(args.places).read_text())
        meta = json.loads(Path(args.meta).read_text())
    else:
        im = np.array(Image.open(urllib.request.urlopen(BASE + "/map.png", timeout=10)).convert("L"))
        places = json.load(urllib.request.urlopen(BASE + "/places", timeout=10))
        meta = json.load(urllib.request.urlopen(BASE + "/state.json", timeout=10))["map"]
    return im, places, meta


class Grid:
    def __init__(self, im, meta):
        self.im, self.H, self.W = im, *im.shape
        self.ox, self.oy = meta["origin"]
        self.occ = im == 0
        self.free = im == 254
        self.dist = ndi.distance_transform_edt(~self.occ) * RES
        d = self.dist
        cost = np.where(d < LETHAL, np.inf, np.where(d < INFLATE, np.exp(-DECAY * (d - LETHAL)), 0.0))
        self.cost = np.where(self.free, cost, np.inf)          # unknown and occupied cannot be entered

    def cell(self, x, y):
        return int(round(self.H - 1 - (y - self.oy) / RES)), int(round((x - self.ox) / RES))

    def xy(self, i, j):
        return self.ox + j * RES, self.oy + (self.H - 1 - i) * RES

    def ok(self, c):
        i, j = c
        return 0 <= i < self.H and 0 <= j < self.W and np.isfinite(self.cost[i, j])

    def nearest_ok(self, c, max_m=0.8):
        """The start cell may be inside the cost margin (dog next to furniture): step out to the nearest cell
        that can be entered, as Nav2 does when the robot starts in an inflated cell."""
        if self.ok(c):
            return c
        best = None
        r = int(max_m / RES)
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                n = (c[0] + di, c[1] + dj)
                if self.ok(n) and (best is None or di * di + dj * dj < best[0]):
                    best = (di * di + dj * dj, n)
        return best[1] if best else None

    def dijkstra(self, start):
        """Route cost from start to every cell (one search serves all candidate stands)."""
        g = np.full(self.cost.shape, np.inf)
        g[start] = 0
        pq = [(0.0, start)]
        steps = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
        while pq:
            gc, (i, j) = heapq.heappop(pq)
            if gc > g[i, j]:
                continue
            for di, dj, L in steps:
                n = (i + di, j + dj)
                if not self.ok(n):
                    continue
                ng = gc + L * RES * (1 + WEIGHT * self.cost[n])
                if ng < g[n]:
                    g[n] = ng
                    heapq.heappush(pq, (ng, n))
        return g

    def line_of_sight(self, a, b):
        """No occupied cell on the straight line from a to b, except within 0.15 m of b (the object itself)."""
        (i0, j0), (i1, j1) = a, b
        n = int(max(abs(i1 - i0), abs(j1 - j0))) + 1
        for t in np.linspace(0, 1, n):
            i, j = int(round(i0 + t * (i1 - i0))), int(round(j0 + t * (j1 - j0)))
            if math.hypot(i - i1, j - j1) * RES < 0.15:
                return True
            if self.occ[i, j]:
                return False
        return True


def choose_stand(G, g, target):
    tc = G.cell(target["x"], target["y"])
    best = None
    for r in (0.6, 0.8, 1.0, 1.2, 1.4):
        for a in range(0, 360, 15):
            x = target["x"] + r * math.cos(math.radians(a))
            y = target["y"] + r * math.sin(math.radians(a))
            c = G.cell(x, y)
            if not G.ok(c) or not np.isfinite(g[c]) or not G.line_of_sight(c, tc):
                continue
            # where to stand should not depend on where the dog happens to start: clearance and a ~0.9 m view
            # distance decide; route cost only breaks ties
            score = 2.0 * max(0.0, 0.45 - G.dist[c]) + 0.6 * abs(r - 0.9) + 0.02 * g[c]
            if best is None or score < best[0]:
                yaw = math.degrees(math.atan2(target["y"] - y, target["x"] - x))
                best = (score, {"x": round(x, 2), "y": round(y, 2), "yaw_deg": round(yaw, 1), "dist_to_target_m": r,
                                "clearance_m": round(float(G.dist[c]), 2), "route_cost": round(float(g[c]), 2)})
    return best[1] if best else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map")
    ap.add_argument("--places")
    ap.add_argument("--meta")
    ap.add_argument("--start", default="desk_oliver", help="place whose stand is the start, or x,y")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "data" / "nav_proto"))
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    im, places, meta = load(a)
    G = Grid(im, meta)
    sx, sy = (places[a.start]["x"], places[a.start]["y"]) if a.start in places else map(float, a.start.split(","))
    s = G.nearest_ok(G.cell(sx, sy))
    g = G.dijkstra(s)
    out = {}
    for pid, p in places.items():
        stand_saved = G.cell(p["x"], p["y"])
        row = {"saved_stand_clearance_m": round(float(G.dist[stand_saved]), 2),
               "saved_stand_reachable": bool(G.ok(stand_saved) and np.isfinite(g[stand_saved]))}
        if p.get("target"):
            row["chosen_stand"] = choose_stand(G, g, p["target"])
        out[pid] = row
    Path(a.out, "nav_proto.json").write_text(json.dumps(out, indent=1))
    rgb = Image.fromarray(np.stack([im] * 3, -1)).resize((G.W * 3, G.H * 3), Image.NEAREST)
    d = ImageDraw.Draw(rgb)
    P = lambda x, y: ((x - G.ox) / RES * 3, (G.H - 1 - (y - G.oy) / RES) * 3)
    for pid, p in places.items():
        q = P(p["x"], p["y"])
        d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], outline=(220, 30, 30), width=2)
        if p.get("target"):
            t = P(p["target"]["x"], p["target"]["y"])
            d.rectangle([t[0] - 3, t[1] - 3, t[0] + 3, t[1] + 3], fill=(120, 0, 160))
            c = out[pid].get("chosen_stand")
            if c:
                q2 = P(c["x"], c["y"])
                d.ellipse([q2[0] - 5, q2[1] - 5, q2[0] + 5, q2[1] + 5], fill=(20, 160, 60))
                d.line([q2, t], fill=(20, 160, 60), width=2)
        d.text((q[0] + 6, q[1] - 6), pid, fill=(180, 0, 0))
    rgb.save(Path(a.out, "nav_proto.png"))
    for pid, r in out.items():
        print(pid, r)


if __name__ == "__main__":
    main()
