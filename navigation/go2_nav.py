"""Path planning on the lab map, for go_to.

Plans on a 10 cm grid built from the mapper's 5 cm cells: walls and furniture (and anything not
mapped yet) are blocked, grown by the dog's half width, and cells near obstacles cost more, so routes
keep to the middle of aisles. A* finds the route; it is then cut down to a few straight legs.

Obstacles the dog runs into that are not on the map (a chair moved, a person) can be added for a
while with block(), so the next plan goes around them.

Near the dog, what the lidar sees now overrides the saved map (set_live): open floor clears mapped
obstacles; obstacles it sees count if they are on the saved map too, or close to the dog. The dog's
lidar cloud is its own accumulated voxel map (not one scan), which smears when the odometry slips,
so far-off "new" obstacles are left to the dog's obstacle avoidance and re-planning. (For the same
reason no ray clearing: points in it may have been seen from somewhere else.)
The dog's own footprint is always clear: it is standing there.
"""
import heapq
import json
import math
import threading
import time

import cv2
import numpy as np

CELL = 0.10                # m per planning cell
ROBOT_R = 0.28             # m: no part of the route closer than this to an obstacle (the Go2 is ~0.31 m wide)
ROBOT_R_TIGHT = 0.20       # fall back to this if nothing fits with ROBOT_R
ROBOT_R_SQUEEZE = 0.12     # last resort, only further than SQUEEZE_NEAR_M from the dog: the saved map often shows
                           # aisles narrower than they are (lidar smear at their edges); go_to drives up to the
                           # narrow part and re-plans once the live lidar can see it (10-23: door_outside corridor)
SQUEEZE_NEAR_M = 1.5       # within this of the dog a squeeze route still needs ROBOT_R_TIGHT (the live view is good here)
CLEAR_PREF = 0.60          # m: prefer staying at least this far from obstacles
NEAR_COST = 6.0            # extra cost per cell at ROBOT_R, falling to 0 at CLEAR_PREF
GOAL_SNAP_M = 1.2          # a goal on an obstacle moves to the nearest reachable cell within this
ESCAPE_M = 0.8             # a start the map shows as blocked steps out to open floor within this
LEG_MAX_M = 2.5            # longest straight leg after shortcutting
BLOCK_S = 120.0            # temporary obstacles last this long
FOOTPRINT_R = 0.35         # m around the dog that is always open floor (it is standing there)
LIVE_NEW_R = 1.2           # live obstacles that aren't on the saved map count only this close to the dog
MID_BLOCKS = False         # use the map's desk/table-top layer as obstacles (see _grid)
# Under desks and tables. The live lidar marks open floor under a desk or table top ("under" cells, go2_agent
# _update_live); routes may cross them, but each 10 cm cell costs UNDER_COST extra (a 1 m stretch under a desk counts
# as 1 + 10 * UNDER_COST m), so the planner goes under a desk only when the other ways are much longer. Not a block:
# blocking desk tops closed every route to marker B on 10-23 (the aisle there runs under desk-top edges). What stands
# under a desk (legs, drawers, chair seats) is a normal live obstacle (go2_agent BUMP_H).
UNDER_COST = 3.0           # extra cost per cell under a desk top seen live (0 = off)
MID_COST = 3.0             # the same for the saved map's desk-top layer, anywhere: the live view only covers LIVE_R, and
                           # past it a map that shows a desk's underside open (chairs moved out while mapping) would
                           # otherwise invite a route under it (0 = off)
MID_FILL = 0.6             # ... only where the layer is a solid surface (>= this fraction of a 0.35 m window): thin or
                           # scattered layer cells are chair backs, people and smear, not desk or table tops
