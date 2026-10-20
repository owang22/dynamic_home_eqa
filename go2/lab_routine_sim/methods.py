"""The methods compared (DESIGN.md). Each has forecast(day) -> {prop: {"plan", "p_out", "why"}} and
evening(day, report). A method only ever sees `report`s: what the dog saw, never the truth.

report = {"day", "searches": {prop: {"plan", "found_at" or None, "looks"}},
          "seen": {place: [prop ids, maybe "SIGN"]} for every place looked at today,
          "patrol": [places], "forecast": this morning's forecast}
"""
from __future__ import annotations

import json
from collections import Counter

import world as W
from llm import ask_json, ask_json_budget

PROPS = list(W.PROPS)


# ---------- simple methods (no model) ----------

class History:
    """Structured record of sightings, kept by the rule methods."""

    def __init__(self):
        self.sightings = {p: [] for p in PROPS}     # (day, place)
        self.not_found = {p: [] for p in PROPS}     # days searched and not found
        self.searched = {p: [] for p in PROPS}

    def add(self, r):
        for place, seen in r["seen"].items():
            for p in seen:
                if p in self.sightings:
                    self.sightings[p].append((r["day"], place))
        for p, s in r["searches"].items():
            self.searched[p].append(r["day"])
            if not s["found_at"]:
                self.not_found[p].append(r["day"])

    def p_out(self, p, days=None):
        s = [d for d in self.searched[p] if days is None or d in days]
        nf = [d for d in self.not_found[p] if days is None or d in days]
        return round((len(nf) + 0.1) / (len(s) + 1), 3)

    def state(self):
        return {"sightings": self.sightings, "not_found": self.not_found, "searched": self.searched}

    def load(self, s):
        self.sightings = {p: [tuple(x) for x in v] for p, v in s["sightings"].items()}
        self.not_found, self.searched = s["not_found"], s["searched"]


def _fill(plan, extra):
    out = []
    for x in list(plan) + list(extra):
        if x not in out and x in W.PROP_PLACES:
            out.append(x)
    return out[:5]


def _by_freq(sightings):
    c = Counter(pl for _, pl in sightings)
    last = {pl: d for d, pl in sightings}
    return sorted(c, key=lambda pl: (-c[pl], -last[pl]))


class RuleMethod:
    llm = False

    def __init__(self, world):
        self.world, self.h = world, History()

    def evening(self, day, report):
        self.h.add(report)
        return {}

    def state(self):
        return {"history": self.h.state()}

    def load(self, s):
        self.h.load(s["history"])

    def forecast(self, day):
        return {p: self.one(p, day) for p in PROPS}, {}


class LastSeen(RuleMethod):
    name = "last_seen"

    def one(self, p, day):
        s = self.h.sightings[p]
        recent = [pl for _, pl in sorted(s, key=lambda x: -x[0])]
        return {"plan": _fill(recent, _by_freq(s) + W.PROP_PLACES), "p_out": self.h.p_out(p), "why": "last seen"}


class MostOften(RuleMethod):
    name = "most_often"

    def one(self, p, day):
        s = self.h.sightings[p]
        return {"plan": _fill(_by_freq(s), W.PROP_PLACES), "p_out": self.h.p_out(p), "why": "most often"}


class SameWeekday(RuleMethod):
    name = "same_weekday"

    def one(self, p, day):
        wd = W.weekday(day)
        same = [d for d in range(1, day) if W.weekday(d) == wd]
        s = self.h.sightings[p]
        on_same = [pl for d, pl in sorted(s, key=lambda x: -x[0]) if d in same]
        return {"plan": _fill(on_same, _by_freq(s) + W.PROP_PLACES), "p_out": self.h.p_out(p, set(same)),
                "why": "same weekday"}


