"""Paired comparisons between crops on the same queries (task 2), with bootstrap CIs, plus a fused descriptor
(sum of full and upper similarities). GT = clean set, console poses, 1 m / 30 deg.
    python3 vpr_compare.py -> results/vpr_compare.json
"""
import json
import numpy as np
import vcommon as V, vpr_eval as E

R = V.load_records(); ids = [r["id"] for r in R]
vm = [r["day"] in ("10-19", "10-20") for r in R]
D = {c: E.load_desc("", c, ids, vm) for c in ("full", "upper", "top", "lower")}
SP = E.splits(R, "clean")
rng = np.random.default_rng(0)


def hits(S, sn):
    q, db, excl = SP[sn]
    pos, _, _ = E.gt(R, q, db)
    sim = S(q, db)
    if excl is not None:
        sim = np.where(excl, -9, sim); pos = pos & ~excl
    has = pos.any(1)
    top = sim.argmax(1)
    top5 = np.argsort(-sim, 1)[:, :5]
    return pos[np.arange(len(q)), top][has], np.take_along_axis(pos, top5, 1).any(1)[has]


def mk(crop, dn="dino_vlad"):
    X = D[crop][dn]
    return lambda q, db: X[q] @ X[db].T


def fused(q, db, w=0.5):
    return (1 - w) * (D["full"]["dino_vlad"][q] @ D["full"]["dino_vlad"][db].T) + w * (D["upper"]["dino_vlad"][q] @ D["upper"]["dino_vlad"][db].T)


def fused_ul(q, db):
    return 0.5 * (D["upper"]["dino_vlad"][q] @ D["upper"]["dino_vlad"][db].T) + 0.5 * (D["lower"]["dino_vlad"][q] @ D["lower"]["dino_vlad"][db].T)


methods = {"full": mk("full"), "upper": mk("upper"), "top": mk("top"), "lower": mk("lower"), "full+upper": fused,
           "upper+lower": fused_ul}
groups = {"cross_day(x_22v20+x_20v22)": ["x_22v20", "x_20v22"], "within_10-20": ["within_10-20"],
          "within_10-22": ["within_10-22"], "lodo_10-22": ["lodo_10-22"]}
out = {}
for g, sns in groups.items():
    H = {m: [np.concatenate(x) for x in zip(*[hits(f, sn) for sn in sns])] for m, f in methods.items()}
    n = len(H["full"][0])
    res = {m: {"R@1": float(h[0].mean()), "R@5": float(h[1].mean())} for m, h in H.items()}
    for a, b in [("upper", "lower"), ("full", "upper"), ("full+upper", "full"), ("upper", "top"), ("upper+lower", "full")]:
        d = H[a][0].astype(float) - H[b][0].astype(float)
        bs = [d[rng.integers(0, n, n)].mean() for _ in range(2000)]
        res[f"{a} - {b} (R@1)"] = [float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    res["n"] = n
    out[g] = res
    print(g, "n", n, " ".join(f"{m}:{res[m]['R@1']:.2f}/{res[m]['R@5']:.2f}" for m in methods))
    for k, v in res.items():
        if " - " in k: print("   ", k, f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]")
json.dump(out, open("results/vpr_compare.json", "w"), indent=1)
