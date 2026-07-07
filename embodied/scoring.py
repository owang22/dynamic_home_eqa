"""
scoring.py — MCQ scoring: Brier score over the option simplex, calibration
(ECE), and abstention.

E0 found that exact-match scoring can't distinguish "confidently wrong"
from "correctly unsure": a resense trip that refutes a stale belief
(agent now honestly doesn't know) scored identically to never resensing at
all (agent confidently repeats the same now-wrong guess), because both
verdicts are simply "not equal to ground truth". Brier scoring over a full
probability simplex, plus a genuine Abstain response scored strictly
between wrong and correct, is the fix — refuting a belief and abstaining
must beat confidently repeating a wrong guess, or the whole resense-vs-
answer decision this phase studies stays structurally undecidable whenever
an object has moved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class Choice:
    option_index: int
    confidence:   float   # in [0, 1]; remainder spread uniformly over the other options


@dataclass(frozen=True)
class Abstain:
    """Insufficient belief to answer. Distinct from choosing the "not in
    the house" option, which is a contentful, scoreable claim about where
    the object is (namely: outside) — never conflate the two."""
    pass


Answer = Union[Choice, Abstain]


@dataclass(frozen=True)
class ScoringConfig:
    r_abstain: float = 0.5

    def __post_init__(self) -> None:
        if not (0.0 < self.r_abstain < 1.0):
            raise ValueError(
                f"r_abstain must sit strictly between the wrong (0.0) and "
                f"correct (1.0) payoffs — a value outside (0, 1) makes a "
                f"degenerate always-abstain or never-abstain policy win by "
                f"construction regardless of actual belief quality. Got "
                f"{self.r_abstain!r}."
            )


def option_probabilities(answer: Choice, n_options: int) -> list[float]:
    """Choice(option_index, confidence) -> a full probability simplex over
    n_options: `confidence` on the chosen option, the remainder spread
    uniformly over the rest."""
    if n_options <= 0:
        raise ValueError("n_options must be positive")
    remainder = (1.0 - answer.confidence) / (n_options - 1) if n_options > 1 else 0.0
    probs = [remainder] * n_options
    probs[answer.option_index] = answer.confidence
    return probs


def brier_score(
    answer: Answer,
    correct_index: Optional[int],
    n_options: int,
    config: ScoringConfig,
) -> float:
    """Utility in [0, 1]: 1.0 = confident and correct, 0.0 = confident and
    wrong, config.r_abstain for Abstain.

    correct_index=None means the report-time true anchor isn't among this
    question's fixed options at all (the object moved somewhere the
    distractor construction didn't anticipate) — a question-generation
    shortfall, not something to attribute to the policy's answer, so every
    answer (Choice or Abstain) scores the same neutral r_abstain rather
    than rewarding or punishing whatever confidence distribution happened
    to be chosen against an unanswerable question.
    """
    if correct_index is None:
        return config.r_abstain
    if isinstance(answer, Abstain):
        return config.r_abstain
    probs = option_probabilities(answer, n_options)
    target = [0.0] * n_options
    target[correct_index] = 1.0
    squared_error = sum((p - t) ** 2 for p, t in zip(probs, target))
    # Multi-class Brier squared-error against a one-hot target ranges
    # [0, 2] (0 = perfect, 2 = all mass on one wrong class) — rescaled to
    # this module's [0, 1] utility convention.
    return max(0.0, 1.0 - squared_error / 2.0)


def compute_ece(confidences: list[float], corrects: list[bool], n_bins: int = 10) -> float:
    """Expected Calibration Error over (confidence-in-chosen-option,
    was-it-correct) pairs — the standard equal-width-bin ECE. Abstained
    questions carry no "confidence in a specific prediction" and must be
    excluded by the caller before this is called (mirrors how accuracy is
    reported "of non-abstained answers" elsewhere in this module's
    consumers)."""
    if len(confidences) != len(corrects):
        raise ValueError("confidences and corrects must be the same length")
    if not confidences:
        return 0.0
    bins: list[list[tuple[float, bool]]] = [[] for _ in range(n_bins)]
    for conf, correct in zip(confidences, corrects):
        idx = min(int(conf * n_bins), n_bins - 1)
        bins[idx].append((conf, correct))
    total = len(confidences)
    ece = 0.0
    for bucket in bins:
        if not bucket:
            continue
        bucket_conf = sum(c for c, _ in bucket) / len(bucket)
        bucket_acc = sum(1 for _, correct in bucket if correct) / len(bucket)
        ece += (len(bucket) / total) * abs(bucket_conf - bucket_acc)
    return ece
