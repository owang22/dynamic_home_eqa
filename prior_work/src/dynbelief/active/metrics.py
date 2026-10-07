"""Active-probe metrics (brief Section 5). Object-clustered bootstrap CIs
(Stage-1c discipline). Cross-scene conventions:
  C2 pool GAPS not levels; chance-corrected accuracy (acc-chance)/(1-chance)
     when a level must be pooled.
  C3 budget axis normalised as looks/n_rooms.
  ELSEWHERE scored as a binary abstention decision (AbstainEQA framing):
     precision, recall, F1, over-abstention.
"""
from __future__ import annotations

import numpy as np


def _cluster_boot(vals_by_obj: dict, n_boot: int, seed: int, stat=np.mean):
    keys = list(vals_by_obj)
    if not keys:
        return float("nan"), float("nan"), float("nan")
    flat = [v for vs in vals_by_obj.values() for v in vs]
    mean = float(stat(flat)) if flat else float("nan")
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(len(keys), size=len(keys), replace=True)
        vs = [v for i in pick for v in vals_by_obj[keys[i]]]
        if vs:
            draws.append(stat(vs))
    lo, hi = (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))) \
        if draws else (float("nan"), float("nan"))
    return mean, lo, hi


def summarize(rows: list[dict], key: str = "correct", n_boot: int = 1000,
              seed: int = 0) -> dict:
    """Object-clustered mean + 95% CI of `key` over episodes."""
    by_obj: dict = {}
    for r in rows:
        by_obj.setdefault(r["obj"], []).append(float(r[key]))
    m, lo, hi = _cluster_boot(by_obj, n_boot, seed)
    return {"mean": m, "lo": lo, "hi": hi, "n": len(rows),
            "n_obj": len(by_obj)}


def chance_level(rows: list[dict]) -> float:
    """1 / (n_rooms + 1) — rooms plus the ELSEWHERE option, the option-set size."""
    if not rows:
        return float("nan")
    n = np.mean([r["n_rooms"] + 1 for r in rows])
    return 1.0 / n


def chance_corrected(rows: list[dict], n_boot: int = 1000, seed: int = 0) -> dict:
    """(acc - chance)/(1 - chance), object-clustered — the only accuracy LEVEL
    that may be pooled across scenes (C2)."""
    ch = chance_level(rows)
    by_obj: dict = {}
    for r in rows:
        by_obj.setdefault(r["obj"], []).append((r["correct"] - ch) / (1 - ch))
    m, lo, hi = _cluster_boot(by_obj, n_boot, seed)
    return {"mean": m, "lo": lo, "hi": hi, "chance": ch, "n": len(rows)}


def gap(rows_a: list[dict], rows_b: list[dict], key: str = "correct",
        n_boot: int = 1000, seed: int = 0) -> dict:
    """Paired per-object gap a−b (C2: pool gaps, not levels). Objects are the
    shared cluster unit; episodes matched by (obj, t_seen, t_query)."""
    def idx(rows):
        d: dict = {}
        for r in rows:
            d[(r["obj"], r["t_seen"], r["t_query"])] = r
        return d
    A, B = idx(rows_a), idx(rows_b)
    shared = set(A) & set(B)
    by_obj: dict = {}
    for k in shared:
        by_obj.setdefault(k[0], []).append(float(A[k][key]) - float(B[k][key]))
    m, lo, hi = _cluster_boot(by_obj, n_boot, seed)
    return {"gap": m, "lo": lo, "hi": hi, "n_pairs": len(shared),
            "n_obj": len(by_obj), "sig": bool(lo > 0 or hi < 0)}


def looks_by_stratum(rows: list[dict], stratum_of: dict) -> dict:
    """Mean looks per volatility stratum + the 'wasted looks on stable objects'
    figure (brief: over-sensing = the dual failure)."""
    by: dict = {}
    for r in rows:
        by.setdefault(stratum_of.get(r["obj"], "?"), []).append(r["looks_spent"])
    out = {s: round(float(np.mean(v)), 3) for s, v in by.items()}
    out["wasted_looks_on_stable"] = out.get("static", 0.0)
    return out


def abstention(rows: list[dict], n_boot: int = 1000, seed: int = 0) -> dict:
    """ELSEWHERE as a binary abstain decision (AbstainEQA). should_abstain =
    object truly in no sensable room. Precision = of ELSEWHERE answers, frac
    correct; Recall = of truly-elsewhere, frac answered ELSEWHERE;
    over_abstention = ELSEWHERE answered when object WAS in a room (1-precision
    event), the lazy-escape-hatch failure."""
    tp = sum(1 for r in rows if r["answered_elsewhere"] and r["is_elsewhere"])
    fp = sum(1 for r in rows if r["answered_elsewhere"] and not r["is_elsewhere"])
    fn = sum(1 for r in rows if not r["answered_elsewhere"] and r["is_elsewhere"])
    n_abst = tp + fp
    n_true = tp + fn
    prec = tp / n_abst if n_abst else float("nan")
    rec = tp / n_true if n_true else float("nan")
    f1 = (2 * prec * rec / (prec + rec)) if (n_abst and n_true and prec + rec > 0) else float("nan")
    looks_elsewhere = [r["looks_spent"] for r in rows
                       if r["answered_elsewhere"] and r["is_elsewhere"]]
    return {"precision": round(prec, 3) if n_abst else None,
            "recall": round(rec, 3) if n_true else None,
            "f1": round(f1, 3) if (n_abst and n_true) else None,
            "over_abstention_rate": round(fp / max(1, len(rows)), 3),
            "n_elsewhere_true": n_true, "n_elsewhere_answered": n_abst,
            "looks_to_elsewhere": round(float(np.mean(looks_elsewhere)), 3)
            if looks_elsewhere else None}


def by_transition(rows: list[dict], n_boot: int = 1000, seed: int = 0) -> dict:
    """Accuracy split by n_transitions_in_interval (0 vs >=1) — the same axis
    where passive Stage-1 b3 wins (cross-consistency check)."""
    z = [r for r in rows if r["n_transitions_in_interval"] == 0]
    p = [r for r in rows if r["n_transitions_in_interval"] >= 1]
    return {"no_transition": summarize(z, n_boot=n_boot, seed=seed) if z else None,
            "transition_inside": summarize(p, n_boot=n_boot, seed=seed) if p else None}
