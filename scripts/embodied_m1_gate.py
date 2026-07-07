#!/usr/bin/env python3
"""
embodied_m1_gate.py — M1 gate: rerun the frozen E0 configuration with the
new MCQ/Brier/ECE/abstain scoring (no belief-model or policy-logic changes
beyond what the new Answer type forced) and write the attribution row.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import rerun_frozen_e0, summarize_rows
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import (
    AlwaysResense,
    AnswerImmediately,
    ConfidenceStop,
    DecayThreshold,
    DecayVoi,
    DecayVoiRouting,
)
from dynamic_home_eqa.embodied.question import categories_ever_outdoor, category_anchor_history, generate_mcq_question


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"

    train_manifests = [
        json.loads((out_dir / folder / "manifest.json").read_text())
        for folder in FROZEN.train_folders
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

    policies = {
        "answer_immediately": AnswerImmediately(),
        "always_resense":     AlwaysResense(),
        "confidence_stop":    ConfidenceStop(),
        "decay_threshold":    DecayThreshold(),
        "decay_voi":          DecayVoi(),
        "decay_voi_routing":  DecayVoiRouting(),
    }

    result_path = _DYNAMIC_EQA / "embodied_results" / "m1_result.json"
    rows = rerun_frozen_e0(
        milestone="m1", policies=policies, question_factory=question_factory,
        out_dir=out_dir, result_path=result_path,
    )
    print(f"Wrote {len(rows)} raw rows -> {result_path}")

    for s in summarize_rows(rows):
        print(f"  {s['policy']:20s} wait={s['wait_hours']:4.2f}h n={s['n']:3d}  "
              f"acc={s['accuracy']:.3f}  brier={s['mean_brier']:.3f}  ece={s['ece']:.3f}  "
              f"abstain={s['abstain_rate']:.2f}  latency={s['mean_latency_s']:6.1f}s  "
              f"travel={s['mean_travel_m']:6.2f}m")


if __name__ == "__main__":
    main()
