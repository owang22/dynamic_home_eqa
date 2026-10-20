"""Third version of the household pictures (hssd_a_v3): sharper pictures, corrected model sizes
and models, and things spread out on surfaces instead of stacked.

Import this before render_snapshot_v3 / placement_check_v3 / model_check_v3. It sets module
values of lib (picture size, picture folder, log folder, home class, and optionally the run
folder) and patches common.open_home in this process only. No v1/v2 file is edited, and the
v2 code paths (lib.SnapshotHomeV2, render_snapshot.py, run_all_v2.py) behave as before.

What changes against v2 (README.md, "Third version"):
1. Pictures 1280x960 (was 640x480), same 75 deg lens, same camera stands (spot_views.json).
   The colour picture is drawn at 2560x1920 and reduced 2x2 -> 1 (supersampling: smooth
   edges); the id picture is drawn at 1280x960. Ambient occlusion (habitat's HBAO) is on, so
   things get contact shadows where they touch a surface. Pixel counts in truth.json are at
   1280x960 (4x the 640x480 counts); "visible" is >= 120 pixels (= the old 30 at 640x480).
2. Models: models_v3.json lists, per object type (or type|model id), a new longest side
   (rescale), a different model (replace), or no model (drop), each with the reason. Made
   from the size check (model_sizes_v3.py) and the model look check (model_check_v3.py).
3. Where things go (SnapshotHomeV3, README.md "Third version", item 3): a thing on a surface
   has its centre and at least SUPPORT_SHARE of its own outline over the surface, no overlap with
   another thing's turned rectangle, and rests on the scanned surface under its outline. A thing
   the snapshot puts on top of a thing that is not a carrier for it (CARRIERS) goes beside it.
   A thing whose v2 spot breaks these rules gets a new spot: its own place, then another place
   of the same furniture, then (last resort) the nearest other furniture of the room; each move
   is a repair in truth.json and `drawn_on` names where it was drawn. Cloth heaps and piles in a
   sink are left. Furniture tops are packed from their edges.

Environment overrides: PICS_V3 (picture folder), RUN_V3 (snapshot run folder, e.g.
.../lived_home/hssd_a2), RUN_V3_LOGS (log subfolder name under run_v3/, default 'hssd_a').
"""
from __future__ import annotations

import json
import math
import os
import pathlib

import numpy as np

import lib

common, scene = lib.common, lib.scene
RENDER = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------- settings
W, H = 1280, 960
SUPERSAMPLE = 2                   # colour drawn at (SUPERSAMPLE*W) x (SUPERSAMPLE*H), then reduced
VISIBLE_PX = 120                  # = 30 px at 640x480, scaled by the 4x pixel area
HBAO = True
MODELS_V3 = RENDER / "models_v3.json"
MODELS_BUILT = RENDER / "models_v3_built.json"      # made by make_meshes_v3.py
SUPPORT_SHARE = 0.8               # share of a footprint that must be over its surface

lib.W, lib.H = W, H
lib.VISIBLE_PX = VISIBLE_PX
if os.environ.get("RUN_V3"):
    lib.RUN = pathlib.Path(os.environ["RUN_V3"])
lib.PICS = pathlib.Path(os.environ.get("PICS_V3", "/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v3"))
lib.SPOT_VIEWS = RENDER / "spot_views.json"
lib.CODE = RENDER / "run_v3" / os.environ.get("RUN_V3_LOGS", "hssd_a")
(lib.CODE / "logs" / "snapshots").mkdir(parents=True, exist_ok=True)


