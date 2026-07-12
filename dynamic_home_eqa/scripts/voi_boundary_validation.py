#!/usr/bin/env python3
"""
voi_boundary_validation.py — VoI validation batch, item 1: does DecayVoi's
value-of-information arithmetic ever actually decline a resense?

E1 lambda forensics found decay_voi behaviorally identical to always_resense
in every run to date (E0's 3-policy check, the M2/M3 gates, the E1
rehearsal) — zero declined resenses, at any wait_hours, on this scene, at
DecayVoiConfig's default latency_weight. That is zero behavioral evidence
for the project's central VoI claim. This script sweeps LATENCY_WEIGHT_SWEEP
(scripts/e1_cost_heterogeneity.py) against BOTH question axes (location,
state) and reports, per wait_hours, the latency_weight at which decay_voi's
behavior transitions from "always resenses" (matches always_resense on
every trial) through "mixed" to "never resenses" (matches answer_immediately
on every trial).

Existence requirement: at least one (latency_weight, wait_hours, axis) cell
with a genuine declined resense. If the full sweep never produces one,
this script does NOT widen the sweep or tune anything — it traces one
concrete trial's gain/cost arithmetic by hand (see trace_one_trial below)
and reports the units audit, per the standing rule against tuning constants
before understanding why they don't bind.

Only decay_voi is run at each sweep point (not the full policy set) —
always_resense and answer_immediately's rows are read from the already-
validated embodied_results/m3_result.json (both are latency_weight-
independent: always_resense never consults cost, answer_immediately never
resenses at all, so neither needs rerunning at each sweep point).

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import (
    behavior_code_hash,
    fit_location_kernels_from_train,
    fit_state_kernels_from_train,
    rerun_frozen_e0,
    rerun_frozen_state_e0,
    state_category_stats_from_train,
)
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import DecayVoi, DecayVoiConfig
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore
from dynamic_home_eqa.embodied.question import (
    categories_ever_outdoor,
    category_anchor_history,
    generate_mcq_question,
    generate_state_question,
)
from dynamic_home_eqa.env.deltas import STATE_VARIABLES
from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE
from dynamic_home_eqa.generation.exports import category_location_change_stats
from dynamic_home_eqa.scripts.e1_cost_heterogeneity import LATENCY_WEIGHT_SWEEP

_M3_RESULT_PATH = _DYNAMIC_EQA / "embodied_results" / "m3_result.json"
_RESULTS_DIR = _DYNAMIC_EQA / "embodied_results"
# NOT embodied_results/ directly: build_attribution_table.py globs
# "*_result.json" at that directory's top level to find milestone
# manifests (fingerprint/code_hash-stamped, written by write_result_
# manifest) — this script's own summary output is a diagnostic artifact,
# not a milestone manifest, and landing it alongside the real ones broke
# that glob (KeyError: 'fingerprint'). embodied_results/diagnostics/ is
# outside the top-level glob.
_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"


def _resensed(row: dict) -> bool:
    """A trial counts as "resensed" if it did anything other than answer
    on the first invocation with zero travel — matches how always_resense
    (always True) and answer_immediately (always False) bound the two
    ends of the spectrum decay_voi is being checked against."""
    return row["policy_invocations"] > 1 or row["distance_traveled_m"] > 0.0


def _reference_rows(axis: str) -> dict:
    """always_resense / answer_immediately rows from the already-validated
    m3_result.json, keyed by (wait_hours, label) — both policies are
    latency_weight-independent so they never need rerunning here."""
    result = json.loads(_M3_RESULT_PATH.read_text())
    rows = [r for r in result["rows"] if r["question_type"] == axis]
    always = {(r["wait_hours"], r["label"]): r for r in rows if r["policy"] == "always_resense"}
    immediate = {(r["wait_hours"], r["label"]): r for r in rows if r["policy"] == "answer_immediately"}
    return {"always_resense": always, "answer_immediately": immediate}


def run_location_sweep(out_dir: pathlib.Path) -> dict[float, list[dict]]:
    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)
    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)

    def question_factory(label, category, asked_t, world, decay_models):
        return generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )

    rows_by_lw: dict[float, list[dict]] = {}
    for lw in LATENCY_WEIGHT_SWEEP:
        tmp = _RESULTS_DIR / "_voi_boundary_location_tmp.json"
        rows = rerun_frozen_e0(
            milestone="voi_boundary", policies={"decay_voi": DecayVoi(DecayVoiConfig(latency_weight=lw))},
            question_factory=question_factory, out_dir=out_dir, result_path=tmp,
            belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
        )
        tmp.unlink()
        rows_by_lw[lw] = rows
        print(f"  location latency_weight={lw}: {len(rows)} trials")
    return rows_by_lw


def run_state_sweep(out_dir: pathlib.Path) -> dict[float, list[dict]]:
    state_flip_stats = state_category_stats_from_train(out_dir, FROZEN)
    state_category_stats = {
        key: {"location_changes": stats["flip_count"], "mean_dwell_hours": stats["mean_dwell_hours"]}
        for key, stats in state_flip_stats.items()
    }
    state_train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.state_train_folders
    ]
    state_variable_domains = {
        key: STATE_VARIABLES[key.split("::")[1]]["values"] for key in state_category_stats
    }
    state_kernels = fit_state_kernels_from_train(out_dir, FROZEN)
    state_resense_anchors = {f"{cat}::{var}": cat for cat, var in STATEFUL_FURNITURE.items()}

    def question_factory(label, category, variable, asked_t, world, decay_models):
        return generate_state_question(
            label=label, category=category, variable=variable, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes, decay_models=decay_models,
        )

    rows_by_lw: dict[float, list[dict]] = {}
    for lw in LATENCY_WEIGHT_SWEEP:
        tmp = _RESULTS_DIR / "_voi_boundary_state_tmp.json"
        rows = rerun_frozen_state_e0(
            milestone="voi_boundary", policies={"decay_voi": DecayVoi(DecayVoiConfig(latency_weight=lw))},
            question_factory=question_factory, out_dir=out_dir, result_path=tmp,
            belief_factory=lambda _decay_models: PosteriorBeliefStore(state_kernels, resense_anchors=state_resense_anchors),
        )
        tmp.unlink()
        rows_by_lw[lw] = rows
        print(f"  state latency_weight={lw}: {len(rows)} trials")
    return rows_by_lw


def transition_table(rows_by_lw: dict[float, list[dict]]) -> dict[float, dict[float, float]]:
    """{wait_hours: {latency_weight: fraction_resensed}} — the monotone
    transition a sensible policy should show: 1.0 (always resenses) at low
    latency_weight, declining toward 0.0 (never resenses) as it grows."""
    waits = sorted({r["wait_hours"] for rows in rows_by_lw.values() for r in rows})
    table: dict[float, dict[float, float]] = {w: {} for w in waits}
    for lw, rows in rows_by_lw.items():
        by_wait: dict[float, list[dict]] = {}
        for r in rows:
            by_wait.setdefault(r["wait_hours"], []).append(r)
        for w, wrows in by_wait.items():
            table[w][lw] = sum(1 for r in wrows if _resensed(r)) / len(wrows)
    return table


def find_declined_resenses(rows_by_lw: dict[float, list[dict]]) -> list[dict]:
    """Every (latency_weight, wait_hours, label) trial where decay_voi did
    NOT resense — the existence requirement's direct evidence."""
    declines = []
    for lw, rows in rows_by_lw.items():
        for r in rows:
            if not _resensed(r):
                declines.append({"latency_weight": lw, "wait_hours": r["wait_hours"], "label": r["label"]})
    return declines


