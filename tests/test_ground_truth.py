"""
Unit tests for embodied/ground_truth.py's true_state (M3: state-change
dynamics) — pure env.replay.state_at replay, no habitat_sim needed (unlike
test_embodied_world.py's true_anchor cross-check, which needs a real
EmbodiedWorld).
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.ground_truth import true_state
from dynamic_home_eqa.env.deltas import Change
from dynamic_home_eqa.env.state import ObjectInstance, SceneState


def _initial_state():
    return SceneState(instances={
        "tv_1": ObjectInstance(instance_id="tv_1", category="tv", current_semantic="tv",
                                states={"power": "unpowered"}),
    })


def _state_change(t, from_state, to_state, label="tv_1", variable="power"):
    return Change(
        activity="test", phase="enter", instance_id=label, change_type="state_change",
        object_category="tv", from_semantic="tv", to_semantic="tv",
        reason="", t=t, state_variable=variable, from_state=from_state, to_state=to_state,
    )


def test_true_state_before_any_change_is_scene_init_value():
    assert true_state("tv_1", "power", 0.0, _initial_state(), []) == "unpowered"


def test_true_state_reflects_most_recent_flip():
    changes = [_state_change(7.0, "unpowered", "powered")]
    assert true_state("tv_1", "power", 7.5, _initial_state(), changes) == "powered"
    assert true_state("tv_1", "power", 6.9, _initial_state(), changes) == "unpowered"


def test_true_state_tracks_multiple_flips_independently():
    changes = [
        _state_change(7.0, "unpowered", "powered"),
        _state_change(8.0, "powered", "unpowered"),
        _state_change(20.0, "unpowered", "powered"),
    ]
    assert true_state("tv_1", "power", 7.5, _initial_state(), changes) == "powered"
    assert true_state("tv_1", "power", 9.0, _initial_state(), changes) == "unpowered"
    assert true_state("tv_1", "power", 21.0, _initial_state(), changes) == "powered"


def test_true_state_returns_none_for_unknown_label():
    assert true_state("nonexistent_1", "power", 1.0, _initial_state(), []) is None


def test_true_state_returns_none_for_untracked_variable():
    assert true_state("tv_1", "brightness", 1.0, _initial_state(), []) is None
