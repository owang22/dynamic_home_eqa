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
``forecasts.jsonl``, ``population.jsonl``, ``calls.jsonl``,
``scratch_versions.jsonl`` (every scratch memory an agent ever held,
with the instant and the event that wrote it), ``decisions.jsonl``
(every dispatcher briefing and reply, ``llm`` look rule), and the brain's
:meth:`~NotebookMixtureBrain.diagnostics` for ``diagnostics.json``.

**Speed** (2026-09-16). The per-agent calls of one round are independent
(each agent sees only its own notebook), so ``parallel`` of them are
sent at once and vLLM decodes them together (continuous batching: a
27B model's decode is bound by reading the weights, which one batch
does once for every stream); replies are accounted and applied in
agent order, so logs and forks are as sequential. An agent under
``skip_below`` weight gives no question forecast (it contributes
nothing to the mixture) but is still graded at every look, so it can
recover. Scratch memory is capped at 600 words (was 800).

**Variants** (:class:`NotebookConfig`, selected by arm kind). The
description above is ``notebook_mixture``, the first run's design. The
3-day cold-start run of 2026-09-16 showed one agent at 0.99 after three
looks (two of them decided by blank look forecasts read as 1% on
everything), the disagreement trigger then never firing again, and the
nightly review forking the same near-zero lineage every night. Two
revisions answer that:

* ``notebook_voi``: a look forecast must name at least one object and a
  blank one is scored at the population's weighted-mean score (neutral)
  instead of the floor; each look's score is multiplied by ``beta``
  (0.3) before it moves a weight, since one look grades every object
  but an agent's forecast rests on a few sentences; the look decision
  is the one-step value of information of the MIXTURE forecast (the
  same ``voi >= lambda`` rule the other arms use, lambda 0.05, best
  value-per-cost receptacle, a listed resident when ``ON_PERSON`` is
  the candidate), plus use-it-or-lose-it (look while looks left exceed
  the questions likely left today); the nightly review is skipped on a
  day without looks, and otherwise the TOP agent condenses its scratch
  into a revised BELIEFS (a fork with half of a real weight) and the
  lowest agent is retired in favour of one fresh contrasting document
  born at the equal share ``1/N`` (fair entry). Two rules added after
  the first ``notebook_voi`` attempt (every agent forked at the first
  look because a log score is always negative and read as failure, so
  the population hit 10 in three looks): a follow-up fork is accepted
  only from an agent that scored below the panel's weighted-average
  score on that look and has not forked today (``fork_gate``); the
  review runs at a day's end only once ``review_every_looks`` looks
  have accumulated since the last review, and never retires an agent
  born since that review.
* ``notebook_llmDecide``: ``notebook_voi`` with the look decision made
  by one further LLM call per round, the dispatcher, which reads the
  question, the clock, the looks and questions left today, the mixture
  forecast, the agents' split, the one-step gain of each candidate
  look, this question's looks so far, TODAY'S LEDGER (every decision so
  far today with its gain and what the look found) and its own NOTE (a
  short memory it rewrites on every call), and returns look-or-answer
  with a target, a reason and the new note. No threshold is given: the
  first run showed the dispatcher agreeing with the stated 0.05 rule
  on 37 of 37 decisions and citing it in every reason.

Second revision (2026-09-16, after both variants ran at 0.61 / 0.62):
the effective number of agents was ~2 throughout (top two held 83-94%
of the weight) while ten notebooks paid for forecasts and follow-ups,
and both arms spent the day's eight looks within the first hour (one
question took all eight). So: ``population_cap`` 5; follow-ups only for
agents at ``followup_min_weight`` or in the top 3 (everyone is still
graded at every look); ``max_looks_per_question`` 3.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import pathlib
import random
import time
import dataclasses
from dataclasses import dataclass, field
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Tuple)

from baselines.beliefs.base import BeliefModel
from baselines.llm_hypotheses.prompt import away_sentences
from baselines.policies.base import DecisionPolicy
from baselines.policies.voi_sense import value_of_information
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
SCRATCH_MAX_WORDS = 600   # was 800 until 2026-09-16: the follow-up was the costliest call
POPULATION_CAP = 10
INITIAL_AGENTS = 4

QUESTION_FORECAST_MAX_TOKENS = 1200
LOOK_FORECAST_MAX_TOKENS = 1200
FOLLOWUP_MAX_TOKENS = 4000
FORK_MAX_TOKENS = 4000
INITIAL_MAX_TOKENS = 14000

CALL_TYPES = ("initial", "question_forecast", "look_forecast", "follow_up",
              "fork", "review", "birth", "decide")
"""``fork`` is the retry of a follow-up whose fork document broke the
beliefs cap (a condensed rewrite); ``review`` is the end-of-day forced
fork; ``birth`` the review's fresh contrasting document (``top_fresh``
reviews); ``decide`` the dispatcher call (``llm`` look rule)."""


