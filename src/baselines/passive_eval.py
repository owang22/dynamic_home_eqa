"""Horizon-controlled passive evaluation: history, recency, and forecast
horizon deconfounded.

The descriptive per-day passive read-out (the ``run`` grid's
accuracy-by-day curve) scores a belief trained on days 1..D against
questions inside those same days, so later checkpoints simultaneously
have more history, more recent sightings, and shorter forecast horizons —
a rising curve cannot be attributed to adaptation. This module implements
the controlled protocol that replaces it for any learning-curve claim:

* **Fixed-horizon checkpoints.** For each checkpoint day ``D`` the belief
  consumes the initial tour plus every scripted sighting with
  ``t < D * 86 400`` (the first D days) and nothing else — no sensing
  anywhere. It then answers the bank's own questions with
  ``D * 86 400 < t_query <= (D + max horizon) * 86 400``, each assigned
  to the smallest configured horizon ``h`` with
  ``t_query - D * 86 400 <= h * 86 400``. Scores are reported per
  ``(D, h)`` cell and never pooled across ``h``, so a curve over D shows
  "more history at the same horizon" and nothing else. A question inside
  several checkpoints' windows is scored once per checkpoint — same
  question, different amounts of history, which is the comparison the
  protocol exists to make.
* **Recency stratification.** Every scored question records the time
  since the belief's last sighting of the queried object (``None`` when
  it was never sighted, e.g. objects out of the house during the tour);
  accuracy binned by that value shows how fast each belief's information
  decays — the single most informative passive plot.
* **Proper scores.** Each cell reports top-1 accuracy AND mean negative
  log-likelihood (natural log) of the true receptacle, with the
  probability floored at ``log_loss_epsilon`` before the log. The frozen
  panel runs hard exclusions and one-hot recency beliefs whose configured
  probability floor is 0, where a single confident miss would make the
  mean infinite, so the protocol floors every model at the same
  configured epsilon.
* **Unit of analysis.** The household is the independent unit:
  :func:`aggregate_households` averages per-household cell values with
  equal weight per household (never per question) and bootstraps over
  households for intervals. Exact sample sizes (households, questions)
  ride along in every cell.

All times are seconds since episode start; a day is 86 400 s. Runs are
deterministic in (bank, belief spec, protocol config, seed):
per-question predictions use ``predict_readonly`` so tie-break draws
never couple one question's answer to another's.
"""

from __future__ import annotations

import dataclasses
import math
import random
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import DAY_SECONDS, Episode, Observation

BOOTSTRAP_RESAMPLES = 1000
"""Bootstrap resamples over households for aggregate intervals."""

NEVER_SIGHTED_BIN = "never"
"""Recency-bin label for questions about never-sighted objects."""


@dataclasses.dataclass(frozen=True)
class PassiveProtocolConfig:
    """The protocol's fixed knobs. Defaults are the standard protocol;
    they are set a priori and never tuned per bank."""

    checkpoint_days: Tuple[int, ...] = (1, 3, 5, 7, 10, 14)
    horizons_days: Tuple[float, ...] = (0.25, 1.0, 3.0, 7.0)
    recency_bin_edges_h: Tuple[float, ...] = (1.0, 6.0, 24.0, 72.0)
    log_loss_epsilon: float = 1e-3
    seed: int = 0

    def __post_init__(self) -> None:
        if not self.checkpoint_days or not self.horizons_days:
            raise ValueError("PassiveProtocolConfig: checkpoint_days and "
                             "horizons_days must be non-empty")
        if list(self.checkpoint_days) != sorted(set(self.checkpoint_days)):
            raise ValueError("PassiveProtocolConfig: checkpoint_days must "
                             "be strictly increasing")
        if list(self.horizons_days) != sorted(set(self.horizons_days)):
            raise ValueError("PassiveProtocolConfig: horizons_days must "
                             "be strictly increasing")
        if list(self.recency_bin_edges_h) != sorted(
                set(self.recency_bin_edges_h)):
            raise ValueError("PassiveProtocolConfig: recency_bin_edges_h "
                             "must be strictly increasing")
        if not 0.0 < self.log_loss_epsilon < 1.0:
            raise ValueError(
                f"PassiveProtocolConfig: log_loss_epsilon "
                f"{self.log_loss_epsilon} must be in (0, 1)")

    def recency_bin(self, time_since_sighting_s: Optional[int]) -> str:
        """Label for a time-since-last-sighting value (seconds)."""
        if time_since_sighting_s is None:
            return NEVER_SIGHTED_BIN
        hours = time_since_sighting_s / 3600
        low = 0.0
        for edge in self.recency_bin_edges_h:
            if hours < edge:
                return f"[{low:g}h,{edge:g}h)"
            low = edge
        return f"[{low:g}h,inf)"

    def recency_bin_labels(self) -> Tuple[str, ...]:
        """All bin labels in order, the never-sighted bin last."""
        edges = (0.0, *self.recency_bin_edges_h)
        finite = tuple(f"[{lo:g}h,{hi:g}h)"
                       for lo, hi in zip(edges, edges[1:]))
        return (*finite, f"[{edges[-1]:g}h,inf)", NEVER_SIGHTED_BIN)


