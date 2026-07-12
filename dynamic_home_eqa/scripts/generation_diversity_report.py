#!/usr/bin/env python3
"""
generation_diversity_report.py — pure counting instrumentation over every
validated generation folder currently on disk. No rendering, no model
calls. Prerequisite for the realism-score correlation study
(results/reports/realism_score_trace.md) and a direct check on whether
this project's volatile/stable hazard stratification
(embodied.policy.classify_hazard's median-split) reflects a real
separation in the underlying dwell-time data or is an artifact of
splitting an undifferentiated continuum in half.

Reuses embodied.belief.dwell_events unchanged for the dwell-time
computation — the same function every kernel-fitting and reliability-
diagram path in this project already uses, not a new statistic invented
for this report.
"""
from __future__ import annotations

import csv
import json
import pathlib
import statistics
from collections import defaultdict

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.belief import dwell_events
from dynamic_home_eqa.scripts.scene_validation import validate_folder

_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"


def discover_valid_folders(out_dir: pathlib.Path) -> list[str]:
    folders = sorted(p.name for p in out_dir.iterdir() if p.is_dir() and not p.name.startswith("_"))
    valid = []
    for folder in folders:
        gr_path, mf_path = out_dir / folder / "generation_result.json", out_dir / folder / "manifest.json"
        if not (gr_path.exists() and mf_path.exists()):
            continue
        try:
            if validate_folder(out_dir, folder).ok:
                valid.append(folder)
        except Exception:
            continue
    return valid


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    folders = discover_valid_folders(out_dir)
    print(f"{len(folders)} validated folders found")

    move_counts: dict[str, int] = defaultdict(int)
    distinct_anchors: dict[str, set] = defaultdict(set)
    anchor_object_counts: dict[str, set] = defaultdict(set)
    dwell_by_category: dict[str, list[float]] = defaultdict(list)
    dwell_by_category_profile: dict[tuple[str, str], list[float]] = defaultdict(list)
    move_counts_by_profile: dict[tuple[str, str], int] = defaultdict(int)

    for folder in folders:
        manifest = json.loads((out_dir / folder / "manifest.json").read_text())
        profile = manifest.get("resident_profile", "unknown")
        changes = manifest["changes"]
        for c in changes:
            if c.get("change_type") == "state_change":
                continue  # location-axis diversity only; state has its own smaller event set
            cat = c["object_category"]
            move_counts[cat] += 1
            move_counts_by_profile[(cat, profile)] += 1
            distinct_anchors[cat].add(c["to_semantic"])
            anchor_object_counts[c["to_semantic"]].add(c["label"])
        for key, _start_state, dwell in dwell_events(changes):
            dwell_by_category[key].append(dwell)
            dwell_by_category_profile[(key, profile)].append(dwell)

    # --- per-category move counts + distinct anchors ---
    cat_csv = _REPORTS_DIR / "generation_diversity_categories.csv"
    with open(cat_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "move_count", "distinct_anchors"])
        for cat in sorted(move_counts, key=lambda c: -move_counts[c]):
            w.writerow([cat, move_counts[cat], len(distinct_anchors[cat])])

    # --- per-anchor object counts ---
    anchor_csv = _REPORTS_DIR / "generation_diversity_anchors.csv"
    with open(anchor_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anchor", "distinct_objects"])
        for anchor in sorted(anchor_object_counts, key=lambda a: -len(anchor_object_counts[a])):
            w.writerow([anchor, len(anchor_object_counts[anchor])])

    # --- per-category dwell-time distribution (the load-bearing one) ---
    dwell_csv = _REPORTS_DIR / "generation_diversity_dwell.csv"
    dwell_summary = []
    with open(dwell_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "n", "mean_hours", "median_hours", "stdev_hours", "p25_hours", "p75_hours"])
        for cat, samples in sorted(dwell_by_category.items(), key=lambda kv: statistics.mean(kv[1])):
            samples_sorted = sorted(samples)
            n = len(samples_sorted)
            mean = statistics.mean(samples_sorted)
            median = statistics.median(samples_sorted)
            stdev = statistics.stdev(samples_sorted) if n > 1 else 0.0
            p25 = samples_sorted[int(0.25 * (n - 1))]
            p75 = samples_sorted[int(0.75 * (n - 1))]
            w.writerow([cat, n, f"{mean:.3f}", f"{median:.3f}", f"{stdev:.3f}", f"{p25:.3f}", f"{p75:.3f}"])
            dwell_summary.append((cat, n, mean, median))

    # --- per-profile distribution differences (mean dwell per category, per profile) ---
    profile_csv = _REPORTS_DIR / "generation_diversity_by_profile.csv"
    with open(profile_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "profile", "move_count", "mean_dwell_hours", "n_dwell_samples"])
        for (cat, profile), samples in sorted(dwell_by_category_profile.items()):
            mean = statistics.mean(samples) if samples else float("nan")
            w.writerow([cat, profile, move_counts_by_profile[(cat, profile)], f"{mean:.3f}" if samples else "n/a", len(samples)])

    print(f"\nWrote {cat_csv}\nWrote {anchor_csv}\nWrote {dwell_csv}\nWrote {profile_csv}")

    print(f"\nPer-category mean dwell (hours), ascending (most volatile first), n={len(dwell_summary)} categories:")
    for cat, n, mean, median in dwell_summary:
        print(f"  {cat:20s} n={n:4d} mean={mean:8.2f}h median={median:8.2f}h")


if __name__ == "__main__":
    main()
