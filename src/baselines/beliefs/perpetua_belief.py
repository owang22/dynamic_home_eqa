"""Beliefs: Perpetua and Perpetua* over (object, receptacle) edges.

Each receptacle an object has ever been sighted at is one binary
feature, "object present at that receptacle", tracked by its own
persistence/emergence machinery from :mod:`perpetua_filters`:

* :class:`PerpetuaBelief` -- the state machine of arXiv 2507.18808
  (``Perpetua.py`` in montrealrobotics/perpetua-code);
* :class:`PerpetuaStarBelief` -- the Bayesian model selection of
  arXiv 2605.00121 (equations 2-15, no public code).

**Edge streams.** A sighting of object O at receptacle R at time t is
``y = 1`` for edge (O, R) and ``y = 0`` for every other edge of O. A sense
of R at t whose contents lack O is ``y = 0`` for edge (O, R) if that edge
exists. A first sighting at a new receptacle creates the edge, initialised
at that instant; nothing is fed retroactively. Negative evidence enters
the filters directly, so the base class's exclusion machinery is switched
off here (:meth:`_PerpetuaBase._apply_exclusions` is the identity) to
avoid counting it twice; the base's sighting bookkeeping and its
sighting-at-the-prediction-instant short circuit are kept.

**Online fitting.** The original pipeline fits the survival mixtures
offline by EM on a training split. Here every edge's observation stream
is cut into training segments at the observed flips (see
:func:`perpetua_filters.extract_segments`), and the mixtures are refit by
EM once per simulated day, at the first update after a day boundary,
for edges with at least ``min_segments`` completed segments per filter
kind; other edges use a single-component fallback prior. On a refit each
mixture is re-initialised at its existing reset time with the new prior
and the observations since then are replayed, so the switching history
is preserved and the recursion is consistent with the new parameters.
Fallback use is counted per prediction (:meth:`fallback_summary`), reset
events are recorded (:attr:`reset_events`), and per-edge segment counts
are reported (:meth:`edge_summary`).

**Prediction.** ``p_k`` is edge k's presence belief; the distribution is
``p_k / sum(p_k)`` over the object's support, uniform over the support
when the sum is ~0, and uniform over all receptacles for a never-observed
object (base class). Argmax ties prefer the last-sighted receptacle,
then the lexicographically first. No randomness anywhere.

**Perpetua\\* switching prior** ``f(t)`` (the prior probability that the
object is present at the edge's receptacle at time t):
``time_of_day_histogram`` -- the timetable model's shape: among the
object's sightings in t's time-of-day bin, decayed with the panel's
24 h count half-life, the fraction that were at this receptacle, falling
back to the whole decayed history when the bin is empty, with a
pseudo-count of ``prior_pseudocount`` (1) on both sides. Without the
smoothing a freshly created edge's prior is exactly 1 (its only sighting
is the one that created it) and the posterior-triggered reset flips the
edge to the emergence model at creation;
``flat`` -- 0.5, the ablation that isolates the survival machinery;
``fremen`` -- a Fourier prior, interface stubbed, not implemented.

All times are seconds since episode start; a day is 86 400 s.
"""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Tuple, Union

from baselines.beliefs import perpetua_filters as pfl
from baselines.beliefs.base import BeliefModel
from baselines.types import (DAY_SECONDS, Observation, Prediction,
                             SenseResult)

logger = logging.getLogger(__name__)

HOURS_PER_DAY = 24
SWITCHING_PRIORS = ("time_of_day_histogram", "flat", "fremen")
PRIOR_CLIP = 1e-6
"""The switching prior is kept inside ``[PRIOR_CLIP, 1 - PRIOR_CLIP]`` so
neither model can be ruled out for good by a log of zero."""


