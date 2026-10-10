"""For every object type in the snapshot, list the candidate 3D models on disk, and choose
Objaverse (LVIS) models to download for the types nothing on disk covers.

Writes checks/model_candidates.json and checks/lvis_to_download.json.
    ~/miniconda3/bin/python resolve_models.py            (base env: has the objaverse package)
    ~/miniconda3/bin/python resolve_models.py --download
"""
import csv
import glob
import gzip
import json
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from type_table import T  # noqa: E402

HSSD = pathlib.Path("/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab")
PROPS = pathlib.Path("/home/oliver/robot/dynamic_home_eqa_archive/data/objects/external_props")
ASKED = pathlib.Path("/home/oliver/robot/dynamic_home_eqa/prior_work/src/rendered_look/asked_about_models.json")
CACHE = pathlib.Path("/mnt/nvme/oliver/robot/objaverse_cache/hf-objaverse-v1")
MINE = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/habitat_hssd/objaverse/hf-objaverse-v1")
OUT = pathlib.Path(__file__).resolve().parents[1] / "checks"
SNAPSHOT = pathlib.Path("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json")
PER_SOURCE = 6
LVIS_PER_TYPE = 3


def hssd_rows():
    have = {os.path.basename(p)[:-4]: p for p in glob.glob(str(HSSD / "objects/*/*.glb"))}
    rows = []
    for r in csv.DictReader((HSSD / "semantics/objects.csv").open()):
        if r["id"] not in have:
            continue
        try:
            dims = [float(x) for x in r["aligned.dims"].split(",")]
        except ValueError:
            continue
        rows.append({"id": r["id"], "text": (r["wnsynsetkey"] + " | " + r["name"]).lower(),
                     "name": r["name"], "dims": dims, "mesh": have[r["id"]]})
    return rows


def main():
    snap = json.load(SNAPSHOT.open())
    counts = {}
    for o in snap["objects"].values():
        counts[o["type"]] = counts.get(o["type"], 0) + 1
    asked = json.load(ASKED.open())
    props = json.load((PROPS / "mapping.json").open())
    rows = hssd_rows()
    lvis = json.load(gzip.open(CACHE / "lvis-annotations.json.gz"))
    out, want_lvis = {}, {}
    for typ, (size, sources) in T.items():
        cands = []
        for src in sources:
            sub = src.startswith("sub:")
            s = src[4:] if sub else src
            kind, arg = s.split(":", 1)
            if kind == "asked":
                for m in asked[arg]:
                    cands.append({"source": "asked", "id": m["id"], "mesh": m["mesh"], "scale": m["scale"],
                                  "looks_like": m["looks_like"], "size_m": m["size_m"], "sub": sub})
            elif kind == "props":
                for m in [m for m in props if m["category"] == arg][:PER_SOURCE]:
                    cfg = json.load((PROPS / "configs" / f"{m['uid']}.object_config.json").open())
                    cands.append({"source": "props", "id": m["uid"], "config": str(PROPS / "configs" / f"{m['uid']}.object_config.json"),
                                  "mesh": str((PROPS / "configs" / cfg["render_asset"]).resolve()),
                                  "scale": cfg.get("scale", [1.0])[0], "looks_like": " ".join(m.get("tags", [])) or m["uid"], "sub": sub})
            elif kind == "hssd":
                rx = re.compile(arg)
                hits = [r for r in rows if rx.search(r["text"]) and 0.35 * size <= max(r["dims"]) <= 2.2 * size]
                hits.sort(key=lambda r: abs(max(r["dims"]) - size))
                for r in hits[:PER_SOURCE]:
                    cands.append({"source": "hssd", "id": r["id"], "mesh": r["mesh"], "scale": 1.0,
                                  "looks_like": r["name"], "size_m": r["dims"], "sub": sub})
            elif kind == "lvis":
                want_lvis.setdefault(typ, []).append((arg, sub))
        out[typ] = {"count_in_snapshot": counts[typ], "size_m": size, "candidates": cands,
                    "lvis_categories": [a for a, _ in want_lvis.get(typ, [])],
                    "lvis_is_stand_in": any(s for _, s in want_lvis.get(typ, []))}
    # LVIS picks: only for types with no candidate on disk
    need = {t: v for t, v in want_lvis.items() if not out[t]["candidates"]}
    print(f"{len(T)} types; {sum(1 for v in out.values() if v['candidates'])} have a model on disk; "
          f"{len(need)} need Objaverse; {sum(1 for t in T if not out[t]['candidates'] and t not in need)} have no source at all")
    picks = {}
    if need:
        import objaverse
        objaverse._VERSIONED_PATH = str(MINE)
        MINE.mkdir(parents=True, exist_ok=True)
        for f in ("lvis-annotations.json.gz", "object-paths.json.gz"):
            if not (MINE / f).exists():
                os.symlink(CACHE / f, MINE / f)
        if not (MINE / "metadata").exists():
            os.symlink(CACHE / "metadata", MINE / "metadata")
        uids = sorted({u for v in need.values() for cat, _ in v for u in lvis[cat]})
        meta = objaverse.load_annotations(uids)
        for typ, cats in need.items():
            ranked = []
            for cat, sub in cats:
                for u in lvis[cat]:
                    m = meta.get(u, {})
                    faces = m.get("faceCount") or 0
                    if not 200 <= faces <= 150000 or m.get("animationCount", 0):
                        continue
                    # LVIS labels are noisy (earplugs -> "Stylized Rocks"): prefer a model whose
                    # own name or tags contain a word of the type or of the category
                    words = {w for w in re.split(r"[^a-z]+", (typ + " " + cat).lower()) if len(w) >= 3}
                    words |= {w[:-1] for w in words if w.endswith("s")}
                    text = ((m.get("name") or "") + " " + " ".join(t["name"] for t in m.get("tags", []))).lower()
                    named = any(re.search(r"\b" + re.escape(w), text) for w in words)
                    ranked.append((not named, -(m.get("likeCount") or 0), faces, u, cat, sub, m.get("license"), m.get("name"), named))
            ranked.sort()
            picks[typ] = [{"uid": u, "lvis": c, "sub": s, "license": lic, "name": n, "faces": f, "name_matches": nm}
                          for _, _, f, u, c, s, lic, n, nm in ranked[:LVIS_PER_TYPE]]
    (OUT / "model_candidates.json").write_text(json.dumps(out, indent=1))
    (OUT / "lvis_to_download.json").write_text(json.dumps(picks, indent=1))
    if "--download" in sys.argv:
        import objaverse
        objaverse._VERSIONED_PATH = str(MINE)
        uids = sorted({p["uid"] for v in picks.values() for p in v})
        t0 = time.time()
        paths = objaverse.load_objects(uids, download_processes=8)
        took = time.time() - t0
        size = sum(os.path.getsize(p) for p in paths.values())
        print(f"downloaded {len(paths)} of {len(uids)} in {took:.0f} s, {size / 1e9:.2f} GB")
        (OUT / "lvis_downloaded.json").write_text(json.dumps(
            {"paths": paths, "seconds": took, "bytes": size, "asked": len(uids)}, indent=1))


if __name__ == "__main__":
    main()
