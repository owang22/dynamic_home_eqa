"""
attribution.py — shared "rerun the frozen E0 configuration" harness every
post-E0 milestone's gate script calls, so each milestone's effect can be
attributed to its own change and nothing else (a different question set,
day split, or seed between reruns would confound the comparison the
attribution table exists to make).

Each milestone script supplies its own BeliefStore/policy implementations
and a question factory (M1's fixed-anchor MCQ; a later milestone's
posterior-belief-aware question, etc.) but shares this same patrol/dock/
ask loop and result-row schema — the loop itself is not what differs
between milestones.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict
from typing import Callable, Optional

from .belief import BeliefStore, aggregate_category_stats, fit_decay_models
from .config import AgentConfig
from .experiment_config import FROZEN, FrozenConfig
from .question import MCQQuestion
from .runner import EpisodeConfig, QuestionEpisodeRunner
from .scoring import compute_ece
from .world import EmbodiedWorld

QuestionFactory = Callable[[str, str, float, "EmbodiedWorld", dict], MCQQuestion]

# Every module whose code directly determines an episode's outcome
# (decision logic, belief updates, scoring) — NOT experiment_config/
# runner/world, which are already covered by FrozenConfig.fingerprint()
# and this repo's own navmesh/scene bookkeeping. A change to any of these
# four files changes what a result row MEANS even when FrozenConfig's own
# fingerprint is untouched — exactly what happened in the coverage-repair
# phase: fixing calibrate_conformal_theta's calibration-space bug changed
# conformal_decay_threshold's behavior (state briers moved) under an
# unchanged FrozenConfig.fingerprint(), and only a voluntary full-table
# rebuild kept embodied_results/ consistent. behavior_code_hash() closes
# that hole mechanically instead of relying on someone remembering to
# rebuild.
_BEHAVIOR_MODULES = ("policy.py", "belief.py", "posterior.py", "scoring.py")


def _compute_behavior_code_hash() -> str:
    import hashlib

    h = hashlib.sha256()
    module_dir = pathlib.Path(__file__).parent
    for name in _BEHAVIOR_MODULES:
        h.update((module_dir / name).read_bytes())
    return h.hexdigest()[:16]


# Computed ONCE, at import time — NOT lazily inside behavior_code_hash()
# on every call. A gate script's own run can take several minutes
# (habitat_sim, one fresh EmbodiedWorld per trial); re-reading these files
# from disk at the END of that run (when the result manifest is written)
# would record whatever happens to be on disk THEN, not the code this
# process actually ran under the whole time — a real race caught while
# building this guard: a concurrent edit to posterior.py mid-run produced
# two result files (e0, m1) with DIFFERENT code_hashes despite neither
# process's actual behavior having changed after it started. Capturing
# the hash at import time (attribution.py is imported once, near process
# start, before any of these four files' bytes are read again) ties the
# hash to what this process loaded and will run under for its whole
# lifetime, not what's on disk whenever it happens to finish.
_BEHAVIOR_CODE_HASH = _compute_behavior_code_hash()


def behavior_code_hash() -> str:
    """SHA-256 (truncated) over the exact byte contents of every
    behavior-bearing module (see _BEHAVIOR_MODULES), captured once at
    import time (see _BEHAVIOR_CODE_HASH's own comment for why) — stamped
    into every result manifest (see rerun_frozen_e0/rerun_frozen_state_e0)
    so scripts/build_attribution_table.py can refuse to combine rows
    produced by different code, the same fatal semantics it already
    applies to FrozenConfig.fingerprint() mismatches. Hashes file bytes
    directly rather than a git commit — this repo has no git history to
    hash a commit from (see e2_headline_comparison.pipeline_version's own
    docstring for the identical constraint)."""
    return _BEHAVIOR_CODE_HASH


def fit_decay_models_from_train(out_dir: pathlib.Path, config: FrozenConfig = FROZEN):
    from ..generation.exports import category_location_change_stats

    per_day_stats = []
    for folder_name in config.train_folders:
        manifest = json.loads((out_dir / folder_name / "manifest.json").read_text())
        per_day_stats.append(category_location_change_stats(manifest["changes"]))
    return fit_decay_models(aggregate_category_stats(per_day_stats))


def aggregate_flip_stats(days: list[dict[str, dict]]) -> dict[str, dict]:
    """State-axis counterpart of belief.aggregate_category_stats: merges
    category_state_flip_stats from several days into one changes-weighted
    mean_dwell_hours per key."""
    totals: dict[str, dict] = {}
    for day_stats in days:
        for key, stats in day_stats.items():
            agg = totals.setdefault(key, {"flip_count": 0, "_dwell_weighted_sum": 0.0, "_dwell_weight": 0})
            agg["flip_count"] += stats["flip_count"]
            if stats.get("mean_dwell_hours") is not None:
                weight = stats["flip_count"]
                agg["_dwell_weighted_sum"] += stats["mean_dwell_hours"] * weight
                agg["_dwell_weight"] += weight

    out: dict[str, dict] = {}
    for key, agg in totals.items():
        mean_dwell = (agg["_dwell_weighted_sum"] / agg["_dwell_weight"]) if agg["_dwell_weight"] > 0 else None
        out[key] = {"flip_count": agg["flip_count"], "mean_dwell_hours": mean_dwell}
    return out


def state_category_stats_from_train(out_dir: pathlib.Path, config: FrozenConfig = FROZEN) -> dict[str, dict]:
    """Aggregated category_state_flip_stats (keyed "{category}::{variable}")
    across config.state_train_folders. Consumed two ways: fit_decay_models
    (below — only reads mean_dwell_hours, name-agnostic) and
    posterior.fit_transition_kernels (which reads own_weight via
    stats.get("location_changes", 0) specifically) — callers of the
    latter must translate {"flip_count": v} -> {"location_changes": v} at
    the call site (see scripts/embodied_m3_gate.py); kept as a translation
    the M2-kernel-fitting caller does explicitly, rather than silently
    renaming this dict's honest "flip_count" key, which every other
    consumer (and generation/exports.py's own tests) expects."""
    from ..generation.exports import category_state_flip_stats

    per_day_stats = []
    for folder_name in config.state_train_folders:
        manifest = json.loads((out_dir / folder_name / "manifest.json").read_text())
        per_day_stats.append(category_state_flip_stats(manifest["changes"]))
    return aggregate_flip_stats(per_day_stats)


def fit_decay_models_from_state_train(out_dir: pathlib.Path, config: FrozenConfig = FROZEN):
    """State-axis counterpart of fit_decay_models_from_train — one
    DecayModel per synthetic "{category}::{variable}" key."""
    return fit_decay_models(state_category_stats_from_train(out_dir, config))


def fit_location_kernels_from_train(out_dir: pathlib.Path, config: FrozenConfig = FROZEN):
    """One posterior.TransitionKernel per category, fit from
    config.train_folders — the same recipe scripts/embodied_m3_gate.py
    builds its own location_kernels with (category_anchor_history,
    aggregate_category_stats, category_location_change_stats,
    fit_transition_kernels), centralized here so any caller of
    belief.calibrate_conformal_theta (which must be calibrated against
    these exact kernels — the ones PosteriorBeliefStore.validity()
    propagates at deployment, not a separate DecayModel proxy; see that
    function's own docstring) fits the identical kernels rather than
    re-deriving a possibly-divergent copy."""
    from ..generation.exports import category_location_change_stats
    from .posterior import fit_transition_kernels
    from .question import category_anchor_history

    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in config.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    category_stats = aggregate_category_stats(
        [category_location_change_stats(m["changes"]) for m in train_manifests]
    )
    return fit_transition_kernels(train_manifests, category_stats, anchor_history)


def fit_state_kernels_from_train(out_dir: pathlib.Path, config: FrozenConfig = FROZEN):
    """State-axis counterpart of fit_location_kernels_from_train — one
    TransitionKernel per synthetic "{category}::{variable}" key, the same
    recipe scripts/embodied_m3_gate.py builds its own state_kernels with."""
    from ..env.deltas import STATE_VARIABLES
    from .posterior import fit_state_transition_kernels

    state_train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in config.state_train_folders
    ]
    flip_stats = state_category_stats_from_train(out_dir, config)
    category_stats = {
        key: {"location_changes": stats["flip_count"], "mean_dwell_hours": stats["mean_dwell_hours"]}
        for key, stats in flip_stats.items()
    }
    variable_domains = {key: STATE_VARIABLES[key.split("::")[1]]["values"] for key in category_stats}
    return fit_state_transition_kernels(state_train_manifests, category_stats, variable_domains)


def write_result_manifest(
    result_path: pathlib.Path,
    milestone: str,
    config: FrozenConfig,
    rows: list[dict],
) -> None:
    """The one function that writes a milestone result manifest — stamps
    fingerprint and code_hash uniformly. Every gate/experiment script's
    final write must route through this (directly, or via rerun_frozen_e0/
    rerun_frozen_state_e0 below, which call it) rather than constructing
    the manifest dict itself.

    VoI validation batch, item 3 (single-writer manifest enforcement): the
    coverage-repair phase's code_hash guard and the M2/M3 gates' own
    bypass of it (each script merged several rerun_frozen_e0 calls' temp
    files into a final manifest via its own separate json.dumps, omitting
    code_hash entirely) were the same root cause — multiple writers with
    no single choke point to enforce a guard at. tests/test_single_writer_
    manifest.py greps every script for a manifest-shaped json.dumps call
    outside this module and fails if one is found, so a new script that
    writes its own manifest fails CI rather than relying on review."""
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps({
        "milestone": milestone,
        "fingerprint": config.fingerprint(),
        "code_hash": behavior_code_hash(),
        "config": asdict(config),
        "rows": rows,
    }, indent=2))


