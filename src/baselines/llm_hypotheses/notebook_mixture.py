"""Arm: the notebook mixture. A population of LLM agents, each owning a
notebook of beliefs about the household; every agent gives probability
forecasts, its weight is updated by how much probability it gave to what
the robot actually saw, and answers and looks come from the weighted
population.

**The notebook** (:class:`Notebook`) has two sections. BELIEFS is free
text and fixed for the life of an agent: changing it is a *fork* — a new
agent whose beliefs are a rewrite of its parent's, born with half the
parent's weight. SCRATCH MEMORY is free text the agent may rewrite at
any time. Both are capped (:data:`BELIEFS_MAX_WORDS`,
:data:`SCRATCH_MAX_WORDS`); the caps force agents to compress sightings
into patterns instead of hoarding a log. The weight is the record of
how well one fixed document predicted the house, which is why beliefs
never change in place.

**Forecasts.** Every call sees only the agent's own notebook, the
household vocabulary, the clock, the robot's room and what this
question's looks have already shown — no log of earlier questions, so
the notebook is the only memory. A *question forecast* is a
distribution over spots (receptacles plus ``ON_PERSON`` /
``OUT_OF_HOUSE``); a *look forecast*, given before a look is revealed,
is a yes/no probability per object for the target receptacle or
resident. Spots or objects an agent leaves out get :data:`P_MIN`, the
only floor there is, applied when scoring or combining and never shown
to the agent.

**Weights** move only at looks: for every agent and every known object,
``log p`` if the object was there and ``log(1 - p)`` if it was absent,
both with equal weight, then ``w *= exp(total)`` and renormalize (in
log space). Scoring empty spots is what lets a belief like "her keys
leave the house on workdays" earn weight.

**Answering and looking** (:meth:`NotebookMixtureBrain.decide`). The
mixture distribution is the weight-averaged forecast; its top spot is
the answer. Whether to look is decided by drawing two agents in
proportion to weight (Thompson sampling): agreement answers; otherwise
the first drawn agent picks the look from its top spot (a receptacle;
the carrier of ``ON_PERSON`` when this question has listed them; else
the receptacle in the carrier's room its forecast likes best), falling
through to the second agent. After a look every agent forecasts it
first, the result is revealed, weights update, and each agent gets a
follow-up in which it may rewrite its scratch memory and/or propose a
fork. The question is then re-asked from the top; the day's budget is
the only limit on looks per question.

**Population** (:class:`Population`): starts as 4 contrasting documents
written by one cold-start call; forks split the parent's weight; a cap
of :data:`POPULATION_CAP` retires the lowest-weight agent other than a
new fork; after the last question of a day the lowest-weight agent must
fork if its weight is below the equal share ``1/N``.

**Where it plugs in.** :class:`NotebookMixtureBelief` /
:class:`NotebookMixturePolicy` share one :class:`NotebookMixtureBrain`,
exactly as the log reader does: the harness commits the prediction it
computed before the final ``decide`` call, so the forecasts happen
inside the belief's ``predict`` for the question's object, and the
policy relays the brain's decision. Per-object snapshot predictions
(``predict_readonly``) never reach the LLM. All LLM calls are
sequential; only one runs at a time.

**Output**, under the arm's run folder: ``notebooks/<agent>/v1.md``
(every beliefs document, with parent and why), ``looks.jsonl``,
``forecasts.jsonl``, ``population.jsonl``, ``calls.jsonl``, and the
brain's :meth:`~NotebookMixtureBrain.diagnostics` for
``diagnostics.json``.
"""

from __future__ import annotations

import json
import math
import pathlib
import random
import time
from dataclasses import dataclass, field
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Tuple)

from baselines.beliefs.base import BeliefModel
from baselines.llm_hypotheses.prompt import away_sentences
from baselines.policies.base import DecisionPolicy
from baselines.types import (DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Action,
                             AnswerNow, EpisodeContext, Observation,
                             PersonSenseResult, Prediction, Question, Sense,
                             SensePerson, SenseResult)

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

P_MIN = 0.01
"""The one floor. A spot or object an agent leaves out of a forecast is
taken at ``P_MIN``; when scoring, every probability is read inside
``[P_MIN, 1 - P_MIN]`` so neither a confident miss (``log 0``) nor a
confident false alarm (``log(1 - 1)``) can remove an agent for ever.
Applied only when scoring or combining, never shown to the agent, and
the only correction there is: everything else stays uncorrected so
overreactions are visible."""

BELIEFS_MAX_WORDS = 1200
SCRATCH_MAX_WORDS = 800
POPULATION_CAP = 10
INITIAL_AGENTS = 4

QUESTION_FORECAST_MAX_TOKENS = 1200
LOOK_FORECAST_MAX_TOKENS = 1200
FOLLOWUP_MAX_TOKENS = 6000
FORK_MAX_TOKENS = 4000
INITIAL_MAX_TOKENS = 14000

CALL_TYPES = ("initial", "question_forecast", "look_forecast", "follow_up",
              "fork", "review")
"""``fork`` is the retry of a follow-up whose fork document broke the
beliefs cap (a condensed rewrite); ``review`` is the end-of-day forced
fork."""

# minItems 1: on the 3-day hh_001 run 19 of 491 question forecasts came
# back as "spots": [] (the why described an answer the list left out),
# which the floor turns into a uniform forecast. The grammar now asks
# for at least one entry.
_SPOT_LIST = {"type": "array", "minItems": 1, "items": {
    "type": "object",
    "properties": {"spot": {"type": "string"}, "p": {"type": "number"}},
    "required": ["spot", "p"]}}
QUESTION_FORECAST_SCHEMA = {
    "type": "object",
    "properties": {
        "spots": _SPOT_LIST,
        "carrier": {"type": "string"},
        "carrier_room": {"type": "string"},
        "why": {"type": "string"}},
    "required": ["spots", "why"],
}
LOOK_FORECAST_SCHEMA = {
    "type": "object",
    "properties": {
        "objects": {"type": "array", "items": {
            "type": "object",
            "properties": {"object": {"type": "string"},
                           "p": {"type": "number"}},
            "required": ["object", "p"]}}},
    "required": ["objects"],
}
_FORK_SCHEMA = {
    "type": "object",
    "properties": {"beliefs": {"type": "string"}, "why": {"type": "string"}},
    "required": ["beliefs", "why"],
}
FOLLOWUP_SCHEMA = {
    "type": "object",
    "properties": {"scratch": {"type": "string"}, "fork": _FORK_SCHEMA},
    "required": ["scratch"],
}
FORK_SCHEMA = _FORK_SCHEMA
INITIAL_SCHEMA = {
    "type": "object",
    "properties": {"documents": {
        "type": "array", "minItems": INITIAL_AGENTS, "maxItems": INITIAL_AGENTS,
        "items": {"type": "object",
                  "properties": {"guess": {"type": "string"},
                                 "beliefs": {"type": "string"}},
                  "required": ["guess", "beliefs"]}}},
    "required": ["documents"],
}

