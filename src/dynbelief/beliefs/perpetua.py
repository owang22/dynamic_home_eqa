"""b3_perpetua_star — per-edge persistence+emergence mixture with a
time-varying switching prior f(t) (arXiv 2605.00121, implemented from the
brief's operational definition).

Model. For each (object o, receptacle r) edge, X_{o,r}(t) in {0,1} indicates
"o is in r". X follows a two-state Markov process whose transition hazards
are modulated by the shared switching prior f(t):

    leave (persistence loss)  1 -> 0 at rate  mu_or  * f(t)
    emerge                    0 -> 1 at rate  eta_or * f(t)

Closed-form recursion (paper eq. for the posterior mean; standard
time-inhomogeneous 2-state chain): with F(t0,t1) = ∫ f dt and
p_eq = eta / (mu + eta),

    p(t1) = p_eq + (p(t0) - p_eq) * exp( -(mu + eta) * F(t0, t1) )

which is exactly the persistence component (the exponential carrying the
last observation forward) plus the emergence component (relaxation toward
the equilibrium occupancy). No sampling, no numerical ODE.

Special cases the unit tests pin down:
  - pure persistence (f = 0, single component): F = 0, so p(t) stays frozen
    at the last observed value forever.
  - constant f = 1: p(t) = p_eq + (p0 - p_eq) e^{-(mu+eta)Δt}, hand-checkable.

Parameter estimation. Sufficient statistics come from consecutive
observation pairs of each object (the same pair stream every tier records):
for edge (o, r), a pair (t1,p1)->(t2,p2) contributes
    on-dwell  Δt and a leave event iff p1 == r and p2 != r,
    off-dwell Δt and an enter event iff p1 != r and p2 == r.
MLE hazards mu = leaves/on-dwell, eta = enters/off-dwell, hierarchically
smoothed toward the object's CLASS pooled rates (add-k pseudo-counts) so
sparse edges inherit class behaviour. Rates are re-fit lazily when new
pairs arrive; they survive reset() (routine knowledge).

predict(). Per-edge posteriors are advanced from their last anchor
(observation or reset) and then normalized across receptacles; leftover
mass is reserved for the ELSEWHERE slot:
    S = Σ_r p_r ;  S <= 1: elsewhere = 1 - S ;  S > 1: divide by S.
An observation of o at parent p anchors edge (o,p) at 1 and every other
edge of o at 0 (a parent observation is complete for that object). An
object never observed anchors every edge at its trained equilibrium at t0.

f(t) is swappable (`switching_prior` callable with .cumulative) so Stage 1's
offline schedule prior drops in alongside `fremen` and `constant`.
"""
from __future__ import annotations

import numpy as np

from dynbelief import ELSEWHERE_ID
from dynbelief.beliefs.base import _Common, object_class
from dynbelief.beliefs.fremen import SwitchingPrior, constant_prior

_SMOOTH_K = 0.5          # pseudo-events toward class rates
_DEFAULT_MU = 1.0 / 720  # 12h mean dwell when nothing is known
# Default emergence rate for a NEVER-OBSERVED edge is set at predict-time so
# that the total placed-equilibrium mass across all R receptacles is ~0.5
# (the other half stays on elsewhere/absent): an object with no learned
# affinity for a receptacle must not accumulate eta/(mu+eta) mass on every
# one of ~50 candidates — measured on the first gate run, that summed to
# S >> 1, normalization zeroed the elsewhere slot, and argmax landed on an
# arbitrary receptacle for every unobserved object (the exact population
# where "elsewhere" is the right call).
_DEFAULT_PLACED_EQ_TOTAL = 0.5
# Ablation toggle for the C2 occupancy pinning below (stage1b attribution
# runs flip it off to separate "fix changed the model" from "metric/sampling
# changed the measurement"). Always True in real runs.
_PIN_OCCUPANCY = True
# Only pin objects whose observed in-house fraction is at least this value.
# 0.0 pins everything — the stage1b ablation showed blanket pinning trades
# displaced accuracy for put-away calibration (0.388 -> 0.315 displaced),
# because scaling DOWN the placed budget of objects with real away-time makes
# their filter sticky on stale anchors. Restricting the fix to its motivating
# population (objects that almost never leave the house) keeps displaced
# accuracy at the unpinned level while cutting those objects' spurious
# elsewhere mass from ~0.35 to ~0.02 (stage1b C2 ablation, ep049w).
_PIN_MIN_PLACED_FRAC = 0.9


