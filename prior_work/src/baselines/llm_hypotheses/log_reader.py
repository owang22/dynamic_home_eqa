"""Arm: an LLM reads the sighting log and decides directly. No belief
model, no hypotheses, no mixture.

Tests whether the hypothesis machinery buys anything at a 28-day
horizon, or whether the log is small enough that a model can just read
it. Two variants:

* ``log_reader`` — every decision is one LLM call over the whole log.
* ``log_reader_notes`` — the same, plus a scratchpad the model owns:
  once per simulated day it is handed the day's log and may overwrite
  one free-form notes file, which then sits in every call's prefix. The
  notes files are the primary output of that variant: if the model
  writes down rest locations and clock-scheduled activities on its own,
  that structure is discoverable rather than assumed by our schema.

**Where it plugs in.** :class:`LogReaderBelief` and
:class:`LogReaderPolicy` satisfy the existing interfaces, sharing one
:class:`LogReaderBrain`. The harness commits the prediction it computed
BEFORE the final ``decide`` call, so the LLM call has to happen inside
the belief's ``predict`` for the question's object; the policy then
relays the brain's decision (``Sense`` or ``AnswerNow``). Per-object
snapshot predictions (``predict_readonly``, 35 per question) never reach
the LLM: they return the object's last sighting.

**Information condition** matches the graph arm: the object table lists
only objects seen so far, the tour is the log's first entries stamped
with its hour, and the anonymized condition uses the same token maps.

**Cost lever.** Every call is ``stable prefix + append-only log +
question``; nothing in the prefix changes within a day (the notes
variant changes it once a day), so the server's prefix cache hits on
almost everything. The log is never filtered to the queried object.

**Output** is guided JSON with thinking off (2472+ calls; a think block
per call would take days)::

    {"action": "sense", "receptacle": "kitchen_table_k1", "why": "..."}
    {"action": "answer", "ranked": ["kitchen_table_k1", ...], "why": "..."}

``ranked`` (1 to 5) is turned into a rank-shaped pseudo-distribution so
the harness has a ``Prediction`` to record; top-1 is comparable with the
other arms, log-loss is not (``log_loss_valid: False`` in diagnostics).
"""

from __future__ import annotations

import collections
import json
import pathlib
import random
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.llm_hypotheses.protocol_text import weekday_index as _weekday_index, day0_name as _day0_name
from baselines.llm_hypotheses.prompt import away_sentences
from baselines.policies.base import DecisionPolicy
from baselines.types import (DAY_SECONDS, ON_PERSON, Action, AnswerNow,
                             EpisodeContext, Observation, PersonSenseResult,
                             Prediction, Question, Sense, SensePerson,
                             SenseResult)

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MAX_RANKED = 5
DECISION_MAX_TOKENS = 400
NOTES_MAX_TOKENS = 24000
"""Budget for one notes rewrite INCLUDING the think block (Qwen3.8
spends 3k-8k tokens thinking before it writes): at 6000 the file was
cut mid-sentence on most days and once an unclosed think block was
taken for the notes. The written file itself is asked to stay short."""
NOTES_MAX_WORDS = 1200
RANK_WEIGHTS = (0.55, 0.20, 0.12, 0.08, 0.05)
"""Pseudo-probabilities for a ranked answer; a shape, not a calibration."""

DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["sense", "answer"]},
        "receptacle": {"type": "string"},
        "ranked": {"type": "array", "items": {"type": "string"},
                   "minItems": 1, "maxItems": MAX_RANKED},
        "why": {"type": "string"}},
    "required": ["action", "why"],
}

SYSTEM_PROMPT = (
    "You control a home robot's memory. You read its sighting log and "
    "decide, for one question at a time, whether to look inside a "
    "receptacle or to answer where an object is.")


def stamp(t: int) -> str:
    day, rem = divmod(int(t), DAY_SECONDS)
    return f"d{day:02d} {WEEKDAY_NAMES[_weekday_index(day)]} {rem // 3600:02d}:{rem % 3600 // 60:02d}"


