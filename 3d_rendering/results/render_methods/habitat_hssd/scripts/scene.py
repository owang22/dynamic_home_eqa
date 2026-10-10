"""Household A's day-7 18:00 snapshot placed into HSSD home 107734254_176000121 in habitat-sim.

    home = Home(); home.place_everything()
Then home.sim renders; home.records says where every object went and why.

How each relation becomes a 3D position
---------------------------------------
Surfaces are found from what the renderer draws, not from the receptacle meshes: a ring of
small cameras looking straight down from 25 cm above the spot height. A cell (2 cm) counts as
part of the spot when the first thing drawn there belongs to the spot's furniture (or, for a
floor, to the house shell inside the room's outline) and lies within 3 cm of the spot height.
Anything drawn above (a lamp, a back rest, a cabinet) blocks the cell. Only cells connected to
the spot centre are kept.

  on_top a place     a free cell of that surface; the object's turned footprint must lie at
                     least 60% on free cells; its bottom rests on the highest drawn point under
                     its footprint (a second down camera), so it never sinks into a cushion.
  on_top an object   its centre lies inside the reference's footprint (shrunk by 20%); it rests
                     on the highest drawn point there (the cutting board's face, a thermos lid).
  next_to            same surface as the reference, footprint 1-15 cm from the reference's.
                     A next_to whose reference is a place (4 cases) is on that place.
  under              "A under B": A takes B's spot on the surface and B is set on top of A.
  inside a place     closed places (drawers, cabinets, compartments): laid out in rows around
                     the spot centre at the spot height; a drawer's contents move with the
                     drawer when it opens. Open places (sink, fireplace opening): dropped onto
                     what the down camera sees at the spot centre.
  inside an object   open containers (bowl, basket, tray): dropped onto the bottom at the
                     container's centre. Closed containers (bags, first-aid kit): the object is
                     put at the container's centre if it fits in the container's box, else it
                     is left out and counted.
  worn_by / in_pocket_of: not drawn (the figures are single fixed meshes).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from type_table import T  # noqa: E402

CELL = 0.02
FIRST_THING = 5000
FIRST_PERSON = 9000
FURNITURE_RIGID = 1000
FURNITURE_AO = 2000
DOWN = 256  # pixels of the down-looking camera
CHECKS = common.OUT / "checks"

LIES_FLAT = {
    "paperback book", "cookbook", "piano music book", "field notebook", "restaurant notebook",
    "music notebook", "sketchbook", "sketch paper pad", "sticky notes", "landscape magazine",
    "newspaper", "mail", "receipts", "restaurant receipt", "menu folder", "project folder",
    "tablet", "phone", "laptop", "wallet", "keys", "reading glasses", "pen", "mechanical pencil",
    "ruler", "toothbrush", "hairbrush", "forks", "table knives", "table spoons", "serving spoon",
    "wooden spoon", "silicone spatula", "whisk", "tongs", "ladle", "paring knife", "knives",
    "measuring spoons", "rolling pin", "cutting board", "wooden tray", "ceramic tray",
    "serving platter", "coaster", "cloth napkin", "napkins", "towel", "tea towels",
    "kitchen towel", "dish towel", "microfiber cloths", "bath mat", "throw blanket", "sheet",
    "pillowcase", "sleep shirt", "sleep pants", "work blouse", "work trousers", "lounge pants",
    "work cardigan", "evening sweater", "restaurant shirt", "evening shirt", "chef jacket",
    "jacket", "apron", "robe", "dress", "jeans", "hoodie", "linen scarf", "belt", "socks",
    "wool socks", "gardening gloves", "rubber gloves", "fabric samples", "planting sketches",
    "knife roll", "bookmark", "nail clippers", "hair clip", "batteries", "carrots", "banana",
    "spare umbrella", "flashlight", "phone charger", "headphones", "remote control", "watch",
    "shoehorn", "measuring tape", "pencil case", "garment bag",
}


def steady(*parts) -> float:
    h = hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


class Grid:
    """A spot as a map of 2 cm cells in world x, z."""

    def __init__(self, x0, z0, valid, heights, y):
        self.x0, self.z0, self.valid, self.heights, self.y = x0, z0, valid, heights, y
        self.used = np.zeros_like(valid)

    def centre(self, i, j):
        return self.x0 + (j + 0.5) * CELL, self.z0 + (i + 0.5) * CELL

    def index(self, x, z):
        return int((z - self.z0) / CELL), int((x - self.x0) / CELL)

    def rect_cells(self, cx, cz, hx, hz):
        i0, j0 = self.index(cx - hx, cz - hz)
        i1, j1 = self.index(cx + hx, cz + hz)
        return max(i0, 0), max(j0, 0), min(i1 + 1, self.valid.shape[0]), min(j1 + 1, self.valid.shape[1])


class Home:
    def __init__(self, width=640, height=480, extra_cameras=()):
        t0 = time.time()
        self.snap = common.snapshot()
        cams = [dict(uuid="down_depth", kind="depth", width=DOWN, height=DOWN, hfov=90),
                dict(uuid="down_ids", kind="ids", width=DOWN, height=DOWN, hfov=90)]
        cams += list(extra_cameras)
        self.sim = common.open_home(cams)
        self.sensors = self.sim._Simulator__sensors[0]
        self.timings = {"open_home_s": round(time.time() - t0, 2)}
        self.rom = self.sim.get_rigid_object_manager()
        self.aom = self.sim.get_articulated_object_manager()
        self.templates = self.sim.get_object_template_manager()
        self._index_furniture()
        self.things: Dict[str, object] = {}
        self.facts: Dict[str, dict] = {}
        self.records: Dict[str, dict] = {}
        self.grids: Dict[str, Grid] = {}
        self.figures: Dict[str, object] = {}
        self.drawer_items: Dict[str, List[str]] = defaultdict(list)
        self.open_move = {}     # place -> transform of its drawer since shut
        self.opened_for_placing = []

    # ------------------------------------------------------------------ rendering helpers
    def shoot(self, *uuids):
        for u in uuids:
            self.sensors[u].draw_observation()
        return {u: self.sensors[u].get_observation() for u in uuids}

    def down_points(self, eye):
        common.look_from(self.sim, eye, eye + np.array([0.0, -1.0, 0.0001]))
        seen = self.shoot("down_depth", "down_ids")
        depth, ids = seen["down_depth"], seen["down_ids"]
        f = (DOWN / 2) / math.tan(math.radians(45))
        cols, rows = np.meshgrid(np.arange(DOWN) - DOWN / 2 + 0.5, np.arange(DOWN) - DOWN / 2 + 0.5)
        import quaternion  # noqa: F401
        turn = quaternion.as_rotation_matrix(self.sim.get_agent(0).get_state().rotation)
        rays = np.stack([cols / f, -rows / f, -np.ones_like(cols)], axis=-1)
        world = eye + (rays * depth[..., None]) @ turn.T
        world[depth <= 0] = np.nan
        return world, ids

    # ------------------------------------------------------------------ furniture
    def _index_furniture(self):
        self.rigid = list(self.rom.get_objects_by_handle_substring("").values())
        self.aos = list(self.aom.get_objects_by_handle_substring("").values())
        for n, thing in enumerate(self.rigid):
            thing.semantic_id = FURNITURE_RIGID + n
        self.ao_link_ids = {}
        for n, ao in enumerate(self.aos):
            ids = set()
            for node in ao.visual_scene_nodes:
                node.semantic_id = FURNITURE_AO + n
            ids.add(FURNITURE_AO + n)
            self.ao_link_ids[ao.handle] = ids
            try:
                ao.set_light_setup(common.LIGHTS)
            except Exception:
                pass

    def furniture_of(self, place: str):
        g = self.snap["places"][place]["geometry"]
        if "template" not in g:
            return None
        pool = self.aos if g.get("articulated") else self.rigid
        cands = [t for t in pool if t.handle.startswith(g["template"])]
        if not cands:
            return None
        pos = np.array(g["position"])
        return min(cands, key=lambda t: np.linalg.norm(np.array(t.translation) - pos))

    def ids_of(self, thing) -> set:
        if thing is None:
            return {0}
        if hasattr(thing, "joint_positions"):
            return self.ao_link_ids[thing.handle]
        return {thing.semantic_id}

    # ------------------------------------------------------------------ surfaces
    def grid_for(self, place: str) -> Optional[Grid]:
        if place in self.grids:
            return self.grids[place]
        p = self.snap["places"][place]
        g = p["geometry"]
        h, c, area = g["height"], np.array(g["center"]), g["area"]
        if place in self.open_move:      # a drawer pulled out: its spot moved with it
            import magnum as mn
            q = self.open_move[place].transform_point(mn.Vector3(*[float(v) for v in c]))
            c, h = np.array([q.x, q.y, q.z]), float(q.y)
        furniture = self.furniture_of(place)
        if g["source"].startswith("region"):
            region = next(r for r in common_regions() if r["name"] == g["source"].split("'")[1])
            poly = np.array(region["poly_loop"])
            low = np.array([poly[:, 0].min(), 0, poly[:, 2].min()])
            high = np.array([poly[:, 0].max(), 0, poly[:, 2].max()])
            ids, lift, step = {0}, 1.0, 1.6
        else:
            low, high = common.box_of(furniture) if furniture is not None else (c - 0.5, c + 0.5)
            ids, lift, step = self.ids_of(furniture), 0.25, 0.4
            poly = None
        grid = self._scan(place, low, high, h, c, area, ids, lift, step, poly)
        if poly is None and grid.valid.sum() * CELL ** 2 < 0.3 * area:
            # a lower shelf: the first scan saw the shelf or top above it; look again from 8 cm
            second = self._scan(place, low, high, h, c, area, ids, 0.08, 0.14, poly)
            if second.valid.sum() > grid.valid.sum():
                grid = second
        self.grids[place] = grid
        return grid

    def _scan(self, place, low, high, h, c, area, ids, lift, step, poly):
        nx = int((high[0] - low[0]) / CELL) + 3
        nz = int((high[2] - low[2]) / CELL) + 3
        x0, z0 = low[0] - CELL, low[2] - CELL
        top = np.full((nz, nx), np.nan)
        owner = np.full((nz, nx), -1)
        for x in np.arange(low[0] + step / 2, high[0] + step / 2, step):
            for z in np.arange(low[2] + step / 2, high[2] + step / 2, step):
                world, sid = self.down_points(np.array([x, h + lift, z]))
                ok = np.isfinite(world[..., 0])
                gi = ((world[..., 2][ok] - z0) / CELL).astype(int)
                gj = ((world[..., 0][ok] - x0) / CELL).astype(int)
                inside = (gi >= 0) & (gi < nz) & (gj >= 0) & (gj < nx)
                ys, ss = world[..., 1][ok][inside], sid[ok][inside]
                gi, gj = gi[inside], gj[inside]
                # keep the highest point per cell (what a thing set down there would meet)
                order = np.argsort(ys)
                top[gi[order], gj[order]] = ys[order]
                owner[gi[order], gj[order]] = ss[order]
        valid = np.isfinite(top) & (np.abs(top - h) <= 0.03) & np.isin(owner, list(ids))
        if poly is not None:
            from matplotlib.path import Path
            xs, zs = np.meshgrid(x0 + (np.arange(nx) + 0.5) * CELL, z0 + (np.arange(nz) + 0.5) * CELL)
            valid &= Path(poly[:, [0, 2]]).contains_points(np.stack([xs.ravel(), zs.ravel()], 1)).reshape(valid.shape)
        valid = ndimage.binary_opening(valid, iterations=1)
        labels, n = ndimage.label(valid)
        if n:
            ci, cj = int((c[2] - z0) / CELL), int((c[0] - x0) / CELL)
            reach = 0.3 * math.sqrt(area) + 0.1
            keep = set()
            ii, jj = np.nonzero(valid)
            near = np.hypot((ii - ci) * CELL, (jj - cj) * CELL) <= reach
            keep = set(labels[ii[near], jj[near]].tolist())
            if not keep:
                sizes = ndimage.sum(valid, labels, range(1, n + 1))
                keep = {int(np.argmax(sizes)) + 1}
            valid = np.isin(labels, list(keep))
        return Grid(x0, z0, valid, top, h)

    def rest_height(self, x, z, hx, hz, above, centre_only=False, place=None):
        """Highest drawn point under a footprint, seen from above. Only points of the spot's
        furniture, of placed things, or (for a floor) of the floor itself count: a wall or a
        cabinet side seen at a slant is not something to rest on."""
        world, sid = self.down_points(np.array([x, above, z]))
        if centre_only:
            r = 0.35 * min(hx, hz)
            m = np.hypot(world[..., 0] - x, world[..., 2] - z) <= max(r, 0.015)
        else:
            m = (np.abs(world[..., 0] - x) <= hx) & (np.abs(world[..., 2] - z) <= hz)
        allowed = (sid >= FIRST_THING) & (sid < FIRST_PERSON)
        if place is not None:
            g = self.snap["places"][place]["geometry"]
            if g["source"].startswith("region"):
                allowed |= (sid == 0) & (world[..., 1] < g["height"] + 0.05)
            else:
                allowed |= np.isin(sid, list(self.ids_of(self.furniture_of(place))))
        else:
            allowed |= True
        ys = world[..., 1][m & allowed]
        ys = ys[np.isfinite(ys)]
        return float(np.percentile(ys, 98)) if len(ys) else None

    # ------------------------------------------------------------------ models
    def choose_models(self):
        cands = json.load((CHECKS / "model_candidates.json").open())
        lvis = json.load((CHECKS / "lvis_to_download.json").open())
        paths = json.load((CHECKS / "lvis_downloaded.json").open())["paths"]
        bad = set(json.load((CHECKS / "rejected_models.json").open())["ids_or_type_ids"]) \
            if (CHECKS / "rejected_models.json").exists() else set()
        by_type = defaultdict(list)
        for oid, o in sorted(self.snap["objects"].items()):
            by_type[o["type"]].append(oid)
        chosen = {}
        for typ, oids in by_type.items():
            size = T[typ][0]
            options = [dict(c, fit=None) for c in cands[typ]["candidates"]]
            for p in lvis.get(typ, []):
                if p["uid"] in paths:
                    options.append({"source": "objaverse", "id": p["uid"], "mesh": paths[p["uid"]], "scale": None,
                                    "fit": size, "looks_like": p["name"], "sub": p["sub"], "license": p["license"]})
            options = [o for o in options if o["id"] not in bad and f"{typ}|{o['id']}" not in bad]
            for n, oid in enumerate(oids):
                chosen[oid] = options[n % len(options)] if options else None
        return chosen

    def add_model(self, mesh, scale, sid, key):
        import habitat_sim
        import magnum as mn
        t = self.templates.create_new_template(key)
        t.render_asset_handle = mesh
        t.collision_asset_handle = mesh
        t.scale = mn.Vector3(scale, scale, scale)
        tid = self.templates.register_template(t, key)
        thing = self.rom.add_object_by_template_id(tid, light_setup_key=common.LIGHTS)
        if thing is None:
            return None
        thing.motion_type = habitat_sim.physics.MotionType.KINEMATIC
        thing.semantic_id = sid
        for node in thing.visual_scene_nodes:
            node.semantic_id = sid
        return thing

    def add_objects(self):
        import magnum as mn
        t0 = time.time()
        chosen = self.choose_models()
        for n, (oid, o) in enumerate(sorted(self.snap["objects"].items())):
            m = chosen[oid]
            rec = {"type": o["type"], "relation": o["relation"], "reference": o["reference"],
                   "place": o["place"], "hidden_in_snapshot": o["hidden"], "model": None}
            self.records[oid] = rec
            if m is None:
                rec["model"] = {"source": "none"}
                continue
            sid = FIRST_THING + n
            scale = m["scale"] if m["scale"] is not None else 1.0
            thing = self.add_model(m["mesh"], scale, sid, f"{m['id']}@{scale:.5f}")
            if thing is not None and m.get("fit"):
                size = np.array(thing.root_scene_node.cumulative_bb.size())
                if size.max() > 0:
                    self.rom.remove_object_by_id(thing.object_id)
                    scale = m["fit"] / float(size.max())
                    thing = self.add_model(m["mesh"], scale, sid, f"{m['id']}@{scale:.5f}")
            if thing is None:
                rec["model"] = {"source": m["source"], "id": m["id"], "failed": "did not load"}
                continue
            size = np.array(thing.root_scene_node.cumulative_bb.size())
            if not np.all(np.isfinite(size)) or size.max() <= 1e-4:
                rec["model"] = {"source": m["source"], "id": m["id"], "failed": "empty box"}
                self.rom.remove_object_by_id(thing.object_id)
                continue
            # turn so the thinnest side is up, for things that lie flat
            base = mn.Quaternion()
            if o["type"] in LIES_FLAT:
                thin = int(np.argmin(size))
                if thin == 0 and size[0] * 1.3 < size[1]:
                    base = mn.Quaternion.rotation(mn.Deg(90), mn.Vector3(0, 0, 1))
                elif thin == 2 and size[2] * 1.3 < size[1]:
                    base = mn.Quaternion.rotation(mn.Deg(90), mn.Vector3(1, 0, 0))
            self.things[oid] = thing
            self.facts[oid] = {"sid": sid, "base": base, "size": size.tolist()}
            rec["model"] = {"source": m["source"], "id": m["id"], "looks_like": m.get("looks_like", "")[:60],
                            "stand_in": bool(m.get("sub")), "scale": round(scale, 5),
                            "size_m": [round(float(v), 3) for v in size]}
            self.park(oid)
        self.timings["add_objects_s"] = round(time.time() - t0, 2)

    def park(self, oid):
        import magnum as mn
        self.things[oid].translation = mn.Vector3(0.0, -60.0 - 0.5 * len(self.things), 0.0)

    def turn(self, oid, yaw):
        import magnum as mn
        thing = self.things[oid]
        thing.rotation = mn.Quaternion.rotation(mn.Rad(yaw), mn.Vector3(0, 1, 0)) * self.facts[oid]["base"]
        thing.translation = mn.Vector3(0, 0, 0)
        low, high = common.box_of(thing)
        return low, high

    def set_at(self, oid, x, y, z):
        """Box centred on x, z with its bottom at y (rotation already set by turn)."""
        import magnum as mn
        thing = self.things[oid]
        thing.translation = mn.Vector3(0, 0, 0)
        low, high = common.box_of(thing)
        thing.translation = mn.Vector3(float(x - (low[0] + high[0]) / 2), float(y - low[1]),
                                       float(z - (low[2] + high[2]) / 2))

    def footprint(self, oid):
        low, high = common.box_of(self.things[oid])
        return low, high

    # ------------------------------------------------------------------ placement
    def place_everything(self):
        t0 = time.time()
        self.add_objects()
        objs = self.snap["objects"]
        under_of = {o["reference"]: oid for oid, o in objs.items() if o["relation"] == "under"}
        done, order = set(), []
        pending = list(sorted(objs))
        while pending:
            progressed = False
            for oid in list(pending):
                o = objs[oid]
                ref = o["reference"]
                needs = None
                if o["reference_kind"] == "object" and o["relation"] != "under":
                    needs = ref
                if oid in under_of:            # B sits on A when "A under B"
                    needs = under_of[oid]
                if o["relation"] == "under":
                    needs = None
                if needs is None or needs in done:
                    order.append(oid)
                    done.add(oid)
                    pending.remove(oid)
                    progressed = True
            if not progressed:
                order += pending
                break
        for oid in order:
            self.place_one(oid, under_of)
        for place in self.opened_for_placing:
            self.open_part(place, 0.0)
            self.grids.pop(place, None)
        self.timings["place_s"] = round(time.time() - t0, 2)

    def place_one(self, oid, under_of):
        o = self.snap["objects"][oid]
        rec = self.records[oid]
        rel, ref, kind = o["relation"], o["reference"], o["reference_kind"]
        place = o["place"]
        pkind = self.snap["places"][place]["kind"]
        if oid not in self.things:
            rec.update(placed=False, why="no 3D model")
            return
        if rel in ("worn_by", "in_pocket_of"):
            rec.update(placed=False, why=f"{rel.replace('_', ' ')} {ref}: figures are fixed meshes")
            return
        g0 = self.snap["places"][place]["geometry"]
        if "rotation" in g0 and not g0["source"].startswith("region"):
            # line things up with the furniture (a quarter turn either way), with a little
            # wobble on open surfaces and none in drawers; turned footprints waste room
            w, _, yq, _ = g0["rotation"]
            yaw = 2 * math.atan2(yq, w) + int(steady("q", oid) * 4) * math.pi / 2
            if pkind != "closed":
                yaw += (steady("w", oid) - 0.5) * math.radians(30)
        else:
            yaw = steady("yaw", oid) * 2 * math.pi
        if o["type"] in ("work loafers", "running shoes", "rain boots", "kitchen clogs"):
            yaw = steady("yaw", place) * 2 * math.pi + (steady("y2", oid) - 0.5) * 0.6
        low, high = self.turn(oid, yaw)
        hx, hz, hy = (high[0] - low[0]) / 2, (high[2] - low[2]) / 2, high[1] - low[1]
        g = self.snap["places"][place]["geometry"]
        # the object a thing sits on, when "A under B" or "B on_top A"
        base_obj = under_of.get(oid) if oid in under_of else (ref if kind == "object" and rel == "on_top" else None)
        if base_obj is not None and not self.records.get(base_obj, {}).get("placed"):
            base_obj = None
        if pkind == "closed" and not (kind == "object" and rel == "inside"):
            self._place_closed(oid, place, hx, hz, hy, base_obj)
            return
        if kind == "object" and rel == "inside":
            self._place_inside_object(oid, ref, hx, hz, hy)
            return
        if base_obj is not None:
            self._place_on_object(oid, base_obj, hx, hz)
            return
        if pkind == "open":
            c = g["center"]
            y = self.rest_height(c[0], c[2], hx, hz, g["height"] + 0.3, centre_only=True, place=place)
            y = g["height"] if y is None or abs(y - g["height"]) > 0.15 else y
            jitter = self._siblings(place)
            rec["_sib"] = place
            self.set_at(oid, c[0] + jitter[0], y, c[2] + jitter[1])
            rec.update(placed=True, how="dropped into open place at its centre", x=c[0], y=y, z=c[2])
            return
        grid = self.grid_for(place)
        near = None
        if rel == "next_to" and kind == "object" and self.records.get(ref, {}).get("placed"):
            near = self.footprint(ref)
        spot = self._free_spot(grid, oid, hx, hz, near)
        if spot is None:
            rec.update(placed=False, why=f"no free room on {place} ({int(grid.valid.sum())} cells, "
                                         f"{int((grid.valid & ~grid.used).sum())} free)")
            self.park(oid)
            return
        x, z, share = spot
        y = self.rest_height(x, z, hx, hz, grid.y + 0.25 if grid.y > 0.05 else 1.0, place=place)
        y = grid.y if y is None or y < grid.y - 0.03 or y > grid.y + 0.5 else y
        self.set_at(oid, x, y, z)
        how = "next to its reference" if near is not None else "on a free cell of the surface"
        if rel == "next_to" and kind == "place":
            how = "on the place (next_to names the place itself)"
        rec.update(placed=True, how=how, x=x, y=y, z=z, share_of_footprint_on_free_cells=round(share, 2),
                   did_not_fit=self._crowded)

    def _siblings(self, key):
        n = sum(1 for r in self.records.values() if r.get("_sib") == key)
        return (0.06 * math.cos(n * 2.1) * (n > 0), 0.06 * math.sin(n * 2.1) * (n > 0))

    def _free_spot(self, grid, oid, hx, hz, near, need=0.6):
        free = (grid.valid & ~grid.used).astype(float)
        ny, nx = max(1, int(hz / CELL)), max(1, int(hx / CELL))
        share = ndimage.uniform_filter(free, size=(2 * ny + 1, 2 * nx + 1), mode="constant")
        ok = (share >= need) & grid.valid & ~grid.used
        crowded = False
        if not ok.any():
            # no room left: overlap what is there (it then rests on top of it), or overhang
            if not grid.valid.any():
                return None
            share = ndimage.uniform_filter(grid.valid.astype(float), size=(2 * ny + 1, 2 * nx + 1), mode="constant")
            least_used = ndimage.uniform_filter(grid.used.astype(float), size=(2 * ny + 1, 2 * nx + 1), mode="constant")
            score = np.where(grid.valid, share - 0.5 * least_used, -9)
            ok = score >= score.max() - 0.02
            crowded = True
        ii, jj = np.nonzero(ok)
        xs, zs = grid.x0 + (jj + 0.5) * CELL, grid.z0 + (ii + 0.5) * CELL
        if near is not None:
            lo, hi = near
            gapx = np.maximum(0, np.maximum(lo[0] - (xs + hx), (xs - hx) - hi[0]))
            gapz = np.maximum(0, np.maximum(lo[2] - (zs + hz), (zs - hz) - hi[2]))
            gap = np.maximum(gapx, gapz)
            inside = (gapx == 0) & (gapz == 0)
            score = np.where(inside, 9, np.abs(gap - 0.04))
            k = int(np.argmin(score + 0.001 * np.array([steady(oid, i) for i in range(len(score))])))
        else:
            # prefer cells that keep the whole footprint on free cells, then a steady random pick
            best = share[ii, jj] >= 0.999
            pool = np.flatnonzero(best) if best.any() else np.arange(len(ii))
            k = int(pool[int(steady("spot", oid) * len(pool))])
        x, z = float(xs[k]), float(zs[k])
        i0, j0, i1, j1 = grid.rect_cells(x, z, hx + CELL, hz + CELL)
        grid.used[i0:i1, j0:j1] = True
        self._crowded = crowded
        return x, z, float(share[ii[k], jj[k]])

    def _place_on_object(self, oid, base, hx, hz):
        rec = self.records[oid]
        lo, hi = self.footprint(base)
        cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
        bx, bz = (hi[0] - lo[0]) / 2 * 0.8, (hi[2] - lo[2]) / 2 * 0.8
        n = sum(1 for r in self.records.values() if r.get("_on") == base)
        rec["_on"] = base
        # spread several things over the base: golden-angle positions inside its footprint
        r = 0.0 if n == 0 else min(1.0, 0.45 * math.sqrt(n))
        a = n * 2.399 + steady("on", base) * 6.28
        x = cx + max(bx - hx * 0.3, 0) * r * math.cos(a)
        z = cz + max(bz - hz * 0.3, 0) * r * math.sin(a)
        y = self.rest_height(x, z, min(hx, bx + 0.01), min(hz, bz + 0.01), hi[1] + 0.25,
                             place=self.snap["objects"][oid]["place"])
        y = hi[1] if y is None else y
        self.set_at(oid, x, y, z)
        rec.update(placed=True, how=f"on top of {base}", x=x, y=y, z=z)

    def _place_inside_object(self, oid, ref, hx, hz, hy):
        rec = self.records[oid]
        ref_holds = self.snap["objects"][ref]["holds"]
        if not self.records.get(ref, {}).get("placed"):
            rec.update(placed=False, why=f"its container {ref} was not placed")
            self.park(oid)
            return
        lo, hi = self.footprint(ref)
        cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
        if ref_holds in ("open",):
            n = sum(1 for r in self.records.values() if r.get("_in") == ref)
            rec["_in"] = ref
            jx = 0.15 * (hi[0] - lo[0]) * math.cos(n * 2.4) * (n > 0)
            jz = 0.15 * (hi[2] - lo[2]) * math.sin(n * 2.4) * (n > 0)
            y = self.rest_height(cx + jx, cz + jz, (hi[0] - lo[0]) / 2, (hi[2] - lo[2]) / 2, hi[1] + 0.3, centre_only=True,
                                 place=self.snap["objects"][oid]["place"])
            y = lo[1] + 0.01 if y is None else y
            self.set_at(oid, cx + jx, y, cz + jz)
            rec.update(placed=True, how=f"dropped into open container {ref}", x=cx + jx, y=y, z=cz + jz)
            return
        # closed container or pockets: inside its box if it fits
        fits = (2 * hx <= (hi[0] - lo[0]) * 0.95 and 2 * hz <= (hi[2] - lo[2]) * 0.95 and hy <= (hi[1] - lo[1]) * 0.9) or \
               (2 * hz <= (hi[0] - lo[0]) * 0.95 and 2 * hx <= (hi[2] - lo[2]) * 0.95 and hy <= (hi[1] - lo[1]) * 0.9)
        if fits:
            self.set_at(oid, cx, lo[1] + 0.01, cz)
            rec.update(placed=True, how=f"inside closed container {ref} (centred in its box)", x=cx, y=lo[1] + 0.01, z=cz)
        else:
            self.park(oid)
            rec.update(placed=False, why=f"larger than the box of its closed container {ref}")

    def _place_closed(self, oid, place, hx, hz, hy, base_obj):
        rec = self.records[oid]
        g = self.snap["places"][place]["geometry"]
        c = np.array(g["center"])
        if base_obj is not None:
            lo, hi = self.footprint(base_obj)
            x, z, y = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, hi[1]
        elif self.is_drawer(place):
            if place not in self.open_move:
                self.open_part(place, 1.0)
                self.opened_for_placing.append(place)
            grid = self.grid_for(place)
            spot = self._free_spot(grid, oid, hx, hz, None, need=0.999) if grid.valid.any() else None
            if spot is None:
                x, z, y = float(np.mean(grid.x0)), float(np.mean(grid.z0)), grid.y
                rec.update(placed=False, why="no cells found on the opened drawer's bottom")
                self.park(oid)
                return
            x, z, share = spot
            top = self.rest_height(x, z, hx, hz, grid.y + 0.25, place=place)
            y = grid.y if top is None or abs(top - grid.y) > 0.3 else top
            self.set_at(oid, x, y, z)
            rec.update(placed=True, how="inside a drawer: placed on the drawer bottom while it was pulled out, "
                       "then the drawer was shut with it", x=float(x), y=float(y), z=float(z),
                       did_not_fit=self._crowded, link=g["source"].split(" on link ")[-1])
            self.drawer_items[place].append(oid)
            return
        else:
            n = sum(1 for r in self.records.values() if r.get("_closed") == place)
            side = math.sqrt(max(g["area"], 0.01))
            cols = max(1, int(side / 0.16))
            x = c[0] + ((n % cols) - (cols - 1) / 2) * min(0.16, side / cols)
            z = c[2] + ((n // cols) % cols - (cols - 1) / 2) * min(0.16, side / cols) * 0.8
            # keep the footprint inside a square of the spot's area around its centre
            room_x, room_z = max(side / 2 - hx, 0.0), max(side / 2 - hz, 0.0)
            x = float(np.clip(x, c[0] - room_x, c[0] + room_x))
            z = float(np.clip(z, c[2] - room_z, c[2] + room_z))
            y = g["height"] + 0.005
            rec["_closed"] = place
        self.set_at(oid, x, y, z)
        link = g["source"].split(" on link ")[-1] if " on link " in g["source"] else None
        rec.update(placed=True, how="inside a closed place, in rows around the spot centre at the spot height"
                   if base_obj is None else f"inside a closed place, on top of {base_obj}",
                   x=float(x), y=float(y), z=float(z), link=link)
        if link and g.get("articulated"):
            self.drawer_items[place].append(oid)

    # ------------------------------------------------------------------ drawers
    def is_drawer(self, place: str) -> bool:
        g = self.snap["places"][place]["geometry"]
        if not g.get("articulated") or " on link " not in g["source"] or g.get("behind_door"):
            return False
        ao = self.furniture_of(place)
        name = g["source"].split(" on link ")[-1]
        link = [i for i in ao.get_link_ids() if ao.get_link_name(i) == name]
        return bool(link) and "Prismatic" in str(ao.get_link_joint_type(link[0]))

    def open_part(self, place: str, fraction: float = 1.0):
        """Opens the drawer or door a closed place sits on and moves the things in it with it."""
        import magnum as mn
        g = self.snap["places"][place]["geometry"]
        ao = self.furniture_of(place)
        link_name = g["source"].split(" on link ")[-1]
        moving = g.get("behind_door") or link_name
        link = next(i for i in ao.get_link_ids() if ao.get_link_name(i) == moving)
        carried = next(i for i in ao.get_link_ids() if ao.get_link_name(i) == link_name)
        before = ao.get_link_scene_node(carried).absolute_transformation()
        pos = list(ao.joint_positions)
        off = ao.get_link_joint_pos_offset(link)
        lo, hi = ao.joint_position_limits
        pos[off] = float(lo[off] + fraction * (hi[off] - lo[off]))
        ao.joint_positions = pos
        after = ao.get_link_scene_node(carried).absolute_transformation()
        move = after @ before.inverted()
        for oid in self.drawer_items.get(place, []):
            thing = self.things[oid]
            thing.transformation = move @ thing.transformation
        total = move @ self.open_move.get(place, mn.Matrix4())
        if fraction == 0.0:
            self.open_move.pop(place, None)
        else:
            self.open_move[place] = total
        return {"link": moving, "joint_value": pos[off], "limit": [float(lo[off]), float(hi[off])],
                "carried_link": link_name, "moved_things": self.drawer_items.get(place, [])}

    # ------------------------------------------------------------------ people
    def add_people(self):
        import magnum as mn
        figures = {"mara": "a1abed1c22106419c83bd81061c47ca4b0d34e8b",   # 'People Mary sitting'
                   "julian": "3177564b8a33e1b23a375695df99e534105bbfe9"}  # 'Alberto seated'
        out = {}
        for n, (who, fid) in enumerate(sorted(figures.items())):
            seat = self.snap["people"][who]["place"]
            g = self.snap["places"][seat]["geometry"]
            mesh = str(common.HSSD / "objects" / fid[0] / f"{fid}.glb")
            fig = self.add_model(mesh, 1.0, FIRST_PERSON + n, f"figure_{fid}")
            grid = self.grid_for(seat)
            ii, jj = np.nonzero(grid.valid)
            xs, zs = grid.x0 + (jj + 0.5) * CELL, grid.z0 + (ii + 0.5) * CELL
            clear = ndimage.distance_transform_edt(grid.valid)[ii, jj] * CELL
            if who == "julian":   # on the sectional, the seat cell nearest the coffee table
                ct = np.array(self.snap["places"]["living_room_living_room_coffee_table_top"]["geometry"]["center"])
                k = int(np.argmin(np.hypot(xs - ct[0], zs - ct[2]) + 9 * (clear < 0.2)))
            else:
                k = int(np.argmax(clear))
            sx, sz = float(xs[k]), float(zs[k])
            # facing: away from whatever stands above the seat behind it (a back rest),
            # else toward the island counter
            furn = self.furniture_of(seat)
            world, sid = self.down_points(np.array([sx, g["height"] + 1.2, sz]))
            back = np.isin(sid, list(self.ids_of(furn))) & (world[..., 1] > g["height"] + 0.2)
            if back.sum() > 200:
                bx, bz = np.nanmean(world[..., 0][back]), np.nanmean(world[..., 2][back])
                face = np.array([sx - bx, sz - bz])
            else:
                isl = np.array(self.snap["places"]["kitchen_kitchen_island_island_countertop"]["geometry"]["center"])
                face = np.array([isl[0] - sx, isl[2] - sz])
            face /= np.linalg.norm(face) + 1e-9
            yaw = math.atan2(face[0], face[1])        # figures face +z before turning
            fig.rotation = mn.Quaternion.rotation(mn.Rad(yaw), mn.Vector3(0, 1, 0))
            # the seat contact is the figure's own origin height less 2-3 cm (measured from the
            # meshes); the hips sit about 0.2 m behind the origin
            # sit on the drawn cushion top, not on the receptacle height under it
            top = self.rest_height(sx, sz, 0.3, 0.3, g["height"] + 0.6, centre_only=True, place=seat)
            seat_y = top if top is not None and abs(top - g["height"]) < 0.25 else g["height"]
            # Measured from both meshes (trimesh, vertex slices): the underside of the thighs
            # is 0.36 m above the feet, and the hips are about 0.2 m behind the middle of the
            # box. habitat moves an object's origin to its mass centre, so place by the box.
            fig.translation = mn.Vector3(0, 0, 0)
            lo, hi = common.box_of(fig)
            mid = np.array([sx, sz]) + face * 0.15
            fig.translation = mn.Vector3(float(mid[0] - (lo[0] + hi[0]) / 2), float(seat_y - 0.36 - lo[1]),
                                         float(mid[1] - (lo[2] + hi[2]) / 2))
            self.figures[who] = fig
            out[who] = {"figure": fid, "seat": seat, "x": sx, "z": sz, "seat_top_y": round(seat_y, 3),
                        "spot_height": g["height"], "yaw_deg": round(math.degrees(yaw), 1)}
        return out


_REGIONS = None


def common_regions():
    global _REGIONS
    if _REGIONS is None:
        path = common.HSSD / "semantics/scenes" / f"{common.SCENE}.semantic_config.json"
        _REGIONS = json.load(path.open())["region_annotations"]
    return _REGIONS
