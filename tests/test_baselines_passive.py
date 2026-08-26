"""Tests for the horizon-controlled passive protocol and the bake-off.

Covers: the checkpoint information barrier (a poisoned post-checkpoint
sighting must not change any prediction — asserted by construction on
the full scored output), the three analytic fixture banks, cell/recency
bookkeeping, aggregation invariants, and bake-off determinism
(byte-identical JSON across runs from the same seed).
"""
from __future__ import annotations

import dataclasses
import json
import random

import pytest

from baselines.bank import (JsonlBank, write_fast_churn_bank,
                            write_gate_pass_bank, write_periodic_probe_bank,
                            write_two_regime_bank)
from baselines.bakeoff import (bakeoff_specs, results_json, run_bakeoff,
                               write_reports)
from baselines.passive_eval import (PassiveProtocolConfig,
                                    aggregate_households,
                                    evaluate_checkpoint, group_cells,
                                    group_recency)
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS, Observation

PANEL_AND_CANDIDATES = tuple(bakeoff_specs())


def _run(bank: JsonlBank, spec: dict, config: PassiveProtocolConfig):
    episode = next(bank.episodes())
    scored = []
    for checkpoint in config.checkpoint_days:
        belief = build_registered_belief(dict(spec), random.Random(0))
        scored += evaluate_checkpoint(episode, belief, checkpoint, config)
    return scored


# ----------------------------------------------------- information barrier


def test_poisoned_sighting_after_checkpoint_changes_nothing(tmp_path):
    """The barrier holds by construction: append a decisive sighting after
    the checkpoint cutoff and the entire scored output is unchanged."""
    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    episode = next(bank.episodes())
    config = PassiveProtocolConfig(checkpoint_days=(7,),
                                   horizons_days=(0.25, 1.0, 3.0))
    poison = Observation(object_id="badge_shift", object_class="badge",
                         receptacle_id="shelf_s",
                         t=7 * DAY_SECONDS + 60, source="scripted")
    poisoned = dataclasses.replace(
        episode, scripted_observations=tuple(sorted(
            (*episode.scripted_observations, poison), key=lambda o: o.t)))
    for spec in PANEL_AND_CANDIDATES:
        clean = evaluate_checkpoint(
            episode, build_registered_belief(dict(spec), random.Random(0)),
            7, config)
        dirty = evaluate_checkpoint(
            poisoned, build_registered_belief(dict(spec), random.Random(0)),
            7, config)
        assert clean == dirty, spec["name"]


def test_no_question_at_or_before_checkpoint_is_scored(tmp_path):
    bank = write_gate_pass_bank(tmp_path / "pass.jsonl")
    episode = next(bank.episodes())
    config = PassiveProtocolConfig(checkpoint_days=(6,),
                                   horizons_days=(0.25, 1.0, 3.0, 7.0))
    belief = build_registered_belief({"name": "last_observation"},
                                     random.Random(0))
    scored = evaluate_checkpoint(episode, belief, 6, config)
    assert scored
    for q in scored:
        assert q.t_query > 6 * DAY_SECONDS
        assert q.horizon_days in config.horizons_days
        # The assigned horizon is the smallest that covers the elapsed gap.
        elapsed = q.t_query - 6 * DAY_SECONDS
        assert elapsed <= q.horizon_days * DAY_SECONDS
        smaller = [h for h in config.horizons_days if h < q.horizon_days]
        if smaller:
            assert elapsed > smaller[-1] * DAY_SECONDS


# ------------------------------------------------------- analytic fixtures


def test_periodic_probe_time_models_are_perfect_at_short_horizon(tmp_path):
    """Strict periodicity + dense sightings: the time-conditioned models
    must hit 1.0 at horizons <= 1 day."""
    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    config = PassiveProtocolConfig(checkpoint_days=(7,),
                                   horizons_days=(0.25, 1.0))
    for spec in ({"name": "timetable", "bin_hours": 1, "day_scheme": "all",
                  "half_life_h": 24},
                 {"name": "periodic_persistence"}):
        cells = group_cells(_run(bank, spec, config))
        assert cells, spec["name"]
        for (_, horizon), score in cells.items():
            assert horizon <= 1.0
            assert score.top1_accuracy == 1.0, (spec["name"], horizon)