class RulesKnown(RuleMethod):
    """Ceiling: knows every rule and the change day; still sees the sign only through the dock patrol."""
    name = "rules_known"

    def one(self, p, day):
        r = W.rule_now(self.world, p, day)
        t, P = r["type"], r["places"]
        wd = W.date_of(day).weekday()
        if t == "away" and wd in (1, 3):
            return {"plan": _fill(P, W.PROP_PLACES), "p_out": 0.97, "why": "away day"}
        if t == "cue":
            sign = "SIGN" in self.h_seen_dock.get(day - 1, [])
            first = P[0] if sign else P[1]
        elif t == "random":
            first = P[0]
        elif t == "rotation":
            first = P[(day - 1) % 3]
        else:
            first = W._rule_place(r, day, self.world.cleaning)
        return {"plan": _fill([first] + P, W.PROP_PLACES), "p_out": 0.03, "why": "rule"}

    def __init__(self, world):
        super().__init__(world)
        self.h_seen_dock = {}

    def evening(self, day, report):
        self.h_seen_dock[day] = report["seen"].get("dock", [])
        return super().evening(day, report)

    def state(self):
        return {"history": self.h.state(), "dock": self.h_seen_dock}

    def load(self, s):
        super().load(s)
        self.h_seen_dock = {int(k): v for k, v in (s.get("dock") or {}).items()}


# ---------- model methods ----------

SYSTEM = (
    "You are the memory and planning part of a robot dog (Unitree Go2) that works in a university robotics lab. "
    "Each lab day (Monday to Friday; the lab is closed at weekends) the dog is asked to find some of seven objects. "
    "People in the lab move these objects around. The dog's camera is low (0.37 m), so it only checks these 14 places:\n"
    + "\n".join(f"- {k}: {d}" for k, (d, _) in W.PLACES.items())
    + "\n\nThe seven objects:\n" + "\n".join(f"- {k}: {d}" for k, d in W.PROPS.items())
    + "\n\nEach lab day: in the morning, before looking anywhere, you forecast where each object is. Then the dog "
    "searches for three of the objects, looking at the places in your forecast in order and stopping when it sees "
    "the object. Then it patrols the dock and four other places. Everything the dog sees at each place it looks at is "
    "reported to you. Objects stay put during the day. The camera misses an object that is really there about 1 time "
    "in 10. An object can also be out of the lab for the day (someone took it with them); then no place has it."
)


def _scenery(place):
    return W.PLACES[place][1]


def render_day(r) -> str:
    """One lab day as the model sees it."""
    day = r["day"]
    lines = [f"Day {day}, {W.weekday(day)} {W.date_of(day).isoformat()}."]
    lines.append("Searches:")
    for p, s in r["searches"].items():
        looked = ", ".join(s["plan"][: s["looks"]]) if s["plan"] else "(no places given)"
        res = f"found at {s['found_at']} (look {s['looks']})" if s["found_at"] else "not found in any of them"
        lines.append(f"- {p}: looked at {looked}; {res}")
    lines.append(f"Patrol: {', '.join(r['patrol'])}.")
    lines.append("What the dog saw at every place it looked at today (of the seven objects, plus anything unusual):")
    for place in sorted(r["seen"]):
        objs = [("a " + W.SIGN) if x == "SIGN" else x for x in r["seen"][place]]
        scen = _scenery(place)
        txt = ", ".join(objs) if objs else "none of the seven objects"
        lines.append(f"- {place}: {txt}" + (f" (also the usual {', '.join(scen)})" if scen else ""))
    return "\n".join(lines)


def render_forecast_check(r) -> str:
    seen_at = {}
    for place, seen in r["seen"].items():
        for p in seen:
            seen_at.setdefault(p, place)
    lines = ["This morning's forecast against what the dog saw today:"]
    for p in PROPS:
        f = r["forecast"].get(p) or {}
        first = (f.get("plan") or ["(none)"])[0]
        if p in seen_at:
            res = f"seen at {seen_at[p]}"
        elif p in r["searches"]:
            res = "searched for and not found"
        else:
            res = "not seen today (not searched for)"
        lines.append(f"- {p}: you forecast {first} first, out-of-lab probability {f.get('p_out', '?')}; {res}")
    return "\n".join(lines)


FORECAST_SCHEMA = {
    "type": "object",
    "properties": {"forecast": {"type": "object", "properties": {
        p: {"type": "object", "properties": {
            "plan": {"type": "array", "items": {"type": "string", "enum": W.PROP_PLACES}, "minItems": 5, "maxItems": 5},
            "p_out": {"type": "number", "minimum": 0, "maximum": 1},
            "why": {"type": "string", "maxLength": 240}},
            "required": ["plan", "p_out", "why"]} for p in PROPS},
        "required": PROPS}},
    "required": ["forecast"],
}

FORECAST_ASK = (
    "Today is day {day}, {wd} {date}. Forecast every one of the seven objects. For each give: 'plan', up to 5 "
    "different places to look, most likely first (the dock is not a place objects are kept, so it is never in a plan); "
    "'p_out', the probability (0 to 1) that the object is out of the lab today; 'why', one short sentence."
)


