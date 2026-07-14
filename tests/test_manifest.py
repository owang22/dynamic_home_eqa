"""
Unit tests for generation/manifest.py, targeting the specific trace-integrity
bugs this phase fixed: insert-once bookkeeping, real-instance-backed
categories never being insert_new, no-op suppression, and chain consistency.

Uses real scene 102343992 (its furniture census determines which categories
are real-instance-backed vs. volatile) with hand-crafted displacement
proposals, rather than a full pipeline run, so each scenario is precise and
fast.
"""
from __future__ import annotations

from dynamic_home_eqa.generation.manifest import build_manifest
from dynamic_home_eqa.trace_validate import validate

_SCENE = "102343992"  # has real "chair" instances (Tier 2a), no real "phone" instances


def _base_result(displacements: list[dict]) -> dict:
    return {
        "household_id": "test_household",
        "persona": {"occupants": [{"name": "Alex", "age_band": "adult"}]},
        "traces": [
            {"occupant_name": "Alex", "activities": [
                {"activity": "resting", "location": "kitchen", "start": 0.0, "end": 24.0},
            ]},
        ],
        "clutter": [],
        "displacements": displacements,
    }


def _prop(cat, rel, anchor, start, end, occupant="Alex", location="kitchen", reason="test",
          activity="resting"):
    # Displacement proposals lead with `reason` (pre-proposal reasoning),
    # carried into the manifest verbatim alongside the window's activity.
    return {
        "object_category": cat, "target_relationship": rel, "target_anchor": anchor,
        "reason": reason, "_occupant": occupant, "_start": start, "_end": end,
        "_location": location, "_activity": activity,
    }


def _despawn_prop(cat, start, end, occupant="Alex", location="kitchen"):
    """A Phase 3 put-away: the occupant's own Tier-3 item leaves the scene.
    Mirrors what pipeline.py stamps onto a "put_away" proposal."""
    return {
        "object_category": cat, "target_relationship": "on", "target_anchor": "put_away",
        "reason": "put away for the night", "_occupant": occupant, "_start": start, "_end": end,
        "_location": location, "_activity": "evening_routine", "_despawn": True,
    }


