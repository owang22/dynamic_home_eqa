#!/usr/bin/env python3
"""
compare_agents.py — Run the full agent comparison and emit a frontier plot.

Compares:
  1. DeltaThreshold frontier (τ sweep)  — model-free reference curve
  2. LLM world-knowledge agent          — sees household type, time of day,
                                          object context; NO numerical prior

If LLM beats DeltaThreshold at the same resense rate, the model is extracting
useful signal from household context beyond pure staleness.

Output:
  frontier.png  — accuracy vs resense-rate scatter + frontier curve

Usage:
  python scripts/compare_agents.py results/
  python scripts/compare_agents.py results/ --model Qwen/Qwen3-14B-AWQ
  python scripts/compare_agents.py results/ --out my_frontier.png --llm-budget 15
  python scripts/compare_agents.py results/ --skip-llm   # baselines only (instant)

PARTNR WorldGraph mode:
  python scripts/compare_agents.py results/ --use-world-graph --partnr-mode
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT   = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.agents.baselines import DeltaThreshold, AlwaysAnswer, AlwaysResense
from dynamic_home_eqa.agents.harness import run_eval, EvalMetrics

_DEFAULT_MODEL = "Qwen/Qwen3-14B-AWQ"

_TAU_VALUES = [0.13, 0.4, 0.63, 1.13, 1.75, 2.13, 3.13, 4.13, 5.25, 6.5, 8.0]

_DT_BUDGET  = 100_000
_LLM_BUDGET = 100


def _resolve(path: str) -> pathlib.Path:
    p = pathlib.Path(path)
    if not p.is_absolute():
        c = (_DYNAMIC_EQA / p).resolve()
        if c.exists():
            return c
    return p.resolve()


# ──────────────────────────────────────────────────────────────────────────────
# Run all conditions
# ──────────────────────────────────────────────────────────────────────────────

def run_all(
    results_dir: pathlib.Path,
    model: str,
    dt_budget: int,
    llm_budget: int,
    skip_llm: bool,
    use_world_graph: bool = False,
    partnr_mode: bool = False,
) -> dict[str, EvalMetrics]:
    out: dict[str, EvalMetrics] = {}

    print("── DeltaThreshold sweep (uncapped budget) ───────────────────────")
    for tau in _TAU_VALUES:
        key     = f"DeltaThreshold(τ={tau})"
        agent   = DeltaThreshold(tau)
        metrics = run_eval(agent, results_dir, total_budget=dt_budget, with_prior=False)
        out[key] = metrics
        print(f"  τ={tau:<4}  acc={metrics.accuracy:.1%}  resense={metrics.resense_rate:.1%}")

    if skip_llm:
        return out

    label = "LLM-world-knowledge"
    if partnr_mode:
        label += "-partnr"
    print(f"\n── {label} (budget={llm_budget}) ──────────────────────────────────")
    from dynamic_home_eqa.agents.llm_agent import LLMAgent
    agent = LLMAgent(
        model=model,
        use_world_graph=use_world_graph,
        partnr_mode=partnr_mode,
    )
    out[label] = run_eval(
        agent, results_dir, total_budget=llm_budget, with_prior=False
    )
    m = out[label]
    print(f"  acc={m.accuracy:.1%}  resense={m.resense_rate:.1%}")

    return out


# ──────────────────────────────────────────────────────────────────────────────
# Plot
# ──────────────────────────────────────────────────────────────────────────────

def plot_frontier(metrics: dict[str, EvalMetrics], out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np

    LABEL_BBOX = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.9)

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f9f9f9")

    tau_keys = sorted(
        [k for k in metrics if k.startswith("DeltaThreshold")],
        key=lambda k: float(k.split("τ=")[1].rstrip(")")),
    )
    dt_acc     = [metrics[k].accuracy     for k in tau_keys]
    dt_resense = [metrics[k].resense_rate for k in tau_keys]
    taus       = [float(k.split("τ=")[1].rstrip(")")) for k in tau_keys]

    ax.plot(dt_resense, dt_acc, "o--", color="#4878CF", lw=2.0,
            markersize=7, label="DeltaThreshold(τ) frontier", zorder=3)

    annotate_taus = {0.4, 1.13, 2.13, 4.13, 6.5}
    for tau, x, y in zip(taus, dt_resense, dt_acc):
        if tau in annotate_taus:
            ax.annotate(f"τ={tau}", (x, y), textcoords="offset points",
                        xytext=(7, 5), fontsize=10, fontweight="bold",
                        color="#4878CF", bbox=LABEL_BBOX)

    llm_styles = {
        "LLM-world-knowledge":        dict(marker="*", color="#d62728", s=280,
                                           label="LLM (world knowledge)", zorder=5),
        "LLM-world-knowledge-partnr": dict(marker="*", color="#ff7f0e", s=280,
                                           label="LLM (PARTNR mode)", zorder=5),
    }
    for key, style in llm_styles.items():
        if key not in metrics:
            continue
        m = metrics[key]
        ax.scatter([m.resense_rate], [m.accuracy], **style)
        ax.annotate(
            f"{m.accuracy:.0%}",
            (m.resense_rate, m.accuracy),
            textcoords="offset points", xytext=(10, -8),
            fontsize=11, fontweight="bold",
            color=style["color"],
            bbox=LABEL_BBOX,
        )

    ax.set_xlabel("Resense rate", fontsize=13, fontweight="bold")
    ax.set_ylabel("Accuracy",     fontsize=13, fontweight="bold")
    n_questions = sum(m.n_trials for m in list(metrics.values())[:1])
    llm_pts = {k: v for k, v in metrics.items() if "LLM" in k}
    llm_budget_str = ""
    if llm_pts:
        m0 = next(iter(llm_pts.values()))
        llm_budget_str = f" · LLM agent (budget={m0.total_resenses}/{n_questions})"
    ax.set_title(
        f"Dynamic EQA — accuracy vs. resense rate\n"
        f"DeltaThreshold frontier (uncapped budget){llm_budget_str}",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlim(-0.03, 1.05)
    ax.set_ylim(0.0, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.tick_params(labelsize=11)
    ax.grid(True, alpha=0.35)
    ax.legend(loc="lower right", fontsize=11, framealpha=0.9)

    ax.fill_between([0, 0.5], [0.75, 0.75], [1.05, 1.05],
                    alpha=0.05, color="green")
    ax.text(0.02, 0.98, "High accuracy\nLow resense cost",
            transform=ax.transAxes, va="top", ha="left",
            fontsize=10, color="#2ca02c", alpha=0.8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="none", alpha=0.85))

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
    print(f"\nPlot saved → {out_path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────────────────────
# Summary table
# ──────────────────────────────────────────────────────────────────────────────

def print_summary(metrics: dict[str, EvalMetrics]) -> None:
    print("\n" + "═" * 80)
    print(f"{'Agent':<35}  {'Accuracy':>8}  {'Resense':>8}  {'by difficulty'}")
    print("─" * 80)
    for key, m in metrics.items():
        bd  = m.accuracy_by("difficulty")
        row = "  ".join(f"{k}={v:.0%}" for k, v in sorted(bd.items()))
        print(f"{key:<35}  {m.accuracy:>8.1%}  {m.resense_rate:>8.1%}  {row}")
    print("═" * 80)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results_dir")
    ap.add_argument("--model", default=_DEFAULT_MODEL)
    ap.add_argument("--dt-budget", type=int, default=_DT_BUDGET,
                    help="Budget for DeltaThreshold sweep (default: uncapped)")
    ap.add_argument("--llm-budget", type=int, default=_LLM_BUDGET,
                    help="Constrained budget for LLM agent (default: 100)")
    ap.add_argument("--total-budget", type=int, default=None,
                    help="Set both --dt-budget and --llm-budget to this value")
    ap.add_argument("--out", default="frontier.png",
                    help="Output PNG path (default: frontier.png)")
    ap.add_argument("--skip-llm", action="store_true",
                    help="Run baselines only (instant); skip model loading")
    ap.add_argument("--use-world-graph", action="store_true",
                    help="Use WorldGraph.get_world_descr() in LLM prompt (PARTNR mode)")
    ap.add_argument("--partnr-mode", action="store_true",
                    help="Use PARTNR robot/human framing in system prompt")
    ap.add_argument("--save-json", default=None,
                    help="Also save raw metrics as JSON")
    args = ap.parse_args()

    results_dir = _resolve(args.results_dir)
    out_path    = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = (_DYNAMIC_EQA / out_path).resolve()

    dt_budget  = args.total_budget if args.total_budget is not None else args.dt_budget
    llm_budget = args.total_budget if args.total_budget is not None else args.llm_budget

    print(f"Results dir  : {results_dir}")
    print(f"DT budget    : {dt_budget} (uncapped frontier sweep)")
    n_scene_dirs = sum(1 for _ in results_dir.glob("*/questions.json"))
    print(f"LLM budget   : {llm_budget} (~{llm_budget/max(n_scene_dirs,1):.0%} resense cap)")
    print(f"Model        : {args.model if not args.skip_llm else '(skipped)'}")

    metrics = run_all(
        results_dir, args.model, dt_budget, llm_budget, args.skip_llm,
        use_world_graph=args.use_world_graph,
        partnr_mode=args.partnr_mode,
    )
    print_summary(metrics)
    plot_frontier(metrics, out_path)

    if args.save_json:
        summary = {
            k: {"accuracy": m.accuracy, "resense_rate": m.resense_rate}
            for k, m in metrics.items()
        }
        pathlib.Path(args.save_json).write_text(json.dumps(summary, indent=2))
        print(f"Metrics JSON → {args.save_json}")


if __name__ == "__main__":
    main()
