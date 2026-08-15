"""Render the learning-curve figures from results/learning_curves.csv.

SUPERSEDED: produced output archived in
``superseded/homer_pilot_2026_08/``; retained for regeneration.

Figure 1 (E1): accuracy on the fixed test queries vs number of training
days, one panel per household, hue = method (fixed assignment so a method
keeps its colour everywhere), mean over day-order permutations.

Figure 2 (E2): the held-out story — the shared per-object fallback vs the
pooled model, overall (solid) and on the moved-only slice (dashed), mean
over permutations x mask draws. This is the figure that shows WHERE any
learning goes: more observed days cannot teach a fallback anything about
a held-out object, but they do sharpen the pooled structure.

    PYTHONPATH=src python -m homer.plot_curves
"""

from __future__ import annotations

import collections
import csv
import pathlib

_INK, _MUTED, _GRID = "#33322e", "#6f6d64", "#dddbd2"
# Fixed method -> hue (validated categorical palette order).
HUES = {"frequency": "#2a78d6", "pooled": "#eb6834", "fremen": "#1baf7a",
        "markov": "#eda100", "modal": "#e87ba4", "persistence": "#008300",
        "fallback": "#e87ba4"}


def _load(path: pathlib.Path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _mean(rows, key="accuracy"):
    vals = [float(r[key]) for r in rows if r[key] != ""]
    return sum(vals) / len(vals) if vals else None


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    rows = _load(pathlib.Path("results/learning_curves.csv"))
    out = pathlib.Path("results")
    households = sorted({r["household"] for r in rows})
    grid = sorted({int(r["n_days"]) for r in rows})

    # ---------------- Figure 1: E1 ----------------
    e1 = [r for r in rows if r["protocol"] == "E1"]
    methods = [m for m in ("frequency", "pooled", "fremen", "markov",
                           "modal", "persistence")
               if any(r["method"] == m for r in e1)]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
    for ax, h in zip(axes, households):
        for m in methods:
            ys = [_mean([r for r in e1 if r["household"] == h
                         and r["method"] == m and int(r["n_days"]) == n])
                  for n in grid]
            ax.plot(grid, ys, color=HUES[m], linewidth=2, marker="o",
                    markersize=3.5)
        ax.set_xscale("log")
        ax.set_xticks(grid, [str(n) for n in grid])
        ax.set_title(f"Household {h}", loc="left", fontsize=10, color=_INK)
        ax.set_xlabel("training days observed (log)", fontsize=9,
                      color=_MUTED)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=_INK, labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("top-1 accuracy on fixed test queries", fontsize=9,
                       color=_INK)
    axes[0].set_ylim(0.55, 1.0)
    axes[0].legend(handles=[Line2D([], [], color=HUES[m], linewidth=2.5,
                                   label=m) for m in methods],
                   loc="lower right", fontsize=8, frameon=False, ncol=2)
    fig.suptitle("E1 learning curves — accuracy vs days of observation "
                 "(mean over 3 day-orderings)", x=0.005, ha="left",
                 fontsize=11, color=_INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out / "learning_curves_e1.png", dpi=150)
    plt.close(fig)

    # ---------------- Figure 2: E2 ----------------
    e2 = [r for r in rows if r["protocol"] == "E2"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
    for ax, h in zip(axes, households):
        for m in ("fallback", "pooled"):
            for key, style in (("accuracy", "solid"),
                               ("accuracy_moved_only", "dashed")):
                ys = [_mean([r for r in e2 if r["household"] == h
                             and r["method"] == m
                             and int(r["n_days"]) == n], key)
                      for n in grid]
                ax.plot(grid, ys, color=HUES[m], linewidth=2,
                        linestyle=style, marker="o", markersize=3.5)
        ax.set_xscale("log")
        ax.set_xticks(grid, [str(n) for n in grid])
        ax.set_title(f"Household {h}", loc="left", fontsize=10, color=_INK)
        ax.set_xlabel("training days observed (log)", fontsize=9,
                      color=_MUTED)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=_INK, labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("top-1 accuracy, held-out objects", fontsize=9,
                       color=_INK)
    axes[0].set_ylim(-0.02, 1.0)
    handles = [Line2D([], [], color=HUES["fallback"], linewidth=2.5,
                      label="per-object fallback (all per-object methods)"),
               Line2D([], [], color=HUES["pooled"], linewidth=2.5,
                      label="pooled"),
               Line2D([], [], color=_INK, linewidth=1.6, label="overall"),
               Line2D([], [], color=_INK, linewidth=1.6, linestyle="dashed",
                      label="moved-only slice")]
    axes[0].legend(handles=handles, loc="center left", fontsize=8,
                   frameon=False)
    fig.suptitle("E2 learning curves — held-out objects: overall vs the "
                 "moved-only slice (mean over 3 orderings x 5 draws)",
                 x=0.005, ha="left", fontsize=11, color=_INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out / "learning_curves_e2.png", dpi=150)
    plt.close(fig)
    print(f"wrote {out}/learning_curves_e1.png and learning_curves_e2.png")


if __name__ == "__main__":
    main()