def test_despawn_puts_tier3_item_away():
    # phone is placed out, then put away at night: the second event is a
    # removal to the symbolic "away" slot, chaining from where it was.
    # change_type is "remove" — the existing "object leaves the world"
    # contract env/replay.py & world_graph_adapter.py already implement.
    result = _base_result([
        _prop("phone", "on", "table", 1.0, 2.0),
        _despawn_prop("phone", 3.0, 4.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    phone_changes = sorted(
        (c for c in manifest["changes"] if c["object_category"] == "phone"),
        key=lambda c: c["t"],
    )
    assert len(phone_changes) == 2
    assert phone_changes[0]["change_type"] == "insert_new"
    assert phone_changes[1]["change_type"] == "remove"
    assert phone_changes[1]["to_semantic"] == "away"
    assert phone_changes[1]["from_semantic"] == phone_changes[0]["to_semantic"]
    # The occupant puts away their own carried item, so they're the mover.
    assert phone_changes[1]["mover"] == "Alex"
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()


def test_despawned_item_reappears_as_move_existing_from_away():
    # Put away, then brought back out: re-appearance must chain from "away"
    # as a move_existing (not a second insert_new), and stay trace-valid.
    result = _base_result([
        _prop("phone", "on", "table", 1.0, 2.0),
        _despawn_prop("phone", 3.0, 4.0),
        _prop("phone", "on", "counter", 5.0, 6.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    phone_changes = sorted(
        (c for c in manifest["changes"] if c["object_category"] == "phone"),
        key=lambda c: c["t"],
    )
    assert [c["change_type"] for c in phone_changes] == ["insert_new", "remove", "move_existing"]
    assert phone_changes[2]["from_semantic"] == "away"
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()


def test_despawn_without_prior_placement_is_dropped_and_counted():
    # A put-away for an item that was never placed out in this replay has
    # nothing to remove — dropped, not emitted as a despawn-from-nowhere.
    result = _base_result([
        _despawn_prop("phone", 1.0, 2.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    assert manifest["changes"] == []
    assert manifest["integrity_stats"]["dropped_despawn_notout"] == 1


def test_real_instance_backed_category_is_always_move_existing():
    result = _base_result([
        _prop("chair", "on", "counter", 1.0, 2.0),
        _prop("chair", "on", "table", 5.0, 6.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair_changes = [c for c in manifest["changes"] if c["object_category"] == "chair"]
    assert len(chair_changes) == 2
    assert all(c["change_type"] == "move_existing" for c in chair_changes)
    # First event's from_semantic is the real starting slot, never None —
    # the object already existed in the scene.
    assert chair_changes[0]["from_semantic"] is not None


def test_volatile_category_insert_new_fires_exactly_once():
    result = _base_result([
        _prop("phone", "on", "table", 1.0, 2.0),
        _prop("phone", "on", "counter", 3.0, 4.0),
        _prop("phone", "on", "table", 5.0, 6.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    phone_changes = sorted(
        (c for c in manifest["changes"] if c["object_category"] == "phone"),
        key=lambda c: c["t"],
    )
    assert len(phone_changes) == 3
    assert phone_changes[0]["change_type"] == "insert_new"
    assert phone_changes[0]["from_semantic"] is None
    assert phone_changes[1]["change_type"] == "move_existing"
    assert phone_changes[2]["change_type"] == "move_existing"


def test_no_op_proposal_is_dropped_and_counted():
    result = _base_result([
        _prop("chair", "on", "counter", 1.0, 2.0),
        _prop("chair", "on", "counter", 3.0, 4.0),  # same resolved slot -> no-op
        _prop("chair", "on", "table", 5.0, 6.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair_changes = [c for c in manifest["changes"] if c["object_category"] == "chair"]
    assert len(chair_changes) == 2  # the repeat-to-counter proposal was dropped
    assert manifest["integrity_stats"]["dropped_noop"] == 1


def test_chain_consistency_across_multiple_moves():
    result = _base_result([
        _prop("chair", "on", "counter", 1.0, 2.0),
        _prop("chair", "on", "table", 3.0, 4.0),
        _prop("chair", "next_to", "bed", 5.0, 6.0, location="bedroom"),
    ])
    result["traces"][0]["activities"] = [
        {"activity": "resting", "location": "kitchen", "start": 0.0, "end": 4.5},
        {"activity": "resting", "location": "bedroom", "start": 4.5, "end": 24.0},
    ]
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()


def test_unattended_proposal_is_rejected_and_counted():
    # Alex is only ever in "kitchen" per traces; a proposal claiming
    # "bedroom" has nobody present there and must be rejected.
    result = _base_result([
        _prop("phone", "on", "table", 1.0, 2.0, location="bedroom"),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    assert manifest["changes"] == []
    assert manifest["integrity_stats"]["rejected_unattended"] == 1


def test_reason_is_verbatim_and_change_carries_activity():
    # The proposal's leading `reason` (pre-proposal reasoning) is carried into
    # the manifest verbatim — no templating, no separate purpose field — and
    # each change names the activity window it was part of. No assumed_from is
    # stored, and the retired divergence counter is gone from integrity_stats.
    result = _base_result([
        _prop("chair", "on", "counter", 1.0, 2.0),
        _prop("chair", "on", "table", 3.0, 4.0,
              reason="cooking needs counter space, so the chair moves to the table",
              activity="cooking"),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    second = sorted((c for c in manifest["changes"] if c["object_category"] == "chair"),
                    key=lambda c: c["t"])[1]
    assert "llm_claimed_from" not in second
    assert "purpose" not in second
    assert second["reason"] == "cooking needs counter space, so the chair moves to the table"
    assert second["activity"] == "cooking"
    assert "llm_claim_divergence" not in manifest["integrity_stats"]


def test_clutter_placement_resolves_to_move_existing_not_insert_new():
    result = _base_result([
        _prop("book", "on", "table", 1.0, 2.0),
    ])
    result["clutter"] = [
        {"object_category": "book", "target_relationship": "on", "target_anchor": "shelves",
         "reason": "starting placement"},
    ]
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    book_changes = [c for c in manifest["changes"] if c["object_category"] == "book"]
    assert len(book_changes) == 1
    assert book_changes[0]["change_type"] == "move_existing"


# ---------------------------------------------------------------------------
# Anchor Admission round (Version B): reachability backstop + capacity gate.
# load_anchor_admission_map is monkeypatched (rather than relying on a real
# cache file for scene 102343992) so each test controls exactly what the
# admission map says, independent of whether scripts/compute_anchor_admission_map.py
# has ever actually been run for this scene.
# ---------------------------------------------------------------------------

def _patch_admission_map(monkeypatch, admission_map):
    monkeypatch.setattr(
        "dynamic_home_eqa.generation.manifest.load_anchor_admission_map",
        lambda scene_id: admission_map,
    )


def test_unreachable_anchor_is_rejected_and_counted_when_flag_on(monkeypatch):
    # Reachability Removal Phase 1: the hard gate is now opt-in
    # (reachability_filtering=True) rather than always-on — this proves
    # the mechanism itself still works when explicitly restored, so it
    # doesn't silently bit-rot before door handling lands.
    _patch_admission_map(monkeypatch, {
        "anchors": {"kitchen.counter": {"reachable": False, "capacity": None, "capacity_source": None}},
    })
    result = _base_result([_prop("phone", "on", "counter", 1.0, 2.0)])
    manifest = build_manifest(_SCENE, "test_profile", 0, result, reachability_filtering=True)
    assert manifest["changes"] == []
    assert manifest["integrity_stats"]["rejected_unreachable_anchor"] == 1


def test_unreachable_anchor_is_kept_by_default(monkeypatch):
    # Phase 1's actual default: reachability_filtering=False means a
    # navmesh-unreachable anchor no longer rejects a proposal at all —
    # with interior doors closed and out of scope, navmesh reachability
    # is wrong for most indoor rooms.
    _patch_admission_map(monkeypatch, {
        "anchors": {"kitchen.counter": {"reachable": False, "capacity": None, "capacity_source": None}},
    })
    result = _base_result([_prop("phone", "on", "counter", 1.0, 2.0)])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    assert len(manifest["changes"]) == 1
    assert manifest["integrity_stats"]["rejected_unreachable_anchor"] == 0


def test_capacity_one_anchor_rejects_second_arrival_and_counts(monkeypatch):
    _patch_admission_map(monkeypatch, {
        "anchors": {"kitchen.counter": {"reachable": True, "capacity": 1, "capacity_source": "receptacle"}},
    })
    result = _base_result([
        _prop("phone", "on", "counter", 1.0, 2.0),
        _prop("wallet", "on", "counter", 3.0, 4.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    changes = manifest["changes"]
    assert len(changes) == 1
    assert changes[0]["object_category"] == "phone"
    assert manifest["integrity_stats"]["rejected_over_capacity"] == 1


def test_capacity_frees_up_after_the_occupant_moves_away(monkeypatch):
    _patch_admission_map(monkeypatch, {
        "anchors": {
            "kitchen.counter": {"reachable": True, "capacity": 1, "capacity_source": "receptacle"},
            "kitchen.cabinet": {"reachable": True, "capacity": None, "capacity_source": None},
        },
    })
    result = _base_result([
        _prop("phone", "on", "counter", 1.0, 2.0),   # arrives, counter now 1/1
        _prop("phone", "on", "cabinet", 3.0, 4.0),   # phone leaves -> frees counter
        _prop("wallet", "on", "counter", 5.0, 6.0),  # wallet can now arrive
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    assert len(manifest["changes"]) == 3
    assert manifest["integrity_stats"]["rejected_over_capacity"] == 0


def test_no_admission_map_disables_gates_and_is_recorded_not_silent(monkeypatch):
    _patch_admission_map(monkeypatch, None)
    result = _base_result([_prop("chair", "on", "counter", 1.0, 2.0)])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    assert manifest["integrity_stats"]["admission_map_used"] is False
    assert manifest["integrity_stats"]["rejected_unreachable_anchor"] == 0
    assert manifest["integrity_stats"]["rejected_over_capacity"] == 0
    assert len(manifest["changes"]) == 1


# ---------------------------------------------------------------------------
# Tuck/untuck (chairs slide on the floor: pulled out via next_to, tucked back
# via tucked_under — resolve_slot gives tucked its own "<anchor>.tucked" slot).
# ---------------------------------------------------------------------------

def test_tuck_untuck_cycle_is_real_changes_not_noops():
    # chair pulled out beside the table, then tucked back under the SAME
    # table: distinct slots, so the tuck is a real change (not no-op
    # suppressed), and the chain stays valid.
    result = _base_result([
        _prop("chair", "next_to", "kitchen.table_1", 1.0, 2.0),
        _prop("chair", "tucked_under", "kitchen.table_1", 3.0, 4.0,
              reason="done with breakfast, tucking the chair back in"),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair = sorted((c for c in manifest["changes"] if c["object_category"] == "chair"),
                   key=lambda c: c["t"])
    assert len(chair) == 2
    assert chair[0]["to_semantic"] == "kitchen.table_1"
    assert chair[1]["to_semantic"] == "kitchen.table_1.tucked"
    assert chair[1]["from_semantic"] == "kitchen.table_1"
    assert manifest["integrity_stats"]["dropped_noop"] == 0
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()


def test_double_tuck_at_same_anchor_is_a_noop():
    # tucking an already-tucked chair at the same furniture IS a no-op.
    result = _base_result([
        _prop("chair", "tucked_under", "kitchen.table_1", 1.0, 2.0),
        _prop("chair", "tucked_under", "kitchen.table_1", 3.0, 4.0),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair = [c for c in manifest["changes"] if c["object_category"] == "chair"]
    assert len(chair) == 1
    assert manifest["integrity_stats"]["dropped_noop"] == 1


def test_multiple_instances_animate_independently_by_room():
    # Scene 102343992 has two real chairs. Proposals in DIFFERENT rooms must
    # animate the chair already in that room, not drag one chair everywhere.
    result = _base_result([
        _prop("chair", "next_to", "kitchen.table_1", 1.0, 2.0, location="kitchen"),
        _prop("chair", "next_to", "kitchen.counter_1", 3.0, 4.0, location="kitchen"),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair = sorted((c for c in manifest["changes"] if c["object_category"] == "chair"),
                   key=lambda c: c["t"])
    assert len(chair) == 2
    # Second proposal finds the chair the FIRST move brought into the kitchen
    # (same instance, now in-room), chaining correctly.
    assert chair[0]["label"] == chair[1]["label"]
    assert chair[1]["from_semantic"] == chair[0]["to_semantic"]
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()
