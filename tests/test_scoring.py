"""Unit tests for embodied/scoring.py."""
from __future__ import annotations

import pytest

from dynamic_home_eqa.embodied.scoring import (
    Abstain,
    Choice,
    ScoringConfig,
    brier_score,
    compute_ece,
    option_probabilities,
)


def test_scoring_config_accepts_valid_r_abstain():
    ScoringConfig(r_abstain=0.5)  # must not raise


@pytest.mark.parametrize("bad", [0.0, 1.0, -0.1, 1.1])
def test_scoring_config_rejects_r_abstain_outside_open_interval(bad):
    with pytest.raises(ValueError):
        ScoringConfig(r_abstain=bad)


def test_option_probabilities_confident_choice():
    probs = option_probabilities(Choice(option_index=1, confidence=1.0), n_options=3)
    assert probs == pytest.approx([0.0, 1.0, 0.0])


def test_option_probabilities_spreads_remainder_uniformly():
    probs = option_probabilities(Choice(option_index=0, confidence=0.7), n_options=4)
    assert probs[0] == pytest.approx(0.7)
    assert probs[1] == probs[2] == probs[3] == pytest.approx(0.1)
    assert sum(probs) == pytest.approx(1.0)


def test_brier_score_confident_correct_is_one():
    config = ScoringConfig()
    answer = Choice(option_index=0, confidence=1.0)
    assert brier_score(answer, correct_index=0, n_options=3, config=config) == pytest.approx(1.0)


def test_brier_score_confident_wrong_is_zero():
    config = ScoringConfig()
    answer = Choice(option_index=1, confidence=1.0)
    assert brier_score(answer, correct_index=0, n_options=3, config=config) == pytest.approx(0.0)


def test_brier_score_abstain_is_r_abstain():
    config = ScoringConfig(r_abstain=0.42)
    assert brier_score(Abstain(), correct_index=0, n_options=3, config=config) == pytest.approx(0.42)


def test_brier_score_unanswerable_question_is_neutral_regardless_of_answer():
    config = ScoringConfig(r_abstain=0.5)
    confident_choice = Choice(option_index=0, confidence=1.0)
    assert brier_score(confident_choice, correct_index=None, n_options=3, config=config) == pytest.approx(0.5)
    assert brier_score(Abstain(), correct_index=None, n_options=3, config=config) == pytest.approx(0.5)


def test_brier_score_refute_then_abstain_beats_confidently_wrong():
    """The exact degeneracy E0 found: a refuted belief (Abstain) must score
    strictly better than a confidently-repeated stale (wrong) guess."""
    config = ScoringConfig(r_abstain=0.5)
    confidently_wrong = Choice(option_index=1, confidence=1.0)
    refuted = Abstain()
    assert (
        brier_score(refuted, correct_index=0, n_options=3, config=config)
        > brier_score(confidently_wrong, correct_index=0, n_options=3, config=config)
    )


def test_brier_score_uncertain_correct_beats_confident_wrong_but_loses_to_confident_correct():
    config = ScoringConfig()
    uncertain_correct = Choice(option_index=0, confidence=0.4)
    confident_wrong = Choice(option_index=1, confidence=1.0)
    confident_correct = Choice(option_index=0, confidence=1.0)
    s_uncertain = brier_score(uncertain_correct, 0, 3, config)
    s_wrong = brier_score(confident_wrong, 0, 3, config)
    s_confident = brier_score(confident_correct, 0, 3, config)
    assert s_wrong < s_uncertain < s_confident


def test_compute_ece_zero_for_perfectly_calibrated():
    # confidence == empirical accuracy in every bin
    confidences = [0.9] * 10
    corrects = [True] * 9 + [False]  # 90% accuracy at 0.9 confidence
    assert compute_ece(confidences, corrects) == pytest.approx(0.0, abs=1e-9)


def test_compute_ece_positive_for_miscalibrated():
    confidences = [1.0] * 10
    corrects = [True] * 5 + [False] * 5  # confident but only 50% accurate
    assert compute_ece(confidences, corrects) == pytest.approx(0.5, abs=1e-9)


def test_compute_ece_empty_input_is_zero():
    assert compute_ece([], []) == 0.0


def test_compute_ece_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        compute_ece([0.5], [True, False])