def test_two_regime_daytype_beats_most_frequent(tmp_path):
    """Weekend queries after a frozen weekday-heavy checkpoint: regime
    inference must beat the 24 h-half-life frequency model by a wide
    margin (here: perfectly vs not at all)."""
    bank = write_two_regime_bank(tmp_path / "regime.jsonl")
    config = PassiveProtocolConfig(checkpoint_days=(26,),
                                   horizons_days=(1.0, 2.0))
    daytype = _run(bank, {"name": "daytype_mixture"}, config)
    frequency = _run(bank, {"name": "most_frequent", "half_life_h": 24},
                     config)
    acc_daytype = sum(q.correct for q in daytype) / len(daytype)
    acc_frequency = sum(q.correct for q in frequency) / len(frequency)
    assert acc_daytype >= acc_frequency + 0.5
    assert acc_daytype == 1.0


def test_fast_churn_all_models_approach_frequency_floor(tmp_path):
    """As time-since-last-sighting grows on an unlearnable churner, every
    model must converge to the frequency model's stale-bin accuracy."""
    bank = write_fast_churn_bank(tmp_path / "churn.jsonl")
    config = PassiveProtocolConfig(checkpoint_days=(3,),
                                   horizons_days=(0.25, 1.0, 3.0, 7.0))
    stale_bin = "[72h,inf)"
    floor = group_recency(_run(
        bank, {"name": "most_frequent", "half_life_h": 24},
        config))[stale_bin]
    assert floor.n_questions >= 20
    for spec in PANEL_AND_CANDIDATES:
        stale = group_recency(_run(bank, dict(spec), config))[stale_bin]
        assert abs(stale.top1_accuracy - floor.top1_accuracy) <= 0.2, (
            spec["name"], stale.top1_accuracy, floor.top1_accuracy)


# ------------------------------------------------------------ aggregation


def test_recency_bins_and_labels():
    config = PassiveProtocolConfig()
    assert config.recency_bin(1800) == "[0h,1h)"
    assert config.recency_bin(3600) == "[1h,6h)"
    assert config.recency_bin(80 * 3600) == "[72h,inf)"
    assert config.recency_bin(None) == "never"
    assert config.recency_bin_labels()[-1] == "never"


def test_aggregate_households_is_unweighted_and_shows_spread():
    from baselines.passive_eval import CellScore
    cells = {
        "hh_a": {(7, 1.0): CellScore(n_questions=1000, top1_accuracy=0.9,
                                     mean_log_loss=0.2)},
        "hh_b": {(7, 1.0): CellScore(n_questions=10, top1_accuracy=0.1,
                                     mean_log_loss=2.0)},
    }
    (acc, loss), = aggregate_households(cells, seed=0).values()
    # Unweighted over households: 0.5, not the question-weighted ~0.89.
    assert acc.mean == pytest.approx(0.5)
    assert acc.n_households == 2
    assert acc.n_questions == 1010
    assert acc.per_household == {"hh_a": 0.9, "hh_b": 0.1}
    assert acc.ci_low <= acc.mean <= acc.ci_high
    assert loss.mean == pytest.approx(1.1)


# ------------------------------------------------------------ determinism


def test_bakeoff_reports_are_byte_identical_across_runs(tmp_path):
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    config = PassiveProtocolConfig(checkpoint_days=(4, 7),
                                   horizons_days=(0.25, 1.0, 3.0))
    payloads = []
    for run_dir in (tmp_path / "run1", tmp_path / "run2"):
        results = run_bakeoff([bank.path], seed=0, config=config)
        write_reports(results, [bank.path], 0, config, run_dir)
        payloads.append((run_dir / "bakeoff_results.json").read_bytes())
        # Sanity: the JSON parses and covers every model.
        parsed = json.loads(payloads[-1])
        assert len(parsed["models"]) == len(PANEL_AND_CANDIDATES)
    assert payloads[0] == payloads[1]


def test_results_json_carries_sample_sizes(tmp_path):
    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    config = PassiveProtocolConfig(checkpoint_days=(7,),
                                   horizons_days=(0.25, 1.0, 3.0))
    results = run_bakeoff([bank.path], seed=0, config=config)
    payload = results_json(results, [bank.path], 0, config)
    for model in payload["models"]:
        for cell in model["aggregate_cells"].values():
            assert cell["top1_accuracy"]["n_households"] == 1
            assert cell["top1_accuracy"]["n_questions"] > 0
