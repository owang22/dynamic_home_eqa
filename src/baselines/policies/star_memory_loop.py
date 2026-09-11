"""STAR-style memory loop: recall from indexed memory, or sense, or answer.

Reference: STAR (Chen et al., arXiv:2511.14004, ICRA 2026). Its loop: an
LLM sees the task, a working memory of past action-outcome pairs, and
the remaining budget, and each step picks a temporal action (retrieve
from long-term memory) or a spatial action (physically look). No
probability distribution, no cost arithmetic. STAR is vision-based; in
this symbolic setting perception maps onto the existing Sense action.

One policy class, :class:`StarMemoryLoopPolicy`, with a pluggable
:class:`ActionSelector`, so the LLM and the scripted control share the
identical loop, working memory, caps and bookkeeping:

* per question the policy keeps a working memory -- a list of
  (action, outcome) strings, reset at each new question id;
* each step the selector sees the question, the working memory, the
  remaining budget and the action menu (a :class:`LoopView`) and returns
  one recall tool call, one Sense, or an answer;
* recall results and sense results are appended to working memory as
  text; recalls are free, senses cost budget;
* total steps per question are capped (``max_steps``, default 8) and
  recall calls separately (``max_recalls``, default 4), so a selector
  cannot loop forever on free actions.

An unparseable selector output or an illegal action (unknown/unsensable/
already-tried receptacle, sense with zero budget, recall past its cap)
is appended to working memory as a rejection line and the selector is
retried once; a second failure on the same step falls through to
answering the belief's argmax. Both events are counted per question
(:attr:`StarMemoryLoopPolicy.last_question_stats`).

The selector gets the belief's distribution only through that fallback
argmax (``LoopView.fallback_receptacle``): STAR has no belief, and
keeping the selector blind to the probabilities is what makes the
comparison against belief-reading policies mean something.

Harness caveat (recorded in STATUS.md): the standard harness feeds the
ambient stream to beliefs only and always commits the belief argmax as
the answer, so this policy runs under the study-local runner in
``baselines.star_study``, which additionally calls :meth:`observe` on
every piece of evidence (building the memory index) and honours
:attr:`answer_override` when the selector answers a location of its
own. Under the standard harness the loop still terminates and behaves,
but memory stays empty and overrides are ignored -- the study runner is
the supported home.

All times are seconds since episode start.
"""

from __future__ import annotations

import abc
import dataclasses
import json
from typing import Callable, Dict, List, Mapping, Optional, Tuple, Union

from baselines.memory.indexed_observation_log import IndexedObservationLog
from baselines.memory.recall_tools import (RecallResult, freshest_sighting,
                                           recall_object_history,
                                           recall_receptacle_history,
                                           recall_time_pattern)
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Observation,
                             Prediction, Question, Sense, SenseResult)

RECALL_TOOLS = ("recall_object_history", "recall_receptacle_history",
                "recall_time_pattern")
"""The temporal actions; Sense is the spatial one."""

DEFAULT_MAX_STEPS = 8
DEFAULT_MAX_RECALLS = 4
DEFAULT_FRESH_AGE_S = 3600
"""Scripted control: a sighting younger than this answers directly."""


# ----------------------------------------------------------- actions

@dataclasses.dataclass(frozen=True)
class RecallCall:
    """Free temporal action: run one recall tool."""

    tool: str
    object_id: Optional[str] = None
    receptacle_id: Optional[str] = None
    hour_window: int = 1


@dataclasses.dataclass(frozen=True)
class SenseCall:
    """Spatial action: pay one budget unit to look inside a receptacle."""

    receptacle_id: str


@dataclasses.dataclass(frozen=True)
class AnswerCall:
    """Commit to a location (any legal answer, sensable or not).

    ``from_fallback`` marks an answer the selector merely copied from
    the belief-argmax fallback window; it is excluded from the
    answered-from-memory count."""

    receptacle_id: str
    from_fallback: bool = False


StarAction = Union[RecallCall, SenseCall, AnswerCall]


