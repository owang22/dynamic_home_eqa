"""Pre-Stage-2 analysis toolkit (stage1b): dataset characterization (A1–A3),
bootstrap CIs (B5), calibration/ECE (D1–D2), and the Δt nested-model test
(C3). Pure functions over ReplayWorld + probe record lists.
"""
from __future__ import annotations

import numpy as np

from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs.base import object_class


# ── A1: volatility ───────────────────────────────────────────────────────────

def volatility_table(world) -> list[dict]:
    """Per-object moves-per-day (human events only — day-boundary resets are
    logging artifacts, not motion) + volatility tercile."""
    n_days = world.n_days
    rows = []
    for obj in world.objects():
        n_moves = len(world.change_times(obj))
        rows.append({"obj_id": obj, "label": world.obj_label[obj],
                     "class": object_class(world.obj_label[obj]),
                     "n_moves": n_moves, "moves_per_day": n_moves / n_days})
    rates = sorted(r["moves_per_day"] for r in rows)
    lo = rates[len(rates) // 3]
    hi = rates[2 * len(rates) // 3]
    for r in rows:
        if r["moves_per_day"] == 0 or r["moves_per_day"] <= lo:
            r["tercile"] = "static"
        elif r["moves_per_day"] <= hi:
            r["tercile"] = "occasional"
        else:
            r["tercile"] = "dynamic"
    return rows


def volatility_summary(rows: list[dict]) -> dict:
    x = np.array([r["moves_per_day"] for r in rows])
    from scipy.stats import skew
    return {"mean": float(x.mean()), "median": float(np.median(x)),
            "skew": float(skew(x)) if len(x) > 2 else None,
            "n_static": sum(r["tercile"] == "static" for r in rows),
            "n_occasional": sum(r["tercile"] == "occasional" for r in rows),
            "n_dynamic": sum(r["tercile"] == "dynamic" for r in rows)}


# ── A2: periodicity / predictability ─────────────────────────────────────────

def predictability_table(world, grid_min: int = 30) -> list[dict]:
    """Two per-object scores, [0, 1] each:

    repeat24h — P(parent(t) == parent(t - 1 day)) over the whole timeline:
      the day-lag autocorrelation of the location signal. High = the object
      re-visits the same place at the same time of day.
    move_concentration — 1 − normalized entropy of the object's move-time-of-
      day histogram (2h bins): high = moves are routine-locked to specific
      hours, low = moves scattered uniformly (volatility WITHOUT
      predictability, the regime where b3 collapses toward b2).

    predictability = mean of the two (repeat24h alone for objects with < 2
    moves, whose move histogram is degenerate)."""
    horizon = world.horizon_min()
    rows = []
    for obj in world.objects():
        sig = [world.true_parent(obj, t) for t in range(0, horizon, grid_min)]
        per_day = MIN_PER_DAY // grid_min
        same = [int(sig[i] == sig[i - per_day]) for i in range(per_day, len(sig))]
        repeat24h = float(np.mean(same)) if same else 0.0

        times = world.change_times(obj)
        if len(times) >= 2:
            bins = np.zeros(12)
            for t in times:
                bins[(t % MIN_PER_DAY) // 120] += 1
            p = bins / bins.sum()
            nz = p[p > 0]
            ent = float(-(nz * np.log(nz)).sum()) / np.log(len(bins))
            concentration = 1.0 - ent
            score = 0.5 * (repeat24h + concentration)
        else:
            concentration = None
            score = repeat24h
        rows.append({"obj_id": obj, "label": world.obj_label[obj],
                     "class": object_class(world.obj_label[obj]),
                     "n_moves": len(times), "repeat24h": round(repeat24h, 4),
                     "move_concentration": (round(concentration, 4)
                                            if concentration is not None else None),
                     "predictability": round(float(score), 4)})
    return rows


# ── A3: class–volatility coupling ────────────────────────────────────────────

def class_volatility_coupling(vol_rows: list[dict]) -> dict:
    """One-way ANOVA of per-object move rate grouped by class: eta^2 (share
    of volatility variance explained by class alone) + per-class means. High
    eta^2 flags class as a volatility proxy — any class-informed component
    can then pick up the 'moved' signal without modeling dynamics."""
    groups: dict[str, list[float]] = {}
    for r in vol_rows:
        groups.setdefault(r["class"], []).append(r["moves_per_day"])
    all_x = np.array([r["moves_per_day"] for r in vol_rows])
    grand = all_x.mean()
    ss_between = sum(len(g) * (np.mean(g) - grand) ** 2 for g in groups.values())
    ss_total = float(((all_x - grand) ** 2).sum())
    eta2 = ss_between / ss_total if ss_total > 0 else 0.0
    per_class = {c: {"n": len(g), "mean_moves_per_day": round(float(np.mean(g)), 3)}
                 for c, g in sorted(groups.items())}
    flagged = [c for c, v in per_class.items()
               if v["mean_moves_per_day"] > 2 * float(grand) and v["n"] >= 2]
    return {"eta2_class_on_volatility": round(float(eta2), 4),
            "grand_mean_moves_per_day": round(float(grand), 4),
            "per_class": per_class, "flagged_classes": flagged}


# ── B5: cluster bootstrap CI ─────────────────────────────────────────────────

def bootstrap_ci(records: list[dict], key: str = "correct", by: str = "obj",
                 n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """(mean, lo95, hi95) with a CLUSTER bootstrap over objects — probes of
    one object share its trajectory and are not independent samples."""
    rng = np.random.default_rng(seed)
    if not records:
        return float("nan"), float("nan"), float("nan")
    clusters: dict = {}
    for r in records:
        clusters.setdefault(r[by], []).append(float(r[key]))
    keys = list(clusters)
    mean = float(np.mean([v for vals in clusters.values() for v in vals]))
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(len(keys), size=len(keys), replace=True)
        vals = [v for i in pick for v in clusters[keys[i]]]
        stats.append(np.mean(vals))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return mean, float(lo), float(hi)


# ── D1/D2: calibration ───────────────────────────────────────────────────────

def ece(records: list[dict], conf_key: str = "p_chosen", n_bins: int = 10) -> dict:
    """Expected calibration error on the CHOSEN option's probability, plus
    the reliability curve."""
    conf = np.array([r[conf_key] for r in records])
    corr = np.array([r["correct"] for r in records], dtype=float)
    bins = np.linspace(0, 1, n_bins + 1)
    which = np.clip(np.digitize(conf, bins) - 1, 0, n_bins - 1)
    curve, e = [], 0.0
    for b in range(n_bins):
        m = which == b
        if not m.any():
            curve.append({"bin": b, "n": 0, "conf": None, "acc": None})
            continue
        c, a = float(conf[m].mean()), float(corr[m].mean())
        e += (m.mean()) * abs(a - c)
        curve.append({"bin": b, "n": int(m.sum()), "conf": round(c, 4), "acc": round(a, 4)})
    return {"ece": round(float(e), 4), "curve": curve}


def fit_temperature(records: list[dict], conf_key: str = "p_true") -> float:
    """Single temperature T minimizing NLL of the true option under
    p^(1/T)/norm — approximated on the true-option probability with the
    complement lumped (binary NLL), which is what the stopping rule consumes."""
    p = np.clip(np.array([r[conf_key] for r in records]), 1e-6, 1 - 1e-6)
    y = np.array([r["correct"] for r in records], dtype=float)
    best_T, best_nll = 1.0, np.inf
    for T in np.linspace(0.25, 4.0, 76):
        q = p ** (1.0 / T)
        # clip after sharpening: at small T the ratio rounds to exactly 0/1
        # in float64 and the NLL goes NaN, silently dropping that T
        q = np.clip(q / (q + (1 - p) ** (1.0 / T)), 1e-9, 1 - 1e-9)
        nll = float(-(y * np.log(q) + (1 - y) * np.log(1 - q)).mean())
        if nll < best_nll:
            best_T, best_nll = float(T), nll
    return best_T


def apply_temperature(records: list[dict], T: float,
                      conf_key: str = "p_true") -> list[dict]:
    out = []
    for r in records:
        p = min(max(r[conf_key], 1e-6), 1 - 1e-6)
        q = p ** (1.0 / T)
        q = q / (q + (1 - p) ** (1.0 / T))
        r2 = dict(r)
        r2[conf_key] = float(q)
        out.append(r2)
    return out


# ── C3: nested-model test for time-of-day structure ─────────────────────────

def nested_tod_test(records: list[dict]) -> dict:
    """Cell-level accuracy regressed on Δt (linear + quadratic) vs. Δt +
    time-of-day harmonics of t_seen and t_query (sin/cos, 1st + 2nd). F-test
    on the added terms: significant time-of-day terms are the evidence that
    the residual beyond Δt is structure, not noise."""
    from collections import defaultdict
    from scipy.stats import f as fdist
    cells = defaultdict(list)
    for r in records:
        cells[(r["t_seen_tod"], r["t_query_tod"])].append(r["correct"])
    pts = [(s, q, float(np.mean(v))) for (s, q), v in cells.items()]
    if len(pts) < 20:
        return {"note": "too few cells", "n_cells": len(pts)}
    s = np.array([p[0] for p in pts]) / MIN_PER_DAY * 2 * np.pi
    q = np.array([p[1] for p in pts]) / MIN_PER_DAY * 2 * np.pi
    dt = np.array([p[1] - p[0] for p in pts]) / MIN_PER_DAY
    y = np.array([p[2] for p in pts])
    X0 = np.column_stack([np.ones_like(dt), dt, dt ** 2])
    tod = np.column_stack([np.sin(s), np.cos(s), np.sin(2 * s), np.cos(2 * s),
                           np.sin(q), np.cos(q), np.sin(2 * q), np.cos(2 * q)])
    X1 = np.column_stack([X0, tod])

    def rss(X):
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        return float(((y - X @ beta) ** 2).sum())

    rss0, rss1 = rss(X0), rss(X1)
    df1 = X1.shape[1] - X0.shape[1]
    df2 = len(y) - X1.shape[1]
    F = ((rss0 - rss1) / df1) / (rss1 / max(df2, 1))
    pval = float(fdist.sf(F, df1, max(df2, 1)))
    return {"n_cells": len(pts), "rss_dt_only": round(rss0, 4),
            "rss_dt_plus_tod": round(rss1, 4), "F": round(float(F), 3),
            "p_value": pval, "tod_terms_significant": bool(pval < 0.01)}
