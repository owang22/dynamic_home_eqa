"""Robust position audit of the console poses from strongly matched picture pairs (ground-truth check).

Assumption, checked on the clean day: pictures with >= 100 SIFT+E inliers were taken within ~1 m of each other
(on 10-20 within-day, such pairs have console distance median 0.28 m, p90 0.64 m, 1 % > 1 m).
Unknown per-picture offsets o_i (2D) with (p_b + o_b) - (p_a + o_a) ~ 0 (Cauchy, scale 0.5 m) and a weak prior
o_i ~ 0 (weight 0.05). Picture is 'pos-suspect' if |o_i| > 1.0 m and it has >= 2 strong pairs.
Output results/pos_audit.json; prints per-day offsets.
    python3 pos_audit.py
"""
import json, collections
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr
import vcommon as V

R = {r["id"]: r for r in V.load_records()}
P = [p for p in json.load(open("results/pair_yaw.json")) if p["inl"] >= 100]
ids = sorted(set([p["a"] for p in P] + [p["b"] for p in P]))
ix = {k: i for i, k in enumerate(ids)}
n, m = len(ids), len(P)
a = np.array([ix[p["a"]] for p in P]); b = np.array([ix[p["b"]] for p in P])
X = np.array([[R[k]["x"], R[k]["y"]] for k in ids])
o = np.zeros((n, 2)); lam = 0.05
for it in range(30):
    res = (X[b] + o[b]) - (X[a] + o[a])
    w = 1.0 / (1.0 + (np.linalg.norm(res, axis=1) / 0.5) ** 2)
    A = lil_matrix((m + n, n)); sw = np.sqrt(w)
    A[np.arange(m), b] = sw; A[np.arange(m), a] = -sw
    A[m + np.arange(n), np.arange(n)] = np.sqrt(lam)
    A = A.tocsr()
    for c in range(2):
        rhs = np.concatenate([-sw * (X[b, c] - X[a, c]), np.zeros(n)])
        o[:, c] = lsqr(A, rhs, atol=1e-10, btol=1e-10)[0]
deg = np.bincount(np.concatenate([a, b]), minlength=n)
res = (X[b] + o[b]) - (X[a] + o[a])
out = {k: {"ox": float(o[i, 0]), "oy": float(o[i, 1]), "n_pairs": int(deg[i]),
           "suspect": bool(np.hypot(*o[i]) > 1.0 and deg[i] >= 2), "day": R[k]["day"], "time": R[k]["time"]} for k, i in ix.items()}
json.dump(out, open("results/pos_audit.json", "w"), indent=1)
print("strong pairs", m, "pictures", n, "| pair distance after correction: median", np.median(np.linalg.norm(res, axis=1)).round(2),
      "| before:", np.median(np.linalg.norm(X[b] - X[a], axis=1)).round(2))
by = collections.defaultdict(list)
for k, v in out.items():
    if v["n_pairs"] >= 2: by[v["day"]].append([v["ox"], v["oy"]])
for d in sorted(by):
    x = np.array(by[d]); nn = np.linalg.norm(x, axis=1)
    print(d, "n", len(x), "mean offset", x.mean(0).round(2), "median |o|", np.median(nn).round(2), "p90", np.percentile(nn, 90).round(2), "suspect", int((nn > 1).sum()))
for d in ("10-22",):
    agg = collections.defaultdict(list)
    for v in out.values():
        if v["day"] == d and v["n_pairs"] >= 2: agg[v["time"][-5:-1] + "x"].append(np.hypot(v["ox"], v["oy"]))
    print(d, {k: (len(v), round(float(np.median(v)), 2)) for k, v in sorted(agg.items())})