def open_home_v3(cameras, physics: bool = True, navmesh: bool = True):
    """common.open_home with habitat's ambient occlusion (HBAO) switched on. Same dataset, scene,
    six lights and camera setup."""
    import habitat_sim
    import magnum as mn

    backend = habitat_sim.SimulatorConfiguration()
    backend.scene_dataset_config_file = str(common.DATASET)
    backend.scene_id = common.SCENE
    backend.enable_physics = physics
    backend.gpu_device_id = 0
    backend.override_scene_light_defaults = True
    backend.scene_light_setup = common.LIGHTS
    backend.enable_hbao = HBAO
    kinds = {"colour": habitat_sim.SensorType.COLOR, "ids": habitat_sim.SensorType.SEMANTIC,
             "depth": habitat_sim.SensorType.DEPTH}
    specs = []
    for camera in cameras:
        spec = habitat_sim.CameraSensorSpec()
        spec.uuid = camera["uuid"]
        spec.sensor_type = kinds[camera["kind"]]
        spec.resolution = [camera["height"], camera["width"]]
        spec.position = mn.Vector3(0, 0, 0)
        spec.hfov = camera.get("hfov", 90)
        if camera.get("clear_color") is not None:
            spec.clear_color = mn.Color4(*camera["clear_color"])
        specs.append(spec)
    agent = habitat_sim.agent.AgentConfiguration()
    agent.sensor_specifications = specs
    agent.height = 0.0
    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend, [agent]))
    light, fixed = habitat_sim.gfx.LightInfo, habitat_sim.gfx.LightPositionModel.Global
    sim.set_light_setup([
        light(vector=mn.Vector4(*direction, 0.0), color=mn.Color3(strength, strength, strength), model=fixed)
        for direction, strength in [((0, -1, 0), 1.0), ((1, -0.6, 0.3), 0.7), ((-1, -0.6, -0.3), 0.7),
                                    ((0.3, -0.6, 1), 0.7), ((-0.3, -0.6, -1), 0.7), ((0, 1, 0), 0.35)]
    ], common.LIGHTS)
    if navmesh:
        settings = habitat_sim.NavMeshSettings()
        settings.set_defaults()
        settings.agent_radius = 0.2
        settings.agent_height = 0.5
        settings.include_static_objects = True
        sim.recompute_navmesh(sim.pathfinder, settings)
    return sim


common.open_home = open_home_v3


# ---------------------------------------------------------------- carriers
BOOKS = {"paperback book", "cookbook", "piano music book", "field notebook", "restaurant notebook",
         "music notebook", "sketchbook", "landscape magazine", "sketch paper pad", "menu folder",
         "project folder"}
PAPER = {"mail", "receipts", "restaurant receipt", "bookmark", "sticky notes", "planting sketches",
         "newspaper"}
PLATES = {"plate"}
BOWLS = {"bowl", "bowls", "snack bowl", "mixing bowl"}
CUTLERY = {"forks", "table knives", "table spoons", "serving spoon", "paring knife", "knives",
           "measuring spoons", "wooden spoon"}
LOOSE_FOOD = {"apple", "banana", "lemons", "carrots", "butter", "market herbs"}
CUPS = {"mug", "mugs", "water glass", "wine glass"}
ANYTHING = {"wooden tray", "ceramic tray", "serving platter", "cutting board", "laundry basket"}
# base type -> the types it may carry on top ("*" = anything). Cloth on cloth is a rule below.
CARRIERS = {
    **{t: "*" for t in ANYTHING},
    **{t: PLATES | BOWLS | CUTLERY | LOOSE_FOOD | {"cloth napkin", "napkins"} for t in PLATES},
    **{t: BOWLS | CUTLERY | LOOSE_FOOD for t in BOWLS},
    **{t: BOOKS | PAPER for t in BOOKS},
    "coaster": CUPS,
    "cloth napkin": CUTLERY,
}


def may_carry(base_type: str, top_type: str) -> bool:
    """True when a thing of top_type may lie on a thing of base_type (see CARRIERS)."""
    if lib.is_soft(base_type) and lib.is_soft(top_type):
        return True                       # folded clothes, towels, sheets on each other
    allowed = CARRIERS.get(base_type)
    return allowed == "*" or (allowed is not None and top_type in allowed)


def carriers_table() -> dict:
    """The carrier rule written out, for truth.json and the README."""
    return {"cloth_on_cloth": "any soft thing (clothes, towels, sheets, napkins, cloths) on another",
            **{b: ("anything" if a == "*" else sorted(a)) for b, a in sorted(CARRIERS.items())}}


