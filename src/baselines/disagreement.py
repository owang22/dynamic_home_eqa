"""Do the zoo's beliefs disagree enough for a mixture to have anything to
work with?

A mixture over belief models is only worth building if its particles say
different things, and a sense can only sharpen the mixture's weights if
those differences are large enough to be resolved by looking somewhere.
This module measures the differences themselves — no mixture, no policy,
no sensing.

Two panels are measured, because "a hypothesis about household dynamics"
can mean two different things:

* :data:`FAMILY_PANEL` — one representative per model family (recency,
  frequency, timetable, regime mixture, Markov, hazard, hierarchy,
  Perpetua). Particles that disagree about the SHAPE of the dynamics.
* :data:`PARAMETER_PANEL` — one family, :class:`~baselines.beliefs.
  smoothed_recency.SmoothedRecency`, at six smoothing half-lives from 1 h
  to 48 h. Particles that agree on the shape and disagree about the RATE:
  how fast this household churns.

Both run on the same diet: PASSIVE (initial tour plus the bank's scripted
evidence, no sensing), each belief predicting every bank question at its
own ``t_query`` via ``predict_readonly`` so no tie-break draw couples one
question to another. Every belief sees an identical stream, so any
difference between them is the model, not the data.

Per question the module records

* whether all beliefs in the panel share an argmax;
* the mean pairwise Jensen-Shannon divergence (base 2, so 0 is identical
  and 1 is disjoint support) over all belief pairs;
* the queried object's volatility tercile (true location changes per day,
  from the bank's own trajectories, tercile taken WITHIN the household so
  households of different overall churn stay comparable);
* the hour of day of ``t_query``.

and per belief pair, the fraction of questions where that pair shares an
argmax.

Volatility and hour of day are the two breakouts because they are the two
obvious places for disagreement to hide: a parked object is one every
model gets right, and the hours a household is asleep are hours where
nothing moves.

All times are seconds since episode start; a day is 86 400 s.

Usage:
  python -m baselines.disagreement --households 2 \\
      --out-dir reports/baselines/disagreement
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import math
import pathlib
import random
import statistics
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS, Episode, Prediction

logger = logging.getLogger(__name__)

DEFAULT_BANK_DIR = pathlib.Path("banks/baselines/fleet")

FAMILY_PANEL: Tuple[Dict[str, Any], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent", "half_life_h": 24.0},
    {"name": "timetable", "half_life_h": 24.0},
    {"name": "daytype_mixture"},
    {"name": "markov1"},
    {"name": "periodic_persistence"},
    {"name": "hierarchy_backoff"},
    {"name": "smoothed_recency"},
    {"name": "perpetua_star"},
)
"""One representative per belief family, at the registry's fixed defaults.
The LLM belief (needs a filled prompt cache) and the oracle program
posterior (privileged access to the household program) are out: neither is
a deployable hypothesis about dynamics."""

PARAMETER_PANEL: Tuple[Dict[str, Any], ...] = tuple(
    {"name": "smoothed_recency", "smoothing_half_life_h": h}
    for h in (1.0, 3.0, 6.0, 12.0, 24.0, 48.0))
"""One family at six rates. 6 h is the frozen default; the others bracket
it by a factor of six in each direction."""

PANELS: Mapping[str, Tuple[Dict[str, Any], ...]] = {
    "family": FAMILY_PANEL, "parameter": PARAMETER_PANEL}

N_TERCILES = 3


def panel_labels(panel: Sequence[Mapping[str, Any]]) -> Tuple[str, ...]:
    """Short display label per panel member: the belief name, plus the one
    varied key when a panel repeats a name."""
    names = [str(spec["name"]) for spec in panel]
    labels = []
    for spec, name in zip(panel, names):
        extra = [f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}"
                 for k, v in spec.items() if k != "name"]
        labels.append(f"{name}({','.join(extra)})"
                      if names.count(name) > 1 and extra else name)
    return tuple(labels)


# ------------------------------------------------------------ divergence


def jensen_shannon(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Jensen-Shannon divergence in bits: 0 when identical, 1 when the two
    distributions have disjoint support."""
    total = 0.0
    for key in set(p) | set(q):
        pk, qk = p.get(key, 0.0), q.get(key, 0.0)
        mk = 0.5 * (pk + qk)
        if pk > 0.0:
            total += 0.5 * pk * math.log2(pk / mk)
        if qk > 0.0:
            total += 0.5 * qk * math.log2(qk / mk)
    return max(0.0, min(1.0, total))


def mean_pairwise_divergence(
        distributions: Sequence[Mapping[str, float]]) -> float:
    """Mean Jensen-Shannon divergence over all unordered pairs."""
    pairs = [jensen_shannon(distributions[i], distributions[j])
             for i in range(len(distributions))
             for j in range(i + 1, len(distributions))]
    return statistics.mean(pairs) if pairs else 0.0


# ------------------------------------------------------------- volatility


