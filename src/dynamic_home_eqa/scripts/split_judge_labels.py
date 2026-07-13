#!/usr/bin/env python3
"""
split_judge_labels.py — Phase 1.1.4: split the returned human-labeled
candidate set into EVAL (~48) and EXEMPLAR (~12), deterministically by a
recorded seed. EXEMPLAR is reserved for Phase-2 few-shot and is permanently
excluded from every metric (no leakage). Also prints human-vs-machine
agreement so the over-scoring the harness will quantify is visible now.

Writes results/judge_label_set/split_manifest.json (the seed + the exact
EVAL/EXEMPLAR id lists the harness loads).

Usage:
    python -m dynamic_home_eqa.scripts.split_judge_labels
    python -m dynamic_home_eqa.scripts.split_judge_labels --seed 0 --n-exemplar 12
"""
from __future__ import annotations

import argparse
import collections
import pathlib

from dynamic_home_eqa.judge_eval.labels import (
    load_labeled_csv, split_eval_exemplar, write_split,
)
from dynamic_home_eqa.judge_eval.metrics import BAND_LABEL
from dynamic_home_eqa.paths import REPO_ROOT

_DEFAULT_CSV = "results/judge_label_set/labeled_candidates.csv"
_DEFAULT_OUT = "results/judge_label_set"


def _agreement_report(cands) -> None:
    n = len(cands)
    exact = sum(1 for c in cands if c.machine_band == c.human_band)
    over = sum(1 for c in cands if c.machine_band > c.human_band)
    under = sum(1 for c in cands if c.machine_band < c.human_band)
    hh = collections.Counter(c.human_band for c in cands)
    mm = collections.Counter(c.machine_band for c in cands)
    print(f"\nHuman-vs-machine band agreement (n={n}):")
    print(f"  exact match     : {exact}/{n} ({exact/n:.0%})")
    print(f"  machine HIGHER  : {over}/{n} ({over/n:.0%})   <- the judge's known over-scoring")
    print(f"  machine LOWER   : {under}/{n} ({under/n:.0%})")
    print("  band distribution (band: human / machine):")
    for b in (3, 2, 1, 0):
        print(f"    {b} {BAND_LABEL[b]:<20}: {hh.get(b,0):>2} / {mm.get(b,0):>2}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=_DEFAULT_CSV)
    ap.add_argument("--out-dir", default=_DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-exemplar", type=int, default=12)
    args = ap.parse_args()

    csv_path = pathlib.Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = REPO_ROOT / csv_path
    out_dir = pathlib.Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir

    cands = load_labeled_csv(csv_path)
    print(f"loaded {len(cands)} labeled candidates from {csv_path.name}")
    _agreement_report(cands)

    eval_set, exemplar = split_eval_exemplar(cands, seed=args.seed, n_exemplar=args.n_exemplar)
    write_split(eval_set, exemplar, args.seed, out_dir, csv_path)

    import collections as _c
    ev_bands = _c.Counter(c.human_band for c in eval_set)
    ex_bands = _c.Counter(c.human_band for c in exemplar)
    n_dl = sum(1 for c in exemplar if c.is_dinner_laptop)
    print(f"\nsplit (seed={args.seed}):")
    print(f"  EVAL     : {len(eval_set)}  bands " + " ".join(f"{b}={ev_bands.get(b,0)}" for b in (3,2,1,0)))
    print(f"  EXEMPLAR : {len(exemplar)}  bands " + " ".join(f"{b}={ex_bands.get(b,0)}" for b in (3,2,1,0))
          + f"  (dinner-laptop cases: {n_dl})")
    print(f"  wrote {out_dir / 'split_manifest.json'}")


if __name__ == "__main__":
    main()
