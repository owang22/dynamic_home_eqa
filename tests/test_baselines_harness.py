"""Harness invariants: determinism, ground-truth isolation, budget rules."""

from __future__ import annotations

import json
import pathlib
import random

from baselines.agent import Agent
from baselines.bank import write_synthetic_bank
from baselines.beliefs import LastObservation
from baselines.harness import run_episode
from baselines.policies import AlwaysSense, NeverSense
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, EpisodeContext, Episode, Prediction,
                             Question, Sense)


def _episode(tmp_path: pathlib.Path) -> Episode:
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    return next(bank.episodes())


def _run_log(episode: Episode, seed: int) -> str:
    agent = Agent(belief=LastObservation(random.Random(seed)),
                  policy=AlwaysSense())
    records = [r.to_json_dict() for r in run_episode(agent, episode)]
    return "\n".join(json.dumps(r) for r in records)


def test_same_seed_gives_byte_identical_run_logs(tmp_path: pathlib.Path) -> None:
    episode = _episode(tmp_path)
    assert _run_log(episode, seed=7) == _run_log(episode, seed=7)


def test_agent_view_exposes_no_ground_truth(tmp_path: pathlib.Path) -> None:
    # Isolation is structural: the context type simply lacks the accessors.
    view = _episode(tmp_path).agent_view()
    assert isinstance(view, EpisodeContext)
    assert not hasattr(view, "true_location")
    assert not hasattr(view, "receptacle_contents")
    assert not hasattr(view, "trajectories")


class _GreedySensor(DecisionPolicy):
    """Pathological policy that asks to sense forever; the harness must
    still terminate every question by exhausting the budget."""

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int) -> Action:
        return Sense(receptacle_id=prediction.argmax)


def test_budget_exhaustion_forces_answer(tmp_path: pathlib.Path) -> None:
    episode = _episode(tmp_path)  # budget_per_day == 2
    agent = Agent(belief=LastObservation(random.Random(0)),
                  policy=_GreedySensor())
    records = list(run_episode(agent, episode))
    by_day: dict[tuple[str, int], int] = {}
    for r in records:
        by_day[(r.episode_id, r.day_index)] = \
            by_day.get((r.episode_id, r.day_index), 0) + r.budget_spent
    # Never more than the day's budget, and the greedy policy always drains it.
    assert all(spent == episode.budget_per_day for spent in by_day.values())
    # Once drained, questions are answered by force and flagged as such.
    forced = [r for r in records if r.forced_answer]
    assert forced, "greedy policy should hit forced answers"
    assert all(r.budget_after == 0 for r in forced)
    assert all(r.actions[-1]["type"] == "forced_answer" for r in forced)


def test_budget_accounting_is_per_question_and_recorded(
        tmp_path: pathlib.Path) -> None:
    episode = _episode(tmp_path)
    agent = Agent(belief=LastObservation(random.Random(0)),
                  policy=AlwaysSense())
    records = list(run_episode(agent, episode))
    for r in records:
        assert r.budget_before - r.budget_spent == r.budget_after
        assert 0 <= r.budget_spent <= 1  # AlwaysSense caps at one per question


def test_information_diet_is_identical_across_agents(
        tmp_path: pathlib.Path) -> None:
    # Two agents that never sense must see identical predictions per
    # question: the prediction is a pure function of the shared stream.
    episode = _episode(tmp_path)
    logs = []
    for _ in range(2):
        agent = Agent(belief=LastObservation(random.Random(3)),
                      policy=NeverSense())
        logs.append([(r.question_id, r.distribution)
                     for r in run_episode(agent, episode)])
    assert logs[0] == logs[1]
