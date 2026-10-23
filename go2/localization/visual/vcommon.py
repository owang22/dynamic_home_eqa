"""Shared helpers for the camera-relocalization study (go2/localization/visual/, 2026-10-23, offline, no dog).

Records: go2/lab_agent/memory.py load() (last record per id wins). Each record gets:
  day ('10-19'/'10-20'/'10-22'), session (event-log name or None), and trust flags from the event logs
  (read-only use of ../cache/<session>.npz written by the lidar study's common.py):
    v_lin, v_ang   odom speed at the frame time (m/s, deg/s), central difference over +-0.5 s
    ev_dt          seconds to the nearest localizer jump / start / hand event (jumps_events.csv)
    dpos_log       distance between the index pose and the event-log map pose at the frame time
  trusted = not (10-19 before 16:54) and ev_dt > 5 s and v_ang < 30 deg/s and dpos_log < 0.3 m (when logged)
Camera: 720p calibration copied from the go2-lab image (front_camera_720.yaml). Pictures are stored at 640x360
(trail) or 1280x720 (some photos); K is scaled to the actual size.
"""
from __future__ import annotations

import csv
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GO2 = HERE.parents[1]
sys.path.insert(0, str(GO2 / "lab_agent"))
sys.path.insert(0, str(HERE.parent))
import memory  # noqa: E402

LCACHE = HERE.parent / "cache"
JUMPS = HERE.parent / "results" / "jumps_events.csv"

K720 = np.array([[864.39938, 0, 639.19798], [0, 863.73849, 373.28118], [0, 0, 1.0]])
DIST720 = np.array([-0.354630, 0.102054, -0.001614, -0.001249, 0.0])
CAM_H = 0.40


# The calibrated focal length under-reads rotations by ~12 % on the stored frames: image-estimated yaw changes
# over 1-4 s are 0.878x odom, and fx*0.90 makes them agree (slope 1.003, results/fx_sweep.json). Odom yaw itself is
# right within ~2 % over full 360-deg turns (results/yaw_scale_check.json). So the effective HFOV is ~79 deg, not 73.
FX_SCALE = 0.90


def K_for(w, h, eff=True):
    s = w / 1280.0
    K = K720.copy()
    K[:2] *= s
    if eff:
        K[0, 0] *= FX_SCALE; K[1, 1] *= FX_SCALE
    return K


