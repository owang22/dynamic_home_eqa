"""Episode runner: replays a bank against an agent under the study's rules.

The harness owns everything that protects result validity:

* **Identical observation streams** — every agent gets the identical stream: the initial
  tour, then per question all scripted observations with ``t <= t_query``
  not yet delivered, in time order. Sensing is the only divergence. The
  passive patrol is FIXED and agent-independent: it does not react to
  where a policy has sent the robot (see "Robot position" below).
* **Budget accounting** — the harness decrements the per-day budget by the
  sense's COST, refuses a ``Sense`` it cannot afford (forcing an answer,
  flagged in the log), and records per-question spend. Policies only ever
  read ``budget_remaining``.
* **Robot position and travel cost** — the harness tracks which room the
  robot is in and prices each sense from it: 1.0 for a receptacle in the
  current room, ``1 + room_change_cost`` for one anywhere else. Position
  is ``home_base_room`` at the start of every day, moves to the room of
  every ambient room visit delivered up to the question's ``t_query``,
  and moves to the room of every receptacle actively sensed. The live
  position rides on the :class:`~baselines.types.EpisodeContext` the
  agent was reset with, so policies read the price through
  ``context.sense_cost(receptacle_id)`` without the harness widening the
  ``decide`` signature. At ``room_change_cost = 0`` (the default) every
  sense costs 1 and the accounting is exactly what it was before.
* **Sensability** — a bank may declare receptacles unsensable (legal
  answers that can only be inferred, e.g. OUT_OF_HOUSE). Sensing one is a
  policy contract violation and raises loudly — it is never silently
  refused, because a policy that tries has misread its context.
* **Person sensing** — on a bank whose header declares ``person_sensing``
  every receptacle sense result also lists the residents in that
  receptacle's room at ``t_query`` (``residents_present``), and a policy
  may return :class:`~baselines.types.SensePerson` for a resident an
  earlier sense of the SAME question listed. The result is a
  :class:`~baselines.types.PersonSenseResult`: everything that resident
  carries at ``t_query``, at ``ON_PERSON``. It costs the same-room price
  (1.0), leaves the robot where it is, and is logged as a ``sense_person``
  action. A person sense for a resident no sense of this question has
  listed is a contract violation and raises, exactly like an unsensable
  receptacle; on a bank without ``person_sensing`` every person sense
  raises. ``ON_PERSON`` and ``OUT_OF_HOUSE`` remain answer tokens no
  :class:`~baselines.types.Sense` may target.
* **Ground-truth isolation** — agents are reset with
  :meth:`~baselines.types.Episode.agent_view`, which has no ground-truth
  accessor; only harness code touches ``true_location``.
* **Scoring** — exact receptacle_id match against
  ``true_location(object_id, t_query)``. No aliasing here by contract.
* **Full-state scoring** — after each question is resolved, the harness
  snapshots the belief's argmax for EVERY object and scores each against
  ground truth at that instant (``belief_state`` in the record). This is
  the probe set nothing can game: sensing cannot react to it because the
  agent never learns it is being scored on it. Task accuracy (queried
  objects only) minus belief accuracy (all objects) measures how much a
  policy steers its budget toward what gets asked. Snapshots use
  ``predict_readonly`` (tie-break generator state restored afterwards), so
  scoring a never-observed object cannot perturb the agent's own later
  fallback answers — banks without an initial tour stay clean.
* **Logging** — one JSON-serializable record per question with the full
  prediction, every action and sense result, the answer, correctness,
  budget movement, and the full-state snapshot, sufficient to replay/debug
  a run from the log alone.

All times are seconds since episode start.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Dict, Iterator, List, Optional, Tuple, Union

from baselines.agent import Agent
from baselines.types import (DAY_SECONDS, ON_PERSON, Answer, AnswerNow,
                             Episode, EpisodeContext, Observation,
                             PersonSenseResult, Question, RobotPosition,
                             Sense, SensePerson, SenseResult)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QuestionRecord:
    """Everything that happened for one question (one run-log line).

    ``actions`` holds one entry per policy decision in order; sense entries
    embed the returned contents, the room sensed and what the sense cost
    (plus ``residents_present`` on a person-sensing bank), and
    ``sense_person`` entries the resident, their room, what they carried
    and the cost. ``forced_answer`` marks that the policy asked to sense
    and was overruled because the remaining budget could not cover that
    sense's cost.

    The three budget fields are floats: a sense costs 1.0 in the robot's
    current room and ``1 + room_change_cost`` elsewhere, so spend is
    fractional whenever that surcharge is not a whole number.
    ``budget_spent`` is therefore a COST, not a count; ``n_senses`` is
    the count.
    """

    episode_id: str
    household_id: str
    agent: str
    belief: str
    policy: str
    day_index: int
    question_id: str
    object_id: str
    object_class: str
    t_query: int
    distribution: Dict[str, float]
    actions: Tuple[Dict[str, object], ...]
    answer_receptacle: str
    confidence: float
    truth_receptacle: str
    correct: bool
    budget_before: float
    budget_spent: float
    budget_after: float
    forced_answer: bool
    # Full-state snapshot after this question resolved:
    # object_id -> [object_class, predicted argmax, correct]. The queried
    # object appears here too (post-sense state, same as the answer).
    belief_state: Dict[str, Tuple[str, str, bool]]
    belief_accuracy: float
    # Room-change cost bookkeeping. ``n_senses`` counts senses where
    # ``budget_spent`` sums their costs; ``same_room_senses`` counts those
    # that needed no room change; ``robot_room_at_query`` is where the
    # robot stood when the question arrived, before any of its own senses.
    # Defaults keep run logs written before the room-cost model loadable.
    n_senses: int = 0
    same_room_senses: int = 0
    robot_room_at_query: Optional[str] = None

    def to_json_dict(self) -> Dict[str, object]:
        """Plain-dict form for JSONL writing."""
        return asdict(self)


def _stream_until(evidence: Tuple[Union[Observation, SenseResult], ...],
                  cursor: int, t: int, agent: Agent,
                  episode: Episode, position: RobotPosition) -> int:
    """Deliver ambient evidence with ``.t <= t``; return the new cursor.

    Evidence is what :meth:`Episode.evidence_stream` yields: plain
    observations for glimpse banks, per-receptacle sense results for
    room-visit banks (whose emptiness is negative evidence the belief
    base class already understands).

    A room-visit sense result also MOVES the robot: the patrol is where
    the robot physically is between questions. A glimpse ``Observation``
    does not — it is a disembodied sighting, not a visit.
    """
    while cursor < len(evidence) and evidence[cursor].t <= t:
        item = evidence[cursor]
        agent.observe(item)
        if isinstance(item, SenseResult):
            room = episode.receptacle_rooms.get(item.receptacle_id)
            if room is not None:
                position.room = room
        cursor += 1
    return cursor


def run_episode(agent: Agent, episode: Episode,
                room_change_cost: float = 0.0) -> Iterator[QuestionRecord]:
    """Replay one episode against one agent, yielding one record per question.

    ``room_change_cost`` (``c``) prices a sense outside the robot's
    current room at ``1 + c`` against 1.0 inside it; at the default 0.0
    every sense costs 1 and this is the flat-budget model unchanged.

    The per-question decision loop is bounded by
    ``len(sensable_receptacle_ids)`` senses (plus one per resident on a
    person-sensing bank) — a receptacle or resident may not be sensed
    twice within one question, so that is already an upper bound on any
    well-behaved policy, and it terminates under fractional costs where
    a budget-derived bound would not.
    """
    if room_change_cost < 0.0:
        raise ValueError(f"run_episode: room_change_cost {room_change_cost} "
                         f"must be >= 0")
    position = RobotPosition(room=episode.home_base_room)
    context = episode.agent_view(room_change_cost, position)
    agent.reset(context)
    for obs in episode.initial_observations:
        agent.observe(obs)

    cursor = 0
    evidence = episode.evidence_stream()
    for day_index, day_questions in enumerate(episode.questions_by_day):
        # Deliver everything that happened before this day begins, THEN
        # put the robot back at its home base: the reset is an event at
        # the day boundary, so a late visit from yesterday must not
        # outlive it. Delivery order to the belief is unchanged.
        cursor = _stream_until(evidence, cursor, day_index * DAY_SECONDS - 1,
                               agent, episode, position)
        position.room = episode.home_base_room
        budget = float(episode.budget_per_day)
        for question in day_questions:
            cursor = _stream_until(evidence, cursor, question.t_query, agent,
                                   episode, position)
            record = _run_question(agent, episode, question, day_index,
                                   budget, context, position)
            budget = record.budget_after
            yield record


def _run_question(agent: Agent, episode: Episode, question: Question,
                  day_index: int, budget: float, context: EpisodeContext,
                  position: RobotPosition) -> QuestionRecord:
    """Decision loop for a single question; returns its full record."""
    budget_before = budget
    actions: List[Dict[str, object]] = []
    forced = False
    last_sense: SenseResult | None = None
    room_at_query = position.room
    n_senses = same_room_senses = 0
    max_senses = len(context.sensable_receptacle_ids)
    if episode.person_sensing:
        max_senses += len(episode.resident_ids)
    # Residents listed by this question's receptacle senses -> the room
    # they were listed in. A person sense is legal only for a listed
    # resident: the listing is how the robot knows where they are.
    listed: Dict[str, Optional[str]] = {}
    object_class = (question.object_class
                    or episode.object_classes.get(question.object_id, ""))
    agent.belief.ensure_object(question.object_id, object_class)

    while True:
        prediction = agent.predict(question)
        action = agent.decide(question, prediction, budget, last_sense)
        if isinstance(action, AnswerNow):
            actions.append({"type": "answer"})
            break
        if isinstance(action, SensePerson):
            target: str = action.resident_id
            if not episode.person_sensing:
                raise ValueError(
                    f"{agent.name} asked to sense resident {target!r} on "
                    f"{question.question_id}, but the bank declares no "
                    f"person_sensing — policies read it off their context")
            if target not in listed:
                raise ValueError(
                    f"{agent.name} asked to sense resident {target!r} on "
                    f"{question.question_id} before any sense of this "
                    f"question listed them — a resident can be looked at "
                    f"only after a look in the room they are in")
            cost = 1.0                    # the same-room price; no travel
            room = listed[target]
        else:
            assert isinstance(action, Sense)
            target = action.receptacle_id
            if target in episode.unsensable_receptacle_ids:
                raise ValueError(
                    f"{agent.name} asked to sense unsensable receptacle "
                    f"{target!r} on {question.question_id} — "
                    f"policies receive the sensable set in their context and "
                    f"must never target an unsensable one")
            cost = context.sense_cost(target)
            room = episode.receptacle_rooms.get(target)
        if cost > budget:
            forced = True
            actions.append({"type": "forced_answer",
                            "refused_sense": target,
                            "cost": cost, "budget_remaining": budget})
            break
        if n_senses >= max_senses:
            # Unreachable for a policy that senses each receptacle at most
            # once per question (every policy in the roster does); the
            # bound exists so no policy can loop forever under fractional
            # costs, where "budget runs out" is not a step bound.
            logger.warning("%s %s: sense-step cap %d reached; forcing an "
                           "answer", agent.name, question.question_id,
                           max_senses)
            forced = True
            actions.append({"type": "step_cap_answer",
                            "refused_sense": target})
            break
        budget -= cost
        n_senses += 1
        if isinstance(action, SensePerson):
            same_room_senses += 1
            contents = episode.carried_objects(target, question.t_query)
            result: SenseResult = PersonSenseResult(
                receptacle_id=ON_PERSON, t=question.t_query,
                contents=contents,
                object_classes={obj: episode.object_classes.get(obj, "")
                                for obj in contents},
                resident_id=target, room=room)
            entry: Dict[str, object] = {
                "type": "sense_person", "resident_id": target,
                "room": room, "contents": list(contents), "cost": cost}
        else:
            same_room = room is not None and room == position.room
            same_room_senses += int(same_room)
            contents = episode.receptacle_contents(target, question.t_query)
            present = (episode.residents_in_room(room, question.t_query)
                       if episode.person_sensing else ())
            result = SenseResult(receptacle_id=target, t=question.t_query,
                                 contents=contents,
                                 object_classes={
                                     obj: episode.object_classes.get(obj, "")
                                     for obj in contents},
                                 residents_present=present)
            entry = {"type": "sense", "receptacle_id": target,
                     "contents": list(contents), "room": room,
                     "cost": cost, "same_room": same_room}
            if episode.person_sensing:
                entry["residents_present"] = list(present)
                for res in present:
                    listed[res] = room
            if room is not None:
                position.room = room  # the robot travelled there to look
        for obj in contents:
            agent.belief.ensure_object(
                obj, episode.object_classes.get(obj, ""))
        agent.observe(result)
        last_sense = result
        actions.append(entry)

    answer = Answer(question_id=question.question_id,
                    predicted_receptacle_id=prediction.argmax,
                    confidence=prediction.confidence,
                    budget_spent=budget_before - budget)
    truth = episode.true_location(question.object_id, question.t_query)

    belief_state: Dict[str, Tuple[str, str, bool]] = {}
    for obj, obj_class in sorted(episode.object_classes.items()):
        # The queried object's snapshot IS the answer: re-predicting could
        # break a floor-level tie differently and desync the snapshot
        # from the recorded answer.
        guess = (prediction.argmax if obj == question.object_id
                 else agent.belief.predict_readonly(obj, question.t_query).argmax)
        belief_state[obj] = (
            obj_class, guess,
            guess == episode.true_location(obj, question.t_query))
    belief_accuracy = (sum(ok for _, _, ok in belief_state.values())
                       / len(belief_state))
    record = QuestionRecord(
        episode_id=episode.episode_id, household_id=episode.household_id,
        agent=agent.name, belief=agent.belief.name, policy=agent.policy.name,
        day_index=day_index, question_id=question.question_id,
        object_id=question.object_id,
        object_class=object_class,
        t_query=question.t_query,
        distribution=dict(prediction.distribution),
        actions=tuple(actions),
        answer_receptacle=answer.predicted_receptacle_id,
        confidence=answer.confidence,
        truth_receptacle=truth,
        correct=answer.predicted_receptacle_id == truth,
        budget_before=budget_before, budget_spent=answer.budget_spent,
        budget_after=budget, forced_answer=forced,
        belief_state=belief_state, belief_accuracy=belief_accuracy,
        n_senses=n_senses, same_room_senses=same_room_senses,
        robot_room_at_query=room_at_query)
    logger.debug("%s %s: %s (truth %s) spent=%g", agent.name,
                 question.question_id, answer.predicted_receptacle_id,
                 truth, answer.budget_spent)
    return record
