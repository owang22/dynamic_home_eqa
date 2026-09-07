"""Conformal-triggered sensing: the quantile, age-binned fitting, the
household split, policy termination, and sweep determinism."""

from __future__ import annotations

import pathlib
import random
from typing import List, Tuple

import pytest

from baselines.agent import Agent
from baselines.bank import write_synthetic_bank
from baselines.beliefs import LastObservation
from baselines.beliefs.base import BeliefModel
from baselines.conformal.calibration import (CalibrationPair, QhatTable,
                                             age_bin_index, collect_pairs,
                                             conformal_qhat,
                                             fit_age_binned_qhat,
                                             household_split)
from baselines.conformal.sweep import main as sweep_main
from baselines.harness import run_episode
from baselines.policies.conformal_sense import (ConformalSense,
                                                belief_age_fn)
from baselines.policies.never_sense import NeverSense
from baselines.types import (AnswerNow, EpisodeContext, Observation,
                             Prediction, Question, Sense)

H = 3600
TEN_SCORES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]


def test_conformal_qhat_hand_computed() -> None:
    # n = 10, alpha = 0.2: rank ceil(11 * 0.8) = 9 -> 9th smallest.
    assert conformal_qhat(TEN_SCORES, 0.2) == 0.85
    # alpha = 0.5: rank ceil(5.5) = 6 -> 0.55; order of input irrelevant.
    assert conformal_qhat(list(reversed(TEN_SCORES)), 0.5) == 0.55
    # alpha = 0.05: rank ceil(10.45) = 11 > n -> vacuous.
    assert conformal_qhat(TEN_SCORES, 0.05) == 1.0
    assert conformal_qhat([], 0.2) == 1.0
    with pytest.raises(ValueError):
        conformal_qhat(TEN_SCORES, 1.0)


def _pair(age_h: float | None, score: float, hh: str = "hh") -> CalibrationPair:
    return CalibrationPair(household_id=hh, episode_id="ep", question_id="q",
                           object_id="o", t_query=0, age_h=age_h,
                           score=score, top_prob=1 - score, correct=score == 0)


def test_fit_age_binned_thin_bin_falls_back_to_global() -> None:
    young = [_pair(1.0, s) for s in [0.1] * 35 + [0.9] * 5]   # 40 pairs
    old = [_pair(100.0, 0.95) for _ in range(5)]              # thin bin
    never = [_pair(None, 0.99) for _ in range(3)]             # also oldest
    table = fit_age_binned_qhat(young + old + never, alpha=0.2,
                                age_edges_h=(6, 24, 72), min_n=30)
    assert table.bin_counts == (40, 0, 0, 8)
    assert table.bin_fallback == (False, True, True, True)
    assert table.bin_qhats[0] == conformal_qhat([p.score for p in young], 0.2)
    assert table.bin_qhats[3] == table.global_qhat
    assert table.qhat_for(None, binned=True) == table.global_qhat
    assert table.qhat_for(1.0, binned=False) == table.global_qhat
    assert age_bin_index(6.0, (6, 24, 72)) == 1
    assert age_bin_index(None, (6, 24, 72)) == 3


def test_household_split_is_disjoint_and_deterministic() -> None:
    ids = [f"hh_{i:03d}" for i in range(20)]
    split = household_split(ids, split_seed=0)
    assert set(split) == set(ids)
    assert sum(v == "calibration" for v in split.values()) == 10
    assert split == household_split(reversed(ids), split_seed=0)
    assert split != household_split(ids, split_seed=1)
    tiny = household_split(["a", "b"], split_seed=3)
    assert sorted(tiny.values()) == ["calibration", "test"]


class _AlwaysUniform(BeliefModel):
    """A belief that never concentrates, whatever it has seen."""

    def _predict_for_object(self, object_id: str, history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        return self._uniform()


def _table(alpha: float = 0.1, qhat: float = 1.0) -> QhatTable:
    return QhatTable(alpha=alpha, age_edges_h=(6.0,), global_qhat=qhat,
                     n_global=100, bin_qhats=(qhat, qhat), bin_counts=(50, 50),
                     bin_fallback=(False, False))


def test_policy_senses_at_most_once_per_sensable_receptacle() -> None:
    recs = ("a", "b", "c", "d", "OUT")
    context = EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=recs,
        object_classes={"o": "mug"}, budget_per_day=100, n_days=1,
        unsensable_receptacle_ids=("OUT",))
    belief = _AlwaysUniform(random.Random(0))
    belief.reset(context)
    policy = ConformalSense(random.Random(1), _table(), belief_age_fn(belief),
                            binned=True)
    policy.reset(context)
    q = Question(question_id="q0", object_id="o", t_query=10 * H, day_index=0)
    sensed = []
    for _ in range(20):
        action = policy.decide(q, belief.predict("o", q.t_query), 100, q.t_query)
        if isinstance(action, AnswerNow):
            break
        assert isinstance(action, Sense)
        sensed.append(action.receptacle_id)
    else:
        pytest.fail("policy never answered")
    assert len(sensed) == len(context.sensable_receptacle_ids)
    assert len(set(sensed)) == len(sensed)
    assert "OUT" not in sensed


