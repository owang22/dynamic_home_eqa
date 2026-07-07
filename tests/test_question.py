"""
Tests for embodied/question.py — MCQ generation, distractor construction,
and the required blind-baseline guard (an agent that never observes
anything, guessing only from the option set, must score at chance; if it
doesn't, option construction is leaking which index is correct).

Uses real fixture data but no habitat_sim — generate_mcq_question only
needs (initial_state, changes), not a live EmbodiedWorld.
"""
from __future__ import annotations

import json
import pathlib
import random

import pytest

from dynamic_home_eqa.embodied.belief import fit_decay_models
from dynamic_home_eqa.embodied.question import (
    MCQQuestion,
    categories_ever_outdoor,
    category_anchor_history,
    generate_mcq_question,
)
from dynamic_home_eqa.embodied.scoring import Choice, ScoringConfig, brier_score
from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest
from dynamic_home_eqa.generation.exports import category_location_change_stats

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def real_day():
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    initial_state, changes = initial_state_and_changes_from_manifest(manifest)
    return manifest, initial_state, changes


@pytest.fixture(scope="module")
def decay_models(real_day):
    manifest, _, _ = real_day
    stats = category_location_change_stats(manifest["changes"])
    return fit_decay_models(stats)


@pytest.fixture(scope="module")
def dynamic_labels(real_day):
    manifest, _, _ = real_day
    return sorted({c["label"] for c in manifest["changes"]})


def _category_of(manifest: dict, label: str) -> str:
    for c in manifest["changes"]:
        if c["label"] == label:
            return c["object_category"]
    raise KeyError(label)


# ---------------------------------------------------------------------------
# category_anchor_history / categories_ever_outdoor
# ---------------------------------------------------------------------------

def test_category_anchor_history_collects_real_anchors(real_day):
    manifest, _, _ = real_day
    history = category_anchor_history([manifest])
    assert history  # scene has real changes
    for cat, anchors in history.items():
        assert anchors
        for anchor in anchors:
            assert isinstance(anchor, str) and anchor


def test_category_anchor_history_merges_across_multiple_manifests():
    m1 = {"changes": [{"object_category": "book", "to_semantic": "shelf"}]}
    m2 = {"changes": [{"object_category": "book", "to_semantic": "table"}]}
    history = category_anchor_history([m1, m2])
    assert history["book"] == {"shelf", "table"}


def test_categories_ever_outdoor_detects_outdoor_slot():
    m = {"changes": [{"object_category": "phone", "to_semantic": "outdoor"}]}
    assert "phone" in categories_ever_outdoor([m])


def test_categories_ever_outdoor_excludes_indoor_only_category():
    m = {"changes": [{"object_category": "book", "to_semantic": "living_room.shelf"}]}
    assert "book" not in categories_ever_outdoor([m])


# ---------------------------------------------------------------------------
# generate_mcq_question
# ---------------------------------------------------------------------------

def test_generated_question_has_target_among_options_when_truth_exists(real_day, decay_models, dynamic_labels):
    manifest, initial_state, changes = real_day
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])

    label = dynamic_labels[0]
    category = _category_of(manifest, label)
    q = generate_mcq_question(
        label=label, category=category, asked_t=12.0,
        initial_state=initial_state, changes=changes,
        anchor_history=anchor_history, outdoor_categories=outdoor_categories,
        decay_models=decay_models,
    )
    assert isinstance(q, MCQQuestion)
    assert len(q.options) == len(set(q.options))  # no duplicate options
    if q.correct_index is not None:
        assert 0 <= q.correct_index < len(q.options)


def test_generated_question_is_deterministic_for_same_label_and_time(real_day, decay_models):
    manifest, initial_state, changes = real_day
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])

    kwargs = dict(
        label="chair_1", category="chair", asked_t=10.0,
        initial_state=initial_state, changes=changes,
        anchor_history=anchor_history, outdoor_categories=outdoor_categories,
        decay_models=decay_models,
    )
    q1 = generate_mcq_question(**kwargs)
    q2 = generate_mcq_question(**kwargs)
    assert q1.options == q2.options
    assert q1.correct_index == q2.correct_index


