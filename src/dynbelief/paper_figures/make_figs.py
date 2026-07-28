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
  * One chart per file. NO caption text is rendered — titles, axis labels and
    value labels carry the figure; the caption strings in save() calls are
    in-code documentation only.
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
BOX = dict(boxstyle="round,pad=0.3", fc="white", ec="#d9d8d3", alpha=0.92)
# Proper model names for titles (row tags are lowercase keys internally).
# Draw order: bands/reference lines 1-2, marks/bars 3, errorbar whiskers 4,
# and ALL numeric labels on Z_TEXT so a whisker can never obscure a value.
Z_TEXT = 10
MODEL_DISPLAY = {"deepseek": "DeepSeek-V4-Flash", "qwen36": "Qwen3.6-35B-A3B",
                 "glm": "GLM-4.5-Air"}


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
    ax.tick_params(colors=INK2, labelsize=12)
    if xlab:
        ax.set_xlabel(xlab, fontsize=13, color=INK, labelpad=6)
    if ylab:
        ax.set_ylabel(ylab, fontsize=13, color=INK, labelpad=6)
    if title:
        ax.set_title(title, fontsize=15, color=INK, pad=8)


def fig1(w=7.4, h=4.9):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=SURF)
    return fig, ax


def save(fig, sub, name, caption=None):
    """Write the figure. `caption` is NOT rendered — figures carry no caption
    text (the paper supplies it). The argument is kept because the strings at
    the call sites document what each chart shows and what its pitfalls are;
    dropping the rendering here guarantees no call site can reintroduce one."""
    d = OUT / sub
    d.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=0.5)
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
                    textcoords="offset points", va="center", fontsize=11.5,
                    fontweight="bold", color=INK, zorder=Z_TEXT,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none",
                              alpha=0.8))


def end_labels(ax, ends, big=False):
    """Value labels at the right end of each series, vertically dodged."""
    ends = sorted(ends, key=lambda e: e[1])
    span = ax.get_ylim()[1] - ax.get_ylim()[0]
    gap = 0.06 if big else 0.045
    shown = [e[1] for e in ends]
    for i in range(1, len(shown)):
        if shown[i] - shown[i - 1] < gap * span:
            shown[i] = shown[i - 1] + gap * span
    h_in = ax.get_position().height * ax.figure.get_figheight()
    for (x_, y_), sy in zip(ends, shown):
        ax.annotate(f"{y_:.2f}", (x_, y_), xytext=(7, (sy - y_) * 72 * h_in / span),
                    textcoords="offset points", va="center",
                    fontsize=16 if big else 11.5,
                    fontweight="bold", color=INK, zorder=Z_TEXT,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none",
                              alpha=0.8))


def logx(ax, cks=CKPTS):
    ax.set_xscale("log")
    ax.set_xticks(cks)
    ax.set_xticklabels([str(c) for c in cks])
    ax.minorticks_off()


def linx(ax, cks=CKPTS):
    """Linear day axis. Checkpoints are unevenly spaced (1,2,3,5,7,10,14), so a
    linear scale spreads the late, flat days and compresses the early ones where
    the arms actually separate — the opposite emphasis to logx."""
    ax.set_xscale("linear")
    ax.set_xticks(cks)
    ax.set_xticklabels([str(c) for c in cks])
    ax.set_xlim(min(cks) - 0.6, max(cks) + 0.6)
    ax.minorticks_off()


# ══════════════════ passive_adaptation ══════════════════
SUB1 = "passive_adaptation"
P_ARMS = [("fusion", "LLM + Classical (fusion)", BLUE, "-", "o", 2.6),
          ("llm_direct", "LLM (reflective memory)", ORANGE, "-", "s", 2.2),
          ("llm_nomem", "LLM (no reflection)", YELLOW, "-.", "D", 1.9),
          ("classical_C3g", "Classical", AQUA, "--", "^", 2.0)]


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
    style(ax, "Days of observation (log)", "Accuracy (exact receptacle)", title)
    ax.legend(frameon=False, fontsize=12, loc="best", labelcolor=INK)
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
                    arrowprops=dict(arrowstyle="->", color=INK2, lw=1), zorder=Z_TEXT)
    logx(ax)
    style(ax, "Days of observation (log)",
          "Accuracy − Classical (paired per household)", title)
    ax.legend(frameon=False, fontsize=12, loc="lower right", labelcolor=INK)
    save(fig, SUB1, f"paired_delta_vs_classical_{tag}.png",
         "Within-household difference vs. the Classical arm; household variance cancels. Largest on day 1, before Classical has any data.")


