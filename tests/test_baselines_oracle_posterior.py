"""OracleBelief: realization weighting, degeneracy diagnostic, pipeline
interplay. Hand-built ensembles, no simulator. Times are seconds."""

from __future__ import annotations

import math
import pathlib
import random

import numpy as np
import pytest

from baselines.beliefs.oracle_program_posterior import (
    DEFAULT_EPS, OracleProgramPosterior, RealizationEnsemble, bank_seed_of,
    oracle_seeds)
from baselines.types import EpisodeContext, Observation, SenseResult

H = 3600
OUT = "OUT_OF_HOUSE"
RECS = ("a", "b", OUT)
N_MIN = 2 * 1440          # two days


def _ensemble() -> RealizationEnsemble:
    # Three realizations of two objects. Object o: seeds 0 and 1 keep it
    # at a all day, seed 2 moves it to b at 10:00. Object p: at b in every
    # seed, leaves the house at 12:00 in seed 1 only.
    points = {
        "o": [[(0, "a")], [(0, "a")], [(0, "a"), (10 * H, "b")]],
        "p": [[(0, "b")], [(0, "b"), (12 * H, OUT)], [(0, "b")]],
    }
    return RealizationEnsemble(seeds=(1001, 1002, 1003), receptacle_ids=RECS,
                               n_minutes=N_MIN, change_points=points)


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="hh_timeline_seed0", household_id="hh",
        receptacle_ids=RECS, object_classes={"o": "mug", "p": "keys"},
        budget_per_day=2, n_days=2, unsensable_receptacle_ids=(OUT,))


def _model(eps: float = DEFAULT_EPS, floor: float = 0.0
           ) -> OracleProgramPosterior:
    model = OracleProgramPosterior(random.Random(0), _ensemble(), eps=eps,
                                   floor_mass=floor)
    model.reset(_context())
    return model


def test_grid_reads_like_truth_at() -> None:
    ens = _ensemble()
    assert list(ens.codes_at("o", 9 * H)) == [0, 0, 0]
    assert list(ens.codes_at("o", 10 * H)) == [0, 0, 1]      # at the change
    assert list(ens.codes_at("o", 10 * H - 1)) == [0, 0, 0]  # just before
    assert list(ens.codes_at("p", 40 * H)) == [1, 2, 1]      # clipped horizon


def test_positive_sighting_weights_disagreeing_realizations() -> None:
    model = _model()
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    w = model.weights()
    # Seeds 0, 1 disagree (o at a), seed 2 agrees: eps, eps, 1 normalized.
    expect = np.array([DEFAULT_EPS, DEFAULT_EPS, 1.0])
    assert np.allclose(w, expect / expect.sum())
    assert model.effective_sample_size() == pytest.approx(
        1.0 / float(np.square(w).sum()))
    assert model.n_observations == 1


def test_empty_look_inverts_agreement() -> None:
    model = _model()
    # A sense of a at 11:00 that contains only p is an empty look for o at
    # a (seed 2 agrees: o is at b there) AND a positive sighting of p at a
    # (every seed disagrees: p is at b or OUT), so every seed takes one
    # eps for p and seeds 0, 1 a second one for o.
    model.update(SenseResult(receptacle_id="a", t=11 * H, contents=("p",)))
    w = model.weights()
    expect = np.array([DEFAULT_EPS ** 2, DEFAULT_EPS ** 2, DEFAULT_EPS])
    assert np.allclose(w, expect / expect.sum())
    assert model.n_observations == 2


def test_soft_never_hard() -> None:
    model = _model(eps=0.5)
    for _ in range(3):
        model.update(Observation(object_id="o", object_class="mug",
                                 receptacle_id="b", t=11 * H,
                                 source="scripted"))
    w = model.weights()
    assert w.min() > 0.0 and w[2] > w[0] == w[1]
    assert w[0] / w[2] == pytest.approx(0.5 ** 3)