UNDER_GROW = 0.15          # the dog's half width: cells this close to an under cell count too (its body would be under)
UNDER_HARD = False         # testing only: block under cells instead (what OVERHEAD_MAX 1.0 did on 10-23)
SPECK_CELLS = 2            # obstacle specks this small (5 cm map cells, nothing touching) are lidar smear, not furniture
# Fallback tiers, tried in order only when the normal plan (tier 0, all three radii) finds nothing and there are
# live obstacles or temporary blocks (route_planning/deploy/TIERS.md). Each: (name, clearance bonus for live
# obstacles that aren't on the saved map: the route may pass this much closer to them, never through them;
# keep the temporary blocks). Overhead (desk/table-top) cells and saved-map obstacles are never relaxed.
# Skipped while the map says the dog is lost (mapper.lost_since): a wrong pose gets no extra routes.
LIVE_THIN_BONUS = 0.16     # ROBOT_R - ROBOT_R_SQUEEZE: pass unconfirmed live obstacles at squeeze distance
# Default (ablation 10-25): only ignore the temporary blocks; live obstacles keep full clearance. The thin tiers
# ("thin_live", LIVE_THIN_BONUS, True/False) fixed 5 more replays but passed ~0.07 m from a real wooden panel in 3.
FALLBACK_TIERS = [("live", 0.0, True), ("live_noblocks", 0.0, False)]
TRAIL_R = 0.20             # squeeze near the dog is allowed this close to where it walked recently (set_trail):
                           # it got in that way, so it can get out (10-24 15:28: stuck at door_outside)
SQ2 = math.sqrt(2)


