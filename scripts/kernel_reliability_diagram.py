#!/usr/bin/env python3
"""
kernel_reliability_diagram.py — VoI validation batch, item 2: predicted
validity vs. empirically realized survival, per wait bucket, per axis.

conformal_coverage_check.py's diagnosis already computes both quantities
per held-out dwell event at a fixed wait_hours: _posterior_validity_at_
dwell(kernel, start_state, wait) (predicted — "the belief store would
report this much confidence at this wait") and dwell >= wait_hours
(realized — "the object actually survived at least that long"). This
script is the join conformal_coverage_check.py's own diagnosis stopped
short of: bin the predicted-validity axis, and for each bin report the
empirical frequency of survival — the standard reliability-diagram
construction (predicted probability vs. observed frequency, y=x if
well-calibrated), turning the coverage collapse CONFORMAL_COVERAGE_
FINDING.md reports into a measured curve instead of an inferred cause.

Because _posterior_validity_at_dwell(kernel, start_state, wait) depends
only on (kernel, start_state, wait) — not on which individual historical
event contributed it (see belief.calibrate_conformal_theta_by_wait's own
docstring) — the number of numerically DISTINCT predicted values per axis
is small (bounded by the number of distinct (category/key, state) pairs);
what varies across held-out events sharing a predicted value is the
REALIZED outcome, which is exactly what this diagram measures.

Pure Python — no habitat_sim needed (reads only existing generation_out
manifests, same inputs conformal_coverage_check.py already uses).
"""
from __future__ import annotations

import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import (
    fit_location_kernels_from_train,
    fit_state_kernels_from_train,
)
from dynamic_home_eqa.embodied.belief import _posterior_validity_at_dwell, dwell_events
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.posterior import TransitionKernel

_N_BINS = 10


def reliability_points(
    kernels: dict[str, TransitionKernel],
    held_out_events: list[tuple[str, str, float]],
    wait_hours: float,
) -> list[tuple[float, bool]]:
    """(predicted_validity, realized_survived) for every held-out event,
    evaluated at a fixed wait_hours — realized_survived is True iff the
    event's own real dwell was at least that long."""
    points = []
    for key, start_state, dwell in held_out_events:
        kernel = kernels.get(key)
        if kernel is None:
            continue
        predicted = _posterior_validity_at_dwell(kernel, start_state, wait_hours)
        points.append((predicted, dwell >= wait_hours))
    return points


def bin_reliability(points: list[tuple[float, bool]], n_bins: int = _N_BINS) -> list[dict]:
    """Equal-width bins over [0, 1] of predicted validity; per bin, the
    empirical survival frequency and n. Empty bins are omitted (nothing
    measured there, not a zero)."""
    bins: list[list[tuple[float, bool]]] = [[] for _ in range(n_bins)]
    for p, r in points:
        idx = min(n_bins - 1, max(0, int(p * n_bins)))
        bins[idx].append((p, r))
    out = []
    for i, b in enumerate(bins):
        if not b:
            continue
        preds = [p for p, _r in b]
        reals = [r for _p, r in b]
        out.append({
            "bin_lo": i / n_bins, "bin_hi": (i + 1) / n_bins,
            "mean_predicted": sum(preds) / len(preds),
            "observed_frequency": sum(reals) / len(reals),
            "n": len(b),
        })
    return out


def write_plot(axis_bins: dict[str, dict[float, list[dict]]], out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(axis_bins), figsize=(6.5 * len(axis_bins), 5.5), squeeze=False)
    for i, (axis, by_wait) in enumerate(axis_bins.items()):
        ax = axes[0][i]
        ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1, label="perfectly calibrated")
        for wait, bins in sorted(by_wait.items()):
            if not bins:
                continue
            xs = [b["mean_predicted"] for b in bins]
            ys = [b["observed_frequency"] for b in bins]
            sizes = [20 + 4 * b["n"] for b in bins]
            ax.scatter(xs, ys, s=sizes, alpha=0.75, label=f"wait={wait}h")
            ax.plot(xs, ys, alpha=0.3, linewidth=1)
        ax.set_xlabel("predicted validity (kernel)")
        ax.set_ylabel("observed survival frequency")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f"{axis} axis: kernel reliability")
        ax.legend(fontsize=7, loc="best")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    reports_dir = _DYNAMIC_EQA / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    eval_manifest = json.loads((out_dir / FROZEN.eval_folder / "manifest.json").read_text())
    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)
    location_held_out = dwell_events(eval_manifest["changes"])

    state_eval_manifest = json.loads((out_dir / FROZEN.state_eval_folder / "manifest.json").read_text())
    state_kernels = fit_state_kernels_from_train(out_dir, FROZEN)
    state_held_out = dwell_events(state_eval_manifest["changes"])

    axis_bins: dict[str, dict[float, list[dict]]] = {"location": {}, "state": {}}
    csv_rows: list[dict] = []
    for axis, kernels, held_out in (
        ("location", location_kernels, location_held_out),
        ("state", state_kernels, state_held_out),
    ):
        print(f"\n{axis} axis:")
        for wait in FROZEN.wait_hours_sweep:
            points = reliability_points(kernels, held_out, wait)
            bins = bin_reliability(points)
            axis_bins[axis][wait] = bins
            for b in bins:
                print(f"  wait={wait}: predicted~={b['mean_predicted']:.3f} "
                      f"observed={b['observed_frequency']:.3f} n={b['n']}")
                csv_rows.append({"axis": axis, "wait_hours": wait, **b})

    import csv as _csv
    csv_path = reports_dir / "kernel_reliability.csv"
    with open(csv_path, "w", newline="") as f:
        writer = _csv.DictWriter(f, fieldnames=["axis", "wait_hours", "bin_lo", "bin_hi", "mean_predicted", "observed_frequency", "n"])
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(f"\nWrote {csv_path}")

    plot_path = reports_dir / "kernel_reliability.png"
    write_plot(axis_bins, plot_path)
    print(f"Wrote {plot_path}")


if __name__ == "__main__":
    main()
