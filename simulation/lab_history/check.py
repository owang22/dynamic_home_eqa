"""Checks one generated history against its own hidden world. Exits non-zero on the first broken invariant.

    python -m simulation.lab_history.check /data/oliver/simulation_out/lab_history/d60_s0
"""
import json
import sys
from pathlib import Path

from .generate import line, split_colour
from .world import Config, World


def load(path):
    return [json.loads(line) for line in open(path)]


def main(out):
    out = Path(out)
    meta = json.loads((out / "routines.json").read_text())
    world = World(Config(**meta["config"]))
    events, etruth = load(out / "events.jsonl"), load(out / "events_truth.jsonl")
    truth, qs = load(out / "truth.jsonl"), load(out / "questions.jsonl")
    failures = []

    def check(ok, msg):
        if not ok:
            failures.append(msg)

    # 1. the world rebuilt from routines.json matches the written truth
    for r in truth[::7]:
        where = world.person_place if r["kind"] == "person" else world.object_place
        check(where(r["entity"], r["t_start"]) == r["place"], f"truth mismatch {r}")

    # 2. truth intervals cover the run with no gaps, per entity
    by = {}
    for r in truth:
        by.setdefault(r["entity"], []).append(r)
    end = world.day_start(world.cfg.days)
    for name, rows in by.items():
        check(rows[0]["t_start"] == world.day_start(0) and rows[-1]["t_end"] == end, f"{name}: not full span")
        check(all(a["t_end"] == b["t_start"] for a, b in zip(rows, rows[1:])), f"{name}: gap or overlap")

    # 3. every event's text names what was seen, and its truth agrees with the world
    for ev, tr in zip(events, etruth):
        check(ev["id"] == tr["id"], f"event order {ev['id']}")
        objs = [o.name for o in world.objects if world.object_place(o.name, ev["t"]) == ev["place"]]
        check(sorted(objs) == sorted(tr["objects"]), f"{ev['id']}: objects {objs} vs {tr['objects']}")
        for o in world.objects:
            if o.name in tr["objects"] and o.name not in tr["missed"] and o.name not in tr["misnamed"]:
                names = [x["name"] for x in ev["seen"]["objects"]]
                check(split_colour(o.desc)[1] in names, f"{ev['id']}: {o.desc} missing from seen")
        check(ev["text"] == line(ev["seen"]), f"{ev['id']}: text is not the rendering of seen")

    # 4. routines: owner-carried objects are out exactly when the owner is; weekday objects follow the weekday
    for o in world.objects:
        for day in range(world.cfg.days):
            r = world.regime(o, day)
            t = world.day_start(day) + 11 * 3600
            if r["type"] == "follows_owner":
                check((world.object_place(o.name, t) is None) == (world.person_place(r["owner"], t) is None),
                      f"{o.name} day {day}: not with {r['owner']}")
            if r["type"] == "weekday" and world.is_workday(day) and not meta["noise_days"][o.name].get(str(day)):
                want = r["places"][1] if world.weekday(day) in r["days"] else r["places"][0]
                check(world.object_place(o.name, t) == want, f"{o.name} day {day}: weekday rule broken")

    # 5. where_now answers equal the truth at question time
    for q in qs:
        if q["kind"] == "where_now":
            got = world.object_place(q["entity"], q["t"])
            check((got or "not in the lab") == q["answer"], f"{q['id']}: answer {q['answer']} vs {got}")

    if failures:
        print(f"{len(failures)} failures; first 10:")
        print("\n".join(failures[:10]))
        sys.exit(1)
    print(f"ok: {len(events)} events, {len(truth)} truth intervals, {len(qs)} questions, {len(world.objects)} objects")


if __name__ == "__main__":
    main(sys.argv[1])
