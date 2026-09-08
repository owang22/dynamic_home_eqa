"""Unit tests for the belief base pipeline: the floor mix, the decaying
negative-evidence factors, the supersession rule, and the way
OUT_OF_HOUSE emerges from floor survival. Times are seconds since
episode start."""

from __future__ import annotations

import random

import pytest

from baselines.beliefs import LastObservation, MostFrequentLocation
from baselines.beliefs.base import DEFAULT_FLOOR_MASS
from baselines.types import EpisodeContext, Observation, SenseResult

OUT = "OUT_OF_HOUSE"
RECS = ("a", "b", "c", OUT)
H = 3600


def _context(objects: dict[str, str] | None = None) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes=objects or {"o": "mug"}, budget_per_day=1, n_days=2,
        unsensable_receptacle_ids=(OUT,))


def _obs(rec: str, t: int, obj: str = "o") -> Observation:
    return Observation(object_id=obj, object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _empty_sense(rec: str, t: int) -> SenseResult:
    return SenseResult(receptacle_id=rec, t=t, contents=())


def _last_obs(**kwargs: float) -> LastObservation:
    model = LastObservation(random.Random(0), **kwargs)
    model.reset(_context())
    return model


def test_floor_mix_arithmetic_on_a_hand_example() -> None:
    # One-hot on a through the floor: (1 - f) * 1 + f/4 on a, f/4 elsewhere.
    model = _last_obs()
    model.update(_obs("a", 10))
    pred = model.predict("o", 20)
    f = DEFAULT_FLOOR_MASS
    assert pred.distribution["a"] == pytest.approx(1 - f + f / 4)
    for rec in ("b", "c", OUT):
        assert pred.distribution[rec] == pytest.approx(f / 4)
    assert pred.argmax == "a"
    assert sum(pred.distribution.values()) == pytest.approx(1.0)
    assert set(pred.distribution) == set(RECS)   # the full location space


def test_recording_via_negative_observations() -> None:
    model = _last_obs()
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    model.update(_empty_sense("b", 25))
    model.update(_empty_sense("a", 30))          # newest look wins
    assert model.negative_observations("o", 40) == {"a": 30, "b": 25}
    # Only the newest look per receptacle is kept, so at t=27 the look at
    # a (now recorded at 30) is in the future and does not count yet.
    assert model.negative_observations("o", 27) == {"b": 25}
    assert model.negative_observations("o", 15) == {}


def test_fresh_empty_look_suppresses_fully() -> None:
    # An empty look at the query instant: w(0) = 1, factor 0, exactly.
    model = _last_obs()
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    pred = model.predict("o", 20)
    assert pred.distribution["a"] == 0.0
    assert pred.argmax != "a"
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_half_suppression_at_one_half_life() -> None:
    # negative_half_life_h = 2: a look 2 h old halves the receptacle's
    # floor-mixed mass before renormalization.
    model = _last_obs(negative_half_life_h=2.0)
    model.update(_obs("a", 0))
    model.update(_empty_sense("a", 10))
    pred = model.predict("o", 10 + 2 * H)
    f = DEFAULT_FLOOR_MASS
    pre_a = (1 - f + f / 4) * 0.5
    total = pre_a + 3 * f / 4
    assert pred.distribution["a"] == pytest.approx(pre_a / total)
    assert pred.distribution["b"] == pytest.approx((f / 4) / total)
    assert pred.argmax == "a"      # half of 0.985 still beats the floor


def test_look_superseded_by_a_strictly_later_sighting() -> None:
    model = _last_obs()
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    model.update(_obs("a", 30))     # strictly later sighting: back at a
    assert model.negative_observations("o", 40) == {}
    pred = model.predict("o", 40)
    f = DEFAULT_FLOOR_MASS
    assert pred.argmax == "a"
    assert pred.distribution["a"] == pytest.approx(1 - f + f / 4)


def test_look_survives_an_equal_time_sighting_elsewhere() -> None:
    # Seeing o at b at the same instant a was sensed empty is consistent
    # with (and does not supersede) the empty look at a.
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_obs("a", 12))
    model.update(_empty_sense("a", 20))
    model.update(_obs("b", 20))
    assert model.negative_observations("o", 25) == {"a": 20}
    pred = model.predict("o", 25)
    assert pred.distribution["a"] < pred.distribution["b"]
    assert pred.argmax == "b"


