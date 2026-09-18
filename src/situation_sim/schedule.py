"""Daily schedule realization: role templates, event edits, jitter, bouts.

The placement function needs "what activity just ended" and "what the
resident does next", so each resident gets a realized list of bouts per day.
Timing constants are the copied values in ``timing_constants``.
"""
from __future__ import annotations

import copy
import math
import pathlib
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

from situation_sim import timing_constants as tc
from situation_sim.household import Household, Resident
from situation_sim.situation import DaySituation

ELSEWHERE = "ELSEWHERE"
MIN_PER_DAY = 1440


def load_activities(path: Optional[pathlib.Path] = None) -> dict:
    path = path or pathlib.Path(__file__).with_name("activities.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def _hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


@dataclass
class Bout:
    resident: str
    activity: str
    start: int                 # minutes from the day's midnight
    end: int
    room: str                  # room id or ELSEWHERE
    surface: Optional[str]     # receptacle id where used objects are left
    uses: List[str]            # object classes / group tokens fetched at start
    tidies: bool = False
    tidy_rooms: List[str] = field(default_factory=list)
    added_by: Optional[str] = None     # cause id that added the block
    edited_by: List[str] = field(default_factory=list)  # causes that delayed/shortened/extended it
    bout_index: int = 0
    n_bouts: int = 1

    @property
    def away(self) -> bool:
        return self.room == ELSEWHERE


def resolve_room(token: str, res: Resident, hh: Household) -> str:
    if token == ELSEWHERE:
        return ELSEWHERE
    if token == "bedroom":
        return res.bedroom
    if token == "workspace":
        return res.workspace
    if token == "dining_or_kitchen":
        return hh.has_room("dining") or "kitchen"
    return token


def resolve_surface(token: Optional[str], room: str, hh: Household) -> Optional[str]:
    if token is None or room == ELSEWHERE:
        return None
    if token == "dining_or_kitchen_table":
        token = "dining_table" if room.startswith("dining") else "kitchen_table"
    return hh.rec_of_kind(token, room)


def _poisson(rng: random.Random, lam: float) -> int:
    # Knuth; lam is small here
    L = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def _home_at(blocks: List[dict], minute: int) -> bool:
    """Is a resident with these (nominal) blocks at home at ``minute``?"""
    for b in blocks:
        if b["_room"] == ELSEWHERE and b["start"] <= minute < b["start"] + b["duration"]:
            return False
    return True


def build_day(hh: Household, sit: DaySituation, events: Dict[str, dict],
              acts: dict, seed: int) -> List[Bout]:
    """Realize every resident's bouts for one day; returns them sorted by start."""
    rng = random.Random(f"schedule:{seed}:{sit.day_index}")
    templates = acts["activities"]
    daytype = "weekend" if sit.is_weekend else "weekday"
    residents = sorted(hh.residents.values(), key=lambda r: r.id)

    # 1. nominal blocks per resident with event edits (remove/delay/shorten/extend)
    nominal: Dict[str, List[dict]] = {}
    for res in residents:
        blocks = copy.deepcopy(acts["schedules"][res.role][daytype])
        for b in blocks:
            b["start"] = _hhmm(b["start"])
            b["_room"] = resolve_room(templates[b["activity"]]["room"], res, hh)
            b["_edited"] = []
            b["_added_by"] = None
        # per-realization block drop, BEFORE jitter and before event edits
        # (so an event that adds a block for "whoever is home" sees the
        # blocks that actually happen)
        kept = []
        for b in blocks:
            skip_p = min(b.get("skip_p", 0.0), tc.MAX_SKIP_P)
            if skip_p and rng.random() < skip_p:
                continue
            kept.append(b)
        blocks = kept
        # lunch_out replaces lunch when both survive the skip draw
        if any(b["activity"] == "lunch_out" for b in blocks):
            blocks = [b for b in blocks if b["activity"] != "lunch"]
        for c in sit.events_for(res.id):
            sch = events[c.event].get("schedule", {})
            blocks = [b for b in blocks if b["activity"] not in sch.get("remove", [])]
            for act, mins in sorted(sch.get("delay", {}).items()):
                for b in blocks:
                    if b["activity"] == act:
                        b["start"] += mins
                        b["_edited"].append(c.id)
            for act, factor in sorted(sch.get("shorten", {}).items()):
                for b in blocks:
                    if b["activity"] == act:
                        b["duration"] = int(round(b["duration"] * factor))
                        b["_edited"].append(c.id)
            for act, mins in sorted(sch.get("extend", {}).items()):
                matches = [b for b in blocks if b["activity"] == act]
                if matches:            # only the last block of that activity runs long
                    matches[-1]["duration"] += mins
                    matches[-1]["_edited"].append(c.id)
        nominal[res.id] = blocks

    # 2. event-added blocks, with "who" resolved against nominal schedules
    for c in sorted(sit.causes, key=lambda c: c.id):
        if c.kind != "event":
            continue
        for add in events[c.event].get("schedule", {}).get("add", []):
            start = _hhmm(add["start"])
            who = add["who"]
            if who == "owner":
                targets = [c.resident]
            elif who == "all":
                targets = [r.id for r in residents]
            elif who == "all_home":
                targets = [r.id for r in residents if _home_at(nominal[r.id], start)]
            elif who in ("first_home", "one_home"):
                home = [r.id for r in residents if _home_at(nominal[r.id], start)]
                if home:
                    targets = [home[0]]
                elif who == "first_home":
                    # whoever gets back first after the start
                    def back(rid: str) -> int:
                        ends = [b["start"] + b["duration"] for b in nominal[rid]
                                if b["_room"] == ELSEWHERE and b["start"] <= start]
                        return max(ends) if ends else start
                    targets = [min((r.id for r in residents), key=lambda rid: (back(rid), rid))]
                else:
                    targets = []
            else:
                raise ValueError(who)
            for rid in targets:
                res = hh.residents[rid]
                tmpl = templates[add["activity"]]
                room = add.get("room", tmpl["room"])
                nominal[rid].append({
                    "activity": add["activity"], "start": start,
                    "duration": add["duration"],
                    "mean_bouts": add.get("mean_bouts", tmpl.get("mean_bouts", 1)),
                    "_room": resolve_room(room, res, hh), "_edited": [],
                    "_added_by": c.id, "skip_p": 0.0,
                })

    # 3. skip, jitter, overlap resolution, fragmentation
    out: List[Bout] = []
    for res in residents:
        blocks = nominal[res.id]
        kept = sorted(blocks, key=lambda b: (b["start"], b["activity"]))
        realized = []
        dropped: List[str] = []
        for b in kept:
            tmpl = templates[b["activity"]]
            sigma = tc.JITTER_CLASSES_MIN[tmpl["jitter"]] * res.jitter_scale
            start = int(round(b["start"] + rng.gauss(0, sigma)))
            dur = int(b["duration"])
            realized.append((start, dur, b))
        # authored order is kept (jitter never reorders blocks); a shifted
        # block pushes the next one; the pushed block keeps at
        # least KEEP_BLOCK_SHARE of its length if it has to be trimmed to
        # fit before the following block
        # `external`-class blocks (a commute) are anchors: they are never
        # pushed; the block before them is trimmed to end at the anchor,
        # and dropped if it would keep less than KEEP_BLOCK_SHARE of itself.
        cursor = 0
        placed = []
        for start, dur, b in realized:
            is_anchor = templates[b["activity"]]["jitter"] == "external"
            if is_anchor:
                while placed and placed[-1][1] > start:
                    ps, pe, pb = placed[-1]
                    if start - ps >= math.ceil((pe - ps) * tc.KEEP_BLOCK_SHARE):
                        placed[-1][1] = start
                        break
                    placed.pop()
                    dropped.append(pb["activity"])
            else:
                start = max(start, cursor)
            placed.append([start, start + dur, b])
            cursor = start + dur
        for s, e, b in placed:
            if s >= MIN_PER_DAY:
                continue
            e = min(e, MIN_PER_DAY)
            if b["activity"] == "sleep":
                e = MIN_PER_DAY
            tmpl = templates[b["activity"]]
            room = b["_room"]
            surface = resolve_surface(tmpl.get("surface"), room, hh)
            mean_bouts = max(tc.MIN_MEAN_BOUTS, min(tc.MAX_MEAN_BOUTS,
                                                   float(b.get("mean_bouts", tmpl.get("mean_bouts", 1)))))
            n = 1
            if mean_bouts > 1.0:
                n = max(1, _poisson(rng, mean_bouts))
            window = e - s
            # each bout and each gap at least MIN_BOUT_MINUTES
            while n > 1 and window < (2 * n - 1) * tc.MIN_BOUT_MINUTES:
                n -= 1
            pieces = []
            if n == 1:
                pieces = [(s, e)]
            else:
                # split window into n bouts separated by gaps taking ~30% of it
                gap_total = int(window * 0.3)
                bout_total = window - gap_total
                cuts = sorted(rng.random() for _ in range(n - 1))
                lens = []
                prev = 0.0
                for c in cuts + [1.0]:
                    lens.append(c - prev)
                    prev = c
                bout_lens = [max(tc.MIN_BOUT_MINUTES, int(bout_total * l)) for l in lens]
                gap = max(tc.MIN_BOUT_MINUTES, gap_total // (n - 1))
                t = s
                for bl in bout_lens:
                    pieces.append((t, min(t + bl, e)))
                    t += bl + gap
                pieces = [(a, bb) for a, bb in pieces if bb - a >= tc.MIN_BOUT_MINUTES and a < e]
                n = len(pieces)
            for i, (a, bb) in enumerate(pieces):
                out.append(Bout(res.id, b["activity"], a, bb, room, surface,
                                list(tmpl.get("uses", [])), bool(tmpl.get("tidies", False)),
                                list(tmpl.get("tidy_rooms", [room])),
                                b["_added_by"], list(b["_edited"]), i, n))
                if i + 1 < len(pieces) and room != ELSEWHERE:
                    # the gap between two bouts is a short break in the
                    # kitchen (a drink, a snack): used objects get put down
                    # and fetched again, which is where drift comes from
                    ga, gb = bb, pieces[i + 1][0]
                    if gb - ga >= tc.MIN_BOUT_MINUTES:
                        out.append(Bout(res.id, "break", ga, gb, "kitchen",
                                        hh.rec_of_kind("counter", "kitchen"), ["phone"],
                                        False, [], b["_added_by"], [], 0, 1))
    out.sort(key=lambda b: (b.start, b.resident, b.activity))
    return out