def anonymization_ablation():
    models = [("deepseek-anonfix", "DeepSeek"), ("qwen36-anonfix", "Qwen3.6"),
              ("glm-anonfix", "GLM-4.5-Air")]
    fig, ax = fig1(8.0, 5.2)
    w, xpos = 0.34, np.arange(len(models))
    for j, (arm, lab, c) in enumerate([("llm_named", "Named receptacles", BLUE),
                                       ("llm_anon", "Names stripped", ORANGE)]):
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
        for x_, v in zip(xpos + (j - 0.5) * w, vals):
            # INSIDE the bar: these CIs are wide enough that a label above the
            # whisker lands outside the axes (and in the title).
            ax.text(x_, v - 0.018, f"{v:.2f}", ha="center", va="top",
                    fontsize=13, fontweight="bold", color="white", zorder=Z_TEXT)
    ax.axhline(0.065, color="#a8a7a2", lw=1.2, ls=(0, (1, 3)), zorder=1)
    ax.annotate("Chance", (-0.45, 0.075), fontsize=10.5, color="#8d8c88",
                va="bottom", ha="left", zorder=Z_TEXT)
    ax.set_xticks(xpos)
    ax.set_xticklabels([m for _, m in models], fontsize=13)
    ax.set_ylim(0, 0.80)
    style(ax, None, "Accuracy on regime-flipped targets",
          "Ablation: Anonymize Receptacle Names")
    ax.legend(frameon=False, fontsize=12.5, loc="upper center", ncol=2,
              labelcolor=INK, columnspacing=1.6)
    save(fig, SUB1, "anonymization_ablation.png",
         "Stripping names removes semantic priors, evidence digest kept. Costs DeepSeek and Qwen; GLM gains (exception, 2 of 3).")


# ══════════════════ reflection_gating ══════════════════
SUB2 = "reflection_gating"
G_ARMS = [("llm_surprise", "Surprise-gated reflection", BLUE, "-", "o", 2.6),
          ("llm_direct", "Nightly reflection", ORANGE, "--", "s", 2.2),
          ("llm_nomem", "No reflection", GRAY, ":", "x", 1.9)]


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
    style(ax, "Days of observation (log)", "Accuracy (exact receptacle)",
          f"Reflection Strategies at Distractor Load {d}")
    ax.legend(frameon=False, fontsize=12, loc="upper left", labelcolor=INK)
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
    ax.annotate(f"LLM calls per household: gate {calls[12]:.1f} vs nightly 14",
                xy=(0.03, 0.04), xycoords="axes fraction", fontsize=9.5,
                color=INK, bbox=BOX, zorder=Z_TEXT)
    style(ax, "Distractor objects per household", "Accuracy (days 5-14, phase-averaged)",
          "Accuracy vs. Distractor Load")
    ax.legend(frameon=False, fontsize=12, loc="upper right", labelcolor=INK)
    save(fig, SUB2, "accuracy_vs_distractor_load.png",
         "Nightly reflection degrades as noise accumulates; the gate holds because a padded stream rarely fires it.")


