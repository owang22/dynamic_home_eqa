"""C4 — latent-regime HMM: the classical routine-inferencer, and the most
important comparison arm (the LLM's edge over C4 isolates the value of
language-encoded knowledge).

Model: a hidden discrete DAY-TYPE regime chain shared across ALL objects
(one regime per calendar day; Markov over consecutive days), with per-object
emissions conditioned on (regime, time-of-day bucket):

    P(day d's snapshots | regime k) =
        prod_rows prod_obj  emis[obj][k, tod(row), state(obj,row)]

Fit by EM (Baum-Welch over the day sequence) with Dirichlet-smoothed emission
updates. The regime label is LEARNED (L3: no profile day-type input); after
fitting we log the regime-per-day schedule so T1 households can be checked
for workday/off-day alignment (W4 qualitative figure).

Hyperparameters: n_regimes swept in {2,3,4}, selected by held-out day
log-likelihood (L4, never query accuracy). Multiple restarts (default 5) with
fixed seeds; label switching across runs is handled by selecting on held-out
likelihood only (W4).

Prediction at query time t (day D, one past the history): regime marginal =
forward posterior of day D-1 propagated one step through the learned
transition matrix; occupancy = sum_k P(regime=k) emis[obj][k, tod(t), r].

Leave rates: same constant per-class MLE as C1."""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.classical.rates.base import (
    default_class, hazard_mle, occupancy_counts, split_history,
)

N_TOD = 6                       # 4h time-of-day buckets
ALPHA = 0.5                     # Dirichlet emission smoothing


