"""Belief-model interface and the evidence bookkeeping every basic model
shares.

A belief model consumes the observation stream (plus any sense results the
policy pays for) and answers ``predict(object_id, t)`` with a distribution
over receptacles. All times are seconds since episode start.

Shared bookkeeping lives here so concrete models stay single-idea. The
base class maintains, per object:

* the chronological list of **positive sightings** ``(t, receptacle_id)``
  — concrete models build their base distribution from this via
  :meth:`_predict_from_history`;
* the set of **exclusions**: a sense of receptacle R at time t whose
  contents do NOT include object O is evidence that O is not in R at t.
  Exclusions are recorded here and applied on top of every concrete
  model's base distribution at prediction time, so no model reimplements
  (or silently drops) negative evidence.

Exclusion recency rule (the single place timestamps are compared — see
:meth:`BeliefModel._active_exclusions`): an exclusion of O at R recorded
at ``t_ex`` applies as long as no positive sighting of O anywhere is
STRICTLY LATER than ``t_ex``. A later sighting means the object has moved
since the exclusion was observed, so the exclusion is stale and ignored.
A positive sighting at exactly ``t_ex`` does not invalidate it: seeing O
elsewhere at the same instant is consistent with its absence from R.
"""

from __future__ import annotations

import abc
import logging
import random
from typing import Dict, List, Mapping, Set, Tuple, Union

from baselines.types import (EpisodeContext, Observation, Prediction,
                             SenseResult)

logger = logging.getLogger(__name__)

MAX_EXCLUSION_FLOOR = 0.01
"""Upper bound on the per-receptacle probability floor for excluded
receptacles; large floors would let exclusions dominate the distribution."""


