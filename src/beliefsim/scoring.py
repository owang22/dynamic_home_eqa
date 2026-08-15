"""Scoring and aggregation — the single code path every reported number
takes.

Two rules are enforced here, both of them consequences of defects found in
the superseded HOMER+ pilot (see
``superseded/homer_pilot_2026_08/README.md``):

**Argmax ties are broken by a seeded RNG, never by key order.** The pilot
ranked candidates with a stable sort on descending probability, so a flat
distribution silently resolved to the alphabetically-first receptacle. That
turned the uniform control from a chance floor (1/|R| ~ 0.04) into a
measurement of one arbitrary receptacle's occupancy (0.000 to 0.103,
depending on the household), and a comparison against it produced a
published-sounding conclusion that was pure artifact. Any belief that is
flat, or flat across its top candidates, must have that indifference
expressed as randomness. Runs are repeated over several seeds
(:data:`DEFAULT_SEEDS`) and the spread reported, because a single seed of a
tie-heavy method is not a measurement.

**Every table and plot derives from one long-format CSV through the
functions in this module,** and micro vs macro averaging is an explicit
argument that the emitted header states. The pilot reported one quantity as
0.196, 0.052 and 0.076 from two code paths, none of them labelled. There is
no defensible default here: micro weights instants (so busy objects and long
days dominate), macro weights the unit of analysis equally (so a household
with few displaced instants still counts once). Both are legitimate; leaving
it implicit is not.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, Mapping, Sequence, Tuple

DEFAULT_SEEDS: Tuple[int, ...] = (0, 1, 2, 3, 4)
"""Scoring seeds. Five is the minimum that gives a visible spread; the
tie-break is the only consumer of randomness in scoring itself, so this is
about the stability of the reported number, not about statistical power
(the unit of analysis is the household, n=3)."""

LOG_LOSS_FLOOR = 1e-6
"""Probability floor for log-loss. A belief that assigns exactly zero to the
truth is infinitely wrong, which would make any aggregate infinite and
destroy the metric's usefulness for comparing policies. The floor caps the
per-instant penalty at -ln(1e-6) = 13.8 nats. It is deliberately far below
1/|R| (~0.04) so a confident-and-wrong belief is still punished far harder
than an uninformative one."""


def argmax_tiebroken(distribution: Mapping[str, float],
                     rng: random.Random) -> str:
    """Highest-probability key, ties broken by ``rng``.

    Ties are compared on exact float equality. That is the right test here:
    the tie that matters is the structural one (a uniform prior, or a
    fallback that spreads mass evenly over untouched receptacles), where the
    values are produced by the same division and are bit-identical. Two
    independently-computed near-equal probabilities are a genuine ranking,
    not indifference, and must not be shuffled.
    """
    if not distribution:
        raise ValueError("argmax of an empty distribution")
    top = max(distribution.values())
    tied = [k for k, v in distribution.items() if v == top]
    return tied[0] if len(tied) == 1 else rng.choice(sorted(tied))


def brier(distribution: Mapping[str, float], truth: str,
          receptacles: Sequence[str]) -> float:
    """Multiclass Brier score: sum_r (p_r - 1[r == truth])^2, range [0, 2].

    Scored over the full receptacle set, not the distribution's support, so
    that a belief which omits receptacles is not rewarded for the omission.
    """
    total = 0.0
    for r in receptacles:
        p = distribution.get(r, 0.0)
        total += (p - (1.0 if r == truth else 0.0)) ** 2
    return total


def log_loss(distribution: Mapping[str, float], truth: str) -> float:
    """Negative log probability of the truth, in nats, floored at
    :data:`LOG_LOSS_FLOOR`."""
    return -math.log(max(distribution.get(truth, 0.0), LOG_LOSS_FLOOR))


def score_instant(distribution: Mapping[str, float], truth: str,
                  receptacles: Sequence[str],
                  rng: random.Random) -> Dict[str, float]:
    """All per-instant metrics for one (belief, ground truth) pair.

    Emitted together so that top-1 and the proper scores can never disagree
    about which belief they describe. Top-1 alone cannot show whether a
    policy's uncertainty is meaningful, which is exactly what an
    uncertainty-driven policy depends on.
    """
    return {"correct": float(argmax_tiebroken(distribution, rng) == truth),
            "brier": brier(distribution, truth, receptacles),
            "log_loss": log_loss(distribution, truth)}


def aggregate(rows: Iterable[Mapping[str, object]], value: str, *,
              mode: str, unit: str = "household") -> float:
    """Mean of ``value`` over ``rows``, micro or macro. No default mode.

    ``mode="micro"`` averages over rows: every scored instant counts once.
    ``mode="macro"`` averages the per-``unit`` micro-averages: every unit
    counts once regardless of how many instants it contributed.

    Units contributing zero rows cannot be represented (they have no mean),
    so macro is over the units actually present. That silent dropping is the
    exact bias found in the pilot's learning-curve aggregation; callers who
    care must check :func:`unit_counts` alongside the number.
    """
    rows = [r for r in rows if r.get(value) not in (None, "")]
    if not rows:
        return float("nan")
    if mode == "micro":
        return sum(float(r[value]) for r in rows) / len(rows)
    if mode == "macro":
        by_unit: Dict[object, list] = {}
        for r in rows:
            by_unit.setdefault(r[unit], []).append(float(r[value]))
        return sum(sum(v) / len(v) for v in by_unit.values()) / len(by_unit)
    raise ValueError(f"mode must be 'micro' or 'macro', got {mode!r}")


def unit_counts(rows: Iterable[Mapping[str, object]], value: str, *,
                unit: str = "household") -> Dict[object, int]:
    """Rows contributing to ``value`` per unit — the audit companion to
    :func:`aggregate`, so a macro-average built from wildly unequal or
    missing units is visible rather than inferred."""
    counts: Dict[object, int] = {}
    for r in rows:
        if r.get(value) not in (None, ""):
            counts[r[unit]] = counts.get(r[unit], 0) + 1
    return counts


def aggregation_note(mode: str, unit: str = "household") -> str:
    """The sentence every emitted table must carry in its header."""
    if mode == "micro":
        return ("Aggregation: MICRO — mean over scored instants; units "
                "contributing more instants weigh more.")
    if mode == "macro":
        return (f"Aggregation: MACRO over {unit} — mean of per-{unit} "
                f"means; each {unit} weighs equally.")
    raise ValueError(f"mode must be 'micro' or 'macro', got {mode!r}")
