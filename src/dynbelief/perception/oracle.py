"""Stage 0.2 — OraclePerceiver.

An object is perceived iff:
  (a) it lies inside the FOV cone from the pose (XZ plane),
  (b) it is within range d_max, and
  (c) the camera->object-center ray is unobstructed.

Occlusion is evaluated against COLLISION PROXIES, never visual meshes: the
ray is walked across the scene's top-down occupancy grid (the same
navmesh-derived grid the rest of this repo treats as physical truth —
non-navigable cells are walls and furniture footprints). Rule: the ray is
blocked iff it crosses a contiguous non-navigable run of >= `block_run_m`
BEFORE the final `tail_m` of the ray. The tail allowance exists because a
perceived object legitimately SITS ON furniture — the last half-metre of the
ray always enters the supporting furniture's own footprint, and that must
not count as occlusion. Walls (and any intervening furniture deeper than
block_run_m) do.

Object positions come from logged ground truth via ReplayWorld: an object's
position at t is its parent receptacle's census position (objects at
ELSEWHERE are nowhere and are never perceived). On perceive, identity /
parent / states are read from ground truth — the oracle never guesses.

360-degree option: fov_deg=360 turns the cone check off (a viewpoint visit
that sweeps in place), which is the fallback viewpoints' intended use since
their yaw is not curated.
"""
from __future__ import annotations

import math

from dynbelief import ELSEWHERE_ID
from dynbelief.perception.base import Pose


class OraclePerceiver:
    def __init__(self, world, fov_deg: float = 360.0, d_max: float = 5.0,
                 block_run_m: float = 0.5, tail_m: float = 0.8) -> None:
        from dynamic_home_eqa.topdown_map import load_topdown_map
        self.world = world
        self.fov_rad = math.radians(fov_deg)
        self.d_max = d_max
        self.block_run_m = block_run_m
        self.tail_m = tail_m
        self._td = load_topdown_map(world.scene_id)
        # receptacle positions cached once (registry census positions)
        self._recep_pos = {rid: world.position_of(rid)
                           for rid in world.receptacles(include_elsewhere=False)}

    # ── geometry ──────────────────────────────────────────────────────────────
    def _in_fov(self, pose: Pose, x: float, z: float) -> bool:
        if self.fov_rad >= 2 * math.pi - 1e-9:
            return True
        ang = math.atan2(z - pose.z, x - pose.x)
        d = (ang - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        return abs(d) <= self.fov_rad / 2

    def ray_unobstructed(self, x0: float, z0: float, x1: float, z1: float) -> bool:
        """Grid-walk the XZ segment; blocked iff a contiguous non-navigable
        run >= block_run_m occurs before the final tail_m (module docstring)."""
        td = self._td
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 1e-6:
            return True
        step = td.meters_per_pixel * 0.5
        n = max(1, int(length / step))
        run = 0.0
        for i in range(n + 1):
            s = i * step
            if s > length - self.tail_m:
                break
            fx = x0 + (x1 - x0) * (s / length)
            fz = z0 + (z1 - z0) * (s / length)
            r, c = td.world_to_pixel(fx, fz)
            navigable = td.is_in_bounds(r, c) and bool(td.grid[r, c])
            if navigable:
                run = 0.0
            else:
                run += step
                if run >= self.block_run_m:
                    return False
        return True

    # ── Perceiver protocol ────────────────────────────────────────────────────
    def observe(self, pose: Pose, t_min: int) -> dict[int, tuple[int, dict]]:
        state = self.world.state_at(t_min)
        out: dict[int, tuple[int, dict]] = {}
        for obj_id, (parent_id, states) in state.items():
            if parent_id == ELSEWHERE_ID:
                continue
            pos = self._recep_pos.get(parent_id)
            if pos is None:
                continue
            x, z = pos[0], pos[2]
            if math.hypot(x - pose.x, z - pose.z) > self.d_max:
                continue
            if not self._in_fov(pose, x, z):
                continue
            if not self.ray_unobstructed(pose.x, pose.z, x, z):
                continue
            out[obj_id] = (parent_id, dict(states))
        return out

    def current_room(self, pose: Pose) -> str | None:
        """Nearest receptacle's room, restricted to receptacles with an
        unobstructed short ray — a cheap, render-free room id."""
        best, best_d = None, float("inf")
        for rid, pos in self._recep_pos.items():
            if pos is None:
                continue
            d = math.hypot(pos[0] - pose.x, pos[2] - pose.z)
            if d < best_d and self.ray_unobstructed(pose.x, pose.z, pos[0], pos[2]):
                best, best_d = rid, d
        return self.world.room_of(best) if best is not None else None
