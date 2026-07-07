"""
Tests for scripts/kernel_reliability_diagram.py's pure-logic pieces
(bin_reliability) — the full reliability_points/main() path needs real
generation_out data and is exercised by actually running the script, not
re-derived here with synthetic fixtures.
"""
from __future__ import annotations

from dynamic_home_eqa.scripts.kernel_reliability_diagram import bin_reliability


class TestBinReliability:
    def test_perfectly_calibrated_points_land_on_the_diagonal(self):
        # All points at predicted=0.75 with 75% actually surviving.
        points = [(0.75, True)] * 3 + [(0.75, False)]
        bins = bin_reliability(points, n_bins=10)
        assert len(bins) == 1
        assert bins[0]["mean_predicted"] == 0.75
        assert bins[0]["observed_frequency"] == 0.75
        assert bins[0]["n"] == 4

    def test_empty_bins_are_omitted_not_zero(self):
        points = [(0.05, True), (0.95, False)]
        bins = bin_reliability(points, n_bins=10)
        # Only the two occupied bins appear, not all 10.
        assert len(bins) == 2

    def test_overconfidence_shows_as_observed_below_predicted(self):
        # Predicted validity 0.8, but only 20% actually survived.
        points = [(0.8, True)] * 2 + [(0.8, False)] * 8
        bins = bin_reliability(points, n_bins=10)
        assert bins[0]["mean_predicted"] == 0.8
        assert bins[0]["observed_frequency"] == 0.2
        assert bins[0]["observed_frequency"] < bins[0]["mean_predicted"]

    def test_underconfidence_shows_as_observed_above_predicted(self):
        points = [(0.1, True)] * 8 + [(0.1, False)] * 2
        bins = bin_reliability(points, n_bins=10)
        assert bins[0]["observed_frequency"] > bins[0]["mean_predicted"]

    def test_bin_boundaries_partition_zero_to_one(self):
        points = [(0.0, True), (0.15, True), (0.99, False), (1.0, False)]
        bins = bin_reliability(points, n_bins=10)
        for b in bins:
            assert 0.0 <= b["bin_lo"] < b["bin_hi"] <= 1.0

    def test_n_matches_total_points_across_bins(self):
        points = [(0.1 * i, i % 2 == 0) for i in range(10)]
        bins = bin_reliability(points, n_bins=10)
        assert sum(b["n"] for b in bins) == len(points)
