#!/usr/bin/env python3
"""Consolidate a built household set into one dataset file.

Reads the per-household directories produced by `storyfirst.py` and writes
a single JSON Lines file, one household per line, carrying everything a
consumer needs: who lives there, what they own, where things start, every
activity they perform and every object movement that results.

    python src/revamp_v2/export_dataset.py \
        --set profiles/revamp_v2/storyfirst/gpt-5.6-terra \
        --out data/household_dataset.jsonl

Record schema (one per household):

    household_id     str    "hh_001"
    household_type   str    "working_professional_solo"
    days             int    length of the simulated run
    seed             int    realization seed
    residents        list   {id, name, age, occupation, personality}
    receptacles      list   {id, room}
    objects          list   {id, class, owner, home}
    activities       list   {resident, activity, at, t0, t1}
    events           list   {t, object, from, to, by}

Times are integer minutes from the start of day 0. `at` and the object
`from`/`to` fields name a receptacle id, or "ELSEWHERE" when the resident
is out of the house. `by` names the activity that caused a movement.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml


def _household_number(path: pathlib.Path) -> int:
    digits = "".join(c for c in path.name if c.isdigit())
    return int(digits) if digits else 0


def build_record(hh_dir: pathlib.Path, seed: int) -> dict:
    timeline = hh_dir / f"timeline_seed{seed}"
    persona = yaml.safe_load((hh_dir / "persona.yaml").read_text())
    program = yaml.safe_load((hh_dir / "program.yaml").read_text())
    movement = yaml.safe_load((hh_dir / "object_movement.yaml").read_text())
    meta = json.loads((timeline / "meta.json").read_text())

    homes = {e["object"]: e["home"] for e in movement["object_rules"]}
    owners = {o["id"]: o["owner"] for o in persona["object_inventory"]}

    residents = [{"id": r["id"], "name": r.get("name"), "age": r.get("age"),
                  "occupation": r.get("occupation"),
                  "personality": r.get("personality")}
                 for r in persona["residents"]]
    objects = [{"id": o["id"], "class": o.get("class"),
                "owner": owners.get(o["id"]), "home": homes.get(o["id"])}
               for o in persona["object_inventory"]]
    receptacles = [{"id": r["id"], "room": r["room"]}
                   for r in program["receptacles"]]

    activities = []
    for line in (timeline / "residents.jsonl").read_text().splitlines():
        b = json.loads(line)
        activities.append({"resident": b["resident"], "activity": b["activity"],
                           "at": b["at"], "t0": b["t0"], "t1": b["t1"]})
    events = []
    for line in (timeline / "events.jsonl").read_text().splitlines():
        e = json.loads(line)
        events.append({"t": e["t"], "object": e["object"],
                       "from": e["from"], "to": e["to"], "by": e.get("by")})

    return {"household_id": program["household"],
            "household_type": program["household_type"],
            "days": int(program["days"]), "seed": seed,
            "residents": residents, "receptacles": receptacles,
            "objects": objects, "activities": activities, "events": events}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", dest="set_dir", type=pathlib.Path, required=True,
                    help="a built set directory containing hh*/ folders")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    hh_dirs = sorted((d for d in args.set_dir.glob("hh*") if d.is_dir()),
                     key=_household_number)
    if not hh_dirs:
        sys.exit(f"no households under {args.set_dir}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    n_events = n_activities = 0
    with args.out.open("w") as fh:
        for hh_dir in hh_dirs:
            record = build_record(hh_dir, args.seed)
            n_events += len(record["events"])
            n_activities += len(record["activities"])
            fh.write(json.dumps(record) + "\n")
            print(f"{record['household_id']}: {len(record['residents'])} residents, "
                  f"{len(record['objects'])} objects, "
                  f"{len(record['activities'])} activities, "
                  f"{len(record['events'])} events")
    size_mb = args.out.stat().st_size / 1e6
    print(f"\n{len(hh_dirs)} households, {n_activities} activities, "
          f"{n_events} events -> {args.out} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
