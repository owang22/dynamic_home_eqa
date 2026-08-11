"""Unit tests for the three basic belief models against hand-computed
expectations. Times are seconds since episode start."""

from __future__ import annotations

import random

import pytest

from baselines.beliefs import (LastObservation, MostFrequentLocation,
                               TimetableConfig, TimetableLookup)
from baselines.types import DAY_SECONDS, EpisodeContext, Observation, SenseResult

H = 3600
RECS = ("a", "b", "c")


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes={"o": "mug"}, budget_per_day=1, n_days=2)


def _obs(rec: str, t: int) -> Observation:
    return Observation(object_id="o", object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def test_last_observation_tracks_most_recent_sighting() -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_obs("b", 20))
    # Last sighting is b@t=20, so the prediction is one-hot on b.
    pred = model.predict("o", 100)
    assert pred.argmax == "b"
    assert pred.distribution == {"b": 1.0}
    assert pred.confidence == 1.0


def test_never_observed_falls_back_to_uniform() -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    pred = model.predict("ghost", 0)
    # Uniform over the three receptacles; argmax is one of them.
    assert pred.distribution == {r: pytest.approx(1 / 3) for r in RECS}
    assert pred.argmax in RECS


def test_most_frequent_prefers_the_mode() -> None:
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    # a seen twice, b once: distribution 2/3 vs 1/3, argmax a.
    for rec, t in (("a", 10), ("b", 20), ("a", 30)):
        model.update(_obs(rec, t))
    pred = model.predict("o", 100)
    assert pred.argmax == "a"
    assert pred.distribution == {"a": pytest.approx(2 / 3),
                                 "b": pytest.approx(1 / 3)}


def test_most_frequent_breaks_ties_by_recency() -> None:
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    # a and b tie 1-1; b was seen later, so recency breaks the tie to b.
    model.update(_obs("a", 10))
    model.update(_obs("b", 20))
    assert model.predict("o", 100).argmax == "b"


def test_sense_result_contents_count_as_positive_sightings() -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(SenseResult(receptacle_id="c", t=50, contents=("o",)))
    # The sense placed o in c at t=50, later than the a sighting.
    assert model.predict("o", 100).argmax == "c"


def test_timetable_uses_the_query_bin() -> None:
    model = TimetableLookup(random.Random(0),
                            TimetableConfig(bin_hours=1, day_scheme="all"))
    model.reset(_context())
    # Same clock hour on different days shares a bin: 9:00 sightings say a,
    # a single 20:00 sighting says b.
    model.update(_obs("a", 9 * H))
    model.update(_obs("a", DAY_SECONDS + 9 * H))
    model.update(_obs("b", 20 * H))
    assert model.predict("o", DAY_SECONDS + 9 * H + 600).argmax == "a"
    assert model.predict("o", DAY_SECONDS + 20 * H + 600).argmax == "b"


def test_timetable_empty_bin_degrades_to_most_frequent() -> None:
    model = TimetableLookup(random.Random(0),
                            TimetableConfig(bin_hours=1, day_scheme="all"))
    model.reset(_context())
    model.update(_obs("a", 9 * H))
    model.update(_obs("a", 10 * H))
    model.update(_obs("b", 20 * H))
    # 15:00 was never observed: the whole history votes, mode is a.
    pred = model.predict("o", DAY_SECONDS + 15 * H)
    assert pred.argmax == "a"
    assert pred.distribution == {"a": pytest.approx(2 / 3),
                                 "b": pytest.approx(1 / 3)}


def test_timetable_weekday_weekend_scheme_separates_days() -> None:
    model = TimetableLookup(
        random.Random(0),
        TimetableConfig(bin_hours=1, day_scheme="weekday_weekend"))
    model.reset(_context())
    # 9:00 on a weekday (day 0) says a; 9:00 on a weekend (day 5) says b.
    model.update(_obs("a", 9 * H))
    model.update(_obs("b", 5 * DAY_SECONDS + 9 * H))
    assert model.predict("o", 1 * DAY_SECONDS + 9 * H).argmax == "a"
    assert model.predict("o", 6 * DAY_SECONDS + 9 * H).argmax == "b"


def test_timetable_config_validation() -> None:
    with pytest.raises(ValueError, match="bin_hours"):
        TimetableConfig(bin_hours=5)
    with pytest.raises(ValueError, match="day_scheme"):
        TimetableConfig(day_scheme="lunar")


def test_decayed_most_frequent_tracks_the_drifting_mode() -> None:
    # Three stale sightings at a vs one fresh at b: infinite memory keeps
    # a; a 12 h half-life discounts the two-day-old votes to ~1/16 each
    # and the fresh sighting wins.
    naive = MostFrequentLocation(random.Random(0))
    decayed = MostFrequentLocation(random.Random(0), half_life_h=12)
    for model in (naive, decayed):
        model.reset(_context())
        for t in (0, H, 2 * H):
            model.update(_obs("a", t))
        model.update(_obs("b", 2 * DAY_SECONDS))
    t_query = 2 * DAY_SECONDS + H
    assert naive.predict("o", t_query).argmax == "a"
    assert decayed.predict("o", t_query).argmax == "b"


def test_decayed_timetable_tracks_bin_drift() -> None:
    # The 09:00 bin says a for a week, then the routine changes to b: a
    # 24 h half-life flips the bin within a day; infinite memory holds a.
    naive = TimetableLookup(random.Random(0), TimetableConfig())
    decayed = TimetableLookup(random.Random(0), TimetableConfig(),
                              half_life_h=24)
    for model in (naive, decayed):
        model.reset(_context())
        for d in range(7):
            model.update(_obs("a", d * DAY_SECONDS + 9 * H))
        model.update(_obs("b", 7 * DAY_SECONDS + 9 * H))
    t_query = 8 * DAY_SECONDS + 9 * H
    assert naive.predict("o", t_query).argmax == "a"
    assert decayed.predict("o", t_query).argmax == "b"


def test_half_life_validation() -> None:
    with pytest.raises(ValueError, match="half_life_h"):
        MostFrequentLocation(random.Random(0), half_life_h=0)
    with pytest.raises(ValueError, match="half_life_h"):
        TimetableLookup(random.Random(0), TimetableConfig(), half_life_h=-1)
