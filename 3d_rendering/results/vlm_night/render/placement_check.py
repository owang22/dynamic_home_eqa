"""Measure a snapshot's 3D placement (no pictures): floating things, things standing out of
containers, and overlaps. Runs the old placement (v1, lib.SnapshotHome, as in hssd_a) or the
new one (v2, lib.SnapshotHomeV2, as in hssd_a_v2) on the same snapshot.

    ~/miniconda3/envs/dynamic_eqa/bin/python placement_check.py <day> <HHMM> v1|v2

Writes run_v2/checks/placement_<v>_day_XX_HHMM.json and prints the counts.

- floating: a placed thing whose bottom is more than 3 cm above whatever is under it. The thing,
  and every thing over its footprint whose bottom is higher than its bottom, is moved away; a
  down camera 5 cm over the thing's bottom looks straight down at 25 points over its footprint
  (10-90% across each side); the gap is the bottom less the highest point found.
- off_its_support: same samples, but only points of what the thing is meant to rest on as
  drawn (its base for thing-on-thing, else its place's furniture or floor); more than 3 cm
  above that, or none of it under the thing (gap null): it rests on something else.
  Things inside containers are left to above_rim.
  Counted over things not in a closed place or closed container (those cannot be seen).
- above_rim: a thing inside a container (an object) whose top is more than 10 cm above the
  container's box top (its rim), for open and closed containers.
- overlaps: pairs of placed things, neither on, in or under the other (along the snapshot's
  chain of relations), whose boxes share more than 25% of the smaller box's volume and more
  than 1 cm of height. Same thresholds for both versions; boxes of turned things are loose.
"""
from __future__ import annotations

import json
import sys

import magnum as mn
import numpy as np

import lib


def chain(objs, oid):
    out, cur = set(), oid
    while objs[cur]["reference_kind"] == "object" and cur not in out:
        out.add(cur)
        cur = objs[cur]["reference"]
    out.add(cur)
    return out


