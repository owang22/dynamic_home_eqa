#!/usr/bin/env python3
"""
analyze_realism_study.py — reads webapp/realism_eval's SQLite DB and
computes the three things Step 3 of the human-eval instructions asked
for: inter-annotator agreement per rubric axis, human-vs-automatic
correlation per axis vs per signal, and overall quality rates (the
suspicion-stratum split this used to be reported per-stratum against was
removed along with the suspicion-scoring machinery that fed it — every
response in the pool is now a uniform random sample, so there's no
biased/unbiased distinction left to stratify by).

Design choices, stated rather than left implicit:

- Agreement is pairwise weighted (quadratic) Cohen's kappa, averaged
  across every annotator pair, not Krippendorff's alpha. The instructions
  offered either; under ASSIGNMENT_MODE="shared" every annotator rates
  the identical item set (no missing-data pattern to reconcile, which is
  alpha's main advantage over kappa), so pairwise kappa is simpler to
  implement correctly and equivalent in what it measures here.
- Each ordinal axis's "cannot tell"/"cannot judge" escape value is
  EXCLUDED from the ordinal agreement/correlation computation (it isn't a
  point on the plausibility scale, it's a refusal to place one) and
  reported separately as its own rate. Folding it into the ordinal scale
  at either end would silently bias both kappa and correlation.
- Low agreement on an axis is reported as "this question is ill-posed
  for this item set", not averaged away or hidden — this script never
  drops an axis from the report for scoring badly.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
from collections import defaultdict
from itertools import combinations
from typing import Optional

import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

_DEFAULT_DB = _DYNAMIC_EQA / "results" / "realism_eval" / "realism_eval.db"

# Ordinal scales, escape values excluded (see module docstring).
ORDINAL_SCALES: dict[str, list[str]] = {
    "placement": ["clearly_wrong", "slightly_off", "resting_naturally"],
    "behavior": ["implausible", "unusual_but_possible", "plausible"],
    "visibility": ["not_visible", "visible_but_hard", "clearly_visible"],
}
ESCAPE_VALUES: dict[str, str] = {
    "placement": "cannot_tell",
    "behavior": "cannot_judge",
    "visibility": None,  # visibility has no escape value in this rubric
}
AUTOMATIC_SIGNALS = [
    "degenerate_viewpoint",
    "geometric_after_supported", "geometric_after_embedded",
    "deterministic_plausibility_confidence", "llm_self_graded_realism_day_mean",
]
# The rubric value each axis's "low quality" end maps to, for the
# overall headline rate.
LOW_QUALITY_VALUE = {"placement": "clearly_wrong", "behavior": "implausible"}


def load_responses(db_path: pathlib.Path, dataset_version: str) -> list[dict]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM responses_{dataset_version}").fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["issues"] = json.loads(d["issues"]) if d.get("issues") else []
        out.append(d)
    return out


def _ordinal_value(axis: str, raw: Optional[str]) -> Optional[int]:
    if raw is None or raw == ESCAPE_VALUES.get(axis):
        return None
    scale = ORDINAL_SCALES[axis]
    return scale.index(raw) if raw in scale else None


def escape_rate(responses: list[dict], axis: str) -> Optional[float]:
    escape = ESCAPE_VALUES.get(axis)
    if escape is None:
        return None
    vals = [r[axis] for r in responses if r.get(axis) is not None]
    if not vals:
        return None
    return sum(1 for v in vals if v == escape) / len(vals)


def pairwise_weighted_kappa(responses: list[dict], axis: str) -> dict:
    """Average pairwise quadratic-weighted Cohen's kappa across every
    annotator pair, computed only over items BOTH annotators rated with a
    non-escape value on this axis. Returns per-pair n and kappa too, not
    just the mean — a mean over pairs with very different n is misleading
    on its own."""
    by_participant: dict[str, dict[str, int]] = defaultdict(dict)
    for r in responses:
        v = _ordinal_value(axis, r.get(axis))
        if v is not None:
            by_participant[r["participant_id"]][r["item_id"]] = v

    participants = sorted(by_participant)
    pair_results = []
    for p1, p2 in combinations(participants, 2):
        shared = set(by_participant[p1]) & set(by_participant[p2])
        if len(shared) < 2:
            continue
        y1 = [by_participant[p1][i] for i in sorted(shared)]
        y2 = [by_participant[p2][i] for i in sorted(shared)]
        if len(set(y1)) == 1 and len(set(y2)) == 1 and y1[0] == y2[0]:
            kappa = 1.0  # perfect, degenerate agreement — cohen_kappa_score is undefined (0/0) here
        else:
            kappa = cohen_kappa_score(y1, y2, weights="quadratic", labels=list(range(len(ORDINAL_SCALES[axis]))))
        pair_results.append({"pair": (p1, p2), "n": len(shared), "kappa": kappa})

    if not pair_results:
        return {"n_pairs": 0, "mean_kappa": None, "pairs": [], "interpretation": "insufficient overlapping data"}

    mean_kappa = float(np.mean([p["kappa"] for p in pair_results]))
    return {
        "n_pairs": len(pair_results),
        "mean_kappa": mean_kappa,
        "pairs": pair_results,
        "interpretation": _interpret_kappa(mean_kappa),
    }


def _interpret_kappa(k: float) -> str:
    # Landis & Koch (1977) bands — standard, not invented for this script.
    if k < 0.0:
        return "no agreement (worse than chance) — this question is likely ill-posed for this item set"
    if k < 0.20:
        return "slight agreement — treat this axis's ratings as unreliable"
    if k < 0.40:
        return "fair agreement"
    if k < 0.60:
        return "moderate agreement"
    if k < 0.80:
        return "substantial agreement"
    return "almost perfect agreement"


def human_vs_automatic_correlation(responses: list[dict], axis: str, signal: str) -> dict:
    """Spearman rank correlation (robust to the automatic signals' very
    different scales — a 0/1 boolean vs a continuous score) between an
    ordinal rubric axis and one automatic signal, with a bootstrap 95% CI.
    Escape-value ratings are excluded (see module docstring)."""
    pairs = [
        (_ordinal_value(axis, r.get(axis)), r.get(signal))
        for r in responses
        if _ordinal_value(axis, r.get(axis)) is not None and r.get(signal) is not None
    ]
    if len(pairs) < 8:
        return {"n": len(pairs), "rho": None, "p": None, "ci95": None, "note": "too few paired observations"}

    xs = np.array([p[0] for p in pairs], dtype=float)
    ys = np.array([float(p[1]) for p in pairs])
    if np.std(xs) == 0 or np.std(ys) == 0:
        return {"n": len(pairs), "rho": None, "p": None, "ci95": None, "note": "no variance in one variable"}

    rho, p = stats.spearmanr(xs, ys)
    rng = np.random.default_rng(0)
    boots = []
    n = len(xs)
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        bx, by = xs[idx], ys[idx]
        if np.std(bx) == 0 or np.std(by) == 0:
            continue
        r, _ = stats.spearmanr(bx, by)
        boots.append(r)
    ci95 = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))) if boots else None

    return {"n": len(pairs), "rho": float(rho), "p": float(p), "ci95": ci95}


def overall_quality_rates(responses: list[dict]) -> dict:
    """The clearly-wrong / implausible fraction across the whole response
    set — the pool's headline quality number. Every response is now a
    uniform random sample (suspicion-based over-sampling of "risky-
    looking" events was removed), so this is no longer split by stratum;
    the whole pool has the property only the random_baseline stratum used
    to have."""
    entry = {"n_responses": len(responses)}
    for axis, low_value in LOW_QUALITY_VALUE.items():
        vals = [r[axis] for r in responses if r.get(axis) is not None]
        entry[f"{axis}_low_quality_rate"] = (
            sum(1 for v in vals if v == low_value) / len(vals) if vals else None
        )
    return entry


def build_report(db_path: pathlib.Path, dataset_version: str) -> dict:
    responses = load_responses(db_path, dataset_version)
    n_participants = len({r["participant_id"] for r in responses})

    agreement = {axis: pairwise_weighted_kappa(responses, axis) for axis in ORDINAL_SCALES}
    escape_rates = {axis: escape_rate(responses, axis) for axis in ORDINAL_SCALES if ESCAPE_VALUES.get(axis)}
    correlations = {
        axis: {signal: human_vs_automatic_correlation(responses, axis, signal) for signal in AUTOMATIC_SIGNALS}
        for axis in ORDINAL_SCALES
    }
    quality = overall_quality_rates(responses)

    return {
        "n_responses": len(responses),
        "n_participants": n_participants,
        "agreement": agreement,
        "escape_rates": escape_rates,
        "correlations": correlations,
        "quality": quality,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(_DEFAULT_DB))
    ap.add_argument("--dataset-version", default="v1")
    ap.add_argument("--out", default=str(_DYNAMIC_EQA / "results" / "reports" / "human_realism_study_analysis.json"))
    args = ap.parse_args()

    report = build_report(pathlib.Path(args.db), args.dataset_version)
    print(f"n_responses={report['n_responses']}  n_participants={report['n_participants']}")
    if report["n_responses"] == 0:
        print("No responses in the DB yet — nothing to analyze. This is expected before a real study runs; "
              "see results/reports/human_realism_study.md for the design and this script's own test suite "
              "for correctness evidence in the absence of real data.")
    for axis, agree in report["agreement"].items():
        print(f"  {axis}: mean kappa={agree['mean_kappa']}  ({agree['interpretation']})  n_pairs={agree['n_pairs']}")

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
