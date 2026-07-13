#!/usr/bin/env python3
"""
budget_matched_random_calibration.py — calibrates RandomResenseConfig.
p_resense so budget_matched_random's realized mean travel distance matches
decay_voi's ~2.2m on the frozen scene (results/reports/e2_preliminary.md:
2.26m stable-location, 2.18m volatile-location; target = 2.22m, their
mean).

Scene-limited by design, same precedent as voi_boundary_validation.py's
own latency_weight calibration: the frozen scene only, not the full pool
— a real, measured calibration rather than an invented constant, with the
same "too thin to widen without rerunning" caveat voi_boundary.md already
carries for its own single-scene value.

Sweeps a small p grid, runs the location axis only (the axis
budget_matched_random exists to compare against decay_voi's headline
number), picks the p whose realized mean distance_traveled_m is closest
to the 2.22m target, and reports the full grid so the choice is
inspectable, not just asserted.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train, rerun_frozen_e0
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import RandomResense, RandomResenseConfig
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore
from dynamic_home_eqa.embodied.question import categories_ever_outdoor, category_anchor_history, generate_mcq_question

_TARGET_METERS = 2.22
# First pass (0.1, 0.25, 0.4, 0.6, 0.85) bracketed the target between 0.1
# (1.758m) and 0.25 (4.688m) — refining within that bracket rather than
# guessing, since the curve is steep and non-linear there (multi-leg
# search compounding, not a simple frequency scaling).
_P_GRID = (0.1, 0.12, 0.14, 0.16, 0.18, 0.2)
_RESULTS_DIR = _DYNAMIC_EQA / "embodied_results"
_DIAGNOSTICS_DIR = _RESULTS_DIR / "diagnostics"


def main() -> None:
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

    print(f"Calibrating budget_matched_random's p_resense against target={_TARGET_METERS}m "
          f"(frozen scene, location axis only)")
    grid_results: list[tuple[float, float, int]] = []
    for p in _P_GRID:
        tmp = _RESULTS_DIR / "_budget_matched_random_calibration_tmp.json"
        rows = rerun_frozen_e0(
            milestone="budget_matched_random_calibration",
            policies={"budget_matched_random": RandomResense(RandomResenseConfig(p_resense=p, seed=0))},
            question_factory=question_factory, out_dir=out_dir, result_path=tmp,
            belief_factory=lambda _decay_models: PosteriorBeliefStore(location_kernels),
        )
        tmp.unlink()
        mean_m = sum(r["distance_traveled_m"] for r in rows) / len(rows)
        grid_results.append((p, mean_m, len(rows)))
        print(f"  p_resense={p:.2f}: mean_distance={mean_m:.3f}m (n={len(rows)})")

    best_p, best_m, best_n = min(grid_results, key=lambda triple: abs(triple[1] - _TARGET_METERS))
    print(f"\nClosest to target {_TARGET_METERS}m: p_resense={best_p:.2f} (mean_distance={best_m:.3f}m, n={best_n})")

    _DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _DIAGNOSTICS_DIR / "budget_matched_random_calibration_result.json"
    out_path.write_text(json.dumps({
        "target_meters": _TARGET_METERS,
        "grid": [{"p_resense": p, "mean_distance_m": m, "n": n} for p, m, n in grid_results],
        "chosen_p_resense": best_p,
        "chosen_mean_distance_m": best_m,
        "scene": FROZEN.scene,
    }, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
