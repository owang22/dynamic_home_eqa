"""
Tests for embodied/question.py's generate_state_question (M3: state-change
dynamics) — synthetic SceneState/Change data, no habitat_sim needed (mirrors
test_ground_truth.py's approach).
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.question import MCQQuestion, generate_state_question
from dynamic_home_eqa.env.deltas import Change
from dynamic_home_eqa.env.state import ObjectInstance, SceneState

_DECAY_MODELS: dict = {}


def _initial_state():
    return SceneState(instances={
        "tv_1": ObjectInstance(instance_id="tv_1", category="tv", current_semantic="tv",
                                states={"power": "unpowered"}),
    })


def _state_change(t, from_state, to_state):
    return Change(
        activity="test", phase="enter", instance_id="tv_1", change_type="state_change",
        object_category="tv", from_semantic="tv", to_semantic="tv",
        reason="", t=t, state_variable="power", from_state=from_state, to_state=to_state,
    )


def test_options_are_the_full_state_domain():
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert set(q.options) == {"unpowered", "powered"}
    assert len(q.options) == 2


def test_label_and_category_are_synthetic_belief_keys():
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert q.label == "tv_1::power"
    assert q.category == "tv::power"


def test_underlying_identity_preserved_for_scoring():
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert q.underlying_label == "tv_1"
    assert q.state_variable == "power"
    assert q.question_type == "state"


def test_correct_index_matches_current_truth():
    changes = [_state_change(0.5, "unpowered", "powered")]
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), changes, _DECAY_MODELS)
    assert q.options[q.correct_index] == "powered"


def test_correct_index_reflects_scene_init_when_no_changes_yet():
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert q.options[q.correct_index] == "unpowered"


def test_deterministic_for_same_label_and_time():
    q1 = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    q2 = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert q1.options == q2.options
    assert q1.correct_index == q2.correct_index


def test_returns_an_mcqquestion():
    q = generate_state_question("tv_1", "tv", "power", 1.0, _initial_state(), [], _DECAY_MODELS)
    assert isinstance(q, MCQQuestion)


def test_location_question_defaults_are_unaffected():
    # Sanity: MCQQuestion's new M3 fields default to today's location-question
    # behavior for any question NOT built via generate_state_question.
    q = MCQQuestion(label="book_1", category="book", stem="", options=("a", "b"),
                     correct_index=0, asked_t=1.0, hazard_class="stable", distractor_provenance=("a", "b"))
    assert q.question_type == "location"
    assert q.underlying_label is None
    assert q.state_variable is None