def test_policy_answers_on_singleton_set_and_on_found() -> None:
    context = EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=("a", "b"),
        object_classes={"o": "mug"}, budget_per_day=2, n_days=1)
    belief = LastObservation(random.Random(0))
    belief.reset(context)
    belief.update(Observation(object_id="o", object_class="mug",
                              receptacle_id="a", t=0, source="initial_tour"))
    policy = ConformalSense(random.Random(1), _table(qhat=0.0),
                            belief_age_fn(belief), binned=False)
    policy.reset(context)
    q = Question(question_id="q0", object_id="o", t_query=5 * H, day_index=0)
    # One-hot on a, qhat 0 -> singleton set -> answer without sensing.
    assert isinstance(policy.decide(q, belief.predict("o", q.t_query), 2,
                                    q.t_query), AnswerNow)
    assert policy.name == "ConformalSense(alpha=0.1,global)"
    # A one-hot belief carries a single key; with the vacuous qhat = 1 the
    # set spans every receptacle (the omitted ones at p = 0), so it senses.
    vacuous = ConformalSense(random.Random(1), _table(qhat=1.0),
                             belief_age_fn(belief), binned=False)
    vacuous.reset(context)
    assert isinstance(vacuous.decide(q, belief.predict("o", q.t_query), 2,
                                     q.t_query), Sense)


def test_policy_runs_through_harness(tmp_path: pathlib.Path) -> None:
    episode = next(write_synthetic_bank(tmp_path / "bank.jsonl").episodes())
    belief = LastObservation(random.Random(0))
    agent = Agent(belief=belief, policy=ConformalSense(
        random.Random(1), _table(qhat=1.0), belief_age_fn(belief), True))
    records = list(run_episode(agent, episode))
    assert records and all(r.budget_spent <= episode.budget_per_day
                           for r in records)


def test_last_positive_sighting_time_and_age() -> None:
    belief = LastObservation(random.Random(0))
    belief.reset(EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=("a", "b"),
        object_classes={"o": "mug"}, budget_per_day=1, n_days=1))
    assert belief.last_positive_sighting_time("o", 10) is None
    belief.update(Observation(object_id="o", object_class="mug",
                              receptacle_id="a", t=10, source="scripted"))
    belief.update(Observation(object_id="o", object_class="mug",
                              receptacle_id="b", t=20, source="scripted"))
    assert belief.last_positive_sighting_time("o", 15) == 10
    assert belief.last_positive_sighting_time("o", 20) == 20
    assert belief.last_positive_sighting_time("o", 5) is None
    age = belief_age_fn(belief)
    assert age("o", 20 + 2 * H) == 2.0
    assert age("never", 100) is None


def test_collect_pairs_tags_household(tmp_path: pathlib.Path) -> None:
    episode = next(write_synthetic_bank(tmp_path / "bank.jsonl").episodes())
    belief = LastObservation(random.Random(0))
    passive = collect_pairs(Agent(belief=belief, policy=NeverSense()),
                            episode, belief_age_fn(belief))
    assert len(passive.pairs) == len(passive.records) == 12
    assert {p.household_id for p in passive.pairs} == {"synthetic_hh"}
    for pair, record in zip(passive.pairs, passive.records):
        assert pair.score == pytest.approx(
            1 - record.distribution.get(record.truth_receptacle, 0.0))
        assert pair.correct == record.correct


def _demo_args(out: pathlib.Path) -> List[str]:
    return ["--demo", "--out", str(out), "--seed", "3",
            "--beliefs", "last_observation,most_frequent",
            "--alphas", "0.1,0.2", "--workers", "2"]


def test_sweep_is_deterministic(tmp_path: pathlib.Path) -> None:
    assert sweep_main(_demo_args(tmp_path / "run1")) == 0
    assert sweep_main(_demo_args(tmp_path / "run2")) == 0
    first = (tmp_path / "run1" / "sweep_results.csv").read_bytes()
    assert first == (tmp_path / "run2" / "sweep_results.csv").read_bytes()
    assert ((tmp_path / "run1" / "coverage_by_age.csv").read_bytes()
            == (tmp_path / "run2" / "coverage_by_age.csv").read_bytes())
    for name in ("coverage_by_age.png", "accuracy_vs_budget.png",
                 "calibration.json", "provenance.json", "summary.md"):
        assert (tmp_path / "run1" / name).exists()
    dumps = sorted(p.name for p in (tmp_path / "run1" / "questions").iterdir())
    assert "last_observation__never_sense.jsonl.gz" in dumps
    assert "most_frequent__conformal_age_binned_alpha0.2.jsonl.gz" in dumps
    assert b"ConformalSense(alpha=0.2,age_binned)" in first
