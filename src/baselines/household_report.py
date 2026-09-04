#!/usr/bin/env python3
"""Per-household report from household_analysis cells: separation,
history, and age-of-observation, both modes, seeds averaged per home.

Reads reports/baselines/household_analysis/{cells.csv.gz,households.json}
and writes household_report.md plus figures beside it. Seeds of one home
are pooled (equal question counts, so pooling equals the mean); the
per-seed spread is reported once per home so the reader knows the
noise floor.

Usage:
  python -m baselines.household_report [--in-dir ...] [--out-dir ...]
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import pathlib
import statistics
from typing import (Dict, Iterator, List, Optional, Sequence,
                    Tuple)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

from baselines.passive_eval import NEVER_SIGHTED_BIN   # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_IN = REPO_ROOT / "reports" / "baselines" / "household_analysis"
ORACLE = "routine_oracle"
LAST_OBS = "LastObservation"

# Fixed display order (bake-off order: frozen panel, then candidates) and
# the reference categorical palette in its validated slot order — hue
# follows the model, never its rank in a table.
MODEL_ORDER = ("LastObservation", "MostFrequentLocation", "TimetableLookup",
               "Markov1", "PeriodicPersistence", "DaytypeMixture",
               "HierarchyBackoff", "SmoothedRecency", "Perpetua",
               "PerpetuaStar", "PerpetuaStarFlat")
SHORT = {"LastObservation": "LastObs", "MostFrequentLocation": "MostFreq",
         "TimetableLookup": "Timetable", "Markov1": "Markov1",
         "PeriodicPersistence": "Periodic", "DaytypeMixture": "DaytypeMix",
         "HierarchyBackoff": "HierBackoff", "SmoothedRecency": "SmoothedRec",
         "Perpetua": "Perpetua", "PerpetuaStar": "PerpetuaStar",
         "PerpetuaStarFlat": "PerpStarFlat"}
PALETTE = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
           "#008300", "#4a3aa7", "#e34948", "#00838f", "#6d4c41", "#9e9d24")
PERPETUA_MODELS = ("Perpetua", "PerpetuaStar", "PerpetuaStarFlat")
PERPETUA_FOCUS = ("MostFrequentLocation", "Markov1", "Perpetua",
                  "PerpetuaStar", "PerpetuaStarFlat")
"""The survival models against the two frequency comparators, for the
focused per-home figure. The full per-home figure carries every model;
this one carries the five that the Perpetua question is about."""
LONG_AGES = ("[24h,48h)", "[48h,72h)", "[72h,inf)")
MIN_N = 30
"""Fewest questions a (home, age bin) cell needs before a figure draws it
or a table quotes it as a number. hh_016 has 3 questions with a sighting
3 days old; an accuracy of 1.000 on those is not a result."""


def wilson(correct: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson 95% interval for a binomial proportion. Questions of one
    home's seeds are pooled, so this is the sampling noise of the
    question set; seed-to-seed spread is reported separately."""
    if n == 0:
        return (0.0, 1.0)
    p = correct / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
AGE_RAMP = {"[24h,48h)": "#7ecdd3", "[48h,72h)": "#2a9aa4",
            "[72h,inf)": "#00646d"}
"""One hue, light to dark, for the three long-age bins: age is ordered,
so it takes a sequential ramp, never categorical hues."""
ROUTINE_MODELS = ("MostFrequentLocation", "TimetableLookup", "Markov1",
                  "PeriodicPersistence", "DaytypeMixture",
                  "HierarchyBackoff")
"""Models whose answer comes from the routine they inferred, as opposed to
the ones that lean on the freshest sighting (LastObservation,
SmoothedRecency, and the three Perpetua survival models, whose belief
decays from the last observation). Membership is deliberately unchanged
by the Perpetua additions so the "routine > LastObs" column keeps the
meaning it had in earlier reports."""

SURFACE, INK, INK2, GRID, ORACLE_GRAY = ("#fcfcfb", "#0b0b0b", "#52514e",
                                         "#e8e7e2", "#8a8983")
AGE_ORDER = ("[0h,0.25h)", "[0.25h,1h)", "[1h,3h)", "[3h,6h)", "[6h,12h)",
             "[12h,24h)", "[24h,48h)", "[48h,72h)", "[72h,inf)",
             NEVER_SIGHTED_BIN)
AGE_LABEL = {"[0h,0.25h)": "<15m", "[0.25h,1h)": "15m-1h", "[1h,3h)": "1-3h",
             "[3h,6h)": "3-6h", "[6h,12h)": "6-12h", "[12h,24h)": "12-24h",
             "[24h,48h)": "1-2d", "[48h,72h)": "2-3d", "[72h,inf)": "3d+",
             NEVER_SIGHTED_BIN: "never"}
HEADLINE = (7, 1.0)


def base_name(model: str) -> str:
    return model.split("(")[0]


# ------------------------------------------------------------- loading --

def load_cells(in_dir: pathlib.Path) -> List[dict]:
    rows = []
    with gzip.open(in_dir / "cells.csv.gz", "rt") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "household": r["household"], "seed": int(r["seed"]),
                "model": r["model"], "mode": r["mode"],
                "day": int(float(r["day"])), "horizon": float(r["horizon"]),
                "age_bin": r["age_bin"], "n": int(r["n"]),
                "correct": int(r["correct"]),
                "logloss": None if r["logloss"] in ("", "None")
                else float(r["logloss"])})
    return rows


class Agg:
    """Sum n and correct over rows grouped by a key; accuracy on demand."""

    def __init__(self, rows: Sequence[dict], key) -> None:
        self.n: Dict = collections.defaultdict(int)
        self.c: Dict = collections.defaultdict(int)
        for r in rows:
            k = key(r)
            self.n[k] += r["n"]
            self.c[k] += r["correct"]

    def acc(self, k) -> Optional[float]:
        return self.c[k] / self.n[k] if self.n.get(k) else None