def rerun_frozen_e0(
    milestone: str,
    policies: dict[str, object],
    question_factory: QuestionFactory,
    out_dir: pathlib.Path,
    result_path: pathlib.Path,
    config: FrozenConfig = FROZEN,
    belief_factory: Optional[Callable[[dict], BeliefStore]] = None,
    agent_config: Optional[AgentConfig] = None,
) -> list[dict]:
    """Run every (policy, wait_hours, label) trial in the frozen
    configuration, one fresh world/belief/patrol per trial (see E0's own
    module docstring for why sequential per-episode questions confound the
    wait_hours variable), and write a result file tagged with the frozen
    config's fingerprint so build_attribution_table.py can verify every
    milestone actually used the identical setup.

    agent_config, if given, is passed through to every EmbodiedWorld this
    builds — e.g. E1's cost_model toggle (embodied.config.CostModelConfig)
    swaps what travel_time_to reports to the policy without touching
    FrozenConfig.fingerprint() at all (agent_config is not part of that
    hash — see experiment_config.FrozenConfig's own docstring for what is).
    Defaults to None (EmbodiedWorld's own AgentConfig() default), matching
    every milestone before E1 exactly.
    """
    eval_manifest = json.loads((out_dir / config.eval_folder / "manifest.json").read_text())
    eval_result = json.loads((out_dir / config.eval_folder / "generation_result.json").read_text())
    decay_models = fit_decay_models_from_train(out_dir, config)

    if belief_factory is None:
        belief_factory = lambda _decay_models: BeliefStore(decay_models=_decay_models)  # noqa: E731

    rows: list[dict] = []
    for policy_name, policy in policies.items():
        for wait_hours in config.wait_hours_sweep:
            for label in config.labels:
                world = EmbodiedWorld(config.scene, eval_result, eval_manifest, config=agent_config)
                belief = belief_factory(decay_models)
                try:
                    runner = QuestionEpisodeRunner(
                        world, belief, policy, EpisodeConfig(patrol_start=config.patrol_start, wait_hours=wait_hours)
                    )
                    runner.patrol()

                    instances = world.current_instances()
                    if label not in instances:
                        continue
                    category, _slot = instances[label]

                    runner.dock_and_wait(wait_hours)
                    question = question_factory(label, category, world.t, world, decay_models)
                    episode = runner.run_question(question)

                    rows.append({
                        "milestone":           milestone,
                        "fingerprint":         config.fingerprint(),
                        # scene + eval_folder identify this row's cluster
                        # for E1-E4's clustered statistics (questions
                        # within a scene-day are not independent — see
                        # scripts/e2_headline_comparison.py's module
                        # docstring); one scene contributes one eval day
                        # today, so (scene, eval_folder) together are the
                        # cluster key, not scene alone, once a scene ever
                        # contributes more than one eval day.
                        "scene":               config.scene,
                        "eval_folder":         config.eval_folder,
                        "policy":              policy_name,
                        "wait_hours":          wait_hours,
                        "label":               label,
                        "category":            category,
                        "hazard_class":        question.hazard_class,
                        "question_type":       question.question_type,
                        "correct":             episode.correct,
                        "abstained":           episode.abstained,
                        "confidence":          episode.confidence,
                        "brier":               episode.brier,
                        "answer_latency_s":    episode.answer_latency_s,
                        "distance_traveled_m": episode.distance_traveled_m,
                        "policy_invocations":  episode.policy_invocations,
                        # Full per-observation event stream (patrol/wait/
                        # decision/resense/answer entries — see runner.py's
                        # QuestionEpisodeRunner._log), kept so a mechanism
                        # decomposition (which flips were caused by which
                        # observation, vs. summary accuracy/Brier/ECE alone)
                        # can be computed from this result file directly
                        # rather than requiring a dedicated rerun.
                        "log":                 episode.log,
                    })
                finally:
                    world.close()

    write_result_manifest(result_path, milestone, config, rows)
    return rows


