"""Refine the map poses of the calm "fresh" snapshots (persistence.py's keyframes) by iterative consensus
registration, because the console's poses are too noisy for a 0.1 m persistence map (figs/persistence_console.png).

    python3 go2/localization/refine_poses.py

Iteration k:
  0. the saved map (weight 0.5) stays in the reference in every iteration, and no keyframe may move more than
     0.6 m / 15 deg from its console pose (without these the consensus drifts away from the map: v1 run)
  1. consensus map from the current poses: per 0.05 m cell, the fraction of in-view keyframes that put a cell with
     column top >= 0.4 m there; built leave-one-day-out (a keyframe is matched only against other days' data, so it
     cannot match itself and the result is cross-day consistent). Iteration 0 also adds the saved map as a prior.
  2. soft likelihood field = consensus blurred with sigma_k (0.25, 0.15, 0.10, 0.07 m)
  3. each keyframe: correlative search around its current pose (+-0.4 m, +-8 deg, 0.5 deg steps), refine
  4. per session, a running median (5 keyframes) of the correction is applied, and corrections whose own match is
     not better than the smoothed one are replaced by it (outlier rejection; odom between keyframes is trusted)
Outputs results/refined_poses/<session>.npz {cloud, T_map_odom, T_console, score, score_console}
and results/refine_log.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import jumps  # noqa: E402
import matcher  # noqa: E402
import persistence as P  # noqa: E402

RES = 0.05
OX, OY = common.MAP_ORIGIN
GW, GH = 283, 289
ZMIN = 0.4
SIGMAS = (0.25, 0.15, 0.10, 0.07)
PRIOR_W = 0.5                 # the saved map stays in the reference (anchors the gauge)
MAX_DEV_M, MAX_DEV_DEG = 0.6, 15.0  # never move a keyframe further than this from the console pose
OUT = common.HERE / "results" / "refined_poses"


def keyframes():
    calls = jumps.agent_calls()
    kf = []
    for s in P.MAP_SESSIONS:
        d, snaps = P.snapshot_poses(s, calls, "console")
        for i, T, dog in snaps:
            ob, _ = common.cloud(d, i)
            ob = ob[ob[:, 2] >= ZMIN][:, :2].astype(float)
            if len(ob) < 30:
                continue
            kf.append(dict(session=s, day=s[:10], cloud=i, t=float(d["c_t"][i]), pts=ob, dog=dog.astype(float),
                           T0=np.array(T, float), T=np.array(T, float)))
    return kf


def raster(kfs, mask_days=None):
    occ = np.zeros((GH, GW), np.float32)
    view = np.zeros((GH, GW), np.float32)
    gx, gy = np.meshgrid(OX + (np.arange(GW) + 0.5) * RES, OY + (np.arange(GH) + 0.5) * RES)
    for k in kfs:
        T = k["T"]
        q = common.transform_pts(T, k["pts"])
        dog = common.transform_pts(T, k["dog"][None])[0]
        r0 = int((dog[1] - 3.3 - OY) / RES)
        c0 = int((dog[0] - 3.3 - OX) / RES)
        r1, c1 = r0 + int(6.6 / RES), c0 + int(6.6 / RES)
        r0, c0, r1, c1 = max(r0, 0), max(c0, 0), min(r1, GH), min(c1, GW)
        sub = (gx[r0:r1, c0:c1] - dog[0]) ** 2 + (gy[r0:r1, c0:c1] - dog[1]) ** 2 <= 3.0 ** 2
        view[r0:r1, c0:c1] += sub
        ci = np.floor((q[:, 0] - OX) / RES).astype(int)
        cj = np.floor((q[:, 1] - OY) / RES).astype(int)
        ok = (ci >= 0) & (ci < GW) & (cj >= 0) & (cj < GH)
        m = np.zeros((GH, GW), bool)
        # cloud cells are 0.1 m: mark the 2x2 block of 0.05 cells around each centre
        for di in (0, -1):
            for dj in (0, -1):
                ii, jj = np.clip(ci[ok] + di, 0, GW - 1), np.clip(cj[ok] + dj, 0, GH - 1)
                m[jj, ii] = True
        occ += m
    return occ, view


def field_from_consensus(occ, view, sigma, prior=None, prior_w=0.0):
    f = np.where(view >= 2, occ / np.maximum(view, 1), 0.0).astype(np.float32)
    if prior is not None:
        f = np.maximum(f, prior_w * prior)
    lf = ndimage.gaussian_filter(f, sigma / RES)
    lf /= max(lf.max(), 1e-6)
    F = matcher.Field(np.zeros((GH, GW), bool), RES, (OX, OY), sigma=0.1)
    F.lf = lf.astype(np.float32)
    return F


def pivot_pts(k):
    """Points relative to the dog (pivot) in odom axes, and the pose of the pivot in the map for transform T."""
    return k["pts"] - k["dog"]


def pivot_pose(T, dog):
    p = common.transform_pts(T, dog[None])[0]
    return np.array([p[0], p[1], T[2]])


def T_from_pivot(pp, dog):
    # T * dog = pp.xy, T.yaw = pp.yaw  ->  T.xy = pp.xy - R(yaw) dog
    c, s = math.cos(pp[2]), math.sin(pp[2])
    return np.array([pp[0] - (c * dog[0] - s * dog[1]), pp[1] - (s * dog[0] + c * dog[1]), pp[2]])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    kf = keyframes()
    days = sorted({k["day"] for k in kf})
    print(f"{len(kf)} keyframes over {len(days)} days")
    M = common.load_map()
    prior = ((M == 0)[::-1]).astype(np.float32)
    log = []
    for it, sig in enumerate(SIGMAS):
        fields = {}
        for dd in days:
            occ, view = raster([k for k in kf if k["day"] != dd])
            fields[dd] = field_from_consensus(occ, view, sig, prior, PRIOR_W)
        moves = []
        for k in kf:
            F = fields[k["day"]]
            rel = pivot_pts(k)
            pp = pivot_pose(k["T"], k["dog"])
            rk = matcher.match(F, rel, pp, 8, 0.5, 0.4, top_k=3)
            if not rk:
                k["cand"] = pp
                k["sc"] = 0
                continue
            b = rk[0]
            k["cand"] = np.array(b[1:])
            k["sc"] = b[0]
            k["sc_cur"] = F.score(rel, pp)
            k["margin"] = b[0] - (rk[1][0] if len(rk) > 1 else 0)
        # per-session robust smoothing of the correction (in pivot coordinates)
        for s in P.MAP_SESSIONS:
            ks = [k for k in kf if k["session"] == s]
            if not ks:
                continue
            cur = np.array([pivot_pose(k["T"], k["dog"]) for k in ks])
            cand = np.array([k["cand"] for k in ks])
            dlt = cand - cur
            dlt[:, 2] = common.wrap(dlt[:, 2])
            sm = np.stack([ndimage.median_filter(dlt[:, j], size=5, mode="nearest") for j in range(3)], -1)
            for k, c, dl, smd in zip(ks, cur, dlt, sm):
                F = fields[k["day"]]
                rel = pivot_pts(k)
                own = c + dl
                smooth = c + smd
                use = own if F.score(rel, own) > F.score(rel, smooth) + 0.02 and k.get("margin", 0) > 0.02 else smooth
                p0 = pivot_pose(k["T0"], k["dog"])
                dev = use - p0
                dev[2] = common.wrap(dev[2])
                r = math.hypot(dev[0], dev[1])
                if r > MAX_DEV_M:
                    dev[:2] *= MAX_DEV_M / r
                dev[2] = float(np.clip(dev[2], -math.radians(MAX_DEV_DEG), math.radians(MAX_DEV_DEG)))
                use = p0 + dev
                newT = T_from_pivot(use, k["dog"])
                moves.append((math.hypot(*(use[:2] - c[:2])), abs(math.degrees(common.wrap(use[2] - c[2])))))
                k["T"] = newT
        mv = np.array(moves)
        tot = np.array([(math.hypot(*(pivot_pose(k["T"], k["dog"])[:2] - pivot_pose(k["T0"], k["dog"])[:2])),
                         abs(math.degrees(common.wrap(k["T"][2] - k["T0"][2])))) for k in kf])
        entry = dict(iter=it, sigma=sig, move_med_m=float(np.median(mv[:, 0])), move_p90_m=float(np.percentile(mv[:, 0], 90)),
                     move_med_deg=float(np.median(mv[:, 1])), total_from_console_med_m=float(np.median(tot[:, 0])),
                     total_from_console_p90_m=float(np.percentile(tot[:, 0], 90)),
                     total_from_console_med_deg=float(np.median(tot[:, 1])),
                     total_from_console_p90_deg=float(np.percentile(tot[:, 1], 90)),
                     score_med=float(np.median([k["sc"] for k in kf])))
        log.append(entry)
        print(entry)
    for s in P.MAP_SESSIONS:
        ks = [k for k in kf if k["session"] == s]
        if not ks:
            continue
        np.savez(OUT / f"{s}.npz", cloud=np.array([k["cloud"] for k in ks]), T_map_odom=np.array([k["T"] for k in ks]),
                 T_console=np.array([k["T0"] for k in ks]), t=np.array([k["t"] for k in ks]),
                 dog=np.array([k["dog"] for k in ks]))
    json.dump(log, open(common.HERE / "results" / "refine_log.json", "w"), indent=1)


if __name__ == "__main__":
    main()
