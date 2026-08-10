"""Core value types for the sense-or-answer baseline study.

These frozen dataclasses are the shared vocabulary between banks, belief
models, decision policies, the harness, and the metrics layer. All
timestamps everywhere in this package are **seconds since episode start**
(``int``); a simulated day is :data:`DAY_SECONDS` long, and
``day_index = t // DAY_SECONDS``.

The ground-truth boundary is enforced structurally: :class:`Episode` owns
the ``true_location`` accessor, while agents only ever receive an
:class:`EpisodeContext` — a narrowed view that simply has no ground-truth
attribute to misuse.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from typing import Mapping, Tuple, Union

DAY_SECONDS = 86_400
"""Length of one simulated day, in seconds."""

OBSERVATION_SOURCES = ("initial_tour", "sense", "scripted")
"""Provenance labels an :class:`Observation` may carry."""

PROBABILITY_TOLERANCE = 1e-6
"""Slack allowed when checking that a distribution sums to one."""


@dataclass(frozen=True)
class Observation:
    """A single sighting: ``object_id`` was at ``receptacle_id`` at time ``t``.

    ``t`` is in seconds since episode start. ``source`` records provenance:
    ``initial_tour`` (the episode-opening walkthrough), ``sense`` (derived
    from a paid sense action), or ``scripted`` (a sighting the bank delivers
    as part of the fixed observation stream).
    """

    object_id: str
    object_class: str
    receptacle_id: str
    t: int
    source: str

    def __post_init__(self) -> None:
        if self.source not in OBSERVATION_SOURCES:
            raise ValueError(
                f"Observation({self.object_id}@{self.t}): source {self.source!r} "
                f"not in {OBSERVATION_SOURCES}")
        if self.t < 0:
            raise ValueError(f"Observation({self.object_id}): negative t {self.t}")


@dataclass(frozen=True)
class SenseResult:
    """Full true contents of one receptacle at time ``t`` (seconds).

    ``contents`` is the complete tuple of object_ids present. Absence of an
    object from ``contents`` is meaningful *negative* information — the
    object is definitely not in this receptacle at ``t``. The basic belief
    models ignore that signal (they only fold in the positive sightings),
    but the field contract guarantees completeness so later models can
    exploit it without a schema change.
    """

    receptacle_id: str
    t: int
    contents: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.t < 0:
            raise ValueError(f"SenseResult({self.receptacle_id}): negative t {self.t}")


@dataclass(frozen=True)
class Question:
    """An object-localization query posed at ``t_query`` (seconds).

    ``day_index`` is redundant with ``t_query // DAY_SECONDS`` but is stored
    explicitly because banks group questions by day; the loader verifies the
    two agree.
    """

    question_id: str
    object_id: str
    t_query: int
    day_index: int

    def __post_init__(self) -> None:
        if self.t_query < 0:
            raise ValueError(f"Question({self.question_id}): negative t_query")
        if self.day_index != self.t_query // DAY_SECONDS:
            raise ValueError(
                f"Question({self.question_id}): day_index {self.day_index} "
                f"inconsistent with t_query {self.t_query} "
                f"(expected {self.t_query // DAY_SECONDS})")


@dataclass(frozen=True)
class Answer:
    """A final committed answer to one question.

    ``confidence`` is the probability the answering belief assigned to the
    predicted receptacle (in [0, 1]; degenerate beliefs may emit constants).
    ``budget_spent`` is the number of sense actions consumed on this
    question, filled in by the harness — policies never account budget.
    """

    question_id: str
    predicted_receptacle_id: str
    confidence: float
    budget_spent: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Answer({self.question_id}): confidence {self.confidence} "
                f"outside [0, 1]")
        if self.budget_spent < 0:
            raise ValueError(
                f"Answer({self.question_id}): negative budget_spent")


@dataclass(frozen=True)
class Prediction:
    """A belief's output: a distribution over receptacles plus its argmax.

    ``distribution`` maps receptacle_id -> probability and must sum to 1
    (within :data:`PROBABILITY_TOLERANCE`). ``argmax`` must be a key of the
    distribution carrying maximal probability; when several receptacles tie,
    the belief model chooses among them (with its seeded generator) so that
    downstream consumers never re-break ties.
    """

    distribution: Mapping[str, float]
    argmax: str

    def __post_init__(self) -> None:
        total = sum(self.distribution.values())
        if abs(total - 1.0) > PROBABILITY_TOLERANCE:
            raise ValueError(f"Prediction: distribution sums to {total}, not 1")
        if self.argmax not in self.distribution:
            raise ValueError(f"Prediction: argmax {self.argmax!r} not in distribution")
        top = max(self.distribution.values())
        if self.distribution[self.argmax] < top - PROBABILITY_TOLERANCE:
            raise ValueError(
                f"Prediction: argmax {self.argmax!r} has p="
                f"{self.distribution[self.argmax]}, but max is {top}")

    @property
    def confidence(self) -> float:
        """Probability assigned to the argmax."""
        return float(self.distribution[self.argmax])


@dataclass(frozen=True)
class AnswerNow:
    """Policy decision: commit to the current prediction, spend nothing."""


@dataclass(frozen=True)
class Sense:
    """Policy decision: spend one budget unit looking inside ``receptacle_id``."""

    receptacle_id: str


Action = Union[AnswerNow, Sense]
"""What a :class:`~baselines.policies.base.DecisionPolicy` may return.

