"""Straighten a lab map offline, from a recording of the mapping drive (Oliver, 10-23).

The dog's yaw drifts (a few deg/min walking, 7-14 deg per full turn in place), and its /point_cloud2 is
its own voxel map (5 cm voxels, odom frame, a ~6 m window around the dog) in which every voxel stays
where it was first placed, with the yaw the dog had then. A long drive therefore leaves walls in
several slightly rotated copies. The lab is "Manhattan" (walls, desk rows and aisles at right angles),
so the angle of freshly placed structure, mod 90 deg, tells the heading error at each moment:

  1. room axis: dominant direction mod 90 of the current saved map (reported; the correction itself is
     anchored at the start of the drive, when the console's line-up T was made, so the frame stays put)
  2. heading error delta(t): angle mod 90 of voxels placed for the first time in a ~3 s window, measured by
     the sharpest x/y projection histograms, then a Kalman filter + RTS smoother whose process noise
     grows with time and, much more, with the angle turned (so delta can step at turns in place)
  3. corrected trajectory: odom increments rotated by -delta(t), integrated from the start pose
  4. every voxel is re-placed with the pose at its first appearance (rotated by -delta about where the
     dog was then), and the grid is rebuilt with the same votes as Mapper.add_cloud; the mid/high layers
     count distinct 2 s windows instead of frames, and are cleared where the floor shows through
  5. writes <maps>/lab_straightened.grid.npz (same keys as lab.grid.npz) and pictures

Stage 1 needs ROS (rosbag2_py); run it in the rosrobot image. The rest needs numpy + cv2 only:
  docker run --rm --entrypoint bash -v /home/nesl/oliver:/src -v <out>:/out rosrobot -c \
    'source /opt/ros/humble/setup.bash; python3 /src/go2_straighten.py --bag /src/go2_recordings/<rec> \
     --cache /out/cache.npz --maps /src/go2_maps --pics /out/pics'
"""
import argparse
import json
import math
import os

import numpy as np

RES, SIZE = 0.05, 1000           # same grid as go2_mapper.py
MIN_H, MAX_H = 0.20, 0.60        # bump band (go2_mapper.py)
MID_H, HIGH_H, CEIL_MIN_H = (0.60, 1.20), (1.20, 2.20), 2.20
SCORE_CAP, OCC_SCORE = 5, 2
MAP_MAX_TURN = 0.15              # rad/s: views taken while turning faster don't vote (go2_dashboard.py)
VIEW_DT = 0.5                    # s between views (the console maps at 2 Hz)
VOXEL = 0.05                     # the dog's voxel size; voxel centres sit at (k + 0.5) * VOXEL
CROP = 4.0                       # m: box around the dog kept when reading the bag (the dog's window is ~3.2)
R_MAP = 2.75                     # m: only points this close to the dog vote (fresh, well placed)
R_LAYER, R_CLEAR = 2.5, 2.0      # m: layer hits / layer clearing (floor seen, band empty) within this range
LAYER_WIN = 2.0                  # s: a layer cell counts once per window of this length...
LAYER_PASSES = 3                 # ...and needs this many windows (net of clears) to be kept
# heading evidence: every MEAS_STEP s, the voxels the dog placed in the last MEAS_AGE s near itself
ANG_STEP = 0.5
ANG = np.arange(-45, 45, ANG_STEP)  # deg: candidate wall angles mod 90
MEAS_STEP, MEAS_AGE = 1.0, 15.0  # s
MEAS_BAND = (0.20, 1.30)         # m above floor (the dog's voxel map stops at ~1.3 m)
MEAS_R = 3.5                     # m from the dog
MEAS_MIN_CELLS = 80
EVID_K = 2.0                     # nats between a window's best angle and its median angle (before confidence)
# drift model: phi(t) = phi0 + SCALE * (odom yaw turned since start, signed) + BIAS * minutes, then a slow
# residual tracked through the evidence (random walk per second and per degree turned)
SCALE_RANGE = (-0.06, 0.06, 0.001)    # deg error per deg turned (7-14 deg per 360 = 0.02-0.04)
BIAS_RANGE = (-4.0, 4.0, 0.05)        # deg/min
RES_MAX, RES_SIGMA = 12.0, 5.0        # deg: residual range and its weak prior
Q_TIME, Q_TURN = 0.05, 0.02           # deg^2/s, deg^2/deg
HOST_UID = 1000


def wrap90(a):
    """degrees -> (-45, 45]"""
    return (a + 45.0) % 90.0 - 45.0


