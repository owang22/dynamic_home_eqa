"""Scoring, aggregation, and the two basic plots.

Consumes the per-question records the harness emits and produces:

* ``questions.csv`` — tidy long format, one row per question, one column
  per scalar record field (the distribution and action list stay in the
  JSONL run log; CSV keeps scalars only).
* ``aggregate.csv`` — one row per (agent, stratum) with task/belief
  accuracy and budget
  statistics. Strata: ``overall``, each ``object_class``, and each
  ``day_index``; every row also carries the run's ``budget_per_day`` so
  rows from runs at different budget levels concatenate directly into
  accuracy-vs-budget curves later.
* two plots: accuracy by agent (bar) and accuracy vs day_index by agent
  (line). Line hue encodes the belief model (three fixed-order hues from a
  colorblind-validated palette) and line style encodes the policy, so nine
  series never need nine hues.

All times are seconds since episode start; ``day_index`` is derived by the
bank, not recomputed here.
"""

from __future__ import annotations

import csv
import json
import logging
import pathlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Tuple

from baselines.harness import QuestionRecord

logger = logging.getLogger(__name__)

_CSV_FIELDS = (
    "agent", "belief", "policy", "episode_id", "household_id", "day_index",
    "question_id", "object_id", "object_class", "t_query",
    "answer_receptacle", "truth_receptacle", "correct", "confidence",
    "budget_before", "budget_spent", "budget_after", "forced_answer",
    "belief_accuracy")

# Fixed-order categorical hues (validated palette; hue = belief identity).
_BELIEF_HUES = ("#2a78d6", "#eb6834", "#1baf7a")
_POLICY_STYLES = ("solid", "dashed", "dotted")
_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"


@dataclass(frozen=True)
class AggregateRow:
    """One aggregate cell: an agent's accuracies within one stratum.

    ``task_accuracy`` is correctness on the queried objects
    (what the study's task rewards). ``belief_accuracy`` is FULL-STATE
    accuracy — mean correctness of the belief's argmax over all objects
    (of this stratum's class, day, or everything) at question times: the
    probe set sensing cannot react to. ``attention_gap`` = task - belief;
    positive means the agent steers its budget toward what gets asked,
    zero means it senses indiscriminately.
    """

    agent: str
    belief: str
    policy: str
    budget_per_day: int
    stratum_type: str    # "overall" | "object_class" | "day_index"
    stratum: str
    n_questions: int
    task_accuracy: float
    belief_accuracy: float
    attention_gap: float
    mean_budget_per_question: float
    mean_budget_per_day: float


