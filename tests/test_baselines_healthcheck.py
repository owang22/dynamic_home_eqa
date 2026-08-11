"""Healthcheck integration: a bank engineered to PASS all gates and a
static-world bank engineered to FAIL not_trivial, verified end to end
through the JSON report."""

from __future__ import annotations

import pathlib
from typing import Dict

import pytest

from baselines.bank import write_gate_fail_static_bank, write_gate_pass_bank
from baselines.healthcheck import (HealthcheckConfig, load_healthcheck_config,
                                   run_healthcheck, write_report)


def _gate_verdicts(report_json: Dict[str, object]) -> Dict[str, bool]:
    gates = report_json["gates"]
    assert isinstance(gates, list)
    return {str(g["name"]): bool(g["passed"]) for g in gates}


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


def test_engineered_pass_bank_passes_every_gate(pass_report) -> None:  # type: ignore[no-untyped-def]
    verdicts = _gate_verdicts(pass_report.json_dict)
    assert verdicts == {name: True for name in (
        "solvable", "not_trivial", "not_impossible", "discriminative",
        "powered")}
    assert pass_report.gates_pass
    # household_type present -> the stratified check ran (not SKIPPED).
    strat = pass_report.json_dict["stratified_discriminative"]
    assert isinstance(strat, dict) and "synthetic_mixed" in strat


def test_engineered_static_bank_fails_not_trivial(fail_report) -> None:  # type: ignore[no-untyped-def]
    verdicts = _gate_verdicts(fail_report.json_dict)
    assert verdicts["not_trivial"] is False
    assert verdicts["solvable"] is True     # static worlds are solvable
    assert verdicts["powered"] is True      # the failure is dynamics, not scale
    assert not fail_report.gates_pass
    assert not fail_report.overall_pass
    # No household_type metadata -> stratified check is marked SKIPPED.
    strat = fail_report.json_dict["stratified_discriminative"]
    assert isinstance(strat, str) and "SKIPPED" in strat


def test_overall_pass_requires_clean_tree(pass_report) -> None:  # type: ignore[no-untyped-def]
    # The report may only claim overall PASS when every gate passed AND
    # the git tree was clean at run time — reproducibility is part of the
    # verdict, so this identity must hold whatever state the tree is in.
    j = pass_report.json_dict
    assert j["overall_pass"] == (j["gates_pass"] and not j["git_dirty"])
    if j["git_dirty"]:
        assert "REFUSED" in str(j["overall_note"])


def test_report_carries_provenance_and_measurements(pass_report) -> None:  # type: ignore[no-untyped-def]
    j = pass_report.json_dict
    for key in ("bank_manifest_hash", "config_hash", "git_commit", "seed",
                "timestamp", "n_questions", "panel"):
        assert key in j, key
    panel = j["panel"]
    assert isinstance(panel, dict)
    assert set(panel["never_sense_task_accuracy"]) == {
        "last_observation", "most_frequent", "timetable"}
    for gate in j["gates"]:
        assert {"name", "passed", "measured", "threshold", "comparison",
                "rationale"} <= set(gate)


def test_write_report_emits_json_and_text(
        pass_report, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    write_report(pass_report, tmp_path)
    assert (tmp_path / "healthcheck.json").exists()
    text = (tmp_path / "healthcheck.txt").read_text()
    for token in ("solvable", "not_trivial", "not_impossible",
                  "discriminative", "powered", "OVERALL"):
        assert token in text


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
