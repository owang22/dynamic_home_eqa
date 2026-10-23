"""Small/large routing for the lab agent: rules at the turn boundary, hard signals within a turn.

    from router import classify, Monitor
    route = classify("walk to kang's desk", place_ids)      # Route(name="place", tier="small", tools=[...], why=...)
    mon = Monitor(route)                                      # pass mon.on_step to SmallAgent(on_step=...)
    trace = SmallAgent(..., tools=route.tools, on_step=mon.on_step).run(text)
    if mon.escalated: hand the whole remaining turn to the big model (mon.reason says why)

Turn routes (research_hierarchy.md section 4, rules first):
  stop    "stop" / "halt" alone: no model at all; the caller posts /agent/stop at once
  place   go_to a named place (fuzzy match to a place id), status, list_places, release   -> small, PLACE_TOOLS
  memory  "have you seen / where is / what did you see"                                     -> small, MEMORY_TOOLS
  big     people counting / busy-ness, who / find a person, go to a thing, attributes (colour, wearing, what is
          on ...), relocalization, multi-step ("and then"), anything not matched            -> big model
Within-turn escalation (Monitor): REFUSED / blocked / no_route / ERROR in a tool result; the same call twice;
more than `max_steps` tool calls; two invalid actions; ask_expert; a final answer that cites no picture the small
model opened (variant "neg_ok": a "not seen" answer may stand after two different searches without time filters).
The whole remaining turn goes up, not one step.
"""
from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass, field

from small_agent import MEMORY_TOOLS, PLACE_TOOLS

PIC = re.compile(r"\b([tpl]\d{9,}(?:_\d+)?)\b")

STOP_ONLY = re.compile(r"\W*(please\s+)?(stop|halt|freeze|wait|stay|no|stop (it|now|right now|the dog|moving|there))"
                       r"(\s+(now|please|right now))?\W*", re.I)
MOVE = re.compile(r"\b(go|walk|move|drive|head|come|bring|take|navigate|return|get)\b", re.I)
PEOPLE = re.compile(r"\b(how many|count|busy|quiet|anyone|anybody|someone|somebody|people|persons?|who)\b", re.I)
FIND_PERSON = re.compile(r"\b(find|look for|search for|follow|where is|where's)\s+(him|her|them|me|oliver|khang|kang|"
                         r"pragya|gaofeng|brian|joseph|yuyang|liying|someone|somebody|a person|the person)\b", re.I)
ATTR = re.compile(r"\b(colou?r|wearing|wear|dressed|what kind|what brand|what is on|what's on|on top of|"
                  r"how big|how tall|open or closed|on or off)\b", re.I)
RELOC = re.compile(r"\b(re-?locali[sz]e|locali[sz]ation|locali[sz]ed|lost|where are you|your position|"
                   r"lined up|initial pose)\b", re.I)
MULTI = re.compile(r"\b(and then|then|after that|afterwards|and stop|and come back)\b", re.I)
MEMORY = re.compile(r"\b(have you seen|did you see|seen|see any|where is|where's|where are|where did|is there|are there|"
                    r"what did you see|when did you|last see|last time)\b", re.I)
ADMIN = re.compile(r"\b(status|list (the )?places|what places|release|give (back )?control)\b", re.I)
NO_MOVE = re.compile(r"\b(do not|don't|dont|without|no need to|never)\s+(move|moving|drive|driving|walk|walking|go)"
                     r"( the dog| it)?\b", re.I)
NEG = re.compile(r"(not seen|haven't seen|have not seen|did not see|didn't see|no pictures|not found|could not find|"
                 r"couldn't find|not in (any|the)|no \w+( \w+)? (was |were )?(seen|found)|i have not|i haven't|"
                 r"cannot confirm|can't confirm|not confirmed)", re.I)


@dataclass
class Route:
    name: str            # stop | place | memory | big
    tier: str            # none | small | big
    why: str
    tools: list = field(default_factory=list)
    place: str | None = None