def write_questions_csv(records: Sequence[QuestionRecord],
                        path: pathlib.Path) -> None:
    """Write the tidy one-row-per-question CSV."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_CSV_FIELDS)
        for r in records:
            row = r.to_json_dict()
            writer.writerow([row[field] for field in _CSV_FIELDS])
    logger.info("wrote %d question rows -> %s", len(records), path)


def load_run_log(path: pathlib.Path) -> List[QuestionRecord]:
    """Reload a ``run_log.jsonl`` into records for post-hoc metrics.

    Every metric in this module (including full-state ``belief_accuracy``)
    is recomputable from the log alone — no episode re-run — because the
    harness logs the belief's per-object argmax snapshot with each
    question. JSON round-trips lists; tuple-typed fields are restored.
    """
    records: List[QuestionRecord] = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            row["actions"] = tuple(row["actions"])
            row["belief_state"] = {
                obj: (str(cls), str(guess), bool(ok))
                for obj, (cls, guess, ok) in row["belief_state"].items()}
            records.append(QuestionRecord(**row))
    logger.info("loaded %d records from %s", len(records), path)
    return records


def aggregate(records: Sequence[QuestionRecord],
              budget_per_day: int) -> List[AggregateRow]:
    """Aggregate records into per-(agent, stratum) accuracy/budget rows."""
    by_agent: Dict[str, List[QuestionRecord]] = defaultdict(list)
    for r in records:
        by_agent[r.agent].append(r)

    rows: List[AggregateRow] = []
    for agent, recs in sorted(by_agent.items()):
        strata: List[Tuple[str, str, List[QuestionRecord]]] = [
            ("overall", "all", recs)]
        by_class: Dict[str, List[QuestionRecord]] = defaultdict(list)
        by_day: Dict[int, List[QuestionRecord]] = defaultdict(list)
        for r in recs:
            by_class[r.object_class].append(r)
            by_day[r.day_index].append(r)
        strata += [("object_class", cls, rs) for cls, rs in sorted(by_class.items())]
        strata += [("day_index", str(d), rs) for d, rs in sorted(by_day.items())]

        n_days = len({(r.episode_id, r.day_index) for r in recs})
        total_spent = sum(r.budget_spent for r in recs)
        for stratum_type, stratum, rs in strata:
            # Full-state accuracy restricted to this stratum: for a class
            # stratum, only snapshot entries of that class count; for
            # day/overall strata every snapshot entry counts.
            hits = total = 0
            for r in rs:
                for _, (cls, _, ok) in r.belief_state.items():
                    if stratum_type == "object_class" and cls != stratum:
                        continue
                    hits += ok
                    total += 1
            belief_acc = hits / total if total else 0.0
            task_acc = sum(r.correct for r in rs) / len(rs)
            rows.append(AggregateRow(
                agent=agent, belief=rs[0].belief, policy=rs[0].policy,
                budget_per_day=budget_per_day,
                stratum_type=stratum_type, stratum=stratum,
                n_questions=len(rs),
                task_accuracy=task_acc,
                belief_accuracy=belief_acc,
                attention_gap=task_acc - belief_acc,
                mean_budget_per_question=sum(
                    r.budget_spent for r in rs) / len(rs),
                mean_budget_per_day=total_spent / n_days if n_days else 0.0))
    return rows


def write_aggregate_csv(rows: Sequence[AggregateRow],
                        path: pathlib.Path) -> None:
    """Write the aggregate CSV (one row per agent x stratum)."""
    fields = ("agent", "belief", "policy", "budget_per_day", "stratum_type",
              "stratum", "n_questions", "task_accuracy", "belief_accuracy",
              "attention_gap", "mean_budget_per_question",
              "mean_budget_per_day")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([getattr(row, field) for field in fields])
    logger.info("wrote %d aggregate rows -> %s", len(rows), path)


def _style_maps(rows: Sequence[AggregateRow]) -> Tuple[Mapping[str, str],
                                                       Mapping[str, str]]:
    """Stable hue-per-belief and dash-per-policy assignments.

    Hues are assigned to beliefs in first-appearance order and never
    re-assigned when a belief is filtered out — color follows the entity.
    """
    beliefs: List[str] = []
    policies: List[str] = []
    for row in rows:
        if row.belief not in beliefs:
            beliefs.append(row.belief)
        if row.policy not in policies:
            policies.append(row.policy)
    if len(beliefs) > len(_BELIEF_HUES) or len(policies) > len(_POLICY_STYLES):
        raise ValueError(
            f"plotting supports up to {len(_BELIEF_HUES)} beliefs and "
            f"{len(_POLICY_STYLES)} policies; fold extras or add encodings")
    return (dict(zip(beliefs, _BELIEF_HUES)),
            dict(zip(policies, _POLICY_STYLES)))


def plot_accuracy_bar(rows: Sequence[AggregateRow],
                      path: pathlib.Path) -> None:
    """Horizontal bar chart of overall accuracy per agent (single hue —
    identity is on the axis, so color carries no second meaning)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    overall = sorted((r for r in rows if r.stratum_type == "overall"),
                     key=lambda r: r.task_accuracy)
    labels = [r.agent for r in overall]
    task = [r.task_accuracy for r in overall]
    belief = [r.belief_accuracy for r in overall]
    y = list(range(len(overall)))
    fig, ax = plt.subplots(figsize=(9, 0.62 * len(overall) + 1.6))
    ax.barh([i + 0.19 for i in y], task, height=0.34,
            color=_BELIEF_HUES[0], label="task (queried objects)")
    ax.barh([i - 0.19 for i in y], belief, height=0.34,
            color=_BELIEF_HUES[0], alpha=0.45,
            label="belief (all objects — probe set)")
    ax.set_yticks(y, labels)
    for i, v in enumerate(task):
        ax.text(v + 0.012, i + 0.19, f"{v:.2f}", va="center", fontsize=8,
                color=_INK)
    for i, v in enumerate(belief):
        ax.text(v + 0.012, i - 0.19, f"{v:.2f}", va="center", fontsize=8,
                color=_MUTED)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("accuracy", color=_INK)
    ax.set_title("Task vs full-state accuracy by agent", color=_INK, loc="left")
    ax.tick_params(colors=_INK, labelsize=9)
    ax.xaxis.grid(True, color=_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(_MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("wrote %s", path)


def plot_accuracy_by_day(rows: Sequence[AggregateRow],
                         path: pathlib.Path) -> None:
    """Line chart: accuracy vs day_index, hue = belief, dash = policy.

    DESCRIPTIVE ONLY: a later day simultaneously has more history, more
    recent sightings, and a shorter forecast horizon, so a rising curve
    here cannot be attributed to adaptation. Learning-curve claims use
    the horizon-controlled protocol in :mod:`baselines.passive_eval`.

    Agents frequently score identically on small banks, which would hide
    coincident series entirely; a small per-agent horizontal dodge
    (< 0.1 day) keeps every series visible without misstating any value.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    hue_of, style_of = _style_maps(rows)
    day_rows = [r for r in rows if r.stratum_type == "day_index"]
    by_agent: Dict[str, List[AggregateRow]] = defaultdict(list)
    for r in day_rows:
        by_agent[r.agent].append(r)

    fig, ax = plt.subplots(figsize=(9, 5))
    n_agents = len(by_agent)
    for i, (agent, rs) in enumerate(sorted(by_agent.items())):
        rs = sorted(rs, key=lambda r: int(r.stratum))
        dodge = (i - (n_agents - 1) / 2) * (0.16 / max(n_agents - 1, 1))
        ax.plot([int(r.stratum) + dodge for r in rs],
                [r.task_accuracy for r in rs],
                color=hue_of[rs[0].belief], linestyle=style_of[rs[0].policy],
                linewidth=2, marker="o", markersize=4.5, alpha=0.9)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("day index", color=_INK)
    ax.set_ylabel("accuracy", color=_INK)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("Accuracy vs day, by agent (hue = belief, dash = policy)",
                 color=_INK, loc="left")
    ax.tick_params(colors=_INK, labelsize=9)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    hue_handles = [Line2D([], [], color=hue, linewidth=3, label=belief)
                   for belief, hue in hue_of.items()]
    style_handles = [Line2D([], [], color=_INK, linestyle=style, label=policy)
                     for policy, style in style_of.items()]
    first = ax.legend(handles=hue_handles, title="belief", loc="lower left",
                      fontsize=8, title_fontsize=8, frameon=False)
    ax.add_artist(first)
    ax.legend(handles=style_handles, title="policy", loc="lower right",
              fontsize=8, title_fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("wrote %s", path)