StateQuestionFactory = Callable[[str, str, str, float, "EmbodiedWorld", dict], MCQQuestion]


def rerun_frozen_state_e0(
    milestone: str,
    policies: dict[str, object],
    question_factory: StateQuestionFactory,
    out_dir: pathlib.Path,
    result_path: pathlib.Path,
    config: FrozenConfig = FROZEN,
    belief_factory: Optional[Callable[[dict], BeliefStore]] = None,
    agent_config: Optional[AgentConfig] = None,
) -> list[dict]:
    """State-axis counterpart of rerun_frozen_e0 (M3: state-change
    dynamics) — same patrol/dock/ask loop and result-row schema, over
    config.state_labels (real instance ids, e.g. "fridge_1") against
    config.state_eval_folder/state_train_folders instead of the location
    ones. question_factory here takes (label, category, variable, asked_t,
    world, decay_models) — one extra argument versus QuestionFactory,
    since a label's state variable isn't recoverable from world.
    current_instances() the way its location category is.

    Tagged with the SAME config.fingerprint() rerun_frozen_e0 uses (both
    read every field of the one shared FrozenConfig instance) — calling
    both against the same `config` for one milestone lets their rows share
    one attribution-table fingerprint without special-casing.

    agent_config: see rerun_frozen_e0's own docstring — passed through
    unchanged to every EmbodiedWorld this builds.
    """
    from ..env.inventory import STATEFUL_FURNITURE

    eval_manifest = json.loads((out_dir / config.state_eval_folder / "manifest.json").read_text())
    eval_result = json.loads((out_dir / config.state_eval_folder / "generation_result.json").read_text())
    decay_models = fit_decay_models_from_state_train(out_dir, config)

    if belief_factory is None:
        belief_factory = lambda _decay_models: BeliefStore(decay_models=_decay_models)  # noqa: E731

    rows: list[dict] = []
    for policy_name, policy in policies.items():
        for wait_hours in config.wait_hours_sweep:
            for label in config.state_labels:
                world = EmbodiedWorld(config.scene, eval_result, eval_manifest, config=agent_config)
                belief = belief_factory(decay_models)
                try:
                    runner = QuestionEpisodeRunner(
                        world, belief, policy, EpisodeConfig(patrol_start=config.patrol_start, wait_hours=wait_hours)
                    )
                    runner.patrol()

                    instances = world.current_instances()
                    if label not in instances:
                        continue
                    category, _slot = instances[label]
                    variable = STATEFUL_FURNITURE.get(category)
                    if variable is None:
                        continue

                    runner.dock_and_wait(wait_hours)
                    question = question_factory(label, category, variable, world.t, world, decay_models)
                    episode = runner.run_question(question)

                    rows.append({
                        "milestone":           milestone,
                        "fingerprint":         config.fingerprint(),
                        "scene":               config.scene,
                        "eval_folder":         config.state_eval_folder,
                        "policy":              policy_name,
                        "wait_hours":          wait_hours,
                        "label":               question.label,   # synthetic "label::variable" belief key
                        "category":            question.category,
                        "hazard_class":        question.hazard_class,
                        "question_type":       question.question_type,
                        "correct":             episode.correct,
                        "abstained":           episode.abstained,
                        "confidence":          episode.confidence,
                        "brier":               episode.brier,
                        "answer_latency_s":    episode.answer_latency_s,
                        "distance_traveled_m": episode.distance_traveled_m,
                        "policy_invocations":  episode.policy_invocations,
                        "log":                 episode.log,
                    })
                finally:
                    world.close()

    write_result_manifest(result_path, milestone, config, rows)
    return rows