def ask_think_then_plain(system, prompt, schema, max_tokens):
    """Thinking on; if the thinking runs out of room or the answer does not parse, ask again without thinking.
    The first attempt's info is kept under 'first_try'."""
    out, info = ask_json(system, prompt, schema, think=True, max_tokens=max_tokens)
    if out is not None:
        return out, info
    out2, info2 = ask_json(system, prompt, schema, think=False, max_tokens=7000)
    info2["first_try"] = {k: info.get(k) for k in ("finish", "usage", "seconds", "error")}
    info2["fallback_no_thinking"] = True
    return out2, info2


class LLMMethod:
    llm = True
    think_forecast = False   # forecasts without thinking (speed: 3-6 min per thinking call); see DESIGN.md
    think_evening = False    # main run: no thinking anywhere; the *_think methods turn it on (4 labs)

    def ask_evening(self, prompt, schema):
        if self.think_evening:
            out, info = ask_json_budget(SYSTEM, prompt, schema)
            return out, info
        return ask_json(SYSTEM, prompt, schema, think=False, max_tokens=7000)

    def __init__(self, world):
        self.world = world
        self.memory = None
        self.days = []        # full_log keeps rendered days

    def memory_text(self) -> str:
        raise NotImplementedError

    def forecast(self, day):
        prompt = self.memory_text() + "\n\n" + FORECAST_ASK.format(day=day, wd=W.weekday(day), date=W.date_of(day).isoformat())
        if self.think_forecast:
            out, info = ask_json_budget(SYSTEM, prompt, FORECAST_SCHEMA, answer_tokens=3000)
        else:
            out, info = ask_json(SYSTEM, prompt, FORECAST_SCHEMA, think=False, max_tokens=3000)
        info["prompt_chars"] = len(prompt)
        fc = (out or {}).get("forecast") or {}
        res = {}
        for p in PROPS:
            f = fc.get(p) or {}
            res[p] = {"plan": _fill(f.get("plan") or [], W.PROP_PLACES), "plan_given": len(f.get("plan") or []), "p_out": float(f.get("p_out", 0.1) or 0),
                      "why": f.get("why", ""), **({} if f else {"failed": True})}
        return res, info

    def evening(self, day, report):
        return {}

    def state(self):
        return {"memory": self.memory, "days": self.days}

    def load(self, s):
        self.memory, self.days = s["memory"], s["days"]


class NoMemory(LLMMethod):
    name = "no_memory"

    def memory_text(self):
        return "You have no memory of earlier lab days."


class FullLog(LLMMethod):
    name = "full_log"

    def memory_text(self):
        if not self.days:
            return "This is the first lab day: nothing has been seen yet."
        return "Everything the dog has seen on earlier lab days, day by day:\n\n" + "\n\n".join(self.days)

    def evening(self, day, report):
        self.days.append(render_day(report) + "\n" + render_forecast_check(report))
        return {}


class FullLogThink(FullLog):
    """Full log, with thinking at forecast time: is writing memory just a way to do the reasoning earlier?"""
    name = "full_log_think"
    think_forecast = True


NOTES_SCHEMA = {"type": "object", "properties": {"notes": {"type": "string", "maxLength": 8000}}, "required": ["notes"]}
NOTES_ASK = (
    "Write your notes for tomorrow morning. They are the only thing you will have from today and every earlier day: "
    "anything not written in them is forgotten. Keep whatever will help you forecast where each object will be on "
    "future days: where each object will be, and when or why. Up to 8000 characters."
)


class Notes(LLMMethod):
    name = "notes"

    def memory_text(self):
        if self.memory is None:
            return "This is the first lab day: you have no notes yet."
        return "Your notes, written by you at the end of the last lab day (the only record you have of earlier days):\n" + self.memory

    def evening(self, day, report):
        prompt = (self.memory_text() + "\n\nToday's report.\n" + render_day(report) + "\n\n"
                  + render_forecast_check(report) + "\n\n" + NOTES_ASK)
        out, info = self.ask_evening(prompt, NOTES_SCHEMA)
        info["prompt_chars"] = len(prompt)
        if out and isinstance(out.get("notes"), str):
            self.memory = out["notes"]
        else:
            info["kept_old_memory"] = True
        return info


