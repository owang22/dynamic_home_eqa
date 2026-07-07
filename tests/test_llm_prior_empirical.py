"""
Tests for llm_prior/empirical.py — pure Python over synthetic change
lists, no generation_out/ or model dependency.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.llm_prior.empirical import empirical_location_frequency, empirical_stay_probability


def _change(t, category, to_semantic, label="book_1"):
    return {"t": t, "label": label, "object_category": category, "to_semantic": to_semantic}


class TestEmpiricalLocationFrequency:
    def test_counts_normalize_to_one(self):
        bucket = [_change(1.0, "book", "shelf"), _change(2.0, "book", "table"), _change(3.0, "book", "shelf")]
        freq = empirical_location_frequency(bucket, "book", ("shelf", "table", "OUTSIDE"))
        assert freq["shelf"] == pytest.approx(2 / 3)
        assert freq["table"] == pytest.approx(1 / 3)
        assert freq["OUTSIDE"] == pytest.approx(0.0)

    def test_ignores_other_categories(self):
        bucket = [_change(1.0, "book", "shelf"), _change(2.0, "candle", "table")]
        freq = empirical_location_frequency(bucket, "book", ("shelf", "OUTSIDE"))
        assert freq["shelf"] == pytest.approx(1.0)

    def test_raises_when_category_absent_from_bucket(self):
        bucket = [_change(1.0, "candle", "table")]
        with pytest.raises(ValueError, match="no change events"):
            empirical_location_frequency(bucket, "book", ("shelf", "OUTSIDE"))

    def test_dest_outside_support_still_counted_toward_total(self):
        # A destination not in the fixed support (shouldn't happen given
        # D1's support is derived from real anchors, but must not corrupt
        # the total's denominator if it ever does).
        bucket = [_change(1.0, "book", "shelf"), _change(2.0, "book", "some_weird_slot")]
        freq = empirical_location_frequency(bucket, "book", ("shelf", "OUTSIDE"))
        assert freq["shelf"] == pytest.approx(0.5)


class TestEmpiricalStayProbability:
    def test_computes_survival_fraction(self):
        bucket = [_change(1.0, "book", "shelf")]
        all_by_label = {
            "book_1": [
                {"t": 1.0, "object_category": "book"},
                {"t": 3.0, "object_category": "book"},  # gap=2h
            ],
        }
        p = empirical_stay_probability(bucket, all_by_label, "book", reference_hours=1.0)
        assert p == pytest.approx(1.0)  # 2h gap >= 1h reference

    def test_short_gap_does_not_survive(self):
        bucket = [_change(1.0, "book", "shelf")]
        all_by_label = {
            "book_1": [
                {"t": 1.0, "object_category": "book"},
                {"t": 1.5, "object_category": "book"},  # gap=0.5h
            ],
        }
        p = empirical_stay_probability(bucket, all_by_label, "book", reference_hours=1.0)
        assert p == pytest.approx(0.0)

    def test_raises_when_category_absent_from_bucket(self):
        with pytest.raises(ValueError, match="no change events"):
            empirical_stay_probability([], {}, "book", reference_hours=1.0)
