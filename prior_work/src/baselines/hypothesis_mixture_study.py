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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.beliefs.hypothesis_mixture import (DEFAULT_ABSENCE_UNIFORMS,
                                                  DEFAULT_PARTICLE_SPECS,
                                                  HypothesisMixture)
from baselines.harness import run_episode
from baselines.policies.hypothesis_disambiguation import (
    HypothesisDisambiguationSense)
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.registry import build_registered_belief
from baselines.types import Episode

logger = logging.getLogger(__name__)

DEFAULT_BANK_DIR = pathlib.Path("banks/baselines/fleet_day0")
ABSENCE_WEIGHTS = (0.0, 0.1, 0.25, 0.5, 1.0)
"""Swept to set :data:`~baselines.beliefs.hypothesis_mixture.
DEFAULT_ABSENCE_WEIGHT`; 0.0 is presence-only scoring."""
LAMBDAS = (0.02, 0.08, 0.2)
BETAS = (0.0, 0.02, 0.05, 0.1, 0.25)
"""beta 0 is the myopic policy itself. The rest are set against the
bonus's CEILING: a binary Jensen-Shannon divergence cannot exceed
``ln 2 = 0.693``, so the bonus contributes at most ``0.693 * beta``,
while voi runs 0.01-0.1 at these lambdas. The earlier 0.5/2.0 sweep gave
the bonus up to 1.39 against a voi of ~0.05 and simply drowned the
question-answering term — visible in that run as beta=2 spending most of
its budget on disambiguation."""

ROOM_COST_LEVELS = (0.0, 0.5, 1.0)
"""Room-change surcharge ``c``: a sense outside the robot's room costs
``1 + c``. Raising it is the condition under which disambiguation should
look BEST — cheap in-room looks let the robot pick up weight evidence
without a trip — so it is the discriminating test, not a robustness
check."""

BUDGET_SCALE = True
"""Scale ``budget_per_day`` by ``1 + c`` alongside the room cost, so a
run at c = 1 can still afford the same number of cross-room senses and
the comparison is not simply "less budget". Same-room senses stay at
1.0, so the scaled budget buys strictly more of them — which is the
asymmetry the sweep is probing."""

_HUES = {0.0: "#6f6d64", 0.02: "#8fb8e8", 0.05: "#2a78d6",
         0.1: "#1a4f91", 0.25: "#c2503a"}
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
    """One (household, room cost, beta, lambda) run."""

    household_id: str
    room_cost: float
    budget_per_day: int
    beta: float
    lam: float
    n_questions: int
    n_days: int
    accuracy: float
    senses_per_day: float
    same_room_senses: int
    senses_needed: int
    senses_disambiguation: int
    final_ess: float
    correct: List[bool]
    """Per-question correctness in bank order. Every cell at one
    (household, room cost, lambda) sees the identical question sequence,
    so betas can be compared question-by-question — a paired test, which
    is far better powered than comparing two independent accuracies."""
    ess_series: List[Tuple[int, float]]


def with_budget(episode: Episode, budget_per_day: int) -> Episode:
    """The episode at a different per-day sensing budget."""
    return dataclasses.replace(episode, budget_per_day=budget_per_day)


def run_cell(episode: Episode, beta: float, lam: float, seed: int,
             room_cost: float = 0.0) -> TrialCell:
    belief = HypothesisMixture(random.Random(seed))
    rng = random.Random(seed + 1)
    policy: VoIThresholdSense
    if beta == 0.0:
        policy = VoIThresholdSense(rng, lam=lam)
    else:
        policy = HypothesisDisambiguationSense(rng, lam=lam, belief=belief,
                                               beta=beta)
    records = list(run_episode(Agent(belief=belief, policy=policy), episode,
                               room_change_cost=room_cost))
    n_days = len(episode.questions_by_day)
    split = (policy.sense_split
             if isinstance(policy, HypothesisDisambiguationSense) else [])
    n_senses = sum(r.n_senses for r in records)
    return TrialCell(
        household_id=episode.household_id, room_cost=room_cost,
        budget_per_day=episode.budget_per_day, beta=beta, lam=lam,
        n_questions=len(records), n_days=n_days,
        accuracy=statistics.mean(float(r.correct) for r in records),
        senses_per_day=n_senses / n_days,
        same_room_senses=sum(r.same_room_senses for r in records),
        senses_needed=(sum(1 for _, needed in split if needed)
                       if split else n_senses),
        senses_disambiguation=sum(1 for _, needed in split if not needed),
        final_ess=belief.effective_sample_size,
        correct=[bool(r.correct) for r in records],
        ess_series=list(belief.ess_history))


