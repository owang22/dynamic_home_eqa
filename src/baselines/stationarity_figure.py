"""Accuracy by OBJECT stationarity: does the stationary tail carry the
aggregate number?

Every existing passive breakdown slices by the age of the last sighting,
by home, by resident group or by regime. None slices by the OBJECT. This
module scores the bake-off slate plus the routine oracle in continuous
mode (belief kept current, :func:`passive_eval.evaluate_continuous`) and
bins every question by how much the queried object actually moves over
the episode, a pure ground-truth property:

* ``moves_per_day`` — true location changes / episode days;
* ``displaced_share`` — 1 - modal share: the fraction of the horizon the
  object spends away from its home base (:mod:`bankstats`).

Output (``--out-dir``): ``accuracy_by_object_mobility.png`` (one curve per
model, oracle dashed; a lower panel shows what share of the questions
each bin holds), ``cells.csv`` (household x model x measure x bin:
n, correct), ``objects.csv`` (per object: both measures), ``summary.md``
and ``provenance.json``. Deterministic in (banks, slate, rng seed).

Usage:
  python -m baselines.stationarity_figure                  # 20 seed-0 fleet banks
  python -m baselines.stationarity_figure --households hh_001 --oracle-seeds 20 \
      --out-dir /tmp/x
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import datetime
import json
import logging
import math
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.bankstats import _object_dwell
from baselines.cli import _derived_rng, git_state
from baselines.household_analysis import (DEFAULT_ORACLE_SEEDS_PER_BANK,
                                          ORACLE_NAME, REPO_ROOT, bank_path,
                                          household_meta, select_specs,
                                          timeline_dir)
from baselines.passive_eval import (PassiveProtocolConfig,
                                    evaluate_continuous)
from baselines.registry import build_registered_belief
from baselines.routine_oracle import ORACLE_SEED_BASE, oracle_predictions

logger = logging.getLogger(__name__)

MEASURES: Dict[str, Tuple[float, ...]] = {
    # upper edges of the bins after the exact-zero bin; last bin open
    "moves_per_day": (0.5, 1.0, 2.0, 3.0, 4.0, 6.0),
    "displaced_share": (0.1, 0.2, 0.3, 0.4, 0.5),
}
MEASURE_LABELS = {
    "moves_per_day": "true moves per day (object)",
    "displaced_share": "share of time away from home receptacle (object)",
}
ZERO_LABEL = "0 (static)"
CELL_COLUMNS = ("household", "model", "measure", "bin", "n", "correct")
OBJECT_COLUMNS = ("household", "object_id", "object_class", "n_questions",
                  "moves_per_day", "displaced_share")


def bin_labels(measure: str) -> List[str]:
    edges = MEASURES[measure]
    labels = [ZERO_LABEL, f"(0,{edges[0]:g}]"]
    labels += [f"({lo:g},{hi:g}]" for lo, hi in zip(edges, edges[1:])]
    labels.append(f">{edges[-1]:g}")
    return labels


def bin_of(measure: str, value: float) -> str:
    if value <= 0.0:
        return ZERO_LABEL
    edges = MEASURES[measure]
    lo = 0.0
    for hi in edges:
        if value <= hi:
            return f"({lo:g},{hi:g}]"
        lo = hi
    return f">{edges[-1]:g}"


def object_mobility(episode: Any) -> Dict[str, Dict[str, float]]:
    out = {}
    for object_id, traj in episode.trajectories.items():
        dwell = _object_dwell(episode, object_id)
        out[object_id] = {
            "moves_per_day": (len(traj) - 1) / episode.n_days,
            "displaced_share": 1.0 - dwell.modal_share,
        }
    return out


def analyze_bank(task: Dict[str, Any]) -> Dict[str, Any]:
    household = task["household"]
    specs: Sequence[Dict[str, Any]] = task["specs"]
    config = PassiveProtocolConfig(seed=task["rng_seed"])
    bank_dir = task.get("bank_dir")
    path = bank_path(household, 0,
                     pathlib.Path(bank_dir) if bank_dir else None)
    episodes = list(JsonlBank(path=path).episodes())
    agg: Dict[Tuple[str, str, str], List[int]] = collections.defaultdict(
        lambda: [0, 0])
    objects: List[Tuple[Any, ...]] = []

    def add(model: str, mobility: Dict[str, float], correct: bool) -> None:
        for measure in MEASURES:
            cell = agg[(model, measure, bin_of(measure, mobility[measure]))]
            cell[0] += 1
            cell[1] += int(correct)

    for episode in episodes:
        mob = object_mobility(episode)
        counts = collections.Counter(q.object_id
                                     for day in episode.questions_by_day
                                     for q in day)
        for object_id, m in sorted(mob.items()):
            objects.append((household, object_id,
                            episode.object_classes.get(object_id, ""),
                            counts.get(object_id, 0),
                            round(m["moves_per_day"], 4),
                            round(m["displaced_share"], 4)))
        for spec in specs:
            rng = _derived_rng(task["rng_seed"], "household_analysis",
                               str(spec["name"]), episode.episode_id,
                               "continuous")
            belief = build_registered_belief(dict(spec), rng)
            for q in evaluate_continuous(episode, belief, config):
                add(belief.name, mob[q.object_id], q.correct)
        if task["oracle_seeds"] > 0:
            result = oracle_predictions(
                timeline_dir(household, 0), episode,
                n_seeds=task["oracle_seeds"], seed_base=ORACLE_SEED_BASE)
            if result is not None:
                modal, _ = result
                questions = [q for day in episode.questions_by_day
                             for q in day]
                for pred, q in zip(modal, questions):
                    truth = episode.true_location(q.object_id, q.t_query)
                    add(ORACLE_NAME, mob[q.object_id], pred == truth)
    rows = [(household, model, measure, b, n, c)
            for (model, measure, b), (n, c) in sorted(agg.items())]
    return {"household": household, "rows": rows, "objects": objects}


def wilson(correct: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = correct / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (centre - half, centre + half)


def short_name(model: str) -> str:
    base = model.split("(")[0]
    return {"LastObservation": "LastObs", "MostFrequentLocation": "MostFreq",
            "TimetableLookup": "Timetable", "PeriodicPersistence": "Periodic",
            "DaytypeMixture": "DaytypeMix", "HierarchyBackoff": "HierBackoff",
            "SmoothedRecency": "SmoothedRec", ORACLE_NAME: "routine oracle",
            }.get(base, base)


HIGHLIGHT = {  # representative models (hues match household_report's
    # palette); everything else is a grey context line
    "LastObs": "#2a78d6", "MostFreq": "#eb6834", "Perpetua": "#00838f",
    "OracleBelief": "#b0308f",
}


def pooled(rows: Sequence[Tuple[Any, ...]]) -> Dict[Tuple[str, str, str], List[int]]:
    out: Dict[Tuple[str, str, str], List[int]] = collections.defaultdict(
        lambda: [0, 0])
    for _, model, measure, b, n, c in rows:
        out[(model, measure, b)][0] += int(n)
        out[(model, measure, b)][1] += int(c)
    return out


def render(rows: Sequence[Tuple[Any, ...]], out_path: pathlib.Path,
           min_n: int = 30) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cells = pooled(rows)
    models = sorted({r[1] for r in rows}, key=short_name)
    fig, axes = plt.subplots(
        2, len(MEASURES), figsize=(7.2 * len(MEASURES), 7.4),
        gridspec_kw={"height_ratios": [4, 1.2]}, sharex="col")
    for col, measure in enumerate(MEASURES):
        labels = bin_labels(measure)
        xs = list(range(len(labels)))
        ax, ax_n = axes[0][col], axes[1][col]
        ref = next(m for m in models if m != ORACLE_NAME)
        n_per_bin = [cells[(ref, measure, b)][0] for b in labels]
        total = sum(n_per_bin) or 1
        for model in models:
            name = short_name(model)
            ys, lo, hi = [], [], []
            for b in labels:
                n, c = cells[(model, measure, b)]
                if n < min_n:
                    ys.append(float("nan")); lo.append(float("nan")); hi.append(float("nan"))
                    continue
                ys.append(c / n)
                l, h = wilson(c, n)
                lo.append(l); hi.append(h)
            if model == ORACLE_NAME:
                ax.plot(xs, ys, ls="--", color="#555555", lw=2.0,
                        label=name, zorder=4)
                ax.fill_between(xs, lo, hi, color="#555555", alpha=0.12,
                                lw=0)
            elif name in HIGHLIGHT:
                colour = HIGHLIGHT[name]
                ax.plot(xs, ys, marker="o", ms=5, lw=2.0, color=colour,
                        label=name, zorder=5)
                ax.fill_between(xs, lo, hi, color=colour, alpha=0.12, lw=0)
            else:
                ax.plot(xs, ys, lw=1.0, color="#b5b5b5", zorder=2,
                        label="other classical" if model == next(
                            m for m in models if short_name(m) not in HIGHLIGHT
                            and m != ORACLE_NAME) else None)
        ax.set_ylim(0, 1)
        ax.set_ylabel("top-1 accuracy (belief kept current)")
        ax.set_title(f"by {MEASURE_LABELS[measure]}", loc="left",
                     fontsize=11)
        ax.grid(axis="y", color="#e6e6e6")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax_n.bar(xs, [n / total for n in n_per_bin], color="#cfcfcf",
                 width=0.6)
        for x, n in zip(xs, n_per_bin):
            ax_n.text(x, n / total + 0.01, f"n={n}", ha="center",
                      va="bottom", fontsize=7.5, color="#555555")
        ax_n.set_ylim(0, max(n / total for n in n_per_bin) * 1.35)
        ax_n.set_ylabel("share of\nquestions")
        ax_n.set_xticks(xs)
        ax_n.set_xticklabels(labels, rotation=25, ha="right")
        ax_n.set_xlabel(MEASURE_LABELS[measure])
        for side in ("top", "right"):
            ax_n.spines[side].set_visible(False)
    handles, labels_ = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", ncol=len(handles),
               frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Accuracy by object stationarity — 20 seed-0 fleet banks, "
                 "all query days pooled; shading = Wilson 95%; "
                 f"bins under {min_n} questions not drawn", fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


MOBILITY_SPLIT = {
    "low (≤1 move/day)": ("0 (static)", "(0,0.5]", "(0.5,1]"),
    "high (>2 moves/day)": ("(2,3]", "(3,4]", "(4,6]", ">6"),
}
"""The dumbbell split of the moves-per-day bins; the (1,2] middle bin is
deliberately left out of both ends so the two dots are far apart in
mobility, not just in accuracy."""
SPLIT_COLORS = {"low (≤1 move/day)": "#7ecdd3", "high (>2 moves/day)": "#00646d"}


def render_overall(rows: Sequence[Tuple[Any, ...]], out_path: pathlib.Path,
                   min_n: int = 30) -> None:
    """The tables' message as one figure: per model, accuracy on
    low-mobility vs high-mobility objects (dumbbell, one teal hue light
    to dark) and the question-weighted overall (black tick), Wilson 95%
    whiskers on every mark. Models sorted by overall accuracy."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cells = pooled(rows)
    labels = bin_labels("moves_per_day")

    def summed(model, bins):
        n = sum(cells[(model, "moves_per_day", b)][0] for b in bins)
        c = sum(cells[(model, "moves_per_day", b)][1] for b in bins)
        return c, n

    models = sorted({r[1] for r in rows},
                    key=lambda m: summed(m, labels)[0] / max(1, summed(m, labels)[1]))
    fig, ax = plt.subplots(figsize=(8.2, 0.42 * len(models) + 1.9))
    ys = list(range(len(models)))
    for y, model in zip(ys, models):
        pts = {}
        for split, bins in MOBILITY_SPLIT.items():
            c, n = summed(model, bins)
            if n < min_n:
                continue
            lo, hi = wilson(c, n)
            pts[split] = c / n
            ax.plot([lo, hi], [y, y], color=SPLIT_COLORS[split],
                    linewidth=1.4, alpha=0.6, solid_capstyle="butt", zorder=2)
        if len(pts) == 2:
            ax.plot(sorted(pts.values()), [y, y], color="#e0dfda",
                    linewidth=2, zorder=1)
        for split, v in pts.items():
            ax.plot(v, y, "o", color=SPLIT_COLORS[split], markersize=8,
                    markeredgecolor="white", markeredgewidth=1.2,
                    label=split if y == ys[0] else None, zorder=3)
        c, n = summed(model, labels)
        lo, hi = wilson(c, n)
        ax.plot([lo, hi], [y, y], color="#0b0b0b", linewidth=1.2,
                alpha=0.5, zorder=3)
        ax.plot(c / n, y, "|", color="#0b0b0b", markersize=13,
                markeredgewidth=2, zorder=4,
                label="all questions (question-weighted)"
                if y == ys[0] else None)
    ax.set_yticks(ys)
    ax.set_yticklabels([short_name(m) for m in models], fontsize=9)
    ax.set_xlabel("top-1 accuracy (belief kept current)")
    ax.set_xlim(0.3, 1.0)
    ax.set_ylim(-1, len(models))
    ax.grid(axis="x", color="#e6e6e6")
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax.set_title("Accuracy by model on low- vs high-mobility objects\n"
                 "(dots = mobility split, tick = all questions; "
                 "bars = Wilson 95%; axis starts at 0.3)",
                 loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def write_summary(rows: Sequence[Tuple[Any, ...]], out_dir: pathlib.Path,
                  prov: Dict[str, Any]) -> None:
    cells = pooled(rows)
    models = sorted({r[1] for r in rows}, key=short_name)
    lines = ["# Accuracy by object stationarity", "",
             f"Generated {prov['timestamp']} at commit "
             f"`{prov['git']['commit'][:12]}`"
             f"{' (dirty tree)' if prov['git'].get('dirty') else ''} by "
             "`python -m baselines.stationarity_figure`. "
             f"{prov['n_households']} seed-0 fleet banks, belief kept current, "
             "all query days pooled, questions pooled across homes. Each "
             "object is binned by a ground-truth property of its own "
             "trajectory; the columns of every table are bins of that "
             "property, so a model's curve shows how it does on objects "
             "that move that much. Bins under 30 questions are blank.", "",
             "![](accuracy_by_object_mobility.png)", "",
             "The same data collapsed to one row per model: accuracy on "
             "low-mobility objects (≤1 true move/day, light dot) vs "
             "high-mobility ones (>2, dark dot), black tick = all "
             "questions, question-weighted. The tables below are the "
             "data view of both figures.", "",
             "![](overall_by_model.png)", ""]
    for measure in MEASURES:
        labels = bin_labels(measure)
        ref = next(m for m in models if m != ORACLE_NAME)
        ns = [cells[(ref, measure, b)][0] for b in labels]
        lines += [f"## By {MEASURE_LABELS[measure]}", "",
                  "| model | " + " | ".join(labels) + " | all (question-weighted) | mean over bins |",
                  "|---|" + "---|" * (len(labels) + 2),
                  "| n | " + " | ".join(str(n) for n in ns) + f" | {sum(ns)} | |"]
        for model in models:
            accs = []
            for b in labels:
                n, c = cells[(model, measure, b)]
                accs.append(c / n if n >= 30 else None)
            tot_n = sum(cells[(model, measure, b)][0] for b in labels)
            tot_c = sum(cells[(model, measure, b)][1] for b in labels)
            drawn = [a for a in accs if a is not None]
            lines.append(
                f"| {short_name(model)} | "
                + " | ".join("" if a is None else f"{a:.3f}" for a in accs)
                + f" | {tot_c / tot_n:.3f} | "
                + f"{sum(drawn) / len(drawn):.3f} |")
        lines.append("")
    lines += ["`cells.csv` has the same counts per household; "
              "`objects.csv` lists both measures per object.", ""]
    (out_dir / "summary.md").write_text("\n".join(lines))


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--oracle-seeds", type=int,
                    default=DEFAULT_ORACLE_SEEDS_PER_BANK)
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=REPO_ROOT / "reports" / "baselines" / "stationarity")
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None)
    ap.add_argument("--no-oracle-belief", action="store_true",
                    help="skip the OracleBelief spec (default: appended "
                    "with the sweep-selected config when selected.json "
                    "exists)")
    args = ap.parse_args()
    specs = select_specs(args.models)
    selected = (REPO_ROOT / "results" / "oracle_program_posterior"
                / "selected.json")
    if not args.no_oracle_belief and selected.exists():
        cfg = json.loads(selected.read_text())
        specs = list(specs) + [{"name": "oracle_program_posterior",
                                "eps": cfg["eps"],
                                "half_life_h": cfg["half_life_h"]}]
    meta = household_meta(args.bank_dir)
    households = list(args.households) if args.households else sorted(meta)
    tasks = [{"household": h, "specs": list(specs),
              "oracle_seeds": args.oracle_seeds, "rng_seed": args.rng_seed,
              "bank_dir": str(args.bank_dir) if args.bank_dir else None}
             for h in households]
    rows: List[Tuple[Any, ...]] = []
    objects: List[Tuple[Any, ...]] = []
    with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:
        for res in pool.map(analyze_bank, tasks):
            logger.info("done %s", res["household"])
            rows += res["rows"]
            objects += res["objects"]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "cells.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(CELL_COLUMNS); w.writerows(rows)
    with (args.out_dir / "objects.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(OBJECT_COLUMNS); w.writerows(objects)
    prov = {"timestamp": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"),
            "git": dict(zip(("commit", "dirty"), git_state(REPO_ROOT))),
            "households": households,
            "n_households": len(households), "specs": list(specs),
            "oracle_seeds": args.oracle_seeds, "rng_seed": args.rng_seed,
            "bank_dir": str(args.bank_dir or "fleet"),
            "measures": {k: list(v) for k, v in MEASURES.items()}}
    (args.out_dir / "provenance.json").write_text(json.dumps(prov, indent=2))
    render(rows, args.out_dir / "accuracy_by_object_mobility.png")
    render_overall(rows, args.out_dir / "overall_by_model.png")
    write_summary(rows, args.out_dir, prov)
    logger.info("wrote %s", args.out_dir)


if __name__ == "__main__":
    main()
