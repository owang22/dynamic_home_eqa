"""VERSION22 expanded-bank analysis (Change 0): paired-difference presentation.

The binding constraint on the day-14 arm comparison was cluster count: 12
households -> 36 (household x object) clusters, unbalanced across rarity terciles
(rare 18 / medium 8 / frequent 10). This expands the base with 3 NEW confusable
pairs x 2 seed-instances (version22b, 12 households -> 24), lifting the pooled
count to >=15 clusters in every tercile.

Two presentations, reported side by side:
  1. OLD bank (frozen version22, 12 hh) vs EXPANDED (version22 + version22b, 24 hh),
     day-14 accuracy per arm with clustered bootstrap CIs — shows the band shrink.
  2. PAIRED per-cluster difference (default): for each (household, object) cluster,
     the mean day-14 accuracy of arm A minus arm B on the SAME cluster, then a
     clustered bootstrap CI on that per-cluster Delta. This cancels between-household
     variance (the dominant noise source) and is the CI-separated presentation.

Pooling: rows carry `bank`, `hh`, `object`, so old vs expanded is just a filter on
which row-files load. version22 stays frozen (its files are never rewritten).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

from dynbelief.reflect.run import OUT

# frozen 12-household base + the 24-household expansion (12 base + 12 new)
OLD_TAG, NEW_TAG = "v22", "v22b"
ARMS = ["llm_direct", "llm_surprise", "llm_nomem", "fusion", "classical_C3g", "classical_C1"]
PRETTY = {"llm_direct": "LLM nightly", "llm_surprise": "LLM surprise-gated",
          "llm_nomem": "LLM raw digest", "fusion": "fusion", "classical_C3g": "classical C3g",
          "classical_C1": "classical C1"}


def _load(tag, level):
    """All rows for a bank tag at a distractor level (nightly/classical/fusion
    from all_rows_* + the surprise arm from rows_surprise_*)."""
    out = []
    p = OUT / f"all_rows_{tag}_distractor_d{level}.jsonl"
    if p.exists():
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    p = OUT / f"rows_surprise_{tag}_surprise_d{level}.jsonl"
    if p.exists():
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


def _rows(level, expanded: bool):
    """OLD = frozen 12hh (v22). EXPANDED = v22 + v22b (24hh). hh ids are disjoint
    across banks (v22b uses "__i{n}" instances), so pooling is a clean union."""
    rows = _load(OLD_TAG, level)
    if expanded:
        rows = rows + _load(NEW_TAG, level)
    return rows


def _cluster_means(rows, arm, field, ckpt=14):
    """mean of `field` per (hh, object) cluster for one arm at one checkpoint."""
    by = defaultdict(list)
    for r in rows:
        if r["model"] == arm and r["ckpt"] == ckpt:
            by[(r["hh"], r["object"])].append(r[field])
    return {k: float(np.mean(v)) for k, v in by.items() if v}


def _boot_ci(vals, nb=5000, seed=11):
    if not vals:
        return (float("nan"),) * 3
    rng = np.random.default_rng(seed)
    v = np.asarray(vals)
    m = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(nb)]
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def unpaired_table(level, field="correct"):
    lab = "RECEPTACLE" if field == "correct" else "ROOM"
    print("=" * 92)
    print(f"OLD (12hh) vs EXPANDED (24hh) — day-14 {lab} accuracy, clustered bootstrap 95% CI "
          f"(distractors={level})")
    print("=" * 92)
    print(f"  {'arm':20s}{'OLD n_clu':>10}{'OLD acc [CI]':>22}{'EXP n_clu':>11}{'EXP acc [CI]':>22}")
    for arm in ARMS:
        cells = []
        for expanded in (False, True):
            cm = _cluster_means(_rows(level, expanded), arm, field)
            if not cm:
                cells.append((0, None)); continue
            cells.append((len(cm), _boot_ci(list(cm.values()))))
        (no, oci), (ne, eci) = cells
        def fmt(ci):
            return "-" if ci is None else f"{ci[0]:.2f} [{ci[1]:.2f},{ci[2]:.2f}]"
        print(f"  {PRETTY[arm]:20s}{no:>10}{fmt(oci):>22}{ne:>11}{fmt(eci):>22}")


def paired_table(level, field="correct", baseline="llm_direct"):
    """Per-cluster Delta (arm - baseline) at day 14, clustered bootstrap CI on the
    Delta. Only clusters where BOTH arms have data are used (true pairing)."""
    lab = "RECEPTACLE" if field == "correct" else "ROOM"
    print("\n" + "=" * 92)
    print(f"PAIRED per-cluster Delta vs {PRETTY[baseline]} — day-14 {lab}, clustered bootstrap 95% CI "
          f"(distractors={level})")
    print(f"  (Delta>0 => arm beats {PRETTY[baseline]} on the same household-object; CI excluding 0 = separated)")
    print("=" * 92)
    for expanded in (False, True):
        tag = "EXPANDED 24hh" if expanded else "OLD 12hh"
        rows = _rows(level, expanded)
        base = _cluster_means(rows, baseline, field)
        print(f"\n  [{tag}]   n_clusters(baseline)={len(base)}")
        print(f"    {'arm':20s}{'n_paired':>9}{'mean Delta [95% CI]':>26}{'':>6}")
        for arm in ARMS:
            if arm == baseline:
                continue
            am = _cluster_means(rows, arm, field)
            deltas = [am[k] - base[k] for k in am if k in base]
            if not deltas:
                continue
            m, lo, hi = _boot_ci(deltas)
            sep = "  * CI>0" if lo > 0 else ("  * CI<0" if hi < 0 else "")
            print(f"    {PRETTY[arm]:20s}{len(deltas):>9}{f'{m:+.3f} [{lo:+.3f},{hi:+.3f}]':>26}{sep}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=6,
                    help="distractor level to analyze (0/3/6/12)")
    ap.add_argument("--baseline", default="llm_direct")
    args = ap.parse_args()
    for field in ("correct", "room_correct"):
        unpaired_table(args.level, field)
        paired_table(args.level, field, args.baseline)
        print()


if __name__ == "__main__":
    main()
