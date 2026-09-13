"""Tests for the hypothesis converter: parsing/validation strictness,
prediction semantics of hand-written hypotheses (the brief's build-first
step), sighting-driven parameter movement, and the mixture separation
check — a hypothesis matching the household's true profile must outgain
a plausible-but-wrong one within days of sightings. Times are seconds
since episode start; day 0 is Monday."""

from __future__ import annotations

import json
import math
import random

import pytest

from baselines.beliefs.hypothesis_program import (
    HypothesisProgramBelief, HypothesisValidationError, parse_hypothesis)
from baselines.beliefs.llm_hypothesis_mixture import LLMHypothesisMixture
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS, EpisodeContext, Observation

H = 3600
RECS = ("desk", "kitchen_table", "hamper", "shelf", "OUT_OF_HOUSE")
OBJECTS = {"laptop_1": "laptop", "mug_1": "mug",
           "towel_1": "towel", "towel_2": "towel"}


def _context(n_days: int = 28) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh_test", receptacle_ids=RECS,
        object_classes=OBJECTS, budget_per_day=2, n_days=n_days,
        unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def _obs(obj: str, rec: str, t: int) -> Observation:
    return Observation(object_id=obj, object_class=OBJECTS[obj],
                       receptacle_id=rec, t=t, source="scripted")


def _at(day: int, hour: float) -> int:
    return int(day * DAY_SECONDS + hour * H)


WORK_HYPOTHESIS = {
    "hypothesis_id": "h_work",
    "rationale": "laptop works at the kitchen table on weekdays",
    "rest": {"laptop_1": "desk", "class:towel": "shelf"},
    "activities": [
        {"name": "work", "days": "weekday", "frequency_per_week": 5,
         "start_hour": 9.0, "duration_h": 8.0,
         "moves": [{"target": "laptop_1", "to": "kitchen_table",
                    "chance": "usually", "after": "returned"}]},
        {"name": "shower", "days": "both", "frequency_per_week": 7,
         "start_hour": 7.0, "duration_h": 0.5,
         "moves": [{"target": "class:towel", "to": "hamper",
                    "chance": "sometimes", "after": "left"}]},
    ],
}


def _belief(raw=WORK_HYPOTHESIS, seed: int = 0) -> HypothesisProgramBelief:
    model = HypothesisProgramBelief(random.Random(seed), raw)
    model.reset(_context())
    return model


# ---------------------------------------------------------------- parsing

def test_parse_expands_classes_and_resolves_rest() -> None:
    hyp = parse_hypothesis(WORK_HYPOTHESIS, OBJECTS, RECS)
    assert hyp.rest["towel_1"] == "shelf" and hyp.rest["towel_2"] == "shelf"
    shower = hyp.activities[1]
    assert shower.moves[0].targets == ("towel_1", "towel_2")
    assert shower.occurrence_probability() == 1.0


def test_parse_rejects_unknown_ids_and_names_them() -> None:
    bad = json.loads(json.dumps(WORK_HYPOTHESIS))
    bad["rest"]["marys_cup"] = "desk"
    bad["activities"][0]["moves"][0]["to"] = "dining_table"
    with pytest.raises(HypothesisValidationError) as err:
        parse_hypothesis(bad, OBJECTS, RECS)
    assert set(err.value.bad_strings) == {"marys_cup", "dining_table"}


def test_parse_rejects_unknown_chance_label() -> None:
    bad = json.loads(json.dumps(WORK_HYPOTHESIS))
    bad["activities"][0]["moves"][0]["chance"] = "0.7"
    with pytest.raises(HypothesisValidationError):
        parse_hypothesis(bad, OBJECTS, RECS)


# ------------------------------------------------------------- prediction

def test_weekday_window_puts_laptop_at_work_surface() -> None:
    model = _belief()
    midday_monday = model.predict("laptop_1", _at(0, 13.0))
    assert midday_monday.argmax == "kitchen_table"
    night_monday = model.predict("laptop_1", _at(0, 22.0))
    assert night_monday.argmax == "desk"


def test_weekend_day_does_not_trigger_weekday_activity() -> None:
    model = _belief()
    midday_saturday = model.predict("laptop_1", _at(5, 13.0))
    assert midday_saturday.argmax == "desk"


