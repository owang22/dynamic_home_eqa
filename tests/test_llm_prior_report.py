"""
Tests for llm_prior/report.py's scoring functions against the REAL
committed elicitation cache and manifests (llm_prior_cache/, results/
reports/l0_manifests/) — no live model calls, no network, per L0's "no
live LLM calls in pytest" rule. If these files are ever regenerated
(a prompt-template or model change), this test's numbers should be
revisited, not silently kept green against stale expectations.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from dynamic_home_eqa.llm_prior.report import score_dynamics_priors, score_location_priors

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent
_MANIFEST_DIR = _DYNAMIC_EQA / "results" / "reports" / "l0_manifests"
_OUT_DIR = _DYNAMIC_EQA / "generation_out"

pytestmark = pytest.mark.skipif(
    not _MANIFEST_DIR.exists(), reason="L0 elicitation manifests not present (run llm_prior/elicit.py first)"
)


def _manifest(family: str) -> dict:
    return json.loads((_MANIFEST_DIR / f"l0_manifest_{family}.json").read_text())


class TestScoreLocationPriors:
    def test_all_three_modes_present(self):
        scores = score_location_priors(_manifest("qwen"), _OUT_DIR)
        assert set(scores) == {"mcq_logprob", "verbalized", "sample_count"}

    def test_scored_plus_failures_covers_every_location_target(self):
        manifest = _manifest("qwen")
        n_location_targets = sum(1 for t in manifest["targets"] if t["axis"] == "location")
        scores = score_location_priors(manifest, _OUT_DIR)
        for mode, s in scores.items():
            assert s["n_scored"] + s["n_parse_failures"] == n_location_targets

    def test_brier_scores_are_valid_range(self):
        scores = score_location_priors(_manifest("phi3"), _OUT_DIR)
        for mode, s in scores.items():
            if s["brier_mean"] is not None:
                assert 0.0 <= s["brier_mean"] <= 2.0  # multiclass Brier range


class TestScoreDynamicsPriors:
    def test_has_fitted_reference_and_per_mode(self):
        result = score_dynamics_priors(_manifest("qwen"), _OUT_DIR)
        assert "fitted_reference" in result
        assert "per_mode" in result
        assert set(result["per_mode"]) == {"mcq_logprob", "verbalized", "sample_count"}

    def test_fitted_reference_covers_every_swept_wait(self):
        from dynamic_home_eqa.embodied.experiment_config import FROZEN

        result = score_dynamics_priors(_manifest("qwen"), _OUT_DIR)
        for wait in FROZEN.wait_hours_sweep:
            assert wait in result["fitted_reference"]["location"]

    def test_no_parse_failures_on_committed_cache(self):
        # Regression for an elicit.py bug
        # (location targets never got a dynamics elicitation at all,
        # showing up as n_parse_failures == every location target).
        for family in ("qwen", "phi3"):
            result = score_dynamics_priors(_manifest(family), _OUT_DIR)
            for mode, s in result["per_mode"].items():
                assert s["n_parse_failures"] == 0, f"{family}/{mode} has unexpected parse failures"
