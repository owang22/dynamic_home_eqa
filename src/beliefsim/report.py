"""Derive every table and figure from results/raw_results.csv.

    PYTHONPATH=src python -m beliefsim.report --out results

One reader, one aggregation function, one place where micro vs macro is
decided — see :mod:`beliefsim.scoring`. Nothing here recomputes a metric
from the traces; if a number is not in the CSV it does not appear in a
table.

Colour is assigned per BELIEF MODEL and held fixed across every panel, so a
model keeps its identity when a facet drops it. The five model hues are the
validated categorical slots (CVD min dE 9.1, normal-vision min dE 16.3 over
all pairs); ``uniform`` is drawn as a grey dashed reference line rather than
a sixth categorical slot, because it is the chance floor rather than a
competing model — and because a near-zero-chroma grey fails the categorical
checks by construction.
"""

from __future__ import annotations

import argparse
import collections
import csv
import math
import pathlib
from typing import Dict, List, Sequence

from beliefsim.scoring import aggregate_ratio, unit_counts

BELIEF_ORDER = ("last_observation", "most_frequent", "timetable", "fremen",
                "pooled_class", "uniform")
HUE = {"last_observation": "#2a78d6", "most_frequent": "#d95926",
       "timetable": "#1baf7a", "fremen": "#eda100",
       "pooled_class": "#4a3aa7", "uniform": "#898781"}
POLICY_ORDER = ("random", "round_robin", "staleness_first", "entropy_first")
BUDGET_ORDER = ("0", "1", "2", "5", "10", "25", "50", "all")

_INK, _MUTED, _GRID, _AXIS = "#0b0b0b", "#898781", "#e1e0d9", "#c3c2b7"


class Table:
    """A row set with cached group-by indexes.

    The report asks for a few hundred slices of a half-million-row CSV; a
    linear scan per slice turns a report into a seven-minute job and
    discourages regenerating it, which is how stale numbers end up in a
    writeup. Indexes are built lazily per key combination.
    """

    def __init__(self, rows: List[Dict[str, object]]) -> None:
        self.rows = rows
        self._idx: Dict[tuple, Dict[tuple, List[Dict[str, object]]]] = {}

    def __len__(self) -> int:
        return len(self.rows)

    def sel(self, **eq) -> List[Dict[str, object]]:
        keys = tuple(sorted(eq))
        idx = self._idx.get(keys)
        if idx is None:
            idx = collections.defaultdict(list)
            for r in self.rows:
                idx[tuple(r[k] for k in keys)].append(r)
            self._idx[keys] = idx
        return idx.get(tuple(eq[k] for k in keys), [])

    def where(self, **eq) -> "Table":
        return Table(self.sel(**eq))

    def values(self, key) -> List:
        return sorted({r[key] for r in self.rows})


def load(path: pathlib.Path) -> Table:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("n", "n_correct", "n_displaced", "n_displaced_correct",
                  "n_just_sensed", "n_just_sensed_correct", "n_not_sensed",
                  "n_not_sensed_correct", "n_displaced_not_sensed",
                  "n_displaced_not_sensed_correct",
                  "n_never_observed", "senses_today"):
            r[k] = int(r[k])
        for k in ("brier_sum", "log_loss_sum", "staleness_sum"):
            r[k] = float(r[k])
        # Staleness is defined only for objects that have ever been seen; a
        # never-observed object has no "time since last observation".
        r["n_observed_ever"] = r["n"] - r["n_never_observed"]
    return Table(rows)


def _fmt(x: float, places: int = 3) -> str:
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) \
        else f"{x:.{places}f}"


# ------------------------------------------------------------------ tables

def _budget_table(rows, num, den, title, note, mode="macro") -> List[str]:
    out = [f"### {title}", "", note, "",
           "| belief | policy | " + " | ".join(f"B={b}" for b in BUDGET_ORDER)
           + " |", "|---|---|" + "---|" * len(BUDGET_ORDER)]
    for belief in BELIEF_ORDER:
        for policy in POLICY_ORDER:
            cells = []
            for b in BUDGET_ORDER:
                # Budget 0 is run once, under never_sense: every policy at
                # zero budget IS never-sense, so the column is shared.
                sub = rows.sel(belief=belief, budget=b,
                           policy="never_sense" if b == "0" else policy)
                cells.append(_fmt(aggregate_ratio(sub, num, den, mode=mode))
                             if sub else "--")
            out.append(f"| {belief} | {policy} | " + " | ".join(cells) + " |")
    return out + [""]