def test_left_rule_keeps_object_out_through_the_evening() -> None:
    model = _belief()
    evening = model.predict("towel_1", _at(0, 21.0))
    # "sometimes" (0.35) displaced to the hamper, rest of the mass on the
    # stated shelf: shelf still leads, but the hamper carries real mass.
    assert evening.argmax == "shelf"
    assert evening.distribution["hamper"] > 0.25


def test_uncovered_object_falls_back_to_statistics() -> None:
    model = _belief()
    for day in range(3):
        model.update(_obs("mug_1", "kitchen_table", _at(day, 8.0)))
    prediction = model.predict("mug_1", _at(3, 12.0))
    assert prediction.argmax == "kitchen_table"


# --------------------------------------------------------------- learning

def test_confirming_sightings_raise_the_chance() -> None:
    model = _belief()
    before = model.predict("laptop_1", _at(0, 13.0)).distribution[
        "kitchen_table"]
    for day in range(4):
        model.update(_obs("laptop_1", "kitchen_table", _at(day, 13.0)))
    after = model.predict("laptop_1", _at(4, 13.0)).distribution[
        "kitchen_table"]
    assert after > before + 0.05


def test_contradicting_sightings_lower_the_chance() -> None:
    model = _belief()
    before = model.predict("laptop_1", _at(0, 13.0)).distribution[
        "kitchen_table"]
    for day in range(4):
        model.update(_obs("laptop_1", "desk", _at(day, 13.0)))
    after = model.predict("laptop_1", _at(4, 13.0)).distribution[
        "kitchen_table"]
    assert after < before - 0.05


def test_sightings_move_a_wrong_rest_location() -> None:
    model = _belief()
    for day in range(2):
        for hour in (6.0, 20.0, 22.0):
            model.update(_obs("laptop_1", "shelf", _at(day, hour)))
    moved = model.predict("laptop_1", _at(2, 22.0))
    assert moved.argmax == "shelf"


def test_sightings_shift_a_stated_start_hour() -> None:
    model = _belief()
    # Work actually starts at 11: repeated confirming sightings should
    # drag the fitted start hour toward it.
    for day in range(5):
        if day % 7 < 5:
            model.update(_obs("laptop_1", "kitchen_table", _at(day, 11.5)))
    fitted = model.fitted_parameters()["start_hours"][0]
    assert fitted["stated_start_hour"] == 9.0
    assert fitted["fitted_start_hour"] > 9.6


def test_fitted_parameters_report_evidence_counts() -> None:
    model = _belief()
    model.update(_obs("laptop_1", "kitchen_table", _at(0, 13.0)))
    report = model.fitted_parameters()
    work = next(r for r in report["rules"] if r["activity"] == "work")
    assert work["stated_chance"] == "usually"
    assert work["evidence"] > 0.0


# ------------------------------------------------------------- separation

WRONG_HYPOTHESIS = {
    "hypothesis_id": "h_wrong",
    "rationale": "plausible but wrong: laptop works from the shelf, "
                 "weekends too, towels never move",
    "rest": {"laptop_1": "kitchen_table", "class:towel": "hamper"},
    "activities": [
        {"name": "work", "days": "both", "frequency_per_week": 7,
         "start_hour": 14.0, "duration_h": 6.0,
         "moves": [{"target": "laptop_1", "to": "shelf",
                    "chance": "almost_always", "after": "returned"}]},
    ],
}


def _simulate_true_world(model, n_days: int) -> None:
    """Sightings from the world WORK_HYPOTHESIS describes: laptop on the
    kitchen table on weekday middays, on the desk in the evening; towels
    on the shelf, in the hamper after some evening showers."""
    rng = random.Random(7)
    for day in range(n_days):
        weekday = day % 7 < 5
        if weekday:
            model.update(_obs("laptop_1", "kitchen_table", _at(day, 13.0)))
        model.update(_obs("laptop_1", "desk", _at(day, 21.0)))
        for towel in ("towel_1", "towel_2"):
            if rng.random() < 0.35:
                model.update(_obs(towel, "hamper", _at(day, 20.0)))
            else:
                model.update(_obs(towel, "shelf", _at(day, 10.0)))