def distractor_robustness():
    """Accuracy vs distractor load for EVERY arm, with Classical as the flat
    reference. Distractors touch only distractor objects, which are never
    queried, so the per-edge Classical fit is invariant by construction — the
    flat line is a proof-of-construction, not a measurement. Everything that
    reads the observation stream semantically degrades."""
    def all_arms_rows(d):
        """Like gate_rows but WITHOUT the obs_spec filter: the offline arms
        (Classical, fusion) are produced by report.py and never carry an
        obs_spec field, so filtering on it silently drops them. Each distractor
        file holds exactly one run, so no filter is needed."""
        sur = [r for b in ("v22", "v22b")
               for r in L(REP / f"reflect/rows_surprise_{b}_surprise_d{d}.jsonl")]
        oth = [r for b in ("v22", "v22b")
               for r in L(REP / f"reflect/all_rows_{b}_distractor_d{d}.jsonl")]
        return sur + oth

    ARMS = [("llm_surprise", "Surprise-gated reflection", BLUE, "-", "o", 2.8),
            ("llm_direct", "Nightly reflection", ORANGE, "--", "s", 2.6),
            ("llm_nomem", "No reflection", YELLOW, "-.", "D", 2.2),
            ("fusion", "LLM + Classical (fusion)", MAGENTA, "-", "v", 2.4),
            ("classical_C3g", "Classical", AQUA, ":", "^", 2.6)]
    fig, ax = fig1(8.0, 5.4)
    ends = []
    for m, lab, c, ls, mk, lw in ARMS:
        ys, lo, hi = [], [], []
        for d in DISTS:
            rows = all_arms_rows(d)
            hhs = sorted({r["hh"] for r in rows})
            per = [phase_mean([r for r in rows if r["hh"] == hh and r["ckpt"] >= 5
                               and r["model"] == m]) for hh in hhs]
            per = [x for x in per if not np.isnan(x)]
            a_, b_ = boot_vec(per)
            ys.append(float(np.mean(per))); lo.append(a_); hi.append(b_)
        draw(ax, np.array(DISTS), np.array(ys), np.array(lo), np.array(hi),
             c, ls, mk, lab, lw, band=(m != "classical_C3g"), endlab=False)
        ends.append([DISTS[-1], ys[-1]])
    end_labels(ax, ends, big=True)
    ax.set_xticks(DISTS)
    _big_axes(ax, "Robustness to Distractor Load",
              xlab="Distractor Objects per Household",
              ylab="Accuracy (days 5-14)", loc="lower left")
    save(fig, SUB2, "accuracy_vs_distractor_load_all_arms.png")


# Distractor load as the SERIES, days as the x-axis. One arm only (surprise
# gate, DeepSeek) so the plot isolates what clutter does to a single method.
# Endpoints only: the intermediate loads sit between these two and crowd the
# plot without changing the claim.
LOAD_COLORS = [(0, "0 distractors", "#1baf7a", "-", "o"),
               (12, "12 distractors", "#eb6834", "--", "v")]


def surprise_load_curves(model_tag="deepseek"):
    fig, ax = fig1(8.0, 5.4)
    ends = []
    for d, lab, c, ls, mk in LOAD_COLORS:
        rows = [r for b in ("v22", "v22b")
                for r in L(REP / f"reflect/rows_surprise_{b}_surprise_d{d}.jsonl")]
        xs, ys, lo, hi = hh_curve(rows, "llm_surprise")
        if not len(xs):
            continue
        ax.fill_between(xs, lo, hi, color=c, alpha=0.10, lw=0)
        ax.plot(xs, ys, ls, color=c, lw=2.8, marker=mk, ms=8, mec=SURF, mew=1.4,
                label=lab, zorder=3)
        ends.append([xs[-1], ys[-1]])
    end_labels(ax, ends, big=True)
    linx(ax)
    _big_axes(ax, "Surprise-Gated Reflection vs. Distractor Load\n"
                  f"{MODEL_DISPLAY.get(model_tag, model_tag)}",
              ylab="Accuracy", loc="lower right")
    save(fig, SUB2, f"surprise_gate_by_distractor_load_{model_tag}.png")


