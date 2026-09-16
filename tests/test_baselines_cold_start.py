"""The cold-start fleet recipe: no tour, no patrol, routine-driven
questions. The bank must start with zero sightings of every object and
still carry its full daily question quota; adding the query fields to
the fleet config must not move a byte of the existing fleet export.
All times are seconds since episode start."""

from __future__ import annotations

import json
import pathlib

import pytest

from baselines.bank import JsonlBank
from baselines.export_bank import export
from baselines.fleet import (FleetExportConfig, HouseholdSource,
                             export_one, load_fleet_config)

CONFIGS = pathlib.Path("src/baselines/configs")
HH = pathlib.Path("profiles/households/generated/gpt-5.6-terra/hh_001")
needs_household = pytest.mark.skipif(
    not (HH / "timeline_seed0" / "events.jsonl").exists(),
    reason="generated household hh_001 not present")


def _source() -> HouseholdSource:
    from baselines.fleet import discover_households
    return next(s for s in discover_households((HH.parents[1],))
                if s.slug == str(HH))


def _rows(path: pathlib.Path) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f]


def test_cold_start_config_differs_from_fleet_only_where_intended() -> None:
    fleet_cfg, _ = load_fleet_config(CONFIGS / "fleet.yaml")
    cold_cfg, _ = load_fleet_config(CONFIGS / "cold_start.yaml")
    # fleet.yaml is untouched: the new fields take their defaults there.
    assert fleet_cfg.query_generation == "uniform"
    assert fleet_cfg.query_rules is None
    assert cold_cfg == FleetExportConfig(
        **{**fleet_cfg.__dict__,
           "questions_per_day": 24, "budget_per_day": 8,
           "visits_per_day": 0, "initial_tour": False,
           "tour_start": "day0",
           "query_generation": "routine_driven",
           "query_rules": str(CONFIGS / "query_rules_cold_start.yaml"),
           "person_sensing": True})


def test_cold_start_rules_are_v1_with_a_lower_background_rate() -> None:
    from baselines.query_stream import load_query_rules
    v1 = load_query_rules(CONFIGS / "query_rules_v1.yaml")
    cold = load_query_rules(CONFIGS / "query_rules_cold_start.yaml")
    assert cold.background_query_rate == pytest.approx(1.6)
    assert cold.rules == v1.rules


@needs_household
def test_cold_start_bank_has_no_evidence_and_a_full_question_quota(
        tmp_path: pathlib.Path) -> None:
    cfg, _ = load_fleet_config(CONFIGS / "cold_start.yaml")
    bank_path = tmp_path / "cold_bank.jsonl"
    export_one(_source(), cfg, bank_path)
    rows = _rows(bank_path)
    header = rows[0]
    assert header["query_generation"] == "routine_driven"
    assert header["visits_per_day"] == 0
    # zero patrol rows, zero sightings of any kind, no tour snapshot
    assert not [r for r in rows if r["kind"] == "room_visit"]
    assert not [r for r in rows if r["kind"] == "observation"]
    assert not [r for r in rows if r.get("source") == "initial_tour"]
    # ... which the loader sees as zero sightings per object
    episode = next(JsonlBank(path=bank_path).episodes())
    assert episode.initial_observations == ()
    assert episode.scripted_observations == ()
    assert not list(episode.evidence_stream())
    # every day carries exactly its quota, split background/routine
    questions = [r for r in rows if r["kind"] == "question"]
    per_day = {}
    for q in questions:
        per_day[q["day_index"]] = per_day.get(q["day_index"], 0) + 1
    assert sorted(per_day) == list(range(header["n_days"]))
    assert set(per_day.values()) == {24}
    origins = {q["origin"].split(":")[0] for q in questions}
    assert origins == {"activity", "background"}


@needs_household
def test_fleet_export_is_unchanged_by_the_query_fields(
        tmp_path: pathlib.Path) -> None:
    """The fleet path with fleet.yaml writes the same bytes as a direct
    export() call that never mentions query_generation / query_rules."""
    cfg, _ = load_fleet_config(CONFIGS / "fleet.yaml")
    source = _source()
    via_fleet = tmp_path / "fleet_bank.jsonl"
    export_one(source, cfg, via_fleet)
    direct = tmp_path / "direct_bank.jsonl"
    export(source.timeline, source.spec, direct, cfg.seed,
           cfg.sightings_per_day, cfg.questions_per_day,
           cfg.first_question_day, cfg.budget_per_day, cfg.query_mode,
           initial_tour=cfg.initial_tour,
           sightings_per_object_day=cfg.sightings_per_object_day,
           budget_per_sensable_receptacle=cfg.budget_per_sensable_receptacle,
           observation_model=cfg.observation_model, patrol=cfg.patrol,
           visits_per_day=cfg.visits_per_day, tour_start=cfg.tour_start,
           tour_max_day=cfg.tour_max_day)
    assert via_fleet.read_bytes() == direct.read_bytes()
    assert _rows(via_fleet)[0]["query_generation"] == "uniform"
