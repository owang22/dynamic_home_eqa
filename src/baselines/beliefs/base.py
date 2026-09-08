"""Belief-model interface and the one prediction pipeline every model
shares.

A belief model consumes the observation stream (plus any sense results the
policy pays for) and answers ``predict(object_id, t)`` with a distribution
over locations. All times are seconds since episode start.

The design, in three sentences:

1. The belief state space is all receptacles plus OUT_OF_HOUSE (unchanged
   vocabulary); every model outputs one distribution over it with a small
   floor everywhere, so no location is ever impossible.
2. An empty look at receptacle r at time t is an observation: evidence
   the object was not at r at t, decaying with age like any observation,
   and superseded by any strictly later positive sighting of the object.
3. There is no elimination rule anywhere: fresh empty looks crush sensed
   receptacles' mass, OUT_OF_HOUSE can never receive negative evidence
   (it cannot be looked at), so its floor mass survives renormalization
   and wins exactly when everything else has been seen empty.

Shared bookkeeping lives here so concrete models stay single-idea. The
base class maintains, per object, the chronological list of positive
sightings ``(t, receptacle_id)`` (concrete models build their base
distribution from this via :meth:`_predict_from_history`) and the newest
empty look per receptacle (a sense of R at t whose contents do NOT
include O). :meth:`negative_observations` is the public readout of the
latter.

:meth:`BeliefModel.predict` composes, in this fixed order:

1. the concrete model's distribution ``p_model`` (models may put zero on
   OUT_OF_HOUSE, or on anything);
2. the floor mix ``p = (1 - floor_mass) * p_model + floor_mass * uniform``
   over ALL locations including OUT_OF_HOUSE;
3. negative evidence: for each sensable receptacle r whose newest empty
   look at ``t_obs`` is not superseded by a later sighting, ``p(r)`` is
   multiplied by ``1 - w(t - t_obs)`` with ``w(d) = 2^(-d / half_life)``,
   so a look at the query instant suppresses fully (``w(0) = 1``) and one
   a half-life old suppresses by half. Unsensable locations never receive
   a factor. Models that ingest negatives themselves (class attribute
   :attr:`BeliefModel.consumes_negative_evidence_natively`) skip this
   step and keep steps 2 and 4;
4. renormalization.

A positive sighting AT the prediction instant short-circuits all of it
(one-hot on that receptacle): an observation of the object at the query
instant is ground truth then, and no model prior may outvote it.

Supersession rule (the single place timestamps are compared, in
:meth:`negative_observations`): an empty look at R recorded at ``t_ex``
counts as long as no positive sighting of O anywhere is STRICTLY LATER
than ``t_ex``. A later sighting means the object has moved since the
look, so the look is stale and ignored. A positive sighting at exactly
``t_ex`` does not supersede it: seeing O elsewhere at the same instant is
consistent with its absence from R.
"""

from __future__ import annotations

import abc
import logging
import random
from typing import Dict, List, Mapping, Optional, Set, Tuple, Union

from baselines.types import (EpisodeContext, Observation, Prediction,
                             SenseResult)

logger = logging.getLogger(__name__)

DEFAULT_FLOOR_MASS = 0.02
"""Share of every prediction spread uniformly over all locations (step 2
of the pipeline). Fixed a priori for every model; never tuned per bank."""

DEFAULT_NEGATIVE_HALF_LIFE_H = 24.0
"""Negative-evidence half-life for models without a half-life of their
own (a model with one uses it, see :meth:`BeliefModel.negative_half_life_h`)."""

SECONDS_PER_HOUR = 3600.0


