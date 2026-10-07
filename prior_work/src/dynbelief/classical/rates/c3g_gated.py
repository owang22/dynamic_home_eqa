"""C3g — HELD-OUT-GATED periodic GLM: the FROZEN canonical classical opponent.

Motivation (E7 diagnosis): the ungated C3 periodic GLM (c3_glm.py) fits a
per-object logistic model on 13 Fourier/calendar features whenever the object has
>=8 observations. In the sparse-event regime (8..~40 events) that is enough to
FIT the periodic surface but not enough to fit it WELL: phase/period are
mis-estimated and the model underperforms plain persistence. Empirically its
learning curve DEGRADES with more data and drops BELOW C1 (e.g. pet-heavy cushion
C3=0.29 vs C1=0.86 at D>=10) -- an anti-learning artifact, not signal.

Fix (the same L4 model-selection discipline already used to sweep C): enable the
periodic term per OBJECT only when it demonstrably GENERALIZES -- i.e. beats the
constant empirical-occupancy model on that object's own held-out observation
likelihood (time-ordered 80/20 split). Objects with too few events to form a
usable validation split fall back to constant. Result: persistence/constant
everywhere by default, periodicity only where it is earned on held-out data.

This drops the overfit crashes (pet cushion, sparse shift laptop -> constant,
tracks C1) while keeping the genuine weekly cycle (retiree coffee_mug -> periodic
-> 1.0). BIC on TRAIN likelihood was tried first and rejected: with 13 features
its complexity penalty is so steep it discards even the real cycle. Held-out
likelihood is the honest, self-calibrating criterion.

This is the single named classical model frozen for all "vs classical" claims,
the learning curves, and the hybrid's non-LLM branch. Do not tune per experiment.
"""
from __future__ import annotations

import numpy as np

from dynbelief.classical.rates.base import (
    calendar_features, default_class, occupancy_counts)
from dynbelief.classical.rates.c3_glm import C3PeriodicGLM

_LOG_EPS = 1e-9
_MIN_VAL = 3          # need >=3 held-out points to trust the comparison
# MDL-style gate: the periodic GLM must improve held-out predictive log-likelihood
# by at least _TAU nats PER held-out observation over the constant model. A small
# obs-likelihood edge (pet cushion, sparse shift laptop ~0.4 nats/pt) does not
# survive -> those fall back to constant and track C1 (no crash); a true weekly
# cycle (retiree coffee_mug ~1.2 nats/pt) clears it and keeps the periodic term.
_TAU = 0.7


class C3GatedGLM(C3PeriodicGLM):
    name = "C3g_gated"

    def fit(self, observation_history: list[dict]) -> None:
        super().fit(observation_history)
        # per-object rows in time order (super already filtered to valid recep)
        xs: dict[str, list] = {}
        ys: dict[str, list] = {}
        for row in sorted(observation_history, key=lambda r: r["t_min"]):
            phi = calendar_features(row["t_min"])
            for o, r in row["parents"].items():
                if r in self._idx:                # _idx maps receptacles -> col
                    xs.setdefault(o, []).append(phi)
                    ys.setdefault(o, []).append(self._idx[r])
        self.gated_out: dict[str, dict] = {}
        for o in list(self._models.keys()):
            X = np.array(xs[o]); y = np.array(ys[o]); n = len(y)
            n_val = max(_MIN_VAL, int(round(0.2 * n)))
            n_fit = n - n_val
            keep = False; ll_glm = ll_const = float("nan")
            # need a fit split with >=2 classes and a val split of >=_MIN_VAL
            if n_fit >= 4 and n_val >= _MIN_VAL and len(set(y[:n_fit].tolist())) >= 2:
                from sklearn.linear_model import LogisticRegression
                Xf, yf = X[:n_fit], y[:n_fit]
                Xv, yv = X[n_fit:], y[n_fit:]
                gm = LogisticRegression(C=self.C, max_iter=1000).fit(Xf, yf)
                pos = {c: j for j, c in enumerate(gm.classes_)}
                pv = gm.predict_proba(Xv)
                ll_glm = float(np.sum([np.log(np.clip(
                    pv[i, pos[yv[i]]] if yv[i] in pos else _LOG_EPS, _LOG_EPS, 1.0))
                    for i in range(n_val)]))
                # constant model from the SAME fit rows (class-backed off occupancy)
                per_obj, per_cls = occupancy_counts(
                    [{"t_min": 0, "parents": {o: self.candidates[c]}} for c in yf],
                    self.candidates)
                pc = per_obj[o]
                ll_const = float(np.sum([np.log(np.clip(pc[yv[i]], _LOG_EPS, 1.0))
                                         for i in range(n_val)]))
                keep = (ll_glm - ll_const) / n_val > _TAU
            self.gated_out[o] = {"n": int(n), "n_val": int(n_val),
                                 "kept_glm": bool(keep), "gain_per_pt":
                                 round((ll_glm - ll_const) / max(n_val, 1), 3),
                                 "ll_glm": round(ll_glm, 3), "ll_const": round(ll_const, 3)}
            if not keep:
                del self._models[o]               # -> _dist falls back to constant
                self._classes.pop(o, None)

    def estimator_for(self, object_id: str) -> str:
        if object_id in self._models:
            return "glm_gated"
        if object_id in self._occ_obj:
            return "constant"
        if default_class(object_id) in self._occ_cls:
            return "fallback_class_backoff"
        return "fallback_uniform"
