"""
Tests for llm_prior/targets.py against the frozen scene's real, committed
generation_out/ data — pure Python, no habitat_sim, no model calls.
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.posterior import OUTSIDE
from dynamic_home_eqa.llm_prior.targets import (
    N_TIME_BUCKETS,
    enumerate_location_targets,
    enumerate_state_targets,
    enumerate_targets,
    render_persona,
    render_room_inventory,
)

_OUT_DIR = pathlib.Path(__file__).parent.parent / "generation_out"


class TestEnumerateTargets:
    def test_every_target_time_bin_is_in_range(self):
        targets = enumerate_targets(_OUT_DIR, FROZEN)
        assert targets
        for t in targets:
            assert 0 <= t.time_bin < N_TIME_BUCKETS

    def test_location_support_matches_d1_kernel_states(self):
        from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train

        kernels = fit_location_kernels_from_train(_OUT_DIR, FROZEN)
        targets = enumerate_location_targets(_OUT_DIR, FROZEN)
        assert targets
        for t in targets:
            assert set(t.support) == set(kernels[t.key].states)

    def test_state_support_matches_d1_kernel_states(self):
        from dynamic_home_eqa.embodied.attribution import fit_state_kernels_from_train

        kernels = fit_state_kernels_from_train(_OUT_DIR, FROZEN)
        targets = enumerate_state_targets(_OUT_DIR, FROZEN)
        assert targets
        for t in targets:
            assert tuple(t.support) == tuple(kernels[t.key].states)

    def test_no_duplicate_targets(self):
        targets = enumerate_targets(_OUT_DIR, FROZEN)
        keys = [(t.axis, t.key, t.time_bin) for t in targets]
        assert len(keys) == len(set(keys))

    def test_location_support_includes_outside(self):
        targets = enumerate_location_targets(_OUT_DIR, FROZEN)
        for t in targets:
            assert OUTSIDE in t.support

    def test_only_occurring_time_bins_present(self):
        # Regression for the "present in the train split" filter: every
        # enumerated (key, time_bin) must have a real change event in that
        # bucket, not the full cross product.
        from dynamic_home_eqa.embodied.posterior import bucket_changes_by_time_of_day

        train_manifests = [json.loads((_OUT_DIR / f / "manifest.json").read_text()) for f in FROZEN.train_folders]
        per_bucket = bucket_changes_by_time_of_day(train_manifests, n_buckets=N_TIME_BUCKETS)
        occurring_categories_by_bucket = [
            {c.get("object_category") for c in bucket} for bucket in per_bucket
        ]
        for t in enumerate_location_targets(_OUT_DIR, FROZEN):
            assert t.key in occurring_categories_by_bucket[t.time_bin]


class TestRenderPersona:
    def test_renders_every_occupant_verbatim(self):
        result = json.loads((_OUT_DIR / FROZEN.train_folders[0] / "generation_result.json").read_text())
        persona = result["persona"]
        text = render_persona(persona)
        for occ in persona["occupants"]:
            assert occ["name"] in text
            assert occ["habits"] in text
        assert persona["household_type"] in text
        assert persona["schedule_notes"] in text

    def test_does_not_reference_train_day_events(self):
        result = json.loads((_OUT_DIR / FROZEN.train_folders[0] / "generation_result.json").read_text())
        manifest = json.loads((_OUT_DIR / FROZEN.train_folders[0] / "manifest.json").read_text())
        text = render_persona(result["persona"])
        # No change event's free-text "reason" field should leak into the
        # persona rendering (it's generated from a different, event-level
        # LLM stage, never persona output).
        for c in manifest["changes"][:20]:
            reason = c.get("reason")
            if reason:
                assert reason not in text


class TestRenderRoomInventory:
    def test_contains_known_categories(self):
        text = render_room_inventory(FROZEN.scene)
        assert "fridge" in text or "oven" in text or "tv" in text

    def test_does_not_reference_train_day_events(self):
        manifest = json.loads((_OUT_DIR / FROZEN.train_folders[0] / "manifest.json").read_text())
        text = render_room_inventory(FROZEN.scene)
        for c in manifest["changes"][:20]:
            reason = c.get("reason")
            if reason:
                assert reason not in text

    def test_known_categories_not_in_furniture_census_are_appended(self):
        # Uses a synthetic category name rather than a real Tier-2b one
        # (e.g. "book") — env.inventory.load_scene_state is lru_cache'd by
        # scene_id process-wide, and some other test in the full suite
        # observably populates it with clutter categories for this same
        # scene_id before this test runs, making a real category's
        # presence/absence in the census order-dependent. A name no real
        # census would ever contain sidesteps that entirely.
        text = render_room_inventory(FROZEN.scene, known_categories=("zzz_synthetic_test_category", "yyy_synthetic_test_category"))
        assert "zzz_synthetic_test_category" in text
        assert "yyy_synthetic_test_category" in text

    def test_known_category_already_in_furniture_census_is_not_duplicated(self):
        text = render_room_inventory(FROZEN.scene, known_categories=("fridge",))
        assert text.count("fridge") == 1

    def test_known_categories_get_no_room_or_location_attached(self):
        # The whole point of the fix: presence only, never a location —
        # that would reintroduce the same leak the fix exists to avoid.
        text = render_room_inventory(FROZEN.scene, known_categories=("zzz_synthetic_test_category",))
        also_present_line = next(line for line in text.splitlines() if "zzz_synthetic_test_category" in line)
        assert also_present_line.startswith("Also present")
