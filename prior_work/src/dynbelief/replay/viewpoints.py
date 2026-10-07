"""Stage 0.3 — viewpoints.

Loads `viewpoints.json` from the episode dir when the sim team supplies one:
  [{"vp_id", "position": [x,y,z], "yaw": rad,
    "visible_slots": [receptacle_ids], "travel_min": {vp_id: float}}]

Fallback (this repo IS the sim team, and no curated file exists yet): one
viewpoint per room at the room's navigable centroid. visible_slots = the
receptacles whose census room matches — the brief allows visible_slots to be
precomputed via oracle raycasts; room membership is the coarse first cut, and
the OraclePerceiver remains the runtime authority on what is actually seen.
travel_min uses shortest-path distance on the top-down navigable grid (BFS —
respects walls, i.e. the same collision proxy perception uses), at 1.0 m/s
walking speed, falling back to euclidean if the grid disconnects two rooms.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib

import numpy as np

_WALK_M_PER_MIN = 60.0  # 1.0 m/s


class Viewpoints:
    def __init__(self, entries: list[dict]) -> None:
        self._by_id = {e["vp_id"]: e for e in entries}

    def ids(self) -> list[str]:
        return sorted(self._by_id)

    def get(self, vp_id: str) -> dict:
        return self._by_id[vp_id]

    def visible_from(self, vp_id: str) -> list[int]:
        return list(self._by_id[vp_id]["visible_slots"])

    def travel(self, a: str, b: str) -> float:
        if a == b:
            return 0.0
        return float(self._by_id[a]["travel_min"][b])

    @classmethod
    def load(cls, episode_dir: str | pathlib.Path, world=None) -> "Viewpoints":
        p = pathlib.Path(episode_dir) / "viewpoints.json"
        if p.exists():
            return cls(json.loads(p.read_text()))
        assert world is not None, "no viewpoints.json — need world for fallback"
        entries = one_per_room(world)
        p.write_text(json.dumps(entries, indent=1))  # cache for reproducibility
        return cls(entries)


def _grid_bfs_dist_m(grid, meters_per_pixel: float,
                     start: tuple[int, int], goals: dict[str, tuple[int, int]]) -> dict[str, float]:
    """Shortest navigable-grid distance (meters) from start to each goal
    cell; math.inf where unreachable."""
    H, W = grid.shape
    dist = np.full((H, W), -1.0)
    q = collections.deque()
    if 0 <= start[0] < H and 0 <= start[1] < W and grid[start]:
        dist[start] = 0.0
        q.append(start)
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < H and 0 <= cc < W and grid[rr, cc] and dist[rr, cc] < 0:
                dist[rr, cc] = dist[r, c] + 1
                q.append((rr, cc))
    out = {}
    for k, (r, c) in goals.items():
        d = dist[r, c] if (0 <= r < H and 0 <= c < W) else -1.0
        out[k] = float(d * meters_per_pixel) if d >= 0 else math.inf
    return out


def _nearest_navigable(grid, cell: tuple[int, int], max_r: int = 20) -> tuple[int, int]:
    """Room centroids can land inside a furniture footprint; snap to the
    nearest navigable cell within max_r pixels."""
    r0, c0 = cell
    if 0 <= r0 < grid.shape[0] and 0 <= c0 < grid.shape[1] and grid[r0, c0]:
        return cell
    for rad in range(1, max_r + 1):
        for dr in range(-rad, rad + 1):
            for dc in (-rad, rad) if abs(dr) < rad else range(-rad, rad + 1):
                rr, cc = r0 + dr, c0 + dc
                if 0 <= rr < grid.shape[0] and 0 <= cc < grid.shape[1] and grid[rr, cc]:
                    return rr, cc
    return cell


def one_per_room(world) -> list[dict]:
    """Fallback viewpoint set: one per room, at the room's navigable
    centroid, yaw 0 (the OraclePerceiver may sweep yaw; see its docstring)."""
    from dynamic_home_eqa.topdown_map import load_topdown_map, room_centroids

    td = load_topdown_map(world.scene_id)
    cents = room_centroids(world.scene_id)
    recs_by_room: dict[str, list[int]] = {}
    for rid in world.receptacles(include_elsewhere=False):
        room = world.room_of(rid)
        if room:
            recs_by_room.setdefault(room, []).append(rid)

    vp_cells: dict[str, tuple[int, int]] = {}
    entries = []
    for room in sorted(cents):
        if room not in recs_by_room:
            continue  # a room with no tracked receptacle offers nothing to see
        x, z = cents[room]
        cell = _nearest_navigable(td.grid, td.world_to_pixel(x, z))
        vp_cells[f"vp_{room}"] = cell
        wx = td.bounds_min[0] + cell[1] * td.meters_per_pixel
        wz = td.bounds_min[2] + cell[0] * td.meters_per_pixel
        entries.append({"vp_id": f"vp_{room}", "room": room,
                        "position": [float(wx), 0.0, float(wz)], "yaw": 0.0,
                        "visible_slots": sorted(recs_by_room[room])})

    for e in entries:
        dists = _grid_bfs_dist_m(td.grid, td.meters_per_pixel,
                                 vp_cells[e["vp_id"]], vp_cells)
        travel = {}
        for other in entries:
            d = dists[other["vp_id"]]
            if math.isinf(d):  # grid-disconnected rooms: euclidean fallback
                dx = e["position"][0] - other["position"][0]
                dz = e["position"][2] - other["position"][2]
                d = math.hypot(dx, dz)
            travel[other["vp_id"]] = round(d / _WALK_M_PER_MIN, 3)
        e["travel_min"] = travel
    return entries