The policy signals *answer now* rather than constructing an
:class:`Answer` itself: the final answer record needs budget accounting,
which is the harness's job by contract.
"""


@dataclass(frozen=True)
class EpisodeContext:
    """The agent-visible slice of an episode. Contains no ground truth.

    This is what ``BeliefModel.reset`` receives. It is constructed by
    :meth:`Episode.agent_view` and deliberately lacks any ground-truth
    accessor — isolation by construction, not convention.
    """

    episode_id: str
    household_id: str
    receptacle_ids: Tuple[str, ...]
    object_classes: Mapping[str, str]
    budget_per_day: int
    n_days: int


@dataclass(frozen=True)
class Episode:
    """One full evaluation episode, including ground truth.

    ``trajectories`` maps object_id -> tuple of ``(t, receptacle_id)``
    change-points sorted by ``t`` (piecewise-constant location; the first
    entry must be at t=0). Only the harness may call
    :meth:`true_location`; agents receive :meth:`agent_view` instead.

    ``initial_observations`` (source ``initial_tour``) and
    ``scripted_observations`` (source ``scripted``, sorted by t) together
    form the fixed observation stream every agent receives identically.
    ``questions_by_day`` holds one tuple of questions per simulated day,
    each tuple sorted by ``t_query``.
    """

    episode_id: str
    household_id: str
    receptacle_ids: Tuple[str, ...]
    object_classes: Mapping[str, str]
    initial_observations: Tuple[Observation, ...]
    scripted_observations: Tuple[Observation, ...]
    questions_by_day: Tuple[Tuple[Question, ...], ...]
    budget_per_day: int
    trajectories: Mapping[str, Tuple[Tuple[int, str], ...]] = field(repr=False)

    def __post_init__(self) -> None:
        if self.budget_per_day < 0:
            raise ValueError(f"Episode {self.episode_id}: negative budget_per_day")
        recs = set(self.receptacle_ids)
        for obj, traj in self.trajectories.items():
            if not traj or traj[0][0] != 0:
                raise ValueError(
                    f"Episode {self.episode_id}: trajectory for {obj} must "
                    f"start at t=0 (got {traj[:1]})")
            ts = [t for t, _ in traj]
            if ts != sorted(ts):
                raise ValueError(
                    f"Episode {self.episode_id}: trajectory for {obj} not sorted")
            for _, rec in traj:
                if rec not in recs:
                    raise ValueError(
                        f"Episode {self.episode_id}: trajectory for {obj} uses "
                        f"unknown receptacle {rec!r}")

    @property
    def n_days(self) -> int:
        """Number of simulated days (question-list length)."""
        return len(self.questions_by_day)

    def true_location(self, object_id: str, t: int) -> str:
        """Ground-truth receptacle of ``object_id`` at time ``t`` (seconds).

        Harness-only by contract; agents never see this object. Raises
        ``KeyError`` for unknown objects and ``ValueError`` for negative t.
        """
        if t < 0:
            raise ValueError(f"true_location: negative t {t}")
        traj = self.trajectories[object_id]
        idx = bisect.bisect_right([p[0] for p in traj], t) - 1
        return traj[idx][1]

    def receptacle_contents(self, receptacle_id: str, t: int) -> Tuple[str, ...]:
        """All object_ids truly inside ``receptacle_id`` at ``t``, sorted.

        Used by the harness to materialize :class:`SenseResult`s.
        """
        if receptacle_id not in self.receptacle_ids:
            raise KeyError(
                f"Episode {self.episode_id}: unknown receptacle {receptacle_id!r}")
        return tuple(sorted(
            obj for obj in self.trajectories
            if self.true_location(obj, t) == receptacle_id))

    def agent_view(self) -> EpisodeContext:
        """The narrowed, ground-truth-free view handed to agents."""
        return EpisodeContext(
            episode_id=self.episode_id,
            household_id=self.household_id,
            receptacle_ids=self.receptacle_ids,
            object_classes=self.object_classes,
            budget_per_day=self.budget_per_day,
            n_days=self.n_days)