MISPLACEMENT_SENTENCE = ("Household objects are sometimes misplaced, "
                         "forgotten, or moved for no reason.")
"""The one thing the prompt says about the world (the brief's words)."""

SYSTEM_PROMPT = f"""You are one agent in a small population that keeps notebooks about one household on behalf of a home robot. The robot is asked, many times a day, where one object is right now, and it may spend a limited number of looks per day: a look opens one receptacle (it reveals everything inside and lists the residents in that room), or checks one resident the robot has just listed (it reveals everything they have on them).

Your notebook has two sections.
BELIEFS: your account of how this household lives and how its objects move — patterns, rules, conjectures, dependencies between objects — each with a short why that cites the evidence behind it. This section stays fixed for the life of an agent. To change it you propose a FORK: a new agent whose BELIEFS are a rewrite of yours together with a why for the change, while you keep running unchanged. BELIEFS holds at most {BELIEFS_MAX_WORDS} words, so a fork that would grow past that is written as a condensed rewrite.
SCRATCH MEMORY: free text you may add to, rewrite or trim at any time, at most {SCRATCH_MAX_WORDS} words; when it grows past that you trim it.

Your forecasts are scored by the log of the probability you gave to what the robot actually saw: an object found where you said, and equally an object absent from a spot or a spot found empty. Your weight in the population rises and falls with that score.

{MISPLACEMENT_SENTENCE}"""


def stamp(t: int) -> str:
    day, rem = divmod(int(t), DAY_SECONDS)
    return f"d{day:02d} {WEEKDAY_NAMES[day % 7]} {rem // 3600:02d}:{rem % 3600 // 60:02d}"


def word_count(text: str) -> int:
    return len(text.split())


# ------------------------------------------------------------- notebook


class NotebookError(ValueError):
    """Base of the notebook rule violations."""


class BeliefsEditRejected(NotebookError):
    """Beliefs are changed by forking, never in place."""


class ScratchTooLong(NotebookError):
    """Scratch memory over :data:`SCRATCH_MAX_WORDS`: trim it."""


class BeliefsTooLong(NotebookError):
    """A beliefs document over :data:`BELIEFS_MAX_WORDS`: fork a
    condensed rewrite."""


def check_beliefs(text: str) -> str:
    n = word_count(text)
    if n > BELIEFS_MAX_WORDS:
        raise BeliefsTooLong(f"beliefs run to {n} words; the cap is "
                             f"{BELIEFS_MAX_WORDS}")
    return text


class Notebook:
    """One agent's two sections. ``beliefs`` is read-only after
    construction (assigning raises :class:`BeliefsEditRejected`);
    ``scratch`` may be assigned freely within its cap."""

    def __init__(self, beliefs: str, scratch: str = "") -> None:
        self._beliefs = check_beliefs(beliefs)
        self._scratch = ""
        self.scratch = scratch

    @property
    def beliefs(self) -> str:
        return self._beliefs

    @beliefs.setter
    def beliefs(self, value: str) -> None:
        raise BeliefsEditRejected(
            "beliefs are changed by forking a new agent, never in place")

    @property
    def scratch(self) -> str:
        return self._scratch

    @scratch.setter
    def scratch(self, value: str) -> None:
        n = word_count(value)
        if n > SCRATCH_MAX_WORDS:
            raise ScratchTooLong(f"scratch memory runs to {n} words; the cap "
                                 f"is {SCRATCH_MAX_WORDS}")
        self._scratch = value

    def render(self) -> str:
        return (f"## BELIEFS\n{self.beliefs.strip() or '(empty)'}\n\n"
                f"## SCRATCH MEMORY\n{self.scratch.strip() or '(empty)'}")


# ----------------------------------------------------------- population


@dataclass
class NotebookAgent:
    agent_id: str
    notebook: Notebook
    parent_id: Optional[str]
    why: str
    guess: str
    generation: int
    born_t: int
    log_weight: float = 0.0
    retired_t: Optional[int] = None
    retired_reason: str = ""
    n_forks: int = 0

    @property
    def live(self) -> bool:
        return self.retired_t is None


def _normalize_log(values: Mapping[str, float]) -> Dict[str, float]:
    m = max(values.values())
    z = m + math.log(sum(math.exp(v - m) for v in values.values()))
    return {k: v - z for k, v in values.items()}


class Population:
    """The live agents, their weights (kept normalized in log space) and
    the fork / cap / review rules. No LLM in here; the brain feeds it
    documents and scores."""

    def __init__(self, cap: int = POPULATION_CAP) -> None:
        self.cap = cap
        self.agents: Dict[str, NotebookAgent] = {}
        self.retired: Dict[str, NotebookAgent] = {}
        self._n = 0
        self.events: List[Dict[str, Any]] = []
        self.n_forks = 0
        self.n_retirements = 0

    # ---------------------------------------------------------- reading

    @property
    def size(self) -> int:
        return len(self.agents)

    @property
    def weights(self) -> Dict[str, float]:
        return {a: math.exp(ag.log_weight) for a, ag in self.agents.items()}

    def rank(self, agent_id: str) -> int:
        """1-based rank by weight (1 = heaviest)."""
        order = sorted(self.agents, key=lambda a: -self.agents[a].log_weight)
        return order.index(agent_id) + 1

    def lowest(self) -> str:
        return min(self.agents, key=lambda a: self.agents[a].log_weight)

    def review_candidate(self) -> Optional[str]:
        """The agent an end-of-day review must fork: the lowest-weight
        one, when its weight is below the equal share ``1/N``."""
        if not self.agents:
            return None
        low = self.lowest()
        if self.agents[low].log_weight < -math.log(self.size):
            return low
        return None

    # ---------------------------------------------------------- writing

    def _new_id(self) -> str:
        self._n += 1
        return f"a{self._n:02d}"

    def _renormalize(self) -> None:
        if not self.agents:
            return
        for a, lw in _normalize_log(
                {a: ag.log_weight for a, ag in self.agents.items()}).items():
            self.agents[a].log_weight = lw

    def _event(self, t: int, kind: str, **fields: Any) -> None:
        self.events.append({"t": t, "event": kind, **fields,
                            "weights": {a: round(w, 6)
                                        for a, w in self.weights.items()}})

    def add_initial(self, documents: Sequence[Tuple[str, str]],
                    t: int) -> List[NotebookAgent]:
        """The cold-start agents: ``(guess, beliefs)`` each, equal
        weight, empty scratch memory."""
        born = []
        for guess, beliefs in documents:
            agent = NotebookAgent(self._new_id(), Notebook(beliefs), None, "",
                                  guess, 1, t)
            self.agents[agent.agent_id] = agent
            born.append(agent)
        self._renormalize()
        for agent in born:
            self._event(t, "birth", agent=agent.agent_id, guess=agent.guess)
        return born

    def update_log_weights(self, scores: Mapping[str, float], t: int,
                           target: str) -> Dict[str, float]:
        """Add each live agent's look score to its log weight and
        renormalize. Returns the weights after."""
        for a, s in scores.items():
            if a in self.agents:
                self.agents[a].log_weight += s
        self._renormalize()
        self._event(t, "look_update", target=target,
                    scores={a: round(s, 4) for a, s in scores.items()})
        return self.weights

    def fork(self, parent_id: str, beliefs: str, why: str, t: int
             ) -> Tuple[NotebookAgent, Optional[NotebookAgent]]:
        """A new agent with ``beliefs`` and a copy of the parent's
        scratch memory; the parent's weight is split in half between the
        two, nobody else moves. Over the cap, the lowest-weight agent
        other than the fork is retired. Raises :class:`BeliefsTooLong`
        (the caller asks for a condensed rewrite)."""
        parent = self.agents[parent_id]
        notebook = Notebook(beliefs, parent.notebook.scratch)
        child = NotebookAgent(self._new_id(), notebook, parent_id, why,
                              parent.guess, parent.generation + 1, t)
        parent.log_weight -= math.log(2.0)
        child.log_weight = parent.log_weight
        parent.n_forks += 1
        self.agents[child.agent_id] = child
        self.n_forks += 1
        self._event(t, "fork", agent=child.agent_id, parent=parent_id, why=why)
        retired = None
        if self.size > self.cap:
            victim = min((a for a in self.agents if a != child.agent_id),
                         key=lambda a: self.agents[a].log_weight)
            retired = self.retire(victim, t, "population cap")
        return child, retired

    def retire(self, agent_id: str, t: int, reason: str) -> NotebookAgent:
        agent = self.agents.pop(agent_id)
        agent.retired_t = t
        agent.retired_reason = reason
        self.retired[agent_id] = agent
        self.n_retirements += 1
        self._renormalize()
        self._event(t, "retire", agent=agent_id, reason=reason)
        return agent


