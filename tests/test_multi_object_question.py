"""
Tests for embodied/question.py's D2 multi-object question generator
(generate_multi_object_question, TargetSpec, MultiObjectQuestion) — stems
referencing 2-3 instances, each independently report-time resolvable, with
the same required blind-baseline chance guard extended from single-object
questions (test_question.py's own test_blind_uniform_guesser_scores_at_
chance_not_above).

Uses real fixture data but no habitat_sim — generate_multi_object_question
only needs (initial_state, changes), not a live EmbodiedWorld.
"""
from __future__ import annotations

import json
import pathlib
import random

import pytest

from dynamic_home_eqa.embodied.belief import fit_decay_models
from dynamic_home_eqa.embodied.question import (
    MultiObjectQuestion,
    TargetSpec,
    categories_ever_outdoor,
    category_anchor_history,
    generate_multi_object_question,
)
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
def categories(real_day):
    manifest, _, _ = real_day
    out: dict[str, str] = {}
    for c in manifest["changes"]:
        out.setdefault(c["label"], c["object_category"])
    return out


@pytest.fixture(scope="module")
def dynamic_labels(real_day):
    manifest, _, _ = real_day
    return sorted({c["label"] for c in manifest["changes"]})


def _generate(labels, real_day, decay_models, categories, asked_t=12.0, n_options=4):
    manifest, initial_state, changes = real_day
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    return generate_multi_object_question(
        labels=labels, categories=categories, asked_t=asked_t,
        initial_state=initial_state, changes=changes,
        anchor_history=anchor_history, outdoor_categories=outdoor_categories,
        decay_models=decay_models, n_options=n_options,
    )


# ---------------------------------------------------------------------------
# Construction and validation
# ---------------------------------------------------------------------------

def test_rejects_fewer_than_two_labels(real_day, decay_models, categories, dynamic_labels):
    with pytest.raises(ValueError, match="2-3 labels"):
        _generate((dynamic_labels[0],), real_day, decay_models, categories)


def test_rejects_more_than_three_labels(real_day, decay_models, categories, dynamic_labels):
    with pytest.raises(ValueError, match="2-3 labels"):
        _generate(tuple(dynamic_labels[:4]), real_day, decay_models, categories)


def test_rejects_duplicate_labels(real_day, decay_models, categories, dynamic_labels):
    label = dynamic_labels[0]
    with pytest.raises(ValueError, match="distinct labels"):
        _generate((label, label), real_day, decay_models, categories)


def test_accepts_two_labels(real_day, decay_models, categories, dynamic_labels):
    q = _generate(tuple(dynamic_labels[:2]), real_day, decay_models, categories)
    assert isinstance(q, MultiObjectQuestion)
    assert q.n_targets == 2
    assert len(q.targets) == 2


def test_accepts_three_labels(real_day, decay_models, categories, dynamic_labels):
    q = _generate(tuple(dynamic_labels[:3]), real_day, decay_models, categories)
    assert q.n_targets == 3
    assert len(q.targets) == 3


# ---------------------------------------------------------------------------
# Each target is independently report-time resolvable
# ---------------------------------------------------------------------------

def test_each_target_matches_what_a_single_object_question_would_produce(real_day, decay_models, categories, dynamic_labels):
    from dynamic_home_eqa.embodied.question import generate_mcq_question

    manifest, initial_state, changes = real_day
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    labels = tuple(dynamic_labels[:2])

    q = _generate(labels, real_day, decay_models, categories)
    for label, target in zip(labels, q.targets):
        solo = generate_mcq_question(
            label=label, category=categories[label], asked_t=12.0,
            initial_state=initial_state, changes=changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )
        assert target.options == solo.options
        assert target.correct_index == solo.correct_index
        assert target.distractor_provenance == solo.distractor_provenance
        assert target.hazard_class == solo.hazard_class


def test_targets_are_independently_scoreable_TargetSpec_instances(real_day, decay_models, categories, dynamic_labels):
    q = _generate(tuple(dynamic_labels[:2]), real_day, decay_models, categories)
    for target in q.targets:
        assert isinstance(target, TargetSpec)
        assert target.label
        assert target.category


# ---------------------------------------------------------------------------
# hazard_class = max over targets
# ---------------------------------------------------------------------------

def test_hazard_class_is_volatile_if_any_target_is_volatile(real_day, decay_models, categories, dynamic_labels):
    q = _generate(tuple(dynamic_labels[:3]), real_day, decay_models, categories)
    any_volatile = any(t.hazard_class == "volatile" for t in q.targets)
    if any_volatile:
        assert q.hazard_class == "volatile"
    else:
        assert q.hazard_class == "stable"


def test_hazard_class_is_stable_only_if_every_target_is_stable(real_day, decay_models, categories, dynamic_labels):
    q = _generate(tuple(dynamic_labels[:2]), real_day, decay_models, categories)
    if q.hazard_class == "stable":
        assert all(t.hazard_class == "stable" for t in q.targets)


# ---------------------------------------------------------------------------
# Blind-baseline chance guard, extended to multi-object questions
# ---------------------------------------------------------------------------

def test_blind_uniform_guesser_scores_at_chance_per_target():
    """Same guard as test_question.py's single-object version, extended:
    a blind guesser answering each TARGET within a multi-object question
    independently (uniformly random per target) must score within noise
    of chance — multi-object bundling must not itself leak which index is
    correct for any referenced instance."""
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    initial_state, changes = initial_state_and_changes_from_manifest(manifest)
    stats = category_location_change_stats(manifest["changes"])
    decay_models = fit_decay_models(stats)
    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    labels = sorted({c["label"] for c in manifest["changes"]})
    cats = {}
    for c in manifest["changes"]:
        cats.setdefault(c["label"], c["object_category"])

    rng = random.Random(5678)
    correct_count = 0
    chance_count = 0.0
    n_targets_scored = 0

    for i in range(len(labels) - 1):
        pair = (labels[i], labels[i + 1])
        for asked_t in (6.0, 9.0, 12.0, 15.0, 18.0, 21.0):
            q = generate_multi_object_question(
                labels=pair, categories=cats, asked_t=asked_t,
                initial_state=initial_state, changes=changes,
                anchor_history=anchor_history, outdoor_categories=outdoor_categories,
                decay_models=decay_models,
            )
            for target in q.targets:
                if target.correct_index is None or len(target.options) < 2:
                    continue
                n_targets_scored += 1
                chance_count += 1.0 / len(target.options)
                guess = rng.randrange(len(target.options))
                if guess == target.correct_index:
                    correct_count += 1

    assert n_targets_scored >= 30, "need enough answerable targets for the chance-rate check to be meaningful"
    observed_rate = correct_count / n_targets_scored
    expected_chance_rate = chance_count / n_targets_scored
    assert abs(observed_rate - expected_chance_rate) < 0.15, (
        f"blind guesser scored {observed_rate:.3f} vs chance {expected_chance_rate:.3f} on multi-object "
        f"targets — bundling may be leaking which index is correct"
    )
