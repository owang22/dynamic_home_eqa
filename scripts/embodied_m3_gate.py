#!/usr/bin/env python3
"""
embodied_m3_gate.py — M3 gate: rerun the frozen E0 configuration extended
with a state-change question stratum (M3: state-change dynamics — see
scripts/generate_state_stratum.py for the data and env/deltas.py's
STATE_VARIABLES for the registry), appending both location and state rows
to the attribution table under milestone "m3".

Reuses M2's posterior-belief/search-resense machinery unchanged for the
state axis: a state variable's belief is a PosteriorBeliefStore keyed by
synthetic "{category}::{variable}" categories (see posterior.py's module
docstring) — same TransitionKernel/top_candidates/search-resense code, no
new belief logic. The one real state-axis addition is the loop shape
(rerun_frozen_state_e0 in attribution.py), since a state label's variable
isn't recoverable from world.current_instances() the way its location
category is.

Also closes a gap a pre-E1-E4 baseline audit found: tod_prior (M2's own
zero-live-sensing floor) had been dropped from this gate's policy set by
omission — restored here, location axis only (a state-axis tod_prior
variant would need its own bucketed state kernels and belief-store
plumbing; a documented future extension, not silently promised as done).

conformal_decay_threshold is NOT in this gate's policy set. It was added
during the pre-E1-E4 audit, then dropped again during the coverage-repair
phase: after fixing two real calibration bugs (a state-axis key mismatch,
then a calibration-vs-deployment statistic-space mismatch — see belief.
calibrate_conformal_theta's docstring), realized coverage still missed its
1-alpha target at every wait_hours bucket except the shortest (0.25h) —
confirmed a dwell-time covariate shift (deployment queries fixed elapsed
times up to 4h; most natural calibration dwell events are much shorter),
then ruled out both a population mismatch (restricting calibration to
exactly the deployment-eligible categories changed theta by <0.001) and a
finite-sample quantile-correction error (identical theta with or without
it, given >250 calibration events) as the cause. The residual explanation
is that the fitted TransitionKernel's exponential-decay model doesn't
match this scene's real multi-hour dwell dynamics — a modeling gap no
calibration scheme can patch. See scripts/conformal_coverage_check.py for
the full diagnosis and CONFORMAL_COVERAGE_FINDING.md for the write-up (an
E4 calibration-sensitivity note, not a bug to fix here). The Mondrian
machinery (belief.calibrate_conformal_theta_by_wait, DecayThresholdConfig.
theta_by_wait) is kept for a future, better-fitting hazard model — it is
not itself wrong, the model it calibrates is.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import (
    rerun_frozen_e0,
    rerun_frozen_state_e0,
    state_category_stats_from_train,
    summarize_rows,
    write_result_manifest,
)
from dynamic_home_eqa.embodied.belief import aggregate_category_stats
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import (
    AlwaysResense,
    AnswerImmediately,
    CoverageStop,
    DecayThreshold,
    DecayVoi,
    DecayVoiRouting,
)
from dynamic_home_eqa.embodied.posterior import (
    TimeOfDayBeliefStore,
    PosteriorBeliefStore,
    bucket_changes_by_time_of_day,
    fit_state_transition_kernels,
    fit_transition_kernels,
    fit_transition_kernels_by_time_of_day,
)
from dynamic_home_eqa.embodied.question import (
    categories_ever_outdoor,
    category_anchor_history,
    generate_mcq_question,
    generate_state_question,
)
from dynamic_home_eqa.env.deltas import STATE_VARIABLES
from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE
from dynamic_home_eqa.generation.exports import category_location_change_stats

_N_TOD_BUCKETS = 4


def _policies() -> dict[str, object]:
    """M1's policy set. conformal_decay_threshold is deliberately absent —
    see this module's own docstring for why (dropped in the coverage-
    repair phase after its guarantee failed at every wait_hours bucket
    except the shortest). tod_prior is handled separately (own belief
    store, location axis only — see main())."""
    return {
        "answer_immediately":         AnswerImmediately(),
        "always_resense":             AlwaysResense(),
        "coverage_stop":             CoverageStop(),
        "decay_threshold":             DecayThreshold(),
        "decay_voi":                   DecayVoi(),
        "decay_voi_routing":           DecayVoiRouting(),
    }


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    results_dir = _DYNAMIC_EQA / "embodied_results"

    # -- location axis: identical fitting to M2's gate -----------------------
    train_manifests = [
        json.loads((out_dir / folder / "manifest.json").read_text()) for folder in FROZEN.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)
    location_category_stats = aggregate_category_stats(
        [category_location_change_stats(m["changes"]) for m in train_manifests]
    )
    location_kernels = fit_transition_kernels(train_manifests, location_category_stats, anchor_history)

    # tod_prior's own bucketed kernels — identical to M2's gate.
    per_bucket_changes = bucket_changes_by_time_of_day(train_manifests, n_buckets=_N_TOD_BUCKETS)
    category_stats_by_bucket = [category_location_change_stats(bucket) for bucket in per_bucket_changes]
    bucketed_kernels = fit_transition_kernels_by_time_of_day(
        train_manifests, category_stats_by_bucket, anchor_history, n_buckets=_N_TOD_BUCKETS,
    )

    def location_question_factory(label, category, asked_t, world, decay_models):
        return generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )

    # -- state axis: same kernel-fitting machinery, translated stats --------
    # fit_transition_kernels reads own_weight via stats["location_changes"];
    # state_category_stats_from_train's own honest key is "flip_count" (see
    # its docstring) — translate once, here, at the one call site that needs it.
    state_flip_stats = state_category_stats_from_train(out_dir, FROZEN)
    state_category_stats = {
        key: {"location_changes": stats["flip_count"], "mean_dwell_hours": stats["mean_dwell_hours"]}
        for key, stats in state_flip_stats.items()
    }
    state_train_manifests = [
        json.loads((out_dir / folder / "manifest.json").read_text()) for folder in FROZEN.state_train_folders
    ]
    state_variable_domains = {
        key: STATE_VARIABLES[key.split("::")[1]]["values"] for key in state_category_stats
    }
    state_kernels = fit_state_transition_kernels(state_train_manifests, state_category_stats, state_variable_domains)
    # A state belief's "states" are value labels ("open"/"closed"), not
    # navigable places — resense_anchors tells PosteriorBeliefStore.
    # top_candidates to always route resensing to the underlying
    # furniture's own real anchor (its bare category name — see
    # topdown_map.anchor_world_positions) instead of trying to travel to
    # a value name (see posterior.PosteriorBeliefStore's docstring).
    state_resense_anchors = {f"{cat}::{var}": cat for cat, var in STATEFUL_FURNITURE.items()}

    def state_question_factory(label, category, variable, asked_t, world, decay_models):
        return generate_state_question(
            label=label, category=category, variable=variable, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes, decay_models=decay_models,
        )

    result_path = results_dir / "m3_result.json"
    tmp_location = results_dir / "_m3_location_tmp.json"
    tmp_state = results_dir / "_m3_state_tmp.json"
    tmp_tod = results_dir / "_m3_tod_prior_tmp.json"

    location_rows = rerun_frozen_e0(
        milestone="m3", policies=_policies(), question_factory=location_question_factory,
        out_dir=out_dir, result_path=tmp_location,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
    )
    tmp_location.unlink()

    # tod_prior (M4 pre-suite baseline check): AnswerImmediately's
    # existing rule run against TimeOfDayBeliefStore — the zero-live-sensing
    # floor. Location axis only (see this script's module docstring for why
    # a state-axis tod_prior variant is a documented future extension, not
    # silently promised as done here).
    tod_rows = rerun_frozen_e0(
        milestone="m3", policies={"tod_prior": AnswerImmediately()}, question_factory=location_question_factory,
        out_dir=out_dir, result_path=tmp_tod,
        belief_factory=lambda _decay_models: TimeOfDayBeliefStore(bucketed_kernels, n_buckets=_N_TOD_BUCKETS),
    )
    tmp_tod.unlink()

    state_rows = rerun_frozen_state_e0(
        milestone="m3", policies=_policies(), question_factory=state_question_factory,
        out_dir=out_dir, result_path=tmp_state,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(state_kernels, resense_anchors=state_resense_anchors),
    )
    tmp_state.unlink()

    all_rows = location_rows + tod_rows + state_rows
    write_result_manifest(result_path, "m3", FROZEN, all_rows)
    print(f"Wrote {len(all_rows)} raw rows ({len(location_rows)} location, {len(state_rows)} state) -> {result_path}")

    print(f"\n{'question_type':<14}{'policy':<20} {'wait_h':>6} {'n':>4} {'acc':>6} {'brier':>7} {'ece':>7} {'abstain':>8}")
    for qtype in ("location", "state"):
        rows = [r for r in all_rows if r["question_type"] == qtype]
        for s in summarize_rows(rows):
            print(f"{qtype:<14}{s['policy']:<20} {s['wait_hours']:>6.2f} {s['n']:>4d} "
                  f"{s['accuracy']:>6.3f} {s['mean_brier']:>7.3f} {s['ece']:>7.3f} {s['abstain_rate']:>8.2f}")


if __name__ == "__main__":
    main()
