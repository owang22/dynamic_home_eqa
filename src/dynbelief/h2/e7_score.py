"""Granularity-split + deployment-weighted scoring of the enriched E7 rows.

Two reviewer moves:
  (2) Score at the granularity of the knowledge. The LLM's regime inference is
      room+timing level; a receptacle top-1 punishes it for precision it never
      claimed. Report room-level AND receptacle-level (AND top-3) accuracy.
  (3) Make the metric match the deployment story. The pooled-over-k curve dilutes
      the benefit with the mid-k tie region; deployment is cold-start / early-k.
      Report cold-start (k=0, "never-observed"), day-one (k≤2), and early-k AUC
      (k≤4) as headlines, with the full curve as honest context.

Consumes e7_rows_<label>.jsonl carrying per-query pred/true/top3_correct. Room map
from the manual profiles. Paired (LLM−C3g) reported at both granularities.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.profiles.schema import load_profile

EARLY_K = [k for k in e7.K_GRID if k <= 4]
DAYONE_K = [k for k in e7.K_GRID if 1 <= k <= 2]


def _room_of(base):
    m = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
    m["elsewhere"] = "elsewhere"
    return m


def _load(label):
    rows = [json.loads(l) for l in (core.OUT / f"e7_rows_{label}.jsonl").read_text().splitlines() if l.strip()]
    roommaps = {}
    for r in rows:
        base = r["hh"]
        if base not in roommaps:
            roommaps[base] = _room_of(base)
        rm = roommaps[base]
        r["room_correct"] = int(rm.get(r.get("pred"), "x") == rm.get(r.get("true"), "y"))
    return rows


def _cluster_means(rows, rar, model, ks, field):
    by = defaultdict(list)
    for r in rows:
        if r["rarity"] == rar and r["model"] == model and r["k"] in ks:
            by[(r["hh"], r["object"])].append(r[field])
    return {c: float(np.mean(v)) for c, v in by.items() if v}


def _boot_mean(vals, nb=4000, seed=9):
    if not vals:
        return (np.nan, np.nan, np.nan)
    a = np.array(vals); rng = np.random.default_rng(seed)
    m = [np.mean(a[rng.integers(0, len(a), len(a))]) for _ in range(nb)]
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _paired(rows, rar, llm, ks, field, nb=5000, seed=13):
    a = _cluster_means(rows, rar, llm, ks, field)
    b = _cluster_means(rows, rar, "classical_C3g", ks, field)
    clus = sorted(set(a) & set(b)); d = np.array([a[c]-b[c] for c in clus])
    if len(d) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    m = [np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(nb)]
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def report(label):
    rows = _load(label)
    fields = [("receptacle", "correct"), ("room", "room_correct"), ("top-3", "top3_correct")]
    regions = [("cold-start k=0 (never-observed)", [0]), ("day-one k≤2", DAYONE_K),
               ("early-k AUC k≤4", EARLY_K), ("all k", e7.K_GRID)]
    print("=" * 92)
    print(f"E7 granularity + deployment-weighted scoring   (model={label})")
    print("=" * 92)
    for rar, _, _ in e7.TERCILES:
        print(f"\n########## {rar.upper()} tercile ##########")
        for gname, field in fields:
            print(f"\n  granularity = {gname.upper()}")
            print(f"    {'region':32}{'LLM':>14}{'C3g':>14}{'paired Δ (95% CI)':>26}")
            for rname, ks in regions:
                lm, llo, lhi = _boot_mean([v for vs in _cluster_means(rows, rar, label, ks, field).values() for v in [vs]])
                cm, clo, chi = _boot_mean([v for vs in _cluster_means(rows, rar, "classical_C3g", ks, field).values() for v in [vs]])
                dm, dlo, dhi = _paired(rows, rar, label, ks, field)
                sig = " *" if (dlo > 0 or dhi < 0) else ""
                print(f"    {rname:32}{lm:>14.2f}{cm:>14.2f}"
                      f"{f'{dm:+.3f} [{dlo:+.2f},{dhi:+.2f}]':>26}{sig}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--headline", action="store_true", help="compact cross-stratum headline table")
    args = ap.parse_args()
    if args.headline:
        headline(args.label)
    else:
        report(args.label)


def headline(label):
    """One compact table: room-level cold-start & early-k paired gap per stratum."""
    rows = _load(label)
    print("=" * 78)
    print(f"HEADLINE — room-level LLM advantage (paired LLM−C3g), model={label}")
    print("=" * 78)
    print(f"  {'stratum':10}{'cold-start Δ (k=0)':>26}{'early-k Δ (k≤4)':>26}")
    for rar, _, _ in e7.TERCILES:
        c = _paired(rows, rar, label, [0], "room_correct")
        e = _paired(rows, rar, label, EARLY_K, "room_correct")
        f = lambda t: f"{t[0]:+.2f} [{t[1]:+.2f},{t[2]:+.2f}]" + (" *" if (t[1] > 0 or t[2] < 0) else "")
        print(f"  {rar:10}{f(c):>26}{f(e):>26}")


if __name__ == "__main__":
    main()
