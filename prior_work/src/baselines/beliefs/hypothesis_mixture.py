"""Belief: a weighted mixture over existing zoo beliefs, each treated as
one hypothesis about the household's dynamics.

Every particle is a full belief model from the registry, consuming the
identical evidence stream. The mixture holds one log weight per particle,
uniform at reset, and updates it at EVIDENCE time: before an event is
applied, each particle is asked for its current distribution over the
objects the event speaks about, and its log weight gains that event's
log likelihood. The event is then applied to every particle as normal.

An event's log likelihood for particle i has two halves. **Presence**:
``log p_i(O at R)`` for every object O the event reports at receptacle R
— particles that keep predicting where things actually turn up gain
weight. **Absence**: ``absence_weight * log(1 - p_i(O at R))`` for every
object a sense result shows is NOT in R — which is what punishes a
confident false positive. A one-hot particle certain the mug is in a
drawer that is then opened and found mug-free takes ``log(0.02) = -3.9``
where presence-only scoring charged it nothing at all.

Two corrections make the absence half usable, both configurable:

* **Selection** (``absence_threshold``). A look at a drawer holding 2 of
  40 objects yields 38 absence terms against 2 presence terms, and most
  of the 38 are objects no particle ever placed there — ``log(0.999)``
  each, individually negligible but systematically punishing whichever
  particle spreads the most mass around, so the weights start measuring
  who is best at predicting emptiness. Only objects on which SOME
  particle claimed at least ``absence_threshold`` mass are scored. The
  set is chosen by the max over particles, never by the mixture's
  weighted mass: every particle must be scored on the same object set
  (absence terms are all ``<= 0``, so a particle handed more terms is
  penalized merely for holding opinions), and a weight-dependent set
  would let the current leader choose its own exam.
* **Tempering** (``absence_weight``). The surviving absence terms are
  not independent observations — one look produces all of them at once,
  and they share the single question of whether that receptacle's
  contents are what the particle thought. Scoring them at full strength
  counts one physical act as many observations. The weight is a blunt
  dependence correction; :data:`DEFAULT_ABSENCE_WEIGHT` records what it
  was set from.

Setting ``absence_weight`` to 0 recovers presence-only scoring exactly.

The predict-before-update hook this needs lives HERE, inside
:meth:`update`, not in the harness: every consumer (harness, passive
evaluation, replay, traces) delivers evidence through ``update``, so
implementing the hook inside it covers them all without widening any
shared contract.

Weights are tempered by a forgetting factor applied once per EVENT (not
once per term): ``log_w = decay * log_w + event_log_likelihood``. Per
term would make the forgetting rate depend on how many objects a look
happened to touch — a 40-object look would apply ``decay^40`` and wipe
the history in one glance. At ``decay = 1`` the weights are the exact
Bayesian posterior over a fixed hypothesis set and collapse onto one
particle within days; below 1 old evidence fades and the mixture can
re-open when the household changes regime. Normalization is in log
space; the effective sample size ``1 / sum(w_i^2)`` is tracked after
every weight update (``ess_history``).

Prediction is the weight-normalized average of the particles' own
predictions. Each particle already applied its own floor mix and
empty-look suppression, so both arrive in the average and the mixture
level adds NEITHER again: its own ``floor_mass`` defaults to 0 and it
opts out of the suppression step — a second application of either would
double-count, and with one particle the mixture must equal that particle
exactly (asserted in tests).

All times are seconds since episode start.
"""

from __future__ import annotations

import math
import os as _os
import random
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from baselines.beliefs.base import DEFAULT_FLOOR_MASS, BeliefModel
from baselines.types import (EpisodeContext, Observation, Prediction,
                             SenseResult)

DEFAULT_DECAY = 0.6
"""Forgetting factor on log weights, applied once per evidence event.

The steady-state log-weight gap between two particles is roughly the
per-event gap over ``1 - decay``. One room-visit event scores several
objects at once and opens a gap of order a nat, and a healthy mixture
wants a steady-state gap of a couple of nats (leader weight ~0.6 over
seven particles), which puts ``decay`` near 0.5-0.6. Measured on the two
day-0 trial banks over 7 days, final ESS / leader weight:

===== ================ ================
decay hh_001           hh_002
===== ================ ================
0.99  1.00 / 1.00      1.00 / 1.00
0.95  2.04 / 0.65      1.00 / 1.00
0.90  1.89 / 0.69      1.00 / 1.00
0.80  1.88 / 0.71      1.02 / 0.99
0.70  2.09 / 0.67      1.37 / 0.85
0.60  2.27 / 0.63      2.17 / 0.63
0.50  2.45 / 0.59      2.72 / 0.51
===== ================ ================

(full 28-day evidence stream — the hardest case, since collapse pressure
grows with evidence.) 0.6 is the largest value at which BOTH households
stay above ESS 2. It
is deliberately reactive: the weights track who has predicted the last
handful of looks, which is the quantity a disambiguating sense can move.
1.0 is the pure posterior (collapses; see the tests)."""