@dataclasses.dataclass(frozen=True)
class ScoredQuestion:
    """One question scored at one checkpoint (times in seconds)."""

    household_id: str
    episode_id: str
    belief: str                     # the belief's display name
    checkpoint_day: int             # D: evidence frozen at D * 86 400 s
    horizon_days: float             # assigned (D, h) cell
    question_id: str
    object_id: str
    t_query: int
    correct: bool
    log_loss: float                 # -ln(max(p(truth), epsilon))
    time_since_sighting_s: Optional[int]   # None = never sighted
    recency_bin: str


@dataclasses.dataclass(frozen=True)
class CellScore:
    """Mean scores over one set of scored questions."""

    n_questions: int
    top1_accuracy: float
    mean_log_loss: float


def _horizon_of(elapsed_s: int,
                horizons_days: Sequence[float]) -> Optional[float]:
    """Smallest configured horizon covering ``elapsed_s``; None if beyond."""
    for h in horizons_days:
        if elapsed_s <= h * DAY_SECONDS:
            return h
    return None


def evaluate_checkpoint(episode: Episode, belief: BeliefModel,
                        checkpoint_day: int,
                        config: PassiveProtocolConfig
                        ) -> List[ScoredQuestion]:
    """Score one belief at one checkpoint on one episode.

    The belief must be freshly constructed (its evidence store empty);
    this function resets it, feeds the tour plus scripted sightings
    strictly before the checkpoint cutoff, and scores every question
    inside the horizon window. Raises if the belief has already seen
    another episode (reset makes that impossible to observe, so the
    caller contract is fresh-per-checkpoint for determinism).
    """
    cutoff = checkpoint_day * DAY_SECONDS
    belief.reset(episode.agent_view())
    last_sighting: Dict[str, int] = {}

    def saw(object_id: str, t: int) -> None:
        last_sighting[object_id] = max(last_sighting.get(object_id, t), t)

    for obs in episode.initial_observations:
        belief.update(obs)
        saw(obs.object_id, obs.t)
    for event in episode.evidence_stream():
        if event.t >= cutoff:
            break
        belief.update(event)
        if isinstance(event, Observation):
            saw(event.object_id, event.t)
        else:                        # a room visit's per-receptacle result
            for object_id in event.contents:
                saw(object_id, event.t)

    scored: List[ScoredQuestion] = []
    for day in episode.questions_by_day:
        for question in day:
            elapsed = question.t_query - cutoff
            if elapsed <= 0:
                continue
            horizon = _horizon_of(elapsed, config.horizons_days)
            if horizon is None:
                continue
            prediction = belief.predict_readonly(question.object_id,
                                                 question.t_query)
            truth = episode.true_location(question.object_id,
                                          question.t_query)
            p_truth = prediction.distribution.get(truth, 0.0)
            since = (question.t_query - last_sighting[question.object_id]
                     if question.object_id in last_sighting else None)
            scored.append(ScoredQuestion(
                household_id=episode.household_id,
                episode_id=episode.episode_id, belief=belief.name,
                checkpoint_day=checkpoint_day, horizon_days=horizon,
                question_id=question.question_id,
                object_id=question.object_id, t_query=question.t_query,
                correct=prediction.argmax == truth,
                log_loss=-math.log(max(p_truth, config.log_loss_epsilon)),
                time_since_sighting_s=since,
                recency_bin=config.recency_bin(since)))
    return scored