class SelectorError(Exception):
    """Raised by a selector whose output could not be parsed into a
    :class:`StarAction`; the loop books it as ``unparseable``."""


@dataclasses.dataclass(frozen=True)
class LoopView:
    """Everything a selector may look at for one step.

    ``working_memory`` is the (action, outcome) lines so far this
    question, oldest first. ``last_recall`` carries the structured
    records behind the newest recall (None before any); the scripted
    selector acts on it, the LLM selector must ignore it.
    ``fallback_receptacle`` is the belief argmax -- the ONLY window on
    the belief, reserved for fallbacks.
    """

    question: Question
    object_class: str
    working_memory: Tuple[str, ...]
    budget_remaining: float
    steps_used: int
    recalls_used: int
    max_steps: int
    max_recalls: int
    tried: Tuple[str, ...]
    sensable_receptacles: Tuple[str, ...]
    all_locations: Tuple[str, ...]
    rooms: Mapping[str, str]
    fallback_receptacle: str
    last_recall: Optional[RecallResult]


class ActionSelector(abc.ABC):
    """One step of the loop: view in, action out."""

    @property
    def name(self) -> str:
        return type(self).__name__

    def reset(self) -> None:
        """Start of a fresh episode. Stateless selectors need not override."""

    @abc.abstractmethod
    def select(self, view: LoopView) -> StarAction:
        """Return the next action, or raise :class:`SelectorError`."""


# ------------------------------------------------------------ policy

