"""VERSION22 expanded-bank figures (Change 0 deliverable).

Uses the EXPANDED pool (frozen version22 12hh + version22b 12hh = 24 households,
>=15 clusters/tercile). Three x-axis treatments x two arm sets, receptacle + room:

  x-axes:
    - days          : accuracy vs days of experience (checkpoints), faceted by
                      observation density.
    - observations  : accuracy vs CUMULATIVE observations consumed (= days x
                      obs/day), all densities overlaid on one information axis.
    - obs_per_day   : day-14 accuracy vs observations/day (the density axis;
                      true useful obs held ~3.2/day, distractors inflate it).

  arm sets:
    - main   : OUR GATE (llm_surprise) + fusion + classical, gate HIGHLIGHTED.
               Nightly reflection and raw digest are intentionally dropped here.
    - llm    : the LLM-only comparison — nightly vs raw-digest vs gate.

Everything writes to reports/reflect/v22_figures/.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.reflect.run import OUT, CKPTS
from dynbelief.reflect.v22_expanded import _rows          # expanded pool loader

FIG_DIR = OUT / "v22_figures"
LEVELS = [0, 3, 6, 12]
OBS_PER_DAY = {0: 3.2, 3: 6.2, 6: 9.2, 12: 15.2}          # measured, expanded pool

# gate highlighted; fusion + classical are the comparison
MAIN_ARMS = ["llm_surprise", "fusion", "classical_C3g"]
LLM_ARMS = ["llm_direct", "llm_nomem", "llm_surprise"]
GATE_VS_CLASSICAL = ["llm_surprise", "classical_C3g"]     # head-to-head
STYLE = {
    "llm_surprise":  dict(color="#e8890c", lw=3.0, ms=7, zorder=5, label="surprise-gate (ours)"),
    "fusion":        dict(color="#2a9d8f", lw=1.9, ms=5, zorder=3, label="fusion"),
    "classical_C3g": dict(color="#2e6f95", lw=1.9, ms=5, zorder=3, label="classical C3g", ls="--"),
    "llm_direct":    dict(color="#d1495b", lw=1.9, ms=5, zorder=3, label="nightly reflection"),
    "llm_nomem":     dict(color="#8d99ae", lw=1.9, ms=5, zorder=3, label="raw digest"),
}


def _arm_label(tag):
    return {"main": "gate + fusion + classical",
            "llm": "LLM strategies",
            "gate_vs_classical": "surprise-gate vs classical"}.get(tag, tag)


# whole-week checkpoints have BALANCED day-of-week coverage under the fixed Monday
# start, so they are free of the weekly-alignment ripple that produces the day-5
# hump (see HUMP_DIAGNOSIS.md). The intermediate checkpoints (5, 10) are phase-
# contaminated. A true phase-AVERAGE of the LLM arm needs re-running reflection at
# every start weekday (data is Monday-only); restricting to these checkpoints is
# the free, comparable equivalent that removes the alignment ripple.
PHASE_CLEAN_CKPTS = [1, 7, 14]


def fig_days_phase_clean(arms, field, tag):
    """days_gate_vs_classical, phase-normalized: the phase-clean whole-week
    checkpoints (D=7, 14; + D=1 anchor) are drawn BOLD and connected — that is the
    alignment-ripple-free comparison — while the phase-contaminated intermediate
    points (D=5, 10) are shown hollow/faint for reference only."""
    lab = "Receptacle" if field == "correct" else "Room"
    fig, axes = plt.subplots(1, len(LEVELS), figsize=(4.3 * len(LEVELS), 4.6), sharey=True)
    for ax, lv in zip(axes, LEVELS):
        rows = _rows(lv, expanded=True)
        for arm in arms:
            allx, ally = [], []
            for ck in CKPTS:
                r = _acc(rows, arm, field, [ck])
                if r:
                    allx.append(ck); ally.append(r[0])
            s = STYLE[arm]
            # faint full curve + hollow contaminated markers
            ax.plot(allx, ally, s.get("ls", "-"), color=s["color"], lw=1.0, alpha=0.35, zorder=2)
            cont = [(x, y) for x, y in zip(allx, ally) if x not in PHASE_CLEAN_CKPTS]
            if cont:
                ax.scatter(*zip(*cont), facecolors="none", edgecolors=s["color"],
                           s=34, alpha=0.5, zorder=3)
            # bold phase-clean curve
            cx = [x for x in allx if x in PHASE_CLEAN_CKPTS]
            cy = [y for x, y in zip(allx, ally) if x in PHASE_CLEAN_CKPTS]
            ax.plot(cx, cy, s.get("ls", "-"), color=s["color"], marker="o",
                    ms=s["ms"] + 1, lw=s["lw"], zorder=5, label=s["label"])
        ax.set_title(f"~{OBS_PER_DAY[lv]:.0f} obs/day  ({lv} distractors)", fontsize=10)
        ax.set_xlabel("days of experience"); ax.grid(alpha=0.25); ax.set_ylim(0, 0.62)
        for xc in (5, 10):
            ax.axvline(xc, color="#ccc", ls=":", lw=0.8, zorder=1)
    axes[0].set_ylabel(f"{lab}-level accuracy")
    axes[0].legend(fontsize=8.5, loc="upper left")
    fig.suptitle(f"VERSION22 expanded (24 hh) — {lab.lower()} accuracy vs DAYS, PHASE-NORMALIZED "
                 f"({_arm_label(tag)})\nbold = phase-clean whole-week checkpoints (D=7,14; balanced "
                 f"coverage) · hollow = alignment-contaminated D=5,10 (the hump) · dotted lines mark them",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = FIG_DIR / f"days_{tag}_phaseclean_{field}.png"
    fig.savefig(out, dpi=140); plt.close(fig); print("wrote", out)


def _acc(rows, arm, field, ckpts=None):
    """clustered bootstrap mean + 95% CI over (hh, object) clusters."""
    by = defaultdict(list)
    for r in rows:
        if r["model"] == arm and (ckpts is None or r["ckpt"] in ckpts):
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    clus = list(by); rng = np.random.default_rng(7)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus)) for v in by[clus[i]]])
         for _ in range(2000)]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _plot(ax, arm, xs, ys, los=None, his=None):
    s = STYLE[arm]
    ax.plot(xs, ys, s.get("ls", "-"), color=s["color"], marker="o", ms=s["ms"],
            lw=s["lw"], zorder=s["zorder"], label=s["label"])
    if los is not None:
        ax.fill_between(xs, los, his, color=s["color"], alpha=0.12, zorder=s["zorder"] - 1)


# ── x = days of experience (faceted by density) ──────────────────────────────

def fig_days(arms, field, tag):
    lab = "Receptacle" if field == "correct" else "Room"
    fig, axes = plt.subplots(1, len(LEVELS), figsize=(4.3 * len(LEVELS), 4.6), sharey=True)
    for ax, lv in zip(axes, LEVELS):
        rows = _rows(lv, expanded=True)
        for arm in arms:
            xs, ys, los, his = [], [], [], []
            for ck in CKPTS:
                r = _acc(rows, arm, field, [ck])
                if r:
                    xs.append(ck); ys.append(r[0]); los.append(r[1]); his.append(r[2])
            if xs:
                _plot(ax, arm, xs, ys, los, his)
        ax.set_title(f"~{OBS_PER_DAY[lv]:.0f} obs/day  ({lv} distractors)", fontsize=10)
        ax.set_xlabel("days of experience"); ax.grid(alpha=0.25); ax.set_ylim(0, 0.62)
    axes[0].set_ylabel(f"{lab}-level accuracy")
    axes[0].legend(fontsize=8.5, loc="upper left")
    fig.suptitle(f"VERSION22 expanded (24 hh) — {lab.lower()}-level accuracy vs DAYS of experience "
                 f"({_arm_label(tag)})",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = FIG_DIR / f"days_{tag}_{field}.png"
    fig.savefig(out, dpi=140); plt.close(fig); print("wrote", out)


# ── x = cumulative observations consumed (all densities overlaid) ────────────

def fig_observations(arms, field, tag):
    """x = cumulative observations consumed (days x obs/day). Each density is its
    OWN monotonic line (never connected across densities — that would falsely
    equate 'many useful obs' with 'few obs + clutter' at the same x). The clean
    ~3-obs/day line (no distractors) is bold; denser (distractor-inflated) lines
    are faded and sit to the RIGHT at the same accuracy — more observations, no
    gain, because the extra observations are clutter."""
    lab = "Receptacle" if field == "correct" else "Room"
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    alphas = {0: 1.0, 3: 0.55, 6: 0.4, 12: 0.28}
    for arm in arms:
        s = STYLE[arm]
        for lv in LEVELS:
            rows = _rows(lv, expanded=True)
            xs, ys = [], []
            for ck in CKPTS:
                r = _acc(rows, arm, field, [ck])
                if r:
                    xs.append(ck * OBS_PER_DAY[lv]); ys.append(r[0])
            if not xs:
                continue
            bold = lv == 0
            ax.plot(xs, ys, s.get("ls", "-"), color=s["color"], marker="o",
                    ms=s["ms"] if bold else 3, lw=s["lw"] if bold else 1.1,
                    zorder=s["zorder"], alpha=alphas[lv],
                    label=s["label"] if bold else None)
    ax.set_xscale("log")
    ax.set_xlabel("cumulative observations consumed  (days x obs/day, log scale)")
    ax.set_ylabel(f"{lab}-level accuracy"); ax.grid(alpha=0.25, which="both")
    ax.set_ylim(0, 0.62); ax.legend(fontsize=9, loc="lower right")
    ax.set_title(f"VERSION22 expanded (24 hh) — {lab.lower()}-level accuracy vs TOTAL observations\n"
                 f"({_arm_label(tag)}); "
                 "bold = ~3 useful obs/day (no clutter), faded = distractor-inflated (shifted right, no gain)",
                 fontsize=10.0)
    fig.tight_layout()
    out = FIG_DIR / f"observations_{tag}_{field}.png"
    fig.savefig(out, dpi=140); plt.close(fig); print("wrote", out)


# ── x = observations/day (day-14 density axis) ───────────────────────────────

def fig_obs_per_day(arms, field, tag):
    lab = "Receptacle" if field == "correct" else "Room"
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    for arm in arms:
        xs, ys, los, his = [], [], [], []
        for lv in LEVELS:
            r = _acc(_rows(lv, expanded=True), arm, field, [14])
            if r:
                xs.append(OBS_PER_DAY[lv]); ys.append(r[0]); los.append(r[1]); his.append(r[2])
        if xs:
            _plot(ax, arm, xs, ys, los, his)
    ax.set_xlabel("observations / day  (true useful ~3.2 + distractors)")
    ax.set_ylabel(f"{lab}-level accuracy (day 14)"); ax.grid(alpha=0.25)
    ax.set_ylim(0, 0.62); ax.set_xticks([OBS_PER_DAY[l] for l in LEVELS])
    ax.set_xticklabels([f"{OBS_PER_DAY[l]:.0f}" for l in LEVELS])
    ax.legend(fontsize=9, loc="best")
    ax.set_title(f"VERSION22 expanded (24 hh) — day-14 {lab.lower()} accuracy vs OBSERVATIONS/DAY\n"
                 f"({_arm_label(tag)}); "
                 "distractors inflate obs/day but are never queried", fontsize=10.5)
    fig.tight_layout()
    out = FIG_DIR / f"obs_per_day_{tag}_{field}.png"
    fig.savefig(out, dpi=140); plt.close(fig); print("wrote", out)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for field in ("correct", "room_correct"):
        for arms, tag in ((MAIN_ARMS, "main"), (LLM_ARMS, "llm"),
                          (GATE_VS_CLASSICAL, "gate_vs_classical")):
            fig_days(arms, field, tag)
            fig_observations(arms, field, tag)
            fig_obs_per_day(arms, field, tag)
    print("\nall figures in", FIG_DIR)


if __name__ == "__main__":
    main()