# ---------------------------------------------------------------- stage 1: read the bag (ROS image only)
def extract(bag, cache):
    """/odom (t, x, y, z, yaw) and the part of every /point_cloud2 within CROP of the dog -> one npz."""
    import rosbag2_py
    from nav_msgs.msg import Odometry
    from rclpy.serialization import deserialize_message
    from sensor_msgs.msg import PointCloud2
    from sensor_msgs_py import point_cloud2
    r = rosbag2_py.SequentialReader()
    r.open(rosbag2_py.StorageOptions(uri=bag, storage_id="sqlite3"), rosbag2_py.ConverterOptions("cdr", "cdr"))
    r.set_filter(rosbag2_py.StorageFilter(topics=["/odom", "/point_cloud2"]))
    od, ct, chunks, last = [], [], [], None
    while r.has_next():
        topic, data, t = r.read_next()
        if topic == "/odom":
            m = deserialize_message(data, Odometry)
            p, q = m.pose.pose.position, m.pose.pose.orientation
            yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            last = (t * 1e-9, p.x, p.y, p.z, yaw)
            od.append(last)
        elif last is not None:
            m = deserialize_message(data, PointCloud2)
            pts = point_cloud2.read_points_numpy(m, field_names=("x", "y", "z"), skip_nans=True)
            near = pts[(np.abs(pts[:, 0] - last[1]) < CROP) & (np.abs(pts[:, 1] - last[2]) < CROP)]
            ct.append(t * 1e-9)
            chunks.append(near.astype(np.float32))
    np.savez(cache, odom=np.array(od), ct=np.array(ct), off=np.cumsum([0] + [len(c) for c in chunks]),
             pts=np.concatenate(chunks))


# ---------------------------------------------------------------- helpers
def manhattan(P, binm=0.1, step=0.5):
    """Dominant direction mod 90 of 2D points (deg in [-45, 45)) and a confidence: the angle whose x and
    y projection histograms are sharpest (sum of squared bin counts), relative to the median angle."""
    if len(P) < 50:
        return np.nan, 0.0
    P = P - P.mean(0)
    angs = np.arange(-45, 45, step)
    sc = np.empty(len(angs))
    for i, a in enumerate(np.radians(angs)):
        c, s = math.cos(a), math.sin(a)
        u = np.floor((c * P[:, 0] + s * P[:, 1]) / binm).astype(np.int64)
        v = np.floor((-s * P[:, 0] + c * P[:, 1]) / binm).astype(np.int64)
        sc[i] = ((np.bincount(u - u.min()) ** 2).sum() + (np.bincount(v - v.min()) ** 2).sum()) / len(P)
    k = int(sc.argmax())
    y0, y1, y2 = sc[k - 1], sc[k], sc[(k + 1) % len(sc)]          # parabolic refinement
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) < 0 else 0.0
    return wrap90(angs[k] + d * step), float(sc[k] / np.median(sc) - 1)


def occ_points(score, jitter=True):
    """map-frame centres of occupied cells (jittered within the cell, so the grid's own axes don't win)."""
    r, c = np.nonzero(score >= OCC_SCORE)
    P = np.c_[c, r].astype(np.float64) + 0.5
    if jitter:
        P += np.random.default_rng(1).uniform(-0.5, 0.5, P.shape)
    return P * RES


def wall_stats(score, seen):
    """How Manhattan and how crisp a map is. theta: dominant wall angle mod 90 (map frame). Then, against it:
    line segments (OpenCV LSD on the occupied cells, x4 upsampled): length-weighted median |deviation| from
    the nearest Manhattan direction and the share of length within 2 / 5 deg; edge orientation (structure
    tensor, sigma 1.5 cells, on occupied-cell boundaries): coherence-weighted median |deviation|; sharpness:
    nats per occupied cell gained by projecting on the best axes vs a typical angle (crisper = higher);
    occupied cells, and occupied per seen cell (thinner walls = lower)."""
    import cv2
    P = occ_points(score)
    theta = manhattan(P)[0]
    L = projection_loglik(P, ANG)
    occ = (score >= OCC_SCORE).astype(np.uint8) * 255
    big = cv2.GaussianBlur(cv2.resize(occ, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), (0, 0), 2)
    seg = cv2.createLineSegmentDetector().detect(big)[0]
    seg = np.zeros((0, 4)) if seg is None else seg[:, 0].astype(float)
    ln = np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1])
    seg, ln = seg[ln > 4 * 8], ln[ln > 4 * 8]                          # segments of 40 cm or more
    dev = np.abs(wrap90(np.degrees(np.arctan2(seg[:, 3] - seg[:, 1], seg[:, 2] - seg[:, 0])) - theta))   # rows = +y
    def wmed(v, w):
        o = np.argsort(v)
        cw = np.cumsum(w[o])
        return float(v[o][np.searchsorted(cw, cw[-1] / 2)]) if len(v) else float("nan")
    f = cv2.GaussianBlur(occ.astype(np.float32) / 255, (0, 0), 1.0)
    gx, gy = cv2.Sobel(f, cv2.CV_32F, 1, 0), cv2.Sobel(f, cv2.CV_32F, 0, 1)
    jxx, jyy, jxy = (cv2.GaussianBlur(v, (0, 0), 1.5) for v in (gx * gx, gy * gy, gx * gy))
    edge = (cv2.dilate(occ, np.ones((3, 3), np.uint8)) > 0) & (occ == 0)
    ori = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy))[edge]        # gradient direction (normal to the wall)
    coh = (np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-9))[edge]
    edev = np.abs(wrap90(ori - theta))
    # local wall angle in 2.5 m tiles vs the global one: are the walls perpendicular everywhere?
    tdev, tw = [], []
    ij = np.floor(P / 2.5).astype(np.int64)
    for key in np.unique(ij, axis=0):
        q = P[(ij == key).all(1)]
        if len(q) >= 60:
            a_, c_ = manhattan(q)
            tdev.append(abs(wrap90(a_ - theta)))
            tw.append(len(q) * max(c_, 0))
    tdev, tw = np.array(tdev), np.array(tw)
    return {"theta_deg": round(float(theta), 2),
            "tiles": int(len(tdev)), "tile_median_abs_dev_deg": round(wmed(tdev, tw), 2),
            "tile_within_3deg": round(float(tw[tdev < 3].sum() / max(tw.sum(), 1e-9)), 3),
            "segments": int(len(ln)), "seg_median_abs_dev_deg": round(wmed(dev, ln), 2),
            "seg_len_within_2deg": round(float(ln[dev < 2].sum() / max(ln.sum(), 1)), 3),
            "seg_len_within_5deg": round(float(ln[dev < 5].sum() / max(ln.sum(), 1)), 3),
            "edge_median_abs_dev_deg": round(wmed(edev, coh), 2),
            "sharpness_nats_per_cell": round(float((L.max() - np.median(L)) / len(P)), 3),
            "occupied_cells": int(len(P)), "seen_cells": int(seen.sum()),
            "occupied_per_seen": round(len(P) / max(int(seen.sum()), 1), 3)}


