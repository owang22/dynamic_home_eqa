"""
Tests for embodied/placement_check.py's pure classification logic — no
habitat_sim needed (check_placement() itself, which does real ray
casting, is exercised only by the render job's live integration test).
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.placement_check import (
    aggregate_placement_checks,
    classify_placement,
)


class TestClassifyPlacement:
    def test_supported_when_downward_hit_is_close(self):
        result = classify_placement(0.1, [None] * 8)
        assert result.supported is True
        assert result.support_distance_m == 0.1

    def test_unsupported_when_no_downward_hit(self):
        result = classify_placement(None, [None] * 8)
        assert result.supported is False
        assert result.support_distance_m is None

    def test_unsupported_when_downward_hit_too_far(self):
        result = classify_placement(1.5, [None] * 8)
        assert result.supported is False

    def test_not_embedded_when_ring_is_clear(self):
        result = classify_placement(0.1, [None] * 8)
        assert result.embedded is False
        assert result.embedded_ring_fraction == 0.0

    def test_embedded_when_majority_of_ring_hits_near_zero(self):
        ring = [0.01, 0.02, 0.01, None, 0.29, 0.28, 0.015, 0.3]
        result = classify_placement(0.1, ring)
        assert result.embedded is True
        assert result.embedded_ring_fraction == 0.5

    def test_not_embedded_when_few_ring_hits_near_zero(self):
        ring = [0.01, 0.29, 0.28, None, 0.29, 0.28, 0.27, 0.3]
        result = classify_placement(0.1, ring)
        assert result.embedded is False

    def test_passed_requires_supported_and_not_embedded(self):
        assert classify_placement(0.1, [None] * 8).passed is True
        assert classify_placement(None, [None] * 8).passed is False
        assert classify_placement(0.1, [0.01] * 8).passed is False

    def test_empty_ring_is_not_embedded(self):
        result = classify_placement(0.1, [])
        assert result.embedded is False
        assert result.embedded_ring_fraction == 0.0


class TestAggregatePlacementChecks:
    def test_pass_rates_by_category_and_anchor(self):
        checks = [
            ("keys", "bedroom", classify_placement(0.1, [None] * 8)),   # pass
            ("keys", "bedroom", classify_placement(None, [None] * 8)),  # fail
            ("cup", "kitchen.table", classify_placement(0.1, [None] * 8)),  # pass
        ]
        agg = aggregate_placement_checks(checks)
        assert agg["by_category"]["keys"] == {"n": 2, "pass_rate": 0.5}
        assert agg["by_category"]["cup"] == {"n": 1, "pass_rate": 1.0}
        assert agg["by_anchor"]["bedroom"] == {"n": 2, "pass_rate": 0.5}
        assert agg["by_anchor"]["kitchen.table"] == {"n": 1, "pass_rate": 1.0}
