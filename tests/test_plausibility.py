"""Unit tests for plausibility.py."""
from __future__ import annotations

from dynamic_home_eqa.plausibility import (
    capability_factor,
    day_report,
    egress_factor,
    pingpong_factor,
    score_confidence,
)
from dynamic_home_eqa.rooms import slot_room


def test_capability_factor_penalizes_toddler_restricted_category():
    assert capability_factor("laptop", "toddler") < 1.0


def test_capability_factor_neutral_for_adult():
    assert capability_factor("laptop", "adult") == 1.0


def test_capability_factor_neutral_for_toddler_unrestricted_category():
    assert capability_factor("book", "toddler") == 1.0


def test_egress_factor_penalizes_furniture_outdoors():
    assert egress_factor("stool", "outdoor") < 1.0


def test_egress_factor_neutral_for_non_furniture_outdoors():
    assert egress_factor("book", "outdoor") == 1.0


def test_egress_factor_neutral_indoors():
    assert egress_factor("stool", "living_room") == 1.0


def test_pingpong_factor_neutral_below_threshold():
    assert pingpong_factor([1.0, 1.2], 1.3) == 1.0


def test_pingpong_factor_penalizes_frequent_moves():
    # 4 prior moves within the last hour, threshold is 3 — should penalize.
    prior = [0.8, 0.85, 0.9, 0.95]
    assert pingpong_factor(prior, 1.0) < 1.0


def test_pingpong_factor_ignores_moves_outside_window():
    prior = [0.0, 0.1, 0.2, 0.3]  # all > 1h before t=5.0
    assert pingpong_factor(prior, 5.0) == 1.0


def test_score_confidence_multiplies_penalties():
    # toddler + laptop is a capability violation; score should be reduced
    # below 1.0 but stay positive.
    score = score_confidence("laptop", "toddler", "living_room", [], 10.0)
    assert 0.0 < score < 1.0


def test_score_confidence_full_when_nothing_flagged():
    score = score_confidence("book", "adult", "living_room", [], 10.0)
    assert score == 1.0


def test_day_report_flags_capability_violation():
    changes = [
        {"t": 10.0, "label": "laptop_1", "object_category": "laptop",
         "to_semantic": "office.desk", "mover": "Sophia"},
    ]
    report = day_report(changes, {"Sophia": "toddler"}, slot_room)
    assert report.count("capability") == 1


def test_day_report_flags_egress_violation():
    changes = [
        {"t": 10.0, "label": "stool_1", "object_category": "stool",
         "to_semantic": "outdoor", "mover": "Alex"},
    ]
    report = day_report(changes, {"Alex": "adult"}, slot_room)
    assert report.count("egress") == 1


def test_day_report_flags_pingpong():
    changes = [
        {"t": t, "label": "candle_1", "object_category": "candle",
         "to_semantic": "living_room.corner", "mover": "Alex"}
        for t in [0.0, 0.1, 0.2, 0.3, 0.4]
    ]
    report = day_report(changes, {"Alex": "adult"}, slot_room)
    assert report.count("pingpong") > 0


def test_day_report_no_warnings_on_clean_day():
    changes = [
        {"t": 10.0, "label": "book_1", "object_category": "book",
         "to_semantic": "living_room.shelf", "mover": "Alex"},
    ]
    report = day_report(changes, {"Alex": "adult"}, slot_room)
    assert not report.warnings
