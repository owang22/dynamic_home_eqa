"""Tests for the hypothesis-mixture belief and the disambiguation-sensing
policy: weight normalization, bad particles losing weight, the forgetting
factor, single-particle equivalence, and beta = 0 reproducing the myopic
VoI policy exactly. Times are seconds since episode start."""

from __future__ import annotations

import math
import pathlib
import random

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.beliefs.hypothesis_mixture import HypothesisMixture
from baselines.harness import run_episode
from baselines.policies.hypothesis_disambiguation import (
    HypothesisDisambiguationSense, entropy, weight_entropy_reduction)
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.registry import build_registered_belief
from baselines.types import EpisodeContext, Observation, Prediction

H = 3600
RECS = ("a", "b", "c", "d")
TWO_PARTICLES = ({"name": "last_observation"},
                 {"name": "most_frequent", "half_life_h": 24.0})


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes={"o": "mug"}, budget_per_day=2, n_days=10)


def _obs(rec: str, t: int) -> Observation:
    return Observation(object_id="o", object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _mixture(**kwargs: object) -> HypothesisMixture:
    model = HypothesisMixture(random.Random(0), **kwargs)  # type: ignore[arg-type]
    model.reset(_context())
    return model


def _episode(tmp_path: pathlib.Path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    return next(JsonlBank(tmp_path / "bank.jsonl").episodes())


def test_weights_stay_normalized_and_finite_over_an_episode(
        tmp_path) -> None:
    episode = _episode(tmp_path)
    model = HypothesisMixture(random.Random(0))
    model.reset(episode.agent_view())
    for obs in episode.initial_observations:
        model.update(obs)
    for evidence in episode.evidence_stream():
        model.update(evidence)
    weights = model.weights
    assert all(math.isfinite(w) and w >= 0.0 for w in weights)
    assert sum(weights) == pytest.approx(1.0)
    assert model.ess_history       # weights actually moved


def test_a_badly_predicting_particle_loses_weight() -> None:
    # last_observation keeps betting on the previous receptacle while the
    # object alternates; most_frequent hedges across both and scores the
    # observed receptacle higher on average.
    model = _mixture(particle_specs=TWO_PARTICLES)
    for step in range(20):
        model.update(_obs("a" if step % 2 else "b", step * H))
    w_last_obs, w_most_frequent = model.weights
    assert w_most_frequent > 0.7
    assert w_last_obs < 0.3


def test_decay_one_collapses_and_the_default_keeps_ess_above_one(
        tmp_path) -> None:
    episode = _episode(tmp_path)

    def final_ess(decay: float) -> float:
        model = HypothesisMixture(random.Random(0), decay=decay)
        model.reset(episode.agent_view())
        for obs in episode.initial_observations:
            model.update(obs)
        for evidence in episode.evidence_stream():
            model.update(evidence)
        return model.effective_sample_size

    collapsed = final_ess(1.0)
    tempered = final_ess(HypothesisMixture(random.Random(0)).decay)
    assert collapsed == pytest.approx(1.0, abs=0.05)
    assert tempered > 1.2
    assert tempered > collapsed


def test_single_particle_mixture_predicts_as_the_particle() -> None:
    spec = {"name": "most_frequent", "half_life_h": 24.0}
    mixture = _mixture(particle_specs=(spec,))
    solo = build_registered_belief(dict(spec), random.Random(1))
    solo.reset(_context())
    for rec, t in (("a", 0), ("b", H), ("a", 2 * H)):
        mixture.update(_obs(rec, t))
        solo.update(_obs(rec, t))
    ours = mixture.predict("o", 5 * H)
    theirs = solo.predict("o", 5 * H)
    assert ours.argmax == theirs.argmax
    for rec in RECS:
        assert ours.distribution[rec] == pytest.approx(
            theirs.distribution[rec], abs=1e-9)


def test_entropy_reduction_is_positive_iff_particles_disagree() -> None:
    weights = [0.5, 0.5]
    assert weight_entropy_reduction(weights, [0.9, 0.1]) > 0.0
    assert weight_entropy_reduction(weights, [0.4, 0.4]) == pytest.approx(
        0.0, abs=1e-12)
    assert entropy([1.0]) == 0.0
    assert entropy([0.5, 0.5]) == pytest.approx(math.log(2))


def test_beta_zero_reproduces_the_myopic_voi_policy_exactly(
        tmp_path) -> None:
    episode = _episode(tmp_path)

    def records(policy_kind: str):
        belief = HypothesisMixture(random.Random(7),
                                   particle_specs=TWO_PARTICLES)
        rng = random.Random(13)
        policy = (VoIThresholdSense(rng, lam=0.05)
                  if policy_kind == "myopic" else
                  HypothesisDisambiguationSense(rng, lam=0.05,
                                                belief=belief, beta=0.0))
        return list(run_episode(Agent(belief=belief, policy=policy), episode))

    myopic = records("myopic")
    disambiguation = records("disambiguation")
    assert len(myopic) == len(disambiguation)
    for a, b in zip(myopic, disambiguation):
        assert a.actions == b.actions
        assert a.answer_receptacle == b.answer_receptacle
        assert a.correct == b.correct
        assert a.budget_spent == b.budget_spent


def test_positive_beta_can_only_add_senses_and_flags_them(tmp_path) -> None:
    episode = _episode(tmp_path)
    belief = HypothesisMixture(random.Random(7),
                               particle_specs=TWO_PARTICLES)
    policy = HypothesisDisambiguationSense(random.Random(13), lam=0.05,
                                           belief=belief, beta=5.0)
    records = list(run_episode(Agent(belief=belief, policy=policy), episode))
    assert records
    assert len(policy.sense_split) == sum(r.n_senses for r in records)
    # At a beta this large some sense must have been taken for
    # disambiguation alone.
    assert any(not needed for _, needed in policy.sense_split)
