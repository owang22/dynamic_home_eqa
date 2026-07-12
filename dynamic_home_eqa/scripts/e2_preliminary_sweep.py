#!/usr/bin/env python3
"""
e2_preliminary_sweep.py — Results-First batch, item 1: E2 headline
comparison run on every scene-day validated TODAY, not held back for the
pool to finish.

Per scene: fits that scene's own location (and, where available, state)
TransitionKernels from its own train days (same recipe attribution.
fit_location_kernels_from_train/fit_state_kernels_from_train use for the
frozen scene, parameterized by a scene-specific FrozenConfig instead of the
module-level FROZEN singleton), then runs the full policy set (minus
conformal_decay_threshold — dropped in the coverage-repair phase, see
embodied_m3_gate.py's own docstring) across both axes, all wait_hours.
decay_voi/decay_voi_routing use latency_weight=0.01 — the validated
binding value from voi_boundary_validation.py, not DecayVoiConfig's own
untested default (see results/reports/voi_boundary.md).

Each scene's rows are written to their own embodied_results/diagnostics/
e2_preliminary_<scene>_result.json (NOT embodied_results/ directly — see
voi_boundary_validation.py's own comment for why: build_attribution_
table.py globs "*_result.json" at that directory's top level for
milestone manifests, and these per-scene sweep files are a different
artifact, feeding e2_preliminary_report.py's clustered aggregation, not
the single-scene attribution table).

A scene missing state data entirely (no state_train_folders/state_labels)
runs the location axis only for that scene — reported, not silently
padded.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import replace

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import (
    aggregate_category_stats,
    rerun_frozen_e0,
    rerun_frozen_state_e0,
    state_category_stats_from_train,
    write_result_manifest,
)
from dynamic_home_eqa.embodied.experiment_config import FROZEN, FrozenConfig
from dynamic_home_eqa.embodied.policy import (
    AlwaysResense,
    AnswerImmediately,
    CoverageStop,
    DecayThreshold,
    DecayVoi,
    DecayVoiConfig,
    DecayVoiRouting,
    RandomResense,
    RandomResenseConfig,
    TimeOnlyThreshold,
)
from dynamic_home_eqa.embodied.posterior import (
    PosteriorBeliefStore,
    TimeOfDayBeliefStore,
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
from dynamic_home_eqa.scripts.scene_validation import validate_folder

_N_TOD_BUCKETS = 4
_BINDING_LATENCY_WEIGHT = 0.01  # results/reports/voi_boundary.md
# results/reports/budget_matched_random.md — calibrated so budget_matched_
# random's realized mean travel distance matches decay_voi's ~2.2m on the
# frozen scene (scripts/budget_matched_random_calibration.py's own grid
# search, not guessed).
_BUDGET_MATCHED_P_RESENSE = 0.12
_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"
_POOL_STATE_PATH = _DYNAMIC_EQA / "generation_out" / "_expand_scene_pool_state.json"


def _policies() -> dict[str, object]:
    """Same policy set embodied_m3_gate.py uses, minus conformal_decay_
    threshold (dropped in the coverage-repair phase), with decay_voi/
    decay_voi_routing at the validated binding latency_weight instead of
    the untested default, plus two cheap model-free control baselines
    (budget_matched_random, time_only_threshold) added for the LLM-agent
    comparison phase — see results/reports/INDEX.md."""
    voi_config = DecayVoiConfig(latency_weight=_BINDING_LATENCY_WEIGHT)
    return {
        "answer_immediately":     AnswerImmediately(),
        "always_resense":         AlwaysResense(),
        "coverage_stop":          CoverageStop(),
        "decay_threshold":        DecayThreshold(),
        "decay_voi":              DecayVoi(voi_config),
        "decay_voi_routing":      DecayVoiRouting(voi_config),
        "budget_matched_random":  RandomResense(RandomResenseConfig(p_resense=_BUDGET_MATCHED_P_RESENSE, seed=0)),
        "time_only_threshold":    TimeOnlyThreshold(),
    }


def _folder_names(scene_id: str, profile: str) -> tuple[str, tuple[str, ...], str]:
    base = f"{scene_id}_{profile}"
    day0 = base
    train_folders = (day0,) + tuple(f"{base}_day{d}" for d in range(1, 4))
    eval_folder = f"{base}_day4"
    return day0, train_folders, eval_folder


def _all_days_valid(out_dir: pathlib.Path, folders: tuple[str, ...]) -> bool:
    return all((out_dir / f).exists() and validate_folder(out_dir, f).ok for f in folders)


def discover_scene_configs(out_dir: pathlib.Path) -> list[FrozenConfig]:
    """One FrozenConfig per scene that is disk-verified location-qualifying
    today (the frozen scene plus every pool scene with 5/5 trace_validate-
    passing days and a nonempty qualified_labels list), each carrying its
    own scene/profile/folders/labels but sharing FROZEN's experiment
    parameters (wait_hours_sweep, patrol_start, seed, navmesh) — those are
    experiment design choices, not per-scene data."""
    configs = [FROZEN]
    if not _POOL_STATE_PATH.exists():
        return configs

    state = json.loads(_POOL_STATE_PATH.read_text())
    for scene_id, info in sorted(state.items()):
        if not info.get("reachable") or not info.get("profile"):
            continue
        profile = info["profile"]
        qualified = tuple(info.get("qualified_labels") or ())
        if not qualified:
            continue

        day0, train_folders, eval_folder = _folder_names(scene_id, profile)
        location_folders = train_folders + (eval_folder,)
        if not _all_days_valid(out_dir, location_folders):
            continue

        state_train_folders: tuple[str, ...] = ()
        state_eval_folder = ""
        state_labels: tuple[str, ...] = ()
        state_base = f"{scene_id}_{profile}_state"
        candidate_state_train = (state_base,) + tuple(f"{state_base}_day{d}" for d in range(1, 4))
        candidate_state_eval = f"{state_base}_day4"
        if _all_days_valid(out_dir, candidate_state_train + (candidate_state_eval,)):
            # State labels aren't tracked in the pool state file the way
            # location's qualified_labels are — derive them the same way
            # generate_state_stratum.py's own scene qualification does:
            # every STATEFUL_FURNITURE category present in this scene's
            # state manifests, one instance each ("{category}_1").
            eval_manifest = json.loads((out_dir / candidate_state_eval / "manifest.json").read_text())
            present_categories = {
                c["object_category"] for c in eval_manifest["changes"] if c.get("change_type") == "state_change"
            }
            candidate_state_labels = tuple(sorted(f"{cat}_1" for cat in present_categories if cat in STATEFUL_FURNITURE))
            if candidate_state_labels:
                state_train_folders = candidate_state_train
                state_eval_folder = candidate_state_eval
                state_labels = candidate_state_labels

        configs.append(replace(
            FROZEN,
            scene=scene_id, profile=profile, train_folders=train_folders, eval_folder=eval_folder,
            labels=qualified, state_train_folders=state_train_folders,
            state_eval_folder=state_eval_folder, state_labels=state_labels,
        ))
    return configs


def run_scene(config: FrozenConfig, out_dir: pathlib.Path) -> pathlib.Path:
    """Runs the full policy set (location axis, plus state axis and
    tod_prior where that scene has the data) for one scene, writing its
    own diagnostics/e2_preliminary_<scene>_result.json. Returns the
    written path."""
    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in config.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)
    location_category_stats = aggregate_category_stats(
        [category_location_change_stats(m["changes"]) for m in train_manifests]
    )
    location_kernels = fit_transition_kernels(train_manifests, location_category_stats, anchor_history)

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

    results_dir = out_dir.parent / "embodied_results"
    tmp_location = results_dir / f"_e2_prelim_{config.scene}_location_tmp.json"
    tmp_tod = results_dir / f"_e2_prelim_{config.scene}_tod_tmp.json"

    location_rows = rerun_frozen_e0(
        milestone="e2_preliminary", policies=_policies(), question_factory=location_question_factory,
        out_dir=out_dir, result_path=tmp_location, config=config,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
    )
    tmp_location.unlink()

    tod_rows = rerun_frozen_e0(
        milestone="e2_preliminary", policies={"tod_prior": AnswerImmediately()},
        question_factory=location_question_factory, out_dir=out_dir, result_path=tmp_tod, config=config,
        belief_factory=lambda _decay_models: TimeOfDayBeliefStore(bucketed_kernels, n_buckets=_N_TOD_BUCKETS),
    )
    tmp_tod.unlink()

    state_rows: list[dict] = []
    if config.state_labels:
        state_flip_stats = state_category_stats_from_train(out_dir, config)
        state_category_stats = {
            key: {"location_changes": stats["flip_count"], "mean_dwell_hours": stats["mean_dwell_hours"]}
            for key, stats in state_flip_stats.items()
        }
        state_train_manifests = [
            json.loads((out_dir / f / "manifest.json").read_text()) for f in config.state_train_folders
        ]
        state_variable_domains = {
            key: STATE_VARIABLES[key.split("::")[1]]["values"] for key in state_category_stats
        }
        state_kernels = fit_state_transition_kernels(state_train_manifests, state_category_stats, state_variable_domains)
        state_resense_anchors = {f"{cat}::{var}": cat for cat, var in STATEFUL_FURNITURE.items()}

        def state_question_factory(label, category, variable, asked_t, world, decay_models):
            return generate_state_question(
                label=label, category=category, variable=variable, asked_t=asked_t,
                initial_state=world.initial_state, changes=world.changes, decay_models=decay_models,
            )

        tmp_state = results_dir / f"_e2_prelim_{config.scene}_state_tmp.json"
        state_rows = rerun_frozen_state_e0(
            milestone="e2_preliminary", policies=_policies(), question_factory=state_question_factory,
            out_dir=out_dir, result_path=tmp_state, config=config,
            belief_factory=lambda _decay_models: PosteriorBeliefStore(state_kernels, resense_anchors=state_resense_anchors),
        )
        tmp_state.unlink()

    all_rows = location_rows + tod_rows + state_rows
    _DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _DIAGNOSTICS_DIR / f"e2_preliminary_{config.scene}_result.json"
    write_result_manifest(out_path, "e2_preliminary", config, all_rows)
    return out_path


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    configs = discover_scene_configs(out_dir)
    print(f"Running preliminary E2 sweep on {len(configs)} validated scene(s): "
          f"{[c.scene for c in configs]}")

    written = []
    for i, config in enumerate(configs):
        print(f"\n[{i + 1}/{len(configs)}] scene={config.scene} profile={config.profile} "
              f"n_location_labels={len(config.labels)} n_state_labels={len(config.state_labels)}")
        path = run_scene(config, out_dir)
        written.append(path)
        print(f"  wrote {path}")

    print(f"\nWrote {len(written)} per-scene result file(s) under {_DIAGNOSTICS_DIR}")


if __name__ == "__main__":
    main()
