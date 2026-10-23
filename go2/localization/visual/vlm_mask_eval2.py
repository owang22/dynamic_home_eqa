"""Masking test on the pictures the 27B labelled before the shared VLM went down (146 of 10-20, 12 of 10-22):
within 10-20, db = other sessions only (11:xx vs 19:xx, ~7 h apart: chairs, bags and people moved) and db = any
picture > 60 s away. Unmasked vs masked (movable+person removed; or only fixed kept), same pictures, same GT.
    python3 vlm_mask_eval2.py -> results/vlm_mask_eval2.json
"""
import json
from pathlib import Path
import numpy as np
import vcommon as V, vpr_eval as E

HERE = Path(__file__).resolve().parent
R = V.load_records()
sub = [r for r in R if (HERE / "cache" / "vlm_27b" / f"{r['id']}.json").exists() and r["clean"] and r["day"] == "10-20"]
ids = [r["id"] for r in sub]
T = np.array([r["t"] for r in sub]); ses = np.array([str(r["session"]) for r in sub])
q = np.arange(len(sub))
variants = {"other_session": (ses[:, None] == ses[None]), "any_60s": np.abs(T[:, None] - T[None]) < 60}
rng = np.random.default_rng(0)
out = {}
for crop in ("full", "upper"):
    D = {}
    for tag in ("", "_m27", "_f27"):
        E.RNG = np.random.default_rng(0)
        D[tag] = E.load_desc(tag, crop, ids, [True] * len(sub))["dino_vlad"]
    for vn, excl in variants.items():
        H = {}
        for tag, S in D.items():
            res, h1, h5, rank, has = E.evaluate(S, sub, q, q, excl | np.eye(len(q), dtype=bool))
            H[tag] = (h1.astype(float), h5.astype(float)); out[f"{crop}|{vn}|{tag or 'unmasked'}"] = res
        n = len(H[""][0])
        line = f"{crop:5s} {vn:13s} n={n} R@1/R@5 unmasked {H[''][0].mean():.2f}/{H[''][1].mean():.2f}"
        for tag in ("_m27", "_f27"):
            d = H[tag][0] - H[""][0]
            bs = [d[rng.integers(0, n, n)].mean() for _ in range(2000)]
            out[f"{crop}|{vn}|{tag}|diff"] = [float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            line += f" | {'movable masked' if tag == '_m27' else 'fixed only'} {H[tag][0].mean():.2f}/{H[tag][1].mean():.2f} (R@1 {d.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}])"
        print(line)
json.dump(out, open(HERE / "results" / "vlm_mask_eval2.json", "w"), indent=1)