class LogReaderBrain:
    """The shared state and the two LLM calls (decide, write notes).

    ``client`` has the ``generate(system, user, seed, temperature,
    max_tokens, reasoning_effort=..., schema=...)`` interface of
    :class:`~baselines.llm_hypotheses.elicit.CachedThinkingClient`; a
    stub with the same signature serves tests. ``omap`` / ``rmap`` are
    the anonymization maps (empty when named); the log and every prompt
    are written in the model's vocabulary and the decision is translated
    back to real ids.
    """

    def __init__(self, client: Any, notes: bool = False,
                 aided: bool = False,
                 omap: Optional[Mapping[str, str]] = None,
                 rmap: Optional[Mapping[str, str]] = None,
                 cmap: Optional[Mapping[str, str]] = None,
                 log_dir: Optional[pathlib.Path] = None,
                 temperature: float = 0.2, seed: int = 5) -> None:
        self.client = client
        self.notes_enabled = notes
        self.aided = aided
        """The same help the treeLongLeaf prompts give: the out-of-house
        mechanics paragraph in the prefix, and a per-object table of
        weekday-daytime looks at each object's usual place (found versus
        found nothing) after the log."""
        self._omap = dict(omap or {})
        self._rmap = dict(rmap or {})
        self._cmap = dict(cmap or {})
        self._rev_r = {v: k for k, v in self._rmap.items()}
        self._log_dir = pathlib.Path(log_dir) if log_dir else None
        self._temperature = temperature
        self._seed = seed
        self.reset(None)

    # ---------------------------------------------------------- lifecycle

    def reset(self, context: Optional[EpisodeContext]) -> None:
        self.context = context
        self.log: List[str] = []
        self.known: Dict[str, str] = {}          # real object id -> class
        self.notes = ""
        self.notes_versions: List[Dict[str, Any]] = []
        self.spent_today = 0.0
        self.day = -1
        self.notes_day = -1
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.generation_seconds = 0.0
        self.decisions: List[Dict[str, Any]] = []
        self.invalid_decisions = 0
        self._seen: Dict[str, Dict[str, int]] = {}      # real obj -> rec -> n
        self._looks: List[Tuple[int, str, Tuple[str, ...]]] = []
        self._question_key: Optional[Tuple[str, int]] = None
        self._sensed_this_question: List[str] = []
        # residents this question's own looks listed -> the room; only
        # these may be looked at (the harness enforces the same rule)
        self._listed_this_question: Dict[str, Optional[str]] = {}
        self._awaiting_sense = False
        self._last: Optional[Dict[str, Any]] = None
        if self._log_dir:
            self._log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------- naming

    def obj(self, real: str) -> str:
        return self._omap.get(real, real)

    def rec(self, real: str) -> str:
        return self._rmap.get(real, real)

    def real_rec(self, token: str) -> str:
        return self._rev_r.get(token, token)

    # ---------------------------------------------------------------- log

    def observe(self, evidence: Any) -> None:
        """Append one evidence event to the log, in the model's
        vocabulary. The tour's entries are tagged as the walkthrough. A
        receptacle look on a person-sensing bank also names the residents
        in that room; a person look lists what the resident carries (each
        listed object is at ON_PERSON with that resident, in that room)."""
        t = evidence.t
        if isinstance(evidence, Observation):
            self.known.setdefault(evidence.object_id, evidence.object_class)
            c = self._seen.setdefault(evidence.object_id, {})
            c[evidence.receptacle_id] = c.get(evidence.receptacle_id, 0) + 1
            self._looks.append((t, evidence.receptacle_id, (evidence.object_id,)))
            tag = " [walkthrough]" if evidence.source == "initial_tour" else ""
            self.log.append(f"{stamp(t)}{tag} {self.obj(evidence.object_id)} "
                            f"at {self.rec(evidence.receptacle_id)}")
            return
        for o in evidence.contents:
            self.known.setdefault(o, evidence.object_classes.get(o, ""))
            c = self._seen.setdefault(o, {})
            c[evidence.receptacle_id] = c.get(evidence.receptacle_id, 0) + 1
        self._looks.append((t, evidence.receptacle_id,
                            tuple(evidence.contents)))
        inside = (", ".join(self.obj(o) for o in evidence.contents)
                  or "(nothing)")
        if isinstance(evidence, PersonSenseResult):
            where = f" in {evidence.room}" if evidence.room else ""
            self.log.append(f"{stamp(t)} look {self.rec(evidence.resident_id)}"
                            f"{where}: {inside}")
            self._awaiting_sense = False
            return
        line = f"{stamp(t)} look {self.rec(evidence.receptacle_id)}: {inside}"
        if self._person_sensing():
            who = ", ".join(self.rec(r) for r in evidence.residents_present)
            line += f"; residents here: {who or 'nobody'}"
        if self._awaiting_sense and self._question_key is not None \
                and t == self._question_key[1]:
            room = (self.context.receptacle_rooms or {}).get(
                evidence.receptacle_id) if self.context else None
            for r in evidence.residents_present:
                self._listed_this_question[r] = room
        self._awaiting_sense = False
        self.log.append(line)

    def _person_sensing(self) -> bool:
        return bool(self.context is not None and self.context.person_sensing)

    def _lookable_residents(self) -> List[str]:
        """Residents this question's looks listed and the model has not
        looked at yet (real ids)."""
        return [r for r in self._listed_this_question
                if r not in self._sensed_this_question]

    # ------------------------------------------------------------- prompt

    def _stable_prefix(self) -> str:
        assert self.context is not None
        ctx = self.context
        rooms = ctx.receptacle_rooms or {}
        rec_lines = []
        for r in ctx.receptacle_ids:
            room = rooms.get(r)
            rec_lines.append(f"  {self.rec(r)}" + (f"  in {room}" if room else ""))
        rec_lines.append(away_sentences(self._rmap).replace("`", ""))
        person = self._person_sensing()
        if person and ctx.resident_ids:
            rec_lines.append("")
            rec_lines.append("RESIDENTS:")
            rec_lines += [f"  {self.rec(r)}" for r in ctx.resident_ids]
        person_format = (
            ' On a look at a receptacle, "; residents here: <residents>" '
            'names who was in that room at that moment. "dNN Day HH:MM look '
            '<resident> in <room>: <objects>" lists everything that resident '
            f'was carrying at that moment: each listed object was at '
            f'{self.rec(ON_PERSON)}, with that resident, in that room.'
            if person else "")
        person_sensing = (
            " A look at a resident reports every object they are carrying; "
            "it costs the same as a look at a receptacle and is possible "
            "only for a resident that one of this question's looks has "
            "shown in a room." if person else "")
        person_output = (
            ' A resident id, exactly as listed, is also a valid "receptacle" '
            'for a sense once a look this question has shown them in a room.'
            if person else "")
        text = f"""A home robot patrols a home and records what it sees. You will be given its log, then one question. Decide whether to look inside one receptacle first, or to answer now.

RECEPTACLES (every place an object can be):
{chr(10).join(rec_lines)}

LOG FORMAT: one line per event, oldest first. "dNN Day HH:MM <object> at <receptacle>" is a sighting; "dNN Day HH:MM look <receptacle>: <objects>" lists everything found inside that receptacle at that moment.{person_format} Lines tagged [walkthrough] are from the robot's installation tour. The log lists what the robot saw; it is the only information there is.

SENSING: one look inspects one receptacle and reports every object inside it.{person_sensing} Each look costs from a daily budget of {ctx.budget_per_day} that resets at midnight. A look answers the current question and also stays in the log for every later question, so a look can be spent on learning rather than on the question at hand. There is no penalty for spending budget beyond not having it later.

SCORING: an answer scores one point if its first ranked receptacle is where the object actually is at the question's time, and zero otherwise.

OUTPUT: one JSON object. Either {{"action": "sense", "receptacle": "<receptacle id>", "why": "..."}} or {{"action": "answer", "ranked": ["<most likely receptacle>", "...up to 5..."], "why": "..."}}. Use receptacle ids exactly as listed.{person_output}"""
        if self.aided:
            text += ("\n\nOBJECTS LEAVE THE HOUSE: residents take things with "
                     "them to work, to school, to the gym, on errands and on "
                     "trips; an object that is out is invisible to every look "
                     "while it is out, and the walkthrough happened at one "
                     "instant, so anything that was out with someone then is "
                     "missing from the walkthrough and first appears in the "
                     "log later. A sighting anywhere in the house says the "
                     "object is in; an empty look at its usual place, at an "
                     "hour it is usually there, is weak evidence it is out. "
                     "After the log you get, per object, a count of weekday "
                     "daytime looks at its usual place that found it versus "
                     "found nothing.")
        if self.notes_enabled:
            text += (f"\n\nYOUR NOTES (a file you wrote for yourself, "
                     f"rewritten once a day; empty until you write it):\n"
                     f"{self.notes or '(empty)'}")
        return text

    def _absence_block(self, start_h: float = 9.0, end_h: float = 17.0) -> str:
        """Per sighted object: usual place, and weekday ``start_h``-``end_h``
        looks there split into found / found nothing. From the robot's
        own looks only."""
        lines = [f"WEEKDAY {start_h:g}:00-{end_h:g}:00 LOOKS AT EACH OBJECT'S "
                 f"USUAL PLACE (found it / found nothing):"]
        for obj in sorted(self._seen):
            modal = max(self._seen[obj], key=self._seen[obj].get)
            found = empty = 0
            for t, rec, contents in self._looks:
                if rec != modal or (t // DAY_SECONDS) % 7 in (5, 6):
                    continue
                hour = (t % DAY_SECONDS) / 3600.0
                if not start_h <= hour < end_h:
                    continue
                if obj in contents:
                    found += 1
                else:
                    empty += 1
            lines.append(f"  {self.obj(obj)}: usually {self.rec(modal)} "
                         f"({sum(self._seen[obj].values())} sightings); "
                         f"found {found}, found nothing {empty}")
        return "\n".join(lines)

    def _objects_block(self) -> str:
        lines = [f"  {self.obj(o)}  (class: {self._cmap.get(c, c)})"
                 for o, c in sorted(self.known.items())]
        return "OBJECTS the robot has seen so far:\n" + "\n".join(lines)

    def _question_block(self, object_id: str, t: int,
                        looks_left: int) -> str:
        remaining = max(0.0, (self.context.budget_per_day if self.context
                              else 0) - self.spent_today)
        sensed = [self.rec(r) for r in self._sensed_this_question]
        lookable = self._lookable_residents()
        residents = ""
        if lookable:
            residents = ("\nRESIDENTS this question's looks have shown, each "
                         "a valid look target now: " + ", ".join(
                             self.rec(r) + (f" (in {self._listed_this_question[r]})"
                                            if self._listed_this_question[r] else "")
                             for r in lookable))
        return (f"QUESTION: where is {self.obj(object_id)} right now?\n"
                f"NOW: {stamp(t)}\n"
                f"BUDGET: {remaining:g} looks left today"
                + (f"; already looked this question at {', '.join(sensed)}"
                   if sensed else "")
                + f"; at most {looks_left} more looks on this question."
                + residents)

    # ----------------------------------------------------------- decision

    def decide(self, object_id: str, t: int) -> Dict[str, Any]:
        """One LLM call for the current question state. Returns
        ``{"action": "sense", "receptacle": real id}`` or
        ``{"action": "answer", "ranked": [real ids]}``. Invalid output
        (unknown or repeated receptacle, unsensable target, empty ranked
        list) degrades to an answer from the log and is counted."""
        assert self.context is not None
        day = t // DAY_SECONDS
        if day != self.day:
            self.day = day
            self.spent_today = 0.0
        if self.notes_enabled and day != self.notes_day:
            self.notes_day = day
            if self.log:
                self._write_notes(t)
        key = (object_id, t)
        if key != self._question_key:
            self._question_key = key
            self._sensed_this_question = []
            self._listed_this_question = {}
            self._awaiting_sense = False
        sensable = [r for r in self.context.sensable_receptacle_ids
                    if r not in self._sensed_this_question]
        looks_left = len(sensable) + len(self._lookable_residents())
        parts = [self._stable_prefix(), self._objects_block(),
                 "LOG:\n" + "\n".join(self.log)]
        if self.aided:
            # After the log, so the cached prefix through the log survives
            # the table changing with every sighting.
            parts.append(self._absence_block())
        parts.append(self._question_block(object_id, t, looks_left))
        user = "\n\n".join(parts)
        started = time.monotonic()
        row = self.client.generate(SYSTEM_PROMPT, user, seed=self._seed,
                                   temperature=self._temperature,
                                   max_tokens=DECISION_MAX_TOKENS,
                                   schema=DECISION_SCHEMA)
        self._account(row, time.monotonic() - started)
        try:
            parsed = json.loads(row["payload"])
        except (json.JSONDecodeError, TypeError):
            parsed = {}
        if not isinstance(parsed, dict):
            parsed = {}
        decision = self._validate(parsed, object_id, sensable)
        decision["t"] = t
        decision["object"] = object_id
        decision["why"] = str(parsed.get("why", ""))[:300]
        decision["raw"] = parsed if decision.get("invalid") else None
        decision["prompt_chars"] = len(user)
        decision["prompt_tokens"] = row.get("prompt_tokens")
        # A cache hit replays in no time; report what generation cost
        # when it was live, and say it was a hit.
        decision["seconds"] = round(
            (row.get("generation_seconds") or 0.0) if row.get("cached")
            else time.monotonic() - started, 2)
        decision["cached"] = bool(row.get("cached"))
        self.decisions.append(decision)
        self._last = decision
        self._log_call(user, row, decision)
        return decision

    def _log_call(self, user: str, row: Mapping[str, Any],
                  decision: Mapping[str, Any]) -> None:
        """Human-readable trail under ``log_dir``: every decision as one
        JSONL line (``calls.jsonl``), and the full prompt plus reply for
        the first three calls and every 250th after that
        (``prompt_NNNNN.md``), so a run can be read without replaying
        it."""
        if not self._log_dir:
            return
        n = len(self.decisions)
        with open(self._log_dir / "calls.jsonl", "a") as fh:
            fh.write(json.dumps({k: v for k, v in decision.items()
                                 if k != "raw"}) + "\n")
        if n <= 3 or n % 250 == 0:
            (self._log_dir / f"prompt_{n:05d}.md").write_text(
                f"# call {n}: {decision.get('object')} at "
                f"{stamp(int(decision.get('t', 0)))}\n\n## system\n\n"
                f"{SYSTEM_PROMPT}\n\n## user\n\n{user}\n\n## reply\n\n"
                f"{row.get('payload')}\n")

    def _validate(self, parsed: Mapping[str, Any], object_id: str,
                  sensable: Sequence[str]) -> Dict[str, Any]:
        assert self.context is not None
        action = str(parsed.get("action", ""))
        remaining = self.context.budget_per_day - self.spent_today
        if action == "sense":
            target = self.real_rec(str(parsed.get("receptacle", "")))
            if target in self._lookable_residents() and 1.0 <= remaining:
                return {"action": "sense", "resident": target}
            cost = self.context.sense_cost(target) if target in sensable else None
            if target in sensable and cost is not None and cost <= remaining:
                return {"action": "sense", "receptacle": target}
            self.invalid_decisions += 1
            return {"action": "answer", "ranked": self._fallback(object_id),
                    "invalid": f"sense {target!r} not allowed"}
        ranked = [self.real_rec(str(r)) for r in (parsed.get("ranked") or [])]
        ranked = [r for r in ranked if r in self.context.receptacle_ids]
        if action == "answer" and ranked:
            return {"action": "answer", "ranked": ranked[:MAX_RANKED]}
        self.invalid_decisions += 1
        return {"action": "answer", "ranked": self._fallback(object_id),
                "invalid": f"unusable answer {parsed!r}"[:120]}

    def _fallback(self, object_id: str) -> List[str]:
        """Last location the log has the object at (ON_PERSON for a
        person look that found it), else the first receptacle: only for
        output the model got wrong."""
        for _, receptacle, contents in reversed(self._looks):
            if object_id in contents:
                return [receptacle]
        assert self.context is not None
        return [self.context.receptacle_ids[0]]

    def note_sense(self, target: str) -> None:
        """Account a look the policy is about to make: a receptacle, or
        a listed resident (same-room price)."""
        assert self.context is not None
        if target in self._listed_this_question:
            self.spent_today += 1.0
        else:
            self.spent_today += self.context.sense_cost(target)
        self._sensed_this_question.append(target)
        self._awaiting_sense = True

    # --------------------------------------------------------------- notes

    def _write_notes(self, t: int) -> None:
        """Once a day: hand the model its notes and the log, let it
        overwrite the file. Thinking is allowed here (one call a day)."""
        user = "\n\n".join([
            self._stable_prefix().split("\n\nYOUR NOTES")[0],
            self._objects_block(),
            "LOG so far:\n" + "\n".join(self.log),
            f"YOUR NOTES as they stand:\n{self.notes or '(empty)'}",
            f"It is {stamp(t)}. Rewrite your notes file. It is yours: any "
            f"format, any content, whatever will help you answer later "
            f"questions well and spend looks well. It is shown to you in "
            f"full before every decision, so keep it under about "
            f"{NOTES_MAX_WORDS} words. Reply with the complete new contents "
            f"of the file as plain text — no JSON wrapper, no code fences, "
            f"nothing before or after it."])
        started = time.monotonic()
        row = self.client.generate(SYSTEM_PROMPT, user, seed=self._seed + 1,
                                   temperature=self._temperature,
                                   max_tokens=NOTES_MAX_TOKENS)
        self._account(row, time.monotonic() - started)
        text = self._clean_notes(row)
        status = "ok"
        if text is None:
            status = "rejected"        # unclosed think block or empty: keep the old notes
        elif row.get("finish_reason") == "length":
            status = "truncated"
            self.notes = text
        else:
            self.notes = text
        self.notes_versions.append({"t": t, "day": t // DAY_SECONDS,
                                    "status": status, "notes": self.notes,
                                    "finish_reason": row.get("finish_reason"),
                                    "think_closed": row.get("think_closed"),
                                    "completion_tokens": row.get("completion_tokens"),
                                    "think": row.get("think", "")})
        if self._log_dir:
            day = t // DAY_SECONDS
            (self._log_dir / f"notes_day{day:02d}.md").write_text(self.notes)
            (self._log_dir / f"notes_day{day:02d}_call.md").write_text(
                f"# notes rewrite, day {day}: status {status}, "
                f"finish {row.get('finish_reason')}, think_closed "
                f"{row.get('think_closed')}\n\n## prompt\n\n{user}\n\n"
                f"## thinking\n\n{row.get('think', '')}\n\n## reply\n\n"
                f"{row.get('payload', '')}\n")

    @staticmethod
    def _clean_notes(row: Mapping[str, Any]) -> Optional[str]:
        """The notes text out of a reply, or None when the reply is not a
        notes file: a think block that never closed (the payload is
        reasoning, and a cached row from the thinking template carries
        ``think_closed`` False with an empty ``think``), or nothing at
        all. Unwraps a ``{"notes": ...}`` object and code fences the
        model may add despite being asked not to."""
        text = str(row.get("payload") or "").strip()
        if not text:
            return None
        if row.get("think_closed") is False and not row.get("think"):
            return None
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[1] if "\n" in text else text
            text = text.rsplit("```", 1)[0].strip()
        if text.startswith("{"):
            try:
                obj = json.loads(text)
                if isinstance(obj, dict) and isinstance(obj.get("notes"), str):
                    return obj["notes"].strip() or None
            except json.JSONDecodeError:
                # A truncated {"notes": "..."} wrapper: salvage the string.
                head = text.find('"notes"')
                if head >= 0:
                    body = text[text.find(":", head) + 1:].strip().lstrip('"')
                    body = body.rstrip('"}').strip()
                    return json.loads('"' + body.replace('"', '\\"') + '"') \
                        if "\\n" in body else body or None
        return text

    def _account(self, row: Mapping[str, Any], elapsed: float) -> None:
        self.calls += 1
        self.prompt_tokens += int(row.get("prompt_tokens") or 0)
        self.completion_tokens += int(row.get("completion_tokens") or 0)
        self.generation_seconds += (row.get("generation_seconds")
                                    if not row.get("cached") else 0.0) or 0.0

    def stats(self) -> Dict[str, Any]:
        return {"calls": self.calls, "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "generation_seconds": round(self.generation_seconds, 1),
                "invalid_decisions": self.invalid_decisions,
                "notes_versions": len(self.notes_versions),
                "notes_rejected": sum(1 for v in self.notes_versions
                                      if v.get("status") == "rejected"),
                "notes_truncated": sum(1 for v in self.notes_versions
                                       if v.get("status") == "truncated"),
                "log_lines": len(self.log)}


class LogReaderBelief(BeliefModel):
    """An append-only log plus the brain. ``predict`` for an object is the
    brain's decision for the current question; ``predict_readonly`` (the
    harness's per-object snapshot) is the last sighting, no LLM."""

    consumes_negative_evidence_natively = True

    def __init__(self, rng: random.Random, brain: LogReaderBrain,
                 label: Optional[str] = None) -> None:
        super().__init__(rng, floor_mass=0.0)
        self.brain = brain
        self._label = label
        self.log_loss_valid = False

    @property
    def name(self) -> str:
        return self._label or ("LogReaderNotes" if self.brain.notes_enabled
                               else "LogReader")

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        self.brain.reset(context)

    def update(self, evidence) -> None:
        self.brain.observe(evidence)
        super().update(evidence)

    def _ranked_prediction(self, ranked: Sequence[str]) -> Prediction:
        assert self._context is not None
        dist: Dict[str, float] = {}
        for r, w in zip(ranked, RANK_WEIGHTS):
            dist[r] = dist.get(r, 0.0) + w
        rest = 1.0 - sum(dist.values())
        others = [r for r in self._context.receptacle_ids if r not in dist]
        for r in others:
            dist[r] = rest / len(others) if others else 0.0
        if not others:
            total = sum(dist.values())
            dist = {r: p / total for r, p in dist.items()}
        return Prediction(distribution=dist, argmax=ranked[0])

    def _last_seen(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        if history:
            return self._ranked_prediction([history[-1][1]])
        return self._cold_start(object_id, t)

    def predict(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            # Found by a look at the question instant: answer it, no call.
            self.brain._last = {"action": "answer", "ranked": [current],
                                "found": True, "t": t, "object": object_id}
            return Prediction(distribution={current: 1.0}, argmax=current)
        decision = self.brain.decide(object_id, t)
        if decision["action"] == "answer":
            return self._ranked_prediction(decision["ranked"])
        return self._last_seen(object_id, t)

    def predict_readonly(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            return Prediction(distribution={current: 1.0}, argmax=current)
        return self._last_seen(object_id, t)

    def _predict_for_object(self, object_id: str, history, t: int
                            ) -> Prediction:
        return self._last_seen(object_id, t)


class LogReaderPolicy(DecisionPolicy):
    """Relays the brain's latest decision for the question."""

    def __init__(self, brain: LogReaderBrain) -> None:
        self.brain = brain

    @property
    def name(self) -> str:
        return "LogReaderPolicy"

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        last = self.brain._last
        if (last is None or last.get("object") != question.object_id
                or last.get("t") != question.t_query):
            return AnswerNow()
        if last["action"] == "sense" and "resident" in last:
            if 1.0 <= budget_remaining:
                self.brain.note_sense(last["resident"])
                return SensePerson(last["resident"])
            return AnswerNow()
        if last["action"] == "sense":
            target = last["receptacle"]
            if self.brain.context.sense_cost(target) <= budget_remaining:
                self.brain.note_sense(target)
                return Sense(target)
        return AnswerNow()
