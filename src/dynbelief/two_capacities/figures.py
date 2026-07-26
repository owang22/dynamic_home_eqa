"""Two-Capacities figure suite (F1-F5), with the D3 plot-hygiene fixes:
oracle dropped from risk-coverage; per-split rate denominators stated; off-scale
verbalized confidences excluded. Consistent arm colors; CIs shaded."""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.answer_or_resense.run_aor import OUT as AOR_OUT
from dynbelief.two_capacities.diagnostics import rows_of

OUT = AOR_OUT.parent / "two_capacities"
COLORS = {"classical": "#2e6f95", "llm": "#d1495b", "hybrid": "#2a9d8f",
          "llm_thresh": "#9b5de5", "oracle": "#666666", "llm_selfconf": "#f2a541",
          "llm_v1_pinned": "#8338ec"}
B, Q = 5, 10


def _day_ci(rows, kind, field="cf_correct", nb=800):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["kind"] == kind:
            by[r["day"]][r["hh"]].append(r[field])
    days = sorted(by)
    mean, lo, hi = [], [], []
    rng = np.random.default_rng(2)
    for d in days:
        clus = list(by[d])
        vals = [v for c in clus for v in by[d][c]]
        mean.append(np.mean(vals))
        m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                      for v in by[d][clus[i]]]) for _ in range(nb)]
        lo.append(np.percentile(m, 2.5)); hi.append(np.percentile(m, 97.5))
    return days, mean, lo, hi


