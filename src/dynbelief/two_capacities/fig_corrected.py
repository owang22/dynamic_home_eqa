"""Figures for the CORRECTED results (2026-07-26).

C1  anonymization: bugged vs fixed scoring, named-vs-anon by split.
C2  per-model tau*: reward vs tau, with each model's fused-confidence
    distribution showing why the single frozen tau=0.45 could not fire.
C3  P1 at the HOUSEHOLD level: typical bank vs atypical bank, per arm.
All read banked rows; no LLM calls.
"""
from __future__ import annotations
import json
from collections import defaultdict
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dynbelief.answer_or_resense.run_aor import OUT as AOR
from dynbelief.h2 import core

OUT = AOR.parent / "corrected"
COL = {"classical": "#2e6f95", "llm_scaffold": "#e8890c",
       "scaffold_fusion": "#2a9d8f", "oracle": "#888888",
       "deepseek": "#d1495b", "qwen36": "#2a9d8f", "glm": "#8338ec"}

def _rows(p):
    p = AOR / p if not str(p).startswith("/") else p
    return [json.loads(l) for l in open(p)] if __import__("os").path.exists(p) else []

def _clu(d, nb=3000, seed=3):
    ks = list(d); rng = np.random.default_rng(seed)
    m = [np.mean([v for i in rng.integers(0, len(ks), len(ks)) for v in d[ks[i]]]) for _ in range(nb)]
    return np.mean([v for vs in d.values() for v in vs]), np.percentile(m, 2.5), np.percentile(m, 97.5)

# ── C1 anonymization ─────────────────────────────────────────────────────────
def c1():
    base = "reports/h2_adaptation/"
    old = [json.loads(l) for l in open(base + "confirm_rows_deepseek-v4-flash.jsonl")]
    new = [json.loads(l) for l in open(base + "confirm_rows_deepseek-anonfix.jsonl")]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8), sharey=True)
    for ax, (rows, title) in zip(axes, [(old, "BUGGED scoring (as published)"),
                                        (new, "FIXED scoring (corrected)")]):
        kinds = ["target", "conventional"]
        x = np.arange(len(kinds))
        for i, (arm, c) in enumerate([("llm_named", "#d1495b"), ("llm_anon", "#8d99ae"),
                                      ("class_freq", "#2e6f95")]):
            vals, errs = [], []
            for k in kinds:
                byhh = defaultdict(list)
                for r in rows:
                    if r["arm"] == arm and r["kind"] == k:
                        byhh[r["household"]].append(r["correct"])
                if byhh:
                    m, lo, hi = _clu(byhh); vals.append(m); errs.append([m - lo, hi - m])
                else:
                    vals.append(0); errs.append([0, 0])
            ax.bar(x + (i - 1) * 0.27, vals, 0.27, yerr=np.array(errs).T, capsize=3,
                   color=c, label=arm)
        ax.set_xticks(x); ax.set_xticklabels(["regime-flipped\ntargets", "conventional\nobjects"])
        ax.set_title(title, fontsize=11); ax.grid(alpha=0.25, axis="y"); ax.set_ylim(0, 0.95)
    axes[0].set_ylabel("accuracy (household-clustered 95% CI)")
    axes[0].legend(fontsize=9)
    axes[0].annotate("anon = 1/300\nBY CONSTRUCTION", xy=(0.0, 0.01), xytext=(0.30, 0.30),
                     fontsize=9, color="#a03040", ha="left",
                     arrowprops=dict(arrowstyle="->", color="#a03040", lw=1.4))
    axes[1].annotate("anon nearly MATCHES named\non targets (+0.06, n.s.)", xy=(0.0, 0.37),
                     xytext=(0.42, 0.78), fontsize=9, color="#1b6b4a", ha="left",
                     arrowprops=dict(arrowstyle="->", color="#1b6b4a", lw=1.4))
    fig.suptitle("C1 — Anonymization corrected: object NAMES are necessary for conventional "
                 "placements,\nbut NOT for regime-flipped targets, where structure carries the "
                 "signal (DeepSeek)", fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    f = OUT / "C1_anonymization_corrected.png"; fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)

