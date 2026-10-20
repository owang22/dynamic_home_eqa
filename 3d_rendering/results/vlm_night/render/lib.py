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
from scipy import ndimage

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


SOFT_WORDS = ("towel", "shirt", "pants", "blouse", "trousers", "cardigan", "sweater", "jacket", "apron",
              "robe", "dress", "jeans", "hoodie", "scarf", "socks", "gloves", "sheet", "pillowcase",
              "blanket", "napkin", "cloth", "bath mat", "garment bag", "fabric samples", "delicates bag")
MAP_CELL = 0.01            # cell of the height maps used by SnapshotHomeV2 (metres)


def is_soft(typ: str) -> bool:
    return any(w in typ for w in SOFT_WORDS)


class SnapshotHomeV2(SnapshotHome):
    """SnapshotHome with three placement fixes and a record of every repair (hssd_a_v2).

    1. Open containers (basket, bowl, tray) and open places (sinks, bathtub, fireplace opening):
       the committed code dropped every content at the centre with a few cm of jitter, and each
       rested on the one before, so contents stood in towers. Here the inside of a container is
       measured from above (cells of the container's own mesh lying low, below its rim) and each
       content is set on a free part of it, as low as it goes. It rests on another content only
       when no free part fits it; soft things (clothes, towels) then sink into the soft thing
       below by up to 40% of their height, as a pile of laundry does.
    2. Thing on thing: the committed code rested the top thing on the highest drawn point under
       a footprint as wide as the base's box top, so a towel meant for a tray rested on the bowls
       beside the tray. Here the base's real upper surface is measured from above; the thing's
       centre goes over it, at the spot where it rests lowest (on the base, not on neighbours).
       When the base is much smaller than the thing (its top under a quarter of the thing's
       footprint, or a tall thing on a narrower top), the thing is put beside the base on the
       same surface instead, and that is recorded.
    3. Every repair is recorded per object in self.repairs: {object, kind, what, from, to}.
    """

    # ------------------------------------------------------------------ helpers
    def _repair(self, oid, kind, what, frm, to):
        r = {"object": oid, "kind": kind, "what": what, "from": frm, "to": to}
        self.repairs.append(r)
        self.records[oid].setdefault("repairs", []).append(r)

    @property
    def repairs(self):
        if not hasattr(self, "_repairs"):
            self._repairs = []
        return self._repairs

    def _look_down(self, cx, cz, top_y, half, need_sid=None):
        """Down camera over (cx, cz). Tries a height that covers `half` metres around the
        centre, then lower ones, until the wanted mesh is seen (a shelf above may block).
        Placed things lying wholly above top_y over the view are moved away meanwhile (a
        towel on bottles beside a thermos would hide the thermos top)."""
        import magnum as mn
        moved = {}
        for o2, r2 in self.records.items():
            if not r2.get("placed") or o2 not in self.things:
                continue
            lo, hi = self.footprint(o2)
            if lo[1] > top_y + 0.005 and hi[0] > cx - half and lo[0] < cx + half and hi[2] > cz - half and lo[2] < cz + half:
                moved[o2] = self.things[o2].translation
                self.things[o2].translation = moved[o2] + mn.Vector3(0, 80, 0)
        world = sid = None
        try:
            for lift in (float(np.clip(half + 0.05, 0.25, 0.6)), 0.15, 0.08):
                world, sid = self.down_points(np.array([cx, top_y + lift, cz]))
                if need_sid is None or int((sid == need_sid).sum()) > 20:
                    break
        finally:
            for o2, t in moved.items():
                self.things[o2].translation = t
        return world, sid

    @staticmethod
    def _bin(world, sid, sel, x0, z0, nx, nz, cell=MAP_CELL):
        """Highest selected point per cell (-inf where none) and the id of that point."""
        H = np.full((nz, nx), -np.inf)
        O = np.full((nz, nx), -1)
        ok = sel & np.isfinite(world[..., 1])
        gi = np.floor((world[..., 2][ok] - z0) / cell).astype(int)
        gj = np.floor((world[..., 0][ok] - x0) / cell).astype(int)
        ys, ss = world[..., 1][ok], sid[ok]
        inside = (gi >= 0) & (gi < nz) & (gj >= 0) & (gj < nx)
        gi, gj, ys, ss = gi[inside], gj[inside], ys[inside], ss[inside]
        order = np.argsort(ys)
        H[gi[order], gj[order]] = ys[order]
        O[gi[order], gj[order]] = ss[order]
        return H, O

    def _support_sel(self, world, sid, place, extra_sids=()):
        """Points a thing on `place` may rest on (same rule as SnapshotHome.rest_height)."""
        objs = self.snap["objects"]
        same = [f["sid"] for o2, f in self.facts.items()
                if objs[o2]["place"] == place and self.records[o2].get("placed")]
        sel = np.isin(sid, same + list(extra_sids))
        g = self.snap["places"][place]["geometry"]
        if g["source"].startswith("region"):
            sel |= (sid == 0) & (world[..., 1] < g["height"] + 0.05)
        else:
            spot_y = self.grids[place].y if place in self.grids else g["height"]
            sel |= np.isin(sid, list(self.ids_of(self.furniture_of(place)))) & (world[..., 1] <= spot_y + 0.10)
        return sel

    def _turn_extra(self, oid, angle):
        import magnum as mn
        thing = self.things[oid]
        thing.rotation = mn.Quaternion.rotation(mn.Rad(angle), mn.Vector3(0, 1, 0)) * thing.rotation
        thing.translation = mn.Vector3(0, 0, 0)
        lo, hi = common.box_of(thing)
        thing.translation = mn.Vector3(0, -30, 0)     # out of sight of the down cameras
        return (hi[0] - lo[0]) / 2, (hi[2] - lo[2]) / 2, hi[1] - lo[1]

    def _size(self, oid):
        lo, hi = self.footprint(oid)
        return (hi[0] - lo[0]) / 2, (hi[2] - lo[2]) / 2, hi[1] - lo[1]

    def _sid_names(self, sids):
        by_sid = {f["sid"]: o for o, f in self.facts.items()}
        out = []
        for s in sids:
            s = int(s)
            if s in by_sid:
                out.append(by_sid[s])
            elif s == 0:
                out.append("the house shell")
            elif s >= 0:
                out.append("furniture")
        return sorted(set(out))

    def _choose(self, oid, cand_i, cand_j, x0, z0, H, free=None, prefer=None, cell=MAP_CELL, within=None):
        """Best (orientation, cell) for a thing whose centre may be at the candidate cells.
        H: height map of what it may rest on. free: cells it may cover without overlapping
        (None = no such rule). within: cells the footprint should stay over (90%) (None = no
        such rule). Picks, in order: whole footprint on free cells, footprint over `within`, lowest resting
        height (5 mm steps), nearest to `prefer` (a cell), a steady random tie-break.
        Leaves the thing turned to the chosen orientation; returns a dict."""
        best = None
        for k, angle in enumerate((0.0, math.pi / 2)):
            hx, hz, hy = self._turn_extra(oid, angle if k == 1 else 0.0)
            ny, nx = 2 * int(round(hz / cell)) + 1, 2 * int(round(hx / cell)) + 1
            M = ndimage.maximum_filter(H, size=(ny, nx), mode="constant", cval=-np.inf)
            y = M[cand_i, cand_j]
            if free is not None:
                share = ndimage.uniform_filter(free.astype(float), size=(ny, nx), mode="constant")[cand_i, cand_j]
            else:
                share = np.ones(len(cand_i))
            fits = share >= 0.98
            if within is not None:
                inside = ndimage.uniform_filter(within.astype(float), size=(ny, nx), mode="constant")[cand_i, cand_j] >= 0.9
            else:
                inside = np.ones(len(cand_i), bool)
            near = np.zeros(len(cand_i)) if prefer is None else \
                np.hypot(cand_i - prefer[0], cand_j - prefer[1]) * cell
            rnd = np.array([scene.steady("pick", oid, k, n) for n in range(len(cand_i))]) * 0.01
            yk = np.where(np.isfinite(y), np.round(y / 0.005), -1e9)
            key = np.lexsort((near + rnd, yk, ~inside, ~fits))
            n = int(key[0])
            cand = dict(k=k, angle=angle, n=n, fits=bool(fits[n]), share=float(share[n]),
                        y=float(y[n]) if np.isfinite(y[n]) else None, hx=hx, hz=hz, hy=hy,
                        x=x0 + (cand_j[n] + 0.5) * cell, z=z0 + (cand_i[n] + 0.5) * cell)
            score = (not cand["fits"], not inside[n], yk[n], near[n] + rnd[n])
            if best is None or score < best[0]:
                best = (score, cand)
            # turn back before trying the next orientation
            if k == 1:
                self._turn_extra(oid, -math.pi / 2)
        c = best[1]
        if c["k"] == 1:
            self._turn_extra(oid, math.pi / 2)
        return c

    # ------------------------------------------------------------------ order
    def place_everything(self):
        """scene.Home.place_everything, except that things inside open places (sinks, the
        bathtub, the fireplace opening) are placed first, flattest first, so that when a sink
        is too full for all of them, plates lie at the bottom and mugs and pans on them,
        not plates balanced on mug rims. They depend on nothing, so moving them first keeps
        every thing after what it rests on."""
        import time as _time
        t0 = _time.time()
        self.add_objects()
        objs = self.snap["objects"]
        under_of = {o["reference"]: oid for oid, o in objs.items() if o["relation"] == "under"}
        done, order = set(), []
        pending = list(sorted(objs))
        while pending:
            progressed = False
            for oid in list(pending):
                o = objs[oid]
                needs = o["reference"] if o["reference_kind"] == "object" and o["relation"] != "under" else None
                if oid in under_of:
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

        def in_open_place(oid):
            o = objs[oid]
            return o["place"] in self.snap["places"] and self.snap["places"][o["place"]]["kind"] == "open" and \
                o["reference_kind"] == "place" and oid not in under_of and oid in self.things

        def height(oid):
            import magnum as mn
            thing = self.things[oid]
            keep = thing.rotation
            thing.rotation = self.facts[oid]["base"]
            thing.translation = mn.Vector3(0, 0, 0)
            lo, hi = common.box_of(thing)
            thing.rotation = keep
            self.park(oid)
            return float(hi[1] - lo[1])

        first = sorted([o for o in order if in_open_place(o)], key=lambda o: (height(o), o))
        order = first + [o for o in order if o not in set(first)]
        for oid in order:
            self.place_one(oid, under_of)
        for place in self.opened_for_placing:
            self.open_part(place, 0.0)
            self.grids.pop(place, None)
        self.timings["place_s"] = round(_time.time() - t0, 2)

    # ------------------------------------------------------------------ 2. thing on thing
    def _place_on_object(self, oid, base, hx, hz):
        objs = self.snap["objects"]
        rec = self.records[oid]
        place = objs[oid]["place"]
        btype, holds = objs[base]["type"], objs[base]["holds"]
        if holds == "open" and ("tray" in btype or "platter" in btype):
            return self._place_in_open(oid, base, word="on")
        lo, hi = self.footprint(base)
        bsid = self.facts[base]["sid"]
        cell = MAP_CELL
        m = max(hx, hz) + 0.04
        x0, z0 = lo[0] - m, lo[2] - m
        nx, nz = int((hi[0] - lo[0] + 2 * m) / cell) + 1, int((hi[2] - lo[2] + 2 * m) / cell) + 1
        cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
        world, sid = self._look_down(cx, cz, hi[1], max(hi[0] - lo[0], hi[2] - lo[2]) / 2 + m, need_sid=bsid)
        Hb, _ = self._bin(world, sid, sid == bsid, x0, z0, nx, nz)
        if not np.isfinite(Hb).any():
            super()._place_on_object(oid, base, hx, hz)
            self._repair(oid, "base_not_seen", f"the top of {base} could not be seen from above; "
                         "rested on its box top (old rule)", f"on top of {base}", f"y={rec['y']:.3f}")
            return
        top = float(Hb[np.isfinite(Hb)].max())
        # its upper surface: what lies within half its height of its top (a book's face, a
        # mug's rim, a tissue box's top under the tissue, most of a heap of cloth)
        T = Hb >= top - max(0.015, 0.5 * (top - lo[1]))
        F = ndimage.binary_fill_holes(ndimage.binary_closing(T, iterations=2) | T)
        _, _, hy = self._size(oid)
        area_F = F.sum() * cell ** 2
        fi, fj = np.nonzero(F)
        ext = min(np.ptp(fi) + 1, np.ptp(fj) + 1) * cell
        min_side = 2 * min(hx, hz)
        tall = hy >= 1.5 * min_side
        # cloth drapes over a smaller base (a shirt on a pair of trousers), so only a tiny
        # base (under a tenth of its footprint, a towel on a sponge) sends cloth beside it
        share_min = 0.1 if is_soft(objs[oid]["type"]) else 0.25
        small = area_F < share_min * 4 * hx * hz or (tall and ext < 0.8 * min_side)
        why_small = (f"its top ({area_F * 1e4:.0f} cm2) is under {share_min:.0%} of the thing's footprint "
                     f"({4 * hx * hz * 1e4:.0f} cm2)") if area_F < share_min * 4 * hx * hz else \
            f"a tall thing ({hy * 100:.0f} cm) on a top narrower ({ext * 100:.0f} cm) than itself"
        if small and self.snap["places"][place]["kind"] != "closed" and self._beside(oid, base, hx, hz, why_small):
            return
        sel = self._support_sel(world, sid, place, extra_sids=[bsid])
        Hs, Os = self._bin(world, sid, sel, x0, z0, nx, nz)
        Hs = np.maximum(Hs, Hb)
        C = ndimage.binary_erosion(F)
        if not C.any():
            C = F
        ci, cj = np.nonzero(C)
        if len(ci) > 800:
            keep = np.linspace(0, len(ci) - 1, 800).astype(int)
            ci, cj = ci[keep], cj[keep]
        c = self._choose(oid, ci, cj, x0, z0, Hs, prefer=(fi.mean(), fj.mean()))
        y = top if c["y"] is None else c["y"]
        self.set_at(oid, c["x"], y, c["z"])
        rec["_on"] = base
        rec.update(placed=True, how=f"on top of {base} (on its measured top surface)", x=c["x"], y=y, z=c["z"],
                   did_not_fit=y > top + 0.03)
        if small:
            self._repair(oid, "small_base_kept", f"{base} is much smaller than it ({why_small}), but its "
                         "place is closed, so it stays on top", f"on top of {base}", f"on top of {base}")
        if y > top + 0.03:
            i0, j0 = int((c["z"] - c["hz"] - z0) / cell), int((c["x"] - c["hx"] - x0) / cell)
            i1, j1 = int((c["z"] + c["hz"] - z0) / cell) + 1, int((c["x"] + c["hx"] - x0) / cell) + 1
            under = Os[max(i0, 0):i1, max(j0, 0):j1][Hs[max(i0, 0):i1, max(j0, 0):j1] > top + 0.03]
            self._repair(oid, "on_neighbours", f"no part of {base}'s top is clear: rests {100 * (y - top):.0f} cm "
                         f"above it, on {', '.join(self._sid_names(np.unique(under))) or 'something'}",
                         f"on top of {base} (top at y={top:.3f})", f"y={y:.3f}")

    def _beside(self, oid, base, hx, hz, why):
        rec = self.records[oid]
        place = self.snap["objects"][oid]["place"]
        grid = self.grid_for(place)
        if grid is None or not grid.valid.any():
            return False
        spot = self._free_spot(grid, oid, hx, hz, self.footprint(base))
        if spot is None:
            return False
        x, z, share = spot
        hx, hz, _ = self._size(oid)
        self.park(oid)
        if rec.get("_rest_y") is not None:
            y = rec.pop("_rest_y")
        else:
            y = self.rest_height(x, z, hx, hz, grid.y + 0.25 if grid.y > 0.05 else 1.0, place=place)
            y = grid.y if y is None or y < grid.y - 0.03 or y > grid.y + 0.5 else y
        self.set_at(oid, x, y, z)
        rec.update(placed=True, how=f"beside {base} on the same surface ({base} is too small to hold it)",
                   x=x, y=y, z=z, did_not_fit=self._crowded, beside=base)
        self._repair(oid, "beside_small_base", f"{base} is much smaller than it: {why}",
                     f"on top of {base}", f"next to {base} on {place}")
        return True

    # ------------------------------------------------------------------ 1. inside things
    def _place_inside_object(self, oid, ref, hx, hz, hy):
        if not self.records.get(ref, {}).get("placed"):
            return super()._place_inside_object(oid, ref, hx, hz, hy)
        if self.snap["objects"][ref]["holds"] == "open":
            return self._place_in_open(oid, ref, word="inside")
        return self._place_in_closed(oid, ref, hx, hz, hy)

    def _inside_of(self, ref):
        """Cells of an open container's inside, measured from above while it is empty:
        (x0, z0, inside mask, floor heights). Cached per container."""
        cache = self.__dict__.setdefault("_insides", {})
        if ref in cache:
            return cache[ref]
        lo, hi = self.footprint(ref)
        cell = MAP_CELL
        x0, z0 = lo[0] - cell, lo[2] - cell
        nx, nz = int((hi[0] - lo[0]) / cell) + 3, int((hi[2] - lo[2]) / cell) + 3
        rsid = self.facts[ref]["sid"]
        world, sid = self._look_down((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, hi[1],
                                     max(hi[0] - lo[0], hi[2] - lo[2]) / 2, need_sid=rsid)
        Hc, _ = self._bin(world, sid, sid == rsid, x0, z0, nx, nz)
        depth = hi[1] - lo[1]
        seen = np.isfinite(Hc)
        how = "measured"
        if seen.sum() < 10:
            # not visible from above (a shelf over it): its box, shrunk, with a flat bottom
            ii, jj = np.mgrid[0:nz, 0:nx]
            xs, zs = x0 + (jj + 0.5) * cell, z0 + (ii + 0.5) * cell
            inner = (np.abs(xs - (lo[0] + hi[0]) / 2) <= 0.42 * (hi[0] - lo[0])) & \
                    (np.abs(zs - (lo[2] + hi[2]) / 2) <= 0.42 * (hi[2] - lo[2]))
            Hc = np.where(inner, lo[1] + 0.005, hi[1])
            how = "box (not seen from above)"
        else:
            # the inside: cells of the container's own mesh lying below its rim (lower than
            # 35% of its height under the top); a flat top (a board-like tray): all of it
            span = float(Hc[seen].max() - Hc[seen].min())
            inner = seen & (Hc <= hi[1] - max(0.35 * depth, 0.005))
            filled = ndimage.binary_fill_holes(seen)
            if span < max(0.3 * depth, 0.01) and seen.sum() >= 0.6 * filled.sum():
                inner = ndimage.binary_erosion(seen)
                how = "flat top"
            elif inner.sum() < max(10, 0.15 * filled.sum()):
                # only the rim is drawn from above (inside faces are one-sided and culled):
                # its box, shrunk, with a flat bottom; the rim stays as seen
                ii, jj = np.mgrid[0:nz, 0:nx]
                xs, zs = x0 + (jj + 0.5) * cell, z0 + (ii + 0.5) * cell
                inner = (np.abs(xs - (lo[0] + hi[0]) / 2) <= 0.42 * (hi[0] - lo[0])) & \
                        (np.abs(zs - (lo[2] + hi[2]) / 2) <= 0.42 * (hi[2] - lo[2]))
                Hc = np.where(inner & ~seen, lo[1] + 0.01, Hc)
                how = "box (inside not drawn from above)"
            er = ndimage.binary_erosion(inner)
            if er.sum() >= 0.5 * inner.sum():
                inner = er
        cache[ref] = (x0, z0, inner, Hc, how)
        return cache[ref]

    def _fold(self, oid, f):
        """Swap the thing's model for the same mesh scaled by f across and 1/f up (in the
        model's own axes: the one that points up after its lying-flat turn gets 1/f)."""
        import habitat_sim
        import magnum as mn
        old = self.things[oid]
        rot = old.rotation
        s0 = old.creation_attributes.scale
        up_local = self.facts[oid]["base"].inverted().transform_vector(mn.Vector3(0, 1, 0))
        v = int(np.argmax(np.abs([up_local.x, up_local.y, up_local.z])))
        sc = [s0[0] * f, s0[1] * f, s0[2] * f]
        sc[v] = s0[v] / f
        mesh = old.creation_attributes.render_asset_handle
        key = f"{old.creation_attributes.handle}|fold{f:.3f}"
        t = self.templates.create_new_template(key)
        t.render_asset_handle = mesh
        t.collision_asset_handle = mesh
        t.scale = mn.Vector3(*sc)
        tid = self.templates.register_template(t, key)
        sid = self.facts[oid]["sid"]
        self.rom.remove_object_by_id(old.object_id)
        thing = self.rom.add_object_by_template_id(tid, light_setup_key=common.LIGHTS)
        thing.motion_type = habitat_sim.physics.MotionType.KINEMATIC
        thing.semantic_id = sid
        for node in thing.visual_scene_nodes:
            node.semantic_id = sid
        thing.rotation = rot
        thing.translation = mn.Vector3(0, -60, 0)
        self.things[oid] = thing
        self.records[oid]["folded"] = round(f, 3)

    def _contents_of(self, ref):
        return [o for o, r in self.records.items() if r.get("_in") == ref and r.get("placed")]

    def _box_mask(self, oids, x0, z0, shape, cell=MAP_CELL):
        used = np.zeros(shape, bool)
        tops = np.full(shape, -np.inf)
        for o in oids:
            lo, hi = self.footprint(o)
            i0, j0 = max(int((lo[2] - z0) / cell), 0), max(int((lo[0] - x0) / cell), 0)
            i1, j1 = int((hi[2] - z0) / cell) + 1, int((hi[0] - x0) / cell) + 1
            used[i0:i1, j0:j1] = True
            tops[i0:i1, j0:j1] = np.maximum(tops[i0:i1, j0:j1], hi[1])
        return used, tops

    def _place_in_open(self, oid, ref, word="inside"):
        objs = self.snap["objects"]
        rec = self.records[oid]
        lo, hi = self.footprint(ref)
        x0, z0, inner, Hc, how_in = self._inside_of(ref)
        contents = self._contents_of(ref)
        used, _ = self._box_mask(contents, x0, z0, inner.shape)
        # what the thing may rest on now: the container's inside and the contents' drawn tops
        world, sid = self._look_down((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, hi[1], max(hi[0] - lo[0], hi[2] - lo[2]) / 2)
        csids = [self.facts[o]["sid"] for o in contents]
        Hk, Ok = self._bin(world, sid, np.isin(sid, csids), x0, z0, inner.shape[1], inner.shape[0])
        if how_in.startswith("box"):
            _, Hk2 = self._box_mask(contents, x0, z0, inner.shape)
            Hk = np.maximum(Hk, Hk2)
        floor = np.where(inner, Hc, -np.inf)
        H = np.maximum(floor, Hk)
        ci, cj = np.nonzero(inner)
        prefer = (ci.mean(), cj.mean())
        soft = is_soft(objs[oid]["type"])

        def best_cover(hx_, hz_):
            out = 0.0
            for a_, b_ in ((hx_, hz_), (hz_, hx_)):
                size = (2 * int(round(b_ / MAP_CELL)) + 1, 2 * int(round(a_ / MAP_CELL)) + 1)
                out = max(out, float(ndimage.uniform_filter(inner.astype(float), size=size, mode="constant")[ci, cj].max()))
            return out

        hx0, hz0, hy0 = self._size(oid)
        if soft and best_cover(hx0, hz0) < 0.95:
            # a garment or towel wider than the inside is folded to fit: its footprint shrinks
            # and it grows thicker by the same factor (as much cloth, folded once or twice)
            f = 1.0
            while f > 0.45 and best_cover(hx0 * f, hz0 * f) < 0.95:
                f -= 0.05
            f = max(f, 0.45)
            self._fold(oid, f)
            self._repair(oid, "folded_to_fit", f"wider than the inside of {ref}: folded, its footprint "
                         f"scaled by {f:.2f} and its thickness by {1 / f:.2f}",
                         f"{2 * hx0 * 100:.0f} x {2 * hz0 * 100:.0f} cm, {hy0 * 100:.0f} cm thick",
                         f"{2 * hx0 * f * 100:.0f} x {2 * hz0 * f * 100:.0f} cm, {hy0 / f * 100:.0f} cm thick")
        c = self._choose(oid, ci, cj, x0, z0, H, free=inner & ~used, prefer=prefer, within=inner)
        i, j = ci[c["n"]], cj[c["n"]]
        fp = (slice(max(i - int(round(c["hz"] / MAP_CELL)), 0), i + int(round(c["hz"] / MAP_CELL)) + 1),
              slice(max(j - int(round(c["hx"] / MAP_CELL)), 0), j + int(round(c["hx"] / MAP_CELL)) + 1))
        cover = float(inner[fp].mean())
        under_floor = floor[fp][np.isfinite(floor[fp])]
        under_all = H[fp][np.isfinite(H[fp])]
        if soft and len(under_all):
            # cloth drapes: it rests on the middle of what is under it, not on the highest point
            fl = float(np.median(under_floor)) if len(under_floor) else lo[1] + 0.005
            y = float(np.median(under_all))
        else:
            fl = float(under_floor.max()) if len(under_floor) else lo[1] + 0.005
            y = c["y"] if c["y"] is not None else fl
        if cover < 0.9:
            # wider than the inside: it lies across the container, on its rim
            rim = np.maximum(H, Hc)[fp]
            y = float(rim[np.isfinite(rim)].max()) if np.isfinite(rim).any() else hi[1]
        stacked = cover >= 0.9 and y > fl + 0.02
        if stacked and soft:
            y = max(fl, y - 0.4 * c["hy"])
        self.set_at(oid, c["x"], y, c["z"])
        rec["_in"] = ref
        rec.update(placed=True, how=f"{word} open container {ref}, on a free part of its inside" if not stacked
                   else f"{word} open container {ref}, resting on its other contents (no free part fits)",
                   x=c["x"], y=y, z=c["z"], did_not_fit=bool(stacked or cover < 0.9))
        if cover < 0.9:
            self._repair(oid, "wider_than_container", f"wider than the inside of {ref} ({cover:.0%} of its "
                         "footprint over the inside): lies across the container, on its rim",
                         f"{word} {ref}", f"centre ({c['x']:.2f}, {c['z']:.2f}), y={y:.3f}")
        if stacked:
            under = self._sid_names(np.unique(Ok[fp][Hk[fp] > fl + 0.02]))
            self._repair(oid, "stacked_in_container", f"no free part of {ref}'s inside fits it: rests on "
                         f"{', '.join(under) or 'other contents'}" + (" (soft: sunk 40% into them)" if soft else ""),
                         f"{word} {ref}, on its bottom", f"y={y:.3f}, {100 * (y - fl):.0f} cm above the bottom")
        over = y + c["hy"] - hi[1]
        if over > 0.10:
            self._repair(oid, "sticks_out_of_container", f"its top is {100 * over:.0f} cm above the rim of {ref}",
                         f"{word} {ref}", f"top at y={y + c['hy']:.3f}, rim at {hi[1]:.3f}")

    def _place_in_closed(self, oid, ref, hx, hz, hy):
        """Closed container or pockets: inside the box (shrunk to 80% across, as bags taper),
        spread over its bottom, resting on other contents only when no free part fits; left out
        when it would stick out of the top."""
        rec = self.records[oid]
        lo, hi = self.footprint(ref)
        fits = (2 * hx <= (hi[0] - lo[0]) * 0.95 and 2 * hz <= (hi[2] - lo[2]) * 0.95 and hy <= (hi[1] - lo[1]) * 0.9) or \
               (2 * hz <= (hi[0] - lo[0]) * 0.95 and 2 * hx <= (hi[2] - lo[2]) * 0.95 and hy <= (hi[1] - lo[1]) * 0.9)
        if not fits:
            return super()._place_inside_object(oid, ref, hx, hz, hy)
        cell = MAP_CELL
        x0, z0 = lo[0] - cell, lo[2] - cell
        nx, nz = int((hi[0] - lo[0]) / cell) + 3, int((hi[2] - lo[2]) / cell) + 3
        ii, jj = np.mgrid[0:nz, 0:nx]
        xs, zs = x0 + (jj + 0.5) * cell, z0 + (ii + 0.5) * cell
        inner = (np.abs(xs - (lo[0] + hi[0]) / 2) <= 0.4 * (hi[0] - lo[0]) + cell) & \
                (np.abs(zs - (lo[2] + hi[2]) / 2) <= 0.4 * (hi[2] - lo[2]) + cell)
        contents = self._contents_of(ref)
        used, tops = self._box_mask(contents, x0, z0, inner.shape)
        H = np.maximum(np.where(inner, lo[1] + 0.01, -np.inf), tops)
        ci, cj = np.nonzero(inner)
        c = self._choose(oid, ci, cj, x0, z0, H, free=inner & ~used, prefer=(ci.mean(), cj.mean()))
        y = c["y"] if c["y"] is not None else lo[1] + 0.01
        if y + c["hy"] > hi[1] + 0.02:
            self.park(oid)
            rec.update(placed=False, why=f"no room left inside its closed container {ref} "
                                         f"(it would stick {100 * (y + c['hy'] - hi[1]):.0f} cm out of the top)")
            return
        self.set_at(oid, c["x"], y, c["z"])
        rec["_in"] = ref
        stacked = y > lo[1] + 0.03
        rec.update(placed=True, how=f"inside closed container {ref}" + (" (on its other contents)" if stacked else ""),
                   x=c["x"], y=y, z=c["z"])
        if stacked:
            self._repair(oid, "stacked_in_container", f"no free part of closed {ref}'s bottom fits it: rests on "
                         "its other contents", f"inside {ref}, on its bottom", f"y={y:.3f}")

    # ------------------------------------------------------------------ surfaces
    def _underside(self, oid, cell=scene.CELL):
        """The thing's underside at its current turn, seen from below with nothing around:
        per cell (relative to the box centre) the height of its lowest point above its box
        bottom (NaN where it has nothing). A vacuum cleaner's hose arches high; its wheels
        are at 0."""
        import magnum as mn
        thing = self.things[oid]
        thing.translation = mn.Vector3(0, 0, 0)
        lo, hi = common.box_of(thing)
        far = (0.0, -45.0, 0.0)
        thing.translation = mn.Vector3(far[0] - (lo[0] + hi[0]) / 2, far[1] - lo[1], far[2] - (lo[2] + hi[2]) / 2)
        reach = max(hi[0] - lo[0], hi[2] - lo[2]) / 2 + 0.1
        eye = np.array([far[0], far[1] - reach, far[2]])
        common.look_from(self.sim, eye, eye + np.array([0.0, 1.0, 0.0001]))
        seen = self.shoot("down_depth", "down_ids")
        depth, ids = seen["down_depth"], seen["down_ids"]
        f = (scene.DOWN / 2) / math.tan(math.radians(45))
        cols, rows = np.meshgrid(np.arange(scene.DOWN) - scene.DOWN / 2 + 0.5, np.arange(scene.DOWN) - scene.DOWN / 2 + 0.5)
        import quaternion  # noqa: F401
        turn = quaternion.as_rotation_matrix(self.sim.get_agent(0).get_state().rotation)
        rays = np.stack([cols / f, -rows / f, -np.ones_like(cols)], axis=-1)
        world = eye + (rays * depth[..., None]) @ turn.T
        ok = (depth > 0) & (ids == self.facts[oid]["sid"])
        nx = 2 * int(math.ceil((hi[0] - lo[0]) / 2 / cell)) + 1
        nz = 2 * int(math.ceil((hi[2] - lo[2]) / 2 / cell)) + 1
        U = np.full((nz, nx), np.inf)
        gi = np.floor((world[..., 2][ok] - far[2]) / cell + nz / 2).astype(int)
        gj = np.floor((world[..., 0][ok] - far[0]) / cell + nx / 2).astype(int)
        inside = (gi >= 0) & (gi < nz) & (gj >= 0) & (gj < nx)
        np.minimum.at(U, (gi[inside], gj[inside]), world[..., 1][ok][inside] - far[1])
        thing.translation = mn.Vector3(0, -30, 0)
        U[~np.isfinite(U)] = np.nan
        return np.maximum(U, 0.0)

    def _free_spot(self, grid, oid, hx, hz, near, need=0.6):
        """scene.Home._free_spot, except when no spot keeps the whole footprint on free cells
        (or, for next_to, none within 15 cm of the reference does). The committed code then
        took a steady random spot with at least 60% free (or the least used one), and the
        thing rested on whatever its box overlapped (a tray on a honey jar, 12 cm up; the
        vacuum cleaner, whose hose makes its box 1.1 x 1.2 m, on the laundry basket).
        Here, on open surfaces it also tries the thing turned by 30-150 degrees, and for each
        spot works out where it would really rest: its underside (seen from below) against
        the surface and the boxes of the things already there, so a hose may pass over a
        basket. It picks: a spot where it rests within 3 cm of the surface first, then (for
        next_to) one within 15 cm of the reference; then the whole box on free cells; then at least 70% of the parts it stands on (its underside
        within 5 cm of its bottom) over the surface (else as much as there is); then the
        lowest resting height (1 cm steps); then the most of it over the surface (10% steps);
        then the gap nearest 4 cm (next_to).
        A spot not wholly on free cells counts as not fitting (did_not_fit), recorded as a
        repair; its resting height is kept in the record (_rest_y) for place_one.
        In an open place (a sink, the bathtub) the scanned bottom is only the flat part, often
        narrower than a plate; there the lower walls (up to 12 cm above the bottom) count as
        bottom too, so a plate lies on the bottom with its rim in the wall's curve instead
        of resting on the counter's edge 17 cm up."""
        if not grid.valid.any():
            return None
        place = next((p for p, g in self.grids.items() if g is grid), None)
        is_open = place is not None and self.snap["places"][place]["kind"] == "open"
        valid = grid.valid
        if is_open:
            low_wall = np.isfinite(grid.heights) & (grid.heights >= grid.y - 0.03) & (grid.heights < grid.y + 0.12)
            valid = ndimage.binary_fill_holes(grid.valid | low_wall)
        free = (valid & ~grid.used).astype(float)
        size0 = (2 * max(1, int(hz / scene.CELL)) + 1, 2 * max(1, int(hx / scene.CELL)) + 1)
        share0 = ndimage.uniform_filter(free, size=size0, mode="constant")
        ok0 = (share0 >= need) & valid & ~grid.used
        if near is None and not is_open and (ok0 & (share0 >= 0.999)).any():
            return super()._free_spot(grid, oid, hx, hz, near, need)
        # what a thing set down here meets: the surface, things already on it (their boxes),
        # and anything drawn above the surface (a tap, a back rest)
        S = np.where(valid, grid.y, -1e3)
        block = ~valid & np.isfinite(grid.heights) & (grid.heights > grid.y + 0.03)
        S = np.where(block, grid.heights, S)
        for o2, r2 in self.records.items():
            if place is None or o2 == oid or not r2.get("placed") or self.snap["objects"][o2]["place"] != place \
                    or o2 not in self.things:
                continue
            lo, hi = self.footprint(o2)
            i0, j0, i1, j1 = grid.rect_cells((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, (hi[0] - lo[0]) / 2, (hi[2] - lo[2]) / 2)
            S[i0:i1, j0:j1] = np.maximum(S[i0:i1, j0:j1], hi[1])
        nzs, nxs = S.shape
        turnable = place is not None and self.snap["places"][place]["kind"] != "closed"
        soft = is_soft(self.snap["objects"][oid]["type"])
        best = None
        for k in range(6 if turnable else 1):
            if k:
                hx, hz, _ = self._turn_extra(oid, math.radians(30))
            U = self._underside(oid)
            size = (2 * max(1, int(hz / scene.CELL)) + 1, 2 * max(1, int(hx / scene.CELL)) + 1)
            share = ndimage.uniform_filter(free, size=size, mode="constant")
            ok = (share >= need) & valid & ~grid.used
            cand = ok if ok.any() else valid
            # resting height at every centre cell: max over the underside of (support - underside)
            Y = np.full(S.shape, -1e3)
            onv = np.zeros(S.shape)
            uz, ux = U.shape
            pi, pj = np.nonzero(np.isfinite(U))
            stand = U[pi, pj] <= 0.05
            Sp = np.pad(S, ((uz, uz), (ux, ux)), constant_values=-1e3)
            Vp = np.pad(valid.astype(float), ((uz, uz), (ux, ux)))
            for di, dj, u, st in zip(pi - uz // 2, pj - ux // 2, U[pi, pj], stand):
                win = (slice(uz + di, uz + di + nzs), slice(ux + dj, ux + dj + nxs))
                np.maximum(Y, Sp[win] - u, out=Y)
                if st:
                    onv += Vp[win]
            onv /= max(int(stand.sum()), 1)
            ii, jj = np.nonzero(cand)
            xs, zs = grid.x0 + (jj + 0.5) * scene.CELL, grid.z0 + (ii + 0.5) * scene.CELL
            yrest = np.maximum(Y[ii, jj], grid.y)
            lift = yrest - grid.y
            on_surface = onv[ii, jj]
            far = np.zeros(len(ii))
            near_score = np.zeros(len(ii))
            if near is not None:
                lo, hi = near
                gapx = np.maximum(0, np.maximum(lo[0] - (xs + hx), (xs - hx) - hi[0]))
                gapz = np.maximum(0, np.maximum(lo[2] - (zs + hz), (zs - hz) - hi[2]))
                gap = np.maximum(gapx, gapz)
                inside = (gapx == 0) & (gapz == 0)
                far = np.where(inside, 2, (gap > 0.15).astype(float))
                near_score = np.abs(gap - 0.04)
            rnd = np.array([scene.steady("spot2", oid, k, n) for n in range(len(ii))]) * 0.001
            whole = share[ii, jj] >= 0.999
            # a hard thing must stand 70% on the surface or it tips; cloth may hang over an
            # edge (a towel over the sink's rim) down to 30%
            tip = np.where(on_surface < (0.3 if soft else 0.7), np.round(20 * (1 - on_surface)), 0)
            # resting on other things (over 3 cm up) is worse than being more than 15 cm away
            first = far + 3 * (lift > 0.03)
            cols = (near_score + rnd - 0.01 * share[ii, jj], np.round(10 * (1 - on_surface)),
                    np.round(lift / 0.01), tip, ~whole, first)
            n = int(np.lexsort(cols)[0])
            score = tuple(float(c[n]) for c in cols[::-1]) + (k,)
            if best is None or score < best[0]:
                best = (score, k, float(xs[n]), float(zs[n]), hx, hz, float(share[ii[n], jj[n]]), bool(whole[n]),
                        float(yrest[n]), float(on_surface[n]))
        _, k, x, z, hx, hz, sh, whole, yrest, on_surface = best
        if turnable:
            self._turn_extra(oid, math.radians(30 * k - 150))     # back to the chosen turn
        if k:
            self.records[oid]["turned_to_fit_deg"] = 30 * k
        i0, j0, i1, j1 = grid.rect_cells(x, z, hx + scene.CELL, hz + scene.CELL)
        grid.used[i0:i1, j0:j1] = True
        self._crowded = not whole
        if not whole or is_open:
            self.records[oid]["_rest_y"] = yrest
            self.records[oid]["share_standing_on_surface"] = round(on_surface, 2)
        return x, z, sh

    # ------------------------------------------------------------------ open places, repairs
    def place_one(self, oid, under_of):
        super().place_one(oid, under_of)
        objs = self.snap["objects"]
        o, rec = objs[oid], self.records[oid]
        if not rec.get("placed"):
            rec.pop("_rest_y", None)
            return
        rel, ref, kind, place = o["relation"], o["reference"], o["reference_kind"], o["place"]
        surface_how = ("on a free cell of the surface", "next to its reference",
                       "on the place (next_to names the place itself)")
        if rec.get("_rest_y") is not None and rec.get("how") in surface_how:
            # crowded: rest where its underside meets what is there (worked out in _free_spot),
            # not on the highest point under its box as scene.place_one did
            y = rec.pop("_rest_y")
            self.set_at(oid, rec["x"], y, rec["z"])
            rec["y"] = y
        elif rec.get("turned_to_fit_deg") and place in self.grids and rec.get("how") in surface_how:
            # scene.place_one measured the resting height over the footprint before the turn
            grid = self.grids[place]
            hx, hz, _ = self._size(oid)
            self.park(oid)            # so the down camera does not see the thing itself
            y = self.rest_height(rec["x"], rec["z"], hx, hz, grid.y + 0.25 if grid.y > 0.05 else 1.0, place=place)
            y = grid.y if y is None or y < grid.y - 0.03 or y > grid.y + 0.5 else y
            self.set_at(oid, rec["x"], y, rec["z"])
            rec["y"] = y
        if rec.get("how") == "dropped into open place at its centre":
            self._spread_in_open_place(oid, place)
        ref_drawn = kind != "object" or self.records.get(ref, {}).get("placed")
        if rel == "next_to" and kind == "place":
            self._repair(oid, "next_to_a_place", "next_to names a place, not a thing: put on that place",
                         f"next to {ref}", f"on {place}")
        elif kind == "object" and rel in ("next_to", "on_top") and not ref_drawn:
            why = self.records.get(ref, {}).get("why", "not drawn")
            self._repair(oid, "reference_not_drawn", f"{rel.replace('_', ' ')} {ref}, which is not drawn ({why}): "
                         "put on a free part of the place", f"{rel.replace('_', ' ')} {ref}", f"on {place}")
        elif rel == "next_to" and kind == "object" and "next to its reference" in rec.get("how", ""):
            lo, hi = self.footprint(oid)
            rlo, rhi = self.footprint(ref)
            gap = max(0.0, rlo[0] - hi[0], lo[0] - rhi[0], rlo[2] - hi[2], lo[2] - rhi[2])
            if gap > 0.15:
                self._repair(oid, "far_from_reference", f"no free cell within 15 cm of {ref}: the nearest "
                             f"free one is {100 * gap:.0f} cm away", f"next to {ref}", f"{100 * gap:.0f} cm from it")
        if rec.get("did_not_fit") and not any(r["kind"] in ("on_neighbours", "stacked_in_container",
                                                            "wider_than_container", "open_place_crowded")
                                              for r in rec.get("repairs", [])):
            over = self._overlapping(oid)
            share = rec.get("share_of_footprint_on_free_cells")
            self._repair(oid, "overlap" if over else "overhang",
                         f"no free room on {place}: placed " + ("overlapping its neighbours" if over else
                                                               "hanging over the edge or over blocked cells") +
                         ", resting on what is under it",
                         f"a free part of {place}",
                         (f"{share:.0%} of its footprint on free cells; " if share is not None else "") +
                         (f"overlaps {', '.join(over)}" if over else "overlaps no placed thing (hangs over the edge)"))

    def _overlapping(self, oid):
        objs = self.snap["objects"]
        lo, hi = self.footprint(oid)
        out = []
        for o2, r2 in self.records.items():
            if o2 == oid or not r2.get("placed") or objs[o2]["place"] != objs[oid]["place"] or o2 not in self.things:
                continue
            l2, h2 = self.footprint(o2)
            ox = min(hi[0], h2[0]) - max(lo[0], l2[0])
            oz = min(hi[2], h2[2]) - max(lo[2], l2[2])
            if ox > 0 and oz > 0:
                a = min((hi[0] - lo[0]) * (hi[2] - lo[2]), (h2[0] - l2[0]) * (h2[2] - l2[2]))
                if ox * oz > 0.2 * a:
                    out.append(o2)
        return sorted(out)

    def _spread_in_open_place(self, oid, place):
        rec = self.records[oid]
        grid = self.grid_for(place)
        if grid is None or not grid.valid.any():
            self._repair(oid, "open_place_bottom_not_found", f"the bottom of {place} was not found: dropped "
                         "at its centre (old rule)", f"inside {place}", f"y={rec['y']:.3f}")
            return
        hx, hz, _ = self._size(oid)
        self.park(oid)            # it was dropped at the centre: out of the way of the cameras
        spot = self._free_spot(grid, oid, hx, hz, None, need=0.9)
        if spot is None:
            self.set_at(oid, rec["x"], rec["y"], rec["z"])
            return
        x, z, share = spot
        hx, hz, _ = self._size(oid)
        self.park(oid)
        if rec.get("_rest_y") is not None:
            y = rec.pop("_rest_y")
        else:
            y = self.rest_height(x, z, hx, hz, grid.y + 0.3, place=place)
            y = grid.y if y is None or y < grid.y - 0.03 or y > grid.y + 0.5 else y
        self.set_at(oid, x, y, z)
        rec.pop("_sib", None)
        rec.update(how="in the open place, on a free part of its bottom", x=x, y=y, z=z,
                   share_of_footprint_on_free_cells=round(share, 2), did_not_fit=self._crowded)
        if self._crowded:
            over = self._overlapping(oid)
            self._repair(oid, "open_place_crowded", f"no free part of {place}'s bottom fits it: overlaps or "
                         "rests on " + (", ".join(over) or "its edge"), f"inside {place}", f"y={y:.3f}")


HOME_CLASS = SnapshotHome     # lib_v2 sets SnapshotHomeV2


def open_home(snap_file: pathlib.Path, cameras=(), home_class=None):
    common.SNAPSHOT = pathlib.Path(snap_file)
    return (home_class or HOME_CLASS)(extra_cameras=list(cameras))


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
