"""Answer-or-Resense evaluation: P1-P4 verdicts, risk-coverage, resense-rate
trajectories (KARL-trap check), calibration-in-action, verbalized-confidence ECE.

All metrics day-clustered (bootstrap over (hh, day) clusters), typical/atypical
split, staggered phases pooled (offsets balanced by construction).
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.answer_or_resense.run_aor import OUT

ARMS = ["classical", "llm", "hybrid", "llm_thresh", "oracle"]
COLORS = {"classical": "#2e6f95", "llm": "#d1495b", "hybrid": "#2a9d8f",
          "llm_thresh": "#9b5de5", "oracle": "#666666"}


def _rows(arm, bank, tag):
    fs = sorted(glob.glob(str(OUT / f"rows_{arm}_{bank}_{tag}.jsonl")))
    rows = []
    for f in fs:
        rows += [json.loads(l) for l in open(f)]
    return rows


def _clu_boot(vals_by_clu, nb=3000, seed=3):
    clus = list(vals_by_clu)
    if not clus:
        return (float("nan"),) * 3
    rng = np.random.default_rng(seed)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                  for v in vals_by_clu[clus[i]]]) for _ in range(nb)]
    allv = [v for vs in vals_by_clu.values() for v in vs]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def reward_table(data, kinds=("typical", "atypical", None)):
    print("\n== cumulative reward per household-day (day-clustered 95% CI) ==")
    for kind in kinds:
        lab = kind or "ALL"
        print(f"  [{lab}]")
        for arm, rows in data.items():
            by = defaultdict(list)
            for r in rows:
                if kind and r["kind"] != kind:
                    continue
                by[(r["hh"], r["day"])].append(r["reward"])
            per_day = {k: [np.sum(v)] for k, v in by.items()}
            m, lo, hi = _clu_boot(per_day)
            print(f"    {arm:11s} {m:.2f} [{lo:.2f},{hi:.2f}] /query-group-day")


def accuracy_split(data):
    print("\n== answered-query accuracy (selective), typical vs atypical ==")
    for arm, rows in data.items():
        parts = []
        for kind in ("typical", "atypical"):
            a = [r["correct"] for r in rows if r["kind"] == kind and r["action"] == "answer"]
            cov = np.mean([r["action"] == "answer" for r in rows if r["kind"] == kind])
            parts.append(f"{kind[:4]} acc={np.mean(a):.2f} cov={cov:.2f}")
        print(f"    {arm:11s} " + " | ".join(parts))


def resense_trajectory(data, B, Q, fname):
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), sharey=True)
    for ax, kind in zip(axes, ("typical", "atypical")):
        for arm, rows in data.items():
            by = defaultdict(list)
            for r in rows:
                if r["kind"] == kind:
                    by[r["day"]].append(r["action"] == "resense")
            days = sorted(by)
            ax.plot(days, [np.mean(by[d]) for d in days], "-o", ms=4,
                    color=COLORS[arm], label=arm)
        ax.axhline(B / Q, color="#999", ls=":", lw=1.2)
        ax.text(0.3, B / Q + 0.015, f"budget ceiling B/Q={B/Q:.2f}", fontsize=8, color="#777")
        ax.set_title(f"{kind} queries"); ax.set_xlabel("day")
        ax.grid(alpha=0.25); ax.set_ylim(-0.02, min(1.0, B / Q * 2.2))
    axes[0].set_ylabel("resense rate")
    axes[0].legend(fontsize=8.5)
    fig.suptitle("Resense rate over days (KARL-trap check: pinned-at-ceiling = "
                 "over-resensing; ~0 with high error = overconfidence)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / fname, dpi=140)
    print("wrote", OUT / fname)
    # KARL flags
    for arm, rows in data.items():
        rr = np.mean([r["action"] == "resense" for r in rows])
        if rr > 0.92 * (B / Q):
            print(f"  KARL FLAG: {arm} resense rate {rr:.2f} pinned at ceiling {B/Q:.2f}")


def calibration_in_action(data):
    """P(wrong | answered) vs resense rate — overconfidence = high error while
    rarely resensing. Uses cf_correct (counterfactual) for resensed queries."""
    print("\n== calibration-in-action ==")
    out = {}
    for arm, rows in data.items():
        for kind in ("typical", "atypical"):
            k = [r for r in rows if r["kind"] == kind]
            ans = [r for r in k if r["action"] == "answer"]
            p_wrong_ans = 1 - np.mean([r["correct"] for r in ans]) if ans else float("nan")
            rr = np.mean([r["action"] == "resense" for r in k])
            # counterfactual: would the resensed queries' answers have been wrong?
            res = [r for r in k if r["action"] == "resense"]
            p_wrong_res = 1 - np.mean([r["cf_correct"] for r in res]) if res else float("nan")
            out[(arm, kind)] = (p_wrong_ans, rr, p_wrong_res)
            print(f"    {arm:11s} {kind[:4]}: P(wrong|answered)={p_wrong_ans:.2f}  "
                  f"resense_rate={rr:.2f}  P(wrong|resensed,cf)={p_wrong_res:.2f}")
    return out


def risk_coverage(data, fname):
    """Sweep a confidence threshold post-hoc over each arm's logged conf:
    coverage = frac answered, risk = error rate among answered."""
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), sharey=True)
    for ax, kind in zip(axes, ("typical", "atypical")):
        for arm, rows in data.items():
            k = [r for r in rows if r["kind"] == kind and r.get("conf") is not None]
            if not k:
                continue
            confs = sorted({round(r["conf"], 2) for r in k})
            xs, ys = [], []
            for th in confs:
                sel = [r for r in k if r["conf"] >= th]
                if len(sel) < 10:
                    continue
                xs.append(len(sel) / len(k))
                ys.append(1 - np.mean([r["cf_correct"] for r in sel]))
            ax.plot(xs, ys, "-", color=COLORS[arm], lw=1.8, label=arm)
        ax.set_title(f"{kind} queries"); ax.set_xlabel("coverage (fraction answered)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("risk (error rate among answered)")
    axes[0].legend(fontsize=8.5)
    fig.suptitle("Risk-coverage (selective prediction), by arm's internal confidence", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / fname, dpi=140)
    print("wrote", OUT / fname)


def ece_verbalized(data):
    print("\n== ECE of the LLM's VERBALIZED confidence (answered queries) ==")
    for arm in ("llm", "hybrid", "llm_thresh"):
        rows = [r for r in data.get(arm, []) if r.get("verbal_conf") is not None
                and r["action"] == "answer"]
        if not rows:
            continue
        bins = np.linspace(0, 1, 11)
        ece, n_tot = 0.0, len(rows)
        for b0, b1 in zip(bins[:-1], bins[1:]):
            sel = [r for r in rows if b0 <= r["verbal_conf"] < b1]
            if not sel:
                continue
            acc = np.mean([r["correct"] for r in sel])
            conf = np.mean([r["verbal_conf"] for r in sel])
            ece += len(sel) / n_tot * abs(acc - conf)
        mean_c = np.mean([r["verbal_conf"] for r in rows])
        mean_a = np.mean([r["correct"] for r in rows])
        print(f"    {arm:11s} ECE={ece:.3f}  mean verbal conf {mean_c:.2f} vs acc {mean_a:.2f}"
              f"  ({'OVERconfident' if mean_c > mean_a + 0.05 else 'ok/under'})")


def learning_curve(data, fname):
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), sharey=True)
    for ax, kind in zip(axes, ("typical", "atypical")):
        for arm, rows in data.items():
            by = defaultdict(list)
            for r in rows:
                if r["kind"] == kind:
                    by[r["day"]].append(r["cf_correct"])   # answer quality, incl. cf
            days = sorted(by)
            ax.plot(days, [np.mean(by[d]) for d in days], "-o", ms=4,
                    color=COLORS[arm], label=arm)
        ax.set_title(f"{kind} queries"); ax.set_xlabel("day")
        ax.grid(alpha=0.25); ax.set_ylim(0, 1)
    axes[0].set_ylabel("answer accuracy (incl. counterfactual)")
    axes[0].legend(fontsize=8.5)
    fig.suptitle("Learning under self-gathered data (scarce mode): accuracy vs day", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / fname, dpi=140)
    print("wrote", OUT / fname)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="conf")
    ap.add_argument("--tag", required=True, help="cfg tag glob, e.g. 'Q6_B2_r0.4_w0.0*'")
    ap.add_argument("--B", type=int, default=2)
    ap.add_argument("--Q", type=int, default=6)
    args = ap.parse_args()
    data = {}
    for arm in ARMS:
        rows = _rows(arm, args.bank, args.tag)
        if rows:
            data[arm] = rows
    print("arms loaded:", {a: len(r) for a, r in data.items()})
    reward_table(data)
    accuracy_split(data)
    calibration_in_action(data)
    ece_verbalized(data)
    resense_trajectory(data, args.B, args.Q, f"resense_rate_{args.bank}.png")
    risk_coverage(data, f"risk_coverage_{args.bank}.png")
    learning_curve(data, f"learning_curve_{args.bank}.png")


if __name__ == "__main__":
    main()
