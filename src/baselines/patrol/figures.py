"""The four report figures as PNGs, from the same run logs the summary reads.

    python3 -m baselines.patrol.figures --logs "classical/*.jsonl" "llm/*/run_log.jsonl" --banks "banks/*.jsonl" --out figs/
"""
from __future__ import annotations

import argparse
import glob
import pathlib
import sys
from collections import defaultdict
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from baselines.patrol.summary import Cell, DAY_SHORT, THRESHOLDS, group, load_logs, shift_days_from_banks, truth_kind

SHORT = {"LastObservation": "last seen", "MostFrequentLocation": "most frequent", "TimetableLookup(bin=1h,days=all)": "timetable",
         "Markov1(a=1,cut=24h,hl=24h)": "markov1", "PeriodicPersistence(min_dep=2,bin=1h,hl=24h)": "periodic",
         "SmoothedRecency(hl=6h,freq=24h)": "smoothed recency", "HierarchyBackoff(po=5,pc=5,hl=24h)": "hierarchy backoff",
         "DaytypeMixture(K=3,bin=2h,hl=24h)": "daytype mixture", "Perpetua(lognormal,K<=3,pm=0.01,steps=10)": "perpetua",
         "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "perpetua*"}


def short(a: str) -> str:
    return SHORT.get(a, a.replace("llm_", "LLM ").replace("/look_on", "").replace("/look_off", " (no look)"))


# The MAIN figure roster: three classical beliefs that behave differently (recency, frequency, periodicity)
# and two LLM memories (naive, summary), each told and not told. The other classical beliefs sit within a
# point or two of these and only add overlapping lines; "recent" tracks naive. --all restores everyone.
MAIN_CLASSICAL = ("LastObservation", "MostFrequentLocation", "PeriodicPersistence(min_dep=2,bin=1h,hl=24h)")
MAIN_LLM_PREFIX = ("llm_naive/told/", "llm_naive/not_told/", "llm_summary/told/", "llm_summary/not_told/")
COLORS = {"LastObservation": "#1f77b4", "MostFrequentLocation": "#2ca02c", "PeriodicPersistence(min_dep=2,bin=1h,hl=24h)": "#9467bd",
          "llm_naive": "#d62728", "llm_recent": "#ff7f0e", "llm_summary": "#8c564b"}


def in_main(agent: str) -> bool:
    return agent in MAIN_CLASSICAL or any(agent.startswith(p) for p in MAIN_LLM_PREFIX) \
        or (agent.startswith("llm_") and "/not_told/" not in agent and "/told/" not in agent)


def style(agent: str) -> str:
    """Classical solid; LLM told dashed, not-told dotted."""
    if not agent.startswith("llm_"):
        return "-"
    return ":" if "/not_told/" in agent else "--"


def label(agent: str) -> str:
    s = short(agent)
    return s.replace("/not_told", " (not told)").replace("/told", " (told)")


def color(agent: str):
    if agent in COLORS:
        return COLORS[agent]
    for k, c in COLORS.items():
        if agent.startswith(k):
            return c
    return None


def day_labels(days, day_names, shift_count, n_hh):
    return [f"{DAY_SHORT.get(day_names.get(d, str(d)), d)}{'*' if shift_count[d] == n_hh else ('°' if shift_count[d] else '')}" for d in days]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True)
    ap.add_argument("--banks", nargs="+", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--density", type=int, default=4, help="patrol density for the per-day figures")
    ap.add_argument("--all", action="store_true", help="every agent in the logs (default: the MAIN roster only)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    rows = load_logs([p for pat in a.logs for p in glob.glob(pat)])
    if not a.all:
        rows = [r for r in rows if in_main(r.get("agent") or r["belief"])]
    shift, names, moved = shift_days_from_banks([p for pat in a.banks for p in glob.glob(pat)])
    for r in rows:
        r["agent"] = r.get("agent") or r["belief"]
        r["shift"] = r["day_index"] in set(shift.get(r["household"], []))
    households = sorted({r["household"] for r in rows})
    days = sorted({r["day_index"] for r in rows})
    shift_count = defaultdict(int)
    for h in households:
        for d in shift.get(h, []):
            shift_count[d] += 1
    labels = day_labels(days, names, shift_count, len(households))
    weekend = [i for i, d in enumerate(days) if names.get(d) in ("Saturday", "Sunday")]

    def shade(ax):
        for i in weekend:
            ax.axvspan(i - 0.5, i + 0.5, color="0.9", zorder=0)

    # 1. accuracy per day per agent, density a.density, look off (classical) and look on/off (LLM)
    for look_set, fname in ((("off",), "fig1_accuracy_per_day_look_off.png"), (("voi", "llm"), "fig1_accuracy_per_day_look_on.png")):
        sub = [r for r in rows if r["patrol_hours"] == a.density and r["look"] in look_set]
        if not sub:
            continue
        agents = sorted({r["agent"] for r in sub})
        cells = group(sub, ("agent", "day_index"), None)
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
        for ax, kinds, title in ((axes[0], None, "all questions"), (axes[1], ("spot",), "in-house spot truths only")):
            for ag in agents:
                ys = []
                for d in days:
                    rs = [r for r in sub if r["agent"] == ag and r["day_index"] == d and (kinds is None or truth_kind(r["truth"]) in kinds)]
                    ys.append(sum(r["correct"] for r in rs) / len(rs) if rs else float("nan"))
                ax.plot(range(len(days)), ys, marker="o", ms=4, lw=1.8, label=label(ag), color=color(ag), ls=style(ag))
            shade(ax)
            ax.set_xticks(range(len(days))); ax.set_xticklabels(labels); ax.set_ylim(0.5, 1.0); ax.grid(alpha=0.3)
            ax.set_title(f"accuracy per day, patrol every {a.density} h, look {'/'.join(look_set)} — {title}")
        axes[1].legend(fontsize=8, ncol=1, loc="lower left")
        fig.text(0.01, 0.01, "* every household shifts that day (weekend, grey); ° some households (guests / illness); LLM dashed = told the residents' messages, dotted = not told", fontsize=8)
        fig.tight_layout(); fig.savefig(a.out / fname, dpi=130); plt.close(fig)

    # 2. accuracy vs density: classical agents at every density; LLM agents only where they ran at
    #    more than one density (the look-on density check)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, lks in zip(axes, (("off",), ("voi", "llm"), ("top",))):
        sub = [r for r in rows if r["look"] in lks]
        cells = group(sub, ("agent", "patrol_hours"), None)
        for ag in sorted({r["agent"] for r in sub}):
            dens = sorted({d for (a, d) in cells if a == ag})
            if len(dens) < 2:
                continue
            ax.plot(dens, [cells[(ag, d)].acc_all for d in dens], marker="o", lw=1.8, label=label(ag), color=color(ag), ls=style(ag))
        all_dens = sorted({r["patrol_hours"] for r in sub})
        ax.set_xscale("log", base=2); ax.set_xticks(all_dens); ax.set_xticklabels([f"every {d} h" for d in all_dens])
        ax.set_title(f"accuracy vs patrol density, look {'/'.join(lks)}"); ax.grid(alpha=0.3); ax.set_ylim(0.6, 1.0)
        ax.legend(fontsize=8, ncol=1)
    fig.tight_layout(); fig.savefig(a.out / "fig2_accuracy_vs_density.png", dpi=130); plt.close(fig)

    # 3. told vs not told per day (LLM)
    rows_all = load_logs([p for pat in a.logs for p in glob.glob(pat)])
    for r in rows_all:
        r["agent"] = r.get("agent") or r["belief"]
    told = sorted({r["agent"] for r in rows_all if "/told/" in r["agent"] and r["look"] in ("llm",)})
    if told:
        fig, ax = plt.subplots(figsize=(9, 5))
        cells = group(rows_all, ("agent", "day_index"), None)
        for i, ag in enumerate(told):
            nt = ag.replace("/told/", "/not_told/")
            c = color(ag)
            ax.plot(range(len(days)), [cells.get((ag, d), Cell()).acc_all for d in days], marker="o", lw=1.8, color=c, label=short(ag).replace("/told", "") + " told")
            ax.plot(range(len(days)), [cells.get((nt, d), Cell()).acc_all for d in days], marker="x", ls="--", lw=1.4, color=c, label=short(nt).replace("/not_told", "") + " not told")
        shade(ax); ax.set_xticks(range(len(days))); ax.set_xticklabels(labels); ax.grid(alpha=0.3); ax.legend(fontsize=7, ncol=2)
        ax.set_title("told vs not told, accuracy per day (LLM agents, look on, pooled households)")
        fig.tight_layout(); fig.savefig(a.out / "fig3_told_vs_not_told.png", dpi=130); plt.close(fig)

    # 4. abstain rate and answered accuracy per day at threshold 0.5 (look voi / llm)
    sub = [r for r in rows if r["look"] in ("voi", "llm")]
    if sub:
        agents = sorted({r["agent"] for r in sub})
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        for thr, ls in ((0.5, "-"), (None, ":")):
            cells = group(sub, ("agent", "day_index"), thr)
            for ag in agents:
                if thr is None and not ag.startswith("llm"):
                    continue
                if thr is None and "/not_told/" in ag:
                    continue      # the outright-ABSTAIN overlay once per memory (told arm) keeps the panel readable
                lab = label(ag) + ("" if thr else " · outright ABSTAIN only")
                axes[0].plot(range(len(days)), [cells.get((ag, d), Cell()).abstain_rate for d in days], marker="o", ms=4, lw=1.8, ls=(style(ag) if thr else "-."), color=color(ag), label=lab, alpha=1 if thr else .7)
                axes[1].plot(range(len(days)), [cells.get((ag, d), Cell()).acc_answered for d in days], marker="o", ms=4, lw=1.8, ls=(style(ag) if thr else "-."), color=color(ag), label=lab, alpha=1 if thr else .7)
        for ax, t in zip(axes, ("abstain rate per day (abstain when top probability < 0.5)\nLLM dashed = told, dotted = not told; dash-dot = the LLM's own ABSTAIN answers only", "accuracy among the questions actually answered")):
            shade(ax); ax.set_xticks(range(len(days))); ax.set_xticklabels(labels); ax.grid(alpha=0.3); ax.set_title(t, fontsize=10)
        axes[0].legend(fontsize=8, ncol=1, loc="center")
        fig.tight_layout(); fig.savefig(a.out / "fig4_abstain_per_day.png", dpi=130); plt.close(fig)
    print(f"wrote figures to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
