"""Value-of-information study: the two VoI policies on the representative
grid, against ResolvableMassSense and conformal-global at their best
configurations from ``results/conformal_sweep_v2/``.

Stages (``--stage``; outputs under ``--out``, default
``results/voi_policies/``):

  grid     calibration pairs (one passive walk per belief on the
           calibration households; the global conformal tables are refit
           from them and checked against the reference sweep's stored
           quantiles where the belief was in it), then every cell on the
           test households: NeverSense, SequentialSearch, VoIThresholdSense
           at lambda in {0.01, 0.02, 0.05, 0.1, 0.2, 0.3} under the budget
           caps (fixed-budget mode) and with the cap disabled (soft-budget
           mode), VoIBudgetPriceSense at gamma in {0.01, 0.05, 0.1}, and
           one line each for ResolvableMassSense and conformal-global at
           the reference sweep's best (alpha, tau) / alpha for that belief
           and budget (beliefs the reference sweep did not run get the
           configuration most of its beliefs preferred at that budget, and
           the findings say so) -> ``grid.csv``, ``accuracy_by_day.csv``,
           question dumps.
  report   ``frontier.png`` (accuracy against senses per question, both
           modes, per belief) and ``findings.md``: raw deltas of the VoI
           policies against the two comparators per (belief, budget),
           whether the price policy moves budget toward hard questions
           (senses per question binned by the belief's confidence at the
           first decision, against SequentialSearch), and the oracle-belief
           ceiling question when OracleBelief is in the grid.

Usage:
  PYTHONPATH=src python -m baselines.voi_study --stage grid report --workers 60
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import math
import pathlib
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.conformal.calibration import (CalibrationPair, QhatTable,
                                             fit_global_qhat)
from baselines.representative_grid import (BELIEF_SPECS, REFERENCE_SWEEP,
                                           REPO_ROOT, REPRESENTATIVE_BUDGETS,
                                           EpisodeRef, GridTask, PolicySpec,
                                           aggregate_rows, episode_index,
                                           fleet_bank_paths, fmt,
                                           llm_pending_fraction, merge_parts,
                                           part_path, passive_pairs,
                                           provenance, read_csv, read_dump,
                                           reference_split, run_plain_task,
                                           run_pool, write_csv, DAY_FIELDS,
                                           GRID_FIELDS)

logger = logging.getLogger(__name__)

DEFAULT_OUT = REPO_ROOT / "results" / "voi_policies"
LAMBDAS: Tuple[float, ...] = (0.01, 0.02, 0.05, 0.1, 0.2, 0.3)
GAMMAS: Tuple[float, ...] = (0.01, 0.05, 0.1)
LAMBDA0 = 0.05
"""Starting price of the budget-tracking policy: the middle of the
fixed grid."""
CONFIDENCE_BINS: Tuple[Tuple[float, float], ...] = (
    (0.0, 0.5), (0.5, 0.8), (0.8, 0.95), (0.95, 1.01))
"""Bins of the belief's confidence at the first decision (max p)."""

REFERENCE_ORDER = ("NeverSense", "SequentialSearch")


# --------------------------------------------------- reference sweep bests

