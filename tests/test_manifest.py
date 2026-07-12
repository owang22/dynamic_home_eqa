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


def _prop(cat, rel, anchor, start, end, occupant="Alex", location="kitchen", assumed_from=None):
    p = {
        "object_category": cat, "target_relationship": rel, "target_anchor": anchor,
        "reason": "test", "_occupant": occupant, "_start": start, "_end": end,
        "_location": location,
    }
    if assumed_from is not None:
        p["assumed_from"] = assumed_from
    return p


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


def test_llm_claim_divergence_is_counted_not_used_for_from_semantic():
    result = _base_result([
        _prop("chair", "on", "counter", 1.0, 2.0, assumed_from="the moon"),
    ])
    manifest = build_manifest(_SCENE, "test_profile", 0, result)
    chair_change = manifest["changes"][0]
    assert chair_change["llm_claimed_from"] == "the moon"
    assert chair_change["from_semantic"] != "the moon"  # real tracked state, not the LLM's claim
    assert manifest["integrity_stats"]["llm_claim_divergence"] == 1


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
