#!/usr/bin/env python3
"""
embodied_e0_regime_check.py — E0: is the resense-vs-answer decision problem
even non-vacuous at walk_speed_mps=1?

Concern (from the embodied-agent phase spec): this house crosses in tens of
seconds while per-category hazards are on an hours scale, so travel may be
so cheap that always_resense dominates every reasonable latency penalty and
the decision problem never separates from the floor/ceiling policies. This
script collects raw (policy, wait_hours, label, correct, latency_seconds)
records for answer_immediately / always_resense / decay_voi, then sweeps the
latency-penalty weight lambda in utility = accuracy - lambda *
answer_latency_hours to check whether any reasonable lambda produces
separation. Must be run BEFORE building E1-E4 sweep machinery (per the
phase spec) — if no lambda separates them, that machinery would be
measuring a vacuous decision problem.

Labels are drawn through embodied.sampling.qualify_labels (the same rule
FROZEN_LABELS uses) and episodes delegate to
embodied.attribution.rerun_frozen_e0 — the same harness FROZEN_LABELS and
the M1 gate use — rather than a parallel reimplementation of the
patrol/dock/ask loop.

Each (policy, wait_hours, question) trial gets a FRESH world/belief/patrol
and asks exactly one question — asking several questions sequentially in
one episode compounds: dock_and_wait(w) called
N times in a row means the Nth question actually experiences N*w hours of
total elapsed time since patrol, not w, silently confounding the wait_hours
variable this whole script exists to sweep cleanly.

Requires habitat_sim (the dynamic_eqa env).

Usage:
    python -m dynamic_home_eqa.scripts.embodied_e0_regime_check \\
        --scene 102343992 --profile family_with_kids \\
        --train-folders 102343992_family_with_kids ... \\
        --eval-folder 102343992_family_with_kids_day4 \\
        --out e0_raw.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import rerun_frozen_e0, summarize_rows
from dynamic_home_eqa.embodied.experiment_config import FrozenConfig
from dynamic_home_eqa.embodied.policy import AlwaysResense, AnswerImmediately, DecayVoi
from dynamic_home_eqa.embodied.question import (
    category_anchor_history,
    categories_ever_outdoor,
    generate_mcq_question,
)
from dynamic_home_eqa.embodied.sampling import qualify_labels

_WAIT_HOURS_SWEEP = (0.25, 0.5, 1.0, 2.0, 4.0)
_LAMBDA_SWEEP = (0.0, 0.001, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
_PATROL_START = 6.0


def _policies():
    return {
        "answer_immediately": AnswerImmediately(),
        "always_resense":     AlwaysResense(),
        "decay_voi":          DecayVoi(),
    }


def _qualified_config(
    scene_id: str, eval_folder: str, train_folders: list[str],
    out_dir: pathlib.Path, n_questions: int,
) -> FrozenConfig:
    """A FrozenConfig for this (scene, eval_folder, train_folders) whose
    `labels` are the qualifying subset under embodied.sampling's two-
    property rule (exists at patrol_start AND every historical anchor slot
    reachable from the start pose) — not the raw "moved at least once"
    set. FrozenConfig.fingerprint() hashes only field values, so this
    config's fingerprint automatically matches experiment_config.FROZEN
    whenever these args match its defaults, letting E0's result row join
    the same attribution table as M1's without any special-casing."""
    eval_manifest = json.loads((out_dir / eval_folder / "manifest.json").read_text())
    eval_result = json.loads((out_dir / eval_folder / "generation_result.json").read_text())
    history_manifests = [eval_manifest] + [
        json.loads((out_dir / folder / "manifest.json").read_text()) for folder in train_folders
    ]
    qualifications = qualify_labels(
        scene=scene_id, eval_result=eval_result, eval_manifest=eval_manifest,
        history_manifests=history_manifests, patrol_start=_PATROL_START,
    )
    labels = tuple(sorted(q.label for q in qualifications if q.qualifies))[:n_questions]
    return FrozenConfig(
        scene=scene_id, train_folders=tuple(train_folders), eval_folder=eval_folder,
        labels=labels, wait_hours_sweep=_WAIT_HOURS_SWEEP, patrol_start=_PATROL_START,
    )


