"""Walk to a map point when the console's go_to gives up ("blocked" / "no route").

The console plans on its live map, where a low object such as a mop bucket can close an aisle completely (board
#19-#20, 2026-10-22). The saved map still has the aisle, and the dog's own obstacle avoidance can deal with what is
really in the way. So: plan on the saved map (/map.png) with a 0.18 m hard margin and a graded cost (nav_proto.py,
the planner change proposed on board #18), cut the route into straight legs of at most 1.2 m, and walk each leg
with the console's plain turn + move calls (obstacle avoidance stays on). A leg that is blocked is retried by
stepping 35 degrees to one side for 0.4 m and aiming again, then the other side; after that the walk stops and
says where it is.
"""
from __future__ import annotations

import io
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "console"))
import nav_proto as N  # noqa: E402

N.LETHAL = 0.18          # Go2 half-width 0.155 m + 2.5 cm
LEG_M = 1.2
ARRIVE_M = 0.3


def plan(png, meta, start, goal):
    """Waypoints [(x, y)] from start to goal on the saved map, or None. The goal moves to the nearest square it can
    stand on (within 0.8 m) if it is inside the margin."""
    from PIL import Image
    G = N.Grid(np.array(Image.open(io.BytesIO(png)).convert("L")), meta)
    s = G.nearest_ok(G.cell(*start))
    t = G.nearest_ok(G.cell(*goal))
    if s is None or t is None:
        return None
    g = G.dijkstra(s)
    if not np.isfinite(g[t]):
        return None
    cells = [t]                                   # walk back downhill from the goal to the start
    steps = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    while cells[-1] != s and len(cells) < 5000:
        i, j = cells[-1]
        nb = [(g[i + di, j + dj], (i + di, j + dj)) for di, dj in steps
              if 0 <= i + di < G.H and 0 <= j + dj < G.W]
        cells.append(min(nb)[1])
    cells.reverse()
    # straight legs: keep the furthest cell still in clear sight of the last waypoint, at most LEG_M away
    pts, k = [cells[0]], 0
    while k < len(cells) - 1:
        best = k + 1
        for m in range(k + 1, len(cells)):
            if math.dist(cells[k], cells[m]) * N.RES > LEG_M or not clear(G, cells[k], cells[m]):
                break
            best = m
        pts.append(cells[best])
        k = best
    return [G.xy(*c) for c in pts[1:]]


def clear(G, a, b):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for t in np.linspace(0, 1, n):
        if not G.ok((int(round(a[0] + t * (b[0] - a[0]))), int(round(a[1] + t * (b[1] - a[1]))))):
            return False
    return True


def walk(agent, pose, waypoints, yaw_deg=None, log=None):
    """agent(name, **args) calls the console; pose() -> {x, y, yaw (rad)}. Returns (reached, notes)."""
    notes = log if log is not None else []
    for wx, wy in waypoints:
        side = 1
        for attempt in range(4):
            p = pose()
            d = math.hypot(wx - p["x"], wy - p["y"])
            if d < ARRIVE_M:
                break
            turn = (math.degrees(math.atan2(wy - p["y"], wx - p["x"]) - p["yaw"]) + 180) % 360 - 180
            if abs(turn) > 8:
                agent("turn", deg=round(turn, 1))
            r = agent("move", m=round(min(d, 1.5), 2))
            moved = r.get("moved_m") or 0
            notes.append(f"leg to ({wx:.2f}, {wy:.2f}): {r.get('result')} after {moved} m")
            if r.get("result") == "done" or moved >= 0.8 * min(d, 1.5):
                continue
            # blocked: step aside and aim again (first one side, then the other)
            agent("turn", deg=35 * side)
            s = agent("move", m=0.4)
            notes.append(f"  stepped {'left' if side > 0 else 'right'}: {s.get('result')} after {s.get('moved_m')} m")
            side = -side
        else:
            p = pose()
            if math.hypot(wx - p["x"], wy - p["y"]) >= ARRIVE_M:
                notes.append(f"gave up at ({p['x']:.2f}, {p['y']:.2f}), {math.hypot(wx - p['x'], wy - p['y']):.2f} m short of a waypoint")
                return False, notes
    if yaw_deg is not None:
        p = pose()
        turn = (yaw_deg - math.degrees(p["yaw"]) + 180) % 360 - 180
        if abs(turn) > 8:
            agent("turn", deg=round(turn, 1))
    return True, notes