def test_distractor_provenance_parallels_options(real_day, decay_models, dynamic_labels):
    manifest, initial_state, changes = real_day
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])

    for label in dynamic_labels[:5]:
        category = _category_of(manifest, label)
        q = generate_mcq_question(
            label=label, category=category, asked_t=14.0,
            initial_state=initial_state, changes=changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )
        assert len(q.distractor_provenance) == len(q.options)
        assert set(q.distractor_provenance) <= {"target", "prior_history", "category_plausible", "not_in_house"}


# ---------------------------------------------------------------------------
# Blind-baseline guard (required by the phase spec)
# ---------------------------------------------------------------------------

def test_blind_uniform_guesser_scores_at_chance_not_above():
    """An agent that never observes anything — just picks a uniformly
    random option index per question — must score within noise of chance
    (1/n_options accuracy on average). If it scores meaningfully above
    chance, the option set's construction (e.g. always placing the correct
    answer first) is leaking which index is correct, and this test must
    fail loudly rather than let that ship."""
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    initial_state, changes = initial_state_and_changes_from_manifest(manifest)
    stats = category_location_change_stats(manifest["changes"])
    decay_models = fit_decay_models(stats)
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    labels = sorted({c["label"] for c in manifest["changes"]})

    rng = random.Random(1234)
    correct_count = 0
    chance_count = 0.0
    n_questions = 0

    for label in labels:
        category = _category_of(manifest, label)
        for asked_t in (6.0, 9.0, 12.0, 15.0, 18.0, 21.0):
            q = generate_mcq_question(
                label=label, category=category, asked_t=asked_t,
                initial_state=initial_state, changes=changes,
                anchor_history=anchor_history, outdoor_categories=outdoor_categories,
                decay_models=decay_models,
            )
            if q.correct_index is None or len(q.options) < 2:
                continue
            n_questions += 1
            chance_count += 1.0 / len(q.options)
            guess = rng.randrange(len(q.options))
            if guess == q.correct_index:
                correct_count += 1

    assert n_questions >= 30, "need enough answerable questions for the chance-rate check to be meaningful"
    observed_rate = correct_count / n_questions
    expected_chance_rate = chance_count / n_questions
    # Generous tolerance (binomial noise over a few hundred trials at ~25%
    # chance rate has a standard deviation of several percentage points);
    # the point is catching a gross leak (e.g. always index 0), not
    # asserting exact statistical equivalence.
    assert abs(observed_rate - expected_chance_rate) < 0.15, (
        f"blind guesser scored {observed_rate:.3f} vs chance {expected_chance_rate:.3f} "
        f"— option construction may be leaking which index is correct"
    )


def test_correct_index_position_is_not_always_the_same_slot():
    """A cheaper, more direct check than the statistical guess test above:
    across many generated questions, the correct option's position in the
    list must vary — if it were always index 0 (e.g. because "target" is
    appended first and never shuffled), that alone is the leak."""
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    initial_state, changes = initial_state_and_changes_from_manifest(manifest)
    stats = category_location_change_stats(manifest["changes"])
    decay_models = fit_decay_models(stats)
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    labels = sorted({c["label"] for c in manifest["changes"]})

    positions = []
    for label in labels:
        category = _category_of(manifest, label)
        for asked_t in (6.0, 9.0, 12.0, 15.0, 18.0, 21.0):
            q = generate_mcq_question(
                label=label, category=category, asked_t=asked_t,
                initial_state=initial_state, changes=changes,
                anchor_history=anchor_history, outdoor_categories=outdoor_categories,
                decay_models=decay_models,
            )
            if q.correct_index is not None:
                positions.append(q.correct_index)

    assert len(set(positions)) > 1, "correct_index never varies across questions — likely a shuffle/order bug"