def test_prediction_is_weighted_location_distribution() -> None:
    model = _model()
    # o at b seen at 11:00 -> weights (eps, eps, 1)/(1 + 2 eps). At 11:30
    # o is at a in seeds 0, 1 and at b in seed 2.
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    pred = model.predict("o", 11 * H + 1800)
    z = 1.0 + 2 * DEFAULT_EPS
    assert pred.distribution["a"] == pytest.approx(2 * DEFAULT_EPS / z)
    assert pred.distribution["b"] == pytest.approx(1.0 / z)
    assert pred.argmax == "b"
    diag = model.last_prediction_diagnostics()
    assert diag is not None and diag["ess"] == pytest.approx(
        model.effective_sample_size())
    # Before the move, every realization has o at a: one-hot on a.
    assert model.predict("o", 9 * H).distribution["a"] == 1.0
    # A sighting at the prediction instant short-circuits everything.
    assert model.predict("o", 11 * H).distribution == {"b": 1.0}


def test_negative_step_not_applied_twice() -> None:
    # Fresh empty look at a for o at 11:00 (sense contents ()). Seeds 0, 1
    # take eps for o (o is at a there); seed 2 agrees. p is absent from a
    # in every seed: no factor. The base pipeline must NOT also multiply
    # a by 0 (its query-instant factor): a keeps the weighted mass
    # 2 eps / (1 + 2 eps) that the weights alone give.
    model = _model()
    assert model.consumes_negative_evidence_natively
    model.update(SenseResult(receptacle_id="a", t=11 * H, contents=()))
    pred = model.predict("o", 11 * H)
    z = 1.0 + 2 * DEFAULT_EPS
    assert pred.distribution["a"] == pytest.approx(2 * DEFAULT_EPS / z)
    assert model.negative_observations("o", 11 * H) == {"a": 11 * H}


def test_floor_mix_applies() -> None:
    model = _model(floor=0.3)
    pred = model.predict("o", 9 * H)
    assert pred.distribution["a"] == pytest.approx(0.7 + 0.1)
    assert pred.distribution[OUT] == pytest.approx(0.1)
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_routine_prediction_ignores_observations() -> None:
    model = _model()
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    routine = model.routine_prediction("o", 11 * H + 1800)
    assert routine.distribution["a"] == pytest.approx(2 / 3)
    assert routine.argmax == "a"
    # Exact ties break to the smallest receptacle id, as routine_oracle.
    tie = model.routine_prediction("p", 13 * H)
    assert tie.distribution == {"b": pytest.approx(2 / 3), OUT: pytest.approx(1 / 3)}
    assert model.routine_prediction("p", 13 * H).argmax == "b"


def test_ess_ranges_from_n_seeds_to_one() -> None:
    model = _model(eps=1e-6)
    assert model.effective_sample_size() == pytest.approx(3.0)
    model.update(Observation(object_id="p", object_class="keys",
                             receptacle_id=OUT, t=13 * H, source="scripted"))
    assert model.effective_sample_size() == pytest.approx(1.0, abs=1e-5)


def test_reset_validates_vocabulary() -> None:
    model = OracleProgramPosterior(random.Random(0), _ensemble())
    with pytest.raises(ValueError, match="missing from the realizations"):
        model.reset(EpisodeContext(
            episode_id="e", household_id="hh", receptacle_ids=RECS,
            object_classes={"o": "mug", "q": "pen"}, budget_per_day=1,
            n_days=2))
    with pytest.raises(ValueError, match="does not have"):
        model.reset(EpisodeContext(
            episode_id="e", household_id="hh", receptacle_ids=("a", OUT),
            object_classes={"o": "mug"}, budget_per_day=1, n_days=2))
    with pytest.raises(ValueError):
        OracleProgramPosterior(random.Random(0), _ensemble(), eps=1.0)


def test_save_load_roundtrip(tmp_path: pathlib.Path) -> None:
    ens = _ensemble()
    path = tmp_path / "ens.npz"
    ens.save(path)
    back = RealizationEnsemble.load(path)
    assert back.seeds == ens.seeds and back.receptacle_ids == ens.receptacle_ids
    for obj in ens.objects:
        assert np.array_equal(back.grid[obj], ens.grid[obj])