def summarize_rows(rows: list[dict]) -> list[dict]:
    """One summary row per (milestone, policy, wait_hours): accuracy (of
    non-abstained, answerable questions), mean Brier, ECE, abstain rate,
    mean latency, mean travel distance."""
    by_key: dict[tuple, list[dict]] = {}
    for r in rows:
        by_key.setdefault((r["milestone"], r["policy"], r["wait_hours"]), []).append(r)

    summaries = []
    for (milestone, policy, wait_hours), group in sorted(by_key.items()):
        n = len(group)
        abstain_rate = sum(1 for r in group if r["abstained"]) / n if n else 0.0
        scored = [r for r in group if r["correct"] is not None]
        accuracy = (sum(1 for r in scored if r["correct"]) / len(scored)) if scored else float("nan")
        mean_brier = sum(r["brier"] for r in group) / n if n else float("nan")
        confidences = [r["confidence"] for r in scored if r["confidence"] is not None]
        corrects = [r["correct"] for r in scored if r["confidence"] is not None]
        ece = compute_ece(confidences, corrects) if confidences else float("nan")
        mean_latency = sum(r["answer_latency_s"] for r in group) / n if n else float("nan")
        mean_travel = sum(r["distance_traveled_m"] for r in group) / n if n else float("nan")
        summaries.append({
            "milestone": milestone, "policy": policy, "wait_hours": wait_hours, "n": n,
            "accuracy": accuracy, "mean_brier": mean_brier, "ece": ece,
            "abstain_rate": abstain_rate, "mean_latency_s": mean_latency, "mean_travel_m": mean_travel,
        })
    return summaries
