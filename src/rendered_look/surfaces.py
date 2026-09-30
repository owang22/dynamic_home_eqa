"""Finding where things can rest on a piece of furniture, from what the renderer draws.

A camera is put above the furniture looking straight down. Its depth picture
and its picture of object ids give, for every pixel, a point in the world and
the thing that point belongs to. The resting surface is the most common
height among the furniture's own points inside the wanted band. Using the
drawn surface rather than the collision shape means a thing placed at that
height looks placed, which is what the pictures are for.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from rendered_look import home

CELL = 0.02  # metres per cell of the map of the surface


def points_below(sim, eye: np.ndarray, size: int, hfov: float = 90.0):
    """World points and ids seen by a camera at `eye` looking straight down."""
    home.look_from(sim, eye, eye + np.array([0.0, -1.0, 0.0001]))
    seen = sim.get_sensor_observations()
    depth, ids = seen["down_depth"], seen["down_ids"]
    focal = (size / 2) / np.tan(np.radians(hfov) / 2)
    cols, rows = np.meshgrid(np.arange(size) - size / 2 + 0.5, np.arange(size) - size / 2 + 0.5)
    agent = sim.get_agent(0).get_state()
    import quaternion  # noqa: F401  (numpy-quaternion, gives as_rotation_matrix)
    turn = quaternion.as_rotation_matrix(agent.rotation)
    rays = np.stack([cols / focal, -rows / focal, -np.ones_like(cols)], axis=-1)
    world = eye + (rays * depth[..., None]) @ turn.T
    return world, ids, depth


class Surface:
    def __init__(self, place: str, height: float, xz: np.ndarray, clearance: np.ndarray,
                 heights: Optional[np.ndarray] = None) -> None:
        self.place, self.height = place, height
        self.xz, self.clearance = xz, clearance  # usable cell centres, metres to the nearest edge
        self.heights = heights if heights is not None else np.full(len(xz), height)
        self.every_point: Optional[np.ndarray] = None   # x, y, z of all drawn points of the furniture

    def usual_height_under(self, x: float, z: float, radius: float) -> float:
        """The middle height of everything drawn on the furniture under a
        footprint: where a body lying on a bed comes to rest, folds of the
        blanket and all."""
        if self.every_point is None:
            return self.height
        near = np.hypot(self.every_point[:, 0] - x, self.every_point[:, 2] - z) <= radius
        return float(np.median(self.every_point[near, 1])) if near.sum() >= 20 else self.height

    def height_under(self, x: float, z: float, radius: float) -> float:
        """The highest drawn point of the surface under a footprint, so a thing
        rests on a cushion's crown instead of sinking into it."""
        near = np.hypot(self.xz[:, 0] - x, self.xz[:, 1] - z) <= max(radius, CELL * 2)
        return float(self.heights[near].max()) if near.any() else self.height

    def summary(self) -> dict:
        return {"height_m": round(self.height, 3), "usable_cells": int(len(self.xz)),
                "area_m2": round(len(self.xz) * CELL * CELL, 3),
                "widest_clearance_m": round(float(self.clearance.max()) if len(self.xz) else 0.0, 3)}


def find_surface(sim, place: str, thing, band: Tuple[float, float],
                 camera_height: Optional[float] = None, tolerance: float = 0.02,
                 size: int = 512) -> Surface:
    from scipy import ndimage

    low, high = home.world_box(thing)
    centre = (low + high) / 2
    span = max(high[0] - low[0], high[2] - low[2])
    top = band[1] + 0.05
    # high enough to see the whole footprint, unless something above forces it lower
    eye_y = camera_height if camera_height is not None else top + max(0.45, span * 0.62)
    world, ids, depth = points_below(sim, np.array([centre[0], eye_y, centre[2]]), size)
    own = (ids == thing.semantic_id) & (world[..., 1] >= band[0]) & (world[..., 1] <= band[1])
    if own.sum() < 50:
        raise ValueError(f"{place}: only {int(own.sum())} points of the furniture lie in the band "
                         f"{band}; heights seen on it: "
                         f"{np.round(np.percentile(world[..., 1][ids == thing.semantic_id], [5, 50, 95]), 2).tolist() if (ids == thing.semantic_id).any() else 'none'}")
    heights = world[..., 1][own]
    counts, edges = np.histogram(heights, bins=np.arange(band[0], band[1] + 0.011, 0.01))
    best = int(np.argmax(counts))
    height = float((edges[best] + edges[best + 1]) / 2)
    flat = own & (np.abs(world[..., 1] - height) <= tolerance)
    # a map of the surface in world x, z
    x0, z0 = low[0] - 0.1, low[2] - 0.1
    nx, nz = int((high[0] - low[0] + 0.2) / CELL) + 1, int((high[2] - low[2] + 0.2) / CELL) + 1
    grid = np.zeros((nz, nx), dtype=bool)
    gx = ((world[..., 0][flat] - x0) / CELL).astype(int)
    gz = ((world[..., 2][flat] - z0) / CELL).astype(int)
    keep = (gx >= 0) & (gx < nx) & (gz >= 0) & (gz < nz)
    grid[gz[keep], gx[keep]] = True
    tall = np.full((nz, nx), -np.inf)
    np.maximum.at(tall, (gz[keep], gx[keep]), world[..., 1][flat][keep])
    # anything drawn above the surface (a lamp, a back rest, a pillow) blocks the cell under it
    above = (world[..., 1] > height + tolerance + 0.01) & (world[..., 1] < height + 0.6)
    ax = ((world[..., 0][above] - x0) / CELL).astype(int)
    az = ((world[..., 2][above] - z0) / CELL).astype(int)
    keep = (ax >= 0) & (ax < nx) & (az >= 0) & (az < nz)
    blocked = np.zeros_like(grid)
    blocked[az[keep], ax[keep]] = True
    grid = ndimage.binary_closing(grid, iterations=2) & ~ndimage.binary_dilation(blocked, iterations=1)
    clearance = ndimage.distance_transform_edt(grid) * CELL
    cells = np.argwhere(grid)
    xz = np.stack([x0 + (cells[:, 1] + 0.5) * CELL, z0 + (cells[:, 0] + 0.5) * CELL], axis=1)
    cell_heights = tall[grid]
    cell_heights[~np.isfinite(cell_heights)] = height
    found = Surface(place, height, xz, clearance[grid], cell_heights)
    found.every_point = world[own]
    return found


def floor_surface(sim, place: str, near: Tuple[float, float], region: dict,
                  reach: float = 0.9) -> Surface:
    """Floor cells within `reach` of a point, on the walkable floor of the room."""
    xs = np.arange(near[0] - reach, near[0] + reach, CELL * 2)
    zs = np.arange(near[1] - reach, near[1] + reach, CELL * 2)
    cells, gaps = [], []
    floor_y = float(region["floor_height"])
    for x in xs:
        for z in zs:
            if not home.inside(x, z, region["poly_loop"]):
                continue
            point = np.array([x, floor_y, z], dtype=np.float32)
            if not sim.pathfinder.is_navigable(point, 0.3):
                continue
            cells.append((x, z))
            gaps.append(sim.pathfinder.distance_to_closest_obstacle(point, 1.0))
    if not cells:
        raise ValueError(f"{place}: no walkable floor within {reach} m of {near}")
    # the walkable floor stops a robot's radius short of every obstacle, so add that back
    return Surface(place, floor_y, np.array(cells), np.array(gaps) + 0.25)
