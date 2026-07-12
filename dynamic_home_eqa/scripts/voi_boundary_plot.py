#!/usr/bin/env python3
"""
voi_boundary_plot.py — plots voi_boundary_result.json's transition table
(fraction of decay_voi trials that resensed, vs. latency_weight, one line
per wait_hours) for results/reports/voi_boundary.md. Separate from
voi_boundary_validation.py so the plot can be regenerated without rerunning
the (expensive, habitat_sim) sweep itself.
"""
from __future__ import annotations

import json
import pathlib
import sys

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA


def main() -> None:
    result = json.loads((_DYNAMIC_EQA / "embodied_results" / "diagnostics" / "voi_boundary_result.json").read_text())
    lws = [float(x) for x in result["latency_weight_sweep"]]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    for wait, row in sorted(result["location_transition_table"].items(), key=lambda kv: float(kv[0])):
        ys = [row[str(lw)] if str(lw) in row else row.get(lw) for lw in lws]
        ax.plot(lws, ys, marker="o", label=f"wait={wait}h")
    ax.set_xscale("log")
    ax.set_xlabel("latency_weight (accuracy-units per second of travel)")
    ax.set_ylabel("fraction of trials resensed")
    ax.set_title("decay_voi transition: location axis")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    out_path = _DYNAMIC_EQA / "results" / "reports" / "voi_boundary_transition.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