def _tod(t: int) -> int:
    return int((t % MIN_PER_DAY) // (MIN_PER_DAY // N_TOD))


class C4RegimeHMM:
    name = "C4_regime"

    def __init__(self, candidates: list[str], n_regimes: int = 2,
                 n_restarts: int = 5, seed: int = 7, em_iters: int = 40):
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.n_regimes = int(n_regimes)
        self.n_restarts = int(n_restarts)
        self.seed = int(seed)
        self.em_iters = int(em_iters)
        self._rates: dict[str, float] = {}
        self._occ_obj: dict[str, np.ndarray] = {}
        self._occ_cls: dict[str, np.ndarray] = {}
        self._objs: list[str] = []
        self._emis: dict[str, np.ndarray] = {}   # obj -> (K, N_TOD, R)
        self._trans: np.ndarray | None = None    # (K, K)
        self._regime_next: np.ndarray | None = None  # P(regime at query day)
        self.regime_schedule: list[np.ndarray] = []  # per-day posterior (W4)
        self.degenerate = False

    # ── EM ───────────────────────────────────────────────────────────────────
    def _day_tensors(self, history):
        """Per day: list of (obj_idx_into self._objs, tod, recep_idx)."""
        days = sorted({r["day"] for r in history})
        oidx = {o: i for i, o in enumerate(self._objs)}
        per_day = {d: [] for d in days}
        for row in history:
            tod = _tod(row["t_min"])
            for o, r in row["parents"].items():
                if o in oidx and r in self._idx:
                    per_day[row["day"]].append((oidx[o], tod, self._idx[r]))
        return days, per_day

    def _day_loglik(self, obs, emis_log):
        """log P(day's obs | regime k) for all k. obs: [(oi, tod, ri)]."""
        K = self.n_regimes
        ll = np.zeros(K)
        for (oi, tod, ri) in obs:
            ll += emis_log[oi][:, tod, ri]
        return ll

    def _em_once(self, days, per_day, rng):
        K, R = self.n_regimes, len(self.candidates)
        nobj = len(self._objs)
        emis = rng.dirichlet(np.ones(R), size=(nobj, K, N_TOD))     # (n,K,T,R)
        trans = np.full((K, K), 1.0 / K) + rng.uniform(0, .1, (K, K))
        trans /= trans.sum(1, keepdims=True)
        init = np.full(K, 1.0 / K)
        ll_prev = -np.inf
        for _ in range(self.em_iters):
            emis_log = np.log(np.clip(emis, 1e-12, 1))
            # forward-backward over days
            n = len(days)
            logB = np.array([self._day_loglik(per_day[d], emis_log) for d in days])
            la = np.zeros((n, K)); lb = np.zeros((n, K))
            la[0] = np.log(init) + logB[0]
            logT = np.log(np.clip(trans, 1e-12, 1))
            for i in range(1, n):
                la[i] = logB[i] + _logsumexp_mat(la[i - 1][:, None] + logT)
            for i in range(n - 2, -1, -1):
                lb[i] = _logsumexp_mat((logT + logB[i + 1] + lb[i + 1])[None, :, :].squeeze(0), axis=1)
            ll = _logsumexp(la[-1])
            g = la + lb - ll                                   # log gamma
            gamma = np.exp(g - g.max(1, keepdims=True))
            gamma /= gamma.sum(1, keepdims=True)
            # xi for transitions
            xi_acc = np.zeros((K, K))
            for i in range(1, n):
                lx = la[i - 1][:, None] + logT + logB[i] + lb[i] - ll
                x = np.exp(lx - lx.max())
                xi_acc += x / max(1e-12, x.sum())
            # M-step
            init = gamma[0] + 1e-3
            init /= init.sum()
            trans = xi_acc + ALPHA
            trans /= trans.sum(1, keepdims=True)
            counts = np.full((nobj, K, N_TOD, R), ALPHA)
            for i, d in enumerate(days):
                for (oi, tod, ri) in per_day[d]:
                    counts[oi, :, tod, ri] += gamma[i]
            emis = counts / counts.sum(-1, keepdims=True)
            if abs(ll - ll_prev) < 1e-6:
                break
            ll_prev = ll
        return ll, emis, trans, init, gamma

    def fit(self, observation_history: list[dict]) -> None:
        self._rates = hazard_mle(observation_history)
        self._occ_obj, self._occ_cls = occupancy_counts(
            observation_history, self.candidates)
        self._objs = sorted({o for r in observation_history for o in r["parents"]})
        days, per_day = self._day_tensors(observation_history)
        if len(days) < 2 or not self._objs:
            self.degenerate = True                # W2: cold start; occupancy fallback
            self._trans = None
            return
        best = None
        for s in range(self.n_restarts):
            rng = np.random.default_rng(self.seed + s)
            out = self._em_once(days, per_day, rng)
            if best is None or out[0] > best[0]:
                best = out
        ll, emis, trans, init, gamma = best
        self._emis = {o: emis[i] for i, o in enumerate(self._objs)}
        self._trans = trans
        self.regime_schedule = [gamma[i] for i in range(len(days))]   # W4
        # regime marginal for the query day = last posterior @ transition
        self._regime_next = gamma[-1] @ trans

    # ── RateModel interface ───────────────────────────────────────────────────
    def _dist(self, object_id: str, t: int) -> np.ndarray:
        if self._trans is None or object_id not in self._emis:
            v = self._occ_obj.get(object_id)
            if v is None:
                v = self._occ_cls.get(default_class(object_id))
            if v is None:
                return np.full(len(self.candidates), 1.0 / len(self.candidates))
            return v
        e = self._emis[object_id][:, _tod(t), :]        # (K, R)
        p = self._regime_next @ e
        return p / p.sum()

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        return float(self._dist(object_id, t)[self._idx[receptacle_id]])

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        return self._rates.get(default_class(object_id), 0.0)

    def estimator_for(self, object_id: str) -> str:
        if self._trans is not None and object_id in self._emis:
            return "regime"
        if object_id in self._occ_obj:
            return "fallback_empirical_occ"
        return "fallback_class_backoff"

    # ── L4 selection helper: held-out day log-likelihood ─────────────────────
    def heldout_day_loglik(self, history: list[dict]) -> float:
        fit_rows, val_rows = split_history(history)
        if not val_rows:
            return float("nan")
        tmp = C4RegimeHMM(self.candidates, self.n_regimes, self.n_restarts,
                          self.seed, self.em_iters)
        tmp.fit(fit_rows)
        if tmp._trans is None:
            return float("nan")
        emis_log = {o: np.log(np.clip(tmp._emis[o], 1e-12, 1)) for o in tmp._emis}
        # score val days under the regime prior propagated from fit
        days = sorted({r["day"] for r in val_rows})
        oidx = {o: i for i, o in enumerate(tmp._objs)}
        regime = tmp._regime_next
        tot, n = 0.0, 0
        for d in days:
            ll_k = np.zeros(tmp.n_regimes)
            cnt = 0
            for row in [r for r in val_rows if r["day"] == d]:
                tod = _tod(row["t_min"])
                for o, r_obs in row["parents"].items():
                    if o in emis_log and r_obs in tmp._idx:
                        ll_k += emis_log[o][:, tod, tmp._idx[r_obs]]
                        cnt += 1
            if cnt:
                tot += _logsumexp(np.log(np.clip(regime, 1e-12, 1)) + ll_k)
                n += cnt
            regime = regime @ tmp._trans
        return tot / max(1, n)


def _logsumexp(v):
    m = np.max(v)
    return float(m + np.log(np.sum(np.exp(v - m))))


def _logsumexp_mat(m, axis=0):
    mx = m.max(axis=axis)
    return mx + np.log(np.exp(m - np.expand_dims(mx, axis)).sum(axis=axis))
