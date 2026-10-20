#!/usr/bin/env python3
"""
e2_preliminary_report.py — Results-First batch, item 1: aggregate whatever
scenes e2_preliminary_sweep.py has finished into a headline comparison.

Reuses scripts/e2_headline_comparison.py's own clustered-statistics
machinery unchanged (headline_table, stratified_decomposition,
bootstrap_over_clusters, cluster_key) — with real multiple scenes now
available (not the single-scene rehearsal), bootstrap CIs over scene-day
clusters are meaningful for the first time, not degenerate by
construction.

Every output is labeled PRELIMINARY: this reads whatever per-scene result
files exist in embodied_results/diagnostics/ at the time it is run, which
may be a subset of the full discovered scene list if e2_preliminary_
sweep.py is still running or was stopped early — the scene count actually
included is reported explicitly, not silently padded or implied complete.

Does not require habitat_sim — reads only existing JSON result files.
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.scripts.e0_mechanism_decomposition import Outcome, classify
from dynamic_home_eqa.scripts.e2_headline_comparison import (
    _fmt_ci,
    headline_table,
    stratified_decomposition,
    write_csv,
    write_frontier_plots,
)

_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"
_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
_TAG = "PRELIMINARY"


def load_results() -> list[dict]:
    return [
        json.loads(p.read_text())
        for p in sorted(_DIAGNOSTICS_DIR.glob("e2_preliminary_*_result.json"))
    ]


_SHARED_CONFIG_FIELDS = ("wait_hours_sweep", "patrol_start", "seed", "navmesh")


def check_consistency(results: list[dict]) -> str:
    """code_hash (the behavior-bearing modules) must be identical across
    every per-scene result file, the same fatal semantics build_
    attribution_table.py already applies. FrozenConfig.fingerprint()
    itself is NOT checked for equality here — unlike the single-scene
    attribution table, a fingerprint legitimately (and correctly) differs
    per scene, since it hashes scene/profile/folders/labels along with
    the shared experiment parameters. What must match across scenes is
    only the SHARED design (wait_hours_sweep, patrol_start, seed,
    navmesh) — checked separately below — and the code that ran."""
    if not results:
        raise ValueError("no per-scene result files found under embodied_results/diagnostics/ — "
                          "run scripts/e2_preliminary_sweep.py first")
    code_hashes = {r["code_hash"] for r in results}
    if len(code_hashes) > 1:
        raise ValueError(f"Code-hash mismatch across per-scene result files: {code_hashes}")

    for field in _SHARED_CONFIG_FIELDS:
        values = {repr(r["config"][field]) for r in results}
        if len(values) > 1:
            raise ValueError(f"Shared config field {field!r} differs across per-scene result files: {values}")

    return code_hashes.pop()


def main() -> None:
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results = load_results()
    code_hash = check_consistency(results)

    scenes = sorted({r["config"]["scene"] for r in results})
    rows = [row for r in results for row in r["rows"]]
    print(f"Aggregating {len(results)} scene(s), {len(rows)} row(s): {scenes}")
    print(f"code_hash={code_hash} (per-scene fingerprints differ by design — see check_consistency)")

    headline = headline_table(rows)
    decomposition = stratified_decomposition(rows)

    print(f"\n{'policy':<26}{'hazard':<10}{'qtype':<10}{'n':>5}  accuracy")
    for r in headline:
        print(f"{r['policy']:<26}{r['hazard_class']:<10}{r['question_type']:<10}{r['n_rows']:>5}  {_fmt_ci(r['accuracy'])}")

    tag = f"_{_TAG}"
    csv_path = _REPORTS_DIR / f"e2{tag}_headline.csv"
    write_csv(headline, csv_path)
    print(f"\nWrote {csv_path}")

    import csv as _csv
    decomp_path = _REPORTS_DIR / f"e2{tag}_mechanism_decomposition.csv"
    all_transition_keys = sorted({k for row in decomposition for k in row if k not in ("policy", "hazard_class")})
    with open(decomp_path, "w", newline="") as f:
        writer = _csv.DictWriter(f, fieldnames=["policy", "hazard_class"] + all_transition_keys)
        writer.writeheader()
        for row in decomposition:
            writer.writerow({**{k: 0 for k in all_transition_keys}, **row})
    print(f"Wrote {decomp_path}")

    write_frontier_plots(headline, _REPORTS_DIR, rehearsal=True)
    # write_frontier_plots names files with the REHEARSAL tag (its own
    # module constant) — rename to the PRELIMINARY tag so the
    # two phases' outputs are never confused in the reports directory.
    for name in ("e2_frontier_accuracy_vs_latency", "e2_frontier_accuracy_vs_travel"):
        src = _REPORTS_DIR / f"{name}_REHEARSAL.png"
        dst = _REPORTS_DIR / f"{name}_{_TAG}.png"
        if src.exists():
            src.rename(dst)
    print(f"Wrote frontier plots to {_REPORTS_DIR}")

    n_degenerate = sum(1 for r in headline if r["accuracy"].degenerate)
    print(f"\n{len(scenes)} scene(s) included of the full discovered set — see pool_status.md for total. "
          f"{n_degenerate}/{len(headline)} (policy, hazard, question_type) cells have n_clusters<2 "
          f"('no CI possible' is the honest report, not a bug, for those).")


if __name__ == "__main__":
    main()
