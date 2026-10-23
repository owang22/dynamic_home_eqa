"""Robust rotation averaging of the console's yaw error from verified picture pairs (ground-truth audit).

Each verified pair (results/pair_yaw.json) gives err_ab = console dyaw - image dyaw = e_b - e_a, where e is the
console's yaw error of a picture. Solve for e by IRLS (Cauchy, scale 8 deg) with a weak prior e ~ 0 (weight 0.05)
that fixes the gauge to the console's average. A picture is 'yaw-suspect' when |e| > 20 deg and it has >= 2
verified partners. Output: results/yaw_audit.json {id: {e, n_pairs, suspect}} and a per-day summary.
    python3 yaw_audit.py
"""
import json, collections
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr
import vcommon as V

P = json.load(open("results/pair_yaw.json"))
ids = sorted(set([p["a"] for p in P] + [p["b"] for p in P]))
ix = {k: i for i, k in enumerate(ids)}
n = len(ids); m = len(P)
a = np.array([ix[p["a"]] for p in P]); b = np.array([ix[p["b"]] for p in P])
err = np.array([p["err"] for p in P])
e = np.zeros(n); lam = 0.05
for it in range(30):
    r = V.wrap_deg(err - (e[b] - e[a]))
    w = 1.0 / (1.0 + (r / 8.0) ** 2)
    tgt = e[b] - e[a] + r
    A = lil_matrix((m + n, n))
    sw = np.sqrt(w)
    A[np.arange(m), b] = sw; A[np.arange(m), a] = -sw
    A[m + np.arange(n), np.arange(n)] = np.sqrt(lam)
    rhs = np.concatenate([sw * tgt, np.zeros(n)])
    e = lsqr(A.tocsr(), rhs, atol=1e-10, btol=1e-10)[0]
    e = V.wrap_deg(e)
r = V.wrap_deg(err - (e[b] - e[a]))
deg = np.bincount(np.concatenate([a, b]), minlength=n)
R = {r_["id"]: r_ for r_ in V.load_records()}
out = {k: {"e": float(e[i]), "n_pairs": int(deg[i]), "suspect": bool(abs(e[i]) > 20 and deg[i] >= 2), "day": R[k]["day"],
           "time": R[k]["time"]} for k, i in ix.items()}
json.dump(out, open("results/yaw_audit.json", "w"), indent=1)
print("pairs", m, "pictures", n, "| residual after averaging: median", np.median(np.abs(r)).round(2), "p90", np.percentile(np.abs(r), 90).round(1),
      "share > 10 deg", (np.abs(r) > 10).mean().round(3))
by = collections.defaultdict(list)
for k, v in out.items():
    if v["n_pairs"] >= 2: by[v["day"]].append(abs(v["e"]))
for d in sorted(by):
    x = np.array(by[d]); print(d, "n", len(x), "median |e|", np.median(x).round(1), "p75", np.percentile(x, 75).round(1), "p90", np.percentile(x, 90).round(1),
                               "suspect (>20 deg)", int((x > 20).sum()))
# time structure on 10-22: print e by time
for d in ("10-20", "10-22"):
    xs = sorted((v["time"][-5:], round(v["e"]), v["n_pairs"]) for v in out.values() if v["day"] == d and v["n_pairs"] >= 2)
    agg = collections.defaultdict(list)
    for t, ev, npair in xs: agg[t[:4] + "x"].append(ev)
    print(d, {k: (len(v), int(np.median(v))) for k, v in agg.items()})
