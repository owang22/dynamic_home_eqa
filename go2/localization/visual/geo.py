"""Local-feature matching and relative pose between two pictures (task 3).

SIFT (OpenCV) on the 640x360 grey picture, cached per picture in cache/sift/<id>.npz (pts in pixels, desc).
match(a, b, region): ratio-test matches (0.8, mutual), optionally only keypoints with row < row_max in BOTH pictures;
undistort with the 720p calibration (scaled), essential matrix (RANSAC, 1.5 px), recoverPose.
Returns n_inliers, relative yaw (deg, + = picture b's camera is turned LEFT of a's, same sign as map yaw),
and the horizontal direction of b's camera centre seen from a (angle in a's camera frame, + = to the left).
"""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

import vcommon as V

HERE = Path(__file__).resolve().parent
SIFT_DIR = HERE / "cache" / "sift"
SIFT_DIR.mkdir(parents=True, exist_ok=True)
K = V.K_for(640, 360)
_sift = None
_cache = {}


def feats(rec):
    pid = rec["id"]
    if pid in _cache:
        return _cache[pid]
    p = SIFT_DIR / f"{pid}.npz"
    if p.exists():
        z = np.load(p)
        out = (z["pts"], z["desc"])
    else:
        global _sift
        if _sift is None:
            _sift = cv2.SIFT_create(nfeatures=2000, contrastThreshold=0.02)
        im = cv2.imread(rec["path"], cv2.IMREAD_GRAYSCALE)
        im = cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA)
        kp, d = _sift.detectAndCompute(im, None)
        pts = np.array([k.pt for k in kp], np.float32).reshape(-1, 2)
        d = np.zeros((0, 128), np.float32) if d is None else d
        # RootSIFT
        d = np.sqrt(d / (np.abs(d).sum(1, keepdims=True) + 1e-7)).astype(np.float32)
        np.savez(p, pts=pts, desc=d)
        out = (pts, d)
    if len(_cache) > 3000:
        _cache.clear()
    _cache[pid] = out
    return out


_bf = cv2.BFMatcher(cv2.NORM_L2)


def raw_matches(a, b, row_max=None, mask_a=None, mask_b=None):
    pa, da = feats(a); pb, db = feats(b)
    ia = np.arange(len(pa)); ib = np.arange(len(pb))
    if row_max is not None:
        ia = ia[pa[:, 1] < row_max]; ib = ib[pb[:, 1] < row_max]
    if mask_a is not None:
        ia = ia[mask_a[pa[ia, 1].astype(int).clip(0, 359), pa[ia, 0].astype(int).clip(0, 639)]]
    if mask_b is not None:
        ib = ib[mask_b[pb[ib, 1].astype(int).clip(0, 359), pb[ib, 0].astype(int).clip(0, 639)]]
    if len(ia) < 8 or len(ib) < 8:
        return np.zeros((0, 2)), np.zeros((0, 2))
    m = _bf.knnMatch(da[ia], db[ib], k=2)
    good = [x[0] for x in m if len(x) == 2 and x[0].distance < 0.8 * x[1].distance]
    m2 = _bf.match(db[ib], da[ia])
    back = {x.queryIdx: x.trainIdx for x in m2}
    good = [g for g in good if back.get(g.trainIdx) == g.queryIdx]
    A = pa[ia[[g.queryIdx for g in good]]]; B = pb[ib[[g.trainIdx for g in good]]]
    return A, B


def undist(p):
    if len(p) == 0:
        return p
    return cv2.undistortPoints(p.reshape(-1, 1, 2).astype(np.float64), K, V.DIST720).reshape(-1, 2)


def rel_pose(a, b, row_max=None, mask_a=None, mask_b=None, thr_px=1.5):
    A, B = raw_matches(a, b, row_max, mask_a, mask_b)
    out = {"n_match": int(len(A)), "inl": 0, "yaw": float("nan"), "bearing": float("nan"), "rot_only": False}
    if len(A) < 12:
        return out
    na, nb = undist(A), undist(B)
    E, msk = cv2.findEssentialMat(na, nb, np.eye(3), method=cv2.RANSAC, prob=0.999, threshold=thr_px / K[0, 0])
    if E is None or E.shape != (3, 3):
        return out
    n, R, t, msk2 = cv2.recoverPose(E, na, nb, np.eye(3), mask=msk.copy())
    inl = int(msk.sum())
    # rotation-only check: fit a pure rotation homography; if it explains as many inliers the baseline is too
    # small for a reliable translation direction (yaw is still fine)
    H, mh = cv2.findHomography(na, nb, cv2.RANSAC, thr_px / K[0, 0])
    out.update(inl=inl, yaw=math.degrees(math.atan2(R[0, 2], R[2, 2])), n_h=int(mh.sum()) if mh is not None else 0)
    # camera centre of b in a's frame: C_b = -R^T t
    C = -(R.T @ t).ravel()
    out["bearing"] = math.degrees(math.atan2(-C[0], C[2]))     # + = left of a's optical axis
    out["rot_only"] = bool(mh is not None and mh.sum() >= 0.9 * inl)
    out["pitch"] = math.degrees(math.asin(np.clip(-R[1, 2], -1, 1)))
    return out