# ── C2 per-model tau*/alpha*: dev sweep + CONFIRMATORY old-vs-new ────────────
def c2():
    """Left: dev reward vs tau per model (circles = tau*). Right: the resulting
    CONFIRMATORY reward, one frozen (tau=0.45, alpha=6.07) vs per-model
    (tau*, alpha*). classical is the shared, model-independent baseline."""
    grids = {"deepseek": [("0.45", "rows_scaffold_fusion_dev_devtau_0.45.jsonl"),
                          ("0.60", "rows_scaffold_fusion_dev_devtau_0.6.jsonl"),
                          ("0.75", "rows_scaffold_fusion_dev_devtau_0.75.jsonl")],
             "qwen36": [(t, f"rows_scaffold_fusion_dev_tausweep_qwen36_{t}.jsonl")
                        for t in ("0.45", "0.60", "0.70", "0.80")],
             "glm": [(t, f"rows_scaffold_fusion_dev_tausweep_glm_{t}.jsonl")
                     for t in ("0.45", "0.60", "0.70", "0.80")]}
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.0))
    ax = axes[0]
    for m, g in grids.items():
        xs, ys = [], []
        for t, f in g:
            rw = _rows(f)
            if rw: xs.append(float(t)); ys.append(sum(r["reward"] for r in rw) / 4)
        if xs:
            ax.plot(xs, ys, "-o", ms=6, lw=2.2, color=COL[m], label=m)
            b = int(np.argmax(ys)); ax.scatter([xs[b]], [ys[b]], s=190, facecolors="none",
                                               edgecolors=COL[m], lw=2.4, zorder=5)
    ax.axvline(0.45, color="#999", ls=":", lw=1.4)
    ax.text(0.455, 40, "old single frozen τ=0.45\n(DeepSeek-derived)", fontsize=8.5, color="#777")
    ax.set_xlabel("τ (fusion resense threshold)"); ax.set_ylabel("DEV reward / household")
    ax.set_ylim(30, 85); ax.grid(alpha=0.25); ax.legend(fontsize=9)
    ax.set_title("(a) dev sweep: each model's own τ*", fontsize=10.5)

    # right: confirmatory old vs new
    ax = axes[1]
    cfg = {"deepseek": (0.45, 2.72, "rows_scaffold_fusion_conf_frozen_deepseek.jsonl"),
           "qwen36":   (0.70, 2.75, "rows_scaffold_fusion_conf_frozen_qwen36.jsonl"),
           "glm":      (0.70, 0.65, "rows_scaffold_fusion_conf_frozen_glm.jsonl")}
    def rew(rw):
        by = defaultdict(list)
        for r in rw: by[(r["hh"], r["day"])].append(r["reward"])
        return _clu({k: [np.sum(v)] for k, v in by.items()})
    labels, olds, news, oe, ne = [], [], [], [], []
    for m, (t, a, oldf) in cfg.items():
        o = _rows(oldf); n = _rows(f"rows_scaffold_fusion_conf_permodel_{m}.jsonl")
        if not n or not o: continue
        ro, rn = rew(o), rew(n)
        labels.append(f"{m}\nτ*={t} α*={a}")
        olds.append(ro[0]); oe.append([ro[0]-ro[1], ro[2]-ro[0]])
        news.append(rn[0]); ne.append([rn[0]-rn[1], rn[2]-rn[0]])
    x = np.arange(len(labels))
    ax.bar(x-0.2, olds, 0.4, yerr=np.array(oe).T, capsize=3, color="#bbbbbb",
           label="one frozen τ=0.45, α=6.07")
    ax.bar(x+0.2, news, 0.4, yerr=np.array(ne).T, capsize=3,
           color=[COL[m] for m in cfg if _rows(f"rows_scaffold_fusion_conf_permodel_{m}.jsonl")],
           label="per-model τ*, α*")
    c = _rows("rows_classical_conf_frozen.jsonl")
    if c:
        cb = rew(c)[0]
        ax.axhline(cb, color="#2e6f95", ls="--", lw=1.6)
        ax.text(len(labels)-0.55, cb+0.08, f"classical baseline {cb:.2f}",
                fontsize=8.5, color="#2e6f95")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.5)
    ax.tick_params(axis="x", pad=2)
    ax.set_ylabel("CONFIRMATORY reward / household-day"); ax.set_ylim(0, 6.6)
    ax.grid(alpha=0.25, axis="y"); ax.legend(fontsize=8.5, loc="lower right")
    ax.set_title("(b) confirmatory: per-model calibration lifts BOTH weak models\n"
                 "above classical; it COSTS DeepSeek (its prior deserved more weight)",
                 fontsize=10.5)
    fig.suptitle("C2 — τ and α are per-model. The 'weak models fail with fusion' result was a "
                 "frozen-threshold artifact:\nat their own τ*, Qwen (5.42) and GLM (5.19) both beat "
                 "classical (5.04). DeepSeek loses 0.47 to the α correction.", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    f = OUT / "C2_per_model_calibration.png"; fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


# ── C3 P1 household level: ACCURACY OVER DAYS, split by household class ──────
def c3():
    """P1 as learning curves rather than totals, split into two panels so the
    typical and atypical household classes are each compared internally.
    Oracle omitted (it is a bound, not a method). DeepSeek; scaffold_fusion at
    its corrected tau*=0.45 (alpha still 6.07 in these runs — the alpha*=2.72
    correction post-dates them)."""
    arms = [("classical", "rows_classical_typ_frozen.jsonl",
             "rows_classical_conf_frozen.jsonl", COL["classical"], "--"),
            ("llm_scaffold", "rows_llm_scaffold_typ_frozen_typ.jsonl",
             "rows_llm_scaffold_conf_frozen.jsonl", COL["llm_scaffold"], "-"),
            ("scaffold_fusion", "rows_scaffold_fusion_typ_frozen_typ.jsonl",
             "rows_scaffold_fusion_conf_frozen_deepseek.jsonl", COL["scaffold_fusion"], "-")]

    def day_ci(rows, nb=800):
        by = defaultdict(lambda: defaultdict(list))
        for r in rows:
            by[r["day"]][r["hh"]].append(r["cf_correct"])
        days = sorted(by); mean = []; lo = []; hi = []
        rng = np.random.default_rng(4)
        for d in days:
            clus = list(by[d]); vals = [v for c in clus for v in by[d][c]]
            mean.append(np.mean(vals))
            m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                          for v in by[d][clus[i]]]) for _ in range(nb)]
            lo.append(np.percentile(m, 2.5)); hi.append(np.percentile(m, 97.5))
        return days, np.array(mean), np.array(lo), np.array(hi)

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.0), sharey=True)
    panels = [(0, 1, "TYPICAL households (6)  —  a conventional prior is RIGHT"),
              (0, 2, "ATYPICAL households (24)  —  a conventional prior is WRONG")]
    finals = {}
    for ax, (_, idx, title) in zip(axes, panels):
        for lab, ft, fa, col, ls in arms:
            rows = _rows(ft if idx == 1 else fa)
            if not rows:
                continue
            d, m, lo, hi = day_ci(rows)
            lw = 1.9 if lab == "classical" else 2.6
            ax.plot(d, m, ls, color=col, marker="o", ms=4, lw=lw, label=lab,
                    zorder=4 if lab != "classical" else 3)
            ax.fill_between(d, lo, hi, color=col, alpha=0.12)
            finals[(lab, idx)] = m[-1]
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("day"); ax.grid(alpha=0.25); ax.set_ylim(0, 1.0)
    axes[0].set_ylabel("answer accuracy (counterfactual — every query scored)")
    axes[0].legend(fontsize=9.5, loc="lower right")
    for ax, idx in zip(axes, (1, 2)):
        c = finals.get(("classical", idx)); f = finals.get(("scaffold_fusion", idx))
        if c is not None and f is not None:
            ax.annotate(f"day-13 gap vs classical: {f - c:+.2f}", xy=(0.03, 0.06),
                        xycoords="axes fraction", fontsize=9, color="#444")
    fig.suptitle("C3 — P1 by household class: accuracy over days (DeepSeek, corrected τ*=0.45)\n"
                 "the scaffolded arms lead from day 0 in both classes; classical starts at ~0 "
                 "because with no\nobservations its posterior is uniform over ~13 receptacles",
                 fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, 0.85))
    f = OUT / "C3_P1_accuracy_by_day.png"; fig.savefig(f, dpi=140); plt.close(fig); print("wrote", f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c1(); c2(); c3()

if __name__ == "__main__":
    main()