CONTINUOUS_HORIZON = 0.0
"""``horizon_days`` value marking a continuous-mode score: the belief
was updated with every sighting strictly before the query, so the only
"forecast" is the age of its evidence, recorded per question."""


def question_ages(episode: Episode, cutoff: Optional[int] = None
                  ) -> Dict[str, Optional[int]]:
    """question_id -> seconds since the ambient stream last showed that
    object before the query (None: never). A property of the episode,
    not of any belief — every model in continuous mode has exactly this
    evidence when it answers. With ``cutoff`` (seconds), evidence stops
    there: the ages a belief frozen at that checkpoint answers with."""
    last_sighting: Dict[str, int] = {}
    events = [e for e in episode.evidence_stream()
              if cutoff is None or e.t < cutoff]
    questions = sorted((q for day in episode.questions_by_day for q in day),
                       key=lambda q: q.t_query)
    for obs in episode.initial_observations:
        last_sighting[obs.object_id] = max(
            last_sighting.get(obs.object_id, obs.t), obs.t)
    ages: Dict[str, Optional[int]] = {}
    i = 0
    for q in questions:
        while i < len(events) and events[i].t < q.t_query:
            ev = events[i]
            ids = ([ev.object_id] if isinstance(ev, Observation)
                   else list(ev.contents))
            for object_id in ids:
                last_sighting[object_id] = max(
                    last_sighting.get(object_id, ev.t), ev.t)
            i += 1
        ages[q.question_id] = (q.t_query - last_sighting[q.object_id]
                               if q.object_id in last_sighting else None)
    return ages


def evaluate_continuous(episode: Episode, belief: BeliefModel,
                        config: PassiveProtocolConfig
                        ) -> List[ScoredQuestion]:
    """Score one belief on one episode with evidence applied up to each
    query: "how good is the belief right now", as opposed to
    :func:`evaluate_checkpoint`'s frozen-at-D forecast. Evidence and
    questions are merged in time order; a sighting at exactly the query
    instant is NOT applied first (strict <), so no question is answered
    by the observation that would make it trivial. ``checkpoint_day`` is
    the query's own day (history length), ``horizon_days`` is
    :data:`CONTINUOUS_HORIZON`, and the age of the object's last
    sighting is recorded per question."""
    belief.reset(episode.agent_view())
    last_sighting: Dict[str, int] = {}

    def saw(object_id: str, t: int) -> None:
        last_sighting[object_id] = max(last_sighting.get(object_id, t), t)

    for obs in episode.initial_observations:
        belief.update(obs)
        saw(obs.object_id, obs.t)
    events = list(episode.evidence_stream())
    questions = sorted((q for day in episode.questions_by_day for q in day),
                       key=lambda q: q.t_query)
    scored: List[ScoredQuestion] = []
    i = 0
    for question in questions:
        while i < len(events) and events[i].t < question.t_query:
            event = events[i]
            belief.update(event)
            if isinstance(event, Observation):
                saw(event.object_id, event.t)
            else:
                for object_id in event.contents:
                    saw(object_id, event.t)
            i += 1
        prediction = belief.predict_readonly(question.object_id,
                                             question.t_query)
        truth = episode.true_location(question.object_id, question.t_query)
        p_truth = prediction.distribution.get(truth, 0.0)
        since = (question.t_query - last_sighting[question.object_id]
                 if question.object_id in last_sighting else None)
        scored.append(ScoredQuestion(
            household_id=episode.household_id,
            episode_id=episode.episode_id, belief=belief.name,
            checkpoint_day=question.t_query // DAY_SECONDS,
            horizon_days=CONTINUOUS_HORIZON,
            question_id=question.question_id,
            object_id=question.object_id, t_query=question.t_query,
            correct=prediction.argmax == truth,
            log_loss=-math.log(max(p_truth, config.log_loss_epsilon)),
            time_since_sighting_s=since,
            recency_bin=config.recency_bin(since)))
    return scored


