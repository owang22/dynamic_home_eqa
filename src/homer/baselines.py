"""Phase 3 — floors, per-object statistical models, and the pooled model.

Every baseline exposes ``predict(object_id, t) -> dict[receptacle, prob]``
(a normalized distribution) after ``fit(...)``. Under E2 a held-out object
has zero training rows; each docstring states the fallback.

The pooled model is the pivotal comparison of the pilot: it shares
structure ACROSS objects (what lives-in-the-fridge things do at 6 pm) with
no persona representation at all. If it matches a persona-conditioned
method on held-out objects, the persona framing is not what is doing the
work.
"""

from __future__ import annotations

import collections
import math
from typing import Dict, List, Mapping, Sequence

Distribution = Dict[str, float]


def _norm(weights: Mapping[str, float]) -> Distribution:
    total = sum(weights.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in weights.items()}


def _hour(t: float) -> int:
    return int(t // 60) % 24


class Uniform:
    """Sanity floor: uniform over the receptacle vocabulary."""

    name = "uniform"

    def fit(self, occupancy, receptacles: Sequence[str],
            initial: Mapping[str, str], heldout: Sequence[str]) -> None:
        self._dist = _norm({r: 1.0 for r in receptacles})

    def predict(self, object_id: str, t: float) -> Distribution:
        return self._dist


class Persistence:
    """Last observed location. With no test-day observations this is the
    object's location at the END of training day 64; for a held-out object
    it is the initial placement — the only observation that exists."""

    name = "persistence"

    def fit(self, occupancy, receptacles, initial, heldout) -> None:
        self._last: Dict[str, str] = {}
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            for byhour in days:
                if byhour:
                    self._last[obj] = byhour[max(byhour)]
        for obj in heldout:
            if obj in initial:
                self._last[obj] = initial[obj]
        self._initial = dict(initial)

    def predict(self, object_id: str, t: float) -> Distribution:
        rec = self._last.get(object_id) or self._initial.get(object_id)
        return {rec: 1.0} if rec else {}


class Modal:
    """Most frequent training location (hour-weighted). Held-out fallback:
    the POOLED receptacle-popularity prior re-anchored on the initial
    placement — i.e. the initial placement with probability equal to the
    pooled self-stay rate, remainder by pooled popularity. Documented
    choice: a plain uniform fallback wastes the one observation E2 grants."""

    name = "modal"

    def fit(self, occupancy, receptacles, initial, heldout) -> None:
        self._dist: Dict[str, Distribution] = {}
        pooled: collections.Counter = collections.Counter()
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            counts: collections.Counter = collections.Counter()
            for byhour in days:
                counts.update(byhour.values())
            pooled.update(counts)
            if counts:
                self._dist[obj] = _norm(counts)
        prior = _norm(pooled)
        for obj in heldout:
            init = initial.get(obj)
            if init is None:
                self._dist[obj] = prior
                continue
            mix = {r: 0.5 * p for r, p in prior.items()}
            mix[init] = mix.get(init, 0.0) + 0.5
            self._dist[obj] = _norm(mix)

    def predict(self, object_id: str, t: float) -> Distribution:
        return self._dist.get(object_id, {})


class Frequency:
    """Per-object empirical distribution conditioned on hour-of-day, with
    Laplace-smoothed backoff to the object's unconditional distribution
    (hours with little data shrink toward the object's overall habit).
    Held-out fallback: same as Modal's (documented there)."""

    name = "frequency"

    def fit(self, occupancy, receptacles, initial, heldout) -> None:
        self._by_hour: Dict[str, Dict[int, collections.Counter]] = {}
        self._overall: Dict[str, collections.Counter] = {}
        self._fallback = Modal()
        self._fallback.fit(occupancy, receptacles, initial, heldout)
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            by_hour: Dict[int, collections.Counter] = \
                collections.defaultdict(collections.Counter)
            overall: collections.Counter = collections.Counter()
            for byhour in days:
                for hour, rec in byhour.items():
                    by_hour[hour][rec] += 1
                    overall[rec] += 1
            self._by_hour[obj] = by_hour
            self._overall[obj] = overall
        self._heldout = set(heldout)

    def predict(self, object_id: str, t: float) -> Distribution:
        if object_id in self._heldout or object_id not in self._by_hour:
            return self._fallback.predict(object_id, t)
        hour_counts = self._by_hour[object_id].get(_hour(t), {})
        overall = self._overall[object_id]
        total_overall = sum(overall.values()) or 1
        # 5 pseudo-observations of the overall habit per hour cell.
        mix = {r: hour_counts.get(r, 0) + 5 * overall.get(r, 0) / total_overall
               for r in set(hour_counts) | set(overall)}
        return _norm(mix)


class Markov:
    """Per-object first-order hourly transition model, Laplace-smoothed
    (alpha=0.5 over receptacles seen by the object, so mass cannot leak to
    places the object never visits). Prediction runs the chain forward from
    the object's modal 06:00 state to the query hour — the test day is
    unobserved, so the chain must be seeded from training structure, not
    from a test observation. Held-out fallback: Modal's."""

    name = "markov"

    def fit(self, occupancy, receptacles, initial, heldout) -> None:
        self._fallback = Modal()
        self._fallback.fit(occupancy, receptacles, initial, heldout)
        self._trans: Dict[str, Dict[str, collections.Counter]] = {}
        self._start: Dict[str, str] = {}
        self._support: Dict[str, List[str]] = {}
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            trans: Dict[str, collections.Counter] = \
                collections.defaultdict(collections.Counter)
            starts: collections.Counter = collections.Counter()
            support: set = set()
            for byhour in days:
                if 6 in byhour:
                    starts[byhour[6]] += 1
                hours = sorted(byhour)
                for a, b in zip(hours, hours[1:]):
                    if b == a + 1:
                        trans[byhour[a]][byhour[b]] += 1
                support.update(byhour.values())
            if starts:
                self._start[obj] = starts.most_common(1)[0][0]
                self._trans[obj] = trans
                self._support[obj] = sorted(support)
        self._heldout = set(heldout)

    def predict(self, object_id: str, t: float) -> Distribution:
        if object_id in self._heldout or object_id not in self._start:
            return self._fallback.predict(object_id, t)
        support = self._support[object_id]
        dist = {r: 1.0 if r == self._start[object_id] else 0.0
                for r in support}
        trans = self._trans[object_id]
        for _ in range(max(0, _hour(t) - 6)):
            nxt = {r: 0.0 for r in support}
            for src, p in dist.items():
                if p <= 0:
                    continue
                row = trans.get(src, {})
                total = sum(row.values()) + 0.5 * len(support)
                for dst in support:
                    nxt[dst] += p * (row.get(dst, 0) + 0.5) / total
            dist = nxt
        return _norm(dist)


class Pooled:
    """The pooled cross-object model — the key E2 competitor.

    Structure shared across objects: P(receptacle | initial_receptacle,
    hour), estimated from every observed object's hourly occupancy, with
    Laplace smoothing and backoff to P(receptacle | hour). The intuition it
    operationalizes: objects that start the day in the fridge behave like
    fridge things at 6 pm, whoever they are. For OBSERVED objects the
    pooled component is blended with the object's own hour-conditional
    counts (empirical-Bayes m-estimate, m=12), so it never does worse than
    frequency by much; for HELD-OUT objects it backs off to the pure
    pooled component keyed by the initial placement — exactly the graceful
    degradation the protocol is probing."""

    name = "pooled"
    M = 12.0

    def fit(self, occupancy, receptacles, initial, heldout) -> None:
        self._initial = dict(initial)
        self._heldout = set(heldout)
        by_init: Dict[str, Dict[int, collections.Counter]] = \
            collections.defaultdict(lambda: collections.defaultdict(
                collections.Counter))
        by_hour: Dict[int, collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._own: Dict[str, Dict[int, collections.Counter]] = {}
        for obj, days in occupancy.items():
            if obj in heldout:
                continue
            init = initial.get(obj)
            own: Dict[int, collections.Counter] = \
                collections.defaultdict(collections.Counter)
            for byhour in days:
                for hour, rec in byhour.items():
                    by_hour[hour][rec] += 1
                    own[hour][rec] += 1
                    if init is not None:
                        by_init[init][hour][rec] += 1
            self._own[obj] = own
        self._by_init = by_init
        self._by_hour = by_hour
        self._receptacles = list(receptacles)

    def _pooled(self, object_id: str, hour: int) -> Distribution:
        init = self._initial.get(object_id)
        cell = (self._by_init.get(init, {}).get(hour)
                if init is not None else None)
        base = self._by_hour.get(hour, {})
        mix: Dict[str, float] = {}
        total_base = sum(base.values()) or 1
        for r in set(base) | set(cell or {}) | {init} - {None}:
            mix[r] = ((cell or {}).get(r, 0)
                      + 5.0 * base.get(r, 0) / total_base + 0.1)
        return _norm(mix)

    def predict(self, object_id: str, t: float) -> Distribution:
        hour = _hour(t)
        pooled = self._pooled(object_id, hour)
        if object_id in self._heldout or object_id not in self._own:
            return pooled
        own = self._own[object_id].get(hour, {})
        n = sum(own.values())
        mix = {r: own.get(r, 0) + self.M * pooled.get(r, 0.0)
               for r in set(own) | set(pooled)}
        return _norm(mix)


ALL_BASELINES = (Uniform, Persistence, Modal, Frequency, Markov, Pooled)
