"""Pure-logic tests for scripts/build_realized_day.py's habitat_sim-free
pieces — anchor classification and the packing candidate generator. The
actual placement (habitat_sim raycasts/rigid objects) is exercised by
running the builder for real (see results/reports/realized_day_build_log.json)."""
from __future__ import annotations

import math

import pytest

from dynamic_home_eqa.scripts.build_realized_day import (
    NO_ASSET_CATEGORIES,
    SPAWNABLE_ASSET_BY_CATEGORY,
    CATEGORY_SUBSTITUTED,
    UncoveredCategoryError,
    _bind_categories,
    _packing_candidates,
    assert_category_has_asset_coverage,
    classify_anchor,
    normalize_stateful_anchor,
)


class TestNormalizeStatefulAnchor:
    def test_room_qualified_stateful_furniture_aliases_to_bare_category(self):
        assert normalize_stateful_anchor("kitchen.fridge") == "fridge"
        assert normalize_stateful_anchor("living_room.tv") == "tv"

    def test_non_stateful_dotted_anchor_is_unchanged(self):
        assert normalize_stateful_anchor("dining.table") == "dining.table"

    def test_bare_anchor_is_unchanged(self):
        assert normalize_stateful_anchor("fridge") == "fridge"
        assert normalize_stateful_anchor("kitchen") == "kitchen"


class TestClassifyAnchor:
    def test_bare_room_name_is_region(self):
        kind, cats = classify_anchor("kitchen")
        assert kind == "region"

    def test_on_surface_slot_is_instance(self):
        kind, cats = classify_anchor("dining.table")
        assert kind == "instance"
        assert "table" in cats

    def test_room_qualified_stateful_furniture_is_instance_via_alias(self):
        kind, cats = classify_anchor("kitchen.fridge")
        assert kind == "instance"
        assert cats == ["fridge"]

    def test_floor_near_offset_is_region_despite_having_cats(self):
        kind, cats = classify_anchor("living_room.open_floor")
        assert kind == "region"

    def test_current_offset_is_region(self):
        kind, cats = classify_anchor("living_room.corner")
        assert kind == "region"

    def test_room_qualified_tier1_furniture_not_in_slot_anchors_is_instance(self):
        # Pre-Pool-Build Remediation follow-up: "kitchen.range_hood" used to
        # be this test's own "should be unbacked" example — a real,
        # confirmed bug (28/68 anchor_unbacked events in a real rebuild
        # traced to exactly this: a TIER1_FURNITURE category not among the
        # 16 hand-authored SLOT_ANCHORS entries, even though
        # rooms.resolve_slot() already verifies it against the real
        # per-room census at generation time and a real position exists
        # for it in topdown_map.anchor_world_positions). Now correctly
        # "instance", not "unbacked" — see classify_anchor's own docstring.
        kind, cats = classify_anchor("kitchen.range_hood")
        assert kind == "instance"
        assert cats == ["range_hood"]

    def test_room_qualified_non_tier1_category_is_still_unbacked(self):
        # "stool" is TIER2_HSSD_NATIVE (movable clutter), not TIER1_FURNITURE
        # (anchor-capable furniture) — the room-qualified TIER1_FURNITURE
        # fallback above must not over-accept a category that was never
        # meant to serve as a placement anchor.
        kind, cats = classify_anchor("kitchen.stool")
        assert kind == "unbacked"
        assert cats is None

    def test_garbage_anchor_is_unbacked(self):
        kind, cats = classify_anchor("nonexistent_anchor_xyz")
        assert kind == "unbacked"

    def test_dotted_anchor_with_unresolvable_room_is_unbacked(self):
        # category IS a real TIER1_FURNITURE member, but the room prefix
        # doesn't resolve via slot_room() -- the fallback is gated on both,
        # not just category membership.
        kind, cats = classify_anchor("not_a_real_room.table")
        assert kind == "unbacked"
        assert cats is None