# -------------------------------------------------------------- scoring


def clip_p(p: float) -> float:
    return min(max(float(p), P_MIN), 1.0 - P_MIN)


def look_score(forecast: Mapping[str, float], contents: Iterable[str],
               objects: Iterable[str]) -> float:
    """One agent's score for one look: over every known object, ``log
    p`` if it was there and ``log(1 - p)`` if it was absent, ``p`` the
    agent's yes/no probability (an object left out counts at
    :data:`P_MIN`; every ``p`` is read inside ``[P_MIN, 1 - P_MIN]``)."""
    present = set(contents)
    total = 0.0
    for obj in objects:
        p = clip_p(forecast.get(obj, P_MIN))
        total += math.log(p) if obj in present else math.log(1.0 - p)
    return total


def normalize_question_forecast(spots: Mapping[str, float],
                                all_spots: Sequence[str]) -> Dict[str, float]:
    """An agent's question forecast as a distribution over every spot: a
    spot left out (or given a non-positive value) gets :data:`P_MIN`,
    then everything is renormalized to sum to 1."""
    raw = {s: (float(spots[s]) if s in spots and float(spots[s]) > 0.0
               else P_MIN) for s in all_spots}
    z = sum(raw.values())
    return {s: v / z for s, v in raw.items()}


def argmax_spot(dist: Mapping[str, float], order: Sequence[str]) -> str:
    """The top spot; exact ties go to the earlier spot in ``order``."""
    return max(order, key=lambda s: (dist.get(s, 0.0), -order.index(s)))


# ---------------------------------------------------------------- brain


