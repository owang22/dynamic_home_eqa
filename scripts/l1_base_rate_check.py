#!/usr/bin/env python3
"""
l1_base_rate_check.py — L1 T0: is the fitted kernel's location-axis win
real spatial prediction, or just base-rate exploitation (most objects
mostly don't move)? One comparison: the fitted kernel's predicted
survival vs. a trivial "stay put forever" predictor (constant 1.0,
regardless of elapsed wait), both scored by Brier against the SAME
held-out dwell events kernel_reliability_diagram.py already uses.

This is deliberately NOT the same number as l0_llm_prior_calibration.md's
location-prior Brier (0.787) — that construction scores a (category,
time_bin)-BUCKET-level destination distribution against the bucket's own
empirical mode, with no per-instance "current position" input at all, so
a "stay put" baseline has no analog there (you cannot stay put relative
to nothing). The dwell/survival framing used here has a well-defined
current position (each dwell event's own start_state) and is the
kernel's own conditional prediction machinery
(embodied.belief._posterior_validity_at_dwell) — reused unchanged, not
reimplemented, exactly like l0_llm_prior_calibration.md reused it for the
state-axis long-horizon cell.

Pure Python — no habitat_sim needed.
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

sys.path.insert(0, str(_DYNAMIC_EQA / "scripts"))
from kernel_reliability_diagram import reliability_points  # noqa: E402


def brier(predicted: float, realized: bool) -> float:
    return (predicted - (1.0 if realized else 0.0)) ** 2


def stay_put_points(held_out_events: list[tuple[str, str, float]], wait_hours: float) -> list[tuple[float, bool]]:
    """Same (predicted, realized) shape as reliability_points, but
    predicted is always 1.0 — "I predict it never moves, at any wait" —
    the textbook base-rate-exploiting strategy for a survival curve."""
    return [(1.0, dwell >= wait_hours) for _key, _start_state, dwell in held_out_events]


def mean_brier(points: list[tuple[float, bool]]) -> float:
    return sum(brier(p, r) for p, r in points) / len(points)


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    reports_dir = _DYNAMIC_EQA / "results" / "reports"

    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)
    eval_manifest = json.loads((out_dir / FROZEN.eval_folder / "manifest.json").read_text())
    location_held_out = dwell_events(eval_manifest["changes"])

    print(f"Location axis, {len(location_held_out)} held-out dwell events, "
          f"wait_hours sweep {FROZEN.wait_hours_sweep}:\n")

    kernel_points_all: list[tuple[float, bool]] = []
    stay_put_points_all: list[tuple[float, bool]] = []
    rows = []
    for wait in FROZEN.wait_hours_sweep:
        k_points = reliability_points(location_kernels, location_held_out, wait)
        s_points = stay_put_points(location_held_out, wait)
        k_brier = mean_brier(k_points)
        s_brier = mean_brier(s_points)
        kernel_points_all.extend(k_points)
        stay_put_points_all.extend(s_points)
        print(f"  wait={wait}h: kernel_brier={k_brier:.4f}  stay_put_brier={s_brier:.4f}  n={len(k_points)}")
        rows.append({"wait_hours": wait, "kernel_brier": k_brier, "stay_put_brier": s_brier, "n": len(k_points)})

    overall_kernel = mean_brier(kernel_points_all)
    overall_stay_put = mean_brier(stay_put_points_all)
    print(f"\nOverall (pooled across all waits): kernel_brier={overall_kernel:.4f}  "
          f"stay_put_brier={overall_stay_put:.4f}  n={len(kernel_points_all)}")

    out_path = reports_dir / "l1_base_rate_check.json"
    out_path.write_text(json.dumps({
        "per_wait": rows,
        "overall_kernel_brier": overall_kernel,
        "overall_stay_put_brier": overall_stay_put,
        "n_total": len(kernel_points_all),
    }, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
