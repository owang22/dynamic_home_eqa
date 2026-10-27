"""Lab map built straight from the dog's lidar clouds, which arrive already placed in the dog's own
world frame (odom). The dog's onboard estimate is clean, so no scan matching while mapping.

The odom frame restarts whenever the dog reboots, so each session needs one transform from odom to
the saved map. `align()` finds it by matching what the lidar sees now against the saved map
(rotation by brute force, translation by FFT correlation). Places and map_pose are in map frame.
"""
import json
import math
import os
import shutil
import threading
import time
from collections import deque

import cv2
import numpy as np

RES = 0.05                 # m per cell
SIZE = 1000                # cells per side: a 50 m square, centred on where mapping started
MIN_H, MAX_H = 0.20, 0.60  # obstacle heights above the floor that go on the map: what the dog can bump into (m).
                           # The lidar's voxels are ~10 cm tall, so floor points scatter up to ~15 cm.
# Higher layers, recorded while mapping (Oliver, 10-23): desk and table tops (route planning: the dog must not
# go under them), high fixed structure (shelves, cabinet tops, door frames) and the ceiling's height profile
# (lights, ducts, beams). These don't move when chairs do, so they're also what line-up should lean on.
MID_H = (0.60, 1.20)       # desk/table tops
HIGH_H = (1.20, 2.20)      # shelves, cabinet tops, door frames
CEIL_MIN_H = 2.20          # anything above this is ceiling or hangs from it
LAYER_OCC = 2              # a cell is in a layer after this many lidar views with points in its band
SCORE_CAP = 5              # each cell's score: +1 per obstacle sighting, -1 per clear sighting, kept within ±5,
OCC_SCORE = 2              # so a few clear looks erase a stale obstacle; occupied at a score of 2 or more
SAME_SESSION_M, SAME_SESSION_RAD = 1.0, 0.5   # dog this close to where it was: same odom frame, keep the alignment
ALIGN_OK = 0.5             # (points on saved walls - points on saved open floor) / points, at the best fit
ALIGN_MARGIN = 0.15        # best fit must beat the best clearly different rotation by this much
ALIGN_RETRY_S = 20.0       # wait this long before trying again after a failed line-up
ALIGN_MAX_PTS = 2500
HINT_R = 0.75              # "the dog is about here" (clicked on the map): search within this of the click (m)
HINT_YAW_TOL = math.radians(45)   # and, when a heading was dragged too, within this of it
TRACK_RANGE_M, TRACK_STEP_CELLS = 0.20, 1    # drift correction: search ±20 cm in 5 cm steps
TRACK_DEG, TRACK_DEG_STEP = 2.0, 0.5          # and ±2 degrees in half-degree steps, around the robot
# After a turn in place the heading is often several degrees off (views are skipped while turning, and the gyro's
# scale error adds up), and ±2 deg per view at TRACK_GAIN catches up slowly. So for the first POST_TURN_VIEWS views
# after the odom heading changed by more than POST_TURN_DEG, search ±TRACK_DEG_WIDE (stops early once a
# correction is under 1 deg).
POST_TURN_DEG, POST_TURN_VIEWS, TRACK_DEG_WIDE = 45.0, 3, 5.0
TRACK_SIGMA = 0.08         # m: how sharply a lidar point must sit on a mapped wall to count
TRACK_MIN_PTS = 80         # need this many obstacle points in a view to correct from it
TRACK_MIN_FIT = 0.35       # mean wall likelihood at the best fit
TRACK_MIN_GAIN = 0.03      # best fit must beat "no correction" by this much
TRACK_GAIN = 0.6           # apply this fraction of each correction (smooths noise)
TRACK_MAX_PTS = 700
# While the dog stands still (odom within STILL_M of where it stopped), the tracker may keep turning (it cancels the
# gyro drift: 20 deg in 7 min at B on 10-26) but its translation is limited: few points can walk the pose along a
# smeared wall (10-26 16:53: 0.36 m of map motion from views of 91-131 cells while odom moved 0.06 m).
STILL_MODE = "both"        # "off", "pts" (translate only with >= STILL_MIN_PTS cells), "cap" (at most STILL_CAP_M of
                           # translation in total per still period), "both"
STILL_M = 0.10             # m of odom motion that ends a still period
STILL_MIN_PTS = 200        # cells in the view needed to translate while still
STILL_CAP_M = 0.10         # m of translation allowed per still period
# Marker re-anchor (marker_fix): a surveyed ArUco marker seen well gives the dog's map position from the camera's
# range and bearing, with the map heading kept (a marker's own yaw is too noisy for heading: MAD ~9 deg, 10-26).
# Only fix_ok, unambiguous, near and head-on sightings count; several must agree; the shift is capped; and the lidar
# must not clearly prefer the current pose (oblique sightings at 2.5 m read 0.4 m long on 10-26 while the lidar fit
# the current pose). A refused fix raises suspect instead of moving the dog.
MK_CAM_AHEAD = 0.30        # m, camera ahead of base_link (the survey's convention)
MK_MAX_VIEW = 45.0         # deg between the marker's normal and the line of sight (IPPE; reads ~10 deg high at 2.5 m)
MK_MAX_DIST = 2.5          # m
MK_MAX_AMBIG = 0.5         # IPPE best/second reprojection error ratio
MK_YAW_SANITY = 35.0       # deg: heading implied by the marker's yaw must be within this of the map heading
MK_WINDOW_S = 3.0          # sightings within this window are pooled
MK_MIN_N = 3               # ...need this many
MK_MAX_SPREAD = 0.10       # m: and they must agree to within this (median distance from their median)
MK_MIN_SHIFT = 0.15        # m: smaller disagreements are left to the lidar tracker
MK_MAX_SHIFT = 1.0         # m: larger ones are refused (a mis-surveyed or moved marker; or the wrong one)
MK_LIDAR_MARGIN = 0.05     # the recent views' wall fit at the marker pose may be at most this much worse
MK_COOLDOWN_S = 5.0
MK_SUSPECT_M = 0.30        # a disagreement this large also raises suspect (smaller ones are only logged)
MK_MOVE = False            # logging only: a fix that passes every gate is logged as "would_move" (loc event + suspect)
                           # and the dog is NOT moved. True = re-anchor (not yet: 10-26 B-stand case, map off at B's door)
MK_GATE = "joint"          # lidar check: "all" (recent views, every voxel), "fresh" (voxels placed in the last
                           # TRACK_FRESH_S; abstains below MK_FRESH_MIN cells: a standing dog's old voxels agree with
                           # whatever pose placed them), "joint" (as fresh, and the heading is chosen along the
                           # marker's range-bearing curve where the fresh voxels fit best, +-MK_JOINT_DEG)