# ------------------------------------------------- absence-weight sweep


@dataclasses.dataclass(frozen=True)
class AbsenceCell:
    """One passive pass at one absence setting."""

    household_id: str
    absence_weight: float
    absence_uniforms: float
    labels: List[str]
    weights: List[float]
    ess: float
    presence_spread: float
    absence_spread: float
    passive_accuracy: float


def _spread(values: Sequence[float]) -> float:
    """Max minus min — how much a scoring half discriminates between
    particles. A half whose spread is near zero is paying everyone the
    same and cannot move the weights."""
    return max(values) - min(values) if values else 0.0


def run_absence_cell(episode: Episode, absence_weight: float,
                     absence_uniforms: float, seed: int) -> AbsenceCell:
    """Passive diet (no sensing), weights scored under one setting, then
    the mixture's accuracy on the bank's own questions."""
    belief = HypothesisMixture(random.Random(seed),
                               absence_weight=absence_weight,
                               absence_uniforms=absence_uniforms)
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)
    evidence = list(episode.evidence_stream())
    cursor = 0
    correct = total = 0
    for day in episode.questions_by_day:
        for question in day:
            while (cursor < len(evidence)
                   and evidence[cursor].t <= question.t_query):
                belief.update(evidence[cursor])
                cursor += 1
            prediction = belief.predict_readonly(question.object_id,
                                                 question.t_query)
            correct += int(prediction.argmax == episode.true_location(
                question.object_id, question.t_query))
            total += 1
    return AbsenceCell(
        household_id=episode.household_id, absence_weight=absence_weight,
        absence_uniforms=absence_uniforms,
        labels=[p.name.split("(")[0] for p in belief.particles],
        weights=belief.weights, ess=belief.effective_sample_size,
        presence_spread=_spread(belief.presence_totals),
        absence_spread=_spread(belief.absence_totals),
        passive_accuracy=correct / total if total else 0.0)


def format_absence_report(cells: Sequence[AbsenceCell]) -> str:
    labels = cells[0].labels
    lines = ["# Setting the absence weight", "",
             "Passive diet, no sensing. `spread` is max-minus-min of the "
             "cumulative log likelihood each half of the scoring paid out "
             "across particles: the half with the larger spread is the one "
             "moving the weights.", ""]
    for household in sorted({c.household_id for c in cells}):
        lines += [f"## {household}", "",
                  "| absence_weight | threshold | ESS | presence spread | "
                  "absence spread | passive acc | " + " | ".join(labels) + " |",
                  "|---" * (6 + len(labels)) + "|"]
        for cell in [c for c in cells if c.household_id == household]:
            weights = " | ".join(f"{w:.2f}" for w in cell.weights)
            lines.append(
                f"| {cell.absence_weight:g} | {cell.absence_uniforms:g} | "
                f"{cell.ess:.2f} | {cell.presence_spread:.0f} | "
                f"{cell.absence_spread:.0f} | {cell.passive_accuracy:.3f} | "
                f"{weights} |")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------- paired testing


BOOTSTRAP_RESAMPLES = 2000


def paired_delta(treatment: Sequence[bool], control: Sequence[bool],
                 seed: int = 0) -> Tuple[float, float, float]:
    """Mean per-question accuracy difference and a bootstrap interval.

    Both arms answered the SAME questions in the same order, so the unit
    of analysis is the per-question difference (+1 / 0 / -1) rather than
    two independent accuracies. Resampling those differences gives an
    interval that already nets out how hard the questions were, which is
    most of the variance an unpaired comparison has to fight.

    Returns ``(mean, low, high)`` at the 95% level. An interval straddling
    0 means this trial cannot sign the effect — which, at trial sizes, is
    the expected outcome for anything small.
    """
    diffs = [float(a) - float(b) for a, b in zip(treatment, control)]
    if not diffs:
        return 0.0, 0.0, 0.0
    mean = statistics.mean(diffs)
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(
        statistics.mean([diffs[rng.randrange(n)] for _ in range(n)])
        for _ in range(BOOTSTRAP_RESAMPLES))
    low = means[int(0.025 * BOOTSTRAP_RESAMPLES)]
    high = means[int(0.975 * BOOTSTRAP_RESAMPLES) - 1]
    return mean, low, high


