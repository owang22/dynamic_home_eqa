"""Pure-logic tests for scripts/gold_set.py's diff_statuses — no
habitat_sim needed (running the gold set itself requires a real
renderer)."""
from __future__ import annotations

from dynamic_home_eqa.scripts.gold_set import GOLD_SET, diff_statuses


class TestDiffStatuses:
    def test_identical_expected_and_actual_reports_no_flips(self):
        expected = {"a": {"before_status": "ok", "after_status": "ok"}}
        rows = diff_statuses(expected, expected)
        assert rows == [{
            "name": "a", "expected_before": "ok", "actual_before": "ok", "before_flip": False,
            "expected_after": "ok", "actual_after": "ok", "after_flip": False, "flipped": False,
        }]

    def test_a_before_status_change_is_flagged_as_a_flip(self):
        expected = {"a": {"before_status": "ok", "after_status": "ok"}}
        actual = {"a": {"before_status": "object_spawn_failed", "after_status": "ok"}}
        rows = diff_statuses(expected, actual)
        assert rows[0]["before_flip"] is True
        assert rows[0]["after_flip"] is False
        assert rows[0]["flipped"] is True

    def test_an_item_missing_from_actual_is_still_reported(self):
        expected = {"a": {"before_status": "ok", "after_status": "ok"}}
        rows = diff_statuses(expected, {})
        assert rows[0]["actual_before"] is None
        assert rows[0]["flipped"] is True

    def test_report_lists_every_item_not_just_flips(self):
        expected = {
            "a": {"before_status": "ok", "after_status": "ok"},
            "b": {"before_status": "ok", "after_status": "ok"},
        }
        rows = diff_statuses(expected, expected)
        assert len(rows) == 2
        assert all(not r["flipped"] for r in rows)


class TestGoldSetDefinition:
    def test_has_exactly_eight_items(self):
        assert len(GOLD_SET) == 8

    def test_names_are_unique(self):
        names = [item.name for item in GOLD_SET]
        assert len(names) == len(set(names))

    def test_unresolved_name_item_is_the_only_synthetic_one(self):
        synthetic = [item for item in GOLD_SET if item.bad_label is not None]
        assert [item.name for item in synthetic] == ["unresolved-name"]