def wrap_deg(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def horizon_row(look_deg, h=360, w=640, col=None, eff=False):
    """Image row (in a w x h distorted picture) where a level ray at the camera centre column lands,
    for camera pitch look_deg (positive = camera tilted up -> horizon moves down)."""
    import cv2
    K = K_for(w, h, eff)
    col = K[0, 2] if col is None else col
    th = math.radians(look_deg)
    # level ray in camera coords (x right, y down, z forward) for a camera pitched up by th: y = +tan(th)
    xn = (col - K[0, 2]) / K[0, 0]
    pts = np.array([[[xn, math.tan(th)]]], dtype=np.float64)
    img, _ = cv2.projectPoints(np.array([[xn, math.tan(th), 1.0]]), np.zeros(3), np.zeros(3), K, DIST720)
    return float(img[0, 0, 1])


def elevation_of_row(row, h=360, w=640, look_deg=0.0, eff=False):
    """Elevation angle above level (deg) of the ray through (centre column, row)."""
    import cv2
    K = K_for(w, h, eff)
    p = cv2.undistortPoints(np.array([[[K[0, 2], row]]], dtype=np.float64), K, DIST720)
    yn = p[0, 0, 1]
    return -math.degrees(math.atan(yn)) + look_deg


def _day(r):
    return datetime.fromtimestamp(r["t"]).strftime("%m-%d")


_SESS = None


def _sessions():
    global _SESS
    if _SESS is None:
        _SESS = {}
        for p in sorted(LCACHE.glob("*.npz")):
            z = np.load(p)
            if len(z["t"]):
                _SESS[p.stem] = (z["t"], z["odom"], z["map"])
    return _SESS


def _events():
    ev = []
    if JUMPS.exists():
        for row in csv.DictReader(JUMPS.open()):
            if row["kind"] in ("jump", "start", "hand?", "hand"):
                ev.append(float(row["t"]))
    return np.array(sorted(ev))


def load_records(trust=True):
    R = sorted(memory.load(), key=lambda r: r["t"])
    S = _sessions()
    ev = _events()
    for r in R:
        r["day"] = _day(r)
        t = r["t"]
        r["session"] = None
        r["v_lin"] = r["v_ang"] = r["dpos_log"] = r["dyaw_log"] = float("nan")
        for name, (tt, od, mp) in S.items():
            if tt[0] - 1 <= t <= tt[-1] + 1:
                r["session"] = name
                i0, i1 = np.searchsorted(tt, [t - 0.5, t + 0.5])
                i0, i1 = max(i0, 0), min(i1, len(tt) - 1)
                if i1 > i0 and tt[i1] > tt[i0]:
                    dt = tt[i1] - tt[i0]
                    r["v_lin"] = float(np.hypot(*(od[i1, :2] - od[i0, :2])) / dt)
                    r["v_ang"] = float(abs(math.degrees((od[i1, 3] - od[i0, 3] + math.pi) % (2 * math.pi) - math.pi)) / dt)
                k = int(np.clip(np.searchsorted(tt, t), 0, len(tt) - 1))
                if np.all(np.isfinite(mp[k])):
                    r["dpos_log"] = float(math.hypot(mp[k, 0] - r["x"], mp[k, 1] - r["y"]))
                    r["dyaw_log"] = float(wrap_deg(math.degrees(mp[k, 2]) - r["yaw_deg"]))
                break
        r["ev_dt"] = float(np.min(np.abs(ev - t))) if len(ev) else float("inf")
        bad_early = r["day"] == "10-19" and datetime.fromtimestamp(t).strftime("%H:%M") < "16:54"
        r["trusted"] = bool(not bad_early and r["ev_dt"] > 5.0
                            and not (r["v_ang"] > 30.0)
                            and not (r["dpos_log"] > 0.3))
        r["bad_early"] = bad_early
    # yaw audit (yaw_audit.py): console yaw error estimated from verified picture pairs; suspect if |e| > 20 deg
    au = HERE / "results" / "yaw_audit.json"
    A = __import__("json").load(au.open()) if au.exists() else {}
    for r in R:
        a = A.get(r["id"])
        r["audit_e"] = a["e"] if a and a["n_pairs"] >= 2 else float("nan")
        r["yaw_suspect"] = bool(a and a["suspect"])
    pa = HERE / "results" / "pos_audit.json"
    PA = __import__("json").load(pa.open()) if pa.exists() else {}
    for r in R:
        p = PA.get(r["id"])
        r["pos_suspect"] = bool(p and p["suspect"])
        # 10-22 after the three hand placements at 16:24:02-16:24:38 (jumps_events.csv, 1.8 m / 57 deg): the
        # pictures say the console poses from then on are 1.5-3 m off (pos_audit: 16:3x median 1.5 m; NOTES 3)
        r["seg_bad"] = r["day"] == "10-22" and datetime.fromtimestamp(r["t"]).strftime("%H:%M:%S") >= "16:24:38"
        r["clean"] = r["trusted"] and not r["yaw_suspect"] and not r["pos_suspect"] and not r["seg_bad"]
    # audited yaw: console yaw minus the session-local (same session, +-90 s, >= 2 audited pictures) median of the
    # audit's yaw error. Smoothed so that a picture's own matches do not set its own ground truth.
    for r in R:
        r["yaw_console"] = r["yaw_deg"]
        near = [x["audit_e"] for x in R if x["session"] == r["session"] and r["session"] is not None
                and abs(x["t"] - r["t"]) <= 90 and x["audit_e"] == x["audit_e"]]
        r["yaw_fix"] = float(np.median(near)) if len(near) >= 2 else 0.0
        r["yaw_audited"] = float(wrap_deg(r["yaw_deg"] - r["yaw_fix"]))
    return R