def pooled_correct(cells: Sequence[TrialCell], room_cost: float, lam: float,
                   beta: float) -> List[bool]:
    """Per-question correctness for one (room cost, lambda, beta),
    concatenated over households in a fixed household order so the pairing
    with another beta lines up question for question."""
    chosen = sorted((c for c in cells if c.room_cost == room_cost
                     and c.lam == lam and c.beta == beta),
                    key=lambda c: c.household_id)
    return [flag for cell in chosen for flag in cell.correct]


def format_paired_report(cells: Sequence[TrialCell], seed: int = 0) -> str:
    lines = ["# Disambiguation sensing against the myopic policy", "",
             "Paired per-question comparison against `beta = 0` at the same "
             "room cost and lambda, bootstrapped over questions (95%). "
             "`senses/day` and `same-room %` say what the budget bought.", ""]
    for room_cost in sorted({c.room_cost for c in cells}):
        budget = next(c.budget_per_day for c in cells
                      if c.room_cost == room_cost)
        lines += [f"## room_change_cost c = {room_cost:g} "
                  f"(budget {budget}/day)", "",
                  "| lambda | beta | accuracy | delta vs myopic | 95% CI | "
                  "senses/day | same-room % | disambig senses | ESS |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for lam in sorted({c.lam for c in cells}):
            control = pooled_correct(cells, room_cost, lam, 0.0)
            for beta in sorted({c.beta for c in cells}):
                group = [c for c in cells if c.room_cost == room_cost
                         and c.lam == lam and c.beta == beta]
                if not group:
                    continue
                treatment = pooled_correct(cells, room_cost, lam, beta)
                mean, low, high = paired_delta(treatment, control, seed)
                senses = sum(c.senses_per_day * c.n_days for c in group)
                same_room = (sum(c.same_room_senses for c in group) / senses
                             if senses else 0.0)
                marker = "" if beta else " (baseline)"
                lines.append(
                    f"| {lam:g} | {beta:g}{marker} | "
                    f"{statistics.mean(c.accuracy for c in group):.4f} | "
                    f"{mean:+.4f} | [{low:+.4f}, {high:+.4f}] | "
                    f"{statistics.mean(c.senses_per_day for c in group):.1f} | "
                    f"{same_room:.0%} | "
                    f"{sum(c.senses_disambiguation for c in group)} | "
                    f"{statistics.mean(c.final_ess for c in group):.2f} |")
        lines.append("")
    return "\n".join(lines)


# ----------------------------------------------- what the weights buy


class UniformWeightMixture(HypothesisMixture):
    """Ablation: the same mixture with its weights pinned uniform.

    Scoring is computed and then discarded, so this is the unweighted
    average of the identical particles on the identical diet. The gap
    between it and the real mixture is the entire value of knowing which
    hypothesis is right — and therefore the ceiling on what any amount of
    disambiguation sensing could ever buy.
    """

    def _apply_event(self, log_likelihoods: Sequence[float], t: int) -> None:
        self.ess_history.append((t, self.effective_sample_size))


def passive_accuracy(episode: Episode, belief: Any) -> float:
    """Argmax accuracy on the bank's questions under the passive diet."""
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)
    evidence = list(episode.evidence_stream())
    cursor = correct = total = 0
    for day in episode.questions_by_day:
        for question in day:
            while (cursor < len(evidence)
                   and evidence[cursor].t <= question.t_query):
                belief.update(evidence[cursor])
                cursor += 1
            prediction = belief.predict_readonly(question.object_id,
                                                 question.t_query)
            correct += int(prediction.argmax == episode.true_location(
                question.object_id, question.t_query))
            total += 1
    return correct / total if total else 0.0


