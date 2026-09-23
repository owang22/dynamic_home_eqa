"""Published LLM-memory designs on the frozen regime banks, beside the in-house arms of ``llm.py``.

    python3 -m baselines.patrol.llm_sota --bank B1 B2 --out results/sota_memory/nottold \
        --cache results/sota_memory/cache --memory pinned --told not_told

The question loop is ``llm.run_arm``'s ``conf`` path, copied rather than
patched so ``llm.py`` stays untouched for the arms already run on it: same
header, same answer format, same nightly noticing call, same scoring. What
differs is only the memory block — and, for stores with a write policy,
the LLM calls that maintain the store as evidence arrives (``Store.on_group``).

Degenerate check: ``--memory naive`` here must reproduce ``llm.py``'s naive
arm prompt-for-prompt (run it with ``--replay-only`` against that arm's
cache: every call must be a cache hit and every answer identical).

Memories
* ``naive``   passthrough to ``llm.memory_lines`` (the check above).
* ``pinned``  the naive block unchanged, with the most recent sighting of the
  object at about this time of day (within PIN_TOD_WINDOW_S of the query's
  clock time, any earlier moment) repeated at the top under its own heading.
  Same contents, same write policy; only the salience of one line changes.
  It isolates read-time failure: the answer is often already in the buffer.
* ``debate``  role-assigned debate (Liang et al. 2024 MAD / Du et al. 2024 style, one round): over the
  naive block, an EVIDENCE advocate argues from the latest sightings and a ROUTINE advocate from the
  long-run pattern (the two positions our logs show in tension); a judge sees both and answers in the
  usual format. 3 calls per question. ``debate_oracle``: the same, with the judge alone also shown the
  residents' messages (run on the banks_f1_return header: sick from day 14, back at work day 24) —
  an upper bound on how much of the gap is detecting the stage rather than reasoning over the prompt.
* ``nocard``  the recent-sightings list with the residents' descriptions removed from the prompt: each
  resident line becomes "- <name> (a resident)". Every other arm carries a written daily routine
  ("at the desk at home from 9 to about 5:30") that is never updated when the routine changes; this
  asks how much of the evidence-overriding comes from that written routine rather than a learned prior.
* ``facts_mem0`` / ``facts_zep`` / ``facts_stale``: one shared nightly FACT STORE, three published
  revision policies. Each night an LLM writes routine-level facts from that day's sightings of the
  objects that move ("laptop_yuki: desk_b1, 09:00-17:30"); a second call applies the policy against
  the facts already held about the same objects:
    - mem0  (Chhikara et al. 2025): per new fact ADD / UPDATE an old one / NOOP; old facts it
      contradicts are DELETED and gone.
    - zep   (Rasmussen et al. 2025, Graphiti): a contradicted fact is INVALIDATED -- its validity window
      is closed on that day -- and kept; the reader sees every fact with the period it held.
    - stale (Chao et al. 2026, STALE/CUPMem): old facts are labelled KEEP / STALE / REPLACE; the reader
      is told current facts ground the answer and stale ones are history only.
  Read budget, identical for all three: at most FACT_CAP facts about the object + its newest
  RECENT_CAP sightings + up to 10 empty-listing lines (the recent-sightings list shows 60 sightings).
  Adaptations, stated: ingestion is nightly per day rather than per message; sightings are structured
  already, so there is no entity-extraction step; facts are keyed by object.
* ``truecard`` the recent-sightings list with the residents' descriptions kept TRUE for each day: on the
  sick days (the days of the bank's "home sick" messages) the sick resident's line says "home sick at the
  moment, resting on the couch in the living room through the day; no work or trips out" (the simulator's
  own description of the sick-day event); on every other day the original description.
``--days`` answers only the listed days. This is exact only where each arm makes it so, NOT a guarantee
of the harness. Arms with no LLM writes (naive, pinned, nocard, debate) are exact because their state never
depends on which days were answered. The fact stores are exact because each nightly write filters sightings
to before the end of its own day; without that filter the writes for skipped days would see later evidence
(a bug found 2026-09-23 02:45). Any NEW arm that writes must earn exactness the same way: compare a write
prompt under two different --days settings; it must be byte-identical.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.patrol import llm as L
from baselines.patrol.leak_check import check_prompt
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Episode

PIN_TOD_WINDOW_S = 3600


class Store:
    """A memory design: what it keeps (``on_group`` may call the LLM to
    maintain it) and what the question prompt shows (``lines``)."""
    kind = "base"
    in_house = None      # llm.memory_lines kind to delegate to, if any

    def __init__(self, ask, day_names: Dict[int, str]) -> None:
        self.ask, self.day_names = ask, day_names

    def on_group(self, t: int, items: Sequence[Any], memory: L.Memory) -> None:
        """Called after ``memory.update_group`` for every evidence instant."""

    def lines(self, memory: L.Memory, obj: str, t_query: int) -> List[str]:
        return L.memory_lines(memory, self.in_house, obj, self.day_names, None, query_t=t_query)

    def budget(self, memory: L.Memory, obj: str, t_query: int) -> int:
        """Facts shown at answer time (reported beside accuracy: prompt length alone moves it)."""
        return sum(1 for s in self.lines(memory, obj, t_query) if s.startswith("- ") and s != "- none")


class Naive(Store):
    kind, in_house = "naive", "naive"


class LongContext(Store):
    """passthrough to llm.memory_lines 'longcontext' (every sighting of the object + the whole movement log): used to
    re-run that arm fresh on a day subset and measure its rerun noise."""
    kind, in_house = "longcontext", "longcontext"


class Pinned(Store):
    kind, in_house = "pinned", "naive"

    def lines(self, memory, obj, t_query):
        base = L.memory_lines(memory, "naive", obj, self.day_names, None, query_t=t_query)
        same = [(t, r) for t, r in memory.history(obj) if L._tod_gap(t, t_query) <= PIN_TOD_WINDOW_S]
        head = [f"Most recent sighting of {obj} at about this time of day (within an hour of {L.hhmm(t_query)}):"]
        head += [f"- {L.clock(same[-1][0], self.day_names)}: {same[-1][1]}"] if same else ["- none"]
        return head + [""] + base


class NoCard(Store):
    kind, in_house = "nocard", "naive"
    strip_cards = True


class TrueCard(Store):
    kind, in_house = "truecard", "naive"
    SICK = "Weekdays: home sick at the moment, resting on the couch in the living room through the day; no work or trips out."


class Debate(Store):
    kind, in_house = "debate", "naive"
    oracle = False


class DebateOracle(Debate):
    kind, oracle = "debate_oracle", True


FACT_CAP, RECENT_CAP = 20, 40
FACTS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {"facts": {"type": "array", "maxItems": 80, "items": {
        "type": "object", "properties": {"object": {"type": "string"}, "spot": {"type": "string"},
                                         "hours": {"type": "string", "maxLength": 40}},
        "required": ["object", "spot", "hours"], "additionalProperties": False}}},
    "required": ["facts"], "additionalProperties": False}
POLICY_TEXT = {
    "mem0": ("You maintain the robot's memory. For each NEW fact choose one operation: ADD (it is new information), "
             "UPDATE an old fact (it refines or replaces that old fact; give the old fact's id), or NOOP (the memory already "
             "holds it). For each OLD fact that the new facts contradict, choose DELETE; old facts not mentioned are kept."),
    "zep": ("You maintain a temporal knowledge graph. For each NEW fact decide whether it DUPLICATES an old current fact "
            "(give its id) or is ADDed. For each OLD current fact that a new fact contradicts (the object can no longer be "
            "at that spot in those hours), choose INVALIDATE: the old fact is kept, but its validity period ends today. "
            "Old facts not mentioned stay current."),
    "stale": ("You maintain the robot's memory and must decide which memories are no longer valid. For each OLD current "
              "fact affected by today's evidence, label it KEEP (still valid), STALE (no longer valid, even if nothing states "
              "so explicitly), or REPLACE (superseded by a specific new fact; give its id). For each NEW fact decide whether it "
              "DUPLICATES an old current fact (give its id) or is ADDed."),
}
OLD_OPS = {"mem0": ["DELETE"], "zep": ["INVALIDATE"], "stale": ["KEEP", "STALE", "REPLACE"]}
NEW_OPS = {"mem0": ["ADD", "UPDATE", "NOOP"], "zep": ["ADD", "DUPLICATE"], "stale": ["ADD", "DUPLICATE"]}


def policy_schema(pol: str) -> Dict[str, Any]:
    return {"type": "object", "properties": {
        "new_facts": {"type": "array", "items": {"type": "object", "properties": {
            "new": {"type": "string"}, "op": {"type": "string", "enum": NEW_OPS[pol]}, "old": {"type": ["string", "null"]}},
            "required": ["new", "op", "old"], "additionalProperties": False}},
        "old_facts": {"type": "array", "items": {"type": "object", "properties": {
            "old": {"type": "string"}, "op": {"type": "string", "enum": OLD_OPS[pol]}, "by": {"type": ["string", "null"]}},
            "required": ["old", "op", "by"], "additionalProperties": False}}},
        "required": ["new_facts", "old_facts"], "additionalProperties": False}


def stays(h: List[Tuple[int, str]], day: int) -> List[str]:
    """One day's episode text for the fact extractor: consecutive sightings at the same spot merged into a stay
    'spot from-to (seen t1, t2)', where 'to' is the first sighting elsewhere; a stay running in from the night
    before starts at 00:00, one still open at the last sighting says 'still there at HH:MM'."""
    d0, d1 = day * DAY_SECONDS, (day + 1) * DAY_SECONDS
    out = []
    i = 0
    while i < len(h):
        j = i
        while j + 1 < len(h) and h[j + 1][1] == h[i][1]:
            j += 1
        start, end = h[i][0], (h[j + 1][0] if j + 1 < len(h) else None)
        seen = [t for t, _ in h[i:j + 1] if d0 <= t < d1]
        if start < d1 and (end is None or end > d0) and (seen or (end is not None and end > d0)):
            a = "00:00" if start < d0 else L.hhmm(start)
            b = (L.hhmm(end) if end is not None and end < d1 else
                 ("24:00" if end is not None else f"still there at {L.hhmm(seen[-1]) if seen else '00:00'}"))
            sn = f" (seen {', '.join(L.hhmm(t) for t in seen)})" if seen else ""
            out.append(f"{h[i][1]} {a}-{b}{sn}" if not b.startswith("still") else f"{h[i][1]} from {a}, {b}{sn}")
        i = j + 1
    return out


class FactStore(Store):
    kind, policy = "facts", None

    def __init__(self, ask, day_names):
        super().__init__(ask, day_names)
        self.facts: List[Dict[str, Any]] = []     # id, obj, spot, hours, since, until, status
        self.n = 0
        self.log: List[dict] = []

    def fact_text(self, f: dict) -> str:
        return f"{f['spot']}, {f['hours']}"

    def nightly(self, day: int, memory: L.Memory, ctx: dict) -> None:
        L0 = L.header_lines((day + 1) * DAY_SECONDS - 60, self.day_names, ctx["cards"], ctx["rooms"], ctx["patrol_hours"],
                            False, ctx["hints"](day))
        movers, mover_objs = [], []
        cutoff = (day + 1) * DAY_SECONDS      # the night's write sees only what had been seen by the end of that day,
        for o in sorted(memory.sightings):   # whenever it runs: no later sightings leak in, and --days stays exact
            h = [(t, r) for t, r in memory.history(o) if t < cutoff]
            if len({r for _, r in h}) < 2:
                continue
            st = stays(h, day)
            if st:
                mover_objs.append(o)
                movers.append(f"- {o}: " + "; ".join(st))
                held = [f for f in self.facts if f["obj"] == o and f["status"] == "current"]
                if held:
                    movers.append("    memory already holds: " + "; ".join(self.fact_text(f) for f in held))
        if not movers:
            return
        ex = L0 + ["", f"It is the end of {L.day_label(day, self.day_names)}. Extract facts for the robot's memory.", "",
                   "Today's stays of the objects that move: each stay is a spot and the stretch from the first sighting "
                   "there until the object was next seen somewhere else (times in between are when it was seen there):"]
        ex += movers + ["", "Write facts about each object's ROUTINE: which spot it is at during which stretch of a typical "
                        "day, as today's stays show it. Give stretches, not single moments (write 09:30-17:30, never "
                        "09:30-09:30); merge stays at the same spot. One fact per object and spot. Where today agrees "
                        "with a fact the memory already holds (same spot, times within about an hour), repeat that fact's "
                        "exact wording. Use only object and spot names above.",
                        'Reply with JSON: {"facts": [{"object": ..., "spot": ..., "hours": "HH:MM-HH:MM"}, ...]}']
        text, _ = self.ask([{"role": "system", "content": L.SYSTEM}, {"role": "user", "content": "\n".join(ex)}],
                           # at least one fact per object listed: with an unconstrained list the model returned
                           # {"facts": []} on 4 of 9 nights (withdrawn/facts_zep_hh0_empty_nights)
                           {**FACTS_SCHEMA, "properties": {"facts": {**FACTS_SCHEMA["properties"]["facts"],
                                                                     "minItems": min(len(mover_objs), 80)}}},
                           3000, f"facts extract day {day}", llm_authored=self.authored())
        try:
            new = [f for f in json.loads(text or "{}").get("facts", [])
                   if f.get("object") in memory.sightings and f.get("spot") in ctx["allowed"]]
        except ValueError:
            new = []
        if not new:
            self.log.append({"day": day, "extracted": 0}); return
        new_ids = {f"n{i + 1}": f for i, f in enumerate(new)}
        objs = sorted({f["object"] for f in new})
        cur = {f["id"]: f for f in self.facts if f["obj"] in objs and f["status"] == "current"}
        pr = L0 + ["", f"It is the end of {L.day_label(day, self.day_names)}.", POLICY_TEXT[self.policy], ""]
        for o in objs:
            pr.append(f"{o}:")
            pr += [f"  old {i}: {self.fact_text(f)} (since day {f['since']})" for i, f in cur.items() if f["obj"] == o] or ["  old: none"]
            pr += [f"  new {i}: {f['spot']}, {f['hours']}" for i, f in new_ids.items() if f["object"] == o]
        pr += ["", 'Reply with JSON: {"new_facts": [{"new": id, "op": ..., "old": old id or null}], '
                   '"old_facts": [{"old": id, "op": ..., "by": new id or null}]}']
        text, _ = self.ask([{"role": "system", "content": L.SYSTEM}, {"role": "user", "content": "\n".join(pr)}],
                           policy_schema(self.policy), 2500, f"facts revise day {day}",
                           llm_authored=tuple(self.fact_text(f) for f in cur.values()))
        try:
            dec = json.loads(text or "{}")
        except ValueError:
            dec = {}
        ops: Dict[str, int] = {}
        for d in dec.get("old_facts", []):
            f = cur.get(d.get("old"))
            if f is None:
                continue
            op = d.get("op")
            ops[op] = ops.get(op, 0) + 1
            if op == "DELETE":
                f["status"] = "deleted"
            elif op in ("INVALIDATE", "STALE", "REPLACE"):
                f["status"], f["until"] = "stale", day
        for d in dec.get("new_facts", []):
            nf = new_ids.get(d.get("new"))
            if nf is None:
                continue
            op = d.get("op")
            ops[op] = ops.get(op, 0) + 1
            if op in ("NOOP", "DUPLICATE") and d.get("old") in cur:
                continue
            if op == "UPDATE" and d.get("old") in cur:
                old = cur[d["old"]]
                old.update(spot=nf["spot"], hours=nf["hours"], since=day)
                continue
            self.n += 1
            self.facts.append({"id": f"f{self.n}", "obj": nf["object"], "spot": nf["spot"], "hours": nf["hours"],
                               "since": day, "until": None, "status": "current"})
        self.log.append({"day": day, "extracted": len(new), "ops": ops,
                         "current": sum(f["status"] == "current" for f in self.facts), "total": len(self.facts)})

    def fact_lines(self, obj: str) -> List[str]:
        mine = [f for f in self.facts if f["obj"] == obj]
        if self.policy == "mem0":
            cur = [f for f in mine if f["status"] == "current"][-FACT_CAP:]
            return [f"Memories about {obj}:"] + ([f"- {self.fact_text(f)} (noted day {f['since']})" for f in cur] or ["- none"])
        if self.policy == "zep":
            keep = [f for f in mine if f["status"] in ("current", "stale")][-FACT_CAP:]
            return [f"Facts about {obj}, each with the period it held:"] + (
                [f"- {self.fact_text(f)} (valid from day {f['since']}" + (f" to day {f['until']})" if f["until"] is not None else "; still current)")
                 for f in keep] or ["- none"])
        cur = [f for f in mine if f["status"] == "current"]
        old = [f for f in mine if f["status"] == "stale"]
        old = old[-max(0, FACT_CAP - len(cur[-FACT_CAP:])):] if len(cur) < FACT_CAP else []
        cur = cur[-FACT_CAP:]
        return ([f"Current facts about {obj} (ground your answer in these):"]
                + ([f"- {self.fact_text(f)} (since day {f['since']})" for f in cur] or ["- none"])
                + ["", f"Historical facts about {obj} (no longer valid; context only, not a default answer):"]
                + ([f"- {self.fact_text(f)} (day {f['since']} to day {f['until']})" for f in old] or ["- none"]))

    def lines(self, memory, obj, t_query):
        h = memory.history(obj)
        out = self.fact_lines(obj) + ["", f"Latest sightings of {obj} (oldest first, at most {RECENT_CAP}):"]
        out += [f"- {L.clock(t, self.day_names)}: {r}" for t, r in h[-RECENT_CAP:]] or ["- none"]
        chk = memory.checked_lines(obj, self.day_names, 10)
        if chk:
            out += ["", "Listings since the last sighting that did NOT show it:"] + chk
        return out

    def authored(self):
        return tuple(self.fact_text(f) for f in self.facts)


class FactsMem0(FactStore):
    kind, policy = "facts_mem0", "mem0"


class FactsZep(FactStore):
    kind, policy = "facts_zep", "zep"


class FactsStale(FactStore):
    kind, policy = "facts_stale", "stale"


STORES = {c.kind: c for c in (Naive, LongContext, Pinned, NoCard, TrueCard, Debate, DebateOracle, FactsMem0, FactsZep, FactsStale)}


def strip_cards(lines: List[str], names: Dict[str, str]) -> List[str]:
    """Replace the 'Residents:' block's description lines with bare names."""
    i = lines.index("Residents:")
    j = i + 1
    while j < len(lines) and lines[j].startswith("- "):
        j += 1
    assert j - i - 1 == len(names), (j - i - 1, names)
    return lines[:i + 1] + [f"- {n} (a resident)" for n in names.values()] + lines[j:]

