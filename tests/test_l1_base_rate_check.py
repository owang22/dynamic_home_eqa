"""
Tests for scripts/l1_base_rate_check.py's pure-logic pieces — no
habitat_sim, no generation_out dependency for these.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.scripts.l1_base_rate_check import brier, mean_brier, stay_put_points


class TestBrier:
    def test_perfect_confident_prediction_scores_zero(self):
        assert brier(1.0, True) == pytest.approx(0.0)
        assert brier(0.0, False) == pytest.approx(0.0)

    def test_worst_prediction_scores_one(self):
        assert brier(1.0, False) == pytest.approx(1.0)
        assert brier(0.0, True) == pytest.approx(1.0)

    def test_uniform_prediction_scores_quarter(self):
        assert brier(0.5, True) == pytest.approx(0.25)
        assert brier(0.5, False) == pytest.approx(0.25)


class TestStayPutPoints:
    def test_always_predicts_one(self):
        events = [("book", "shelf", 5.0), ("candle", "table", 0.1)]
        points = stay_put_points(events, wait_hours=1.0)
        assert all(p == 1.0 for p, _r in points)

    def test_realized_matches_dwell_survival(self):
        events = [("book", "shelf", 5.0), ("candle", "table", 0.1)]
        points = stay_put_points(events, wait_hours=1.0)
        assert points[0] == (1.0, True)   # dwell 5.0 >= wait 1.0
        assert points[1] == (1.0, False)  # dwell 0.1 < wait 1.0

    def test_length_matches_input(self):
        events = [("a", "s1", 1.0), ("b", "s2", 2.0), ("c", "s3", 3.0)]
        assert len(stay_put_points(events, wait_hours=1.5)) == 3


class TestMeanBrier:
    def test_averages_correctly(self):
        points = [(1.0, True), (1.0, False), (0.0, False)]
        # briers: 0.0, 1.0, 0.0 -> mean 1/3
        assert mean_brier(points) == pytest.approx(1 / 3)

    def test_all_correct_gives_zero(self):
        points = [(1.0, True), (0.0, False)]
        assert mean_brier(points) == pytest.approx(0.0)
