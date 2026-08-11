"""Off-policy belief replay: separate belief quality from data quality.

In a live run, the policy shapes the observation stream (its senses become
evidence), so comparing two agents confounds *how well the belief models
the dynamics* with *how informative the collected data was*. This module
kills that confound by replaying the exact evidence stream each agent
generated — initial tour, scripted sightings, and that agent's sense
results, reconstructed from the run log — through EVERY belief model:

    matrix[generating agent][evaluating belief] = full-state belief
        accuracy of the evaluating belief on that agent's stream

Read down a column: which belief best exploits a fixed observation stream (pure
belief quality). Read across a row: which agent collected the most
informative data (pure collection quality — differences down a column
cannot be explained by data anymore, and vice versa).

Scoring matches the harness's full-state snapshot: after delivering all
evidence up to and including a question's senses, predict every object and
compare to ground truth at t_query. The diagonal therefore reproduces the
live run's belief accuracy exactly (asserted in tests).

Everything is reconstructed from artifacts the run already wrote
(run_log.jsonl + provenance.json -> bank + config); no new simulation.

Usage:
  python -m baselines.replay smoke_results/baselines_hh001 \
      --out reports/baselines/hh_001_replay_matrix.md
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import pathlib
from collections import defaultdict
from typing import Any, Dict, List, Sequence, Tuple

import yaml

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, build_belief
from baselines.types import Episode, SenseResult

logger = logging.getLogger(__name__)


def _load_records(run_dir: pathlib.Path) -> Dict[str, List[Dict[str, Any]]]:
    """Run-log records grouped by generating agent, in time order."""
    by_agent: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    with open(run_dir / "run_log.jsonl") as f:
        for line in f:
            r = json.loads(line)
            by_agent[r["agent"]].append(r)
    for records in by_agent.values():
        records.sort(key=lambda r: (r["episode_id"], r["t_query"]))
    return by_agent


def replay_stream(episode: Episode, records: Sequence[Dict[str, Any]],
                  belief_spec: Dict[str, Any], seed: int,
                  generating_agent: str) -> float:
    """Full-state belief accuracy of one belief over one agent's stream.

    The belief's tie-break generator is seeded exactly as the live run
    seeded the generating agent's, so replaying an agent's own stream with
    its own belief spec reproduces the live numbers bit for bit.
    """
    policy_name = records[0]["policy"]
    rng = _derived_rng(seed, str(belief_spec["name"]), policy_name,
                       episode.episode_id)
    belief = build_belief(belief_spec, rng)
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)

    cursor = 0
    scripted = episode.scripted_observations
    hits = total = 0
    for record in records:
        t_query = int(record["t_query"])
        while cursor < len(scripted) and scripted[cursor].t <= t_query:
            belief.update(scripted[cursor])
            cursor += 1
        # Replicate the live decision loop's generator consumption exactly:
        # the harness called predict() once before every action (including
        # the final answer), and any tie-break draws those calls made are
        # part of the belief's state. Scoring then matches the live
        # full-state snapshot: the queried object scores by the final
        # (answer) prediction, everything else by predict_readonly.
        answer_pred = None
        for action in record["actions"]:
            answer_pred = belief.predict(str(record["object_id"]), t_query)
            if action["type"] == "sense":
                belief.update(SenseResult(
                    receptacle_id=str(action["receptacle_id"]), t=t_query,
                    contents=tuple(action["contents"])))
        assert answer_pred is not None   # actions always end with an answer
        for obj in episode.object_classes:
            guess = (answer_pred.argmax if obj == record["object_id"]
                     else belief.predict_readonly(obj, t_query).argmax)
            hits += guess == episode.true_location(obj, t_query)
            total += 1
    return hits / total if total else 0.0


def build_matrix(run_dir: pathlib.Path
                 ) -> Tuple[List[str], List[str], Dict[Tuple[str, str], float]]:
    """(generating agents, evaluating beliefs, accuracy matrix) for a run."""
    provenance = json.loads((run_dir / "provenance.json").read_text())
    config = yaml.safe_load(
        pathlib.Path(provenance["config_path"]).read_text())
    belief_specs: List[Dict[str, Any]] = list(config["agents"]["beliefs"])
    seed = int(provenance["seed"])
    bank = JsonlBank(path=pathlib.Path(provenance["bank_path"]))
    episodes = {e.episode_id: e for e in bank.episodes()}

    by_agent = _load_records(run_dir)
    agents = sorted(by_agent)
    eval_names: List[str] = []
    matrix: Dict[Tuple[str, str], float] = {}
    for agent in agents:
        by_episode: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in by_agent[agent]:
            by_episode[r["episode_id"]].append(r)
        for spec in belief_specs:
            accs = [replay_stream(episodes[eid], recs, spec, seed, agent)
                    for eid, recs in sorted(by_episode.items())]
            acc = sum(accs) / len(accs)
            name = str(spec["name"])
            if name not in eval_names:
                eval_names.append(name)
            matrix[(agent, name)] = acc
            logger.debug("replay %s on stream(%s): %.3f", name, agent, acc)
    return agents, eval_names, matrix


def render(run_dir: pathlib.Path, agents: List[str], beliefs: List[str],
           matrix: Dict[Tuple[str, str], float]) -> str:
    """Markdown report for one replay matrix."""
    lines = [
        "# Off-policy belief replay",
        "",
        f"Run: `{run_dir}`. Cell = full-state belief accuracy of the",
        "column's belief model on the observation stream the row's agent",
        "generated (tour + scripted sightings + that agent's senses).",
        "Columns separate belief quality from data; rows separate data",
        "quality from belief.",
        "",
        "| stream from \\ belief | " + " | ".join(beliefs) + " |",
        "|" + "|".join("---" for _ in range(len(beliefs) + 1)) + "|",
    ]
    for agent in agents:
        cells = [f"{matrix[(agent, b)]:.3f}" for b in beliefs]
        lines.append(f"| {agent} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Column spread at fixed row = belief-model differences on identical",
        "data. Row spread at fixed column = data-collection differences",
        "under an identical belief.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    agents, beliefs, matrix = build_matrix(args.run_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(args.run_dir, agents, beliefs, matrix))
    csv_path = args.out.with_suffix(".csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generating_agent"] + beliefs)
        for agent in agents:
            writer.writerow([agent] + [f"{matrix[(agent, b)]:.6f}"
                                       for b in beliefs])
    print(f"wrote {args.out} and {csv_path}")


if __name__ == "__main__":
    main()