class StarMemoryLoopPolicy(DecisionPolicy):
    """The shared loop around a pluggable selector (module docstring)."""

    def __init__(self, selector: ActionSelector,
                 rooms: Optional[Mapping[str, str]] = None,
                 max_steps: int = DEFAULT_MAX_STEPS,
                 max_recalls: int = DEFAULT_MAX_RECALLS) -> None:
        if max_steps < 1 or max_recalls < 0 or max_recalls >= max_steps:
            raise ValueError(
                f"StarMemoryLoopPolicy: need max_steps >= 1 and "
                f"0 <= max_recalls < max_steps, got "
                f"({max_steps}, {max_recalls})")
        self._selector = selector
        self._rooms: Dict[str, str] = dict(rooms or {})
        self._max_steps = max_steps
        self._max_recalls = max_recalls
        self._context: Optional[EpisodeContext] = None
        self._memory: Optional[IndexedObservationLog] = None
        self._question_id: Optional[str] = None
        self._working_memory: List[str] = []
        self._tried: List[str] = []
        self._steps = 0
        self._recalls = 0
        self._senses = 0
        self._last_recall: Optional[RecallResult] = None
        self._answer_override: Optional[str] = None
        self._pending_sense_line = False
        self._stats: Dict[str, int] = {}

    @property
    def name(self) -> str:
        return f"StarMemoryLoop({self._selector.name})"

    @property
    def memory(self) -> IndexedObservationLog:
        if self._memory is None:
            raise RuntimeError(f"{self.name}: observe/decide before reset()")
        return self._memory

    @property
    def answer_override(self) -> Optional[str]:
        """The selector's own committed location for the newest answered
        question, or None when the answer fell back to the belief argmax.
        Consumed by the study runner; cleared on the next question."""
        return self._answer_override

    @property
    def last_working_memory(self) -> Tuple[str, ...]:
        """The (action, outcome) lines of the current/most recent
        question -- the loop's full transcript, for run-log inspection."""
        return tuple(self._working_memory)

    @property
    def last_question_stats(self) -> Dict[str, int]:
        """Counters for the question answered most recently: recalls,
        senses, answered_from_memory (an AnswerCall with zero senses
        spent), answered_by_selector, unparseable, illegal, fallbacks,
        step_cap_hits."""
        return dict(self._stats)

    def reset(self, context: EpisodeContext) -> None:
        self._context = context
        self._memory = IndexedObservationLog(context.object_classes,
                                             self._rooms)
        self._selector.reset()
        self._question_id = None
        self._answer_override = None
        self._stats = {}

    def observe(self, evidence: Union[Observation, SenseResult]) -> None:
        """Feed one piece of agent-visible evidence to long-term memory.

        The study runner calls this alongside the belief's own update;
        the standard harness never does (see module docstring)."""
        self.memory.ingest(evidence)

    # ---------------------------------------------------------- decide

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._context is None:
            raise RuntimeError(f"{self.name}: decide() before reset()")
        if self._question_id != question.question_id:
            self._start_question(question)
        if self._pending_sense_line and last_sense is not None:
            self._book_sense_outcome(question, last_sense)
        if (last_sense is not None
                and question.object_id in last_sense.contents):
            # Found at the query instant: ground truth, answer it.
            return self._answer(last_sense.receptacle_id,
                                by_selector=False, note="found")
        return self._loop(question, prediction, budget_remaining)

    def _start_question(self, question: Question) -> None:
        self._question_id = question.question_id
        self._working_memory = []
        self._tried = []
        self._steps = 0
        self._recalls = 0
        self._senses = 0
        self._last_recall = None
        self._answer_override = None
        self._pending_sense_line = False
        self._stats = {k: 0 for k in
                       ("recalls", "senses", "answered_from_memory",
                        "answered_by_selector", "unparseable", "illegal",
                        "fallbacks", "step_cap_hits")}

    def _book_sense_outcome(self, question: Question,
                            sense: SenseResult) -> None:
        self._pending_sense_line = False
        if question.object_id in sense.contents:
            outcome = f"FOUND {question.object_id}"
        else:
            listing = ", ".join(sense.contents) if sense.contents else "empty"
            outcome = f"{question.object_id} NOT here (contents: {listing})"
        self._working_memory.append(
            f"sense {sense.receptacle_id} -> {outcome}")

    def _loop(self, question: Question, prediction: Prediction,
              budget_remaining: float) -> Action:
        assert self._context is not None
        failures_this_step = 0
        while True:
            if self._steps >= self._max_steps:
                self._stats["step_cap_hits"] += 1
                return self._fallback("step cap reached")
            view = self._view(question, prediction, budget_remaining)
            try:
                action = self._selector.select(view)
            except SelectorError as err:
                self._stats["unparseable"] += 1
                failures_this_step += 1
                if failures_this_step >= 2:
                    return self._fallback(f"unparseable action: {err}")
                self._working_memory.append(
                    f"rejected: unparseable action ({err})")
                continue
            problem = self._illegal(action, budget_remaining)
            if problem is not None:
                self._stats["illegal"] += 1
                failures_this_step += 1
                if failures_this_step >= 2:
                    return self._fallback(f"illegal action: {problem}")
                self._working_memory.append(f"rejected: {problem}")
                continue
            failures_this_step = 0
            if isinstance(action, RecallCall):
                self._run_recall(question, action)
                continue
            if isinstance(action, SenseCall):
                self._steps += 1
                self._senses += 1
                self._stats["senses"] += 1
                self._tried.append(action.receptacle_id)
                self._pending_sense_line = True
                return Sense(receptacle_id=action.receptacle_id)
            assert isinstance(action, AnswerCall)
            return self._answer(action.receptacle_id, by_selector=True,
                                from_fallback=action.from_fallback)

    def _view(self, question: Question, prediction: Prediction,
              budget_remaining: float) -> LoopView:
        assert self._context is not None
        return LoopView(
            question=question,
            object_class=self._context.object_classes.get(
                question.object_id, "unknown"),
            working_memory=tuple(self._working_memory),
            budget_remaining=budget_remaining,
            steps_used=self._steps, recalls_used=self._recalls,
            max_steps=self._max_steps, max_recalls=self._max_recalls,
            tried=tuple(self._tried),
            sensable_receptacles=self._context.sensable_receptacle_ids,
            all_locations=self._context.receptacle_ids,
            rooms=self._rooms,
            fallback_receptacle=prediction.argmax,
            last_recall=self._last_recall)

    def _illegal(self, action: StarAction,
                 budget_remaining: float) -> Optional[str]:
        """A human-readable objection, or None when the action is legal."""
        assert self._context is not None
        if isinstance(action, RecallCall):
            if action.tool not in RECALL_TOOLS:
                return f"unknown recall tool {action.tool!r}"
            if self._recalls >= self._max_recalls:
                return (f"recall cap reached "
                        f"({self._max_recalls} per question)")
            if action.tool == "recall_receptacle_history":
                if action.receptacle_id not in self._context.receptacle_ids:
                    return (f"unknown receptacle "
                            f"{action.receptacle_id!r} for recall")
            return None
        if isinstance(action, SenseCall):
            if action.receptacle_id not in self._context.sensable_receptacle_ids:
                return f"cannot sense {action.receptacle_id!r}"
            if action.receptacle_id in self._tried:
                return (f"already sensed {action.receptacle_id!r} "
                        f"this question")
            if budget_remaining <= 0:
                return "no sense budget left"
            return None
        if action.receptacle_id not in self._context.receptacle_ids:
            return f"unknown answer location {action.receptacle_id!r}"
        return None

    def _run_recall(self, question: Question, call: RecallCall) -> None:
        self._steps += 1
        self._recalls += 1
        self._stats["recalls"] += 1
        object_id = call.object_id or question.object_id
        now_t = question.t_query
        if call.tool == "recall_object_history":
            result = recall_object_history(self.memory, object_id, now_t)
            label = f"recall_object_history({object_id})"
        elif call.tool == "recall_receptacle_history":
            assert call.receptacle_id is not None
            result = recall_receptacle_history(self.memory,
                                               call.receptacle_id, now_t)
            label = f"recall_receptacle_history({call.receptacle_id})"
        else:
            result = recall_time_pattern(self.memory, object_id, now_t,
                                         hour_window=call.hour_window)
            label = (f"recall_time_pattern({object_id}, "
                     f"+/-{call.hour_window}h)")
        self._last_recall = result
        self._working_memory.append(f"{label} ->\n{result.text}")

    def _answer(self, receptacle_id: str, by_selector: bool,
                note: str = "", from_fallback: bool = False) -> Action:
        self._steps += 1
        if by_selector:
            self._stats["answered_by_selector"] += 1
            if self._senses == 0 and not from_fallback:
                self._stats["answered_from_memory"] += 1
            self._answer_override = receptacle_id
        else:
            # A found-at-query-instant answer agrees with the belief's
            # one-hot override, so no override is needed; a fallback
            # answer IS the belief argmax by definition.
            self._answer_override = None
        self._working_memory.append(
            f"answer {receptacle_id}" + (f" ({note})" if note else ""))
        return AnswerNow()

    def _fallback(self, reason: str) -> Action:
        self._stats["fallbacks"] += 1
        self._working_memory.append(f"fallback to belief argmax: {reason}")
        return self._answer_via_fallback()

    def _answer_via_fallback(self) -> Action:
        self._answer_override = None
        return AnswerNow()


