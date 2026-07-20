"""Symbolic generator: profile -> N-day receptacle-level movement logs.

Emits the EXACT episode format gt_logger writes and ReplayWorld reads
(registry.json + events.jsonl + snapshot_day*.json), so the entire
downstream stack — belief zoo, day-budget harness, llm_agent memory tables —
replays profile worlds unchanged.

Dynamics semantics (deterministic given (profile, seed)):

  * Calendar: day 0 = Monday. Blocks with end <= start wrap past midnight.
  * Jitter: each realized block start = nominal + U[-j, +j] (integer
    minutes), duration preserved. Realized blocks per resident are made
    consistent chronologically: an overlapping SAME-activity successor is
    merged (union — covers the spec profile's Fri-night sleep meeting the
    weekend sleep block); a DIFFERENT-activity successor is clamped to start
    at the previous realized end (shrinking it; dropped if squeezed to
    nothing, counted in meta).
  * during: at realized block start each `during` object moves to its
    during-receptacle. after: at realized block end, each `after` object
    goes to dest with prob p, else to `else` (or stays if no else).
    dest null = ELSEWHERE (carried/left the house) until some later
    during/after places it again.
  * p_misplace: per day, with prob p_misplace the object drifts to a uniform
    pick from misplace_set at a uniform minute in [08:00, 22:00) that is not
    inside any realized block binding that object (noise outside scripted
    activities, per the schema).
  * Dish-cycle (generator-level, all profiles, per the schema comment):
    objects sitting on any `sink*` receptacle at 21:30 return to their
    placement home at 21:45 with p = 0.9.
  * Events are recorded only when the parent actually changes; moved_by is
    "activity:<name>" | "misplace" | "dish_cycle". Snapshots at every day's
    00:00 reflect state strictly before that minute's events (the
    ReplayWorld bisect contract).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
from dataclasses import dataclass
from typing import Optional

from dynbelief import ELSEWHERE_ID, ELSEWHERE_LABEL
from dynbelief.profiles.schema import (
    Profile, DAY_IDX, MIN_PER_DAY, default_class,
)

DISH_CHECK_MIN = 21 * 60 + 30
DISH_RETURN_MIN = 21 * 60 + 45
DISH_RETURN_P = 0.9
MISPLACE_WINDOW = (8 * 60, 22 * 60)


@dataclass
class RealizedBlock:
    resident: str
    activity: str
    t0: int          # absolute minutes
    t1: int


def _seed_int(profile: Profile, seed: int) -> int:
    h = hashlib.sha256(f"{profile.household}:{seed}".encode()).hexdigest()
    return int(h[:16], 16)


def realize_schedule(ch: Profile, n_days: int, rng: random.Random) -> list[RealizedBlock]:
    blocks: list[RealizedBlock] = []
    dropped = 0
    for r in ch.residents:
        realized: list[RealizedBlock] = []
        for day in range(n_days):
            weekday = day % 7
            todays = [b for b in r.schedule
                      if weekday in (DAY_IDX[d] for d in b.days)]
            todays.sort(key=lambda b: b.start_min)
            for b in todays:
                j = ch.activities[b.activity].jitter_min if b.activity in ch.activities else 0
                t0 = day * MIN_PER_DAY + b.start_min + (rng.randint(-j, j) if j else 0)
                t1 = t0 + b.duration
                if realized and t0 < realized[-1].t1:
                    prev = realized[-1]
                    if prev.activity == b.activity:
                        prev.t1 = max(prev.t1, t1)   # merge same-activity overlap
                        continue
                    t0 = prev.t1                     # clamp different-activity
                    if t0 >= t1:
                        dropped += 1
                        continue
                realized.append(RealizedBlock(r.id, b.activity, t0, t1))
        blocks.extend(realized)
    blocks.sort(key=lambda x: (x.t0, x.resident))
    if dropped:
        blocks_meta_dropped[0] = dropped  # noqa: F821 — see simulate()
    return blocks


def simulate(ch: Profile, n_days: int = 30, seed: int = 0):
    """Returns (events, snapshots, meta). events: [{t_min, label,
    parent_label, moved_by}]; snapshots: [{day, t_min, parents{label:label}}]."""
    rng = random.Random(_seed_int(ch, seed))
    global blocks_meta_dropped
    blocks_meta_dropped = [0]
    blocks = realize_schedule(ch, n_days, rng)

    # ---- proposal stream: (t, seq, obj, dest_or_None_marker, moved_by) -----
    proposals: list[tuple[int, int, str, Optional[str], str, Optional[float]]] = []
    seq = 0
    for blk in blocks:
        act = ch.activities.get(blk.activity)
        if act is None:
            continue
        for obj, rid in act.during.items():
            proposals.append((blk.t0, seq, obj, rid, f"activity:{blk.activity}", None))
            seq += 1
        for obj, br in act.after.items():
            # branch resolved at apply time (needs one rng draw in t-order)
            proposals.append((blk.t1, seq, obj, "__AFTER__", f"activity:{blk.activity}", None))
            seq += 1

    # misplacement noise
    bound_ivals: dict[str, list[tuple[int, int]]] = {}
    for blk in blocks:
        act = ch.activities.get(blk.activity)
        if act is None:
            continue
        for obj in act.objects:
            bound_ivals.setdefault(obj, []).append((blk.t0, blk.t1))
    for obj, p in sorted(ch.placements.items()):
        if p.p_misplace <= 0:
            continue
        for day in range(n_days):
            if rng.random() >= p.p_misplace:
                continue
            for _ in range(8):  # find a minute outside the object's blocks
                t = day * MIN_PER_DAY + rng.randrange(*MISPLACE_WINDOW)
                if not any(a <= t < b for a, b in bound_ivals.get(obj, [])):
                    dest = rng.choice(p.misplace_set)
                    proposals.append((t, seq, obj, dest, "misplace", None))
                    seq += 1
                    break

    # dish-cycle checkpoints (resolved at apply time against current state)
    for day in range(n_days):
        proposals.append((day * MIN_PER_DAY + DISH_CHECK_MIN, seq,
                          "__DISH__", None, "dish_cycle", None))
        seq += 1

    proposals.sort(key=lambda x: (x[0], x[1]))

    # ---- apply chronologically --------------------------------------------
    state: dict[str, str] = {o: p.home for o, p in ch.placements.items()}
    after_lookup = {name: a.after for name, a in ch.activities.items()}
    events: list[dict] = []
    snapshots: list[dict] = []
    horizon = n_days * MIN_PER_DAY
    next_snap_day = 0

    def _move(t, obj, dest, moved_by):
        cur = state.get(obj)
        dest_label = dest if dest is not None else ELSEWHERE_LABEL
        if cur == dest_label:
            return
        state[obj] = dest_label
        events.append({"t_min": t, "label": obj,
                       "parent_label": dest_label, "moved_by": moved_by})

    pending_dish: list[tuple[int, str]] = []
    for (t, _s, obj, dest, moved_by, _x) in proposals:
        if t >= horizon:
            continue
        while next_snap_day * MIN_PER_DAY <= t and next_snap_day < n_days:
            snapshots.append({"day": next_snap_day,
                              "t_min": next_snap_day * MIN_PER_DAY,
                              "parents": dict(sorted(state.items()))})
            next_snap_day += 1
        # flush due dish returns (queued at 21:30, fire at 21:45)
        while pending_dish and pending_dish[0][0] <= t:
            dt, dobj = pending_dish.pop(0)
            if state.get(dobj, "").startswith("sink"):
                _move(dt, dobj, ch.placements[dobj].home, "dish_cycle")
        if obj == "__DISH__":
            for dobj in sorted(state):
                if state[dobj].startswith("sink") and rng.random() < DISH_RETURN_P:
                    pending_dish.append((t + (DISH_RETURN_MIN - DISH_CHECK_MIN), dobj))
            continue
        if dest == "__AFTER__":
            br = after_lookup[moved_by.split(":", 1)[1]][obj]
            if rng.random() < br.p:
                _move(t, obj, br.dest, moved_by)
            elif br.else_dest is not None:
                _move(t, obj, br.else_dest, moved_by)
            continue
        _move(t, obj, dest, moved_by)

    for dt, dobj in pending_dish:
        if dt < horizon and state.get(dobj, "").startswith("sink"):
            _move(dt, dobj, ch.placements[dobj].home, "dish_cycle")
    events.sort(key=lambda e: e["t_min"])
    while next_snap_day < n_days:
        snapshots.append({"day": next_snap_day,
                          "t_min": next_snap_day * MIN_PER_DAY,
                          "parents": dict(sorted(state.items()))})
        next_snap_day += 1

    meta = {"household": ch.household, "seed": seed, "n_days": n_days,
            "n_events": len(events), "dropped_blocks": blocks_meta_dropped[0],
            "n_realized_blocks": len(blocks)}
    return events, snapshots, meta


def write_episode(ch: Profile, out_dir: str | pathlib.Path,
                  n_days: int = 30, seed: int = 0) -> pathlib.Path:
    """Simulate and write a ReplayWorld-compatible episode directory."""
    events, snapshots, meta = simulate(ch, n_days=n_days, seed=seed)
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    obj_ids = {lbl: i for i, lbl in enumerate(sorted(ch.placements))}
    recep_ids = {ELSEWHERE_LABEL: ELSEWHERE_ID}
    for i, rid in enumerate(sorted(ch.receptacle_ids), start=1):
        recep_ids[rid] = i
    recep_meta = {}
    for lbl, i in recep_ids.items():
        recep_meta[str(i)] = {
            "label": lbl,
            "room": None if lbl == ELSEWHERE_LABEL else ch.room_of(lbl),
            "position": None,
            "category": None if lbl == ELSEWHERE_LABEL else default_class(lbl),
        }

    registry = {
        "scene_id": ch.household,
        "n_days": n_days, "days": list(range(n_days)),
        "folders": [], "objects": obj_ids, "receptacles": recep_ids,
        "receptacle_meta": recep_meta, "elsewhere_id": ELSEWHERE_ID,
        "generator": {"kind": "profile_symbolic_v1", "seed": seed,
                      "profile": ch.household, "status": ch.status,
                      "derived_from": ch.derived_from,
                      "transformation": ch.transformation, **{
                          k: meta[k] for k in ("n_events", "dropped_blocks",
                                               "n_realized_blocks")}},
        "object_class": {o: p.cls for o, p in ch.placements.items()},
    }
    (out / "registry.json").write_text(json.dumps(registry, indent=1))

    with open(out / "events.jsonl", "w") as f:
        for e in sorted(events, key=lambda e: (e["t_min"], e["label"])):
            f.write(json.dumps({"t_min": e["t_min"],
                                "object_id": obj_ids[e["label"]],
                                "parent_id": recep_ids[e["parent_label"]],
                                "states": {}, "moved_by": e["moved_by"]}) + "\n")

    for snap in snapshots:
        (out / f"snapshot_day{snap['day']}.json").write_text(json.dumps({
            "t_min": snap["t_min"], "day": snap["day"],
            "parents": {str(obj_ids[o]): recep_ids[p]
                        for o, p in snap["parents"].items()},
            "states": {},
        }, indent=1))
    return out
