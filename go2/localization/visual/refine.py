"""Pose refinement after retrieval (task 3).

For each query: top-10 db pictures by DINOv2-VLAD (crop --rcrop), each verified by SIFT + essential matrix with
keypoints restricted to a region (--region full|upper|lower; upper = rows < 162, lower = rows >= 198 of 360).
Yaw:  yaw_q = yaw_db + relative yaw (best-verified db picture; also an inlier-weighted circular mean of the
      verified ones within 1.5 m of the best).
Position: (a) best verified db position; (b) inlier-weighted mean of up to 3 verified db pictures within 1.5 m
      of the best; (c) bearing triangulation (rays from >= 2 verified db pictures whose rays cross at >= 20 deg),
      falling back to (b) when unavailable or > 1.5 m from (b).
Errors are against the query's console pose (and yaw against the audited yaw). Output results/refine_<tag>.json
with one row per query.
    python3 refine.py --split x_22v20 --region upper --rcrop full
"""
from __future__ import annotations

import argparse
import json
import math
from multiprocessing import Pool

import numpy as np

import vcommon as V
import vpr_eval as E

ROWS = {"full": None, "upper": 162, "lower": None}
R = None


def _init():
    global R
    R = V.load_records()


def _match(args):
    qi, dbs, region, matcher = args
    if matcher == "lg":
        import geo_lg as geo
    else:
        import geo
    q = R[qi]
    out = []
    for d in dbs:
        if region == "lower":
            m = np.zeros((360, 640), bool); m[198:] = True
            o = geo.rel_pose(R[d], q, mask_a=m, mask_b=m)
        else:
            o = geo.rel_pose(R[d], q, row_max=ROWS[region])
        out.append((int(d), o))
    return qi, out


def circmean(a, w):
    a = np.radians(a)
    return math.degrees(math.atan2((w * np.sin(a)).sum(), (w * np.cos(a)).sum()))


