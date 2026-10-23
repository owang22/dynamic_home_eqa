"""Multi-session pose graph over the keyframes: an offline "lifelong map" back-end, so that the persistence map
and the localizer evaluation can use poses better than the console's.

    python3 go2/localization/pgo.py [--holdout 0.3]

Unknowns: map->odom T_k (x, y, yaw) per keyframe (revisits.py keyframes = calm "fresh" snapshots).
Residual blocks:
  revisit  T_a * R_ab == T_b         (R_ab from direct cloud-to-cloud registration, revisits.py)
           sigma 0.05 m (at the dog) / 1 deg, Cauchy loss (scale 3 sigma) against wrong registrations
           (solved in two stages: first loose (0.2 m / 3 deg, console 1 m / 20 deg) without robust loss, then tight)
  odometry T_k == T_{k+1} within a session (odom is the only motion source between keyframes):
           yaw sigma 0.5 deg + 4 deg per minute between them (the measured gyro drift is 0.6-4.8 deg/min),
           position at the dog sigma 0.03 m + 0.03 m per metre walked
  console  dog position and heading under T_k == console map pose: sigma 0.5 m / 10 deg, Cauchy loss
           (keeps the solution in the saved map's frame; individual wrong console poses are down-weighted)
Afterwards the whole solution is moved by one rigid transform onto the console's frame on average
(anchor_to_console), so that places.json coordinates keep their meaning.
A random --holdout fraction of revisit pairs is left out of the solve and used to test it.
Output: results/pgo_poses/<session>.npz {cloud, T_map_odom, T_console, t, dog}, results/pgo_eval.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import revisits  # noqa: E402

OUT = common.HERE / "results"


def apply(T, p):
    c, s = math.cos(T[2]), math.sin(T[2])
    return np.array([T[0] + c * p[0] - s * p[1], T[1] + s * p[0] + c * p[1]])


def solve(pr, train_idx, sig_rev=(0.05, 1.0), sig_con=(0.5, 10.0), drift_deg_min=4.0, x0=None, loss="cauchy",
          f_scale=3.0):
    n = len(pr["kf_T"])
    x0 = pr["kf_T"].astype(float).ravel().copy() if x0 is None else x0.ravel().copy()
    sess = pr["kf_session"]
    t = pr["kf_t"]
    dog = pr["kf_dog"]
    order = np.lexsort((t, sess))
    odo = []
    for a, b in zip(order[:-1], order[1:]):
        if sess[a] == sess[b]:
            dt_min = (t[b] - t[a]) / 60
            dist = float(np.hypot(*(dog[b] - dog[a])))
            odo.append((a, b, 0.03 + 0.03 * dist, math.radians(0.5 + drift_deg_min * dt_min)))
    rev = [pr["pairs"][i] for i in train_idx]
    blocks = []  # (kind, data)
    for a, b, sc, mg, rx, ry, ryaw in rev:
        blocks.append(("rev", int(a), int(b), np.array([rx, ry, ryaw])))
    nrev = len(blocks)
    for a, b, sp, sy in odo:
        blocks.append(("odo", a, b, (sp, sy)))
    nodo = len(odo)
    con_pose = np.array([np.r_[apply(T, d), T[2]] for T, d in zip(pr["kf_T"], dog)])

    nblk = len(blocks) + n
    wts = np.ones(nblk)

    def resid(x, raw=False):
        X = x.reshape(-1, 3)
        r = []
        for kind, a, b, data in blocks:
            if kind == "rev":
                Ta = X[a]
                TaR = common.compose(Ta, data)
                p1 = apply(TaR, dog[b])
                p2 = apply(X[b], dog[b])
                dy = float(common.wrap(TaR[2] - X[b][2]))
                r += [(p1[0] - p2[0]) / sig_rev[0], (p1[1] - p2[1]) / sig_rev[0], math.degrees(dy) / sig_rev[1]]
            else:
                sp, sy = data
                p1 = apply(X[a], dog[b])
                p2 = apply(X[b], dog[b])
                dy = float(common.wrap(X[a][2] - X[b][2]))
                r += [(p1[0] - p2[0]) / sp, (p1[1] - p2[1]) / sp, dy / sy]
        for k in range(n):
            p = apply(X[k], dog[k])
            r += [(p[0] - con_pose[k, 0]) / sig_con[0], (p[1] - con_pose[k, 1]) / sig_con[0],
                  math.degrees(float(common.wrap(X[k][2] - con_pose[k, 2]))) / sig_con[1]]
        r = np.array(r)
        return r if raw else r * np.repeat(np.sqrt(wts), 3)

    # sparsity
    m = 3 * (len(blocks) + n)
    S = lil_matrix((m, 3 * n), dtype=int)
    row = 0
    for kind, a, b, data in blocks:
        for j in range(3):
            S[row:row + 3, 3 * a + j] = 1
            S[row:row + 3, 3 * b + j] = 1
        row += 3
    for k in range(n):
        S[row:row + 3, 3 * k:3 * k + 3] = 1
        row += 3
    # robust only on revisit and console blocks: emulate with per-residual scaling via f_scale & loss on all
    # robust loss on revisit and console blocks only, by iteratively reweighted least squares (Cauchy weights);
    # odometry blocks stay quadratic so the graph cannot "jump" between consecutive keyframes (v2 applied the
    # robust loss to every residual, which let it break odometry: up to 1.4 m jumps within 30 s)
    is_odo = np.array([k == "odo" for k, *_ in blocks] + [False] * n)
    x = x0
    for _ in range(6 if loss != "linear" else 1):
        res = least_squares(resid, x, jac_sparsity=S, loss="linear", method="trf", x_scale="jac",
                            max_nfev=100, verbose=0)
        x = res.x
        if loss == "linear":
            break
        rb = np.linalg.norm(resid(x, raw=True).reshape(-1, 3), axis=1)
        wts = np.where(is_odo, 1.0, 1.0 / (1.0 + (rb / f_scale) ** 2))
    X = res.x.reshape(-1, 3)
    X[:, 2] = common.wrap(X[:, 2])
    return X, dict(nrev=nrev, nodo=nodo, cost=float(res.cost), nfev=int(res.nfev))


def anchor_to_map(pr, X, iters=2):
    """The graph fixes the poses relative to each other; its absolute frame comes from the console prior, which is
    biased (the console turns with the odom gyro drift while the dog stands). Fix the gauge by fitting the pooled
    keyframe map (cells occupied in >= 50% of the keyframes that see them, column top >= 0.4 m) rigidly onto the
    saved map, and apply that one rigid transform G to all poses (T <- G * T)."""
    import matcher
    from persistence import accumulate  # noqa: F401  (same grid conventions)
    M = common.load_map()
    F = matcher.Field((M == 0)[::-1], 0.05, common.MAP_ORIGIN, sigma=0.1)
    kf_pts = {}
    for s in sorted(set(pr["kf_session"])):
        d = common.load(str(s))
        for k in np.flatnonzero(pr["kf_session"] == s):
            ob, _ = common.cloud(d, int(pr["kf_cloud"][k]))
            kf_pts[k] = ob[ob[:, 2] >= 0.4][:, :2].astype(float)
    Gs = []
    for _ in range(iters):
        res, ox, oy, W, H = 0.1, common.MAP_ORIGIN[0], common.MAP_ORIGIN[1], 142, 145
        occ = np.zeros((H, W))
        view = np.zeros((H, W))
        gx, gy = np.meshgrid(ox + (np.arange(W) + 0.5) * res, oy + (np.arange(H) + 0.5) * res)
        for k, pts in kf_pts.items():
            q = common.transform_pts(X[k], pts)
            dg = apply(X[k], pr["kf_dog"][k])
            view += (gx - dg[0]) ** 2 + (gy - dg[1]) ** 2 <= 9.0
            ci = np.floor((q[:, 0] - ox) / res).astype(int)
            cj = np.floor((q[:, 1] - oy) / res).astype(int)
            ok = (ci >= 0) & (ci < W) & (cj >= 0) & (cj < H)
            m = np.zeros((H, W), bool)
            m[cj[ok], ci[ok]] = True
            occ += m
        f = np.where(view >= 3, occ / np.maximum(view, 1), 0)
        r, c = np.nonzero(f >= 0.5)
        xy = np.stack([ox + (c + 0.5) * res, oy + (r + 0.5) * res], -1)
        ctr = xy.mean(0)
        b = matcher.match(F, xy - ctr, (ctr[0], ctr[1], 0.0), 20, 0.25, 1.0, top_k=1)[0]
        # G: rotate by b.yaw about ctr, then move ctr to (b.x, b.y)
        cg, sg = math.cos(b[3]), math.sin(b[3])
        G = np.array([b[1] - (cg * ctr[0] - sg * ctr[1]), b[2] - (sg * ctr[0] + cg * ctr[1]), b[3]])
        X = np.array([common.compose(G, T) for T in X])
        Gs.append(dict(dx=float(b[1] - ctr[0]), dy=float(b[2] - ctr[1]), deg=float(math.degrees(b[3])), score=float(b[0])))
        print("gauge fit to saved map:", Gs[-1])
    return X, Gs


def anchor_to_console(pr, X):
    """Gauge = the console's frame on average (that is the frame places.json and the console's planner use):
    the rigid G that best maps the graph's dog poses onto the console's (median heading difference, then the
    median position difference after rotating about the centroid). T <- G * T."""
    dog = pr["kf_dog"]
    P_g = np.array([np.r_[apply(T, d), T[2]] for T, d in zip(X, dog)])
    P_c = np.array([np.r_[apply(T, d), T[2]] for T, d in zip(pr["kf_T"], dog)])
    th = float(np.median(common.wrap(P_c[:, 2] - P_g[:, 2])))
    ctr = P_g[:, :2].mean(0)
    c, s = math.cos(th), math.sin(th)
    rot = (P_g[:, :2] - ctr) @ np.array([[c, s], [-s, c]]) + ctr
    t = np.median(P_c[:, :2] - rot, axis=0)
    G = np.array([ctr[0] + t[0] - (c * ctr[0] - s * ctr[1]), ctr[1] + t[1] - (s * ctr[0] + c * ctr[1]), th])
    X = np.array([common.compose(G, T) for T in X])
    g = dict(deg=math.degrees(th), dx=float(t[0]), dy=float(t[1]))
    print("gauge fit to console:", g)
    return X, [g]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    pr = revisits.load_pairs()
    npairs = len(pr["pairs"])
    rng = np.random.default_rng(a.seed)
    perm = rng.permutation(npairs)
    nte = int(a.holdout * npairs)
    test, train = perm[:nte], perm[nte:]
    # graduated: a loose, non-robust solve first (so large console heading errors can be corrected), then tight
    # and robust starting from it
    X1, info1 = solve(pr, train, sig_rev=(0.2, 3.0), sig_con=(1.0, 20.0), loss="linear")
    X, info = solve(pr, train, x0=X1, loss="cauchy", f_scale=3.0)
    # gauge: the console's frame (v1 fitted the pooled map rigidly to the saved map instead, which rotated the
    # whole solution by about -9 deg against the console; the saved map is locally bent, see REPORT.md)
    X, gauge = anchor_to_console(pr, X)
    info["gauge"] = gauge
    tab = {(str(s), int(c)): T for s, c, T in zip(pr["kf_session"], pr["kf_cloud"], X)}
    pte = dict(pr)
    pte["pairs"] = pr["pairs"][test]
    ptr = dict(pr)
    ptr["pairs"] = pr["pairs"][train]
    ev = {}
    for label, f in (("console", revisits.console_T(pr)), ("pgo", lambda s, c: tab.get((s, c)))):
        for split, pp in (("test", pte), ("train", ptr)):
            e = revisits.evaluate(pp, f)
            if not len(e):
                continue
            ev[f"{label}_{split}"] = dict(n=len(e), med_m=float(np.median(e[:, 0])), med_deg=float(np.median(e[:, 1])),
                                          p90_m=float(np.percentile(e[:, 0], 90)), p90_deg=float(np.percentile(e[:, 1], 90)),
                                          ok=float(np.mean((e[:, 0] < 0.3) & (e[:, 1] < 5))))
            print(revisits.summarize(e, f"{label} [{split}]"))
    dev = np.array([(np.hypot(*(apply(T, d) - apply(T0, d))), abs(math.degrees(common.wrap(T[2] - T0[2]))))
                    for T, T0, d in zip(X, pr["kf_T"], pr["kf_dog"])])
    print(f"pgo vs console at the dog: median {np.median(dev[:, 0]):.2f} m / {np.median(dev[:, 1]):.1f} deg, "
          f"p90 {np.percentile(dev[:, 0], 90):.2f} m / {np.percentile(dev[:, 1], 90):.1f} deg")
    ev["pgo_vs_console"] = dict(med_m=float(np.median(dev[:, 0])), med_deg=float(np.median(dev[:, 1])),
                                p90_m=float(np.percentile(dev[:, 0], 90)), p90_deg=float(np.percentile(dev[:, 1], 90)))
    ev["info"] = info
    ev["holdout"] = a.holdout
    folder = OUT / ("pgo_poses" if a.holdout == 0 else f"pgo_poses_holdout{a.holdout}")
    folder.mkdir(exist_ok=True)
    for s in sorted(set(pr["kf_session"])):
        k = pr["kf_session"] == s
        np.savez(folder / f"{s}.npz", cloud=pr["kf_cloud"][k], T_map_odom=X[k], T_console=pr["kf_T"][k],
                 t=pr["kf_t"][k], dog=pr["kf_dog"][k])
    json.dump(ev, open(OUT / f"pgo_eval_holdout{a.holdout}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
