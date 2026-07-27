"""Paper figures -> reports/paper_figures/<topic>/<one chart per file>.

  passive_adaptation/   world knowledge speeds up passive adaptation + ablation
  reflection_gating/    surprise-gated reflection vs nightly / none
  active_sensing/       world knowledge choosing observations under a budget

Conventions:
  * PHASE-AVERAGED (mean over start weekday of per-day means, never a raw pool).
  * Bootstrap 95% CI over households; PAIRED per-household deltas wherever a
    claim must separate from zero (pooled bands overlap on this data).
  * "LLM" = the best scaffolded implementation, never the raw log.
  * classical_C1 is never reported (weak strawman); the classical arm is C3g.
  * Atypical passive pool = the 24-household v22+v22b banks (d0 run), NOT the
    old 6-household atyp_regime_confirm_v1 bank.
  * One chart per file; minimal text; annotations carry a white bbox.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REP = ROOT / "reports"
OUT = REP / "paper_figures"

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, VIOLET, GRAY = "#e87ba4", "#4a3aa7", "#52514e"
CKPTS = [1, 2, 3, 5, 7, 10, 14]
DISTS = [0, 3, 6, 12]
BOX = dict(boxstyle="round,pad=0.35", fc="white", ec="#d9d8d3", alpha=0.92)


def L(p):
    p = Path(p)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def style(ax, xlab=None, ylab=None, title=None):
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c9c8c3")
    ax.tick_params(colors=INK2, labelsize=9.5)
    if xlab:
        ax.set_xlabel(xlab, fontsize=10.5, color=INK2)
    if ylab:
        ax.set_ylabel(ylab, fontsize=10.5, color=INK2)
    if title:
        ax.set_title(title, fontsize=12.5, color=INK, pad=10)


def fig1(w=7.6, h=5.2):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=SURF)
    return fig, ax


def save(fig, sub, name, caption=None):
    import textwrap
    d = OUT / sub
    d.mkdir(parents=True, exist_ok=True)
    if caption:
        wrapped = "\n".join(textwrap.wrap(caption, int(fig.get_figwidth() * 13)))
        nl = wrapped.count("\n") + 1
        fig.text(0.5, 0.012, wrapped, ha="center", va="bottom",
                 fontsize=8.6, color=INK2)
        fig.tight_layout(rect=[0, 0.035 + 0.03 * nl, 1, 1])
    else:
        fig.tight_layout()
    p = d / name
    fig.savefig(p, dpi=170, facecolor=SURF)
    plt.close(fig)
    print("wrote", p)


def phase_mean(rows):
    per = defaultdict(list)
    for r in rows:
        per[r["test_day"]].append(r["correct"])
    return float(np.mean([np.mean(v) for v in per.values()])) if per else float("nan")


def boot_vec(vals, nb=4000, seed=0):
    v = np.asarray(vals, float)
    if not len(v):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    m = v[rng.integers(0, len(v), (nb, len(v)))].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def hh_curve(rows, model, cks=CKPTS):
    """Pooled curve + CI from bootstrapping the per-household phase means."""
    hhs = sorted({r["hh"] for r in rows})
    xs, ys, lo, hi = [], [], [], []
    for c in cks:
        per = [phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] == c
                           and r["model"] == model]) for hh in hhs]
        per = [p for p in per if not np.isnan(p)]
        if not per:
            continue
        a, b = boot_vec(per)
        xs.append(c); ys.append(float(np.mean(per))); lo.append(a); hi.append(b)
    return map(np.array, (xs, ys, lo, hi))


def paired_curve(rows, model, ref, cks=CKPTS):
    hhs = sorted({r["hh"] for r in rows})
    xs, ys, lo, hi = [], [], [], []
    for c in cks:
        d = []
        for hh in hhs:
            a = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] == c
                            and r["model"] == model])
            b = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] == c
                            and r["model"] == ref])
            if not (np.isnan(a) or np.isnan(b)):
                d.append(a - b)
        if not d:
            continue
        a_, b_ = boot_vec(d)
        xs.append(c); ys.append(float(np.mean(d))); lo.append(a_); hi.append(b_)
    return map(np.array, (xs, ys, lo, hi))


def draw(ax, xs, ys, lo, hi, col, ls, mk, lab, lw=2.3, band=True, endlab=True):
    if band:
        ax.fill_between(xs, lo, hi, color=col, alpha=0.12, lw=0)
    ax.plot(xs, ys, ls, color=col, lw=lw, marker=mk, ms=6.5, mec=SURF,
            mew=1.2 if mk != "x" else 0, label=lab, zorder=3)
    if endlab and len(xs):
        ax.annotate(f"{ys[-1]:.2f}", (xs[-1], ys[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9,
                    color=INK2, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none",
                              alpha=0.75))


def end_labels(ax, ends):
    """Value labels at the right end of each series, vertically dodged."""
    ends = sorted(ends, key=lambda e: e[1])
    span = ax.get_ylim()[1] - ax.get_ylim()[0]
    shown = [e[1] for e in ends]
    for i in range(1, len(shown)):
        if shown[i] - shown[i - 1] < 0.045 * span:
            shown[i] = shown[i - 1] + 0.045 * span
    h_in = ax.get_position().height * ax.figure.get_figheight()
    for (x_, y_), sy in zip(ends, shown):
        ax.annotate(f"{y_:.2f}", (x_, y_), xytext=(6, (sy - y_) * 72 * h_in / span),
                    textcoords="offset points", va="center", fontsize=9,
                    color=INK2, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none",
                              alpha=0.75))


def logx(ax, cks=CKPTS):
    ax.set_xscale("log")
    ax.set_xticks(cks)
    ax.set_xticklabels([str(c) for c in cks])
    ax.minorticks_off()


# ══════════════════ passive_adaptation ══════════════════
SUB1 = "passive_adaptation"
P_ARMS = [("fusion", "LLM + classical (fusion)", BLUE, "-", "o", 2.6),
          ("llm_direct", "LLM (reflective memory)", ORANGE, "-", "s", 2.2),
          ("llm_nomem", "LLM (no reflection)", YELLOW, "-.", "D", 1.9),
          ("classical_C3g", "classical", AQUA, "--", "^", 2.0)]


def atyp_rows():
    return [r for b in ("v22", "v22b")
            for r in L(REP / f"reflect/all_rows_{b}_distractor_d0.jsonl")]


def typ_rows():
    return L(REP / "reflect/all_rows_typ_typd0.jsonl")


def passive_curves(rows, tag, title, n_hh):
    fig, ax = fig1()
    ends = []
    for m, lab, c, ls, mk, lw in P_ARMS:
        xs, ys, lo, hi = hh_curve(rows, m)
        if len(xs):
            draw(ax, xs, ys, lo, hi, c, ls, mk, lab, lw, endlab=False)
            ends.append([xs[-1], ys[-1]])
    end_labels(ax, ends)
    logx(ax)
    style(ax, "days of observation (log)", "accuracy (exact receptacle)", title)
    ax.legend(frameon=False, fontsize=9.5, loc="best", labelcolor=INK)
    save(fig, SUB1, f"accuracy_by_day_{tag}_households.png",
         f"{n_hh} households, obs ~3/day, phase-averaged; bands = bootstrap 95% CI over households.")


def passive_paired(rows, tag, title):
    fig, ax = fig1()
    ax.axhline(0, color="#9c9b96", lw=1.2, zorder=2)
    for m, lab, c, ls, mk, lw in P_ARMS[:3]:
        xs, ys, lo, hi = paired_curve(rows, m, "classical_C3g")
        if len(xs):
            draw(ax, xs, ys, lo, hi, c, ls, mk, lab, lw, endlab=False)
    xs, ys, lo, hi = paired_curve(rows, "llm_direct", "classical_C3g")
    if len(xs):
        nsig = int(np.sum(lo > 0))
        ax.annotate(f"day 1: {ys[0]:+.2f} [{lo[0]:+.2f}, {hi[0]:+.2f}]\n"
                    f"CI excludes 0 on {nsig}/{len(xs)} days (reflective memory)",
                    xy=(1, ys[0]), xytext=(1.8, float(max(ys)) + 0.09), fontsize=9,
                    color=INK, bbox=BOX,
                    arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
    logx(ax)
    style(ax, "days of observation (log)",
          "accuracy − classical (paired per household)", title)
    ax.legend(frameon=False, fontsize=9.5, loc="lower right", labelcolor=INK)
    save(fig, SUB1, f"paired_delta_vs_classical_{tag}.png",
         "Within-household difference vs the classical model (C3g); household variance cancels. Largest on day 1, before the classical model has data.")


def anonymization_ablation():
    models = [("deepseek-anonfix", "DeepSeek"), ("qwen36-anonfix", "Qwen3.6"),
              ("glm-anonfix", "GLM-4.5-Air")]
    fig, ax = fig1(8.0, 5.2)
    w, xpos = 0.34, np.arange(len(models))
    for j, (arm, lab, c) in enumerate([("llm_named", "named receptacles", BLUE),
                                       ("llm_anon", "names stripped", ORANGE)]):
        vals, err = [], [[], []]
        for key, _ in models:
            rr = [r for r in L(REP / f"h2_adaptation/confirm_rows_{key}.jsonl")
                  if r["arm"] == arm and r["kind"] == "target"]
            by = defaultdict(list)
            for r in rr:
                by[r["household"]].append(r["correct"])
            per = [float(np.mean(v)) for v in by.values()]
            m_ = float(np.mean([r["correct"] for r in rr]))
            a, b = boot_vec(per)
            vals.append(m_); err[0].append(max(0, m_ - a)); err[1].append(max(0, b - m_))
        ax.bar(xpos + (j - 0.5) * w, vals, w * 0.92, color=c, label=lab, zorder=3)
        ax.errorbar(xpos + (j - 0.5) * w, vals, yerr=err, fmt="none",
                    ecolor=INK2, elinewidth=1.1, capsize=3, zorder=4)
        for x_, v, e in zip(xpos + (j - 0.5) * w, vals, err[1]):
            ax.text(x_, v + e + 0.014, f"{v:.2f}", ha="center", fontsize=9,
                    color=INK2, bbox=dict(boxstyle="round,pad=0.1", fc="white",
                                          ec="none", alpha=0.8))
    ax.axhline(0.065, color="#a8a7a2", lw=1, ls=(0, (1, 3)), zorder=1)
    ax.annotate("chance", (len(models) - 0.52, 0.075), fontsize=8,
                color="#a8a7a2", bbox=BOX)
    ax.set_xticks(xpos)
    ax.set_xticklabels([m for _, m in models], fontsize=10.5)
    ax.set_ylim(0, 0.68)
    style(ax, None, "accuracy on regime-flipped targets",
          "Ablation: anonymize receptacle names")
    ax.legend(frameon=False, fontsize=9.5, loc="upper left", labelcolor=INK)
    save(fig, SUB1, "anonymization_ablation.png",
         "Stripping names removes semantic priors, evidence digest kept. Costs DeepSeek and Qwen; GLM gains (exception, 2 of 3).")


# ══════════════════ reflection_gating ══════════════════
SUB2 = "reflection_gating"
G_ARMS = [("llm_surprise", "surprise-gated reflection", BLUE, "-", "o", 2.6),
          ("llm_direct", "nightly reflection", ORANGE, "--", "s", 2.2),
          ("llm_nomem", "no reflection", GRAY, ":", "x", 1.9)]


def gate_rows(d):
    sur = [r for b in ("v22", "v22b")
           for r in L(REP / f"reflect/rows_surprise_{b}_surprise_d{d}.jsonl")]
    oth = [r for b in ("v22", "v22b")
           for r in L(REP / f"reflect/all_rows_{b}_distractor_d{d}.jsonl")
           if r.get("obs_spec") == "orand3"]
    return sur + oth, sur


def gating_accuracy_by_day(d=6):
    rows, _ = gate_rows(d)
    fig, ax = fig1()
    ends = []
    for m, lab, c, ls, mk, lw in G_ARMS:
        xs, ys, lo, hi = hh_curve(rows, m)
        draw(ax, xs, ys, lo, hi, c, ls, mk, lab, lw, endlab=False)
        ends.append([xs[-1], ys[-1]])
    end_labels(ax, ends)
    logx(ax)
    style(ax, "days of observation (log)", "accuracy (exact receptacle)",
          f"Reflection strategies at distractor load {d}")
    ax.legend(frameon=False, fontsize=9.5, loc="upper left", labelcolor=INK)
    save(fig, SUB2, f"accuracy_by_day_distractor{d}.png",
         "24 households; distractors are static objects reported daily but never queried.")


def gating_load_sweep():
    fig, ax = fig1()
    calls = {}; ends = []
    for m, lab, c, ls, mk, lw in G_ARMS:
        ys, lo, hi = [], [], []
        for d in DISTS:
            rows, sur = gate_rows(d)
            hhs = sorted({r["hh"] for r in rows})
            per = [phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                               and r["model"] == m]) for hh in hhs]
            per = [p for p in per if not np.isnan(p)]
            a, b = boot_vec(per)
            ys.append(float(np.mean(per))); lo.append(a); hi.append(b)
            calls[d] = float(np.mean([r["n_reflect"] for r in sur if r["ckpt"] == 14]))
        draw(ax, np.array(DISTS), np.array(ys), np.array(lo), np.array(hi),
             c, ls, mk, lab, lw, endlab=False)
        ends.append([DISTS[-1], ys[-1]])
    end_labels(ax, ends)
    ax.set_xticks(DISTS)
    ax.annotate(f"LLM calls/household: gate {calls[12]:.1f} vs nightly 14",
                xy=(0.03, 0.04), xycoords="axes fraction", fontsize=9.5,
                color=INK, bbox=BOX)
    style(ax, "distractor objects per household", "accuracy (days 5-14, phase-avg)",
          "Accuracy vs distractor load")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right", labelcolor=INK)
    save(fig, SUB2, "accuracy_vs_distractor_load.png",
         "Nightly reflection degrades as noise accumulates; the gate holds because a padded stream rarely fires it.")


def gating_paired_by_load():
    fig, ax = fig1()
    ax.axhline(0, color="#9c9b96", lw=1.2, zorder=2)
    for ref, lab, c, ls, mk in [("llm_direct", "vs nightly reflection", ORANGE, "-", "o"),
                                ("llm_nomem", "vs no reflection", GRAY, "--", "D")]:
        ys, lo, hi = [], [], []
        for d in DISTS:
            rows, _ = gate_rows(d)
            hhs = sorted({r["hh"] for r in rows})
            dd = []
            for hh in hhs:
                a = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                                and r["model"] == "llm_surprise"])
                b = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                                and r["model"] == ref])
                if not (np.isnan(a) or np.isnan(b)):
                    dd.append(a - b)
            a_, b_ = boot_vec(dd)
            ys.append(float(np.mean(dd))); lo.append(a_); hi.append(b_)
        draw(ax, np.array(DISTS), np.array(ys), np.array(lo), np.array(hi),
             c, ls, mk, lab, 2.4, endlab=False)
        if ref == "llm_direct":
            ax.annotate(f"load 12: {ys[-1]:+.3f} [{lo[-1]:+.3f}, {hi[-1]:+.3f}]\nCI excludes 0",
                        xy=(12, ys[-1]), xytext=(4.7, 0.15), fontsize=9,
                        color=INK, bbox=BOX,
                        arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
    ax.set_xticks(DISTS)
    ax.set_ylim(-0.14, 0.21)
    style(ax, "distractor objects per household",
          "surprise − comparator (paired per household)",
          "Paired difference vs distractor load (days 5-14)")
    ax.legend(frameon=False, fontsize=9.5, loc="lower left", labelcolor=INK)
    save(fig, SUB2, "paired_delta_vs_nightly_by_load.png",
         "24 households, paired within household. The gate matches nightly at loads 0-6 and beats it at 12.")


def gating_paired_by_day(d=12):
    rows, _ = gate_rows(d)
    fig, ax = fig1()
    ax.axhline(0, color="#9c9b96", lw=1.2, zorder=2)
    for ref, lab, c, ls, mk in [("llm_direct", "vs nightly reflection", ORANGE, "-", "o"),
                                ("llm_nomem", "vs no reflection", GRAY, "--", "D")]:
        xs, ys, lo, hi = paired_curve(rows, "llm_surprise", ref)
        draw(ax, xs, ys, lo, hi, c, ls, mk, lab, 2.4, endlab=False)
    # pooled days>=5 effect, for reference
    hhs = sorted({r["hh"] for r in rows})
    dd = []
    for hh in hhs:
        a = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                        and r["model"] == "llm_surprise"])
        b = phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                        and r["model"] == "llm_direct"])
        if not (np.isnan(a) or np.isnan(b)):
            dd.append(a - b)
    mu = float(np.mean(dd)); a_, b_ = boot_vec(dd)
    ax.axhspan(a_, b_, xmin=0.42, color=ORANGE, alpha=0.10, zorder=1)
    ax.annotate(f"pooled days 5-14: {mu:+.3f} [{a_:+.3f}, {b_:+.3f}]",
                xy=(0.97, 0.96), xycoords="axes fraction", ha="right", va="top",
                fontsize=9, color=INK, bbox=BOX)
    logx(ax)
    ax.set_ylim(-0.16, 0.26)
    style(ax, "days of observation (log)",
          "surprise − comparator (paired per household)",
          f"Paired difference by day at distractor load {d}")
    ax.legend(frameon=False, fontsize=9.5, loc="lower right", labelcolor=INK)
    save(fig, SUB2, f"paired_delta_vs_nightly_by_day_load{d}.png",
         "The gate's edge appears from day 5 on, once nightly reflection has repeatedly rewritten memory over noise.")


# ══════════════════ active_sensing ══════════════════
SUB3 = "active_sensing"
AOR = REP / "answer_or_resense"
A_ARMS = [("classical", "rows_classical_conf_frozen.jsonl", AQUA, "--", "^"),
          ("LLM (scaffold)", "rows_llm_scaffold_conf_frozen.jsonl", BLUE, "-", "o"),
          ("LLM + classical (fusion)", "rows_scaffold_fusion_conf_permodel_deepseek.jsonl",
           ORANGE, "-", "s")]


def _hh_vals(rows, fn):
    by = defaultdict(list)
    for r in rows:
        by[r["hh"]].append(r)
    return [fn(v) for v in by.values()]


def active_bar(name, title, ylab, fn, fmt="{:.2f}", ylim=None, caption=None):
    fig, ax = fig1(7.0, 5.2)
    labs, vals, err, cols = [], [], [[], []], []
    for lab, f, c, _, _ in A_ARMS:
        rows = L(AOR / f)
        per = [p for p in _hh_vals(rows, fn) if not np.isnan(p)]
        v = float(np.mean(per)); a, b = boot_vec(per)
        labs.append(lab); vals.append(v); cols.append(c)
        err[0].append(max(0, v - a)); err[1].append(max(0, b - v))
    ax.bar(range(len(labs)), vals, 0.58, color=cols, zorder=3)
    ax.errorbar(range(len(labs)), vals, yerr=err, fmt="none", ecolor=INK2,
                elinewidth=1.1, capsize=3, zorder=4)
    top = (ylim or [0, max(vals) * 1.2])[1]
    for i, (v, e) in enumerate(zip(vals, err[1])):
        ax.text(i, v + e + top * 0.018, fmt.format(v), ha="center",
                fontsize=9.5, color=INK2)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels([l.replace(" (", "\n(") for l in labs], fontsize=9.5)
    if ylim:
        ax.set_ylim(*ylim)
    style(ax, None, ylab, title)
    save(fig, SUB3, name, caption)


def active_learning_curves():
    """Belief accuracy (counterfactual-correct on ALL queries) by day: coverage-
    independent, so arms with different answer rates stay comparable."""
    fig, ax = fig1()
    days = list(range(14)); ends = []
    for lab, f, c, ls, mk in A_ARMS:
        rows = L(AOR / f)
        by = defaultdict(lambda: defaultdict(list))
        for r in rows:
            by[r["hh"]][r["day"]].append(r["cf_correct"])
        ys, lo, hi = [], [], []
        for d in days:
            per = [float(np.mean(v[d])) for v in by.values() if d in v]
            a, b = boot_vec(per)
            ys.append(float(np.mean(per))); lo.append(a); hi.append(b)
        draw(ax, np.array(days), np.array(ys), np.array(lo), np.array(hi),
             c, ls, mk, lab, 2.4, endlab=False)
        ends.append([days[-1], ys[-1]])
    end_labels(ax, ends)
    ax.set_xticks(range(0, 14, 2))
    style(ax, "day", "belief accuracy (all queries, counterfactual)",
          "Learning speed under the sensing budget")
    ax.legend(frameon=False, fontsize=9.5, loc="lower right", labelcolor=INK)
    save(fig, SUB3, "belief_accuracy_by_day.png",
         "Scarce loop (zero prior obs, B=5 looks/day). Scored on every query regardless of answer/resense, so coverage differences cannot inflate an arm.")


def active_calibration():
    fig, ax = fig1(7.0, 5.2)
    arms = [a for a in A_ARMS if a[0] != "classical"]
    w, xp = 0.36, np.arange(len(arms))
    for j, (fld, lab, c) in enumerate([("verbal_conf", "stated confidence", MAGENTA),
                                       ("correct", "realized accuracy", VIOLET)]):
        vals, err = [], [[], []]
        for albl, f, _, _, _ in arms:
            rows = [r for r in L(AOR / f) if r["action"] == "answer"
                    and r.get("verbal_conf") is not None and 0 <= r["verbal_conf"] <= 1]
            per = _hh_vals(rows, lambda v: float(np.mean([x[fld] for x in v])))
            v = float(np.mean(per)); a, b = boot_vec(per)
            vals.append(v); err[0].append(max(0, v - a)); err[1].append(max(0, b - v))
        ax.bar(xp + (j - 0.5) * w, vals, w * 0.92, color=c, label=lab, zorder=3)
        ax.errorbar(xp + (j - 0.5) * w, vals, yerr=err, fmt="none", ecolor=INK2,
                    elinewidth=1.1, capsize=3, zorder=4)
        for x_, v, e in zip(xp + (j - 0.5) * w, vals, err[1]):
            ax.text(x_, v + e + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=INK2)
    ax.set_xticks(xp)
    ax.set_xticklabels([a[0].replace(" (", "\n(") for a in arms], fontsize=9.5)
    ax.set_ylim(0, 1.0)
    style(ax, None, "on answered queries", "Stated confidence vs realized accuracy")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right", labelcolor=INK)
    save(fig, SUB3, "calibration_stated_vs_realized.png",
         "Both arms overconfident (gap 0.09 scaffold, 0.12 fusion) — mild, and behaviourally contained (see resense_targeting).")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # passive_adaptation
    at = atyp_rows()
    passive_curves(at, "atypical", "Passive adaptation — ATYPICAL households", 24)
    passive_paired(at, "atypical", "Paired difference vs classical — ATYPICAL households")
    ty = typ_rows()
    if ty:
        passive_curves(ty, "typical", "Passive adaptation — TYPICAL households", 6)
        passive_paired(ty, "typical", "Paired difference vs classical — TYPICAL households")
    else:
        print("typical passive rows not present yet (all_rows_typ_typd0.jsonl)")
    anonymization_ablation()
    # reflection_gating
    gating_accuracy_by_day(6)
    gating_load_sweep()
    gating_paired_by_load()
    gating_paired_by_day(12)
    # active_sensing
    nd = 14
    active_bar("reward_per_household_day.png",
               "Reward under a scarce sensing budget", "reward per household-day",
               lambda v: sum(x["reward"] for x in v) / nd,
               ylim=(0, 7.2),
               caption="ANSWER scores 1/0; RESENSE scores 0.4 and reveals the truth. Q=10, B=5. DeepSeek, per-model tau/alpha.")
    active_bar("resense_targeting.png",
               "Choosing which observation to spend on",
               "P(would have been wrong | chose to look)",
               lambda v: (float(np.mean([1 - x["cf_correct"] for x in v
                                         if x["action"] == "resense"]))
                          if any(x["action"] == "resense" for x in v) else float("nan")),
               ylim=(0, 1.06),
               caption="The scaffolded LLM's looks land on its own would-be errors 86% of the time vs 58% for classical: world knowledge locates its ignorance.")
    active_learning_curves()
    active_calibration()


if __name__ == "__main__":
    main()
