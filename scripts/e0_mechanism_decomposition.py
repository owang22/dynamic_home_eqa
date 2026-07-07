#!/usr/bin/env python3
"""
e0_mechanism_decomposition.py — decompose E0's resense-driven accuracy gain
into two distinct mechanisms under single-anchor belief (pre-M2):

  (a) true discovery — an answer flips from wrong to right because a
      resense (or the en-route observations gathered while walking to one)
      updated belief to the correct anchor.
  (b) selective abstention — a wrong answer is removed from the accuracy
      denominator because a resense refuted the previously-believed anchor
      without discovering the correct one, so the policy abstains instead
      of answering wrong.

These support different claims about *why* a resensing policy's accuracy-
of-non-abstained beats answer_immediately's: (a) says the agent found the
truth; (b) says it only got better at knowing when it doesn't know. E0's
separation finding (see embodied_e0_regime_check.py) doesn't distinguish
them — this script does, entirely from data already in
embodied_results/e0_result.json (each row's "log" field — see
attribution.rerun_frozen_e0), no new simulation run.

Why answer_immediately is a valid per-trial baseline, not an approximation:
for a given (label, wait_hours), every policy's trial shares an identical
patrol trace and identical elapsed wait — patrol() and dock_and_wait() never
consult the policy (see runner.py) — so the three policies diverge only
inside run_question()'s decision loop. answer_immediately's outcome for
that (label, wait_hours) is therefore exactly "what would have been
answered without resensing" for the other two policies at that same
(label, wait_hours), and any difference from it is attributable to that
trial's own resense actions (its log's "goto_resense" entries).

Requires no habitat_sim — reads only embodied_results/e0_result.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()

_BASELINE_POLICY = "answer_immediately"
_UNCHANGED_CATEGORIES = ("unchanged_right", "unchanged_wrong")
_REPORTED_CATEGORIES = ("unchanged_right", "unchanged_wrong", "wrong_to_right", "wrong_to_abstain", "right_to_abstain")


@dataclass(frozen=True)
class Outcome:
    correct: Optional[bool]
    abstained: bool

    @classmethod
    def from_row(cls, row: dict) -> "Outcome":
        return cls(correct=row["correct"], abstained=row["abstained"])

    @property
    def state(self) -> str:
        if self.abstained:
            return "abstain"
        return "right" if self.correct else "wrong"


def classify(baseline: Outcome, other: Outcome) -> str:
    """One of: unchanged_right, unchanged_wrong, wrong_to_right,
    wrong_to_abstain, right_to_abstain, right_to_wrong (a regression — not
    expected, reported rather than hidden), or baseline_abstained_<state>
    (the baseline itself never answered this trial — there is no "flip" to
    attribute, reported separately rather than forced into wrong_to_*)."""
    b, o = baseline.state, other.state
    if b == "abstain":
        return f"baseline_abstained_{o}"
    if b == o:
        return f"unchanged_{b}"
    return f"{b}_to_{o}"


def _resense_anchors(log: list[dict]) -> list[str]:
    return [e["anchor"] for e in log if e.get("kind") == "goto_resense"]


@dataclass(frozen=True)
class TransitionRecord:
    policy: str
    wait_hours: float
    label: str
    transition: str
    resense_anchors: tuple[str, ...]


def _scene_key(row: dict) -> tuple[str, str]:
    """(scene, eval_folder) — the disambiguator decompose()'s pairing keys
    were missing (decay_voi reconciliation batch): a bare (wait_hours,
    label) key collides across scenes whenever a generic object label
    ("book_1", "candle_1", ...) recurs in more than one scene's qualified-
    label set, which is the common case on a multi-scene pool. On a
    single-scene result file every row shares one (scene, eval_folder), so
    this is a no-op there — the bug only manifests, and was only found,
    once decompose()/its e2_headline_comparison.py counterpart ran against
    multi-scene rows. Falls back to "" rather than a FrozenConfig default
    so this module stays independent of any one frozen scene."""
    return (row.get("scene", ""), row.get("eval_folder", ""))


def decompose(rows: list[dict]) -> list[TransitionRecord]:
    by_policy_wait_label = {(r["policy"], *_scene_key(r), r["wait_hours"], r["label"]): r for r in rows}
    baseline_rows = {
        (scene, eval_folder, wait_hours, label): r
        for (policy, scene, eval_folder, wait_hours, label), r in by_policy_wait_label.items()
        if policy == _BASELINE_POLICY
    }

    policies = sorted({p for (p, _s, _e, _w, _l) in by_policy_wait_label} - {_BASELINE_POLICY})
    records: list[TransitionRecord] = []
    for (policy, scene, eval_folder, wait_hours, label), row in by_policy_wait_label.items():
        if policy not in policies:
            continue
        baseline_row = baseline_rows.get((scene, eval_folder, wait_hours, label))
        if baseline_row is None:
            continue  # baseline trial missing (label wasn't current instances at that trial)
        transition = classify(Outcome.from_row(baseline_row), Outcome.from_row(row))
        records.append(TransitionRecord(
            policy=policy, wait_hours=wait_hours, label=label, transition=transition,
            resense_anchors=tuple(_resense_anchors(row.get("log", []))),
        ))
    return records


def summarize(records: list[TransitionRecord]) -> list[dict]:
    """One row per (policy, wait_hours): counts of each transition category
    plus the resense anchors observed in the flipping trials (attribution
    of the flip to its triggering observation)."""
    by_key: dict[tuple, list[TransitionRecord]] = defaultdict(list)
    for rec in records:
        by_key[(rec.policy, rec.wait_hours)].append(rec)

    summaries = []
    for (policy, wait_hours), recs in sorted(by_key.items()):
        counts: dict[str, int] = defaultdict(int)
        triggers: dict[str, list[str]] = defaultdict(list)
        for rec in recs:
            counts[rec.transition] += 1
            if rec.transition not in _UNCHANGED_CATEGORIES:
                triggers[rec.transition].append(f"{rec.label}:{','.join(rec.resense_anchors) or 'no_resense'}")
        summaries.append({
            "policy": policy, "wait_hours": wait_hours, "n": len(recs),
            "counts": dict(counts), "triggers": dict(triggers),
        })
    return summaries


def print_report(summaries: list[dict]) -> None:
    header = f"{'policy':<20} {'wait_h':>6} {'n':>4} " + " ".join(f"{k:>18}" for k in _REPORTED_CATEGORIES)
    print(header)
    print("-" * len(header))
    for s in summaries:
        row = f"{s['policy']:<20} {s['wait_hours']:>6.2f} {s['n']:>4d} " + " ".join(
            f"{s['counts'].get(k, 0):>18d}" for k in _REPORTED_CATEGORIES
        )
        print(row)
        extra = {k: v for k, v in s["counts"].items() if k not in _REPORTED_CATEGORIES}
        if extra:
            print(f"  other transitions: {extra}")
        for category, triggers in s["triggers"].items():
            if category not in _UNCHANGED_CATEGORIES:
                print(f"  {category} triggered by: {triggers}")

    total_discovery = sum(s["counts"].get("wrong_to_right", 0) for s in summaries)
    total_abstention = sum(s["counts"].get("wrong_to_abstain", 0) for s in summaries)
    total_regression = sum(s["counts"].get("right_to_abstain", 0) for s in summaries) + sum(
        s["counts"].get("right_to_wrong", 0) for s in summaries
    )
    print(f"\nTotals across all resensing policies/wait_hours: "
          f"wrong->right (discovery)={total_discovery}  "
          f"wrong->abstain (selective abstention)={total_abstention}  "
          f"right->{{abstain,wrong}} (regression)={total_regression}")
    if total_discovery == 0 and total_abstention > 0:
        print("FINDING: separation is driven ENTIRELY by selective abstention, not discovery. "
              "M2 (posterior-over-anchors belief + search resense) is the milestone expected to "
              "create the discovery mechanism, not optional polish on an already-working one.")
    elif total_discovery > 0 and total_abstention > 0:
        print(f"FINDING: separation is a MIX — {total_discovery} discovery-driven and "
              f"{total_abstention} selective-abstention-driven flips. Both mechanisms contribute.")
    elif total_discovery > 0:
        print("FINDING: separation is driven by genuine discovery.")
    else:
        print("FINDING: no flips of either mechanism found — resensing changed nothing for any trial.")


def write_csv(records: list[TransitionRecord], out_path: pathlib.Path) -> None:
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["policy", "wait_hours", "label", "transition", "resense_anchors"])
        writer.writeheader()
        for rec in records:
            writer.writerow({
                "policy": rec.policy, "wait_hours": rec.wait_hours, "label": rec.label,
                "transition": rec.transition, "resense_anchors": ";".join(rec.resense_anchors),
            })


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result-path", default=str(_DYNAMIC_EQA / "embodied_results" / "e0_result.json"))
    ap.add_argument("--out", default=str(_DYNAMIC_EQA / "e0_mechanism_decomposition.csv"))
    args = ap.parse_args()

    result = json.loads(pathlib.Path(args.result_path).read_text())
    rows = result["rows"]

    if not any(r.get("log") for r in rows):
        sys.exit(
            f"No per-observation logs found in {args.result_path} — rerun "
            "scripts/embodied_e0_regime_check.py (attribution.rerun_frozen_e0 now "
            "persists episode.log) before running this decomposition."
        )

    records = decompose(rows)
    summaries = summarize(records)
    print_report(summaries)

    out_path = pathlib.Path(args.out)
    write_csv(records, out_path)
    print(f"\nWrote {len(records)} per-trial transition records -> {out_path}")


if __name__ == "__main__":
    main()