def gating_paired_by_load():
    fig, ax = fig1()
    ax.axhline(0, color="#9c9b96", lw=1.2, zorder=2)
    for ref, lab, c, ls, mk in [("llm_direct", "vs. nightly reflection", ORANGE, "-", "o"),
                                ("llm_nomem", "vs. no reflection", GRAY, "--", "D")]:
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
                        arrowprops=dict(arrowstyle="->", color=INK2, lw=1), zorder=Z_TEXT)
    ax.set_xticks(DISTS)
    ax.set_ylim(-0.14, 0.21)
    style(ax, "Distractor objects per household",
          "Surprise − comparator (paired per household)",
          "Paired Difference vs. Distractor Load (days 5-14)")
    ax.legend(frameon=False, fontsize=12, loc="lower left", labelcolor=INK)
    save(fig, SUB2, "paired_delta_vs_nightly_by_load.png",
         "24 households, paired within household. The gate matches nightly at loads 0-6 and beats it at 12.")


def gating_paired_by_day(d=12):
    rows, _ = gate_rows(d)
    fig, ax = fig1()
    ax.axhline(0, color="#9c9b96", lw=1.2, zorder=2)
    for ref, lab, c, ls, mk in [("llm_direct", "vs. nightly reflection", ORANGE, "-", "o"),
                                ("llm_nomem", "vs. no reflection", GRAY, "--", "D")]:
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
                fontsize=9, color=INK, bbox=BOX, zorder=Z_TEXT)
    logx(ax)
    ax.set_ylim(-0.16, 0.26)
    style(ax, "Days of observation (log)",
          "Surprise − comparator (paired per household)",
          f"Paired Difference by Day at Distractor Load {d}")
    ax.legend(frameon=False, fontsize=12, loc="lower right", labelcolor=INK)
    save(fig, SUB2, f"paired_delta_vs_nightly_by_day_load{d}.png",
         "The gate's edge appears from day 5 on, once nightly reflection has repeatedly rewritten memory over noise.")


