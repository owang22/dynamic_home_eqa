"""Belief: a weighted mixture over existing zoo beliefs, each treated as
one hypothesis about the household's dynamics.

Every particle is a full belief model from the registry, consuming the
identical evidence stream. The mixture holds one log weight per particle,
uniform at reset, and updates it at SIGHTING time: before a positive
sighting of object O at receptacle R is applied, each particle is asked
for its current distribution over O's location, and its log weight gains
``log(p_particle(R))`` — particles that kept predicting where things
actually turn up gain weight, particles that did not lose it. The
sighting is then applied to every particle as normal. A room-visit sense
result scores one such term per object in its contents; its empty looks
update the particles' evidence but never the weights (an absence is
consistent with many hypotheses at once and its likelihood is not what
the weighting scheme is calibrated on).

The predict-before-update hook this needs lives HERE, inside
:meth:`update`, not in the harness: every consumer (harness, passive
evaluation, replay, traces) delivers evidence through ``update``, so
implementing the hook inside it covers them all without widening any
shared contract.

Weights are tempered by a forgetting factor applied per weighted
sighting: ``log_w = decay * log_w + log(p)``. At ``decay = 1`` the
weights are the exact Bayesian posterior over a fixed hypothesis set and
collapse onto one particle within days; below 1 old evidence fades and
the mixture can re-open when the household changes regime. Normalization
is in log space; the effective sample size ``1 / sum(w_i^2)`` is tracked
after every weight update (``ess_history``).

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
import random
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from baselines.beliefs.base import DEFAULT_FLOOR_MASS, BeliefModel
from baselines.types import (EpisodeContext, Observation, Prediction,
                             SenseResult)

DEFAULT_DECAY = 0.95
"""Forgetting factor on log weights, applied per weighted sighting. The
steady-state log-weight gap between two particles scales as
``1 / (1 - decay)`` times the per-sighting likelihood gap, so on the
passive diet (roughly 30-60 weighted sightings per day) 1.0 and 0.98
both collapse onto one particle (ESS 1.00 / 1.03 on the gate-pass
fixture) while 0.95 keeps a clear leader without degeneracy (ESS 2.4,
leader weight 0.57). 1.0 is the pure posterior (collapses; see the
tests)."""

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

_MIN_LIKELIHOOD = 1e-12
"""Floor on a particle's per-sighting likelihood before the log, so a
degenerate zero-floor particle cannot send a weight to -inf."""


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
                 floor_mass: float = 0.0,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        if not 0.0 < decay <= 1.0:
            raise ValueError(
                f"HypothesisMixture: decay {decay} outside (0, 1]")
        from baselines.registry import build_registered_belief
        specs = [dict(s) for s in (particle_specs if particle_specs is not None
                                   else DEFAULT_PARTICLE_SPECS)]
        if not specs:
            raise ValueError("HypothesisMixture: particle list is empty")
        self._decay = float(decay)
        self._particles: List[BeliefModel] = [
            build_registered_belief(
                spec, random.Random(rng.getrandbits(64)))
            for spec in specs]
        self._log_weights: List[float] = [0.0] * len(specs)
        self.ess_history: List[Tuple[int, float]] = []

    @property
    def name(self) -> str:
        return (f"HypothesisMixture(k={len(self._particles)},"
                f"decay={self._decay:g})")

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

    def _weigh_sighting(self, object_id: str, receptacle_id: str,
                        t: int) -> None:
        """The predict-before-update step: score every particle on the
        sighting about to be applied, then temper and renormalize (by
        subtracting the max; the ``weights`` property finishes the job)."""
        for index, particle in enumerate(self._particles):
            p = particle.predict_readonly(
                object_id, t).distribution.get(receptacle_id, 0.0)
            self._log_weights[index] = (
                self._decay * self._log_weights[index]
                + math.log(max(p, _MIN_LIKELIHOOD)))
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

    def _register_object(self, object_id: str, object_class: str) -> None:
        for particle in self._particles:
            particle.ensure_object(object_id, object_class)

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        # Weigh BEFORE any particle sees the evidence, one term per
        # positive sighting; empty looks skip the weighting (module
        # docstring) but still reach every particle below.
        if isinstance(evidence, Observation):
            self.ensure_object(evidence.object_id, evidence.object_class)
            self._weigh_sighting(evidence.object_id, evidence.receptacle_id,
                                 evidence.t)
        else:
            for obj in evidence.contents:
                self.ensure_object(obj, evidence.object_classes.get(obj, ""))
                self._weigh_sighting(obj, evidence.receptacle_id, evidence.t)
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