# ---------------------------------------------------------------- stage 2: the correction
def voxel_births(pts, off):
    """For every point: index of the first cloud in which its voxel appeared (the time the dog placed it)."""
    n = len(off) - 1
    idx = np.repeat(np.arange(n, dtype=np.int32), np.diff(off))
    k = np.floor(pts / VOXEL).astype(np.int64)          # floor, not round: centres are at half-voxels
    key = (k[:, 0] + 2 ** 20) * 2 ** 42 + (k[:, 1] + 2 ** 20) * 2 ** 21 + (k[:, 2] + 2 ** 20)
    del k
    _, fi, inv = np.unique(key, return_index=True, return_inverse=True)
    return idx, idx[fi][inv].astype(np.int32)


def heading_evidence(pts, off, ct, birth, rx, ry, floor, ot, oyaw):
    """Per window: (t, mean placement time, cells, confidence, best angle) and a log-likelihood curve over
    ANG for the angle mod 90 (odom frame) of the structure the dog placed in the last MEAS_AGE seconds within
    MEAS_R of itself. Columns (x, y voxels) count once and are jittered so the voxel grid's axes don't win."""
    rng = np.random.default_rng(0)
    steps = np.arange(ct[0] + MEAS_AGE / 2, ct[-1], MEAS_STEP)
    info = np.full((len(steps), 5), np.nan)
    ll = np.zeros((len(steps), len(ANG)))
    for k, t in enumerate(steps):
        i = min(np.searchsorted(ct, t), len(ct) - 1)
        p, b = pts[off[i]:off[i + 1]], birth[off[i]:off[i + 1]]
        h = p[:, 2] - floor[i]
        s = ((h > MEAS_BAND[0]) & (h < MEAS_BAND[1]) & (ct[i] - ct[b] < MEAS_AGE)
             & (np.hypot(p[:, 0] - rx[i], p[:, 1] - ry[i]) < MEAS_R))
        col, first = np.unique(np.floor(p[s, :2] / VOXEL).astype(np.int64), axis=0, return_index=True)
        info[k, :3] = (ct[i], ct[b[s]].mean() if s.any() else ct[i], len(col))
        if len(col) < MEAS_MIN_CELLS:
            continue
        P = (col + 0.5) * VOXEL + rng.uniform(-VOXEL / 2, VOXEL / 2, col.shape)
        L = projection_loglik(P, ANG)
        span = L.max() - np.median(L)
        conf = min(1.0, span / len(P) / 0.3)            # nats per point gained at the best angle
        ll[k] = EVID_K * conf * (L - L.max()) / max(span, 1e-9)
        info[k, 3:] = (conf, ANG[L.argmax()])
    return info, ll


def projection_loglik(P, angs, binm=0.1):
    """Log-likelihood of 2D points under "they lie on lines along angle a and a+90", for each angle a:
    sum over the x and y projection histograms of c*log(c/n) (sharper histograms = higher)."""
    P = P - P.mean(0)
    out = np.empty(len(angs))
    for i, a in enumerate(np.radians(angs)):
        c, s = math.cos(a), math.sin(a)
        tot = 0.0
        for w in (c * P[:, 0] + s * P[:, 1], -s * P[:, 0] + c * P[:, 1]):
            h = np.bincount(np.floor((w - w.min()) / binm).astype(np.int64))
            h = h[h > 0]
            tot += (h * np.log(h / len(P))).sum()
        out[i] = tot
    return out


