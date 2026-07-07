"""
Tests for embodied/sampling.py's frozen-label qualification rule: a label
must (1) exist at patrol_start and (2) have every historical anchor slot
reachable from the agent's start pose. This is the rule that replaced the
original FROZEN_LABELS (10 labels picked only by "moved at least once"),
after the M1 gate's 80% abstain rate traced to exactly these two properties
going unscreened.

Requires habitat_sim (qualify_labels builds a real EmbodiedWorld) —
skipped, not failed, when unavailable.
"""
from __future__ import annotations

import json
import pathlib

import pytest

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"
_REAL_SCENE = "102343992"


def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)


@pytest.fixture(scope="module")
def real_day():
    result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    return result, manifest


def test_candidate_labels_matches_dynamic_labels_in_manifest(real_day):
    from dynamic_home_eqa.embodied.sampling import candidate_labels

    _result, manifest = real_day
    expected = sorted({c["label"] for c in manifest["changes"]})
    assert list(candidate_labels(manifest)) == expected


def test_qualify_labels_flags_missing_at_patrol_start(real_day):
    from dynamic_home_eqa.embodied.sampling import qualify_labels

    result, manifest = real_day
    # book_1 is present from t=0 (in_initial); keys_1 is insert_new at
    # t=6.057 — patrol_start=6.0 must split these two ways.
    results = qualify_labels(
        scene=_REAL_SCENE, eval_result=result, eval_manifest=manifest,
        history_manifests=[manifest], patrol_start=6.0,
    )
    by_label = {r.label: r for r in results}
    assert by_label["book_1"].exists_at_patrol_start
    assert not by_label["keys_1"].exists_at_patrol_start
    assert not by_label["keys_1"].qualifies
    assert "does not exist" in by_label["keys_1"].reason()


def test_qualify_labels_flags_unreachable_historical_slot(real_day, monkeypatch):
    """world._ensure_sim already filters disqualified (sub-threshold-
    island) anchors out of _anchor_positions, so a slot like
    living_room.sofa now silently resolves to a reachable room-centroid
    fallback instead — the anchor-filtering fix (world.py) working as
    intended. To test qualify_labels' own reachability-checking logic in
    isolation (not world.py's already-covered anchor filtering, see
    test_reachability.py), monkeypatch _resolve_slot_position to return
    the raw, genuinely-disconnected position for one synthetic slot."""
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.embodied.sampling import qualify_labels
    from dynamic_home_eqa.topdown_map import anchor_world_positions

    result, manifest = real_day
    raw_sofa_pos = anchor_world_positions(_REAL_SCENE)["living_room.sofa"]

    synthetic_manifest = {
        "changes": manifest["changes"] + [{
            "t": 6.5, "label": "book_1", "change_type": "move_existing",
            "object_category": "book", "from_semantic": "living_room.shelf",
            "to_semantic": "unreachable_test_slot", "mover": "test",
            "llm_claimed_from": None, "reason": "test",
            "confidence": 1.0, "object_handle": None,
        }],
    }

    original = EmbodiedWorld._resolve_slot_position

    def _patched(self, label, slot):
        if slot == "unreachable_test_slot":
            return raw_sofa_pos
        return original(self, label, slot)

    monkeypatch.setattr(EmbodiedWorld, "_resolve_slot_position", _patched)

    results = qualify_labels(
        scene=_REAL_SCENE, eval_result=result, eval_manifest=manifest,
        history_manifests=[synthetic_manifest], patrol_start=6.0,
    )
    by_label = {r.label: r for r in results}
    assert "unreachable_test_slot" in by_label["book_1"].unreachable_slots
    assert not by_label["book_1"].qualifies
    assert "unreachable" in by_label["book_1"].reason()


def test_qualifying_label_has_no_unreachable_slots(real_day):
    from dynamic_home_eqa.embodied.sampling import qualify_labels

    result, manifest = real_day
    results = qualify_labels(
        scene=_REAL_SCENE, eval_result=result, eval_manifest=manifest,
        history_manifests=[manifest], patrol_start=6.0,
    )
    by_label = {r.label: r for r in results}
    assert by_label["book_1"].qualifies
    assert by_label["book_1"].unreachable_slots == ()