def moves_per_day(episode: Episode) -> Dict[str, float]:
    """True location changes per day, per object, from the bank's
    trajectories. The t=0 row is the starting position, not a move."""
    days = max(1, episode.n_days)
    return {obj: (len(traj) - 1) / days
            for obj, traj in episode.trajectories.items()}


def volatility_terciles(moves: Mapping[str, float]) -> Dict[str, int]:
    """Object -> tercile index (0 calmest, 2 most volatile) by moves per
    day, split WITHIN this household. Ties land in the lower tercile, so a
    household whose objects mostly never move reports a crowded tercile 0
    rather than a fake split."""
    ordered = sorted(moves, key=lambda o: (moves[o], o))
    n = len(ordered)
    return {obj: min(N_TERCILES - 1, (rank * N_TERCILES) // n)
            for rank, obj in enumerate(ordered)} if n else {}


# --------------------------------------------------------- the short run


@dataclasses.dataclass(frozen=True)
class QuestionRow:
    """One question, seen by every belief in one panel."""

    household_id: str
    question_id: str
    object_id: str
    t_query: int
    hour: int
    volatility_tercile: int
    argmaxes: Tuple[str, ...]
    mean_jsd: float

    @property
    def unanimous(self) -> bool:
        return len(set(self.argmaxes)) == 1


def passive_rows(episode: Episode, panel: Sequence[Mapping[str, Any]],
                 seed: int = 0) -> List[QuestionRow]:
    """Every bank question scored by every panel member on the passive
    diet. Beliefs are built once and fed the stream in time order, so this
    costs one pass per belief over the episode."""
    view = episode.agent_view()
    models = []
    for index, spec in enumerate(panel):
        model = build_registered_belief(
            dict(spec), random.Random(seed * 1000 + index))
        model.reset(view)
        for obs in episode.initial_observations:
            model.update(obs)
        models.append(model)

    terciles = volatility_terciles(moves_per_day(episode))
    evidence = list(episode.evidence_stream())
    cursor = 0
    rows: List[QuestionRow] = []
    for day in episode.questions_by_day:
        for question in day:
            while (cursor < len(evidence)
                   and evidence[cursor].t <= question.t_query):
                for model in models:
                    model.update(evidence[cursor])
                cursor += 1
            predictions: List[Prediction] = []
            for model in models:
                model.ensure_object(question.object_id, question.object_class)
                predictions.append(
                    model.predict_readonly(question.object_id,
                                           question.t_query))
            rows.append(QuestionRow(
                household_id=episode.household_id,
                question_id=question.question_id,
                object_id=question.object_id,
                t_query=question.t_query,
                hour=(question.t_query % DAY_SECONDS) // 3600,
                volatility_tercile=terciles.get(question.object_id, 0),
                argmaxes=tuple(p.argmax for p in predictions),
                mean_jsd=mean_pairwise_divergence(
                    [p.distribution for p in predictions])))
    return rows


# ------------------------------------------------------------ aggregation


def _summary(rows: Sequence[QuestionRow]) -> Dict[str, Any]:
    return {"n_questions": len(rows),
            "unanimous_argmax_fraction":
                sum(r.unanimous for r in rows) / len(rows) if rows else 0.0,
            "mean_pairwise_jsd":
                statistics.mean(r.mean_jsd for r in rows) if rows else 0.0,
            "median_pairwise_jsd":
                statistics.median(r.mean_jsd for r in rows) if rows else 0.0}


def _by(rows: Sequence[QuestionRow], key: str) -> Dict[str, Dict[str, Any]]:
    buckets: Dict[Any, List[QuestionRow]] = {}
    for row in rows:
        buckets.setdefault(getattr(row, key), []).append(row)
    return {str(k): _summary(v) for k, v in sorted(buckets.items())}


def pair_agreement(rows: Sequence[QuestionRow], n_beliefs: int
                   ) -> List[List[float]]:
    """Matrix of the fraction of questions where each belief pair shares
    an argmax (1.0 on the diagonal)."""
    matrix = [[1.0] * n_beliefs for _ in range(n_beliefs)]
    if not rows:
        return matrix
    for i in range(n_beliefs):
        for j in range(i + 1, n_beliefs):
            share = sum(r.argmaxes[i] == r.argmaxes[j]
                        for r in rows) / len(rows)
            matrix[i][j] = matrix[j][i] = share
    return matrix


def measure(panel_name: str, bank_paths: Sequence[pathlib.Path],
            seed: int = 0) -> Dict[str, Any]:
    """Run one panel over the banks and aggregate."""
    panel = PANELS[panel_name]
    labels = panel_labels(panel)
    rows: List[QuestionRow] = []
    for path in bank_paths:
        episode = next(JsonlBank(path).episodes())
        household_rows = passive_rows(episode, panel, seed=seed)
        rows.extend(household_rows)
        logger.info("%s: %s, %d questions, unanimous %.3f, mean JSD %.3f",
                    panel_name, episode.household_id, len(household_rows),
                    _summary(household_rows)["unanimous_argmax_fraction"],
                    _summary(household_rows)["mean_pairwise_jsd"])
    return {"panel": panel_name,
            "beliefs": list(labels),
            "specs": [dict(s) for s in panel],
            "households": [p.name for p in bank_paths],
            "overall": _summary(rows),
            "by_volatility_tercile": _by(rows, "volatility_tercile"),
            "by_hour": _by(rows, "hour"),
            "pair_argmax_agreement": pair_agreement(rows, len(panel)),
            "jsd_values": [r.mean_jsd for r in rows]}


# --------------------------------------------------------------- figures


_HUE = "#2a78d6"
_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"


def _style(ax: Any) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    ax.tick_params(colors=_MUTED, labelsize=8)
    ax.set_axisbelow(True)


def render_divergence_histogram(result: Mapping[str, Any],
                                out_path: pathlib.Path) -> None:
    """Figure 1: how far apart the panel's predictions are, per question."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    values = result["jsd_values"]
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.hist(values, bins=40, range=(0.0, 1.0), color=_HUE, zorder=2)
    mean = result["overall"]["mean_pairwise_jsd"]
    ax.axvline(mean, color=_MUTED, linestyle=":", linewidth=1.3, zorder=3)
    ax.text(mean + 0.012, ax.get_ylim()[1] * 0.94, f"mean {mean:.3f}",
            fontsize=8, color=_MUTED, va="top")
    ax.set_xlabel("mean pairwise Jensen-Shannon divergence (bits)",
                  fontsize=9, color=_INK)
    ax.set_ylabel("questions", fontsize=9, color=_INK)
    ax.set_title(
        f"How far apart do the {result['panel']} panel's beliefs sit? "
        f"({result['overall']['n_questions']} questions, "
        f"{len(result['households'])} households)",
        fontsize=9.5, color=_INK, loc="left")
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_agreement_matrix(result: Mapping[str, Any],
                            out_path: pathlib.Path) -> None:
    """Figure 2: argmax agreement fraction for every belief pair."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = result["beliefs"]
    matrix = result["pair_argmax_agreement"]
    size = 1.0 + 0.62 * len(labels)
    fig, ax = plt.subplots(figsize=(size + 2.2, size + 0.8))
    image = ax.imshow(matrix, cmap="Blues", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=7.5)
    ax.set_yticklabels(labels, fontsize=7.5)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{matrix[i][j]:.2f}", ha="center", va="center",
                    fontsize=7,
                    color="white" if matrix[i][j] > 0.55 else _INK)
    ax.set_title(
        f"Share of questions where each pair picks the same receptacle "
        f"({result['panel']} panel)", fontsize=9.5, color=_INK, loc="left")
    bar = fig.colorbar(image, ax=ax, fraction=0.045)
    bar.ax.tick_params(colors=_MUTED, labelsize=8)
    ax.tick_params(colors=_MUTED)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------- main


