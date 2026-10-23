"""Why is within-day recall on 10-22 lower than cross-day? Diagnostics on the full-frame DINOv2 VLAD ranking."""
import numpy as np, collections
import vcommon as V, vpr_eval as E
R = V.load_records(); ids = [r["id"] for r in R]
D = E.load_desc("", "full", ids, [r["day"] in ("10-19", "10-20") for r in R])
S = D["dino_vlad"]
SP = E.splits(R)
for sn in ["within_10-20", "within_10-22", "lodo_10-22"]:
    q, db, excl = SP[sn]
    res, h1, h5, rank, has = E.evaluate(S, R, q, db, excl)
    pos, dist, ang = E.gt(R, q, db)
    top = rank[:, 0]
    d1 = dist[np.arange(len(q)), top]; a1 = ang[np.arange(len(q)), top]
    sim = (S[q] * S[db[top]]).sum(1)
    hi = sim > np.percentile(sim, 75)
    print(sn, "R@1", round(res["R@1"], 2), "| top1 dist med", np.median(d1).round(2), "p75", np.percentile(d1, 75).round(2),
          "| high-sim quartile: dist med", np.median(d1[hi]).round(2), "yaw med", np.median(a1[hi]).round(1),
          "share >1m", (d1[hi] > 1).mean().round(2))
    src = collections.Counter((R[q[i]]["source"], bool(h)) for i, h in zip(np.where(has)[0], h1))
    print("   by source (source, hit@1):", dict(src))
    sess = collections.Counter((R[q[i]]["session"] == R[db[top[i]]]["session"]) for i in range(len(q)))
    print("   top1 same session:", dict(sess))
    # failures with high similarity but far away -> pose inconsistency candidates
    f = [(sim[i], d1[i], a1[i], R[q[i]]["id"], R[db[top[i]]]["id"]) for i in range(len(q)) if has[i] and not pos[i, top[i]]]
    f.sort(reverse=True)
    for x in f[:6]: print("   fail", np.round(x[:3], 2), x[3:], R[ids.index(x[3])]["time"][-5:], R[ids.index(x[4])]["time"][-5:])
