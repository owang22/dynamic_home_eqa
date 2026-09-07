"""Split conformal calibration of a belief model's stated confidence.

The nonconformity score of one question is ``1 - p(truth)``: the
probability the belief did NOT put on the true receptacle. Split conformal
prediction takes the scores of a calibration set of n questions and
returns the quantile

    qhat = the ceil((n + 1)(1 - alpha))-th smallest score

so that, for a fresh question exchangeable with the calibration set, the
prediction set ``{r : 1 - p(r) <= qhat}`` contains the truth with
probability at least ``1 - alpha``. When n is too small for that rank to
exist (``ceil((n + 1)(1 - alpha)) > n``) the guarantee can only be met by
the vacuous set, so ``qhat = 1.0``.

Beliefs are far more reliable a minute after a sighting than three days
after one, and one global quantile averages the two: it over-covers young
questions and under-covers old ones. The age-binned fit computes one qhat
per bin of BELIEF AGE (hours since the newest positive sighting the
answer rests on; a never-sighted object counts as infinitely old and
lands in the last bin) and falls back to the global qhat in any bin
thinner than ``min_n`` questions.

The calibration/test split is at HOUSEHOLD level: every question of a
household lands on the same side, chosen by a salted hash of the
household id, so calibration and test never share a household (questions
of one household are not exchangeable with each other in the way the
guarantee assumes — they share objects, rooms and routines).

All times are seconds since episode start; ages are in hours.
"""

from __future__ import annotations

import hashlib
import math
from bisect import bisect_right
from dataclasses import dataclass
from typing import (Callable, Dict, Iterable, List, Mapping, Optional,
                    Sequence, Set, Tuple)

from baselines.agent import Agent
from baselines.harness import QuestionRecord, run_episode
from baselines.types import Episode

DEFAULT_AGE_EDGES_H: Tuple[float, ...] = (6.0, 24.0, 72.0)
"""Default belief-age bin edges in hours: [0, 6), [6, 24), [24, 72), 72+."""

DEFAULT_ALPHAS: Tuple[float, ...] = (0.02, 0.05, 0.1, 0.2)
"""Default miscoverage levels swept."""

MIN_BIN_N = 30
"""An age bin with fewer calibration questions than this uses the global
quantile instead of its own (the same per-cell floor the report figures
use)."""

AgeFn = Callable[[str, int], Optional[float]]
"""``(object_id, t) -> belief age in hours`` (None: never sighted)."""


@dataclass(frozen=True)
class CalibrationPair:
    """One passive question: what the belief said and how wrong it was.

    ``score`` is the nonconformity ``1 - p(truth)``; ``age_h`` the belief
    age at query time (None when the object had never been sighted);
    ``household_id`` is what the calibration/test split keys on, so the
    bank is walked once and split afterwards.
    """

    household_id: str
    episode_id: str
    question_id: str
    object_id: str
    t_query: int
    age_h: Optional[float]
    score: float
    top_prob: float
    correct: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0 + 1e-9:
            raise ValueError(
                f"CalibrationPair({self.question_id}): score {self.score} "
                f"outside [0, 1]")
        if self.age_h is not None and self.age_h < 0:
            raise ValueError(
                f"CalibrationPair({self.question_id}): negative age")


@dataclass(frozen=True)
class QhatTable:
    """Fitted quantiles for one (belief, alpha): global and per age bin.

    ``bin_qhats[i]`` is the quantile used for age bin ``i`` in age-binned
    mode; ``bin_fallback[i]`` marks bins that were too thin and carry the
    global value. Global mode ignores the bins entirely.
    """

    alpha: float
    age_edges_h: Tuple[float, ...]
    global_qhat: float
    n_global: int
    bin_qhats: Tuple[float, ...]
    bin_counts: Tuple[int, ...]
    bin_fallback: Tuple[bool, ...]

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha < 1.0:
            raise ValueError(f"QhatTable: alpha {self.alpha} outside (0, 1)")
        n_bins = len(self.age_edges_h) + 1
        for name, seq in (("bin_qhats", self.bin_qhats),
                          ("bin_counts", self.bin_counts),
                          ("bin_fallback", self.bin_fallback)):
            if len(seq) != n_bins:
                raise ValueError(
                    f"QhatTable: {name} has {len(seq)} entries for "
                    f"{n_bins} age bins")

    def qhat_for(self, age_h: Optional[float], binned: bool) -> float:
        """The quantile to threshold a question of belief age ``age_h``."""
        if not binned:
            return self.global_qhat
        return self.bin_qhats[age_bin_index(age_h, self.age_edges_h)]


