#!/usr/bin/env python3
"""Replay REAL CASAS activity intervals through an object-binding spec.

The revamp_v1 counterpart (profiles/revamp_v1/simulate_schedule.py) invents
its schedule from weekly blocks + jitter; here the schedule is the real
thing — labeled ADL intervals extracted by extract_activities.py — and only
the object layer is simulated. Same rule mechanics, one extension: `during`
entries may carry p / only_from, because real activities repeat many times a
day and not every bout touches every object.

Emits the exact revamp_v1 timeline format (events.jsonl, hourly.csv,
meta.json), so visualization/spatialize.py and the web viewer consume it
unchanged. Deterministic given (binding, window, seed). Day-name stamps use
the REAL calendar (aruba day 0 = Thu 2010-11-04), re-zeroed so t=0 is the
window's first midnight.

Usage:
  python simulate_from_casas.py aruba_binding.yaml \
      --start-day 0 --days 14 --seed 0 --out aruba/timeline_14d
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import heapq
import json
import math
import pathlib
import random

import yaml

ELSEWHERE = "ELSEWHERE"
TIDY_MIN, TIDY_MAX = 2.0, 5.0   # minutes per tidied item
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MISPLACE_WINDOW = (10 * 60, 21 * 60 + 30)


def stamp(t: int, base_wd: int) -> str:
    d, m = divmod(t, 1440)
    return f"d{d:02d} {DAY_NAMES[(base_wd + d) % 7]} {m // 60:02d}:{m % 60:02d}"


def norm_rule(rule) -> dict:
    """Allow bare receptacle strings as shorthand for {dest: r}."""
    return {"dest": rule} if isinstance(rule, str) else rule


def validate(spec: dict) -> None:
    recs = {r["id"] for r in spec["receptacles"]} | {ELSEWHERE}
    objs = set(spec["placements"])
    reachable = {o: {p["home"]} for o, p in spec["placements"].items()}
    for name, act in spec["activities"].items():
        for phase in ("during", "after"):
            for obj, rule in act.get(phase, {}).items():
                rule = norm_rule(rule)
                assert obj in objs, f"{name}.{phase}: unknown object {obj}"
                targets = set(rule["dist"]) if "dist" in rule else \
                    {rule["dest"]} | ({rule["else"]} if "else" in rule else set())
                if "dist" in rule:
                    assert abs(sum(rule["dist"].values()) - 1) < 1e-6, \
                        f"{name}.{phase}.{obj}: dist sum != 1"
                for r in targets | set(rule.get("only_from", [])):
                    assert r in recs, f"{name}.{phase}.{obj}: unknown receptacle {r}"
                reachable[obj] |= targets
    for obj, p in spec["placements"].items():
        static, mobile = p.get("static", False), \
            len(reachable[obj]) > 1 or "p_misplace" in p
        assert not (mobile and static), f"{obj}: static but rules move it"
        assert mobile or static, f"{obj}: can never move — declare static or add rules"

    prof = yaml.safe_load((pathlib.Path(spec["_dir"]) / spec["source_profile"]).read_text())
    inv = {o["id"] for o in prof["object_inventory"]}
    assert set(spec["placements"]) == inv, \
        f"placements != inventory; missing={inv - objs} extra={objs - inv}"


def sample(rule: dict, rng: random.Random) -> str:
    if "dist" in rule:
        r, acc = rng.random(), 0.0
        for dest, p in rule["dist"].items():
            acc += p
            if r < acc:
                return dest
        return dest
    if "p" in rule and rng.random() >= rule["p"]:
        return rule.get("else")            # None = no move
    return rule["dest"]


def resolve_anchors(path):
    if path is None:
        return {}
    cfg = yaml.safe_load(path.read_text())
    scene = json.loads((path.parent / cfg["scene_assets"] / "scene.json").read_text())
    regions = {r["name"]: r for r in scene["rooms"]}
    spec = yaml.safe_load((path.parent / cfg["schedule_spec"]).read_text())
    rec_room = {r["id"]: r["room"] for r in spec["receptacles"]}
    out = {}
    for rid, rcfg in cfg["receptacles"].items():
        region = regions[cfg["room_map"][rec_room[rid]]]
        mn, mx = region["min_bounds"], region["max_bounds"]
        fx, fz = rcfg["anchor"]
        out[rid] = (mn[0] + fx * (mx[0] - mn[0]), mn[2] + fz * (mx[2] - mn[2]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("binding", type=pathlib.Path)
    ap.add_argument("--start-day", type=int, default=0)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--anchors", type=pathlib.Path, default=None,
                    help="visualization spatial config; enables nearest-first tidy order")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    spec = yaml.safe_load(args.binding.read_text())
    spec["_dir"] = str(args.binding.parent)
    validate(spec)
    rng = random.Random(args.seed)

    csv_path = args.binding.parent / spec["activities_csv"]
    rows = list(csv.DictReader(open(csv_path)))
    day0 = dt.date.fromisoformat(rows[0]["start"][:10])
    base_wd = (day0.weekday() + args.start_day) % 7
    off = args.start_day * 1440
    horizon = args.days * 1440

    # boundary events from the real intervals, re-zeroed to the window
    events_in = []
    for r in rows:
        t0, t1 = float(r["t0_min"]) - off, float(r["t1_min"]) - off
        act = spec["activities"].get(r["activity"])
        if act is None or t1 <= 0 or t0 >= horizon:
            continue
        events_in.append((max(t0, 0), 0, "during", (r["activity"], act, min(t1, horizon))))
        if t1 < horizon:
            events_in.append((t1, 1, "after", (r["activity"], act, t1)))
    for d in range(args.days):
        for obj, p in spec["placements"].items():
            if "p_misplace" in p and rng.random() < p["p_misplace"]:
                t = d * 1440 + rng.randrange(*MISPLACE_WINDOW)
                events_in.append((t, 2, "misplace", (obj, rng.choice(p["misplace_set"]))))
    events_in.sort(key=lambda e: (e[0], e[1]))

    pos = {o: p["home"] for o, p in spec["placements"].items()}
    anchors = resolve_anchors(args.anchors)
    rec_order = {r["id"]: i for i, r in enumerate(spec["receptacles"])}
    tidy_stats = {"bouts": 0, "moved": 0, "cut_short": 0}
    log = []

    def move(t, obj, dest, by):
        if dest is not None and pos[obj] != dest:
            log.append({"t": int(t), "stamp": stamp(int(t), base_wd), "object": obj,
                        "from": pos[obj], "to": dest, "by": by})
            pos[obj] = dest

    heap = [(e[0], e[1], i, e[2], e[3]) for i, e in enumerate(events_in)]
    heapq.heapify(heap)
    hseq = len(heap)

    def plan_tidy(t0, t1, name, act):
        """Nearest-first tidy walk, limited by the real bout's duration —
        a 3-minute Housekeeping bout now touches one item, not the house."""
        nonlocal hseq
        cands = [o for o in spec["placements"]
                 if pos[o] not in (ELSEWHERE, spec["placements"][o]["home"])]
        tidy_stats["bouts"] += 1
        here, t = act.get("at"), t0
        while cands:
            def dist(o):
                a, b = anchors.get(pos[o]), anchors.get(here)
                return math.hypot(a[0]-b[0], a[1]-b[1]) if a and b \
                    else rec_order.get(pos[o], 99)
            cands.sort(key=dist)
            obj = cands.pop(0)
            if rng.random() >= act["reset_all"]["p"]:
                continue
            t += rng.uniform(TIDY_MIN, TIDY_MAX)
            if t >= t1:
                tidy_stats["cut_short"] += 1
                break
            heapq.heappush(heap, (t, 3, hseq, "tidy",
                                  (obj, spec["placements"][obj]["home"], name)))
            hseq += 1
            here = spec["placements"][obj]["home"]

    hourly = []
    for h in range(args.days * 24 + 1):
        boundary = h * 60
        while heap and heap[0][0] < boundary:
            t, _, _, kind, payload = heapq.heappop(heap)
            if kind == "misplace":
                obj, dest = payload
                if pos[obj] != ELSEWHERE:
                    move(t, obj, dest, "misplace")
                continue
            if kind == "tidy":
                obj, home, name = payload
                if pos[obj] not in (ELSEWHERE, home):
                    move(t, obj, home, f"tidy:{name}")
                    tidy_stats["moved"] += 1
                continue
            name, act, t_end = payload
            if kind == "during" and "reset_all" in act:
                plan_tidy(t, t_end, name, act)
            for obj, rule in act.get(kind, {}).items():
                rule = norm_rule(rule)
                if "only_from" in rule and pos[obj] not in rule["only_from"]:
                    continue
                move(t, obj, sample(rule, rng), f"activity:{name}")
        if h < args.days * 24:
            hourly.append({"t": boundary, "stamp": stamp(boundary, base_wd), **dict(pos)})

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "residents.jsonl", "w") as f:
        for r in rows:
            t0, t1 = float(r["t0_min"]) - off, float(r["t1_min"]) - off
            act = spec["activities"].get(r["activity"])
            if act is None or t1 <= 0 or t0 >= horizon:
                continue
            f.write(json.dumps({"resident": "resident_1",
                                "activity": r["activity"],
                                "t0": int(max(t0, 0)), "t1": int(min(t1, horizon)),
                                "at": act.get("at")}) + "\n")
    with open(args.out / "events.jsonl", "w") as f:
        for e in log:
            f.write(json.dumps(e) + "\n")
    objects = list(spec["placements"])
    with open(args.out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + objects)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in objects])
    moves = {}
    for e in log:
        moves[e["object"]] = moves.get(e["object"], 0) + 1
    (args.out / "meta.json").write_text(json.dumps({
        "household": spec["household"], "spec": str(args.binding),
        "activities_csv": str(csv_path), "real_day0": str(day0),
        "start_day": args.start_day, "days": args.days, "seed": args.seed,
        "n_events": len(log), "tidying": tidy_stats,
        "moves_per_object": dict(sorted(moves.items(), key=lambda kv: -kv[1])),
    }, indent=2))
    print(f"{spec['household']}: {len(log)} events over {args.days} real days "
          f"(window day {args.start_day}+, day0={day0}) -> {args.out}")


if __name__ == "__main__":
    main()
