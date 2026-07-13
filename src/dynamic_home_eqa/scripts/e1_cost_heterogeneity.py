#!/usr/bin/env python3
"""
e1_cost_heterogeneity.py — E1: travel-cost heterogeneity.

IV: cost model (real_geodesic vs flat). Claim tested: distance-dependent
travel cost changes which policy wins the accuracy-vs-cost frontier — a
policy whose resense-vs-answer tradeoff assumes every leg costs the same
(as a text-only or grid-world benchmark effectively would) should make
worse decisions than one that sees this scene's real, geometry-dependent
travel time, and the ranking gap should show up here.

Reuses the M3 gate's own location-axis kernels/question machinery
unchanged (fit_location_kernels_from_train, category_anchor_history) —
the belief side of every policy is completely unaffected by cost_model
(posterior.TransitionKernel/PosteriorBeliefStore never see travel time at
all); only runner.py's travel_time_to closure, and therefore policy.act()'s
own resense-vs-answer decision, changes. Policy set matches embodied_
m3_gate.py's own _policies() (no conformal_decay_threshold — dropped in
the coverage-repair phase, see that module's docstring). embodied_results/
m3_result.json's location rows ARE the real_geodesic arm already
(EmbodiedWorld's own AgentConfig() default before this script existed) —
this script only needs to run the flat arm fresh.

flat_leg_seconds is fixed to this scene's pool-mean geodesic leg time
(mean geodesic_time from the agent's initial spawn pose to every
category-plausible anchor in category_anchor_history) so total travel
budgets are comparable across the two cost models, rather than the flat
model being a free win (or an artificial loss) from an arbitrary constant.

REHEARSAL: one scene (102343992) — same single-cluster bootstrap caveat
as scripts/e2_headline_comparison.py; every output is tagged REHEARSAL.

Coverage-repair phase, item 3 (E1 lambda forensics): the rehearsal run
this script originally shipped with (cost_model swept, latency_weight
left at DecayVoiConfig's own default) found zero rank changes and zero
row-level differences at all between the real_geodesic and flat arms.
That null result is VOID AS EVIDENCE, not a finding — see LATENCY_WEIGHT_
SWEEP below and this module's own notes for why. --latency-weight lets a
caller run this script at a specific point in E0's own separation region
instead of DecayVoi's untested default; the full (cost_model x
latency_weight) grid is deferred to the multi-scene pool (see this
module's docstring further down), not run here.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib
from typing import Optional

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import (
    fit_location_kernels_from_train,
    rerun_frozen_e0,
)
from dynamic_home_eqa.embodied.config import AgentConfig, CostModelConfig
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import (
    AlwaysResense,
    AnswerImmediately,
    CoverageStop,
    DecayThreshold,
    DecayVoi,
    DecayVoiConfig,
    DecayVoiRouting,
)
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore
from dynamic_home_eqa.embodied.question import (
    categories_ever_outdoor,
    category_anchor_history,
    generate_mcq_question,
)
from dynamic_home_eqa.embodied.world import EmbodiedWorld

_REHEARSAL_TAG = "REHEARSAL"
_M3_RESULT_PATH = _DYNAMIC_EQA / "embodied_results" / "m3_result.json"

# Coverage-repair phase, item 3 (E1 lambda forensics), corrected in the
# VoI validation batch: DecayVoiConfig.latency_weight is a PER-SECOND
# rate (cost = latency_weight * travel_seconds — see policy.py's
# DecayVoi.act()), NOT per-hour; an earlier version of this comment
# described the binding region in per-hour terms and mis-transcribed the
# sweep values that follow as if they were already per-second, which they
# were, but the accompanying prose obscured that and invited exactly this
# kind of units error. All values below are in the field's own native
# unit: accuracy-units penalty per SECOND of travel.
#
# The default (1.0/3600 ~= 0.000278/s) prices a ~4s leg at ~0.001
# accuracy — far below the accuracy-gain magnitudes (0.1-0.9) that
# actually drive DecayVoi's resense-vs-answer decision, so cost could
# never bind at that default; the original E1 rehearsal (default
# latency_weight, cost_model swept) found zero rank changes and zero
# row-level differences at all, which is VOID AS EVIDENCE for or against
# E1's claim, not a null finding.
#
# embodied_e0_regime_check.py's own "utility sweep" does NOT test this
# either: it re-weights ALREADY-COLLECTED accuracy/latency data post hoc
# to rank whole policies by utility = accuracy - lambda*latency_hours
# (note: hours there, a DIFFERENT quantity from this policy's own
# per-second latency_weight), using decay_voi's OWN internal decisions
# (made at its fixed default latency_weight) as one fixed input, not a
# live decision variable. Rerunning E0 confirms decay_voi's accuracy AND
# mean_latency were identical to always_resense's at every wait_hours
# tested — so E0's reported "separation" is a real accuracy split between
# resensing and not, but between {always_resense, decay_voi} as a TIED
# GROUP versus answer_immediately, not evidence about any lambda where
# DecayVoi's OWN threshold would choose differently from "always
# resense".
#
# For cost to bind (cost ~= gain), latency_weight ~= gain / travel_seconds.
# With gain of order 0.1-0.9 and this scene's legs running ~4-30s, that
# puts the binding region at roughly 0.003-0.2 per second. LATENCY_WEIGHT_
# SWEEP below brackets that region with margin on both sides — well below
# (still tied to always_resense, for confirmation) and well above (fully
# suppressed, cost dwarfs any possible gain).
LATENCY_WEIGHT_SWEEP: tuple[float, ...] = (0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0)


def _policies(latency_weight: Optional[float] = None) -> dict[str, object]:
    """Same policy set the M3 gate's location axis uses (scripts/
    embodied_m3_gate.py's own _policies) — duplicated here rather than
    imported, matching this repo's existing pattern of each gate script
    owning its policy set inline (m2_gate/m3_gate do not share one
    either). conformal_decay_threshold is absent — see embodied_m3_gate.
    py's module docstring for why it was dropped in the coverage-repair
    phase (its guarantee failed at every wait_hours bucket but the
    shortest, traced to kernel misspecification, not a calibration bug).

    latency_weight, if given, overrides DecayVoi/DecayVoiRouting's own
    DecayVoiConfig default for both policies — the E1 lambda-forensics
    sweep axis (see LATENCY_WEIGHT_SWEEP above). None (the default)
    reproduces the untested DecayVoiConfig() default exactly."""
    decay_voi_config = DecayVoiConfig() if latency_weight is None else DecayVoiConfig(latency_weight=latency_weight)
    return {
        "answer_immediately":       AnswerImmediately(),
        "always_resense":           AlwaysResense(),
        "coverage_stop":          CoverageStop(),
        "decay_threshold":          DecayThreshold(),
        "decay_voi":                DecayVoi(decay_voi_config),
        "decay_voi_routing":        DecayVoiRouting(decay_voi_config),
    }


def compute_pool_mean_leg_seconds(out_dir: pathlib.Path, config=FROZEN) -> float:
    """Mean geodesic_time from the agent's initial spawn pose to every
    category-plausible anchor (category_anchor_history, pooled across all
    categories) reachable from that pose — this scene's own average
    "go check on something" leg, in seconds. Unreachable anchors
    (geodesic_time == inf) are excluded, matching how travel_time_to
    itself treats them (a cost model only ever assigns a finite value to
    something the agent could actually walk to)."""
    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in config.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    all_anchors = sorted({a for anchors in anchor_history.values() for a in anchors})

    eval_manifest = json.loads((out_dir / config.eval_folder / "manifest.json").read_text())
    eval_result = json.loads((out_dir / config.eval_folder / "generation_result.json").read_text())
    world = EmbodiedWorld(config.scene, eval_result, eval_manifest)
    try:
        origin = world.pose.position
        legs = []
        for anchor in all_anchors:
            vp = world.viewpoint_for(anchor)
            if vp is None:
                continue
            cost = world.geodesic_time(origin, vp.position)
            if cost == float("inf"):
                continue
            legs.append(cost)
    finally:
        world.close()

    if not legs:
        raise ValueError("no reachable anchors found — cannot compute a pool-mean leg time")
    return sum(legs) / len(legs)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--latency-weight", type=float, default=None,
                     help="Override DecayVoiConfig's own default (accuracy-units penalty per "
                          "second of travel) for both decay_voi and decay_voi_routing — the E1 "
                          "lambda-forensics sweep axis (see LATENCY_WEIGHT_SWEEP). Default: "
                          "DecayVoiConfig's own untested default.")
    args = ap.parse_args()

    out_dir = _DYNAMIC_EQA / "generation_out"
    results_dir = _DYNAMIC_EQA / "embodied_results"

    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders
    ]
    anchor_history = category_anchor_history(train_manifests)
    outdoor_categories = categories_ever_outdoor(train_manifests)
    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)

    flat_leg_seconds = compute_pool_mean_leg_seconds(out_dir, FROZEN)
    print(f"Pool-mean geodesic leg time: {flat_leg_seconds:.2f}s (flat_leg_seconds)")

    def question_factory(label, category, asked_t, world, decay_models):
        return generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=world.initial_state, changes=world.changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models,
        )

    flat_agent_config = AgentConfig(
        cost_model=CostModelConfig(mode="flat", flat_leg_seconds=flat_leg_seconds),
    )

    lw_tag = "default" if args.latency_weight is None else f"lw{args.latency_weight}"
    result_path = results_dir / f"e1_flat_{lw_tag}_result.json"

    rerun_frozen_e0(
        milestone="e1_flat", policies=_policies(args.latency_weight), question_factory=question_factory,
        out_dir=out_dir, result_path=result_path,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
        agent_config=flat_agent_config,
    )
    print(f"Wrote {result_path}")

    if not _M3_RESULT_PATH.exists():
        print(f"\nNo real_geodesic arm found at {_M3_RESULT_PATH} — run scripts/embodied_m3_gate.py "
              "first, then rerun this script's comparison step separately (see "
              "scripts/e1_frontier_comparison.py).")
        return


if __name__ == "__main__":
    main()