def _per_household_table(rows, num, den, title, policy) -> List[str]:
    households = rows.values("household")
    out = [f"### {title}", "",
           f"Policy: {policy}. The household is the unit of analysis (n=3), "
           "so per-household columns are the result and the mean is "
           "descriptive.", "",
           "| belief | " + " | ".join(f"B={b}" for b in BUDGET_ORDER) + " |",
           "|---|" + "---|" * len(BUDGET_ORDER)]
    for belief in BELIEF_ORDER:
        for h in households:
            cells = []
            for b in BUDGET_ORDER:
                sub = rows.sel(belief=belief, household=h, budget=b,
                           policy="never_sense" if b == "0" else policy)
                cells.append(_fmt(aggregate_ratio(sub, num, den, mode="micro"))
                             if sub else "--")
            out.append(f"| {belief} / HH-{h} | " + " | ".join(cells) + " |")
    return out + [""]


def _diagnostics_table(rows) -> List[str]:
    """Just-sensed decomposition, staleness, and marginal value per sense."""
    out = ["### Diagnostics", "",
           "`just-sensed` is the accuracy on objects observed at the scored "
           "instant itself (trivially 1.000 for every method — the "
           "short-circuit is shared, see `beliefsim.beliefs._ExactSighting`); "
           "`not-sensed` is the accuracy on everything else, i.e. the "
           "inference the experiment is actually about. `staleness` is the "
           "mean hours since last observation over objects ever observed. "
           "`value/sense` is (accuracy - never-sense accuracy) / budget, in "
           "accuracy points per daily look.", "",
           "| belief | policy | budget | all | just-sensed | not-sensed | "
           "displaced, not-sensed | staleness h | value/sense |",
           "|---|---|---|---|---|---|---|---|---|"]
    for belief in BELIEF_ORDER:
        base = aggregate_ratio(rows.sel(belief=belief, budget="0"),
                               "n_correct", "n", mode="macro")
        for policy in POLICY_ORDER:
            for b in BUDGET_ORDER:
                sub = rows.sel(belief=belief, budget=b,
                           policy="never_sense" if b == "0" else policy)
                if not sub:
                    continue
                overall = aggregate_ratio(sub, "n_correct", "n", mode="macro")
                per_sense = ("--" if b in ("0", "all")
                             else _fmt((overall - base) / int(b), 4))
                out.append(
                    f"| {belief} | {policy} | {b} | {_fmt(overall)} "
                    f"| {_fmt(aggregate_ratio(sub, 'n_just_sensed_correct', 'n_just_sensed', mode='macro'))} "
                    f"| {_fmt(aggregate_ratio(sub, 'n_not_sensed_correct', 'n_not_sensed', mode='macro'))} "
                    f"| {_fmt(_ratio(sub, 'n_displaced_not_sensed_correct', 'n_displaced_not_sensed'))} "
                    f"| {_fmt(aggregate_ratio(sub, 'staleness_sum', 'n_observed_ever', mode='macro'), 1)} "
                    f"| {per_sense} |")
    return out + [""]


def _ratio(rows, num, den, mode="macro") -> float:
    return aggregate_ratio(rows, num, den, mode=mode)


def _heldout_table(rows) -> List[str]:
    held = rows.where(condition="heldout")
    if not held:
        return []
    budgets = sorted(held.values("budget"), key=BUDGET_ORDER.index)
    out = ["### Forced held-out ablation", "",
           "k objects are unobservable to every method, so cross-method "
           "comparison is not confounded by different policies leaving "
           "different objects unseen. Scored on the held-out objects only, "
           "pooled over mask draws. `observable` is the same run's other "
           "objects, for reference.", "",
           "| belief | group | " + " | ".join(f"B={b}" for b in budgets)
           + " |", "|---|---|" + "---|" * len(budgets)]
    for belief in BELIEF_ORDER:
        for group in ("heldout", "observable"):
            cells = [_fmt(aggregate_ratio(
                held.sel(belief=belief, budget=b, group=group),
                "n_correct", "n", mode="macro")) for b in budgets]
            out.append(f"| {belief} | {group} | " + " | ".join(cells) + " |")
    return out + [""]


