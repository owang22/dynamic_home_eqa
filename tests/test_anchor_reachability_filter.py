"""Pure-logic tests for generation/anchor_reachability_filter.py."""
from __future__ import annotations

from dynamic_home_eqa.generation.anchor_reachability_filter import (
    prune_room_inventory_by_reachability,
    prune_scene_wide_by_reachability,
)


def _admission_map(**anchors) -> dict:
    return {"anchors": {name: {"reachable": v, "capacity": None, "capacity_source": None}
                         for name, v in anchors.items()}}


class TestPruneRoomInventoryByReachability:
    def test_none_admission_map_is_a_no_op(self):
        room_inventory = {"dining_room": {"table": 1}}
        assert prune_room_inventory_by_reachability(room_inventory, {}, None) is room_inventory

    def test_drops_a_category_only_in_the_room_where_it_resolves_unreachable(self):
        # "table" is the SLOT_ANCHORS anchor for BOTH dining.table and
        # office.desk (rooms.py's own documented example) — a real,
        # concrete case where the same category resolves to a DIFFERENT
        # slot per room. dining.table is reachable, office.desk is not:
        # the precision this whole design is built to preserve is that
        # "table" stays offered in dining_room even though it's dropped
        # in office.
        admission_map = _admission_map(**{"dining.table": True, "office.desk": False})
        room_inventory = {"dining_room": {"table": 1}, "office": {"table": 1}}
        pruned = prune_room_inventory_by_reachability(room_inventory, {}, admission_map)
        assert pruned == {"dining_room": {"table": 1}}
        assert "office" not in pruned

    def test_keeps_a_category_whose_slot_cannot_be_resolved_at_all(self):
        # No SLOT_ANCHORS entry for this category in this room, and no
        # real instance in room_instance_categories either -> resolve_slot
        # raises UnresolvableSlotError -> the filter must NOT drop it
        # (that's the existing unbacked-anchor gate's job, not this one's).
        admission_map = _admission_map(**{"dining.table": True})
        room_inventory = {"kitchen": {"totally_unknown_category": 1}}
        pruned = prune_room_inventory_by_reachability(room_inventory, {"kitchen": set()}, admission_map)
        assert pruned == room_inventory

    def test_empty_room_inventory_is_a_no_op(self):
        admission_map = _admission_map(**{"dining.table": False})
        assert prune_room_inventory_by_reachability({}, {}, admission_map) == {}
        assert prune_room_inventory_by_reachability(None, {}, admission_map) is None


class TestPruneSceneWideByReachability:
    def test_none_admission_map_is_a_no_op(self):
        anchor_inventory = {"table": 3}
        assert prune_scene_wide_by_reachability(anchor_inventory, {}, None) is anchor_inventory

    def test_drops_a_category_whose_room_agnostic_slot_is_unreachable(self):
        # room=None resolution for a STATEFUL_FURNITURE-style bare category
        # (e.g. "tv") resolves to itself (see rooms.resolve_slot's
        # room=None branch) -- confirmed unreachable here.
        admission_map = _admission_map(tv=False)
        pruned = prune_scene_wide_by_reachability({"tv": 1, "table": 2}, {}, admission_map)
        assert "tv" not in pruned
        # "table" has no entry in this admission_map at all -> is_reachable
        # returns None (unknown, not known-unreachable) -> kept.
        assert pruned["table"] == 2

    def test_empty_anchor_inventory_is_a_no_op(self):
        admission_map = _admission_map(tv=False)
        assert prune_scene_wide_by_reachability({}, {}, admission_map) == {}
        assert prune_scene_wide_by_reachability(None, {}, admission_map) is None