DEFAULT_PARTICLE_SPECS: Tuple[Dict[str, Any], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent", "half_life_h": 24.0},
    {"name": "timetable", "half_life_h": 24.0},
    {"name": "markov1"},
    {"name": "periodic_persistence"},
    {"name": "hierarchy_backoff"},
    {"name": "smoothed_recency"},
)
"""One representative per belief family, at registry defaults. The
disagreement measurement (STATUS 2026-09-11) showed cross-family
particles are the ones with something to disagree about. `daytype_mixture`
and `perpetua_star` are family representatives too but cost an order of
magnitude more per update; they are left out of the default list for
speed and can be added through the config's particle list."""

DEFAULT_ABSENCE_WEIGHT = 0.25
"""Scale on the absence half of an event's log likelihood (module
docstring). 0 is presence-only scoring.

Set against the SPREAD each half pays out across particles — max minus
min of its cumulative log likelihood — which is what actually moves a
softmax. Over 7 days on the two day-0 trial banks the presence half
spreads 173 (hh_001) and 293 (hh_002) nats, while the absence half
spreads ``282 * w`` and ``473 * w``. The two halves therefore cross over
near ``w = 0.6``: above it the weights are driven mainly by which
particle is best at predicting emptiness, which is not the question. At
0.25 absence carries about 40% of presence's discriminating power and
final ESS holds at 4.5 (against 5.2 presence-only, 2.8 at w = 1).

Task accuracy does NOT discriminate here — 0.630/0.571 presence-only
against 0.635/0.571 at w = 1, flat inside noise — so the default rests
on the spread argument and the dependence argument above it, not on a
measured accuracy win. Full table:
``reports/baselines/hypothesis_mixture/absence_weight.md``."""

DEFAULT_ABSENCE_UNIFORMS = 2.0
"""How many times uniform mass some particle must place on the sensed
receptacle before an object's absence is scored at all.

Expressed in multiples of ``1 / n_locations`` rather than as a flat
probability, because a flat one is not household-agnostic: 0.05 is twice
uniform in a 40-location home and five times BELOW uniform in a
4-location one, where it would admit everything. At 2x uniform the rule
reads "some particle thinks this object is at least twice as likely to
be here as chance" — a claim worth testing — and it drops the long tail
of objects nobody expected to be there. 0 scores every absence.

It earns its place on hh_002, where dropping it to 0 (scoring all ~40
absences per look) takes final ESS from 4.53 to 3.62 and passive accuracy
from 0.571 to 0.565: the tail terms are near-identical across particles,
so they add common-mode pressure toward collapse without adding signal.
On hh_001 it is a wash (4.46 vs 4.43, accuracy identical)."""

_MIN_LIKELIHOOD = float(__import__("os").environ.get("HYPOTHESIS_MIN_LIKELIHOOD", "1e-12"))
"""Floor on a particle's likelihood for one sighting. Confidence study: HYPOTHESIS_MIN_LIKELIHOOD=0.02
caps a miss at ~3.9 nats (x temper) so one round cannot hand the mixture to a single document."""
"""Floor on a particle's per-term likelihood before the log, so a
degenerate zero-floor particle cannot send a weight to -inf. Reached only
by a particle running at ``floor_mass`` 0; the panel's 0.02 floor caps a
confident false positive at ``log(0.02)`` on its own."""


