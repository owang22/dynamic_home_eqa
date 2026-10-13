"""Counts over every rendered snapshot -> PICS/summary.json, and a short printout.

    ~/miniconda3/envs/dynamic_eqa/bin/python summarize.py
"""
import json
from collections import Counter, defaultdict

import numpy as np

import lib

files = sorted(lib.PICS.glob("day_*/*/truth.json"))
times, per_snap = [], []
leaks = defaultdict(set)
never_seen_open = Counter()
not_placed_why = Counter()
visible_px_on_spot, visible_px_off_spot = [], []
spot_visible = defaultdict(list)
for f in files:
    t = json.load(f.open())
    key = f"day {t['day']:02d} {t['time']}"
    times.append(t["timings"]["total_s"])
    per_snap.append({"snapshot": key, **t["summary"], "total_s": t["timings"]["total_s"]})
    for x in t["hidden_in_snapshot_but_visible"]:
        leaks[(x["object"], x["place"])].add(key)
    for x in t["placed_not_hidden_in_no_picture"]:
        never_seen_open[(x["object"], x["place"], x["why"][:30])] += 1
    for x in t["not_placed"]:
        not_placed_why[x["why"].split(":")[0].split(" mara")[0].split(" julian")[0][:60]] += 1
    for spot, p in t["pictures"].items():
        spot_visible[spot].append(p["visible_objects_on_this_spot"])
        for o in p["objects"]:
            if o["visible"] and not o["hidden_in_snapshot"]:
                (visible_px_on_spot if o["on_this_spot"] else visible_px_off_spot).append(o["pixels"])


def q(v):
    return {f"p{p}": int(np.percentile(v, p)) for p in (10, 25, 50, 75, 90)} if v else {}


on, off = np.array(visible_px_on_spot), np.array(visible_px_off_spot)
out = {
    "snapshots": len(files),
    "seconds_per_snapshot": {"mean": round(float(np.mean(times)), 1), "min": min(times), "max": max(times)},
    "visible_not_hidden_pixel_counts": {
        "on_this_spot": {"n": len(on), **q(visible_px_on_spot),
                         "share_under_300px": round(float((on < 300).mean()), 3)},
        "elsewhere_in_picture": {"n": len(off), **q(visible_px_off_spot),
                                 "share_under_300px": round(float((off < 300).mean()), 3)},
    },
    "not_placed_reasons_over_all_snapshots": dict(not_placed_why.most_common()),
    "hidden_but_visible_objects": [{"object": o, "place": p, "snapshots": len(s)}
                                   for (o, p), s in sorted(leaks.items(), key=lambda kv: -len(kv[1]))],
    "placed_open_never_visible": [{"object": o, "place": p, "why": w, "snapshots": n}
                                  for (o, p, w), n in never_seen_open.most_common()],
    "mean_visible_on_spot_per_picture": {s: round(float(np.mean(v)), 2) for s, v in sorted(spot_visible.items())},
    "per_snapshot": per_snap,
}
lib.json_dump(out, lib.PICS / "summary.json")
print(json.dumps({k: v for k, v in out.items() if k not in ("per_snapshot", "mean_visible_on_spot_per_picture",
                                                             "placed_open_never_visible", "hidden_but_visible_objects")}, indent=1))
print("hidden but visible:", len(out["hidden_but_visible_objects"]))
for x in out["hidden_but_visible_objects"][:25]:
    print("  ", x)
print("placed, not hidden, in no picture (object/place pairs):", len(out["placed_open_never_visible"]))
for x in out["placed_open_never_visible"][:25]:
    print("  ", x)
cols = ["placed", "not_placed", "placed_overlapping_or_overhanging", "placed_not_hidden_in_no_picture",
        "hidden_in_snapshot_but_visible", "visible_somewhere"]
for c in cols:
    v = [s[c] for s in per_snap]
    print(f"{c}: mean {np.mean(v):.1f} min {min(v)} max {max(v)}")