@dataclass(frozen=True)
class NotebookConfig:
    """The knobs that separate the variants (module docstring)."""
    look_rule: str = "thompson"      # thompson | voi | llm
    beta: float = 1.0                # look score multiplier before the update
    invalid_look: str = "floor"      # floor | neutral
    review: str = "lowest"           # lowest | top_fresh
    voi_lambda: float = 0.05
    use_it_or_lose_it: bool = False
    questions_per_day: float = 24.0  # for use-it-or-lose-it and the dispatcher
    fork_gate: bool = False          # follow-up forks only from below-average scorers, once a day
    review_every_looks: int = 0      # 0: nightly; else at day end once this many looks since the last review
    skip_below: float = 0.0          # agents under this weight give no question forecast (looks still grade them)
    parallel: int = 1                # per-agent LLM calls in flight at once (vLLM batches them)
    population_cap: int = POPULATION_CAP
    followup_min_weight: float = 0.0  # follow-ups only for agents at this weight or in the top 3 (everyone is graded)
    max_looks_per_question: int = 0  # 0: no cap
    tell_questions_per_day: bool = True  # False: the dispatcher learns the day's length from yesterday's ledger
    label: str = "notebook_mixture"


NOTEBOOK_VOI = NotebookConfig(look_rule="voi", beta=0.3, invalid_look="neutral",
                              review="top_fresh", use_it_or_lose_it=True,
                              fork_gate=True, review_every_looks=12,
                              skip_below=0.01, parallel=8, population_cap=5,
                              followup_min_weight=0.05, max_looks_per_question=3,
                              label="notebook_voi")
NOTEBOOK_LLM_DECIDE = dataclasses.replace(NOTEBOOK_VOI, look_rule="llm",
                                          tell_questions_per_day=False,
                                          label="notebook_llmDecide")