def _format_report(results: Mapping[str, Mapping[str, Any]]) -> str:
    lines = ["# Belief disagreement measurement", ""]
    for name, result in results.items():
        overall = result["overall"]
        lines += [f"## {name} panel ({len(result['beliefs'])} beliefs)", "",
                  "  " + ", ".join(result["beliefs"]), "",
                  f"  questions            {overall['n_questions']}",
                  f"  unanimous argmax     "
                  f"{overall['unanimous_argmax_fraction']:.3f}",
                  f"  mean pairwise JSD    {overall['mean_pairwise_jsd']:.3f}",
                  f"  median pairwise JSD  "
                  f"{overall['median_pairwise_jsd']:.3f}", ""]
        for breakout in ("by_volatility_tercile", "by_hour"):
            lines.append(f"  {breakout}")
            lines.append(f"    {'bucket':>8} {'n':>6} {'unanimous':>10} "
                         f"{'mean JSD':>9}")
            for bucket, cell in result[breakout].items():
                lines.append(
                    f"    {bucket:>8} {cell['n_questions']:>6} "
                    f"{cell['unanimous_argmax_fraction']:>10.3f} "
                    f"{cell['mean_pairwise_jsd']:>9.3f}")
            lines.append("")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank-dir", type=pathlib.Path,
                        default=DEFAULT_BANK_DIR)
    parser.add_argument("--households", type=int, default=2,
                        help="how many banks to read, in name order")
    parser.add_argument("--panels", nargs="+", default=sorted(PANELS),
                        choices=sorted(PANELS))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", type=pathlib.Path,
                        default=pathlib.Path("reports/baselines/disagreement"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    banks = sorted(args.bank_dir.glob("*_bank.jsonl"))[:args.households]
    if not banks:
        parser.error(f"no banks under {args.bank_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    results = {name: measure(name, banks, seed=args.seed)
               for name in args.panels}
    for name, result in results.items():
        render_divergence_histogram(
            result, args.out_dir / f"{name}_jsd_histogram.png")
        render_agreement_matrix(
            result, args.out_dir / f"{name}_argmax_agreement.png")
    (args.out_dir / "disagreement.json").write_text(
        json.dumps(results, indent=2, sort_keys=True))
    report = _format_report(results)
    (args.out_dir / "disagreement.md").write_text(report + "\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
