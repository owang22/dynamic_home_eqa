"""
Tests for scripts/render_suspicious_events.py's pure-logic suspicion
scoring — no habitat_sim, no rendering needed for these.
"""
from __future__ import annotations

from dynamic_home_eqa.scripts.render_suspicious_events import pool_category_anchor_counts, score_events


def _change(t, label, category, from_semantic, to_semantic, confidence=1.0):
    return {
        "t": t, "label": label, "object_category": category, "change_type": "move_existing",
        "from_semantic": from_semantic, "to_semantic": to_semantic, "confidence": confidence,
        "mover": "Test", "reason": "test reason",
    }


class TestScoreEvents:
    def test_cross_room_move_scores_higher_than_same_room(self):
        changes = [
            _change(1.0, "book_1", "book", "bedroom", "kitchen"),
            _change(1.0, "cup_1", "cup", "kitchen", "kitchen.fridge"),
        ]
        counts = {("book", "kitchen"): 10, ("cup", "kitchen.fridge"): 10}
        scored = score_events(changes, counts)
        by_label = {c["label"]: (s, r) for s, c, r in scored}
        assert by_label["book_1"][0] > by_label["cup_1"][0]
        assert any("cross-room" in r for r in by_label["book_1"][1])

    def test_rare_category_anchor_pairing_flagged(self):
        changes = [_change(1.0, "vase_1", "vase", "kitchen", "bathroom.bathtub")]
        counts = {("vase", "bathroom.bathtub"): 1}
        scored = score_events(changes, counts)
        score, event, reasons = scored[0]
        assert any("rare pairing" in r for r in reasons)

    def test_low_confidence_increases_score(self):
        changes = [
            _change(1.0, "a_1", "a", "x", "y", confidence=1.0),
            _change(1.0, "b_1", "b", "x", "y", confidence=0.3),
        ]
        counts = {("a", "y"): 10, ("b", "y"): 10}
        scored = score_events(changes, counts)
        by_label = {c["label"]: s for s, c, _r in scored}
        assert by_label["b_1"] > by_label["a_1"]

    def test_ping_pong_detected(self):
        changes = [
            _change(1.0, "keys_1", "keys", None, "bedroom"),
            _change(2.0, "keys_1", "keys", "bedroom", "kitchen"),
            _change(3.0, "keys_1", "keys", "kitchen", "bedroom"),  # returns to t=1's anchor
        ]
        counts = {("keys", "bedroom"): 10, ("keys", "kitchen"): 10}
        scored = score_events(changes, counts)
        by_t = {c["t"]: r for _s, c, r in scored}
        assert any("ping-pong" in r for r in by_t[3.0])
        assert not any("ping-pong" in r for r in by_t[1.0])

    def test_state_change_events_excluded(self):
        changes = [
            _change(1.0, "book_1", "book", "bedroom", "kitchen"),
            {"t": 1.0, "label": "fridge_1", "change_type": "state_change", "object_category": "fridge",
             "state_variable": "door", "from_state": "closed", "to_state": "open", "confidence": 1.0},
        ]
        counts = {("book", "kitchen"): 10}
        scored = score_events(changes, counts)
        assert len(scored) == 1
        assert scored[0][1]["label"] == "book_1"

    def test_sorted_descending_by_score(self):
        changes = [
            _change(1.0, "a_1", "a", "kitchen", "kitchen.fridge"),  # same room, common
            _change(1.0, "b_1", "b", "bedroom", "kitchen"),  # cross-room + rare
        ]
        counts = {("a", "kitchen.fridge"): 100, ("b", "kitchen"): 1}
        scored = score_events(changes, counts)
        assert scored[0][1]["label"] == "b_1"
        assert scored[0][0] > scored[1][0]


class TestPoolCategoryAnchorCounts:
    def test_counts_across_folders(self, tmp_path):
        folder_a = tmp_path / "scene_a"
        folder_b = tmp_path / "scene_b"
        for folder, changes in (
            (folder_a, [_change(1.0, "book_1", "book", None, "kitchen")]),
            (folder_b, [_change(1.0, "book_2", "book", None, "kitchen"), _change(1.0, "cup_1", "cup", None, "kitchen")]),
        ):
            folder.mkdir()
            (folder / "manifest.json").write_text(__import__("json").dumps({"changes": changes}))
        counts = pool_category_anchor_counts(tmp_path, ["scene_a", "scene_b"])
        assert counts[("book", "kitchen")] == 2
        assert counts[("cup", "kitchen")] == 1