class HypothesisMixture(BeliefModel):
    """Weighted average of zoo beliefs with sighting-likelihood weights.

    ``particle_specs`` are registry belief specs (default
    :data:`DEFAULT_PARTICLE_SPECS`); each particle gets its own generator
    derived from the mixture's so runs stay deterministic. ``decay`` is
    the forgetting factor of the module docstring.
    """

    # Every particle already suppressed its empty looks; a second pass at
    # the mixture level would double-count them (module docstring).
    consumes_negative_evidence_natively = True

    def __init__(self, rng: random.Random,
                 particle_specs: Optional[Sequence[Mapping[str, Any]]] = None,
                 decay: float = DEFAULT_DECAY,
                 absence_weight: float = DEFAULT_ABSENCE_WEIGHT,
                 absence_uniforms: float = DEFAULT_ABSENCE_UNIFORMS,
                 floor_mass: float = 0.0,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        if not 0.0 < decay <= 1.0:
            raise ValueError(
                f"HypothesisMixture: decay {decay} outside (0, 1]")
        if absence_weight < 0.0:
            raise ValueError(
                f"HypothesisMixture: absence_weight {absence_weight} "
                f"must be >= 0")
        if absence_uniforms < 0.0:
            raise ValueError(
                f"HypothesisMixture: absence_uniforms {absence_uniforms} "
                f"must be >= 0")
        from baselines.registry import build_registered_belief
        specs = [dict(s) for s in (particle_specs if particle_specs is not None
                                   else DEFAULT_PARTICLE_SPECS)]
        if not specs:
            raise ValueError("HypothesisMixture: particle list is empty")
        self._decay = float(decay)
        self._absence_weight = float(absence_weight)
        self._absence_uniforms = float(absence_uniforms)
        self._particles: List[BeliefModel] = [
            build_registered_belief(
                spec, random.Random(rng.getrandbits(64)))
            for spec in specs]
        self._log_weights: List[float] = [0.0] * len(specs)
        self.ess_history: List[Tuple[int, float]] = []
        # Diagnostics: cumulative log likelihood each particle earned from
        # each half of the scoring. Their SPREAD across particles is what
        # says whether presence or absence is driving the weights — the
        # measurement that sets absence_weight.
        self.presence_totals: List[float] = [0.0] * len(specs)
        self.absence_totals: List[float] = [0.0] * len(specs)

    @property
    def name(self) -> str:
        return (f"HypothesisMixture(k={len(self._particles)},"
                f"decay={self._decay:g},abs={self._absence_weight:g})")

    @property
    def absence_weight(self) -> float:
        return self._absence_weight

    @property
    def absence_uniforms(self) -> float:
        return self._absence_uniforms

    @property
    def absence_threshold(self) -> float:
        """The selection rule as a probability: ``absence_uniforms`` times
        uniform over this household's locations."""
        return self._absence_uniforms / len(self._receptacles())

    @property
    def particles(self) -> Tuple[BeliefModel, ...]:
        return tuple(self._particles)

    @property
    def decay(self) -> float:
        return self._decay

    # ------------------------------------------------------------- weights

    @property
    def weights(self) -> List[float]:
        """Normalized particle weights (log-space normalization)."""
        top = max(self._log_weights)
        raw = [math.exp(lw - top) for lw in self._log_weights]
        total = sum(raw)
        return [w / total for w in raw]

    @property
    def effective_sample_size(self) -> float:
        """``1 / sum(w_i^2)`` over the normalized weights: k when uniform,
        1 when collapsed onto a single particle."""
        return 1.0 / sum(w * w for w in self.weights)

    def _claimed_mass(self, object_id: str, receptacle_id: str,
                      t: int) -> List[float]:
        """Each particle's current mass on ``receptacle_id`` for
        ``object_id``, in particle order. No generator is perturbed."""
        return [p.predict_readonly(object_id, t).distribution.get(
                    receptacle_id, 0.0) for p in self._particles]

    def _event_log_likelihoods(
            self, evidence: Union[Observation, SenseResult]) -> List[float]:
        """Per-particle log likelihood of one evidence event, presence and
        absence halves together (module docstring).

        Called BEFORE the event reaches any particle, so every term is a
        genuine forecast: scoring after the update would hand a one-hot
        recency model likelihood 1 on every sighting and measure
        memorization instead of prediction.
        """
        totals = [0.0] * len(self._particles)
        if isinstance(evidence, Observation):
            self._add_presence(totals, evidence.object_id,
                               evidence.receptacle_id, evidence.t)
            return totals

        receptacle, t = evidence.receptacle_id, evidence.t
        for obj in evidence.contents:
            self._add_presence(totals, obj, receptacle, t)
        if self._absence_weight <= 0.0:
            return totals
        # A person sense clears one resident; it excludes ON_PERSON as a
        # whole only once every resident is cleared (base class rule).
        absent_at = self.absence_location(evidence)
        if absent_at is None:
            return totals
        present = set(evidence.contents)
        for obj in sorted(self._objects):
            if obj not in present:
                self._add_absence(totals, obj, absent_at, t)
        return totals

    def _add_presence(self, totals: List[float], object_id: str,
                      receptacle_id: str, t: int) -> None:
        """``log p_i(object at receptacle)`` into ``totals`` per particle."""
        for index, mass in enumerate(
                self._claimed_mass(object_id, receptacle_id, t)):
            term = math.log(max(mass, _MIN_LIKELIHOOD))
            totals[index] += term
            self.presence_totals[index] += term

    def _add_absence(self, totals: List[float], object_id: str,
                     receptacle_id: str, t: int) -> None:
        """``absence_weight * log(1 - p_i(object at receptacle))``, skipped
        entirely when no particle claimed ``absence_threshold`` mass there.

        The skip test is the max over particles — one object set for every
        particle, chosen without reference to the current weights (module
        docstring).
        """
        masses = self._claimed_mass(object_id, receptacle_id, t)
        if max(masses) < self.absence_threshold:
            return
        for index, mass in enumerate(masses):
            term = self._absence_weight * math.log(
                max(1.0 - mass, _MIN_LIKELIHOOD))
            totals[index] += term
            self.absence_totals[index] += term

    def _apply_event(self, log_likelihoods: Sequence[float], t: int) -> None:
        """Temper by ``decay``, add the event, renormalize (subtracting the
        max — a uniform shift, so it leaves every weight gap untouched
        under the next tempering step too)."""
        # Confidence study knobs (env): HYPOTHESIS_DECAY overrides the per-event
        # forgetting factor; HYPOTHESIS_LL_TEMPER scales each event's log
        # likelihood (a patrol pass is ~35 events on the same instant).
        decay = float(_os.environ.get("HYPOTHESIS_DECAY", self._decay))
        temper = float(_os.environ.get("HYPOTHESIS_LL_TEMPER", "1.0"))
        self._log_weights = [decay * lw + temper * d for lw, d
                             in zip(self._log_weights, log_likelihoods)]
        top = max(self._log_weights)
        self._log_weights = [lw - top for lw in self._log_weights]
        self.ess_history.append((t, self.effective_sample_size))

    # ----------------------------------------------------------- lifecycle

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        for particle in self._particles:
            particle.reset(context)
        self._log_weights = [0.0] * len(self._particles)
        self.ess_history = []
        self.presence_totals = [0.0] * len(self._particles)
        self.absence_totals = [0.0] * len(self._particles)

    def _register_object(self, object_id: str, object_class: str) -> None:
        for particle in self._particles:
            particle.ensure_object(object_id, object_class)

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        # Register first (an object the mixture has never heard of has no
        # forecast to score), then weigh the whole event, then let it
        # reach the particles.
        if isinstance(evidence, Observation):
            self.ensure_object(evidence.object_id, evidence.object_class)
        else:
            for obj in evidence.contents:
                self.ensure_object(obj, evidence.object_classes.get(obj, ""))
        self._apply_event(self._event_log_likelihoods(evidence), evidence.t)
        super().update(evidence)
        for particle in self._particles:
            particle.update(evidence)

    # ---------------------------------------------------------- prediction

    def particle_distributions(self, object_id: str,
                               t: int) -> List[Dict[str, float]]:
        """Every particle's current predictive distribution for
        ``object_id`` at ``t``, in particle order, without perturbing any
        generator. The disambiguation policy reads this."""
        return [dict(p.predict_readonly(object_id, t).distribution)
                for p in self._particles]

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        mixed: Dict[str, float] = {}
        for weight, particle in zip(self.weights, self._particles):
            for rec, p in particle.predict_readonly(
                    object_id, t).distribution.items():
                mixed[rec] = mixed.get(rec, 0.0) + weight * p
        top = max(mixed.values())
        tied = sorted(r for r, p in mixed.items() if p == top)
        return Prediction(distribution=mixed, argmax=tied[0])

    def predict_readonly(self, object_id: str, t: int) -> Prediction:
        """Base behaviour, extended to restore every particle's generator
        as well as the mixture's own."""
        states = [p._rng.getstate() for p in self._particles]
        try:
            return super().predict_readonly(object_id, t)
        finally:
            for particle, state in zip(self._particles, states):
                particle._rng.setstate(state)

    def last_prediction_diagnostics(self) -> Union[Dict[str, float], None]:
        return {"effective_sample_size": self.effective_sample_size}
