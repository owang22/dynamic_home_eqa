"""Change 3 — precision-weighted fusion: alpha ESTIMATED, never set.

alpha/(alpha+n) is the exact Beta/Dirichlet posterior weight of a prior worth
alpha pseudo-observations against n real ones — the functional form is not the
problem; the hand-tuned alpha is. Three tiers replace the dev-set alpha search:

  Tier 1  alpha* estimated from the prior's TRACK RECORD on the dev bank: the
          LLM regime prior's held-out hit rate is converted to the effective
          observation count k whose Beta posterior would match that reliability.
          alpha* is an EMPIRICAL QUANTITY ("the prior is worth ~alpha* obs"),
          not a hyperparameter.
  Tier 2  alpha varies per edge with the CounterfactCoT do-contrast (Change 2):
          alpha_edge = contrast_edge * alpha* / mean_dev_contrast, so the
          dev-bank average matches Tier 1. Contingent on the Change-2
          calibration plot passing; else fall back to Tier 1.
  Tier 3  (PRIMARY) blend DISTRIBUTIONS at the ACTIVITY-NODE level. The
          statistical channel's pooled f_activity(t) carries an effective event
          count n_g (group precision, activity_graph.group_neff); the LLM prior
          over the object's location is a distribution whose precision comes
          from the do-contrast. Precision-weighted (conjugate) combination:

              p_fused = (kappa * prior + n_g * p_data) / (kappa + n_g)

          which IS alpha/(alpha+n) with alpha = kappa (prior precision) and
          n = n_g (data precision) — alpha emerges from the ratio, never set.

  HONESTY (do not skip): the two precisions are NOT in the same units by
  default. The LLM prior's spread and the statistical posterior's variance live
  on different scales, so naive inverse-variance combination silently
  mis-weights by the unit mismatch. Tier 3 therefore carries EXACTLY ONE
  calibration constant U (prior-precision -> data-event units), fit on the DEV
  bank so the prior's average worth matches its Tier-1 measured reliability:
  kappa_edge = U * contrast_edge, with U chosen so mean(kappa) == alpha*.
  Tier 3 is not parameter-free — it replaces a free mixing hyperparameter with
  one interpretable, dev-calibrated unit-conversion constant, reported with its
  observation-count interpretation.
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np


# ── Tier 1: alpha* from the prior's dev-bank track record ────────────────────

def alpha_star_from_track_record(hit_rate: float, n_cands_mean: float) -> float:
    """Convert the LLM prior's held-out hit rate into an effective observation
    count. Model: a Dirichlet(1) belief updated by k observations of the true
    receptacle gives the true cell posterior mass (1+k)/(C+k). Solve
    (1+k)/(C+k) = hit_rate for k:  k = (C*h - 1)/(1 - h). This is the k whose
    posterior would be exactly as reliable as the prior empirically is."""
    h = min(0.95, max(1.0 / n_cands_mean + 1e-6, float(hit_rate)))
    return max(0.5, (n_cands_mean * h - 1.0) / (1.0 - h))


def tier1_alpha(dev_rows: list[dict], n_cands_mean: float) -> dict:
    """dev_rows: llm_direct rows from the dev bank (with 'correct'). Returns
    {'alpha_star', 'hit_rate', 'n'} — alpha* reported as an empirical quantity."""
    hits = [r["correct"] for r in dev_rows]
    h = float(np.mean(hits)) if hits else 0.0
    return {"alpha_star": round(alpha_star_from_track_record(h, n_cands_mean), 2),
            "hit_rate": round(h, 4), "n": len(hits)}


# ── Tier 2/3: contrast-scaled per-edge alpha (one unit constant U) ───────────

def unit_constant(alpha_star: float, dev_contrasts: list[float]) -> float:
    """U converts contrast (unitless, [0,1]) into pseudo-observations, fit so
    the DEV-bank mean alpha matches Tier-1 alpha*. THE one calibration constant."""
    m = float(np.mean(dev_contrasts)) if dev_contrasts else 0.0
    return alpha_star / m if m > 1e-6 else alpha_star


def kappa_edge(U: float, contrast: float) -> float:
    """Per-edge prior precision in data-event units."""
    return max(0.0, U * float(contrast))


# ── Tier 3: activity-node distribution blend ─────────────────────────────────

def fuse_distribution(prior: dict[str, float], p_data: dict[str, float] | None,
                      kappa: float, n_g: float, cand_set: list[str]) -> dict[str, float]:
    """Precision-weighted conjugate blend of the prior distribution (LLM,
    precision kappa) with the data distribution (pooled activity fit, precision
    n_g = group effective event count). n_g=0 or no data dist -> pure prior;
    kappa=0 -> pure data. This IS alpha/(alpha+n) with alpha=kappa, n=n_g."""
    pz = sum(max(0.0, prior.get(c, 0.0)) for c in cand_set)
    pr = {c: (max(0.0, prior.get(c, 0.0)) / pz if pz > 0 else 1.0 / len(cand_set))
          for c in cand_set}
    if p_data is None or n_g <= 0:
        return pr
    dz = sum(max(0.0, p_data.get(c, 0.0)) for c in cand_set)
    pd = {c: (max(0.0, p_data.get(c, 0.0)) / dz if dz > 0 else 1.0 / len(cand_set))
          for c in cand_set}
    tot = kappa + n_g
    if tot <= 0:
        return pd
    return {c: (kappa * pr[c] + n_g * pd[c]) / tot for c in cand_set}


class PrecisionFusedRM:
    """C3g-compatible wrapper: base rate model (classical or activity-tied) with
    the TARGET object's occupancy replaced by the Tier-3 blend of the LLM prior
    distribution and the base model's own distribution, weighted kappa vs n_g.

    n_g comes from the activity group when the base is ActivityTiedRates (so the
    prior fades as the GROUP accumulates events — rare tied objects benefit
    before any single one would); for a classical base it falls back to the
    object's own event count."""

    def __init__(self, base, obj: str, prior: dict[str, float], kappa: float,
                 n_g: float):
        self.base, self.obj = base, obj
        self.candidates = base.candidates
        self._prior, self._kappa, self._ng = prior, float(kappa), float(n_g)

    def occupancy(self, o: str, r: str, t: int) -> float:
        if o != self.obj:
            return self.base.occupancy(o, r, t)
        p_data = {c: self.base.occupancy(o, c, t) for c in self.candidates}
        fused = fuse_distribution(self._prior, p_data, self._kappa, self._ng,
                                  self.candidates)
        return float(fused.get(r, 0.0))

    def rate(self, o: str, r: str, t: int) -> float:
        return self.base.rate(o, r, t)