def weight_value(episode: Episode, seed: int) -> Dict[str, float]:
    """Passive accuracy of the weighted mixture, the uniform-weight
    ablation, and every particle alone."""
    rows = {
        "mixture (learned weights)": passive_accuracy(
            episode, HypothesisMixture(random.Random(seed))),
        "mixture (uniform weights)": passive_accuracy(
            episode, UniformWeightMixture(random.Random(seed)))}
    for spec in DEFAULT_PARTICLE_SPECS:
        rows[str(spec["name"])] = passive_accuracy(
            episode, build_registered_belief(dict(spec), random.Random(seed)))
    return rows


def format_weight_value_report(
        per_household: Mapping[str, Mapping[str, float]]) -> str:
    lines = ["# What do the mixture weights actually buy?", "",
             "Passive diet, no sensing. `learned` minus `uniform` is the "
             "value of knowing which hypothesis is right, and therefore the "
             "ceiling on what disambiguation sensing could buy. Particle "
             "rows show the spread of skill the weights have to work with.",
             ""]
    for household, rows in sorted(per_household.items()):
        lines += [f"## {household}", "", "| belief | passive accuracy |",
                  "|---|---|"]
        lines += [f"| {name} | {value:.4f} |" for name, value in rows.items()]
        delta = (rows["mixture (learned weights)"]
                 - rows["mixture (uniform weights)"])
        best = max(v for k, v in rows.items() if not k.startswith("mixture"))
        lines += ["",
                  f"learned - uniform: **{delta:+.4f}**",
                  f"learned - best single particle: "
                  f"**{rows['mixture (learned weights)'] - best:+.4f}**", ""]
    return "\n".join(lines)


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
    """One panel per room-change cost: accuracy against realized senses."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    costs = sorted({c.room_cost for c in cells})
    fig, axes = plt.subplots(1, len(costs), figsize=(4.9 * len(costs), 4.3),
                             squeeze=False, sharey=True)
    for ax, room_cost in zip(axes[0], costs):
        here = [c for c in cells if c.room_cost == room_cost]
        budget = here[0].budget_per_day
        for beta in sorted({c.beta for c in here}):
            points: Dict[float, Tuple[float, float]] = {}
            for lam in sorted({c.lam for c in here}):
                group = [c for c in here if c.beta == beta and c.lam == lam]
                points[lam] = (
                    statistics.mean(c.senses_per_day for c in group),
                    statistics.mean(c.accuracy for c in group))
            xs = [points[lam][0] for lam in sorted(points, reverse=True)]
            ys = [points[lam][1] for lam in sorted(points, reverse=True)]
            label = "myopic (beta=0)" if beta == 0.0 else f"beta={beta:g}"
            ax.plot(xs, ys, color=_HUES[beta], linewidth=1.7, marker="o",
                    markersize=4.5, label=label, zorder=2)
        ax.set_xlabel("realized senses per day", fontsize=9, color=_INK)
        ax.set_title(f"c = {room_cost:g}, budget {budget}/day",
                     fontsize=9.5, color=_INK, loc="left")
        _style(ax)
    axes[0][0].set_ylabel("task accuracy", fontsize=9, color=_INK)
    axes[0][-1].legend(frameon=False, fontsize=8, labelcolor=_INK)
    fig.suptitle("Does paying for disambiguation buy accuracy back?",
                 fontsize=10, color=_INK, x=0.01, ha="left")
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

    configs = sorted({(c.room_cost, c.beta, c.lam)
                      for c in cells if c.beta > 0.0})
    labels = [f"c={rc:g}\nb={beta:g}\nl={lam:g}" for rc, beta, lam in configs]
    needed, extra = [], []
    for rc, beta, lam in configs:
        group = [c for c in cells if c.room_cost == rc and c.beta == beta
                 and c.lam == lam]
        needed.append(sum(c.senses_needed for c in group))
        extra.append(sum(c.senses_disambiguation for c in group))
    fig, ax = plt.subplots(figsize=(1.2 + 0.42 * len(configs), 4.0))
    xs = range(len(configs))
    ax.bar(xs, needed, color=_MUTED, width=0.6,
           label="needed by the question", zorder=2)
    ax.bar(xs, extra, bottom=needed, color="#2a78d6", width=0.6,
           label="taken for disambiguation", zorder=2)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=5.5)
    ax.set_ylabel("senses (all households)", fontsize=9, color=_INK)
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
    parser.add_argument("--stage", nargs="+",
                        default=["absence", "value", "frontier"],
                        choices=["absence", "value", "frontier"])
    parser.add_argument("--out-dir", type=pathlib.Path,
                        default=pathlib.Path("results/hypothesis_mixture_trial"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    banks = sorted(args.bank_dir.glob("*_bank.jsonl"))[:args.households]
    if not banks:
        parser.error(f"no banks under {args.bank_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if "absence" in args.stage:
        absence: List[AbsenceCell] = []
        for path in banks:
            episode = truncated(next(JsonlBank(path).episodes()), args.days)
            # The 0-weight row is presence-only; the 0-uniforms row shows
            # what dropping the selection rule costs.
            settings = [(w, DEFAULT_ABSENCE_UNIFORMS)
                        for w in ABSENCE_WEIGHTS] + [(0.25, 0.0)]
            for weight, uniforms in settings:
                row = run_absence_cell(episode, weight, uniforms, args.seed)
                absence.append(row)
                logger.info(
                    "%s absence_weight=%g uniforms=%g: ESS %.2f, "
                    "presence spread %.0f, absence spread %.0f, acc %.3f",
                    row.household_id, weight, uniforms, row.ess,
                    row.presence_spread, row.absence_spread,
                    row.passive_accuracy)
        report_dir = pathlib.Path("reports/baselines/hypothesis_mixture")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "absence_weight.md").write_text(
            format_absence_report(absence) + "\n")
        (report_dir / "absence_weight.json").write_text(json.dumps(
            [dataclasses.asdict(c) for c in absence], indent=2))
    if "value" in args.stage:
        per_household = {}
        for path in banks:
            episode = truncated(next(JsonlBank(path).episodes()), args.days)
            rows = weight_value(episode, args.seed)
            per_household[episode.household_id] = rows
            logger.info("%s weight value: learned %.4f, uniform %.4f (%+.4f)",
                        episode.household_id,
                        rows["mixture (learned weights)"],
                        rows["mixture (uniform weights)"],
                        rows["mixture (learned weights)"]
                        - rows["mixture (uniform weights)"])
        report_dir = pathlib.Path("reports/baselines/hypothesis_mixture")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "weight_value.md").write_text(
            format_weight_value_report(per_household) + "\n")
    if "frontier" not in args.stage:
        return 0

    cells: List[TrialCell] = []
    for path in banks:
        base = truncated(next(JsonlBank(path).episodes()), args.days)
        for room_cost in ROOM_COST_LEVELS:
            budget = (round(base.budget_per_day * (1.0 + room_cost))
                      if BUDGET_SCALE else base.budget_per_day)
            episode = with_budget(base, budget)
            for beta in BETAS:
                for lam in LAMBDAS:
                    cell = run_cell(episode, beta, lam, args.seed,
                                    room_cost=room_cost)
                    cells.append(cell)
                    logger.info(
                        "%s c=%g budget=%d beta=%g lambda=%g: acc %.4f, "
                        "%.1f senses/day (%d disambiguation), ESS %.2f",
                        cell.household_id, room_cost, budget, beta, lam,
                        cell.accuracy, cell.senses_per_day,
                        cell.senses_disambiguation, cell.final_ess)

    mid_lam = sorted(LAMBDAS)[len(LAMBDAS) // 2]
    render_frontier(cells, args.out_dir / "frontier.png")
    render_ess([c for c in cells if c.room_cost == ROOM_COST_LEVELS[0]],
               mid_lam, args.out_dir / "ess_over_time.png")
    render_sense_split(cells, args.out_dir / "sense_split.png")
    (args.out_dir / "paired_comparison.md").write_text(
        format_paired_report(cells, args.seed) + "\n")
    (args.out_dir / "trial_results.json").write_text(json.dumps(
        [dataclasses.asdict(c) for c in cells], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
