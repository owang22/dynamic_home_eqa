"""Does a household keep its arrangement, or drift into clutter?

For every snapshot (positions_HHMM.json, 08:00 to 22:00), over things not being
carried (nor inside something carried), with usual places from homes.json, or
worked out from household.json for runs from before 2026-10-10:
- at usual place: share of things with a usual place that are there
- lying about: clean things away from their usual place on a floor, seat, bed,
  basin or stove. This is the clutter.
- elsewhere: away from their usual place but on another shelf, table or in
  another drawer. A thing can find a new place of its own (a laptop that now
  lives on the desk); this is not counted as clutter.
- dirty clothes out: worn clothes on a floor, seat or bed (a laundry question)
- hidden: share of all things out of sight

The check compares "lying about" on days 2-4 with the last three days (after
day 4): it fails when it grew by more than 5 things or half, whichever is more.

Usage: python -m lived_home.drift <run> [<run> ...]   (writes <run>/drift.json)
"""
from __future__ import annotations

import json
import pathlib
import sys

from lived_home.layout import Layout
from lived_home.world import _drop_kind, homes

GROWTH_MIN, GROWTH_SHARE = 5, 0.5   # clutter may grow by 5 things or by half, whichever is more
CARRIED = ("held_by", "worn_by", "in_pocket_of")


def run_homes(run: pathlib.Path) -> dict:
    if (run / "homes.json").exists():
        return json.loads((run / "homes.json").read_text())
    spec = json.loads((run / "household.json").read_text())
    return homes({o["id"]: o for o in spec["objects"]}, Layout.from_json(spec["layout"]))


def carried(o: dict, objs: dict) -> bool:
    """On a person, or inside something (inside something...) that is."""
    seen = set()
    while True:
        if o["relation"] in CARRIED:
            return True
        ref = o.get("reference")
        if o["relation"] != "inside" or o.get("reference_kind") != "object" or ref not in objs or ref in seen:
            return False
        seen.add(ref)
        o = objs[ref]


def measure(state: dict, home: dict, layout: Layout) -> dict:
    """at_home: share of things with a usual place that are there. lying_about:
    clean things away from their usual place on a floor, seat, bed, basin or stove.
    elsewhere: away from their usual place on another shelf, table or in another
    drawer (possibly a new place of their own; not counted as clutter). dirty_out:
    worn clothes lying on a floor, seat or bed."""
    objs = state["objects"]
    n = at_home = lying = elsewhere = dirty_out = 0
    for oid, o in objs.items():
        h = home.get(oid)
        if carried(o, objs):
            continue
        place = layout.places.get(o.get("place"))
        drop = bool(place) and _drop_kind(place, o["relation"]) in ("floor", "seat", "wet", "hot")
        if o.get("dirty"):
            dirty_out += drop
            continue
        if not h:
            continue
        n += 1
        home_now = (o["relation"] == "inside" and o.get("reference") == h["carrier"]) if "carrier" in h \
            else o.get("place") == h["place"]
        at_home += home_now
        if not home_now:
            lying += drop
            elsewhere += not drop
    return {"at_home": at_home / max(1, n), "lying_about": lying, "elsewhere": elsewhere,
            "dirty_out": dirty_out, "hidden": sum(o["hidden"] for o in objs.values()) / len(objs)}


def check(run: pathlib.Path) -> dict:
    spec = json.loads((run / "household.json").read_text())
    layout = Layout.from_json(spec["layout"])
    home = run_homes(run)
    days, first = {}, None
    for d in sorted(run.glob("day_*")):
        files = sorted(d.glob("positions_[0-9]*.json"))
        snaps = [measure(json.loads(f.read_text()), home, layout) for f in files]
        if snaps:
            first = first or snaps[0]
            days[int(d.name.split("_")[1])] = {k: sum(s[k] for s in snaps) / len(snaps) for k in snaps[0]}
    nums = sorted(days)
    early = [d for d in nums if 2 <= d <= 4]
    late = [d for d in nums[-3:] if d > 4]
    mean = lambda ds, k: (sum(days[d][k] for d in ds) / len(ds)) if ds else None
    out = {"run": run.name, "first_snapshot": first, "days": days, "early_days": early, "late_days": late}
    for k in ("at_home", "lying_about", "elsewhere", "dirty_out", "hidden"):
        out[f"{k}_early"], out[f"{k}_late"] = mean(early, k), mean(late, k)
    ok = len(nums) >= 6 and out["lying_about_early"] is not None and out["lying_about_late"] is not None
    out["growth"] = (out["lying_about_late"] - out["lying_about_early"]) if ok else None
    out["limit"] = max(GROWTH_MIN, GROWTH_SHARE * out["lying_about_early"]) if ok else None
    out["passes"] = ok and out["growth"] <= out["limit"]
    return out


def main() -> None:
    bad = False
    for arg in sys.argv[1:]:
        run = pathlib.Path(arg)
        r = check(run)
        if not r["days"]:
            print(f"{run.name}: no positions_HHMM.json snapshots (runs before 2026-10-08); cannot check")
            continue
        (run / "drift.json").write_text(json.dumps(r, indent=1))
        f = r["first_snapshot"]
        print(f"{run.name}: day  at usual place  lying about  elsewhere  dirty clothes out  hidden")
        print(f"  d1 08:00 {100 * f['at_home']:9.0f}%  {f['lying_about']:11.1f}  {f['elsewhere']:9.1f}  "
              f"{f['dirty_out']:17.1f}  {100 * f['hidden']:5.0f}%")
        for d, v in r["days"].items():
            print(f"  {d:>8} {100 * v['at_home']:9.0f}%  {v['lying_about']:11.1f}  {v['elsewhere']:9.1f}  "
                  f"{v['dirty_out']:17.1f}  {100 * v['hidden']:5.0f}%")
        if r["growth"] is None:
            print("  needs 6 or more days to judge")
            bad = True
            continue
        verdict = "passes" if r["passes"] else "FAILS"
        print(f"  lying about: days {r['early_days']} {r['lying_about_early']:.1f} -> days {r['late_days']} "
              f"{r['lying_about_late']:.1f} (grew {r['growth']:+.1f}; limit {r['limit']:.1f}): {verdict}")
        bad |= not r["passes"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
