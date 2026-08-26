"""Candidate belief bake-off under the horizon-controlled passive protocol.

Runs the frozen instrument panel PLUS the candidate belief slate (see
:mod:`baselines.registry`) over every gate-passing bank from the fleet
run, entirely passively (:mod:`baselines.passive_eval` — no sensing
anywhere; every belief sees the identical tour + scripted sighting
stream, frozen per checkpoint). Candidates never enter the healthcheck:
gate verdicts come from the fleet summary, computed by the frozen panel
alone.

Outputs under the report directory:

* ``bakeoff_results.json`` — the full machine-readable result: protocol
  config, per-(household, model) cell scores and recency strata,
  cross-household aggregates with bootstrap intervals and per-household
  values, exact sample sizes. Deterministic in (banks, config, seed):
  byte-identical across re-runs — timestamps live in ``provenance.json``.
* ``leaderboard.md`` — the headline (D=7, h=1) table, one table per
  (D, h) cell, the recency-stratified table, and the per-household
  winners table.
* ``recency_curves.png`` — accuracy vs time-since-last-sighting, one
  line per model: how fast each belief's information decays.
* ``provenance.json`` — config/bank hashes, git commit, seed, timestamp.

``recommendation.md`` (which candidates to promote) is an authored
analysis, not a generated artifact; this module produces the evidence it
cites. All times are seconds since episode start; a day is 86 400 s.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import json
import logging
import pathlib
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, git_state
from baselines.healthcheck import BELIEF_PANEL
from baselines.passive_eval import (AggregateScore, CellScore,
                                    PassiveProtocolConfig, ScoredQuestion,
                                    aggregate_households, bootstrap_mean,
                                    evaluate_checkpoint, group_cells,
                                    group_recency)
from baselines.registry import CANDIDATE_SLATE, build_registered_belief
from baselines.types import Episode

logger = logging.getLogger(__name__)

HEADLINE_CELL = (7, 1.0)
"""The (checkpoint day, horizon days) cell the headline table reports."""

# Fixed-order categorical hues (panel first, then candidates); hue =
# model identity, consistent across every bake-off figure.
_MODEL_HUES = ("#2a78d6", "#eb6834", "#1baf7a", "#8a5cd6", "#c2312e",
               "#b8860b", "#4d4d4d")
_INK = "#33322e"
_GRID = "#dddbd2"


def bakeoff_specs() -> Tuple[Dict[str, Any], ...]:
    """Panel + candidate belief specs, in fixed display order."""
    return (*BELIEF_PANEL, *CANDIDATE_SLATE)


def _cell_key(cell: Tuple[int, float]) -> str:
    return f"D={cell[0]},h={cell[1]:g}"


def _score_dict(score: CellScore) -> Dict[str, Any]:
    return {"n_questions": score.n_questions,
            "top1_accuracy": round(score.top1_accuracy, 6),
            "mean_log_loss": round(score.mean_log_loss, 6)}


def _aggregate_dict(agg: AggregateScore) -> Dict[str, Any]:
    return {"n_households": agg.n_households,
            "n_questions": agg.n_questions,
            "mean": round(agg.mean, 6),
            "ci95": [round(agg.ci_low, 6), round(agg.ci_high, 6)],
            "per_household": {h: round(v, 6)
                              for h, v in sorted(agg.per_household.items())}}


def run_model_on_episode(episode: Episode, spec: Dict[str, Any], seed: int,
                         config: PassiveProtocolConfig
                         ) -> List[ScoredQuestion]:
    """All checkpoints of one belief spec on one episode.

    A fresh belief per checkpoint, seeded from (seed, "bakeoff", spec
    name, episode, checkpoint) so results are independent of run order.
    """
    scored: List[ScoredQuestion] = []
    for checkpoint in config.checkpoint_days:
        rng = _derived_rng(seed, "bakeoff", str(spec["name"]),
                           episode.episode_id, str(checkpoint))
        belief = build_registered_belief(dict(spec), rng)
        scored += evaluate_checkpoint(episode, belief, checkpoint, config)
    return scored


@dataclasses.dataclass(frozen=True)
class ModelResult:
    """One model's scores across the fleet's gate-passing banks."""

    spec_name: str                 # registry/config name
    display_name: str              # the belief's self-reported name
    cells: Dict[str, Dict[Tuple[int, float], CellScore]]   # household ->
    recency: Dict[str, Dict[str, CellScore]]               # household ->


def run_bakeoff(banks: Sequence[pathlib.Path], seed: int,
                config: PassiveProtocolConfig) -> List[ModelResult]:
    """Every panel + candidate model over every bank, passively.

    The household unit is the BANK (one exported household each; a
    multi-episode bank pools its episodes), labeled by the bank filename
    stem — household_ids alone collide across profile sets (revamp_v1
    hh1 and storyfirst hh1 are both ``hh_001``).
    """
    by_label: Dict[str, List[Episode]] = {}
    for path in banks:
        label = path.stem.removesuffix("_bank")
        if label in by_label:
            raise ValueError(f"duplicate bank label {label!r}")
        by_label[label] = list(JsonlBank(path=path).episodes())

    results: List[ModelResult] = []
    for spec in bakeoff_specs():
        cells: Dict[str, Dict[Tuple[int, float], CellScore]] = {}
        recency: Dict[str, Dict[str, CellScore]] = {}
        display = build_registered_belief(
            dict(spec), _derived_rng(seed, "name")).name
        for label, episodes in by_label.items():
            scored = [q for episode in episodes
                      for q in run_model_on_episode(episode, dict(spec),
                                                    seed, config)]
            cells[label] = group_cells(scored)
            recency[label] = group_recency(scored)
        results.append(ModelResult(spec_name=str(spec["name"]),
                                   display_name=display, cells=cells,
                                   recency=recency))
        logger.info("bakeoff: %s done (%d households)", display,
                    len(episodes))
    return results


def results_json(results: Sequence[ModelResult], banks: Sequence[pathlib.Path],
                 seed: int, config: PassiveProtocolConfig) -> Dict[str, Any]:
    """The deterministic machine-readable report (no timestamps here)."""
    out: Dict[str, Any] = {
        "protocol": dataclasses.asdict(config),
        "seed": seed,
        "banks": [str(p) for p in banks],
        "models": [],
    }
    for result in results:
        aggregates = aggregate_households(result.cells, seed)
        recency_agg = _aggregate_recency(result.recency, seed)
        out["models"].append({
            "name": result.spec_name,
            "display_name": result.display_name,
            "per_household": {
                household: {
                    "cells": {_cell_key(c): _score_dict(s)
                              for c, s in cells.items()},
                    "recency": {label: _score_dict(s)
                                for label, s
                                in sorted(result.recency[household].items())},
                }
                for household, cells in sorted(result.cells.items())},
            "aggregate_cells": {
                _cell_key(c): {"top1_accuracy": _aggregate_dict(acc),
                               "mean_log_loss": _aggregate_dict(loss)}
                for c, (acc, loss) in aggregates.items()},
            "aggregate_recency": {
                label: {"top1_accuracy": _aggregate_dict(acc),
                        "mean_log_loss": _aggregate_dict(loss)}
                for label, (acc, loss) in recency_agg.items()},
        })
    return out


def _aggregate_recency(recency_by_household: Mapping[str, Dict[str,
                                                               CellScore]],
                       seed: int
                       ) -> Dict[str, Tuple[AggregateScore, AggregateScore]]:
    """Cross-household aggregates per recency bin (bins present anywhere;
    each bin averages the households that have it — bin membership is a
    property of the household's sighting stream, not of the model)."""
    labels = sorted({label for bins in recency_by_household.values()
                     for label in bins})
    out: Dict[str, Tuple[AggregateScore, AggregateScore]] = {}
    for label in labels:
        present = {h: bins[label] for h, bins in
                   recency_by_household.items() if label in bins}
        accs = {h: s.top1_accuracy for h, s in present.items()}
        losses = {h: s.mean_log_loss for h, s in present.items()}
        n_questions = sum(s.n_questions for s in present.values())
        out[label] = (bootstrap_mean(accs, n_questions, seed),
                      bootstrap_mean(losses, n_questions, seed))
    return out


# ------------------------------------------------------------ leaderboard


def _fmt_agg(agg: AggregateScore) -> str:
    spread = (f" [{agg.ci_low:.3f}, {agg.ci_high:.3f}]"
              if agg.n_households > 1 else "")
    return f"{agg.mean:.3f}{spread}"


def _cell_table(results: Sequence[ModelResult], cell: Tuple[int, float],
                seed: int) -> List[str]:
    """One markdown table for one (D, h) cell, sorted by accuracy."""
    rows = []
    for result in results:
        aggs = aggregate_households(result.cells, seed)
        if cell not in aggs:
            continue
        acc, loss = aggs[cell]
        rows.append((result.display_name, acc, loss))
    rows.sort(key=lambda r: -r[1].mean)
    if not rows:
        return [f"(no questions in cell {_cell_key(cell)})", ""]
    n = rows[0][1]
    lines = [
        f"Cell `{_cell_key(cell)}`: {n.n_households} households, "
        f"{n.n_questions} questions total. Accuracy/log-loss are "
        f"unweighted per-household means; brackets are the 95% bootstrap "
        f"interval over households; per-household spread is min..max.",
        "",
        "| model | top-1 accuracy | acc spread | mean log-loss | "
        "loss spread |",
        "|---|---|---|---|---|",
    ]
    for name, acc, loss in rows:
        acc_vals = sorted(acc.per_household.values())
        loss_vals = sorted(loss.per_household.values())
        lines.append(
            f"| {name} | {_fmt_agg(acc)} "
            f"| {acc_vals[0]:.3f}..{acc_vals[-1]:.3f} "
            f"| {_fmt_agg(loss)} "
            f"| {loss_vals[0]:.3f}..{loss_vals[-1]:.3f} |")
    lines.append("")
    return lines


def _winners_table(results: Sequence[ModelResult],
                   cell: Tuple[int, float]) -> List[str]:
    """Per-household winners at the headline cell (accuracy and log-loss)."""
    households = sorted({h for r in results for h in r.cells})
    lines = [
        f"Per-household winners at `{_cell_key(cell)}` (a model that only "
        "wins on one household type is still informative):",
        "",
        "| household | best accuracy | best log-loss |",
        "|---|---|---|",
    ]
    for household in households:
        scored = [(r.display_name, r.cells[household][cell])
                  for r in results
                  if cell in r.cells.get(household, {})]
        if not scored:
            continue
        best_acc = max(scored, key=lambda s: s[1].top1_accuracy)
        best_loss = min(scored, key=lambda s: s[1].mean_log_loss)
        lines.append(
            f"| {household} | {best_acc[0]} ({best_acc[1].top1_accuracy:.3f})"
            f" | {best_loss[0]} ({best_loss[1].mean_log_loss:.3f}) |")
    lines.append("")
    return lines


def render_leaderboard(results: Sequence[ModelResult], seed: int,
                       config: PassiveProtocolConfig) -> str:
    """The full markdown leaderboard report."""
    all_cells = sorted({c for r in results
                        for cells in r.cells.values() for c in cells})
    lines = [
        "# Passive belief bake-off — horizon-controlled protocol",
        "",
        "Frozen panel + candidate slate, evaluated with NO sensing: per "
        "checkpoint day D the belief sees the tour plus sightings from "
        "days before D only, and answers questions at forecast horizons "
        "h days past D. Cells are never pooled across h. The household "
        "is the unit of analysis throughout. (The old per-day passive "
        "curve is descriptive-only — it conflates history, recency, and "
        "horizon; this protocol replaces it for any learning-curve "
        "claim.)",
        "",
        f"## Headline cell {_cell_key(HEADLINE_CELL)}",
        "",
        *_cell_table(results, HEADLINE_CELL, seed),
        "## Recency stratification (pooled over checkpoints)",
        "",
        "Accuracy binned by time since the belief's last sighting of the "
        "queried object — how fast each model's information decays "
        "(`recency_curves.png` plots this). Values are per-household "
        "means; n = questions pooled over the households that have the "
        "bin.",
        "",
        *_recency_table(results, seed),
        *_winners_table(results, HEADLINE_CELL),
        "## All cells",
        "",
    ]
    for cell in all_cells:
        lines += [f"### {_cell_key(cell)}", "",
                  *_cell_table(results, cell, seed)]
    return "\n".join(lines)


def _recency_table(results: Sequence[ModelResult],
                   seed: int) -> List[str]:
    labels = _recency_labels(results)
    lines = ["| model | " + " | ".join(labels) + " |",
             "|" + "---|" * (len(labels) + 1)]
    for result in results:
        agg = _aggregate_recency(result.recency, seed)
        cells = []
        for label in labels:
            if label in agg:
                acc, _ = agg[label]
                cells.append(f"{acc.mean:.3f} (n={acc.n_questions})")
            else:
                cells.append("—")
        lines.append(f"| {result.display_name} | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def _recency_labels(results: Sequence[ModelResult]) -> List[str]:
    """Bin labels in increasing-staleness order (from the protocol config
    ordering embedded in the label text; 'never' sorts last)."""
    seen = {label for r in results for bins in r.recency.values()
            for label in bins}
    def key(label: str) -> Tuple[int, float]:
        if label == "never":
            return (1, 0.0)
        return (0, float(label[1:].split("h", 1)[0]))
    return sorted(seen, key=key)


def plot_recency_curves(results: Sequence[ModelResult], seed: int,
                        path: pathlib.Path) -> None:
    """Overlaid accuracy-vs-recency curves, one line per model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [l for l in _recency_labels(results) if l != "never"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, result in enumerate(results):
        agg = _aggregate_recency(result.recency, seed)
        xs = [j for j, label in enumerate(labels) if label in agg]
        ys = [agg[label][0].mean for label in labels if label in agg]
        ax.plot(xs, ys, color=_MODEL_HUES[i % len(_MODEL_HUES)],
                linewidth=2, marker="o", markersize=4.5,
                label=result.display_name)
    ax.set_xticks(range(len(labels)), labels, fontsize=8)
    ax.set_xlabel("time since last sighting of the queried object",
                  color=_INK)
    ax.set_ylabel("top-1 accuracy (mean over households)", color=_INK)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("Information decay by belief model "
                 "(horizon-controlled passive protocol)",
                 color=_INK, loc="left")
    ax.tick_params(colors=_INK, labelsize=9)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("wrote %s", path)


# ------------------------------------------------------------------ CLI


def _passing_banks(fleet_summary: pathlib.Path) -> List[pathlib.Path]:
    """Bank paths of every gate-passing fleet row."""
    summary = json.loads(fleet_summary.read_text())
    paths = [pathlib.Path(row["bank_path"]) for row in summary["banks"]
             if row["status"] == "ok" and row["gates_pass"]]
    if not paths:
        raise ValueError(f"{fleet_summary}: no gate-passing banks")
    return paths


def write_reports(results: Sequence[ModelResult],
                  banks: Sequence[pathlib.Path], seed: int,
                  config: PassiveProtocolConfig,
                  out_dir: pathlib.Path) -> None:
    """All bake-off artifacts except the authored recommendation.md."""
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = results_json(results, banks, seed, config)
    (out_dir / "bakeoff_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (out_dir / "leaderboard.md").write_text(
        render_leaderboard(results, seed, config))
    plot_recency_curves(results, seed, out_dir / "recency_curves.png")
    commit, dirty = git_state(pathlib.Path(__file__).resolve().parent)
    (out_dir / "provenance.json").write_text(json.dumps({
        "banks": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in banks},
        "git_commit": commit, "git_dirty": dirty, "seed": seed,
        "timestamp": datetime.datetime.now(
            datetime.timezone.utc).isoformat()}, indent=2) + "\n")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fleet-summary", type=pathlib.Path,
                        default=pathlib.Path(
                            "reports/baselines/fleet/fleet_summary.json"),
                        help="gate verdicts source; only passing banks run")
    parser.add_argument("--banks", type=pathlib.Path, nargs="*",
                        default=None,
                        help="explicit bank list (overrides --fleet-summary)")
    parser.add_argument("--out-dir", type=pathlib.Path,
                        default=pathlib.Path("reports/baselines/bakeoff"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    banks = (list(args.banks) if args.banks
             else _passing_banks(args.fleet_summary))
    config = PassiveProtocolConfig(seed=args.seed)
    results = run_bakeoff(banks, args.seed, config)
    write_reports(results, banks, args.seed, config, args.out_dir)
    print(f"bakeoff: {len(results)} models x {len(banks)} banks "
          f"-> {args.out_dir}")


if __name__ == "__main__":
    main()