# ---------------------------------------------------------------- the home
class SnapshotHomeV3(lib.SnapshotHomeV2):
    """SnapshotHomeV2 with the v3 model table and the spread-out rule (module docstring)."""

    # ------------------------------------------------------------ models
    def _model_rules(self):
        """models_v3.json (by hand) and models_v3_built.json (make_meshes_v3.py), merged; the built
        rules win. Lookup order: by_object, then by_model ('type|model id'), then by_type."""
        if not hasattr(self, "_rules"):
            hand = json.loads(MODELS_V3.read_text()) if MODELS_V3.exists() else {}
            built = json.loads(MODELS_BUILT.read_text()) if MODELS_BUILT.exists() else {}
            self._rules = {k: {**hand.get(k, {}), **built.get(k, {})} for k in ("by_object", "by_model", "by_type")}
        return self._rules

    def choose_models(self):
        chosen = super().choose_models()
        rules = self._model_rules()
        self.model_changes = {}
        for oid, m in chosen.items():
            typ = self.snap["objects"][oid]["type"]
            rule = rules["by_object"].get(oid) or \
                (rules["by_model"].get(f"{typ}|{m['id']}") if m is not None else None) or rules["by_type"].get(typ)
            if not rule:
                continue
            old = None if m is None else {"source": m["source"], "id": m["id"],
                                          "looks_like": (m.get("looks_like") or "")[:60]}
            if rule.get("drop"):
                chosen[oid] = None
            elif rule.get("mesh"):
                chosen[oid] = {"source": rule.get("source", "objaverse"), "id": rule["id"], "mesh": rule["mesh"],
                               "scale": None, "fit": rule["longest_m"], "looks_like": rule.get("looks_like", ""),
                               "sub": rule.get("stand_in", False)}
            elif rule.get("longest_m") and m is not None:
                chosen[oid] = dict(m, scale=None, fit=rule["longest_m"])
            self.model_changes[oid] = {"from": old, "rule": {k: v for k, v in rule.items() if k != "mesh"}}
        return chosen

    def add_objects(self):
        super().add_objects()
        import magnum as mn
        rules = self._model_rules()
        for oid, ch in getattr(self, "model_changes", {}).items():
            rec = self.records[oid]
            if ch["rule"].get("drop"):
                rec["model"] = {"source": "none", "dropped": ch["rule"].get("why")}
            up = ch["rule"].get("turn")
            if up and oid in self.facts:        # model lies on its side: stand it up
                axis = {"x": mn.Vector3(1, 0, 0), "z": mn.Vector3(0, 0, 1)}[up[0]]
                self.facts[oid]["base"] = mn.Quaternion.rotation(mn.Deg(float(up[1:])), axis)
            rec["model_change"] = ch
        del rules

    # ------------------------------------------------------------ spreading out
    # A thing on a surface (or in an open place) must have its centre over the surface and at
    # least SUPPORT_SHARE of its footprint over it, and its box must not overlap another thing's
    # box. When v2 put it elsewhere (overhanging, or overlapping when the surface was full), or
    # when it is not allowed on top of its base (CARRIERS), a new spot is looked for, in order:
    # its own place; another place of the same piece of furniture; the nearest surface of another
    # piece of furniture in the same room (last resort, listed as moved_to_other_furniture).
    def _support_area(self, place):
        grid = self.grid_for(place)
        if grid is None:
            return None, None
        V = grid.valid
        if self.snap["places"][place]["kind"] == "open":
            from scipy import ndimage
            low_wall = np.isfinite(grid.heights) & (grid.heights >= grid.y - 0.03) & (grid.heights < grid.y + 0.12)
            V = ndimage.binary_fill_holes(grid.valid | low_wall)
        return grid, V

    def _shape(self, oid):
        """The thing's own outline seen from below at its current turn (cells of scene.CELL,
        odd-sized, centred on its box centre): a cable loop is its cable, a plate its disc,
        not its whole box. The thing is put back where it was."""
        import magnum as mn
        thing = self.things[oid]
        keep = mn.Vector3(thing.translation)
        U = self._underside(oid)
        thing.translation = keep
        M = np.isfinite(U)
        if not M.any():
            M = np.ones_like(M)
        return M

    def _support_share(self, oid, place):
        """(box centre over the surface, share of the thing's outline over the surface)."""
        grid, V = self._support_area(place)
        if grid is None or not V.any():
            return False, 0.0
        lo, hi = self.footprint(oid)
        M = self._shape(oid)
        nz, nx = M.shape
        ci, cj = grid.index((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2)
        mi, mj = np.nonzero(M)
        gi, gj = ci + mi - nz // 2, cj + mj - nx // 2
        ok = (gi >= 0) & (gi < V.shape[0]) & (gj >= 0) & (gj < V.shape[1])
        over = np.zeros(len(gi), bool)
        over[ok] = V[gi[ok], gj[ok]]
        centre = 0 <= ci < V.shape[0] and 0 <= cj < V.shape[1] and bool(V[ci, cj])
        return centre, float(over.mean())

    def _occupied(self, grid, oid, y_lo, y_hi, per_thing=False):
        """Cells covered by other placed things whose boxes reach into [y_lo, y_hi]: each thing's
        own turned rectangle (its model box turned as drawn), not its world-aligned box, so a
        thing set at a slant does not block the corners around it. per_thing: also return
        {thing: its cell mask}."""
        import magnum as mn
        O = np.zeros(grid.valid.shape, bool)
        each = {}
        c = scene.CELL
        zc = grid.z0 + (np.arange(O.shape[0]) + 0.5) * c
        xc = grid.x0 + (np.arange(O.shape[1]) + 0.5) * c
        for o2, r2 in self.records.items():
            if o2 == oid or not r2.get("placed") or o2 not in self.things:
                continue
            lo, hi = self.footprint(o2)
            if hi[1] < y_lo or lo[1] > y_hi:
                continue
            j0, j1 = int(np.floor((lo[0] - grid.x0) / c)), int(np.floor((hi[0] - grid.x0) / c)) + 1
            i0, i1 = int(np.floor((lo[2] - grid.z0) / c)), int(np.floor((hi[2] - grid.z0) / c)) + 1
            i0, j0 = max(i0, 0), max(j0, 0)
            i1, j1 = min(i1, O.shape[0]), min(j1, O.shape[1])
            if i1 <= i0 or j1 <= j0:
                continue
            thing = self.things[o2]
            bb, M = thing.root_scene_node.cumulative_bb, thing.transformation
            corners = np.array([[q.x, q.z] for q in (M.transform_point(mn.Vector3(x, y, z))
                                                      for x in (bb.min.x, bb.max.x) for y in (bb.min.y, bb.max.y)
                                                      for z in (bb.min.z, bb.max.z))])
            X, Z = np.meshgrid(xc[j0:j1], zc[i0:i1])
            pts = np.stack([X.ravel(), Z.ravel()], 1)
            # inside the turned rectangle: project on its two horizontal axes
            ex = np.array([M.transform_vector(mn.Vector3(1, 0, 0)).x, M.transform_vector(mn.Vector3(1, 0, 0)).z])
            ez = np.array([M.transform_vector(mn.Vector3(0, 0, 1)).x, M.transform_vector(mn.Vector3(0, 0, 1)).z])
            ey = np.array([M.transform_vector(mn.Vector3(0, 1, 0)).x, M.transform_vector(mn.Vector3(0, 1, 0)).z])
            inside = np.ones(len(pts), bool)
            ctr = corners.mean(axis=0)
            for e in (ex, ez, ey):
                n = np.linalg.norm(e)
                if n < 1e-6:
                    continue
                e = e / n
                proj = corners @ e
                pp = pts @ e
                inside &= (pp >= proj.min() - 0.5 * c) & (pp <= proj.max() + 0.5 * c)
            del ctr
            O[i0:i1, j0:j1] |= inside.reshape(X.shape)
            if per_thing:
                m = np.zeros(O.shape, bool)
                m[i0:i1, j0:j1] = inside.reshape(X.shape)
                each[o2] = m
        return (O, each) if per_thing else O

    def _overlapping_any(self, oid, place):
        """Placed things (on any place) whose turned rectangles cover at least 3 cells of oid's own
        outline at its height, except those it may lie on or among (CARRIERS, cloth on cloth)."""
        grid, V = self._support_area(place)
        if grid is None:
            return []
        lo, hi = self.footprint(oid)
        M = self._shape(oid)
        nz, nx = M.shape
        ci, cj = grid.index((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2)
        mi, mj = np.nonzero(M)
        gi, gj = ci + mi - nz // 2, cj + mj - nx // 2
        ok = (gi >= 0) & (gi < V.shape[0]) & (gj >= 0) & (gj < V.shape[1])
        gi, gj = gi[ok], gj[ok]
        _, each = self._occupied(grid, oid, lo[1] + 0.01, hi[1] - 0.01, per_thing=True)
        objs = self.snap["objects"]
        out = []
        for o2, m in each.items():
            if int(m[gi, gj].sum()) < 3:
                continue
            if may_carry(objs[o2]["type"], objs[oid]["type"]) or may_carry(objs[oid]["type"], objs[o2]["type"]):
                continue
            out.append(o2)
        return sorted(out)

    def _tight_spot(self, oid, place, near=None, prefer=None, max_gap=None, on_contents=False):
        """Best spot on place: centre over the surface, >= SUPPORT_SHARE of the footprint over
        it, no overlap with other things' boxes (on_contents: allowed when nothing else fits,
        for open places such as a sink). Tries the thing as it is and turned a quarter.
        near: a box (lo, hi) to stay close to (gap <= max_gap if given). Returns a dict or None;
        leaves the thing turned as chosen."""
        from scipy import ndimage
        grid, V = self._support_area(place)
        if grid is None or not V.any():
            return None
        c = scene.CELL
        best = None
        yaws = self._square_yaws(oid, place)
        for k in (0, 1):
            lo_, hi_ = self.turn(oid, yaws[k])
            self.park(oid)
            hx, hz, hy = (hi_[0] - lo_[0]) / 2, (hi_[2] - lo_[2]) / 2, hi_[1] - lo_[1]
            M = self._shape(oid).astype(float)
            self.park(oid)
            share = ndimage.correlate(V.astype(float), M / M.sum(), mode="constant")
            O = self._occupied(grid, oid, grid.y + 0.01, grid.y + hy)
            occ = ndimage.correlate(O.astype(float), M, mode="constant") > 0.5
            base = V & (share >= SUPPORT_SHARE)
            for allow in ((False, True) if on_contents else (False,)):
                cand = base if allow else base & ~occ
                if cand.any():
                    break
            if not cand.any():
                continue
            ii, jj = np.nonzero(cand)
            xs, zs = grid.x0 + (jj + 0.5) * c, grid.z0 + (ii + 0.5) * c
            if near is not None:
                lo, hi = near
                gap = np.maximum(np.maximum(lo[0] - (xs + hx), (xs - hx) - hi[0]),
                                 np.maximum(lo[2] - (zs + hz), (zs - hz) - hi[2]))
                gap = np.maximum(gap, 0.0)
                if max_gap is not None:
                    keep = gap <= max_gap
                    if not keep.any():
                        continue
                    ii, jj, xs, zs, gap = ii[keep], jj[keep], xs[keep], zs[keep], gap[keep]
                dist = gap
            elif prefer is not None:
                dist = np.hypot(xs - prefer[0], zs - prefer[1])
            else:
                dist = np.zeros(len(xs))
            on_things = occ[ii, jj] if allow else np.zeros(len(ii), bool)
            whole = share[ii, jj] >= 0.999
            rnd = np.array([scene.steady("tight", oid, k, n) for n in range(len(ii))]) * 1e-4
            key = np.lexsort((dist + rnd, ~whole, on_things))
            n = int(key[0])
            score = (bool(on_things[n]), not bool(whole[n]), float(dist[n]))
            if best is None or score < best[0]:
                best = (score, dict(k=k, x=float(xs[n]), z=float(zs[n]), share=float(share[ii[n], jj[n]]),
                                    on_contents=bool(on_things[n]), gap=float(dist[n]) if near is not None else None))
        if best is None:
            self.turn(oid, self._yaw_before)
            self.park(oid)
            return None
        self.turn(oid, yaws[best[1]["k"]])
        self.park(oid)
        return best[1]

    def _square_yaws(self, oid, place):
        """Two turns to try: lined up with the place's furniture (no slant), and a quarter turn
        from that. Remembers the thing's current turn in self._yaw_before."""
        import magnum as mn
        q = self.things[oid].rotation * self.facts[oid]["base"].inverted()
        self._yaw_before = 2 * math.atan2(q.vector.y, q.scalar)
        g = self.snap["places"][place]["geometry"]
        if "rotation" in g and not g["source"].startswith("region"):
            w, _, yq, _ = g["rotation"]
            a = 2 * math.atan2(yq, w)
            k = round((self._yaw_before - a) / (math.pi / 2))
            first = a + k * math.pi / 2
        else:
            first = self._yaw_before
        del mn
        return first, first + math.pi / 2

    def _settle_y(self, oid, place, x, z):
        """Resting height on place's surface under the thing's own outline centred at (x, z): the
        highest scanned surface point under it (the scan keeps only points within 3 cm of the
        spot height, so a back cushion, a basin rim or a neighbour never lifts it)."""
        grid, V = self._support_area(place)
        M = self._shape(oid)
        nz, nx = M.shape
        ci, cj = grid.index(x, z)
        mi, mj = np.nonzero(M)
        gi, gj = ci + mi - nz // 2, cj + mj - nx // 2
        ok = (gi >= 0) & (gi < V.shape[0]) & (gj >= 0) & (gj < V.shape[1])
        gi, gj = gi[ok], gj[ok]
        sel = grid.valid[gi, gj] & np.isfinite(grid.heights[gi, gj])
        if not sel.any():
            return float(grid.y)
        return float(max(grid.y, np.max(grid.heights[gi[sel], gj[sel]])))

    def _put(self, oid, place, spot):
        grid = self.grids[place]
        hx, hz, _ = self._size(oid)
        x, z = spot["x"], spot["z"]
        self.park(oid)
        y = self._settle_y(oid, place, x, z)
        self.park(oid)
        self.set_at(oid, x, y, z)
        i0, j0, i1, j1 = grid.rect_cells(x, z, hx + scene.CELL, hz + scene.CELL)
        grid.used[i0:i1, j0:j1] = True
        rec = self.records[oid]
        rec.pop("_rest_y", None)
        rec.update(placed=True, x=x, y=y, z=z, did_not_fit=False, share_over_surface=round(spot["share"], 2))
        if place != self.snap["objects"][oid]["place"]:
            rec["drawn_on"] = place
        else:
            rec.pop("drawn_on", None)
        return y

    def _free_spot(self, grid, oid, hx, hz, near, need=0.6):
        """SnapshotHomeV2._free_spot, except on furniture surfaces (not floors, not sinks) when the
        thing fits wholly on free cells and has no reference to stay near: v2 took a steady random
        such spot, which scattered things over the middle, so a full nightstand had no room left
        for the last few. Here the spot is one as close to the edge of the free area (the surface
        edge or a neighbour) as possible, so things are packed against each other and the edges."""
        from scipy import ndimage
        place = next((p for p, g in self.grids.items() if g is grid), None)
        P = self.snap["places"].get(place) if place else None
        if near is not None or P is None or P["kind"] != "surface" or P["furniture"] == "floor" or not grid.valid.any():
            return super()._free_spot(grid, oid, hx, hz, near, need)
        free = grid.valid & ~grid.used
        size = (2 * max(1, int(hz / scene.CELL)) + 1, 2 * max(1, int(hx / scene.CELL)) + 1)
        share = ndimage.uniform_filter(free.astype(float), size=size, mode="constant")
        cand = (share >= 0.999) & free
        if not cand.any():
            return super()._free_spot(grid, oid, hx, hz, near, need)
        D = ndimage.distance_transform_edt(free)
        ii, jj = np.nonzero(cand)
        d = D[ii, jj]
        pool = np.flatnonzero(d <= d.min() + 1.0)
        k = int(pool[int(scene.steady("pack", oid) * len(pool))])
        x, z = grid.x0 + (jj[k] + 0.5) * scene.CELL, grid.z0 + (ii[k] + 0.5) * scene.CELL
        i0, j0, i1, j1 = grid.rect_cells(x, z, hx + scene.CELL, hz + scene.CELL)
        grid.used[i0:i1, j0:j1] = True
        self._crowded = False
        return float(x), float(z), 1.0

    def _furniture_key(self, place):
        P = self.snap["places"][place]
        return (P["room"], P["furniture"])

    def _relocate(self, oid, why, frm, near=None, prefer=None, first_kind="respaced_on_its_place"):
        """Find a spot in the order: own place, same furniture, other furniture in the room. When
        none is found the thing is put back exactly where it was (turn and position)."""
        import magnum as mn
        thing = self.things[oid]
        keep = (thing.translation, thing.rotation)        # magnum returns copies
        got = self._relocate_try(oid, why, frm, near, prefer, first_kind)
        if got is None:
            thing.rotation, thing.translation = keep[1], keep[0]
        return got

    def _relocate_try(self, oid, why, frm, near, prefer, first_kind):
        objs, places = self.snap["objects"], self.snap["places"]
        place = objs[oid]["place"]
        P = places[place]
        on_floor = P["furniture"] == "floor"
        # 1. own place (near the base first when there is one)
        tries = [(place, dict(near=near, max_gap=0.15) if near is not None else dict(prefer=prefer))]
        if near is not None:
            tries.append((place, dict(near=near)))
        for p, kw in tries:
            spot = self._tight_spot(oid, p, **kw)
            if spot is not None:
                self._put(oid, p, spot)
                what = f"{why}: put on a free spot of {p}" + (f", {100 * spot['gap']:.0f} cm from its base"
                                                             if spot.get("gap") is not None else "")
                self._repair(oid, first_kind, what, frm, f"on {p}")
                return "own place"
        if near is not None:
            ref = near
        else:
            lo, hi = self.footprint(oid)
            ref = (lo, hi)
        cx, cz = (ref[0][0] + ref[1][0]) / 2, (ref[0][2] + ref[1][2]) / 2
        # 2. same furniture, 3. other furniture in the room
        same, other = [], []
        for p, Q in places.items():
            if p == place or Q["room"] != P["room"] or Q["kind"] != "surface":
                continue          # never into a sink or bathtub, never into a closed place
            if (Q["furniture"] == "floor") != on_floor:
                continue
            d = math.hypot(Q["geometry"]["center"][0] - cx, Q["geometry"]["center"][2] - cz)
            if not on_floor and self._furniture_key(p) == self._furniture_key(place):
                same.append((d, p))
            elif Q["kind"] == "surface":
                other.append((d, p))
        for group, kind in ((sorted(same), "moved_on_same_furniture"), (sorted(other)[:10], "moved_to_other_furniture")):
            for _, p in group:
                spot = self._tight_spot(oid, p, prefer=(cx, cz))
                if spot is None:
                    continue
                self._put(oid, p, spot)
                self._repair(oid, kind, f"{why}; no free spot on {place}" +
                             ("" if kind == "moved_on_same_furniture" else
                              f" or elsewhere on the {P['furniture']}: moved to the nearest other furniture with room"),
                             frm, f"on {p}")
                return kind
        return None

    def _place_on_object(self, oid, base, hx, hz):
        objs = self.snap["objects"]
        place = objs[oid]["place"]
        btype, ttype = objs[base]["type"], objs[oid]["type"]
        under = objs[base].get("relation") == "under" and objs[base].get("reference") == oid
        if may_carry(btype, ttype) or self.snap["places"][place]["kind"] != "surface":
            return super()._place_on_object(oid, base, hx, hz)
        if under and (ttype in lib.scene.LIES_FLAT or lib.is_soft(ttype)) and \
                (ttype in BOOKS | PAPER or lib.is_soft(ttype)):
            # "A under B" with B a cloth or a paper: B covers A, as the snapshot means
            return super()._place_on_object(oid, base, hx, hz)
        word = f"{base} is under it in the snapshot" if under else f"the snapshot puts it on top of {base}"
        why = f"{word}, but a {btype} is not something a {ttype} is set on"
        self.park(oid)
        got = self._relocate(oid, why, f"on top of {base}", near=self.footprint(base), first_kind="beside_not_a_carrier")
        if got:
            self.records[oid]["how"] = f"beside {base} (not stacked)" if got == "own place" else \
                f"on {self.records[oid].get('drawn_on')} (not stacked; no room near {base})"
            self.records[oid]["beside"] = base
            return
        super()._place_on_object(oid, base, hx, hz)
        self._repair(oid, "stacked_no_free_surface", f"{why}; no surface in the room has free room, so it "
                     "stays on top", f"on top of {base}", f"on top of {base}")

    def place_one(self, oid, under_of):
        """SnapshotHomeV2.place_one; then, for a thing on a surface or in an open place (not on or in
        another thing), when it overhangs (centre off the surface or under SUPPORT_SHARE of its
        footprint over it) or overlaps its neighbours, a new spot (see _relocate). Cloth that
        overlaps only cloth (a heap of clothes) is left, unless it overhangs."""
        super().place_one(oid, under_of)
        objs = self.snap["objects"]
        rec = self.records[oid]
        place = objs[oid]["place"]
        if not rec.get("placed") or oid not in self.things or place not in self.snap["places"] or \
                self.snap["places"][place]["kind"] not in ("surface", "open") or rec.get("_on") or rec.get("_in") or \
                rec.get("drawn_on") or rec.get("beside") and any(r["kind"] in V3_MOVES for r in rec.get("repairs", [])):
            return
        bad = [r for r in rec.get("repairs", []) if r["kind"] in ("overlap", "overhang", "open_place_crowded")]
        centre, share = self._support_share(oid, place)
        overhang = not centre or share < SUPPORT_SHARE
        overlap = any(r["kind"] in ("overlap", "open_place_crowded") for r in bad)
        if not overlap and self.snap["places"][place]["kind"] == "surface":
            # v2 only saw neighbours from the same place; a thing moved here from elsewhere counts too
            others = self._overlapping_any(oid, place)
            if others:
                overlap = True
                bad.append({"kind": "_v3_overlap", "others": others})
        if overlap and not overhang:
            nb = self._overlapping(oid) + next((r["others"] for r in bad if r["kind"] == "_v3_overlap"), [])
            if self.snap["places"][place]["kind"] == "open" or \
                    (lib.is_soft(objs[oid]["type"]) and nb and all(lib.is_soft(objs[n]["type"]) for n in nb)):
                return            # a heap in a sink or a heap of clothes is allowed
        if not overhang and not overlap:
            lo, hi = self.footprint(oid)
            cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
            keep = lo[1]
            y = self._settle_y(oid, place, cx, cz)
            if keep - y > 0.03 and not self._overlapping(oid) and self.snap["places"][place]["kind"] == "surface":
                self.set_at(oid, cx, y, cz)
                rec["y"] = y
                self._repair(oid, "lowered_onto_surface", f"rested {100 * (keep - y):.0f} cm above {place} (on a "
                             "raised part of the furniture or a neighbour's box): set down on the surface",
                             f"on {place}", f"y={y:.3f}")
            else:
                self.set_at(oid, cx, keep, cz)
            for r in bad:         # v2's overhang counted cells kept free around neighbours; it is over the surface
                if r["kind"] == "overhang":
                    rec["repairs"].remove(r)
                    self.repairs.remove(r)
            return
        others = next((r["others"] for r in bad if r["kind"] == "_v3_overlap"), [])
        names = sorted(set(self._overlapping(oid)) | set(others))
        what = (f"{'centre off the surface, ' if not centre else ''}{100 * share:.0f}% of its footprint over "
                f"{place}" if overhang else f"no free room on {place}: it would overlap {', '.join(names) or 'its neighbours'}")
        lo, hi = self.footprint(oid)
        got = self._relocate(oid, what, f"a free part of {place}", prefer=((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2))
        bad = [r for r in bad if r["kind"] != "_v3_overlap"]
        if got:
            for r in bad:
                rec["repairs"].remove(r)
                self.repairs.remove(r)
            rec["how"] = f"on {rec.get('drawn_on') or place}, a free spot found by the v3 support rule"
        elif overhang and not any(r["kind"] == "overhang" for r in bad):
            self._repair(oid, "overhang", f"{what}; no free spot in the room", f"a free part of {place}",
                         f"{100 * share:.0f}% over the surface")
        elif others and not any(r["kind"] == "overlap" for r in bad):
            self._repair(oid, "overlap", f"{what}; no free spot in the room", f"a free part of {place}",
                         f"overlaps {', '.join(others)}")


V3_MOVES = {"beside_not_a_carrier", "respaced_on_its_place", "moved_on_same_furniture", "moved_to_other_furniture",
            "stacked_no_free_surface"}


lib.HOME_CLASS = SnapshotHomeV3
