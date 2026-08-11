#!/usr/bin/env python3
"""Deterministic stage-2 simulator: schedule spec -> N-day object timelines.

Reads a hand-compiled schedule spec (see claude-fable-5/schedules/*.yaml),
realizes each resident's weekly activity blocks with per-block start jitter,
and moves objects at block boundaries. A block may carry `p: 0.55` — each
listed day it then fires only with that probability (seeded), for
sometimes-things like an occasional weekend outing; omitted means every
listed day, as before.

  during:   at realized block start, each bound object moves to its
            during-receptacle, to ELSEWHERE (carried out of the house), or
            to person:<resident_id> (picked up and carried)
  after:    at realized block end, each bound object is placed by one of
              {dest: r}                          always r
              {dest: r, p: 0.8, else: r2}        r w.p. p, else r2
              {dist: {r: 0.5, r2: 0.3, r3: 0.2}} categorical
            an optional only_from: [locations] gates the move on where the
            object currently sits
  reset_all: {p: q [, objects: [...]]}
            a TIDYING PROCESS, not an instant sweep: starting when the
            block starts, the resident doing it walks the house returning
            astray objects to their placement homes, nearest-first from
            wherever they currently stand (greedy walk over anchor
            geometry when --anchors is given, room-grouped spec order
            otherwise). Each item takes U(2,5) minutes scaled by the
            tidier's jitter_scale (a messy or distractible person tidies
            slower), each is handled w.p. q, and the bout ends when the
            block does — a 5-minute tidy touches 1-2 items, a long sweep
            does the whole house. Optional objects: restricts scope
            (e.g. a nightly toy sweep). Objects that are ELSEWHERE or
            whose home is on a person are never tidied.

Jitter model (calibrated against CASAS free-living homes — see
casas/README.md): each activity declares either a named `jitter` class or a
legacy `jitter_min` (uniform +/-N). Classes draw start offsets from a
Gaussian clamped at +/-2.5 sigma:

    external  sigma 10   contractual anchors: shifts, commutes, appointments
    routine   sigma 30   body-clock / chained-to-anchor activities
    flexible  sigma 75   self-paced daily activities
    loose     sigma 110  whim-driven activities

Each resident may carry `jitter_scale` (default 1.0, bounded [0.5, 2.0]):
a punctuality persona multiplying every sigma for that resident — and the
per-item tidying time above.

Overlap resolution (per resident, chronological): when realized blocks
collide, the MORE-ANCHORED block (smaller effective sigma) keeps its
boundary; a pushed block keeps its duration; same-activity overlaps merge;
blocks squeezed to nothing are dropped (all counted in meta.json).

Locations are receptacle ids plus two virtual kinds: ELSEWHERE (out of the
house) and person:<resident_id> (carried; the object is wherever its
carrier is — e.g. a phone whose placement home IS person:resident_1).
Activities may declare `at: <receptacle|ELSEWHERE>`, where the activity
takes place; realized blocks are written to residents.jsonl so the
spatializer can place carried objects and draw the residents themselves.

Emits: events.jsonl (every parent change, with cause), hourly.csv,
residents.jsonl, meta.json. Deterministic given (spec, seed, days).

Usage:
  python simulate_schedule.py claude-fable-5/schedules/hh_001_schedule.yaml \
      --days 14 --seed 0 --anchors ../../visualization/configs/hh_001_102343992.yaml \
      --out claude-fable-5/timelines/hh_001_seed0
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import pathlib
import random

import yaml

ELSEWHERE = "ELSEWHERE"
PERSON = "person:"
DAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MISPLACE_WINDOW = (10 * 60, 21 * 60 + 30)
TIDY_MIN, TIDY_MAX = 2.0, 5.0          # minutes per tidied item, pre-scale

JITTER_CLASSES = {"external": 10, "routine": 30, "flexible": 75, "loose": 110}


def hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def stamp(t: int) -> str:
    d, m = divmod(int(t), 1440)
    return f"d{d:02d} {DAY_NAMES[d % 7]} {m // 60:02d}:{m % 60:02d}"


def jitter_sigma(act: dict, classes: dict, scale: float = 1.0) -> float:
    if "jitter" in act:
        return classes[act["jitter"]] * scale
    return act.get("jitter_min", 0) * scale / (3 ** 0.5)


def sample_jitter(act: dict, classes: dict, rng: random.Random,
                  scale: float = 1.0) -> int:
    if "jitter" in act:
        s = classes[act["jitter"]] * scale
        return round(max(-2.5 * s, min(2.5 * s, rng.gauss(0, s))))
    j = round(act.get("jitter_min", 0) * scale)
    return rng.randint(-j, j) if j else 0


# ---------------------------------------------------------------- validate

def validate(spec: dict) -> None:
    resident_ids = {r["id"] for r in spec["residents"]}
    recs = {r["id"] for r in spec["receptacles"]}
    locs = recs | {ELSEWHERE} | {PERSON + rid for rid in resident_ids}
    objs = set(spec["placements"])

    for obj, p in spec["placements"].items():
        assert p["home"] in locs, f"{obj}: unknown home {p['home']}"
        for r in p.get("misplace_set", []):
            assert r in recs, f"{obj}: misplace target must be a receptacle, got {r}"

    reachable = {obj: {p["home"]} for obj, p in spec["placements"].items()}
    for name, act in spec["activities"].items():
        if "at" in act:
            assert act["at"] in recs | {ELSEWHERE}, f"{name}: unknown at {act['at']}"
        if "reset_all" in act:
            for obj in act["reset_all"].get("objects", []):
                assert obj in objs, f"{name}.reset_all: unknown object {obj}"
        for obj, r in act.get("during", {}).items():
            assert obj in objs, f"{name}.during: unknown object {obj}"
            assert r in locs, f"{name}.during: unknown location {r}"
            reachable[obj].add(r)
        for obj, rule in act.get("after", {}).items():
            assert obj in objs, f"{name}.after: unknown object {obj}"
            if "dist" in rule:
                assert abs(sum(rule["dist"].values()) - 1.0) < 1e-6, \
                    f"{name}.after.{obj}: dist does not sum to 1"
                targets = set(rule["dist"])
            else:
                targets = {rule["dest"]} | ({rule["else"]} if "else" in rule else set())
            for r in targets | set(rule.get("only_from", [])):
                assert r in locs, f"{name}.after.{obj}: unknown location {r}"
            reachable[obj] |= targets

    for res in spec["residents"]:
        for b in res["schedule"]:
            if "p" in b:
                assert 0.0 < b["p"] <= 1.0, \
                    f"block {b['activity']}: p {b['p']} outside (0, 1]"
    scheduled = {b["activity"] for res in spec["residents"] for b in res["schedule"]}
    assert scheduled <= set(spec["activities"]), \
        f"blocks without activity defs: {scheduled - set(spec['activities'])}"
    classes = {**JITTER_CLASSES, **spec.get("jitter_classes", {})}
    for name, act in spec["activities"].items():
        if "jitter" in act:
            assert act["jitter"] in classes, \
                f"{name}: unknown jitter class {act['jitter']!r}"

    # Reachability lint: immobility must be declared, never accidental.
    # A tidy (reset_all) can also move an object back home, so any object in
    # tidy scope whose current position can differ from home counts mobile.
    for obj, p in spec["placements"].items():
        static = p.get("static", False)
        mobile = len(reachable[obj]) > 1 or "p_misplace" in p
        assert not (mobile and static), \
            f"{obj}: declared static but has rules that would move it {sorted(reachable[obj])}"
        assert mobile or static, (
            f"{obj}: can never move (every rule targets {reachable[obj]}) — "
            f"give it another destination or declare `static: true`")


def check_inventory(spec: dict, spec_path: pathlib.Path) -> None:
    prof_path = (spec_path.parent / spec["source_profile"]).resolve()
    prof = yaml.safe_load(prof_path.read_text())
    inventory = {o["id"] for o in prof["object_inventory"]}
    placed = set(spec["placements"])
    assert placed == inventory, (
        f"placements != profile inventory; missing={sorted(inventory - placed)} "
        f"extra={sorted(placed - inventory)}")


# ---------------------------------------------------------------- simulate

def sample_after(rule: dict, rng: random.Random) -> str:
    if "dist" in rule:
        r, acc = rng.random(), 0.0
        for dest, p in rule["dist"].items():
            acc += p
            if r < acc:
                return dest
        return dest
    if "p" in rule and rng.random() >= rule["p"]:
        return rule.get("else", rule["dest"])
    return rule["dest"]


def simulate(spec: dict, days: int, seed: int,
             anchors: dict[str, tuple[float, float]]):
    rng = random.Random(seed)
    classes = {**JITTER_CLASSES, **spec.get("jitter_classes", {})}
    pos = {obj: p["home"] for obj, p in spec["placements"].items()}
    horizon = days * 1440
    scale_of = {r["id"]: r.get("jitter_scale", 1.0) for r in spec["residents"]}
    rec_order = {r["id"]: i for i, r in enumerate(spec["receptacles"])}

    # ---- realize blocks per resident (jitter + anchor-priority overlaps)
    stats = {"merged": 0, "truncated": 0, "dropped": 0,
             "tidy_bouts": 0, "tidy_moved": 0, "tidy_ran_out_of_time": 0}
    heap, hseq = [], 0

    def push(t, order, kind, payload):
        nonlocal hseq
        heapq.heappush(heap, (t, order, hseq, kind, payload))
        hseq += 1

    resident_blocks = {}
    for res in spec["residents"]:
        scale = res.get("jitter_scale", 1.0)
        assert 0.5 <= scale <= 2.0, \
            f"{res['id']}: jitter_scale {scale} outside calibrated range [0.5, 2.0]"
        jittered = []
        for block in res["schedule"]:
            name = block["activity"]
            act = spec["activities"][name]
            start, end = hhmm(block["start"]), hhmm(block["end"])
            dur = (end - start) % 1440 or 1440
            for d in range(days):
                if DAYS[d % 7] not in block["days"]:
                    continue
                if "p" in block and rng.random() >= block["p"]:
                    continue                      # sometimes-block skipped today
                n0 = d * 1440 + start
                t0 = n0 + sample_jitter(act, classes, rng, scale)
                jittered.append((n0, t0, t0 + dur, name, act))
        jittered.sort(key=lambda b: (b[0], b[1]))

        realized = []
        for _, t0, t1, name, act in jittered:
            if realized and t0 < realized[-1][1]:
                p0, p1, pname, pact = realized[-1]
                if name == pname:
                    realized[-1] = (p0, max(p1, t1), pname, pact)
                    stats["merged"] += 1
                    continue
                if jitter_sigma(act, classes, scale) <= jitter_sigma(pact, classes, scale):
                    stats["truncated"] += 1
                    if t0 <= p0:
                        realized.pop()
                        stats["dropped"] += 1
                    else:
                        realized[-1] = (p0, t0, pname, pact)
                else:
                    dur = t1 - t0
                    t0 = p1
                    t1 = t0 + dur
                    stats["truncated"] += 1
            realized.append((t0, t1, name, act))
        resident_blocks[res["id"]] = realized

        for t0, t1, name, act in realized:
            if 0 <= t0 < horizon:
                push(t0, 0, "during", (res["id"], name, act))
            if t1 < horizon:
                push(t1, 1, "after", (res["id"], name, act))

    # ---- daily misplacement (also how a carried phone gets set down astray)
    for d in range(days):
        for obj, p in spec["placements"].items():
            if p.get("static") or "p_misplace" not in p:
                continue
            if rng.random() < p["p_misplace"]:
                t = d * 1440 + rng.randrange(*MISPLACE_WINDOW)
                push(t, 2, "misplace", (obj, rng.choice(p["misplace_set"])))

    # ---- apply chronologically; tidy bouts inject their own future events
    log, hourly = [], []
    statics = {o for o, p in spec["placements"].items() if p.get("static")}

    def move(t, obj, dest, by):
        if dest is not None and pos[obj] != dest:
            log.append({"t": int(t), "stamp": stamp(t), "object": obj,
                        "from": pos[obj], "to": dest, "by": by})
            pos[obj] = dest

    def plan_tidy(t0, t1, res_id, name, act):
        """Sequential nearest-first tidy walk, time-limited by the block."""
        cfg = act["reset_all"]
        scope = set(cfg.get("objects", spec["placements"]))
        cands = [o for o in scope
                 if o not in statics
                 and not spec["placements"][o]["home"].startswith(PERSON)
                 and pos[o] != ELSEWHERE
                 and not pos[o].startswith(PERSON)
                 and pos[o] != spec["placements"][o]["home"]]
        stats["tidy_bouts"] += 1
        here = act.get("at")
        t = t0
        while cands:
            # nearest candidate from where the tidier stands
            def dist(o):
                a, b = anchors.get(pos[o]), anchors.get(here)
                if a and b:
                    return math.hypot(a[0] - b[0], a[1] - b[1])
                return rec_order.get(pos[o], 99)          # fallback: spec order
            cands.sort(key=dist)
            obj = cands.pop(0)
            if rng.random() >= cfg["p"]:
                continue                                   # skipped this bout
            t += rng.uniform(TIDY_MIN, TIDY_MAX) * scale_of.get(res_id, 1.0)
            if t >= t1:
                stats["tidy_ran_out_of_time"] += 1
                break
            push(t, 3, "tidy", (obj, spec["placements"][obj]["home"], name))
            here = spec["placements"][obj]["home"]         # walk continues from there

    ei_hour = 0
    for h in range(days * 24 + 1):
        boundary = h * 60
        while heap and heap[0][0] < boundary:
            t, _, _, kind, payload = heapq.heappop(heap)
            if kind == "during":
                res_id, name, act = payload
                for obj, r in act.get("during", {}).items():
                    move(t, obj, r, f"activity:{name}")
                if "reset_all" in act:
                    # find this block's end for the time budget
                    end = next((b1 for (b0, b1, n, _) in resident_blocks[res_id]
                                if n == name and b0 <= t < b1), t + 30)
                    plan_tidy(t, min(end, days * 1440), res_id, name, act)
            elif kind == "after":
                res_id, name, act = payload
                for obj, rule in act.get("after", {}).items():
                    if "only_from" in rule and pos[obj] not in rule["only_from"]:
                        continue
                    move(t, obj, sample_after(rule, rng), f"activity:{name}")
            elif kind == "tidy":
                obj, home, name = payload
                if pos[obj] not in (ELSEWHERE, home) and not pos[obj].startswith(PERSON):
                    move(t, obj, home, f"tidy:{name}")
                    stats["tidy_moved"] += 1
            elif kind == "misplace":
                obj, dest = payload
                if pos[obj] != ELSEWHERE:                  # person-held CAN be set down
                    move(t, obj, dest, "misplace")
        if h < days * 24:
            hourly.append({"t": boundary, "stamp": stamp(boundary), **dict(pos)})

    return log, hourly, resident_blocks, stats


# ---------------------------------------------------------------- main

def resolve_anchors(path: pathlib.Path | None) -> dict:
    """Receptacle -> (x, z) via the spatial config, matching spatialize.py's
    fraction-of-bbox rule (without the polygon nudge — proximity ordering
    doesn't need it)."""
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
    ap.add_argument("spec", type=pathlib.Path)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--anchors", type=pathlib.Path, default=None,
                    help="visualization spatial config; enables nearest-first tidy order")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    spec = yaml.safe_load(args.spec.read_text())
    validate(spec)
    check_inventory(spec, args.spec)
    anchors = resolve_anchors(args.anchors)
    log, hourly, resident_blocks, stats = simulate(spec, args.days, args.seed, anchors)

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "events.jsonl", "w") as f:
        for e in log:
            f.write(json.dumps(e) + "\n")
    objects = list(spec["placements"])
    with open(args.out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + objects)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in objects])
    with open(args.out / "residents.jsonl", "w") as f:
        for res_id, blocks in resident_blocks.items():
            for t0, t1, name, act in blocks:
                if t1 <= 0 or t0 >= args.days * 1440:
                    continue
                f.write(json.dumps({
                    "resident": res_id, "activity": name,
                    "t0": int(max(t0, 0)), "t1": int(min(t1, args.days * 1440)),
                    "at": act.get("at")}) + "\n")
    moves = {}
    for e in log:
        moves[e["object"]] = moves.get(e["object"], 0) + 1
    (args.out / "meta.json").write_text(json.dumps({
        "household": spec["household"], "spec": str(args.spec), "days": args.days,
        "seed": args.seed, "n_events": len(log),
        "jitter_classes": {**JITTER_CLASSES, **spec.get("jitter_classes", {})},
        "block_realization": {k: stats[k] for k in ("merged", "truncated", "dropped")},
        "tidying": {k: stats[k] for k in ("tidy_bouts", "tidy_moved",
                                          "tidy_ran_out_of_time")},
        "moves_per_object": dict(sorted(moves.items(), key=lambda kv: -kv[1])),
    }, indent=2))
    print(f"{spec['household']}: {len(log)} events over {args.days} days "
          f"(blocks m/t/d: {stats['merged']}/{stats['truncated']}/{stats['dropped']}; "
          f"tidy: {stats['tidy_moved']} moves in {stats['tidy_bouts']} bouts, "
          f"{stats['tidy_ran_out_of_time']} cut short) -> {args.out}")


if __name__ == "__main__":
    main()