def fit_drift(info, ot, oyaw):
    """Robust grid search for phi0, SCALE (gyro scale error) and BIAS (deg/min) such that the windows' best
    angles mod 90 sit on phi0 + SCALE*yaw_turned + BIAS*minutes; each window is compared at the mean time
    its voxels were placed."""
    ok = ~np.isnan(info[:, 4])
    tb, conf, ang = info[ok, 1], info[ok, 3], info[ok, 4]
    yw = np.degrees(np.interp(tb, ot, oyaw) - oyaw[0])
    tm = (tb - ot[0]) / 60
    best = None
    for sc in np.arange(*SCALE_RANGE):
        for bi in np.arange(*BIAS_RANGE):
            r = ang - sc * yw - bi * tm
            p0 = math.degrees(math.atan2((conf * np.sin(np.radians(4 * r))).sum(), (conf * np.cos(np.radians(4 * r))).sum())) / 4
            e = wrap90(r - p0)
            score = (conf * np.exp(-0.5 * (e / 2.5) ** 2)).sum()
            if best is None or score > best[0]:
                best = (score, sc, bi, p0)
    _, sc, bi, p0 = best
    e = wrap90(ang - sc * yw - bi * tm - p0)
    return {"phi0": p0, "scale": sc, "bias_deg_min": bi, "inliers_3deg": float((np.abs(e) < 3).mean()),
            "median_abs_resid": float(np.median(np.abs(e)))}


def drift_model(fit, t, ot, oyaw):
    return fit["phi0"] + fit["scale"] * np.degrees(np.interp(t, ot, oyaw) - oyaw[0]) + fit["bias_deg_min"] * (t - ot[0]) / 60


def track_residual(info, ll, fit, ot, oyaw):
    """Viterbi over the residual phi - model (RES grid) through the windows' likelihood curves, so slow
    departures from the drift model (and the model's own error) are followed. Returns (t, phi) on the
    windows' mean placement times."""
    R = np.arange(-RES_MAX, RES_MAX + 1e-9, ANG_STEP)
    tb = info[:, 1]
    o = np.argsort(tb)
    tb, llo = tb[o], ll[o]
    model = drift_model(fit, tb, ot, oyaw)
    yaw_t = np.interp(tb, ot, oyaw)
    prior = -0.5 * (R / RES_SIGMA) ** 2
    em = np.array([np.interp(wrap90(model[k] + R), ANG, llo[k], period=90) for k in range(len(tb))]) + prior
    D = R[None, :] - R[:, None]
    score, back = em[0].copy(), np.zeros((len(tb), len(R)), np.int32)
    for k in range(1, len(tb)):
        q = Q_TIME * max(tb[k] - tb[k - 1], 0.05) + Q_TURN * abs(math.degrees(yaw_t[k] - yaw_t[k - 1]))
        tot = score[:, None] - 0.5 * D ** 2 / q
        back[k] = tot.argmax(0)
        score = tot.max(0) + em[k]
    path = np.zeros(len(tb), np.int64)
    path[-1] = score.argmax()
    for k in range(len(tb) - 1, 0, -1):
        path[k - 1] = back[k, path[k]]
    res = np.convolve(np.pad(R[path], 5, mode="edge"), np.ones(11) / 11, "valid")   # +-5 windows
    keep = np.r_[True, np.diff(tb) > 1e-3]
    return tb[keep], (model + res)[keep], model[keep]


def corrected_poses(ot, ox, oy, oyaw, tg, phi):
    """delta(t) = phi(t) - phi(start); odom increments rotated by -delta, integrated from the start pose."""
    delta = np.radians(np.interp(ot, tg, phi - phi[0]))
    dm = 0.5 * (delta[1:] + delta[:-1])
    dx, dy = np.diff(ox), np.diff(oy)
    cx = ox[0] + np.r_[0, np.cumsum(np.cos(-dm) * dx - np.sin(-dm) * dy)]
    cy = oy[0] + np.r_[0, np.cumsum(np.sin(-dm) * dx + np.cos(-dm) * dy)]
    return cx, cy, oyaw - delta, delta