def test_seed_conventions_exclude_the_bank_world() -> None:
    assert bank_seed_of("hh_001_timeline_seed0") == 0
    assert bank_seed_of("hh_007_timeline_seed3") == 3
    with pytest.raises(ValueError):
        bank_seed_of("synthetic")
    seeds = oracle_seeds(0, 800)
    assert len(seeds) == 800 and 0 not in seeds and min(seeds) == 1001
    assert min(oracle_seeds(1, 800)) == 11001
    assert math.isclose(DEFAULT_EPS, 0.05)


# ---------------------------------------------------------- forgetting

def test_half_life_ages_every_factor() -> None:
    model = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.5,
                                   half_life_h=2.0, floor_mass=0.0)
    model.reset(_context())
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    # Seeds 0, 1 disagree: log-weight log(0.5); one half-life later, half.
    model.predict("o", 13 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 0.5)
    # An earlier query never un-ages the weights.
    model.predict("o", 12 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 0.5)
    # Many half-lives on, the factor is gone: ESS back to the seed count.
    model.predict("o", 40 * H)
    assert model.effective_sample_size() == pytest.approx(3.0, abs=1e-3)
    # Aging happens at observations too: a second disagreement a
    # half-life after the first counts log(0.5) * (1 + 1/2).
    fresh = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.5,
                                   half_life_h=2.0, floor_mass=0.0)
    fresh.reset(_context())
    for t in (11 * H, 13 * H):
        fresh.update(Observation(object_id="o", object_class="mug",
                                 receptacle_id="b", t=t, source="scripted"))
    w = fresh.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 1.5)


def test_no_half_life_never_forgets() -> None:
    model = _model(eps=0.5)
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    model.predict("o", 40 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5)
    assert model.half_life_h is None


def test_half_life_in_name_and_validated() -> None:
    assert _model().name == "OracleBelief(eps=0.05)"
    model = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.3,
                                   half_life_h=24.0)
    assert model.name == "OracleBelief(eps=0.3,hl=24h)"
    assert model.half_life_h == 24.0
    with pytest.raises(ValueError, match="half_life_h"):
        OracleProgramPosterior(random.Random(0), _ensemble(), half_life_h=0.0)


def test_registry_passes_the_knobs() -> None:
    from baselines.registry import build_registered_belief

    model = build_registered_belief(
        {"name": "oracle_program_posterior", "ensemble": _ensemble(),
         "eps": 0.3, "half_life_h": 24}, random.Random(0))
    assert isinstance(model, OracleProgramPosterior)
    assert model.eps == 0.3 and model.half_life_h == 24.0
    plain = build_registered_belief(
        {"name": "oracle_program_posterior", "ensemble": _ensemble()},
        random.Random(0))
    assert isinstance(plain, OracleProgramPosterior)
    assert plain.eps == DEFAULT_EPS and plain.half_life_h is None


def test_study_config_and_selection() -> None:
    from baselines.oracle_posterior_study import (ESS_STOP, OracleConfig,
                                                  select_config)

    cfg = OracleConfig(0.3, 24.0)
    assert cfg.slug == "eps0.3__hl24h"
    assert OracleConfig.from_json(cfg.to_json()) == cfg
    assert OracleConfig(0.05, None).slug == "eps0.05__hlnone"
    assert cfg.spec()["half_life_h"] == 24.0
    assert cfg.spec()["name"] == "oracle_program_posterior"

    def row(config: str, subset: str, ess: float, acc: float) -> dict:
        return {"config": config, "subset": subset, "median_ess": ess,
                "accuracy": acc, "eligible": int(ess >= ESS_STOP)}

    table = [row("a", "calibration", 1.0, 0.9), row("a", "test", 1.0, 0.9),
             row("b", "calibration", 6.0, 0.7), row("b", "test", 6.0, 0.95),
             row("c", "calibration", 9.0, 0.7), row("c", "test", 9.0, 0.5)]
    # Degenerate 'a' is out however accurate; the tie between b and c on
    # calibration accuracy goes to the larger ESS; test rows never count.
    chosen = select_config(table)
    assert chosen is not None and chosen["config"] == "c"
    assert select_config([row("a", "calibration", 1.0, 0.9)]) is None