class TestPackingCandidates:
    def test_first_candidate_is_always_the_anchor_itself(self):
        candidates = list(_packing_candidates("label_1", max_offset_m=0.5))
        assert candidates[0] == (0.0, 0.0)

    def test_deterministic_across_calls(self):
        a = list(_packing_candidates("stool_1", max_offset_m=0.4))
        b = list(_packing_candidates("stool_1", max_offset_m=0.4))
        assert a == b

    def test_different_labels_give_different_rings(self):
        a = list(_packing_candidates("stool_1", max_offset_m=0.4))
        b = list(_packing_candidates("chair_1", max_offset_m=0.4))
        assert a != b

    def test_radius_grows_monotonically_by_tier_and_stays_within_max(self):
        candidates = list(_packing_candidates("label_1", max_offset_m=0.6))
        radii = [math.hypot(dx, dz) for dx, dz in candidates]
        # first _N_ANGLES_PER_TIER+1 entries: center then tier-1 ring (radius ~0.1)
        assert radii[0] == 0.0
        assert all(r <= 0.6 + 1e-9 for r in radii)
        # last tier's radius should be close to max_offset_m
        assert max(radii) > 0.5

    def test_covers_multiple_angles_at_the_same_tier(self):
        candidates = list(_packing_candidates("label_1", max_offset_m=0.6))
        radii = [round(math.hypot(dx, dz), 6) for dx, dz in candidates]
        # the outermost tier's radius should appear _N_ANGLES_PER_TIER times
        outer_radius = max(radii)
        assert radii.count(outer_radius) >= 5


class TestSpawnableAssetMapping:
    """Moved here from tests/test_realism_render_job.py at the render-job
    cutover — this data is build-time-only now (scripts/build_realized_day.py
    owns it; the render job no longer spawns anything)."""

    def test_no_category_appears_in_more_than_one_bucket(self):
        spawnable = set(SPAWNABLE_ASSET_BY_CATEGORY)
        bind = _bind_categories()
        assert spawnable.isdisjoint(NO_ASSET_CATEGORIES)
        assert spawnable.isdisjoint(bind)
        assert NO_ASSET_CATEGORIES.isdisjoint(bind)

    def test_substituted_categories_are_a_subset_of_spawnable(self):
        assert CATEGORY_SUBSTITUTED <= set(SPAWNABLE_ASSET_BY_CATEGORY)

    def test_wallet_and_keys_are_now_spawnable(self):
        # wallet/keys were PERCEPTUAL-TIER-EXCLUDED (NO_ASSET_CATEGORIES)
        # under the old ring-camera search; re-verified under the
        # Spectator Camera round's closer, unconstrained search and both
        # now have real, mechanically-accepted Objaverse assets — see
        # results/reports/asset_candidates_result.json.
        assert "wallet" in SPAWNABLE_ASSET_BY_CATEGORY
        assert "keys" in SPAWNABLE_ASSET_BY_CATEGORY
        assert not NO_ASSET_CATEGORIES

    def test_bind_categories_cover_tier1_and_tier2a(self):
        # Tier 2a (HSSD-native clutter) + Tier 1 stateful furniture — real
        # geometry HSSD itself places, confirmed against a real
        # scene_instance.json for the frozen scene.
        bind = _bind_categories()
        assert {"chair", "stool", "potted_plant", "cushion"} <= bind
        assert {"oven", "tv", "fridge", "wardrobe"} <= bind


class TestAssertCategoryHasAssetCoverage:
    def test_spawnable_category_passes(self):
        assert_category_has_asset_coverage("vase")  # does not raise

    def test_bind_eligible_category_passes(self):
        assert_category_has_asset_coverage("stool")  # does not raise

    def test_now_spawnable_category_passes(self):
        # wallet used to be a documented NO_ASSET_CATEGORIES exclusion;
        # now covered via SPAWNABLE_ASSET_BY_CATEGORY instead — see
        # TestSpawnableAssetMapping.test_wallet_and_keys_are_now_spawnable.
        assert_category_has_asset_coverage("wallet")  # does not raise

    def test_unknown_category_raises_loudly(self):
        with pytest.raises(UncoveredCategoryError):
            assert_category_has_asset_coverage("umbrella_stand_nobody_has_ever_seen")
