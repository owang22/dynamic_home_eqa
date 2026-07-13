#!/usr/bin/env python3
"""
embodied_m2_gate.py — M2 gate: rerun the frozen E0 configuration under
posterior-over-anchors belief (embodied/posterior.py) instead of belief.py's
single-anchor model, plus a tod_prior baseline (posterior.
TimeOfDayBeliefStore) that predicts purely from the fitted time-of-day
schedule prior with zero live sensing. Appends both to the attribution
table under milestone "m2".

Motivation (navmesh-connectivity phase's step-1 decomposition,
scripts/e0_mechanism_decomposition.py run against embodied_results/
e0_result.json): E0's resense-driven separation was 100% selective
abstention (wrong answers converted to abstains) and 0% true discovery
(wrong answers converted to right). Under belief.py's single-anchor model,
a negative observation has nowhere to put "not there, but maybe here
instead" — it can only stop trusting the stale belief, never actually find
the object again. posterior.PosteriorBeliefStore exists specifically to
create that missing discovery mechanism: a negative observation
renormalizes mass onto the remaining candidate anchors, and
policy._search_targets/top_candidates() then greedily visits the best-
ranked one. This gate reruns the identical frozen questions and the
identical decomposition script to check whether it did — see this script's
own printed summary and the decomposition rerun in its usage note below.

policy.py's decision boundary (resense vs. answer, per policy) is
unchanged from M1 — see policy.py's module docstring; only the belief
store being searched is richer. tod_prior is not a new decision rule: it
is AnswerImmediately's existing "never resense" rule pointed at
TimeOfDayBeliefStore instead, isolating how much a fitted schedule alone
(zero live sensing) predicts, as the floor a resensing policy must beat to
justify sensing at all. (This baseline was originally named
"fremen_predict" / FremenBeliefStore — renamed in the Suite Buildout phase
because it does no frequency-domain fit and calling it FreMEn overstated
what it does; see TimeOfDayBeliefStore's own docstring.)

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).

Usage:
    python -m dynamic_home_eqa.scripts.embodied_m2_gate
    python -m dynamic_home_eqa.scripts.e0_mechanism_decomposition \\
        --result-path embodied_results/m2_result.json \\
        --out e0_mechanism_decomposition_m2.csv
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import rerun_frozen_e0, summarize_rows, write_result_manifest
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
    PosteriorBeliefStore,
    TimeOfDayBeliefStore,
    bucket_changes_by_time_of_day,
    fit_transition_kernels,
    fit_transition_kernels_by_time_of_day,
)
from dynamic_home_eqa.embodied.question import categories_ever_outdoor, category_anchor_history, generate_mcq_question
from dynamic_home_eqa.generation.exports import category_location_change_stats

_N_TOD_BUCKETS = 4


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    results_dir = _DYNAMIC_EQA / "embodied_results"

    train_manifests = [
        json.loads((out_dir / folder / "manifest.json").read_text()) for folder in FROZEN.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)

    per_day_stats = [category_location_change_stats(m["changes"]) for m in train_manifests]
    category_stats = aggregate_category_stats(per_day_stats)
    kernels = fit_transition_kernels(train_manifests, category_stats, anchor_history)

    per_bucket_changes = bucket_changes_by_time_of_day(train_manifests, n_buckets=_N_TOD_BUCKETS)
    category_stats_by_bucket = [category_location_change_stats(bucket) for bucket in per_bucket_changes]
    bucketed_kernels = fit_transition_kernels_by_time_of_day(
        train_manifests, category_stats_by_bucket, anchor_history, n_buckets=_N_TOD_BUCKETS,
    )

    def question_factory(label, category, asked_t, world, decay_models):
        return generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )

    # Main posterior-belief policies: identical policy set to M1's gate —
    # only the belief store searched against changes (see module docstring).
    posterior_policies = {
        "answer_immediately": AnswerImmediately(),
        "always_resense":     AlwaysResense(),
        "coverage_stop":    CoverageStop(),
        "decay_threshold":    DecayThreshold(),
        "decay_voi":          DecayVoi(),
        "decay_voi_routing":  DecayVoiRouting(),
    }
    tmp_posterior = results_dir / "_m2_posterior_tmp.json"
    posterior_rows = rerun_frozen_e0(
        milestone="m2", policies=posterior_policies, question_factory=question_factory,
        out_dir=out_dir, result_path=tmp_posterior,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(kernels),
    )
    tmp_posterior.unlink()

    # tod_prior: AnswerImmediately's existing rule run against
    # TimeOfDayBeliefStore — the zero-live-sensing floor.
    tmp_tod = results_dir / "_m2_tod_prior_tmp.json"
    tod_rows = rerun_frozen_e0(
        milestone="m2", policies={"tod_prior": AnswerImmediately()}, question_factory=question_factory,
        out_dir=out_dir, result_path=tmp_tod,
        belief_factory=lambda _decay_models: TimeOfDayBeliefStore(bucketed_kernels, n_buckets=_N_TOD_BUCKETS),
    )
    tmp_tod.unlink()

    all_rows = posterior_rows + tod_rows
    result_path = results_dir / "m2_result.json"
    write_result_manifest(result_path, "m2", FROZEN, all_rows)
    print(f"Wrote {len(all_rows)} raw rows -> {result_path}")

    for s in summarize_rows(all_rows):
        print(f"  {s['policy']:20s} wait={s['wait_hours']:4.2f}h n={s['n']:3d}  "
              f"acc={s['accuracy']:.3f}  brier={s['mean_brier']:.3f}  ece={s['ece']:.3f}  "
              f"abstain={s['abstain_rate']:.2f}  latency={s['mean_latency_s']:6.1f}s  "
              f"travel={s['mean_travel_m']:6.2f}m")


if __name__ == "__main__":
    main()
