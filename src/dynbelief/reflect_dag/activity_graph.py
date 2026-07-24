"""Change 1 — activity V-structure underneath the persona.

FBN (Zhang et al., ICCV 2025) cannot place a direct object<->scene edge in a DAG
(a bidirectional relation is forbidden), so it routes through a FUNCTION node as a
collider: object -> function <- scene. That collider is what makes atypical
LAYOUTS representable (a yoga mat in a bedroom is fine because the mat affords
*exercise* regardless of room). Our temporal analogue: object location and
time-of-day are not causally ordered, so route them through an ACTIVITY collider

    object -> activity <- time_of_day

and hang the whole thing under the persona the reflection already infers:

    persona (regime label) -> {activities} -> per-object location/timing edges

The persona supplies the PRIOR over which activity structure is plausible; the
activity nodes supply the PARAMETER-TYING a monolithic persona latent cannot:
objects sharing an activity share its timing fit, so a rare (2-event) object
inherits its activity group's pooled f(t). This module is the statistical side —
the DAG container + the tied-timing rate model. The LLM authors the structure
(structure_elicit.py); here we FIT parameters and expose the group precision the
precision-weighted fusion (precision_fusion.py) needs.

The rate model duck-types C3GatedGLM (occupancy/rate/candidates), so it drops into
the frozen _belief/_predict path unchanged. C3g itself is NOT modified.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from dynbelief.classical.rates.base import (
    calendar_features, default_class, hazard_mle, occupancy_counts)

# Fixed activity vocabulary (brief). Objects are tied to at most one activity;
# the "none" bucket falls back to the per-object constant (C1-like) model.
ACTIVITY_VOCAB = ["sleep", "work_departure", "meal", "exercise", "leisure", "errand"]

_LOG_EPS = 1e-9
# MDL-style gate, C3g discipline but rescaled for the BINARY pooled model:
# C3g's tau=0.7 nats/pt was calibrated for a ~15-way multinomial where the
# constant model's per-point ll is ~-2.7; the tied model is a 2-way (home/away)
# problem whose MAXIMUM possible gain over a balanced constant is ln2=0.69, so
# 0.7 would reject a perfect fit. Same criterion (held-out nats/pt), rescaled by
# the outcome cardinality: tau_bin = 0.7 * ln(2)/ln(15) ~= 0.18 -> 0.15.
_TAU = 0.15
_MIN_VAL = 3
_MIN_GROUP_EVENTS = 8   # a group needs >=8 pooled events before its f(t) is even
                        # considered (mirrors C3g's per-object >=8 rule, but on
                        # the POOLED count — the whole point of tying).


@dataclass
class ActivityStructure:
    """The LLM-authored (or oracle/scrambled) structure for one household.

    persona: the regime label the reflection already produces.
    activity_objects: activity -> [object ids it moves] (a partition-ish map;
      an object may appear under at most one activity — first wins).
    atypical_activities: activities the structure flagged as regime-shifted
      (logged for the per-activity atypicality decomposition)."""
    persona: str
    activity_objects: dict[str, list[str]]
    atypical_activities: list[str] = field(default_factory=list)
    source: str = "llm"        # llm | oracle | scrambled | none

    def object_activity(self) -> dict[str, str]:
        m: dict[str, str] = {}
        for act, objs in self.activity_objects.items():
            if act not in ACTIVITY_VOCAB:
                continue
            for o in objs:
                m.setdefault(o, act)          # first assignment wins
        return m


def _two_modes(recs: list[str]):
    """(home, away) = the two most frequent receptacles in an object's history.
    away is None if the object never leaves its dominant receptacle."""
    if not recs:
        return None, None
    c = defaultdict(int)
    for r in recs:
        c[r] += 1
    order = sorted(c, key=lambda r: -c[r])
    return order[0], (order[1] if len(order) > 1 else None)


class ActivityTiedRates:
    """C3g-compatible rate model with activity parameter-tying.

    For each activity GROUP, pool every tied object's (calendar_features(t) ->
    at-its-away-receptacle?) events into ONE logistic f_activity(t). Gate the
    pooled fit exactly as C3g gates its per-object term (held-out nats/point >
    _TAU, and >= _MIN_GROUP_EVENTS pooled events). occupancy() then blends each
    object's home vs away receptacle by the shared f(t); ungrouped or gated-out
    objects fall back to the per-object constant empirical occupancy (== C3g's
    fallback, so this model degrades gracefully to classical, never below it)."""

    name = "activity_tied"

    def __init__(self, candidates: list[str], structure: ActivityStructure):
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.structure = structure
        self._obj_act = structure.object_activity()
        self._rates: dict[str, float] = {}
        self._occ_obj: dict[str, np.ndarray] = {}
        self._occ_cls: dict[str, np.ndarray] = {}
        self._home: dict[str, str] = {}
        self._away: dict[str, str] = {}
        self._fmodel: dict[str, object] = {}     # activity -> logistic f(t)
        self._group_neff: dict[str, int] = {}    # activity -> pooled event count
        self.gated: dict[str, dict] = {}         # activity -> gate diagnostics

    # ── fit ──────────────────────────────────────────────────────────────────
    def fit(self, observation_history: list[dict]) -> None:
        from sklearn.linear_model import LogisticRegression
        hist = sorted(observation_history, key=lambda r: r["t_min"])
        self._rates = hazard_mle(hist)
        self._occ_obj, self._occ_cls = occupancy_counts(hist, self.candidates)

        # per-object receptacle history -> (home, away)
        obj_recs: dict[str, list[str]] = defaultdict(list)
        for row in hist:
            for o, r in row["parents"].items():
                if r in self._idx:
                    obj_recs[o].append(r)
        for o, recs in obj_recs.items():
            self._home[o], self._away[o] = _two_modes(recs)

        # pool (phi, at-away?) across each activity group
        pool_x: dict[str, list] = defaultdict(list)
        pool_y: dict[str, list] = defaultdict(list)
        for row in hist:
            phi = calendar_features(row["t_min"])
            for o, r in row["parents"].items():
                act = self._obj_act.get(o)
                if act is None or self._away.get(o) is None or r not in self._idx:
                    continue
                pool_x[act].append(phi)
                pool_y[act].append(1 if r == self._away[o] else 0)

        for act in pool_x:
            X = np.array(pool_x[act]); y = np.array(pool_y[act]); n = len(y)
            self._group_neff[act] = int(n)
            keep, gain = False, float("nan")
            if n >= _MIN_GROUP_EVENTS and len(set(y.tolist())) >= 2:
                n_val = max(_MIN_VAL, int(round(0.2 * n)))
                n_fit = n - n_val
                if n_fit >= 4 and len(set(y[:n_fit].tolist())) >= 2:
                    gm = LogisticRegression(C=1.0, max_iter=1000).fit(X[:n_fit], y[:n_fit])
                    pos = {c: j for j, c in enumerate(gm.classes_)}
                    pv = gm.predict_proba(X[n_fit:])
                    yv = y[n_fit:]
                    base = float(np.mean(y[:n_fit]))          # constant group rate
                    ll_glm = float(np.sum([np.log(np.clip(
                        pv[i, pos[yv[i]]] if yv[i] in pos else _LOG_EPS, _LOG_EPS, 1.0))
                        for i in range(n_val)]))
                    ll_const = float(np.sum([np.log(np.clip(
                        base if yv[i] == 1 else 1 - base, _LOG_EPS, 1.0))
                        for i in range(n_val)]))
                    gain = (ll_glm - ll_const) / n_val
                    keep = gain > _TAU
                    if keep:
                        self._fmodel[act] = LogisticRegression(C=1.0, max_iter=1000).fit(X, y)
            self.gated[act] = {"n_pooled": int(n), "kept": bool(keep),
                               "gain_per_pt": round(gain, 3) if gain == gain else None,
                               "n_objects": sum(1 for o in self._obj_act
                                                if self._obj_act[o] == act)}

    # ── precision hooks (for precision_fusion.py) ────────────────────────────
    def group_of(self, obj: str) -> str | None:
        act = self._obj_act.get(obj)
        return act if act in self._fmodel else None

    def group_neff(self, obj: str) -> int:
        """Pooled event count of the object's activity group (0 if ungrouped /
        gated out). This is the DATA precision the fusion weights against the
        prior — a rare object inherits its GROUP's count, not its own."""
        act = self._obj_act.get(obj)
        return self._group_neff.get(act, 0) if act in self._fmodel else 0

    def f_activity(self, obj: str, t: int) -> float | None:
        act = self._obj_act.get(obj)
        m = self._fmodel.get(act)
        if m is None or self._away.get(obj) is None:
            return None
        proba = m.predict_proba(calendar_features(t).reshape(1, -1))[0]
        pos = {c: j for j, c in enumerate(m.classes_)}
        return float(proba[pos[1]]) if 1 in pos else 0.0

    # ── C3g-compatible interface ─────────────────────────────────────────────
    def _dist(self, obj: str, t: int) -> np.ndarray:
        f = self.f_activity(obj, t)
        if f is not None:
            out = np.full(len(self.candidates), 1e-4)
            out[self._idx[self._away[obj]]] = f
            out[self._idx[self._home[obj]]] = max(1e-4, 1.0 - f)
            return out / out.sum()
        v = self._occ_obj.get(obj)
        if v is None:
            v = self._occ_cls.get(default_class(obj))
        if v is None:
            return np.full(len(self.candidates), 1.0 / len(self.candidates))
        return v

    def occupancy(self, obj: str, receptacle_id: str, t: int) -> float:
        return float(self._dist(obj, t)[self._idx[receptacle_id]])

    def rate(self, obj: str, receptacle_id: str, t: int) -> float:
        return self._rates.get(default_class(obj), 0.0)

    def estimator_for(self, obj: str) -> str:
        if self.group_of(obj):
            return f"activity_tied[{self._obj_act[obj]}]"
        if obj in self._occ_obj:
            return "constant"
        return "fallback"