def trace_one_trial(out_dir: pathlib.Path) -> str:
    """Hand-traces one location trial's gain/cost arithmetic at the
    default latency_weight, for the escalation report if no lambda in the
    sweep ever produces a decline — see DecayVoi.act()'s own formula."""
    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)
    lines = ["Trace of DecayVoi.act()'s arithmetic (cost = latency_weight * travel_seconds; "
             "gain = 1 - validity_if_no_resense; resense iff gain > cost):"]
    for key, kernel in list(location_kernels.items())[:3]:
        for wait in (0.25, 1.0, 4.0):
            from dynamic_home_eqa.embodied.belief import _posterior_validity_at_dwell
            validity = _posterior_validity_at_dwell(kernel, kernel.states[0], wait)
            gain = 1.0 - validity
            for travel_s in (4.0, 15.0, 30.0):
                cost_default = (1.0 / 3600.0) * travel_s
                lines.append(
                    f"  category={key} wait={wait}h travel={travel_s}s: "
                    f"validity_if_no_resense~={validity:.4f} gain={gain:.4f} "
                    f"cost_at_default_latency_weight={cost_default:.6f} "
                    f"resense_at_default={'YES' if gain > cost_default else 'no'}"
                )
    return "\n".join(lines)


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"

    print("Running location axis sweep...")
    location_rows = run_location_sweep(out_dir)
    print("Running state axis sweep...")
    state_rows = run_state_sweep(out_dir)

    location_table = transition_table(location_rows)
    state_table = transition_table(state_rows)

    print("\nLocation transition table (fraction of trials resensed, by wait_hours x latency_weight):")
    for w in sorted(location_table):
        row = location_table[w]
        print(f"  wait={w}: " + "  ".join(f"lw={lw}:{row.get(lw, float('nan')):.2f}" for lw in LATENCY_WEIGHT_SWEEP))

    print("\nState transition table:")
    for w in sorted(state_table):
        row = state_table[w]
        print(f"  wait={w}: " + "  ".join(f"lw={lw}:{row.get(lw, float('nan')):.2f}" for lw in LATENCY_WEIGHT_SWEEP))

    declines = find_declined_resenses(location_rows) + find_declined_resenses(state_rows)
    print(f"\nDeclined-resense trials found: {len(declines)}")
    if not declines:
        print("\nNO declined resense found anywhere in the sweep. Tracing one trial's arithmetic by hand:")
        print(trace_one_trial(out_dir))
    else:
        print("Existence requirement MET. Sample of declined trials:")
        for d in declines[:10]:
            print(f"  {d}")

    out = {
        "code_hash": behavior_code_hash(),
        "fingerprint": FROZEN.fingerprint(),
        "latency_weight_sweep": list(LATENCY_WEIGHT_SWEEP),
        "location_transition_table": location_table,
        "state_transition_table": state_table,
        "declined_resense_trials": declines,
    }
    _DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _DIAGNOSTICS_DIR / "voi_boundary_result.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
