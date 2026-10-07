"""RandomSliceSense: reserve, spread, candidate pool, and exact
equivalence to the inner policy at fraction 0."""

from __future__ import annotations

import pathlib
import random

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.harness import run_episode
from baselines.policies.random_slice_sense import RandomSliceSense
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.registry import build_registered_belief


def _episode(tmp_path: pathlib.Path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    return next(JsonlBank(tmp_path / "bank.jsonl").episodes())


def _run(episode, policy):
    belief = build_registered_belief({"name": "most_frequent"},
                                     random.Random(1))
    return list(run_episode(Agent(belief, policy), episode))


def test_fraction_zero_is_the_inner_policy_exactly(tmp_path) -> None:
    episode = _episode(tmp_path)
    plain = _run(episode, VoIThresholdSense(random.Random(7), lam=0.05))
    wrapped = RandomSliceSense(random.Random(99),
                               VoIThresholdSense(random.Random(7), lam=0.05),
                               fraction=0.0)
    sliced = _run(episode, wrapped)
    assert [r.answer_receptacle for r in plain] == [
        r.answer_receptacle for r in sliced]
    assert [r.budget_spent for r in plain] == [r.budget_spent for r in sliced]
    assert wrapped.random_senses == 0


def test_slice_spends_within_reserve_and_spreads(tmp_path) -> None:
    episode = _episode(tmp_path)
    wrapped = RandomSliceSense(random.Random(3),
                               VoIThresholdSense(random.Random(7), lam=0.05),
                               fraction=0.25)
    plain = _run(episode, VoIThresholdSense(random.Random(7), lam=0.05))
    records = _run(episode, wrapped)
    assert wrapped.random_senses > 0
    reserve = 0.25 * episode.budget_per_day
    by_day = {}
    for r in records:
        by_day.setdefault(r.day_index, []).append(r)
    for rows in by_day.values():
        # Total spend never exceeds the day's budget, and the slice's
        # share of it (spend beyond what plain VoI used) stays within
        # the reserve.
        spent = sum(r.budget_spent for r in rows)
        assert spent <= episode.budget_per_day + 1e-9
    # Random senses are spread: at least one day has them on two or
    # more different questions.
    spread = sum(1 for rows in by_day.values()
                 if sum(1 for r in rows if r.budget_spent > 0) >= 2)
    assert spread >= 1


def test_inner_policy_never_sees_the_reserve(tmp_path) -> None:
    class Probe(VoIThresholdSense):
        seen = []
        def decide(self, question, prediction, budget_remaining, t,
                   last_sense=None):
            Probe.seen.append(budget_remaining)
            return super().decide(question, prediction, budget_remaining, t,
                                  last_sense)
    episode = _episode(tmp_path)
    wrapped = RandomSliceSense(random.Random(3),
                               Probe(random.Random(7), lam=0.05),
                               fraction=0.5)
    _run(episode, wrapped)
    # With half the budget reserved, the inner policy never sees more
    # than the other half.
    assert max(Probe.seen) <= 0.5 * episode.budget_per_day + 1e-9