class NotebookMixtureBrain:
    """The population, its notebooks, and every LLM call.

    ``client`` has the ``generate(system, user, seed, temperature,
    max_tokens, reasoning_effort=..., schema=...)`` interface of
    :class:`~baselines.llm_hypotheses.elicit.CachedThinkingClient`; a
    stub with the same signature serves the tests. ``omap`` / ``rmap``
    / ``cmap`` are the anonymization maps (empty when named); prompts
    are written in the model's vocabulary and every id coming back is
    translated to a real id.
    """

    def __init__(self, client: Any,
                 omap: Optional[Mapping[str, str]] = None,
                 rmap: Optional[Mapping[str, str]] = None,
                 cmap: Optional[Mapping[str, str]] = None,
                 log_dir: Optional[pathlib.Path] = None,
                 temperature: float = 0.2, seed: int = 5,
                 cap: int = POPULATION_CAP) -> None:
        self.client = client
        self._omap = dict(omap or {})
        self._rmap = dict(rmap or {})
        self._cmap = dict(cmap or {})
        self._rev_o = {v: k for k, v in self._omap.items()}
        self._rev_r = {v: k for k, v in self._rmap.items()}
        self._log_dir = pathlib.Path(log_dir) if log_dir else None
        self._temperature = temperature
        self._seed = seed
        self._cap = cap
        self._rng = random.Random(seed)
        self.reset(None)

    # ---------------------------------------------------------- lifecycle

    def reset(self, context: Optional[EpisodeContext]) -> None:
        self.context = context
        self.population = Population(self._cap)
        self.objects: Dict[str, str] = dict(context.object_classes) if context else {}
        self.spent_today = 0.0
        self.day = -1
        self.calls = 0
        self.call_totals: Dict[str, Dict[str, float]] = {
            k: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "seconds": 0.0} for k in CALL_TYPES}
        self.calls_per_day: Dict[int, Dict[str, Dict[str, float]]] = {}
        self.budget_exhausted_at: Dict[int, Optional[str]] = {}
        self.population_size_per_day: Dict[int, int] = {}
        self.invalid_forecasts = 0
        self.scratch_truncated = 0
        self.forks_rejected = 0
        self.reviews_failed = 0
        self.n_looks = 0
        self.n_question_rounds = 0
        self.decisions: List[Dict[str, Any]] = []
        self._question_key: Optional[Tuple[str, int]] = None
        self._sensed_this_question: List[str] = []
        self._listed_this_question: Dict[str, Optional[str]] = {}
        self._seen_lines: List[str] = []           # this question's results
        self._pending_look: Optional[Dict[str, Any]] = None
        self._last: Optional[Dict[str, Any]] = None
        self._finished = False
        if self._log_dir:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            (self._log_dir / "notebooks").mkdir(exist_ok=True)

    def finish(self, t: Optional[int] = None) -> None:
        """After the episode: the last day's review and the final
        notebooks. Idempotent."""
        if self._finished:
            return
        self._finished = True
        if self.day >= 0:
            self._end_of_day_review(self.day)
        self._write_final_notebooks()

    # ------------------------------------------------------------- naming

    def obj(self, real: str) -> str:
        return self._omap.get(real, real)

    def rec(self, real: str) -> str:
        return self._rmap.get(real, real)

    def real_obj(self, token: str) -> str:
        return self._rev_o.get(token, token)

    def real_rec(self, token: str) -> str:
        return self._rev_r.get(token, token)

    def _person_sensing(self) -> bool:
        return bool(self.context is not None and self.context.person_sensing)

    def _spots(self) -> Tuple[str, ...]:
        assert self.context is not None
        return tuple(self.context.receptacle_ids)

    def _known_objects(self) -> List[str]:
        return sorted(self.objects)

    def _remaining(self) -> float:
        assert self.context is not None
        return max(0.0, self.context.budget_per_day - self.spent_today)

    # ------------------------------------------------------------- prompt

    def _household_block(self) -> str:
        assert self.context is not None
        ctx = self.context
        rooms = ctx.receptacle_rooms or {}
        by_room: Dict[str, List[str]] = {}
        for r in ctx.receptacle_ids:
            if r in (ON_PERSON, OUT_OF_HOUSE):
                continue
            by_room.setdefault(rooms.get(r, "(no room)"), []).append(self.rec(r))
        room_lines = [f"  {room}: {', '.join(recs)}"
                      for room, recs in by_room.items()]
        objects = [f"  {self.obj(o)} ({self._cmap.get(c, c)})"
                   for o, c in sorted(self.objects.items())]
        text = (f"HOUSEHOLD\nOBJECTS (id (class)):\n{chr(10).join(objects)}\n\n"
                f"ROOMS AND RECEPTACLES:\n{chr(10).join(room_lines)}\n"
                f"Answer spots are every receptacle above plus "
                f"{self.rec(ON_PERSON)} and {self.rec(OUT_OF_HOUSE)}. "
                f"{away_sentences(self._rmap).replace('`', '')}")
        if ctx.resident_ids:
            text += ("\n\nRESIDENTS: "
                     + ", ".join(self.rec(r) for r in ctx.resident_ids))
        text += (f"\n\nLOOK BUDGET: {ctx.budget_per_day} looks per day, "
                 f"reset at midnight.")
        return text

    def _notebook_block(self, agent: NotebookAgent) -> str:
        return f"YOUR NOTEBOOK (agent {agent.agent_id})\n{agent.notebook.render()}"

    def _now_block(self, t: int) -> str:
        assert self.context is not None
        room = self.context.robot_position.room
        text = f"NOW: {stamp(t)}. The robot is in {room or 'an unknown room'}."
        text += f" Looks left today: {self._remaining():g}."
        if self._seen_lines:
            text += ("\nSEEN SO FAR ON THIS QUESTION:\n"
                     + "\n".join(f"  {line}" for line in self._seen_lines))
        else:
            text += "\nSEEN SO FAR ON THIS QUESTION: nothing yet."
        return text

    def _question_request(self, object_id: str) -> str:
        return (f"REQUEST: where is {self.obj(object_id)} right now? Give a "
                f"probability for every spot you consider possible — "
                f"receptacles, {self.rec(ON_PERSON)}, {self.rec(OUT_OF_HOUSE)} "
                f"— summing to 1; spots you leave out are taken as very "
                f"unlikely. If {self.rec(ON_PERSON)} gets any probability, "
                f"also give carrier (the resident id) and carrier_room (the "
                f"room you think that resident is in now). One sentence why. "
                f"Use ids exactly as listed.")

    def _look_request(self, look: Mapping[str, Any]) -> str:
        if "resident" in look:
            target = (f"resident {self.rec(look['resident'])} "
                      f"(in {look.get('room') or 'a room seen this question'})")
        else:
            target = (f"receptacle {self.rec(look['receptacle'])} "
                      f"(in {look.get('room') or 'its room'})")
        return (f"REQUEST: the robot is about to look at {target}. For every "
                f"object you think is there right now, give the probability "
                f"that it is there — each object is its own yes/no "
                f"probability. Objects you leave out are taken as very "
                f"unlikely to be there. Use ids exactly as listed.")

    # ---------------------------------------------------------------- LLM

    def _call(self, call_type: str, agent_id: Optional[str], user: str,
              schema: Mapping[str, Any], max_tokens: int, t: int,
              seed_offset: int = 0) -> Tuple[Optional[Dict[str, Any]],
                                             Dict[str, Any]]:
        """One sequential LLM call. Returns ``(parsed JSON or None,
        row)`` and accounts it under ``call_type`` and the day."""
        started = time.monotonic()
        row = self.client.generate(SYSTEM_PROMPT, user,
                                   seed=self._seed + seed_offset,
                                   temperature=self._temperature,
                                   max_tokens=max_tokens, schema=schema)
        elapsed = time.monotonic() - started
        seconds = ((row.get("generation_seconds") or 0.0) if row.get("cached")
                   else elapsed)
        self.calls += 1
        tot = self.call_totals[call_type]
        tot["calls"] += 1
        tot["prompt_tokens"] += int(row.get("prompt_tokens") or 0)
        tot["completion_tokens"] += int(row.get("completion_tokens") or 0)
        tot["seconds"] += seconds
        day = t // DAY_SECONDS
        per_day = self.calls_per_day.setdefault(day, {}).setdefault(
            call_type, {"calls": 0, "prompt_tokens": 0,
                        "completion_tokens": 0, "seconds": 0.0})
        per_day["calls"] += 1
        per_day["prompt_tokens"] += int(row.get("prompt_tokens") or 0)
        per_day["completion_tokens"] += int(row.get("completion_tokens") or 0)
        per_day["seconds"] += seconds
        try:
            parsed = json.loads(row.get("payload") or "")
        except (json.JSONDecodeError, TypeError):
            parsed = None
        if not isinstance(parsed, dict):
            parsed = None
        entry = {"n": self.calls, "t": t, "stamp": stamp(t), "day": day,
                 "type": call_type, "agent": agent_id,
                 "prompt_tokens": row.get("prompt_tokens"),
                 "completion_tokens": row.get("completion_tokens"),
                 "seconds": round(seconds, 2), "cached": bool(row.get("cached")),
                 "finish_reason": row.get("finish_reason"),
                 "parsed": parsed is not None, "prompt_chars": len(user)}
        if self._log_dir:
            with open(self._log_dir / "calls.jsonl", "a") as fh:
                fh.write(json.dumps(entry) + "\n")
            n_type = int(tot["calls"])
            if n_type <= 2 or self.calls % 200 == 0:
                (self._log_dir / f"prompt_{self.calls:05d}_{call_type}.md"
                 ).write_text(f"# call {self.calls} ({call_type}, agent "
                              f"{agent_id}) at {stamp(t)}\n\n## system\n\n"
                              f"{SYSTEM_PROMPT}\n\n## user\n\n{user}\n\n"
                              f"## reply\n\n{row.get('payload')}\n")
        return parsed, row

    # ----------------------------------------------------------- lifecycle

    def _ensure_started(self, t: int) -> None:
        if self.population.size or self.population.retired:
            return
        self._initial_call(t)

    def _initial_call(self, t: int) -> None:
        """Cold start: one call writes the contrasting starting
        documents, each a guess about how the household lives."""
        start = (t // DAY_SECONDS) * DAY_SECONDS
        user = "\n\n".join([
            self._household_block(),
            f"START: {stamp(start)}. The robot has just been installed and "
            f"has seen nothing yet.",
            f"Write {INITIAL_AGENTS} contrasting starting BELIEFS documents, "
            f"each built on a different guess about how this household "
            f"lives. Each becomes one agent's BELIEFS section (at most "
            f"{BELIEFS_MAX_WORDS} words each). Reply as JSON: "
            f'{{"documents": [{{"guess": "...", "beliefs": "..."}}, ...]}} '
            f"with exactly {INITIAL_AGENTS} entries."])
        docs: List[Tuple[str, str]] = []
        for attempt in range(3):
            parsed, _ = self._call("initial", None, user, INITIAL_SCHEMA,
                                   INITIAL_MAX_TOKENS, t, seed_offset=attempt)
            docs = []
            for d in (parsed or {}).get("documents", []) or []:
                if isinstance(d, dict) and str(d.get("beliefs", "")).strip():
                    beliefs = str(d["beliefs"])
                    if word_count(beliefs) > BELIEFS_MAX_WORDS:
                        beliefs = " ".join(beliefs.split()[:BELIEFS_MAX_WORDS])
                    docs.append((str(d.get("guess", ""))[:300], beliefs))
            if len(docs) >= INITIAL_AGENTS:
                docs = docs[:INITIAL_AGENTS]
                break
        if not docs:
            # A model that produced nothing usable still gets a
            # population: blank, equal documents. They cannot separate,
            # and the run's diagnostics say so.
            docs = [("(initial call produced no document)", "")
                    for _ in range(INITIAL_AGENTS)]
        for agent in self.population.add_initial(docs, t):
            self._write_notebook(agent)
        self._flush_population_events()

    def _new_day(self, t: int) -> None:
        day = t // DAY_SECONDS
        if day == self.day:
            return
        if self.day >= 0:
            self._end_of_day_review(self.day)
        self.day = day
        self.spent_today = 0.0
        self.budget_exhausted_at.setdefault(day, None)

    # ----------------------------------------------------------- forecasts

    def _question_forecasts(self, object_id: str, t: int
                            ) -> Dict[str, Dict[str, Any]]:
        """One call per live agent. Each entry: ``dist`` over every spot
        (real ids, floored and renormalized), ``top``, ``carrier``,
        ``carrier_room``, ``why``, ``raw`` (the spots as given)."""
        spots = self._spots()
        out: Dict[str, Dict[str, Any]] = {}
        for agent_id in list(self.population.agents):
            agent = self.population.agents[agent_id]
            user = "\n\n".join([self._household_block(),
                                self._notebook_block(agent),
                                self._now_block(t),
                                self._question_request(object_id)])
            parsed, _ = self._call("question_forecast", agent_id, user,
                                   QUESTION_FORECAST_SCHEMA,
                                   QUESTION_FORECAST_MAX_TOKENS, t)
            given: Dict[str, float] = {}
            for item in (parsed or {}).get("spots", []) or []:
                if not isinstance(item, dict):
                    continue
                spot = self.real_rec(str(item.get("spot", "")))
                try:
                    p = float(item.get("p", 0.0))
                except (TypeError, ValueError):
                    continue
                if spot in spots and p > 0:
                    given[spot] = given.get(spot, 0.0) + p
            if not given:
                self.invalid_forecasts += 1
            dist = normalize_question_forecast(given, spots)
            carrier = self.real_rec(str((parsed or {}).get("carrier") or ""))
            out[agent_id] = {
                "dist": dist, "top": argmax_spot(dist, spots),
                "carrier": carrier if carrier in (self.context.resident_ids
                                                  if self.context else ())
                else None,
                "carrier_room": str((parsed or {}).get("carrier_room") or "")
                or None,
                "why": str((parsed or {}).get("why", ""))[:400],
                "raw": {s: round(p, 4) for s, p in given.items()},
                "invalid": not given}
        return out

    def _look_forecasts(self, look: Mapping[str, Any], t: int
                        ) -> Dict[str, Dict[str, float]]:
        """One call per live agent, before the look is revealed:
        ``agent -> {real object: p}`` (objects left out are absent)."""
        out: Dict[str, Dict[str, float]] = {}
        for agent_id in list(self.population.agents):
            agent = self.population.agents[agent_id]
            user = "\n\n".join([self._household_block(),
                                self._notebook_block(agent),
                                self._now_block(t),
                                self._look_request(look)])
            parsed, _ = self._call("look_forecast", agent_id, user,
                                   LOOK_FORECAST_SCHEMA,
                                   LOOK_FORECAST_MAX_TOKENS, t)
            given: Dict[str, float] = {}
            for item in (parsed or {}).get("objects", []) or []:
                if not isinstance(item, dict):
                    continue
                o = self.real_obj(str(item.get("object", "")))
                try:
                    p = float(item.get("p", 0.0))
                except (TypeError, ValueError):
                    continue
                if o in self.objects:
                    given[o] = p
            if parsed is None:
                self.invalid_forecasts += 1
            out[agent_id] = given
        return out

    # ------------------------------------------------------------ decide

    def decide(self, object_id: str, t: int) -> Dict[str, Any]:
        """One round for the current question state: every agent's
        question forecast, the mixture, and the look decision. Returns
        ``{"distribution", "argmax", "action": "answer" |
        "sense", ["receptacle" | "resident"]}``."""
        assert self.context is not None
        self._new_day(t)
        self._ensure_started(t)
        # after the cold start, so day 0 reads 4 rather than 0
        self.population_size_per_day.setdefault(self.day, self.population.size)
        if object_id not in self.objects:
            self.objects[object_id] = ""
        key = (object_id, t)
        if key != self._question_key:
            self._question_key = key
            self._sensed_this_question = []
            self._listed_this_question = {}
            self._seen_lines = []
            self._pending_look = None
        self.n_question_rounds += 1
        forecasts = self._question_forecasts(object_id, t)
        spots = self._spots()
        weights = self.population.weights
        mixture = {s: sum(weights[a] * f["dist"][s] for a, f in forecasts.items())
                   for s in spots}
        z = sum(mixture.values()) or 1.0
        mixture = {s: p / z for s, p in mixture.items()}
        answer = argmax_spot(mixture, spots)
        decision: Dict[str, Any] = {
            "t": t, "object": object_id, "distribution": mixture,
            "argmax": answer, "action": "answer", "round": self.n_question_rounds,
            "n_sensed": len(self._sensed_this_question)}
        remaining = self._remaining()
        if remaining < 1.0:
            decision["reason"] = "no budget"
        else:
            ids = list(forecasts)
            draw = self._rng.choices(ids, weights=[weights[a] for a in ids], k=2)
            decision["draw"] = draw
            decision["draw_tops"] = [forecasts[a]["top"] for a in draw]
            if forecasts[draw[0]]["top"] == forecasts[draw[1]]["top"]:
                decision["reason"] = "agreement"
            else:
                for agent_id in draw:
                    look = self.choose_look(forecasts[agent_id])
                    if look is not None:
                        decision.update(look)
                        decision["action"] = "sense"
                        decision["reason"] = f"disagreement; look by {agent_id}"
                        decision["look_by"] = agent_id
                        break
                else:
                    decision["reason"] = "disagreement; no legal look"
        self._last = decision
        self.decisions.append({k: v for k, v in decision.items()
                               if k != "distribution"})
        self._write_row("forecasts.jsonl", {
            "t": t, "stamp": stamp(t), "object": object_id,
            "round": self.n_question_rounds,
            "n_sensed": len(self._sensed_this_question),
            "weights": {a: round(w, 6) for a, w in weights.items()},
            "forecasts": {a: {"spots": f["raw"], "top": f["top"],
                              "carrier": f["carrier"],
                              "carrier_room": f["carrier_room"],
                              "why": f["why"], "invalid": f["invalid"]}
                          for a, f in forecasts.items()},
            "mixture": {s: round(p, 6) for s, p in mixture.items() if p > 1e-6},
            "answer": answer, "action": decision["action"],
            "reason": decision.get("reason"), "draw": decision.get("draw"),
            "look": {k: decision[k] for k in ("receptacle", "resident")
                     if k in decision}})
        return decision

    def choose_look(self, forecast: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """The look one drawn agent picks from its top spot, or None when
        nothing legal follows from it (the caller tries the next agent).

        * a receptacle the robot has yet to look at this question, that
          the budget covers -> that receptacle;
        * ``ON_PERSON`` with its carrier listed in the robot's current
          room this question and not yet looked at -> that resident;
        * ``ON_PERSON`` with the carrier not located this question ->
          the receptacle in ``carrier_room`` the agent's own forecast
          likes best (the look lists who is in that room);
        * ``OUT_OF_HOUSE``, or anything else -> None.
        """
        assert self.context is not None
        ctx = self.context
        remaining = self._remaining()
        sensable = [r for r in ctx.sensable_receptacle_ids
                    if r not in self._sensed_this_question]
        top = forecast["top"]
        if top in sensable and ctx.sense_cost(top) <= remaining:
            return {"receptacle": top, "room": ctx.receptacle_rooms.get(top)}
        if top == ON_PERSON and self._person_sensing():
            carrier = forecast.get("carrier")
            if (carrier in self._listed_this_question
                    and carrier not in self._sensed_this_question
                    and 1.0 <= remaining):
                return {"resident": carrier,
                        "room": self._listed_this_question[carrier]}
            room = forecast.get("carrier_room")
            in_room = [r for r in sensable
                       if ctx.receptacle_rooms.get(r) == room
                       and ctx.sense_cost(r) <= remaining]
            if in_room:
                dist = forecast["dist"]
                best = argmax_spot({r: dist.get(r, 0.0) for r in in_room},
                                   in_room)
                return {"receptacle": best, "room": room}
        return None

    # -------------------------------------------------------------- looks

    def note_sense(self, target: str) -> None:
        """The policy is about to look at ``target`` (a receptacle or a
        listed resident): every agent forecasts it BEFORE the result is
        revealed, and the look is accounted against today's budget."""
        assert self.context is not None
        t = self._question_key[1] if self._question_key else 0
        if target in self._listed_this_question:
            look: Dict[str, Any] = {"resident": target,
                                    "room": self._listed_this_question[target]}
            self.spent_today += 1.0
        else:
            look = {"receptacle": target,
                    "room": self.context.receptacle_rooms.get(target)}
            self.spent_today += self.context.sense_cost(target)
        self._sensed_this_question.append(target)
        if self._remaining() < 1.0 and self.budget_exhausted_at.get(self.day) is None:
            self.budget_exhausted_at[self.day] = stamp(t)
        look["t"] = t
        look["forecasts"] = self._look_forecasts(look, t)
        look["weights_before"] = self.population.weights
        self._pending_look = look

    def observe(self, evidence: Any) -> None:
        """Evidence arrives. The result of the pending look runs the
        look procedure (score, weight update, follow-ups); any other
        evidence (an ambient stream, on banks that have one) is only
        recorded for this question's prompts — weights change at looks
        alone."""
        if isinstance(evidence, Observation):
            self.objects.setdefault(evidence.object_id, evidence.object_class)
            return
        for o in evidence.contents:
            self.objects.setdefault(o, evidence.object_classes.get(o, ""))
        t = evidence.t
        contents = tuple(evidence.contents)
        inside = ", ".join(self.obj(o) for o in contents) or "(nothing)"
        if isinstance(evidence, PersonSenseResult):
            target = evidence.resident_id
            room = evidence.room
            line = (f"{stamp(t)} look at resident {self.rec(target)}"
                    f"{f' in {room}' if room else ''}: {inside}")
            listed: Tuple[str, ...] = ()
        else:
            target = evidence.receptacle_id
            room = (self.context.receptacle_rooms or {}).get(target) \
                if self.context else None
            line = f"{stamp(t)} look at {self.rec(target)}: {inside}"
            listed = tuple(evidence.residents_present)
            if self._person_sensing():
                who = ", ".join(self.rec(r) for r in listed) or "nobody"
                line += f"; residents here: {who}"
            if self._question_key is not None and t == self._question_key[1]:
                for r in listed:
                    self._listed_this_question[r] = room
        if self._question_key is not None and t == self._question_key[1]:
            self._seen_lines.append(line)
        pending = self._pending_look
        self._pending_look = None
        if pending is None or pending.get(
                "resident" if isinstance(evidence, PersonSenseResult)
                else "receptacle") != target:
            return
        self._look_procedure(pending, target, room, contents, listed, line, t)

    def _look_procedure(self, look: Dict[str, Any], target: str,
                        room: Optional[str], contents: Tuple[str, ...],
                        listed: Tuple[str, ...], line: str, t: int) -> None:
        objects = self._known_objects()
        forecasts: Dict[str, Dict[str, float]] = look["forecasts"]
        scores = {a: look_score(f, contents, objects)
                  for a, f in forecasts.items()}
        before = look["weights_before"]
        after = self.population.update_log_weights(scores, t, target)
        self.n_looks += 1
        self._write_row("looks.jsonl", {
            "t": t, "stamp": stamp(t), "n": self.n_looks,
            "target": target,
            "kind": "resident" if "resident" in look else "receptacle",
            "room": room, "result": list(contents),
            "residents_listed": list(listed),
            "forecasts": {a: {o: round(p, 4) for o, p in f.items()}
                          for a, f in forecasts.items()},
            "scores": {a: round(s, 4) for a, s in scores.items()},
            "weights_before": {a: round(w, 6) for a, w in before.items()},
            "weights_after": {a: round(w, 6) for a, w in after.items()}})
        self._flush_population_events()
        # Follow-ups, one per agent alive at the look (forks born in this
        # round get no follow-up of their own).
        for agent_id in list(forecasts):
            if agent_id in self.population.agents:
                self._follow_up(agent_id, look, line, forecasts[agent_id],
                                scores[agent_id], t)
        self._flush_population_events()

    def _follow_up(self, agent_id: str, look: Mapping[str, Any], line: str,
                   forecast: Mapping[str, float], score: float, t: int) -> None:
        agent = self.population.agents[agent_id]
        given = ", ".join(f"{self.obj(o)} {p:.2f}" for o, p in forecast.items()) \
            or "(nothing listed)"
        w = self.population.weights[agent_id]
        rank = self.population.rank(agent_id)
        user = "\n\n".join([
            self._household_block(), self._notebook_block(agent),
            f"RESULT OF THE LOOK\n{line}\n"
            f"YOUR FORECAST: {given}; everything else left out.\n"
            f"YOUR SCORE for this look: {score:.2f} (over every object, "
            f"log p for what was there and log(1 - p) for what was absent).\n"
            f"YOUR WEIGHT is now {w:.3f}, rank {rank} of "
            f"{self.population.size}.",
            f"You may rewrite your SCRATCH MEMORY (return its full new text; "
            f"return the current text to keep it as is), and you may propose "
            f"a FORK (new BELIEFS as a complete rewrite of yours, plus why). "
            f"Reply as JSON: {{\"scratch\": \"...\", \"fork\": {{\"beliefs\": "
            f"\"...\", \"why\": \"...\"}}}}; leave fork out to keep your "
            f"beliefs as they are."])
        parsed, _ = self._call("follow_up", agent_id, user, FOLLOWUP_SCHEMA,
                               FOLLOWUP_MAX_TOKENS, t)
        if parsed is None:
            return
        self._apply_scratch(agent, str(parsed.get("scratch", "")), user, t)
        fork = parsed.get("fork")
        if isinstance(fork, dict) and str(fork.get("beliefs", "")).strip():
            self._apply_fork(agent_id, str(fork["beliefs"]),
                             str(fork.get("why", "")), t, "follow_up")

    def _apply_scratch(self, agent: NotebookAgent, text: str, user: str,
                       t: int) -> None:
        """Set the scratch memory; over the cap, one retry asks for a
        trimmed version, and a second overflow is cut at the cap."""
        try:
            agent.notebook.scratch = text
            return
        except ScratchTooLong:
            pass
        retry = (user + f"\n\nYour scratch memory came to {word_count(text)} "
                 f"words; the cap is {SCRATCH_MAX_WORDS}. Return it trimmed "
                 f"to fit, as JSON {{\"scratch\": \"...\"}}.")
        parsed, _ = self._call("follow_up", agent.agent_id, retry,
                               {"type": "object",
                                "properties": {"scratch": {"type": "string"}},
                                "required": ["scratch"]},
                               FOLLOWUP_MAX_TOKENS, t, seed_offset=1)
        trimmed = str((parsed or {}).get("scratch", text))
        try:
            agent.notebook.scratch = trimmed
        except ScratchTooLong:
            agent.notebook.scratch = " ".join(trimmed.split()[:SCRATCH_MAX_WORDS])
            self.scratch_truncated += 1

    def _apply_fork(self, parent_id: str, beliefs: str, why: str, t: int,
                    origin: str) -> Optional[NotebookAgent]:
        """Fork ``parent_id``; over the beliefs cap, one retry asks for a
        condensed rewrite, and a second overflow rejects the fork."""
        for attempt in range(2):
            try:
                child, retired = self.population.fork(parent_id, beliefs, why, t)
            except BeliefsTooLong:
                if attempt == 1:
                    self.forks_rejected += 1
                    self.population.events.append(
                        {"t": t, "event": "fork_rejected", "parent": parent_id,
                         "reason": f"beliefs over {BELIEFS_MAX_WORDS} words "
                                   f"twice", "origin": origin})
                    return None
                parent = self.population.agents[parent_id]
                user = "\n\n".join([
                    self._household_block(), self._notebook_block(parent),
                    f"YOUR PROPOSED FORK ({word_count(beliefs)} words):\n"
                    f"{beliefs}\n\nWHY: {why}",
                    f"BELIEFS holds at most {BELIEFS_MAX_WORDS} words. Write "
                    f"the fork again as a condensed rewrite that fits, with "
                    f"the same why. Reply as JSON: {{\"beliefs\": \"...\", "
                    f"\"why\": \"...\"}}."])
                parsed, _ = self._call("fork", parent_id, user, FORK_SCHEMA,
                                       FORK_MAX_TOKENS, t, seed_offset=1)
                beliefs = str((parsed or {}).get("beliefs", beliefs))
                why = str((parsed or {}).get("why", why))
                continue
            child.why = f"[{origin}] {why}".strip()
            self._write_notebook(child)
            if retired is not None:
                self._write_final_notebook(retired)
            return child
        return None

    # ------------------------------------------------------------- review

    def _end_of_day_review(self, day: int) -> None:
        """After the day's last question: the lowest-weight agent must
        fork if its weight is below the equal share."""
        t = (day + 1) * DAY_SECONDS - 1
        candidate = self.population.review_candidate()
        n = self.population.size
        self.population.events.append({
            "t": t, "event": "review", "day": day, "population": n,
            "candidate": candidate,
            "weights": {a: round(w, 6)
                        for a, w in self.population.weights.items()}})
        if candidate is None:
            self._flush_population_events()
            return
        agent = self.population.agents[candidate]
        w = self.population.weights[candidate]
        user = "\n\n".join([
            self._household_block(), self._notebook_block(agent),
            f"END OF DAY {stamp(t)[:3]} REVIEW. Your weight is {w:.3f}, the "
            f"lowest of {n} agents; the equal share is {1.0 / n:.3f}. Propose a "
            f"fork: new BELIEFS as a complete rewrite of yours, and why. Reply "
            f"as JSON: {{\"beliefs\": \"...\", \"why\": \"...\"}}."])
        child = None
        for attempt in range(2):
            parsed, _ = self._call("review", candidate, user, FORK_SCHEMA,
                                   FORK_MAX_TOKENS, t, seed_offset=attempt)
            beliefs = str((parsed or {}).get("beliefs", "")).strip()
            if not beliefs:
                continue
            child = self._apply_fork(candidate, beliefs,
                                     str((parsed or {}).get("why", "")), t,
                                     "review")
            if child is not None:
                break
        if child is None:
            self.reviews_failed += 1
            self.population.events.append(
                {"t": t, "event": "review_failed", "agent": candidate})
        self._flush_population_events()

    # ------------------------------------------------------------- output

    def _write_row(self, name: str, row: Mapping[str, Any]) -> None:
        if not self._log_dir:
            return
        with open(self._log_dir / name, "a") as fh:
            fh.write(json.dumps(row) + "\n")

    def _flush_population_events(self) -> None:
        if not self._log_dir:
            return
        events, self.population.events = self.population.events, []
        if events:
            with open(self._log_dir / "population.jsonl", "a") as fh:
                for e in events:
                    fh.write(json.dumps(e) + "\n")

    def _write_notebook(self, agent: NotebookAgent) -> None:
        if not self._log_dir:
            return
        d = self._log_dir / "notebooks" / agent.agent_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "v1.md").write_text(
            f"# {agent.agent_id} — beliefs\n\n"
            f"- parent: {agent.parent_id or '(cold start)'}\n"
            f"- generation: {agent.generation}\n"
            f"- born: {stamp(agent.born_t)}\n"
            f"- guess: {agent.guess}\n"
            f"- why: {agent.why or '(initial document)'}\n\n"
            f"{agent.notebook.beliefs}\n")

    def _write_final_notebook(self, agent: NotebookAgent) -> None:
        if not self._log_dir:
            return
        d = self._log_dir / "notebooks" / agent.agent_id
        d.mkdir(parents=True, exist_ok=True)
        status = (f"retired {stamp(agent.retired_t)} ({agent.retired_reason})"
                  if agent.retired_t is not None else "live at the end")
        (d / "scratch_final.md").write_text(
            f"# {agent.agent_id} — scratch memory, final ({status}; "
            f"final weight {math.exp(agent.log_weight):.4f})\n\n"
            f"{agent.notebook.scratch}\n")

    def _write_final_notebooks(self) -> None:
        for agent in list(self.population.agents.values()) + list(
                self.population.retired.values()):
            self._write_final_notebook(agent)
        self._flush_population_events()

    def diagnostics(self) -> Dict[str, Any]:
        pop = self.population
        return {
            "calls": self.calls,
            "call_totals": {k: {**v, "seconds": round(v["seconds"], 1)}
                            for k, v in self.call_totals.items()},
            "calls_per_day": {str(d): {k: {**v, "seconds": round(v["seconds"], 1)}
                                       for k, v in by.items()}
                              for d, by in sorted(self.calls_per_day.items())},
            "budget_exhausted_at": {str(d): s for d, s in
                                    sorted(self.budget_exhausted_at.items())},
            "population_size_per_day": {str(d): n for d, n in
                                        sorted(self.population_size_per_day.items())},
            "population_final": pop.size,
            "forks": pop.n_forks, "retirements": pop.n_retirements,
            "forks_rejected": self.forks_rejected,
            "reviews_failed": self.reviews_failed,
            "scratch_truncated": self.scratch_truncated,
            "invalid_forecasts": self.invalid_forecasts,
            "looks": self.n_looks, "question_rounds": self.n_question_rounds,
            "final_weights": {a: round(w, 6) for a, w in pop.weights.items()},
            "agents": {a: {"parent": ag.parent_id, "generation": ag.generation,
                           "born": stamp(ag.born_t),
                           "retired": stamp(ag.retired_t)
                           if ag.retired_t is not None else None,
                           "retired_reason": ag.retired_reason or None,
                           "beliefs_words": word_count(ag.notebook.beliefs),
                           "scratch_words": word_count(ag.notebook.scratch),
                           "weight": round(math.exp(ag.log_weight), 6)}
                       for a, ag in {**pop.agents, **pop.retired}.items()}}


# ----------------------------------------------------- belief and policy


class NotebookMixtureBelief(BeliefModel):
    """The mixture as a belief. ``predict`` for the question's object
    runs one round of the brain (every agent's forecast, the mixture,
    the look decision); ``predict_readonly`` (the harness's per-object
    snapshot) is the last sighting or uniform, no LLM."""

    consumes_negative_evidence_natively = True

    def __init__(self, rng: random.Random, brain: NotebookMixtureBrain,
                 label: Optional[str] = None) -> None:
        super().__init__(rng, floor_mass=0.0)
        self.brain = brain
        self._label = label
        self.log_loss_valid = True

    @property
    def name(self) -> str:
        return self._label or "NotebookMixture"

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        self.brain.reset(context)

    def update(self, evidence) -> None:
        self.brain.observe(evidence)
        super().update(evidence)

    def _last_seen(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        if history:
            last = history[-1][1]
            return Prediction(distribution={last: 1.0}, argmax=last)
        return self._uniform()

    def predict(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            # Found by a look at the question instant: the answer is
            # certain, so the round is skipped (the base class makes the
            # same short-circuit for every belief).
            self.brain._last = {"action": "answer", "argmax": current,
                                "found": True, "t": t, "object": object_id}
            return Prediction(distribution={current: 1.0}, argmax=current)
        decision = self.brain.decide(object_id, t)
        return Prediction(distribution=decision["distribution"],
                          argmax=decision["argmax"])

    def predict_readonly(self, object_id: str, t: int) -> Prediction:
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            return Prediction(distribution={current: 1.0}, argmax=current)
        return self._last_seen(object_id, t)

    def _predict_for_object(self, object_id: str, history, t: int
                            ) -> Prediction:
        return self._last_seen(object_id, t)


class NotebookMixturePolicy(DecisionPolicy):
    """Relays the brain's latest decision for the question; a look is
    forecast by every agent (``note_sense``) before it is returned."""

    def __init__(self, brain: NotebookMixtureBrain) -> None:
        self.brain = brain

    @property
    def name(self) -> str:
        return "NotebookMixturePolicy"

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        last = self.brain._last
        if (last is None or last.get("object") != question.object_id
                or last.get("t") != question.t_query
                or last.get("action") != "sense"):
            return AnswerNow()
        if "resident" in last:
            if 1.0 <= budget_remaining:
                self.brain.note_sense(last["resident"])
                return SensePerson(last["resident"])
            return AnswerNow()
        target = last["receptacle"]
        if self.brain.context.sense_cost(target) <= budget_remaining:
            self.brain.note_sense(target)
            return Sense(target)
        return AnswerNow()
