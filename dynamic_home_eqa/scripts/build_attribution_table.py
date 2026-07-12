#!/usr/bin/env python3
"""
build_attribution_table.py — aggregate every milestone's result file
(embodied_results/<milestone>_result.json, written by
embodied.attribution.rerun_frozen_e0) into one attribution table.

Fails loudly, not silently, if any two result files disagree on
fingerprint: the whole point of freezing a config (experiment_config.FROZEN)
is that every milestone's row is directly comparable because nothing else
changed. A mismatch means some rerun used a stale config (e.g. before the
navmesh-connectivity phase's climb fix, or a stale FROZEN_LABELS) and
mixing it into the same table would silently misattribute that
milestone's effect.

Also fails loudly on a code_hash mismatch (embodied.attribution.
behavior_code_hash() — a hash of policy.py/belief.py/posterior.py/
scoring.py's byte contents, stamped into every result file by rerun_
frozen_e0/rerun_frozen_state_e0). FrozenConfig.fingerprint() only covers
scene/data/sampling parameters; it does not change when the DECISION or
BELIEF code changes. The coverage-repair phase's own calibration-space
fix (embodied/belief.py's calibrate_conformal_theta) changed conformal_
decay_threshold's behavior under an UNCHANGED fingerprint — only a
voluntary full-table rebuild kept embodied_results/ consistent that
time. code_hash closes that hole mechanically instead of relying on
someone remembering to rebuild.

Does not require habitat_sim — reads only the JSON result files milestone
gate scripts already wrote.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import summarize_rows


def load_results(results_dir: pathlib.Path) -> list[dict]:
    """Every *_result.json directly under results_dir (not stale/ or any
    other subfolder — a superseded result must be moved aside, per the
    navmesh-connectivity phase's own instruction, not left next to the
    live ones for this loader to accidentally pick up)."""
    return [
        json.loads(p.read_text())
        for p in sorted(results_dir.glob("*_result.json"))
    ]


def check_fingerprints(results: list[dict]) -> str:
    """Every result file must share one fingerprint — the frozen config's
    hash of scene/profile/folders/labels/wait_hours/patrol_start/seed/
    navmesh. Raises with a detailed diff, rather than silently aggregating
    mismatched configs into one table, if they don't."""
    if not results:
        raise ValueError("no result files found — nothing to build a table from")

    fingerprints = {r["fingerprint"] for r in results}
    if len(fingerprints) > 1:
        lines = ["Fingerprint mismatch across milestone result files — refusing to build a table:"]
        for r in results:
            lines.append(f"  {r['milestone']}: fingerprint={r['fingerprint']}")
        lines.append("A milestone reran under a different config than the others (e.g. a stale "
                      "FROZEN_LABELS, a navmesh setting change) — move the stale result file to "
                      "archive/embodied_results_stale/ and rerun that milestone's gate under the current "
                      "experiment_config.FROZEN before building this table.")
        raise ValueError("\n".join(lines))
    return fingerprints.pop()


def check_code_hashes(results: list[dict]) -> str:
    """Every result file must share one code_hash (embodied.attribution.
    behavior_code_hash() — the byte contents of policy.py/belief.py/
    posterior.py/scoring.py) — same fatal semantics as check_fingerprints,
    but for the decision/belief code rather than the experiment config. A
    result file written before this guard existed has no "code_hash" key
    at all; that absence is treated as its own distinct value ("<missing>"),
    not silently skipped — it must be regenerated before joining a table
    with files that do have one, exactly like a real mismatch."""
    if not results:
        raise ValueError("no result files found — nothing to build a table from")

    code_hashes = {r.get("code_hash", "<missing>") for r in results}
    if len(code_hashes) > 1:
        lines = ["Code-hash mismatch across milestone result files — refusing to build a table:"]
        for r in results:
            lines.append(f"  {r['milestone']}: code_hash={r.get('code_hash', '<missing>')}")
        lines.append("A milestone's result file was produced by different policy/belief/posterior/"
                      "scoring code than the others (or predates this guard, reported as <missing>) "
                      "— a behavior change under an unchanged FrozenConfig.fingerprint() (e.g. the "
                      "coverage-repair phase's calibration-space fix) would otherwise go undetected. "
                      "Move the stale result file to archive/embodied_results_stale/ and rerun that "
                      "milestone's gate before building this table.")
        raise ValueError("\n".join(lines))
    return code_hashes.pop()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", default=str(_DYNAMIC_EQA / "embodied_results"))
    args = ap.parse_args()

    results_dir = pathlib.Path(args.results_dir)
    results = load_results(results_dir)
    fingerprint = check_fingerprints(results)
    code_hash = check_code_hashes(results)
    print(f"All {len(results)} milestone result file(s) share fingerprint {fingerprint} and code_hash {code_hash}.\n")

    all_rows = [row for r in results for row in r["rows"]]
    summaries = summarize_rows(all_rows)

    header = f"{'milestone':<10} {'policy':<20} {'wait_h':>6} {'n':>4} {'acc':>6} {'brier':>7} {'ece':>7} {'abstain':>8}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(f"{s['milestone']:<10} {s['policy']:<20} {s['wait_hours']:>6.2f} {s['n']:>4d} "
              f"{s['accuracy']:>6.3f} {s['mean_brier']:>7.3f} {s['ece']:>7.3f} {s['abstain_rate']:>8.2f}")


if __name__ == "__main__":
    main()
