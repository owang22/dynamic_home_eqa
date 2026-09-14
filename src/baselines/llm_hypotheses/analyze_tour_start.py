"""Figures and tables for the tour-start + re-asking study.

Reads every arm under ``results/llm_hypotheses/tour_start/<household>/``
and writes, per the brief:

1. accuracy and log-loss over time, named vs anonymized, with the gap
   shown separately — 95% CI bands on every series;
2. effective sample size over time for the LLM arms (does the log-loss
   gain come from averaging over disagreeing hypotheses, or does the
   weight sit on one hypothesis at a time?);
3. when re-asking fired, and the mixture's sighting-prediction quality
   before and after each ask;
4. call counts and generation time;
5. per object, which hypothesis predicted it best, and how much a
   per-object oracle pick would have beaten the mixture;
6. the active-protocol table: policy fixed (myopic VoI, λ=0.05), random
   slice on/off, re-asking on/off.

Scoring everywhere is under ``ON_PERSON ≡ OUT_OF_HOUSE``; the active
harness's exact-match logs are rescored here from their distributions.
"""

from __future__ import annotations

import collections
import gzip
import json
import math
import pathlib
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from baselines.llm_hypotheses.run_tour_start import STUDY_DIR
from baselines.types import DAY_SECONDS

EPS = 1e-3
AWAY = {"ON_PERSON", "OUT_OF_HOUSE"}
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C = {"named": "#2a78d6", "anon": "#1baf7a", "periodic": "#eb6834",
     "mostfreq": "#e34948", "oracle": "#4a3aa7", "fixed": "#eda100",
     "gap": "#4a3aa7"}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF})


def canon(rec: str) -> str:
    return "OUT_OF_HOUSE" if rec in AWAY else rec


def score(row: Dict[str, Any]) -> Tuple[int, float]:
    """(top-1 correct, log-loss) under the merged rule."""
    dist: Dict[str, float] = collections.defaultdict(float)
    for k, v in row["dist"].items():
        dist[canon(k)] += v
    truth = canon(row["truth"])
    argmax = max(dist, key=dist.get) if dist else row["argmax"]
    return int(argmax == truth), -math.log(max(dist.get(truth, 0.0), EPS))


def load(household: str, study_dir: pathlib.Path = STUDY_DIR) -> Dict[str, Dict[str, Any]]:
    arms = {}
    root = study_dir / household
    arms_dir = root / "arms" if (root / "arms").is_dir() else root
    for d in sorted(arms_dir.iterdir()):
        if not (d / "diagnostics.json").exists() or d.name.endswith("_bug"):
            continue
        rows = [json.loads(l) for l in gzip.open(d / "per_question.jsonl.gz", "rt")]
        for r in rows:
            r["top1"], r["ll"] = score(r)
            r["day"] = r["t_query"] // DAY_SECONDS
        arms[d.name] = {"rows": rows,
                        "diag": json.loads((d / "diagnostics.json").read_text())}
    return arms


