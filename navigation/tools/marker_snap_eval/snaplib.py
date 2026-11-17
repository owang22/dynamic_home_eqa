"""Snap a tag sighting onto the lidar surface it sits on (2-D, dog frame: x forward, y left; camera at (CAM, 0))."""
import math
import numpy as np
CAM = 0.30
SNAP_R = 0.4          # m: points used around the detection
SNAP_CORR_DEG = 3.0   # corridor half-angle around the bearing for the first range guess
SNAP_TOL = 0.02       # m: RANSAC inlier distance
SNAP_MAX_RMS = 0.03   # m: fit good enough to trust the facing
SNAP_MIN_IN = 30
SNAP_MIN_EXTENT = 0.2 # m along the line
SNAP_MAX_SHIFT = 0.35 # m: snapped point must be this close to the detection

def snap(m, pts, rng=None, mode="full", max_dev=None):
    """m: sighting (z, x, yaw_deg). pts: Nx3 dog-frame lidar points near it. Returns dict with raw/snapped dog-frame
    tag position, facing (deg, direction the tag's front looks, dog frame), and fit quality; or {"ok": False, why}."""
    rng = rng or np.random.default_rng(0)
    tx, ty = CAM + m["z"], -m["x"]
    b = math.atan2(ty, tx - CAM); rd = math.hypot(tx - CAM, ty)
    raw = {"x": tx, "y": ty, "facing": 180.0 - m["yaw_deg"] + 0.0}
    out = {"raw": raw, "ok": False}
    if pts is None or len(pts) < 20:
        out["why"] = "no lidar points"; return out
    floor = np.percentile(pts[:, 2], 3)
    p = pts[(pts[:, 2] > floor + 0.08) & (pts[:, 2] < floor + 1.5)]
    p = p[np.hypot(p[:, 0] - tx, p[:, 1] - ty) < SNAP_R][:, :2]
    if len(p) < SNAP_MIN_IN:
        out["why"] = f"{len(p)} points above the floor"; return out
    rel = p - [CAM, 0]; r = np.hypot(*rel.T); a = np.arctan2(rel[:, 1], rel[:, 0])
    corr = np.abs((a - b + np.pi) % (2 * np.pi) - np.pi) < math.radians(SNAP_CORR_DEG)
    if corr.sum() < 8:
        out["why"] = "no surface along the bearing"; return out
    r0 = float(np.percentile(r[corr], 10))
    guess = np.array([CAM + r0 * math.cos(b), r0 * math.sin(b)])
    best = None
    for _ in range(300):
        i, j = rng.choice(len(p), 2, replace=False)
        d = p[j] - p[i]; L = np.hypot(*d)
        if L < 0.05: continue
        nrm = np.array([-d[1], d[0]]) / L
        if abs((guess - p[i]) @ nrm) > 0.05: continue          # the line must pass by the surface along the bearing
        if max_dev is not None:                                # normal near the detector's facing (either sign)
            fr = math.radians(raw["facing"]); ang = math.degrees(math.acos(min(1, abs(nrm @ [math.cos(fr), math.sin(fr)]))))
            if ang > max_dev: continue
        dist = np.abs((p - p[i]) @ nrm); inl = dist < SNAP_TOL
        if best is None or inl.sum() > best[0]: best = (inl.sum(), inl)
    if best is None:
        out["why"] = "no line through the surface"; return out
    q = p[best[1]]; c = q.mean(0)
    _, _, vt = np.linalg.svd(q - c); dirv = vt[0]; nrm = np.array([-dirv[1], dirv[0]])
    if nrm @ (np.array([CAM, 0.0]) - c) < 0: nrm = -nrm                  # normal toward the camera = the tag's front
    resid = (q - c) @ nrm; rms = float(np.sqrt(np.mean(resid ** 2)))
    ext = float(np.ptp((q - c) @ dirv))
    u = np.array([math.cos(b), math.sin(b)])                              # ray from the camera along the bearing
    den = u @ nrm
    if abs(den) < 0.2:
        out["why"] = "surface almost along the line of sight"; return out
    s = ((c - [CAM, 0]) @ nrm) / den
    sp = np.array([CAM, 0.0]) + s * u
    out.update(fit={"n": int(len(q)), "rms": round(rms, 4), "extent": round(ext, 3), "range_lidar": round(float(s), 3), "range_det": round(rd, 3)})
    if len(q) < SNAP_MIN_IN or ext < SNAP_MIN_EXTENT:
        out["why"] = f"weak fit (n {len(q)}, extent {ext:.2f})"; return out
    if math.hypot(sp[0] - tx, sp[1] - ty) > SNAP_MAX_SHIFT:
        out["why"] = "snapped point too far from the detection"; return out
    out["snap"] = {"x": float(sp[0]), "y": float(sp[1]), "facing": math.degrees(math.atan2(nrm[1], nrm[0]))}
    if mode == "range":       # keep the detector's facing; only the range along the bearing comes from the lidar
        out["snap"]["facing"] = raw["facing"]
    out["facing_ok"] = rms < SNAP_MAX_RMS
    out["ok"] = True
    return out
