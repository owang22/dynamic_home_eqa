"""
Tests for llm_prior/synthetic_kernel.py — pure math, no model calls.
"""
from __future__ import annotations

import math

import pytest

from dynamic_home_eqa.llm_prior.synthetic_kernel import (
    REFERENCE_HOURS,
    build_synthetic_kernel,
    stay_probability_to_lambda,
)


class TestStayProbabilityToLambda:
    def test_high_stay_probability_gives_low_lambda(self):
        assert stay_probability_to_lambda(0.99) < stay_probability_to_lambda(0.5)

    def test_survival_curve_passes_through_elicited_point(self):
        p = 0.7
        lam = stay_probability_to_lambda(p)
        survival_at_reference = math.exp(-lam * REFERENCE_HOURS)
        assert survival_at_reference == pytest.approx(p, abs=1e-6)

    def test_clamps_degenerate_probabilities(self):
        # Exactly 0 or 1 must not raise or produce inf/zero lambda.
        lam_zero = stay_probability_to_lambda(0.0)
        lam_one = stay_probability_to_lambda(1.0)
        assert math.isfinite(lam_zero) and lam_zero > 0
        assert math.isfinite(lam_one) and lam_one > 0


class TestBuildSyntheticKernel:
    def test_normalizes_dest_dist_over_support(self):
        support = ("shelf", "table", "OUTSIDE")
        dest_dist = {"shelf": 2.0, "table": 2.0, "OUTSIDE": 0.0}  # unnormalized
        kernel = build_synthetic_kernel("book", support, dest_dist, stay_probability=0.5)
        assert kernel.states == support
        assert sum(kernel.dest_dist) == pytest.approx(1.0)
        assert kernel.dest_dist[0] == pytest.approx(0.5)

    def test_raises_on_missing_support_state(self):
        support = ("shelf", "table", "OUTSIDE")
        dest_dist = {"shelf": 1.0, "table": 1.0}  # missing OUTSIDE
        with pytest.raises(ValueError, match="missing support"):
            build_synthetic_kernel("book", support, dest_dist, stay_probability=0.5)

    def test_raises_on_all_zero_dest_dist(self):
        support = ("shelf", "OUTSIDE")
        dest_dist = {"shelf": 0.0, "OUTSIDE": 0.0}
        with pytest.raises(ValueError, match="sums to zero"):
            build_synthetic_kernel("book", support, dest_dist, stay_probability=0.5)

    def test_kernel_usable_with_posterior_validity_at_dwell(self):
        # _posterior_validity_at_dwell is the max propagated mass among
        # non-OUTSIDE states, which includes the renewal process's own
        # chance of landing back on the start state after "changing" —
        # so the expected value is alpha + (1-alpha)*dest_dist[start],
        # not the bare elicited stay_probability (alpha) itself.
        from dynamic_home_eqa.embodied.belief import _posterior_validity_at_dwell

        support = ("shelf", "table", "OUTSIDE")
        dest_dist = {"shelf": 0.6, "table": 0.4, "OUTSIDE": 0.0}
        stay_probability = 0.8
        kernel = build_synthetic_kernel("book", support, dest_dist, stay_probability=stay_probability)
        validity = _posterior_validity_at_dwell(kernel, "shelf", dwell_hours=REFERENCE_HOURS)
        expected = stay_probability + (1 - stay_probability) * dest_dist["shelf"]
        assert validity == pytest.approx(expected, abs=1e-6)