@dataclass(frozen=True)
class PerpetuaConfig:
    """Perpetua hyperparameters. Defaults: ``p_m``/``p_f`` from
    ``examples/perpetua.py`` (the papers estimate them from dataset
    statistics; ours is noise-free, and the filter cannot take 0);
    ``delta_low``/``delta_high``/``eps``/``num_steps`` from the paper
    and the reference defaults; EM settings from ``examples/room.py``."""

    family: str = "lognormal"
    p_m: float = 0.01
    p_f: float = 0.01
    k_range: Tuple[int, ...] = (1, 2, 3)
    em_max_iter: int = 250
    em_tol: float = 1e-4
    prune_threshold: float = 0.01
    refit_every_days: int = 1
    min_segments: int = 2
    fallback_median_h: float = 12.0
    delta_low: float = 0.05
    delta_high: float = 0.95
    num_steps: int = 10
    eps: float = 0.1

    def __post_init__(self) -> None:
        if self.family not in pfl.FAMILIES:
            raise ValueError(f"{type(self).__name__}: family {self.family!r} "
                             f"not in {pfl.FAMILIES}")
        for name in ("p_m", "p_f"):
            v = getattr(self, name)
            if not 0.0 < v < 1.0:
                raise ValueError(f"{type(self).__name__}: {name} {v} "
                                 f"must be in (0, 1)")
        if not self.k_range or min(self.k_range) < 1:
            raise ValueError(f"{type(self).__name__}: k_range {self.k_range}")
        if self.min_segments < 1 or self.refit_every_days < 1:
            raise ValueError(f"{type(self).__name__}: min_segments and "
                             f"refit_every_days must be >= 1")
        if self.fallback_median_h <= 0:
            raise ValueError(f"{type(self).__name__}: fallback_median_h "
                             f"{self.fallback_median_h} must be > 0")
        if not 0.0 <= self.eps <= 1.0:
            raise ValueError(f"{type(self).__name__}: eps {self.eps}")

    def _check_perpetua(self) -> None:
        if not 0.0 <= self.delta_low <= self.delta_high <= 1.0:
            raise ValueError(f"PerpetuaConfig: need 0 <= delta_low <= "
                             f"delta_high <= 1, got {self.delta_low}, "
                             f"{self.delta_high}")
        if self.num_steps < 1:
            raise ValueError(f"PerpetuaConfig: num_steps {self.num_steps}")


@dataclass(frozen=True)
class PerpetuaStarConfig(PerpetuaConfig):
    """Perpetua* hyperparameters. ``gamma`` and ``alpha0_per_h`` are the
    Appendix B.3 values of arXiv 2605.00121 (0.99; 0.01 per hour, the
    paper's 1 h time unit, so the likelihood is nearly flattened after
    ~300 h). ``reset_mode`` selects the reset rule -- ``belief`` (default),
    ``model_posterior`` (diagnostic) or ``none`` (the literal fixed-origin
    recursion, diagnostic); see :class:`perpetua_filters.PerpetuaStarState`
    for the deviation from the paper this encodes."""

    gamma: float = 0.99
    alpha0_per_h: float = 0.01
    switching_prior: str = "time_of_day_histogram"
    prior_bin_hours: int = 1
    prior_half_life_h: float = 24.0
    prior_pseudocount: float = 1.0
    reset_mode: str = "belief"

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 0.0 <= self.gamma <= 1.0:
            raise ValueError(f"PerpetuaStarConfig: gamma {self.gamma}")
        if self.alpha0_per_h < 0:
            raise ValueError(f"PerpetuaStarConfig: alpha0_per_h "
                             f"{self.alpha0_per_h} must be >= 0")
        if self.switching_prior not in SWITCHING_PRIORS:
            raise ValueError(f"PerpetuaStarConfig: switching_prior "
                             f"{self.switching_prior!r} not in "
                             f"{SWITCHING_PRIORS}")
        if self.switching_prior == "fremen":
            raise NotImplementedError(
                "PerpetuaStarConfig: the fremen switching prior is a stub; "
                "only its interface exists")
        if (self.prior_bin_hours <= 0
                or HOURS_PER_DAY % self.prior_bin_hours != 0):
            raise ValueError(f"PerpetuaStarConfig: prior_bin_hours must "
                             f"divide {HOURS_PER_DAY}")
        if self.prior_half_life_h <= 0:
            raise ValueError(f"PerpetuaStarConfig: prior_half_life_h "
                             f"{self.prior_half_life_h} must be > 0")
        if self.prior_pseudocount < 0:
            raise ValueError(f"PerpetuaStarConfig: prior_pseudocount "
                             f"{self.prior_pseudocount} must be >= 0")
        if self.reset_mode not in pfl.RESET_MODES:
            raise ValueError(f"PerpetuaStarConfig: reset_mode "
                             f"{self.reset_mode!r} not in {pfl.RESET_MODES}")