# --------------------------------------------------- scripted control

class ScriptedRecallThenVerify(ActionSelector):
    """The no-LLM control: recall the object's history, answer a fresh
    sighting outright, otherwise verify recalled locations newest-first.

    Per question: (1) recall the object's history; (2) if the newest
    sighting is younger than ``fresh_age_s``, answer its receptacle;
    (3) otherwise sense the recalled sighting locations newest-first,
    skipping ones already tried this question, until a hit (the loop
    answers a hit by itself) or the budget runs out; (4) with recall
    exhausted, answer the belief's argmax (the loop's fallback window).
    Deterministic; runs offline.
    """

    def __init__(self, fresh_age_s: int = DEFAULT_FRESH_AGE_S) -> None:
        if fresh_age_s < 0:
            raise ValueError(
                f"ScriptedRecallThenVerify: negative fresh_age_s "
                f"{fresh_age_s}")
        self._fresh_age_s = fresh_age_s
        self._question_id: Optional[str] = None
        self._plan: List[str] = []
        self._answered_fresh = False

    @property
    def name(self) -> str:
        return f"ScriptedRecallThenVerify(fresh={self._fresh_age_s}s)"

    def reset(self) -> None:
        self._question_id = None
        self._plan = []
        self._answered_fresh = False

    def select(self, view: LoopView) -> StarAction:
        if self._question_id != view.question.question_id:
            self._question_id = view.question.question_id
            self._plan = []
            self._answered_fresh = False
        if view.recalls_used == 0:
            return RecallCall(tool="recall_object_history",
                              object_id=view.question.object_id)
        if not self._plan and view.last_recall is not None \
                and not self._answered_fresh:
            self._build_plan(view)
        fresh = self._fresh_answer(view)
        if fresh is not None:
            self._answered_fresh = True
            return fresh
        for receptacle in self._plan:
            if receptacle in view.tried:
                continue
            if receptacle not in view.sensable_receptacles:
                continue
            if view.budget_remaining <= 0:
                break
            return SenseCall(receptacle_id=receptacle)
        return AnswerCall(receptacle_id=view.fallback_receptacle,
                          from_fallback=True)

    def _build_plan(self, view: LoopView) -> None:
        """Distinct positive-sighting receptacles, newest-first."""
        assert view.last_recall is not None
        seen: List[str] = []
        for record in view.last_recall.records:
            if record.present and record.receptacle_id not in seen:
                seen.append(record.receptacle_id)
        self._plan = seen

    def _fresh_answer(self, view: LoopView) -> Optional[AnswerCall]:
        if view.last_recall is None or view.recalls_used != 1 \
                or view.steps_used != 1:
            return None
        newest = freshest_sighting(view.last_recall.records)
        if newest is None:
            return None
        age_s = view.question.t_query - newest.t
        if age_s < self._fresh_age_s:
            return AnswerCall(receptacle_id=newest.receptacle_id)
        return None


