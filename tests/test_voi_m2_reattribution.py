"""
Tests for scripts/voi_m2_reattribution.py's pure-logic piece
(_discovery_counts) — the full rerun/decompose path needs habitat_sim and
real generation_out data, exercised by actually running the script.
"""
from __future__ import annotations

from dataclasses import dataclass

from dynamic_home_eqa.scripts.voi_m2_reattribution import _discovery_counts


@dataclass
class _FakeRecord:
    transition: str


def test_counts_each_transition_category():
    records = [
        _FakeRecord("wrong_to_right"), _FakeRecord("wrong_to_right"),
        _FakeRecord("wrong_to_abstain"), _FakeRecord("unchanged_right"),
    ]
    counts = _discovery_counts(records)
    assert counts == {"wrong_to_right": 2, "wrong_to_abstain": 1, "unchanged_right": 1}


def test_empty_records_gives_empty_counts():
    assert _discovery_counts([]) == {}
