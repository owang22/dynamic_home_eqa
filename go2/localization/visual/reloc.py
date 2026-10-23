"""Relocalize from camera: a prototype of the routine proposed in REPORT.md (offline; never talks to the console).

    python3 reloc.py --selftest                    # 10-22 spin sets against a 10-20 database, with timing
    python3 reloc.py --query a.jpg b.jpg c.jpg [--odom_yaw 0 60 120]   # pictures from one spin, db = clean pictures

Per picture: DINOv2-VLAD (full frame) top-10 from the database -> SuperPoint+LightGlue + essential matrix (effective
K) -> pose = verified db picture's pose (+ the relative yaw); position = inlier-weighted mean of up to 3 verified db
pictures within 1.5 m. Across the pictures of one spin: take the estimate with the most inliers; 'support' =
other pictures whose estimate lies within 0.75 m (and, when odom yaws are given, whose yaw agrees within 15 deg after
removing the odom turn between captures). Confidence from the precision/coverage curves (results/refine_curves.json):
  high   : >= 200 inliers, or >= 150 with support >= 1     (cross-day precision ~0.9-1.0)
  medium : >= 100 inliers                                    (~0.85-0.9)
  low    : otherwise -> do not use; let the lidar matcher search globally
The proposal is meant to seed / confirm the lidar matcher, not to replace it.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

import vcommon as V
import desc
import geo_lg
import refine

HERE = Path(__file__).resolve().parent


class DB:
    def __init__(self, records):
        self.R = records
        ids = [r["id"] for r in records]
        allR = V.load_records()
        allids = [r["id"] for r in allR]
        import vpr_eval as E
        D = E.load_desc("", "full", allids, [r["day"] in ("10-19", "10-20") for r in allR])["dino_vlad"]
        pos = {k: i for i, k in enumerate(allids)}
        self.X = D[[pos[i] for i in ids]]
        # VLAD vocabulary for new pictures: rebuild exactly as vpr_eval did (same RNG seed and sample)
        E.RNG = np.random.default_rng(0)
        z = np.load(HERE / "cache" / "dino_full.npz")
        tok, off = z["tok"], z["off"]
        zpos = {k: i for i, k in enumerate(z["ids"])}
        vm = [zpos[r["id"]] for r in allR if r["day"] in ("10-19", "10-20")]
        samp = np.concatenate([tok[off[i]:off[i + 1]][E.RNG.choice(off[i + 1] - off[i], min(40, off[i + 1] - off[i]), replace=False)] for i in vm])
        self.C = E.kmeans(samp.astype(np.float32))
        self.E = E
        self.model = None

    def vlad(self, path):
        import timm
        if self.model is None:
            self.model = timm.create_model("vit_large_patch14_reg4_dinov2.lvd142m", pretrained=True, num_classes=0,
                                           dynamic_img_size=True).cuda().half().eval()
        im = desc.load_rgb(path).astype(np.float32) / 255.0
        import cv2
        im = cv2.resize(im, (644, 364), interpolation=cv2.INTER_AREA)
        x = torch.from_numpy(((im - desc.MEAN) / desc.STD).transpose(2, 0, 1)[None]).float().cuda().half()
        with torch.no_grad():
            f = self.model.forward_features(x).float()
        p = torch.nn.functional.normalize(f[0, self.model.num_prefix_tokens:], dim=-1).cpu().numpy().astype(np.float16)
        return self.E.vlad(p, np.array([0, len(p)]), self.C)[0]


def relocalize_one(db, path, k=10, vec=None):
    q = {"id": "q_" + Path(path).stem, "path": str(path)}
    v = db.vlad(path) if vec is None else vec
    top = np.argsort(-(db.X @ v))[:k]
    cands = [(int(j), geo_lg.rel_pose(db.R[j], q)) for j in top]
    est = refine.estimate(db.R, None, cands, 25)
    return est


def combine(ests, odom_yaw=None):
    ok = [(i, e) for i, e in enumerate(ests) if e]
    if not ok:
        return {"confidence": "none"}
    i0, best = max(ok, key=lambda x: x[1]["inl"])
    p0 = np.array(best["pos_w"])
    sup = 0
    for i, e in ok:
        if i == i0 or e["inl"] < 50:
            continue
        if np.linalg.norm(np.array(e["pos_w"]) - p0) > 0.75:
            continue
        if odom_yaw is not None:
            # yaw of capture i predicted from the best one plus the odom turn between them
            pred = best["yaw_w"] + (odom_yaw[i] - odom_yaw[i0])
            if abs(V.wrap_deg(e["yaw_w"] - pred)) > 15:
                continue
        sup += 1
    conf = "high" if best["inl"] >= 200 or (best["inl"] >= 150 and sup >= 1) else "medium" if best["inl"] >= 100 else "low"
    return {"x": best["pos_w"][0], "y": best["pos_w"][1], "yaw_deg": best["yaw_w"], "picture": i0, "inliers": best["inl"],
            "support": sup, "n_pictures": len(ests), "second_far_inliers": best["second_far_inl"], "confidence": conf,
            "db_picture": best["best"]}


def selftest():
    R = V.load_records()
    dbR = [r for r in R if r["clean"] and r["day"] == "10-20"]
    t0 = time.time(); db = DB(dbR); t_build = time.time() - t0
    qs = sorted([r for r in R if r["clean"] and r["day"] == "10-22" and r["session"]], key=lambda r: r["t"])
    sets, cur = [], []
    for r in qs:
        if cur and (r["session"] != cur[0]["session"] or r["t"] - cur[0]["t"] > 40 or math.hypot(r["x"] - cur[0]["x"], r["y"] - cur[0]["y"]) > 0.4):
            sets.append(cur); cur = []
        cur.append(r)
    sets = [s for s in sets if len(s) >= 3]
    S = V._sessions()
    out, lat = [], []
    for s in sets:
        tt, od, _ = S[s[0]["session"]]
        oy = [math.degrees(od[min(np.searchsorted(tt, r["t"]), len(tt) - 1), 3]) for r in s]
        t1 = time.time()
        ests = [relocalize_one(db, r["path"]) for r in s]
        res = combine(ests, oy)
        lat.append((time.time() - t1) / len(s))
        truth = s[0]
        if res["confidence"] != "none":
            res["err_m"] = math.hypot(res["x"] - truth["x"], res["y"] - truth["y"])
            res["err_yaw_vs_console"] = abs(float(V.wrap_deg(res["yaw_deg"] - [r for r in s][res["picture"]]["yaw_deg"])))
        res["has_db_neighbour"] = any(math.hypot(d["x"] - truth["x"], d["y"] - truth["y"]) <= 1.0 for d in dbR)
        out.append(res)
    summ = {"db_pictures": len(dbR), "db_build_s": round(t_build, 1), "spin_sets": len(sets),
            "latency_per_picture_s": round(float(np.median(lat)), 2)}
    for c in ("high", "medium", "low", "none"):
        rr = [o for o in out if o["confidence"] == c]
        summ[c] = {"n": len(rr), "within_1m": sum(o.get("err_m", 9) <= 1.0 for o in rr),
                   "err_m_med": round(float(np.median([o["err_m"] for o in rr])), 2) if rr and c != "none" else None,
                   "with_db_neighbour": sum(o["has_db_neighbour"] for o in rr)}
    print(json.dumps(summ, indent=1))
    json.dump({"summary": summ, "sets": out}, open(HERE / "results" / "reloc_selftest.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--query", nargs="*")
    ap.add_argument("--odom_yaw", nargs="*", type=float)
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        db = DB([r for r in V.load_records() if r["clean"]])
        ests = [relocalize_one(db, p) for p in a.query]
        print(json.dumps(combine(ests, a.odom_yaw), indent=1))