# ---------------------------------------------------------------- stage 3: rebuild the grid
class Grid:
    def __init__(self, origin):
        self.origin = np.array(origin, float)
        self.score = np.zeros((SIZE, SIZE), np.int8)
        self.seen = np.zeros((SIZE, SIZE), bool)
        self.ceil = np.full((SIZE, SIZE), np.nan, np.float32)
        self.hits = {"mid": np.zeros((SIZE, SIZE), np.int16), "high": np.zeros((SIZE, SIZE), np.int16)}
        self.clears = {"mid": np.zeros((SIZE, SIZE), np.int16), "high": np.zeros((SIZE, SIZE), np.int16)}
        self._new_window()

    def _new_window(self):
        self.w_band = {"mid": np.zeros((SIZE, SIZE), bool), "high": np.zeros((SIZE, SIZE), bool)}
        self.w_floor = np.zeros((SIZE, SIZE), bool)

    def cells(self, xy):
        """map-frame points (N,2) -> unique in-bounds cell indices (rows, cols), as Mapper.cells."""
        ij = np.floor((xy - self.origin) / RES).astype(np.int64)
        ok = (ij[:, 0] >= 0) & (ij[:, 0] < SIZE) & (ij[:, 1] >= 0) & (ij[:, 1] < SIZE)
        ij = np.unique(ij[ok], axis=0)
        return ij[:, 1], ij[:, 0]

    def add_view(self, xy, h, r):
        """xy: map-frame points near the dog, h: height above floor, r: distance from the dog.
        Same votes as Mapper.add_cloud for score/seen/ceil; layer evidence collected per window."""
        obs, flat = (h > MIN_H) & (h < MAX_H), h <= MIN_H
        orr, oc = self.cells(xy[obs])
        fr, fc = self.cells(xy[flat])
        keep = ~np.isin(fr * SIZE + fc, orr * SIZE + oc)
        fr, fc = fr[keep], fc[keep]
        self.score[orr, oc] = np.minimum(self.score[orr, oc] + 1, SCORE_CAP)
        self.score[fr, fc] = np.maximum(self.score[fr, fc] - 1, -SCORE_CAP)
        self.seen[orr, oc] = True
        self.seen[fr, fc] = True
        for name, (lo, hi) in (("mid", MID_H), ("high", HIGH_H)):
            rr, cc = self.cells(xy[(h > lo) & (h < hi) & (r < R_LAYER)])
            self.w_band[name][rr, cc] = True
        rr, cc = self.cells(xy[flat & (r < R_CLEAR)])
        self.w_floor[rr, cc] = True
        up = h >= CEIL_MIN_H
        if up.any():
            ij = np.floor((xy[up] - self.origin) / RES).astype(np.int64)
            ok = (ij[:, 0] >= 0) & (ij[:, 0] < SIZE) & (ij[:, 1] >= 0) & (ij[:, 1] < SIZE)
            low = np.full((SIZE, SIZE), np.inf, np.float32)
            np.minimum.at(low, (ij[ok, 1], ij[ok, 0]), h[up][ok].astype(np.float32))
            rr, cc = np.nonzero(np.isfinite(low))
            old = self.ceil[rr, cc]
            self.ceil[rr, cc] = np.where(np.isnan(old), low[rr, cc], 0.8 * old + 0.2 * low[rr, cc])

    def end_window(self):
        """A layer cell gets +1 if its band had points in this window, else a clear if its floor was seen."""
        for name in ("mid", "high"):
            self.hits[name] += self.w_band[name]
            self.clears[name] += self.w_floor & ~self.w_band[name]
        self._new_window()

    def layer(self, name):
        net = self.hits[name].astype(np.int32) - self.clears[name]
        return np.where(net >= LAYER_PASSES, np.minimum(net, 50), 0).astype(np.uint8)