# ══════════════════ active_sensing ══════════════════
SUB3 = "active_sensing"
AOR = REP / "answer_or_resense"
A_ARMS = [("Classical", "rows_classical_conf_frozen.jsonl", AQUA, "--", "^"),
          ("LLM (scaffold)", "rows_llm_scaffold_conf_frozen.jsonl", BLUE, "-", "o"),
          ("LLM + Classical (fusion)", "rows_scaffold_fusion_conf_permodel_deepseek.jsonl",
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
        ax.text(i, v + e + top * 0.022, fmt.format(v), ha="center",
                fontsize=12, fontweight="bold", color=INK, zorder=Z_TEXT)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels([l.replace(" (", "\n(") for l in labs], fontsize=11.5)
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
    style(ax, "Day", "Belief accuracy (all queries, counterfactual)",
          "Learning Speed Under the Sensing Budget")
    ax.legend(frameon=False, fontsize=12, loc="lower right", labelcolor=INK)
    save(fig, SUB3, "belief_accuracy_by_day.png",
         "Counterfactual: every query is scored against what the arm WOULD have answered, including ones it chose to resense on. Coverage cannot inflate an arm — but correct abstentions are counted as errors, so this UNDER-credits an arm that knows when to look.")


def _active_day_curve(ax, sel, val, ylab, title, name, caption):
    """Per-arm daily curve of `val` over the queries selected by `sel`."""
    days = list(range(14)); ends = []
    for lab, f, c, ls, mk in A_ARMS:
        rows = [x for x in L(AOR / f) if sel(x)]
        by = defaultdict(lambda: defaultdict(list))
        for r in rows:
            by[r["hh"]][r["day"]].append(val(r))
        ys, lo, hi = [], [], []
        for d in days:
            per = [float(np.mean(v[d])) for v in by.values() if v.get(d)]
            a_, b_ = boot_vec(per)
            ys.append(float(np.mean(per)) if per else float("nan"))
            lo.append(a_); hi.append(b_)
        draw(ax, np.array(days), np.array(ys), np.array(lo), np.array(hi),
             c, ls, mk, lab, 2.4, endlab=False)
        ends.append([days[-1], ys[-1]])
    end_labels(ax, ends, big=True)
    ax.set_xticks(range(0, 14, 2))
    _big_axes(ax, title, xlab="Day", ylab=ylab, loc="lower right")
    save(fig_of(ax), SUB3, name, caption)


def fig_of(ax):
    return ax.figure


def active_answered_accuracy():
    """Accuracy on the queries the arm ACTUALLY ANSWERED — no counterfactual.
    Must be read next to answer_rate_by_day.png: an arm that abstains on the
    hard queries scores higher here for free, so coverage is the other half."""
    fig, ax = fig1()
    _active_day_curve(ax, lambda x: x["action"] == "answer",
                      lambda r: r["correct"],
                      "Accuracy on answered queries",
                      "Accuracy When the Arm Chose to Answer",
                      "answered_accuracy_by_day.png", None)


def active_answer_rate():
    """Coverage: the fraction of queries answered rather than resensed."""
    fig, ax = fig1()
    _active_day_curve(ax, lambda x: True,
                      lambda r: int(r["action"] == "answer"),
                      "Fraction of queries answered",
                      "Coverage: How Often Each Arm Committed",
                      "answer_rate_by_day.png", None)


def active_calibration():
    fig, ax = fig1(7.0, 5.2)
    # keyed off the ROW FILE, not the display label: matching on the label
    # silently broke when "classical" was capitalized for presentation and
    # left an empty group on the chart.
    arms = [a for a in A_ARMS if "rows_classical" not in a[1]]
    w, xp = 0.36, np.arange(len(arms))
    for j, (fld, lab, c) in enumerate([("verbal_conf", "Stated confidence", MAGENTA),
                                       ("correct", "Realized accuracy", VIOLET)]):
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
            ax.text(x_, v + e + 0.02, f"{v:.2f}", ha="center", fontsize=11.5, fontweight="bold", color=INK2, zorder=Z_TEXT)
    ax.set_xticks(xp)
    ax.set_xticklabels([a[0].replace(" (", "\n(") for a in arms], fontsize=11.5)
    ax.set_ylim(0, 1.0)
    style(ax, None, "On answered queries", "Stated Confidence vs. Realized Accuracy")
    ax.legend(frameon=False, fontsize=12, loc="upper right", labelcolor=INK)
    save(fig, SUB3, "calibration_stated_vs_realized.png",
         "Both LLM arms overconfident (gap 0.09 scaffold, 0.12 fusion) — mild, and behaviourally contained (see the resense-targeting chart).")


# ── clean per-model figures: LLM (reflective memory) vs classical only ──
def _atyp_of(model):
    """Prefer the 24-hh v22+v22b pool for the model; fall back to the 6-hh conf
    bank (rand3) until the v22 runs land."""
    if model == "deepseek":
        return atyp_rows()
    v22 = [r for b in ("v22", "v22b")
           for r in L(REP / f"reflect/all_rows_{b}_d0_{model}.jsonl")]
    return v22 or L(REP / f"reflect/all_rows_conf_{model}_orand3.jsonl")


CLEAN = [  # (model tag, atypical rows fn, typical rows file)
    ("deepseek", atyp_rows, "all_rows_typ_typd0.jsonl"),
    ("qwen36", lambda: _atyp_of("qwen36"), "all_rows_typ_typd0_qwen36.jsonl"),
    ("glm", lambda: _atyp_of("glm"), "all_rows_typ_typd0_glm.jsonl"),
]


def clean_figure(rows, tag, model):
    """LLM (reflective memory, labeled just 'LLM') vs. Classical. Big bold text,
    no caption."""
    if not rows:
        print(f"clean {tag} {model}: rows not present yet")
        return
    fig, ax = fig1(7.8, 5.2)
    ends = []
    for m, lab, c, ls, mk, lw in [("llm_direct", "LLM", ORANGE, "-", "s", 3.2),
                                  ("classical_C3g", "Classical", AQUA, "--", "^", 2.8)]:
        xs, ys, lo, hi = hh_curve(rows, m)
        if not len(xs):
            return
        ax.fill_between(xs, lo, hi, color=c, alpha=0.13, lw=0)
        ax.plot(xs, ys, ls, color=c, lw=lw, marker=mk, ms=9, mec=SURF, mew=1.5,
                label=lab, zorder=3)
        ends.append([xs[-1], ys[-1]])
    # big bold end labels, dodged
    ends.sort(key=lambda e: e[1])
    span = ax.get_ylim()[1] - ax.get_ylim()[0]
    shown = [e[1] for e in ends]
    for i in range(1, len(shown)):
        if shown[i] - shown[i - 1] < 0.06 * span:
            shown[i] = shown[i - 1] + 0.06 * span
    h_in = ax.get_position().height * ax.figure.get_figheight()
    for (x_, y_), sy in zip(ends, shown):
        ax.annotate(f"{y_:.2f}", (x_, y_), xytext=(8, (sy - y_) * 72 * h_in / span),
                    textcoords="offset points", va="center", fontsize=17.5,
                    fontweight="bold", color=INK, zorder=Z_TEXT,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none",
                              alpha=0.8))
    logx(ax)
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=0.9)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#c9c8c3")
    ax.tick_params(colors=INK, labelsize=15.5)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.set_xlabel("Days of Observation", fontsize=17.5, fontweight="bold",
                  color=INK, labelpad=5)
    ax.set_ylabel("Accuracy", fontsize=17.5, fontweight="bold", color=INK,
                  labelpad=5)
    ax.set_title(f"{tag.capitalize()} Households — {MODEL_DISPLAY.get(model, model)}",
                 fontsize=19, fontweight="bold", color=INK, pad=9)
    leg = ax.legend(frameon=False, fontsize=15.5, loc="best", labelcolor=INK)
    for t in leg.get_texts():
        t.set_fontweight("bold")
    save(fig, SUB1, f"clean_llm_vs_classical_{tag}_{model}.png")