def collect_raw_records(config: FrozenConfig, out_dir: pathlib.Path, result_path: pathlib.Path) -> list[dict]:
    train_manifests = [
        json.loads((out_dir / folder / "manifest.json").read_text()) for folder in config.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)

    def question_factory(label, category, asked_t, world, decay_models):
        return generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )

    return rerun_frozen_e0(
        milestone="e0", policies=_policies(), question_factory=question_factory,
        out_dir=out_dir, result_path=result_path, config=config,
    )


def analyze_separation(records: list[dict]) -> None:
    """correct is None for abstained/unanswerable trials (see
    runner.EpisodeResult) — accuracy is computed over the scored subset
    only, the same convention embodied.attribution.summarize_rows uses,
    not by coercing None into 0."""
    by_policy_wait: dict[tuple, list[dict]] = {}
    for r in records:
        by_policy_wait.setdefault((r["policy"], r["wait_hours"]), []).append(r)

    def _accuracy(rows: list[dict]) -> float:
        scored = [r for r in rows if r["correct"] is not None]
        return (sum(1 for r in scored if r["correct"]) / len(scored)) if scored else float("nan")

    def _abstain_rate(rows: list[dict]) -> float:
        return sum(1 for r in rows if r["abstained"]) / len(rows) if rows else float("nan")

    print(f"\n{'='*78}")
    print("Per-(policy, wait_hours) accuracy, abstain rate, and mean latency:")
    print(f"{'='*78}")
    for (policy, wait_hours), rows in sorted(by_policy_wait.items()):
        acc = _accuracy(rows)
        abstain_rate = _abstain_rate(rows)
        mean_latency_s = sum(r["answer_latency_s"] for r in rows) / len(rows)
        mean_dist = sum(r["distance_traveled_m"] for r in rows) / len(rows)
        print(f"  {policy:20s} wait={wait_hours:4.2f}h  n={len(rows):3d}  "
              f"acc={acc:.3f}  abstain={abstain_rate:.2f}  "
              f"mean_latency={mean_latency_s:7.1f}s  mean_dist={mean_dist:6.2f}m")

    print(f"\n{'='*78}")
    print("Utility sweep: utility = accuracy - lambda * mean_answer_latency_hours")
    print(f"{'='*78}")
    policies = sorted({r["policy"] for r in records})
    wait_values = sorted({r["wait_hours"] for r in records})

    def _utilities(wait_hours: float, lam: float) -> dict[str, float]:
        utilities = {}
        for policy in policies:
            rows = by_policy_wait.get((policy, wait_hours), [])
            if not rows:
                continue
            mean_latency_h = (sum(r["answer_latency_s"] for r in rows) / len(rows)) / 3600.0
            utilities[policy] = _accuracy(rows) - lam * mean_latency_h
        return utilities

    any_separation = False
    any_accuracy_gain_from_resensing = False
    any_abstain = any(r["abstained"] for r in records)
    for wait_hours in wait_values:
        print(f"\n-- wait_hours={wait_hours} --")
        header = f"  {'lambda':>10s}" + "".join(f"{p:>22s}" for p in policies) + "   best"
        print(header)
        accs = {policy: _accuracy(by_policy_wait.get((policy, wait_hours), [])) for policy in policies}
        if len(set(round(a, 6) for a in accs.values() if a == a)) > 1:  # a == a filters NaN
            any_accuracy_gain_from_resensing = True

        bests = set()
        for lam in _LAMBDA_SWEEP:
            utilities = _utilities(wait_hours, lam)
            best = max(utilities, key=utilities.get) if utilities else None
            if best is not None:
                bests.add(best)
            row = f"  {lam:>10.4f}" + "".join(f"{utilities.get(p, float('nan')):>22.4f}" for p in policies) + f"   {best}"
            print(row)
        if len(bests) > 1:
            any_separation = True
            print(f"  ==> SEPARATION at wait_hours={wait_hours}: different lambda values favor {bests}")

    print(f"\n{'='*78}")
    print(f"Any wait_hours where resensing changed accuracy at all: {any_accuracy_gain_from_resensing}")
    print(f"Any abstentions in this sweep: {any_abstain}")
    if any_separation and any_accuracy_gain_from_resensing:
        print("VERDICT: separation found, AND it's driven by a genuine accuracy "
              "difference (not just latency cost with tied accuracy). Safe to "
              "proceed to E1-E4.")
    elif any_separation and not any_accuracy_gain_from_resensing:
        print("VERDICT: 'separation' found but accuracy is IDENTICAL across "
              "policies at every wait_hours tested — resensing never changed an "
              "answer, so the floor (answer_immediately) strictly dominates for "
              "any lambda > 0 (same accuracy, zero cost). This is the mirror image "
              "of the spec's anticipated failure mode: not 'always_resense wins "
              "everywhere' but 'resensing never helps here'. Escalate with this "
              "data rather than proceeding — likely needs either more/harder "
              "questions (objects that genuinely moved since patrol) or a "
              "shorter patrol-to-question gap where staleness is more likely.")
    else:
        print("VERDICT: NO separation found across the swept lambda/wait_hours grid — "
              "one policy dominates everywhere. Escalate per the documented fallback "
              "designs (multi-question batches under a shared time budget, or a "
              "reduced walk speed justified as a realistic robot platform) rather "
              "than building E1-E4 on a vacuous regime.")
    print(f"{'='*78}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", default="102343992")
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "generation_out"))
    ap.add_argument("--eval-folder", default="102343992_family_with_kids_day4",
                    help="folder (under --out-dir) to draw eval questions from")
    ap.add_argument("--train-folders", nargs="+", default=[
        "102343992_family_with_kids", "102343992_family_with_kids_day1",
        "102343992_family_with_kids_day2", "102343992_family_with_kids_day3",
    ], help="folders (under --out-dir) to fit DecayModels from")
    ap.add_argument("--out", default=str(_DYNAMIC_EQA / "results" / "e0" / "e0_raw.csv"))
    ap.add_argument("--result-path", default=str(_DYNAMIC_EQA / "embodied_results" / "e0_result.json"))
    ap.add_argument("--n-questions", type=int, default=10)
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    config = _qualified_config(args.scene, args.eval_folder, args.train_folders, out_dir, args.n_questions)
    print(f"Qualified labels ({len(config.labels)}): {config.labels}")
    print(f"Fingerprint: {config.fingerprint()}")

    records = collect_raw_records(config, out_dir, pathlib.Path(args.result_path))

    if not records:
        sys.exit("No records collected — check --eval-folder/--train-folders exist and have qualifying labels.")

    # "log" (the full per-observation event stream) isn't flat-CSV-shaped —
    # it stays in the JSON result file (--result-path) for the mechanism
    # decomposition script; the CSV is the flat summary view.
    flat_fields = [k for k in records[0].keys() if k != "log"]
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=flat_fields)
        writer.writeheader()
        writer.writerows({k: r[k] for k in flat_fields} for r in records)
    print(f"Wrote {len(records)} raw records -> {out_path}")
    print(f"Wrote milestone result -> {args.result_path}")

    print(f"\n{'milestone':<10} {'policy':<20} {'wait_h':>6} {'n':>4} {'acc':>6} {'brier':>7} {'ece':>7} {'abstain':>8}")
    for s in summarize_rows(records):
        print(f"{s['milestone']:<10} {s['policy']:<20} {s['wait_hours']:>6.2f} {s['n']:>4d} "
              f"{s['accuracy']:>6.3f} {s['mean_brier']:>7.3f} {s['ece']:>7.3f} {s['abstain_rate']:>8.2f}")

    analyze_separation(records)


if __name__ == "__main__":
    main()