class BeliefModel(abc.ABC):
    """Base class: evidence bookkeeping, the prediction pipeline,
    tie-breaking.

    Concrete models implement :meth:`_predict_from_history` only. The
    seeded ``rng`` is the model's *only* source of randomness (argmax
    tie-breaks); it is supplied by the harness so runs are fully
    determined by (bank, config, seed).

    ``floor_mass`` is the uniform share of step 2 (default
    :data:`DEFAULT_FLOOR_MASS`; 0.0 is allowed so unit tests can check a
    model's own arithmetic, and is never what runs). ``negative_half_life_h``
    overrides the model's negative-evidence half-life (default: the
    model's own half-life where it has one, else
    :data:`DEFAULT_NEGATIVE_HALF_LIFE_H`).

    ``legacy_exclusion_veto`` reproduces the pre-migration semantics (no
    floor, a hard permanent veto on looked-at receptacles with uniform
    redistribution, an all-excluded fallback). It exists ONLY for the
    paired migration replay (:mod:`baselines.exclusion_migration_replay`)
    and is deleted with it.
    """

    consumes_negative_evidence_natively: bool = False
    """True for models whose own machinery ingests empty looks (the
    Perpetua family feeds them to its filters as ``y = 0``); the pipeline
    then skips step 3 so negatives are not counted twice."""

    def __init__(self, rng: random.Random,
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None,
                 legacy_exclusion_veto: bool = False) -> None:
        if not 0.0 <= floor_mass < 1.0:
            raise ValueError(
                f"{type(self).__name__}: floor_mass {floor_mass} outside [0, 1)")
        if negative_half_life_h is not None and negative_half_life_h <= 0:
            raise ValueError(
                f"{type(self).__name__}: negative_half_life_h "
                f"{negative_half_life_h} must be positive")
        self._rng = rng
        self._floor_mass = float(floor_mass)
        self._negative_half_life_override = negative_half_life_h
        self._legacy_exclusion_veto = legacy_exclusion_veto
        self._context: EpisodeContext | None = None
        self._history: Dict[str, List[Tuple[int, str]]] = {}
        # object_id -> {receptacle_id: newest time O was seen absent from it}
        self._exclusions: Dict[str, Dict[str, int]] = {}
        self._warned_all_excluded: Set[str] = set()

    @property
    def name(self) -> str:
        """Stable identifier used in logs and result tables."""
        return type(self).__name__

    @property
    def floor_mass(self) -> float:
        return self._floor_mass

    @property
    def negative_half_life_h(self) -> float:
        """Half-life (hours) of an empty look's suppression: the
        constructor override, else the model's own half-life
        (:meth:`_default_negative_half_life_h`)."""
        if self._negative_half_life_override is not None:
            return float(self._negative_half_life_override)
        return float(self._default_negative_half_life_h())

    def _default_negative_half_life_h(self) -> float:
        """The model's own evidence half-life, for models that have one;
        the package default otherwise. Read lazily so a subclass can
        answer from fields set after ``super().__init__``."""
        return DEFAULT_NEGATIVE_HALF_LIFE_H

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
        positive sighting per object in its contents, and one empty look
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

    def last_prediction_diagnostics(self) -> Union[Dict[str, float], None]:
        """Optional side channel: numbers about the most recent
        :meth:`predict` that an evaluation may log next to the score
        (e.g. the largest per-edge presence belief of an edge model, its
        absence signal). None for models without one -- the default. Never
        part of the prediction itself."""
        return None

    def last_positive_sighting_time(self, object_id: str,
                                    t: int) -> Union[int, None]:
        """Time of the newest positive sighting of ``object_id`` at or
        before ``t``, or None if none has arrived by then.

        The public readout of the base-class history for consumers that
        need a belief's AGE (time since the evidence its answer rests on)
        without touching the bookkeeping — e.g. age-binned conformal
        calibration. Sightings arrive in time order, so the scan runs
        from the newest end.
        """
        for ot, _ in reversed(self._history.get(object_id, [])):
            if ot <= t:
                return ot
        return None

    def negative_observations(self, object_id: str, t: int) -> Dict[str, int]:
        """Receptacle -> time of its newest empty look for ``object_id``
        that counts at ``t``: looks at or before ``t`` not superseded by a
        strictly later positive sighting (module docstring). Models that
        want negative evidence read this; the pipeline's step 3 is built
        from it. Empty when nothing has been looked at."""
        recorded = self._exclusions.get(object_id)
        if not recorded:
            return {}
        newest_positive = max(
            (ot for ot, _ in self._history.get(object_id, []) if ot <= t),
            default=None)
        return {rec: t_ex for rec, t_ex in recorded.items()
                if t_ex <= t and (newest_positive is None
                                  or t_ex >= newest_positive)}

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
        """Distribution over all locations for ``object_id`` at time ``t``.

        A positive sighting at exactly ``t`` short-circuits everything
        (one-hot on that receptacle). Otherwise the concrete model's
        distribution (uniform fallback for a never-observed object) goes
        through the pipeline of the module docstring: floor mix,
        negative-evidence factors, renormalization. Always sums to 1.
        """
        history = self._history.get(object_id, [])
        current = self._sighting_at(history, t)
        if current is not None:
            return Prediction(distribution={current: 1.0}, argmax=current)
        base = self._predict_for_object(object_id, history, t)
        if self._legacy_exclusion_veto:
            # Pre-migration: models that ingest negatives natively had an
            # identity override; everything else got the hard veto.
            if self._consumes_negative_evidence_natively():
                return base
            return self._legacy_apply_veto(object_id, t, base)
        return self._compose(object_id, t, base)

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

    # ------------------------------------------------------- the pipeline

    def _add_sighting(self, object_id: str, t: int, receptacle_id: str) -> None:
        self._history.setdefault(object_id, []).append((t, receptacle_id))

    def _consumes_negative_evidence_natively(self) -> bool:
        """Whether step 3 is skipped for the prediction being assembled.
        The class attribute by default; a model whose native handling is
        per-prediction (the LLM belief's fallback path) overrides this."""
        return self.consumes_negative_evidence_natively

    def negative_factors(self, object_id: str, t: int) -> Dict[str, float]:
        """Step 3's multipliers: sensable receptacle -> ``1 - w(age)`` for
        every empty look that counts at ``t`` (see
        :meth:`negative_observations`); receptacles without one are
        absent (factor 1). Unsensable locations never appear."""
        looks = self.negative_observations(object_id, t)
        if not looks:
            return {}
        assert self._context is not None
        sensable = set(self._context.sensable_receptacle_ids)
        half_life_s = self.negative_half_life_h * SECONDS_PER_HOUR
        return {rec: 1.0 - 2.0 ** (-max(0, t - t_obs) / half_life_s)
                for rec, t_obs in looks.items() if rec in sensable}

    def _compose(self, object_id: str, t: int, base: Prediction) -> Prediction:
        """Steps 2-4 of the pipeline on the model's distribution ``base``.

        The result always covers every location (the floor puts mass on
        each) and sums to 1. Argmax: the model's own argmax if it still
        tops, else exact ties break with the seeded generator. With
        ``floor_mass`` 0 and every massive receptacle freshly seen empty
        the total can be 0; that degenerate case (unit tests only) falls
        back to uniform.
        """
        receptacles = self._receptacles()
        floor = self._floor_mass / len(receptacles)
        dist = {r: (1.0 - self._floor_mass) * base.distribution.get(r, 0.0)
                + floor for r in receptacles}
        if not self._consumes_negative_evidence_natively():
            for rec, factor in self.negative_factors(object_id, t).items():
                dist[rec] *= factor
        total = sum(dist.values())
        if total <= 0.0:
            return self._uniform()
        dist = {r: v / total for r, v in dist.items()}
        return Prediction(distribution=dist,
                          argmax=self._argmax_of(dist, list(receptacles),
                                                 base.argmax))

    def _argmax_of(self, dist: Mapping[str, float], kept: List[str],
                   base_argmax: str) -> str:
        """Argmax over ``kept``; prefer the base argmax if it still tops,
        otherwise break exact ties with the seeded generator."""
        top = max(dist[r] for r in kept)
        tied = [r for r in kept if dist[r] == top]
        if base_argmax in tied:
            return base_argmax
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)

    # ----------------------------------------------- legacy (replay only)

    def _legacy_apply_veto(self, object_id: str, t: int,
                           base: Prediction) -> Prediction:
        """The pre-migration rule, kept verbatim for the paired replay:
        zero out every receptacle with a counting empty look (the look
        never ages) and spread the reclaimed mass uniformly over the
        rest; if every receptacle is excluded, ignore the exclusions and
        warn once per (object, episode). No floor anywhere."""
        excluded = set(self.negative_observations(object_id, t))
        if not excluded:
            return base
        receptacles = self._receptacles()
        kept = [r for r in receptacles if r not in excluded]
        if not kept:
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
        dist = {r: base.distribution.get(r, 0.0) + share for r in kept}
        dist.update({r: 0.0 for r in excluded})
        total = sum(dist.values())
        dist = {r: v / total for r, v in dist.items()}
        return Prediction(distribution=dist,
                          argmax=self._argmax_of(dist, kept, base.argmax))

    # ------------------------------------------------------------ helpers

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        """The model's own distribution, before the pipeline.

        The default routes a non-empty history to
        :meth:`_predict_from_history` and a never-observed object to the
        uniform fallback. Models that pool evidence ACROSS objects (and so
        can say something useful even about a never-sighted object)
        override this method instead of ``_predict_from_history``; the
        floor, negative evidence, renormalization and the
        sighting-at-prediction-instant override still come from
        :meth:`predict` and are never reimplemented.
        """
        return (self._predict_from_history(history, t) if history
                else self._uniform())

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        """Predict from a non-empty chronological sighting list.

        Per-object models implement this; cross-object models override
        :meth:`_predict_for_object` instead and never reach it.
        """
        raise NotImplementedError(
            f"{self.name}: implement _predict_from_history or override "
            f"_predict_for_object")

    def _receptacles(self) -> Tuple[str, ...]:
        if self._context is None:
            raise RuntimeError(f"{self.name}: predict() before reset()")
        return self._context.receptacle_ids

    def _uniform(self) -> Prediction:
        """Uniform distribution over all locations; random tied argmax."""
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
