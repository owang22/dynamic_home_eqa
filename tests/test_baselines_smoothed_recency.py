"""Unit tests for the smoothed recency belief, its positive-evidence
regression, and the budget sweep's recency stratification. Times are seconds since
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
    model = SmoothedRecency(random.Random(0), config, floor_mass=0.0)
    model.reset(_context())
    for t, rec in [(0, "a"), (3600, "a"), (7200, "b")]:
        model.update(_obs(rec, t))
    return model


def test_fresh_sighting_behaves_like_last_observation() -> None:
    pred = _model().predict("o", 7201)          # one second stale
    assert pred.argmax == "b"
    assert pred.distribution["b"] > 0.999


def _frequency_share(model: SmoothedRecency, count: float) -> float:
    """The frequency component's mass on a receptacle sighted ``count``
    times out of three, under the frequency path's Dirichlet prior."""
    alpha = model.frequency_alpha
    return (count + alpha) / (3.0 + alpha * len(RECS))


def test_stale_sighting_behaves_like_most_frequent() -> None:
    model = _model()
    pred = model.predict("o", 7200 + 600 * 3600)      # 600 h stale
    assert pred.argmax == "a"
    assert pred.distribution["a"] == pytest.approx(_frequency_share(model, 2),
                                                   abs=1e-6)
    assert pred.distribution["b"] == pytest.approx(_frequency_share(model, 1),
                                                   abs=1e-6)


def test_interpolation_at_one_half_life_is_exact() -> None:
    # Elapsed exactly the 6 h smoothing half-life: weight 1/2 on the last
    # receptacle b, 1/2 on the Dirichlet frequency shares.
    model = _model()
    pred = model.predict("o", 7200 + 6 * 3600)
    assert pred.distribution["b"] == pytest.approx(
        0.5 + 0.5 * _frequency_share(model, 1))
    assert pred.distribution["a"] == pytest.approx(
        0.5 * _frequency_share(model, 2))
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_positive_path_matches_pre_migration_fixture() -> None:
    """Regression: on a positive-only stream (no empty looks) the model's
    own distribution is what it was before the negative-evidence
    migration. The fixture was dumped from the pre-migration code on the
    gate-pass bank; the model runs here with floor_mass 0 so the pipeline
    is the identity up to renormalization round-off (1e-12)."""
    import json
    import pathlib
    import tempfile
    from baselines.types import Observation
    fixture = json.loads(pathlib.Path(
        "tests/fixtures/smoothed_recency_positive_path.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        episode = next(write_gate_pass_bank(
            pathlib.Path(tmp) / "b.jsonl", seed=0).episodes())
    model = SmoothedRecency(random.Random(0), SmoothedRecencyConfig(),
                            floor_mass=0.0, frequency_alpha=0.0)
    model.reset(episode.agent_view())
    for obs in episode.initial_observations:
        model.update(obs)
    stream = [e for e in episode.evidence_stream()
              if isinstance(e, Observation)]
    assert len(stream) == len(episode.evidence_stream())
    rows = iter(fixture)
    cursor = 0
    for day in episode.questions_by_day:
        for q in day:
            while cursor < len(stream) and stream[cursor].t <= q.t_query:
                model.update(stream[cursor])
                cursor += 1
            expected = next(rows)
            assert expected["question_id"] == q.question_id
            pred = model.predict_readonly(q.object_id, q.t_query)
            assert pred.argmax == expected["argmax"]
            nonzero = {k: v for k, v in pred.distribution.items() if v != 0.0}
            assert nonzero == pytest.approx(expected["distribution"], abs=1e-12)


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
