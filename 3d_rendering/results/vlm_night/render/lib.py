"""Shared pieces for rendering household A's snapshots at fixed robot viewpoints.

Imports the committed habitat_hssd renderer (scripts/common.py, scripts/scene.py) without
editing it. The snapshot file is chosen by setting common.SNAPSHOT before a Home is built.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

REPO = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
HABITAT_SCRIPTS = REPO / "3d_rendering/results/render_methods/habitat_hssd/scripts"
sys.path.insert(0, str(HABITAT_SCRIPTS))
import common  # noqa: E402
import scene  # noqa: E402

CODE = pathlib.Path(__file__).resolve().parent
RUN = REPO / "3d_rendering/results/lived_home/hssd_a"
PICS = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a")
SPOT_VIEWS = CODE / "spot_views.json"

W, H, HFOV = 640, 480, 75.0
EYE_HEIGHT = 1.0          # metres above the floor (floors are at y = 0 in this home)
MAX_DOWN, MAX_UP = 60.0, 30.0
VISIBLE_PX = 30
PERSON_RELATIONS = ("worn_by", "held_by", "in_pocket_of")


def snapshot_path(day: int, hhmm: str) -> pathlib.Path:
    return RUN / f"day_{day:02d}" / f"positions_{hhmm}.json"


def all_snapshots():
    out = []
    for d in sorted(RUN.glob("day_*")):
        for f in sorted(d.glob("positions_[0-9][0-9][0-9][0-9].json")):
            out.append((int(d.name[4:]), f.stem.split("_")[1]))
    return out


def spot_title(place: dict) -> str:
    room = place["room"].replace("_", " ")
    return f"{place['name']} ({place['furniture']}, {room})" if place["furniture"] != "floor" \
        else f"{place['name']} ({room})"


class SnapshotHome(scene.Home):
    """scene.Home for any snapshot, with two fixes the day-7 18:00 snapshot did not need:
    objects out of the house (place None) and objects held by a person, or resting on or in
    something a person wears, holds or pockets, are not drawn and are recorded as such."""

    def place_one(self, oid, under_of):
        objs = self.snap["objects"]
        o = objs[oid]
        rec = self.records[oid]
        if o["place"] is None or o["place"] not in self.snap["places"]:
            rec.update(placed=False, why=f"out of the house (room {o.get('room')})")
            if oid in self.things:
                self.park(oid)
            return
        seen, cur = set(), oid
        while objs[cur]["reference_kind"] == "object" and cur not in seen:
            seen.add(cur)
            cur = objs[cur]["reference"]
        root = objs[cur]
        if root["relation"] in PERSON_RELATIONS:
            how = root["relation"].replace("_", " ")
            why = f"{how} {root['reference']}" if cur == oid else \
                f"{o['relation']} {o['reference']}, which is {how} {root['reference']}"
            rec.update(placed=False, why=f"with a person, not drawn: {why}")
            if oid in self.things:
                self.park(oid)
            return
        super().place_one(oid, under_of)

    def rest_height(self, x, z, hx, hz, above, centre_only=False, place=None):
        """Same as scene.Home.rest_height, except that a point of the spot's furniture counts
        only when it is at most 10 cm above the spot's height. The committed rule let any
        point of the furniture count, so on a shelf under a desk top (the office desk shelf,
        0.65 m, under the top, 0.79 m) the down camera met the desk top first and things meant
        for the shelf were drawn lying on the desk top. 10 cm leaves room for a cushion's
        bulge. Likewise a placed thing counts only when the snapshot puts it on the same spot,
        so a thing can be stacked on its neighbours but not on the things on a surface above."""
        world, sid = self.down_points(np.array([x, above, z]))
        if centre_only:
            r = 0.35 * min(hx, hz)
            m = np.hypot(world[..., 0] - x, world[..., 2] - z) <= max(r, 0.015)
        else:
            m = (np.abs(world[..., 0] - x) <= hx) & (np.abs(world[..., 2] - z) <= hz)
        allowed = (sid >= scene.FIRST_THING) & (sid < scene.FIRST_PERSON)
        if place is not None:
            same_spot = [f["sid"] for oid, f in self.facts.items()
                         if self.snap["objects"][oid]["place"] == place and self.records[oid].get("placed")]
            allowed = np.isin(sid, same_spot)
            g = self.snap["places"][place]["geometry"]
            if g["source"].startswith("region"):
                allowed |= (sid == 0) & (world[..., 1] < g["height"] + 0.05)
            else:
                spot_y = self.grids[place].y if place in self.grids else g["height"]
                allowed |= np.isin(sid, list(self.ids_of(self.furniture_of(place)))) & \
                    (world[..., 1] <= spot_y + 0.10)
        else:
            allowed |= True
        ys = world[..., 1][m & allowed]
        ys = ys[np.isfinite(ys)]
        return float(np.percentile(ys, 98)) if len(ys) else None

    def _place_closed(self, oid, place, hx, hz, hy, base_obj):
        """Same as scene.Home._place_closed, except in a drawer: the committed code accepts a
        resting height up to 0.3 m above the drawer bottom, so when a drawer is full the
        highest drawn point over the footprint (the countertop, or the drawer above) won, and
        tongs ended up lying on the kitchen counter. Here a thing in a drawer rests at most
        8 cm above the drawer bottom (on another thing in the drawer), else on the bottom."""
        if base_obj is not None or not self.is_drawer(place):
            return super()._place_closed(oid, place, hx, hz, hy, base_obj)
        rec = self.records[oid]
        g = self.snap["places"][place]["geometry"]
        if place not in self.open_move:
            self.open_part(place, 1.0)
            self.opened_for_placing.append(place)
        grid = self.grid_for(place)
        spot = self._free_spot(grid, oid, hx, hz, None, need=0.999) if grid.valid.any() else None
        if spot is None:
            rec.update(placed=False, why="no cells found on the opened drawer's bottom")
            self.park(oid)
            return
        x, z, share = spot
        top = self.rest_height(x, z, hx, hz, grid.y + 0.25, place=place)
        y = top if top is not None and grid.y - 0.03 <= top <= grid.y + 0.08 else grid.y
        self.set_at(oid, x, y, z)
        rec.update(placed=True, how="inside a drawer: placed on the drawer bottom while it was pulled out, "
                   "then the drawer was shut with it", x=float(x), y=float(y), z=float(z),
                   did_not_fit=self._crowded, link=g["source"].split(" on link ")[-1])
        self.drawer_items[place].append(oid)


def open_home(snap_file: pathlib.Path, cameras=()):
    common.SNAPSHOT = pathlib.Path(snap_file)
    return SnapshotHome(extra_cameras=list(cameras))


def camera_frame(home):
    """Rotation matrix (camera to world) of the agent's current pose."""
    import quaternion  # noqa: F401
    return quaternion.as_rotation_matrix(home.sim.get_agent(0).get_state().rotation)


def aim(eye, target):
    """Point to look at from eye so the view centres on target, with the tilt limited."""
    d = np.array(target, float) - np.array(eye, float)
    yaw = math.atan2(d[0], d[2])
    pitch = math.degrees(math.atan2(d[1], math.hypot(d[0], d[2])))
    pitch = max(-MAX_DOWN, min(MAX_UP, pitch))
    p = math.radians(pitch)
    look = np.array(eye, float) + np.array([math.sin(yaw) * math.cos(p), math.sin(p), math.cos(yaw) * math.cos(p)])
    return look, math.degrees(yaw), pitch


def project(points, eye, turn, width, height, hfov=HFOV):
    """World points -> (column, row, camera depth along the view axis)."""
    local = (points - eye) @ turn          # turn is camera->world, so this is world->camera
    z = -local[:, 2]
    f = (width / 2) / math.tan(math.radians(hfov) / 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        col = width / 2 + f * local[:, 0] / z
        row = height / 2 - f * local[:, 1] / z
    return col, row, z


def json_dump(obj, path):
    path = pathlib.Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str))
    tmp.replace(path)