@dataclass
class Edge:
    """One (object, receptacle) feature and everything learned about it."""

    object_id: str
    receptacle_id: str
    t0: int
    machine: Union[pfl.PerpetuaState, pfl.PerpetuaStarState]
    times: List[float] = field(default_factory=list)
    ys: List[bool] = field(default_factory=list)
    last_sighting_t: int = -1
    pf_fallback: bool = True
    ef_fallback: bool = True
    n_persistence_segments: int = 0
    n_emergence_segments: int = 0
    n_resets: int = 0
    warm_pf: Dict[int, pfl.SurvivalMixture] = field(default_factory=dict)
    warm_ef: Dict[int, pfl.SurvivalMixture] = field(default_factory=dict)
    n_events_at_fit: int = -1

    @property
    def any_fallback(self) -> bool:
        return self.pf_fallback or self.ef_fallback


class _PerpetuaBase(BeliefModel):
    """Shared edge-stream construction, online EM, prediction assembly
    and diagnostics; subclasses supply the per-edge machine."""

    def __init__(self, rng: random.Random, config: PerpetuaConfig,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._cfg = config
        self._edges: Dict[str, Dict[str, Edge]] = {}
        self._last_refit_day = -1
        self._reset_events: List[Dict[str, Any]] = []
        self._fallback_by_day: Dict[int, List[int]] = {}
        self._last_diag: Optional[Dict[str, float]] = None
        self._n_refits = 0
        self._fallback_prior = pfl.single_component_prior(
            config.family, config.fallback_median_h * 3600.0)

    # ------------------------------------------------------------ hooks

    def _new_machine(self, t0: float, pf_prior: pfl.SurvivalMixture,
                     ef_prior: pfl.SurvivalMixture
                     ) -> Union[pfl.PerpetuaState, pfl.PerpetuaStarState]:
        raise NotImplementedError

    def _edge_update(self, edge: Edge, y: bool, t: int
                     ) -> List[Tuple[float, str]]:
        raise NotImplementedError

    def _edge_belief(self, edge: Edge, t: int) -> float:
        raise NotImplementedError

    def _rebuild_machine(self, edge: Edge, pf_prior: pfl.SurvivalMixture,
                         ef_prior: pfl.SurvivalMixture) -> None:
        raise NotImplementedError

    # ----------------------------------------------------------- API

    def reset(self, context: Any) -> None:
        super().reset(context)
        self._edges = {}
        self._last_refit_day = -1
        self._reset_events = []
        self._fallback_by_day = {}
        self._last_diag = None
        self._n_refits = 0

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        super().update(evidence)          # sighting bookkeeping (base)
        day = evidence.t // DAY_SECONDS
        if (self._last_refit_day < 0
                or day - self._last_refit_day >= self._cfg.refit_every_days):
            self._refit_all()
            self._last_refit_day = day
        if isinstance(evidence, Observation):
            self._sighting(evidence.object_id, evidence.receptacle_id,
                           evidence.t)
            return
        if self._context is None:
            raise RuntimeError(f"{self.name}: update() before reset()")
        present = set(evidence.contents)
        for obj in evidence.contents:
            self._sighting(obj, evidence.receptacle_id, evidence.t)
        for obj in sorted(self._context.object_classes):
            if obj in present:
                continue
            edge = self._edges.get(obj, {}).get(evidence.receptacle_id)
            if edge is not None:
                self._observe(edge, False, evidence.t)

    def _apply_exclusions(self, object_id: str, t: int,
                          base: Prediction) -> Prediction:
        """Identity: negative evidence already went into the edge filters
        as ``y = 0`` observations, so re-zeroing excluded receptacles here
        would count it twice (decided 2026-09-03)."""
        return base

    # --------------------------------------------------- edge streams

    def _sighting(self, obj: str, rec: str, t: int) -> None:
        edges = self._edges.setdefault(obj, {})
        edge = edges.get(rec)
        if edge is None:
            edge = Edge(object_id=obj, receptacle_id=rec, t0=t,
                        machine=self._new_machine(float(t), self._fallback_prior,
                                                  self._fallback_prior))
            edges[rec] = edge
        edge.last_sighting_t = max(edge.last_sighting_t, t)
        for other, other_edge in sorted(edges.items()):
            self._observe(other_edge, other == rec, t)

    def _observe(self, edge: Edge, y: bool, t: int) -> None:
        edge.times.append(float(t))
        edge.ys.append(bool(y))
        for when, direction in self._edge_update(edge, y, t):
            edge.n_resets += 1
            self._reset_events.append({
                "object_id": edge.object_id, "receptacle_id": edge.receptacle_id,
                "t": when, "direction": direction})
            logger.debug("%s: reset %s/%s at t=%.0f %s", self.name,
                         edge.object_id, edge.receptacle_id, when, direction)

    # ------------------------------------------------------ online EM

    def _refit_all(self) -> None:
        cfg = self._cfg
        self._n_refits += 1
        for edges in self._edges.values():
            for edge in edges.values():
                if len(edge.times) == edge.n_events_at_fit:
                    continue          # same data as the last fit: same fit
                edge.n_events_at_fit = len(edge.times)
                pers, emer = pfl.extract_segments(edge.times, edge.ys)
                edge.n_persistence_segments = len(pers)
                edge.n_emergence_segments = len(emer)
                pf_prior, pf_fb = self._fit(pers, "persistence", edge.warm_pf)
                ef_prior, ef_fb = self._fit(emer, "emergence", edge.warm_ef)
                changed = (pf_fb != edge.pf_fallback or ef_fb != edge.ef_fallback
                           or not pf_fb or not ef_fb)
                edge.pf_fallback, edge.ef_fallback = pf_fb, ef_fb
                if changed:
                    self._rebuild_machine(edge, pf_prior, ef_prior)

    def _fit(self, segments: List[pfl.Segment], kind: str,
             warm: Dict[int, pfl.SurvivalMixture]
             ) -> Tuple[pfl.SurvivalMixture, bool]:
        cfg = self._cfg
        if len(segments) < cfg.min_segments:
            return self._fallback_prior, True
        fit = pfl.select_mixture(segments, kind, cfg.family, cfg.p_m, cfg.p_f,
                                 k_range=cfg.k_range, max_iter=cfg.em_max_iter,
                                 tol=cfg.em_tol,
                                 prune_threshold=cfg.prune_threshold,
                                 warm_starts=warm)
        warm.clear()
        warm.update(fit.per_k)
        return fit.mixture, False

    def _events_since(self, edge: Edge, t0: float) -> List[Tuple[float, bool]]:
        return [(t, y) for t, y in zip(edge.times, edge.ys) if t >= t0]

    # ------------------------------------------------------ prediction

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        """Never-observed objects take the base class's uniform fallback
        (its only use of the seeded generator); everything else is
        assembled from the edge beliefs, deterministically."""
        edges = self._edges.get(object_id, {})
        if not history or not edges:
            return self._uniform()
        beliefs = {rec: self._edge_belief(edge, t)
                   for rec, edge in sorted(edges.items())}
        total = sum(beliefs.values())
        n_fallback = sum(1 for e in edges.values() if e.any_fallback)
        day = int(t // DAY_SECONDS)
        counts = self._fallback_by_day.setdefault(day, [0, 0, 0, 0])
        counts[0] += 1
        counts[1] += int(n_fallback > 0)
        counts[2] += len(edges)
        counts[3] += n_fallback
        self._last_diag = {"max_edge_belief": max(beliefs.values()),
                           "sum_edge_belief": total, "n_edges": len(edges),
                           "n_fallback_edges": n_fallback}
        if total < 1e-12:
            dist = {rec: 1.0 / len(edges) for rec in beliefs}
        else:
            dist = {rec: p / total for rec, p in beliefs.items()}
        top = max(dist.values())
        tied = [rec for rec, p in dist.items() if p == top]
        last_seen = {rec: edges[rec].last_sighting_t for rec in tied}
        newest = max(last_seen.values())
        argmax = min(rec for rec in tied if last_seen[rec] == newest)
        return Prediction(distribution=dist, argmax=argmax)

    # ------------------------------------------------------ diagnostics

    def last_prediction_diagnostics(self) -> Optional[Dict[str, float]]:
        """Pieces of the last :meth:`predict` that a caller may log: the
        largest edge presence belief (the absence signal), their sum, and
        how many edges were on the fallback prior."""
        return self._last_diag

    @property
    def reset_events(self) -> List[Dict[str, Any]]:
        """Every filter reset so far: object, receptacle, time, direction."""
        return list(self._reset_events)

    def fallback_summary(self) -> Dict[int, Dict[str, int]]:
        """Per query day: predictions made, predictions with any fallback
        edge, edge beliefs computed, edge beliefs from a fallback prior."""
        return {day: {"n_predictions": c[0], "n_predictions_any_fallback": c[1],
                      "n_edge_beliefs": c[2], "n_fallback_edge_beliefs": c[3]}
                for day, c in sorted(self._fallback_by_day.items())}

    def edge_summary(self) -> List[Dict[str, Any]]:
        """Per edge: event count, completed segments per kind, fitted
        mixture sizes, fallback flags, reset count."""
        rows = []
        for obj, edges in sorted(self._edges.items()):
            for rec, e in sorted(edges.items()):
                rows.append({
                    "object_id": obj, "receptacle_id": rec, "t0": e.t0,
                    "n_events": len(e.times),
                    "n_sightings": sum(e.ys),
                    "n_persistence_segments": e.n_persistence_segments,
                    "n_emergence_segments": e.n_emergence_segments,
                    "pf_components": e.machine.pf.n_components,
                    "ef_components": e.machine.ef.n_components,
                    "pf_fallback": e.pf_fallback, "ef_fallback": e.ef_fallback,
                    "n_resets": e.n_resets})
        return rows

    @property
    def n_refits(self) -> int:
        return self._n_refits


class PerpetuaBelief(_PerpetuaBase):
    """Perpetua: mixtures of persistence and emergence filters coupled by
    the belief-threshold state machine, one machine per edge."""

    def __init__(self, rng: random.Random, config: PerpetuaConfig,
                 exclusion_floor: float = 0.0) -> None:
        config._check_perpetua()
        super().__init__(rng, config, exclusion_floor=exclusion_floor)

    @property
    def name(self) -> str:
        c = self._cfg
        return (f"Perpetua({c.family},K<={max(c.k_range)},"
                f"pm={c.p_m:g},steps={c.num_steps})")

    def _new_machine(self, t0: float, pf_prior: pfl.SurvivalMixture,
                     ef_prior: pfl.SurvivalMixture) -> pfl.PerpetuaState:
        c = self._cfg
        return pfl.PerpetuaState.create(pf_prior, ef_prior, t0, c.delta_low,
                                        c.delta_high, c.num_steps, c.eps)

    def _edge_update(self, edge: Edge, y: bool, t: int
                     ) -> List[Tuple[float, str]]:
        m = edge.machine
        assert isinstance(m, pfl.PerpetuaState)
        return m.update(y, float(t), self._cfg.p_m, self._cfg.p_f)

    def _edge_belief(self, edge: Edge, t: int) -> float:
        m = edge.machine
        assert isinstance(m, pfl.PerpetuaState)
        return float(m.predict([max(float(t), m.last_t)])[0])

    def _rebuild_machine(self, edge: Edge, pf_prior: pfl.SurvivalMixture,
                         ef_prior: pfl.SurvivalMixture) -> None:
        old = edge.machine
        assert isinstance(old, pfl.PerpetuaState)
        c = self._cfg
        pf = pfl.FilterState.create(pf_prior, old.pf.t0)
        for t, y in self._events_since(edge, old.pf.t0):
            pf = pfl.persistence_update(pf, y, t, c.p_m, c.p_f)
        ef = pfl.FilterState.create(ef_prior, old.ef.t0)
        for t, y in self._events_since(edge, old.ef.t0):
            ef = pfl.emergence_update(ef, y, t, c.p_m, c.p_f)
        edge.machine = replace(old, pf=pf, ef=ef)


class PerpetuaStarBelief(_PerpetuaBase):
    """Perpetua*: both mixtures updated on every observation, Bayesian
    model selection with an annealed likelihood and a switching prior."""

    def __init__(self, rng: random.Random, config: PerpetuaStarConfig,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, config, exclusion_floor=exclusion_floor)
        self._scfg = config

    @property
    def name(self) -> str:
        c = self._scfg
        tag = {"time_of_day_histogram": "", "flat": "Flat",
               "fremen": "Fremen"}[c.switching_prior]
        variant = "" if c.reset_mode == "belief" else f",reset={c.reset_mode}"
        return (f"PerpetuaStar{tag}({c.family},K<={max(c.k_range)},"
                f"pm={c.p_m:g},a0={c.alpha0_per_h:g}/h,g={c.gamma:g}{variant})")

    def _new_machine(self, t0: float, pf_prior: pfl.SurvivalMixture,
                     ef_prior: pfl.SurvivalMixture) -> pfl.PerpetuaStarState:
        c = self._scfg
        return pfl.PerpetuaStarState.create(
            pf_prior, ef_prior, t0, gamma=c.gamma,
            alpha0=c.alpha0_per_h / 3600.0, eps=c.eps,
            reset_mode=c.reset_mode)

    def _edge_update(self, edge: Edge, y: bool, t: int
                     ) -> List[Tuple[float, str]]:
        m = edge.machine
        assert isinstance(m, pfl.PerpetuaStarState)
        f = self.switching_prior(edge.object_id, edge.receptacle_id, t)
        return m.update(y, float(t), self._cfg.p_m, self._cfg.p_f, f)

    def _edge_belief(self, edge: Edge, t: int) -> float:
        m = edge.machine
        assert isinstance(m, pfl.PerpetuaStarState)
        f = self.switching_prior(edge.object_id, edge.receptacle_id, t)
        return m.predict(max(float(t), m.last_t), f)[0]

    def _rebuild_machine(self, edge: Edge, pf_prior: pfl.SurvivalMixture,
                         ef_prior: pfl.SurvivalMixture) -> None:
        old = edge.machine
        assert isinstance(old, pfl.PerpetuaStarState)
        c = self._scfg
        pf = pfl.FilterState.create(pf_prior, old.pf.t0)
        for t, y in self._events_since(edge, old.pf.t0):
            pf = pfl.persistence_update(pf, y, t, c.p_m, c.p_f, c.gamma)
        ef = pfl.FilterState.create(ef_prior, old.ef.t0)
        for t, y in self._events_since(edge, old.ef.t0):
            ef = pfl.emergence_update(ef, y, t, c.p_m, c.p_f, c.gamma)
        edge.machine = replace(old, pf=pf, ef=ef)

    def switching_prior(self, obj: str, rec: str, t: int) -> float:
        """``f(t)``: prior probability that ``obj`` is at ``rec`` at ``t``
        (see the module docstring), clipped away from 0 and 1."""
        c = self._scfg
        if c.switching_prior == "flat":
            return 0.5
        if c.switching_prior == "fremen":
            raise NotImplementedError("fremen switching prior is a stub")
        history = self._history.get(obj, [])
        if not history:
            return 0.5
        bin_size = c.prior_bin_hours * 3600
        query_bin = (t % DAY_SECONDS) // bin_size
        in_bin = [(ot, r) for ot, r in history
                  if (ot % DAY_SECONDS) // bin_size == query_bin]
        pool = in_bin if in_bin else history
        counts = self._weighted_counts(pool, t, c.prior_half_life_h * 3600.0)
        a = c.prior_pseudocount
        f = (counts.get(rec, 0.0) + a) / (sum(counts.values()) + 2 * a)
        return min(max(f, PRIOR_CLIP), 1.0 - PRIOR_CLIP)