ADV_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {"location": {"type": "string"}, "argument": {"type": "string", "maxLength": 500},
                   "confidence": {"type": "number"}},
    "required": ["location", "argument", "confidence"], "additionalProperties": False}
ROLE_EVIDENCE = ("You are one side of a two-sided debate about this question; another assistant argues the other side "
                 "and a judge decides. YOUR SIDE IS FIXED: name the spot where this object was seen on the MOST RECENT "
                 "day it was sighted within about an hour of the current time of day, and make the strongest case that it "
                 "is there now. Do not argue from the usual routine or the residents' descriptions; the other side does that.")
ROLE_ROUTINE = ("You are one side of a two-sided debate about this question; another assistant argues the other side "
                "and a judge decides. YOUR SIDE IS FIXED: name the spot where this object has MOST OFTEN been seen at about "
                "the current time of day across all days so far, and make the strongest case that it is there now, using "
                "the long-run pattern and what the residents normally do. Do not argue from the latest sightings; the other "
                "side does that.")
ADV_REPLY = ('Reply with JSON: {"location": one spot name, "argument": two or three sentences making your side\'s case, '
             '"confidence": number from 0 to 1}')


def _adv(text: Optional[str], allowed: set) -> Tuple[Optional[str], str, Optional[float]]:
    try:
        o = json.loads(text) if text else {}
    except ValueError:
        o = {}
    loc = o.get("location") if o.get("location") in allowed else None
    c = o.get("confidence")
    return loc, str(o.get("argument") or "")[:500], (float(c) if isinstance(c, (int, float)) else None)


