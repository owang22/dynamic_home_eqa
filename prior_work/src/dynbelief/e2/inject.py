"""Prior injection as PSEUDO-OBSERVATIONS with equivalent-sample-size kappa.

The mandated mechanism (not initialization-only): a prior is expressed as
`kappa` days of synthetic snapshots consistent with the elicited (or oracle)
parameters, PREPENDED to the real observation history before the rate model is
fit. The fit then blends prior and data by their sample sizes — a strong kappa
persists through several days of real data (harm-persistence is measurable);
kappa=1 day is quickly overwritten.

This IS the documented, unit-tested transform (elicited params -> pseudo-obs):
the pseudo stream's empirical occupancy reproduces the elicited occupancy per
class (tested), and both C3's GLM coefficients and C1's rate are moved toward
the elicited values via the shared fit path (no bespoke coefficient surgery).

kappa in days: {weak: 1, moderate: 7, strong: 28}.
"""
from __future__ import annotations

import random

from dynbelief import MIN_PER_DAY
from dynbelief.e2.elicit import MOVE_RATE_PER_DAY, TOD_BUCKETS

KAPPA_DAYS = {"weak": 1, "moderate": 7, "strong": 28}
OBS_PER_DAY = 3
OBS_HOURS = [8 * 60, 14 * 60, 20 * 60]     # pseudo-snapshot cadence (jittered)
_TOD_RANGES = [(0, 6), (6, 10), (10, 14), (14, 18), (18, 22), (22, 24)]


def _tod_bucket(t_min: int) -> str:
    h = (t_min % MIN_PER_DAY) / 60
    for (lo, hi), name in zip(_TOD_RANGES, TOD_BUCKETS):
        if lo <= h < hi:
            return name
    return TOD_BUCKETS[0]


def _occupancy_dist(elic_cls: dict, receptacles: list[str]):
    """Elicited class prior -> (home, {recep: weight}) full occupancy over the
    candidate axis (home gets the residual mass)."""
    home = elic_cls["home"] if elic_cls["home"] in receptacles else receptacles[0]
    sec = {r: max(0.0, w) for r, w in elic_cls.get("secondary", {}).items()
           if r in receptacles and r != home}
    ssum = sum(sec.values())
    if ssum > 0.95:                                  # leave the home some mass
        sec = {r: w * 0.9 / ssum for r, w in sec.items()}
        ssum = sum(sec.values())
    dist = dict(sec)
    dist[home] = max(0.05, 1.0 - ssum)
    z = sum(dist.values())
    return home, {r: v / z for r, v in dist.items()}


def pseudo_from_elicited(elicited: dict, obj_class: dict, receptacles: list[str],
                         kappa_days: int, seed: int) -> list[dict]:
    """`kappa_days` of synthetic snapshots from the elicited per-class prior.
    obj_class: {object_id: class}. Objects with no elicited class are placed at
    a uniform-ish default (they contribute little)."""
    rng = random.Random(seed)
    objs = sorted(obj_class)
    rows = []
    state = {}
    for o in objs:
        cls = elicited.get(obj_class[o])
        state[o] = (_occupancy_dist(cls, receptacles)[0] if cls else receptacles[0])
    for d in range(kappa_days):
        weekend = (d % 7) >= 5
        for base in OBS_HOURS:
            t = d * MIN_PER_DAY + base + rng.randint(-60, 60)
            tod = _tod_bucket(t)
            parents = {}
            for o in objs:
                cls = elicited.get(obj_class[o])
                if cls is None:
                    parents[o] = state[o]
                    continue
                home, dist = _occupancy_dist(cls, receptacles)
                active = tod in cls.get("active_windows", {})
                ww = cls.get("weekday_weekend", "same")
                if (ww == "more_weekday" and weekend) or (ww == "more_weekend" and not weekend):
                    active = active and rng.random() < 0.4   # dampen off-type activity
                mr = MOVE_RATE_PER_DAY.get(cls.get("move_rate", "low"), 0.6)
                p_move = min(1.0, mr / OBS_PER_DAY) if active else 0.05
                if rng.random() < p_move:            # resample (a move)
                    rs, ws = zip(*dist.items())
                    state[o] = rng.choices(rs, weights=ws, k=1)[0]
                elif not active:
                    state[o] = home                  # rest at home when inactive
                parents[o] = state[o]
            rows.append({"day": d, "t_min": t, "parents": parents})
    return rows


def pseudo_from_oracle(oracle, obj_class: dict, receptacles: list[str],
                       kappa_days: int, seed: int) -> list[dict]:
    """Porc: `kappa_days` of snapshots drawn from the C5 oracle's true marginal
    occupancy (generator parameters). The machinery control — must help."""
    import numpy as np
    rng = np.random.default_rng(seed)
    objs = sorted(obj_class)
    rows = []
    for d in range(kappa_days):
        for base in OBS_HOURS:
            t = d * MIN_PER_DAY + base + int(rng.integers(-60, 61))
            parents = {}
            for o in objs:
                p = np.array([max(1e-6, oracle.occupancy(o, r, t)) for r in receptacles])
                p = p / p.sum()
                parents[o] = receptacles[int(rng.choice(len(receptacles), p=p))]
            rows.append({"day": d, "t_min": t, "parents": parents})
    return rows


def inject(real_history: list[dict], pseudo: list[dict]) -> list[dict]:
    """Prepend pseudo-observations to the real window. Both are day-aligned by
    weekday (t mod week); day indices may overlap — the rate models bin by
    calendar features of t_min, so this reinforces the prior at the right
    weekday/time-of-day rather than shifting the calendar."""
    return list(pseudo) + list(real_history)
