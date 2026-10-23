"""Semantic text fingerprint as a coarse place prior (task 4b).

Fingerprint of a picture = bag of '<colour> <name>' phrases + single words (TF-IDF, cosine) from
  all     : every object in the stored description (lab_agent memory 'seen', written by the 27B for search)
  static  : only objects whose name is building / heavy furniture (STATIC words) or that are on a wall/ceiling
  vlm27b  : names the permanence probe marked fixed / rarely_moved (only for pictures in cache/vlm_27b)
Evaluated like vpr_eval (clean GT; positives 1 m / 30 deg and 2 m / 45 deg), on the cross-day splits.
    python3 text_fp.py -> results/text_fp.json
"""
import json, math, re
from pathlib import Path
import numpy as np
import vcommon as V, vpr_eval as E

STATIC = {"door", "doors", "door frame", "wall", "whiteboard", "window", "windows", "ceiling", "light", "ceiling light",
          "vent", "pipe", "fire extinguisher", "fire alarm", "tv", "television", "cabinet", "filing cabinet", "shelf",
          "shelving unit", "bookshelf", "desk", "sofa", "couch", "refrigerator", "fridge", "printer", "water dispenser",
          "water cooler", "drawer unit", "locker", "sink", "counter", "workbench", "table", "podium", "lectern",
          "camera", "security camera", "exit sign", "sign", "poster", "clock", "outlet", "microwave", "rack", "metal rack"}


def words(s):
    return re.findall(r"[a-z]+", s.lower())


def phrases(objs, keep):
    out = []
    for o in objs:
        if not keep(o):
            continue
        n = o["name"].lower().strip()
        c = (o.get("colour") or "").lower().strip()
        out += [f"N:{n}", f"CN:{c} {n}"] + [f"W:{w}" for w in words(n)]
    return out


def is_static(o):
    n = o["name"].lower().strip(); on = (o.get("on") or "").lower()
    return n in STATIC or any(n.endswith(" " + s) for s in STATIC) or on in ("wall", "ceiling")


def tfidf(docs):
    vocab = {}
    for d in docs:
        for t in set(d):
            vocab[t] = vocab.get(t, 0) + 1
    idx = {t: i for i, t in enumerate(vocab)}
    N = len(docs)
    X = np.zeros((N, len(idx)), np.float32)
    for i, d in enumerate(docs):
        for t in d:
            X[i, idx[t]] += 1
    X = np.log1p(X) * np.log((1 + N) / (1 + np.array([vocab[t] for t in idx])))[None]
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    return X


def main():
    R = V.load_records()
    vdir = V.HERE / "cache" / "vlm_27b"
    docs = {
        "all": [phrases((r.get("seen") or {}).get("objects", []), lambda o: True) for r in R],
        "static": [phrases((r.get("seen") or {}).get("objects", []), is_static) for r in R],
    }
    have27 = [(vdir / f"{r['id']}.json").exists() for r in R]
    docs["vlm27b"] = [phrases([{"name": i["name"], "colour": ""} for i in json.loads((vdir / f"{r['id']}.json").read_text())["items"]
                               if i["permanence"] in ("fixed", "rarely_moved")], lambda o: True) if h else [] for r, h in zip(R, have27)]
    SP = E.splits(R, "clean")
    out = {}
    for thr in ((1.0, 30.0), (2.0, 45.0)):
        E.GT_THR = thr
        for name, d in docs.items():
            S = tfidf(d)
            for sn in ("x_22v20", "x_20v22", "within_10-20"):
                q, db, excl = SP[sn]
                if name == "vlm27b":
                    h = np.array(have27)
                    q = q[h[q]]; db = db[h[db]]
                    if excl is not None:
                        excl = None if len(q) == 0 else (np.abs(np.array([R[i]["t"] for i in q])[:, None] - np.array([R[i]["t"] for i in db])[None]) < 60)
                    if len(q) < 10:
                        continue
                res, h1, h5, rank, has = E.evaluate(S, R, q, db, excl, ks=(1, 5))
                # R@10 as a prior: is a true neighbour among the 10 best?
                pos, _, _ = E.gt(R, q, db)
                sim = S[q] @ S[db].T
                if excl is not None:
                    sim = np.where(excl, -9, sim); pos = pos & ~excl
                r10 = np.take_along_axis(pos, np.argsort(-sim, 1)[:, :10], 1).any(1)[pos.any(1)].mean()
                res["R@10"] = float(r10)
                out[f"{name}|{sn}|{thr[0]}m"] = res
                print(f"{name:7s} {sn:13s} {thr[0]:.0f}m/{thr[1]:.0f}: n_q {res['n_q']:4d} R@1 {res['R@1']:.2f} R@5 {res['R@5']:.2f} R@10 {r10:.2f} (chance R@1 {res['chance_R@1']:.3f})")
    json.dump(out, open("results/text_fp.json", "w"), indent=1)


if __name__ == "__main__":
    main()
