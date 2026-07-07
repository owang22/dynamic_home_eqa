"""
Tests for scripts/e1_frontier_comparison.py's pure-logic pieces
(rank_change_table, _policy_summary) — the full main()/headline_table
path needs real generation_out data and is exercised by actually running
the script, not re-derived here with synthetic fixtures.
"""
from __future__ import annotations

from dynamic_home_eqa.scripts.e1_frontier_comparison import _policy_summary, rank_change_table


class TestRankChangeTable:
    def _summary(self, **policies):
        """policies: {name: (accuracy, travel_m)}."""
        return {name: {"accuracy": acc, "travel_m": travel, "n_clusters": 1}
                for name, (acc, travel) in policies.items()}

    def test_identical_accuracy_across_arms_yields_zero_delta_for_every_policy(self):
        real = self._summary(a=(0.9, 10.0), b=(0.7, 5.0))
        flat = self._summary(a=(0.9, 10.0), b=(0.7, 5.0))
        table = rank_change_table(real, flat)
        assert all(r["rank_delta"] == 0 for r in table)

    def test_detects_a_rank_flip_between_two_policies(self):
        # Under real_geodesic, a beats b; under flat, b beats a.
        real = self._summary(a=(0.9, 10.0), b=(0.7, 5.0))
        flat = self._summary(a=(0.6, 10.0), b=(0.8, 5.0))
        table = rank_change_table(real, flat)
        by_policy = {r["policy"]: r for r in table}
        assert by_policy["a"]["real_geodesic_rank"] == 1
        assert by_policy["a"]["flat_rank"] == 2
        assert by_policy["a"]["rank_delta"] == 1
        assert by_policy["b"]["real_geodesic_rank"] == 2
        assert by_policy["b"]["flat_rank"] == 1
        assert by_policy["b"]["rank_delta"] == -1

    def test_ties_broken_by_lower_travel(self):
        real = self._summary(a=(0.8, 20.0), b=(0.8, 5.0))
        flat = self._summary(a=(0.8, 20.0), b=(0.8, 5.0))
        table = rank_change_table(real, flat)
        by_policy = {r["policy"]: r for r in table}
        assert by_policy["b"]["real_geodesic_rank"] == 1  # lower travel wins the tie
        assert by_policy["a"]["real_geodesic_rank"] == 2

    def test_policy_missing_from_one_arm_is_excluded(self):
        real = self._summary(a=(0.9, 10.0), b=(0.7, 5.0))
        flat = self._summary(a=(0.6, 10.0))  # "b" never ran under flat
        table = rank_change_table(real, flat)
        assert {r["policy"] for r in table} == {"a"}

    def test_output_sorted_by_real_geodesic_rank(self):
        real = self._summary(a=(0.5, 1.0), b=(0.9, 1.0), c=(0.7, 1.0))
        flat = self._summary(a=(0.5, 1.0), b=(0.9, 1.0), c=(0.7, 1.0))
        table = rank_change_table(real, flat)
        assert [r["policy"] for r in table] == ["b", "c", "a"]


class TestPolicySummary:
    def _bootstrap_stub(self, point, n_clusters=3):
        class _Stub:
            pass
        s = _Stub()
        s.point = point
        s.n_clusters = n_clusters
        return s

    def test_averages_across_hazard_classes_for_one_policy(self):
        headline = [
            {"policy": "decay_voi", "accuracy": self._bootstrap_stub(0.8), "travel_m": self._bootstrap_stub(10.0)},
            {"policy": "decay_voi", "accuracy": self._bootstrap_stub(0.6), "travel_m": self._bootstrap_stub(20.0)},
        ]
        summary = _policy_summary(headline)
        assert summary["decay_voi"]["accuracy"] == 0.7
        assert summary["decay_voi"]["travel_m"] == 15.0

    def test_keeps_policies_separate(self):
        headline = [
            {"policy": "a", "accuracy": self._bootstrap_stub(0.9), "travel_m": self._bootstrap_stub(1.0)},
            {"policy": "b", "accuracy": self._bootstrap_stub(0.5), "travel_m": self._bootstrap_stub(2.0)},
        ]
        summary = _policy_summary(headline)
        assert set(summary) == {"a", "b"}
        assert summary["a"]["accuracy"] == 0.9
        assert summary["b"]["accuracy"] == 0.5

    def test_n_clusters_takes_the_max_across_hazard_classes(self):
        headline = [
            {"policy": "a", "accuracy": self._bootstrap_stub(0.9, n_clusters=1), "travel_m": self._bootstrap_stub(1.0, n_clusters=1)},
            {"policy": "a", "accuracy": self._bootstrap_stub(0.8, n_clusters=4), "travel_m": self._bootstrap_stub(2.0, n_clusters=4)},
        ]
        summary = _policy_summary(headline)
        assert summary["a"]["n_clusters"] == 4