def reference_best(sweep_dir: pathlib.Path = REFERENCE_SWEEP
                   ) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Per (belief display prefix, budget): the reference sweep's best
    conformal-global alpha and best ResolvableMassSense (alpha, tau) by
    test task accuracy, read from its ``frontier.csv``."""
    rows = read_csv(sweep_dir / "frontier.csv")
    out: Dict[Tuple[str, str], Dict[str, Any]] = {}
    beliefs = sorted({r["belief"] for r in rows})
    for belief in beliefs:
        key_belief = belief.split("(", 1)[0]
        for budget in sorted({r["budget"] for r in rows}):
            cell = [r for r in rows if r["belief"] == belief
                    and r["budget"] == budget]
            glob = [r for r in cell if r["mode"] == "global"]
            res = [r for r in cell if r["mode"] == "resolvable"]
            if not glob or not res:
                continue
            g = max(glob, key=lambda r: float(r["task_accuracy"]))
            s = max(res, key=lambda r: float(r["task_accuracy"]))
            out[(key_belief, budget)] = {
                "global_alpha": float(g["alpha"]),
                "global_accuracy": float(g["task_accuracy"]),
                "resolvable_alpha": float(s["alpha"]),
                "resolvable_tau": float(s["tau"]),
                "resolvable_accuracy": float(s["task_accuracy"])}
    return out


def consensus_best(best: Mapping[Tuple[str, str], Dict[str, Any]],
                   budget: str) -> Dict[str, Any]:
    """The configuration most reference beliefs preferred at ``budget``
    (ties: the smaller alpha, then the smaller tau)."""
    g = collections.Counter(v["global_alpha"] for (b, bud), v in best.items()
                            if bud == budget)
    r = collections.Counter((v["resolvable_alpha"], v["resolvable_tau"])
                            for (b, bud), v in best.items() if bud == budget)
    galpha = sorted(g.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    ralpha, rtau = sorted(r.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return {"global_alpha": galpha, "resolvable_alpha": ralpha,
            "resolvable_tau": rtau, "consensus": True}


def comparator_config(best: Mapping[Tuple[str, str], Dict[str, Any]],
                      belief_key: str, budget: int) -> Dict[str, Any]:
    key = (belief_key, str(budget))
    if key in best:
        return {**best[key], "consensus": False}
    return consensus_best(best, str(budget))


# ------------------------------------------------------------------ grid

def fit_tables(pairs: Sequence[CalibrationPair], alphas: Sequence[float]
               ) -> Dict[float, QhatTable]:
    return {a: fit_global_qhat(pairs, a) for a in sorted(set(alphas))}


def check_against_reference(belief_key: str, tables: Mapping[float, QhatTable],
                            sweep_dir: pathlib.Path = REFERENCE_SWEEP) -> None:
    """Log whether the refit global quantiles match the reference sweep's
    (same banks, split and semantics: they must)."""
    calib = sweep_dir / "budget90" / "calibration.json"
    if not calib.exists():
        return
    stored = json.loads(calib.read_text())["tables"]
    for alpha, table in tables.items():
        ref = next((t for t in stored
                    if str(t["belief"]).split("(", 1)[0] == belief_key
                    and t["mode"] == "global"
                    and abs(float(t["alpha"]) - alpha) < 1e-9), None)
        if ref is None:
            continue
        same = abs(float(ref["global_qhat"]) - table.global_qhat) < 1e-9
        (logger.info if same else logger.warning)(
            "%s alpha %g: refit qhat %.6f vs reference %.6f (%s)", belief_key,
            alpha, table.global_qhat, float(ref["global_qhat"]),
            "match" if same else "DIFFERENT")


def policy_specs(budget: Optional[int], questions_per_day: int,
                 comparator: Mapping[str, Any]) -> List[PolicySpec]:
    """The policies of one (budget) column. Soft budget: the VoI
    threshold policies only."""
    specs: List[PolicySpec] = []
    if budget is None:
        return [PolicySpec("voi_threshold", (("lam", lam),),
                           f"VoIThresholdSense_lambda{lam:g}") for lam in LAMBDAS]
    specs += [PolicySpec("never_sense", label="NeverSense"),
              PolicySpec("sequential_search", label="SequentialSearch")]
    specs += [PolicySpec("voi_threshold", (("lam", lam),),
                         f"VoIThresholdSense_lambda{lam:g}") for lam in LAMBDAS]
    specs += [PolicySpec("voi_budget_price",
                         (("gamma", g), ("budget_per_day", budget),
                          ("questions_per_day", questions_per_day),
                          ("lam0", LAMBDA0)),
                         f"VoIBudgetPriceSense_gamma{g:g}") for g in GAMMAS]
    specs.append(PolicySpec(
        "resolvable_mass",
        (("alpha", comparator["resolvable_alpha"]),
         ("tau", comparator["resolvable_tau"])), "ResolvableMassSense_best"))
    specs.append(PolicySpec("conformal_global",
                            (("alpha", comparator["global_alpha"]),),
                            "ConformalGlobal_best"))
    return specs


def stage_grid(out: pathlib.Path, refs: Sequence[EpisodeRef],
               split: Dict[str, str], seed: int, workers: int,
               beliefs: Sequence[str]) -> None:
    calib = [r for r in refs if split[r.household_id] == "calibration"]
    test = [r for r in refs if split[r.household_id] == "test"]
    qpd = {r.questions_per_day for r in refs}
    if len(qpd) != 1:
        raise ValueError(f"questions per day differs across banks: {qpd}")
    questions_per_day = qpd.pop()
    best = reference_best()
    notes: List[str] = []
    beliefs = list(beliefs)
    if "LLMBelief" in beliefs:
        fractions = {r.household_id: llm_pending_fraction(r) for r in test}
        if max(fractions.values()) > 0:
            beliefs.remove("LLMBelief")
            notes.append(
                f"LLMBelief cells skipped: the cached completions leave "
                f"{min(fractions.values()):.0%}-{max(fractions.values()):.0%} "
                f"of a passive replay's queried predictions unanswered per "
                f"test household, and sensing changes the prompts further; "
                f"every cell would need new LLM calls.")
    if "OracleBelief" in beliefs:
        gate = REPO_ROOT / "results" / "oracle_program_posterior" / "ess_gate.md"
        if gate.exists() and "STOP" in gate.read_text():
            beliefs.remove("OracleBelief")
            notes.append("OracleBelief cells not run: the oracle-posterior "
                         "study stopped at its ESS gate (fleet median ESS "
                         "1.00; `results/oracle_program_posterior/`).")
    tasks: List[GridTask] = []
    comparators: Dict[str, Dict[str, Any]] = {}
    for belief_key in beliefs:
        pairs_by_hh = passive_pairs(belief_key, BELIEF_SPECS[belief_key],
                                    calib, seed, workers)
        pairs = [p for hh in sorted(pairs_by_hh) for p in pairs_by_hh[hh]]
        alphas: set[float] = set()
        for budget in REPRESENTATIVE_BUDGETS:
            cfg = comparator_config(best, belief_key, budget)
            comparators[f"{belief_key}@{budget}"] = cfg
            alphas.update((cfg["global_alpha"], cfg["resolvable_alpha"]))
        tables = fit_tables(pairs, sorted(alphas))
        check_against_reference(belief_key, tables)
        for cap in (*REPRESENTATIVE_BUDGETS, None):
            cfg = comparators.get(f"{belief_key}@{cap}", {})
            for spec in policy_specs(cap, questions_per_day, cfg):
                fitted: Dict[str, Any] = {}
                if spec.kind in ("resolvable_mass", "conformal_global"):
                    fitted["table"] = tables[float(spec.get("alpha"))]
                for ref in test:
                    task = GridTask(belief_key, dict(BELIEF_SPECS[belief_key]),
                                    spec, cap, ref, seed, "", fitted)
                    task.part_path = part_path(out, task.cell, ref.episode_id)
                    tasks.append(task)
    tasks.sort(key=lambda t: t.belief_key != "PerpetuaStar")
    results = run_pool(run_plain_task, tasks, workers)
    merge_parts(out)
    grid, days = aggregate_rows(results)
    write_csv(grid, out / "grid.csv", GRID_FIELDS)
    write_csv(days, out / "accuracy_by_day.csv", DAY_FIELDS)
    (out / "comparators.json").write_text(json.dumps(comparators, indent=2))
    (out / "notes.md").write_text("\n".join(f"- {n}" for n in notes) + "\n")
    provenance(out, refs, split, seed=seed, beliefs=beliefs,
               lambdas=list(LAMBDAS), gammas=list(GAMMAS), lambda0=LAMBDA0,
               questions_per_day=questions_per_day, notes=notes)


# ---------------------------------------------------------------- report

_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"
SERIES = (
    # slug prefix, label, hue, marker
    ("NeverSense", "never sense", "#33322e", "*"),
    ("SequentialSearch", "search until found", "#33322e", "^"),
    ("VoIThresholdSense", "VoI threshold (under the cap)", "#2a78d6", "o"),
    ("VoIThresholdSense@soft", "VoI threshold (cap removed)", "#2a78d6", "o"),
    ("VoIBudgetPriceSense", "VoI budget price", "#eb6834", "D"),
    ("ResolvableMassSense_best", "resolvable-mass gate (v2 best)", "#1baf7a", "s"),
    ("ConformalGlobal_best", "conformal global (v2 best)", "#8a4fd1", "P"),
)
_REALLOC_POLICIES = (("SequentialSearch", "search until found", "#33322e"),
                     ("VoIBudgetPriceSense_gamma0.05",
                      "VoI budget price (gamma 0.05)", "#eb6834"))


def _series_of(row: Mapping[str, str]) -> str:
    slug = row["policy"]
    if row["budget"] == "soft":
        return "VoIThresholdSense@soft"
    for prefix, *_ in SERIES:
        if slug.startswith(prefix):
            return prefix
    return slug


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for k successes in n trials (the package's
    interval everywhere; see `metrics.wilson_interval`)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _lambda_of(slug: str) -> str:
    return slug.rsplit("lambda", 1)[1] if "lambda" in slug else ""


def plot_frontier(grid: Sequence[Dict[str, str]], path: pathlib.Path,
                  questions_per_day: int) -> None:
    """Accuracy against cost, one panel per (belief, budget), with 95%
    Wilson intervals on every point. The dashed line is the same VoI
    threshold rule with the cap removed, labelled by lambda: the
    price-based frontier the cap truncates."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    rows: List[Dict[str, Any]] = []
    for r in grid:
        row: Dict[str, Any] = dict(r)
        row["acc"] = float(r["task_accuracy"])
        row["n"] = int(r["n_questions"])
        row["cost"] = float(r["senses_per_question"])
        row["lo"], row["hi"] = wilson(round(row["acc"] * row["n"]), row["n"])
        rows.append(row)
    beliefs = list(dict.fromkeys(r["belief"] for r in rows))
    budgets = [str(b) for b in REPRESENTATIVE_BUDGETS]
    n_q = max(r["n"] for r in rows)
    fig, axes = plt.subplots(len(budgets), len(beliefs), squeeze=False,
                             sharey="row", figsize=(5.0 * len(beliefs), 4.2 * len(budgets)))
    for col, belief in enumerate(beliefs):
        for row_i, budget in enumerate(budgets):
            ax = axes[row_i][col]
            cell = [r for r in rows if r["belief"] == belief
                    and r["budget"] in (budget, "soft")]
            for key, _label, hue, marker in SERIES:
                pts = sorted((r for r in cell if _series_of(r) == key),
                             key=lambda r: r["cost"])
                if not pts:
                    continue
                soft = key.endswith("@soft")
                xs = [r["cost"] for r in pts]
                ys = [r["acc"] for r in pts]
                err = [[r["acc"] - r["lo"] for r in pts],
                       [r["hi"] - r["acc"] for r in pts]]
                if key.startswith("VoIThresholdSense"):
                    ax.plot(xs, ys, color=hue, linewidth=1.3, alpha=0.8,
                            linestyle="--" if soft else "-", zorder=2)
                ax.errorbar(xs, ys, yerr=err, fmt=marker, color=hue,
                            markerfacecolor="white" if soft else hue,
                            markersize=7, capsize=3, linewidth=1, zorder=3)
                if soft:
                    for r in pts:
                        ax.annotate(f"lambda={_lambda_of(r['policy'])}",
                                    (r["cost"], r["acc"]), fontsize=7,
                                    color=hue, textcoords="offset points",
                                    xytext=(4, -9))
            cap = float(budget) / questions_per_day
            ax.axvline(cap, color=_MUTED, linestyle=":", linewidth=1)
            ax.set_title(f"{belief}, {budget} senses/day", fontsize=10,
                         loc="left", color=_INK)
            ax.set_xlabel("senses per question (cost)", color=_INK, fontsize=9)
            if col == 0:
                ax.set_ylabel("task accuracy", color=_INK, fontsize=9)
            ax.tick_params(colors=_INK, labelsize=8)
            ax.grid(True, color=_GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color(_MUTED)
            ax.spines["bottom"].set_color(_MUTED)
            ax.text(cap + 0.02, ax.get_ylim()[0] + 0.02,
                    f"cap = {cap:.2f}/q", fontsize=7, color=_MUTED)
    handles = [Line2D([], [], marker=marker,
                      linestyle="--" if key.endswith("@soft") else "",
                      color=hue,
                      markerfacecolor="white" if key.endswith("@soft") else hue,
                      label=label) for key, label, hue, marker in SERIES]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=9)
    fig.suptitle(
        f"Accuracy against cost on the test households, n = {n_q} questions "
        f"per point, 95% Wilson intervals (about +/-0.006, mostly inside the "
        f"markers).\nDashed: the VoI threshold rule with the cap removed, "
        f"labelled by lambda; the filled dots are the same lambdas under the "
        f"cap.", color=_INK, fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.08, 1, 0.93))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_reallocation(out: pathlib.Path, beliefs: Sequence[str],
                      path: pathlib.Path) -> None:
    """Senses per question by the belief's confidence at the first
    decision: where each policy puts the budget, with the bin's accuracy
    and its 95% Wilson interval above the bar."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    budgets = [str(b) for b in REPRESENTATIVE_BUDGETS]
    fig, axes = plt.subplots(len(budgets), len(beliefs), squeeze=False,
                             sharey="row",
                             figsize=(5.0 * len(beliefs), 4.0 * len(budgets)))
    width = 0.38
    for col, belief in enumerate(beliefs):
        for row_i, budget in enumerate(budgets):
            ax = axes[row_i][col]
            counts: List[int] = []
            for j, (policy, label, hue) in enumerate(_REALLOC_POLICIES):
                cells = _confidence_bins(out, belief, policy, budget)
                if not cells:
                    continue
                xs = [i + (j - 0.5) * width for i in range(len(cells))]
                spend = [c[2] for c in cells]
                ax.bar(xs, spend, width, color=hue, label=label, alpha=0.9)
                for x, (_lab, n, s, acc) in zip(xs, cells):
                    lo, hi = wilson(round(acc * n), n)
                    ax.text(x, s, f"\n{acc:.2f}\n[{lo:.2f}, {hi:.2f}]",
                            ha="center", va="bottom", fontsize=6.5, color=_INK)
                if not counts:
                    counts = [c[1] for c in cells]
            labels = [c[0] for c in _confidence_bins(
                out, belief, _REALLOC_POLICIES[0][0], budget)]
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels([f"{l}\nn={n}" for l, n in zip(labels, counts)],
                               fontsize=8, color=_INK)
            ax.set_title(f"{belief}, {budget} senses/day", fontsize=10,
                         loc="left", color=_INK)
            ax.grid(True, axis="y", color=_GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color(_MUTED)
            ax.spines["bottom"].set_color(_MUTED)
            ax.tick_params(colors=_INK, labelsize=8)
            if col == 0:
                ax.set_ylabel("senses spent per question", color=_INK, fontsize=9)
            if row_i == len(budgets) - 1:
                ax.set_xlabel("belief confidence at the first decision "
                              "(hard on the left)", color=_INK, fontsize=9)
            if col == 0 and row_i == 0:
                ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Where the budget goes: senses per question by how sure the "
                 "belief was before sensing.\nThe pair of numbers above each "
                 "bar is that bin's task accuracy and its 95% Wilson interval.",
                 color=_INK, fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _idx(grid: Sequence[Dict[str, str]]) -> Dict[Tuple[str, str, str], Dict[str, str]]:
    return {(r["belief"], r["policy"], r["budget"]): r for r in grid}


def _confidence_bins(out: pathlib.Path, belief: str, policy: str, budget: str
                     ) -> List[Tuple[str, int, float, float]]:
    """(bin label, n, senses per question, accuracy) from the cell's dump."""
    path = out / "questions" / f"{belief}__{policy}__{budget}.jsonl.gz"
    if not path.exists():
        return []
    bins: Dict[int, List[Tuple[int, int]]] = collections.defaultdict(list)
    for row in read_dump(path):
        c = float(row["first_confidence"])
        for i, (lo, hi) in enumerate(CONFIDENCE_BINS):
            if lo <= c < hi:
                bins[i].append((int(row["budget_spent"]), int(row["correct"])))
                break
    out_rows = []
    for i, (lo, hi) in enumerate(CONFIDENCE_BINS):
        cell = bins.get(i, [])
        label = f"[{lo:g}, {min(hi, 1.0):g}{')' if hi <= 1.0 else ']'}"
        if cell:
            out_rows.append((label, len(cell),
                             sum(s for s, _ in cell) / len(cell),
                             sum(c for _, c in cell) / len(cell)))
        else:
            out_rows.append((label, 0, 0.0, 0.0))
    return out_rows