class Planner:
    def __init__(self, mapper):
        self.mapper = mapper
        self.lock = threading.Lock()
        self.key = None
        self.blocks = []           # (expiry, x, y, r) temporary obstacles in map frame
        self.last = None           # last plan, for the console: {"goal", "path", "t"}
        self.live = None           # what the lidar sees now: (obs xy, free xy, robot x, y, radius, t)
        self.live_view = None      # {"new": cells it added, "cleared": map cells it cleared, "t"}
        self.last_fail = None      # why the last failed plan failed (see _why_failed)
        self.live_over = []        # overhead cells (desk/table tops) from the live lidar
        self.live_under = []       # open floor under a desk/table top, from the live lidar (a cost, see UNDER_COST)
        self.live_hard = []        # live obstacles under a top (legs, chair seats): never relaxed by the fallback tiers
        self.under_cost = None     # per planning cell extra cost from live_under / the mid layer
        self.fail_log = None       # jsonl file for failed plans, set by the agent
        self.trail = []            # recent map xy where the dog walked (set_trail), for squeezing out of a pocket
        self.tier = 0              # fallback tier the grid is built for (0 = normal)

    # ---------- grid ----------
    def _grid(self):
        """Rebuild the planning grid when the map or the temporary obstacles changed."""
        now = time.time()
        self.blocks = [b for b in self.blocks if b[0] > now]
        key = (self.mapper.version, self.mapper.saved_at, tuple(self.blocks), self.live and self.live[5], len(self.live_under))
        if key == self.key:
            return
        from go2_mapper import LAYER_OCC, OCC_SCORE, RES
        with self.mapper.lock:
            score, seen = self.mapper.score.copy(), self.mapper.seen.copy()
            # desk and table tops: never route under them. Off for now: the first map with layers (10-23) had
            # them smeared over half the room, because the dog's accumulated cloud re-counts smears every frame.
            top = (self.mapper.mid >= LAYER_OCC) if MID_BLOCKS else np.zeros_like(seen)
            mid = None
            if MID_COST > 0:     # the solid desk-top cells change only with the map: cache them
                mkey = (self.mapper.version, self.mapper.saved_at)
                if getattr(self, "_mid_key", None) != mkey:
                    m = self.mapper.mid >= LAYER_OCC
                    if MID_FILL > 0:
                        m &= cv2.blur(m.astype(np.float32), (7, 7)) >= MID_FILL
                    self._mid_cache, self._mid_key = m, mkey
                mid = self._mid_cache
        k = int(round(CELL / RES))
        rows, cols = np.nonzero(seen)
        if len(rows) == 0:
            self.occ = None
            self.key = key
            return
        r0, r1 = (rows.min() // k - 2) * k, (rows.max() // k + 3) * k
        c0, c1 = (cols.min() // k - 2) * k, (cols.max() // k + 3) * k
        r0, c0 = max(r0, 0), max(c0, 0)
        occ5 = (score[r0:r1, c0:c1] >= OCC_SCORE) | top[r0:r1, c0:c1]
        # Drop specks: one or two map cells with nothing touching them. They are stray points the dog's cloud
        # left in aisles when its heading drifted (10-23: they narrowed the way to desk_joseph and the workbench
        # below the dog's clearance). Real chair legs and people are still seen by the live lidar near the dog.
        n, lab, st, _ = cv2.connectedComponentsWithStats(occ5.astype(np.uint8), connectivity=8)
        speck = np.r_[False, st[1:, cv2.CC_STAT_AREA] <= SPECK_CELLS]
        self.specks = int(st[1:, cv2.CC_STAT_AREA][speck[1:]].sum())
        occ5 &= ~speck[lab]
        seen5 = seen[r0:r1, c0:c1]
        h, w = occ5.shape[0] // k, occ5.shape[1] // k
        occ = occ5[:h * k, :w * k].reshape(h, k, w, k).any(axis=(1, 3))
        known = seen5[:h * k, :w * k].reshape(h, k, w, k).any(axis=(1, 3))
        # single stray obstacle cells with no neighbours are lidar noise, not furniture
        nb = cv2.filter2D(occ.astype(np.uint8), -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT)
        occ &= nb > 1
        self.origin = (self.mapper.origin[0] + c0 * RES, self.mapper.origin[1] + r0 * RES)
        saved0 = occ.copy()        # saved-map obstacles, before the live view (for the fallback tiers)
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = (xx + 0.5) * CELL + self.origin[0], (yy + 0.5) * CELL + self.origin[1]
        self.live_view = None
        if self.live is not None:
            # near the dog, the current lidar view wins over the saved map
            lo, lf, rx, ry, rad, lt = self.live
            saved = occ.copy()

            def cells(pts, radius):
                if not len(pts):
                    return np.zeros(0, int), np.zeros(0, int), np.zeros(0)
                a = np.asarray(pts, dtype=np.float64).reshape(-1, 2)
                d = np.hypot(a[:, 0] - rx, a[:, 1] - ry)
                cc = np.floor((a[:, 0] - self.origin[0]) / CELL).astype(int)
                rr = np.floor((a[:, 1] - self.origin[1]) / CELL).astype(int)
                ok = (d <= radius) & (rr >= 0) & (rr < h) & (cc >= 0) & (cc < w)
                return rr[ok], cc[ok], d[ok]

            # open floor it sees now clears old obstacles
            rr, cc, _ = cells(lf, rad)
            occ[rr, cc], known[rr, cc] = False, True
            # obstacles it sees: ones the saved map has too, anywhere near; new ones only close by
            # (further out, the dog's smeared cloud makes phantom walls)
            rr, cc, d = cells(lo, rad)
            add = saved[rr, cc] | (d <= LIVE_NEW_R)
            occ[rr[add], cc[add]], known[rr[add], cc[add]] = True, True
            # desk and table tops block wherever the lidar sees them nearby (don't walk under desks)
            rr, cc, _ = cells(self.live_over, rad)
            occ[rr, cc], known[rr, cc] = True, True
            near = np.hypot(cx - rx, cy - ry) <= rad
            self.live_view = {"t": lt,
                              "new": np.c_[cx[occ & ~saved & near], cy[occ & ~saved & near]].round(2).tolist(),
                              "cleared": np.c_[cx[saved & ~occ & near], cy[saved & ~occ & near]].round(2).tolist()}
        # under desks and tables: a routing cost (or, UNDER_HARD, a block), grown by the dog's half width
        under = np.zeros((h, w), np.float32)
        if self.live is not None and self.live_under:
            rr, cc, _ = cells(self.live_under, rad)
            under[rr, cc] = UNDER_COST
        if mid is not None:
            m5 = mid[r0:r1, c0:c1]
            under = np.maximum(under, (m5[:h * k, :w * k].reshape(h, k, w, k).any(axis=(1, 3)) & ~occ) * np.float32(MID_COST))
        if UNDER_GROW > 0 and under.any():
            g = 2 * int(round(UNDER_GROW / CELL)) + 1
            under = cv2.dilate(under, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (g, g)))
        if UNDER_HARD:
            occ |= under > 0
            under[:] = 0
        self.under_cost = under if under.any() else None
        # Split the tier-0 obstacles for the fallback tiers. This never ADDS an obstacle: new_m and hard are both
        # subsets of occ. new_m = live obstacles not on the saved map (relaxable in later tiers); a cell that is an
        # obstacle here because of an overhead (desk/table-top) point in live_over is excluded from new_m, so it
        # stays hard in every tier. Overhead cells that are not obstacles (e.g. only a routing cost) stay free.
        new_m = occ & ~saved0
        if self.live is not None and len(self.live_over):
            a = np.asarray(self.live_over, dtype=np.float64).reshape(-1, 2)
            oc = np.floor((a[:, 0] - self.origin[0]) / CELL).astype(int)
            orr = np.floor((a[:, 1] - self.origin[1]) / CELL).astype(int)
            ok = (orr >= 0) & (orr < h) & (oc >= 0) & (oc < w)
            over_m = np.zeros_like(occ)
            over_m[orr[ok], oc[ok]] = True
            new_m &= ~over_m
        if self.live is not None and len(self.live_hard):
            # live obstacles under a desk/table top or chair back stay hard in every tier too
            a = np.asarray(self.live_hard, dtype=np.float64).reshape(-1, 2)
            hc = np.floor((a[:, 0] - self.origin[0]) / CELL).astype(int)
            hr = np.floor((a[:, 1] - self.origin[1]) / CELL).astype(int)
            ok = (hr >= 0) & (hr < h) & (hc >= 0) & (hc < w)
            hard_m = np.zeros_like(occ)
            hard_m[hr[ok], hc[ok]] = True
            new_m &= ~hard_m
        hard = occ & ~new_m
        blk = np.zeros_like(occ)
        for _, bx, by, br in self.blocks:
            blk |= np.hypot(cx - bx, cy - by) < br
        foot = np.zeros_like(occ)
        if self.live is not None:
            # the dog is standing here, so nothing else is
            foot = np.hypot(cx - self.live[2], cy - self.live[3]) <= FOOTPRINT_R
            known[foot] = True
        self._parts = (hard, new_m, blk, foot)
        self._saved0 = saved0
        self.known = known
        self.key = key
        self._set_tier(0)

    def _set_tier(self, t):
        """Planning grid (occ, dist) for fallback tier t (see FALLBACK_TIERS); tier 0 is the normal one."""
        hard, new_m, blk, foot = self._parts
        _, bonus, use_blocks = FALLBACK_TIERS[t]
        occ = hard | blk if use_blocks else hard.copy()
        new_m = new_m & ~foot
        if not bonus:
            occ |= new_m
        occ &= ~foot
        blocked = occ | ~self.known
        # distance (m) from each cell to the nearest blocked cell
        self.dist = cv2.distanceTransform((~blocked).astype(np.uint8), cv2.DIST_L2, 5) * CELL
        if bonus and new_m.any():
            # live obstacles not on the saved map: may be passed `bonus` closer, never entered
            dn = cv2.distanceTransform((~new_m).astype(np.uint8), cv2.DIST_L2, 5) * CELL
            self.dist = np.minimum(self.dist, np.where(new_m, 0.0, dn + bonus))
            occ = occ | new_m
        self.occ, self.tier = occ, t

    def _why_failed(self, sx, sy, gx, gy, error):
        """Diagnose a failed plan (lock held): would the saved map alone have had a route, and which
        live-lidar cells and temporary blocks were in play. Logged to fail_log for later analysis."""
        lv = self.live_view or {}
        new, cleared = lv.get("new", []), lv.get("cleared", [])
        live, blocks = self.live, list(self.blocks)
        try:
            self.live, self.blocks, self.key = None, [], None
            self._grid()
            saved_ok = any("path" in self._plan(sx, sy, gx, gy, r) for r in (ROBOT_R, ROBOT_R_TIGHT))
        finally:
            self.live, self.blocks, self.key = live, blocks, None
            self._grid()
        why = {"t": round(time.time(), 2), "start": [round(sx, 2), round(sy, 2)], "goal": [round(gx, 2), round(gy, 2)],
               "error": error, "saved_map_has_route": saved_ok,
               "cause": "live lidar or temporary blocks" if saved_ok else "saved map",
               "live_new": new[:400], "live_cleared_n": len(cleared),
               "blocks": [[round(b[1], 2), round(b[2], 2), b[3]] for b in blocks],
               "live_robot": [round(live[2], 2), round(live[3], 2)] if live else None}
        self.last_fail = why
        if self.fail_log:
            try:
                with open(self.fail_log, "a") as f:
                    f.write(json.dumps(why) + "\n")
            except OSError:
                pass
        return {k: why[k] for k in ("saved_map_has_route", "cause")} | {"live_new_cells": len(new), "blocks": len(blocks)}

    def cell(self, x, y):
        return int((y - self.origin[1]) / CELL), int((x - self.origin[0]) / CELL)

    def xy(self, r, c):
        return self.origin[0] + (c + 0.5) * CELL, self.origin[1] + (r + 0.5) * CELL

    def inside(self, r, c):
        return 0 <= r < self.dist.shape[0] and 0 <= c < self.dist.shape[1]

    # ---------- queries ----------
    def clearance(self, x, y):
        """Distance (m) from (x, y) to the nearest obstacle or unmapped area; 0 off the map."""
        with self.lock:
            self._grid()
            if self.occ is None:
                return 0.0
            r, c = self.cell(x, y)
            return float(self.dist[r, c]) if self.inside(r, c) else 0.0

    def nearest_free(self, x, y, radius=GOAL_SNAP_M, rr=ROBOT_R):
        """The reachable cell closest to (x, y) within radius, as (x, y), or None."""
        with self.lock:
            self._grid()
            return self._nearest_free(x, y, radius, rr)

    def _nearest_free(self, x, y, radius, rr):
        if self.occ is None:
            return None
        r, c = self.cell(x, y)
        n = int(radius / CELL) + 1
        best = None
        for dr in range(-n, n + 1):
            for dc in range(-n, n + 1):
                rr_, cc_ = r + dr, c + dc
                if not self.inside(rr_, cc_) or self.dist[rr_, cc_] < rr:
                    continue
                d = math.hypot(dr, dc) * CELL
                if d <= radius and (best is None or d < best[0]):
                    best = (d, rr_, cc_)
        return self.xy(best[1], best[2]) if best else None

    def stand_for(self, tx, ty, dist=0.8):
        """Where the dog should stand to look at a target point: open floor about `dist` away, facing it.
        Returns (x, y, yaw) or None."""
        with self.lock:
            self._grid()
            if self.occ is None:
                return None
            best = None
            for k in range(36):
                a = k * math.pi / 18
                for d in (dist, dist + 0.3, dist + 0.6, max(0.4, dist - 0.3)):
                    x, y = tx + d * math.cos(a), ty + d * math.sin(a)
                    r, c = self.cell(x, y)
                    if not self.inside(r, c) or self.dist[r, c] < ROBOT_R:
                        continue
                    cost = abs(d - dist) - 0.2 * min(self.dist[r, c], 1.0)
                    if best is None or cost < best[0]:
                        best = (cost, x, y)
            if best is None:
                return None
            _, x, y = best
            return x, y, math.atan2(ty - y, tx - x)

    def set_live(self, obs, free, rx, ry, radius, over=(), under=(), hard=()):
        """The lidar's current view around the robot, map-frame xy: obstacle cells (seen in recent
        clouds), open-floor cells, and overhead cells (desk/table tops) that block anywhere in radius."""
        with self.lock:
            self.live = (obs, free, rx, ry, radius, time.time())
            self.live_over = list(over)
            self.live_under = list(under)
            self.live_hard = list(hard)

    def grid_view(self, x, y, r=2.0, robot=None, as_json=False):
        """Read-only look at the planning grid around map point (x, y), r m (capped at 4): what the planner is
        working with, for people and agents diagnosing a no_route / blocked. No planning; never waits on a plan
        (returns None if the planner is busy). PNG (10 px per 10 cm cell, north up) or, as_json, the narrowest
        clearance along the last route and cell counts in the crop. robot: (x, y, yaw) of the dog, drawn if given."""
        if not self.lock.acquire(blocking=False):
            return None
        try:
            self._grid()
            if self.occ is None:
                return {"error": "no map"} if as_json else None
            r = max(0.5, min(4.0, float(r)))
            hard, new_m, blk, foot = self._parts
            saved0, known, dist = self._saved0, self.known, self.dist
            under = self.under_cost if getattr(self, "under_cost", None) is not None else np.zeros(dist.shape, np.float32)
            H, W = dist.shape
            c0, c1 = max(0, int((x - r - self.origin[0]) / CELL)), min(W, int((x + r - self.origin[0]) / CELL) + 1)
            r0, r1 = max(0, int((y - r - self.origin[1]) / CELL)), min(H, int((y + r - self.origin[1]) / CELL) + 1)
            sl = (slice(r0, r1), slice(c0, c1))
            classes = {                                 # each cell's class, first match wins (drawing order)
                "unknown": ~known, "stall_block": blk, "live_new": new_m & ~foot,
                "live_hard": hard & ~saved0 & ~foot, "saved_obstacle": saved0 & hard,
                "cleared_by_live": saved0 & ~hard & ~new_m, "under_cost": (under > 0) & ~hard & ~new_m,
            }
            last = getattr(self, "last_ok", None)
            fail = self.last if self.last and "path" not in self.last else None
            narrow = None
            if last:
                best = None
                for a, b in zip(last["path"], last["path"][1:]):
                    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 0.05))
                    for i in range(n + 1):
                        px, py = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
                        rr, cc = self.cell(px, py)
                        if self.inside(rr, cc) and (best is None or dist[rr, cc] < best[0]):
                            best = (float(dist[rr, cc]), px, py)
                if best:
                    narrow = {"clear_m": round(best[0], 2), "x": round(best[1], 2), "y": round(best[2], 2),
                              "needs_m": {"normal": ROBOT_R, "tight": ROBOT_R_TIGHT, "squeeze": ROBOT_R_SQUEEZE}}
            if as_json:
                return {"x": x, "y": y, "r": r, "cell_m": CELL, "tier": self.tier,
                        "counts": {k: int(v[sl].sum()) for k, v in classes.items()},
                        "clear_here_m": round(float(dist[self.cell(x, y)]), 2) if self.inside(*self.cell(x, y)) else None,
                        "last_route": None if not last else {"path": last["path"], "length_m": last.get("length_m"),
                                                             "tight": last.get("tight"), "squeeze": last.get("squeeze"),
                                                             "fallback": last.get("fallback"), "t": round(last["t"], 1),
                                                             "narrowest": narrow},
                        "last_failure": fail and {"t": round(fail["t"], 1), "start": [round(v, 2) for v in fail.get("start") or []], "goal": [round(v, 2) for v in fail.get("want") or []],
                                                  "error": fail.get("error"), "why": fail.get("why")}}
            colours = {"unknown": (60, 60, 60), "stall_block": (0, 140, 255), "live_new": (40, 40, 230),
                       "live_hard": (160, 40, 160), "saved_obstacle": (25, 25, 25), "cleared_by_live": (170, 235, 170),
                       "under_cost": (130, 200, 255)}
            img = np.full((r1 - r0, c1 - c0, 3), 245, np.uint8)
            for k in ("under_cost", "cleared_by_live", "saved_obstacle", "live_hard", "live_new", "stall_block", "unknown"):
                img[classes[k][sl]] = colours[k]
            S = 10
            img = cv2.resize(img[::-1], None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)

            def px(a, b):
                return int((a - self.origin[0]) / CELL - c0) * S + S // 2, int(r1 - 1 - (b - self.origin[1]) / CELL ) * S + S // 2
            if last:
                pts = [px(*q) for q in last["path"]]
                for u, v in zip(pts, pts[1:]):
                    cv2.line(img, u, v, (0, 170, 0), 2)
                if narrow:
                    cv2.circle(img, px(narrow["x"], narrow["y"]), 7, (0, 0, 255), 2)
                    cv2.putText(img, f"{narrow['clear_m']:.2f} m", px(narrow["x"] + 0.1, narrow["y"]), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 200), 1)
            if robot is not None:
                u = px(robot[0], robot[1])
                cv2.circle(img, u, 6, (200, 120, 0), -1)
                cv2.line(img, u, (u[0] + int(14 * math.cos(robot[2])), u[1] - int(14 * math.sin(robot[2]))), (200, 120, 0), 2)
            cv2.drawMarker(img, px(x, y), (0, 0, 0), cv2.MARKER_CROSS, 12, 1)
            cv2.rectangle(img, (0, 0), (min(img.shape[1] - 1, 260), 19), (255, 255, 255), -1)
            cv2.putText(img, f"({x:.2f}, {y:.2f}) r {r:.1f} m  tier {self.tier}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            ok, buf = cv2.imencode(".png", img)
            return buf.tobytes() if ok else None
        finally:
            self.lock.release()

    def overlay(self):
        """What the live lidar changed on the planning grid, for the console (never waits on a plan)."""
        if not self.lock.acquire(blocking=False):
            return self.live_view
        try:
            self._grid()
            return self.live_view
        finally:
            self.lock.release()

    def raycast(self, x, y, yaw, max_m=4.0, min_m=0.3):
        """First mapped obstacle straight ahead of (x, y) facing yaw, as (x, y), or None."""
        from go2_mapper import OCC_SCORE, RES
        m = self.mapper
        for i in range(int(min_m / RES), int(max_m / RES)):
            px, py = x + math.cos(yaw) * i * RES, y + math.sin(yaw) * i * RES
            c, r = int((px - m.origin[0]) / RES), int((py - m.origin[1]) / RES)
            if not (0 <= r < m.score.shape[0] and 0 <= c < m.score.shape[1]):
                return None
            if m.score[r, c] >= OCC_SCORE:
                return round(px, 2), round(py, 2)
        return None

    def set_trail(self, pts):
        """Where the dog walked recently (map xy), for squeezing out of a pocket the way it came in."""
        with self.lock:
            self.trail = [tuple(p) for p in pts]

    def block(self, x, y, r=0.25):
        """Treat a spot as an obstacle for a while (something the dog ran into that isn't on the map)."""
        with self.lock:
            self.blocks.append((time.time() + BLOCK_S, round(x, 2), round(y, 2), r))

    def plan(self, sx, sy, gx, gy):
        """Route from (sx, sy) to (gx, gy) in map metres. Returns {"path": [[x, y], ...], "length_m",
        "goal": [x, y] actually used} or {"error": reason}."""
        with self.lock:
            self._grid()
            if self.occ is None:
                return {"error": "no map"}
            # lost (the same flag that stops go_to): plan exactly as before, no fallback tiers and no trail
            lost = getattr(self.mapper, "lost_since", None) is not None
            n_tiers = 1 if lost or (self.live is None and not self.blocks) else len(FALLBACK_TIERS)
            first = None
            for t in range(n_tiers):
                if t:
                    self._set_tier(t)
                for rr in (ROBOT_R, ROBOT_R_TIGHT, ROBOT_R_SQUEEZE):
                    out = self._plan(sx, sy, gx, gy, rr, use_trail=not lost)
                    if "path" in out:
                        out["tight"] = rr < ROBOT_R
                        if rr == ROBOT_R_SQUEEZE:
                            self._mark_squeeze(out, sx, sy)
                        break
                first = first or out
                if "path" in out:
                    if t:
                        out["fallback"] = FALLBACK_TIERS[t][0]
                    break
            if self.tier:
                self._set_tier(0)
            if "path" not in out:
                out = first
            if "path" not in out and self.live is not None:
                out["why"] = self._why_failed(sx, sy, gx, gy, out.get("error"))
            self.last = dict(out, t=time.time(), start=[sx, sy], want=[gx, gy])
            if "path" in out:
                self.last_ok = self.last       # for grid_view: the last route that existed
            return out

    def _plan(self, sx, sy, gx, gy, rr, use_trail=True):
        g = self._nearest_free(gx, gy, GOAL_SNAP_M, rr)
        if g is None:
            return {"error": f"no open floor within {GOAL_SNAP_M} m of the goal"}
        gr, gc = self.cell(*g)
        sr, sc = self.cell(sx, sy)
        if not self.inside(sr, sc):
            return {"error": "the robot is off the map"}
        lead = []
        if self.dist[sr, sc] < min(rr, 0.12):
            # The map shows the dog's own spot as blocked (it's close to furniture, or lidar noise):
            # step straight out to the nearest open floor and plan from there. The lidar check while
            # driving still stops it if something is really in the way.
            out = self._nearest_free(sx, sy, ESCAPE_M, rr)
            if out is None:
                return {"error": f"the map shows the dog boxed in: no open floor within {ESCAPE_M} m"}
            lead = [[round(sx, 2), round(sy, 2)]]
            sx, sy = out
            sr, sc = self.cell(sx, sy)
        free = self.dist >= rr
        if rr < ROBOT_R_TIGHT:      # squeeze: only away from the dog, where the map is all we know
            yy, xx = np.mgrid[0:free.shape[0], 0:free.shape[1]]
            ok = (self.dist >= ROBOT_R_TIGHT) | (np.hypot(yy - sr, xx - sc) * CELL > SQUEEZE_NEAR_M)
            if use_trail and self.trail:      # ... or where the dog has just walked
                tr = np.zeros_like(ok)
                for tx, ty in self.trail:
                    r_, c_ = self.cell(tx, ty)
                    if self.inside(r_, c_):
                        tr[r_, c_] = True
                k = 2 * int(TRAIL_R / CELL) + 1
                ok |= cv2.dilate(tr.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))).astype(bool)
            free &= ok
        # the dog may be standing close to something: let it leave through any cell it can reach
        # within half a metre, even if that cell is tighter than rr
        start_ok = self.dist >= min(rr, 0.12)
        cost_near = NEAR_COST * np.clip((CLEAR_PREF - self.dist) / (CLEAR_PREF - rr), 0, 1)
        if self.under_cost is not None:
            cost_near = cost_near + self.under_cost
        H, W = free.shape
        INF = float("inf")
        best = np.full((H, W), INF)
        prev = -np.ones((H, W), np.int64)
        best[sr, sc] = 0.0
        heap = [(math.hypot(gr - sr, gc - sc), 0.0, sr, sc)]
        steps = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, SQ2), (-1, 1, SQ2), (1, -1, SQ2), (1, 1, SQ2)]
        found = False
        while heap:
            _, d, r, c = heapq.heappop(heap)
            if d > best[r, c]:
                continue
            if r == gr and c == gc:
                found = True
                break
            near_start = math.hypot(r - sr, c - sc) * CELL < 0.5
            for dr, dc, w in steps:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < H and 0 <= nc < W):
                    continue
                if not (free[nr, nc] or (near_start and start_ok[nr, nc])):
                    continue
                nd = d + w * (1.0 + cost_near[nr, nc])
                if nd < best[nr, nc]:
                    best[nr, nc] = nd
                    prev[nr, nc] = r * W + c
                    heapq.heappush(heap, (nd + math.hypot(gr - nr, gc - nc), nd, nr, nc))
        if not found:
            return {"error": "no route: the goal is not connected to where the robot is on the map"}
        cells = [(gr, gc)]
        while cells[-1] != (sr, sc):
            k = prev[cells[-1]]
            cells.append((int(k // W), int(k % W)))
        cells.reverse()
        legs = self._shortcut(cells, rr)
        pts = lead + [[round(sx, 2), round(sy, 2)]] + [[round(v, 2) for v in self.xy(r, c)] for r, c in legs[1:]]
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        return {"path": pts, "length_m": round(length, 2), "goal": pts[-1]}

    def _mark_squeeze(self, out, sx, sy):
        """Where a squeeze route first gets narrower than ROBOT_R_TIGHT: squeeze_at [x, y], squeeze_along_m
        (distance along the route from its start) and squeeze_clear_m (the narrowest the map shows)."""
        pts, along, first, narrowest = out["path"], 0.0, None, 9.0
        for a, b in zip(pts, pts[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            for i in range(1, max(2, int(seg / 0.05)) + 1):
                f = i / max(2, int(seg / 0.05))
                x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
                r, c = self.cell(x, y)
                cl = float(self.dist[r, c]) if self.inside(r, c) else 0.0
                if cl < ROBOT_R_TIGHT and math.hypot(x - sx, y - sy) > SQUEEZE_NEAR_M:
                    narrowest = min(narrowest, cl)
                    if first is None:
                        first = (round(x, 2), round(y, 2), round(along + seg * f, 2))
            along += seg
        out["squeeze"] = True
        if first:
            out["squeeze_at"], out["squeeze_along_m"] = [first[0], first[1]], first[2]
            out["squeeze_clear_m"] = round(narrowest, 2)

    def _line_free(self, a, b, rr, skip=0.0):
        """Straight line between cells a and b stays rr clear (ignoring its first `skip` metres)."""
        (r0, c0), (r1, c1) = a, b
        n = int(max(abs(r1 - r0), abs(c1 - c0)) * 2) + 1
        length = math.hypot(r1 - r0, c1 - c0) * CELL
        for i in range(n + 1):
            if length * i / n < skip:
                continue
            r = int(round(r0 + (r1 - r0) * i / n))
            c = int(round(c0 + (c1 - c0) * i / n))
            if self.dist[r, c] < rr:
                return False
        return True

    def _shortcut(self, cells, rr):
        """Fewest straight legs (each at most LEG_MAX_M) that stay rr clear; the first leg may pass
        tighter spots in its first half metre, where the dog may be starting close to something."""
        out = [cells[0]]
        i = 0
        max_cells = LEG_MAX_M / CELL
        while i < len(cells) - 1:
            j = len(cells) - 1
            while j > i + 1:
                a, b = cells[i], cells[j]
                if (math.hypot(b[0] - a[0], b[1] - a[1]) <= max_cells
                        and self._line_free(a, b, rr, skip=0.5 if i == 0 else 0.0)):
                    break
                j -= 1
            out.append(cells[j])
            i = j
        return out
