"""Simulated 'spin and relocalize' (task 5b): group query pictures into spin sets (same session, within 40 s, odom
moved < 0.4 m: the dog turning on the spot), relocalize every picture on its own (refine.py output), then vote.
Consensus = the accepted estimate (inliers >= T) with the most inlier-weighted support from the other accepted
estimates of the set within 0.75 m. Accept the set if >= 2 pictures support it (or a single one with >= 2T inliers).
Compared with single-picture acceptance. Errors vs the console position of the set's first picture.
    python3 spin_sim.py results/refine_x_22v20_full_rfull_lg.json 60
"""
import json, math, sys, collections
import numpy as np
import vcommon as V

path, T = sys.argv[1], int(sys.argv[2])
rows = {r["id"]: r for r in json.load(open(path))}
R = {r["id"]: r for r in V.load_records()}
S = V._sessions()
qs = sorted([R[i] for i in rows], key=lambda r: r["t"])
sets, cur = [], []
for r in qs:
    if r["session"] is None:
        continue
    if cur and (r["session"] != cur[0]["session"] or r["t"] - cur[0]["t"] > 40 or math.hypot(r["x"] - cur[0]["x"], r["y"] - cur[0]["y"]) > 0.4):
        sets.append(cur); cur = []
    cur.append(r)
if cur: sets.append(cur)
sets = [s for s in sets if len(s) >= 3]
res = collections.Counter(); errs_single, errs_spin = [], []
for s in sets:
    est = [(rows[r["id"]], r) for r in s if rows[r["id"]].get("inl", 0) >= T]
    truth = np.array([s[0]["x"], s[0]["y"]])
    # single picture: the first picture of the set alone
    f = rows[s[0]["id"]]
    if f.get("inl", 0) >= T:
        e = math.hypot(*(np.array(f["pos_w"]) - truth)); errs_single.append(e)
        res["single_accepted"] += 1; res["single_correct"] += e <= 1.0
    # any picture of the set alone (best inliers) -- what 'take the best of N' gives
    if est:
        b = max(est, key=lambda x: x[0]["inl"])[0]
        e = math.hypot(*(np.array(b["pos_w"]) - truth)); res["bestofN_accepted"] += 1; res["bestofN_correct"] += e <= 1.0
    # voting
    if est:
        P = np.array([x[0]["pos_w"] for x in est]); W = np.array([x[0]["inl"] for x in est], float)
        sup = [(W[np.linalg.norm(P - P[i], axis=1) <= 0.75].sum(), (np.linalg.norm(P - P[i], axis=1) <= 0.75).sum(), i) for i in range(len(P))]
        wsum, n, i = max(sup)
        ok = n >= 2 or W[i] >= 2 * T
        if ok:
            m = np.linalg.norm(P - P[i], axis=1) <= 0.75
            c = (P[m] * W[m, None]).sum(0) / W[m].sum()
            e = math.hypot(*(c - truth)); errs_spin.append(e)
            res["spin_accepted"] += 1; res["spin_correct"] += e <= 1.0
res["sets"] = len(sets)
res["mean_set_size"] = float(np.mean([len(s) for s in sets]))
out = dict(res)
for k in ("single", "bestofN", "spin"):
    out[f"{k}_coverage"] = res[f"{k}_accepted"] / len(sets)
    out[f"{k}_precision"] = res[f"{k}_correct"] / max(1, res[f"{k}_accepted"])
out["single_err_med"] = float(np.median(errs_single)) if errs_single else None
out["spin_err_med"] = float(np.median(errs_spin)) if errs_spin else None
out["spin_err_p90"] = float(np.percentile(errs_spin, 90)) if errs_spin else None
print(path.split("/")[-1], f"T={T}", json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in out.items()}))