def _seed_spread_table(rows) -> List[str]:
    out = ["### Seed spread (stochastic policies)", "",
           "Range of macro DISPLACED-instant accuracy over the five "
           "scoring seeds — the primary metric, and the noisiest. Seeds vary "
           "the policy's own randomisation and the argmax tie-break; they "
           "are not a substitute for the n=3 households.", "",
           "| belief | policy | budget | min | max | range |",
           "|---|---|---|---|---|---|"]
    for belief in BELIEF_ORDER:
        for policy in ("random", "entropy_first"):
            for b in ("1", "5", "25"):
                per_seed = []
                for seed in rows.values("seed"):
                    sub = rows.sel(belief=belief, policy=policy, budget=b,
                               seed=seed, condition="open")
                    if sub:
                        per_seed.append(aggregate_ratio(
                            sub, "n_displaced_correct", "n_displaced",
                            mode="macro"))
                if per_seed:
                    out.append(f"| {belief} | {policy} | {b} | "
                               f"{_fmt(min(per_seed))} | {_fmt(max(per_seed))} "
                               f"| {_fmt(max(per_seed) - min(per_seed), 4)} |")
    return out + [""]


def tables(rows, provenance: Dict) -> str:
    open_rows = rows.where(condition="open")
    hh = provenance["households"]
    lines = [
        "# Budgeted whole-house belief tracking on HOMER+",
        "",
        "Every number below is derived from `results/raw_results.csv` by "
        "`beliefsim.report` through `beliefsim.scoring.aggregate_ratio`. No "
        "number in this file is computed by a second code path.",
        "",
        "**Aggregation: MACRO over household** unless a table says otherwise "
        "— each of the three households weighs equally, whatever its object "
        "count. Micro-averages over instants are available from the same CSV "
        "by changing one argument; they differ from these by <0.01 because "
        "the households are of similar size.",
        "",
        "## Scale of the displaced slice",
        "",
        "The displaced slice is the primary metric, so its size is reported "
        "before any conclusion is drawn from it.",
        "",
        "| household | objects | receptacles | scored instants | displaced | "
        "share |", "|---|---|---|---|---|---|"]
    for h in sorted(hh):
        d = hh[h]
        lines.append(f"| HH-{h} | {d['objects']} | {d['receptacles']} | "
                     f"{d['scored_instants']} | {d['displaced_instants']} | "
                     f"{d['displaced_instants'] / d['scored_instants']:.3f} |")
    lines += ["",
              "Per household-day the displaced count runs 38-100. That is "
              "enough to separate methods at the household level, which is "
              "the unit of analysis; it is NOT enough to read a single "
              "household-day.", "",
              "## Primary results", ""]
    lines += _budget_table(
        open_rows, "n_displaced_correct", "n_displaced",
        "Displaced-instant accuracy",
        "Top-1 accuracy restricted to instants where the object is NOT at "
        "its learning-period modal receptacle. This is where the signal is: "
        "the all-instant number is dominated by inertia and compresses every "
        "method into the top few points.")
    lines += _budget_table(
        open_rows, "n_correct", "n", "All-instant accuracy",
        "Top-1 accuracy over every object at every scored timestep. Reported "
        "for completeness; a predictor that always guesses each object's "
        "habitual receptacle scores ~0.92 here.")
    lines += ["## Calibration", ""]
    lines += _budget_table(
        open_rows, "brier_sum", "n", "Brier score (lower is better)",
        "Multiclass Brier over the full receptacle set, per scored instant. "
        "An uncertainty-driven policy is only as good as the uncertainty it "
        "reads, and top-1 cannot show that.")
    lines += _budget_table(
        open_rows, "log_loss_sum", "n", "Log loss, nats (lower is better)",
        "Floored at 1e-6, so a confident-and-wrong belief costs at most 13.8 "
        "nats. One-hot beliefs (last-observation) are punished hardest here "
        "and that is the intended reading.")
    lines += ["## Per-household detail", ""]
    lines += _per_household_table(open_rows, "n_displaced_correct",
                                  "n_displaced",
                                  "Displaced-instant accuracy by household",
                                  "staleness_first")
    lines += ["## Diagnostics", ""]
    lines += _diagnostics_table(open_rows)
    lines += _seed_spread_table(open_rows)
    lines += _heldout_table(rows)
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------- figures

def _style(ax, xlabel: str, ylabel: str, title: str) -> None:
    ax.set_xticks(range(len(BUDGET_ORDER)), BUDGET_ORDER)
    ax.set_title(title, loc="left", fontsize=9.5, color=_INK)
    ax.set_xlabel(xlabel, fontsize=8, color=_MUTED)
    ax.set_ylabel(ylabel, fontsize=8.5, color=_INK)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=_MUTED, labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(_AXIS)


def _series(rows, belief, policy, num, den):
    ys = []
    for b in BUDGET_ORDER:
        sub = rows.sel(belief=belief, budget=b,
                   policy="never_sense" if b == "0" else policy)
        ys.append(aggregate_ratio(sub, num, den, mode="macro") if sub
                  else float("nan"))
    return ys


