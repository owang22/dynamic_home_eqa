"""Trial run for disambiguation sensing on the hypothesis mixture.

Two households (the day-0-question trial banks), episodes truncated to
the first ``--days`` question days. Agents are the hypothesis mixture
under the myopic VoI threshold policy (the ``beta = 0`` frontier) and
under :class:`~baselines.policies.hypothesis_disambiguation.
HypothesisDisambiguationSense` at several ``beta``, each swept over the
same lambdas so every policy traces a cost-accuracy frontier.

Figures (the brief's three):

1. ``frontier.png`` — task accuracy vs realized senses per day, one line
   per beta (0 = myopic), points = lambdas.
2. ``ess_over_time.png`` — the mixture's effective sample size over the
   episode, with and without disambiguation, at the middle lambda.
3. ``sense_split.png`` — per configuration, senses the myopic rule would
   have taken anyway ("needed") vs senses only the weight-sharpening
   bonus paid for ("disambiguation").

Everything is written under ``--out-dir`` along with
``trial_results.json`` (all measured numbers). Times are seconds since
episode start.

Usage:
  python -m baselines.hypothesis_mixture_study --days 7 \\
      --out-dir results/hypothesis_mixture_trial
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import pathlib
import random
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.beliefs.hypothesis_mixture import HypothesisMixture
from baselines.harness import run_episode
from baselines.policies.hypothesis_disambiguation import (
    HypothesisDisambiguationSense)
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import Episode

logger = logging.getLogger(__name__)

DEFAULT_BANK_DIR = pathlib.Path("banks/baselines/fleet_day0")
LAMBDAS = (0.02, 0.08, 0.2)
BETAS = (0.0, 0.5, 2.0)
"""beta 0 is the myopic policy itself; the others price the entropy
bonus at half and at double the scale of a typical voi increment."""

_HUES = {0.0: "#6f6d64", 0.5: "#2a78d6", 2.0: "#c2503a"}
_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"


def truncated(episode: Episode, days: int) -> Episode:
    """The episode with only its first ``days`` question days; evidence
    and truth stay whole (the harness never reads past the last query)."""
    return dataclasses.replace(
        episode, questions_by_day=episode.questions_by_day[:days])


@dataclasses.dataclass(frozen=True)
class TrialCell:
    """One (household, beta, lambda) run."""

    household_id: str
    beta: float
    lam: float
    n_questions: int
    n_days: int
    accuracy: float
    senses_per_day: float
    senses_needed: int
    senses_disambiguation: int
    final_ess: float
    ess_series: List[Tuple[int, float]]


def run_cell(episode: Episode, beta: float, lam: float,
             seed: int) -> TrialCell:
    belief = HypothesisMixture(random.Random(seed))
    rng = random.Random(seed + 1)
    policy: VoIThresholdSense
    if beta == 0.0:
        policy = VoIThresholdSense(rng, lam=lam)
    else:
        policy = HypothesisDisambiguationSense(rng, lam=lam, belief=belief,
                                               beta=beta)
    records = list(run_episode(Agent(belief=belief, policy=policy), episode))
    n_days = len(episode.questions_by_day)
    split = (policy.sense_split
             if isinstance(policy, HypothesisDisambiguationSense) else [])
    n_senses = sum(r.n_senses for r in records)
    return TrialCell(
        household_id=episode.household_id, beta=beta, lam=lam,
        n_questions=len(records), n_days=n_days,
        accuracy=statistics.mean(float(r.correct) for r in records),
        senses_per_day=n_senses / n_days,
        senses_needed=(sum(1 for _, needed in split if needed)
                       if split else n_senses),
        senses_disambiguation=sum(1 for _, needed in split if not needed),
        final_ess=belief.effective_sample_size,
        ess_series=list(belief.ess_history))


# --------------------------------------------------------------- figures


def _style(ax: Any) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    ax.tick_params(colors=_MUTED, labelsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)


def render_frontier(cells: Sequence[TrialCell],
                    out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for beta in sorted({c.beta for c in cells}):
        points: Dict[float, Tuple[float, float]] = {}
        for lam in sorted({c.lam for c in cells}):
            group = [c for c in cells if c.beta == beta and c.lam == lam]
            points[lam] = (
                statistics.mean(c.senses_per_day for c in group),
                statistics.mean(c.accuracy for c in group))
        xs = [points[lam][0] for lam in sorted(points, reverse=True)]
        ys = [points[lam][1] for lam in sorted(points, reverse=True)]
        label = "myopic (beta=0)" if beta == 0.0 else f"beta={beta:g}"
        ax.plot(xs, ys, color=_HUES[beta], linewidth=1.8, marker="o",
                markersize=5, label=label, zorder=2)
    ax.set_xlabel("realized senses per day (mean over households)",
                  fontsize=9, color=_INK)
    ax.set_ylabel("task accuracy", fontsize=9, color=_INK)
    ax.set_title("Does paying for disambiguation buy accuracy back?",
                 fontsize=9.5, color=_INK, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=_INK)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_ess(cells: Sequence[TrialCell], lam: float,
               out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    households = sorted({c.household_id for c in cells})
    fig, axes = plt.subplots(1, len(households),
                             figsize=(5.4 * len(households), 3.6),
                             squeeze=False)
    for ax, household in zip(axes[0], households):
        for beta in sorted({c.beta for c in cells}):
            cell = next(c for c in cells if c.household_id == household
                        and c.beta == beta and c.lam == lam)
            xs = [t / 86_400 for t, _ in cell.ess_series]
            ys = [e for _, e in cell.ess_series]
            label = "myopic (beta=0)" if beta == 0.0 else f"beta={beta:g}"
            ax.plot(xs, ys, color=_HUES[beta], linewidth=1.1, label=label,
                    zorder=2)
        ax.set_xlabel("day", fontsize=9, color=_INK)
        ax.set_ylabel("effective sample size", fontsize=9, color=_INK)
        ax.set_title(f"{household} (lambda={lam:g})", fontsize=9.5,
                     color=_INK, loc="left")
        ax.legend(frameon=False, fontsize=8, labelcolor=_INK)
        _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_sense_split(cells: Sequence[TrialCell],
                       out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    configs = sorted({(c.beta, c.lam) for c in cells if c.beta > 0.0})
    labels = [f"b={beta:g}\nl={lam:g}" for beta, lam in configs]
    needed, extra = [], []
    for beta, lam in configs:
        group = [c for c in cells if c.beta == beta and c.lam == lam]
        needed.append(sum(c.senses_needed for c in group))
        extra.append(sum(c.senses_disambiguation for c in group))
    fig, ax = plt.subplots(figsize=(1.2 + 0.9 * len(configs), 4.0))
    xs = range(len(configs))
    ax.bar(xs, needed, color=_MUTED, width=0.6,
           label="needed by the question", zorder=2)
    ax.bar(xs, extra, bottom=needed, color="#2a78d6", width=0.6,
           label="taken for disambiguation", zorder=2)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel("senses (both households)", fontsize=9, color=_INK)
    ax.set_title("What the extra budget actually bought", fontsize=9.5,
                 color=_INK, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=_INK)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------- main


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank-dir", type=pathlib.Path,
                        default=DEFAULT_BANK_DIR)
    parser.add_argument("--households", type=int, default=2)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", type=pathlib.Path,
                        default=pathlib.Path("results/hypothesis_mixture_trial"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    banks = sorted(args.bank_dir.glob("*_bank.jsonl"))[:args.households]
    if not banks:
        parser.error(f"no banks under {args.bank_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    cells: List[TrialCell] = []
    for path in banks:
        episode = truncated(next(JsonlBank(path).episodes()), args.days)
        for beta in BETAS:
            for lam in LAMBDAS:
                cell = run_cell(episode, beta, lam, args.seed)
                cells.append(cell)
                logger.info(
                    "%s beta=%g lambda=%g: acc %.3f, %.1f senses/day "
                    "(%d disambiguation), final ESS %.2f",
                    cell.household_id, beta, lam, cell.accuracy,
                    cell.senses_per_day, cell.senses_disambiguation,
                    cell.final_ess)

    mid_lam = sorted(LAMBDAS)[len(LAMBDAS) // 2]
    render_frontier(cells, args.out_dir / "frontier.png")
    render_ess(cells, mid_lam, args.out_dir / "ess_over_time.png")
    render_sense_split(cells, args.out_dir / "sense_split.png")
    (args.out_dir / "trial_results.json").write_text(json.dumps(
        [dataclasses.asdict(c) for c in cells], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