def f1(arms=("classical", "llm", "hybrid", "llm_v1_pinned")):
    arms = [a for a in arms if rows_of(a)]
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.0), sharey=True)
    for ax, kind in zip(axes, ("typical", "atypical")):
        for arm in arms:
            days, mean, lo, hi = _day_ci(rows_of(arm), kind)
            ax.plot(days, mean, "-o", ms=4, lw=2.2, color=COLORS[arm], label=arm)
            ax.fill_between(days, lo, hi, color=COLORS[arm], alpha=0.12)
        ax.set_title(f"{kind} queries"); ax.set_xlabel("day")
        ax.grid(alpha=0.25); ax.set_ylim(0, 1)
        ins = ax.inset_axes([0.58, 0.08, 0.38, 0.28])
        for arm in arms:
            by = defaultdict(int)
            for r in rows_of(arm):
                if r["action"] == "resense":
                    by[r["day"]] += 1
            days = sorted(set(r["day"] for r in rows_of(arm)))
            ins.plot(days, np.cumsum([by.get(d, 0) / 24 for d in days]),
                     color=COLORS[arm], lw=1.5)
        ins.set_title("cum. self-gathered obs /hh", fontsize=7)
        ins.tick_params(labelsize=6); ins.grid(alpha=0.2)
    axes[0].set_ylabel("answer accuracy (incl. counterfactual)")
    axes[0].legend(fontsize=9, loc="upper left")
    fig.suptitle("F1 - all arms accumulate self-gathered observations at similar rates, but convert them\n"
                 "into accuracy at different rates. NOTE the LLM starts high (prior) and classical at zero;\n"
                 "the mechanism is evidence-following fidelity, not presence/absence of learning (see F6).",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    f = OUT / "F1_gathers_not_learn.png"
    fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def f2(arms=("classical", "llm", "hybrid", "llm_v1_pinned", "oracle")):
    arms = [a for a in arms if rows_of(a)]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for i, arm in enumerate(arms):
        by_obj = defaultdict(list)
        for r in rows_of(arm):
            if r["kind"] == "typical":
                by_obj[(r["hh"], r["obj"])].append(r)
        deltas = []
        for qs in by_obj.values():
            qs.sort(key=lambda r: r["t"])
            first = next((j for j, r in enumerate(qs) if r["action"] == "resense"), None)
            if first is None or first == 0 or first == len(qs) - 1:
                continue
            deltas.append(np.mean([r["cf_correct"] for r in qs[first + 1:]])
                          - np.mean([r["cf_correct"] for r in qs[:first]]))
        if not deltas:
            continue
        rng = np.random.default_rng(5)
        v = np.array(deltas)
        m = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(3000)]
        mean, lo, hi = v.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)
        y = len(arms) - i
        ax.errorbar([mean], [y], xerr=[[mean - lo], [hi - mean]], fmt="o",
                    ms=9, color=COLORS[arm], capsize=4, lw=2)
        ax.text(-0.62, y, f"{arm} (n={len(deltas)})", va="center", fontsize=10)
    ax.axvline(0, color="#888", lw=1)
    ax.set_yticks([]); ax.set_xlim(-0.65, 0.8)
    ax.set_xlabel("paired within-object delta accuracy (after - before first resense)")
    ax.grid(alpha=0.25, axis="x")
    ax.set_title("F2 - improvement on an object AFTER resensing it (typical; object-clustered 95% CI)\n"
                 "CONFOUNDED BY BASELINE: classical starts at 0.00 (no prior -> uniform over 14 cands),\n"
                 "the LLM at 0.42 (it has a prior). Read F6 for the unconfounded test.", fontsize=9.5)
    fig.tight_layout()
    f = OUT / "F2_before_after.png"
    fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def f3():
    rows = [r for r in rows_of("llm")
            if r.get("verbal_conf") is not None and 0 <= r["verbal_conf"] <= 1]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8))
    ax = axes[0]
    for kind, ls in (("typical", "-"), ("atypical", "--")):
        k = [r for r in rows if r["kind"] == kind]
        xs, ys = [], []
        for th in sorted({round(r["verbal_conf"], 2) for r in k}):
            sel = [r for r in k if r["verbal_conf"] >= th]
            if len(sel) < 15:
                continue
            xs.append(len(sel) / len(k))
            ys.append(1 - np.mean([r["cf_correct"] for r in sel]))
        ax.plot(xs, ys, ls, color=COLORS["llm"], lw=2, label=f"llm {kind}")
    ax.set_xlabel("coverage (fraction answered)")
    ax.set_ylabel("risk (error among answered)")
    ax.grid(alpha=0.25); ax.legend(fontsize=9)
    ax.set_title("ranking: risk falls steeply as coverage drops\n(AUROC 0.75-0.79 - it KNOWS)",
                 fontsize=10)
    ax = axes[1]
    bins = np.linspace(0, 1, 11)
    xs, ys = [], []
    for b0, b1 in zip(bins[:-1], bins[1:]):
        sel = [r for r in rows if b0 <= r["verbal_conf"] < b1]
        if sel:
            xs.append((b0 + b1) / 2)
            ys.append(np.mean([r["cf_correct"] for r in sel]))
    ax.bar(xs, ys, width=0.09, color=COLORS["llm"], alpha=0.6)
    ax.plot([0, 1], [0, 1], "--", color="#888", lw=1)
    all_rows = rows_of("llm")
    rr = np.mean([r["action"] == "resense" for r in all_rows])
    err = 1 - np.mean([r["cf_correct"] for r in all_rows])
    ax.plot([rr], [0.04], "o", ms=13, color=COLORS["llm"], zorder=5)
    ax.annotate(f"actual resense rate {rr:.2f}", (rr, 0.04),
                textcoords="offset points", xytext=(10, 12), fontsize=9)
    ax.plot([err], [0.04], "*", ms=19, color="#222", zorder=5)
    ax.annotate(f"error rate {err:.2f}\n(volume-matched target)", (err, 0.04),
                textcoords="offset points", xytext=(8, -34), fontsize=9)
    ax.set_xlabel("verbalized confidence / rate"); ax.set_ylabel("realized accuracy")
    ax.grid(alpha=0.25); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("level: stated conf above realized acc (ECE 0.18);\n"
                 "dot = how often it looks, star = how often it SHOULD", fontsize=10)
    fig.suptitle("F3 - Capacity A decomposed: the ranking is usable, the level is not",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    f = OUT / "F3_ranking_vs_level.png"
    fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def f4(extra=("llm_selfconf", "llm_v1_pinned")):
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    for arm in ("classical", "llm", "hybrid", "oracle") + tuple(extra):
        rows = rows_of(arm)
        if not rows:
            continue
        for kind, marker in (("typical", "o"), ("atypical", "s")):
            k = [r for r in rows if r["kind"] == kind]
            rr = np.mean([r["action"] == "resense" for r in k])
            err = 1 - np.mean([r["cf_correct"] for r in k])
            ax.scatter([err], [rr], s=90, marker=marker,
                       color=COLORS.get(arm, "#333"), zorder=5)
    for p, col in (("v2", "#b23a48"), ("v3", "#b26e3a")):
        fdev = AOR_OUT / f"rows_llm_dev_devprompt_{p}.jsonl"
        if fdev.exists():
            rows = [json.loads(l) for l in fdev.read_text().splitlines()]
            rr = np.mean([r["action"] == "resense" for r in rows])
            err = 1 - np.mean([r["cf_correct"] for r in rows])
            ax.scatter([err], [rr], s=140, marker="X", color=col, zorder=6)
            ax.annotate(f"prompt {p} (dev)", (err, rr), textcoords="offset points",
                        xytext=(8, 4), fontsize=8.5, color=col)
    ax.plot([0, 1], [0, 1], "--", color="#888", lw=1.2)
    ax.text(0.63, 0.68, "resense = error\n(volume-calibrated)", fontsize=8.5,
            color="#666", rotation=38)
    ax.axhline(B / Q, color="#999", ls=":", lw=1.2)
    ax.text(0.02, B / Q + 0.012, f"global budget ceiling B/Q={B/Q:.2f} "
            "(rates per split; budget shared)", fontsize=8, color="#777")
    for arm in ("classical", "llm", "hybrid", "oracle") + tuple(extra):
        if rows_of(arm):
            ax.scatter([], [], color=COLORS.get(arm, "#333"), label=arm)
    ax.scatter([], [], marker="o", color="#999", label="typical")
    ax.scatter([], [], marker="s", color="#999", label="atypical")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_xlabel("error rate (counterfactual, all queries)")
    ax.set_ylabel("resense rate")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(alpha=0.25)
    ax.set_title("F4 - looking vs erring: below diagonal = under-looking (overconfident),\n"
                 "at ceiling = the KARL abstention trap (dev prompts v2/v3)", fontsize=11)
    fig.tight_layout()
    f = OUT / "F4_resense_vs_error.png"
    fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def f5(arms=("classical", "llm", "hybrid", "llm_selfconf", "llm_v1_pinned", "oracle")):
    arms = [a for a in arms if rows_of(a)]
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.8), sharey=True)
    for ax, kind in zip(axes, ("typical", "atypical")):
        for i, arm in enumerate(arms):
            k = [r for r in rows_of(arm) if r["kind"] == kind]
            n_hh = len({r["hh"] for r in k})
            corr = sum(1.0 for r in k if r["action"] == "answer" and r["correct"]) / n_hh
            res = sum(r["reward"] for r in k if r["action"] == "resense") / n_hh
            wrong_n = sum(1 for r in k if r["action"] == "answer" and not r["correct"]) / n_hh
            ax.bar([i], [corr], color=COLORS[arm], alpha=0.95)
            ax.bar([i], [res], bottom=[corr], color=COLORS[arm], alpha=0.45,
                   hatch="//", edgecolor="white")
            ax.text(i, corr + res + 0.6, f"{wrong_n:.0f} wrong", ha="center",
                    fontsize=8, color="#555")
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels(arms, rotation=20, fontsize=8.5)
        ax.set_title(kind); ax.grid(alpha=0.25, axis="y")
    axes[0].set_ylabel("cumulative reward / household (14 days)\n"
                       "solid = correct answers, hatched = resense credit")
    fig.suptitle("F5 - where the reward comes from: the hybrid converts wrongs into "
                 "resenses without losing corrects", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    f = OUT / "F5_reward_decomposition.png"
    fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f1(); f2(); f3(); f4(); f5()


if __name__ == "__main__":
    main()