def test_look_from_nonempty_contents() -> None:
    # Absence is evidence even when the sense saw other objects.
    model = LastObservation(random.Random(0))
    model.reset(_context({"o": "mug", "decoy": "coin"}))
    model.update(_obs("a", 10))
    model.update(_obs("a", 10, obj="decoy"))
    model.update(SenseResult(receptacle_id="a", t=20, contents=("decoy",)))
    assert model.negative_observations("o", 20) == {"a": 20}
    assert model.negative_observations("decoy", 20) == {}
    assert model.predict("o", 20).distribution["a"] == 0.0
    assert model.predict("decoy", 20).argmax == "a"


def test_out_of_house_is_never_suppressed() -> None:
    model = _last_obs()
    model.update(_obs("a", 10))
    # A look at OUT can never be recorded through the harness (it is
    # unsensable); even if one were, the factor map excludes it.
    model._exclusions.setdefault("o", {})[OUT] = 20
    assert OUT not in model.negative_factors("o", 20)
    assert model.predict("o", 20).distribution[OUT] > 0.0


def test_all_sensable_fresh_empty_yields_out_of_house() -> None:
    # The elimination-emerges test: every sensable receptacle looked at
    # empty at the query instant leaves only the floor mass on
    # OUT_OF_HOUSE, which therefore holds probability 1 after
    # renormalization. No policy did anything.
    model = _last_obs()
    model.update(_obs("a", 10))
    for rec in ("a", "b", "c"):
        model.update(_empty_sense(rec, 20))
    pred = model.predict("o", 20)
    assert pred.argmax == OUT
    assert pred.distribution[OUT] == pytest.approx(1.0)
    for rec in ("a", "b", "c"):
        assert pred.distribution[rec] == 0.0


def test_stale_looks_do_not_yield_out_of_house() -> None:
    # The same looks a full day old (24 h half-life): each in-house
    # receptacle keeps half its floor-mixed mass, the last-seen one far
    # more than OUT's untouched floor share, so a passive answer stays
    # at the last sighting.
    model = _last_obs()
    model.update(_obs("a", 10))
    for rec in ("a", "b", "c"):
        model.update(_empty_sense(rec, 20))
    pred = model.predict("o", 20 + 24 * H)
    assert pred.argmax == "a"
    assert pred.distribution[OUT] < pred.distribution["a"]


def test_query_instant_sighting_outvotes_history() -> None:
    # A positive sighting AT the prediction instant is ground truth then;
    # frequency history must not outvote it.
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    for t in (10, 11, 12, 13):
        model.update(_obs("a", t))
    model.update(SenseResult(receptacle_id="b", t=100, contents=("o",)))
    pred = model.predict("o", 100)
    assert pred.argmax == "b"
    assert pred.distribution == {"b": 1.0}
    # One second later the sighting is ordinary history again and the
    # frequency mode (a: 4 sightings vs b: 1) wins back the argmax.
    assert model.predict("o", 101).argmax == "a"


def test_floor_mass_validation_and_zero_floor() -> None:
    with pytest.raises(ValueError, match="floor_mass"):
        LastObservation(random.Random(0), floor_mass=1.0)
    with pytest.raises(ValueError, match="negative_half_life_h"):
        LastObservation(random.Random(0), negative_half_life_h=0.0)
    # floor_mass 0 exposes the model's own arithmetic (unit tests only).
    model = _last_obs(floor_mass=0.0)
    model.update(_obs("a", 10))
    pred = model.predict("o", 20)
    assert pred.distribution["a"] == 1.0 and pred.distribution[OUT] == 0.0


def test_negative_half_life_defaults_to_the_models_own() -> None:
    assert LastObservation(random.Random(0)).negative_half_life_h == 24.0
    assert MostFrequentLocation(
        random.Random(0), half_life_h=6).negative_half_life_h == 6.0
    assert MostFrequentLocation(
        random.Random(0), half_life_h=6,
        negative_half_life_h=1.5).negative_half_life_h == 1.5


def test_legacy_veto_flag_reproduces_the_old_rule() -> None:
    # Replay-only: hard permanent veto, uniform redistribution, no floor.
    model = _last_obs(legacy_exclusion_veto=True)
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    pred = model.predict("o", 20 + 10 * 24 * H)      # never decays
    assert pred.distribution["a"] == 0.0
    for rec in ("b", "c", OUT):
        assert pred.distribution[rec] == pytest.approx(1 / 3)
    assert pred.argmax in ("b", "c", OUT)
