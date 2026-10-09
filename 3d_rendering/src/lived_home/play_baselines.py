"""Simple methods playing the same search task as a person (lived_home.play).

Each method sees the same patrol notes and has the same looks as the player. It
walks to pieces of furniture in its own order, and stops when the thing asked
for is visible there (it recognises it perfectly, unlike a person or a camera).
If it has not seen it after the last look, it answers "can't tell". It does
not answer without seeing, so questions about things put away or carried are
never right for it; those are reported separately.

- nearest: no memory; always the nearest piece of furniture not yet looked at
- last seen: first where a patrol last saw the thing (any thing that fits the
  question), then nearest
- most often: furniture ranked by how many patrols saw the thing there, then
  nearest

The robot starts at the entrance and carries on from wherever the previous
question ended, as the player's robot does.

Usage: python -m lived_home.play_baselines <run>/play/play_data.json
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import sys


def positions(data: dict) -> dict:
    return {f["key"]: (f["x"], f["z"]) for f in data["layout"]["furniture"] if f["x"] is not None}


def entry(data: dict, pos: dict):
    spot = data["layout"]["entry"]
    for f in data["layout"]["furniture"]:
        if any(s["id"] == spot for s in f["spots"]):
            return pos.get(f["key"])
    return next(iter(pos.values()))


def seen_counts(data: dict, q: dict) -> tuple[dict, dict]:
    """Patrol sightings before the question of any thing it accepts."""
    count, last = collections.Counter(), {}
    for p in data["patrols"]:
        if (p["day"], p["time"]) >= (q["day"], q["time"]):
            break
        for s in p["seen"]:
            if set(s["oids"]) & set(q["accept"]):
                count[s["furniture"]] += 1
                last["f"] = s["furniture"]
    return count, last.get("f")


def play(data: dict, method: str) -> list:
    pos = positions(data)
    at = entry(data, pos)
    rows = []
    for q in data["questions"]:
        count, last = seen_counts(data, q)
        if method == "last seen":
            first = [last] if last else []
        elif method == "most often":
            first = [f for f, _ in count.most_common()]
        else:
            first = []
        looked, metres, found = [], 0.0, False
        for _ in range(data["rules"]["max_looks"]):
            todo = [f for f in first if f not in looked and f in pos]
            if todo:
                f = todo[0]
            else:
                rest = [f for f in pos if f not in looked]
                if not rest:
                    break
                f = min(rest, key=lambda k: math.dist(at, pos[k]))
            metres += math.dist(at, pos[f])
            at = pos[f]
            looked.append(f)
            if any(t["oid"] in q["accept"] for t in q["looks"].get(f, [])):
                found = True
                break
        kinds = {a["kind"] for a in q["answer"].values()}
        rows.append({"n": q["n"], "kind": q["kind"], "visible": "visible" in kinds, "found": found,
                     "looks": len(looked), "metres": round(metres, 1)})
    return rows


def summary(rows: list) -> dict:
    vis = [r for r in rows if r["visible"]]
    return {"questions": len(rows), "visible": len(vis),
            "found": sum(r["found"] for r in vis),
            "looks_when_found": round(sum(r["looks"] for r in vis if r["found"]) / max(1, sum(r["found"] for r in vis)), 1),
            "metres": round(sum(r["metres"] for r in rows), 1)}


def main() -> None:
    path = pathlib.Path(sys.argv[1])
    data = json.loads(path.read_text())
    out = {m: play(data, m) for m in ("nearest", "last seen", "most often")}
    res = {m: {"summary": summary(r), "rows": r} for m, r in out.items()}
    (path.parent / "baselines.json").write_text(json.dumps(res, indent=1))
    by_kind = collections.defaultdict(dict)
    for m, r in out.items():
        for k in sorted({x["kind"] for x in r}):
            xs = [x for x in r if x["kind"] == k and x["visible"]]
            by_kind[k][m] = f"{sum(x['found'] for x in xs)}/{len(xs)}" if xs else "-"
    print("method | found (of visible) | looks when found | metres walked")
    for m, r in res.items():
        s = r["summary"]
        print(f"{m:11s} | {s['found']}/{s['visible']} | {s['looks_when_found']} | {s['metres']}")
    print("by question kind (found / visible):")
    for k, v in by_kind.items():
        print(f"  {k:24s} " + "  ".join(f"{m}: {x}" for m, x in v.items()))


if __name__ == "__main__":
    main()
