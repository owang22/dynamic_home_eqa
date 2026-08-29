"""Unit tests for the smoothed recency belief, its exclusion backoff, and
the budget sweep's recency stratification. Times are seconds since
episode start."""

from __future__ import annotations

import collections
import random

import pytest

from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.belief_trace import RECENCY_CONFIG, _question_scores
from baselines.beliefs.smoothed_recency import (SmoothedRecency,
                                                SmoothedRecencyConfig)
from baselines.registry import BELIEF_REGISTRY, CANDIDATE_SLATE
from baselines.routine_oracle import _modal_receptacle
from baselines.types import EpisodeContext, Observation, SenseResult

RECS = ("a", "b", "c", "d")

# Frequency component effectively undecayed, so the frequency
# distribution is plain sighting shares and the interpolation arithmetic
# below stays hand-checkable.
FLAT_FREQ = SmoothedRecencyConfig(smoothing_half_life_h=6.0,
                                  frequency_half_life_h=1e9)


def _context(objects: dict[str, str] | None = None) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes=objects or {"o": "mug"}, budget_per_day=1, n_days=8)


def _obs(rec: str, t: int, obj: str = "o") -> Observation:
    return Observation(object_id=obj, object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _model(config: SmoothedRecencyConfig = FLAT_FREQ) -> SmoothedRecency:
    model = SmoothedRecency(random.Random(0), config)
    model.reset(_context())
    for t, rec in [(0, "a"), (3600, "a"), (7200, "b")]:
        model.update(_obs(rec, t))
    return model


def test_fresh_sighting_behaves_like_last_observation() -> None:
    pred = _model().predict("o", 7201)          # one second stale
    assert pred.argmax == "b"
    assert pred.distribution["b"] > 0.999


def test_stale_sighting_behaves_like_most_frequent() -> None:
    pred = _model().predict("o", 7200 + 600 * 3600)   # 600 h stale
    assert pred.argmax == "a"
    assert pred.distribution["a"] == pytest.approx(2 / 3, abs=1e-6)
    assert pred.distribution["b"] == pytest.approx(1 / 3, abs=1e-6)


def test_interpolation_at_one_half_life_is_exact() -> None:
    # Elapsed exactly the 6 h smoothing half-life: weight 1/2 on the last
    # receptacle b, 1/2 on the (a: 2/3, b: 1/3) frequency shares.
    pred = _model().predict("o", 7200 + 6 * 3600)
    assert pred.distribution["b"] == pytest.approx(0.5 + 0.5 / 3)
    assert pred.distribution["a"] == pytest.approx(0.5 * 2 / 3)
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_excluded_last_receptacle_backs_off_to_frequency() -> None:
    # The self-inflicted collapse this model exists to avoid: negative
    # evidence on the last-seen receptacle must send its mass to the
    # object's other usual spots, not spread it uniformly.
    model = _model()
    model.update(SenseResult(receptacle_id="b", t=8000, contents=()))
    pred = model.predict("o", 9000)
    assert pred.argmax == "a"
    assert pred.distribution["b"] == 0.0
    assert pred.distribution["a"] == pytest.approx(1.0)
    assert pred.distribution["c"] == 0.0 and pred.distribution["d"] == 0.0


def test_backoff_with_no_mass_on_kept_receptacles_is_uniform() -> None:
    # Every receptacle the object was ever seen at is ruled out: the
    # frequency backoff has nothing to say and the uniform default of the
    # base machinery takes over.
    model = _model()
    model.update(SenseResult(receptacle_id="a", t=8000, contents=()))
    model.update(SenseResult(receptacle_id="b", t=8000, contents=()))
    pred = model.predict("o", 9000)
    assert pred.distribution["a"] == 0.0 and pred.distribution["b"] == 0.0
    assert pred.distribution["c"] == pytest.approx(0.5)
    assert pred.distribution["d"] == pytest.approx(0.5)


def test_config_validation() -> None:
    with pytest.raises(ValueError, match="smoothing_half_life_h"):
        SmoothedRecencyConfig(smoothing_half_life_h=0.0)
    with pytest.raises(ValueError, match="frequency_half_life_h"):
        SmoothedRecencyConfig(frequency_half_life_h=-1.0)


def test_registered_as_candidate_and_in_the_slate() -> None:
    assert BELIEF_REGISTRY["smoothed_recency"].panel == "candidate"
    assert {"name": "smoothed_recency"} in CANDIDATE_SLATE


def test_question_scores_recency_counts_add_up(tmp_path) -> None:
    """The sweep's recency table only tells the truth if every question
    lands in exactly one bin and the counts travel with the accuracies."""
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    episode = next(JsonlBank(path=bank.path).episodes())
    overall, recency = _question_scores(
        episode, {"name": "smoothed_recency"}, seed=0, evidence=[])
    n_questions = sum(len(day) for day in episode.questions_by_day)
    assert sum(cell["n"] for cell in recency.values()) == n_questions
    assert set(recency) <= set(RECENCY_CONFIG.recency_bin_labels())
    pooled = sum(cell["accuracy"] * cell["n"] for cell in recency.values())
    assert overall == pytest.approx(pooled / n_questions, abs=1e-3)


def test_oracle_modal_receptacle_is_deterministic() -> None:
    assert _modal_receptacle(collections.Counter(a=3, b=1)) == "a"
    # Exact tie: lexicographically smallest, independent of insert order.
    assert _modal_receptacle(collections.Counter(b=2, a=2)) == "a"
    assert _modal_receptacle(collections.Counter(a=2, b=2)) == "a"
