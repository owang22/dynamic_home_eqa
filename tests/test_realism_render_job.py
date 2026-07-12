"""
Tests for the pure-logic pieces of scripts/realism_render_job.py — no
habitat_sim needed. The actual rendering (habitat_sim + GPU) is exercised
by the one live integration test in tests/test_realism_render_job_live.py.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from dynamic_home_eqa.scripts.realism_render_job import (
    MASK_FAIL_ANCHOR_OUT_OF_FRAME,
    MASK_FAIL_EMPTY,
    MASK_FAIL_OFF_CENTER,
    MASK_FAIL_TOO_LARGE,
    MASK_FAIL_TOO_SMALL,
    PoolItem,
    camera_basis,
    evaluate_object_mask,
    format_caption,
    hour_to_clock,
    project_point,
    select_random_sample_per_type,
)


class TestHourToClock:
    def test_basic_conversion(self):
        assert hour_to_clock(6.057) == "06:03"

    def test_exact_hour(self):
        assert hour_to_clock(14.0) == "14:00"

    def test_rounds_minutes_up_to_next_hour(self):
        assert hour_to_clock(6.999) == "07:00"

    def test_wraps_past_24h(self):
        assert hour_to_clock(25.5) == "01:30"

    def test_zero(self):
        assert hour_to_clock(0.0) == "00:00"


class TestSelectRandomSamplePerType:
    def _pool(self, n, change_type):
        return [
            PoolItem(folder="f", change_type=change_type, event={"label": f"{change_type}_{i}"})
            for i in range(n)
        ]

    def test_respects_per_type_counts(self):
        pool = self._pool(20, "location") + self._pool(20, "state")
        sample = select_random_sample_per_type(pool, n_location=5, n_state=3, seed=0)
        assert sum(1 for p in sample if p.change_type == "location") == 5
        assert sum(1 for p in sample if p.change_type == "state") == 3

    def test_capped_at_available_pool_not_an_error(self):
        pool = self._pool(2, "location") + self._pool(1, "state")
        sample = select_random_sample_per_type(pool, n_location=5, n_state=5, seed=0)
        assert sum(1 for p in sample if p.change_type == "location") == 2
        assert sum(1 for p in sample if p.change_type == "state") == 1

    def test_deterministic_given_seed(self):
        pool = self._pool(20, "location") + self._pool(20, "state")
        sample_a = select_random_sample_per_type(pool, n_location=5, n_state=5, seed=42)
        sample_b = select_random_sample_per_type(pool, n_location=5, n_state=5, seed=42)
        assert [p.event["label"] for p in sample_a] == [p.event["label"] for p in sample_b]

    def test_location_and_state_do_not_cross_contaminate(self):
        pool = self._pool(10, "location") + self._pool(10, "state")
        sample = select_random_sample_per_type(pool, n_location=3, n_state=3, seed=0)
        for p in sample:
            assert p.event["label"].startswith(p.change_type)


class TestCameraBasisAndProjection:
    def test_forward_points_at_target(self):
        eye_pos = (0.0, 0.0, 0.0)
        target = (2.0, 0.3, -3.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        assert eye == (0.0, 1.5, 0.0)
        # full 3D look-at: target should project to BOTH horizontal AND
        # vertical image center now (yaw and pitch), not horizontal only.
        px, py = project_point(eye, forward, right, up, target)
        assert math.isclose(px, 480 / 2.0, abs_tol=0.5)
        assert math.isclose(py, 360 / 2.0, abs_tol=0.5)

    def test_forward_points_at_a_steep_downward_target(self):
        # the exact failure mode this fix targets: a close, low anchor
        # (e.g. floor-level furniture) seen from eye height.
        eye_pos = (0.0, 0.0, 0.0)
        target = (1.2, -1.5, -1.2)
        eye, forward, right, up = camera_basis(eye_pos, target)
        px, py = project_point(eye, forward, right, up, target)
        assert math.isclose(px, 240.0, abs_tol=0.5)
        assert math.isclose(py, 180.0, abs_tol=0.5)

    def test_point_offset_along_right_lands_right_of_center(self):
        eye_pos = (0.0, 0.0, 0.0)
        target = (2.0, 0.3, -3.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        side_point = tuple(target[i] + right[i] * 1.0 for i in range(3))
        px_center, _ = project_point(eye, forward, right, up, target)
        px_side, _ = project_point(eye, forward, right, up, side_point)
        assert px_side > px_center

    def test_point_offset_up_lands_above_center(self):
        eye_pos = (0.0, 0.0, 0.0)
        target = (2.0, 0.3, -3.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        above_point = tuple(target[i] + up[i] * 1.0 for i in range(3))
        _px_center, py_center = project_point(eye, forward, right, up, target)
        _px_above, py_above = project_point(eye, forward, right, up, above_point)
        assert py_above < py_center  # smaller row index = higher on screen

    def test_point_behind_camera_returns_none(self):
        eye_pos = (0.0, 0.0, 0.0)
        target = (2.0, 0.3, -3.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        behind = tuple(eye[i] - forward[i] * 2.0 for i in range(3))
        assert project_point(eye, forward, right, up, behind) is None

    def test_degenerate_zero_distance_falls_back(self):
        # only a genuinely zero-length target-eye vector is degenerate now
        # (previously, "zero HORIZONTAL distance" alone triggered the
        # fallback even for a real, well-defined straight-up/down target —
        # that was exactly the yaw-only limitation this fix removes).
        eye_pos = (0.0, -1.5, 0.0)  # eye ends up at (0,0,0) after the +1.5 offset
        target = (0.0, 0.0, 0.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        assert forward == (0.0, 0.0, -1.0)

    def test_straight_up_target_is_not_degenerate(self):
        # previously misclassified as degenerate (zero HORIZONTAL offset);
        # a real, well-defined pitch-up direction now.
        eye_pos = (0.0, 0.0, 0.0)
        target = (0.0, 5.0, 0.0)
        eye, forward, right, up = camera_basis(eye_pos, target)
        assert forward != (0.0, 0.0, -1.0)
        px, py = project_point(eye, forward, right, up, target)
        assert math.isclose(px, 240.0, abs_tol=0.5)
        assert math.isclose(py, 180.0, abs_tol=0.5)

    def test_right_and_up_are_orthonormal_to_forward(self):
        eye_pos = (0.0, 0.0, 0.0)
        target = (1.2, -1.5, -1.2)
        _eye, forward, right, up = camera_basis(eye_pos, target)
        dot = lambda a, b: sum(a[i] * b[i] for i in range(3))  # noqa: E731
        assert math.isclose(dot(forward, right), 0.0, abs_tol=1e-9)
        assert math.isclose(dot(forward, up), 0.0, abs_tol=1e-9)
        assert math.isclose(dot(right, up), 0.0, abs_tol=1e-9)
        for v in (forward, right, up):
            assert math.isclose(math.sqrt(dot(v, v)), 1.0, abs_tol=1e-9)


class TestFormatCaption:
    _gen_result = {
        "scene_id": "102343992", "profile": "family_with_kids", "day": 0,
        "household_id": "102343992_family_with_kids",
    }

    def test_location_event_caption(self):
        event = {
            "label": "book_1", "object_category": "book", "t": 6.057,
            "from_semantic": "bedroom", "to_semantic": "kitchen",
            "reason": "moved for reading", "mover": "Emily",
        }
        item = PoolItem(folder="f1", change_type="location", event=event)
        cap = format_caption(item, self._gen_result)
        assert cap["t_clock"] == "06:03"
        assert cap["from"] == "bedroom" and cap["to"] == "kitchen"
        assert cap["change_type"] == "location"
        assert cap["scene_id"] == "102343992"

    def test_state_event_caption(self):
        event = {
            "label": "fridge_1", "object_category": "fridge", "t": 6.02,
            "to_semantic": "fridge", "state_variable": "door",
            "from_state": "closed", "to_state": "open",
            "reason": "wake_up started", "mover": "Emily",
        }
        item = PoolItem(folder="f1", change_type="state", event=event)
        cap = format_caption(item, self._gen_result)
        assert cap["from"] == "closed" and cap["to"] == "open"
        assert cap["state_variable"] == "door"
        assert cap["anchor"] == "fridge"
        assert cap["change_type"] == "state"


class TestEvaluateObjectMask:
    """Direct tests for the 4-clause output-truth predicate that replaced
    the whole-frame pixel-diff check and the anchor-projection AIM_FAILED
    gate — see evaluate_object_mask's docstring."""

    W, H = 480, 360

    def _central_mask(self, w=40, h=40, cx=None, cy=None):
        mask = np.zeros((self.H, self.W), dtype=bool)
        cx = self.W // 2 if cx is None else cx
        cy = self.H // 2 if cy is None else cy
        mask[cy - h // 2:cy + h // 2, cx - w // 2:cx + w // 2] = True
        return mask

    def test_empty_mask_fails(self):
        mask = np.zeros((self.H, self.W), dtype=bool)
        passed, reason, info = evaluate_object_mask(mask, (240.0, 180.0))
        assert not passed
        assert reason == MASK_FAIL_EMPTY
        assert info["centroid_px"] is None

    def test_centered_plausible_mask_passes(self):
        mask = self._central_mask()
        passed, reason, info = evaluate_object_mask(mask, (240.0, 180.0))
        assert passed
        assert reason == "ok"
        assert info["centroid_px"] == pytest.approx((240.0, 180.0), abs=1.0)

    def test_tiny_mask_below_area_floor_fails(self):
        mask = self._central_mask(w=2, h=2)  # 4px / 172800px, well under 0.5%
        passed, reason, _info = evaluate_object_mask(mask, (240.0, 180.0))
        assert not passed
        assert reason == MASK_FAIL_TOO_SMALL

    def test_huge_mask_above_area_ceiling_fails(self):
        mask = np.ones((self.H, self.W), dtype=bool)  # 100% of frame
        passed, reason, _info = evaluate_object_mask(mask, (240.0, 180.0))
        assert not passed
        assert reason == MASK_FAIL_TOO_LARGE

    def test_off_center_mask_fails_even_though_visible(self):
        # a plausible-size mask jammed into the corner, outside the
        # central 60% band on both axes
        mask = self._central_mask(w=30, h=30, cx=20, cy=20)
        passed, reason, info = evaluate_object_mask(mask, (240.0, 180.0))
        assert not passed
        assert reason == MASK_FAIL_OFF_CENTER
        assert info["centroid_px"] is not None  # still reported, not hidden

    def test_object_visible_but_anchor_off_frame_fails(self):
        mask = self._central_mask()
        passed, reason, _info = evaluate_object_mask(mask, None)  # anchor behind camera
        assert not passed
        assert reason == MASK_FAIL_ANCHOR_OUT_OF_FRAME

    def test_anchor_outside_pixel_bounds_fails(self):
        mask = self._central_mask()
        passed, reason, _info = evaluate_object_mask(mask, (-5.0, 180.0))
        assert not passed
        assert reason == MASK_FAIL_ANCHOR_OUT_OF_FRAME