MK_FRESH_MIN = 40          # fresh wall cells needed for the lidar to vote
MK_JOINT_DEG = 10.0
# The dog's /point_cloud2 is its own persistent voxel map: a view is mostly voxels placed tens of seconds to
# minutes ago, each with the (drifting) heading the dog had then. The drift tracker therefore matches only
# voxels that first appeared within TRACK_FRESH_S (replay of the 10-23 drive: holds 0.07 m median at
# +6 deg/min extra gyro drift where all voxels end 1.9 m off). Falls back to all voxels when fewer than
# TRACK_FRESH_MIN fresh obstacle points. TRACK_FRESH_S = 0 turns it off.
TRACK_FRESH_S = 20.0
TRACK_FRESH_MIN = 200
VOXEL_KEEP_S = 120.0       # forget a voxel's birth time after it has been out of view this long
MISMATCH_KNOWN = 0.6       # a view whose points mostly fall on mapped area (this fraction)...
MISMATCH_FIT = 0.25        # ...but sit this poorly on its walls even after correcting is off: don't map it
LOST_FIT = 0.65            # "lost": the drift tracker's fit stays under this...
LOST_S = 10.0              # ...for this long...
LOST_MOVE_M = 0.3          # ...while the dog walks at least this far (odom); cleared at LOST_CLEAR or a new placement
LOST_CLEAR = 0.70
LOST_GAP_S = 5.0           # a gap this long between judged views (e.g. the dog stood) restarts the low-fit episode
# "Suspect" (advisory; doesn't stop go_to): the voxels the dog placed in the last SUSPECT_FRESH_S sit poorly on the
# map at the current T, before any correction. Replay of bad starts on the 10-23 drive: 11/11 caught within 11 s
# (current lost rule 4/11, 32 s median); but on 10-24 (room changed since mapping) a well-placed dog sat at
# 0.63-0.72, so it can't tell a wrong pose from a changed room: take a marker fix or a relocalize search.
SUSPECT_FRESH_S = 10.0
SUSPECT_FIT, SUSPECT_CLEAR = 0.65, 0.70
SUSPECT_S, SUSPECT_MOVE_M = 10.0, 0.3
CAND_SEP_M, CAND_SEP_DEG = 0.5, 20.0   # relocalize search: candidates must differ by this much
HOST_UID = 1000


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Mapper:
    def __init__(self, maps_dir, name):
        self.dir, self.name = maps_dir, name
        self.lock = threading.Lock()
        self.score = np.zeros((SIZE, SIZE), np.int8)
        self.seen = np.zeros((SIZE, SIZE), bool)
        self.mid = np.zeros((SIZE, SIZE), np.uint8)      # views with a desk/table-top point in the cell (capped)
        self.high = np.zeros((SIZE, SIZE), np.uint8)     # views with a high-structure point
        self.ceil = np.full((SIZE, SIZE), np.nan, np.float32)   # smoothed lowest point above CEIL_MIN_H (m above floor)
        self.origin = (-SIZE * RES / 2, -SIZE * RES / 2)   # map-frame xy of cell (0, 0)
        self.T = None              # (tx, ty, th): map = R(th) * odom + t; None until aligned
        self.mapping = False
        self.status = "no map"
        self.align_info = None
        self.recent = []           # recent obstacle clouds in odom frame, for aligning
        self.version = 0
        self.saved_at = None
        self._aligning = False
        self._last_try = 0.0
        self.resume_mapping = False
        self.pending = None        # (T, odom) stored with the map, reused if the dog hasn't rebooted
        self.field = None          # (likelihood image, row0, col0, key) for drift correction
        self.track_info = None
        self.tracking = True       # correct drift by matching each lidar view to the map
        self.skipped = 0           # lidar views left off the map because they didn't match it
        # every change of T, so agents and offline analysis can tell placements, line-ups, drift
        # corrections and jumps apart: see _note_T (called from pose() on each console tick)
        self.events = deque(maxlen=50)      # all but small drift corrections
        self.track_log = deque(maxlen=50)   # every drift-correction attempt, applied or not
        self.event_seq = 0
        self._ev_T = None
        self._next = ("unknown", {})        # (kind, extra) set where T is changed
        self._low = None                    # [since, last robot xy, metres walked] while the track fit is low
        self.lost_since = None              # time the dog was judged lost (see LOST_*), else None
        self._vox = (np.empty(0, np.int64), np.empty(0), np.empty(0))   # sorted voxel keys, birth, last seen
        self._odom_yaw = self._track_yaw = None   # latest odom heading (pose()), heading at the last track()
        self._wide = 0                            # views left with the wide heading search
        self._judged_at = None              # last time _judge_lost ran (see LOST_GAP_S)
        self._sus_obs = None                # obstacle points placed within SUSPECT_FRESH_S (from _fresh)
        self.fresh_fit = None               # their fit at the current T
        self._sus_low, self._sus_at = None, None
        self.suspect_since = None           # time the dog was judged suspect (see SUSPECT_*), else None
        if self.load_unsaved():
            self.status = "restored the unsaved map from before the console restarted; lining up with it"
        elif self.load():
            self.status = "saved map loaded; lining up with it"
            self.load_session()
        else:
            self.status = "no saved map: press Start mapping"

    # ---------- frames ----------
    def to_map(self, x, y, yaw=0.0):
        tx, ty, th = self.T
        c, s = math.cos(th), math.sin(th)
        return tx + c * x - s * y, ty + s * x + c * y, wrap(yaw + th)

    def _set_T(self, T, kind, **extra):
        self._next = (kind, extra)
        if kind != "drift_correction":
            self._still_ref, self._still_acc = None, np.zeros(2)
        self.T = T
        if kind != "drift_correction":     # a new placement or line-up: judge lost afresh
            self._low, self.lost_since = None, None
            self._sus_low, self.suspect_since = None, None

    def _note_T(self, odom):
        """Record a change of T as an event: where the dog was on the map before and after."""
        T, old = self.T, self._ev_T
        if T == old:
            return
        self._ev_T = T
        kind, extra = self._next
        self._next = ("unknown", {})
        x, y, yaw = odom["pos"][0], odom["pos"][1], odom["yaw"]

        def at(t):
            if t is None:
                return None
            c, s = math.cos(t[2]), math.sin(t[2])
            return {"x": round(t[0] + c * x - s * y, 3), "y": round(t[1] + s * x + c * y, 3),
                    "yaw": round(wrap(yaw + t[2]), 3)}
        a, b = at(old), at(T)
        moved = math.hypot(b["x"] - a["x"], b["y"] - a["y"]) if a and b else None
        turned = abs(math.degrees(wrap(b["yaw"] - a["yaw"]))) if a and b else None
        big = a is None or b is None or moved > 0.3 or turned > 10
        al = self.align_info or {}
        ev = {"t": round(time.time(), 2), "kind": kind, "from": a, "to": b,
              "moved_m": None if moved is None else round(moved, 3),
              "turned_deg": None if turned is None else round(turned, 1), "jump": bool(a and b and big),
              "fit": al.get("score"), "runner_up": al.get("runner_up"), "status": self.status, **extra}
        if kind == "drift_correction":
            ev.update(fit=extra.get("fit"), runner_up=None)
            if not big:
                return            # small corrections are in track_log only
        self.event_seq += 1
        ev["seq"] = self.event_seq
        self.events.append(ev)

    def loc_info(self, track_n=10):
        al = self.align_info or {}
        sc, ru = al.get("score"), al.get("runner_up")
        return {"status": self.status, "seq": self.event_seq, "events": list(self.events),
                "track": list(self.track_log)[-track_n:], "fit": sc, "runner_up": ru,
                "unsure": sc is not None and (sc < 0.3 or sc - (ru or 0) < 0.05),
                "lost": self.lost_since is not None, "lost_since": self.lost_since,
                "track_fit": (self.track_info or {}).get("fit"),
                "fresh_fit": None if self.fresh_fit is None else round(self.fresh_fit, 3),
                "suspect": self.suspect_since is not None, "suspect_since": self.suspect_since,
                "marker": list(getattr(self, "marker_log", []))[-5:]}

    def pose(self, odom):
        if odom is not None:
            self._odom_yaw = odom["yaw"]
            self._note_T(odom)
        if self.T is None or odom is None:
            return None
        x, y, yaw = self.to_map(odom["pos"][0], odom["pos"][1], odom["yaw"])
        return {"x": round(x, 3), "y": round(y, 3), "yaw": round(yaw, 3)}

    def cells(self, xy):
        """map-frame points (N,2) -> unique in-bounds cell indices (rows, cols), row 0 at the bottom."""
        ij = np.floor((xy - np.array(self.origin)) / RES).astype(np.int64)
        ok = (ij[:, 0] >= 0) & (ij[:, 0] < SIZE) & (ij[:, 1] >= 0) & (ij[:, 1] < SIZE)
        ij = np.unique(ij[ok], axis=0)
        return ij[:, 1], ij[:, 0]

    # ---------- updates from the lidar ----------
    def add_cloud(self, pts, floor, robot=None):
        """pts: (N,3) odom-frame points near the robot; floor: floor height estimate;
        robot: (x, y) of the robot in the odom frame."""
        h = pts[:, 2] - floor
        obs = pts[(h > MIN_H) & (h < MAX_H), :2]
        flat = pts[h <= MIN_H, :2]
        self.recent = (self.recent + [obs[::2].copy()])[-4:]
        ok = True
        if self.T is not None and robot is not None and self.tracking and not self._aligning:
            ok = self.track(self._fresh(pts[(h > MIN_H) & (h < MAX_H)], obs), robot)
        if not self.mapping or self.T is None:
            return
        if not ok:
            self.skipped += 1
            self.status = (f"extending the saved map; skipped {self.skipped} lidar views that don't match it "
                           "(the dog's position on the map may be off: drive back to a well-mapped spot)")
            return
        tx, ty, th = self.T
        R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
        # one vote per cell per cloud: obstacle if anything in the height band, else open floor
        orr, oc = self.cells(obs @ R.T + (tx, ty))
        fr, fc = self.cells(flat @ R.T + (tx, ty))
        keep = ~np.isin(fr * SIZE + fc, orr * SIZE + oc)
        fr, fc = fr[keep], fc[keep]
        layers = {}
        for name, (lo, hi) in (("mid", MID_H), ("high", HIGH_H)):
            layers[name] = self.cells(pts[(h > lo) & (h < hi), :2] @ R.T + (tx, ty))
        up = h >= CEIL_MIN_H
        cxy, ch = pts[up, :2] @ R.T + (tx, ty), h[up]
        with self.lock:
            self.score[orr, oc] = np.minimum(self.score[orr, oc] + 1, SCORE_CAP)
            self.score[fr, fc] = np.maximum(self.score[fr, fc] - 1, -SCORE_CAP)
            self.seen[orr, oc] = True
            self.seen[fr, fc] = True
            for name, (rr, cc) in layers.items():
                a = getattr(self, name)
                a[rr, cc] = np.minimum(a[rr, cc] + 1, 50)
            if len(ch):
                ij = np.floor((cxy - np.array(self.origin)) / RES).astype(np.int64)
                ok = (ij[:, 0] >= 0) & (ij[:, 0] < SIZE) & (ij[:, 1] >= 0) & (ij[:, 1] < SIZE)
                ij, ch = ij[ok], ch[ok]
                low = np.full((SIZE, SIZE), np.inf, np.float32)      # lowest ceiling point per cell in this view
                np.minimum.at(low, (ij[:, 1], ij[:, 0]), ch.astype(np.float32))
                r, c = np.nonzero(np.isfinite(low))
                old = self.ceil[r, c]
                self.ceil[r, c] = np.where(np.isnan(old), low[r, c], 0.8 * old + 0.2 * low[r, c])
            self.version += 1

    def cell_state(self, x, y):
        """'obstacle', 'open' or 'unseen' at map point (x, y)."""
        c, r = int(math.floor((x - self.origin[0]) / RES)), int(math.floor((y - self.origin[1]) / RES))
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            return "unseen"
        with self.lock:
            score, seen = int(self.score[r, c]), bool(self.seen[r, c])
        return "obstacle" if score >= OCC_SCORE else "open" if seen else "unseen"

    # ---------- the map as an image ----------
    def grid(self):
        """uint8 image (row 0 at the bottom): 0 occupied, 254 free, 205 unknown."""
        with self.lock:
            score, seen = self.score.copy(), self.seen.copy()
        img = np.full((SIZE, SIZE), 205, np.uint8)
        occ = score >= OCC_SCORE
        img[seen] = 254
        img[occ] = 0
        return img

    def crop(self, img, margin=20):
        known = np.argwhere(img != 205)
        if len(known) == 0:
            return None
        (r0, c0), (r1, c1) = known.min(0) - margin, known.max(0) + margin + 1
        r0, c0 = max(r0, 0), max(c0, 0)
        r1, c1 = min(r1, SIZE), min(c1, SIZE)
        return img[r0:r1, c0:c1], (self.origin[0] + c0 * RES, self.origin[1] + r0 * RES)

    def room_deg(self):
        """The room's main wall direction in the map frame, mod 90 (deg, in [-45, 45)): the angle at which the
        occupied cells' x and y projections are sharpest (walls and desk rows are at right angles). Cached."""
        if getattr(self, "_room", (None,))[0] == self.version:
            return self._room[1]
        with self.lock:
            rc = np.argwhere(self.score >= OCC_SCORE)
        best = None
        if len(rc) > 200:
            # jitter within each cell, or the grid's own axes (0 and 45 deg) look sharpest
            pts = (rc[:, ::-1] + np.random.default_rng(0).uniform(0, 1, rc.shape)) * RES
            for d in np.arange(-45.0, 45.0, 0.5):
                a = math.radians(d)
                u = pts[:, 0] * math.cos(a) + pts[:, 1] * math.sin(a)
                v = -pts[:, 0] * math.sin(a) + pts[:, 1] * math.cos(a)
                sharp = sum(float((np.bincount(np.floor((w - w.min()) / RES).astype(int)) ** 2).sum()) for w in (u, v))
                if best is None or sharp > best[0]:
                    best = (sharp, float(d))
        self._room = (self.version, None if best is None else best[1])
        return self._room[1]

    def png(self):
        """(png bytes, meta) of the known part of the map, north up; None if empty."""
        cropped = self.crop(self.grid())
        if cropped is None:
            return None, None
        img, (ox, oy) = cropped
        ok, buf = cv2.imencode(".png", img[::-1])
        seen = int((img != 205).sum())
        meta = {"resolution": RES, "origin": [round(ox, 3), round(oy, 3)], "width": int(img.shape[1]),
                "height": int(img.shape[0]), "t": round(time.time(), 2), "mapped_m2": round(seen * RES * RES, 1),
                "mode": self.mode(), "status": self.status, "align": self.align_info, "saved_at": self.saved_at,
                "track": self.track_info, "room_deg": self.room_deg()}
        return buf.tobytes(), meta

    def mode(self):
        if self.mapping:
            return "mapping"
        return "localized" if self.T is not None else "not_aligned"

    # ---------- commands ----------
    def start_mapping(self, odom, fresh):
        with self.lock:
            if fresh:
                self.score[:] = 0
                self.seen[:] = False
                self._clear_layers()
                if self.T is None:
                    self._set_T((0.0, 0.0, 0.0), "new_map")   # new map frame = this session's odom frame
                # else keep the current frame, so saved places stay where they were
                self.status = "mapping a new map"
            elif self.T is None:
                return "Not lined up with the saved map yet, so it can't be extended. Start a new map instead."
            else:
                self.status = "extending the saved map"
            self.skipped = 0
            self.mapping = True
        return None

    def _clear_layers(self):
        self.mid[:] = 0
        self.high[:] = 0
        self.ceil[:] = np.nan

    def layer_png(self, name):
        """PNG of one height layer, cropped exactly like png() so it overlays the map. mid/high: dark =
        structure in that band. ceiling: brightness = ceiling height (dark = lower, e.g. lights), unknown grey."""
        base = self.grid()
        known = np.argwhere(base != 205)
        if len(known) == 0:
            return None
        (r0, c0), (r1, c1) = known.min(0) - 20, known.max(0) + 21
        r0, c0, r1, c1 = max(r0, 0), max(c0, 0), min(r1, SIZE), min(c1, SIZE)
        with self.lock:
            if name == "ceiling":
                a = self.ceil[r0:r1, c0:c1].copy()
            else:
                a = getattr(self, name)[r0:r1, c0:c1] >= LAYER_OCC
        img = np.full(a.shape, 205, np.uint8)
        if name == "ceiling":
            ok = ~np.isnan(a)
            img[ok] = np.clip((a[ok] - CEIL_MIN_H) / 1.5 * 230 + 20, 0, 255).astype(np.uint8)
        else:
            img[base[r0:r1, c0:c1] != 205] = 254
            img[a] = 0
        return cv2.imencode(".png", img[::-1])[1].tobytes()

    def clear(self):
        """Erase the map in memory. The saved file stays until the next save."""
        with self.lock:
            self.score[:] = 0
            self.seen[:] = False
            self._clear_layers()
            self.version += 1
            if self.T is None:
                self._set_T((0.0, 0.0, 0.0), "new_map")
        self.status = "cleared; mapping from scratch" if self.mapping else "cleared (the saved map is unchanged until you save)"
        return None

    def stop_mapping(self):
        self.mapping = False
        self.resume_mapping = False
        self.drop_unsaved()
        self.status = "mapping stopped (not saved)"

    def backup(self, keep=20):
        """Copy the current saved map to history/<name>_<saved time>.* before it is overwritten."""
        path = os.path.join(self.dir, self.name)
        if not os.path.exists(path + ".grid.npz"):
            return
        hist = os.path.join(self.dir, "history")
        os.makedirs(hist, exist_ok=True)
        os.chown(hist, HOST_UID, HOST_UID)
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(os.path.getmtime(path + ".grid.npz")))
        for ext in (".grid.npz", ".pgm", ".yaml"):
            if os.path.exists(path + ext):
                dst = os.path.join(hist, f"{self.name}_{stamp}{ext}")
                shutil.copy2(path + ext, dst)
                os.chown(dst, HOST_UID, HOST_UID)
        old = sorted(f for f in os.listdir(hist) if f.startswith(self.name + "_") and f.endswith(".grid.npz"))
        for f in old[:-keep]:
            for ext in (".grid.npz", ".pgm", ".yaml"):
                try:
                    os.remove(os.path.join(hist, f[:-len(".grid.npz")] + ext))
                except FileNotFoundError:
                    pass

    def revert(self):
        """Throw away unsaved changes: stop mapping and reload the saved map. The alignment is kept,
        since the saved map is in the same frame."""
        self.mapping = False
        self.resume_mapping = False
        self.drop_unsaved()
        path = os.path.join(self.dir, self.name + ".grid.npz")
        if not os.path.exists(path):
            return "There is no saved map to go back to."
        d = np.load(path)
        with self.lock:
            self.read_grid(d)
            self.origin = tuple(d["origin"])
            self.version += 1
        self.field = None
        self.saved_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
        self.status = f"back to the saved map from {self.saved_at}"
        return None

    def save(self, odom=None):
        img = self.grid()
        path = os.path.join(self.dir, self.name)
        self.backup()
        with self.lock:
            np.savez_compressed(path + ".grid.npz", score=self.score, seen=self.seen, origin=np.array(self.origin),
                                mid=self.mid, high=self.high, ceil=self.ceil, **self.frame_info(odom))
        cropped = self.crop(img)
        if cropped is not None:   # standard map files too, for viewing and for Nav2
            c, (ox, oy) = cropped
            cv2.imwrite(path + ".pgm", c[::-1])
            with open(path + ".yaml", "w") as f:
                f.write(f"image: {self.name}.pgm\nmode: trinary\nresolution: {RES}\norigin: [{ox:.3f}, {oy:.3f}, 0]\n"
                        "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n")
        for ext in (".grid.npz", ".pgm", ".yaml"):
            if os.path.exists(path + ext):
                os.chown(path + ext, HOST_UID, HOST_UID)
        self.mapping = False
        self.drop_unsaved()
        self.saved_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.status = f"saved {self.saved_at}"
        return None

    def read_grid(self, d):
        if "mid" in d:       # height layers (maps made after 10-23)
            self.mid[:], self.high[:], self.ceil[:] = d["mid"], d["high"], d["ceil"]
        else:
            self._clear_layers()
        if "score" in d:
            self.score[:], self.seen[:] = d["score"], d["seen"]
        else:   # older files kept raw counts
            self.score[:] = np.clip(d["hits"].astype(np.int32) - d["miss"], -SCORE_CAP, SCORE_CAP)
            self.seen[:] = (d["hits"].astype(np.int32) + d["miss"]) > 0

    def unsaved_path(self):
        return os.path.join(self.dir, self.name + ".unsaved.npz")

    def frame_info(self, odom):
        """The alignment plus where the dog was, so a restart without a dog reboot can reuse it."""
        if self.T is None or odom is None:
            return {}
        return {"T": np.array(self.T), "odom": np.array([odom["pos"][0], odom["pos"][1], odom["yaw"]])}

    # ---------- remembering the line-up across console restarts ----------
    def session_path(self):
        return os.path.join(self.dir, self.name + ".session.json")

    def save_session(self, odom):
        """Remember the current line-up, so a console restart (same dog session) doesn't lose it."""
        if self.T is None or odom is None or self.mapping:
            return
        tmp = self.session_path() + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"T": list(self.T), "odom": [odom["pos"][0], odom["pos"][1], odom["yaw"]],
                       "saved_at": self.saved_at, "t": time.time()}, f)
        os.chown(tmp, HOST_UID, HOST_UID)
        os.replace(tmp, self.session_path())

    def load_session(self):
        try:
            with open(self.session_path()) as f:
                d = json.load(f)
        except (OSError, ValueError):
            return
        # only for the same saved map and recent; try_align then checks the dog hasn't rebooted
        if d.get("saved_at") == self.saved_at and time.time() - d.get("t", 0) < 12 * 3600:
            self.pending = (tuple(d["T"]), tuple(d["odom"]))

    # ---------- drift correction ----------
    def _wall_field(self):
        """Likelihood that a point sits on a mapped wall, per cell (cached; rebuilt every 3 s while mapping)."""
        key = self.version if not self.mapping else int(time.monotonic() / 3)
        if self.field is not None and self.field[3] == key:
            return self.field
        with self.lock:
            occ = self.score >= OCC_SCORE
        rows, cols = np.nonzero(occ)
        if len(rows) < 50:
            self.field = (None, 0, 0, key)
            return self.field
        m = 20
        r0, c0 = max(rows.min() - m, 0), max(cols.min() - m, 0)
        r1, c1 = min(rows.max() + m, SIZE), min(cols.max() + m, SIZE)
        sub = occ[r0:r1, c0:c1]
        d = cv2.distanceTransform((~sub).astype(np.uint8), cv2.DIST_L2, 5) * RES
        self.field = (np.exp(-d * d / (2 * TRACK_SIGMA ** 2)).astype(np.float32), r0, c0, key)
        return self.field

    def _fresh(self, pts3, obs):
        """obs (pts3[:, :2]) limited to voxels that first appeared within TRACK_FRESH_S, or all of obs when
        too few are fresh. Keeps first-seen times per 5 cm voxel of the dog's cloud (pts3: odom-frame xyz)."""
        if TRACK_FRESH_S <= 0 or len(pts3) == 0:
            return obs
        now = time.monotonic()
        k = np.floor(pts3 / RES).astype(np.int64) + 2 ** 20
        key = (k[:, 0] << 42) | (k[:, 1] << 21) | k[:, 2]
        uk, inv = np.unique(key, return_inverse=True)
        keys, born, seen = self._vox
        i = np.minimum(np.searchsorted(keys, uk), max(len(keys) - 1, 0))
        known = (keys[i] == uk) if len(keys) else np.zeros(len(uk), bool)
        b = np.where(known, born[i] if len(keys) else now, now)
        old = np.ones(len(keys), bool)
        old[i[known]] = False
        old &= now - seen < VOXEL_KEEP_S
        keys, born, seen = np.r_[keys[old], uk], np.r_[born[old], b], np.r_[seen[old], np.full(len(uk), now)]
        o = np.argsort(keys, kind="stable")
        self._vox = (keys[o], born[o], seen[o])
        fresh = now - b[inv] <= TRACK_FRESH_S
        self._fresh_obs = obs[fresh]           # marker_fix's lidar check
        self._sus_obs = obs[now - b[inv] <= SUSPECT_FRESH_S]
        return obs[fresh] if fresh.sum() >= TRACK_FRESH_MIN else obs

    def track(self, obs, robot):
        """Nudge T so this lidar view's obstacles sit on the map's walls (odometry drifts, the walls don't).
        Returns False if the view clearly doesn't match the map where it lands (so it shouldn't be mapped)."""
        L, r0, c0, _ = self._wall_field()
        if L is None or len(obs) < TRACK_MIN_PTS:
            return True
        pts = np.unique(np.floor(obs / RES), axis=0) * RES + RES / 2
        if len(pts) < TRACK_MIN_PTS:
            return True
        if len(pts) > TRACK_MAX_PTS:
            pts = pts[np.random.default_rng().choice(len(pts), TRACK_MAX_PTS, replace=False)]
        T = self.T
        tx, ty, th = T
        c, s = math.cos(th), math.sin(th)
        q = pts @ np.array([[c, s], [-s, c]]) + (tx, ty)              # map frame
        rx, ry = tx + c * robot[0] - s * robot[1], ty + s * robot[0] + c * robot[1]
        n = int(round(TRACK_RANGE_M / RES / TRACK_STEP_CELLS))
        offs = np.arange(-n, n + 1) * TRACK_STEP_CELLS
        dr, dc = [a.ravel() for a in np.meshgrid(offs, offs, indexing="ij")]
        H, W = L.shape
        best, zero = None, None
        y = self._odom_yaw
        if y is not None and self._track_yaw is not None and abs(wrap(y - self._track_yaw)) > math.radians(POST_TURN_DEG):
            self._wide = POST_TURN_VIEWS
        self._track_yaw = y
        wide = self._wide > 0
        span = TRACK_DEG_WIDE if wide else TRACK_DEG
        if wide:
            self._wide -= 1
        for deg in np.arange(-span, span + 1e-9, TRACK_DEG_STEP):
            a = math.radians(deg)
            ca, sa = math.cos(a), math.sin(a)
            rel = q - (rx, ry)
            qq = rel @ np.array([[ca, sa], [-sa, ca]]) + (rx, ry)
            cc = np.floor((qq[:, 0] - self.origin[0]) / RES).astype(np.int64) - c0
            rr = np.floor((qq[:, 1] - self.origin[1]) / RES).astype(np.int64) - r0
            R = rr[None, :] + dr[:, None]
            C = cc[None, :] + dc[:, None]
            ok = (R >= 0) & (R < H) & (C >= 0) & (C < W)
            vals = np.where(ok, L[np.clip(R, 0, H - 1), np.clip(C, 0, W - 1)], 0.0).mean(axis=1)
            k = int(vals.argmax())
            if best is None or vals[k] > best[0]:
                best = (float(vals[k]), a, dc[k] * RES, dr[k] * RES)
            if abs(deg) < 1e-9:
                zero = float(vals[(dr == 0) & (dc == 0)][0])
        fit, a, dx, dy = best
        if wide and abs(math.degrees(a)) < 1.0:
            self._wide = 0                        # heading has caught up
        # how much of this view lands on area the map already knows (seen cells)
        cc = np.floor((q[:, 0] - self.origin[0]) / RES).astype(np.int64)
        rr = np.floor((q[:, 1] - self.origin[1]) / RES).astype(np.int64)
        inb = (rr >= 0) & (rr < SIZE) & (cc >= 0) & (cc < SIZE)
        known = float(self.seen[rr[inb], cc[inb]].mean()) if inb.any() else 0.0
        info = {"fit": round(fit, 2), "fit_before": round(zero, 2), "points": int(len(pts)), "wide": wide,
                "known": round(known, 2), "at": time.strftime("%H:%M:%S")}
        matches = not (known >= MISMATCH_KNOWN and fit < MISMATCH_FIT)
        self._judge_lost(fit, robot)
        ff = self._fit_at(self._sus_obs, T)
        if ff is not None:
            self.fresh_fit = ff
            self._judge_suspect(ff, robot)
        if fit < TRACK_MIN_FIT or fit - zero < TRACK_MIN_GAIN or (a == 0 and dx == 0 and dy == 0):
            self.track_info = dict(info, applied=False, matches=matches)
            self.track_log.append(dict(self.track_info, t=round(time.time(), 2), best_dx=round(dx, 3),
                                       best_dy=round(dy, 3), best_ddeg=round(math.degrees(a), 2)))
            return matches
        a, dx, dy = a * TRACK_GAIN, dx * TRACK_GAIN, dy * TRACK_GAIN
        if STILL_MODE != "off":
            ref = getattr(self, "_still_ref", None)
            if ref is None or math.hypot(robot[0] - ref[0], robot[1] - ref[1]) > STILL_M:
                self._still_ref, self._still_acc = (robot[0], robot[1]), np.zeros(2)     # moving: new reference
            else:                                                                        # still
                d = np.array([dx, dy])
                if STILL_MODE in ("pts", "both") and len(pts) < STILL_MIN_PTS:
                    d[:] = 0.0
                    info["still"] = "pts"
                if STILL_MODE in ("cap", "both") and d.any():
                    room = STILL_CAP_M - float(np.hypot(*self._still_acc))
                    n = float(np.hypot(*d))
                    if n > max(room, 0.0):
                        d *= max(room, 0.0) / n
                        info["still"] = "cap"
                self._still_acc = self._still_acc + d
                dx, dy = float(d[0]), float(d[1])
        ca, sa = math.cos(a), math.sin(a)
        # map' = Ra (map - robot) + robot + d, applied to the transform's translation and rotation
        nx = ca * (tx - rx) - sa * (ty - ry) + rx + dx
        ny = sa * (tx - rx) + ca * (ty - ry) + ry + dy
        self.track_info = dict(info, applied=True, matches=matches, dx=round(dx, 3), dy=round(dy, 3),
                               ddeg=round(math.degrees(a), 2))
        self.track_log.append(dict(self.track_info, t=round(time.time(), 2)))
        if self.T is T:           # not replaced meanwhile (line-up, manual frame)
            self._set_T((nx, ny, wrap(th + a)), "drift_correction", **{k: self.track_info[k] for k in ("fit", "dx", "dy", "ddeg")})
        return matches

    def take_frame(self, d):
        if "T" in d and "odom" in d:
            self.pending = (tuple(float(v) for v in d["T"]), tuple(float(v) for v in d["odom"]))

    def autosave(self, odom=None):
        """While mapping, keep a copy on disk so a console restart doesn't lose the map."""
        if not self.mapping:
            return
        with self.lock:
            score, seen = self.score.copy(), self.seen.copy()
            mid, high, ceil = self.mid.copy(), self.high.copy(), self.ceil.copy()
        tmp = self.unsaved_path() + ".tmp.npz"
        np.savez_compressed(tmp, score=score, seen=seen, origin=np.array(self.origin), mid=mid, high=high, ceil=ceil,
                            **self.frame_info(odom))
        os.chown(tmp, HOST_UID, HOST_UID)
        os.replace(tmp, self.unsaved_path())

    def drop_unsaved(self):
        if os.path.exists(self.unsaved_path()):
            os.remove(self.unsaved_path())

    def load_unsaved(self):
        """After a restart mid-mapping: take the unsaved map back, line up with it, keep mapping."""
        if not os.path.exists(self.unsaved_path()):
            return False
        d = np.load(self.unsaved_path())
        with self.lock:
            self.read_grid(d)
            self.origin = tuple(d["origin"])
        self.take_frame(d)
        self.resume_mapping = True
        return True

    def load(self):
        path = os.path.join(self.dir, self.name + ".grid.npz")
        if not os.path.exists(path):
            return False
        d = np.load(path)
        with self.lock:
            self.read_grid(d)
            self.origin = tuple(d["origin"])
        self.take_frame(d)
        self.saved_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
        return True

    # ---------- lining up a new session with the saved map ----------
    def _judge_lost(self, fit, robot):
        now = time.time()
        if self._judged_at is not None and now - self._judged_at > LOST_GAP_S:
            self._low = None               # the dog stood (or views stopped): don't count that time as low fit
        self._judged_at = now
        if fit >= LOST_CLEAR:
            self._low, self.lost_since = None, None
            return
        if fit >= LOST_FIT:
            return
        rx, ry = float(robot[0]), float(robot[1])
        if self._low is None:
            self._low = [now, (rx, ry), 0.0]
            return
        self._low[2] += math.hypot(rx - self._low[1][0], ry - self._low[1][1])
        self._low[1] = (rx, ry)
        if self.lost_since is None and now - self._low[0] >= LOST_S and self._low[2] >= LOST_MOVE_M:
            self.lost_since = round(now, 2)

    def _judge_suspect(self, fit, robot):
        """Like _judge_lost, on the fresh-voxel fit at the current T (advisory only)."""
        now = time.time()
        if self._sus_at is not None and now - self._sus_at > LOST_GAP_S:
            self._sus_low = None
        self._sus_at = now
        if fit >= SUSPECT_CLEAR:
            self._sus_low, self.suspect_since = None, None
            return
        if fit >= SUSPECT_FIT:
            return
        rx, ry = float(robot[0]), float(robot[1])
        if self._sus_low is None:
            self._sus_low = [now, (rx, ry), 0.0]
            return
        self._sus_low[2] += math.hypot(rx - self._sus_low[1][0], ry - self._sus_low[1][1])
        self._sus_low[1] = (rx, ry)
        if self.suspect_since is None and now - self._sus_low[0] >= SUSPECT_S and self._sus_low[2] >= SUSPECT_MOVE_M:
            self.suspect_since = round(now, 2)

    def _fit_at(self, obs, T):
        """Mean wall likelihood of these odom-frame points if the odom-to-map transform were T, or None."""
        L, r0, c0, _ = self._wall_field()
        if L is None or obs is None:
            return None
        pts = np.unique(np.floor(obs / RES), axis=0) * RES + RES / 2
        if len(pts) < TRACK_MIN_PTS:
            return None
        tx, ty, th = T
        c, s = math.cos(th), math.sin(th)
        q = pts @ np.array([[c, s], [-s, c]]) + (tx, ty)
        cc = np.floor((q[:, 0] - self.origin[0]) / RES).astype(np.int64) - c0
        rr = np.floor((q[:, 1] - self.origin[1]) / RES).astype(np.int64) - r0
        H, W = L.shape
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        return float(np.where(ok, L[np.clip(rr, 0, H - 1), np.clip(cc, 0, W - 1)], 0.0).mean())

    def view_fit(self, T):
        """How well the recent lidar views sit on the map's walls if the odom-to-map transform were T: the
        drift tracker's fit (mean wall likelihood, about 0.75-0.9 when placed right), or None."""
        L, r0, c0, _ = self._wall_field()
        if L is None or not self.recent:
            return None
        pts = np.unique(np.floor(np.concatenate(self.recent) / RES), axis=0) * RES + RES / 2
        if len(pts) < TRACK_MIN_PTS:
            return None
        tx, ty, th = T
        c, s = math.cos(th), math.sin(th)
        q = pts @ np.array([[c, s], [-s, c]]) + (tx, ty)
        cc = np.floor((q[:, 0] - self.origin[0]) / RES).astype(np.int64) - c0
        rr = np.floor((q[:, 1] - self.origin[1]) / RES).astype(np.int64) - r0
        H, W = L.shape
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        return round(float(np.where(ok, L[np.clip(rr, 0, H - 1), np.clip(cc, 0, W - 1)], 0.0).mean()), 3)

    def marker_fix(self, odom, sightings, survey):
        """Re-anchor the dog's map position to surveyed markers. sightings: go2_markers items (z, x, yaw_deg,
        view_deg, dist, ambig, fix_ok, held, mark); survey: {mark: {"x", "y", "facing_deg"}} (map frame, facing =
        where the marker's front looks). Returns a dict describing what was done (also kept in marker_log)."""
        now = time.time()
        if self.T is None or odom is None:
            return None
        if not hasattr(self, "_mk_buf"):
            self._mk_buf, self._mk_last, self.marker_log = [], -1e9, deque(maxlen=200)
        mp = self.pose(odom)
        psi = mp["yaw"]
        for m in sightings or []:
            sv = survey.get(m.get("id"))
            why = []
            if sv is None: why.append("unsurveyed")
            if not m.get("fix_ok") or m.get("held"): why.append("not_fix_ok")
            if m.get("ambig") is not None and m["ambig"] >= MK_MAX_AMBIG: why.append("ambiguous")
            if m.get("view_deg", 90) > MK_MAX_VIEW: why.append("oblique")
            if m.get("dist", 9) > MK_MAX_DIST: why.append("far")
            if sv is not None and abs(math.degrees(wrap(math.radians(sv["facing_deg"] - 180 + m.get("yaw_deg", 0)) - psi))) > MK_YAW_SANITY:
                why.append("yaw")
            if why:
                continue
            f, l = MK_CAM_AHEAD + m["z"], -m["x"]
            bx = sv["x"] - (math.cos(psi) * f - math.sin(psi) * l)
            by = sv["y"] - (math.sin(psi) * f + math.cos(psi) * l)
            self._mk_buf.append((now, m["mark"], bx - mp["x"], by - mp["y"], f, l, sv["x"], sv["y"]))
        self._mk_buf = [b for b in self._mk_buf if now - b[0] <= MK_WINDOW_S]
        if len(self._mk_buf) < MK_MIN_N or now - self._mk_last < MK_COOLDOWN_S:
            return None
        d = np.array([(b[2], b[3]) for b in self._mk_buf])
        md = np.median(d, axis=0)
        spread = float(np.median(np.hypot(*(d - md).T)))
        shift = float(math.hypot(*md))
        rec = {"t": round(now, 2), "n": len(d), "marks": sorted({b[1] for b in self._mk_buf}), "dx": round(float(md[0]), 3),
               "dy": round(float(md[1]), 3), "shift": round(shift, 3), "spread": round(spread, 3)}
        if spread > MK_MAX_SPREAD:
            rec["action"] = "spread"
        elif shift < MK_MIN_SHIFT:
            rec["action"] = "agree"
        else:
            T = self.T
            T2 = (T[0] + float(md[0]), T[1] + float(md[1]), T[2])
            fo = getattr(self, "_fresh_obs", None)
            nf = 0 if fo is None or not len(fo) else len(np.unique(np.floor(fo / RES), axis=0))
            if MK_GATE == "all":
                f0, f1 = self.view_fit(T), self.view_fit(T2)
            elif nf < MK_FRESH_MIN:
                f0 = f1 = None                     # too few fresh voxels: the lidar abstains
            else:
                f0, f1 = self._fit_at(fo, T), self._fit_at(fo, T2)
                if MK_GATE == "joint" and f1 is not None:
                    # dog pose for heading offset a: marker position minus the rotated camera offset
                    ox_, oy_ = odom["pos"][0], odom["pos"][1]
                    last = self._mk_buf[-1]
                    ff, ll, mx, my = last[4], last[5], last[6], last[7]
                    best = (f1, 0.0, T2)
                    for a in np.arange(-MK_JOINT_DEG, MK_JOINT_DEG + 1e-9, 1.0):
                        p2 = psi + math.radians(a)
                        X = mx - (math.cos(p2) * ff - math.sin(p2) * ll)
                        Y = my - (math.sin(p2) * ff + math.cos(p2) * ll)
                        Tc = self.T_for(odom, X, Y, p2)
                        fc = self._fit_at(fo, Tc)
                        if fc is not None and fc > best[0] + 1e-6:
                            best = (fc, float(a), Tc)
                    f1, T2 = best[0], best[2]
                    rec["joint_deg"] = best[1]
                    md = np.array([T2[0] + math.cos(T2[2]) * ox_ - math.sin(T2[2]) * oy_ - mp["x"],
                                   T2[1] + math.sin(T2[2]) * ox_ + math.cos(T2[2]) * oy_ - mp["y"]])
                    shift = float(math.hypot(*md))
                    rec.update(dx=round(float(md[0]), 3), dy=round(float(md[1]), 3), shift=round(shift, 3))
            rec.update(fit_now=f0, fit_marker=f1, fresh_cells=nf)
            if shift > MK_MAX_SHIFT:
                rec["action"] = "too_far"
            elif f0 is not None and f1 is not None and f1 < f0 - MK_LIDAR_MARGIN:
                rec["action"] = "lidar_disagrees"
            elif not MK_MOVE:
                rec["action"] = "would_move"
            else:
                rec["action"] = "moved"
                self._set_T(T2, "marker", marks=rec["marks"], shift_m=rec["shift"], gate=MK_GATE)
        if rec["action"] in ("too_far", "lidar_disagrees", "would_move"):
            if self.suspect_since is None and rec["shift"] >= MK_SUSPECT_M:
                self.suspect_since = round(now, 2)
            mp2 = self.pose(odom)
            self.event_seq += 1
            self.events.append({"t": rec["t"], "kind": "marker_disagree", "seq": self.event_seq, "action": rec["action"],
                                "marks": rec["marks"], "pose": mp2, "marker_dx": rec["dx"], "marker_dy": rec["dy"],
                                "shift_m": rec["shift"], "spread_m": rec["spread"], "n": rec["n"],
                                "fit_now": rec.get("fit_now"), "fit_marker": rec.get("fit_marker"),
                                "fresh_cells": rec.get("fresh_cells"), "joint_deg": rec.get("joint_deg"),
                                "jump": False, "status": self.status})
        self._mk_buf, self._mk_last = [], now
        self.marker_log.append(rec)
        return rec

    def T_for(self, odom, x, y, yaw):
        """The odom-to-map transform that puts the dog (at odom) at map pose (x, y, yaw)."""
        th = wrap(yaw - odom["yaw"])
        c, s = math.cos(th), math.sin(th)
        ox, oy = odom["pos"][0], odom["pos"][1]
        return (x - (c * ox - s * oy), y - (s * ox + c * oy), th)

    def candidates(self, odom, centre=None, radius=None, top=5):
        """Where the dog could be: the best line-ups of the recent lidar views with the saved map, without
        applying any. centre=(x, y) with radius (m) searches only there; None searches the whole map.
        Returns ([{x, y, yaw, score, fit}], None) best first, or (None, reason)."""
        if self.mapping:
            return None, "stop mapping first"
        if not (self.score >= OCC_SCORE).any():
            return None, "no saved map to line up with"
        if odom is None or len(self.recent) < 2:
            return None, "no lidar data yet"
        if self._aligning:
            return None, "a line-up is already running; try again in a few seconds"
        self._aligning = True
        try:
            found = self._search(odom, None if centre is None else (centre[0], centre[1], None), radius, keep_all=True)
        finally:
            self._aligning = False
        if isinstance(found, str):
            return None, found
        out = []
        for score, deg, T in found:
            p = self.T_for_pose(T, odom)
            if any(math.hypot(p[0] - o["x"], p[1] - o["y"]) < CAND_SEP_M
                   and abs(math.degrees(wrap(p[2] - o["yaw"]))) < CAND_SEP_DEG for o in out):
                continue
            out.append({"x": round(p[0], 3), "y": round(p[1], 3), "yaw": round(p[2], 3),
                        "yaw_deg": round(math.degrees(p[2]), 1), "score": round(score, 3), "_T": T})
            if len(out) >= top:
                break
        for o in out:
            o["fit"] = self.view_fit(o.pop("_T"))
        return out, None

    @staticmethod
    def T_for_pose(T, odom):
        tx, ty, th = T
        c, s = math.cos(th), math.sin(th)
        x, y = odom["pos"][0], odom["pos"][1]
        return tx + c * x - s * y, ty + s * x + c * y, wrap(odom["yaw"] + th)

    def set_pose(self, odom, x, y, yaw, by, force=False):
        """An agent says the dog is at map (x, y, yaw). Applied exactly (no search) unless it fits the
        recent lidar views worse than the current pose, unless force. Returns (info, None) or (info, reason)."""
        if self.mapping:
            return {}, "stop mapping first"
        if odom is None:
            return {}, "no odometry"
        T = self.T_for(odom, float(x), float(y), float(yaw))
        before = self.view_fit(self.T) if self.T is not None else None
        after = self.view_fit(T)
        info = {"fit_before": before, "fit_after": after}
        if not force and before is not None and (after is None or after < before - 0.02):
            return info, (f"that pose fits the lidar worse than the current one ({after} vs {before}); "
                          "send force: true to apply it anyway")
        self.pending, self.resume_mapping = None, False
        self._set_T(T, "agent_relocalize", by=by, fit=after, fit_before=before)
        self.align_info = {"score": None, "runner_up": None, "by_agent": by, "fit_before": before,
                           "fit_after": after, "at": time.strftime("%H:%M:%S")}
        self.status = f"placed by agent {by} at ({float(x):.2f}, {float(y):.2f}) (fit {after}, was {before})"
        return info, None

    def localize_at(self, odom, x, y, yaw=None, by="console"):
        """A person says the dog is about at map (x, y), optionally facing about yaw (rad). Search
        only near there and take the best heading, without the usual confidence checks."""
        if self.mapping:
            return "stop mapping first"
        if not (self.score >= OCC_SCORE).any():
            return "no saved map to line up with"
        if odom is None or len(self.recent) < 2:
            return "no lidar data yet"
        if self._aligning:
            return "a line-up is already running; try again in a few seconds"
        self.pending, self.resume_mapping = None, False
        self._aligning = True
        self.status = "lining up near the spot you clicked…"
        self._placed_by = by
        threading.Thread(target=self._align, args=(odom, (float(x), float(y), yaw)), daemon=True).start()
        return None

    def try_align(self, odom, force=False):
        """Start an alignment in the background if one is needed and the lidar has data."""
        if self._aligning or self.mapping or odom is None or len(self.recent) < 2:
            return
        if self.T is not None and not force:
            return
        if self.pending and not force:
            T, (px, py, pyaw) = self.pending
            self.pending = None
            if (math.hypot(odom["pos"][0] - px, odom["pos"][1] - py) < SAME_SESSION_M
                    and abs(wrap(odom["yaw"] - pyaw)) < SAME_SESSION_RAD):
                self._set_T(T, "session_restore")
                if self.resume_mapping:
                    self.resume_mapping, self.mapping = False, True
                    self.status = "picked up the unsaved map where it left off; still mapping"
                else:
                    self.status = "saved map loaded (same session as when it was saved)"
                return
        if not force and time.monotonic() - self._last_try < ALIGN_RETRY_S:
            return
        if not (self.score >= OCC_SCORE).any():
            return
        self._last_try = time.monotonic()
        self._aligning = True
        self.status = "lining up with the saved map…"
        threading.Thread(target=self._align, args=(odom,), daemon=True).start()

    def _search(self, odom, hint=None, radius=None, keep_all=False):
        """Line the recent lidar views up with the saved map: for each heading (1 degree steps) the best shift.
        hint (x, y, yaw or None): keep only shifts that put the dog within radius (default HINT_R) of (x, y),
        and headings within HINT_YAW_TOL of yaw. Returns [(score, deg, T)] best first, or a reason string."""
        radius = HINT_R if radius is None else radius
        pts = np.concatenate(self.recent)          # odom frame
        # one point per 5 cm cell, capped, so the search stays light
        pts = np.unique(np.floor(pts / RES), axis=0) * RES + RES / 2
        if len(pts) > ALIGN_MAX_PTS:
            pts = pts[np.random.default_rng(0).choice(len(pts), ALIGN_MAX_PTS, replace=False)]
        img = self.grid()
        cropped = self.crop(img, margin=60)
        if cropped is None or len(pts) < 50:
            return "not enough lidar data to line up yet"
        sub, (ox, oy) = cropped
        walls = cv2.dilate((sub == 0).astype(np.uint8), np.ones((3, 3), np.uint8))
        free = ((sub == 254) & (walls == 0)).astype(np.float32)
        rel = pts - pts.mean(0)
        pad = int(np.ceil(np.abs(rel).max() * 2 / RES)) + 2     # zero padding so shifts don't wrap around
        H, W = walls.shape[0] + pad, walls.shape[1] + pad
        def ft(a):
            z = np.zeros((H, W), np.float32)
            z[:a.shape[0], :a.shape[1]] = a
            return np.fft.rfft2(z)
        FW, FF = ft(walls.astype(np.float32)), ft(free)
        robot_rel = np.array(odom["pos"][:2], dtype=np.float64) - pts.mean(0)
        if hint:
            yy, xx = np.mgrid[0:H, 0:W]
        best = []
        for deg in np.arange(0, 360, 1.0):
            th = math.radians(deg)
            if hint and hint[2] is not None and abs(wrap(odom["yaw"] + th - hint[2])) > HINT_YAW_TOL:
                continue
            c, s = math.cos(th), math.sin(th)
            q = rel @ np.array([[c, s], [-s, c]])  # rotate by th
            ij = np.unique(np.floor(q / RES).astype(np.int64), axis=0)
            qmin = ij.min(0)
            ij -= qmin
            if ij[:, 0].max() >= W or ij[:, 1].max() >= H:
                continue
            L = np.zeros((H, W), np.float32)
            L[ij[:, 1], ij[:, 0]] = 1
            FL = np.conj(np.fft.rfft2(L))
            score = (np.fft.irfft2(FW * FL, s=(H, W)) - np.fft.irfft2(FF * FL, s=(H, W))) / len(ij)
            if hint:
                # keep only shifts that put the dog within radius of the given spot
                qr = robot_rel @ np.array([[c, s], [-s, c]])
                cc0 = (hint[0] - ox - 0.5 * RES) / RES - (qr[0] / RES - qmin[0])
                r0 = (hint[1] - oy - 0.5 * RES) / RES - (qr[1] / RES - qmin[1])
                score = np.where(np.hypot(xx - cc0, yy - r0) <= radius / RES, score, -np.inf)
            if keep_all:          # several shifts per heading (other places that fit): local maxima 0.5 m apart
                sc = np.nan_to_num(score.astype(np.float32), neginf=-1e9)
                peak = (sc == cv2.dilate(sc, np.ones((11, 11), np.uint8))) & (sc > 0)
                ks = np.flatnonzero(peak)
                picks = [int(k) for k in ks[np.argsort(-sc.ravel()[ks])[:5]]]
            else:
                picks = [int(score.argmax())]
            for k in picks:
                r, cc = divmod(k, W)
                # a rotated point q lands at cell (q/RES - qmin) + (cc, r) of the crop
                shift = np.array([ox, oy]) + (np.array([cc, r]) - qmin) * RES
                mean_map = shift + 0.5 * RES       # map position of the cloud's mean point (rel = 0)
                mx, my = pts.mean(0)
                T = (float(mean_map[0] - (c * mx - s * my)), float(mean_map[1] - (s * mx + c * my)), th)
                best.append((float(score.flat[k]), float(deg), T))
        if not best:
            return "could not line up: map too small"
        best = [b for b in best if np.isfinite(b[0])]
        if not best:
            return "could not line up there: the clicked spot is off the mapped area"
        best.sort(key=lambda b: -b[0])
        self._search_pts = len(pts)
        return best

    def _align(self, odom, hint=None):
        """hint: (x, y, yaw or None) in the map from a person; then the dog must end up within
        HINT_R of (x, y) (and HINT_YAW_TOL of yaw), and the best fit there is taken as is."""
        try:
            self.T_found = None
            t0 = time.time()
            best = self._search(odom, hint)
            if isinstance(best, str):
                self.status = best
                return
            score, deg, T = best[0]
            # best fit at a clearly different rotation, to judge ambiguity
            other = next((b[0] for b in best[1:] if abs(wrap(math.radians(b[1] - deg))) > math.radians(10)), 0.0)
            th = T[2]
            self.align_info = {"score": round(score, 2), "runner_up": round(other, 2), "deg": float(deg),
                               "points": int(self._search_pts), "secs": round(time.time() - t0, 1), "at": time.strftime("%H:%M:%S")}
            self.T_found = T
            if self.mapping:      # a new map was started meanwhile; its frame wins
                return
            if hint:
                self._set_T(self.T_found, "hand_placement", by=getattr(self, "_placed_by", "console"),
                            clicked={"x": round(hint[0], 2), "y": round(hint[1], 2),
                                     "yaw": None if hint[2] is None else round(hint[2], 3)})
                self.align_info["by_hand"] = True
                heading = math.degrees(wrap(odom["yaw"] + th))
                self.status = (f"placed by hand near ({hint[0]:.1f}, {hint[1]:.1f}), facing {heading:.0f}° "
                               f"({score:.0%} fit, next best heading {other:.0%})")
                if score < 0.3 or score - other < 0.05:
                    self.status += ": unsure, check the arrow against the camera"
                return
            if self.T is not None:   # placed by hand while this ran
                return
            if score >= ALIGN_OK and score - other >= ALIGN_MARGIN:
                self._set_T(self.T_found, "auto_align")
                self.status = f"lined up with the saved map ({score:.0%} fit)"
                if self.resume_mapping:
                    self.resume_mapping = False
                    self.mapping = True
                    self.status = f"restored the unsaved map ({score:.0%} fit); still mapping"
            else:
                self.status = (f"could not line up confidently ({score:.0%} fit, next best {other:.0%}); "
                               "drive a little so the lidar sees more. Retrying every 20 s.")
        finally:
            self._aligning = False

    def info(self):
        return {"mode": self.mode(), "status": self.status, "align": self.align_info, "saved_at": self.saved_at,
                "aligning": self._aligning, "track": self.track_info}

    # ---------- for tests ----------
    def set_T(self, T):
        self.T = T
