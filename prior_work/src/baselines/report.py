"""Render a Markdown report from a results directory.

Reads what :mod:`baselines.cli` wrote (``questions.csv``, ``aggregate.csv``,
``provenance.json``) and produces a self-contained rundown: provenance,
headline accuracy per agent, the belief x policy pivot, per-object-class
accuracy at the pure-belief baseline (NeverSense), the hardest objects, and
budget usage. Numbers only — interpretation belongs to the reader.

Usage:
  python -m baselines.report smoke_results/baselines_hh001 \
      --out reports/baselines/hh_001_seed0_grid.md
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import defaultdict
from typing import Dict, List, Tuple


def _read_csv(path: pathlib.Path) -> List[Dict[str, str]]:
    with open(path) as f:
        return list(csv.DictReader(f))


def _table(header: List[str], rows: List[List[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def render(run_dir: pathlib.Path) -> str:
    """Build the full Markdown report for one results directory."""
    provenance = json.loads((run_dir / "provenance.json").read_text())
    questions = _read_csv(run_dir / "questions.csv")
    aggregate = _read_csv(run_dir / "aggregate.csv")

    overall = sorted((r for r in aggregate if r["stratum_type"] == "overall"),
                     key=lambda r: -float(r["task_accuracy"]))
    n_questions = len({q["question_id"] for q in questions})
    n_days = len({q["day_index"] for q in questions})
    n_objects = len({q["object_id"] for q in questions})
    budget = overall[0]["budget_per_day"] if overall else "?"

    parts: List[str] = [
        f"# Baselines rundown — {questions[0]['household_id']}",
        "",
        f"Run directory: `{run_dir}`",
        "",
        "Per-day passive numbers in this report are DESCRIPTIVE ONLY: "
        "later days conflate more history, fresher sightings, and shorter "
        "horizons. Learning-curve claims use the horizon-controlled "
        "protocol (`baselines.passive_eval` / the bake-off reports).",
        "",
        "## Provenance",
        "",
        f"- bank: `{provenance['bank_path']}` "
        f"(manifest `{provenance['bank_manifest_hash'][:12]}…`)",
        f"- config: `{provenance['config_path']}` "
        f"(hash `{provenance['config_hash'][:12]}…`)",
        f"- git commit: `{provenance['git_commit'][:12]}`"
        + (" (dirty tree)" if provenance["git_dirty"] else ""),
        f"- seed: {provenance['seed']} · run at {provenance['timestamp']}",
        "",
        f"**{n_questions} questions** over {n_days} question-days, "
        f"{n_objects} distinct objects queried, budget {budget}/day, "
        f"{len(overall)} agents.",
        "",
        "## Headline: accuracy by agent",
        "",
        _table(["agent", "task accuracy", "budget/question", "budget/day"],
               [[r["agent"], f"{float(r['task_accuracy']):.3f}",
                 f"{float(r['mean_budget_per_question']):.2f}",
                 f"{float(r['mean_budget_per_day']):.2f}"] for r in overall]),
    ]

    beliefs: List[str] = []
    policies: List[str] = []
    pivot: Dict[Tuple[str, str], str] = {}
    for r in overall:
        if r["belief"] not in beliefs:
            beliefs.append(r["belief"])
        if r["policy"] not in policies:
            policies.append(r["policy"])
        pivot[(r["belief"], r["policy"])] = f"{float(r['task_accuracy']):.3f}"
    parts += [
        "",
        "## Belief × policy accuracy",
        "",
        _table(["belief \\ policy"] + policies,
               [[b] + [pivot.get((b, p), "–") for p in policies]
                for b in beliefs]),
    ]

    never = [r for r in aggregate
             if r["stratum_type"] == "object_class"
             and r["policy"] == "NeverSense"]
    classes = sorted({r["stratum"] for r in never})
    by_bc = {(r["belief"], r["stratum"]):
             f"{float(r['task_accuracy']):.2f} (n={r['n_questions']})"
             for r in never}
    parts += [
        "",
        "## Per object class, pure belief (NeverSense)",
        "",
        _table(["belief \\ class"] + classes,
               [[b] + [by_bc.get((b, c), "–") for c in classes]
                for b in beliefs]),
    ]

    per_object: Dict[str, List[bool]] = defaultdict(list)
    for q in questions:
        per_object[q["object_id"]].append(q["correct"] == "True")
    hardest = sorted(per_object.items(),
                     key=lambda kv: sum(kv[1]) / len(kv[1]))[:5]
    parts += [
        "",
        "## Hardest objects (accuracy across all agents)",
        "",
        _table(["object", "accuracy", "answers"],
               [[obj, f"{sum(oks) / len(oks):.2f}", str(len(oks))]
                for obj, oks in hardest]),
        "",
        "## Artifacts",
        "",
        f"- per-question rows: `{run_dir}/questions.csv`",
        f"- aggregates (incl. per-day strata): `{run_dir}/aggregate.csv`",
        f"- run log (replayable): `{run_dir}/run_log.jsonl`",
        f"- plots: `{run_dir}/accuracy_by_agent.png`, "
        f"`{run_dir}/accuracy_by_day.png`",
        "- interactive: `/visualization/viewer/beliefs.html` "
        "(belief-vs-truth overlay on the household map)",
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(args.run_dir))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