def place_aliases(pid: str) -> list[str]:
    words = pid.replace("_", " ")
    al = [words]
    if pid.startswith("desk_"):
        who = pid[5:]
        al += [f"{who} desk", f"{who}s desk", f"desk of {who}", f"{who} s desk"]
    if pid.startswith("door_"):
        al += [f"{pid[5:]} door"]
    return al


def norm(text: str) -> str:
    t = text.lower().replace("’", "'")
    t = re.sub(r"'s\b", "s", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return " ".join(t.split())


def resolve_place(text: str, place_ids: list[str]) -> str | None:
    """A place id named in the text: exact alias first, then a close spelling (kang'desk -> desk_kang)."""
    t = f" {norm(text)} "
    for pid in sorted(place_ids, key=len, reverse=True):
        for a in place_aliases(pid):
            if f" {a} " in t:
                return pid
    toks = t.split()
    best, score = None, 0.0
    for pid in place_ids:
        for a in place_aliases(pid):
            n = len(a.split())
            for i in range(len(toks) - n + 1):
                r = difflib.SequenceMatcher(None, " ".join(toks[i:i + n]), a).ratio()
                if r > score:
                    best, score = pid, r
    return best if score >= 0.88 else None


def classify(text: str, place_ids: list[str]) -> Route:
    t = text.strip()
    if STOP_ONLY.fullmatch(t):
        return Route("stop", "none", "stop keyword: no model")
    if RELOC.search(t):
        return Route("big", "big", "relocalization")
    if MULTI.search(t):
        return Route("big", "big", "multi-step request")
    if FIND_PERSON.search(t):
        return Route("big", "big", "find a person")
    moving = bool(MOVE.search(NO_MOVE.sub(" ", t)))
    place = resolve_place(t, place_ids)
    if moving:
        if place and not ATTR.search(t):
            return Route("place", "small", f"go to named place {place}", PLACE_TOOLS, place)
        return Route("big", "big", "go to a thing (needs locate)" if not place else "move with extra conditions")
    if PEOPLE.search(t):
        return Route("big", "big", "people / who / busy-ness")
    if ATTR.search(t):
        return Route("big", "big", "attribute question")
    if ADMIN.search(t):
        return Route("place", "small", "status / places / release", PLACE_TOOLS)
    if MEMORY.search(t):
        return Route("memory", "small", "have you seen / where is", MEMORY_TOOLS)
    return Route("big", "big", "not matched by any rule (ambiguous)")


class Monitor:
    """Within-turn escalation signals for a SmallAgent run. on_step returns True to end the small run when
    `stop_on_signal` (live use); offline it only records, so one run serves every policy."""

    def __init__(self, route: Route | None = None, max_steps: int = 4, stop_on_signal: bool = False,
                 answer_rule: str = "strict"):
        self.route, self.max_steps, self.stop_on_signal, self.answer_rule = route, max_steps, stop_on_signal, answer_rule
        self.signals: list[dict] = []
        self.seen_calls: set = set()
        self.invalid = 0

    @property
    def escalated(self) -> bool:
        return bool(self.signals)

    @property
    def reason(self) -> str | None:
        return self.signals[0]["why"] if self.signals else None

    def _sig(self, step, why):
        self.signals.append({"step": step.get("i"), "t": step.get("t"), "why": why})

    def on_step(self, step, steps, opened) -> bool:
        n0 = len(self.signals)
        tool = step.get("tool")
        if tool is None:
            self.invalid += 1
            if self.invalid >= 2:
                self._sig(step, "two invalid actions")
        elif tool == "ask_expert":
            self._sig(step, "ask_expert: " + str((step.get("args") or {}).get("reason", ""))[:80])
        elif tool == "answer":
            why = answer_problem(step.get("args") or {}, opened, steps, self.route, self.answer_rule)
            if why:
                self._sig(step, why)
        else:
            res = step.get("result") or ""
            if res.startswith(("REFUSED", "ERROR")) or re.search(r"\b(blocked|no_route|aborted)\b", res[:300]):
                self._sig(step, f"{tool} returned {res[:60]!r}")
            key = json.dumps([tool, step.get("args")], sort_keys=True)
            if key in self.seen_calls:
                self._sig(step, f"repeated call {tool}")
            self.seen_calls.add(key)
            ncalls = sum(1 for s in steps if s.get("tool") not in (None, "answer"))
            if ncalls > self.max_steps:
                self._sig(step, f"more than {self.max_steps} tool calls")
        return self.stop_on_signal and len(self.signals) > n0


def answer_problem(ans: dict, opened: list, steps: list, route: Route | None, rule: str = "strict") -> str | None:
    text = ans.get("text") or ""
    cited = set(ans.get("cited_ids") or []) | set(PIC.findall(text))
    if not text.strip():
        return "empty answer"
    if route is not None and route.name == "place":
        return None                                  # driving/status answers need no picture citation
    not_opened = cited - set(opened)
    if not_opened:
        return f"cites pictures it did not open: {sorted(not_opened)[:3]}"
    if cited & set(opened):
        return None
    if rule == "neg_ok" and NEG.search(text):
        searches = [s for s in steps if s.get("tool") == "search_memory"]
        queries = {(s.get("args") or {}).get("query", "").lower() for s in searches}
        filtered = any((s.get("args") or {}).get("since") or (s.get("args") or {}).get("until") for s in searches)
        if len(queries) >= 2 and not filtered:
            return None
        return "'not seen' after fewer than two wordings or with a time filter"
    return "answer cites no picture it opened"


def replay_signals(trace: dict, route: Route | None, max_steps: int = 4, answer_rule: str = "strict") -> list:
    """Re-run the Monitor over a recorded SmallAgent trace (offline policy evaluation)."""
    mon = Monitor(route, max_steps=max_steps, answer_rule=answer_rule)
    steps, opened = [], []
    for s in trace["steps"]:
        steps.append(s)
        if s.get("tool") not in (None, "answer"):
            opened += s.get("pics") or []
        mon.on_step(s, steps, opened)
    if not any(s.get("tool") == "answer" for s in trace["steps"]):
        mon.signals.append({"step": len(trace["steps"]), "t": trace.get("secs"), "why": "no answer within the step limit"})
    return mon.signals


VERIFY_SCHEMA = {"type": "object", "properties": {
    "why": {"type": "string", "maxLength": 300},
    "verdict": {"type": "string", "enum": ["supported", "not supported", "cannot tell"]}},
    "required": ["why", "verdict"]}


def verify_draft(mid, question: str, answer: str, pics: list[tuple[str, bytes]]) -> dict:
    """Draft-then-verify (research_hierarchy.md 4.5): the stronger local model (27B) looks at the pictures the small
    model opened and says whether they support its draft answer. 'not supported' -> escalate."""
    from llm import image_part
    content = []
    for pid, jpg in pics[:6]:
        content += [{"type": "text", "text": f"picture {pid}:"}, image_part(jpg, 768)]
    content.append({"type": "text", "text": (
        "A robot dog's assistant answered a question from these pictures (the ones it opened). Check the answer "
        "against the pictures. 'supported': the pictures show what the answer claims (thing seen or not, where, "
        "colour, count). 'not supported': a main claim is wrong or not visible in them. 'cannot tell': the answer "
        "says something was not seen and the pictures cannot confirm or refute that.\n"
        f"QUESTION: {question}\nANSWER: {answer}")})
    r = mid.chat([{"role": "user", "content": content}], schema=VERIFY_SCHEMA, max_tokens=400)
    return dict(r["json"] or {"verdict": "cannot tell", "why": "no valid reply"}, secs=r["secs"])