CONFIGS = {"notebook_mixture": NotebookConfig(), "notebook_voi": NOTEBOOK_VOI,
           "notebook_llmDecide": NOTEBOOK_LLM_DECIDE}

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
# minItems 1 (2026-09-16): two look forecasts of the first run came back
# as "objects": [] in 8 tokens and were scored as 1% on everything.
LOOK_FORECAST_SCHEMA = {
    "type": "object",
    "properties": {
        "objects": {"type": "array", "minItems": 1, "items": {
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
BIRTH_SCHEMA = {
    "type": "object",
    "properties": {"guess": {"type": "string"}, "beliefs": {"type": "string"}},
    "required": ["guess", "beliefs"],
}
DECIDE_SCHEMA = {
    "type": "object",
    "properties": {"action": {"type": "string", "enum": ["look", "answer"]},
                   "target": {"type": "string"}, "why": {"type": "string"},
                   "note": {"type": "string"}},
    "required": ["action", "why", "note"],
}
DECIDE_MAX_TOKENS = 1500
BIRTH_MAX_TOKENS = 8000
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


DISPATCH_NOTE_MAX_WORDS = 120
DISPATCH_SYSTEM_PROMPT = f"""You are the dispatcher of a home robot. The robot is asked, many times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends one of today's looks (opening one receptacle, or checking one resident it has listed). Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent looks are lost at midnight, and a day has far more questions than looks, so looks are rationed across the day: what a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most {DISPATCH_NOTE_MAX_WORDS} words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {{"action": "look" | "answer", "target": "<receptacle or resident id, for a look>", "why": "<one sentence>", "note": "<your rewritten note>"}}.

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
    last_fork_day: int = -1

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

    def top(self) -> str:
        return max(self.agents, key=lambda a: self.agents[a].log_weight)

    def add_fresh(self, guess: str, beliefs: str, why: str, t: int
                  ) -> NotebookAgent:
        """A new root document born at the equal share ``1/N`` of the
        population it joins (fair entry): everyone else is scaled to
        share the remaining ``(N - 1)/N``."""
        n = self.size + 1
        for ag in self.agents.values():
            ag.log_weight += math.log((n - 1) / n) if n > 1 else 0.0
        agent = NotebookAgent(self._new_id(), Notebook(beliefs), None, why,
                              guess, 1, t)
        agent.log_weight = -math.log(n)
        self.agents[agent.agent_id] = agent
        self._renormalize()
        self._event(t, "birth", agent=agent.agent_id, guess=agent.guess,
                    origin="review")
        return agent

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
                           target: str, beta: float = 1.0) -> Dict[str, float]:
        """Add ``beta`` times each live agent's look score to its log
        weight and renormalize. Returns the weights after."""
        for a, s in scores.items():
            if a in self.agents:
                self.agents[a].log_weight += beta * s
        self._renormalize()
        self._event(t, "look_update", target=target, beta=beta,
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
                 cap: int = POPULATION_CAP,
                 config: NotebookConfig = NotebookConfig()) -> None:
        self.client = client
        self.config = config
        if config.population_cap:
            cap = config.population_cap
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
        self.asked_today = 0
        self.looks_today = 0
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
        self.looks_per_day: Dict[int, int] = {}
        self.looks_since_review = 0
        self.last_review_t = -1
        self.forks_gated = 0
        self.decide_corrected = 0
        self.decisions: List[Dict[str, Any]] = []
        self._question_key: Optional[Tuple[str, int]] = None
        self._sensed_this_question: List[str] = []
        self._listed_this_question: Dict[str, Optional[str]] = {}
        self._seen_lines: List[str] = []           # this question's results
        self._pending_look: Optional[Dict[str, Any]] = None
        self._invalid_look_agents: List[str] = []
        self._skipped_last: List[str] = []
        self._today_look_lines: List[str] = []
        self._dispatch_ledger: List[Dict[str, Any]] = []   # today's decisions
        self._dispatch_note: str = ""                       # the dispatcher's memory
        self._days_seen: List[Tuple[int, int, int]] = []    # (day, questions, looks)
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

    def _generate(self, system: str, user: str, schema: Mapping[str, Any],
                  max_tokens: int, seed_offset: int) -> Tuple[Dict[str, Any], float]:
        """The network part of a call (thread-safe): the client's row and
        the wall seconds it took."""
        started = time.monotonic()
        row = self.client.generate(system, user,
                                   seed=self._seed + seed_offset,
                                   temperature=self._temperature,
                                   max_tokens=max_tokens, schema=schema)
        return row, time.monotonic() - started

    def _call(self, call_type: str, agent_id: Optional[str], user: str,
              schema: Mapping[str, Any], max_tokens: int, t: int,
              seed_offset: int = 0, system: str = SYSTEM_PROMPT,
              done: Optional[Tuple[Dict[str, Any], float]] = None
              ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """One LLM call: generate (unless ``done`` carries a reply already
        fetched in parallel), then account it under ``call_type`` and the
        day, in order. Returns ``(parsed JSON or None, row)``."""
        row, elapsed = done if done is not None else self._generate(
            system, user, schema, max_tokens, seed_offset)
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
                              f"{system}\n\n## user\n\n{user}\n\n"
                              f"## reply\n\n{row.get('payload')}\n")
        return parsed, row

    def _calls(self, call_type: str, jobs: Sequence[Tuple[str, str]],
               schema: Mapping[str, Any], max_tokens: int, t: int,
               system: str = SYSTEM_PROMPT
               ) -> Dict[str, Optional[Dict[str, Any]]]:
        """``jobs`` = ``(agent_id, user)`` pairs, fetched ``parallel`` at a
        time and accounted in the given order. Returns parsed by agent."""
        n = max(1, int(self.config.parallel))
        fetched: Dict[str, Tuple[Dict[str, Any], float]] = {}
        if n > 1 and len(jobs) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
                futures = {a: pool.submit(self._generate, system, user, schema,
                                          max_tokens, 0) for a, user in jobs}
                for a, fut in futures.items():
                    fetched[a] = fut.result()
        out: Dict[str, Optional[Dict[str, Any]]] = {}
        for a, user in jobs:
            parsed, _ = self._call(call_type, a, user, schema, max_tokens, t,
                                   done=fetched.get(a))
            out[a] = parsed
        return out

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
            self._log_scratch(agent, t, "birth")
        self._flush_population_events()

    def _new_day(self, t: int) -> None:
        day = t // DAY_SECONDS
        if day == self.day:
            return
        if self.day >= 0:
            self._end_of_day_review(self.day)
        if self.day >= 0:
            self._days_seen.append((self.day, self.asked_today, self.looks_today))
        self.day = day
        self.spent_today = 0.0
        self.asked_today = 0
        self.looks_today = 0
        self._dispatch_ledger = []
        self.budget_exhausted_at.setdefault(day, None)

    # ----------------------------------------------------------- forecasts

    def _question_forecasts(self, object_id: str, t: int
                            ) -> Dict[str, Dict[str, Any]]:
        """One call per live agent. Each entry: ``dist`` over every spot
        (real ids, floored and renormalized), ``top``, ``carrier``,
        ``carrier_room``, ``why``, ``raw`` (the spots as given)."""
        spots = self._spots()
        out: Dict[str, Dict[str, Any]] = {}
        weights = self.population.weights
        asked = [a for a in self.population.agents
                 if weights[a] >= self.config.skip_below]
        if not asked:
            asked = [self.population.top()]
        self._skipped_last = [a for a in self.population.agents if a not in asked]
        jobs = []
        for agent_id in asked:
            agent = self.population.agents[agent_id]
            jobs.append((agent_id, "\n\n".join([
                self._household_block(), self._notebook_block(agent),
                self._now_block(t), self._question_request(object_id)])))
        replies = self._calls("question_forecast", jobs,
                              QUESTION_FORECAST_SCHEMA,
                              QUESTION_FORECAST_MAX_TOKENS, t)
        for agent_id in asked:
            parsed = replies[agent_id]
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
        jobs = []
        for agent_id in list(self.population.agents):
            agent = self.population.agents[agent_id]
            jobs.append((agent_id, "\n\n".join([
                self._household_block(), self._notebook_block(agent),
                self._now_block(t), self._look_request(look)])))
        replies = self._calls("look_forecast", jobs, LOOK_FORECAST_SCHEMA,
                              LOOK_FORECAST_MAX_TOKENS, t)
        for agent_id, _user in jobs:
            parsed = replies[agent_id]
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
            if parsed is None or not given:
                self.invalid_forecasts += 1
                self._invalid_look_agents.append(agent_id)
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
            self.asked_today += 1
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
        elif self.config.look_rule in ("voi", "llm"):
            self._decide_by_voi(decision, forecasts, mixture, t)
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
            "skipped": list(self._skipped_last),
            "answer": answer, "action": decision["action"],
            "reason": decision.get("reason"), "draw": decision.get("draw"),
            "voi": decision.get("voi"), "dispatch": decision.get("dispatch"),
            "look": {k: decision[k] for k in ("receptacle", "resident")
                     if k in decision}})
        return decision

    # ------------------------------------------------ voi / dispatcher

    def _look_candidates(self, forecasts: Mapping[str, Mapping[str, Any]]
                         ) -> Dict[str, Dict[str, Any]]:
        """Every legal look right now, keyed by the spot it tests:
        each untried sensable receptacle the budget covers, and
        ``ON_PERSON`` when a resident listed this question has not been
        looked at (the resident is the carrier the heaviest forecast
        names if listed, else the first listed)."""
        assert self.context is not None
        ctx = self.context
        remaining = self._remaining()
        out: Dict[str, Dict[str, Any]] = {}
        for r in ctx.sensable_receptacle_ids:
            if r in self._sensed_this_question or ctx.sense_cost(r) > remaining:
                continue
            out[r] = {"receptacle": r, "room": ctx.receptacle_rooms.get(r),
                      "cost": ctx.sense_cost(r)}
        if self._person_sensing() and remaining >= 1.0:
            listed = [r for r in self._listed_this_question
                      if r not in self._sensed_this_question]
            if listed:
                weights = self.population.weights
                heaviest = max(forecasts, key=lambda a: weights.get(a, 0.0))
                carrier = forecasts[heaviest].get("carrier")
                who = carrier if carrier in listed else listed[0]
                out[ON_PERSON] = {"resident": who,
                                  "room": self._listed_this_question[who],
                                  "cost": 1.0}
        return out

    def _decide_by_voi(self, decision: Dict[str, Any],
                       forecasts: Mapping[str, Mapping[str, Any]],
                       mixture: Mapping[str, float], t: int) -> None:
        """The ``voi`` rule, and the ``llm`` rule that reads its verdict."""
        cfg = self.config
        if (cfg.max_looks_per_question
                and len(self._sensed_this_question) >= cfg.max_looks_per_question):
            decision["reason"] = f"question look cap {cfg.max_looks_per_question}"
            return
        cands = self._look_candidates(forecasts)
        if not cands:
            decision["reason"] = "no legal look"
            return
        voi = value_of_information(mixture, list(cands))
        rate = {s: voi[s] / cands[s]["cost"] for s in cands}
        best = max(rate, key=lambda s: (rate[s], mixture.get(s, 0.0)))
        if cfg.tell_questions_per_day:
            per_day = cfg.questions_per_day
        else:
            per_day = float(self._days_seen[-1][1]) if self._days_seen else 0.0
        questions_left = max(0.0, per_day - self.asked_today)
        spare = (cfg.use_it_or_lose_it and voi[best] > 0.0
                 and self._remaining() >= questions_left + 1.0)
        verdict = {"best": best, "voi": round(voi[best], 4),
                   "rate": round(rate[best], 4), "lam": cfg.voi_lambda,
                   "p_now": round(max(mixture.values()), 4),
                   "spare": spare, "questions_left": questions_left,
                   "table": {s: round(v, 4) for s, v in
                             sorted(voi.items(), key=lambda kv: -kv[1])[:5]}}
        decision["voi"] = verdict
        if cfg.look_rule == "llm":
            self._llm_decide(decision, forecasts, mixture, cands, verdict, t)
            return
        if rate[best] >= cfg.voi_lambda or spare:
            decision.update({k: v for k, v in cands[best].items() if k != "cost"})
            decision["action"] = "sense"
            decision["reason"] = ("voi" if rate[best] >= cfg.voi_lambda
                                  else "spare looks") + f" {voi[best]:.3f}"
        else:
            decision["reason"] = f"voi {voi[best]:.3f} below {cfg.voi_lambda:g}"

    def _llm_decide(self, decision: Dict[str, Any],
                    forecasts: Mapping[str, Mapping[str, Any]],
                    mixture: Mapping[str, float],
                    cands: Mapping[str, Mapping[str, Any]],
                    verdict: Mapping[str, Any], t: int) -> None:
        """One dispatcher call; an illegal target on a look falls back
        to the best value-per-cost candidate (counted)."""
        assert self.context is not None
        cfg = self.config
        weights = self.population.weights
        top = sorted(mixture.items(), key=lambda kv: -kv[1])[:5]
        split: Dict[str, float] = {}
        for a, f in forecasts.items():
            split[f["top"]] = split.get(f["top"], 0.0) + weights.get(a, 0.0)
        split_lines = ", ".join(f"{self.rec(s)} {w:.0%}" for s, w in
                                sorted(split.items(), key=lambda kv: -kv[1]))
        p_now = verdict["p_now"]
        voi_lines = []
        for s, v in verdict["table"].items():
            c = cands[s]
            name = (f"resident {self.rec(c['resident'])}" if "resident" in c
                    else self.rec(s))
            voi_lines.append(f"  look at {name}: chance of a right answer "
                             f"{p_now:.0%} -> {min(1.0, p_now + v):.0%} "
                             f"(gain {v:.3f})")
        seen = ("\n".join(f"  {line}" for line in self._seen_lines)
                or "  nothing yet")
        legal = ", ".join(
            (self.rec(c["resident"]) if "resident" in c else self.rec(s))
            for s, c in cands.items())
        ledger = "\n".join(
            f"  {e['stamp'][4:]} {self.obj(e['object'])}: sure {e['p_now']:.0%}, "
            f"best gain {e['gain']:+.3f} -> "
            + (f"looked at {e['target']}: {e.get('found', 'result pending')}"
               if e['action'] == 'look' else "answered")
            for e in self._dispatch_ledger) or "  (first decision of the day)"
        cap_line = (f" At most {cfg.max_looks_per_question} looks per question; "
                    f"this question has used {len(self._sensed_this_question)}."
                    if cfg.max_looks_per_question else "")
        user = "\n\n".join([
            f"QUESTION: where is {self.obj(decision['object'])} right now? "
            f"Asked at {stamp(t)}; the robot is in "
            f"{self.context.robot_position.room or 'an unknown room'}.",
            f"TODAY: looks left {self._remaining():g} of "
            f"{self.context.budget_per_day}; questions so far today "
            f"{self.asked_today}"
            + (f" of about {cfg.questions_per_day:g}" if cfg.tell_questions_per_day
               else "")
            + f"; looks used today {self.looks_today}.{cap_line}"
            + ("" if cfg.tell_questions_per_day else
               (f"\nPREVIOUS DAYS: " + "; ".join(
                   f"{WEEKDAY_NAMES[d % 7]} {q} questions, {l} looks used"
                   for d, q, l in self._days_seen[-7:])
                if self._days_seen else
                "\nPREVIOUS DAYS: none yet - how many questions a day brings "
                "is for you to find out.")),
            f"TODAY'S LEDGER:\n{ledger}",
            f"YOUR NOTE:\n{self._dispatch_note or '(empty)'}",
            "PANEL FORECAST (share of belief): " + ", ".join(
                f"{self.rec(s)} {p:.0%}" for s, p in top) +
            f".\nAGENTS' TOP SPOTS (by credibility): {split_lines}.",
            "VALUE OF INFORMATION (one-step, this question only):\n"
            + "\n".join(voi_lines),
            f"LOOKS SO FAR ON THIS QUESTION:\n{seen}",
            f"LEGAL LOOK TARGETS NOW: {legal}.",
            "Decide: answer now, or look (name the target). One sentence why."])
        parsed, _ = self._call("decide", None, user, DECIDE_SCHEMA,
                               DECIDE_MAX_TOKENS, t, system=DISPATCH_SYSTEM_PROMPT)
        # every briefing and reply, verbatim, for the replay
        self._write_row("decisions.jsonl", {
            "t": t, "stamp": stamp(t), "object": decision["object"],
            "round": decision["round"], "briefing": user, "reply": parsed})
        note = str((parsed or {}).get("note", "")).strip()
        if note:
            words = note.split()
            self._dispatch_note = " ".join(words[:DISPATCH_NOTE_MAX_WORDS])
        action = str((parsed or {}).get("action", "answer")).strip().lower()
        why = str((parsed or {}).get("why", ""))[:300]
        target = str((parsed or {}).get("target", "")).strip()
        real = self.real_rec(target)
        chosen: Optional[str] = None
        if action == "look":
            for s, c in cands.items():
                if real == s or real == c.get("resident") or real == c.get("receptacle"):
                    chosen = s
                    break
            if chosen is None:
                chosen = verdict["best"]
                self.decide_corrected += 1
                decision["dispatch_corrected"] = target
        decision["dispatch"] = {"action": action, "target": target, "why": why,
                                "note": self._dispatch_note}
        entry = {"stamp": stamp(t), "object": decision["object"],
                 "p_now": p_now, "gain": verdict["voi"],
                 "action": "look" if chosen is not None else "answer"}
        if chosen is not None:
            decision.update({k: v for k, v in cands[chosen].items() if k != "cost"})
            decision["action"] = "sense"
            decision["reason"] = f"dispatcher: {why}"
            entry["target"] = self.rec(cands[chosen].get("resident")
                                       or cands[chosen]["receptacle"])
        else:
            decision["reason"] = f"dispatcher: {why}"
        self._dispatch_ledger.append(entry)

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
        self._invalid_look_agents = []
        look["forecasts"] = self._look_forecasts(look, t)
        look["invalid"] = list(self._invalid_look_agents)
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
        self._today_look_lines.append(line)
        if self._dispatch_ledger and self._dispatch_ledger[-1]["action"] == "look":
            self._dispatch_ledger[-1]["found"] = inside
        self._look_procedure(pending, target, room, contents, listed, line, t)

    def _look_procedure(self, look: Dict[str, Any], target: str,
                        room: Optional[str], contents: Tuple[str, ...],
                        listed: Tuple[str, ...], line: str, t: int) -> None:
        objects = self._known_objects()
        forecasts: Dict[str, Dict[str, float]] = look["forecasts"]
        scores = {a: look_score(f, contents, objects)
                  for a, f in forecasts.items()}
        before = look["weights_before"]
        invalid = [a for a in look.get("invalid", []) if a in scores]
        if invalid and self.config.invalid_look == "neutral":
            valid = [a for a in scores if a not in invalid]
            wsum = sum(before.get(a, 0.0) for a in valid)
            neutral = (sum(before.get(a, 0.0) * scores[a] for a in valid) / wsum
                       if valid and wsum > 0 else 0.0)
            for a in invalid:
                scores[a] = neutral
        after = self.population.update_log_weights(scores, t, target,
                                                   beta=self.config.beta)
        self.n_looks += 1
        self.looks_today += 1
        self.looks_since_review += 1
        self.looks_per_day[self.day] = self.looks_per_day.get(self.day, 0) + 1
        self._write_row("looks.jsonl", {
            "t": t, "stamp": stamp(t), "n": self.n_looks,
            "target": target,
            "kind": "resident" if "resident" in look else "receptacle",
            "room": room, "result": list(contents),
            "residents_listed": list(listed),
            "forecasts": {a: {o: round(p, 4) for o, p in f.items()}
                          for a, f in forecasts.items()},
            "scores": {a: round(s, 4) for a, s in scores.items()},
            "beta": self.config.beta, "invalid": invalid,
            "follow_ups": self._follow_up_set(after),
            "neutral_scored": bool(invalid and self.config.invalid_look == "neutral"),
            "weights_before": {a: round(w, 6) for a, w in before.items()},
            "weights_after": {a: round(w, 6) for a, w in after.items()}})
        self._flush_population_events()
        # Follow-ups, one per agent alive at the look (forks born in this
        # round get no follow-up of their own).
        wsum = sum(before.get(a, 0.0) for a in scores) or 1.0
        panel_avg = sum(before.get(a, 0.0) * scores[a] for a in scores) / wsum
        jobs: List[Tuple[str, str, bool]] = []
        active = self._follow_up_set(after)
        for agent_id in list(forecasts):
            if agent_id in self.population.agents and agent_id in active:
                user, may_fork = self._follow_up_prompt(
                    agent_id, line, forecasts[agent_id], scores[agent_id],
                    blank=agent_id in invalid, panel_avg=panel_avg,
                    weight_before=before.get(agent_id, 0.0), all_scores=scores)
                jobs.append((agent_id, user, may_fork))
        replies = self._calls("follow_up", [(a, u) for a, u, _ in jobs],
                              FOLLOWUP_SCHEMA, FOLLOWUP_MAX_TOKENS, t)
        for agent_id, user, may_fork in jobs:
            self._apply_follow_up(agent_id, replies[agent_id], user, may_fork,
                                  scores[agent_id], panel_avg, t)
        self._flush_population_events()

    def _follow_up_set(self, weights: Mapping[str, float]) -> List[str]:
        """Agents that get a follow-up after a look: at
        ``followup_min_weight`` or in the top 3 by weight (0: everyone)."""
        thr = self.config.followup_min_weight
        if not thr:
            return list(self.population.agents)
        ranked = sorted(self.population.agents, key=lambda a: -weights.get(a, 0.0))
        return [a for a in ranked if weights.get(a, 0.0) >= thr or ranked.index(a) < 3]

    def _follow_up_prompt(self, agent_id: str, line: str,
                          forecast: Mapping[str, float], score: float,
                          blank: bool = False,
                          panel_avg: Optional[float] = None,
                          weight_before: Optional[float] = None,
                          all_scores: Optional[Mapping[str, float]] = None
                          ) -> Tuple[str, bool]:
        """The follow-up prompt for one agent after a look, and whether a
        fork from it would be accepted (the gate)."""
        agent = self.population.agents[agent_id]
        given = ", ".join(f"{self.obj(o)} {p:.2f}" for o, p in forecast.items()) \
            or "(nothing listed)"
        w = self.population.weights[agent_id]
        rank = self.population.rank(agent_id)
        if blank and self.config.invalid_look == "neutral":
            score_line = (f"YOUR FORECAST was blank, so this look was scored "
                          f"for you at the population's average ({score:.2f}); "
                          f"name at least one object next time.")
        else:
            score_line = (f"YOUR SCORE for this look: {score:.2f} (over every "
                          f"object, log p for what was there and log(1 - p) "
                          f"for what was absent).")
        if self.config.beta != 1.0:
            score_line += (f" Weights move by {self.config.beta:g} times the "
                           f"score.")
        gate = self.config.fork_gate
        may_fork = True
        if gate:
            below = panel_avg is not None and score < panel_avg
            may_fork = below and agent.last_fork_day != self.day
        if all_scores:
            board = ", ".join(
                f"{a} {sc:.2f}{' (you)' if a == agent_id else ''}"
                for a, sc in sorted(all_scores.items(), key=lambda kv: -kv[1]))
            score_line += f"\nPANEL SCORES on this look, best first: {board}."
        if panel_avg is not None:
            moved = ("" if weight_before is None else
                     (" You gained credibility on it." if w > weight_before + 1e-9
                      else " You lost credibility on it." if w < weight_before - 1e-9
                      else ""))
            score_line += (f" Scores are log probabilities, so every score is "
                           f"negative; the panel's average on this look was "
                           f"{panel_avg:.2f}, and yours is "
                           f"{'above' if score >= panel_avg else 'below'} it."
                           f"{moved}")
        if gate:
            fork_text = (
                "Scratch memory is for detail and dated observations; a FORK is "
                "for a belief this look CONTRADICTED. " +
                ("You may propose a FORK (new BELIEFS as a complete rewrite of "
                 "yours, plus why)." if may_fork else
                 "You scored at or above the panel's average on this look, or "
                 "have already forked today, so no fork this time: rewrite "
                 "SCRATCH MEMORY only."))
        else:
            fork_text = ("You may propose a FORK (new BELIEFS as a complete "
                         "rewrite of yours, plus why).")
        user = "\n\n".join([
            self._household_block(), self._notebook_block(agent),
            f"RESULT OF THE LOOK\n{line}\n"
            f"YOUR FORECAST: {given}; everything else left out.\n"
            f"{score_line}\n"
            f"YOUR WEIGHT is now {w:.3f}, rank {rank} of "
            f"{self.population.size}.",
            f"You may rewrite your SCRATCH MEMORY (return its full new text; "
            f"return the current text to keep it as is). {fork_text} "
            f"Reply as JSON: {{\"scratch\": \"...\", \"fork\": {{\"beliefs\": "
            f"\"...\", \"why\": \"...\"}}}}; leave fork out to keep your "
            f"beliefs as they are."])
        return user, may_fork

    def _apply_follow_up(self, agent_id: str, parsed: Optional[Dict[str, Any]],
                         user: str, may_fork: bool, score: float,
                         panel_avg: Optional[float], t: int) -> None:
        if parsed is None or agent_id not in self.population.agents:
            return
        agent = self.population.agents[agent_id]
        self._apply_scratch(agent, str(parsed.get("scratch", "")), user, t)
        fork = parsed.get("fork")
        if isinstance(fork, dict) and str(fork.get("beliefs", "")).strip():
            if not may_fork:
                self.forks_gated += 1
                self.population.events.append(
                    {"t": t, "event": "fork_gated", "parent": agent_id,
                     "score": round(score, 4),
                     "panel_avg": round(panel_avg, 4) if panel_avg is not None else None})
                return
            child = self._apply_fork(agent_id, str(fork["beliefs"]),
                                     str(fork.get("why", "")), t, "follow_up")
            if child is not None:
                agent.last_fork_day = self.day

    def _apply_scratch(self, agent: NotebookAgent, text: str, user: str,
                       t: int) -> None:
        """Set the scratch memory; over the cap, one retry asks for a
        trimmed version, and a second overflow is cut at the cap."""
        try:
            agent.notebook.scratch = text
            self._log_scratch(agent, t, "follow_up")
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
        self._log_scratch(agent, t, "follow_up_trimmed")

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
            self._log_scratch(child, t, f"fork:{origin}")
            if retired is not None:
                self._write_final_notebook(retired)
            return child
        return None

    # ------------------------------------------------------------- review

    def _end_of_day_review(self, day: int) -> None:
        """After the day's last question. ``lowest``: the lowest-weight
        agent must fork if its weight is below the equal share.
        ``top_fresh``: nothing on a day without looks; otherwise the top
        agent condenses its scratch into revised BELIEFS (a fork) and the
        lowest agent is retired for a fresh contrasting document born at
        the equal share."""
        t = (day + 1) * DAY_SECONDS - 1
        if self.config.review == "top_fresh":
            self._review_top_fresh(day, t)
            return
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

    def _review_top_fresh(self, day: int, t: int) -> None:
        pop = self.population
        n = pop.size
        looks_today = self.looks_per_day.get(day, 0)
        since = self.looks_since_review
        need = self.config.review_every_looks
        weights = {a: round(w, 6) for a, w in pop.weights.items()}
        skipped = None
        if n == 0 or since == 0:
            skipped = "no looks since the last review"
        elif need and since < need:
            skipped = f"{since} looks since the last review, review at {need}"
        if skipped:
            pop.events.append({
                "t": t, "event": "review", "day": day, "population": n,
                "candidate": None, "mode": "top_fresh", "skipped": skipped,
                "looks_since_review": since, "weights": weights})
            self._flush_population_events()
            return
        top = pop.top()
        # Grace period: never retire an agent born since the last review
        # (before the first review: born before today).
        cutoff = (self.last_review_t if self.last_review_t >= 0
                  else day * DAY_SECONDS)
        eligible = [a for a, ag in pop.agents.items()
                    if (ag.born_t <= cutoff if self.last_review_t >= 0
                        else ag.born_t < cutoff)]
        low = min(eligible, key=lambda a: pop.agents[a].log_weight) if eligible else None
        pop.events.append({
            "t": t, "event": "review", "day": day, "population": n,
            "candidate": top, "mode": "top_fresh", "retire": low,
            "looks_today": looks_today, "looks_since_review": since,
            "weights": weights})
        self.looks_since_review = 0
        # (a) the top agent condenses its scratch into revised beliefs
        agent = pop.agents[top]
        user = "\n\n".join([
            self._household_block(), self._notebook_block(agent),
            f"END OF DAY {stamp(t)[:3]} REVIEW. Your weight is "
            f"{pop.weights[top]:.3f}, the highest of {n} agents, after "
            f"{since} look{'s' if since != 1 else ''} since the last review. "
            f"Condense what your SCRATCH MEMORY has taught you into a fork: "
            f"new BELIEFS as a complete rewrite of yours that keeps what the "
            f"looks confirmed, drops what they contradicted, and states the "
            f"patterns your scratch entries point to; and why. Reply as JSON: "
            f"{{\"beliefs\": \"...\", \"why\": \"...\"}}."])
        child = None
        for attempt in range(2):
            parsed, _ = self._call("review", top, user, FORK_SCHEMA,
                                   FORK_MAX_TOKENS, t, seed_offset=attempt)
            beliefs = str((parsed or {}).get("beliefs", "")).strip()
            if not beliefs:
                continue
            child = self._apply_fork(top, beliefs,
                                     str((parsed or {}).get("why", "")), t,
                                     "review")
            if child is not None:
                break
        if child is None:
            self.reviews_failed += 1
            pop.events.append({"t": t, "event": "review_failed", "agent": top})
        # (b) retire the lowest eligible (never the newborn, never an agent
        # born since the last review) for a fresh document
        if low is not None and low in pop.agents and pop.size > 1 and (
                child is None or low != child.agent_id):
            retired = pop.retire(low, t, "review: lowest at end of day")
            self._write_final_notebook(retired)
        guesses = "\n".join(f"  {a}: {ag.guess}" for a, ag in pop.agents.items())
        looks = "\n".join(f"  {line}" for line in self._today_look_lines) \
            or "  (none)"
        user = "\n\n".join([
            self._household_block(),
            f"END OF DAY {stamp(t)[:3]} REVIEW: a new agent joins the "
            f"population with the equal share of the weight.",
            f"THE OTHER AGENTS' GUESSES ABOUT THIS HOUSEHOLD:\n{guesses}",
            f"WHAT THE LOOKS SINCE THE LAST REVIEW SHOWED:\n{looks}",
            f"Write one new BELIEFS document (at most {BELIEFS_MAX_WORDS} "
            f"words) built on a guess about how this household lives that "
            f"CONTRASTS with the guesses above, and is consistent with what "
            f"the looks showed. Reply as JSON: {{\"guess\": \"...\", "
            f"\"beliefs\": \"...\"}}."])
        born = None
        for attempt in range(2):
            parsed, _ = self._call("birth", None, user, BIRTH_SCHEMA,
                                   BIRTH_MAX_TOKENS, t, seed_offset=attempt)
            beliefs = str((parsed or {}).get("beliefs", "")).strip()
            if not beliefs:
                continue
            if word_count(beliefs) > BELIEFS_MAX_WORDS:
                beliefs = " ".join(beliefs.split()[:BELIEFS_MAX_WORDS])
            born = pop.add_fresh(str((parsed or {}).get("guess", ""))[:300],
                                 beliefs, "[review] fresh contrasting document",
                                 t)
            self._write_notebook(born)
            self._log_scratch(born, t, "birth:review")
            break
        if born is None:
            self.reviews_failed += 1
            pop.events.append({"t": t, "event": "birth_failed"})
        self._today_look_lines = []
        self.last_review_t = t
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

    def _log_scratch(self, agent: NotebookAgent, t: int, origin: str) -> None:
        """Every scratch memory an agent ever held, in order, so a replay
        can show the notebook as it stood at any instant."""
        self._write_row("scratch_versions.jsonl", {
            "agent": agent.agent_id, "t": t, "stamp": stamp(t),
            "origin": origin, "words": word_count(agent.notebook.scratch),
            "scratch": agent.notebook.scratch})

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
            "config": dataclasses.asdict(self.config),
            "calls": self.calls,
            "looks_per_day": {str(d): n for d, n in sorted(self.looks_per_day.items())},
            "decide_corrected": self.decide_corrected,
            "forks_gated": self.forks_gated,
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
