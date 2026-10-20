"""placement_check.py (not edited) for the v3 placement, plus what each thing rests on.

    ~/miniconda3/envs/dynamic_eqa/bin/python placement_check_v3.py <day> <HHMM> v2|v3

Same counts and thresholds as placement_check.py (its docstring): floating, off_its_support,
above_rim, overlaps. Runs lib.SnapshotHomeV2 (v2) or lib_v3.SnapshotHomeV3 (v3); RUN_V3 picks
another run's snapshots (e.g. hssd_a2). Added: for every placed thing not in a closed place or
closed container and not inside an object (a bowl, a basket), what the down samples meet
first under it (the same 25 samples as for floating): on_a_thing when most samples that hit
something hit another placed thing, else on_a_surface (furniture or floor). on_a_thing is
split into carrier pairs (lib_v3.may_carry: a cup on a coaster, a towel on a towel, things
on a tray) and the rest (stacked_not_carrier).
Overhang: of the same 25 samples, the share where the first thing met is within 3 cm of the
thing's bottom (held); counted when the centre sample is not held or under 80% are held.
moved_to_other_furniture / moved_on_same_furniture: the v3 repairs of those kinds.

Writes run_v3/checks/<RUN_V3_LOGS or hssd_a>/placement_<v>_day_XX_HHMM.json.
"""
from __future__ import annotations

import json
import sys

import magnum as mn
import numpy as np

import lib_v3
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
    cls = {"v2": lib.SnapshotHomeV2, "v3": lib_v3.SnapshotHomeV3, "v1": lib.SnapshotHome}[ver]
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
    rests = {}
    overhangs = []
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
        gaps, under, ys_all, held = [], [], [], {}
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
                    held[(fx, fz)] = lo[1] - float(patch.flat[k]) <= 0.03
                else:
                    held[(fx, fz)] = False
        for p, t in moved.items():
            home.things[p].translation = t
        gap = min(gaps) if gaps else float("inf")
        if not (objs[o]["relation"] == "inside" and objs[o]["reference_kind"] == "object"):
            sh = sum(held.values()) / 25.0
            if not held.get((0.5, 0.5)) or sh < 0.8:
                overhangs.append({"object": o, "held_share": round(sh, 2), "centre_held": bool(held.get((0.5, 0.5))),
                                  "place": objs[o]["place"], "drawn_on": home.records[o].get("drawn_on")})
            things = [s_ for s_ in under if lib.scene.FIRST_THING <= s_ < lib.scene.FIRST_PERSON]
            if under and len(things) > len(under) / 2:
                by_sid = {f["sid"]: k for k, f in home.facts.items()}
                base = max(set(things), key=things.count)
                bo = by_sid.get(base)
                ok = bo is not None and lib_v3.may_carry(objs[bo]["type"], objs[o]["type"])
                rests[o] = {"on": "a_thing", "thing": bo, "carrier_pair": ok}
            else:
                rests[o] = {"on": "a_surface"}
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
           "repairs": len(getattr(home, "repairs", [])) if ver != "v1" else None,
           "overhang_centre_or_over_20pct": len(overhangs),
           "moved_to_other_furniture": sorted(o for o, r in home.records.items() if any(
               x["kind"] == "moved_to_other_furniture" for x in r.get("repairs", []))),
           "moved_on_same_furniture": sorted(o for o, r in home.records.items() if any(
               x["kind"] == "moved_on_same_furniture" for x in r.get("repairs", []))),
           "overhang_list": overhangs,
           "resting_on_a_surface": sum(1 for r in rests.values() if r["on"] == "a_surface"),
           "resting_on_a_thing": sum(1 for r in rests.values() if r["on"] == "a_thing"),
           "resting_on_a_thing_carrier_pair": sum(1 for r in rests.values() if r["on"] == "a_thing" and r["carrier_pair"]),
           "resting_on_a_thing_not_carrier": sum(1 for r in rests.values() if r["on"] == "a_thing" and not r["carrier_pair"]),
           "stacked_not_carrier": sorted(f"{o} on {r['thing']}" for o, r in rests.items() if r["on"] == "a_thing" and not r["carrier_pair"]),
           "floating": sorted(floating, key=lambda x: -x["gap_cm"]), "off_support": off_support, "above_rim": above_rim, "overlap_pairs": overlaps}
    d = lib_v3.RENDER / "run_v3" / "checks" / lib.CODE.name
    d.mkdir(parents=True, exist_ok=True)
    lib.json_dump(out, d / f"placement_{ver}_day_{day:02d}_{hhmm}.json")
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}))


if __name__ == "__main__":
    sys.exit(main())