def run_arm(bank_path: pathlib.Path, kind: str, told: bool, client: L.LLMClient, out_dir: pathlib.Path,
            max_days: Optional[int] = None, days: Optional[set] = None) -> List[dict]:
    header = json.loads(bank_path.read_text().splitlines()[0])
    kinds = set((header.get("day_kinds") or {}).values())
    L.FLAT_WEEK = bool(kinds) and kinds == {"weekday"}     # read by header_lines; same for every bank of a regime
    patrol_times = header.get("patrol_times") or None
    question_moments = header.get("protocol", {}).get("question_moments", "")
    feedback_delay_min = header.get("protocol", {}).get("feedback_delay_min")
    episode: Episode = next(iter(JsonlBank(bank_path).episodes()))
    day_names = {int(k): v for k, v in header["day_names"].items()}
    cards = header["protocol"]["residents"]
    names = {c["resident_id"]: c["name"] for c in cards}
    patrol_hours = int(header["patrol_hours"])
    oracle_rows = header.get("hint_messages", [])     # debate_oracle: shown to the judge only
    hint_rows = header.get("hint_messages", []) if told else []
    if L.FLAT_WEEK:
        oracle_rows = [{**h, "text": f"Day {h['day_index']}: " + h["text"].split(": ", 1)[-1]} for h in oracle_rows]
        hint_rows = [{**h, "text": f"Day {h['day_index']}: " + h["text"].split(": ", 1)[-1]} for h in hint_rows]
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(episode.receptacle_rooms.items()):
        if rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms[room].append(rec)
    rooms = {r: sorted(v) for r, v in rooms.items()}
    rec_room = {rec: room for room, recs in rooms.items() for rec in recs}
    allowed = {r for r in episode.receptacle_ids if r not in (ON_PERSON, OUT_OF_HOUSE)}
    arm = f"llm_{kind}/{'told' if told else 'not_told'}/look_off"
    tag = {"household": header["household_id"], "patrol_hours": patrol_hours, "look": "off", "agent": arm,
           "belief": arm, "memory": kind, "told": told}
    label = header.get("patrol_label", f"p{patrol_hours}")
    run_dir = out_dir / f"{header['household_id']}_{label}_{kind}_{'told' if told else 'nottold'}_lookoff"
    run_dir.mkdir(parents=True, exist_ok=True)
    calls = open(run_dir / "calls.jsonl", "w")

    def ask(messages, schema, max_tokens, where, llm_authored=()):
        check_prompt(messages, where, llm_authored)
        text, usage = client.complete(messages, schema, max_tokens)
        calls.write(json.dumps({"where": where, "messages": messages, "completion": text, "usage": usage,
                                "llm_authored": [s for s in llm_authored if s]}) + "\n")
        calls.flush()
        return text, usage

    store: Store = STORES[kind](ask, day_names)
    memory = L.Memory(rooms, rec_room, names)
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    first = list(episode.initial_observations) + [e for e in evidence if e.t == tour_t]
    memory.update_group(tour_t, first, day_names)
    store.on_group(tour_t, first, memory)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        cursor += 1

    noticing_day = -1
    store_day = -1
    ctx = {"cards": cards, "rooms": rooms, "patrol_hours": patrol_hours, "allowed": allowed,
           "hints": lambda d: [h["text"] for h in hint_rows if h["day_index"] <= d]}
    noticing: List[dict] = []
    records: List[dict] = []
    n_fallback = 0
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if max_days is not None and q.day_index > max_days:
                break
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                t = evidence[cursor].t
                grp = []
                while cursor < len(evidence) and evidence[cursor].t == t:
                    grp.append(evidence[cursor]); cursor += 1
                memory.update_group(t, grp, day_names)
                store.on_group(t, grp, memory)
            if days is not None and q.day_index not in days:
                continue
            hints = [h["text"] for h in hint_rows if h["day_index"] <= q.day_index]
            if isinstance(store, FactStore):
                while store_day < q.day_index - 1:
                    store_day += 1
                    store.nightly(store_day, memory, ctx)
            while noticing_day < q.day_index - 1:      # identical to llm.run_arm: every arm self-reports nightly
                noticing_day += 1
                day_hints = [h["text"] for h in hint_rows if h["day_index"] <= noticing_day]
                nmsgs = L.noticing_messages(memory, noticing_day, day_names, cards, rooms, patrol_hours, day_hints)
                ntext, _ = ask(nmsgs, L.NOTICING_SCHEMA, 200, f"noticing day {noticing_day}")
                try:
                    nobj = json.loads(ntext) if ntext else {}
                except ValueError:
                    nobj = {}
                noticing.append({"day": noticing_day, "changed": bool(nobj.get("changed")), "who": nobj.get("who"),
                                 "confidence": nobj.get("confidence")})
            q_cards = cards
            if isinstance(store, TrueCard):
                sick = [h["text"] for h in header.get("hint_messages", []) if h["day_index"] == q.day_index and "home sick" in h["text"]]
                if sick:
                    who = sick[0].split(": ", 1)[-1].split(" is home sick")[0].strip()
                    assert who in names.values(), (who, names)
                    q_cards = [{**c, "weekday": TrueCard.SICK} if c["name"] == who else c for c in cards]
            Lh = L.header_lines(q.t_query, day_names, q_cards, rooms, patrol_hours, False, hints, "conf", patrol_times,
                                question_moments, feedback_delay_min)
            if getattr(store, "strip_cards", False):
                Lh = strip_cards(Lh, names)
            Lh += ["", f"Question: where is {q.object_id} (a {q.object_class.replace('_', ' ')}) right now?", ""]
            mem_lines = store.lines(memory, q.object_id, q.t_query)
            msgs = [{"role": "system", "content": L.SYSTEM}, {"role": "user", "content": "\n".join(Lh + mem_lines)}]
            authored = tuple(getattr(store, "authored", lambda: ())())
            extra: Dict[str, Any] = {}
            if isinstance(store, Debate):
                body = "\n".join(Lh + mem_lines)
                side = {}
                for role, instr in (("evidence", ROLE_EVIDENCE), ("routine", ROLE_ROUTINE)):
                    m = [{"role": "system", "content": L.SYSTEM},
                         {"role": "user", "content": body + "\n\n" + instr + "\n\n" + ADV_REPLY}]
                    t_, u_ = ask(m, ADV_SCHEMA, 260, f"{q.question_id} adv_{role}")
                    side[role] = _adv(t_, allowed)
                    usage = {"prompt_tokens": int(usage.get("prompt_tokens", 0)) + int(u_.get("prompt_tokens", 0)),
                             "completion_tokens": int(usage.get("completion_tokens", 0)) + int(u_.get("completion_tokens", 0))} if extra else u_
                    extra = {**extra, f"adv_{role}": side[role][0], f"adv_{role}_conf": side[role][2]}
                jh = [h["text"] for h in oracle_rows if h["day_index"] <= q.day_index] if store.oracle else hints
                Jh = L.header_lines(q.t_query, day_names, cards, rooms, patrol_hours, False, jh, "conf", patrol_times,
                                    question_moments, feedback_delay_min)
                Jh += ["", f"Question: where is {q.object_id} (a {q.object_class.replace('_', ' ')}) right now?", ""]
                Jh += mem_lines + ["", "Two assistants debated this question before you.",
                                   f"- Arguing from the most recent evidence: {side['evidence'][0] or 'no valid spot'} — {side['evidence'][1]}",
                                   f"- Arguing from the long-run routine: {side['routine'][0] or 'no valid spot'} — {side['routine'][1]}",
                                   "You are the judge. Weigh both cases against the sightings above and decide."]
                msgs = [{"role": "system", "content": L.SYSTEM}, {"role": "user", "content": "\n".join(Jh)}]
                authored = (side["evidence"][1], side["routine"][1])
                extra["advocates_agree"] = side["evidence"][0] == side["routine"][0]
            text, u2 = ask(msgs, L.CONF_SCHEMA, 260, q.question_id, llm_authored=authored)
            usage = u2 if not extra else {k: int(usage.get(k, 0)) + int(u2.get(k, 0)) for k in ("prompt_tokens", "completion_tokens")}
            loc, conf, why, status = L.parse_conf(text, allowed)
            fallback = loc is None
            answer = loc if loc else (memory.last_spot_real(q.object_id) or sorted(allowed)[0])
            top = conf if conf is not None and not fallback else 0.0
            truth = episode.true_location(q.object_id, q.t_query)
            n_fallback += int(fallback)
            records.append({**tag, "day_index": q.day_index, "question_id": q.question_id, "object_id": q.object_id,
                            "object_class": q.object_class, "t_query": q.t_query,
                            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                            "completion_tokens": int(usage.get("completion_tokens", 0)), "reasoning": why,
                            "raw_confidence": conf, "patrol_label": label, "answer_before_look": answer,
                            "top_prob_before_look": round(top, 3), "status_before_look": status, "asked_look": None,
                            "status": status, "answer": answer, "top_prob": round(top, 3), "fallback": fallback,
                            "on_person_resident": None, "truth": truth, "correct": answer == truth,
                            "correct_before_look": answer == truth, "abstain_direct": False,
                            "facts_shown": sum(1 for s in mem_lines if s.startswith("- ") and s != "- none"), **extra})
    calls.close()
    n_ok = sum(r["correct"] for r in records)
    print(f"  {tag['household']} {arm:36s} right {n_ok}/{len(records)} fallback {n_fallback} "
          f"calls {client.stats['calls']} cached {client.stats['cached']}", file=sys.stderr, flush=True)
    with open(run_dir / "run_log.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    if isinstance(store, FactStore):
        (run_dir / "facts.json").write_text(json.dumps({"log": store.log, "facts": store.facts}, indent=1))
    with open(run_dir / "noticing.jsonl", "w") as f:
        for r in noticing:
            f.write(json.dumps({**tag, **r}, sort_keys=True) + "\n")
    (run_dir / "stats.json").write_text(json.dumps({"arm": arm, "n": len(records), "right": n_ok, "fallback": n_fallback,
                                                     "dollars": 0.0, "model": client.model}, indent=1))
    return records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=pathlib.Path, nargs="+", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--cache", type=pathlib.Path, required=True)
    ap.add_argument("--memory", nargs="+", required=True, choices=sorted(STORES))
    ap.add_argument("--told", nargs="+", default=["not_told"], choices=["told", "not_told"])
    ap.add_argument("--max-days", type=int, default=None)
    ap.add_argument("--workers", type=int, default=3, help="parallel ARMS (one stream each)")
    ap.add_argument("--replay-only", action="store_true")
    ap.add_argument("--days", default=None, help="answer only these days, e.g. 11-17,21-22,24-26")
    a = ap.parse_args(argv)
    client = L.LLMClient(a.cache, replay_only=a.replay_only)
    days = None
    if a.days:
        days = set()
        for part in a.days.split(","):
            lo, _, hi = part.partition("-")
            days |= set(range(int(lo), int(hi or lo) + 1))
    jobs = [(b, m, t == "told") for b in a.bank for m in a.memory for t in a.told]
    from concurrent.futures import ThreadPoolExecutor
    failed = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_arm, b, m, t, client, a.out, a.max_days, days): (b, m, t) for b, m, t in jobs}
        for f, job in futs.items():
            try:
                f.result()
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"ARM FAILED {job[0].name} {job[1:]}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    print(f"{failed} of {len(jobs)} arm runs failed; {json.dumps(client.stats)}", file=sys.stderr)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "llm_stats.json").write_text(json.dumps({**client.stats, "dollars": 0.0, "model": client.model}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
