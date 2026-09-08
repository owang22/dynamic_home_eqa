"""Budget grid: one accuracy-vs-senses frontier per belief across sweeps.

Reads ``sweep_results.csv`` from several sweep directories (one per
per-day budget) and draws, per belief, task accuracy against mean senses
per question with every policy family as a labeled series: NeverSense,
SequentialSearch, conformal global and age-binned (lines through their
alpha points), ResolvableMassSense (tau x alpha points), and ACI with
oracle and sensed feedback. Marker size encodes the budget. Also writes
the merged rows with a ``budget`` column (``frontier.csv``) and, per
belief, the accuracy-maximising policy at each budget (``frontier.md``).

Usage:
  PYTHONPATH=src python -m baselines.conformal.frontier \\
      --sweep results/conformal_sweep_v2/budget24 \\
      --sweep results/conformal_sweep_v2/budget45 \\
      --sweep results/conformal_sweep_v2/budget90 \\
      --out results/conformal_sweep_v2
"""

from __future__ import annotations

import argparse
import csv
import pathlib
from typing import Any, Dict, List, Optional, Sequence

_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"
SERIES = (
    ("NeverSense", "never sense", "#33322e", "*"),
    ("SequentialSearch", "search until found", "#33322e", "^"),
    ("global", "conformal, one threshold", "#2a78d6", "o"),
    ("age_binned", "conformal, per age bin", "#eb6834", "o"),
    ("resolvable", "resolvable-mass gate", "#1baf7a", "s"),
    ("aci_oracle", "ACI, oracle feedback (diagnostic)", "#8a4fd1", "D"),
    ("aci_sensed", "ACI, sensed feedback", "#c4257c", "x"),
)


def load_rows(sweep_dirs: Sequence[pathlib.Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for d in sweep_dirs:
        with open(d / "sweep_results.csv") as fh:
            for r in csv.DictReader(fh):
                row: Dict[str, Any] = dict(r)
                row["budget"] = int(r["budget_per_day"])
                row["sweep"] = d.name
                for key in ("task_accuracy", "belief_accuracy", "mean_budget"):
                    row[key] = float(r[key])
                for key in ("alpha", "tau", "gamma"):
                    row[key] = float(r[key]) if r.get(key) else None
                rows.append(row)
    return rows


def _short(name: str) -> str:
    return name.split("(", 1)[0]


def plot_frontier(rows: Sequence[Dict[str, Any]], path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    beliefs = list(dict.fromkeys(r["belief"] for r in rows))
    budgets = sorted({int(r["budget"]) for r in rows})
    sizes = {b: 22 + 26 * i for i, b in enumerate(budgets)}
    n = len(beliefs)
    fig, axes = plt.subplots(1, n, sharey=True, figsize=(3.3 * n + 0.8, 4.2),
                             squeeze=False)
    for idx, belief in enumerate(beliefs):
        ax = axes[0][idx]
        mine = [r for r in rows if r["belief"] == belief]
        for mode, _, hue, marker in SERIES:
            pts = [r for r in mine if r["mode"] == mode]
            if not pts:
                continue
            if mode in ("global", "age_binned"):
                for budget in budgets:
                    line = sorted((r for r in pts if r["budget"] == budget),
                                  key=lambda r: r["mean_budget"])
                    ax.plot([r["mean_budget"] for r in line],
                            [r["task_accuracy"] for r in line], color=hue,
                            linewidth=1.2, alpha=0.7, zorder=2)
            for r in pts:
                ax.scatter([r["mean_budget"]], [r["task_accuracy"]],
                           marker=marker, s=sizes[int(r["budget"])], color=hue,
                           zorder=3, alpha=0.85, linewidths=0.8)
        ax.set_title(_short(belief), color=_INK, fontsize=10, loc="left")
        ax.set_xlabel("senses per question (cost)", color=_INK, fontsize=9)
        if idx == 0:
            ax.set_ylabel("share of questions answered right", color=_INK,
                          fontsize=9)
        ax.tick_params(colors=_INK, labelsize=8)
        ax.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(_MUTED)
        ax.spines["bottom"].set_color(_MUTED)
    handles = [Line2D([], [], marker=marker, linestyle="", color=hue, label=label)
               for _, label, hue, marker in SERIES]
    handles += [Line2D([], [], marker="o", linestyle="", color=_MUTED,
                       markersize=4 + 2 * i, label=f"{b} senses/day")
                for i, b in enumerate(budgets)]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=8)
    fig.suptitle("Accuracy against senses per question, every policy, "
                 "three daily budgets (test households)", color=_INK,
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.22, 1, 0.94))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def best_per_budget(rows: Sequence[Dict[str, Any]]) -> List[str]:
    """Markdown: per belief and budget, the most accurate policy and the
    most accurate one at or below SequentialSearch's cost."""
    lines = ["| belief | budget/day | best policy | acc | senses/q | "
             "best at or below search cost | acc | senses/q | search acc | search senses/q |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    beliefs = list(dict.fromkeys(r["belief"] for r in rows))
    for belief in beliefs:
        for budget in sorted({int(r["budget"]) for r in rows}):
            cell = [r for r in rows if r["belief"] == belief
                    and int(r["budget"]) == budget]
            if not cell:
                continue
            best = max(cell, key=lambda r: (r["task_accuracy"], -r["mean_budget"]))
            search = next((r for r in cell if r["mode"] == "SequentialSearch"), None)
            cheaper = [r for r in cell if search is not None
                       and r["mean_budget"] <= search["mean_budget"] + 1e-9]
            best_cheap = (max(cheaper, key=lambda r: (r["task_accuracy"],
                                                      -r["mean_budget"]))
                          if cheaper else None)
            lines.append(
                f"| {_short(belief)} | {budget} | {best['policy']} | "
                f"{best['task_accuracy']:.3f} | {best['mean_budget']:.2f} | "
                + (f"{best_cheap['policy']} | {best_cheap['task_accuracy']:.3f} | "
                   f"{best_cheap['mean_budget']:.2f} | " if best_cheap else "| | | ")
                + (f"{search['task_accuracy']:.3f} | {search['mean_budget']:.2f} |"
                   if search else "| |"))
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sweep", action="append", type=pathlib.Path,
                        required=True, help="a sweep output directory")
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    rows = load_rows(args.sweep)
    args.out.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with open(args.out / "frontier.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    plot_frontier(rows, args.out / "frontier.png")
    md = ["# Budget grid: accuracy against senses per question", "",
          "Figure: `frontier.png` (one panel per belief; marker size = "
          "daily budget). Rows below: the most accurate policy per belief "
          "and budget, and the most accurate one that spends no more than "
          "SequentialSearch.", ""] + best_per_budget(rows)
    (args.out / "frontier.md").write_text("\n".join(md) + "\n")
    print("\n".join(best_per_budget(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
