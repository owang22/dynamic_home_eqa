"""
Tests for scripts/voi_boundary_validation.py's pure-logic pieces
(_resensed, transition_table, find_declined_resenses) — the full sweep
(run_location_sweep/run_state_sweep/main) needs habitat_sim and real
generation_out data, exercised by actually running the script.
"""
from __future__ import annotations

from dynamic_home_eqa.scripts.voi_boundary_validation import (
    _resensed,
    find_declined_resenses,
    transition_table,
)


def _row(wait_hours=1.0, label="book_1", invocations=1, distance=0.0):
    return {"wait_hours": wait_hours, "label": label, "policy_invocations": invocations, "distance_traveled_m": distance}


class TestResensed:
    def test_more_than_one_invocation_counts_as_resensed(self):
        assert _resensed(_row(invocations=2, distance=0.0))

    def test_nonzero_distance_counts_as_resensed(self):
        assert _resensed(_row(invocations=1, distance=5.0))

    def test_single_invocation_zero_distance_is_not_resensed(self):
        assert not _resensed(_row(invocations=1, distance=0.0))


class TestTransitionTable:
    def test_fraction_resensed_computed_per_wait_per_lambda(self):
        rows_by_lw = {
            0.001: [_row(wait_hours=1.0, label="a", invocations=2, distance=5.0),
                    _row(wait_hours=1.0, label="b", invocations=1, distance=0.0)],
            1.0: [_row(wait_hours=1.0, label="a", invocations=1, distance=0.0),
                  _row(wait_hours=1.0, label="b", invocations=1, distance=0.0)],
        }
        table = transition_table(rows_by_lw)
        assert table[1.0][0.001] == 0.5
        assert table[1.0][1.0] == 0.0

    def test_monotonic_decline_is_representable(self):
        rows_by_lw = {
            0.001: [_row(label="a", invocations=2, distance=5.0), _row(label="b", invocations=2, distance=5.0)],
            0.1: [_row(label="a", invocations=2, distance=5.0), _row(label="b", invocations=1, distance=0.0)],
            10.0: [_row(label="a", invocations=1, distance=0.0), _row(label="b", invocations=1, distance=0.0)],
        }
        table = transition_table(rows_by_lw)
        fractions = [table[1.0][lw] for lw in (0.001, 0.1, 10.0)]
        assert fractions == [1.0, 0.5, 0.0]


class TestFindDeclinedResenses:
    def test_finds_trials_that_did_not_resense(self):
        rows_by_lw = {
            0.001: [_row(wait_hours=1.0, label="a", invocations=1, distance=0.0)],
        }
        declines = find_declined_resenses(rows_by_lw)
        assert len(declines) == 1
        assert declines[0]["latency_weight"] == 0.001
        assert declines[0]["label"] == "a"

    def test_ignores_resensed_trials(self):
        rows_by_lw = {0.001: [_row(invocations=2, distance=5.0)]}
        assert find_declined_resenses(rows_by_lw) == []

    def test_empty_when_no_lambda_has_any_declines(self):
        rows_by_lw = {
            0.001: [_row(invocations=2, distance=5.0)],
            1.0: [_row(invocations=2, distance=5.0)],
        }
        assert find_declined_resenses(rows_by_lw) == []
