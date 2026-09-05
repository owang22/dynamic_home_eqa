"""Observation-rate sweep: is Perpetua's behaviour a limit of the model or
of the data?

The full-fleet household analysis showed the survival models beating
every older model past one day of sighting age and losing to every older
model at 12-24 h, with over half of their edge beliefs still on the
fallback prior on day 27. This sweep re-exports every household at
several densities of the SAME passive patrol schedule (``visits_per_day``
of the round-robin room patrol; 6 is the fleet's 1x) and re-runs the
analysis, so learning speed and the two headline effects can be read as
a function of observation volume. Episode length is fixed at the
households' authored 28 days (a longer-episode arm needs a program
transform and is deliberately not part of this run).

Rules of reading: compare only within fixed age-of-sighting bins --
changing the rate changes the mix of question ages, so accuracies pooled
across bins are not comparable between grid points. Homes are never
pooled with each other; seeds of one home are. Cells under ``MIN_N``
questions are masked. Model code and hyperparameters are untouched.

Layout:
  banks/baselines/sweep/visits<v>/            exported banks (gitignored)
  reports/baselines/rate_sweep/visits<v>/     one full household report
  reports/baselines/rate_sweep/summary.md     the cross-rate comparison

Usage:
  python -m baselines.rate_sweep                      # export + analyse + report, all rates
  python -m baselines.rate_sweep --stage export
  python -m baselines.rate_sweep --stage analyse --workers 100
  python -m baselines.rate_sweep --stage report
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import gzip
import json
import logging
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from baselines.bank import JsonlBank
from baselines.export_bank import export
from baselines.household_analysis import (FINE_AGE_EDGES_H, MODEL_SLUG,
                                          bank_path, household_meta,
                                          run_analysis, select_specs,
                                          timeline_dir, truth_category)
from baselines.household_report import (AGE_LABEL, AGE_ORDER, MIN_N,
                                        base_name, build, label_of, wilson)
from baselines.passive_eval import PassiveProtocolConfig, question_ages
from baselines import perpetua_cases

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FLEET_CONFIG = REPO_ROOT / "src" / "baselines" / "configs" / "fleet.yaml"
BANK_ROOT = REPO_ROOT / "banks" / "baselines" / "sweep"
REPORT_ROOT = REPO_ROOT / "reports" / "baselines" / "rate_sweep"
RATES: Tuple[Tuple[str, int], ...] = (("0.5x", 3), ("1x", 6), ("2x", 12),
                                      ("4x", 24))
"""Rate label -> visits per day of the round-robin patrol (1x = the
fleet config's 6)."""
SEEDS = (0, 1)
SWEEP_MODELS = ("last_observation", "periodic_persistence", "daytype_mixture",
                "smoothed_recency", "perpetua", "perpetua_star")
"""Spec names (perpetua_star covers both the time-of-day and the flat
switching prior); the rest of the panel is dropped for this sweep."""
COMPARATORS = ("LastObservation", "PeriodicPersistence", "DaytypeMixture",
               "SmoothedRecency")
SURVIVAL = ("Perpetua", "PerpetuaStar", "PerpetuaStarFlat")
BIN_12_24 = "[12h,24h)"
BIN_1_2D = "[24h,48h)"
BINS_2D_PLUS = ("[48h,72h)", "[72h,inf)")
FALLBACK_TARGET = 0.25


def rate_dir(label: str) -> pathlib.Path:
    return BANK_ROOT / f"visits{dict(RATES)[label]}"


def report_dir(label: str) -> pathlib.Path:
    return REPORT_ROOT / f"visits{dict(RATES)[label]}"


# ------------------------------------------------------------- export --

def export_rate(label: str, visits: int, households: Sequence[str],
                seeds: Sequence[int]) -> List[pathlib.Path]:
    """Export every (household, seed) bank at ``visits`` per day with the
    fleet config's other settings unchanged."""
    cfg = yaml.safe_load(FLEET_CONFIG.read_text())["export"]
    out_dir = rate_dir(label)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for hh in households:
        for seed in seeds:
            timeline = timeline_dir(hh, seed)
            if not (timeline / "events.jsonl").exists():
                logger.warning("no timeline for %s seed %d — skipped", hh, seed)
                continue
            spec = timeline.parent / "program.yaml"
            path = bank_path(hh, seed, out_dir)
            export(timeline, spec, path, seed=int(cfg["seed"]),
                   sightings_per_day=int(cfg["sightings_per_day"]),
                   questions_per_day=int(cfg["questions_per_day"]),
                   first_question_day=int(cfg["first_question_day"]),
                   budget_per_day=int(cfg["budget_per_day"]),
                   query_mode=str(cfg["query_mode"]),
                   initial_tour=bool(cfg["initial_tour"]),
                   observation_model=str(cfg["observation_model"]),
                   patrol=str(cfg["patrol"]), visits_per_day=visits)
            written.append(path)
    logger.info("%s: exported %d banks at %d visits/day -> %s", label,
                len(written), visits, out_dir)
    return written


# ------------------------------------------------------------ analyse --

def analyse_rate(label: str, workers: int, oracle_seeds: int,
                 households: Optional[Sequence[str]] = None) -> None:
    specs = select_specs(SWEEP_MODELS)
    run_analysis(households=households, seeds=SEEDS, specs=specs,
                 oracle_seeds=oracle_seeds, rng_seed=0, workers=workers,
                 out_dir=report_dir(label), bank_dir=rate_dir(label),
                 extra_provenance={"sweep_rate": label,
                                   "visits_per_day": dict(RATES)[label]})


# ------------------------------------------------------------ summary --

def _load_cells(in_dir: pathlib.Path) -> List[Dict[str, Any]]:
    with gzip.open(in_dir / "cells.csv.gz", "rt") as fh:
        rows = []
        for r in csv.DictReader(fh):
            rows.append({"household": r["household"], "seed": int(r["seed"]),
                         "model": r["model"], "mode": r["mode"],
                         "age_bin": r["age_bin"], "n": int(r["n"]),
                         "correct": int(r["correct"])})
    return rows


class _Acc:
    """Pooled correct/n by key, continuous mode only."""

    def __init__(self, rows: Sequence[Dict[str, Any]], key: Any) -> None:
        self.n: Dict[Any, int] = collections.defaultdict(int)
        self.c: Dict[Any, int] = collections.defaultdict(int)
        for r in rows:
            if r["mode"] != "continuous":
                continue
            k = key(r)
            self.n[k] += r["n"]
            self.c[k] += r["correct"]

    def acc(self, k: Any) -> Optional[float]:
        return self.c[k] / self.n[k] if self.n.get(k, 0) >= MIN_N else None


def _bin_of(r: Dict[str, Any], pooled_2d: bool) -> str:
    if pooled_2d and r["age_bin"] in BINS_2D_PLUS:
        return "2d+"
    return str(r["age_bin"])


def paired_table(per_rate: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """Item 2: per (home, seed) paired win/loss and median delta, per
    rate: Perpetua vs LastObs at 12-24 h, and each survival model vs each
    comparator at 1-2d and 2d+ (pooled). A pair counts only when both
    models have >= MIN_N questions in the bin for that home-seed (they
    answer the same questions, so the counts coincide)."""
    lines = ["| rate | survival model | comparator | bin | pairs | wins | losses | median delta | mean delta |",
             "|---|---|---|---|---|---|---|---|---|"]
    for label, rows in per_rate.items():
        acc = _Acc(rows, lambda r: (r["household"], r["seed"],
                                    base_name(r["model"]), _bin_of(r, True)))
        homes_seeds = sorted({(r["household"], r["seed"]) for r in rows})
        combos = [("Perpetua", "LastObservation", BIN_12_24)]
        combos += [(s, c, b) for b in (BIN_1_2D, "2d+") for s in SURVIVAL
                   for c in COMPARATORS]
        for surv, comp, b in combos:
            deltas = []
            for hh, seed in homes_seeds:
                a1, a0 = acc.acc((hh, seed, surv, b)), acc.acc((hh, seed, comp, b))
                if a1 is None or a0 is None:
                    continue
                deltas.append(a1 - a0)
            if not deltas:
                cell = ["0", "-", "-", "-", "-"]
            else:
                cell = [str(len(deltas)),
                        str(sum(d > 0 for d in deltas)),
                        str(sum(d < 0 for d in deltas)),
                        f"{statistics.median(deltas):+.3f}",
                        f"{statistics.mean(deltas):+.3f}"]
            lines.append("| " + " | ".join(
                [label, label_of(surv), label_of(comp),
                 AGE_LABEL.get(b, b)] + cell) + " |")
    return lines


def age_by_group_tables(per_rate: Dict[str, List[Dict[str, Any]]],
                        meta: Dict[str, Dict[str, Any]],
                        models: Sequence[str]) -> List[str]:
    """Item 1 across rates: per resident group, accuracy by bin per model
    with the bin's question count, one block per rate. Cells under MIN_N
    are masked."""
    lines: List[str] = []
    groups = [g for g in ("1", "2", "3+")
              if any(m["resident_group"] == g for m in meta.values())]
    for g in groups:
        n_homes = sum(1 for m in meta.values() if m["resident_group"] == g)
        lines += [f"### {g}-resident homes ({n_homes} homes, seeds 0 and 1 pooled)", ""]
        head = ["rate", "age of last sighting", "n"] + [label_of(m) for m in models] + ["oracle"]
        lines += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for label, rows in per_rate.items():
            sel = [r for r in rows if meta.get(r["household"], {}).get("resident_group") == g]
            acc = _Acc(sel, lambda r: (base_name(r["model"]), r["age_bin"]))
            for b in AGE_ORDER[:-1]:
                n = acc.n.get((base_name(models[0]), b), 0)
                if not n:
                    continue
                cells = [label, AGE_LABEL[b], str(n)]
                for m in list(models) + ["routine_oracle"]:
                    v = acc.acc((base_name(m), b))
                    cells.append("-" if v is None else f"{v:.3f}")
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return lines


def fallback_tables(per_rate_dirs: Dict[str, pathlib.Path]) -> Tuple[List[str], Dict[str, Dict[int, float]]]:
    """Item 3: fallback share of edge beliefs by query day, per rate (the
    three survival models share the fallback machinery and agree to two
    decimals, so one line per rate)."""
    curves: Dict[str, Dict[int, float]] = {}
    for label, d in per_rate_dirs.items():
        path = d / "perpetua_fallback.csv.gz"
        if not path.exists():
            continue
        agg: Dict[int, List[int]] = collections.defaultdict(lambda: [0, 0])
        with gzip.open(path, "rt") as fh:
            for r in csv.DictReader(fh):
                if not r["model"].startswith("PerpetuaStar("):
                    continue
                a = agg[int(r["day"])]
                a[0] += int(r["n_edge_beliefs"])
                a[1] += int(r["n_fallback_edge_beliefs"])
        curves[label] = {day: v[1] / v[0] for day, v in sorted(agg.items()) if v[0]}
    days = sorted({d for c in curves.values() for d in c})
    shown = [d for d in days if d % 3 == 0 or d == days[-1]] if days else []
    head = ["rate"] + [f"day {d}" for d in shown] + [f"first day < {FALLBACK_TARGET}"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for label, c in curves.items():
        first = next((d for d in days if c.get(d, 1.0) < FALLBACK_TARGET), None)
        lines.append("| " + " | ".join(
            [label] + [f"{c[d]:.2f}" if d in c else "-" for d in shown]
            + ["never" if first is None else str(first)]) + " |")
    return lines, curves


def segment_table(per_rate_dirs: Dict[str, pathlib.Path]) -> List[str]:
    """Item 4: completed segments per edge at episode end, per rate."""
    head = ["rate", "edges", "median persistence segs", "share < 2 persistence",
            "median emergence segs", "share < 2 emergence", "mean K persistence"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for label, d in per_rate_dirs.items():
        path = d / "perpetua_edges.csv.gz"
        if not path.exists():
            continue
        ps, es, ks = [], [], []
        with gzip.open(path, "rt") as fh:
            for r in csv.DictReader(fh):
                if not r["model"].startswith("PerpetuaStar("):
                    continue
                ps.append(int(r["n_persistence_segments"]))
                es.append(int(r["n_emergence_segments"]))
                ks.append(int(r["pf_components"]))
        if not ps:
            continue
        n = len(ps)
        lines.append("| " + " | ".join([
            label, str(n), str(statistics.median(ps)),
            f"{sum(v < 2 for v in ps) / n:.2f}", str(statistics.median(es)),
            f"{sum(v < 2 for v in es) / n:.2f}", f"{statistics.mean(ks):.2f}"]) + " |")
    return lines


def truth_share_table(labels: Sequence[str], households: Sequence[str]
                      ) -> List[str]:
    """Item 5: share of questions per age bin whose true answer is out of
    house or on a person, per rate, from the banks themselves (both
    seeds). This is the ceiling every in-house model faces in that bin."""
    cfg = PassiveProtocolConfig(recency_bin_edges_h=FINE_AGE_EDGES_H)
    cats = ("ordinary receptacle", "out of house", "on a person")
    head = ["rate", "age of last sighting", "n"] + [f"share {c}" for c in cats]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for label in labels:
        tab: Dict[str, "collections.Counter[str]"] = collections.defaultdict(collections.Counter)
        for hh in households:
            for seed in SEEDS:
                path = bank_path(hh, seed, rate_dir(label))
                if not path.exists():
                    continue
                for ep in JsonlBank(path=path).episodes():
                    ages = question_ages(ep)
                    for day in ep.questions_by_day:
                        for q in day:
                            truth = ep.true_location(q.object_id, q.t_query)
                            tab[cfg.recency_bin(ages[q.question_id])][truth_category(truth)] += 1
        for b in AGE_ORDER:
            c = tab.get(b)
            if not c:
                continue
            n = sum(c.values())
            lines.append("| " + " | ".join(
                [label, AGE_LABEL.get(b, b), str(n)]
                + [f"{c[k] / n:.2f}" for k in cats]) + " |")
    return lines


def fig_learning_curve(curves: Dict[str, Dict[int, float]],
                       out: pathlib.Path) -> None:
    """Fallback share by query day, one line per rate (sequential ramp:
    rate is ordered)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if not curves:
        return
    ramp = ["#b3dde1", "#5db9c1", "#1a8f9a", "#00646d"]
    fig, ax = plt.subplots(figsize=(6.4, 3.6), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    for (label, c), color in zip(curves.items(), ramp):
        days = sorted(c)
        ax.plot(days, [c[d] for d in days], color=color, linewidth=2,
                label=f"{label} ({dict(RATES)[label]} visits/day)")
    ax.axhline(FALLBACK_TARGET, color="#8a8983", linewidth=1, linestyle=(0, (4, 3)))
    ax.text(ax.get_xlim()[1], FALLBACK_TARGET + 0.01, f"target {FALLBACK_TARGET}",
            ha="right", fontsize=7, color="#52514e")
    ax.set_ylim(0, 1)
    ax.set_xlabel("query day (history length)", fontsize=8, color="#52514e")
    ax.set_ylabel("share of edge beliefs on the fallback prior", fontsize=8, color="#52514e")
    ax.grid(True, color="#e8e7e2", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors="#52514e", labelsize=7)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("Learning speed: fallback share by day and observation rate "
                 "(all homes and seeds pooled; a property of the estimator)",
                 fontsize=8.5, color="#0b0b0b", loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)


def fig_paired_by_home(per_rate: Dict[str, List[Dict[str, Any]]],
                       meta: Dict[str, Dict[str, Any]], out: pathlib.Path,
                       surv: str = "PerpetuaStar") -> None:
    """Per home (seeds pooled), the survival model's accuracy minus
    LastObs's at 12-24 h, 1-2d and 2d+, one panel per bin, one marker
    colour per rate (sequential ramp), Wilson-based conservative bars."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ramp = ["#b3dde1", "#5db9c1", "#1a8f9a", "#00646d"]
    homes = sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
    bins = [(BIN_12_24, "12-24h"), (BIN_1_2D, "1-2d"), ("2d+", "2d+")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 0.36 * len(homes) + 2.2),
                             sharey=True, facecolor="#fcfcfb")
    ys = list(range(len(homes)))[::-1]
    for ax, (b, blabel) in zip(axes, bins):
        ax.set_facecolor("#fcfcfb")
        ax.axvline(0, color="#52514e", linewidth=1.2)
        ax.grid(True, axis="x", color="#e8e7e2", linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors="#52514e", labelsize=7, length=0)
        for k, ((label, rows), color) in enumerate(zip(per_rate.items(), ramp)):
            acc = _Acc(rows, lambda r: (r["household"], base_name(r["model"]), _bin_of(r, True)))
            for y, hh in zip(ys, homes):
                v, r0 = acc.acc((hh, surv, b)), acc.acc((hh, "LastObservation", b))
                n = acc.n.get((hh, surv, b), 0)
                if v is None or r0 is None:
                    continue
                se = ((v * (1 - v) + r0 * (1 - r0)) / n) ** 0.5
                yy = y + (1.5 - k) * 0.18
                ax.plot([v - r0 - 1.96 * se, v - r0 + 1.96 * se], [yy, yy],
                        color=color, linewidth=1.2, zorder=2)
                ax.plot(v - r0, yy, marker="o", markersize=6, color=color,
                        markeredgecolor="#fcfcfb", markeredgewidth=1,
                        linestyle="none", zorder=3,
                        label=label if (y == ys[0] and b == BIN_12_24) else None)
        ax.set_title(f"{label_of(surv)} − LastObs, {blabel}", fontsize=9,
                     color="#0b0b0b", loc="left")
        ax.set_xlabel("accuracy difference", fontsize=8, color="#52514e")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([f"{h} · {meta[h]['residents']}r" for h in homes], fontsize=7)
    handles = [plt.Line2D([], [], marker="o", markersize=6, linestyle="none",
                          color=c, markeredgecolor="#fcfcfb") for c in ramp[:len(per_rate)]]
    fig.legend(handles, [f"{l} ({dict(RATES)[l]} visits/day)" for l in per_rate],
               loc="lower center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.005))
    fig.suptitle(f"{label_of(surv)} minus LastObs per home by observation rate "
                 f"(seeds pooled; bars = conservative 95% interval; cells under "
                 f"{MIN_N} questions not drawn)", fontsize=9.5, color="#0b0b0b",
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)


def cases_by_rate(labels: Sequence[str], workers: int) -> List[str]:
    """Section 6: the four-case split (object moved since its last
    sighting x last-seen receptacle excluded by a later visit) per rate,
    for the 1-day-and-older and the 12-24 h blocks, with LastObs /
    MostFreq / PerpetuaStar accuracy per case. Runs the cases module on
    each rate's banks (per-home tables land in each rate directory); the
    totals here are orientation only."""
    lines: List[str] = []
    for slug, title in (("long", "last sighting 1 day old or older"),
                        ("mid", "last sighting 12-24 h old")):
        lines += [f"### {title}", "",
                  "| rate | case | share | n | LastObs | MostFreq | Perpetua | PerpetuaStar |",
                  "|---|---|---|---|---|---|---|---|"]
        for label in labels:
            d = report_dir(label)
            totals_path = d / f"perpetua_cases_totals_{slug}.json"
            if not totals_path.exists():
                perpetua_cases.build(d, workers, list(SEEDS),
                                     sorted(household_meta(rate_dir(label))),
                                     rate_dir(label))
            totals = json.loads(totals_path.read_text())
            grand = sum(c["n"] for c in totals.values())
            for case_label, _, _ in perpetua_cases.CASES:
                c = totals.get(case_label)
                if not c:
                    continue
                n = c["n"]
                cells = [label, case_label, f"{n / grand:.2f}", str(n)]
                for m in ("last_observation", "most_frequent", "Perpetua", "PerpetuaStar"):
                    cells.append("-" if n < MIN_N else f"{c.get(m, 0) / n:.2f}")
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return lines


def in_house_conditional(labels: Sequence[str]) -> List[str]:
    """Accuracy of the survival models restricted to questions whose true
    answer is an ordinary receptacle (the only ones they can get), per
    rate and bin, from the absence side file. This removes the ceiling
    shift of item 5 from the comparison of their own accuracies across
    rates; it says nothing about the comparators."""
    head = ["rate", "age of last sighting", "n in-house", "Perpetua", "PerpetuaStar", "PerpStarFlat"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    bins = (BIN_12_24, BIN_1_2D) + BINS_2D_PLUS
    for label in labels:
        agg: Dict[Tuple[str, str], List[int]] = collections.defaultdict(lambda: [0, 0])
        path = report_dir(label) / "absence_signal.csv.gz"
        if not path.exists():
            continue
        with gzip.open(path, "rt") as fh:
            for r in csv.DictReader(fh):
                if (r["mode"] != "continuous" or r["age_bin"] not in bins
                        or r["truth_category"] != "ordinary receptacle"):
                    continue
                a = agg[(base_name(r["model"]), r["age_bin"])]
                a[0] += 1
                a[1] += int(r["correct"])
        for b in bins:
            n = agg[("PerpetuaStar", b)][0]
            if not n:
                continue
            cells = [label, AGE_LABEL[b], str(n)]
            for m in SURVIVAL:
                a = agg[(m, b)]
                cells.append("-" if a[0] < MIN_N else f"{a[1] / a[0]:.3f}")
            lines.append("| " + " | ".join(cells) + " |")
    return lines


# ------------------------------------------------------------- explain --

CASE_PLAIN = {
    "stayed, not excluded": "still there,\nspot never re-checked",
    "stayed, EXCLUDED": "came back:\nspot was checked, found empty",
    "moved, not excluded": "moved away,\nold spot never re-checked",
    "moved, EXCLUDED": "moved away,\nold spot checked, empty",
}
"""Plain-language names for the four situations a question can be in.
"Excluded" means a patrol visit inspected the receptacle the object was
last seen at, after that sighting, and the object was not there."""
CASE_ORDER = tuple(CASE_PLAIN)
CASE_COLORS = ("#2a78d6", "#00838f", "#eda100", "#e34948")
"""One hue per situation, fixed order, never recycled."""
EXPLAIN_BINS = ("12-24h", "1-2d", "2d+")


def build_case_join(labels: Sequence[str], workers: int) -> List[Dict[str, Any]]:
    """One record per (rate, household, seed, age bin, situation, model)
    with n and correct: the replay's situation and classical answers
    joined to the survival models' correctness by question id."""
    bins = {"[12h,24h)": "12-24h", "[24h,48h)": "1-2d",
            "[48h,72h)": "2d+", "[72h,inf)": "2d+"}
    agg: Dict[Tuple[Any, ...], List[int]] = collections.defaultdict(lambda: [0, 0])
    for label in labels:
        bank_dir, rep_dir = rate_dir(label), report_dir(label)
        homes = sorted(household_meta(bank_dir))
        tasks = [{"household": h, "seed": s, "bank_dir": str(bank_dir)}
                 for h in homes for s in SEEDS]
        rows: List[Dict[str, Any]] = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            for res in pool.map(perpetua_cases.replay_bank, tasks):
                rows.extend(res)
        perp: Dict[str, Dict[Tuple[str, int, str], int]] = {}
        with gzip.open(rep_dir / "absence_signal.csv.gz", "rt") as fh:
            for r in csv.DictReader(fh):
                if r["mode"] != "continuous" or r["age_bin"] not in bins:
                    continue
                perp.setdefault(r["model"].split("(")[0], {})[
                    (r["household"], int(r["seed"]), r["question_id"])] = int(r["correct"])
        for r in rows:
            if r["age_bin"] not in bins:
                continue
            key = (r["household"], r["seed"], r["qid"])
            if any(key not in v for v in perp.values()):
                continue
            base = (label, r["household"], r["seed"], bins[r["age_bin"]],
                    perpetua_cases._case_of(r))
            pairs = [("LastObs", r["answers"]["last_observation"] == r["truth"]),
                     ("MostFreq", r["answers"]["most_frequent"] == r["truth"])]
            pairs += [(m, bool(v[key])) for m, v in perp.items()]
            for model, ok in pairs:
                cell = agg[base + (model,)]
                cell[0] += 1
                cell[1] += int(ok)
        logger.info("case join: %s done (%d questions)", label, len(rows))
    return [{"rate": k[0], "household": k[1], "seed": k[2], "bin": k[3],
             "case": k[4], "model": k[5], "n": v[0], "correct": v[1]}
            for k, v in agg.items()]


def _cell(join: Sequence[Dict[str, Any]], **where: Any) -> Tuple[int, int]:
    n = c = 0
    for r in join:
        if all(r[k] == v for k, v in where.items()):
            n += r["n"]
            c += r["correct"]
    return n, c


def decompose(join: Sequence[Dict[str, Any]], bin_: str, rate: str,
              model: str, ref: str = "LastObs", base_rate: str = "1x",
              homes: Optional[Sequence[str]] = None) -> Dict[str, float]:
    """Split ``delta(rate) - delta(base_rate)`` into the part explained by
    the changed mix of situations and the part explained by changed
    accuracy WITHIN situations (a Oaxaca split):

        mix      = sum_c [share_c(rate) - share_c(base)] * delta_c(base)
        per_case = sum_c share_c(rate) * [delta_c(rate) - delta_c(base)]

    where ``delta_c`` is ``model`` minus ``ref`` accuracy in situation c.
    A situation with fewer than MIN_N questions at ``rate`` has no
    measurable ``delta_c(rate)``; it keeps its base value, so it lands in
    the mix term (its share is a percent or two wherever this happens).
    """
    sel = [r for r in join if r["bin"] == bin_
           and (homes is None or r["household"] in homes)]

    def parts(rt: str) -> Tuple[Dict[str, float], Dict[str, Optional[float]]]:
        total = sum(r["n"] for r in sel if r["rate"] == rt and r["model"] == ref)
        share, delta = {}, {}
        for c in CASE_ORDER:
            n, cm = _cell(sel, rate=rt, case=c, model=model)
            _n, cr = _cell(sel, rate=rt, case=c, model=ref)
            share[c] = n / total if total else 0.0
            delta[c] = (cm - cr) / n if n >= MIN_N else None
        return share, delta

    share_b, delta_b = parts(base_rate)
    share_r, delta_r = parts(rate)
    mix = per_case = 0.0
    measured = 0.0
    for c in CASE_ORDER:
        db = delta_b[c] or 0.0
        dr = delta_r[c]
        mix += (share_r[c] - share_b[c]) * db
        if dr is not None and delta_b[c] is not None:
            per_case += share_r[c] * (dr - db)
            measured += share_r[c]
    observed = 0.0
    base = 0.0
    for c in CASE_ORDER:
        dr = delta_r[c]
        observed += share_r[c] * (dr if dr is not None else (delta_b[c] or 0.0))
        base += share_b[c] * (delta_b[c] or 0.0)
    return {"observed": observed, "base": base, "mix": mix,
            "per_case": per_case, "measured_share": measured}


def _bootstrap_decompose(join: Sequence[Dict[str, Any]], bin_: str, rate: str,
                         model: str, homes: Sequence[str], draws: int = 500,
                         seed: int = 0) -> Dict[str, Tuple[float, float]]:
    """Percentile interval over households resampled with replacement --
    households are the unit that varies, so they are the unit resampled."""
    import random as _random
    rng = _random.Random(seed)
    keys = ("observed", "mix", "per_case")
    got: Dict[str, List[float]] = {k: [] for k in keys}
    for _ in range(draws):
        pick = [homes[rng.randrange(len(homes))] for _ in homes]
        counts = collections.Counter(pick)
        rows = [dict(r, n=r["n"] * counts[r["household"]],
                     correct=r["correct"] * counts[r["household"]])
                for r in join if r["household"] in counts]
        d = decompose(rows, bin_, rate, model)
        for k in keys:
            got[k].append(d[k])
    out = {}
    for k in keys:
        v = sorted(got[k])
        out[k] = (v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1])
    return out


def fig_case_mix_by_home(join: Sequence[Dict[str, Any]], meta: Dict[str, Dict[str, Any]],
                         bin_: str, out: pathlib.Path) -> None:
    """What CHANGES with the observation rate: the mix of situations, one
    panel per home so no home's mix is averaged away."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    homes = sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
    nc = 5
    nr = -(-len(homes) // nc)
    fig, axes = plt.subplots(nr, nc, figsize=(2.6 * nc, 2.1 * nr),
                             squeeze=False, facecolor="#fcfcfb", sharex=True)
    rates = [l for l, _ in RATES]
    for i, hh in enumerate(homes):
        ax = axes[i // nc][i % nc]
        ax.set_facecolor("#fcfcfb")
        bottom = [0.0] * len(rates)
        totals = []
        for rt in rates:
            totals.append(sum(r["n"] for r in join if r["rate"] == rt
                              and r["bin"] == bin_ and r["household"] == hh
                              and r["model"] == "LastObs"))
        for c, color in zip(CASE_ORDER, CASE_COLORS):
            vals = []
            for k, rt in enumerate(rates):
                n, _ = _cell(join, rate=rt, bin=bin_, household=hh, case=c,
                             model="LastObs")
                vals.append(n / totals[k] if totals[k] else 0.0)
            ax.bar(range(len(rates)), vals, bottom=bottom, color=color,
                   width=0.74, label=CASE_PLAIN[c].replace("\n", " "),
                   edgecolor="#fcfcfb", linewidth=0.8)
            bottom = [a + b for a, b in zip(bottom, vals)]
        ax.set_title(f"{hh} · {meta[hh]['residents']}r", fontsize=7.5,
                     color="#0b0b0b", loc="left")
        ax.set_xticks(range(len(rates)))
        ax.set_xticklabels([f"{r}\nn={t}" for r, t in zip(rates, totals)],
                           fontsize=6)
        ax.set_ylim(0, 1)
        ax.tick_params(colors="#52514e", labelsize=6, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#e8e7e2")
    for j in range(len(homes), nr * nc):
        axes[j // nc][j % nc].axis("off")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.004))
    fig.suptitle(f"What changes with the observation rate: which situation the "
                 f"questions are in ({bin_} since the object was last seen). "
                 f"Shares are exact, not estimates.", fontsize=10,
                 color="#0b0b0b", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.045, 1, 0.965))
    fig.savefig(out, dpi=140, facecolor="#fcfcfb")
    plt.close(fig)


def fig_case_accuracy(join: Sequence[Dict[str, Any]], meta: Dict[str, Dict[str, Any]],
                      bin_: str, out: pathlib.Path, model: str = "PerpetuaStar"
                      ) -> None:
    """What barely changes with the rate: accuracy WITHIN each situation.
    Thin line per home, bold pooled line with a Wilson 95% band."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rates = [l for l, _ in RATES]
    xs = list(range(len(rates)))
    homes = sorted(meta)
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.9), sharey=True,
                             facecolor="#fcfcfb")
    for ax, c in zip(axes, CASE_ORDER):
        ax.set_facecolor("#fcfcfb")
        for hh in homes:
            ys: List[Optional[float]] = []
            for rt in rates:
                n, cm = _cell(join, rate=rt, bin=bin_, household=hh, case=c,
                              model=model)
                ys.append(cm / n if n >= MIN_N else None)
            pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
            if len(pts) > 1:
                ax.plot([p[0] for p in pts], [p[1] for p in pts],
                        color="#6d4c41", linewidth=0.7, alpha=0.28, zorder=2)
        pooled: List[Optional[float]] = []
        lo: List[Optional[float]] = []
        hi: List[Optional[float]] = []
        ns: List[int] = []
        for rt in rates:
            n, cm = _cell(join, rate=rt, bin=bin_, case=c, model=model)
            ns.append(n)
            if n >= MIN_N:
                pooled.append(cm / n)
                a, b = wilson(cm, n)
                lo.append(a)
                hi.append(b)
            else:
                pooled.append(None)
                lo.append(None)
                hi.append(None)
        keep = [(x, p, a, b) for x, p, a, b in zip(xs, pooled, lo, hi) if p is not None]
        if keep:
            ax.fill_between([k[0] for k in keep], [k[2] for k in keep],
                            [k[3] for k in keep], color="#6d4c41", alpha=0.18,
                            linewidth=0, zorder=3)
            ax.plot([k[0] for k in keep], [k[1] for k in keep], color="#6d4c41",
                    linewidth=2.4, marker="o", markersize=6,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.4, zorder=4,
                    label=label_of(model))
        ref: List[Optional[float]] = []
        for rt in rates:
            n, cm = _cell(join, rate=rt, bin=bin_, case=c, model="LastObs")
            ref.append(cm / n if n >= MIN_N else None)
        keep2 = [(x, y) for x, y in zip(xs, ref) if y is not None]
        if keep2:
            ax.plot([k[0] for k in keep2], [k[1] for k in keep2], color="#2a78d6",
                    linewidth=2.2, linestyle=(0, (4, 3)), marker="s",
                    markersize=5, markeredgecolor="#fcfcfb", markeredgewidth=1.2,
                    zorder=4, label="LastObs")
        ax.set_title(CASE_PLAIN[c], fontsize=8.5, color="#0b0b0b", loc="left")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{r}\nn={n}" for r, n in zip(rates, ns)], fontsize=7)
        ax.set_ylim(0, 1.02)
        ax.grid(True, color="#e8e7e2", linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#e8e7e2")
        ax.tick_params(colors="#52514e", labelsize=7, length=0)
        ax.set_xlabel("observation rate", fontsize=8, color="#52514e")
    axes[0].set_ylabel("accuracy within the situation", fontsize=8.5, color="#52514e")
    axes[0].legend(frameon=False, fontsize=8, loc="lower left")
    fig.suptitle(
        f"Accuracy inside each situation, {bin_} since last seen. The first two "
        f"are flat in the rate: a structural loss and a structural win. In the "
        f"fourth, more looking lets LastObs eliminate to \"out of the house\", "
        f"which Perpetua has no way to answer.\nFaint lines are the 20 homes; "
        f"bold line is all homes pooled with a Wilson 95% band; any point under "
        f"{MIN_N} questions is not drawn.",
        fontsize=9, color="#0b0b0b", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)


def fig_decomposition(join: Sequence[Dict[str, Any]], meta: Dict[str, Dict[str, Any]],
                      out: pathlib.Path, model: str = "PerpetuaStar") -> None:
    """Why the headline number moves: the change in (model - LastObs)
    from 1x split into the part from the changed mix of situations and
    the part from changed accuracy within them, with a household
    bootstrap interval."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    homes = sorted(meta)
    rates = [l for l, _ in RATES]
    fig, axes = plt.subplots(1, len(EXPLAIN_BINS), figsize=(4.3 * len(EXPLAIN_BINS), 4.2),
                             sharey=True, facecolor="#fcfcfb")
    for ax, b in zip(axes, EXPLAIN_BINS):
        ax.set_facecolor("#fcfcfb")
        xs = list(range(len(rates)))
        obs: List[float] = []
        mix: List[float] = []
        obs_ci: List[Tuple[float, float]] = []
        for rt in rates:
            d = decompose(join, b, rt, model)
            ci = _bootstrap_decompose(join, b, rt, model, homes)
            obs.append(d["observed"])
            mix.append(d["base"] + d["mix"])
            obs_ci.append(ci["observed"])
        ax.axhline(0, color="#52514e", linewidth=1)
        ax.plot(xs, obs, color="#6d4c41", linewidth=2.4, marker="o", markersize=7,
                markeredgecolor="#fcfcfb", markeredgewidth=1.4, zorder=4,
                label=f"observed {label_of(model)} − LastObs")
        for x, (a, c) in zip(xs, obs_ci):
            ax.plot([x, x], [a, c], color="#6d4c41", linewidth=1.6, zorder=3)
        ax.plot(xs, mix, color="#00838f", linewidth=2.2, linestyle=(0, (4, 3)),
                marker="^", markersize=7, markeredgecolor="#fcfcfb",
                markeredgewidth=1.2, zorder=4,
                label="predicted from the 1x per-situation accuracies\nand this rate's mix")
        ax.set_title(f"{b} since last seen", fontsize=9.5, color="#0b0b0b", loc="left")
        ax.set_xticks(xs)
        ax.set_xticklabels(rates, fontsize=8)
        ax.set_xlabel("observation rate", fontsize=8, color="#52514e")
        ax.grid(True, color="#e8e7e2", linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#e8e7e2")
        ax.tick_params(colors="#52514e", labelsize=7, length=0)
    axes[0].set_ylabel("accuracy difference", fontsize=8.5, color="#52514e")
    axes[0].legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.suptitle(
        "Why the headline number moves. Dashed = what the difference would be "
        "if only the mix of situations had changed and each situation's "
        "accuracy had stayed at its 1x value.\nWhere dashed tracks solid the "
        "mix explains the move (the day-old bands); where they part, accuracy "
        "inside the situations changed (12-24h). Bars: 95% interval from "
        "resampling the 20 homes.", fontsize=9, color="#0b0b0b", x=0.01,
        ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)


def write_explainer(labels: Sequence[str], workers: int) -> pathlib.Path:
    """Figures and a glossary that make the sweep's argument readable."""
    join = build_case_join(labels, workers)
    (REPORT_ROOT / "case_join.json").write_text(json.dumps(join))
    meta = household_meta(rate_dir(labels[0]))
    homes = sorted(meta)
    for b in ("12-24h", "1-2d"):
        fig_case_mix_by_home(join, meta, b, REPORT_ROOT / f"explain_mix_{b}.png")
        fig_case_accuracy(join, meta, b, REPORT_ROOT / f"explain_accuracy_{b}.png")
    fig_decomposition(join, meta, REPORT_ROOT / "explain_decomposition.png")
    md = ["# Reading the rate sweep", "",
          "## What the words mean", "",
          "**Observation rate.** The robot patrols the home on a fixed passive "
          "schedule: a *visit* goes to one room and inspects every receptacle "
          "in it. The fleet's standard schedule is 6 visits a day, which this "
          "sweep calls **1x**; 0.5x, 2x and 4x are 3, 12 and 24 visits a day. "
          "Nothing else about the household changes -- same homes, same object "
          "movements, same questions.", "",
          "**Age of last sighting.** How long before the question was asked the "
          "patrol last saw that object anywhere. Every comparison is inside one "
          "age band, because a denser patrol makes sightings fresher and would "
          "otherwise flatter itself.", "",
          "**Excluded.** After the object was last seen at a receptacle, a "
          "later visit inspected that receptacle and the object was not in it. "
          "The belief base class then rules that receptacle out until the "
          "object is sighted again, for every classical model.", "",
          "**The four situations.** Each question is one of:", ""]
    for c in CASE_ORDER:
        md.append(f"- **{CASE_PLAIN[c]}** (`{c}` in the generated tables)")
    md += ["",
           "The first is where LastObs is right by construction and the "
           "survival models lose; the second is where every classical model is "
           "wrong by construction and the survival models win.", "",
           "## The figures", "",
           "1. `explain_mix_12-24h.png`, `explain_mix_1-2d.png` -- the mix of "
           "situations per home per rate. This is what the rate changes.",
           "2. `explain_accuracy_12-24h.png`, `explain_accuracy_1-2d.png` -- "
           "accuracy inside each situation, per home and pooled with a Wilson "
           "95% band. This is what the rate mostly does not change.",
           "3. `explain_decomposition.png` -- the headline difference by rate, "
           "against what it would be if only the mix had changed and every "
           "situation's accuracy had stayed at its 1x value.", "",
           "## The decomposition, in numbers", "",
           "`observed` is the question-weighted PerpetuaStar minus LastObs "
           "difference in that band; `mix` and `within` sum to the change from "
           "1x; `covered` is the share of questions whose situation had enough "
           f"data ({MIN_N}+) to measure a within-situation change.", "",
           "| age band | rate | observed | change vs 1x | from the mix | from within situations | covered |",
           "|---|---|---|---|---|---|---|"]
    for b in EXPLAIN_BINS:
        for rt in [l for l, _ in RATES]:
            d = decompose(join, b, rt, "PerpetuaStar")
            ci = _bootstrap_decompose(join, b, rt, "PerpetuaStar", homes)
            md.append("| " + " | ".join([
                b, rt, f"{d['observed']:+.3f} [{ci['observed'][0]:+.3f}, {ci['observed'][1]:+.3f}]",
                f"{d['observed'] - d['base']:+.3f}", f"{d['mix']:+.3f}",
                f"{d['per_case']:+.3f}", f"{d['measured_share']:.2f}"]) + " |")
    md.append("")
    path = REPORT_ROOT / "explainer.md"
    path.write_text("\n".join(md) + "\n")
    return path


def write_summary(labels: Sequence[str], workers: int = 32) -> pathlib.Path:
    dirs = {l: report_dir(l) for l in labels if (report_dir(l) / "cells.csv.gz").exists()}
    per_rate = {l: _load_cells(d) for l, d in dirs.items()}
    meta = household_meta(rate_dir(next(iter(dirs))))
    first = next(iter(per_rate.values()))
    present = {base_name(r["model"]) for r in first if r["model"] != "routine_oracle"}
    order = ("LastObservation", "PeriodicPersistence", "DaytypeMixture",
             "SmoothedRecency", "Perpetua", "PerpetuaStar", "PerpetuaStarFlat")
    models = [m for m in order if m in present]
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    fb_lines, curves = fallback_tables(dirs)
    fig_learning_curve(curves, REPORT_ROOT / "learning_curve.png")
    fig_paired_by_home(per_rate, meta, REPORT_ROOT / "paired_by_home_perpetua_star.png",
                       "PerpetuaStar")
    fig_paired_by_home(per_rate, meta, REPORT_ROOT / "paired_by_home_perpetua.png",
                       "Perpetua")
    md = [
        "# Observation-rate sweep: model limit or data limit?",
        "",
        f"Rates {', '.join(f'{l} = {v} visits/day' for l, v in RATES if l in dirs)} "
        f"of the round-robin room patrol; 28-day episodes; {len(meta)} homes x "
        f"seeds {list(SEEDS)}; models {', '.join(label_of(m) for m in models)} + the "
        "routine oracle. Every table compares within a fixed age-of-last-sighting "
        f"bin, homes are never pooled with each other, and cells under {MIN_N} "
        "questions are masked. Per-rate full reports live in the visits<v>/ "
        "directories beside this file.",
        "",
        "## 1. Accuracy by age of last sighting, per resident group and rate",
        "",
    ] + age_by_group_tables(per_rate, meta, models) + [
        "## 2. Paired per-home-seed comparisons",
        "",
        "One pair per (home, seed): both models answer the same questions in the "
        "bin. `wins` counts pairs where the survival model is strictly better; "
        "pairs with fewer than 30 questions are excluded.",
        "",
    ] + paired_table(per_rate) + [
        "",
        "![](paired_by_home_perpetua_star.png)",
        "",
        "![](paired_by_home_perpetua.png)",
        "",
        "## 3. Fallback share by query day (learning speed)",
        "",
        "Share of PerpetuaStar edge beliefs computed from the fallback "
        "single-component prior rather than a fitted mixture; Perpetua and "
        "PerpetuaStarFlat share the fitting and agree to two decimals.",
        "",
    ] + fb_lines + ["", "![](learning_curve.png)", "",
        "## 4. Completed segments per edge at episode end",
        "",
    ] + segment_table(dirs) + ["",
        "## 5. Where the object really is, per age bin and rate",
        "",
        "The share of questions whose true answer is out of the house or on a "
        "person is the part of each bin no in-house model can get; it shifts "
        "with the rate because the rate changes which questions land in which "
        "bin.",
        "",
    ] + truth_share_table(list(dirs), sorted(meta)) + ["",
        "## 6. Survival-model accuracy on in-house questions only",
        "",
        "Same models, same bins, restricted to questions whose true answer is "
        "an ordinary receptacle. Their accuracy across rates can be compared "
        "here without the ceiling shift of section 5; comparators are not "
        "shown because their answers are not in the side file.",
        "",
    ] + in_house_conditional(list(dirs)) + ["",
        "## 7. Why: the four-case split per rate",
        "",
        "Each question by whether the object MOVED since its last sighting "
        "and whether a later visit EXCLUDED the last-seen receptacle (see "
        "`perpetua_cases.md` in each rate directory for the per-home tables; "
        "these totals are orientation only). The rate changes which case a "
        "question lands in, and that is what flips the sign of the "
        "comparison.",
        "",
    ] + cases_by_rate(list(dirs), workers) + [""]
    path = REPORT_ROOT / "summary.md"
    path.write_text("\n".join(md) + "\n")
    return path


# --------------------------------------------------------------- main --

def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage",
                    choices=("export", "analyse", "report", "explain", "all"),
                    default="all")
    ap.add_argument("--rates", nargs="*", default=[l for l, _ in RATES])
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--oracle-seeds", type=int, default=200)
    args = ap.parse_args()
    households = args.households or sorted(household_meta())
    if args.stage in ("export", "all"):
        for label in args.rates:
            export_rate(label, dict(RATES)[label], households, SEEDS)
    if args.stage in ("analyse", "all"):
        for label in args.rates:
            analyse_rate(label, args.workers, args.oracle_seeds, households)
            build(report_dir(label), report_dir(label))
    if args.stage in ("report", "all"):
        print(f"-> {write_summary(args.rates, args.workers)}")
    if args.stage in ("explain", "all"):
        print(f"-> {write_explainer(args.rates, args.workers)}")


if __name__ == "__main__":
    main()