class B3PerpetuaStar(_Common):
    name = "b3_perpetua_star"

    def __init__(self, obj_class_of: dict[int, str],
                 switching_prior: SwitchingPrior | None = None) -> None:
        super().__init__()
        self.obj_class_of = obj_class_of
        self.f = switching_prior or constant_prior()
        self._rates: dict[tuple[int, int], tuple[float, float]] | None = None
        # per-object filter anchor: (t_anchor, edge posterior vector)
        self._anchor: dict[int, tuple[int, np.ndarray]] = {}

    # ── rate fitting ─────────────────────────────────────────────────────────
    def observe(self, t, obs) -> None:
        super().observe(t, obs)
        self._rates = None
        for obj, (parent, _s) in obs.items():
            v = np.zeros(self.n_candidates)
            if parent != ELSEWHERE_ID:
                v[parent] = 1.0
            self._anchor[obj] = (t, v)

    def _fit(self) -> None:
        # Edge stats keyed (obj, recep); class pools keyed (class, recep).
        # OFF-dwell is derived as (object's total observed time - on-dwell),
        # never accumulated only over pairs that touch the receptacle: an
        # edge's off-time is the whole timeline the object spent anywhere
        # else. The earlier per-pair accumulation undercounted off-time by
        # orders of magnitude (hours vs. days), inflating eta until every
        # historically-visited receptacle's equilibrium overtook a fresh
        # observation within hours — measured directly on the Stage-1 probe
        # (b3 0.47 vs b0 0.76 before this fix).
        edge = {}          # (obj, r) -> [on_dt, leaves, enters]
        cls_pool = {}      # (cls, r) -> [on_dt, leaves, enters]
        obj_total = {}     # obj -> observed dt
        cls_total = {}     # cls -> observed dt
        for obj, pairs in self.pair_stats.items():
            cls = self.obj_class_of.get(obj, "?")
            for (t1, p1, t2, p2) in pairs:
                dt = t2 - t1
                if dt <= 0:
                    continue
                obj_total[obj] = obj_total.get(obj, 0.0) + dt
                cls_total[cls] = cls_total.get(cls, 0.0) + dt
                e = edge.setdefault((obj, p1), [0.0, 0, 0])
                c = cls_pool.setdefault((cls, p1), [0.0, 0, 0])
                e[0] += dt; c[0] += dt
                if p2 != p1:
                    e[1] += 1; c[1] += 1
                    e2 = edge.setdefault((obj, p2), [0.0, 0, 0])
                    c2 = cls_pool.setdefault((cls, p2), [0.0, 0, 0])
                    e2[2] += 1; c2[2] += 1
        n_r = max(1, self.n_candidates - 1)
        default_eq = _DEFAULT_PLACED_EQ_TOTAL / n_r
        default_eta = _DEFAULT_MU * default_eq / (1.0 - default_eq)
        rates = {}
        for (obj, r), (on_dt, leaves, enters) in edge.items():
            cls = self.obj_class_of.get(obj, "?")
            c_on, c_lv, c_en = cls_pool.get((cls, r), [0.0, 0, 0])
            c_off = max(cls_total.get(cls, 0.0) - c_on, 0.0)
            off_dt = max(obj_total.get(obj, 0.0) - on_dt, 0.0)
            cls_mu = (c_lv / c_on) if c_on > 0 else _DEFAULT_MU
            cls_eta = (c_en / c_off) if c_off > 0 else default_eta
            mu = (leaves + _SMOOTH_K) / (on_dt + _SMOOTH_K / max(cls_mu, 1e-9)) if on_dt > 0 else cls_mu
            eta = (enters + _SMOOTH_K) / (off_dt + _SMOOTH_K / max(cls_eta, 1e-12)) if off_dt > 0 else cls_eta
            rates[(obj, r)] = (max(mu, 1e-9), max(eta, 1e-12))

        # C2 occupancy pinning: rescale each object's edge equilibria so
        # their total matches the object's OBSERVED in-house (placed)
        # occupancy. Without this, the reserved elsewhere/absent slot ate
        # 30-40% of the mass on objects that were in the house the whole
        # training week (measured on the stage1 probe: b3 acc 0.815 but
        # mean p_true 0.556) — an emergence prior mis-calibration that
        # would make Stage 2's stopping rule over-explore. Decay speed
        # (mu + eta) is preserved; only the equilibrium split moves.
        from dynbelief import ELSEWHERE_ID as _EW
        if not _PIN_OCCUPANCY:
            self._rates = rates
            return
        placed_dt: dict = {}
        for obj, pairs in self.pair_stats.items():
            for (t1, p1, t2, p2) in pairs:
                dt = t2 - t1
                if dt > 0 and p1 != _EW:
                    placed_dt[obj] = placed_dt.get(obj, 0.0) + dt
        by_obj: dict = {}
        for (obj, r), (mu, eta) in rates.items():
            by_obj.setdefault(obj, []).append((r, mu, eta))
        for obj, edges in by_obj.items():
            total = obj_total.get(obj, 0.0)
            if total <= 0:
                continue
            frac = placed_dt.get(obj, 0.0) / total
            if frac < _PIN_MIN_PLACED_FRAC:
                continue
            target = min(frac, 0.98)
            n_unfitted = n_r - len(edges)
            s_eq = sum(eta / (mu + eta) for _, mu, eta in edges) + n_unfitted * default_eq
            if s_eq <= 0:
                continue
            scale = target / s_eq
            for r, mu, eta in edges:
                rate = mu + eta
                p_eq = min(max((eta / rate) * scale, 1e-9), 0.995)
                rates[(obj, r)] = (rate * (1.0 - p_eq), rate * p_eq)
        self._rates = rates

    def _edge_rates(self, obj: int, r: int) -> tuple[float, float]:
        if self._rates is None:
            self._fit()
        n_r = max(1, self.n_candidates - 1)
        default_eq = _DEFAULT_PLACED_EQ_TOTAL / n_r
        default_eta = _DEFAULT_MU * default_eq / (1.0 - default_eq)
        return self._rates.get((obj, r), (_DEFAULT_MU, default_eta))

    # ── filtering ─────────────────────────────────────────────────────────────
    def reset(self, objects, receptacles, t0) -> None:
        super().reset(objects, receptacles, t0)
        self._anchor = {}

    def _equilibrium(self, obj: int) -> np.ndarray:
        v = np.zeros(self.n_candidates)
        for r in range(1, self.n_candidates):
            mu, eta = self._edge_rates(obj, r)
            v[r] = eta / (mu + eta)
        return v

    def _f_for(self, obj: int):
        """f(t) may be global (SwitchingPrior) or per-class (an object with
        .for_class, e.g. priors.schedule_prior.PerClassPrior)."""
        if hasattr(self.f, "for_class"):
            return self.f.for_class(self.obj_class_of.get(obj, "?"))
        return self.f

    def predict(self, t: int) -> dict[int, np.ndarray]:
        out = {}
        for obj in self.objects:
            t0, p0 = self._anchor.get(obj, (self.t0, None))
            if p0 is None:
                p0 = self._equilibrium(obj)
            F = self._f_for(obj).cumulative(t0, t)
            probs = np.zeros(self.n_candidates)
            for r in range(1, self.n_candidates):
                mu, eta = self._edge_rates(obj, r)
                p_eq = eta / (mu + eta)
                probs[r] = p_eq + (p0[r] - p_eq) * np.exp(-(mu + eta) * F)
            S = probs[1:].sum()
            if S > 1.0:
                probs[1:] /= S
                probs[ELSEWHERE_ID] = 0.0
            else:
                probs[ELSEWHERE_ID] = 1.0 - S
            out[obj] = probs
        return out
