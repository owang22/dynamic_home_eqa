#!/usr/bin/env python3
"""
voi_m2_reattribution.py — VoI validation batch, item 1d: does the M2
discovery result (19 discovery-driven vs. 1 abstention-driven flip) survive
when decay_voi is actually exercising judgment (a latency_weight where it
partially declines resenses), rather than shadowing always_resense's
blanket "always resense" rule?

voi_boundary_validation.py's transition table shows decay_voi's location-
axis behavior is genuinely mixed (partial declines, not 0% or 100%) at
latency_weight=0.01 — the boundary between "matches always_resense" and
"fully suppressed" sits between latency_weight=0.01 and 0.03. This script
reruns decay_voi at 0.01 fresh (rerun_frozen_e0 does not persist per-
lambda rows, only the sweep summary), merges it with the already-validated
answer_immediately baseline rows from embodied_results/m3_result.json, and
runs the same wrong->right / wrong->abstain decomposition e0_mechanism_
decomposition.py uses, reporting it side by side with the DEFAULT-lambda
number already on record.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train, rerun_frozen_e0
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import DecayVoi, DecayVoiConfig
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore
from dynamic_home_eqa.embodied.question import categories_ever_outdoor, category_anchor_history, generate_mcq_question
from dynamic_home_eqa.scripts.e0_mechanism_decomposition import decompose, summarize

_M3_RESULT_PATH = _DYNAMIC_EQA / "embodied_results" / "m3_result.json"
# Not embodied_results/ directly — see voi_boundary_validation.py's
# _DIAGNOSTICS_DIR comment: build_attribution_table.py globs
# "*_result.json" at that directory's top level for milestone manifests,
# and this script's own summary output is a diagnostic artifact, not one.
_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"
_BINDING_LATENCY_WEIGHT = 0.01


def _discovery_counts(records) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in records:
        counts[r.transition] = counts.get(r.transition, 0) + 1
    return counts


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    results_dir = _DYNAMIC_EQA / "embodied_results"

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

    tmp = results_dir / "_voi_m2_reattribution_tmp.json"
    binding_rows = rerun_frozen_e0(
        milestone="voi_m2_reattribution",
        policies={"decay_voi": DecayVoi(DecayVoiConfig(latency_weight=_BINDING_LATENCY_WEIGHT))},
        question_factory=question_factory, out_dir=out_dir, result_path=tmp,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
    )
    tmp.unlink()

    m3 = json.loads(_M3_RESULT_PATH.read_text())
    baseline_rows = [r for r in m3["rows"] if r["question_type"] == "location" and r["policy"] == "answer_immediately"]
    default_decay_voi_rows = [r for r in m3["rows"] if r["question_type"] == "location" and r["policy"] == "decay_voi"]

    binding_records = decompose(baseline_rows + binding_rows)
    default_records = decompose(baseline_rows + default_decay_voi_rows)

    binding_counts = _discovery_counts(binding_records)
    default_counts = _discovery_counts(default_records)

    def _discovery_ratio(counts: dict[str, int]) -> tuple[int, int]:
        return counts.get("wrong_to_right", 0), counts.get("wrong_to_abstain", 0)

    binding_discovery, binding_abstention = _discovery_ratio(binding_counts)
    default_discovery, default_abstention = _discovery_ratio(default_counts)

    print(f"decay_voi at DEFAULT latency_weight (matches always_resense in every trial):")
    print(f"  wrong->right (discovery)={default_discovery}  wrong->abstain (selective abstention)={default_abstention}")
    print(f"  full transition counts: {default_counts}")
    print()
    print(f"decay_voi at BINDING latency_weight={_BINDING_LATENCY_WEIGHT} (genuinely mixed resense behavior):")
    print(f"  wrong->right (discovery)={binding_discovery}  wrong->abstain (selective abstention)={binding_abstention}")
    print(f"  full transition counts: {binding_counts}")
    print()

    if binding_discovery < default_discovery:
        print(f"FINDING: discovery count DROPS from {default_discovery} to {binding_discovery} when decay_voi actually "
              f"exercises judgment (declines some resenses) instead of shadowing always_resense. The M2 claim "
              f"is better read as 'search discovers' (a property of resensing itself) than 'VoI decides well' "
              f"(a property of decay_voi's own cost-benefit judgment) — reported straight, not softened.")
    elif binding_discovery == default_discovery:
        print("FINDING: discovery count is UNCHANGED at the binding lambda — the declined resenses did not cost "
              "any discoveries on this scene's trials (the trials that stopped resensing were not the ones "
              "driving the discovery count). Reported straight.")
    else:
        print("FINDING: discovery count INCREASED at the binding lambda — declining some resenses did not just "
              "avoid useless travel, it improved outcomes on this data. Reported straight.")

    _DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _DIAGNOSTICS_DIR / "voi_m2_reattribution_result.json"
    out_path.write_text(json.dumps({
        "binding_latency_weight": _BINDING_LATENCY_WEIGHT,
        "default": {"discovery": default_discovery, "abstention": default_abstention, "counts": default_counts},
        "binding": {"discovery": binding_discovery, "abstention": binding_abstention, "counts": binding_counts},
    }, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
