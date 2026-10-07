"""Diagnostic-report integration: a bank engineered to raise no flags and
a static-world bank engineered to flag not_trivial, verified end to end
through the JSON report. Diagnostics are advisory — nothing disqualifies
a bank — except solvable, whose failure means a bug."""

from __future__ import annotations

import pathlib
from typing import Dict

import pytest

from baselines.bank import write_gate_fail_static_bank, write_gate_pass_bank
from baselines.healthcheck import (HealthcheckConfig, load_healthcheck_config,
                                   run_healthcheck, write_report)


def _flagged(report_json: Dict[str, object]) -> Dict[str, bool]:
    diagnostics = report_json["diagnostics"]
    assert isinstance(diagnostics, list)
    return {str(d["name"]): bool(d["flagged"]) for d in diagnostics}


@pytest.fixture(scope="module")
def pass_report(tmp_path_factory: pytest.TempPathFactory):  # type: ignore[no-untyped-def]
    bank = write_gate_pass_bank(
        tmp_path_factory.mktemp("banks") / "pass.jsonl")
    return run_healthcheck(bank.path, HealthcheckConfig(), None)


@pytest.fixture(scope="module")
def fail_report(tmp_path_factory: pytest.TempPathFactory):  # type: ignore[no-untyped-def]
    bank = write_gate_fail_static_bank(
        tmp_path_factory.mktemp("banks") / "fail.jsonl")
    return run_healthcheck(bank.path, HealthcheckConfig(), None)


def test_engineered_clean_bank_raises_no_flags(pass_report) -> None:  # type: ignore[no-untyped-def]
    flagged = _flagged(pass_report.json_dict)
    assert flagged == {name: False for name in (
        "stationarity", "solvable", "not_trivial", "not_impossible",
        "discriminative", "powered")}
    assert pass_report.flags == ()
    assert pass_report.solvable_ok
    # household_type present -> the stratified check ran (not SKIPPED).
    strat = pass_report.json_dict["stratified_discriminative"]
    assert isinstance(strat, dict) and "synthetic_mixed" in strat


def test_engineered_static_bank_flags_not_trivial(fail_report) -> None:  # type: ignore[no-untyped-def]
    flagged = _flagged(fail_report.json_dict)
    assert flagged["not_trivial"] is True
    assert flagged["stationarity"] is True   # intrinsic diagnostic agrees
    assert flagged["solvable"] is False      # static worlds are solvable
    assert flagged["powered"] is False       # the flag is dynamics, not scale
    assert "not_trivial" in fail_report.flags
    # flags are advisory: the bug check still holds on this bank
    assert fail_report.solvable_ok
    # No household_type metadata -> stratified check is marked SKIPPED.
    strat = fail_report.json_dict["stratified_discriminative"]
    assert isinstance(strat, str) and "SKIPPED" in strat


def test_flags_field_matches_the_diagnostics(pass_report, fail_report) -> None:  # type: ignore[no-untyped-def]
    for report in (pass_report, fail_report):
        flagged = _flagged(report.json_dict)
        assert list(report.flags) == [n for n, f in flagged.items() if f]
        assert report.json_dict["flags"] == list(report.flags)
        # provenance still records tree state, without any refusal semantics
        assert "git_dirty" in report.json_dict


def test_report_carries_provenance_and_measurements(pass_report) -> None:  # type: ignore[no-untyped-def]
    j = pass_report.json_dict
    for key in ("bank_manifest_hash", "config_hash", "git_commit", "seed",
                "timestamp", "n_questions", "panel", "bank_stats"):
        assert key in j, key
    assert 0.0 < j["bank_stats"]["modal_share_time"] < 1.0
    panel = j["panel"]
    assert isinstance(panel, dict)
    assert set(panel["never_sense_task_accuracy"]) == {
        "last_observation", "most_frequent", "timetable"}
    for diagnostic in j["diagnostics"]:
        assert {"name", "flagged", "measured", "threshold", "comparison",
                "rationale", "is_bug_check"} <= set(diagnostic)


def test_write_report_emits_json_and_text(
        pass_report, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    write_report(pass_report, tmp_path)
    assert (tmp_path / "healthcheck.json").exists()
    text = (tmp_path / "healthcheck.txt").read_text()
    for token in ("stationarity", "solvable", "not_trivial",
                  "not_impossible", "discriminative", "powered",
                  "Diagnostics"):
        assert token in text
    assert "disqualif" in text     # the advisory framing is stated on-page


def test_config_loader_rejects_unknown_keys(tmp_path: pathlib.Path) -> None:
    good = tmp_path / "good.yaml"
    good.write_text("seed: 3\nnot_trivial_max: 0.7\n")
    config = load_healthcheck_config(good)
    assert config.seed == 3 and config.not_trivial_max == 0.7
    assert load_healthcheck_config(None) == HealthcheckConfig()
    bad = tmp_path / "bad.yaml"
    bad.write_text("seeed: 3\n")
    with pytest.raises(ValueError, match="seeed"):
        load_healthcheck_config(bad)
