#!/usr/bin/env python3
"""
a2_quick_dynamics_check.py — Phase A, A2: a fast look, not a rigorous
study. Asks the FM to reason in prose about household routine and object
behavior (llm_prior.natural_dynamics's native-modality prompt, not L0's
bucketed-simplex format), extracts a stay-probability from the
concluding line, and scores it against the fitted kernel on the same
dwell/reliability machinery T0 and L0 both used. Location axis, one
model (Llama-3.3-70B-AWQ — A1's clean cross-family pick), no habitat_sim
needed (pure elicitation + scoring, like L0). In-process vLLM client
(this script doesn't run inside a habitat_sim episode, so the HTTP
decoupling A1 needed doesn't apply here — this can just import vllm
directly, same as llm_prior/elicit.py).

Explicitly not a rerun of L0 with a new model: single mode, single
model, no k=20 sampling — a quick check per the task's own scope, drawing
no species-level claim either direction.
"""
from __future__ import annotations

import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train
from dynamic_home_eqa.embodied.belief import dwell_events
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.posterior import bucket_changes_by_time_of_day
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.client import LLAMA33_CROSS_FAMILY, LLMPriorClient
from dynamic_home_eqa.llm_prior.empirical import empirical_location_frequency
from dynamic_home_eqa.llm_prior.natural_dynamics import (
    NaturalParseFailure,
    natural_dynamics_prompt,
    parse_natural_stay_probability,
)
from dynamic_home_eqa.llm_prior.prompts import prompt_hash
from dynamic_home_eqa.llm_prior.synthetic_kernel import build_synthetic_kernel
from dynamic_home_eqa.llm_prior.targets import N_TIME_BUCKETS, enumerate_location_targets, render_persona, render_room_inventory

sys.path.insert(0, str(_DYNAMIC_EQA / "scripts"))
from kernel_reliability_diagram import bin_reliability, reliability_points, write_plot  # noqa: E402

_CACHE_DIR = _DYNAMIC_EQA / "llm_prior_cache"
_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
_SEED = 0


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    targets = enumerate_location_targets(out_dir, FROZEN)
    result = json.loads((out_dir / FROZEN.train_folders[0] / "generation_result.json").read_text())
    persona_text = render_persona(result["persona"])
    known_categories = tuple(sorted({t.key for t in targets}))
    room_text = render_room_inventory(FROZEN.scene, known_categories=known_categories)

    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders]
    per_bucket = bucket_changes_by_time_of_day(train_manifests, n_buckets=N_TIME_BUCKETS)

    client = LLMPriorClient(LLAMA33_CROSS_FAMILY)
    cache = EliciationCache(_CACHE_DIR)

    llm_kernels_by_key: dict[str, list] = {}
    n_failures = 0
    print(f"Eliciting natural-language dynamics reasoning for {len(targets)} location targets...")
    for target in targets:
        system, user = natural_dynamics_prompt(persona_text, room_text, target.key, target.time_bin)
        h = prompt_hash("a2_natural_dynamics", system, user)
        if not cache.has(client.spec.model_id, h, "verbalized", _SEED):
            raw = client.verbalized(system, user, seed=_SEED)
            cache.put(client.spec.model_id, h, "verbalized", _SEED, prompt=user, raw_response=raw)
        entry = cache.get(client.spec.model_id, h, "verbalized", _SEED)
        try:
            stay_p = parse_natural_stay_probability(entry["raw_response"])
            empirical_dest = empirical_location_frequency(per_bucket[target.time_bin], target.key, target.support)
        except (NaturalParseFailure, ValueError) as e:
            n_failures += 1
            print(f"  {target.key}/t{target.time_bin}: PARSE FAILURE ({e})")
            continue
        kernel = build_synthetic_kernel(target.key, target.support, empirical_dest, stay_p)
        llm_kernels_by_key.setdefault(target.key, []).append(kernel)
        print(f"  {target.key}/t{target.time_bin}: stay_probability={stay_p:.2f}")

    print(f"\n{len(targets) - n_failures}/{len(targets)} targets scored, {n_failures} parse failures")

    # Pool per-time-bin kernels into one per category (dwell events aren't
    # time-of-day tagged — same convention L0's report.py already uses).
    from dynamic_home_eqa.embodied.posterior import TransitionKernel
    pooled_kernels = {}
    for key, kernels in llm_kernels_by_key.items():
        mean_lambda = sum(k.lambda_per_hour for k in kernels) / len(kernels)
        support = kernels[0].states
        mean_dest = tuple(sum(k.dest_dist[i] for k in kernels) / len(kernels) for i in range(len(support)))
        pooled_kernels[key] = TransitionKernel(category=key, states=support, lambda_per_hour=mean_lambda, dest_dist=mean_dest)

    fitted_kernels = fit_location_kernels_from_train(out_dir, FROZEN)
    eval_manifest = json.loads((out_dir / FROZEN.eval_folder / "manifest.json").read_text())
    held_out = dwell_events(eval_manifest["changes"])

    print(f"\n{'wait_hours':>10s}  {'fitted_brier':>12s}  {'a2_natural_brier':>17s}")
    rows = []
    fitted_bins_by_wait = {}
    a2_bins_by_wait = {}
    for wait in FROZEN.wait_hours_sweep:
        fitted_points = reliability_points(fitted_kernels, held_out, wait)
        a2_points = reliability_points(pooled_kernels, held_out, wait)
        fitted_brier = sum((p - (1.0 if r else 0.0)) ** 2 for p, r in fitted_points) / len(fitted_points)
        a2_brier = sum((p - (1.0 if r else 0.0)) ** 2 for p, r in a2_points) / len(a2_points) if a2_points else float("nan")
        fitted_bins_by_wait[wait] = bin_reliability(fitted_points)
        a2_bins_by_wait[wait] = bin_reliability(a2_points)
        print(f"{wait:>10.2f}  {fitted_brier:>12.4f}  {a2_brier:>17.4f}")
        rows.append({"wait_hours": wait, "fitted_brier": fitted_brier, "a2_natural_brier": a2_brier})

    write_plot({"fitted": fitted_bins_by_wait, "a2_natural": a2_bins_by_wait}, _REPORTS_DIR / "a2_natural_dynamics_reliability.png")

    out_path = _REPORTS_DIR / "a2_quick_dynamics_check.json"
    out_path.write_text(json.dumps({
        "model_id": client.spec.model_id, "n_targets": len(targets), "n_parse_failures": n_failures,
        "per_wait": rows,
    }, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
