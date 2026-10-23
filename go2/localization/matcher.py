"""Correlative scan-to-grid matcher (Olson 2009 style, brute force over yaw, cv2.matchTemplate over x/y).

Reference = a likelihood field on a grid (value 1 at occupied cells, Gaussian fall-off).
Query     = 2D points (cells of one cloud snapshot), given in some frame plus a guess pose.
For each yaw in the search set, the rotated points are rasterised into a template and cross-correlated with
the field over the translation window; the score is the mean field value at the points (0..1).
"""
from __future__ import annotations

import math

import cv2
import numpy as np
from scipy import ndimage


class Field:
    def __init__(self, occ: np.ndarray, res: float, origin_xy, sigma: float = 0.1, known: np.ndarray | None = None):
        """occ: bool (H,W) with row 0 = min y (i.e. y up), origin_xy = world xy of cell (0,0) corner."""
        self.res, self.ox, self.oy = res, float(origin_xy[0]), float(origin_xy[1])
        self.occ = occ.astype(bool)
        dist = ndimage.distance_transform_edt(~self.occ) * res
        self.lf = np.exp(-0.5 * (dist / sigma) ** 2).astype(np.float32)
        self.H, self.W = occ.shape
        self.known = known

    def lookup(self, xy):
        """Bilinear field value (cell values sit at cell centres), 0 outside."""
        fc = (xy[:, 0] - self.ox) / self.res - 0.5
        fr = (xy[:, 1] - self.oy) / self.res - 0.5
        return ndimage.map_coordinates(self.lf, [fr, fc], order=1, mode="constant", cval=0.0)

    def score(self, pts, pose):
        c, s = math.cos(pose[2]), math.sin(pose[2])
        xy = np.stack([pose[0] + c * pts[:, 0] - s * pts[:, 1], pose[1] + s * pts[:, 0] + c * pts[:, 1]], -1)
        return float(self.lookup(xy).mean()) if len(pts) else 0.0


def search(field: Field, pts: np.ndarray, center, yaws, win_xy: float | None, top_k: int = 1, min_sep_deg=10.0,
           min_sep_m=0.5):
    """Search poses T (x, y, yaw) with T*pts on the field.

    pts: (N,2) in the query frame, expressed relative to a pivot at the query-frame origin.
    center: (x,y) world guess of the pivot; win_xy: half window in metres (None = whole map).
    yaws: iterable of candidate yaws (rad).
    Returns per-yaw best list sorted by score: [(score, x, y, yaw)], and the best overall.
    """
    res = field.res
    if len(pts) == 0:
        return []
    results = []
    if win_xy is None:
        r0, r1, c0, c1 = 0, field.H, 0, field.W
    else:
        cc = (center[0] - field.ox) / res
        rr = (center[1] - field.oy) / res
        w = int(math.ceil(win_xy / res))
        c0, c1 = int(math.floor(cc)) - w, int(math.floor(cc)) + w + 1
        r0, r1 = int(math.floor(rr)) - w, int(math.floor(rr)) + w + 1
    for yaw in yaws:
        c, s = math.cos(yaw), math.sin(yaw)
        q = np.stack([c * pts[:, 0] - s * pts[:, 1], s * pts[:, 0] + c * pts[:, 1]], -1)
        qc = np.floor(q[:, 0] / res).astype(int)
        qr = np.floor(q[:, 1] / res).astype(int)
        mc, mr = qc.min(), qr.min()
        th, tw = qr.max() - mr + 1, qc.max() - mc + 1
        tmpl = np.zeros((th, tw), np.float32)
        np.add.at(tmpl, (qr - mr, qc - mc), 1.0)
        # pivot cell p maps template cell (qr-mr, qc-mc) to field cell (p_r + qr, p_c + qc)
        # => template top-left at field (p_r + mr, p_c + mc). Region of field to cover pivot range [r0,r1)x[c0,c1)
        R0, C0 = r0 + mr, c0 + mc
        R1, C1 = (r1 - 1) + mr + th, (c1 - 1) + mc + tw
        pad = max(0, -R0, -C0, R1 - field.H, C1 - field.W)
        lf = field.lf
        if pad:
            lf = np.pad(lf, pad)
        region = lf[R0 + pad:R1 + pad, C0 + pad:C1 + pad]
        if region.shape[0] < th or region.shape[1] < tw:
            continue
        cor = cv2.matchTemplate(region, tmpl, cv2.TM_CCORR) / len(pts)
        results.append((yaw, cor, r0, c0))
    return results


def best_poses(field, results, top_k=5, min_sep_deg=10.0, min_sep_m=0.5):
    """Collapse per-yaw correlation maps into a ranked list of distinct poses (score, x, y, yaw)."""
    cands = []
    for yaw, cor, r0, c0 in results:
        # take a few peaks per yaw
        flat = cor.ravel()
        k = min(5, flat.size)
        idx = np.argpartition(-flat, k - 1)[:k]
        for i in idx:
            r, c = divmod(int(i), cor.shape[1])
            x = field.ox + (c0 + c) * field.res  # pivot on the cell corner (floor convention, see search)
            y = field.oy + (r0 + r) * field.res
            cands.append((float(flat[i]), x, y, float(yaw)))
    cands.sort(key=lambda a: -a[0])
    out = []
    for cnd in cands:
        if all(abs(math.degrees((cnd[3] - o[3] + math.pi) % (2 * math.pi) - math.pi)) > min_sep_deg
               or math.hypot(cnd[1] - o[1], cnd[2] - o[2]) > min_sep_m for o in out):
            out.append(cnd)
        if len(out) >= top_k:
            break
    return out


def match(field, pts, guess, yaw_win_deg, yaw_step_deg, xy_win, refine=True, top_k=5):
    """Search around guess (x,y,yaw). pts in the query frame (pivot = origin). Returns ranked [(score,x,y,yaw)]."""
    if yaw_win_deg >= 180:
        yaws = np.radians(np.arange(-180, 180, yaw_step_deg))
    else:
        yaws = guess[2] + np.radians(np.arange(-yaw_win_deg, yaw_win_deg + 1e-9, yaw_step_deg))
    res = search(field, pts, guess[:2], yaws, xy_win)
    ranked = best_poses(field, res, top_k=top_k)
    if refine and ranked:
        ranked = [refine_pose(field, pts, r) for r in ranked]
        ranked.sort(key=lambda a: -a[0])
    return ranked


def refine_pose(field, pts, cand, steps=((0.025, 0.5), (0.01, 0.2), (0.004, 0.1)), max_xy=0.05, max_deg=1.0):
    """Small hill-climb in x, y (m) and yaw (deg) around a candidate, bounded to +-max_xy / +-max_deg of it
    (unbounded, it could wander out of the search window and defeat the jump gate: v1 bug, 18 deg 'refinements')."""
    s0, x, y, yaw = cand
    x0, y0, yaw0 = x, y, yaw
    best = (field.score(pts, (x, y, yaw)), x, y, yaw)
    for dxy, ddeg in steps:
        improved = True
        while improved:
            improved = False
            for ddx, ddy, dth in ((dxy, 0, 0), (-dxy, 0, 0), (0, dxy, 0), (0, -dxy, 0), (0, 0, ddeg), (0, 0, -ddeg)):
                p = (best[1] + ddx, best[2] + ddy, best[3] + math.radians(dth))
                if abs(p[0] - x0) > max_xy or abs(p[1] - y0) > max_xy or abs(math.degrees(p[2] - yaw0)) > max_deg:
                    continue
                sc = field.score(pts, p)
                if sc > best[0] + 1e-6:
                    best = (sc, *p)
                    improved = True
    return best
