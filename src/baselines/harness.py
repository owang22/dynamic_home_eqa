"""Episode runner: replays a bank against an agent under the study's rules.

The harness owns everything that protects result validity:

* **Information diet** — every agent gets the identical stream: the initial
  tour, then per question all scripted observations with ``t <= t_query``
  not yet delivered, in time order. Sensing is the only divergence.
* **Budget accounting** — the harness decrements the per-day budget,
  refuses ``Sense`` at zero (forcing an answer, flagged in the log), and
  records per-question spend. Policies only ever read ``budget_remaining``.
* **Ground-truth isolation** — agents are reset with
  :meth:`~baselines.types.Episode.agent_view`, which has no ground-truth
  accessor; only harness code touches ``true_location``.
* **Scoring** — exact receptacle_id match against
  ``true_location(object_id, t_query)``. No aliasing here by contract.
* **Logging** — one JSON-serializable record per question with the full
  prediction, every action and sense result, the answer, correctness, and
  budget movement, sufficient to replay/debug a run from the log alone.

All times are seconds since episode start.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Dict, Iterator, List, Tuple

from baselines.agent import Agent
from baselines.types import (Answer, AnswerNow, Episode, Observation,
                             Question, Sense, SenseResult)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QuestionRecord:
    """Everything that happened for one question (one run-log line).

    ``actions`` holds one entry per policy decision in order; sense entries
    embed the returned contents. ``forced_answer`` marks that the policy
    asked to sense with zero budget and was overruled.
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
    budget_before: int
    budget_spent: int
    budget_after: int
    forced_answer: bool

    def to_json_dict(self) -> Dict[str, object]:
        """Plain-dict form for JSONL writing."""
        return asdict(self)


def _stream_until(observations: Tuple[Observation, ...], cursor: int,
                  t: int, agent: Agent) -> int:
    """Deliver scripted observations with ``obs.t <= t``; return new cursor."""
    while cursor < len(observations) and observations[cursor].t <= t:
        agent.observe(observations[cursor])
        cursor += 1
    return cursor


def run_episode(agent: Agent, episode: Episode) -> Iterator[QuestionRecord]:
    """Replay one episode against one agent, yielding one record per question.

    The per-question decision loop is bounded: each iteration either
    consumes one budget unit (a sense) or terminates (an answer / a forced
    answer), so it runs at most ``budget_remaining + 1`` times regardless
    of policy behaviour.
    """
    agent.reset(episode.agent_view())
    for obs in episode.initial_observations:
        agent.observe(obs)

    cursor = 0
    for day_index, day_questions in enumerate(episode.questions_by_day):
        budget = episode.budget_per_day
        for question in day_questions:
            cursor = _stream_until(
                episode.scripted_observations, cursor, question.t_query, agent)
            record = _run_question(agent, episode, question, day_index, budget)
            budget = record.budget_after
            yield record


def _run_question(agent: Agent, episode: Episode, question: Question,
                  day_index: int, budget: int) -> QuestionRecord:
    """Decision loop for a single question; returns its full record."""
    budget_before = budget
    actions: List[Dict[str, object]] = []
    forced = False

    while True:
        prediction = agent.predict(question)
        action = agent.decide(question, prediction, budget)
        if isinstance(action, AnswerNow):
            actions.append({"type": "answer"})
            break
        assert isinstance(action, Sense)
        if budget <= 0:
            forced = True
            actions.append({"type": "forced_answer",
                            "refused_sense": action.receptacle_id})
            break
        budget -= 1
        contents = episode.receptacle_contents(
            action.receptacle_id, question.t_query)
        result = SenseResult(receptacle_id=action.receptacle_id,
                             t=question.t_query, contents=contents)
        agent.observe(result)
        actions.append({"type": "sense", "receptacle_id": action.receptacle_id,
                        "contents": list(contents)})

    answer = Answer(question_id=question.question_id,
                    predicted_receptacle_id=prediction.argmax,
                    confidence=prediction.confidence,
                    budget_spent=budget_before - budget)
    truth = episode.true_location(question.object_id, question.t_query)
    record = QuestionRecord(
        episode_id=episode.episode_id, household_id=episode.household_id,
        agent=agent.name, belief=agent.belief.name, policy=agent.policy.name,
        day_index=day_index, question_id=question.question_id,
        object_id=question.object_id,
        object_class=episode.object_classes[question.object_id],
        t_query=question.t_query,
        distribution=dict(prediction.distribution),
        actions=tuple(actions),
        answer_receptacle=answer.predicted_receptacle_id,
        confidence=answer.confidence,
        truth_receptacle=truth,
        correct=answer.predicted_receptacle_id == truth,
        budget_before=budget_before, budget_spent=answer.budget_spent,
        budget_after=budget, forced_answer=forced)
    logger.debug("%s %s: %s (truth %s) spent=%d", agent.name,
                 question.question_id, answer.predicted_receptacle_id,
                 truth, answer.budget_spent)
    return record
