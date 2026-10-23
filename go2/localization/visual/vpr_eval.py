"""Place-recognition evaluation (task 2).

    python3 vpr_eval.py [--tag ""] [--crops full,upper,top,lower] [--out results/vpr_eval.json]

Descriptors (from desc.py caches): dino_cls, dino_gem, dino_vlad (AnyLoc-style hard VLAD, K=32, vocabulary from
10-19 + 10-20 tokens only, intra- + L2-normalised), siglip.
Splits (trusted frames only, vcommon.load_records):
  lodo_<day>: queries = that day, db = the other two days (cross-day; furniture/people changed)
  within_<day>: queries and db = same day, db frames within 60 s of the query excluded (no near-duplicates)
Positive: db frame within 1.0 m and 30 deg (console poses). Recall@k over queries that have a positive; also
the share of queries with a positive, and random-retrieval R@1 (mean positive share) as chance level.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import vcommon as V

HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(0)
GT_THR = (1.0, 30.0)
YAW_KEY = "yaw_deg"


def vlad_vocab(tok, off, idx, K=32, n=60000):
    import faiss  # noqa
    raise ImportError


def kmeans(x, K=32, iters=25):
    import torch
    x = torch.from_numpy(x).float().cuda()
    c = x[torch.from_numpy(RNG.choice(len(x), K, replace=False)).cuda()]
    for _ in range(iters):
        a = (x @ c.T).argmax(1)
        for k in range(K):
            s = x[a == k]
            if len(s):
                c[k] = torch.nn.functional.normalize(s.mean(0), dim=0)
    return c.cpu().numpy()


def vlad(tok, off, C):
    import torch
    Ct = torch.from_numpy(C).float().cuda()
    out = []
    for i in range(len(off) - 1):
        x = torch.from_numpy(tok[off[i]:off[i + 1]].astype(np.float32)).cuda()
        a = (x @ Ct.T).argmax(1)
        v = torch.zeros_like(Ct)
        v.index_add_(0, a, x - Ct[a])
        v = torch.nn.functional.normalize(v, dim=1).reshape(-1)
        out.append(torch.nn.functional.normalize(v, dim=0).cpu().numpy())
    return np.stack(out)


def load_desc(tag, crop, ids_all, vocab_mask):
    D = {}
    p = HERE / "cache" / f"dino{tag}_{crop}.npz"
    if p.exists():
        z = np.load(p)
        pos = {k: i for i, k in enumerate(z["ids"])}
        order = np.array([pos[i] for i in ids_all])
        D["dino_cls"] = z["cls"][order]
        D["dino_gem"] = z["gem"][order]
        tok, off = z["tok"], z["off"]
        vm = [pos[i] for i, m in zip(ids_all, vocab_mask) if m]
        samp = np.concatenate([tok[off[i]:off[i + 1]][RNG.choice(off[i + 1] - off[i], min(40, off[i + 1] - off[i]), replace=False)] for i in vm])
        C = kmeans(samp.astype(np.float32))
        D["dino_vlad"] = vlad(tok, off, C)[order]
    p = HERE / "cache" / f"siglip{tag}_{crop}.npz"
    if p.exists():
        z = np.load(p)
        pos = {k: i for i, k in enumerate(z["ids"])}
        D["siglip"] = z["vec"][[pos[i] for i in ids_all]]
    return D


def gt(R, qi, di, rad=1.0, deg=30.0):
    rad, deg = GT_THR
    P = np.array([[r["x"], r["y"]] for r in R]); Y = np.array([r[YAW_KEY] for r in R])
    d = np.linalg.norm(P[qi][:, None] - P[di][None], axis=2)
    a = np.abs(V.wrap_deg(Y[qi][:, None] - Y[di][None]))
    return (d <= rad) & (a <= deg), d, a


def splits(R, key="trusted"):
    T = np.array([r["t"] for r in R]); day = np.array([r["day"] for r in R]); tr = np.array([r[key] for r in R])
    out = {}
    days = ["10-19", "10-20", "10-22"]
    for d in days:
        q = np.where(tr & (day == d))[0]; db = np.where(tr & (day != d))[0]
        out[f"lodo_{d}"] = (q, db, None)
    for d in days:
        q = np.where(tr & (day == d))[0]
        excl = np.abs(T[q][:, None] - T[q][None]) < 60
        out[f"within_{d}"] = (q, q, excl)
    # the two days whose map frames agree (10-19 is offset ~0.75 m from both: pos/yaw audit, NOTES section 2)
    out["x_22v20"] = (np.where(tr & (day == "10-22"))[0], np.where(tr & (day == "10-20"))[0], None)
    out["x_20v22"] = (np.where(tr & (day == "10-20"))[0], np.where(tr & (day == "10-22"))[0], None)
    return out


def evaluate(S, R, q, db, excl, ks=(1, 5)):
    pos, dist, ang = gt(R, q, db)
    sim = S[q] @ S[db].T
    if excl is not None:
        sim = np.where(excl, -9, sim); pos = pos & ~excl
    has = pos.any(1)
    rank = np.argsort(-sim, axis=1)
    res = {"n_q": int(len(q)), "share_with_pos": float(has.mean())}
    hits = {}
    for k in ks:
        h = np.take_along_axis(pos, rank[:, :k], 1).any(1)
        hits[k] = h
        res[f"R@{k}"] = float(h[has].mean()) if has.any() else float("nan")
    valid = (~excl).sum(1) if excl is not None else np.full(len(q), len(db))
    res["chance_R@1"] = float((pos.sum(1)[has] / valid[has]).mean())
    top = rank[:, 0]
    res["top1_dist_med"] = float(np.median(dist[np.arange(len(q)), top][has]))
    res["top1_yawerr_med"] = float(np.median(ang[np.arange(len(q)), top][has]))
    return res, hits[1][has], hits[5][has], rank, has


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="")
    ap.add_argument("--crops", default="full,upper,top,lower")
    ap.add_argument("--out", default="results/vpr_eval.json")
    ap.add_argument("--gt", default="trusted", choices=["trusted", "clean", "audited"])
    ap.add_argument("--thr", default="1.0,30")
    a = ap.parse_args()
    global GT_THR, YAW_KEY
    GT_THR = tuple(float(x) for x in a.thr.split(","))
    if a.gt == "audited":
        YAW_KEY = "yaw_audited"
    R = V.load_records()
    ids = [r["id"] for r in R]
    vocab_mask = [r["day"] in ("10-19", "10-20") for r in R]
    SP = splits(R, "clean" if a.gt == "audited" else a.gt)
    results, hitsave = {}, {}
    for crop in a.crops.split(","):
        D = load_desc(a.tag, crop, ids, vocab_mask)
        for dn, S in D.items():
            for sn, (q, db, excl) in SP.items():
                res, h1, h5, rank, has = evaluate(S, R, q, db, excl)
                results[f"{dn}|{crop}|{sn}"] = res
                hitsave[f"{dn}|{crop}|{sn}"] = h1
                np.save(HERE / "cache" / f"rank{a.tag}_{a.gt}_{dn}_{crop}_{sn}.npy" if a.thr == "1.0,30" else f"rank{a.tag}_{a.gt}_{a.thr}_{dn}_{crop}_{sn}.npy", rank[:, :10])
            print(crop, dn, " ".join(f"{sn}:{results[f'{dn}|{crop}|{sn}']['R@1']:.2f}/{results[f'{dn}|{crop}|{sn}']['R@5']:.2f}" for sn in SP), flush=True)
    json.dump(results, open(a.out, "w"), indent=1)
    np.savez(a.out.replace(".json", "_hits.npz"), **{k.replace("|", "__"): v for k, v in hitsave.items()})
    # summary table
    for sn in SP:
        q, db, excl = SP[sn]
        r0 = next(v for k, v in results.items() if k.endswith(sn))
        print(f"{sn}: n_q={r0['n_q']} with_pos={r0['share_with_pos']:.2f} chance R@1={r0['chance_R@1']:.3f}")


if __name__ == "__main__":
    main()