def test_true_profile_outgains_plausible_wrong_one(tmp_path) -> None:
    hyp_dir = tmp_path / "hyps"
    hyp_dir.mkdir()
    (hyp_dir / "hh_test.json").write_text(json.dumps(
        {"hypotheses": [WORK_HYPOTHESIS, WRONG_HYPOTHESIS]}))
    model = LLMHypothesisMixture(random.Random(0), hyp_dir)
    model.reset(_context())
    _simulate_true_world(model, n_days=7)
    weights = {p.name: w for p, w in zip(model.particles, model.weights)}
    true_w = weights["HypothesisProgram(h_work)"]
    wrong_w = weights["HypothesisProgram(h_wrong)"]
    assert true_w > 2.0 * wrong_w, weights


def test_single_stat_particle_mixture_equals_the_particle(tmp_path) -> None:
    """The stat-only comparison arm: with an empty hypothesis list the
    loader refuses, and with only the stat particle the mixture must
    equal periodic_persistence exactly (parent-class invariant)."""
    hyp_dir = tmp_path / "hyps"
    hyp_dir.mkdir()
    (hyp_dir / "hh_test.json").write_text(json.dumps({"hypotheses": []}))
    model = LLMHypothesisMixture(random.Random(0), hyp_dir)
    with pytest.raises(ValueError):
        model.reset(_context())


def test_registry_builds_both_new_models(tmp_path) -> None:
    single = build_registered_belief(
        {"name": "hypothesis_program", "hypothesis": WORK_HYPOTHESIS},
        random.Random(0))
    single.reset(_context())
    assert single.predict("laptop_1", _at(0, 13.0)).argmax == "kitchen_table"

    hyp_dir = tmp_path / "hyps"
    hyp_dir.mkdir()
    (hyp_dir / "hh_test.json").write_text(json.dumps(
        {"hypotheses": [WORK_HYPOTHESIS]}))
    mixture = build_registered_belief(
        {"name": "llm_hypothesis_mixture", "hypotheses_dir": str(hyp_dir),
         "label": "llm_hyp_named"}, random.Random(0))
    mixture.reset(_context())
    assert mixture.name == "llm_hyp_named"
    assert len(mixture.particles) == 2  # one hypothesis + the stat particle


# ------------------------------------------------- scoring equivalence

def test_location_equivalence_pools_mass_and_relabels_truth() -> None:
    from baselines.passive_eval import AWAY_EQUIVALENCE, PassiveProtocolConfig
    from baselines.types import Prediction
    cfg = PassiveProtocolConfig(location_equivalence=AWAY_EQUIVALENCE)
    tied = Prediction(distribution={"desk": 0.3, "ON_PERSON": 0.35,
                                    "OUT_OF_HOUSE": 0.35}, argmax="ON_PERSON")
    view, truth = cfg.score_view(tied, "OUT_OF_HOUSE")
    assert view.distribution == {"desk": 0.3, "OUT_OF_HOUSE": 0.7}
    assert view.argmax == truth == "OUT_OF_HOUSE"
    # pooling can lift the group above the original argmax
    split = Prediction(distribution={"desk": 0.4, "ON_PERSON": 0.3,
                                     "OUT_OF_HOUSE": 0.3}, argmax="desk")
    assert cfg.score_view(split, "desk")[0].argmax == "OUT_OF_HOUSE"
    # default config is exact match, unchanged
    assert PassiveProtocolConfig().score_view(tied, "OUT_OF_HOUSE") == (
        tied, "OUT_OF_HOUSE")


def test_location_equivalence_rejects_overlapping_groups() -> None:
    from baselines.passive_eval import PassiveProtocolConfig
    with pytest.raises(ValueError):
        PassiveProtocolConfig(location_equivalence=(("a", "b"), ("b", "c")))


def test_rest_accepts_list_of_target_at_pairs_and_rejects_other_shapes() -> None:
    as_list = json.loads(json.dumps(WORK_HYPOTHESIS))
    as_list["rest"] = [{"target": "laptop_1", "at": "desk"},
                       {"target": "class:towel", "to": "shelf"}]
    hyp = parse_hypothesis(as_list, OBJECTS, RECS)
    assert hyp.rest["laptop_1"] == "desk" and hyp.rest["towel_2"] == "shelf"
    bad = json.loads(json.dumps(WORK_HYPOTHESIS))
    bad["rest"] = [{"object": "laptop_1", "place": "desk"}]
    with pytest.raises(HypothesisValidationError):
        parse_hypothesis(bad, OBJECTS, RECS)
