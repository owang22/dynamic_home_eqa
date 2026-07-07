"""
Tests for scripts/build_attribution_table.py's fingerprint-mismatch guard:
mixing result files from different frozen configs (e.g. a milestone rerun
before vs. after the navmesh-connectivity phase's climb fix) into one
table would silently misattribute that milestone's effect to whatever
actually changed — the guard must fail loudly instead.

Does not require habitat_sim (only reads JSON result files).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

_SCRIPT_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "build_attribution_table.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_attribution_table", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return _load_module()


def _result(milestone: str, fingerprint: str, rows: list[dict], code_hash: str = "codeabc") -> dict:
    return {"milestone": milestone, "fingerprint": fingerprint, "code_hash": code_hash, "config": {}, "rows": rows}


def _row(policy: str = "answer_immediately", wait_hours: float = 0.25) -> dict:
    return {
        "milestone": "m1", "fingerprint": "abc", "policy": policy, "wait_hours": wait_hours,
        "label": "book_1", "category": "book", "hazard_class": "low",
        "correct": True, "abstained": False, "confidence": 1.0, "brier": 1.0,
        "answer_latency_s": 0.0, "distance_traveled_m": 0.0, "policy_invocations": 1,
    }


def test_matching_fingerprints_pass(module):
    results = [
        _result("m1", "abc123", [_row()]),
        _result("m2", "abc123", [_row()]),
    ]
    assert module.check_fingerprints(results) == "abc123"


def test_mismatched_fingerprints_raise_loudly(module):
    results = [
        _result("m1", "abc123", [_row()]),
        _result("m2", "def456", [_row()]),
    ]
    with pytest.raises(ValueError, match="Fingerprint mismatch"):
        module.check_fingerprints(results)


def test_empty_results_raise(module):
    with pytest.raises(ValueError, match="no result files"):
        module.check_fingerprints([])


def test_matching_code_hashes_pass(module):
    results = [
        _result("m1", "abc123", [_row()], code_hash="codeabc"),
        _result("m2", "abc123", [_row()], code_hash="codeabc"),
    ]
    assert module.check_code_hashes(results) == "codeabc"


def test_mismatched_code_hashes_raise_loudly(module):
    """The regression test for the coverage-repair phase's own hole: two
    result files sharing an identical fingerprint but differing only in
    code_hash (e.g. a calibration-space fix landed between the two runs,
    changing behavior without touching FrozenConfig at all) must fail the
    build, not silently combine."""
    results = [
        _result("m2", "abc123", [_row()], code_hash="codeold"),
        _result("m3", "abc123", [_row()], code_hash="codenew"),
    ]
    with pytest.raises(ValueError, match="Code-hash mismatch"):
        module.check_code_hashes(results)


def test_missing_code_hash_is_treated_as_its_own_distinct_value(module):
    result_with_hash = _result("m1", "abc123", [_row()], code_hash="codeabc")
    result_without_hash = {"milestone": "m0", "fingerprint": "abc123", "config": {}, "rows": [_row()]}
    with pytest.raises(ValueError, match="Code-hash mismatch"):
        module.check_code_hashes([result_with_hash, result_without_hash])


def test_empty_results_raise_for_code_hashes_too(module):
    with pytest.raises(ValueError, match="no result files"):
        module.check_code_hashes([])


def test_load_results_ignores_stale_subfolder(module, tmp_path):
    results_dir = tmp_path / "embodied_results"
    results_dir.mkdir()
    stale_dir = results_dir / "stale"
    stale_dir.mkdir()

    live = _result("m1", "abc123", [_row()])
    (results_dir / "m1_result.json").write_text(json.dumps(live))
    (stale_dir / "m1_result.json").write_text(json.dumps(_result("m1", "stale999", [_row()])))

    loaded = module.load_results(results_dir)
    assert len(loaded) == 1
    assert loaded[0]["fingerprint"] == "abc123"


def test_load_results_ignores_diagnostics_subfolder(module, tmp_path):
    """Regression test: scripts/voi_boundary_validation.py's own summary
    JSON (not a milestone manifest — no "rows"/consistent "fingerprint"
    shape) originally landed directly in embodied_results/, matched this
    loader's own "*_result.json" glob, and broke check_fingerprints with a
    KeyError the first time build_attribution_table.py ran after it.
    Diagnostic scripts now write under embodied_results/diagnostics/,
    which this loader must not pick up, the same way it already ignores
    stale/."""
    results_dir = tmp_path / "embodied_results"
    results_dir.mkdir()
    diagnostics_dir = results_dir / "diagnostics"
    diagnostics_dir.mkdir()

    live = _result("m1", "abc123", [_row()])
    (results_dir / "m1_result.json").write_text(json.dumps(live))
    # A diagnostic artifact missing the milestone-manifest shape entirely
    # (no "fingerprint" key) — exactly what broke check_fingerprints.
    (diagnostics_dir / "voi_boundary_result.json").write_text(json.dumps({"latency_weight_sweep": [0.01]}))

    loaded = module.load_results(results_dir)
    assert len(loaded) == 1
    assert loaded[0]["fingerprint"] == "abc123"
