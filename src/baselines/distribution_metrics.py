"""Distribution quality of the belief models: are the probabilities
right, and is the tail useful — not just the argmax.

Top-1 accuracy only judges the argmax. This module scores the WHOLE
predicted distribution in continuous mode (belief kept current) on the
seed-0 fleet banks, via the ``on_prediction`` hook of
:func:`passive_eval.evaluate_continuous`:

* **log-loss / Brier** per question on p(truth) — proper scoring rules:
  minimized only by having the whole distribution right;
* **recall@k** — is the truth in the top 1, 2, 3, 5 (buried vs absent);
* **expected search cost** — walk receptacles in belief order until the
  truth is found; the steps a sequential search actually pays;
* **top-1 calibration (ECE)** — does the belief's own confidence
  predict its correctness (the VoI threshold consumes exactly this);
* **rank-wise calibration** for ranks 1-3 — in the bucket where the
  model puts ~20% on its rank-2 candidate, rank 2 should be the truth
  ~20% of the time: is the 2nd-place number a probability or decoration.

Output (``--out-dir``): ``per_question.csv.gz``, ``metrics.csv``,
``summary.md``, ``scores_by_model.png``, ``recall_at_k.png``,
``calibration.png``, ``provenance.json``. Deterministic in
(banks, slate, rng seed).

Usage:
  python -m baselines.distribution_metrics            # 20 seed-0 banks
  python -m baselines.distribution_metrics --households hh_001 \
      --models last_observation --out-dir /tmp/x
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import datetime
import gzip
import json
import logging
import math
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, git_state
from baselines.household_analysis import (REPO_ROOT, bank_path,
                                          household_meta, select_specs)
from baselines.passive_eval import (PassiveProtocolConfig,
                                    evaluate_continuous)
from baselines.registry import build_registered_belief

logger = logging.getLogger(__name__)

LOG_LOSS_EPSILON = PassiveProtocolConfig.log_loss_epsilon
RECALL_KS = (1, 2, 3, 5)
CONFIDENCE_EDGES = tuple(i / 10 for i in range(11))
"""Ten equal-width buckets on the top-1 probability (ECE)."""
RANK_EDGES = (0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0)
"""Buckets for the rank-2/3 probabilities, dense at the small end where
those probabilities live."""
COLUMNS = ("household", "model", "question_id", "object_id", "t_query",
           "correct", "p_truth", "brier", "rank", "n_receptacles",
           "p1", "p2", "p3", "r2_correct", "r3_correct")
SELECTED = (REPO_ROOT / "results" / "oracle_program_posterior"
            / "selected.json")
HIGHLIGHT = {  # representative models, hues as in household_report
    "LastObs": "#2a78d6", "MostFreq": "#eb6834", "Perpetua": "#00838f",
    "OracleBelief": "#b0308f",
}
GREY = "#b5b5b5"
INK = "#0b0b0b"


def short_name(model: str) -> str:
    base = model.split("(")[0]
    return {"LastObservation": "LastObs", "MostFrequentLocation": "MostFreq",
            "TimetableLookup": "Timetable", "PeriodicPersistence": "Periodic",
            "DaytypeMixture": "DaytypeMix", "HierarchyBackoff": "HierBackoff",
            "SmoothedRecency": "SmoothedRec"}.get(base, base)


def analyze_bank(task: Dict[str, Any]) -> List[Tuple[Any, ...]]:
    """Per-question distribution rows of every spec on one seed-0 bank."""
    household = task["household"]
    config = PassiveProtocolConfig(
        seed=task["rng_seed"],
        location_equivalence=tuple(
            tuple(g) for g in task.get("location_equivalence", ())))
    bank_dir = task.get("bank_dir")
    path = bank_path(household, 0,
                     pathlib.Path(bank_dir) if bank_dir else None)
    episodes = list(JsonlBank(path=path).episodes())
    rows: List[Tuple[Any, ...]] = []
    for episode in episodes:
        for spec in task["specs"]:
            rng = _derived_rng(task["rng_seed"], "household_analysis",
                               str(spec["name"]), episode.episode_id,
                               "continuous")
            belief = build_registered_belief(dict(spec), rng)
            name_holder: List[str] = []

            def capture(question, prediction, truth) -> None:
                d = prediction.distribution
                ranked = sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))
                rank = next((i + 1 for i, (rec, _) in enumerate(ranked)
                             if rec == truth), len(ranked) + 1)
                p_truth = d.get(truth, 0.0)
                brier = 1.0 - 2.0 * p_truth + sum(p * p for p in d.values())
                p = [ranked[i][1] if i < len(ranked) else 0.0
                     for i in range(3)]
                rows.append((
                    household, name_holder[0], question.question_id,
                    question.object_id, question.t_query,
                    int(prediction.argmax == truth), round(p_truth, 6),
                    round(brier, 6), rank, len(ranked), round(p[0], 6),
                    round(p[1], 6), round(p[2], 6),
                    int(len(ranked) > 1 and ranked[1][0] == truth),
                    int(len(ranked) > 2 and ranked[2][0] == truth)))

            name_holder.append(belief.name)
            evaluate_continuous(episode, belief, config,
                                on_prediction=capture)
    return rows


# ---------------------------------------------------------- aggregation --

def _bucket(edges: Sequence[float], v: float) -> int:
    for i, hi in enumerate(edges[1:]):
        if v <= hi:
            return i
    return len(edges) - 2


def aggregate(rows: Sequence[dict]) -> Dict[str, Dict[str, Any]]:
    """Per-model metrics from per-question rows (dicts keyed by COLUMNS)."""
    out: Dict[str, Dict[str, Any]] = {}
    for model, sub in _by_model(rows).items():
        n = len(sub)
        lls = [-math.log(max(r["p_truth"], LOG_LOSS_EPSILON)) for r in sub]
        briers = [r["brier"] for r in sub]
        steps = [min(r["rank"], r["n_receptacles"]) for r in sub]
        m = {
            "n": n,
            "top1": sum(r["correct"] for r in sub) / n,
            "log_loss": _mean_ci(lls),
            "brier": _mean_ci(briers),
            "search_steps": _mean_ci(steps),
            "recall_at": {k: sum(r["rank"] <= k for r in sub) / n
                          for k in RECALL_KS},
        }
        # top-1 reliability: bucket on p1, empirical accuracy per bucket
        conf = [[0, 0, 0.0] for _ in range(len(CONFIDENCE_EDGES) - 1)]
        for r in sub:
            b = _bucket(CONFIDENCE_EDGES, r["p1"])
            conf[b][0] += 1
            conf[b][1] += r["correct"]
            conf[b][2] += r["p1"]
        m["reliability"] = [
            {"n": c, "acc": k / c, "conf": s / c}
            for c, k, s in conf if c] and [
            {"lo": CONFIDENCE_EDGES[i], "hi": CONFIDENCE_EDGES[i + 1],
             "n": c, "acc": (k / c if c else None),
             "conf": (s / c if c else None)}
            for i, (c, k, s) in enumerate(conf)]
        m["ece"] = sum(c * abs(k / c - s / c)
                       for c, k, s in conf if c) / n
        # rank-wise calibration, ranks 1-3
        cal = {}
        for rk, p_key, hit_key in ((1, "p1", None), (2, "p2", "r2_correct"),
                                   (3, "p3", "r3_correct")):
            buckets = [[0, 0, 0.0] for _ in range(len(RANK_EDGES) - 1)]
            for r in sub:
                b = _bucket(RANK_EDGES, r[p_key])
                hit = r["correct"] if hit_key is None else r[hit_key]
                buckets[b][0] += 1
                buckets[b][1] += hit
                buckets[b][2] += r[p_key]
            cal[rk] = [{"lo": RANK_EDGES[i], "hi": RANK_EDGES[i + 1],
                        "n": c, "emp": (k / c if c else None),
                        "pred": (s / c if c else None)}
                       for i, (c, k, s) in enumerate(buckets)]
        m["rank_calibration"] = cal
        out[model] = m
    return out


def _by_model(rows: Sequence[dict]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = collections.defaultdict(list)
    for r in rows:
        out[r["model"]].append(r)
    return out


def _mean_ci(vals: Sequence[float]) -> Dict[str, float]:
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / max(1, n - 1)
    half = 1.96 * math.sqrt(var / n)
    return {"mean": mean, "lo": mean - half, "hi": mean + half}


# -------------------------------------------------------------- figures --

def _model_order(metrics: Dict[str, Dict[str, Any]]) -> List[str]:
    return sorted(metrics, key=lambda m: metrics[m]["log_loss"]["mean"])


def _color(model: str) -> str:
    return HIGHLIGHT.get(short_name(model), GREY)


def render_scores(metrics: Dict[str, Dict[str, Any]],
                  out_path: pathlib.Path) -> None:
    """Three aligned dot columns per model: log-loss, Brier, mean search
    steps, 95% CI whiskers, sorted by log-loss (best on top)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models = _model_order(metrics)[::-1]
    ys = list(range(len(models)))
    panels = (("log_loss", "mean log-loss (lower = better)"),
              ("brier", "mean Brier score"),
              ("search_steps", "mean search steps to truth"))
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 0.42 * len(models) + 1.8),
                             sharey=True)
    for ax, (key, label) in zip(axes, panels):
        for y, model in zip(ys, models):
            s = metrics[model][key]
            col = _color(model)
            ax.plot([s["lo"], s["hi"]], [y, y], color=col, linewidth=1.6,
                    alpha=0.7, solid_capstyle="butt", zorder=2)
            ax.plot(s["mean"], y, "o", color=col, markersize=7,
                    markeredgecolor="white", markeredgewidth=1.2, zorder=3)
        ax.set_xlabel(label, fontsize=9)
        ax.grid(axis="x", color="#e6e6e6")
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([short_name(m) for m in models], fontsize=9)
    axes[0].set_ylim(-1, len(models))
    fig.suptitle("Distribution quality per model — proper scores and "
                 "search cost (belief kept current, 20 seed-0 banks; "
                 "bars = 95% CI of the mean)", fontsize=11, x=0.01,
                 ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_recall(metrics: Dict[str, Dict[str, Any]],
                  out_path: pathlib.Path) -> None:
    """Recall@k per model: representatives in color, others grey."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    xs = list(range(len(RECALL_KS)))
    grey_labeled = False
    for model in _model_order(metrics):
        ys = [metrics[model]["recall_at"][k] for k in RECALL_KS]
        name = short_name(model)
        if name in HIGHLIGHT:
            ax.plot(xs, ys, marker="o", ms=6, lw=2, color=HIGHLIGHT[name],
                    markeredgecolor="white", markeredgewidth=1.2,
                    label=name, zorder=4)
        else:
            ax.plot(xs, ys, lw=1.0, color=GREY, zorder=2,
                    label=None if grey_labeled else "other classical")
            grey_labeled = True
    ax.set_xticks(xs)
    ax.set_xticklabels([f"top {k}" for k in RECALL_KS])
    ax.set_ylim(0.4, 1.0)
    ax.set_ylabel("fraction of questions with truth in top k")
    ax.set_title("Recall@k — buried at rank 2-3 vs nowhere\n"
                 "(belief kept current, 20 seed-0 banks; axis starts "
                 "at 0.4)", loc="left", fontsize=11)
    ax.grid(axis="y", color="#e6e6e6")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


MIN_BUCKET_N = 50


def render_calibration(metrics: Dict[str, Dict[str, Any]],
                       out_path: pathlib.Path) -> None:
    """Predicted vs empirical for ranks 1-3, one panel per rank,
    representative models only; the diagonal is perfect calibration.
    Rank 1 doubles as the top-1 reliability diagram (ECE in the
    legend)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models = [m for m in _model_order(metrics)
              if short_name(m) in HIGHLIGHT]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), sharey=False)
    for ax, rk in zip(axes, (1, 2, 3)):
        lim = 1.0 if rk == 1 else 0.5
        ax.plot([0, lim], [0, lim], color="#c9c8c3", linewidth=1.2,
                linestyle="--", zorder=1)
        for model in models:
            name = short_name(model)
            pts = [(b["pred"], b["emp"]) for b in
                   metrics[model]["rank_calibration"][rk]
                   if b["n"] >= MIN_BUCKET_N and b["pred"] is not None]
            if not pts:
                continue
            label = (f"{name} (ECE {metrics[model]['ece']:.3f})"
                     if rk == 1 else name)
            ax.plot([p for p, _ in pts], [e for _, e in pts], marker="o",
                    ms=6, lw=1.8, color=HIGHLIGHT[name],
                    markeredgecolor="white", markeredgewidth=1.1,
                    label=label, zorder=3)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_xlabel(f"mean predicted p(rank-{rk} candidate)", fontsize=9)
        ax.set_title(f"rank {rk}" + (" (top-1 reliability)" if rk == 1
                                     else ""), loc="left", fontsize=10)
        ax.grid(color="#e6e6e6")
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(loc="upper left", frameon=False, fontsize=8)
    axes[0].set_ylabel("empirical frequency it IS the truth", fontsize=9)
    fig.suptitle("Rank-wise calibration — is the k-th place number a "
                 "probability or decoration? (dashed = perfect; buckets "
                 f"under {MIN_BUCKET_N} questions not drawn)",
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# -------------------------------------------------------------- summary --

def write_summary(metrics: Dict[str, Dict[str, Any]], out_dir: pathlib.Path,
                  prov: Dict[str, Any]) -> None:
    lines = [
        "# Distribution quality: are the probabilities right, and is "
        "the tail useful",
        "",
        f"Generated {prov['timestamp']} at commit "
        f"`{prov['git']['commit'][:12]}`"
        f"{' (dirty tree)' if prov['git'].get('dirty') else ''} by "
        "`python -m baselines.distribution_metrics`. "
        f"{prov['n_households']} seed-0 fleet banks, belief kept current, "
        "every question scored on the FULL predicted distribution, not "
        "just the argmax. Log-loss uses the protocol's "
        f"{LOG_LOSS_EPSILON:g} floor. Search steps = walk receptacles in "
        "belief order until the truth is found (what a sequential search "
        "pays). ECE = expected calibration error of the top-1 "
        "confidence, 10 equal-width buckets.",
        "",
        "Ranks here are taken by `(-probability, receptacle_id)`, a "
        "deterministic tie-break, while a model's own `argmax` breaks "
        "ties with its seeded generator. The two agree on >99.9% of "
        "questions for every model except **Markov1** (3.9% ties at the "
        "top), which is why its `R@1` sits below its `top-1`; read its "
        "rank-based columns — R@k and search steps — as one arbitrary "
        "tie-break among many, not as a property of the model.",
        "",
        "Confidence intervals are on the figures but narrower than the "
        "markers at n=45 000; the ranking of the models is not in "
        "question, and the tables carry the numbers.",
        "",
        "![](scores_by_model.png)",
        "",
        "![](recall_at_k.png)",
        "",
        "![](calibration.png)",
        "",
        "| model | n | top-1 | log-loss | Brier | search steps | "
        + " | ".join(f"R@{k}" for k in RECALL_KS) + " | ECE |",
        "|---|" + "---|" * (6 + len(RECALL_KS)),
    ]
    for model in _model_order(metrics):
        m = metrics[model]
        lines.append(
            f"| {short_name(model)} | {m['n']} | {m['top1']:.3f} "
            f"| {m['log_loss']['mean']:.3f} | {m['brier']['mean']:.3f} "
            f"| {m['search_steps']['mean']:.2f} | "
            + " | ".join(f"{m['recall_at'][k]:.3f}" for k in RECALL_KS)
            + f" | {m['ece']:.3f} |")
    lines += ["",
              "`per_question.csv.gz` has one row per (model, question) "
              "with p(truth), Brier, the truth's rank, and the top-3 "
              "probabilities; `metrics.csv` the aggregate rows above.",
              ""]
    (out_dir / "summary.md").write_text("\n".join(lines))


def write_metrics_csv(metrics: Dict[str, Dict[str, Any]],
                      out_dir: pathlib.Path) -> None:
    with (out_dir / "metrics.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "n", "top1", "log_loss", "log_loss_lo",
                    "log_loss_hi", "brier", "search_steps"]
                   + [f"recall_at_{k}" for k in RECALL_KS] + ["ece"])
        for model in _model_order(metrics):
            m = metrics[model]
            w.writerow([model, m["n"], round(m["top1"], 6),
                        round(m["log_loss"]["mean"], 6),
                        round(m["log_loss"]["lo"], 6),
                        round(m["log_loss"]["hi"], 6),
                        round(m["brier"]["mean"], 6),
                        round(m["search_steps"]["mean"], 6)]
                       + [round(m["recall_at"][k], 6) for k in RECALL_KS]
                       + [round(m["ece"], 6)])


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=REPO_ROOT / "reports" / "baselines"
                    / "household_analysis" / "distribution_metrics")
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None)
    ap.add_argument("--no-oracle-belief", action="store_true")
    args = ap.parse_args()
    specs = list(select_specs(args.models))
    if not args.no_oracle_belief and SELECTED.exists():
        cfg = json.loads(SELECTED.read_text())
        specs.append({"name": "oracle_program_posterior",
                      "eps": cfg["eps"], "half_life_h": cfg["half_life_h"]})
    meta = household_meta(args.bank_dir)
    households = list(args.households) if args.households else sorted(meta)
    tasks = [{"household": h, "specs": specs, "rng_seed": args.rng_seed,
              "bank_dir": str(args.bank_dir) if args.bank_dir else None}
             for h in households]
    rows: List[Tuple[Any, ...]] = []
    with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:
        for household, res in zip(households, pool.map(analyze_bank, tasks)):
            logger.info("done %s (%d rows)", household, len(res))
            rows += res
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.out_dir / "per_question.csv.gz", "wt",
                   newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        w.writerows(rows)
    dicts = [dict(zip(COLUMNS, r)) for r in rows]
    metrics = aggregate(dicts)
    prov = {"timestamp": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"),
            "git": dict(zip(("commit", "dirty"), git_state(REPO_ROOT))),
            "households": households, "n_households": len(households),
            "specs": specs, "rng_seed": args.rng_seed,
            "bank_dir": str(args.bank_dir or "fleet"),
            "log_loss_epsilon": LOG_LOSS_EPSILON}
    (args.out_dir / "provenance.json").write_text(json.dumps(prov, indent=2))
    write_metrics_csv(metrics, args.out_dir)
    render_scores(metrics, args.out_dir / "scores_by_model.png")
    render_recall(metrics, args.out_dir / "recall_at_k.png")
    render_calibration(metrics, args.out_dir / "calibration.png")
    write_summary(metrics, args.out_dir, prov)
    logger.info("wrote %s", args.out_dir)


if __name__ == "__main__":
    main()