def estimate(Rr, q, cands, min_inl):
    ver = [(d, o) for d, o in cands if o["inl"] >= min_inl and np.isfinite(o["yaw"])]
    if not ver:
        return None
    ver.sort(key=lambda x: -x[1]["inl"])
    d0, o0 = ver[0]
    b = Rr[d0]
    close = [(d, o) for d, o in ver if math.hypot(Rr[d]["x"] - b["x"], Rr[d]["y"] - b["y"]) <= 1.5][:3]
    w = np.array([o["inl"] for _, o in close], float)
    yaw_best = float(V.wrap_deg(b["yaw_deg"] + o0["yaw"]))
    yaw_w = float(V.wrap_deg(circmean(np.array([Rr[d]["yaw_deg"] + o["yaw"] for d, o in close]), w)))
    pos_best = np.array([b["x"], b["y"]])
    pos_w = (np.array([[Rr[d]["x"], Rr[d]["y"]] for d, _ in close]) * w[:, None]).sum(0) / w.sum()
    # bearing triangulation: ray from db picture position in map direction yaw_db + bearing
    rays = [(np.array([Rr[d]["x"], Rr[d]["y"]]), math.radians(Rr[d]["yaw_deg"] + o["bearing"]), o["inl"])
            for d, o in close if not o["rot_only"] and np.isfinite(o["bearing"])]
    pos_tri, tri_ok = pos_w.copy(), False
    if len(rays) >= 2:
        dirs = np.array([[math.cos(t), math.sin(t)] for _, t, _ in rays])
        ang = max(abs(math.degrees(math.asin(np.clip(np.cross(dirs[i], dirs[j]), -1, 1))))
                  for i in range(len(rays)) for j in range(i + 1, len(rays)))
        if ang >= 20:
            A = np.zeros((2, 2)); bb = np.zeros(2)
            for (p, t, wi), dv in zip(rays, dirs):
                P = np.eye(2) - np.outer(dv, dv)
                A += wi * P; bb += wi * P @ p
            x = np.linalg.solve(A + 1e-6 * np.eye(2), bb)
            # the solution must lie in front of the rays and near the weighted mean
            if np.linalg.norm(x - pos_w) <= 1.5 and all(np.dot(x - p, dv) > 0 for (p, _, _), dv in zip(rays, dirs)):
                pos_tri, tri_ok = x, True
    second = max([o["inl"] for d, o in ver if math.hypot(Rr[d]["x"] - b["x"], Rr[d]["y"] - b["y"]) > 2.0] + [0])
    return {"best": Rr[d0]["id"], "inl": o0["inl"], "n_ver": len(ver), "second_far_inl": second,
            "yaw_best": yaw_best, "yaw_w": yaw_w, "rel_yaw": o0["yaw"], "pos_best": pos_best.tolist(),
            "pos_w": pos_w.tolist(), "pos_tri": pos_tri.tolist(), "tri_ok": tri_ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="x_22v20")
    ap.add_argument("--region", default="full", choices=list(ROWS))
    ap.add_argument("--rcrop", default="full")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--min_inl", type=int, default=25)
    ap.add_argument("--matcher", default="sift", choices=["sift", "lg"])
    a = ap.parse_args()
    _init()
    ids = [r["id"] for r in R]
    D = E.load_desc("", a.rcrop, ids, [r["day"] in ("10-19", "10-20") for r in R])["dino_vlad"]
    q, db, excl = E.splits(R, "clean")[a.split]
    sim = D[q] @ D[db].T
    if excl is not None:
        sim = np.where(excl, -9, sim)
    top = np.argsort(-sim, 1)[:, :a.k]
    jobs = [(int(q[i]), [int(db[j]) for j in top[i]], a.region, a.matcher) for i in range(len(q))]
    if a.matcher == "lg":
        res = dict(map(_match, jobs))
    else:
        with Pool(12, initializer=_init) as pool:
            res = dict(pool.map(_match, jobs, chunksize=4))
    pos, dist, ang = E.gt(R, q, db)
    if excl is not None:
        pos = pos & ~excl
    rows = []
    for i, qi in enumerate(q):
        r = R[qi]
        cands = res[int(qi)]
        est = estimate(R, qi, cands, a.min_inl)
        top1 = R[int(db[top[i, 0]])]
        row = {"id": r["id"], "has_pos": bool(pos[i].any()), "x": r["x"], "y": r["y"], "yaw": r["yaw_deg"],
               "yaw_aud": r["yaw_audited"],
               "top1_err_m": math.hypot(top1["x"] - r["x"], top1["y"] - r["y"]),
               "top1_err_yaw": abs(float(V.wrap_deg(top1["yaw_deg"] - r["yaw_deg"]))),
               "top1_correct": bool(pos[i, top[i, 0]])}
        if est:
            row.update(est)
            for k in ("best", "w", "tri"):
                p = est[f"pos_{k}"]; row[f"err_m_{k}"] = math.hypot(p[0] - r["x"], p[1] - r["y"])
            for k in ("best", "w"):
                row[f"err_yaw_{k}"] = abs(float(V.wrap_deg(est[f"yaw_{k}"] - r["yaw_deg"])))
                row[f"err_yawaud_{k}"] = abs(float(V.wrap_deg(est[f"yaw_{k}"] - r["yaw_audited"])))
            b = R[ids.index(est["best"])]
            row["best_correct"] = bool(math.hypot(b["x"] - r["x"], b["y"] - r["y"]) <= 1.0 and abs(V.wrap_deg(b["yaw_deg"] - r["yaw_deg"])) <= 30)
            # yaw correction is only meaningful vs the db picture's own yaw; error before correction:
            row["err_yaw_nocorr"] = abs(float(V.wrap_deg(b["yaw_deg"] - r["yaw_deg"])))
        rows.append(row)
    tag = f"{a.split}_{a.region}_r{a.rcrop}" + ("_lg" if a.matcher == "lg" else "")
    json.dump(rows, open(f"results/refine_{tag}.json", "w"), indent=1)
    summarize(rows, tag)


def summarize(rows, tag):
    hp = [r for r in rows if r["has_pos"]]
    ver = [r for r in hp if "inl" in r]
    f = lambda k, rr: np.array([r[k] for r in rr if k in r])
    print(f"== {tag}: queries {len(rows)}, with a true neighbour {len(hp)}, verified {len(ver)} ({len(ver)/max(1,len(hp)):.0%})")
    print("   retrieval top-1 correct %.2f | after verification re-rank, best correct %.2f (of verified)" % (
        np.mean([r["top1_correct"] for r in hp]), np.mean([r["best_correct"] for r in ver]) if ver else np.nan))
    for k in ("err_m_best", "err_m_w", "err_m_tri", "err_yaw_nocorr", "err_yaw_best", "err_yaw_w"):
        x = f(k, ver)
        print(f"   {k:16s} median {np.median(x):6.2f}  p75 {np.percentile(x,75):6.2f}  p90 {np.percentile(x,90):6.2f}")
    ok = [r for r in ver if r["best_correct"]]
    x = f("err_yaw_w", ok); y = f("err_yaw_nocorr", ok)
    print(f"   on correct matches (n={len(ok)}): yaw err db-yaw {np.median(y):.1f} -> corrected {np.median(x):.1f} (median); pos err w-mean {np.median(f('err_m_w', ok)):.2f} tri {np.median(f('err_m_tri', ok)):.2f} (tri used {np.mean([r['tri_ok'] for r in ok]):.0%})")


if __name__ == "__main__":
    main()
