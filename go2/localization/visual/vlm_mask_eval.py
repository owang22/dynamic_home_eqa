"""Does masking VLM-labelled movable regions help cross-day retrieval? (task 4a)

Masks: vlm_probe.keep_mask on the 27B's boxes (drop 'movable' + 'person'; variant 'fixedonly' also drops
'rarely_moved'). Masked pixels -> grey before DINOv2 and their tokens are dropped from pooling (desc.py --mask).
Evaluation on the pictures that have VLM output, cross-day splits x_22v20 / x_20v22 (clean GT, 1 m / 30 deg),
unmasked vs masked on the same pictures; paired bootstrap of the R@1 difference.
    python3 vlm_mask_eval.py build      # writes cache/masks_27b_{movable,fixedonly}.npz
    python3 desc.py dino --mask cache/masks_27b_movable.npz --tag _m27 --crops full,upper
    python3 desc.py dino --mask cache/masks_27b_fixedonly.npz --tag _f27 --crops full,upper
    python3 vlm_mask_eval.py eval
"""
import json, sys
from pathlib import Path
import numpy as np
import vcommon as V, vpr_eval as E, vlm_probe as P

HERE = Path(__file__).resolve().parent
R = V.load_records()
vdir = HERE / "cache" / "vlm_27b"
have = [r for r in R if (vdir / f"{r['id']}.json").exists()]

if sys.argv[1] == "build":
    for name, drop in (("movable", ("movable", "person")), ("fixedonly", ("movable", "person", "rarely_moved"))):
        M = {}
        for r in have:
            it = json.loads((vdir / f"{r['id']}.json").read_text())["items"]
            M[r["id"]] = P.keep_mask(it, drop)
        np.savez_compressed(HERE / "cache" / f"masks_27b_{name}.npz", **M)
        print(name, len(M), "mean kept", np.mean([m.mean() for m in M.values()]).round(3),
              "upper kept", np.mean([m[:162].mean() for m in M.values()]).round(3), "lower kept", np.mean([m[198:].mean() for m in M.values()]).round(3))
    sys.exit()

ids = {r["id"] for r in have}
sub = [r for r in R if r["id"] in ids]
sub_ids = [r["id"] for r in sub]
SP = E.splits(sub, "clean")
rng = np.random.default_rng(0)
out = {}
for crop in ("full", "upper"):
    E.RNG = np.random.default_rng(0)
    base = E.load_desc("", crop, sub_ids, [r["day"] in ("10-19", "10-20") for r in sub])["dino_vlad"]
    for tag in ("_m27", "_f27"):
        E.RNG = np.random.default_rng(0)
        Dm = E.load_desc(tag, crop, sub_ids, [r["day"] in ("10-19", "10-20") for r in sub])["dino_vlad"]
        H = {"base": [], "mask": []}
        for sn in ("x_22v20", "x_20v22"):
            q, db, _ = SP[sn]
            for name, S in (("base", base), ("mask", Dm)):
                res, h1, h5, rank, has = E.evaluate(S, sub, q, db, None)
                H[name].append(h1)
                out[f"{crop}|{tag}|{sn}|{name}"] = res
        b = np.concatenate(H["base"]).astype(float); m = np.concatenate(H["mask"]).astype(float)
        d = m - b; n = len(d)
        bs = [d[rng.integers(0, n, n)].mean() for _ in range(2000)]
        out[f"{crop}|{tag}|pooled"] = {"n": n, "R@1_base": b.mean(), "R@1_mask": m.mean(), "diff": d.mean(),
                                         "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
        print(crop, tag, f"n={n} R@1 unmasked {b.mean():.3f} masked {m.mean():.3f} diff {d.mean():+.3f} [{np.percentile(bs,2.5):+.3f}, {np.percentile(bs,97.5):+.3f}]")
json.dump(out, open(HERE / "results" / "vlm_mask_eval.json", "w"), indent=1)