# ------------------------------------------------------------------ quantile

def conformal_qhat(scores: Sequence[float], alpha: float) -> float:
    """The split-conformal quantile of ``scores`` at miscoverage ``alpha``.

    Returns the ``ceil((n + 1)(1 - alpha))``-th smallest score, or 1.0
    (the vacuous threshold: every receptacle is in the set) when n is too
    small for that rank to exist — including n = 0.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"conformal_qhat: alpha {alpha} outside (0, 1)")
    n = len(scores)
    rank = math.ceil((n + 1) * (1.0 - alpha))
    if n == 0 or rank > n:
        return 1.0
    return float(sorted(scores)[rank - 1])


def prediction_set(distribution: Mapping[str, float], qhat: float,
                   receptacles: Iterable[str]) -> Set[str]:
    """Receptacles whose nonconformity ``1 - p`` is at most ``qhat``.

    Ranges over ``receptacles`` (the episode's full set), not over the
    distribution's keys: a one-hot belief carries a single key, and every
    receptacle it omits has p = 0 — those are in the set exactly when
    ``qhat`` is 1, which is what makes the set vacuous rather than a
    fake singleton.
    """
    return {r for r in receptacles
            if 1.0 - distribution.get(r, 0.0) <= qhat}


# ------------------------------------------------------------------ age bins

def age_bin_index(age_h: Optional[float], edges_h: Sequence[float]) -> int:
    """Index of the age bin holding ``age_h``; None (never sighted) is the
    oldest bin. Bins are ``[0, e0), [e0, e1), ..., [e_last, inf)``."""
    if age_h is None:
        return len(edges_h)
    return bisect_right(list(edges_h), age_h)


def age_bin_labels(edges_h: Sequence[float]) -> Tuple[str, ...]:
    """Human-readable bin labels, e.g. ``0-6h, 6-24h, 24-72h, 72h+``."""
    labels = []
    low = 0.0
    for edge in edges_h:
        labels.append(f"{low:g}-{edge:g}h")
        low = edge
    labels.append(f"{low:g}h+")
    return tuple(labels)


def _validated_edges(edges_h: Sequence[float]) -> Tuple[float, ...]:
    edges = tuple(float(e) for e in edges_h)
    if any(e <= 0 for e in edges) or list(edges) != sorted(set(edges)):
        raise ValueError(
            f"age edges must be positive and strictly increasing: {edges}")
    return edges


# --------------------------------------------------------------------- fits

def fit_global_qhat(pairs: Sequence[CalibrationPair], alpha: float,
                    age_edges_h: Sequence[float] = DEFAULT_AGE_EDGES_H
                    ) -> QhatTable:
    """One quantile over every pair; the bins all carry it (as fallback)."""
    edges = _validated_edges(age_edges_h)
    n_bins = len(edges) + 1
    counts = [0] * n_bins
    for pair in pairs:
        counts[age_bin_index(pair.age_h, edges)] += 1
    qhat = conformal_qhat([p.score for p in pairs], alpha)
    return QhatTable(alpha=alpha, age_edges_h=edges, global_qhat=qhat,
                     n_global=len(pairs), bin_qhats=(qhat,) * n_bins,
                     bin_counts=tuple(counts),
                     bin_fallback=(True,) * n_bins)


def fit_age_binned_qhat(pairs: Sequence[CalibrationPair], alpha: float,
                        age_edges_h: Sequence[float] = DEFAULT_AGE_EDGES_H,
                        min_n: int = MIN_BIN_N) -> QhatTable:
    """One quantile per belief-age bin; bins with fewer than ``min_n``
    pairs fall back to the global quantile."""
    edges = _validated_edges(age_edges_h)
    n_bins = len(edges) + 1
    by_bin: List[List[float]] = [[] for _ in range(n_bins)]
    for pair in pairs:
        by_bin[age_bin_index(pair.age_h, edges)].append(pair.score)
    global_qhat = conformal_qhat([p.score for p in pairs], alpha)
    qhats, fallback = [], []
    for scores in by_bin:
        thin = len(scores) < min_n
        qhats.append(global_qhat if thin else conformal_qhat(scores, alpha))
        fallback.append(thin)
    return QhatTable(alpha=alpha, age_edges_h=edges, global_qhat=global_qhat,
                     n_global=len(pairs), bin_qhats=tuple(qhats),
                     bin_counts=tuple(len(s) for s in by_bin),
                     bin_fallback=tuple(fallback))


def coverage_by_age(pairs: Sequence[CalibrationPair], table: QhatTable,
                    binned: bool) -> List[Tuple[str, int, int, float]]:
    """Empirical coverage of the prediction set on held-out pairs, per age
    bin: ``(label, n, n_covered, qhat_used)`` in bin order."""
    labels = age_bin_labels(table.age_edges_h)
    n = [0] * len(labels)
    covered = [0] * len(labels)
    for pair in pairs:
        i = age_bin_index(pair.age_h, table.age_edges_h)
        n[i] += 1
        covered[i] += int(pair.score <= table.qhat_for(pair.age_h, binned))
    return [(labels[i], n[i], covered[i], table.bin_qhats[i] if binned
             else table.global_qhat) for i in range(len(labels))]


# -------------------------------------------------------------------- split

def household_split(household_ids: Iterable[str], split_seed: int,
                    calib_frac: float = 0.5) -> Dict[str, str]:
    """Assign every household to ``"calibration"`` or ``"test"``.

    Households are ordered by a salted SHA-256 of ``(household_id,
    split_seed)`` and the first ``round(calib_frac * n)`` (at least one,
    at most n - 1 when n >= 2) become calibration. Hash-salt-proof and
    independent of the order the ids arrive in; a household never
    appears on both sides by construction.
    """
    if not 0.0 < calib_frac < 1.0:
        raise ValueError(f"calib_frac {calib_frac} outside (0, 1)")
    ids = sorted(set(household_ids))
    if not ids:
        return {}

    def key(hid: str) -> str:
        return hashlib.sha256(f"{hid}:{split_seed}".encode()).hexdigest()

    ranked = sorted(ids, key=lambda h: (key(h), h))
    n_calib = int(round(calib_frac * len(ids)))
    if len(ids) >= 2:
        n_calib = min(max(n_calib, 1), len(ids) - 1)
    return {h: ("calibration" if i < n_calib else "test")
            for i, h in enumerate(ranked)}


# ------------------------------------------------------------ passive pass

@dataclass(frozen=True)
class PassivePass:
    """Everything one no-sensing replay of an episode yields: the
    calibration pairs (tagged with household) and the full records (the
    NeverSense baseline rows and the per-question dump)."""

    pairs: Tuple[CalibrationPair, ...]
    records: Tuple[QuestionRecord, ...]


def collect_pairs(agent: Agent, episode: Episode,
                  age_fn: AgeFn) -> PassivePass:
    """Replay ``episode`` under the passive diet with a never-sensing
    ``agent`` and score every question.

    The harness yields each record before delivering the next question's
    evidence, and a never-sensing agent adds nothing of its own, so the
    belief's state at yield time IS its state at that query: the age is
    read there. One walk of the episode gives pairs and records alike; the
    household split is applied to the pairs downstream.
    """
    pairs: List[CalibrationPair] = []
    records: List[QuestionRecord] = []
    for record in run_episode(agent, episode):
        if record.budget_spent:
            raise ValueError(
                f"collect_pairs needs a never-sensing agent; {agent.name} "
                f"spent budget on {record.question_id}")
        p_truth = record.distribution.get(record.truth_receptacle, 0.0)
        pairs.append(CalibrationPair(
            household_id=record.household_id, episode_id=record.episode_id,
            question_id=record.question_id, object_id=record.object_id,
            t_query=record.t_query,
            age_h=age_fn(record.object_id, record.t_query),
            score=min(1.0, max(0.0, 1.0 - p_truth)),
            top_prob=record.confidence, correct=record.correct))
        records.append(record)
    return PassivePass(pairs=tuple(pairs), records=tuple(records))
