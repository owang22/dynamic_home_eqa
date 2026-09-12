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
from baselines.types import EpisodeContext, Observation, SenseResult

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


def _sense(receptacle: str, t: int, contents: tuple[str, ...]) -> SenseResult:
    return SenseResult(receptacle_id=receptacle, t=t, contents=contents,
                       object_classes={o: "mug" for o in contents})


def test_absence_punishes_a_confident_false_positive() -> None:
    # Both particles are told the mug is at "a"; only last_observation
    # then insists on it. A look at "a" that comes back empty must cost
    # the insistent particle far more than the hedging one.
    model = _mixture(particle_specs=TWO_PARTICLES, absence_weight=1.0)
    model.update(_obs("a", 0))
    model.update(_obs("b", H))
    model.update(_obs("a", 2 * H))
    before = model.weights
    model.update(_sense("a", 3 * H, contents=()))
    after = model.weights
    assert after[0] < before[0]        # last_observation, the false positive
    assert after[1] > before[1]        # most_frequent, which hedged
    assert model.absence_totals[0] < model.absence_totals[1]


def test_absence_weight_zero_is_presence_only_scoring() -> None:
    def final_weights(absence_weight: float) -> list[float]:
        model = _mixture(particle_specs=TWO_PARTICLES,
                         absence_weight=absence_weight)
        model.update(_obs("a", 0))
        model.update(_sense("a", H, contents=()))
        return model.weights

    off = final_weights(0.0)
    on = final_weights(0.5)
    assert off[0] > on[0]              # the false positive goes unpunished
    assert all(total == 0.0 for total
               in _mixture(particle_specs=TWO_PARTICLES,
                           absence_weight=0.0).absence_totals)


def test_absence_threshold_drops_objects_nobody_placed_there() -> None:
    # "o" is last seen at "a"; a look at "d" (which no particle favours)
    # scores no absence term at the default selection, and does at 0.
    def absence_total(uniforms: float) -> float:
        model = _mixture(particle_specs=TWO_PARTICLES, absence_weight=1.0,
                         absence_uniforms=uniforms)
        model.update(_obs("a", 0))
        model.update(_sense("d", H, contents=()))
        return sum(model.absence_totals)

    assert absence_total(2.0) == 0.0
    assert absence_total(0.0) < 0.0


def test_every_particle_is_scored_on_the_same_object_set() -> None:
    # Absence terms are all <= 0, so a particle handed more of them is
    # penalized for holding opinions. Each particle must receive exactly
    # one term per selected object — here, one object over one look.
    model = _mixture(particle_specs=TWO_PARTICLES, absence_weight=1.0)
    model.update(_obs("a", 0))
    model.update(_sense("a", H, contents=()))
    assert all(total < 0.0 for total in model.absence_totals)


def test_decay_applies_once_per_event_not_once_per_object() -> None:
    # One look reporting three objects must temper the history once. With
    # per-object tempering the surviving history would be decay^3.
    model = _mixture(particle_specs=TWO_PARTICLES, decay=0.5,
                     absence_weight=0.0)
    model.update(_obs("a", 0))
    model.update(_obs("a", H))
    before = list(model._log_weights)
    model.update(_sense("b", 2 * H, contents=("o", "p", "q")))
    assert len(model.ess_history) == 3          # three events, three steps
    assert before != list(model._log_weights)


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


def test_paired_delta_signs_a_real_difference_and_straddles_zero_otherwise(
) -> None:
    from baselines.hypothesis_mixture_study import paired_delta

    # Treatment right on every question the control got wrong: a clear
    # +0.5 that the interval must exclude 0 for.
    control = [True, False] * 200
    treatment = [True] * 400
    mean, low, high = paired_delta(treatment, control)
    assert mean == pytest.approx(0.5)
    assert low > 0.0

    # Identical arms: zero difference, zero-width interval.
    mean, low, high = paired_delta(control, control)
    assert (mean, low, high) == (0.0, 0.0, 0.0)

    # A one-question difference in 400 must NOT be called significant.
    nearly = list(control)
    nearly[1] = True
    mean, low, high = paired_delta(nearly, control)
    assert low <= 0.0 <= high


def test_room_cost_makes_the_policy_prefer_the_room_it_is_in(
        tmp_path) -> None:
    from baselines.bank import write_room_cost_bank
    from baselines.hypothesis_mixture_study import run_cell

    write_room_cost_bank(tmp_path / "rooms.jsonl")
    episode = next(JsonlBank(tmp_path / "rooms.jsonl").episodes())
    free = run_cell(episode, beta=0.05, lam=0.01, seed=0, room_cost=0.0)
    priced = run_cell(episode, beta=0.05, lam=0.01, seed=0, room_cost=2.0)
    assert free.room_cost == 0.0 and priced.room_cost == 2.0
    # Same-room senses cost 1.0 either way; cross-room ones triple, so the
    # priced run must not lean on cross-room looks more than the free one.
    def same_room_share(cell: object) -> float:
        total = cell.senses_per_day * cell.n_days   # type: ignore[attr-defined]
        return (cell.same_room_senses / total       # type: ignore[attr-defined]
                if total else 1.0)
    assert same_room_share(priced) >= same_room_share(free)


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
