"""Size check: every model household A uses, as placed (after the renderer's scaling), against a
typical size for its type (typical_sizes_v3.json, from typical_sizes.py).

    ~/miniconda3/envs/dynamic_eqa/bin/python model_sizes_v3.py v2|v3

For each distinct (type, model): the model's box sides (sorted, cm) and the typical sides.
ratio_longest = model longest side / typical longest side; ratio_middle the same for the
middle side. Flagged when either ratio is over 1.8 or under 1/1.8. The middle side catches
wrong shapes (an open umbrella, a crate for a parcel) that the longest side misses; a flag
on the middle side alone is often a shape the model is drawn in (a pair of shoes, a coiled
belt) and is fixed only when the picture showed it was wrong (model_check_v3.py).

Writes run_v3/size_check_<v>.json and run_v3/size_check_<v>.md (a table of flagged rows).
"""
from __future__ import annotations

import json
import sys

import lib_v3
import lib

FLAG = 1.8


def main():
    ver = sys.argv[1]
    cls = lib.SnapshotHomeV2 if ver == "v2" else lib_v3.SnapshotHomeV3
    home = lib.open_home(lib.snapshot_path(4, "1000"), home_class=cls)
    home.add_objects()
    typical = json.loads((lib_v3.RENDER / "typical_sizes_v3.json").read_text())["types"]
    rows, seen = [], set()
    for oid in sorted(home.snap["objects"]):
        rec = home.records[oid]
        m = rec["model"] or {}
        if not m.get("size_m"):
            continue
        key = (rec["type"], m["id"])
        if key in seen:
            continue
        seen.add(key)
        dims = sorted((100 * v for v in m["size_m"]), reverse=True)
        t = typical[rec["type"]]["dims_cm"]
        r1, r2 = dims[0] / t[0], dims[1] / t[1]
        flag = [w for w, r in (("longest", r1), ("middle", r2)) if r > FLAG or r < 1 / FLAG]
        rows.append({"type": rec["type"], "model": m["id"], "looks_like": m.get("looks_like"),
                     "source": m.get("source"), "model_cm": [round(d, 1) for d in dims], "typical_cm": t,
                     "typical_from": typical[rec["type"]]["source"], "ratio_longest": round(r1, 2),
                     "ratio_middle": round(r2, 2), "flag": flag,
                     "v3_change": (rec.get("model_change") or {}).get("rule", {}).get("why")})
    out = lib_v3.RENDER / "run_v3"
    lib.json_dump({"version": ver, "flag_ratio": FLAG, "rows": rows}, out / f"size_check_{ver}.json")
    lines = [f"# Size check ({ver}): flagged models (ratio over {FLAG} or under 1/{FLAG})", "",
             "| type | model | model cm | typical cm | longest x | middle x | flag |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["flag"]:
            lines.append(f"| {r['type']} | {str(r['looks_like'])[:30]} | {' x '.join(f'{d:g}' for d in r['model_cm'])} | "
                         f"{' x '.join(f'{d:g}' for d in r['typical_cm'])} ({r['typical_from']}) | {r['ratio_longest']} | "
                         f"{r['ratio_middle']} | {', '.join(r['flag'])} |")
    (out / f"size_check_{ver}.md").write_text("\n".join(lines) + "\n")
    print(ver, len(rows), "models;", sum(1 for r in rows if "longest" in r["flag"]), "flagged on the longest side;",
          sum(1 for r in rows if r["flag"]), "on either")


if __name__ == "__main__":
    sys.exit(main())