# --------------------------------------------------------- the LLM

GenerateFn = Callable[[str, str, Dict[str, object], int], str]
"""(system, user, json_schema, seed) -> raw completion text. The study
wires this to a served vLLM endpoint with structured output and a prompt
cache (:mod:`baselines.memory.serving`); tests inject a stub."""

ACTION_SCHEMA: Dict[str, object] = {
    "type": "object",
    "properties": {
        "action": {"type": "string",
                   "enum": list(RECALL_TOOLS) + ["sense", "answer"]},
        "args": {
            "type": "object",
            "properties": {
                "object_id": {"type": "string"},
                "receptacle_id": {"type": "string"},
                "hour_window": {"type": "integer",
                                "minimum": 0, "maximum": 6},
            },
            "additionalProperties": False,
        },
    },
    "required": ["action", "args"],
    "additionalProperties": False,
}
"""Structured-output grammar for one action, enforced server-side the
same way the generation client enforces its schemas."""

_SYSTEM_PROMPT = (
    "You are a household robot answering one question about where an "
    "object is RIGHT NOW. Each step you take exactly one action:\n"
    "- recall_object_history(object_id): read your memory of that "
    "object's past sightings and absences (free);\n"
    "- recall_receptacle_history(receptacle_id): read what you have "
    "seen at that receptacle (free);\n"
    "- recall_time_pattern(object_id, hour_window): where that object "
    "was seen around this hour on previous days (free);\n"
    "- sense(receptacle_id): physically look inside one receptacle "
    "(costs 1 from a limited budget; reveals its full true contents);\n"
    "- answer(receptacle_id): commit to a final location, ending the "
    "question. Answer OUT_OF_HOUSE if you believe the object is not in "
    "the house (it cannot be sensed, only inferred).\n"
    "Recalled memory can be stale: objects move. Prefer recalling "
    "before sensing, sense only where it may settle the question, and "
    "answer as soon as you are confident. Respond with EXACTLY ONE "
    "action as JSON: {\"action\": ..., \"args\": {...}}.")


