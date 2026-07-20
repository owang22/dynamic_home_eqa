"""The ONE shared belief filter. Every classical arm runs through this class;
arms differ only in the RateModel they plug in (core architecture requirement).

Process model — inhomogeneous "random-refresh" Markov jump process (the
continuous-time generalization of the two-state telegraph process): an object
in receptacle r keeps it until a refresh event (Poisson, rate lambda(obj, r, t));
at a refresh the state is redrawn from the time-varying occupancy distribution
pi(obj, . , t). Discretized on a step_min grid, the forward propagation is

    b <- b * exp(-lambda*dt)  +  (sum_r b_r * (1-exp(-lambda_r*dt))) * pi(t)

which for two states with constant parameters reproduces the analytic telegraph
solution  q(t) = pi + (q0 - pi) e^{-lambda t}  (unit-tested).

State representation (config flag, both implemented per the brief):
  categorical  R+1-state chain per object; forward algorithm of a CT-HMM.
               Exact normalization. Preferred.
  per_edge     independent binary present/absent recursion per (object,
               receptacle) edge — what FreMEn / persistence-filter methods
               natively do — renormalized across receptacles at query time.
               The renormalization is an APPROXIMATION; the filter records
               `renorm_mass` (pre-normalization total) so its cost is
               measured, not assumed (W5).

Observation model — noiseless snapshots in the current banks, but the
likelihood is pluggable via `fn_rate` (false-negative probability, default 0)
so noise can be added later without touching any arm.

References read for the formulation (reimplemented, not depended on):
  - FreMEn (Krajnik et al., T-RO 2017) + github.com/gestom/fremen — spectral
    occupancy feeding an exponential-persistence predictor.
  - Persistence Filter (Rosen et al.) github.com/david-m-rosen/Persistence-Filter
    — survival-function view of the stay probability (our exp(-int lambda)).
"""
from __future__ import annotations

from typing import Optional, Protocol, Sequence

import numpy as np


class RateModel(Protocol):
    """Pluggable parameter estimator. Arms implement exactly this interface."""

    def fit(self, observation_history: list[dict]) -> None: ...

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        """Prior occupancy P(object at receptacle) at minute t."""
        ...

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        """Refresh (leave) rate per minute while at receptacle_id. Optional
        for arms that are purely occupancy-based; the filter treats a missing
        implementation as rate 0 (C0)."""
        ...


class Filter:
    """Shared Bayes filter for one object. predict(t) -> dict[recep_label, p];
    update((t, receptacle_label)) -> conditions the posterior. Chronological
    use: updates must be fed in time order."""

    def __init__(self, rate_model: RateModel, candidates: Sequence[str],
                 object_id: str, mode: str = "categorical",
                 fn_rate: float = 0.0, step_min: int = 15) -> None:
        assert mode in ("categorical", "per_edge"), mode
        self.rm = rate_model
        self.object_id = object_id
        self.cands = list(candidates)             # includes "elsewhere"
        self.idx = {c: i for i, c in enumerate(self.cands)}
        self.mode = mode
        self.fn_rate = float(fn_rate)
        self.step = int(step_min)
        self.t: Optional[int] = None              # current belief timestamp
        self.b: Optional[np.ndarray] = None       # belief (categorical) or
                                                  # per-edge marginals (per_edge)
        self.renorm_mass: float = 1.0             # per_edge: last pre-norm mass

    # ── initialization ───────────────────────────────────────────────────────
    def reset(self, t0: int, prior: Optional[np.ndarray] = None) -> None:
        n = len(self.cands)
        if prior is not None:
            b = np.asarray(prior, dtype=float)
        else:
            b = np.array([max(1e-9, self.rm.occupancy(self.object_id, c, t0))
                          for c in self.cands])
        self.b = b / b.sum() if self.mode == "categorical" else np.clip(b, 1e-9, 1.0)
        self.t = int(t0)

    # ── propagation (the shared prediction path) ─────────────────────────────
    def _rates(self, t: int) -> np.ndarray:
        get = getattr(self.rm, "rate", None)
        if get is None:
            return np.zeros(len(self.cands))
        return np.array([max(0.0, get(self.object_id, c, t)) for c in self.cands])

    def _pi(self, t: int) -> np.ndarray:
        pi = np.array([max(1e-9, self.rm.occupancy(self.object_id, c, t))
                       for c in self.cands])
        return pi / pi.sum()

    def _propagate_to(self, t: int) -> None:
        assert self.t is not None, "reset() first"
        while self.t < t:
            dt = min(self.step, t - self.t)
            lam = self._rates(self.t)
            stay = np.exp(-lam * dt)
            if self.mode == "categorical":
                pi = self._pi(self.t)
                leaving = float(((1.0 - stay) * self.b).sum())
                self.b = self.b * stay + leaving * pi
                self.b /= self.b.sum()
            else:  # per_edge: independent binary recursion toward edge occupancy
                pi_edge = np.array([max(1e-9, self.rm.occupancy(self.object_id, c, self.t))
                                    for c in self.cands])
                self.b = self.b * stay + (1.0 - stay) * np.clip(pi_edge, 0, 1)
            self.t += dt

    # ── the two-call public interface (brief requirement) ────────────────────
    def predict(self, t: int) -> dict[str, float]:
        """Distribution over receptacles at time t (does not mutate state)."""
        saved_t, saved_b = self.t, None if self.b is None else self.b.copy()
        if self.t is None:
            self.reset(t)
        self._propagate_to(t)
        b = self.b.copy()
        if self.mode == "per_edge":
            self.renorm_mass = float(b.sum())     # W5: log approximation cost
            b = b / max(1e-12, b.sum())
        out = {c: float(b[i]) for i, c in enumerate(self.cands)}
        self.t, self.b = saved_t, saved_b         # predict is side-effect free
        return out

    def update(self, observation: tuple[int, str]) -> None:
        """Condition on a snapshot (t, receptacle_label). With fn_rate=0 this
        collapses the belief to the observed receptacle (noiseless banks)."""
        t, recep = observation
        if self.t is None:
            self.reset(t)
        self._propagate_to(t)
        like = np.full(len(self.cands), self.fn_rate)   # P(z=recep | state!=recep)
        like[self.idx[recep]] = 1.0 - self.fn_rate       # P(z=recep | state=recep)
        if self.fn_rate == 0.0:
            like = (np.arange(len(self.cands)) == self.idx[recep]).astype(float)
        self.b = self.b * like
        if self.mode == "categorical":
            s = self.b.sum()
            self.b = self.b / s if s > 0 else np.full(len(self.cands), 1.0 / len(self.cands))
        else:
            self.b = np.clip(self.b, 1e-9, 1.0)
            self.b[self.idx[recep]] = 1.0 - self.fn_rate if self.fn_rate else 1.0


def uniform_belief(candidates: Sequence[str]) -> dict[str, float]:
    """The mandated explicit uninformative prior for D=0 / no-history cells."""
    p = 1.0 / len(candidates)
    return {c: p for c in candidates}