class BeliefModel(abc.ABC):
    """Base class: evidence bookkeeping, exclusion logic, tie-breaking.

    Concrete models implement :meth:`_predict_from_history` only. The
    seeded ``rng`` is the model's *only* source of randomness (argmax
    tie-breaks); it is supplied by the harness so runs are fully
    determined by (bank, config, seed).

    ``exclusion_floor`` is the probability an excluded receptacle keeps
    (default 0.0 — hard exclusion). It must be small (see
    :data:`MAX_EXCLUSION_FLOOR`) so exclusions actually rule places out.
    """

    def __init__(self, rng: random.Random,
                 exclusion_floor: float = 0.0) -> None:
        if not 0.0 <= exclusion_floor <= MAX_EXCLUSION_FLOOR:
            raise ValueError(
                f"{type(self).__name__}: exclusion_floor {exclusion_floor} "
                f"outside [0, {MAX_EXCLUSION_FLOOR}]")
        self._rng = rng
        self._exclusion_floor = exclusion_floor
        self._context: EpisodeContext | None = None
        self._history: Dict[str, List[Tuple[int, str]]] = {}
        # object_id -> {receptacle_id: newest time O was seen absent from it}
        self._exclusions: Dict[str, Dict[str, int]] = {}
        self._warned_all_excluded: Set[str] = set()

    @property
    def name(self) -> str:
        """Stable identifier used in logs and result tables."""
        return type(self).__name__

    # ---------------------------------------------------------------- API

    def reset(self, context: EpisodeContext) -> None:
        """Start a fresh episode: forget all evidence, remember the context."""
        self._context = context
        self._history = {}
        self._exclusions = {}
        self._warned_all_excluded = set()

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        """Fold one piece of evidence into the belief state.

        An :class:`Observation` is a single positive sighting. A
        :class:`SenseResult` is evidence about EVERY known object: one
        positive sighting per object in its contents, and one exclusion
        (object absent from the sensed receptacle at ``t``) for each known
        object NOT in its contents.
        """
        if isinstance(evidence, Observation):
            self._add_sighting(evidence.object_id, evidence.t,
                               evidence.receptacle_id)
            return
        if self._context is None:
            raise RuntimeError(f"{self.name}: update() before reset()")
        present = set(evidence.contents)
        for obj in evidence.contents:
            self._add_sighting(obj, evidence.t, evidence.receptacle_id)
        for obj in self._context.object_classes:
            if obj not in present:
                by_receptacle = self._exclusions.setdefault(obj, {})
                previous = by_receptacle.get(evidence.receptacle_id, -1)
                by_receptacle[evidence.receptacle_id] = max(previous, evidence.t)

    def predict_readonly(self, object_id: str, t: int) -> Prediction:
        """predict() with the tie-break generator's state restored after.

        Used by the harness for full-state snapshots, which must not
        perturb the run: without this, snapshotting a never-observed
        object would consume randomness and shift the agent's own later
        tie-break answers.
        """
        state = self._rng.getstate()
        try:
            return self.predict(object_id, t)
        finally:
            self._rng.setstate(state)

    def predict(self, object_id: str, t: int) -> Prediction:
        """Distribution over receptacles for ``object_id`` at time ``t``.

        A positive sighting at exactly ``t`` short-circuits everything:
        an observation of the object AT the prediction instant is ground
        truth at that instant, and no model prior may outvote it (a
        frequency belief would otherwise answer from its history right
        after a search sense returned the object elsewhere). Otherwise
        the concrete model's base distribution (uniform fallback for a
        never-observed object) gets current exclusions applied on top —
        see :meth:`_apply_exclusions` for the exact rule and edge cases.
        Always sums to 1.
        """
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            return Prediction(distribution={current: 1.0}, argmax=current)
        base = (self._predict_from_history(history, t) if history
                else self._uniform())
        return self._apply_exclusions(object_id, t, base)

    @staticmethod
    def _sighting_at(history: List[Tuple[int, str]],
                     t: int) -> Union[str, None]:
        """Receptacle of a positive sighting at exactly ``t``, if any
        (latest-arriving wins; a truthful bank never has two receptacles
        for one object at one instant)."""
        for ot, rec in reversed(history):
            if ot == t:
                return rec
        return None

    # ------------------------------------------------- exclusion machinery

    def _add_sighting(self, object_id: str, t: int, receptacle_id: str) -> None:
        self._history.setdefault(object_id, []).append((t, receptacle_id))

    def _active_exclusions(self, object_id: str) -> Set[str]:
        """Receptacles currently ruled out for ``object_id``.

        THE recency rule (module docstring) lives here and only here: an
        exclusion recorded at ``t_ex`` is active iff no positive sighting
        of the object is strictly later than ``t_ex``.
        """
        recorded = self._exclusions.get(object_id)
        if not recorded:
            return set()
        newest_positive = max(
            (ot for ot, _ in self._history.get(object_id, [])), default=None)
        return {rec for rec, t_ex in recorded.items()
                if newest_positive is None or t_ex >= newest_positive}

    def _apply_exclusions(self, object_id: str, t: int,
                          base: Prediction) -> Prediction:
        """Zero out excluded receptacles and redistribute their mass.

        The reclaimed mass is spread UNIFORMLY over all non-excluded
        receptacles — including ones the base distribution gave zero —
        because a negative result is evidence for every receptacle not yet
        ruled out, not only for previously-sighted ones. (Renormalizing
        the surviving support alone would fabricate certainty: with base
        mass on two receptacles and one excluded, the other would jump to
        probability 1.0 even though the object may sit somewhere never
        sighted.) When exclusions cover the entire base support this
        reduces exactly to a uniform distribution over the non-excluded
        receptacles.

        Edge case: if EVERY receptacle is excluded (possible with stale
        exclusions), exclusions are ignored entirely and a warning is
        logged with the object id and query time. The result always sums
        to 1 — the :class:`~baselines.types.Prediction` contract is
        enforced on construction.
        """
        excluded = self._active_exclusions(object_id)
        if not excluded:
            return base
        receptacles = self._receptacles()
        kept = [r for r in receptacles if r not in excluded]
        if not kept:
            # Warn once per (object, episode): the condition persists across
            # every predict (including full-state snapshots) until the next
            # positive sighting, so repeating it would flood the log with
            # thousands of identical lines per run.
            if object_id in self._warned_all_excluded:
                logger.debug(
                    "%s: every receptacle still excluded for %s at t=%d",
                    self.name, object_id, t)
            else:
                self._warned_all_excluded.add(object_id)
                logger.warning(
                    "%s: every receptacle excluded for %s at t=%d; ignoring "
                    "exclusions (stale negative evidence; repeats of this "
                    "condition for this object log at DEBUG)",
                    self.name, object_id, t)
            return base
        excluded_mass = sum(p for r, p in base.distribution.items()
                            if r in excluded)
        share = excluded_mass / len(kept)
        scale = 1.0 - self._exclusion_floor * len(excluded)
        dist = {r: (base.distribution.get(r, 0.0) + share) * scale
                for r in kept}
        dist.update({r: self._exclusion_floor for r in excluded})
        # Exact renormalization: accumulated float error can push the sum
        # (and hence a lone survivor's probability) a few ulp past 1.0,
        # which the strict Answer/Prediction contracts reject.
        total = sum(dist.values())
        dist = {r: v / total for r, v in dist.items()}
        return Prediction(distribution=dist,
                          argmax=self._argmax_of(dist, kept, base.argmax))

    def _argmax_of(self, dist: Mapping[str, float], kept: List[str],
                   base_argmax: str) -> str:
        """Argmax over ``kept``; prefer the base argmax if it still tops,
        otherwise break exact ties with the seeded generator."""
        top = max(dist[r] for r in kept)
        tied = [r for r in kept if dist[r] == top]
        if base_argmax in tied:
            return base_argmax
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)

    # ------------------------------------------------------------ helpers

    @abc.abstractmethod
    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        """Predict from a non-empty chronological sighting list."""

    def _receptacles(self) -> Tuple[str, ...]:
        if self._context is None:
            raise RuntimeError(f"{self.name}: predict() before reset()")
        return self._context.receptacle_ids

    def _uniform(self) -> Prediction:
        """Uniform distribution over all receptacles; random tied argmax."""
        recs = self._receptacles()
        p = 1.0 / len(recs)
        return Prediction(distribution={r: p for r in recs},
                          argmax=self._rng.choice(list(recs)))

    @staticmethod
    def _weighted_counts(history: List[Tuple[int, str]], t: int,
                         half_life_s: Union[float, None]) -> Dict[str, float]:
        """Sighting counts, exponentially decayed by age when a half-life
        is set (weight 2^(-(t - t_obs)/half_life)); plain counts otherwise.

        An infinite-memory histogram is a known-broken estimator in a
        drifting world — old sightings outvote what the world has since
        become — so frequency-style beliefs take an optional half-life.
        """
        counts: Dict[str, float] = {}
        for ot, receptacle in history:
            weight = (1.0 if half_life_s is None
                      else 2.0 ** (-max(0, t - ot) / half_life_s))
            counts[receptacle] = counts.get(receptacle, 0.0) + weight
        return counts

    def _normalized(self, counts: Mapping[str, float],
                    tie_break_recency: List[Tuple[int, str]]) -> Prediction:
        """Frequency-normalize ``counts`` into a Prediction.

        Argmax ties are broken by recency: among tied receptacles, the one
        sighted most recently in ``tie_break_recency`` wins. This is
        deterministic, so tied modal locations never consume randomness.
        """
        total = sum(counts.values())
        dist = {r: c / total for r, c in counts.items()}
        top = max(dist.values())
        tied = [r for r, p in dist.items() if p == top]
        if len(tied) == 1:
            return Prediction(distribution=dist, argmax=tied[0])
        last_seen = {rec: i for i, (_, rec) in enumerate(tie_break_recency)}
        return Prediction(distribution=dist,
                          argmax=max(tied, key=lambda r: last_seen.get(r, -1)))
