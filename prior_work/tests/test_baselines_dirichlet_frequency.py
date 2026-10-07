"""The frequency path's Dirichlet prior: one observation must not yield a
one-hot distribution, and many observations must recover the empirical
histogram. Times are seconds since episode start."""

from __future__ import annotations

import math
import random

import pytest

from baselines.beliefs.base import DEFAULT_FREQUENCY_ALPHA
from baselines.registry import build_registered_belief
from baselines.types import EpisodeContext, Observation

H = 3600
RECS = tuple(f"r{i}" for i in range(27))
"""27 locations: the median receptacle count of the fleet banks, which is
what :data:`DEFAULT_FREQUENCY_ALPHA` is calibrated against."""

FREQUENCY_PATH = {
    "most_frequent": {},
    "timetable": {},
    "markov1": {"mixing_cutoff_h": 1.0},
    "periodic_persistence": {"min_departures": 10 ** 6},
    "smoothed_recency": {"smoothing_half_life_h": 0.01},
}
"""Every belief whose predictive distribution comes off the frequency path
(see :mod:`baselines.beliefs.base`), with the spec that routes it there:
Markov1 reaches it past its mixing cutoff, PeriodicPersistence below its
departure floor, SmoothedRecency once its recency term has decayed.

DaytypeMixture is absent: only its no-day-types fallback is on the
frequency path, and any sighting at all creates a day feature, so the
fallback is unreachable once the model has evidence. Its per-type
timetables stay empirical and it remains one-hot off one observation."""

NO_DECAY = {"half_life_h": 1e6, "frequency_half_life_h": 1e6}
"""Half-lives long enough that counts are the raw sighting split, so the
empirical distribution the posterior converges to is known exactly."""


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes={"o": "mug"}, budget_per_day=1, n_days=400)


def _obs(rec: str, t: int) -> Observation:
    return Observation(object_id="o", object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _build(name: str, **spec: object):
    model = build_registered_belief({"name": name, **spec}, random.Random(0))
    model.reset(_context())
    return model


def _entropy(distribution: dict[str, float]) -> float:
    return -sum(p * math.log(p) for p in distribution.values() if p > 0)


def test_one_observation_leaves_about_four_tenths_on_it() -> None:
    # (1 + alpha) / (1 + alpha * 27) at the default alpha, before the floor
    # mix; the floor moves it by well under a percentage point.
    model = _build("most_frequent", floor_mass=0.0)
    model.update(_obs("r3", 0))
    pred = model.predict("o", 6 * H)
    alpha = DEFAULT_FREQUENCY_ALPHA
    expected = (1.0 + alpha) / (1.0 + alpha * len(RECS))
    assert pred.distribution["r3"] == pytest.approx(expected)
    assert expected == pytest.approx(0.4, abs=0.02)
    assert pred.argmax == "r3"


@pytest.mark.parametrize("name", sorted(FREQUENCY_PATH))
def test_one_observation_has_entropy_well_above_zero(name: str) -> None:
    model = _build(name, **FREQUENCY_PATH[name], **NO_DECAY)
    model.update(_obs("r3", 0))
    pred = model.predict("o", 6 * H)
    # A one-hot histogram under the 0.02 floor scores about 0.12 nats and
    # 0.98 confidence; every frequency-path model must sit far off that.
    assert _entropy(pred.distribution) > 1.0
    assert pred.confidence < 0.6


@pytest.mark.parametrize("name", ["most_frequent", "timetable", "markov1",
                                  "periodic_persistence", "smoothed_recency"])
def test_many_observations_converge_to_the_empirical_distribution(
        name: str) -> None:
    # 300 sightings split 2:1 between two receptacles, all at the same time
    # of day so every binning scheme pools the same sightings.
    model = _build(name, **FREQUENCY_PATH[name], **NO_DECAY)
    for day in range(300):
        model.update(_obs("r1" if day % 3 else "r2", day * 24 * H + 9 * H))
    pred = model.predict("o", 300 * 24 * H + 9 * H)
    assert pred.distribution["r1"] == pytest.approx(2 / 3, abs=0.05)
    assert pred.distribution["r2"] == pytest.approx(1 / 3, abs=0.05)


def test_alpha_is_configurable() -> None:
    model = _build("most_frequent", floor_mass=0.0, frequency_alpha=1.0)
    model.update(_obs("r3", 0))
    pred = model.predict("o", 6 * H)
    n = len(RECS)
    assert pred.distribution["r3"] == pytest.approx(2.0 / (1.0 + n))
    assert pred.distribution["r0"] == pytest.approx(1.0 / (1.0 + n))
    with pytest.raises(ValueError, match="frequency_alpha"):
        _build("most_frequent", frequency_alpha=-0.1)


def test_alpha_zero_is_the_empirical_histogram_it_replaced() -> None:
    model = _build("most_frequent", floor_mass=0.0, frequency_alpha=0.0)
    model.update(_obs("r3", 0))
    pred = model.predict("o", 6 * H)
    assert {r: p for r, p in pred.distribution.items() if p} == {
        "r3": pytest.approx(1.0)}


def test_dirichlet_mean_covers_every_location_and_sums_to_one() -> None:
    model = _build("most_frequent")
    mean = model.dirichlet_mean({"r3": 4.0})
    assert set(mean) == set(RECS)
    assert sum(mean.values()) == pytest.approx(1.0)


def test_models_with_their_own_pseudocount_are_untouched() -> None:
    # The Markov transition row carries Laplace alpha = 1 already; inside
    # the mixing cutoff a single self-transition reads off that row, not
    # the frequency path.
    model = _build("markov1", floor_mass=0.0)
    model.update(_obs("r3", 0))
    model.update(_obs("r3", H))
    pred = model.predict("o", 2 * H)
    weight = 2.0 ** (-1.0 / 24.0)
    assert pred.distribution["r3"] == pytest.approx(
        (1.0 + weight) / (len(RECS) + weight))