# ── anon figures: named LLM vs anonymized LLM vs classical, per model ──
SUBA = "anon"


def _anon_rows(model, tag):
    """rows_{bank}_anon_{model}.jsonl for the banks behind a typical/atypical
    clean figure. The anon runs score llm_direct against the MAPPED truth."""
    banks = ["typ"] if tag == "typical" else ["v22", "v22b"]
    return [r for b in banks for r in L(REP / f"reflect/rows_{b}_anon_{model}.jsonl")]


def _named_rows(model, tag):
    if tag == "typical":
        f = "all_rows_typ_typd0.jsonl" if model == "deepseek"             else f"all_rows_typ_typd0_{model}.jsonl"
        return L(REP / f"reflect/{f}")
    return _atyp_of(model)


def _big_axes(ax, title, xlab="Days of Observation", ylab="Accuracy", loc="best"):
    """Large bold styling shared by the clean, anon, and active day charts."""
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=0.9)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#c9c8c3")
    ax.tick_params(colors=INK, labelsize=15.5)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.set_xlabel(xlab, fontsize=17, fontweight="bold", color=INK, labelpad=5)
    ax.set_ylabel(ylab, fontsize=15.5, fontweight="bold", color=INK, labelpad=5)
    ax.set_title(title, fontsize=17 if "\n" in title else 18,
                 fontweight="bold", color=INK, pad=9)
    leg = ax.legend(frameon=False, fontsize=14.5, loc=loc, labelcolor=INK)
    for t in leg.get_texts():
        t.set_fontweight("bold")