class QwenSelector(ActionSelector):
    """The LLM selector: one served-model call per step.

    Builds a prompt from the view (question, receptacles grouped by
    room, working memory, remaining budget as a number, the action
    menu), requires a single JSON action back (``ACTION_SCHEMA``,
    enforced with the server's structured-output path), and maps it to
    a :class:`StarAction`. Unparseable output raises
    :class:`SelectorError`; the loop owns rejection lines, the single
    retry and the argmax fallback. Deliberately blind to the belief:
    it never reads ``view.fallback_receptacle`` or ``view.last_recall``.
    """

    def __init__(self, generate: GenerateFn, seed: int = 0) -> None:
        self._generate = generate
        self._seed = seed
        self.calls = 0

    @property
    def name(self) -> str:
        return "QwenSelector"

    def reset(self) -> None:
        self.calls = 0

    def select(self, view: LoopView) -> StarAction:
        self.calls += 1
        raw = self._generate(_SYSTEM_PROMPT, self._user_prompt(view),
                             ACTION_SCHEMA, self._seed)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as err:
            raise SelectorError(f"invalid JSON: {err}") from err
        if not isinstance(payload, dict):
            raise SelectorError(f"expected an object, got {type(payload)}")
        action = payload.get("action")
        args = payload.get("args")
        if not isinstance(action, str) or not isinstance(args, dict):
            raise SelectorError(f"malformed action payload: {raw[:200]}")
        return self._to_action(view, action, args)

    def _to_action(self, view: LoopView, action: str,
                   args: Dict[str, object]) -> StarAction:
        receptacle = args.get("receptacle_id")
        object_id = args.get("object_id")
        if action in RECALL_TOOLS:
            hour_window = args.get("hour_window", 1)
            return RecallCall(
                tool=action,
                object_id=(str(object_id) if object_id is not None
                           else view.question.object_id),
                receptacle_id=(str(receptacle) if receptacle is not None
                               else None),
                hour_window=(int(hour_window)
                             if isinstance(hour_window, int) else 1))
        if action == "sense":
            if receptacle is None:
                raise SelectorError("sense without a receptacle_id")
            return SenseCall(receptacle_id=str(receptacle))
        if action == "answer":
            if receptacle is None:
                raise SelectorError("answer without a receptacle_id")
            return AnswerCall(receptacle_id=str(receptacle))
        raise SelectorError(f"unknown action {action!r}")

    def _user_prompt(self, view: LoopView) -> str:
        q = view.question
        day = q.t_query // 86_400
        hour = (q.t_query % 86_400) / 3600.0
        by_room: Dict[str, List[str]] = {}
        for receptacle in view.all_locations:
            room = view.rooms.get(receptacle, "(no room)")
            by_room.setdefault(room, []).append(receptacle)
        room_lines = [
            f"  {room}: {', '.join(receptacles)}"
            for room, receptacles in sorted(by_room.items())]
        unsensable = [r for r in view.all_locations
                      if r not in view.sensable_receptacles]
        memory_lines = ("\n".join(view.working_memory)
                        if view.working_memory else "(empty)")
        recalls_left = view.max_recalls - view.recalls_used
        return (
            f"QUESTION: Where is {q.object_id} (a {view.object_class}) "
            f"right now? It is day {day}, hour {hour:.1f}.\n\n"
            f"RECEPTACLES BY ROOM:\n" + "\n".join(room_lines) + "\n"
            f"Answer-only locations (cannot be sensed): "
            f"{', '.join(unsensable) if unsensable else '(none)'}\n\n"
            f"WORKING MEMORY (this question so far):\n{memory_lines}\n\n"
            f"REMAINING SENSE BUDGET TODAY: {view.budget_remaining}\n"
            f"Recalls left this question: {recalls_left}. "
            f"Already sensed this question: "
            f"{', '.join(view.tried) if view.tried else '(none)'}.\n"
            f"Choose one action.")