def main():
    day, hhmm, ver = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    cls = lib.SnapshotHomeV2 if ver == "v2" else lib.SnapshotHome
    home = lib.open_home(lib.snapshot_path(day, hhmm), home_class=cls)
    home.place_everything()
    objs, places = home.snap["objects"], home.snap["places"]
    placed = [o for o, r in home.records.items() if r.get("placed") and o in home.things]
    box = {o: home.footprint(o) for o in placed}

    def in_closed(o):
        """In a closed place, or (along its chain) inside a closed container or a pocket."""
        if places[objs[o]["place"]]["kind"] == "closed":
            return True
        cur, seen = o, set()
        while objs[cur]["reference_kind"] == "object" and cur not in seen:
            seen.add(cur)
            ref = objs[cur]["reference"]
            if objs[cur]["relation"] == "inside" and objs[ref]["holds"] in ("closed", "pockets"):
                return True
            cur = ref
        return False

    def support_ids(o):
        """What o is meant to rest on as drawn: its base, or its place's furniture (or floor)."""
        r = home.records[o]
        if r.get("_in"):
            return None
        if r.get("_on") and r["_on"] in home.facts:
            return {home.facts[r["_on"]]["sid"]}
        g = places[objs[o]["place"]]["geometry"]
        if g["source"].startswith("region"):
            return {0}
        return set(home.ids_of(home.furniture_of(objs[o]["place"])))

    floating, off_support = [], []
    for o in placed:
        if in_closed(o):
            continue
        lo, hi = box[o]
        # move away the thing and everything over its footprint whose bottom is higher than
        # its bottom, so the down camera (5 cm over the bottom) sees only what could hold it
        moved = {}
        for p in placed:
            lp, hp = box[p]
            if p == o or (lp[1] > lo[1] + 0.003 and hp[0] > lo[0] and lp[0] < hi[0] and hp[2] > lo[2] and lp[2] < hi[2]):
                moved[p] = home.things[p].translation
                home.things[p].translation = moved[p] + mn.Vector3(0, 80, 0)
        gaps, under, ys_all = [], [], []
        for fx in (0.1, 0.3, 0.5, 0.7, 0.9):
            for fz in (0.1, 0.3, 0.5, 0.7, 0.9):
                x, z = lo[0] + fx * (hi[0] - lo[0]), lo[2] + fz * (hi[2] - lo[2])
                world, sid = home.down_points(np.array([x, lo[1] + 0.05, z]))
                c = world.shape[0] // 2
                patch = world[c - 1:c + 2, c - 1:c + 2, 1]
                ids = sid[c - 1:c + 2, c - 1:c + 2]
                ok = np.isfinite(patch)
                if ok.any():
                    k = int(np.argmax(np.where(ok, patch, -np.inf)))
                    gaps.append(lo[1] - float(patch.flat[k]))
                    under.append(int(ids.flat[k]))
                    ys_all.append((float(patch.flat[k]), int(ids.flat[k])))
        for p, t in moved.items():
            home.things[p].translation = t
        gap = min(gaps) if gaps else float("inf")
        want = support_ids(o)
        if want is not None:
            ys = [y for y, s_ in ys_all if s_ in want]
            g2 = lo[1] - max(ys) if ys else float("inf")
            if g2 > 0.03:
                off_support.append({"object": o, "gap_cm": round(100 * g2, 1) if ys else None,
                                    "meant_to_rest_on": home.records[o].get("_on") or objs[o]["place"],
                                    "how": home.records[o].get("how"), "under_ids": sorted(set(under))})
        if gap > 0.03:
            floating.append({"object": o, "gap_cm": round(100 * gap, 1), "relation": objs[o]["relation"],
                             "reference": objs[o]["reference"], "place": objs[o]["place"],
                             "how": home.records[o].get("how"), "under_ids": sorted(set(under))})

    above_rim = []
    for o in placed:
        if objs[o]["relation"] == "inside" and objs[o]["reference_kind"] == "object" and objs[o]["reference"] in box:
            ref = objs[o]["reference"]
            over = box[o][1][1] - box[ref][1][1]
            if over > 0.10:
                above_rim.append({"object": o, "container": ref, "holds": objs[ref]["holds"],
                                  "above_rim_cm": round(100 * over, 1)})

    overlaps = []
    for a_i, a in enumerate(placed):
        ca = chain(objs, a)
        for b in placed[a_i + 1:]:
            if b in ca or a in chain(objs, b):
                continue
            if objs[a]["relation"] == "under" and objs[a]["reference"] == b or \
               objs[b]["relation"] == "under" and objs[b]["reference"] == a:
                continue
            (la, ha), (lb, hb) = box[a], box[b]
            d = np.minimum(ha, hb) - np.maximum(la, lb)
            if (d <= 0).any() or d[1] <= 0.01:
                continue
            va, vb = np.prod(ha - la), np.prod(hb - lb)
            share = float(np.prod(d) / max(min(va, vb), 1e-9))
            if share > 0.25:
                overlaps.append({"a": a, "b": b, "share_of_smaller": round(share, 2), "place_a": objs[a]["place"],
                                 "place_b": objs[b]["place"], "hidden": bool(in_closed(a) or in_closed(b))})

    out = {"day": day, "time": hhmm, "version": ver, "placed": len(placed),
           "floating_over_3cm": len(floating), "off_its_support_over_3cm": len(off_support), "above_rim_over_10cm": len(above_rim),
           "overlaps": len(overlaps), "overlaps_visible": sum(1 for x in overlaps if not x["hidden"]),
           "did_not_fit": sum(1 for o in placed if home.records[o].get("did_not_fit")),
           "repairs": len(getattr(home, "repairs", [])) if ver == "v2" else None,
           "floating": sorted(floating, key=lambda x: -x["gap_cm"]), "off_support": off_support, "above_rim": above_rim, "overlap_pairs": overlaps}
    d = lib.CODE / "run_v2" / "checks"
    d.mkdir(parents=True, exist_ok=True)
    lib.json_dump(out, d / f"placement_{ver}_day_{day:02d}_{hhmm}.json")
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}))


if __name__ == "__main__":
    sys.exit(main())
