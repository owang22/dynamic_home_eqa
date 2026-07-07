"""
Tests for scripts/conformal_coverage_check.py's pure-logic pieces (Wilson
score interval, CoverageResult.within_ci). The full realized_coverage()/
main() path needs real generation_out data and is exercised by actually
running the script, not re-derived here with synthetic fixtures.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.scripts.conformal_coverage_check import CoverageResult, wilson_interval


class TestWilsonInterval:
    def test_zero_n_returns_nan(self):
        lo, hi = wilson_interval(0, 0)
        assert lo != lo and hi != hi  # NaN != NaN

    def test_interval_brackets_the_observed_proportion(self):
        lo, hi = wilson_interval(hits=8, n=10)
        assert lo <= 0.8 <= hi

    def test_interval_widens_with_smaller_n(self):
        lo_small, hi_small = wilson_interval(hits=4, n=5)
        lo_large, hi_large = wilson_interval(hits=400, n=500)
        assert (hi_small - lo_small) > (hi_large - lo_large)

    def test_interval_bounded_within_zero_and_one(self):
        lo, hi = wilson_interval(hits=10, n=10)
        assert 0.0 <= lo <= hi <= 1.0
        lo2, hi2 = wilson_interval(hits=0, n=10)
        assert 0.0 <= lo2 <= hi2 <= 1.0

    def test_symmetric_case_centers_near_half(self):
        lo, hi = wilson_interval(hits=50, n=100)
        assert lo < 0.5 < hi


class TestCoverageResult:
    def _result(self, ci_lo, ci_hi, target, n=10):
        return CoverageResult(
            axis="location", alpha=0.1, theta=0.5, n_held_out=n, hits=5,
            observed=0.5, ci_lo=ci_lo, ci_hi=ci_hi, target=target,
        )

    def test_within_ci_true_when_target_inside(self):
        assert self._result(ci_lo=0.4, ci_hi=0.6, target=0.5).within_ci

    def test_within_ci_false_when_target_outside(self):
        assert not self._result(ci_lo=0.4, ci_hi=0.6, target=0.9).within_ci

    def test_within_ci_false_when_no_held_out_data(self):
        assert not self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=0).within_ci

    def test_summary_reports_drift_when_outside_ci(self):
        result = self._result(ci_lo=0.4, ci_hi=0.6, target=0.9)
        assert "DRIFT" in result.summary()

    def test_summary_reports_ok_when_inside_ci(self):
        result = self._result(ci_lo=0.4, ci_hi=0.6, target=0.5)
        assert "OK" in result.summary()

    def test_summary_handles_zero_held_out_events(self):
        result = self._result(ci_lo=float("nan"), ci_hi=float("nan"), target=0.5, n=0)
        assert "0 held-out events" in result.summary()

    def test_data_starved_true_for_small_but_nonzero_n(self):
        assert self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=5).data_starved

    def test_data_starved_false_for_large_n(self):
        assert not self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=1000).data_starved

    def test_data_starved_false_for_zero_n(self):
        # 0 held-out events is its own ("cannot check coverage") case, not
        # a DATA-STARVED coverage result — see summary()'s early return.
        assert not self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=0).data_starved

    def test_summary_flags_data_starved_for_small_n(self):
        result = self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=5)
        assert "DATA-STARVED" in result.summary()

    def test_summary_omits_data_starved_flag_for_large_n(self):
        result = self._result(ci_lo=0.4, ci_hi=0.6, target=0.5, n=1000)
        assert "DATA-STARVED" not in result.summary()
