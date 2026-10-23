"""Experience-based global relocalization: match the current snapshot against stored snapshots (keyframes with
pose-graph poses) from OTHER days, instead of against a map image.

    python3 go2/localization/keyframe_reloc.py [n_test]

For each test keyframe (random, all days) and each database keyframe from the other days: register the test cloud
onto the database cloud (column top >= 0.4 m) with a full yaw search (3 deg steps) and +-1.0 m around the database
keyframe's position (i.e. "am I near where that picture was taken?"), refine. The database keyframe with the best
score wins; the pose follows as T_test = T_db * R. Ambiguity ratio = best score among database keyframes whose
implied pose differs by >= 0.5 m / 10 deg, over the best.
To avoid leakage the pose graph is re-solved without any revisit pair that involves a test keyframe (the test
keyframes keep only odometry and the console prior), and truth = that re-solve's pose of the test keyframe
(pinned by its own session's other keyframes through odometry).
"""
from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import matcher  # noqa: E402
import pgo  # noqa: E402
import revisits  # noqa: E402

OUT = common.HERE / "results"
_PTS = {}


def kf_points(pr):
    pts = []
    cache = {}
    for s, c in zip(pr["kf_session"], pr["kf_cloud"]):
        s = str(s)
        if s not in cache:
            cache[s] = common.load(s)
        ob, _ = common.cloud(cache[s], int(c))
        pts.append(ob[ob[:, 2] >= 0.4][:, :2].astype(float))
    return pts


def _init(pts, dogs):
    _PTS["pts"], _PTS["dog"] = pts, dogs


def match_db(args):
    """One database keyframe against all test keyframes. Returns {test: (score, R)}."""
    b, tests = args
    pts, dog = _PTS["pts"], _PTS["dog"]
    F = revisits.field_from(pts[b], pad=2.0)
    out = {}
    for a in tests:
        rel = pts[a] - dog[a]
        guess = (dog[b][0], dog[b][1], 0.0)
        res = matcher.search(F, rel, guess[:2], np.radians(np.arange(-180, 180, 3.0)), 1.0)
        rk = matcher.best_poses(F, res, top_k=1)
        if not rk:
            continue
        r = matcher.refine_pose(F, rel, rk[0], max_deg=1.5)
        cth, sth = math.cos(r[3]), math.sin(r[3])
        R = np.array([r[1] - (cth * dog[a][0] - sth * dog[a][1]), r[2] - (sth * dog[a][0] + cth * dog[a][1]), r[3]])
        out[a] = (r[0], R)
    return b, out


def main(n_test=60, seed=1):
    pr = revisits.load_pairs()
    n = len(pr["kf_T"])
    rng = np.random.default_rng(seed)
    test = sorted(rng.choice(n, n_test, replace=False).tolist())
    keep = [i for i, (a, b, *_) in enumerate(pr["pairs"]) if int(a) not in test and int(b) not in test]
    X, info = pgo.solve(pr, keep, sig_rev=(0.2, 3.0), sig_con=(1.0, 20.0), loss="linear")
    X, _ = pgo.solve(pr, keep, x0=X, loss="cauchy", f_scale=3.0)
    X, _ = pgo.anchor_to_console(pr, X)
    pts = kf_points(pr)
    dogs = pr["kf_dog"]
    day = np.array([str(s)[:10] for s in pr["kf_session"]])
    db = [b for b in range(n) if b not in test]
    best = {a: [] for a in test}
    with ProcessPoolExecutor(22, initializer=_init, initargs=(pts, dogs)) as ex:
        for b, out in ex.map(match_db, [(b, [a for a in test if day[a] != day[b]]) for b in db], chunksize=8):
            for a, (sc, R) in out.items():
                Tq = common.compose(X[b], R)
                best[a].append((sc, Tq, b))
    rows = []
    for a in test:
        c = sorted(best[a], key=lambda z: -z[0])
        if not c:
            continue
        sc, Tq, b = c[0]
        pa = pgo.apply(Tq, dogs[a])
        truth = pgo.apply(X[a], dogs[a])
        err = (math.hypot(*(pa - truth)), abs(math.degrees(common.wrap(Tq[2] - X[a][2]))))
        second = next((z[0] for z in c[1:] if math.hypot(*(pgo.apply(z[1], dogs[a]) - pa)) >= 0.5
                       or abs(math.degrees(common.wrap(z[1][2] - Tq[2]))) >= 10), 0.0)
        con = pgo.apply(pr["kf_T"][a], dogs[a])
        con_err = (math.hypot(*(con - truth)), abs(math.degrees(common.wrap(pr["kf_T"][a][2] - X[a][2]))))
        rows.append(dict(test=a, session=str(pr["kf_session"][a]), score=sc, second=second, ratio=second / sc,
                         err_m=err[0], err_deg=err[1], ok=bool(err[0] < 0.3 and err[1] < 10),
                         console_ok=bool(con_err[0] < 0.3 and con_err[1] < 10)))
    ok = np.array([r["ok"] for r in rows])
    ratio = np.array([r["ratio"] for r in rows])
    summ = dict(n=len(rows), success=float(ok.mean()), console_ok_same_truth=float(np.mean([r["console_ok"] for r in rows])),
                ratio_med=float(np.median(ratio)))
    for g in (0.95, 0.9, 0.85, 0.8):
        acc = ratio <= g
        summ[f"accept@{g}"] = float(acc.mean())
        summ[f"precision@{g}"] = float(ok[acc].mean()) if acc.any() else None
    print(json.dumps(summ, indent=1))
    json.dump(dict(summary=summ, rows=rows), open(OUT / "keyframe_reloc.json", "w"), indent=1)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