def anon_figure(tag, model, setting="passive"):
    named, anon = _named_rows(model, tag), _anon_rows(model, tag)
    if not named or not anon:
        print(f"anon {tag} {model}: rows not present yet")
        return
    for r in anon:
        r["model"] = "llm_anon"
    rows = named + anon
    fig, ax = fig1(7.8, 5.2)
    ends = []
    for m, lab, c, ls, mk, lw in [
            ("llm_direct", "LLM (named)", ORANGE, "-", "s", 3.2),
            ("llm_anon", "LLM (anonymized)", VIOLET, "-", "o", 3.2)]:
        xs, ys, lo, hi = hh_curve(rows, m)
        if not len(xs):
            print(f"anon {tag} {model}: missing arm {m}")
            return
        ax.fill_between(xs, lo, hi, color=c, alpha=0.12, lw=0)
        ax.plot(xs, ys, ls, color=c, lw=lw, marker=mk, ms=9, mec=SURF, mew=1.5,
                label=lab, zorder=3)
        ends.append([xs[-1], ys[-1]])
    ends.sort(key=lambda e: e[1])
    span = ax.get_ylim()[1] - ax.get_ylim()[0]
    shown = [e[1] for e in ends]
    for i in range(1, len(shown)):
        if shown[i] - shown[i - 1] < 0.06 * span:
            shown[i] = shown[i - 1] + 0.06 * span
    h_in = ax.get_position().height * ax.figure.get_figheight()
    for (x_, y_), sy in zip(ends, shown):
        ax.annotate(f"{y_:.2f}", (x_, y_), xytext=(8, (sy - y_) * 72 * h_in / span),
                    textcoords="offset points", va="center", fontsize=17.5,
                    fontweight="bold", color=INK, zorder=Z_TEXT,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none",
                              alpha=0.8))
    linx(ax)
    # setting is in BOTH the title and the filename: this folder will hold the
    # passive (ambient stream) and active (self-gathered, answer-or-resense)
    # anonymization runs side by side, and they are not comparable.
    _big_axes(ax, f"{setting.capitalize()} Sensing — {tag.capitalize()} Households\n"
                  f"{MODEL_DISPLAY.get(model, model)}")
    save(fig, SUBA, f"anon_{setting}_accuracy_by_day_{tag}_{model}.png")


def anon_all():
    for model in ("deepseek", "qwen36", "glm"):
        for tag in ("atypical", "typical"):
            anon_figure(tag, model, setting="passive")


def clean_all():
    for model, atyp_fn, typ_file in CLEAN:
        clean_figure(atyp_fn(), "atypical", model)
        clean_figure(L(REP / f"reflect/{typ_file}"), "typical", model)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    clean_all()
    anon_all()
    # passive_adaptation
    at = atyp_rows()
    passive_curves(at, "atypical", "Passive Adaptation — Atypical Households", 24)
    passive_paired(at, "atypical", "Paired Difference vs. Classical — Atypical Households")
    ty = typ_rows()
    if ty:
        passive_curves(ty, "typical", "Passive Adaptation — Typical Households", 6)
        passive_paired(ty, "typical", "Paired Difference vs. Classical — Typical Households")
    else:
        print("typical passive rows not present yet (all_rows_typ_typd0.jsonl)")
    anonymization_ablation()
    # reflection_gating
    gating_accuracy_by_day(6)
    gating_load_sweep()
    distractor_robustness()
    surprise_load_curves()
    gating_paired_by_load()
    gating_paired_by_day(12)
    # active_sensing
    nd = 14
    active_bar("reward_per_household_day.png",
               "Reward Under a Scarce Sensing Budget", "Reward per household-day",
               lambda v: sum(x["reward"] for x in v) / nd,
               ylim=(0, 7.2),
               caption="ANSWER scores 1/0; RESENSE scores 0.4 and reveals the truth. Q=10, B=5. DeepSeek, per-model tau/alpha.")
    active_bar("resense_targeting.png",
               "Choosing Which Observation to Spend On",
               "P(would have been wrong | chose to look)",
               lambda v: (float(np.mean([1 - x["cf_correct"] for x in v
                                         if x["action"] == "resense"]))
                          if any(x["action"] == "resense" for x in v) else float("nan")),
               ylim=(0, 1.06),
               caption="The scaffolded LLM's looks land on its own would-be errors 88% of the time vs. 59% for Classical: world knowledge locates its ignorance.")
    active_learning_curves()
    active_answered_accuracy()
    active_answer_rate()
    active_calibration()


if __name__ == "__main__":
    main()
