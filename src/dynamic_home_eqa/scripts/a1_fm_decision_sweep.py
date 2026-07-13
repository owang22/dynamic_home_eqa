#!/usr/bin/env python3
"""
a1_fm_decision_sweep.py — Phase A, A1: FMDecisionPolicy vs. decay_voi
(and the rest of the existing policy set) on the frozen scene, oracle
perception, known map. Location axis only — A1's belief-summary
rendering is built against PosteriorBeliefStore's location kernels; a
state-axis FM-decision variant is future work, not blocking A1.

Requires TWO things running/available simultaneously:
  1. A vLLM OpenAI-compatible server already running and reachable at
     --base-url (scripts/serve_llm.py, launched separately from the env
     that has vllm — NOT this script's own env).
  2. habitat_sim — run THIS script from an env that has it (e.g.
     explore-eqa). llm_prior/http_client.py's HTTPLLMClient needs only
     `requests`, no vllm import, so this works from an env with no vllm
     installed at all (see that module's own docstring for why the two
     environments are decoupled this way).

decay_voi at the validated binding latency_weight (0.01 — see
results/reports/voi_boundary.md), not DecayVoiConfig's own untested
default.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train, rerun_frozen_e0
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import AlwaysResense, AnswerImmediately, DecayThreshold, DecayVoi, DecayVoiConfig
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore
from dynamic_home_eqa.embodied.question import categories_ever_outdoor, category_anchor_history, generate_mcq_question
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.client import LLAMA33_CROSS_FAMILY, QWEN_GENERATOR
from dynamic_home_eqa.llm_prior.fm_decision import FMDecisionPolicy
from dynamic_home_eqa.llm_prior.http_client import HTTPLLMClient, from_model_spec

_BINDING_LATENCY_WEIGHT = 0.01  # results/reports/voi_boundary.md
_CACHE_DIR = _DYNAMIC_EQA / "llm_prior_cache"
_DIAGNOSTICS_DIR = _DYNAMIC_EQA / "embodied_results" / "diagnostics"

_SPECS = {"llama": LLAMA33_CROSS_FAMILY, "qwen": QWEN_GENERATOR}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:8123/v1 (scripts/serve_llm.py's own output)")
    ap.add_argument("--model-family", choices=tuple(_SPECS), required=True)
    args = ap.parse_args()

    spec = _SPECS[args.model_family]
    client = HTTPLLMClient(from_model_spec(spec, args.base_url))
    cache = EliciationCache(_CACHE_DIR)

    out_dir = _DYNAMIC_EQA / "generation_out"
    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders]
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

    voi_config = DecayVoiConfig(latency_weight=_BINDING_LATENCY_WEIGHT)
    policies = {
        "answer_immediately": AnswerImmediately(),
        "always_resense":     AlwaysResense(),
        "decay_threshold":    DecayThreshold(),
        "decay_voi":          DecayVoi(voi_config),
        "fm_decision":        FMDecisionPolicy(client, cache),
    }

    _DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = _DIAGNOSTICS_DIR / f"a1_fm_decision_{args.model_family}_result.json"
    print(f"Running A1 sweep: model={spec.model_id} ({args.model_family}) against {list(policies)}")
    rows = rerun_frozen_e0(
        milestone="a1_fm_decision", policies=policies, question_factory=question_factory,
        out_dir=out_dir, result_path=result_path, config=FROZEN,
        belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
    )
    print(f"Wrote {len(rows)} rows to {result_path}")


if __name__ == "__main__":
    main()
