"""Belief: cluster days into day-types and mix per-type timetables.

The cheapest model that SHARES information across objects — the
statistical proxy for "knowing what kind of day the household is having".
Three parts, all recomputed lazily from the shared evidence store
whenever new sightings have arrived:

1. **Day clustering.** Each observed day is featurized as the one-hot
   vector of per-object modal sighted locations that day (objects unseen
   that day contribute nothing). Days are clustered into K day-types by
   seeded k-means on those one-hot features (Lloyd iterations from a
   seeded initial assignment; K shrinks to the number of observed days
   when fewer exist).
2. **Per-type timetables.** For each (day-type, object, time-of-day bin):
   decayed sighting counts (frozen 24 h half-life), with the usual
   fallbacks — an empty bin falls back to the (type, object) whole-day
   histogram, an object unseen in the type falls back to its global
   decayed histogram.
3. **Day-type inference.** The query day's type posterior is naive Bayes:
   prior = Laplace-smoothed day counts per type, times a day-of-week term
   ``p(weekday(query) | type)`` (day-of-week is regime evidence the model
   always has, even when no sighting from the query day has arrived yet —
   which is every question under the horizon-controlled passive protocol,
   where evidence is frozen at a checkpoint before the query day), times
   one likelihood term per sighting already seen from the query day
   (``p(object at receptacle in bin | type)``, Laplace-smoothed).

The prediction is the posterior-weighted mixture of the per-type
timetable distributions. All hyperparameters are fixed a priori
(:class:`DaytypeMixtureConfig`); k-means uses its own generator seeded
from ``kmeans_seed`` so clustering is a pure function of the evidence,
never of call order. All times are seconds since episode start; a day is
86 400 s and weekday = ``day_index % 7`` (day 0 = Monday, matching
:mod:`baselines.beliefs.timetable`).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Mapping, Sequence, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import DAY_SECONDS, Prediction

HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7
_KMEANS_MAX_ITERATIONS = 20

_DayFeature = FrozenSet[Tuple[str, str]]   # {(object_id, receptacle_id)}


@dataclass(frozen=True)
class DaytypeMixtureConfig:
    """Fixed hyperparameters (no per-bank tuning)."""

    n_types: int = 3              # K day-types (shrinks to observed days)
    bin_hours: int = 2            # time-of-day bin width for timetables
    half_life_h: float = 24.0     # count decay half-life (frozen, panel-wide)
    kmeans_seed: int = 0          # clustering is deterministic given data

    def __post_init__(self) -> None:
        if self.n_types < 1:
            raise ValueError(
                f"DaytypeMixtureConfig: n_types {self.n_types} must be >= 1")
        if self.bin_hours <= 0 or HOURS_PER_DAY % self.bin_hours != 0:
            raise ValueError(
                f"DaytypeMixtureConfig: bin_hours must divide "
                f"{HOURS_PER_DAY}, got {self.bin_hours}")
        if self.half_life_h <= 0:
            raise ValueError(
                f"DaytypeMixtureConfig: half_life_h {self.half_life_h} "
                f"must be > 0")


def _day_features(history_by_object: Mapping[str, Sequence[Tuple[int, str]]]
                  ) -> Dict[int, _DayFeature]:
    """day_index -> one-hot feature set of per-object modal locations."""
    per_day_counts: Dict[int, Dict[str, Dict[str, int]]] = {}
    for obj, history in history_by_object.items():
        for t, rec in history:
            day = t // DAY_SECONDS
            by_rec = per_day_counts.setdefault(day, {}).setdefault(obj, {})
            by_rec[rec] = by_rec.get(rec, 0) + 1
    features: Dict[int, _DayFeature] = {}
    for day, by_object in per_day_counts.items():
        pairs = []
        for obj, counts in by_object.items():
            top = max(counts.values())
            # Modal ties break lexicographically: deterministic, data-only.
            modal = min(r for r, c in counts.items() if c == top)
            pairs.append((obj, modal))
        features[day] = frozenset(pairs)
    return features


def _kmeans_day_types(features: Dict[int, _DayFeature], k: int,
                      seed: int) -> Dict[int, int]:
    """day_index -> day-type via seeded Lloyd k-means on one-hot features.

    Distance to a centroid (a mean of one-hot vectors, stored sparsely) is
    squared Euclidean. Empty clusters keep their previous centroid. The
    generator is local and seeded, so the result depends only on
    (features, k, seed).
    """
    days = sorted(features)
    k = min(k, len(days))
    rng = random.Random(seed)
    seeds = rng.sample(days, k)
    centroids: List[Dict[Tuple[str, str], float]] = [
        {pair: 1.0 for pair in features[day]} for day in seeds]
    assignment: Dict[int, int] = {}
    for _ in range(_KMEANS_MAX_ITERATIONS):
        new_assignment = {
            day: min(range(k),
                     key=lambda c: _sq_distance(features[day], centroids[c]))
            for day in days}
        if new_assignment == assignment:
            break
        assignment = new_assignment
        for c in range(k):
            members = [features[d] for d in days if assignment[d] == c]
            if members:
                centroids[c] = _mean_one_hot(members)
    return assignment


def _sq_distance(feature: _DayFeature,
                 centroid: Mapping[Tuple[str, str], float]) -> float:
    """Squared Euclidean distance between a one-hot set and a sparse mean."""
    distance = sum((1.0 - centroid.get(pair, 0.0)) ** 2 for pair in feature)
    distance += sum(v * v for pair, v in centroid.items()
                    if pair not in feature)
    return distance


def _mean_one_hot(members: Sequence[_DayFeature]
                  ) -> Dict[Tuple[str, str], float]:
    sums: Dict[Tuple[str, str], float] = {}
    for feature in members:
        for pair in feature:
            sums[pair] = sums.get(pair, 0.0) + 1.0
    return {pair: v / len(members) for pair, v in sums.items()}


class DaytypeMixture(BeliefModel):
    """Posterior-over-day-types mixture of per-type timetables.

    See the module docstring for the three stages. The clustering and
    timetables are cached and rebuilt only when the total sighting count
    changes, so per-question prediction stays cheap.
    """

    def __init__(self, rng: random.Random, config: DaytypeMixtureConfig,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._cfg = config
        self._cached_at_count = -1
        self._day_types: Dict[int, int] = {}
        self._n_types_fit = 0

    @property
    def name(self) -> str:
        return (f"DaytypeMixture(K={self._cfg.n_types},"
                f"bin={self._cfg.bin_hours}h,hl={self._cfg.half_life_h:g}h)")

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        self._refit_if_stale()
        if not self._day_types:
            counts = self._weighted_counts(history, t,
                                           self._cfg.half_life_h * 3600)
            return self._normalized(counts, tie_break_recency=history)
        posterior = self._type_posterior(t)
        mixture: Dict[str, float] = {}
        for day_type, weight in posterior.items():
            for rec, p in self._type_distribution(day_type, history,
                                                  t).items():
                mixture[rec] = mixture.get(rec, 0.0) + weight * p
        return self._normalized(mixture, tie_break_recency=history)

    # ------------------------------------------------------------ fitting

    def _refit_if_stale(self) -> None:
        """Recluster when new evidence arrived; pure function of the store."""
        count = sum(len(h) for h in self._history.values())
        if count == self._cached_at_count:
            return
        features = _day_features(self._history)
        self._day_types = (_kmeans_day_types(features, self._cfg.n_types,
                                             self._cfg.kmeans_seed)
                           if features else {})
        self._n_types_fit = (max(self._day_types.values()) + 1
                             if self._day_types else 0)
        self._cached_at_count = count

    def _sightings_of_type(self, day_type: int,
                           history: Sequence[Tuple[int, str]]
                           ) -> List[Tuple[int, str]]:
        return [(t, r) for t, r in history
                if self._day_types.get(t // DAY_SECONDS) == day_type]

    # ---------------------------------------------------------- inference

    def _type_posterior(self, t: int) -> Dict[int, float]:
        """Naive-Bayes posterior over day-types for the query day.

        Log-space product of the Laplace-smoothed size prior, the
        day-of-week term, and one term per already-seen sighting from the
        query day (none under the frozen-checkpoint protocol).
        """
        query_day = t // DAY_SECONDS
        weekday = query_day % DAYS_PER_WEEK
        day_count = len(self._day_types)
        log_scores: Dict[int, float] = {}
        for day_type in range(self._n_types_fit):
            members = [d for d, c in self._day_types.items() if c == day_type]
            prior = (len(members) + 1.0) / (day_count + self._n_types_fit)
            dow_hits = sum(1 for d in members
                           if d % DAYS_PER_WEEK == weekday)
            dow = (dow_hits + 1.0) / (len(members) + DAYS_PER_WEEK)
            log_scores[day_type] = math.log(prior) + math.log(dow)
        for obj, history in sorted(self._history.items()):
            for ot, rec in history:
                if ot // DAY_SECONDS == query_day and ot <= t:
                    for day_type in log_scores:
                        log_scores[day_type] += math.log(
                            self._sighting_likelihood(day_type, obj, ot, rec))
        top = max(log_scores.values())
        weights = {c: math.exp(s - top) for c, s in log_scores.items()}
        total = sum(weights.values())
        return {c: w / total for c, w in weights.items()}

    def _sighting_likelihood(self, day_type: int, object_id: str,
                             t: int, receptacle: str) -> float:
        """Laplace-smoothed p(object at receptacle in bin(t) | day_type)."""
        bin_size = self._cfg.bin_hours * 3600
        query_bin = (t % DAY_SECONDS) // bin_size
        in_type = self._sightings_of_type(
            day_type, self._history.get(object_id, []))
        in_bin = [(ot, r) for ot, r in in_type
                  if (ot % DAY_SECONDS) // bin_size == query_bin]
        hits = sum(1 for _, r in in_bin if r == receptacle)
        n_receptacles = len(self._receptacles())
        return (hits + 1.0) / (len(in_bin) + n_receptacles)

    def _type_distribution(self, day_type: int,
                           history: Sequence[Tuple[int, str]],
                           t: int) -> Dict[str, float]:
        """The type's timetable distribution for one object at time ``t``.

        Fallback chain: query bin within the type -> the type's whole-day
        histogram -> the object's global history.
        """
        bin_size = self._cfg.bin_hours * 3600
        query_bin = (t % DAY_SECONDS) // bin_size
        in_type = self._sightings_of_type(day_type, history)
        in_bin = [(ot, r) for ot, r in in_type
                  if (ot % DAY_SECONDS) // bin_size == query_bin]
        pool = in_bin or in_type or list(history)
        counts = self._weighted_counts(pool, t, self._cfg.half_life_h * 3600)
        total = sum(counts.values())
        return {r: c / total for r, c in counts.items()}
