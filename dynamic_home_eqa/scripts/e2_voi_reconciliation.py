#!/usr/bin/env python3
"""
e2_voi_reconciliation.py — decay_voi reconciliation batch: explains E2
preliminary's headline accuracy gap (decay_voi 0.438 vs answer_immediately
0.366 vs always_resense 0.510 on volatile-location) at the paired-question
level, using only the logs scripts/e2_preliminary_sweep.py already wrote —
no reruns.

Four things, over the volatile-location stratum:

1. Paired per-question reconciliation: every (scene, eval_folder,
   wait_hours, label) question, decay_voi vs answer_immediately, bucketed
   into (a) identical outcome with no travel and no abstain-divergence,
   (b) decay_voi traveled and the outcome differs, (c) decay_voi abstained
   where the floor answered, (d) neither of the above yet the outcome
   differs anyway — which would indicate a determinism/belief-divergence
   bug and must be empty or escalated before anything else here is trusted.
2. Per-policy abstain rate and accuracy computed two ways (of-non-abstained,
   the number already in e2_preliminary.md; and of-all-questions, scoring
   an abstain at ScoringConfig's own r_abstain=0.5) — the gap between the
   two is the denominator effect selective abstention alone would produce.
3. Clustered (over scene) bootstrap CIs on the three headline accuracy
   numbers and on the paired deltas (decay_voi - answer_immediately,
   decay_voi - always_resense), resampling scene indices once per
   iteration and applying the same resample to both series in a pair
   (not two independent bootstraps) — the statistically correct way to
   ask whether a paired difference excludes zero.
4. A flip-attribution audit: while building bucket (b) above, cross-
   checking against scripts/e2_headline_comparison.py's stratified_
   decomposition() and scripts/e0_mechanism_decomposition.py's decompose()
   guards against a counting bug — both functions paired trials by
   (policy, wait_hours, label) without scene/eval_folder, so on this
   multi-scene pool a generic label recurring across scenes (extremely
   common — "book_1", "candle_1", etc.) silently collapsed onto one
   scene's trial, dropping the rest. Confirmed: 505 answer_immediately
   volatile-location trials collapsed to 70 distinct (wait_hours, label)
   keys before the fix. Fixed in both functions (scene/eval_folder added
   to the pairing key); this script reports the corrected counts.

Does not require habitat_sim — reads only existing JSON result files.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
from dataclasses import dataclass

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.scoring import ScoringConfig
from dynamic_home_eqa.scripts.e2_headline_comparison import cluster_key, stratified_decomposition

_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"
_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
_N_BOOTSTRAP = 2000
_BOOTSTRAP_SEED = 0
_R_ABSTAIN = ScoringConfig().r_abstain


def load_rows(question_type: str = "location", hazard_class: str = "volatile") -> list[dict]:
    rows = []
    for p in sorted(_DIAGNOSTICS_DIR.glob("e2_preliminary_*_result.json")):
        d = json.loads(p.read_text())
        rows.extend(r for r in d["rows"] if r["question_type"] == question_type and r["hazard_class"] == hazard_class)
    return rows


def question_key(row: dict) -> tuple[str, str, float, str]:
    return (row["scene"], row["eval_folder"], row["wait_hours"], row["label"])


def traveled(row: dict) -> bool:
    return row["policy_invocations"] > 1 or row["distance_traveled_m"] > 0.0


def outcome(row: dict) -> tuple:
    return (row["correct"], row["abstained"])


# ---------------------------------------------------------------------------
# Item 1: paired per-question reconciliation
# ---------------------------------------------------------------------------

@dataclass
class PairedBuckets:
    identical: int
    traveled_diff: list[tuple]   # (key, decay_voi_row, floor_row)
    voi_abstained_floor_answered: list[tuple]
    mystery: list[tuple]         # must be empty


def bucket_pairs(rows: list[dict], policy_a: str, policy_b: str) -> PairedBuckets:
    by_policy = {}
    for r in rows:
        by_policy.setdefault(r["policy"], {})[question_key(r)] = r
    a = by_policy[policy_a]
    b = by_policy[policy_b]
    common = sorted(set(a) & set(b))

    identical = 0
    traveled_diff = []
    voi_abstained_floor_answered = []
    mystery = []

    for k in common:
        ra, rb = a[k], b[k]
        same = outcome(ra) == outcome(rb)
        if ra["abstained"] and not rb["abstained"]:
            voi_abstained_floor_answered.append((k, ra, rb))
        elif traveled(ra):
            if same:
                identical += 1
            else:
                traveled_diff.append((k, ra, rb))
        else:
            if same:
                identical += 1
            else:
                mystery.append((k, ra, rb))

    return PairedBuckets(identical, traveled_diff, voi_abstained_floor_answered, mystery)


def trace_for_report(key: tuple, voi_row: dict, floor_row: dict) -> str:
    scene, eval_folder, wait_hours, label = key
    log = voi_row.get("log", [])
    route = [e["anchor"] for e in log if e.get("kind") in ("goto_resense", "goto_anchor")]
    observations = [e for e in log if e.get("kind") in ("goto_resense", "goto_anchor", "decision")]
    answer_event = next((e for e in log if e.get("kind") == "answer"), None)
    return (
        f"  scene={scene} eval_folder={eval_folder} wait_hours={wait_hours} label={label}\n"
        f"    floor: correct={floor_row['correct']} abstained={floor_row['abstained']}\n"
        f"    decay_voi: correct={voi_row['correct']} abstained={voi_row['abstained']} "
        f"invocations={voi_row['policy_invocations']} distance_m={voi_row['distance_traveled_m']:.2f}\n"
        f"    route (resense/anchor visits): {route}\n"
        f"    n_log_events={len(log)}, n_observation_events={len(observations)}\n"
        f"    final answer event: {answer_event}"
    )


# ---------------------------------------------------------------------------
# Item 2: abstain rates and two-way accuracy
# ---------------------------------------------------------------------------

def abstain_rate(rows: list[dict], policy: str) -> float:
    prows = [r for r in rows if r["policy"] == policy]
    return sum(1 for r in prows if r["abstained"]) / len(prows)


def accuracy_of_non_abstained(rows: list[dict], policy: str) -> float:
    prows = [r for r in rows if r["policy"] == policy and not r["abstained"]]
    return sum(1 for r in prows if r["correct"]) / len(prows)


def accuracy_of_all(rows: list[dict], policy: str) -> float:
    prows = [r for r in rows if r["policy"] == policy]
    total = 0.0
    for r in prows:
        if r["abstained"]:
            total += _R_ABSTAIN
        elif r["correct"]:
            total += 1.0
        else:
            total += 0.0
    return total / len(prows)


# ---------------------------------------------------------------------------
# Item 3: clustered bootstrap, including paired deltas
# ---------------------------------------------------------------------------

@dataclass
class BootstrapResult:
    point: float
    ci_lo: "float | None"
    ci_hi: "float | None"
    n_clusters: int

    @property
    def degenerate(self) -> bool:
        return self.n_clusters < 2


def _per_cluster_accuracy(rows: list[dict], policy: str) -> dict[tuple, float]:
    by_cluster: dict[tuple, list[dict]] = {}
    for r in rows:
        if r["policy"] != policy or r["abstained"]:
            continue
        by_cluster.setdefault(cluster_key(r), []).append(r)
    return {k: sum(1 for r in v if r["correct"]) / len(v) for k, v in by_cluster.items() if v}


def bootstrap_over_clusters(values: list[float], n_resamples: int = _N_BOOTSTRAP, seed: int = _BOOTSTRAP_SEED) -> BootstrapResult:
    values = [v for v in values if v == v]
    n = len(values)
    if n == 0:
        return BootstrapResult(float("nan"), None, None, 0)
    point = sum(values) / n
    if n < 2:
        return BootstrapResult(point, None, None, n)
    rng = random.Random(seed)
    means = []
    for _ in range(n_resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * n_resamples)]
    hi = means[min(n_resamples - 1, int(0.975 * n_resamples))]
    return BootstrapResult(point, lo, hi, n)


def paired_bootstrap_delta(rows: list[dict], policy_a: str, policy_b: str, n_resamples: int = _N_BOOTSTRAP, seed: int = _BOOTSTRAP_SEED) -> BootstrapResult:
    """Delta (a - b) in per-cluster accuracy, bootstrapped by resampling
    CLUSTER INDICES once per iteration and applying the identical resample
    to both series — preserves the pairing (same scenes contribute to both
    policies' means in every resample), unlike two independent bootstraps
    over each policy's own cluster means."""
    a_by_cluster = _per_cluster_accuracy(rows, policy_a)
    b_by_cluster = _per_cluster_accuracy(rows, policy_b)
    common = sorted(set(a_by_cluster) & set(b_by_cluster))
    deltas = [a_by_cluster[k] - b_by_cluster[k] for k in common]
    return bootstrap_over_clusters(deltas, n_resamples, seed)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main() -> None:
    rows = load_rows("location", "volatile")
    print(f"Loaded {len(rows)} volatile-location rows across "
          f"{len({r['scene'] for r in rows})} scenes.")

    buckets = bucket_pairs(rows, "decay_voi", "answer_immediately")
    print(f"\nPaired reconciliation (decay_voi vs answer_immediately), n=505 expected:")
    print(f"  identical outcome, no travel/abstain-divergence: {buckets.identical}")
    print(f"  decay_voi traveled, outcome differs: {len(buckets.traveled_diff)}")
    print(f"  decay_voi abstained, floor answered: {len(buckets.voi_abstained_floor_answered)}")
    print(f"  MYSTERY (neither travel nor abstain-diff, outcome differs): {len(buckets.mystery)}")

    if buckets.mystery:
        print("\nESCALATION: mystery bucket is non-empty. Traces:")
        for k, ra, rb in buckets.mystery:
            print(trace_for_report(k, ra, rb))
        print("\nSTOPPING per the standing rule — do not trust anything below until this is resolved.")
        return

    print(f"\nTraveled+differs trace ({len(buckets.traveled_diff)} pairs):")
    for k, ra, rb in buckets.traveled_diff:
        print(trace_for_report(k, ra, rb))

    print(f"\nAbstained-where-floor-answered trace ({len(buckets.voi_abstained_floor_answered)} pairs), "
          f"floor correctness on these:")
    floor_correct_on_abstained = sum(1 for _k, _ra, rb in buckets.voi_abstained_floor_answered if rb["correct"])
    print(f"  floor was correct on {floor_correct_on_abstained}/{len(buckets.voi_abstained_floor_answered)} of these")
    for k, ra, rb in buckets.voi_abstained_floor_answered:
        print(trace_for_report(k, ra, rb))

    print("\n--- Item 2: abstain rates and two-way accuracy ---")
    policies = ["always_resense", "decay_threshold", "decay_voi", "decay_voi_routing", "coverage_stop", "answer_immediately", "tod_prior"]
    for p in policies:
        ar = abstain_rate(rows, p)
        acc_non_abstained = accuracy_of_non_abstained(rows, p)
        acc_all = accuracy_of_all(rows, p)
        print(f"  {p:<20} abstain_rate={ar:.3f}  acc(non-abstained)={acc_non_abstained:.3f}  "
              f"acc(all, r_abstain={_R_ABSTAIN})={acc_all:.3f}")

    print("\n--- Item 3: clustered bootstrap CIs ---")
    for p in ["decay_voi", "answer_immediately", "always_resense"]:
        cluster_accs = list(_per_cluster_accuracy(rows, p).values())
        b = bootstrap_over_clusters(cluster_accs)
        print(f"  {p:<20} {b.point:.3f} [{b.ci_lo}, {b.ci_hi}] (n_clusters={b.n_clusters})" if not b.degenerate
              else f"  {p:<20} {b.point:.3f} (n_clusters={b.n_clusters}, no CI possible)")

    delta_vs_floor = paired_bootstrap_delta(rows, "decay_voi", "answer_immediately")
    delta_vs_ceiling = paired_bootstrap_delta(rows, "decay_voi", "always_resense")
    print(f"\n  paired delta decay_voi - answer_immediately: {delta_vs_floor.point:+.3f} "
          f"[{delta_vs_floor.ci_lo}, {delta_vs_floor.ci_hi}] (n_clusters={delta_vs_floor.n_clusters})")
    print(f"  paired delta decay_voi - always_resense:      {delta_vs_ceiling.point:+.3f} "
          f"[{delta_vs_ceiling.ci_lo}, {delta_vs_ceiling.ci_hi}] (n_clusters={delta_vs_ceiling.n_clusters})")

    print("\n--- Item 4: corrected flip-attribution (bug fixed in stratified_decomposition/decompose) ---")
    all_location_rows = []
    for p in sorted(_DIAGNOSTICS_DIR.glob("e2_preliminary_*_result.json")):
        d = json.loads(p.read_text())
        all_location_rows.extend(r for r in d["rows"] if r["question_type"] == "location")
    decomposition = stratified_decomposition(all_location_rows)
    for row in decomposition:
        if row["hazard_class"] == "volatile":
            print(f"  {row}")


if __name__ == "__main__":
    main()