HYP_SCHEMA = {
    "type": "object",
    "properties": {
        "hypotheses": {"type": "array", "maxItems": 16, "items": {"type": "object", "properties": {
            "id": {"type": "string", "maxLength": 12},
            "object": {"type": "string", "enum": PROPS},
            "statement": {"type": "string", "maxLength": 160},
            "status": {"type": "string", "enum": ["active", "set_aside"]},
            "evidence_for": {"type": "string", "maxLength": 120},
            "evidence_against": {"type": "string", "maxLength": 120},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}},
            "required": ["id", "object", "statement", "status", "evidence_for", "evidence_against", "confidence"]}},
        "notes": {"type": "string", "maxLength": 1600}},
    "required": ["hypotheses", "notes"],
}
HYP_ASK = (
    "Update your hypotheses for tomorrow morning. They and your notes are the only thing you will have from today and "
    "every earlier day: anything not written in them is forgotten.\n"
    "A hypothesis says where an object will be and when or why. For each keep: an id; the object; the statement; "
    "the status, 'active' or 'set_aside'; evidence for (which days fit); evidence against (which days did not); "
    "a confidence from 0 to 1.\n"
    "From today's report: add evidence to the hypotheses it bears on and adjust their confidence. Add a new hypothesis "
    "when something is not explained by the ones you have. When the evidence turns against an active hypothesis, set it "
    "aside instead of deleting it, and say in its evidence when and why. Keep at least one active hypothesis for every "
    "object. Up to 16 hypotheses (statement up to 160 characters, each evidence field up to 120). The notes (up to 1600 characters) are for anything else you need tomorrow."
)


def render_hyps(m) -> str:
    lines = []
    for status in ("active", "set_aside"):
        hs = [h for h in m["hypotheses"] if h["status"] == status]
        lines.append(f"{'Active' if status == 'active' else 'Set aside'} hypotheses ({len(hs)}):")
        for h in sorted(hs, key=lambda h: (h["object"], -h["confidence"])):
            lines.append(f"- [{h['id']}] {h['object']}: {h['statement']} (confidence {h['confidence']}; "
                         f"for: {h['evidence_for']}; against: {h['evidence_against']})")
    lines.append("Notes: " + (m.get("notes") or "(none)"))
    return "\n".join(lines)


class Hypotheses(LLMMethod):
    name = "hypotheses"
    ask_text = HYP_ASK

    def memory_text(self):
        if self.memory is None:
            return "This is the first lab day: you have no hypotheses or notes yet."
        return ("Your hypotheses and notes, written by you at the end of the last lab day (the only record you have of "
                "earlier days):\n" + render_hyps(self.memory))

    def evening(self, day, report):
        prompt = (self.memory_text() + "\n\nToday's report.\n" + render_day(report) + "\n\n"
                  + render_forecast_check(report) + "\n\n" + self.ask_text)
        out, info = self.ask_evening(prompt, HYP_SCHEMA)
        info["prompt_chars"] = len(prompt)
        if out and isinstance(out.get("hypotheses"), list):
            self.memory = {"hypotheses": out["hypotheses"], "notes": out.get("notes", "")}
        else:
            info["kept_old_memory"] = True
        return info


class HypothesesWeekday(Hypotheses):
    """Mechanism check (added 03:00 after the main run): the main run's evidence fields list 'Day 8' with no weekday,
    so weekday patterns cannot surface from them. Same as hypotheses, except evidence is written with weekdays."""
    name = "hypotheses_wd"
    ask_text = HYP_ASK.replace("evidence for (which days fit); evidence against (which days did not)",
                               "evidence for (which days fit, each written with its weekday, e.g. 'Tue d7'); "
                               "evidence against (which days did not, written the same way)")
    assert ask_text != HYP_ASK


class NotesThink(Notes):
    name = "notes_think"
    think_evening = True


class HypothesesThink(Hypotheses):
    name = "hypotheses_think"
    think_evening = True


METHODS = {m.name: m for m in (LastSeen, MostOften, SameWeekday, RulesKnown, NoMemory, FullLog, FullLogThink, Notes,
                               Hypotheses, HypothesesWeekday, NotesThink, HypothesesThink)}


def memory_as_text(name, state) -> str:
    """The method's written memory at a point, for the grader."""
    m = state.get("memory")
    if m is None:
        return ""
    return render_hyps(m) if name.startswith("hypotheses") else m


if __name__ == "__main__":
    print(SYSTEM)
    print(json.dumps(FORECAST_SCHEMA)[:300])
