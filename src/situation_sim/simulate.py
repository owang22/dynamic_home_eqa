"""The simulation loop: walks every resident's bouts through the day, brings
objects to where they are used, decides where they go afterwards, and
records truth rows plus a human-readable trace.

Object model: while an activity runs, the objects it uses sit at the
activity's surface (a laptop on the desk); pocket items (phone, keys,
wallet) ride ON_PERSON. When the activity ends every used object that the
next activity does not need goes through the placement decision. A decision
whose destination is where the object already is produces no move (the
laptop stays on the desk) but still counts as a decision.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from situation_sim import timing_constants as tc
from situation_sim.household import Household, Obj, ON_PERSON, OUT_OF_HOUSE
from situation_sim.placement import World, decide, Decision
from situation_sim.schedule import Bout, ELSEWHERE, build_day
from situation_sim.situation import DaySituation

AWAY = "AWAY"
DAY_SECONDS = 86_400

TRIP_WORDS = {"commute_work": "work", "walk": "a walk", "gym": "the gym",
              "errands": "errands", "lunch_out": "lunch out"}
ACT_WORDS = {"morning_routine": "morning routine", "breakfast": "breakfast",
             "work_session": "work session", "lunch": "lunch", "chores": "chores",
             "tidy": "tidying up", "cook_dinner": "cooking dinner", "dinner": "dinner",
             "evening_tv": "evening TV", "read": "reading", "host_guest": "hosting the guests",
             "unpack_groceries": "unpacking groceries", "laundry": "laundry",
             "rest_couch": "resting on the couch", "sleep": "bed", "break": "a short break"}


def hhmm(minute: int) -> str:
    minute = min(minute, 1439)
    return f"{minute // 60:02d}:{minute % 60:02d}"


def words(activity: str) -> str:
    return ACT_WORDS.get(activity, TRIP_WORDS.get(activity, activity))


@dataclass
class TraceLine:
    minute: int
    order: int
    text: str
    indent: bool = False


@dataclass
class RunResult:
    truth_rows: List[dict]
    resident_rows: List[dict]
    trace_days: List[Tuple[DaySituation, List[TraceLine]]]
    bouts_by_day: List[List[Bout]]
    stats: Dict[str, object] = field(default_factory=dict)


class Simulator:
    def __init__(self, hh: Household, sits: List[DaySituation], events: Dict[str, dict],
                 acts: dict, seed: int, episode_id: str):
        self.hh = hh
        self.sits = sits
        self.events = events
        self.acts = acts
        self.seed = seed
        self.episode_id = episode_id
        self.rng = random.Random(f"simulate:{seed}")
        self.loc: Dict[str, str] = {}
        self.carrier: Dict[str, Optional[str]] = {}
        self.res_room: Dict[str, str] = {}
        self.in_use: Dict[str, List[str]] = {}      # resident -> objects used by the running bout
        self.truth: List[dict] = []
        self.resident_rows: List[dict] = []
        self.last_t: Dict[str, int] = {}
        self.n_decisions = 0
        self.n_moves = 0
        self.n_whim = 0
        self.notes: List[dict] = []   # non-move effects of causes (a forgotten pickup)

    # ---- recording ------------------------------------------------------
    def _t(self, day: int, minute: int) -> int:
        return day * DAY_SECONDS + minute * 60

    def move(self, obj_id: str, day: int, minute: int, rec: str, cause: str,
             causes: List[str], whim: bool = False, reason: str = "",
             carrier: Optional[str] = None, intended: Optional[str] = None,
             whim_p: float = 0.0) -> None:
        t = self._t(day, minute)
        if obj_id in self.last_t and t <= self.last_t[obj_id]:
            t = self.last_t[obj_id] + 1          # keep rows strictly ordered per object
        self.last_t[obj_id] = t
        row = {"kind": "truth", "episode_id": self.episode_id, "object_id": obj_id,
               "t": t, "receptacle_id": rec}
        if rec == ON_PERSON:
            row["carrier"] = carrier
        row["cause"] = cause
        row["causes"] = sorted(set(causes))
        row["whim"] = whim
        if whim:
            row["whim_p"] = whim_p
            row["intended"] = intended
        if reason:
            row["reason"] = reason
        self.truth.append(row)
        self.loc[obj_id] = rec
        self.carrier[obj_id] = carrier if rec == ON_PERSON else None

    def resident_at(self, res_id: str, day: int, minute: int, room: str) -> None:
        if self.res_room.get(res_id) == room:
            return
        self.res_room[res_id] = room
        self.resident_rows.append({"kind": "resident", "episode_id": self.episode_id,
                                   "resident_id": res_id, "t": self._t(day, minute),
                                   "room": room})

    # ---- helpers ----------------------------------------------------------
    def name(self, res_id: str) -> str:
        return self.hh.residents[res_id].name.capitalize()

    def expand_uses(self, res_id: str, tokens: List[str], sit: DaySituation) -> List[Obj]:
        hh = self.hh
        own = hh.objects_of(res_id)
        shared = hh.objects_of(None)
        out: List[Obj] = []
        extra_carry = set()
        for c in sit.events_for(res_id):
            extra_carry.update(self.events[c.event].get("carry", []))
        for tok in tokens:
            if tok == "pocket":
                out += [o for o in own if o.pocket]
            elif tok == "outdoor":
                out += [o for o in own if o.outdoor and (o.cls != "umbrella" or "umbrella" in extra_carry)]
            elif tok in ("bag", "gym", "bag_leader"):
                kind = "bag" if tok != "gym" else "gym"
                for g in sorted(hh.groups.values(), key=lambda g: g.name):
                    if g.owner == res_id and g.kind == kind:
                        out.append(hh.objects[g.leader])
                        if tok != "bag_leader":
                            out += [hh.objects[m] for m in g.members]
            else:
                mine = [o for o in own if o.cls == tok]
                out += mine if mine else [o for o in shared if o.cls == tok]
        seen = set()
        uniq = []
        for o in out:
            if o.id not in seen:
                seen.add(o.id)
                uniq.append(o)
        return uniq

    def blocked_now(self, bouts: List[Bout], minute: int, sit: DaySituation) -> Dict[str, str]:
        blocked: Dict[str, str] = {}
        for c in sorted(sit.causes, key=lambda c: c.id):
            if c.kind != "event":
                continue
            for rule in self.events[c.event].get("block", []):
                active = any(b.activity == rule["during"] and b.start <= minute <= b.end
                             for b in bouts)
                if active:
                    rec = self.hh.rec_of_kind(rule["receptacle"])
                    if rec:
                        blocked[rec] = c.id
        return blocked

    def standing_omission(self, obj: Obj, activity: str) -> bool:
        """Stable per (item, trip type): the resident never takes this on that trip."""
        r = random.Random(f"omission:{self.seed}:{obj.id}:{activity}")
        return r.random() >= tc.CARRY_P

    def is_leader(self, oid: str) -> bool:
        return any(g.leader == oid for g in self.hh.groups.values())

    # ---- core -------------------------------------------------------------
    def run(self) -> RunResult:
        hh = self.hh
        # t=0: everything at its primary home slot, residents asleep
        for o in sorted(hh.objects.values(), key=lambda o: o.id):
            self.move(o.id, 0, 0, o.home[0], "initial", [])
        for r in sorted(hh.residents.values(), key=lambda r: r.id):
            self.resident_at(r.id, 0, 0, r.bedroom)
        trace_days = []
        bouts_by_day = []
        for sit in self.sits:
            bouts = build_day(hh, sit, self.events, self.acts, self.seed)
            lines = self.run_day(sit, bouts)
            trace_days.append((sit, lines))
            bouts_by_day.append(bouts)
        stats = {"placement_decisions": self.n_decisions,
                 "placement_moves": self.n_moves,
                 "whims": self.n_whim,
                 "whim_share_of_decisions": round(self.n_whim / max(1, self.n_decisions), 4),
                 "whim_share_of_moves": round(self.n_whim / max(1, self.n_moves), 4),
                 "notes": self.notes}
        return RunResult(self.truth, self.resident_rows, trace_days, bouts_by_day, stats)

    def run_day(self, sit: DaySituation, bouts: List[Bout]) -> List[TraceLine]:
        day = sit.day_index
        lines: List[TraceLine] = []
        by_res: Dict[str, List[Bout]] = {}
        for b in bouts:
            by_res.setdefault(b.resident, []).append(b)
        timeline = []
        for res_id, bl in sorted(by_res.items()):
            for i, b in enumerate(bl):
                nxt = bl[i + 1] if i + 1 < len(bl) else None
                timeline.append((b.start, 1, res_id, i, b, nxt))
                timeline.append((b.end, 0, res_id, i, b, nxt))
        # ends before starts at the same minute
        timeline.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
        for minute, kind, res_id, i, b, nxt in timeline:
            if kind == 1:
                self.start_bout(sit, bouts, b, lines)
            else:
                self.end_bout(sit, bouts, b, nxt, lines)
        # end of day: anything still on a person is put down at home
        for res_id in sorted(by_res):
            carried = sorted(o for o, c in self.carrier.items() if c == res_id)
            for oid in carried:
                obj = self.hh.objects[oid]
                self.move(oid, day, 1439, obj.home[0], "end_of_day", [],
                          reason="put down before sleep")
                lines.append(TraceLine(1439, 2, f"{oid} → {obj.home[0]}: put down before sleep", True))
        lines.sort(key=lambda l: (l.minute, l.order))
        return lines

    def start_bout(self, sit: DaySituation, bouts: List[Bout], b: Bout,
                   lines: List[TraceLine]) -> None:
        day = sit.day_index
        who = self.name(b.resident)
        needed = self.expand_uses(b.resident, b.uses, sit)
        if b.away:
            self.start_trip(sit, b, needed, lines)
            return
        self.resident_at(b.resident, day, b.start, b.room)
        brought = []
        used: List[str] = []
        for o in needed:
            where = self.loc[o.id]
            if where == OUT_OF_HOUSE:
                continue
            if where == ON_PERSON and self.carrier[o.id] != b.resident:
                continue          # someone else has it
            causes = [b.added_by] if b.added_by else []
            if o.pocket:
                if where != ON_PERSON:
                    self.move(o.id, day, b.start, ON_PERSON, f"pickup:{b.activity}", causes,
                              carrier=b.resident)
                    brought.append(f"{o.id} from {where}")
            elif b.surface is not None and where != b.surface:
                # the activity surface, or the first receptacle in the room
                # that may hold this class; failing that it stays in hand
                target = b.surface if b.surface in o.allowed else None
                if target is None:
                    cands = [r.id for r in self.hh.recs_in(b.room) if r.id in o.allowed]
                    target = cands[0] if cands else ON_PERSON
                if target == ON_PERSON:
                    self.move(o.id, day, b.start, ON_PERSON, f"carry:{b.activity}", causes,
                              carrier=b.resident)
                else:
                    self.move(o.id, day, b.start, target, f"bring:{b.activity}", causes,
                              reason=f"brought to the {self.hh.receptacles[target].kind} for {words(b.activity)}")
                brought.append(f"{o.id} from {where}")
            used.append(o.id)
        self.in_use[b.resident] = used
        frag = f" (bout {b.bout_index + 1}/{b.n_bouts})" if b.n_bouts > 1 else ""
        txt = f"{who} — {words(b.activity)} in the {b.room}{frag}"
        if b.added_by:
            txt += f" [because of {b.added_by}]"
        elif b.edited_by:
            txt += f" [shifted by {', '.join(sorted(set(b.edited_by)))}]"
        if brought:
            txt += "; brings " + ", ".join(brought)
        lines.append(TraceLine(b.start, 1, txt))

    def start_trip(self, sit: DaySituation, b: Bout, needed: List[Obj],
                   lines: List[TraceLine]) -> None:
        day = sit.day_index
        who = self.name(b.resident)
        res = self.hh.residents[b.resident]
        self.resident_at(b.resident, day, b.start, AWAY)
        taken, forgotten, omitted = [], [], []
        for o in needed:
            where = self.loc[o.id]
            if where == OUT_OF_HOUSE:
                continue
            if where == ON_PERSON and self.carrier[o.id] != b.resident:
                continue
            if o.pocket and self.standing_omission(o, b.activity):
                omitted.append(o.id)
                continue
            if o.pocket and where != ON_PERSON:
                p_f = res.forget_p
                p_extra = (2 * res.forget_p * res.mood_sensitivity
                           if sit.has_flag(b.resident, "distracted") else 0.0)
                u = self.rng.random()
                if u < p_f + p_extra:
                    forgotten.append((o.id, where, u >= p_f))
                    continue
            causes = [c.id for c in sit.events_for(b.resident)
                      if o.cls in self.events[c.event].get("carry", [])]
            if b.added_by:
                causes.append(b.added_by)
            self.move(o.id, day, b.start, OUT_OF_HOUSE, f"trip:{b.activity}", causes)
            taken.append(o.id)
        self.in_use[b.resident] = []
        trip = words(b.activity)
        txt = f"{who} leaves for {trip} (back {hhmm(b.end)})"
        if taken:
            txt += "; takes " + self.describe_taken(taken)
        if omitted:
            txt += f"; never takes {', '.join(omitted)} on {trip}"
        lines.append(TraceLine(b.start, 1, txt))
        for oid, where, distracted in forgotten:
            why = "distracted today" if distracted else "just forgot"
            lines.append(TraceLine(b.start, 1, f"forgets {oid} (still at {where}, {why})", True))
            if distracted:
                self.notes.append({"object_id": oid, "t": self._t(day, b.start),
                                   "event": "forgotten_on_departure",
                                   "causes": [f"distracted:{b.resident}"]})

    def describe_taken(self, taken: List[str]) -> str:
        hh = self.hh
        parts = []
        used = set()
        for g in sorted(hh.groups.values(), key=lambda g: g.name):
            if g.leader in taken:
                inside = [m for m in g.members if m in taken]
                used.add(g.leader)
                used.update(inside)
                parts.append(g.leader + (f" (with {', '.join(inside)})" if inside else ""))
        parts += [t for t in taken if t not in used]
        return ", ".join(parts)

    def place(self, oid: str, res_id: str, b: Bout, nxt: Optional[Bout], sit: DaySituation,
              world: World, sub: List[TraceLine], src_note: bool = False) -> Decision:
        hh = self.hh
        obj = hh.objects[oid]
        d = decide(hh, obj, hh.residents[res_id], b, nxt, sit, self.events, world, self.rng)
        self.n_decisions += 1
        if d.whim:
            self.n_whim += 1
        src = self.loc[oid]
        if d.dest != src:
            self.n_moves += 1
            self.move(oid, sit.day_index, b.end, d.dest, f"placement:{d.rule}", d.causes,
                      whim=d.whim, reason=d.reason, intended=d.intended, whim_p=d.whim_p)
            sub.append(TraceLine(b.end, 0, self.describe(oid, src if src_note else None, d), True))
        elif d.whim:
            # whim that happened to pick the current spot cannot occur (alts exclude it)
            pass
        return d

    def end_bout(self, sit: DaySituation, bouts: List[Bout], b: Bout, nxt: Optional[Bout],
                 lines: List[TraceLine]) -> None:
        day = sit.day_index
        hh = self.hh
        who = self.name(b.resident)
        sub: List[TraceLine] = []
        kept: List[str] = []
        needed_next = {o.id for o in self.expand_uses(b.resident, nxt.uses, sit)} if nxt else set()
        world = World(hh, self.loc, self.blocked_now(bouts, b.end, sit))
        if b.away:
            # everything of this resident's that went out comes back now
            if nxt is not None and nxt.start <= b.end:
                arrive = AWAY if nxt.away else nxt.room     # straight on to the next trip
            else:
                arrive = "entry"
            self.resident_at(b.resident, day, b.end, arrive)
            back = sorted(o for o in hh.objects if self.loc[o] == OUT_OF_HOUSE
                          and hh.objects[o].owner == b.resident)
            order = sorted(back, key=lambda o: (0 if self.is_leader(o) else 1, o))
            placed_leader: Dict[str, Decision] = {}
            for oid in order:
                obj = hh.objects[oid]
                if oid in needed_next:
                    self.move(oid, day, b.end, ON_PERSON, f"keep:{nxt.activity}", [],
                              carrier=b.resident)
                    kept.append(oid)
                    continue
                g = hh.groups[obj.group] if obj.group else None
                if g and g.leader != oid and g.leader in placed_leader:
                    lead = placed_leader[g.leader]
                    if lead.dest in obj.allowed:
                        self.n_decisions += 1
                        self.n_moves += 1
                        self.move(oid, day, b.end, lead.dest, f"group:{g.name}", lead.causes,
                                  reason=f"stays in {g.leader}")
                        sub.append(TraceLine(b.end, 0, f"{oid} → {lead.dest}: stays in the {hh.objects[g.leader].cls}", True))
                        continue
                d = self.place(oid, b.resident, b, nxt, sit, world, sub)
                if self.is_leader(oid):
                    placed_leader[oid] = d
            if kept:
                sub.append(TraceLine(b.end, 0, f"keeps {', '.join(kept)} for {words(nxt.activity)}", True))
            lines.append(TraceLine(b.end, 0, f"{who} is back from {words(b.activity)}"))
            lines.extend(sub)
            return

        # a home activity ended: used objects still where this bout put
        # them, plus whatever is on the person
        used = [o for o in self.in_use.get(b.resident, [])
                if (self.loc[o] not in (ON_PERSON, OUT_OF_HOUSE)
                    and hh.receptacles[self.loc[o]].room == b.room)
                or (self.loc[o] == ON_PERSON and self.carrier[o] == b.resident)]
        used += [o for o, c in self.carrier.items() if c == b.resident and o not in used]
        self.in_use[b.resident] = []
        handled = set()
        for oid in sorted(used):
            handled.add(oid)
            if oid in needed_next:
                if self.loc[oid] == ON_PERSON:
                    kept.append(oid)
                continue
            self.place(oid, b.resident, b, nxt, sit, world, sub)
        # a tidy pass also returns whatever is lying around the rooms it covers
        if b.tidies:
            stray = sorted(o for o, r in self.loc.items()
                           if r not in (ON_PERSON, OUT_OF_HOUSE) and o not in handled
                           and hh.receptacles[r].room in b.tidy_rooms
                           and r != hh.objects[o].home[0])
            for oid in stray:
                self.place(oid, b.resident, b, nxt, sit, world, sub, src_note=True)
        if kept and nxt is not None and nxt.away:
            sub.append(TraceLine(b.end, 0, f"keeps {', '.join(kept)} for {words(nxt.activity)}", True))
        if sub:
            lines.append(TraceLine(b.end, 0, f"{who} finishes {words(b.activity)}"))
            lines.extend(sub)

    def describe(self, oid: str, src: Optional[str], d: Decision) -> str:
        frm = f" (from {src})" if src else ""
        if d.whim:
            txt = (f"{oid}{frm} → {d.dest}: WHIM — was heading for {d.intended} ({d.reason}) "
                   f"but landed on {d.dest} instead")
        else:
            txt = f"{oid}{frm} → {d.dest}: {d.reason}"
        if d.causes:
            txt += f" [{', '.join(d.causes)}]"
        return txt
