#!/usr/bin/env python3
"""Dated-activity simulator: detailed_activities + object_motions -> timeline.

Stage 3 of the authoring chain. Where the retired `simulate_schedule.py`
realized a WEEKLY block pattern, this consumes a hand-authored DATED
calendar (`<hh>/detailed_activities.yaml`: one entry per day, clock times,
story notes) plus the per-activity object rules
(`<hh>/object_motions.yaml`), so day-specific story beats — a covered
double shift, a dentist appointment that splits a sleep, a reset that gets
abandoned midway — are expressible directly instead of being averaged into
a weekly template.

Timing model: each activity's realized start is its authored time plus
seeded jitter (same CASAS-calibrated classes as before, scaled by the
resident's punctuality persona), CLAMPED to preserve the authored order —
the calendar is the story, jitter only blurs it. A block runs until the
SAME resident's next block starts, so the author never writes end times.

Multi-resident households: each calendar item may carry `r: <resident_id>`
(default: the first resident). Residents' sequences are realized
independently, so their blocks overlap freely in time — Gordon can nap
while Mei-Lin runs errands — and each block's object rules fire with that
block, tidy walks pacing by the acting resident's own jitter_scale. A
shared moment is written as one block per participant, owned by whoever's
objects move (the persona's chore treaty usually decides).

Object rules per activity (`during` at start, `after` at end) use the same
vocabulary as the retired spec: {dest}, {dest, p, else}, {dist}, optional
only_from, and reset_all for a timed nearest-first tidying walk bounded by
the block's duration. `day_overrides` in object_motions patch specific
days (e.g. a storm week's umbrella).

Emits the standard timeline artifacts, unchanged so the whole downstream
chain (export_bank -> baselines) works as-is: events.jsonl (every parent
change with its causing activity), hourly.csv, residents.jsonl, meta.json.

Deliberate fix carried over: daily misplacement is drawn from AWAKE time
(inside any non-sleep block) instead of a fixed 10:00-21:30 window, which
was wrong for night-shift households — their awake hours are the old
window's sleep hours.

Usage:
  python profiles/revamp_v1/simulate_activities.py \
      profiles/revamp_v1/claude-fable-5/hh1 --seed 0 --out <timeline_dir>
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import pathlib
import random

import yaml

ELSEWHERE = "ELSEWHERE"
PERSON = "person:"
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
JITTER_CLASSES = {"external": 10, "routine": 30, "flexible": 75, "loose": 110}
TIDY_MIN, TIDY_MAX = 2.0, 5.0          # minutes per tidied item, pre-scale
SLEEP_ACTIVITIES = ("daysleep", "sleep", "nap_attempt")


def hhmm(text: str) -> tuple[int, int]:
    """('22:05+1') -> (1325 minutes, +1 day)."""
    plus = text.count("+")
    clock = text.split("+")[0]
    h, m = clock.split(":")
    return int(h) * 60 + int(m), plus


def stamp(t: int) -> str:
    d, m = divmod(int(t), 1440)
    return f"d{d:02d} {DAY_NAMES[d % 7]} {m // 60:02d}:{m % 60:02d}"


class _StrictLoader(yaml.SafeLoader):
    """SafeLoader that REFUSES duplicate mapping keys.

    Plain safe_load keeps the last of two same-key entries silently. In an
    object-motions file that means one of an object's two rules for the same
    activity vanishes — which stranded a cereal bowl on a couch for 21 days
    before this guard existed. One rule per (activity, object) is the
    contract; a second is an authoring error, not an override.
    """


def _no_duplicates(loader: yaml.SafeLoader, node: yaml.MappingNode,
                   deep: bool = False) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise AssertionError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1} "
                f"of {key_node.start_mark.name} — one rule per (activity, "
                f"object); merge them or move one to another activity")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def load(household: pathlib.Path) -> tuple[dict, dict]:
    """Both authored files, with duplicate mapping keys rejected loudly."""
    with open(household / "detailed_activities.yaml") as f:
        acts = yaml.load(f, Loader=_StrictLoader)
    with open(household / "object_motions.yaml") as f:
        motions = yaml.load(f, Loader=_StrictLoader)
    return acts, motions


def validate(acts: dict, motions: dict) -> None:
    """Loud, specific failures: this is the last human-authored boundary."""
    recs = {r["id"] for r in motions["receptacles"]}
    residents = {r["id"] for r in motions["residents"]}
    locs = recs | {ELSEWHERE} | {PERSON + r for r in residents}
    default_r = motions["residents"][0]["id"]
    for day in acts["calendar"]:
        for item in day["activities"]:
            rid = item.get("r", default_r)
            assert rid in residents, (
                f"day {day['day']}: activity {item['a']} names unknown "
                f"resident {rid!r}")
    objs = set(motions["placements"])
    defined = set(motions["object_motions"])
    used = {a["a"] for day in acts["calendar"] for a in day["activities"]}
    assert used <= defined, f"activities without object rules: {sorted(used - defined)}"
    assert defined <= used, f"object rules for unused activities: {sorted(defined - used)}"
    for obj, p in motions["placements"].items():
        assert p["home"] in locs, f"{obj}: unknown home {p['home']}"
        for r in p.get("misplace_set", []):
            assert r in recs, f"{obj}: misplace target {r} is not a receptacle"

    reachable = {obj: {p["home"]} for obj, p in motions["placements"].items()}
    for name, act in motions["object_motions"].items():
        assert act.get("at") in recs | {ELSEWHERE}, f"{name}: bad at {act.get('at')}"
        for obj, dest in act.get("during", {}).items():
            assert obj in objs, f"{name}.during: unknown object {obj}"
            assert dest in locs, f"{name}.during: unknown location {dest}"
            reachable[obj].add(dest)
        for obj, rule in act.get("after", {}).items():
            assert obj in objs, f"{name}.after: unknown object {obj}"
            targets = (set(rule["dist"]) if "dist" in rule
                       else {rule["dest"]} | ({rule["else"]} if "else" in rule else set()))
            if "dist" in rule:
                assert abs(sum(rule["dist"].values()) - 1.0) < 1e-6, \
                    f"{name}.after.{obj}: dist does not sum to 1"
            for r in targets | set(rule.get("only_from", [])):
                assert r in locs, f"{name}.after.{obj}: unknown location {r}"
            reachable[obj] |= targets
        for obj in act.get("reset_all", {}).get("objects", []):
            assert obj in objs, f"{name}.reset_all: unknown object {obj}"
    for obj, p in motions["placements"].items():
        mobile = len(reachable[obj]) > 1 or "p_misplace" in p
        assert mobile != bool(p.get("static")), (
            f"{obj}: static={bool(p.get('static'))} contradicts its rules "
            f"{sorted(reachable[obj])} — declare immobility, never let it happen")


def realize(acts: dict, motions: dict, rng: random.Random,
            days: int) -> list[dict]:
    """Authored calendar -> jittered blocks; order preserved PER RESIDENT."""
    scales = {r["id"]: r.get("jitter_scale", 1.0) for r in motions["residents"]}
    for rid, scale in scales.items():
        assert 0.5 <= scale <= 2.0, \
            f"{rid}: jitter_scale {scale} outside [0.5, 2.0]"
    default_r = motions["residents"][0]["id"]
    per_resident: dict[str, list[tuple[int, str, str]]] = {}
    for entry in acts["calendar"]:
        for item in entry["activities"]:
            minute, plus = hhmm(item["t"])
            per_resident.setdefault(item.get("r", default_r), []).append(
                (entry["day"] * 1440 + minute + 1440 * plus,
                 item["a"], item.get("note", "")))

    blocks: list[dict] = []
    # Deterministic resident order; each resident draws from the shared rng
    # in that order, so runs stay reproducible.
    for rid in sorted(per_resident):
        raw = sorted(per_resident[rid], key=lambda b: b[0])
        mine: list[dict] = []
        for i, (t0, name, note) in enumerate(raw):
            cls = motions["object_motions"][name].get("jitter", "routine")
            sigma = JITTER_CLASSES[cls] * scales[rid]
            offset = round(max(-2.5 * sigma,
                               min(2.5 * sigma, rng.gauss(0, sigma))))
            # Clamp into the open interval between this resident's
            # neighbours: the authored sequence is the story and must
            # survive jitter intact.
            lo = mine[-1]["t0"] + 1 if mine else 0
            hi = raw[i + 1][0] - 1 if i + 1 < len(raw) else days * 1440
            mine.append({"activity": name, "note": note, "resident": rid,
                         "t0": max(lo, min(hi, t0 + offset))})
        for i, b in enumerate(mine):
            b["t1"] = mine[i + 1]["t0"] if i + 1 < len(mine) else days * 1440
            b["at"] = motions["object_motions"][b["activity"]].get("at")
        blocks += mine
    blocks.sort(key=lambda b: b["t0"])
    return [b for b in blocks if b["t0"] < days * 1440]


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


def overrides_for(motions: dict, day: int, activity: str) -> dict:
    """Merged `after` patch from day_overrides for one block."""
    patch: dict = {}
    for ov in motions.get("day_overrides", []) or []:
        if day in ov["days"] and ov["activity"] == activity:
            patch.update(ov.get("after", {}))
    return patch


def simulate(acts: dict, motions: dict, days: int, seed: int):
    rng = random.Random(seed)
    blocks = realize(acts, motions, rng, days)
    placements = motions["placements"]
    pos = {obj: p["home"] for obj, p in placements.items()}
    statics = {o for o, p in placements.items() if p.get("static")}
    rec_order = {r["id"]: i for i, r in enumerate(motions["receptacles"])}
    scales = {r["id"]: r.get("jitter_scale", 1.0)
              for r in motions["residents"]}
    horizon = days * 1440
    log: list[dict] = []
    stats = {"tidy_bouts": 0, "tidy_moved": 0, "tidy_ran_out_of_time": 0,
             "blocks": len(blocks)}

    heap: list = []
    seq = 0

    def push(t, order, kind, payload):
        nonlocal seq
        heapq.heappush(heap, (t, order, seq, kind, payload))
        seq += 1

    def move(t, obj, dest, by):
        if dest is not None and pos[obj] != dest:
            log.append({"t": int(t), "stamp": stamp(t), "object": obj,
                        "from": pos[obj], "to": dest, "by": by})
            pos[obj] = dest

    obj_order = {o: i for i, o in enumerate(placements)}

    def plan_tidy(block, cfg):
        """Timed nearest-first walk, bounded by the block's own duration.

        Candidates keep the placements-declaration order, and distance
        ties break on it: building the list from a set made the walk
        depend on interpreter hash randomization — two runs of the same
        (spec, seed) tidied sink dishes in different orders.
        """
        scope = set(cfg.get("objects", placements))
        cands = [o for o in placements
                 if o in scope
                 and o not in statics
                 and not placements[o]["home"].startswith(PERSON)
                 and pos[o] not in (ELSEWHERE, placements[o]["home"])
                 and not pos[o].startswith(PERSON)]
        stats["tidy_bouts"] += 1
        t, here = block["t0"], block["at"]
        while cands:
            cands.sort(key=lambda o: (abs(rec_order.get(pos[o], 99)
                                          - rec_order.get(here, 0)),
                                      obj_order[o]))
            obj = cands.pop(0)
            if rng.random() >= cfg["p"]:
                continue
            t += rng.uniform(TIDY_MIN, TIDY_MAX) * scales[block["resident"]]
            if t >= block["t1"]:
                stats["tidy_ran_out_of_time"] += 1
                break
            push(t, 3, "tidy", (obj, placements[obj]["home"], block["activity"]))
            here = placements[obj]["home"]

    for block in blocks:
        push(block["t0"], 0, "during", block)
        if block["t1"] < horizon:
            push(block["t1"], 1, "after", block)

    # Daily misplacement, drawn from AWAKE time (see module docstring).
    awake = [(b["t0"], b["t1"]) for b in blocks
             if not any(k in b["activity"] for k in SLEEP_ACTIVITIES)]
    for d in range(days):
        spans = [(max(a, d * 1440), min(b, (d + 1) * 1440))
                 for a, b in awake if a < (d + 1) * 1440 and b > d * 1440]
        spans = [(a, b) for a, b in spans if b > a + 1]
        for obj, p in placements.items():
            if p.get("static") or "p_misplace" not in p or not spans:
                continue
            if rng.random() < p["p_misplace"]:
                a, b = rng.choice(spans)
                push(rng.randrange(a, b), 2, "misplace",
                     (obj, rng.choice(p["misplace_set"])))

    hourly = []
    for h in range(days * 24 + 1):
        boundary = h * 60
        while heap and heap[0][0] < boundary:
            t, _, _, kind, payload = heapq.heappop(heap)
            if kind == "during":
                act = motions["object_motions"][payload["activity"]]
                for obj, dest in act.get("during", {}).items():
                    move(t, obj, dest, f"activity:{payload['activity']}")
                if "reset_all" in act:
                    plan_tidy(payload, act["reset_all"])
            elif kind == "after":
                name = payload["activity"]
                act = motions["object_motions"][name]
                rules = dict(act.get("after", {}))
                rules.update(overrides_for(motions, payload["t0"] // 1440, name))
                for obj, rule in rules.items():
                    if "only_from" in rule and pos[obj] not in rule["only_from"]:
                        continue
                    move(t, obj, sample_after(rule, rng), f"activity:{name}")
            elif kind == "tidy":
                obj, home, name = payload
                if pos[obj] not in (ELSEWHERE, home) and not pos[obj].startswith(PERSON):
                    move(t, obj, home, f"tidy:{name}")
                    stats["tidy_moved"] += 1
            else:
                obj, dest = payload
                if pos[obj] != ELSEWHERE:      # person-held CAN be set down
                    move(t, obj, dest, "misplace")
        if h < days * 24:
            hourly.append({"t": boundary, "stamp": stamp(boundary), **dict(pos)})
    return log, hourly, blocks, stats


def write_outputs(out: pathlib.Path, motions: dict, log, hourly, blocks,
                  stats, days: int, seed: int, household: pathlib.Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "events.jsonl", "w") as f:
        for e in log:
            f.write(json.dumps(e) + "\n")
    objects = list(motions["placements"])
    with open(out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + objects)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in objects])
    with open(out / "residents.jsonl", "w") as f:
        for b in blocks:
            f.write(json.dumps({
                "resident": b["resident"], "activity": b["activity"],
                "t0": int(max(b["t0"], 0)), "t1": int(min(b["t1"], days * 1440)),
                "at": b["at"], "note": b["note"]}) + "\n")
    moves: dict[str, int] = {}
    for e in log:
        moves[e["object"]] = moves.get(e["object"], 0) + 1
    (out / "meta.json").write_text(json.dumps({
        "household": motions["household"],
        "household_type": motions.get("household_type"),
        "source": str(household), "days": days, "seed": seed,
        "n_events": len(log), "jitter_classes": JITTER_CLASSES,
        "activity_stats": stats,
        "moves_per_object": dict(sorted(moves.items(), key=lambda kv: -kv[1])),
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("household", type=pathlib.Path,
                    help="household folder (persona + detailed_activities + object_motions)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--days", type=int, default=None,
                    help="default: the calendar's own `days`")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    acts, motions = load(args.household)
    validate(acts, motions)
    days = args.days or int(acts["days"])
    log, hourly, blocks, stats = simulate(acts, motions, days, args.seed)
    write_outputs(args.out, motions, log, hourly, blocks, stats, days,
                  args.seed, args.household)
    print(f"{motions['household']}: {len(log)} events over {days} days "
          f"({stats['blocks']} activity blocks; tidy {stats['tidy_moved']} "
          f"moves in {stats['tidy_bouts']} bouts, "
          f"{stats['tidy_ran_out_of_time']} cut short) -> {args.out}")


if __name__ == "__main__":
    main()