def score_cell(questions: Sequence[ScoredQuestion]) -> CellScore:
    """Mean top-1 accuracy and log-loss over a non-empty question set."""
    if not questions:
        raise ValueError("score_cell: empty cell — filter before scoring")
    return CellScore(
        n_questions=len(questions),
        top1_accuracy=sum(q.correct for q in questions) / len(questions),
        mean_log_loss=sum(q.log_loss for q in questions) / len(questions))


def group_cells(scored: Sequence[ScoredQuestion]
                ) -> Dict[Tuple[int, float], CellScore]:
    """(checkpoint_day, horizon) -> scores, for one household's questions."""
    by_cell: Dict[Tuple[int, float], List[ScoredQuestion]] = {}
    for q in scored:
        by_cell.setdefault((q.checkpoint_day, q.horizon_days), []).append(q)
    return {cell: score_cell(qs) for cell, qs in sorted(by_cell.items())}


def group_recency(scored: Sequence[ScoredQuestion]
                  ) -> Dict[str, CellScore]:
    """recency-bin label -> scores, pooled over checkpoints (one household)."""
    by_bin: Dict[str, List[ScoredQuestion]] = {}
    for q in scored:
        by_bin.setdefault(q.recency_bin, []).append(q)
    return {label: score_cell(qs) for label, qs in by_bin.items()}


@dataclasses.dataclass(frozen=True)
class AggregateScore:
    """Unweighted cross-household mean with a bootstrap interval.

    ``per_household`` keeps every household's value so no aggregate is
    ever shown without its spread; ``n_questions`` is the total question
    count behind the cell (households x their questions).
    """

    n_households: int
    n_questions: int
    mean: float
    ci_low: float
    ci_high: float
    per_household: Dict[str, float]


def bootstrap_mean(values_by_household: Mapping[str, float],
                   n_questions: int, seed: int) -> AggregateScore:
    """Household-level mean + seeded percentile bootstrap (2.5/97.5).

    Households are the resampling unit; with a single household the
    interval degenerates to the point value (n_households says so).
    """
    households = sorted(values_by_household)
    values = [values_by_household[h] for h in households]
    mean = sum(values) / len(values)
    rng = random.Random(seed)
    resampled = sorted(
        sum(rng.choices(values, k=len(values))) / len(values)
        for _ in range(BOOTSTRAP_RESAMPLES))
    low = resampled[int(0.025 * BOOTSTRAP_RESAMPLES)]
    high = resampled[min(BOOTSTRAP_RESAMPLES - 1,
                         int(0.975 * BOOTSTRAP_RESAMPLES))]
    return AggregateScore(
        n_households=len(households), n_questions=n_questions,
        mean=mean, ci_low=low, ci_high=high,
        per_household=dict(values_by_household))


def aggregate_households(
        cells_by_household: Mapping[str, Mapping[Tuple[int, float],
                                                 CellScore]],
        seed: int) -> Dict[Tuple[int, float],
                           Tuple[AggregateScore, AggregateScore]]:
    """Cross-household (accuracy, log-loss) aggregates per (D, h) cell.

    Only cells present in EVERY household aggregate — a cell some
    household lacks (short bank) would silently change the household mix
    across cells and make curves incomparable.
    """
    if not cells_by_household:
        return {}
    shared = set.intersection(
        *(set(cells) for cells in cells_by_household.values()))
    out: Dict[Tuple[int, float], Tuple[AggregateScore, AggregateScore]] = {}
    for cell in sorted(shared):
        accs = {h: cells[cell].top1_accuracy
                for h, cells in cells_by_household.items()}
        losses = {h: cells[cell].mean_log_loss
                  for h, cells in cells_by_household.items()}
        n_questions = sum(cells[cell].n_questions
                          for cells in cells_by_household.values())
        out[cell] = (bootstrap_mean(accs, n_questions, seed),
                     bootstrap_mean(losses, n_questions, seed))
    return out
