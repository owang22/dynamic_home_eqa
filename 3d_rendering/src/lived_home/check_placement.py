"""Count, on a finished run, the positions the placement rules forbid.

For every positions_HHMM.json snapshot of a run:
- holding: a thing on top of or inside another thing that is not a base or
  container for it (lived_home.placement.holding_problem);
- places: a thing on a floor (or under furniture) or in a basin that does not
  belong there (lived_home.placement.place_problem);
- overfull: a spot whose things take more room than it has, under the area assumed
  when the household was made and under the area measured in the rendered empty
  home where there is a good scan (lived_home.measured_areas).

    python -m lived_home.check_placement <run folder> [--top 15] [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

from lived_home import measured_areas
from lived_home.layout import SURFACE, Layout
from lived_home.placement import holding_problem, place_problem
from lived_home.world import DEPTH, FOOTPRINT

CARRIED = ("held_by", "worn_by", "in_pocket_of")


def snapshots(run: pathlib.Path) -> list:
    """[(day, "HHMM", positions)] in time order."""
    out = []
    for d in sorted(run.glob("day_*")):
        for f in sorted(d.glob("positions_[0-9]*.json")):
            out.append((int(d.name.split("_")[1]), f.stem.split("_")[1], json.loads(f.read_text())))
    return out


def objects_of(spec: dict) -> dict:
    return {o["id"]: o for o in spec["objects"]}


def holding_violations(state: dict, objects: dict) -> list:
    """[(item, rel, base, reason)] in one snapshot."""
    out = []
    for oid, o in state["objects"].items():
        if o.get("reference_kind") != "object" or o["relation"] not in ("on_top", "inside"):
            continue
        base = o["reference"]
        why = holding_problem(objects.get(oid, o), objects.get(base, state["objects"].get(base, {})),
                              o["relation"])
        if why:
            out.append((oid, o["relation"], base, why))
    return out


def resting(o: dict) -> bool:
    """Directly on or in a spot (or next to a thing there), taking room on it."""
    if o["relation"] in CARRIED or o["relation"] == "under" or not o.get("place"):
        return False
    if o.get("reference_kind") == "object":
        return o["relation"] == "next_to"
    return True


def place_violations(state: dict, objects: dict, layout: Layout) -> list:
    """[(item, place, reason)]: things whose own spot (not through a bag) breaks rule 2."""
    out = []
    for oid, o in state["objects"].items():
        if o["relation"] in CARRIED or not o.get("place") or o["place"] not in layout.places:
            continue
        if o["relation"] == "inside" and o.get("reference_kind") == "object":
            continue                              # in a bag: the bag is what lies there
        ref = o["reference"] if o.get("reference_kind") == "object" else None
        why = place_problem(objects.get(oid, o), layout.places[o["place"]], o["relation"], ref)
        if why:
            out.append((oid, o["place"], why))
    return out


def overfull(state: dict, areas: dict) -> list:
    """[(place, used m², room m²)] for spots over their room. areas: place -> (area, kind)."""
    used = collections.Counter()
    for o in state["objects"].values():
        if resting(o):
            used[o["place"]] += FOOTPRINT.get(o.get("size"), FOOTPRINT["medium"])
    out = []
    for pid, u in used.items():
        if pid not in areas or areas[pid][0] is None:
            continue
        area, kind = areas[pid]
        room = area * (DEPTH if kind != SURFACE else 1.0)
        if u > room + 1e-9:
            out.append((pid, round(u, 3), round(room, 3)))
    return out


def area_tables(spec: dict) -> tuple[dict, dict]:
    """(assumed, measured): place -> (area, kind). measured falls back to assumed."""
    rows = measured_areas.load(spec.get("scene"))
    assumed, measured = {}, {}
    for p in spec["layout"]["places"]:
        g = p.get("geometry") or {}
        a = g.get("area_assumed", g.get("area"))
        assumed[p["id"]] = (a, p["kind"])
        measured[p["id"]] = (measured_areas.capacity_area(dict(g, area_assumed=a), rows.get(p["id"]))[0],
                             p["kind"])
    return assumed, measured


def check(run: pathlib.Path, snaps=None, spec=None) -> dict:
    spec = spec or json.loads((run / "household.json").read_text())
    objects = objects_of(spec)
    layout = Layout.from_json(spec["layout"])
    assumed, measured = area_tables(spec)
    snaps = snaps if snaps is not None else snapshots(run)
    hold, place = collections.Counter(), collections.Counter()
    hold_n, place_n, over_a, over_m = [], [], [], []
    over_a_spots, over_m_spots = collections.Counter(), collections.Counter()
    on_obj = []
    for day, t, st in snaps:
        hv = holding_violations(st, objects)
        pv = place_violations(st, objects, layout)
        on_obj.append(sum(1 for o in st["objects"].values() if o.get("reference_kind") == "object"
                          and o["relation"] in ("on_top", "inside")))
        hold_n.append(len(hv))
        place_n.append(len(pv))
        for oid, rel, base, _ in hv:
            hold[(objects[oid]["type"], rel, objects[base]["type"])] += 1
        for oid, pid, _ in pv:
            place[(objects[oid]["type"], pid)] += 1
        oa, om = overfull(st, assumed), overfull(st, measured)
        over_a.append(len(oa))
        over_m.append(len(om))
        over_a_spots.update(p for p, _, _ in oa)
        over_m_spots.update(p for p, _, _ in om)
    n = max(1, len(snaps))
    return {"run": run.name, "snapshots": len(snaps),
            "on_or_in_a_thing_per_snapshot": round(sum(on_obj) / n, 1),
            "holding_violations": sum(hold_n), "holding_per_snapshot": round(sum(hold_n) / n, 2),
            "holding_top": [[*k, v] for k, v in hold.most_common()],
            "place_violations": sum(place_n), "place_per_snapshot": round(sum(place_n) / n, 2),
            "place_top": [[*k, v] for k, v in place.most_common()],
            "overfull_assumed": {"spot_snapshots": sum(over_a), "snapshots_with_any": sum(1 for x in over_a if x),
                                 "spots": dict(over_a_spots.most_common())},
            "overfull_measured": {"spot_snapshots": sum(over_m), "snapshots_with_any": sum(1 for x in over_m if x),
                                  "spots": dict(over_m_spots.most_common())},
            "areas_scanned": sum(1 for p in measured if measured[p][0] != assumed[p][0])}


def report(res: dict, top: int = 15) -> str:
    lines = [f"{res['run']}: {res['snapshots']} snapshots, "
             f"{res['on_or_in_a_thing_per_snapshot']} things on or in another thing per snapshot",
             f"  holding rule broken: {res['holding_violations']} ({res['holding_per_snapshot']} per snapshot)"]
    lines += [f"    {v:4d}  {a} {r.replace('_', ' ')} {b}" for a, r, b, v in res["holding_top"][:top]]
    lines.append(f"  floor/basin rule broken: {res['place_violations']} ({res['place_per_snapshot']} per snapshot)")
    lines += [f"    {v:4d}  {a} at {p}" for a, p, v in res["place_top"][:top]]
    for k in ("overfull_assumed", "overfull_measured"):
        o = res[k]
        lines.append(f"  {k.replace('_', ' with ')} area: {o['snapshots_with_any']} of {res['snapshots']} "
                     f"snapshots have an overfull spot ({o['spot_snapshots']} spot-snapshots)")
        lines += [f"    {v:4d}  {p}" for p, v in list(o["spots"].items())[:top]]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=pathlib.Path)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args()
    res = check(a.run)
    print(report(res, a.top))
    if a.json:
        a.json.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