def rebuild(pts, off, ct, birth, floor, ot, ox, oy, cx, cy, delta, T, origin, turn_rate):
    """Re-place each view's points with the pose at their voxel's first appearance and vote them."""
    th = T[2]
    Rm = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    # pose of the dog at each cloud: odom position, corrected position, heading error
    po = np.c_[np.interp(ct, ot, ox), np.interp(ct, ot, oy)]
    pc = np.c_[np.interp(ct, ot, cx), np.interp(ct, ot, cy)]
    dl = np.interp(ct, ot, delta)
    g = Grid(origin)
    last_t, win = -1e9, None
    views = 0
    for i in range(len(ct)):
        if ct[i] - last_t < VIEW_DT or off[i + 1] == off[i]:
            continue
        w = int((ct[i] - ct[0]) // LAYER_WIN)
        if win is not None and w != win:
            g.end_window()
        win = w
        if abs(np.interp(ct[i], ot, turn_rate)) >= MAP_MAX_TURN:
            continue
        last_t = ct[i]
        p = pts[off[i]:off[i + 1]]
        r = np.hypot(p[:, 0] - po[i, 0], p[:, 1] - po[i, 1])
        s = r < R_MAP
        p, r, b = p[s], r[s], birth[off[i]:off[i + 1]][s]
        # rotate about where the dog was when the voxel was placed, by minus the heading error then
        d = p[:, :2] - po[b]
        c, sn = np.cos(-dl[b]), np.sin(-dl[b])
        q = pc[b] + np.c_[c * d[:, 0] - sn * d[:, 1], sn * d[:, 0] + c * d[:, 1]]
        g.add_view(q @ Rm.T + T[:2], p[:, 2] - floor[i], r)
        views += 1
    g.end_window()
    return g, views


# ---------------------------------------------------------------- pictures
def pictures(pics, old, new, origin, theta_old, theta_new, tg, phi, model, info, ot, turns, traj):
    import cv2
    os.makedirs(pics, exist_ok=True)
    known = np.argwhere(old["seen"] | new["seen"])
    (r0, c0), (r1, c1) = known.min(0) - 15, known.max(0) + 16

    def grid_img(d, theta, color):
        img = np.full((SIZE, SIZE), 205, np.uint8)
        img[d["seen"]] = 254
        img[d["score"] >= OCC_SCORE] = 0
        img = cv2.cvtColor(img[r0:r1, c0:c1][::-1], cv2.COLOR_GRAY2BGR)
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        H, W = img.shape[:2]
        # Manhattan grid at the map's own dominant angle, lines every 1 m
        for a in (theta, theta + 90):
            u = np.array([math.cos(math.radians(a)), -math.sin(math.radians(a))])   # image y is flipped
            nrm = np.array([-u[1], u[0]])
            for k in range(-40, 41):
                p0 = np.array([W / 2, H / 2]) + nrm * k * 60   # 1 m = 20 cells * 3 px
                p1, p2 = p0 - u * 3000, p0 + u * 3000
                cv2.line(img, tuple(int(v) for v in p1), tuple(int(v) for v in p2), color, 1, cv2.LINE_AA)
        return img

    a = grid_img(old, theta_old, (60, 160, 255))
    b = grid_img(new, theta_new, (90, 200, 90))
    if traj is not None:
        for (xs, ys), col in zip(traj, ((255, 120, 0), (200, 0, 200))):
            px = ((np.asarray(xs) - origin[0]) / RES - c0) * 3
            py = ((r1 - r0) - ((np.asarray(ys) - origin[1]) / RES - r0)) * 3
            tgt = b if col == (200, 0, 200) else a
            cv2.polylines(tgt, [np.c_[px, py].astype(np.int32)], False, col, 1, cv2.LINE_AA)
    for img, txt in ((a, f"before  (walls {theta_old:.1f} deg mod 90)"), (b, f"after  (walls {theta_new:.1f} deg mod 90)")):
        cv2.putText(img, txt, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imwrite(os.path.join(pics, "maps_before_after.png"), np.hstack([a, np.full((a.shape[0], 10, 3), 255, np.uint8), b]))

    # delta(t) plot
    W, H, L, B = 1400, 520, 60, 40
    img = np.full((H, W, 3), 255, np.uint8)
    t0, t1 = ot[0], ot[-1]
    lo, hi = -15.0, 40.0
    X = lambda t: (L + (np.asarray(t) - t0) / (t1 - t0) * (W - L - 20)).astype(int)
    Y = lambda v: (H - B - (np.asarray(v) - lo) / (hi - lo) * (H - B - 20)).astype(int)
    for v in range(int(lo), int(hi) + 1, 5):
        cv2.line(img, (L, int(Y(v))), (W - 20, int(Y(v))), (230, 230, 230), 1)
        cv2.putText(img, f"{v}", (10, int(Y(v)) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    for s in range(0, int(t1 - t0) + 1, 60):
        cv2.putText(img, f"{s // 60}m", (int(X(t0 + s)) - 8, H - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    for ta, tb, ang in turns:      # turns in place: shaded, with the angle turned
        cv2.rectangle(img, (int(X(ta)), 20), (max(int(X(tb)), int(X(ta)) + 1), H - B), (255, 225, 200), -1)
        cv2.putText(img, f"{ang:+.0f}", (int(X(ta)), 32), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (150, 80, 0), 1)
    phi0 = phi[0]
    for t, conf, ang in info[~np.isnan(info[:, 4])][:, [1, 3, 4]]:     # each window's best angle, nearest copy
        v = ang + 90 * np.round((np.interp(t, tg, phi) - ang) / 90) - phi0
        cv2.circle(img, (int(X(t)), int(Y(v))), 1 + int(3 * conf), (120, 120, 120), -1, cv2.LINE_AA)
    cv2.polylines(img, [np.c_[X(tg), Y(model - phi0)].astype(np.int32)], False, (0, 170, 0), 1, cv2.LINE_AA)
    cv2.polylines(img, [np.c_[X(tg), Y(phi - phi0)].astype(np.int32)], False, (0, 0, 210), 2, cv2.LINE_AA)
    cv2.putText(img, "heading error delta(t) [deg] vs drive time.  grey: best angle of each window (size = confidence);  "
                "green: drift model;  red: tracked;  blue bands: turns in place (deg)", (L, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)
    cv2.imwrite(os.path.join(pics, "delta.png"), img)

    def mid_img(m, seen):
        img = np.full((SIZE, SIZE, 3), 255, np.uint8)
        img[seen] = (235, 235, 235)
        img[m >= 2] = (0, 110, 230)
        img = img[r0:r1, c0:c1][::-1]
        return cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    a, b = mid_img(old["mid"], old["seen"]), mid_img(new["mid"], new["seen"])
    cv2.putText(a, "old mid layer (0.6-1.2 m)", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(b, "new mid layer", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.imwrite(os.path.join(pics, "mid_before_after.png"), np.hstack([a, np.full((a.shape[0], 10, 3), 255, np.uint8), b]))


# ---------------------------------------------------------------- main
def turn_intervals(ot, oyaw, rate):
    """(start, end, deg turned) of turns in place: yaw rate above 0.3 rad/s, merged when < 1 s apart."""
    fast = np.abs(rate) > 0.3
    out = []
    k = 0
    while k < len(ot):
        if fast[k]:
            j = k
            while j + 1 < len(ot) and (fast[j + 1] or (ot[min(j + 20, len(ot) - 1)] - ot[j] < 1.0 and fast[j + 1:j + 20].any())):
                j += 1
            ang = math.degrees(oyaw[j] - oyaw[k])
            if abs(ang) > 30:
                out.append((ot[k], ot[j], ang))
            k = j + 1
        else:
            k += 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bag", help="recording directory (only needed when the cache doesn't exist)")
    ap.add_argument("--cache", required=True, help="npz of odom + near clouds (made from --bag if missing)")
    ap.add_argument("--maps", default="/home/nesl/oliver/go2_maps")
    ap.add_argument("--name", default="lab")
    ap.add_argument("--poselog", default=None, help="pose log jsonl (default: <maps>/<name>_poselog/<day>.jsonl)")
    ap.add_argument("--out", default=None, help="default: <maps>/<name>_straightened.grid.npz")
    ap.add_argument("--pics", default=None)
    ap.add_argument("--no-correction", action="store_true", help="rebuild with the logged poses (for comparison)")
    a = ap.parse_args()
    if not os.path.exists(a.cache):
        extract(a.bag, a.cache)
    d = np.load(a.cache)
    pts, off, ct, od = d["pts"], d["off"], d["ct"], d["odom"]
    ot, ox, oy, oyaw = od[:, 0], od[:, 1], od[:, 2], np.unwrap(od[:, 4])
    k = np.r_[True, np.diff(ot) > 1e-4]                       # drop duplicate stamps before differentiating
    ot, ox, oy, oyaw = ot[k], ox[k], oy[k], oyaw[k]
    # yaw rate over +-0.25 s (bag receive times jitter too much to differentiate sample to sample)
    rate = (np.interp(ot + 0.25, ot, oyaw) - np.interp(ot - 0.25, ot, oyaw)) / 0.5
    old = dict(np.load(os.path.join(a.maps, a.name + ".grid.npz")))

    # map <- odom transform from the pose log while mapping (go2_dashboard.log_pose)
    day = __import__("time").strftime("%Y%m%d", __import__("time").localtime(ct[0]))
    log = a.poselog or os.path.join(a.maps, f"{a.name}_poselog", day + ".jsonl")
    L = [json.loads(s) for s in open(log)]
    L = [x for x in L if x["mapping"] and x["T"] and ot[0] - 1 <= x["t"] <= ot[-1] + 1]
    Ts = np.array([x["T"] for x in L])
    if np.ptp(Ts, axis=0).max() > 1e-6:
        print("note: T changed while mapping; using the first value (the start line-up)")
    T = Ts[0]

    # 1. room axis of the current map
    theta_room = manhattan(occ_points(old["score"]))[0]
    print(f"room axis of the current map: {theta_room:.2f} deg (mod 90), map frame")

    # 2. heading error over time
    n = len(off) - 1
    floor = np.array([np.percentile(pts[off[i]:off[i + 1], 2], 20) if off[i + 1] > off[i] else np.nan for i in range(n)])
    floor = np.where(np.isnan(floor), np.nanmedian(floor), floor)
    _, birth = voxel_births(pts, off)
    rx, ry = np.interp(ct, ot, ox), np.interp(ct, ot, oy)
    info, ll = heading_evidence(pts, off, ct, birth, rx, ry, floor, ot, oyaw)
    fit = fit_drift(info, ot, oyaw)
    print(f"evidence windows: {len(info)}, usable {(~np.isnan(info[:, 4])).sum()}; drift model: "
          f"{fit['scale'] * 360:.1f} deg per 360 deg turned, {fit['bias_deg_min']:.2f} deg/min, "
          f"{100 * fit['inliers_3deg']:.0f}% of windows within 3 deg (median {fit['median_abs_resid']:.1f})")
    tg, phi, model = track_residual(info, ll, fit, ot, oyaw)
    if a.no_correction:
        phi = np.zeros_like(phi)
    phi_map = phi + math.degrees(T[2])
    print(f"walls at the start: {wrap90(phi_map[0]):.2f} deg in the map frame (room axis of the current map "
          f"{theta_room:.2f}); correction (anchored at start) ranges {np.min(phi - phi[0]):.1f}..{np.max(phi - phi[0]):.1f} deg")

    # 3. corrected trajectory
    cx, cy, cyaw, delta = corrected_poses(ot, ox, oy, oyaw, tg, phi)
    print(f"end of drive moved by {math.hypot(cx[-1] - ox[-1], cy[-1] - oy[-1]):.2f} m, turned {math.degrees(delta[-1]):.1f} deg")

    # places (map frame): move each by how the dog's own track moved where it passed nearest (the map stays
    # anchored at the start, so places near the start barely move)
    th = T[2]
    c, s_ = math.cos(th), math.sin(th)
    oldx, oldy = T[0] + c * ox - s_ * oy, T[1] + s_ * ox + c * oy
    newx, newy = T[0] + c * cx - s_ * cy, T[1] + s_ * cx + c * cy
    places_path = os.path.join(a.maps, a.name + ".places.json")
    moved = {}
    if os.path.exists(places_path):
        places = json.load(open(places_path))
        for k, pl in places.items():
            dist = np.hypot(oldx - pl["x"], oldy - pl["y"])
            near = dist < max(0.75, dist.min() + 0.25)
            dx, dy = np.median(newx[near] - oldx[near]), np.median(newy[near] - oldy[near])
            dyaw = -math.degrees(np.median(delta[near]))
            moved[k] = {"dx": round(float(dx), 3), "dy": round(float(dy), 3), "dyaw_deg": round(dyaw, 1),
                        "track_dist_m": round(float(dist.min()), 2)}
            pl["x"], pl["y"] = round(pl["x"] + dx, 3), round(pl["y"] + dy, 3)
            pl["yaw_deg"] = round((pl["yaw_deg"] + dyaw + 180) % 360 - 180, 1)
            if pl.get("target"):
                pl["target"] = {"x": round(pl["target"]["x"] + dx, 3), "y": round(pl["target"]["y"] + dy, 3)}
        print("places moved:", {k: (round(math.hypot(v["dx"], v["dy"]), 2), v["dyaw_deg"]) for k, v in moved.items()})

    # 4. rebuild
    g, views = rebuild(pts, off, ct, birth, floor, ot, ox, oy, cx, cy, delta, T, old["origin"], rate)
    new = {"score": g.score, "seen": g.seen, "origin": old["origin"], "mid": g.layer("mid"), "high": g.layer("high"),
           "ceil": g.ceil}
    # the frame info (alignment + dog pose at save): kept as the console wrote it
    if "T" in old:
        new["T"] = old["T"]
    if "odom" in old:
        new["odom"] = old["odom"]
    print(f"{views} views voted; mid cells by net passes:",
          {k: int(((g.hits["mid"].astype(int) - g.clears["mid"]) >= k).sum()) for k in (1, 2, 3, 5, 10)},
          "hits-only >=3:", int((g.hits["mid"] >= 3).sum()))

    # 5. numbers
    before = wall_stats(old["score"], old["seen"])
    after = wall_stats(new["score"], new["seen"])
    for nm, dd, st in (("before", old, before), ("after", new, after)):
        st["mid_cells"] = int((dd["mid"] >= 2).sum())
        st["high_cells"] = int((dd["high"] >= 2).sum())
        print(nm, st)
    out = a.out or os.path.join(a.maps, a.name + "_straightened.grid.npz")
    np.savez_compressed(out, **new)
    try:
        os.chown(out, HOST_UID, HOST_UID)
    except PermissionError:
        pass
    with open(os.path.splitext(out)[0].replace(".grid", "") + ".info.json", "w") as f:
        json.dump({"source": a.cache, "T": [float(v) for v in T], "theta_room_current_map_deg": round(float(theta_room), 2),
                   "walls_after_deg": after["theta_deg"], "frame": "same map frame as lab.grid.npz (anchored at the start pose)",
                   "delta_deg": {"t": [round(float(t - ot[0]), 2) for t in tg[::4]],
                                 "delta": [round(float(v), 2) for v in (phi - phi[0])[::4]]},
                   "drift_model": fit, "places_moved": moved, "before": before, "after": after}, f, indent=1)
    try:
        os.chown(os.path.splitext(out)[0].replace(".grid", "") + ".info.json", HOST_UID, HOST_UID)
    except PermissionError:
        pass
    if moved and not a.no_correction:
        ppath = os.path.splitext(out)[0].replace(".grid", "") + ".places.json"
        with open(ppath, "w") as f:
            json.dump(places, f, indent=1)
        try:
            os.chown(ppath, HOST_UID, HOST_UID)
        except PermissionError:
            pass
    if a.pics:
        turns = turn_intervals(ot, oyaw, rate)
        pictures(a.pics, old, new, old["origin"], before["theta_deg"], after["theta_deg"], tg, phi, model, info, ot,
                 turns, ((oldx, oldy), (newx, newy)))
        print(f"{len(turns)} turns in place; pictures in {a.pics}")


if __name__ == "__main__":
    main()