def models_in(rows: Sequence[dict]) -> List[str]:
    present = {r["model"] for r in rows if r["model"] != ORACLE}
    ordered = [m for base in MODEL_ORDER for m in sorted(present)
               if base_name(m) == base]
    return ordered + sorted(present - set(ordered))


def color_of(model: str) -> str:
    base = base_name(model)
    return (PALETTE[MODEL_ORDER.index(base)] if base in MODEL_ORDER
            else INK2)


def label_of(model: str) -> str:
    return SHORT.get(base_name(model), base_name(model))


def f3(x: Optional[float]) -> str:
    return "-" if x is None else f"{x:.3f}"


# ------------------------------------------------------------- tables --

def per_home_overview(rows, meta, models, mode: str,
                      cell=None) -> Tuple[List[dict], str]:
    """One record per home: seed-pooled accuracy per model + oracle +
    separation stats. `cell` restricts frozen mode to one (D, h)."""
    sel = [r for r in rows if r["mode"] == mode
           and (cell is None or (r["day"], r["horizon"]) == cell)]
    a = Agg(sel, lambda r: (r["household"], r["model"]))
    per_seed = Agg(sel, lambda r: (r["household"], r["model"], r["seed"]))
    recs = []
    for hh, m in sorted(meta.items(), key=lambda kv: (
            kv[1]["resident_group"], kv[0])):
        accs = {mod: a.acc((hh, mod)) for mod in models}
        vals = [v for v in accs.values() if v is not None]
        if not vals:
            continue
        best = max(accs, key=lambda k: accs[k] if accs[k] is not None
                   else -1)
        seeds = sorted({r["seed"] for r in sel if r["household"] == hh})
        spread = []
        for mod in models:
            pts = [per_seed.acc((hh, mod, s)) for s in seeds]
            pts = [p for p in pts if p is not None]
            if len(pts) > 1:
                spread.append(max(pts) - min(pts))
        # paired: same questions per seed, so the per-seed difference
        # best - LastObs is the noise that matters for a ranking claim
        paired = []
        for s_ in seeds:
            b_, l_ = per_seed.acc((hh, best, s_)), per_seed.acc(
                (hh, LAST_OBS, s_))
            if b_ is not None and l_ is not None:
                paired.append(b_ - l_)
        recs.append({
            "household": hh, "type": m["household_type"],
            "residents": m["residents"], "group": m["resident_group"],
            "acc": accs, "oracle": a.acc((hh, ORACLE)),
            "best": best, "best_acc": accs[best],
            "best_minus_median": accs[best] - statistics.median(vals),
            "best_minus_lastobs": (accs[best] - accs[LAST_OBS]
                                   if accs.get(LAST_OBS) is not None
                                   else None),
            "seed_spread_max": max(spread) if spread else None,
            "paired_mean": statistics.mean(paired) if paired else None,
            "paired_pos": sum(1 for d in paired if d > 0),
            "paired_n": len(paired),
        })
    head = ["home", "type", "res"] + [label_of(m) for m in models] + [
        "oracle", "best", "best-median", "best-LastObs", "oracle-best",
        "seed range", "paired best-LastObs (seeds>0)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for g in ("1", "2", "3+"):
        grp = [r for r in recs if r["group"] == g]
        if not grp:
            continue
        for r in sorted(grp, key=lambda r: -(r["oracle"] or 0)):
            cells = [r["household"], r["type"], str(r["residents"])]
            cells += [f3(r["acc"][m]) for m in models]
            cells += [f3(r["oracle"]), label_of(r["best"]),
                      f3(r["best_minus_median"]),
                      f3(r["best_minus_lastobs"]),
                      f3(None if r["oracle"] is None
                         else r["oracle"] - r["best_acc"]),
                      f3(r["seed_spread_max"]),
                      ("-" if r["paired_mean"] is None else
                       f"{r['paired_mean']:+.3f} ({r['paired_pos']}/"
                       f"{r['paired_n']})")]
            lines.append("| " + " | ".join(cells) + " |")
        # group mean row
        cells = [f"**{g}-resident mean**", "", str(len(grp))]
        for m in models:
            v = [r["acc"][m] for r in grp if r["acc"][m] is not None]
            cells.append(f3(statistics.mean(v)) if v else "-")
        ov = [r["oracle"] for r in grp if r["oracle"] is not None]
        cells += [f3(statistics.mean(ov)) if ov else "-", "",
                  f3(statistics.mean(r["best_minus_median"] for r in grp)),
                  f3(statistics.mean(r["best_minus_lastobs"] for r in grp
                                     if r["best_minus_lastobs"]
                                     is not None)) if any(
                      r["best_minus_lastobs"] is not None
                      for r in grp) else "-",
                  f3(statistics.mean(r["oracle"] - r["best_acc"]
                                     for r in grp
                                     if r["oracle"] is not None))
                  if ov else "-", "", ""]
        lines.append("| " + " | ".join(cells) + " |")
    return recs, "\n".join(lines)


def age_table(rows, meta, models, group: Optional[str]) -> str:
    sel = [r for r in rows if r["mode"] == "continuous"
           and (group is None
                or meta[r["household"]]["resident_group"] == group)]
    a = Agg(sel, lambda r: (r["model"], r["age_bin"]))
    n = Agg(sel, lambda r: r["age_bin"])
    head = ["age of last sighting", "n"] + [label_of(m) for m in models
                                             ] + ["oracle"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for b in AGE_ORDER:
        if not n.n.get(b):
            continue
        cells = [AGE_LABEL[b], str(n.n[b] // max(1, len(models) + 1))]
        cells += [f3(a.acc((m, b))) for m in models]
        cells.append(f3(a.acc((ORACLE, b))))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def long_age_table(rows, meta, models) -> str:
    """Per home at long ages: what each side retains once the sighting is
    a day or more old. Every model here is recency-aware, so at short
    ages they all sit on LastObs; the informative comparison is at 1-2d
    and 3d+ against the oracle (routine only). The last column is the
    first age bin where the best routine model beats LastObs by at least
    0.02 — a margin above the paired seed noise, not a tie. Cells with
    fewer than MIN_N questions are not quoted."""
    routine = [m for m in models if base_name(m) in ROUTINE_MODELS]
    sel = [r for r in rows if r["mode"] == "continuous"]
    a = Agg(sel, lambda r: (r["household"], r["model"], r["age_bin"]))
    head = ["home", "type", "res", "LastObs 12-24h", "LastObs 1-2d",
            "best model 1-2d", "oracle 1-2d", "LastObs 3d+",
            "best model 3d+", "oracle 3d+", "routine > LastObs by 0.02 from"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for hh, m in sorted(meta.items(), key=lambda kv: (
            kv[1]["resident_group"], kv[0])):
        if not any(k[0] == hh for k in a.n):
            continue

        def lo(b):
            return a.acc((hh, LAST_OBS, b))

        def best_any(b):
            vals = [(a.acc((hh, r, b)), r) for r in models]
            vals = [(v, r) for v, r in vals if v is not None]
            return max(vals) if vals else (None, None)

        def best_routine(b):
            vals = [(a.acc((hh, r, b)), r) for r in routine]
            vals = [(v, r) for v, r in vals if v is not None]
            return max(vals) if vals else (None, None)
        cross = "never"
        for b in AGE_ORDER[:-1]:
            v, _r = best_routine(b)
            lv = lo(b)
            if v is not None and lv is not None and v - lv >= 0.02:
                cross = AGE_LABEL[b]
                break

        def n_of(b):
            return a.n.get((hh, LAST_OBS, b), 0)

        def guarded(v, b):
            n = n_of(b)
            return "-" if v is None else (f"n={n}<{MIN_N}" if n < MIN_N
                                          else f3(v))

        def cell(b):
            v, name = best_any(b)
            if v is None or n_of(b) < MIN_N:
                return guarded(v, b)
            return f"{f3(v)} ({label_of(name)}, n={n_of(b)})"
        lines.append("| " + " | ".join([
            hh, m["household_type"], str(m["residents"]),
            guarded(lo("[12h,24h)"), "[12h,24h)"),
            guarded(lo("[24h,48h)"), "[24h,48h)"), cell("[24h,48h)"),
            guarded(a.acc((hh, ORACLE, "[24h,48h)")), "[24h,48h)"),
            guarded(lo("[72h,inf)"), "[72h,inf)"),
            cell("[72h,inf)"),
            guarded(a.acc((hh, ORACLE, "[72h,inf)")), "[72h,inf)"),
            cross]) + " |")
    return "\n".join(lines)


def truth_by_age_table(meta) -> Optional[str]:
    """Where long-unseen objects actually are: the share of questions
    per age bin whose true location is out of the house, on a person,
    or an ordinary receptacle (seed-0 banks, pooled). Age is not
    exogenous — an object the patrol has not seen for days is one it
    could not see — and this is the size of that selection effect."""
    try:
        from baselines.bank import JsonlBank
        from baselines.household_analysis import (FINE_AGE_EDGES_H,
                                                  bank_path)
        from baselines.passive_eval import (PassiveProtocolConfig,
                                            question_ages)
    except ImportError:
        return None
    cfg = PassiveProtocolConfig(recency_bin_edges_h=FINE_AGE_EDGES_H)
    tab: Dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    for hh in sorted(meta):
        path = bank_path(hh, 0)
        if not path.exists():
            continue
        for ep in JsonlBank(path=path).episodes():
            ages = question_ages(ep)
            for day in ep.questions_by_day:
                for q in day:
                    truth = ep.true_location(q.object_id, q.t_query)
                    cat = ("out of house" if "OUT" in truth.upper()
                           else "on a person" if "PERSON" in truth.upper()
                           else "ordinary receptacle")
                    tab[cfg.recency_bin(ages[q.question_id])][cat] += 1
    if not tab:
        return None
    cats = ("ordinary receptacle", "out of house", "on a person")
    head = ["age of last sighting", "n"] + list(cats)
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for b in AGE_ORDER:
        c = tab.get(b)
        if not c:
            continue
        n = sum(c.values())
        lines.append("| " + " | ".join(
            [AGE_LABEL[b], str(n)] + [f"{c[k] / n:.0%}" for k in cats])
            + " |")
    return "\n".join(lines)


def history_stats(rows, meta, models) -> Tuple[Dict, str]:
    """Continuous-mode accuracy by query day per home; separation early
    vs late, and the day the best model reaches 95% of its own peak
    (3-day rolling mean)."""
    sel = [r for r in rows if r["mode"] == "continuous"]
    a = Agg(sel, lambda r: (r["household"], r["model"], r["day"]))
    days = sorted({r["day"] for r in sel})
    out = {}
    head = ["home", "type", "res", "best model", "best d3-5", "best d20+",
            "sep d3-5", "sep d20+", "LastObs d20+", "oracle d20+",
            "95%-of-peak day"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for hh, m in sorted(meta.items(), key=lambda kv: (
            kv[1]["resident_group"], kv[0])):
        curves = {mod: [a.acc((hh, mod, d)) for d in days] for mod in
                  models + [ORACLE]}
        if all(v is None for v in curves[models[0]]):
            continue

        def window(mod, lo_d, hi_d):
            v = [curves[mod][i] for i, d in enumerate(days)
                 if lo_d <= d <= hi_d and curves[mod][i] is not None]
            return statistics.mean(v) if v else None
        late = {mod: window(mod, 20, 99) for mod in models}
        late = {k: v for k, v in late.items() if v is not None}
        if not late:
            continue
        best = max(late, key=late.get)
        early = {mod: window(mod, 3, 5) for mod in models}
        ev = [v for v in early.values() if v is not None]
        lv = list(late.values())
        sep_early = (early[best] - statistics.median(ev)
                     if early.get(best) is not None and ev else None)
        sep_late = late[best] - statistics.median(lv)
        # 95%-of-peak day on the best model's 3-day rolling mean
        c = curves[best]
        roll = []
        for i in range(len(days)):
            w = [c[j] for j in range(max(0, i - 2), i + 1)
                 if c[j] is not None]
            roll.append(statistics.mean(w) if w else None)
        peak = max(v for v in roll if v is not None)
        day95 = next((days[i] for i, v in enumerate(roll)
                      if v is not None and v >= 0.95 * peak), None)
        out[hh] = {"curves": curves, "best": best, "day95": day95}
        lines.append("| " + " | ".join([
            hh, m["household_type"], str(m["residents"]), label_of(best),
            f3(early.get(best)), f3(late[best]), f3(sep_early),
            f3(sep_late), f3(window(LAST_OBS, 20, 99)),
            f3(window(ORACLE, 20, 99)),
            "-" if day95 is None else str(day95)]) + " |")
    return {"days": days, "homes": out}, "\n".join(lines)


# ------------------------------------------------------------- figures --

def _style(ax, title: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_title(title, fontsize=8, color=INK, loc="left")
    ax.grid(True, color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=7, length=0)
    ax.set_ylim(0, 1.0)


def _line(ax, xs, ys, model: str, **kw) -> None:
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    if not pts:
        return
    if model == ORACLE:
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=ORACLE_GRAY,
                linewidth=2, linestyle=(0, (4, 3)), label="routine oracle",
                **kw)
        return
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color_of(model),
            linewidth=2, marker="o", markersize=5.5, markeredgecolor=SURFACE,
            markeredgewidth=1.5, solid_capstyle="round",
            solid_joinstyle="round", label=label_of(model), **kw)


def _legend(fig, handles_labels) -> None:
    h, l = handles_labels
    fig.legend(h, l, loc="lower center", ncol=min(9, len(l)), frameon=False,
               fontsize=8, labelcolor=INK2,
               bbox_to_anchor=(0.5, -0.01))


def fig_age_by_group(rows, meta, models, out: pathlib.Path) -> None:
    groups = [g for g in ("1", "2", "3+")
              if any(m["resident_group"] == g for m in meta.values())]
    fig, axes = plt.subplots(1, len(groups), figsize=(4.2 * len(groups), 3.6),
                             squeeze=False, facecolor=SURFACE)
    for ax, g in zip(axes[0], groups):
        sel = [r for r in rows if r["mode"] == "continuous"
               and meta[r["household"]]["resident_group"] == g]
        a = Agg(sel, lambda r: (r["model"], r["age_bin"]))
        bins = [b for b in AGE_ORDER[:-1] if a.n.get((models[0], b))]
        xs = list(range(len(bins)))
        for m in models + [ORACLE]:
            _line(ax, xs, [a.acc((m, b)) for b in bins], m)
        n_homes = sum(1 for m in meta.values() if m["resident_group"] == g)
        _style(ax, f"{g}-resident homes (n={n_homes}), belief kept current")
        ax.set_xticks(xs)
        ax.set_xticklabels([AGE_LABEL[b] for b in bins], rotation=0)
        ax.set_xlabel("age of the object's last sighting", fontsize=8,
                      color=INK2)
    axes[0][0].set_ylabel("top-1 accuracy", fontsize=8, color=INK2)
    _legend(fig, axes[0][0].get_legend_handles_labels())
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _grid_of_homes(meta):
    homes = sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
    cols = 5 if len(homes) > 6 else max(1, len(homes))
    rows_n = -(-len(homes) // cols)
    return homes, rows_n, cols


def fig_age_by_home(rows, meta, models, out: pathlib.Path) -> None:
    homes, nr, nc = _grid_of_homes(meta)
    fig, axes = plt.subplots(nr, nc, figsize=(3.4 * nc, 2.7 * nr),
                             squeeze=False, facecolor=SURFACE)
    sel = [r for r in rows if r["mode"] == "continuous"]
    a = Agg(sel, lambda r: (r["household"], r["model"], r["age_bin"]))
    bins = AGE_ORDER[:-1]
    xs = list(range(len(bins)))
    for i, hh in enumerate(homes):
        ax = axes[i // nc][i % nc]
        for m in models + [ORACLE]:
            _line(ax, xs, [a.acc((hh, m, b)) for b in bins], m)
        mt = meta[hh]
        _style(ax, f"{hh} · {mt['household_type'][:38]} · {mt['residents']}r")
        ax.set_xticks(xs)
        ax.set_xticklabels([AGE_LABEL[b] for b in bins], rotation=45,
                           ha="right", fontsize=6)
    for j in range(len(homes), nr * nc):
        axes[j // nc][j % nc].axis("off")
    _legend(fig, axes[0][0].get_legend_handles_labels())
    fig.suptitle("Accuracy by age of last sighting, per home "
                 "(belief kept current, seeds pooled)", fontsize=10,
                 color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(out, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def fig_history_by_home(hist: Dict, meta, models, out: pathlib.Path) -> None:
    homes = [h for h in sorted(meta, key=lambda h: (
        meta[h]["resident_group"], h)) if h in hist["homes"]]
    if not homes:
        return
    nc = 5 if len(homes) > 6 else max(1, len(homes))
    nr = -(-len(homes) // nc)
    fig, axes = plt.subplots(nr, nc, figsize=(3.4 * nc, 2.7 * nr),
                             squeeze=False, facecolor=SURFACE)
    days = hist["days"]
    for i, hh in enumerate(homes):
        ax = axes[i // nc][i % nc]
        curves = hist["homes"][hh]["curves"]
        for m in models + [ORACLE]:
            _line(ax, days, curves[m], m)
        mt = meta[hh]
        _style(ax, f"{hh} · {mt['household_type'][:38]} · {mt['residents']}r")
        ax.set_xlabel("query day (history length)", fontsize=7, color=INK2)
    for j in range(len(homes), nr * nc):
        axes[j // nc][j % nc].axis("off")
    _legend(fig, axes[0][0].get_legend_handles_labels())
    fig.suptitle("Accuracy by query day, per home (belief kept current, "
                 "seeds pooled; 90 questions per day)", fontsize=10,
                 color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(out, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def fig_modes_by_group(rows, meta, models, out: pathlib.Path) -> None:
    """Frozen vs continuous at matched age bins, LastObs and the best
    routine model only, per resident group — four lines, not sixteen."""
    groups = [g for g in ("1", "2", "3+")
              if any(m["resident_group"] == g for m in meta.values())]
    routine = [m for m in models if base_name(m) in ROUTINE_MODELS]
    fig, axes = plt.subplots(1, len(groups), figsize=(4.2 * len(groups), 3.6),
                             squeeze=False, facecolor=SURFACE)
    for ax, g in zip(axes[0], groups):
        sel = [r for r in rows
               if meta[r["household"]]["resident_group"] == g]
        a = Agg(sel, lambda r: (r["mode"], r["model"], r["age_bin"]))
        cont = Agg([r for r in sel if r["mode"] == "continuous"],
                   lambda r: r["model"])
        best_r = (max(routine, key=lambda m: cont.acc(m) or -1)
                  if routine else None)
        bins = [b for b in AGE_ORDER[:-1]
                if a.n.get(("continuous", models[0], b))]
        xs = list(range(len(bins)))
        for m in [LAST_OBS] + ([best_r] if best_r else []):
            if m not in models:
                continue
            _line(ax, xs, [a.acc(("continuous", m, b)) for b in bins], m)
            pts = [a.acc(("frozen", m, b)) for b in bins]
            keep = [(x, y) for x, y in zip(xs, pts) if y is not None]
            if keep:
                ax.plot([p[0] for p in keep], [p[1] for p in keep],
                        color=color_of(m), linewidth=2, linestyle=(0, (2, 2)),
                        marker="s", markersize=5, markeredgecolor=SURFACE,
                        markeredgewidth=1.5,
                        label=f"{label_of(m)} (frozen forecast)")
        _style(ax, f"{g}-resident homes: kept current (solid) vs frozen "
                   f"forecast (dotted)")
        ax.set_xticks(xs)
        ax.set_xticklabels([AGE_LABEL[b] for b in bins])
        ax.set_xlabel("age of the object's last sighting", fontsize=8,
                      color=INK2)
    axes[0][0].set_ylabel("top-1 accuracy", fontsize=8, color=INK2)
    _legend(fig, axes[0][0].get_legend_handles_labels())
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_perpetua_by_home(rows, meta, models, out: pathlib.Path) -> None:
    """The Perpetua question, one panel per home: the three survival
    models against the two frequency comparators. Seeds are pooled within
    a home; homes are never pooled with each other."""
    focus = [m for m in models if base_name(m) in PERPETUA_FOCUS]
    if not any(base_name(m) in PERPETUA_MODELS for m in focus):
        return
    homes, nr, nc = _grid_of_homes(meta)
    fig, axes = plt.subplots(nr, nc, figsize=(3.4 * nc, 2.7 * nr),
                             squeeze=False, facecolor=SURFACE)
    sel = [r for r in rows if r["mode"] == "continuous"]
    a = Agg(sel, lambda r: (r["household"], r["model"], r["age_bin"]))
    bins = AGE_ORDER[:-1]
    xs = list(range(len(bins)))
    for i, hh in enumerate(homes):
        ax = axes[i // nc][i % nc]
        counts = [a.n.get((hh, focus[0], b), 0) for b in bins]
        for m in focus + [ORACLE]:
            ys = [a.acc((hh, m, b)) if n >= MIN_N else None
                  for b, n in zip(bins, counts)]
            _line(ax, xs, ys, m)
            if m == ORACLE:
                continue
            band = [wilson(a.c[(hh, m, b)], a.n[(hh, m, b)])
                    if n >= MIN_N else None for b, n in zip(bins, counts)]
            keep = [(x, lo, hi) for x, bd in zip(xs, band) if bd
                    for lo, hi in [bd]]
            if keep:
                ax.fill_between([k[0] for k in keep], [k[1] for k in keep],
                                [k[2] for k in keep], color=color_of(m),
                                alpha=0.12, linewidth=0, zorder=1)
        mt = meta[hh]
        _style(ax, f"{hh} · {mt['household_type'][:38]} · {mt['residents']}r")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{AGE_LABEL[b]}\nn={n}" for b, n in zip(bins, counts)],
                           rotation=45, ha="right", fontsize=5.5)
        ax.axvspan(len(bins) - 3.5, len(bins) - 0.5, color="#f2f1ec",
                   zorder=0)
    for j in range(len(homes), nr * nc):
        axes[j // nc][j % nc].axis("off")
    _legend(fig, axes[0][0].get_legend_handles_labels())
    fig.suptitle("Perpetua models vs the frequency comparators, per home "
                 "(belief kept current, seeds pooled; shading = Wilson 95% "
                 f"interval; bins under {MIN_N} questions not drawn; grey "
                 "band = 1 day and older)", fontsize=10, color=INK, x=0.01,
                 ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(out, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def fig_perpetua_long_age_delta(rows, meta, models, out: pathlib.Path
                                ) -> None:
    """Per home, at the three long-age bins: each survival model's
    accuracy minus MostFreq's. One row per home, never a fleet mean — the
    question is which homes it helps, and a mean over homes would hide
    exactly that."""
    present = {base_name(m): m for m in models}
    ref = present.get("MostFrequentLocation")
    variants = [present[b] for b in PERPETUA_MODELS if b in present]
    if ref is None or not variants:
        return
    sel = [r for r in rows if r["mode"] == "continuous"]
    a = Agg(sel, lambda r: (r["household"], r["model"], r["age_bin"]))
    homes = sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
    ys = list(range(len(homes)))[::-1]
    fig, axes = plt.subplots(1, len(variants),
                             figsize=(3.6 * len(variants), 0.42 * len(homes) + 2.0),
                             squeeze=False, sharey=True, facecolor=SURFACE)
    for ax, model in zip(axes[0], variants):
        ax.set_facecolor(SURFACE)
        ax.axvline(0, color=INK2, linewidth=1.2, zorder=1)
        ax.grid(True, axis="x", color=GRID, linewidth=1)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=7, length=0)
        for y, hh in zip(ys, homes):
            for k, b in enumerate(LONG_AGES):
                n = a.n.get((hh, model, b), 0)
                v, r0 = a.acc((hh, model, b)), a.acc((hh, ref, b))
                if v is None or r0 is None or n < MIN_N:
                    continue
                # Unpaired normal interval for the difference of two
                # proportions on the same n. The two models answer the
                # SAME questions, so the paired interval is narrower;
                # this one is the conservative bound.
                se = ((v * (1 - v) + r0 * (1 - r0)) / n) ** 0.5
                yy = y + (1 - k) * 0.22       # three bins spread within the row
                ax.plot([v - r0 - 1.96 * se, v - r0 + 1.96 * se], [yy, yy],
                        color=AGE_RAMP[b], linewidth=1.4, zorder=2,
                        solid_capstyle="butt")
                ax.plot(v - r0, yy, marker="o", markersize=7,
                        color=AGE_RAMP[b], markeredgecolor=SURFACE,
                        markeredgewidth=1.2, linestyle="none", zorder=3)
        ax.set_title(f"{label_of(model)} − MostFreq", fontsize=9, color=INK,
                     loc="left")
        ax.set_xlabel("top-1 accuracy difference", fontsize=8, color=INK2)
    axes[0][0].set_yticks(ys)
    axes[0][0].set_yticklabels(
        [f"{h} · {meta[h]['residents']}r" for h in homes], fontsize=7)
    handles = [plt.Line2D([], [], marker="o", markersize=8, linestyle="none",
                          color=AGE_RAMP[b], markeredgecolor=SURFACE,
                          markeredgewidth=1.2) for b in LONG_AGES]
    _legend(fig, (handles, [AGE_LABEL[b] for b in LONG_AGES]))
    fig.suptitle("Where the survival models beat frequency: per-home "
                 "difference at long ages (belief kept current, seeds "
                 "pooled; bars = conservative 95% interval of the "
                 f"difference; bins under {MIN_N} questions not drawn; "
                 "right of the line = the survival model wins)",
                 fontsize=9.5, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_separation(recs: List[dict], out: pathlib.Path) -> None:
    """Dot plot per home: LastObs, best model, oracle on one accuracy
    axis, homes sorted by oracle within resident group."""
    recs = [r for r in recs if r["oracle"] is not None]
    if not recs:
        return
    order = sorted(recs, key=lambda r: (r["group"], -r["oracle"]))
    fig, ax = plt.subplots(figsize=(7, 0.32 * len(order) + 1.6),
                           facecolor=SURFACE)
    ys = list(range(len(order)))[::-1]
    for y, r in zip(ys, order):
        ax.plot([r["acc"].get(LAST_OBS), r["best_acc"]], [y, y],
                color=GRID, linewidth=2, zorder=1)
        if r["acc"].get(LAST_OBS) is not None:
            ax.plot(r["acc"][LAST_OBS], y, "o", color=color_of(LAST_OBS),
                    markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5,
                    label="LastObs", zorder=3)
        ax.plot(r["best_acc"], y, "o", color=color_of(r["best"]),
                markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5,
                zorder=3)
        ax.plot(r["oracle"], y, "|", color=ORACLE_GRAY, markersize=12,
                markeredgewidth=2, label="routine oracle", zorder=2)
        ax.text(1.005, y, f"{label_of(r['best'])}", fontsize=7, color=INK2,
                va="center", transform=ax.get_yaxis_transform())
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['household']} · {r['type'][:30]} · "
                        f"{r['residents']}r" for r in order], fontsize=7,
                       color=INK)
    _style(ax, "Per home: LastObs (blue) to best model (its own hue), "
               "routine oracle as gray tick")
    ax.set_ylim(-1, len(order))
    ax.set_xlim(0.2, 1.0)
    ax.set_xlabel("top-1 accuracy, belief kept current, all questions",
                  fontsize=8, color=INK2)
    h, l = ax.get_legend_handles_labels()
    seen, hh, ll = set(), [], []
    for a_, b_ in zip(h, l):
        if b_ not in seen:
            seen.add(b_); hh.append(a_); ll.append(b_)
    ax.legend(hh, ll, loc="lower right", frameon=False, fontsize=7,
              labelcolor=INK2)
    fig.tight_layout()
    fig.subplots_adjust(right=0.84)     # room for the best-model labels
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


# ------------------------------------------------------ perpetua side --

def _stream_side(in_dir: pathlib.Path, name: str) -> Iterator[dict]:
    """Rows of one gzipped side file, one at a time. The absence-signal
    file is one row per question per model per mode — millions of rows on
    the full fleet — so every consumer here accumulates counters in a
    single pass and never holds the file in memory."""
    path = in_dir / name
    if not path.exists():
        return
    with gzip.open(path, "rt") as fh:
        yield from csv.DictReader(fh)


def perpetua_section(in_dir: pathlib.Path) -> Optional[str]:
    """Tables from the Perpetua side files: the absence signal by age bin
    and where the object really was (kept-current mode), fallback use by
    query day, and how much training data the edges had. Pooling here is
    across questions of one model, not across homes: these are properties
    of the estimator, not household comparisons."""
    cats = ("ordinary receptacle", "out of house", "on a person")
    # model -> age bin -> category -> [n, sum of max belief]
    belief: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    # model -> age bin -> [questions, questions with a fallback edge]
    fb_q: Dict[str, Dict[str, List[int]]] = {}
    for r in _stream_side(in_dir, "absence_signal.csv.gz"):
        if r["mode"] != "continuous":
            continue
        m, b = r["model"], r["age_bin"]
        cell = belief.setdefault(m, {}).setdefault(b, {})
        acc = cell.setdefault(r["truth_category"], [0.0, 0.0])
        acc[0] += 1
        acc[1] += float(r["max_edge_belief"])
        q = fb_q.setdefault(m, {}).setdefault(b, [0, 0])
        q[0] += 1
        q[1] += int(int(r["n_fallback_edges"]) > 0)
    # model -> day -> [edge beliefs, fallback edge beliefs]
    fallback: Dict[str, Dict[int, List[int]]] = {}
    for r in _stream_side(in_dir, "perpetua_fallback.csv.gz"):
        cell = fallback.setdefault(r["model"], {}).setdefault(int(r["day"]),
                                                              [0, 0])
        cell[0] += int(r["n_edge_beliefs"])
        cell[1] += int(r["n_fallback_edge_beliefs"])
    # model -> lists over edges
    edges: Dict[str, Dict[str, List[int]]] = {}
    for r in _stream_side(in_dir, "perpetua_edges.csv.gz"):
        cell = edges.setdefault(r["model"], {"ps": [], "es": [], "rs": [],
                                             "ks": []})
        cell["ps"].append(int(r["n_persistence_segments"]))
        cell["es"].append(int(r["n_emergence_segments"]))
        cell["rs"].append(int(r["n_resets"]))
        cell["ks"].append(int(r["pf_components"]))
    if not belief and not edges:
        return None
    models = sorted(set(belief) | set(edges),
                    key=lambda m: (MODEL_ORDER.index(base_name(m))
                                   if base_name(m) in MODEL_ORDER else 99, m))
    md: List[str] = []
    if belief:
        md += ["Absence signal (kept current, every home and seed): mean of "
               "the largest per-edge presence belief, split by where the "
               "object really was. A usable not-in-the-house threshold needs "
               "the out-of-house column well below the ordinary one. `n` "
               "counts questions; `fallback` is the share of predictions "
               "with at least one edge still on the fallback prior.", ""]
        head = (["model", "age of last sighting", "n"]
                + [f"max belief, {c}" for c in cats] + ["fallback"])
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for m in models:
            for b in AGE_ORDER:
                cell = belief.get(m, {}).get(b)
                if not cell:
                    continue
                cells = []
                for c in cats:
                    acc = cell.get(c)
                    cells.append(f"{acc[1] / acc[0]:.3f} ({int(acc[0])})"
                                 if acc else "-")
                q = fb_q[m][b]
                lines.append("| " + " | ".join(
                    [label_of(m), AGE_LABEL.get(b, b), str(q[0])]
                    + cells + [f"{q[1] / q[0]:.2f}"]) + " |")
        md += lines + [""]
    if fallback:
        md += ["Fallback use by query day: share of edge beliefs computed "
               "from the fallback single-component prior rather than a "
               "fitted mixture.", ""]
        days = sorted({d for v in fallback.values() for d in v})
        shown = [d for d in days if d % 3 == 0 or d == days[-1]]
        head = ["model"] + [f"day {d}" for d in shown]
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for m in models:
            if m not in fallback:
                continue
            cells = []
            for d in shown:
                n, k = fallback[m].get(d, [0, 0])
                cells.append(f"{k / n:.2f}" if n else "-")
            lines.append("| " + " | ".join([label_of(m)] + cells) + " |")
        md += lines + [""]
    if edges:
        md += ["Training data per edge at the end of the kept-current run: "
               "completed segments are what the EM fits on; an edge needs 2 "
               "of a kind to leave the fallback prior for that filter.", ""]
        head = ["model", "edges", "median persistence segs",
                "median emergence segs", "share < 2 persistence",
                "share < 2 emergence", "median resets", "mean K persistence"]
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for m in models:
            if m not in edges:
                continue
            e = edges[m]
            n = len(e["ps"])
            ps, es, rs = sorted(e["ps"]), sorted(e["es"]), sorted(e["rs"])
            lines.append("| " + " | ".join([
                label_of(m), str(n), str(ps[n // 2]), str(es[n // 2]),
                f"{sum(v < 2 for v in ps) / n:.2f}",
                f"{sum(v < 2 for v in es) / n:.2f}", str(rs[n // 2]),
                f"{sum(e['ks']) / n:.2f}"]) + " |")
        md += lines + [""]
    return "\n".join(md)


# -------------------------------------------------------------- report --

def build(in_dir: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    rows = load_cells(in_dir)
    info = json.loads((in_dir / "households.json").read_text())
    prov = json.loads((in_dir / "provenance.json").read_text())
    meta = {h: m for h, m in info["households"].items()
            if any(r["household"] == h for r in rows)}
    models = models_in(rows)
    out_dir.mkdir(parents=True, exist_ok=True)

    recs_c, t_overview = per_home_overview(rows, meta, models, "continuous")
    _recs_f, t_frozen = per_home_overview(rows, meta, models, "frozen",
                                          cell=HEADLINE)
    t_age_all = age_table(rows, meta, models, None)
    t_age = {g: age_table(rows, meta, models, g) for g in ("1", "2", "3+")
             if any(m["resident_group"] == g for m in meta.values())}
    t_long = long_age_table(rows, meta, models)
    t_truth = truth_by_age_table(meta)
    hist, t_hist = history_stats(rows, meta, models)
    t_perpetua = perpetua_section(in_dir)

    fig_age_by_group(rows, meta, models, out_dir / "age_by_group.png")
    fig_age_by_home(rows, meta, models, out_dir / "age_by_home.png")
    fig_history_by_home(hist, meta, models, out_dir / "history_by_home.png")
    fig_modes_by_group(rows, meta, models, out_dir / "modes_by_group.png")
    fig_separation(recs_c, out_dir / "separation_by_home.png")
    fig_perpetua_by_home(rows, meta, models, out_dir / "perpetua_by_home.png")
    fig_perpetua_long_age_delta(rows, meta, models,
                                out_dir / "perpetua_long_age_delta.png")

    seeds = sorted({r["seed"] for r in rows})
    md = [
        "# Per-household passive analysis",
        "",
        f"{len(meta)} households x {len(seeds)} seeds "
        f"({', '.join(map(str, seeds))}), {len(models)} belief models + "
        f"the routine oracle. Seeds of one home are pooled (equal "
        f"question counts, so this is the seed mean); the last column of "
        f"the overview is the largest across-seed range any model showed "
        f"on that home, the noise floor for reading its row. Commit "
        f"`{str(prov['git'][0])[:12]}`, run {prov['generated_at'][:19]}.",
        "",
        "Two evaluation modes over the same questions:",
        "",
        "- **kept current** (continuous): the belief is updated with every "
        "sighting strictly before each query and answers about now. Query "
        "day is the history length; the age of the object's last sighting "
        "is recorded per question.",
        "- **frozen forecast**: the bake-off protocol. The belief is frozen "
        "at day D and answers questions up to 7 days later, bucketed by "
        "horizon; the headline cell is D=7, h=1 (questions 6-24h after "
        "the freeze).",
        "",
        "The routine oracle predicts from the household's authored rules "
        "re-realized under many seeds, with no observations: routine "
        "knowledge alone. Not a hard ceiling; a fresh sighting beats it.",
        "",
        "## Which homes separate the models (belief kept current)",
        "",
        "Sorted by the oracle within resident group, so the most "
        "routine-predictable home of each group comes first.",
        "",
        t_overview,
        "",
        "![](separation_by_home.png)",
        "",
        "## Same homes under the frozen forecast (D=7, h=1)",
        "",
        t_frozen,
        "",
        "## Age of the last sighting",
        "",
        "All homes pooled:",
        "",
        t_age_all,
        "",
    ]
    for g, t in t_age.items():
        md += [f"{g}-resident homes:", "", t, ""]
    md += [
        "![](age_by_group.png)",
        "",
        "Kept current versus frozen forecast at matched ages, LastObs and "
        "the best routine model per group:",
        "",
        "![](modes_by_group.png)",
        "",
        "Every model here uses recent sightings, so at short ages they all "
        "sit on LastObs; the informative comparison is at a day or more, "
        "against the oracle:",
        "",
        t_long,
        "",
        "![](age_by_home.png)",
        "",
        "Age is not exogenous. An object the patrol has not seen for days "
        "is one it could not see — the share of questions whose true "
        "location is out of the house or on a person rises with age "
        "(seed-0 banks, all homes pooled):",
        "",
        t_truth or "(banks not available)",
        "",
        "## History: accuracy by query day",
        "",
        "`sep` is best model minus the median model over that day window; "
        "`95%-of-peak day` is when the best model's 3-day rolling accuracy "
        "first reaches 95% of its own peak.",
        "",
        t_hist,
        "",
        "![](history_by_home.png)",
        "",
    ]
    if t_perpetua:
        md += [
            "## Perpetua and Perpetua*: survival models vs frequency",
            "",
            "The three survival models against the two frequency "
            "comparators the question is about, one panel per home. Homes "
            "are never pooled: a fleet mean would hide which homes the "
            "survival machinery helps.",
            "",
            "![](perpetua_by_home.png)",
            "",
            "The same comparison as a per-home difference at the three "
            "long-age bins, where the models actually diverge:",
            "",
            "![](perpetua_long_age_delta.png)",
            "",
            "### Absence signal, fallback, training data",
            "",
            t_perpetua,
            "",
        ]
    md += [
        "Figures are static; every plotted value appears in the tables "
        "above, which are the table view.",
    ]
    path = out_dir / "household_report.md"
    path.write_text("\n".join(md) + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-dir", type=pathlib.Path, default=DEFAULT_IN)
    ap.add_argument("--out-dir", type=pathlib.Path, default=None)
    args = ap.parse_args()
    path = build(args.in_dir, args.out_dir or args.in_dir)
    print(f"-> {path}")


if __name__ == "__main__":
    main()