def daily(rows: Sequence[dict], key: str, win: int = 3):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["day"]].append(r[key])
    days = sorted(by); m, lo, hi = [], [], []
    for i, d in enumerate(days):
        pool = np.concatenate([by[days[j]] for j in
                               range(max(0, i - win // 2), min(len(days), i + win // 2 + 1))])
        mu = pool.mean(); n = len(pool)
        se = math.sqrt(mu * (1 - mu) / n) if key == "top1" else pool.std(ddof=1) / math.sqrt(n)
        m.append(mu); lo.append(mu - 1.96 * se); hi.append(mu + 1.96 * se)
    return days, np.array(m), np.array(lo), np.array(hi)


def paired_daily_gap(a: Sequence[dict], b: Sequence[dict], key: str, win: int = 3):
    """Per-day paired difference a−b over the same questions, with a
    bootstrap CI on each 3-day window."""
    qa = {r["question_id"]: r[key] for r in a}
    qb = {r["question_id"]: r[key] for r in b}
    day_of = {r["question_id"]: r["day"] for r in a}
    by = collections.defaultdict(list)
    for q in qa:
        if q in qb:
            by[day_of[q]].append(qa[q] - qb[q])
    days = sorted(by); rng = np.random.default_rng(0); m, lo, hi = [], [], []
    for i, d in enumerate(days):
        pool = np.concatenate([by[days[j]] for j in
                               range(max(0, i - win // 2), min(len(days), i + win // 2 + 1))])
        boots = [pool[rng.integers(0, len(pool), len(pool))].mean() for _ in range(500)]
        m.append(pool.mean()); lo.append(np.percentile(boots, 2.5)); hi.append(np.percentile(boots, 97.5))
    return days, np.array(m), np.array(lo), np.array(hi)


def overall(rows: Sequence[dict]) -> Dict[str, float]:
    if not rows:
        return {"n": 0, "top1": float("nan"), "top1_se": float("nan"), "ll": float("nan"), "ll_se": float("nan")}
    t = np.array([r["top1"] for r in rows]); l = np.array([r["ll"] for r in rows])
    return {"n": len(rows), "top1": t.mean(), "top1_se": math.sqrt(t.mean() * (1 - t.mean()) / len(t)),
            "ll": l.mean(), "ll_se": (l.std(ddof=1) / math.sqrt(len(l))) if len(l) > 1 else float("nan")}


def late_discovery(rows: Sequence[dict], diag: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Accuracy restricted to objects first sighted after day 0, and to the
    rest, reported separately: the random-time tour makes the two strata
    systematically different, so they are never averaged here."""
    late = set(diag.get("late_discovered_objects") or [])
    if not late and not any("late_discovered" in r for r in rows):
        return {}
    is_late = lambda r: r.get("late_discovered", r["object_id"] in late)
    return {"late": overall([r for r in rows if is_late(r)]),
            "tour_visible": overall([r for r in rows if not is_late(r)])}


def assumption_recovery(arms: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per graph arm: which ground-truth premises (from the bank's
    ``premises``) the FINAL graph carries a matching assumption value
    for. The rate over households is what the comparison reports; one
    run directory holds one household, so this returns one row per arm."""
    out = []
    for name, arm in sorted(arms.items()):
        d = arm["diag"]
        if not d.get("premises") or "assumption_recovery" not in d:
            continue
        rec = d["assumption_recovery"]
        out.append({"arm": name, "premises": d["premises"], "recovered": rec,
                    "rate": sum(1 for v in rec.values() if v) / max(1, len(rec))})
    return out


def paired(a: Sequence[dict], b: Sequence[dict], key: str) -> Tuple[float, float, float]:
    qa = {r["question_id"]: r[key] for r in a}; qb = {r["question_id"]: r[key] for r in b}
    d = np.array([qa[q] - qb[q] for q in qa if q in qb]); rng = np.random.default_rng(0)
    boots = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
    return d.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)


# ------------------------------------------------------------------ figures

def fig_named_vs_anonymized(arms, out: pathlib.Path) -> None:
    named = arms["passive__llm__tour_named"]["rows"]
    if "passive__llm__tour_anonymized" not in arms:
        return fig_named_only(arms, out)
    anon = arms["passive__llm__tour_anonymized"]["rows"]
    refs = {"MostFrequent 72h (no-LLM)": (arms["passive__mostfreq72"]["rows"], C["periodic"]),
            "Oracle (ceiling)": (arms["passive__oracle"]["rows"], C["oracle"])}
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.4))
    for row, (key, ylabel) in enumerate([("top1", "top-1 accuracy"), ("ll", "log-loss (lower is better)")]):
        ax = axes[row, 0]
        for label, rows, col in [("LLM tour-start named (re-asking)", named, C["named"]),
                                 ("LLM tour-start anonymized (re-asking)", anon, C["anon"])]:
            d, m, lo, hi = daily(rows, key)
            ax.fill_between(d, lo, hi, color=col, alpha=0.13, lw=0); ax.plot(d, m, color=col, lw=2, label=label)
        for label, (rows, col) in refs.items():
            d, m, lo, hi = daily(rows, key)
            ax.fill_between(d, lo, hi, color=col, alpha=0.10, lw=0); ax.plot(d, m, color=col, lw=1.6, label=label)
        ax.set_ylabel(ylabel); ax.set_title("named vs anonymized, passive protocol" if row == 0 else "", loc="left", color=INK, fontsize=10)
        ax = axes[row, 1]
        d, m, lo, hi = paired_daily_gap(named, anon, key)
        ax.fill_between(d, lo, hi, color=C["gap"], alpha=0.15, lw=0); ax.plot(d, m, color=C["gap"], lw=2)
        ax.axhline(0, color=INK2, lw=0.8)
        ax.set_ylabel(f"named − anonymized, {'top-1' if key == 'top1' else 'log-loss'}")
        if row == 0: ax.set_title("the gap (paired per question, 95% CI)", loc="left", color=INK, fontsize=10)
        ax = axes[row, 2]
        for label, rows, col, ls in [("named, re-asking", named, C["named"], "-"),
                                     ("named, fixed set", arms["passive__llm_fixed__tour_named"]["rows"], C["named"], (0, (4, 2))),
                                     ("anonymized, re-asking", anon, C["anon"], "-"),
                                     ("anonymized, fixed set", arms["passive__llm_fixed__tour_anonymized"]["rows"], C["anon"], (0, (4, 2)))]:
            d, m, lo, hi = daily(rows, key)
            if ls == "-": ax.fill_between(d, lo, hi, color=col, alpha=0.12, lw=0)
            ax.plot(d, m, color=col, lw=2, ls=ls, label=label)
        if row == 0: ax.set_title("re-asking vs fixed hypothesis set", loc="left", color=INK, fontsize=10)
        for ax in axes[row]:
            ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
            for e in (3, 7): ax.axvline(e - 0.5, color="#c9c8c2", lw=0.9, ls=(0, (2, 2)))
            ax.set_xticks([0, 3, 7, 14, 21, 27])
            if row == 1: ax.set_xlabel("episode day (d0 = Monday)")
    axes[0, 0].legend(loc="lower left", fontsize=7.5, frameon=False, ncol=1)
    axes[0, 2].legend(loc="lower left", fontsize=7.5, frameon=False)
    fig.suptitle("Tour start: hypotheses written from one walkthrough tour, revised on days 3 and 7 — hh_001, 3-day rolling mean, 95% CI bands",
                 x=0.01, ha="left", fontsize=12, color=INK, fontweight="bold")
    fig.text(0.01, 0.935, "Scoring: ON_PERSON ≡ OUT_OF_HOUSE. Dotted verticals: scheduled re-asks (day 3, day 7). Questions begin on day 3.", fontsize=9, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(out / "named_vs_anonymized_over_time.png", dpi=150); plt.close(fig)


def fig_named_only(arms, out: pathlib.Path) -> None:
    """The over-time figure for a household run in the named condition
    only: re-asking vs fixed set against the references."""
    named = arms["passive__llm__tour_named"]["rows"]
    fixed = arms["passive__llm_fixed__tour_named"]["rows"]
    refs = {"MostFrequent 72h (no-LLM)": (arms["passive__mostfreq72"]["rows"], C["periodic"]),
            "Oracle (ceiling)": (arms["passive__oracle"]["rows"], C["oracle"])}
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2))
    for row, (key, ylabel) in enumerate([("top1", "top-1 accuracy"), ("ll", "log-loss (lower is better)")]):
        ax = axes[row, 0]
        for lab, rows, col, ls in [("LLM tour-start, re-asking", named, C["named"], "-"),
                                   ("LLM tour-start, fixed set", fixed, C["named"], (0, (4, 2)))]:
            d, m, lo, hi = daily(rows, key)
            if ls == "-": ax.fill_between(d, lo, hi, color=col, alpha=0.13, lw=0)
            ax.plot(d, m, color=col, lw=2, ls=ls, label=lab)
        for lab, (rows, col) in refs.items():
            d, m, lo, hi = daily(rows, key)
            ax.fill_between(d, lo, hi, color=col, alpha=0.10, lw=0); ax.plot(d, m, color=col, lw=1.6, label=lab)
        ax.set_ylabel(ylabel)
        if row == 0: ax.set_title("re-asking vs fixed set, passive protocol", loc="left", color=INK, fontsize=10)
        ax = axes[row, 1]
        d, m, lo, hi = paired_daily_gap(named, fixed, key)
        ax.fill_between(d, lo, hi, color=C["gap"], alpha=0.15, lw=0); ax.plot(d, m, color=C["gap"], lw=2); ax.axhline(0, color=INK2, lw=0.8)
        ax.set_ylabel(f"re-asking − fixed, {'top-1' if key == 'top1' else 'log-loss'}")
        if row == 0: ax.set_title("the gap (paired per question, 95% CI)", loc="left", color=INK, fontsize=10)
        for a in axes[row]:
            a.grid(axis="y", color=GRID, lw=0.8); a.set_axisbelow(True)
            for e in (3, 7): a.axvline(e - 0.5, color="#c9c8c2", lw=0.9, ls=(0, (2, 2)))
            a.set_xticks([0, 3, 7, 14, 21, 27])
            if row == 1: a.set_xlabel("episode day (d0 = Monday)")
    axes[0, 0].legend(loc="lower left", fontsize=7.5, frameon=False)
    fig.suptitle("Tour start with re-asking (days 3, 7) vs the fixed set — 3-day rolling mean, 95% CI bands", x=0.01, ha="left", fontsize=12, color=INK, fontweight="bold")
    fig.text(0.01, 0.935, "Scoring: ON_PERSON ≡ OUT_OF_HOUSE. Dotted verticals: scheduled re-asks. Questions begin on day 3.", fontsize=9, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(out / "named_vs_anonymized_over_time.png", dpi=150); plt.close(fig)


def fig_ess_and_reasks(arms, out: pathlib.Path) -> None:
    llm = [(k, v) for k, v in arms.items() if "__llm__" in k]
    fig, axes = plt.subplots(2, len(llm), figsize=(4.2 * len(llm), 6.6), sharex=True, squeeze=False)
    for col, (name, arm) in enumerate(llm):
        diag = arm["diag"]; ess = np.array(diag["ess_history"]); days = ess[:, 0] / DAY_SECONDS
        ax = axes[0, col]
        ax.plot(days, ess[:, 1], color=C["named"] if "named" in name else C["anon"], lw=1.2)
        ax.set_ylim(0.9, 6.2); ax.axhline(1.0, color=INK2, lw=0.6, ls=(0, (2, 2)))
        ax.set_title(name.replace("__", " · "), loc="left", fontsize=9, color=INK)
        if col == 0: ax.set_ylabel("effective sample size\n(6 particles: 5 LLM + 1 stat)")
        q = diag["reask"]["sighting_quality"]; qt = np.array([r["t"] for r in q]) / DAY_SECONDS
        qp = np.array([math.log(max(r["p"], 1e-6)) for r in q])
        win = 40; roll = np.convolve(qp, np.ones(win) / win, mode="valid")
        ax = axes[1, col]
        ax.plot(qt[win - 1:], roll, color=INK, lw=1.2)
        ax.axhline(diag["reask"]["config"]["threshold"], color=C["mostfreq"], lw=0.9, ls=(0, (3, 2)))
        ax.text(27, diag["reask"]["config"]["threshold"], " trigger", color=C["mostfreq"], va="center", fontsize=7.5)
        for e in diag["reask"]["events"]:
            ax.axvline(e["t"] / DAY_SECONDS, color=C["periodic"] if e["changed"] else "#b5b5b5", lw=1.4)
            ax.text(e["t"] / DAY_SECONDS, ax.get_ylim()[1] if False else -0.15,
                    ("revised" if e["changed"] else "kept") + f"\n{e['reason'].split()[0]}",
                    fontsize=7, color=C["periodic"] if e["changed"] else "#7a7a7a", ha="center", va="top")
        ax.set_ylim(-4.5, 0)
        if col == 0: ax.set_ylabel("mixture sighting quality\nmean log p(sighting), 40-sighting window")
        ax.set_xlabel("episode day"); ax.set_xticks([0, 3, 7, 14, 21, 27])
        for a in (axes[0, col], axes[1, col]): a.grid(axis="y", color=GRID, lw=0.8); a.set_axisbelow(True)
    fig.suptitle("Effective sample size over time, and when re-asking fired (orange = set revised, grey = call returned nothing usable)",
                 x=0.01, ha="left", fontsize=11.5, color=INK, fontweight="bold")
    fig.text(0.01, 0.93, "No error bars: both series are deterministic functions of the fixed evidence stream. The quality trigger never fired — the running mean stayed above the threshold in every arm; only the scheduled asks ran.", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.91)); fig.savefig(out / "ess_and_reasks.png", dpi=150); plt.close(fig)


def per_object_oracle(arms, name: str) -> Dict[str, Any]:
    """Per object: log-loss of each particle vs the mixture; the
    per-object oracle picks the best particle per object in hindsight."""
    rows = arms[name]["rows"]
    by_obj = collections.defaultdict(list)
    for r in rows:
        if r.get("particles"): by_obj[r["object_id"]].append(r)
    table = []; mix_total = 0.0; oracle_total = 0.0; n_total = 0
    for obj, qs in sorted(by_obj.items()):
        names = list(qs[0]["particles"]); truth = [canon(r["truth"]) for r in qs]
        part_ll = {}
        for pn in names:
            lls = []
            for r, tr in zip(qs, truth):
                if pn not in r["particles"]: continue
                d = collections.defaultdict(float)
                for k, v in r["particles"][pn].items(): d[canon(k)] += v
                lls.append(-math.log(max(d.get(tr, 0.0), EPS)))
            part_ll[pn] = float(np.mean(lls)) if lls else float("nan")
        mix_ll = float(np.mean([r["ll"] for r in qs]))
        best = min(part_ll, key=part_ll.get)
        table.append({"object": obj, "n": len(qs), "mixture_ll": mix_ll,
                      "best_particle": ("hyp" + best.split("(")[1].rstrip(")")[1:] if best.startswith("HypothesisProgram") else "stat"),
                      "best_ll": part_ll[best], "gain_if_oracle_pick": mix_ll - part_ll[best]})
        mix_total += mix_ll * len(qs); oracle_total += part_ll[best] * len(qs); n_total += len(qs)
    winners = collections.Counter(t["best_particle"] for t in table)
    return {"arm": name, "objects": table, "mixture_ll": mix_total / n_total,
            "per_object_oracle_ll": oracle_total / n_total,
            "oracle_gain_nats": (mix_total - oracle_total) / n_total,
            "best_particle_counts": dict(winners)}


def fig_per_object(report: Dict[str, Any], out: pathlib.Path) -> None:
    objs = sorted(report["objects"], key=lambda t: -t["gain_if_oracle_pick"])
    fig, ax = plt.subplots(figsize=(11, 0.28 * len(objs) + 1.6))
    y = np.arange(len(objs))
    ax.barh(y, [t["gain_if_oracle_pick"] for t in objs], color=C["named"], height=0.62)
    ax.set_yticks(y); ax.set_yticklabels([f"{t['object']}  ← {t['best_particle']}" for t in objs], fontsize=7.5)
    ax.invert_yaxis(); ax.set_xlabel("log-loss saved by picking that object's best hypothesis in hindsight (nats/question)")
    ax.axvline(0, color=INK2, lw=0.8); ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    winners = ", ".join(f"{k}×{v}" for k, v in
                        sorted(report["best_particle_counts"].items(), key=lambda kv: -kv[1]))
    ax.set_title(f"Per-object best hypothesis, and what a per-object oracle pick would save — "
                 f"{report['arm'].replace('__', ' · ')}\n"
                 f"mixture {report['mixture_ll']:.3f} → oracle pick {report['per_object_oracle_ll']:.3f} nats/question "
                 f"(gain {report['oracle_gain_nats']:.3f})   best particle per object: {winners}\n"
                 f"negative bars: the mixture beat every single particle on that object",
                 loc="left", fontsize=9, color=INK)
    fig.tight_layout(); fig.savefig(out / f"per_object_oracle__{report['arm']}.png", dpi=150); plt.close(fig)


def write_tables(arms, out: pathlib.Path) -> str:
    lines = ["# Tour start + re-asking — hh_001", "", "Scoring: ON_PERSON ≡ OUT_OF_HOUSE. ± is one standard error.", ""]
    lines += ["## Passive protocol (fixed patrol, no policy)", "", "| arm | n | top-1 | log-loss |", "|---|---|---|---|"]
    for k in sorted(arms):
        if not k.startswith("passive"): continue
        o = overall(arms[k]["rows"])
        lines.append(f"| {k.replace('passive__', '').replace('__', ' · ')} | {o['n']} | {o['top1']:.3f} ± {o['top1_se']:.3f} | {o['ll']:.3f} ± {o['ll_se']:.3f} |")
    lines += ["", "## Late-discovery accuracy (objects first sighted after day 0, apart from the tour-visible stratum)", "", "| arm | late n | late top-1 | late log-loss | tour-visible n | tour-visible top-1 |", "|---|---|---|---|---|---|"]
    for k in sorted(arms):
        strata = late_discovery(arms[k]["rows"], arms[k]["diag"])
        if not strata: continue
        a, b = strata["late"], strata["tour_visible"]
        lines.append(f"| {k.replace('__', ' · ')} | {a['n']} | {a['top1']:.3f} ± {a['top1_se']:.3f} | {a['ll']:.3f} ± {a['ll_se']:.3f} | {b['n']} | {b['top1']:.3f} ± {b['top1_se']:.3f} |")
    recovery = assumption_recovery(arms)
    if recovery:
        lines += ["", "## Assumption recovery (final graph holds a value matching the bank's ground-truth premise)", "", "| arm | premises | matched | rate |", "|---|---|---|---|"]
        for row in recovery:
            lines.append(f"| {row['arm'].replace('__', ' · ')} | {row['premises']} | {row['recovered']} | {row['rate']:.2f} |")
        (out / "assumption_recovery.json").write_text(json.dumps(recovery, indent=1))
    lines += ["", "## Active protocol (myopic VoI λ=0.05, random slice f)", "", "| arm | top-1 (answer) | log-loss (belief at answer time, after that question's senses) | senses/day | random senses |", "|---|---|---|---|---|"]
    for k in sorted(arms):
        if not k.startswith("active"): continue
        rows = arms[k]["rows"]; o = overall(rows); d = arms[k]["diag"]
        spd = sum(r.get("n_senses", 0) for r in rows) / 28
        lines.append(f"| {k.replace('active__', '').replace('__', ' · ')} | {o['top1']:.3f} ± {o['top1_se']:.3f} | {o['ll']:.3f} ± {o['ll_se']:.3f} | {spd:.1f} | {d.get('random_senses')} |")
    lines += ["", "## Paired comparisons (A − B over the same questions, 95% bootstrap CI)", "", "| comparison | top-1 | log-loss |", "|---|---|---|"]
    pairs = [("passive__llm__tour_named", "passive__llm__tour_anonymized", "named − anonymized (re-asking)"),
             ("passive__llm_fixed__tour_named", "passive__llm_fixed__tour_anonymized", "named − anonymized (fixed set)"),
             ("passive__llm__tour_named", "passive__llm_fixed__tour_named", "re-asking − fixed (named)"),
             ("passive__llm__tour_anonymized", "passive__llm_fixed__tour_anonymized", "re-asking − fixed (anonymized)"),
             ("passive__llm__tour_named", "passive__mostfreq72", "LLM named − MostFreq72 (no-LLM)"),
             ("passive__llm__tour_named", "passive__mostfreq", "LLM named − MostFreq"),
             ("active__llm__tour_named__f0.1", "active__llm__tour_named__f0", "random slice 0.1 − 0 (re-asking)"),
             ("active__llm_fixed__tour_named__f0.1", "active__llm_fixed__tour_named__f0", "random slice 0.1 − 0 (fixed set)"),
             ("active__mostfreq72__f0.1", "active__mostfreq72__f0", "random slice 0.1 − 0 (MostFreq72)"),
             ("active__llm__tour_named__f0", "active__mostfreq72__f0", "LLM named − MostFreq72 (active, f0)")]
    for a, b, label in pairs:
        if a not in arms or b not in arms: continue
        t = paired(arms[a]["rows"], arms[b]["rows"], "top1"); l = paired(arms[a]["rows"], arms[b]["rows"], "ll")
        star = lambda x: "*" if (x[1] > 0 or x[2] < 0) else ""
        lines.append(f"| {label} | {t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]{star(t)} | {l[0]:+.3f} [{l[1]:+.3f}, {l[2]:+.3f}]{star(l)} |")
    lines += ["", "## Re-asking: calls, timing, outcome", "", "| arm | re-asks | live LLM calls | generation s | events |", "|---|---|---|---|---|"]
    for k, arm in sorted(arms.items()):
        d = arm["diag"]
        if "reask" not in d: continue
        ev = "; ".join(f"d{e['day']} {e.get('trigger', e['reason'].split()[0])} → {'revised' if e['changed'] else 'kept'}" for e in d["reask"]["events"])
        llm = d.get("llm", {})
        lines.append(f"| {k.replace('__', ' · ')} | {d['reask']['calls_made']} | {llm.get('live_calls')} | {llm.get('live_generation_seconds')} | {ev} |")
    graph_rows = [(k, a["diag"]["graph"]) for k, a in sorted(arms.items()) if a["diag"].get("graph", {}).get("is_graph")]
    if graph_rows:
        lines += ["", "## Graph arm: leaves, edits, prunes, births", "", "| arm | leaves by day (first → last) | edits | prunes | born / skipped | final assumptions |", "|---|---|---|---|---|---|"]
        for k, g in graph_rows:
            counts = list(g["leaf_count_trace"].values())
            born = sum(1 for b in g["birth_log"] if b.get("kind") == "born"); skipped = len(g["birth_log"]) - born
            final = g.get("final_graph") or {}
            lines.append(f"| {k.replace('__', ' · ')} | {counts[0] if counts else '-'} → {counts[-1] if counts else '-'} | {len(g['edit_log'])} | {len(g['prune_log'])} | {born} / {skipped} | {', '.join(final.get('assumptions', {}))} |")
    cost_path = STUDY_DIR.parent / "generation_cost_tour.json"
    if cost_path.exists():
        cost = json.loads(cost_path.read_text())
        lines += ["", "Tour-start elicitation (last elicit run): " + "; ".join(f"{r['household']} {r['condition']} {r['generation_seconds']:.0f}s, {r['completion_tokens']} tokens, {r['seconds_per_hypothesis']}s/hypothesis" for r in cost["rows"]), ""]
    text = "\n".join(lines) + "\n"
    (out / "tables.md").write_text(text)
    return text


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--household", default="hh_001__bank0",
                    help="run directory name under --study-dir (household__bank<seed>)")
    ap.add_argument("--study-dir", type=pathlib.Path, default=STUDY_DIR / "tl0")
    args = ap.parse_args()
    arms = load(args.household, args.study_dir); out = args.study_dir / args.household / "figures"; out.mkdir(exist_ok=True)
    fig_named_vs_anonymized(arms, out); fig_ess_and_reasks(arms, out)
    reports = []
    for name in ("passive__llm__tour_named", "passive__llm__tour_anonymized", "passive__llm_fixed__tour_named", "passive__llm_fixed__tour_anonymized"):
        if name in arms:
            rep = per_object_oracle(arms, name); reports.append(rep); fig_per_object(rep, out)
    (out / "per_object_oracle.json").write_text(json.dumps(reports, indent=1))
    text = write_tables(arms, out)
    text += "\n## Per-object oracle gap\n\n| arm | mixture log-loss | per-object oracle | gain | best-particle counts |\n|---|---|---|---|---|\n"
    for rep in reports:
        text += f"| {rep['arm'].replace('__', ' · ')} | {rep['mixture_ll']:.3f} | {rep['per_object_oracle_ll']:.3f} | {rep['oracle_gain_nats']:.3f} | {rep['best_particle_counts']} |\n"
    (out / "tables.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