def stage_report(out: pathlib.Path) -> None:
    grid = read_csv(out / "grid.csv")
    idx = _idx(grid)
    beliefs = list(dict.fromkeys(r["belief"] for r in grid))
    budgets = [str(b) for b in REPRESENTATIVE_BUDGETS]
    comparators = json.loads((out / "comparators.json").read_text())
    notes = (out / "notes.md").read_text().strip() if (out / "notes.md").exists() else ""
    prov = json.loads((out / "provenance.json").read_text())
    questions_per_day = int(prov.get("questions_per_day", 90))
    plot_frontier(grid, out / "frontier.png", questions_per_day)
    plot_reallocation(out, beliefs, out / "budget_reallocation.png")
    lines = ["# Value-of-information policies on the representative grid", "",
             "Inputs: the 10 test households of `results/conformal_sweep_v2/` "
             "(split seed 0), budgets 24 and 90 senses per day, beliefs "
             + ", ".join(beliefs) + ". VoIThresholdSense senses the "
             "argmax-voi receptacle while max voi >= lambda "
             "(`policies/voi_sense.py`; one-step lookahead, arithmetic on the "
             "belief's distribution), in fixed-budget mode (the cap binds) and "
             "soft-budget mode (cap disabled; the price alone sets the spend). "
             "VoIBudgetPriceSense starts at lambda 0.05 and moves it by "
             "gamma * (spend rate - budget rate) after every question, clipped "
             "to [0.001, 0.5]. Comparators: ResolvableMassSense and "
             "ConformalSense(global) at the reference sweep's best "
             "configuration for that belief and budget (`comparators.json`; "
             "a belief the reference sweep did not run gets the configuration "
             "most of its beliefs preferred at that budget, marked "
             "'consensus' below). Produced by `python -m baselines.voi_study`; "
             "per-day accuracy per cell in `accuracy_by_day.csv`. Every cell "
             "is 22 500 questions, so the 95% Wilson interval on an accuracy "
             "is about +/-0.006 and differences below about 0.01 are noise; "
             "the tables below are raw numbers, the figures carry the "
             "intervals. Figures: `frontier.png` (accuracy against cost per "
             "belief and budget, with the cap-removed price frontier) and "
             "`budget_reallocation.png` (senses per question by how sure the "
             "belief was before sensing).", ""]
    if notes:
        lines += [notes, ""]

    # 1. Deltas.
    lines += ["## 1. VoI policies against the two comparators, per (belief, budget)",
              "", "Task accuracy (senses per question); delta = VoI policy minus "
              "comparator, raw.", ""]
    for belief in beliefs:
        for budget in budgets:
            res = idx.get((belief, "ResolvableMassSense_best", budget))
            con = idx.get((belief, "ConformalGlobal_best", budget))
            cfg = comparators.get(f"{belief}@{budget}", {})
            if not res or not con:
                continue
            tag = " (consensus config)" if cfg.get("consensus") else ""
            lines += [f"### {belief}, budget {budget}{tag}", "",
                      f"Comparators: {res['policy_name']} {fmt(res['task_accuracy'])} "
                      f"({fmt(res['senses_per_question'], 2)} senses/q); "
                      f"{con['policy_name']} {fmt(con['task_accuracy'])} "
                      f"({fmt(con['senses_per_question'], 2)}). NeverSense "
                      f"{fmt(idx[(belief, 'NeverSense', budget)]['task_accuracy'])}, "
                      f"SequentialSearch "
                      f"{fmt(idx[(belief, 'SequentialSearch', budget)]['task_accuracy'])} "
                      f"({fmt(idx[(belief, 'SequentialSearch', budget)]['senses_per_question'], 2)}).",
                      "", "| policy | accuracy | senses/q | vs ResolvableMass | vs ConformalGlobal |",
                      "|---|---|---|---|---|"]
            for r in grid:
                if r["belief"] != belief or r["budget"] != budget:
                    continue
                if not r["policy"].startswith("VoI"):
                    continue
                acc = float(r["task_accuracy"])
                lines.append(
                    f"| {r['policy_name']} | {acc:.3f} | "
                    f"{float(r['senses_per_question']):.2f} | "
                    f"{acc - float(res['task_accuracy']):+.3f} | "
                    f"{acc - float(con['task_accuracy']):+.3f} |")
            lines.append("")
        soft = sorted((r for r in grid if r["belief"] == belief and r["budget"] == "soft"),
                      key=lambda r: float(r["senses_per_question"]))
        if soft:
            lines += [f"### {belief}, soft budget (cap disabled)", "",
                      "| lambda | accuracy | senses/q | senses/day |", "|---|---|---|---|"]
            for r in soft:
                lines.append(f"| {r['policy'].rsplit('lambda', 1)[1]} "
                             f"| {fmt(r['task_accuracy'])} | {fmt(r['senses_per_question'], 2)} "
                             f"| {fmt(r['senses_per_day'], 1)} |")
            lines.append("")

    # Best VoI per cell summary.
    lines += ["### Summary: best VoI policy per cell vs the better comparator", "",
              "| belief | budget | best VoI (accuracy, senses/q) | better comparator | delta |",
              "|---|---|---|---|---|"]
    for belief in beliefs:
        for budget in budgets:
            vois = [r for r in grid if r["belief"] == belief and r["budget"] == budget
                    and r["policy"].startswith("VoI")]
            comps = [c for c in (idx.get((belief, p, budget)) for p in
                     ("ResolvableMassSense_best", "ConformalGlobal_best")) if c]
            if not vois or not comps:
                continue
            bv = max(vois, key=lambda r: float(r["task_accuracy"]))
            bc = max(comps, key=lambda r: float(r["task_accuracy"]))
            lines.append(f"| {belief} | {budget} | {bv['policy_name']} "
                         f"({fmt(bv['task_accuracy'])}, {fmt(bv['senses_per_question'], 2)}) "
                         f"| {bc['policy_name']} ({fmt(bc['task_accuracy'])}, "
                         f"{fmt(bc['senses_per_question'], 2)}) | "
                         f"{float(bv['task_accuracy']) - float(bc['task_accuracy']):+.3f} |")

    # 2. Reallocation.
    lines += ["", "## 2. Does VoIBudgetPriceSense move budget toward hard questions?",
              "", "Senses per question by the belief's confidence at the "
              "question's first decision (max p before any sense), "
              "VoIBudgetPriceSense (gamma 0.05) against SequentialSearch's "
              "flat spending, with accuracy in the bin. n per bin in "
              "parentheses.", ""]
    for belief in beliefs:
        for budget in budgets:
            ss = _confidence_bins(out, belief, "SequentialSearch", budget)
            bp = _confidence_bins(out, belief, "VoIBudgetPriceSense_gamma0.05", budget)
            if not ss or not bp:
                continue
            lines += [f"### {belief}, budget {budget}", "",
                      "| first-decision confidence | n | SequentialSearch senses/q (acc) "
                      "| VoIBudgetPrice senses/q (acc) |", "|---|---|---|---|"]
            for (label, n, s1, a1), (_, n2, s2, a2) in zip(ss, bp):
                lines.append(f"| {label} | {n} | {s1:.2f} ({a1:.3f}) | "
                             f"{s2:.2f} ({a2:.3f}) |")
            hard_ss = ss[0][2] if ss[0][1] else 0.0
            easy_ss = ss[-1][2] if ss[-1][1] else 0.0
            hard_bp = bp[0][2] if bp[0][1] else 0.0
            easy_bp = bp[-1][2] if bp[-1][1] else 0.0
            lines += ["", f"Hard-to-easy spend ratio (bin [0, 0.5) over bin "
                      f"[0.95, 1]): SequentialSearch "
                      f"{(hard_ss / easy_ss) if easy_ss else float('inf'):.2f}, "
                      f"VoIBudgetPrice "
                      f"{(hard_bp / easy_bp) if easy_bp else float('inf'):.2f}.", ""]

    # 3. Oracle ceiling.
    lines += ["## 3. On OracleBelief, do VoI policies reach the ceiling with fewer senses?", ""]
    if "OracleBelief" in beliefs:
        for budget in budgets:
            cell = sorted((r for r in grid if r["belief"] == "OracleBelief"
                           and r["budget"] == budget),
                          key=lambda r: -float(r["task_accuracy"]))
            top = float(cell[0]["task_accuracy"])
            lines += [f"Budget {budget}: ceiling (best cell) {top:.3f}. Policies "
                      f"within 0.005 of it, by senses per question:", "",
                      "| policy | accuracy | senses/q |", "|---|---|---|"]
            for r in sorted((r for r in cell if top - float(r["task_accuracy"]) <= 0.005),
                            key=lambda r: float(r["senses_per_question"])):
                lines.append(f"| {r['policy_name']} | {fmt(r['task_accuracy'])} | "
                             f"{fmt(r['senses_per_question'], 2)} |")
            lines.append("")
    else:
        lines += ["Not answerable: OracleBelief is not in this grid (the "
                  "oracle-posterior study stopped at its ESS gate, "
                  "`results/oracle_program_posterior/findings.md`).", ""]
    lines += summary_section(grid, idx, beliefs, budgets)
    (out / "findings.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def summary_section(grid: Sequence[Dict[str, str]],
                    idx: Mapping[Tuple[str, str, str], Dict[str, str]],
                    beliefs: Sequence[str],
                    budgets: Sequence[str]) -> List[str]:
    """The read-out: which cells the VoI policies win, lose or tie, at the
    0.01 resolution the sample size supports."""
    wins: List[str] = []
    losses: List[str] = []
    ties: List[str] = []
    for belief in beliefs:
        for budget in budgets:
            vois = [r for r in grid if r["belief"] == belief
                    and r["budget"] == budget and r["policy"].startswith("VoI")]
            comps = [c for c in (idx.get((belief, p, budget)) for p in
                                 ("ResolvableMassSense_best", "ConformalGlobal_best"))
                     if c]
            if not vois or not comps:
                continue
            bv = max(vois, key=lambda r: float(r["task_accuracy"]))
            bc = max(comps, key=lambda r: float(r["task_accuracy"]))
            delta = float(bv["task_accuracy"]) - float(bc["task_accuracy"])
            entry = (f"{belief} at {budget}/day ({delta:+.3f}: "
                     f"{bv['policy_name']} {fmt(bv['task_accuracy'])} at "
                     f"{fmt(bv['senses_per_question'], 2)} senses/q vs "
                     f"{bc['policy_name']} {fmt(bc['task_accuracy'])} at "
                     f"{fmt(bc['senses_per_question'], 2)})")
            (wins if delta > 0.01 else losses if delta < -0.01
             else ties).append(entry)
    out = ["", "## Summary", "",
           "Against the better of the two comparators in each cell, at the "
           "0.01 resolution 22 500 questions support:", ""]
    for label, group in (("VoI ahead", wins), ("VoI behind", losses),
                         ("within noise", ties)):
        out.append(f"- **{label}**: "
                   + ("; ".join(group) if group else "none") + ".")
    return out


# ------------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", nargs="+", choices=("grid", "report"),
                        required=True)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=40)
    parser.add_argument("--beliefs", default=",".join(BELIEF_SPECS))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("baselines").setLevel(logging.INFO)
    refs = episode_index(fleet_bank_paths())
    split = reference_split(refs)
    args.out.mkdir(parents=True, exist_ok=True)
    for stage in args.stage:
        if stage == "grid":
            stage_grid(args.out, refs, split, args.seed, args.workers,
                       [b.strip() for b in args.beliefs.split(",") if b.strip()])
        elif stage == "report":
            stage_report(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
