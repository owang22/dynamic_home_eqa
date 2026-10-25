"""Write one synthetic lab history: the dog's events, the ground truth, the routines and questions. See ../README.md.

    python -m simulation.lab_history.generate --days 60 --seed 0 --out /data/oliver/simulation_out/lab_history/d60_s0

Output files:
    events.jsonl         one per place the dog looked at, in the event format of go2/memory_lab/data.py:
                         id, t, real_t, kind, source, x, y, yaw_deg, place, place_m, path (null), seen, describer, text
    events_truth.jsonl   per event: what was really there, and what the camera missed, misnamed or invented
    truth.jsonl          every person's and object's place as intervals: entity, kind, place, t_start, t_end
    routines.json        places, people, each object's routine(s) in words, the shift log, off-routine days
    questions.jsonl      questions with answers from the truth, and the dog's last sighting before each one
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from .world import REAL_PLACES, Config, World, WEEKDAYS

TICK = 600                       # truth is sampled every 10 minutes
PATROL_HOURS = [9.5, 13.5, 17.5]  # workdays; weekends get one patrol at noon
PATROL_STOPS = 6                 # places per patrol besides the dock
EXTRA_VISIT = 0.3                # per workday: an unplanned look at 2 places
MISS_OBJECT, MISS_PERSON = 0.12, 0.05
ALIAS, INVENT = 0.15, 0.03
COLOURS = {"white", "red", "black", "green", "silver", "blue", "orange", "yellow", "grey", "brown", "pink", "purple"}
ON = {"desk": ["desk", "desk", "floor", "chair"], "meeting": ["table"], "lunch": ["sofa", "floor"],
      "sink": ["floor", "counter"], "entry": ["floor"], "common": ["floor", "shelf", "table"]}


def split_colour(desc):
    """'red umbrella' -> ('red', 'umbrella'); 'stuffed toy dog' -> ('', 'stuffed toy dog')."""
    w = desc.split()
    return (w[0], " ".join(w[1:])) if w[0] in COLOURS and len(w) > 1 else ("", desc)


def line(seen):
    """The one-line rendering go2/memory_lab/data.py uses for text."""
    objs = ", ".join(f"{o['colour']} {o['name']} on {o['on']}".strip() for o in seen["objects"])
    s = seen["summary"]
    if objs:
        s += f" Objects: {objs}."
    if seen["people"]:
        s += f" People: {seen['people']} ({seen['people_notes']})."
    if seen["states"]:
        s += " States: " + "; ".join(seen["states"]) + "."
    return s


def visits(world: World, rng: random.Random):
    """(t, place) for every look the dog takes, in time order."""
    dock = "dock" if "dock" in world.places else None
    route = [p for p in world.places if p != dock]
    rng.shuffle(route)
    n_stops = PATROL_STOPS if dock else PATROL_STOPS + 1
    k, out = 0, []
    for day in range(world.cfg.days):
        hours = PATROL_HOURS if world.is_workday(day) else [12.0]
        for h in hours:
            t = world.day_start(day) + (h + rng.gauss(0, 0.15)) * 3600
            stops = ([dock] if dock else []) + [route[(k + i) % len(route)] for i in range(n_stops)]
            k += n_stops
            out += [(t + 60 * i, p) for i, p in enumerate(stops)]
        if world.is_workday(day) and rng.random() < EXTRA_VISIT:
            t = world.day_start(day) + rng.uniform(8, 19) * 3600
            out += [(t + 60 * i, p) for i, p in enumerate(rng.sample(route, 2))]
    return sorted(out)


def observe(world: World, t, place, rng: random.Random):
    """What the camera reports at a place, as a describe dict (seen), plus what was really there and what went wrong."""
    objs = [o for o in world.objects if world.object_place(o.name, t) == place]
    people = [p for p in world.people if world.person_place(p.name, t) == place]
    kind = world.places[place]["kind"]
    seen_objs, looks, missed, aliased, invented = [], [], [], [], []
    for p in people:
        if rng.random() < MISS_PERSON:
            missed.append(p.name)
        else:
            looks.append(p.look)

    def report(desc):
        colour, name = split_colour(desc)
        seen_objs.append({"name": name, "colour": colour, "on": rng.choice(ON.get(kind, ON["common"])),
                          "across": round(rng.uniform(0.05, 0.95), 2)})
    for o in objs:
        if rng.random() < MISS_OBJECT:
            missed.append(o.name)
        elif rng.random() < ALIAS:
            report(rng.choice(o.aliases))
            aliased.append(o.name)
        else:
            report(o.desc)
    if rng.random() < INVENT:
        fake = rng.choice([o for o in world.objects if o not in objs])
        report(fake.desc)
        invented.append(fake.name)
    rng.shuffle(seen_objs)
    states = ["monitor on"] if kind == "desk" and looks else []
    seen = {"summary": f"View of {world.places[place]['desc']} in the lab.", "objects": seen_objs,
            "people": len(looks), "people_notes": "; ".join(looks), "states": states}
    return seen, {"objects": [o.name for o in objs], "people": [p.name for p in people],
                  "missed": missed, "misnamed": aliased, "invented": invented}


def truth_intervals(world: World):
    end = world.day_start(world.cfg.days)
    entities = [("person", p.name, world.person_place) for p in world.people] + \
               [("object", o.name, world.object_place) for o in world.objects]
    rows = []
    for kind, name, where in entities:
        t, cur, since = world.day_start(0), None, None
        while t < end:
            place = where(name, t)
            if since is None or place != cur:
                if since is not None:
                    rows.append({"entity": name, "kind": kind, "place": cur, "t_start": since, "t_end": t})
                cur, since = place, t
            t += TICK
        rows.append({"entity": name, "kind": kind, "place": cur, "t_start": since, "t_end": end})
    return rows


def phase(world: World, t):
    """Where t falls relative to the routine shifts: before the first, in the first week after one, or later."""
    since = [t - world.day_start(d) for d in world.shift_days if world.day_start(d) <= t]
    if not since:
        return "before_first_shift"
    return "0-7d_after_shift" if min(since) < 7 * 86400 else "7d+_after_shift"


def questions(world: World, events, intervals, n, rng: random.Random, start_day=None, shift_targeted=False):
    """Questions at random lab-hour times from start_day on (default: the last two thirds of the run).
    shift_targeted: only about the people and objects a shift changed, a third each before the first shift, in
    the week after a shift, and later (start_day is then ignored; questions start on day 3)."""
    sightings = {}                # object name -> [(t, place)] of correct-name sightings (misnamed ones don't count)
    for ev, tr in events:
        for name in tr["objects"]:
            if name not in tr["missed"] and name not in tr["misnamed"]:
                sightings.setdefault(name, []).append((ev["t"], ev["place"]))
    by_entity = {}
    for r in intervals:
        by_entity.setdefault(r["entity"], []).append(r)

    def last_sighting(name, t):
        s = [x for x in sightings.get(name, []) if x[0] <= t]
        return {"t": s[-1][0], "place": s[-1][1]} if s else None

    first = 3 if shift_targeted else world.cfg.days // 3 if start_day is None else start_day
    workdays = [d for d in range(first, world.cfg.days) if world.is_workday(d)]
    shifted = {s["who"] for s in world.shift_log}
    objects = [o for o in world.objects if o.name in shifted] if shift_targeted else world.objects
    people = [p for p in world.people if p.name in shifted] if shift_targeted else world.people
    by_phase = defaultdict(list)
    for d in workdays:
        by_phase[phase(world, world.day_start(d) + 12 * 3600)].append(d)
    out = []
    kinds = ["where_now"] * 5 + ["last_in_lab"] * 2 + ["desk_now", "usual_place"]
    if shift_targeted:
        kinds = ["where_now"] * 3 + ["desk_now", "usual_place"]
    while len(out) < n:
        day = rng.choice(by_phase[rng.choice(sorted(by_phase))]) if shift_targeted else rng.choice(workdays)
        t = round(world.day_start(day) + rng.uniform(9, 18) * 3600)
        kind = rng.choice(kinds)
        q = {"id": f"q{len(out):04d}", "t": t, "kind": kind, "phase": phase(world, t)}
        if kind == "where_now":
            o = rng.choice(objects)
            ans = world.object_place(o.name, t)
            ls = last_sighting(o.name, t)
            q.update(entity=o.name, question=f"Where is the {o.desc} now?", answer=ans or "not in the lab",
                     last_sighting=ls, stale=bool(ls and ls["place"] != ans))
        elif kind == "last_in_lab":
            o = rng.choice(world.objects)
            if world.object_place(o.name, t) is not None:
                continue
            past = [r for r in by_entity[o.name] if r["place"] is not None and r["t_end"] <= t]
            if not past:
                continue
            q.update(entity=o.name, question=f"The {o.desc} isn't here now. When and where was it last in the lab?",
                     answer={"t": past[-1]["t_end"], "place": past[-1]["place"]},
                     last_sighting=last_sighting(o.name, t))
        elif kind == "desk_now":
            p = rng.choice(people)
            q.update(entity=p.name, question=f"Which desk does {p.name} ({p.look}) use now?",
                     answer=world.desk_of(p, day))
        else:
            cands = [o for o in objects if world.regime(o, day)["type"] in ("weekday", "away_days", "fixed")]
            if not cands:
                continue
            o = rng.choice(cands)
            wd = rng.randrange(5)
            r = world.regime(o, day)
            usual = {"fixed": lambda: r["places"][0],
                     "weekday": lambda: r["places"][1] if wd in r["days"] else r["places"][0],
                     "away_days": lambda: "not in the lab" if wd in r["days"] else r["places"][0]}[r["type"]]()
            q.update(entity=o.name, question=f"Where is the {o.desc} usually on a {WEEKDAYS[wd]} these days?",
                     answer=usual, routine=world.describe(r))
        out.append(q)
    return out


def generate(cfg: Config, out: Path, n_questions=300, questions_from=None, shift_targeted=False):
    world = World(cfg)
    rng = random.Random(f"lab-history-obs-{cfg.seed}")
    events = []
    for i, (t, place) in enumerate(visits(world, rng)):
        seen, tr = observe(world, t, place, rng)
        pv = world.places[place]
        x, y = round(pv["x"] + rng.gauss(0, 0.15), 2), round(pv["y"] + rng.gauss(0, 0.15), 2)
        tg = pv.get("target")
        yaw = math.degrees(math.atan2(tg["y"] - y, tg["x"] - x)) if tg else rng.uniform(-180, 180)
        ev = {"id": f"sim{cfg.seed}_{i:06d}", "t": round(t, 1), "real_t": round(t, 1), "kind": "picture",
              "source": "sim_patrol", "x": x, "y": y, "yaw_deg": round(yaw, 1), "place": place,
              "place_m": round(math.hypot(x - pv["x"], y - pv["y"]), 2), "path": None, "seen": seen,
              "describer": "sim", "text": line(seen)}
        events.append((ev, {"id": ev["id"], **tr}))
    intervals = truth_intervals(world)
    qs = questions(world, events, intervals, n_questions, rng, questions_from, shift_targeted)

    out.mkdir(parents=True, exist_ok=True)
    with open(out / "events.jsonl", "w") as f:
        f.writelines(json.dumps(ev) + "\n" for ev, _ in events)
    with open(out / "events_truth.jsonl", "w") as f:
        f.writelines(json.dumps(tr) + "\n" for _, tr in events)
    with open(out / "truth.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in intervals)
    with open(out / "questions.jsonl", "w") as f:
        f.writelines(json.dumps(q) + "\n" for q in qs)
    (out / "routines.json").write_text(json.dumps(
        {"config": dataclasses.asdict(cfg), **world.routines()}, indent=1, default=str))
    return world, events, qs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--people", type=int, default=5)
    ap.add_argument("--objects", type=int, default=20)
    ap.add_argument("--shifts", type=int, default=2)
    ap.add_argument("--places", default=str(REAL_PLACES),
                    help="lab places file (default: the real lab, go2/memory_lab/places_2026-10-25.json); "
                         "'standin' for the made-up list")
    ap.add_argument("--questions", type=int, default=300)
    ap.add_argument("--questions-from", type=int, default=None,
                    help="first day questions may fall on (default: days // 3, i.e. after the first shift)")
    ap.add_argument("--shift-targeted", action="store_true",
                    help="questions only about shifted people and objects, balanced before / week after / later")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = Config(days=a.days, seed=a.seed, n_people=a.people, n_objects=a.objects, shifts=a.shifts,
                 places_file=None if a.places == "standin" else a.places)
    world, events, qs = generate(cfg, Path(a.out), a.questions, a.questions_from, a.shift_targeted)
    types = Counter(world.regime(o, 0)["type"] for o in world.objects)
    errs = Counter(k for _, tr in events for k in ("missed", "misnamed", "invented") for _ in tr[k])
    stale = [q for q in qs if q.get("stale")]
    print(f"{len(events)} events over {cfg.days} days; camera errors {dict(errs)}")
    print(f"routines: {dict(types)}; shift days {world.shift_days}")
    print(f"{len(qs)} questions {dict(Counter(q['kind'] for q in qs))}, phases {dict(Counter(q['phase'] for q in qs))}; "
          f"where_now with a stale last sighting: {len(stale)}")
    print(f"written to {a.out}")


if __name__ == "__main__":
    main()