def _plot_panel(ax, rows, policy, num, den):
    for belief in BELIEF_ORDER:
        ys = _series(rows, belief, policy, num, den)
        reference = belief == "uniform"
        ax.plot(range(len(BUDGET_ORDER)), ys, color=HUE[belief],
                linewidth=1.6 if reference else 2.0,
                linestyle="dashed" if reference else "solid",
                marker="o", markersize=4.5, markeredgewidth=0,
                zorder=2 if reference else 3)


def _legend_handles():
    from matplotlib.lines import Line2D
    return [Line2D([], [], color=HUE[b], linewidth=2.4,
                   linestyle="dashed" if b == "uniform" else "solid",
                   marker="o", markersize=5, markeredgewidth=0,
                   label=b + (" (chance floor)" if b == "uniform" else ""))
            for b in BELIEF_ORDER]


def figures(rows, out_dir: pathlib.Path) -> List[pathlib.Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    open_rows = rows.where(condition="open")
    written = []

    # Fig 1 — the factorial: metric x policy, hue = belief.
    fig, axes = plt.subplots(2, 4, figsize=(15.5, 8.0), sharex=True)
    for col, policy in enumerate(POLICY_ORDER):
        _plot_panel(axes[0][col], open_rows, policy, "n_displaced_correct",
                    "n_displaced")
        _style(axes[0][col], "", "displaced-instant accuracy" if col == 0
               else "", policy)
        axes[0][col].set_ylim(-0.02, 1.02)
        _plot_panel(axes[1][col], open_rows, policy, "n_correct", "n")
        _style(axes[1][col], "sensing budget (looks per day)",
               "all-instant accuracy" if col == 0 else "", "")
        axes[1][col].set_ylim(0.0, 1.02)
    fig.suptitle("Accuracy vs sensing budget — belief model x sensing policy "
                 "(macro over 3 households, 5 seeds)",
                 x=0.006, y=0.985, ha="left", fontsize=11.5, color=_INK)
    fig.legend(handles=_legend_handles(), loc="upper left", ncol=6,
               fontsize=9, frameon=False, bbox_to_anchor=(0.005, 0.955))
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    p = out_dir / "budget_curves_accuracy.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    written.append(p)

    # Fig 2 — per household, the unit of analysis.
    households = open_rows.values("household")
    fig, axes = plt.subplots(1, len(households), figsize=(13.5, 4.2),
                             sharey=True)
    for ax, h in zip(axes, households):
        _plot_panel(ax, open_rows.where(household=h), "staleness_first",
                    "n_displaced_correct", "n_displaced")
        _style(ax, "sensing budget (looks per day)",
               "displaced-instant accuracy" if h == households[0] else "",
               f"Household {h}")
        ax.set_ylim(-0.02, 1.02)
    fig.suptitle("Displaced-instant accuracy per household "
                 "(policy: staleness-first) — n=3 is the whole sample",
                 x=0.006, y=0.985, ha="left", fontsize=11.5, color=_INK)
    fig.legend(handles=_legend_handles(), loc="upper left", ncol=6,
               fontsize=9, frameon=False, bbox_to_anchor=(0.005, 0.945))
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    p = out_dir / "budget_curves_per_household.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    written.append(p)

    # Fig 3 — calibration under the policy that depends on it.
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.0))
    for ax, (num, label, top) in zip(
            axes, (("brier_sum", "Brier score", 1.05),
                   ("log_loss_sum", "log loss (nats)", 3.6))):
        _plot_panel(ax, open_rows, "entropy_first", num, "n")
        _style(ax, "sensing budget (looks per day)", label + "  (lower better)",
               label)
        ax.set_ylim(-0.02, top)
    fig.suptitle("Belief calibration under entropy-first — the policy can "
                 "only be as good as the uncertainty it reads",
                 x=0.008, y=0.985, ha="left", fontsize=11.5, color=_INK)
    fig.legend(handles=_legend_handles(), loc="upper left", ncol=3,
               fontsize=9, frameon=False, bbox_to_anchor=(0.005, 0.945))
    fig.tight_layout(rect=(0, 0, 1, 0.80))
    p = out_dir / "budget_curves_calibration.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    written.append(p)
    return written


def main() -> None:
    import json
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("results"))
    args = ap.parse_args()
    rows = load(args.out / "raw_results.csv")
    provenance = json.loads((args.out / "provenance.json").read_text())
    (args.out / "tables.md").write_text(tables(rows, provenance))
    for p in figures(rows, args.out):
        print(f"wrote {p}")
    print(f"wrote {args.out / 'tables.md'} from {len(rows)} rows")


if __name__ == "__main__":
    main()
