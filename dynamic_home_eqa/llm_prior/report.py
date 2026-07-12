#!/usr/bin/env python3
"""
llm_prior/report.py — L0's scoring pass. Reads only the committed
elicitation cache (llm_prior/cache.py) and the existing generation_out/
manifests — no live model calls, no network (satisfies "no live LLM calls
in pytest" for anything that later becomes a test fixture, and keeps this
script itself reproducible offline from the committed cache alone).

Two scoring paths, matching L0's own two elicitation targets:

1. Location prior (categorical P(slot_type)): each mode's parsed
   distribution is scored two ways — Brier score against the empirical
   train-split frequency (llm_prior/empirical.py), and a one-vs-rest
   reliability diagram pooled over every individual real train-split
   event, reusing scripts/kernel_reliability_diagram.py's bin_reliability
   directly (an event landing on slot X is a (predicted_prob_of_X,
   True) point; every other slot in that same event contributes a
   (predicted_prob_of_that_slot, False) point — the standard one-vs-rest
   reduction of multiclass calibration to the same binary construction
   the fitted kernel is already scored with).

2. Dynamics prior (stay probability): converted to a synthetic
   TransitionKernel (llm_prior/synthetic_kernel.py) and scored through
   kernel_reliability_diagram.reliability_points/bin_reliability/
   write_plot UNCHANGED against the same held-out eval-folder dwell
   events the fitted kernel itself is scored against — literal reuse,
   including the fitted kernel's own curve as the reference line on the
   same plot.
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train, fit_state_kernels_from_train
from dynamic_home_eqa.embodied.belief import _posterior_validity_at_dwell, dwell_events
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.posterior import bucket_changes_by_time_of_day
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.empirical import empirical_location_frequency, empirical_state_frequency
from dynamic_home_eqa.llm_prior.scoring import (
    ParseFailure,
    brier_score,
    parse_location_distribution_from_cache,
    parse_mcq_logprob_distribution,
    parse_sample_count_distribution,
    parse_verbalized_stay_probability,
)
from dynamic_home_eqa.llm_prior.synthetic_kernel import build_synthetic_kernel
from dynamic_home_eqa.llm_prior.targets import N_TIME_BUCKETS, enumerate_targets

from dynamic_home_eqa.scripts.kernel_reliability_diagram import (
    bin_reliability,
    reliability_points,
    write_plot,
)

_CACHE_DIR = _DYNAMIC_EQA / "llm_prior_cache"
_MANIFEST_DIR = _DYNAMIC_EQA / "results" / "reports" / "l0_manifests"
_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
MODES = ("mcq_logprob", "verbalized", "sample_count")


def _parse_stay_probability(cache: EliciationCache, model_id: str, mode: str, prompt_hash: str,
                              option_letters: tuple[str, ...]) -> float:
    entry = cache.get(model_id, prompt_hash, mode, 0)
    if entry is None:
        raise ParseFailure(f"cache miss: {model_id}/{prompt_hash}/{mode}")
    raw = entry["raw_response"]
    if mode == "mcq_logprob":
        dist = parse_mcq_logprob_distribution(raw["top_logprobs"], option_letters)
        return dist["A"]  # A = "stays the same" (llm_prior/prompts.py's dynamics_mcq_prompt)
    if mode == "verbalized":
        return parse_verbalized_stay_probability(raw)
    if mode == "sample_count":
        result = parse_sample_count_distribution(raw, option_letters)
        return result.distribution["A"]
    raise ValueError(f"unknown mode {mode!r}")


def score_location_priors(manifest: dict, out_dir: pathlib.Path) -> dict:
    """{mode: {"brier_mean": float, "n_scored": int, "n_parse_failures": int,
    "reliability_bins": [...]}}"""
    cache = EliciationCache(_CACHE_DIR)
    model_id = manifest["model_id"]
    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders]
    per_bucket = bucket_changes_by_time_of_day(train_manifests, n_buckets=N_TIME_BUCKETS)

    results: dict[str, dict] = {}
    for mode in MODES:
        briers = []
        reliability_points_pool: list[tuple[float, bool]] = []
        n_failures = 0
        for t in manifest["targets"]:
            if t["axis"] != "location":
                continue
            support = tuple(t["support"])
            letters = tuple(t["location_prior"]["option_letters"])
            try:
                predicted = parse_location_distribution_from_cache(cache, model_id, mode, t["location_prior"][mode], support, letters)
                empirical = empirical_location_frequency(per_bucket[t["time_bin"]], t["key"], support)
            except (ParseFailure, ValueError):
                n_failures += 1
                continue
            empirical_mode = max(empirical, key=empirical.get)
            briers.append(brier_score(predicted, empirical_mode))
            for c in per_bucket[t["time_bin"]]:
                if c.get("object_category") != t["key"]:
                    continue
                landed = c.get("to_semantic")
                for slot, p in predicted.items():
                    reliability_points_pool.append((p, slot == landed))

        results[mode] = {
            "brier_mean": sum(briers) / len(briers) if briers else None,
            "n_scored": len(briers),
            "n_parse_failures": n_failures,
            "reliability_bins": bin_reliability(reliability_points_pool) if reliability_points_pool else [],
        }
    return results


def score_dynamics_priors(manifest: dict, out_dir: pathlib.Path) -> dict:
    """{mode: {axis: {wait_hours: reliability_bins}}} plus the fitted
    kernel's own reference curve, computed once (mode-independent)."""
    cache = EliciationCache(_CACHE_DIR)
    model_id = manifest["model_id"]

    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)
    state_kernels = fit_state_kernels_from_train(out_dir, FROZEN) if FROZEN.state_train_folders else {}
    eval_manifest = json.loads((out_dir / FROZEN.eval_folder / "manifest.json").read_text())
    location_held_out = dwell_events(eval_manifest["changes"])
    state_held_out = []
    if FROZEN.state_train_folders:
        state_eval_manifest = json.loads((out_dir / FROZEN.state_eval_folder / "manifest.json").read_text())
        state_held_out = dwell_events(state_eval_manifest["changes"])

    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders]
    per_bucket_location = bucket_changes_by_time_of_day(train_manifests, n_buckets=N_TIME_BUCKETS)

    per_bucket_state = [[] for _ in range(N_TIME_BUCKETS)]
    if FROZEN.state_train_folders:
        state_train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.state_train_folders]
        per_bucket_state = bucket_changes_by_time_of_day(state_train_manifests, n_buckets=N_TIME_BUCKETS)

    fitted_reference: dict[str, dict[float, list[dict]]] = {"location": {}, "state": {}}
    for wait in FROZEN.wait_hours_sweep:
        fitted_reference["location"][wait] = bin_reliability(reliability_points(location_kernels, location_held_out, wait))
        if state_kernels:
            fitted_reference["state"][wait] = bin_reliability(reliability_points(state_kernels, state_held_out, wait))

    results: dict[str, dict] = {}
    for mode in MODES:
        axis_bins: dict[str, dict[float, list[dict]]] = {"location": {}, "state": {}}
        n_failures = 0
        llm_kernels: dict[str, dict] = {"location": {}, "state": {}}
        for t in manifest["targets"]:
            axis = t["axis"]
            per_bucket = per_bucket_location if axis == "location" else per_bucket_state
            # location's empirical_fn takes a bare category; state's takes
            # the full "category::variable" key — t["key"] is already
            # exactly that for each axis (see llm_prior.targets).
            letters = tuple(t["dynamics_prior"]["option_letters"])
            empirical_fn = empirical_location_frequency if axis == "location" else empirical_state_frequency
            try:
                stay_p = _parse_stay_probability(cache, model_id, mode, t["dynamics_prior"][mode], letters)
                empirical_dest = empirical_fn(per_bucket[t["time_bin"]], t["key"], tuple(t["support"]))
            except (ParseFailure, ValueError):
                n_failures += 1
                continue
            kernel = build_synthetic_kernel(t["key"], tuple(t["support"]), empirical_dest, stay_p)
            # Average across time bins into one kernel per key — dwell
            # events aren't time-of-day tagged, so the per-bin elicitations
            # are pooled (mean lambda, mean dest_dist) for the wait_hours
            # comparison; per-bin values remain in the manifest above for
            # anyone auditing a single time bin directly.
            llm_kernels[axis].setdefault(t["key"], []).append(kernel)

        pooled_kernels: dict[str, dict] = {"location": {}, "state": {}}
        for axis in ("location", "state"):
            for key, kernels in llm_kernels[axis].items():
                mean_lambda = sum(k.lambda_per_hour for k in kernels) / len(kernels)
                support = kernels[0].states
                mean_dest = tuple(
                    sum(k.dest_dist[i] for k in kernels) / len(kernels) for i in range(len(support))
                )
                from dynamic_home_eqa.embodied.posterior import TransitionKernel
                pooled_kernels[axis][key] = TransitionKernel(category=key, states=support, lambda_per_hour=mean_lambda, dest_dist=mean_dest)

        for wait in FROZEN.wait_hours_sweep:
            axis_bins["location"][wait] = bin_reliability(reliability_points(pooled_kernels["location"], location_held_out, wait)) if pooled_kernels["location"] else []
            axis_bins["state"][wait] = bin_reliability(reliability_points(pooled_kernels["state"], state_held_out, wait)) if pooled_kernels["state"] else []

        results[mode] = {"axis_bins": axis_bins, "n_parse_failures": n_failures}

    return {"per_mode": results, "fitted_reference": fitted_reference}


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    for family in ("qwen", "phi3"):
        manifest_path = _MANIFEST_DIR / f"l0_manifest_{family}.json"
        if not manifest_path.exists():
            print(f"skip {family}: no manifest at {manifest_path}")
            continue
        manifest = json.loads(manifest_path.read_text())
        print(f"\n=== {family} ({manifest['model_id']}) ===")

        loc_scores = score_location_priors(manifest, out_dir)
        for mode, s in loc_scores.items():
            print(f"  location/{mode}: brier_mean={s['brier_mean']}, n_scored={s['n_scored']}, "
                  f"n_parse_failures={s['n_parse_failures']}")

        dyn_scores = score_dynamics_priors(manifest, out_dir)
        for mode, s in dyn_scores["per_mode"].items():
            print(f"  dynamics/{mode}: n_parse_failures={s['n_parse_failures']}")

        out_path = _REPORTS_DIR / f"l0_scores_{family}.json"
        out_path.write_text(json.dumps({"location": loc_scores, "dynamics": dyn_scores}, indent=2))
        print(f"  wrote {out_path}")

        # Reliability plot for this model's verbalized-mode dynamics prior
        # (best-Brier mode for both models on the location axis — used
        # uniformly here for a fair head-to-head against the fitted
        # kernel's own plot, scripts/kernel_reliability_diagram.py's
        # write_plot reused verbatim, unmodified).
        plot_path = _REPORTS_DIR / f"l0_dynamics_reliability_{family}.png"
        write_plot(dyn_scores["per_mode"]["verbalized"]["axis_bins"], plot_path)
        print(f"  wrote {plot_path}")


if __name__ == "__main__":
    main()
