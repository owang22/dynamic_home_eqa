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
from typing import Mapping, Optional, Tuple, Union

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
    object was not in this receptacle at ``t``. The belief base class
    consumes both signals: contents become positive sightings, and every
    known object missing from them gets an empty look at this receptacle,
    an observation that suppresses the receptacle with a weight decaying
    in age (see :mod:`baselines.beliefs.base` for the pipeline and the
    supersession rule).
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
    ``budget_spent`` is the total sense COST consumed on this question
    (the number of senses when every sense costs 1; fractional under a
    room-change cost), filled in by the harness — policies never account
    budget.
    """

    question_id: str
    predicted_receptacle_id: str
    confidence: float
    budget_spent: float

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


@dataclass
class RobotPosition:
    """Mutable holder for the robot's current room, owned by the harness.

    The harness updates ``room`` as passive room visits are delivered and
    active senses execute (and resets it to the home base at each day
    start); policies read it only through
    :meth:`EpisodeContext.sense_cost`. ``None`` means position is unknown
    (banks without room information), in which case every sense costs 1.
    """

    room: Optional[str] = None


@dataclass(frozen=True)
class EpisodeContext:
    """The agent-visible slice of an episode. Contains no ground truth.

    This is what ``BeliefModel.reset`` receives. It is constructed by
    :meth:`Episode.agent_view` and deliberately lacks any ground-truth
    accessor — isolation by construction, not convention.

    ``receptacle_rooms`` maps each in-house receptacle to its room (empty
    for banks that carry no room map) and ``home_base_room`` is the room
    the robot starts each day in. ``robot_position`` is a live view of
    the harness-tracked current room and ``room_change_cost`` the
    surcharge ``c`` for sensing outside it; together they give policies
    :meth:`sense_cost` without widening the ``decide`` signature.
    """

    episode_id: str
    household_id: str
    receptacle_ids: Tuple[str, ...]
    object_classes: Mapping[str, str]
    budget_per_day: int
    n_days: int
    unsensable_receptacle_ids: Tuple[str, ...] = ()
    receptacle_rooms: Mapping[str, str] = field(default_factory=dict)
    home_base_room: Optional[str] = None
    room_change_cost: float = 0.0
    robot_position: RobotPosition = field(default_factory=RobotPosition)

    @property
    def sensable_receptacle_ids(self) -> Tuple[str, ...]:
        """Receptacles a Sense action may target. Unsensable ones (e.g. an
        OUT_OF_HOUSE pseudo-receptacle — the robot cannot look outside the
        house) are still legitimate ANSWERS; they can only be inferred,
        never observed directly."""
        blocked = set(self.unsensable_receptacle_ids)
        return tuple(r for r in self.receptacle_ids if r not in blocked)

    def sense_cost(self, receptacle_id: str) -> float:
        """Budget cost of sensing ``receptacle_id`` from the current room:
        1.0 in the room the robot is already in, ``1.0 + c`` anywhere
        else. Banks without a room map cost every sense 1.0 (the model
        degenerates to today's flat accounting)."""
        if not self.receptacle_rooms:
            return 1.0
        room = self.receptacle_rooms.get(receptacle_id)
        if room is not None and room == self.robot_position.room:
            return 1.0
        return 1.0 + self.room_change_cost


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
    each tuple sorted by ``t_query``. ``household_type`` is optional bank
    metadata (e.g. "family_with_kids") used by the healthcheck's
    stratified gates; agents never see it.
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
    household_type: Optional[str] = None
    unsensable_receptacle_ids: Tuple[str, ...] = ()
    receptacle_rooms: Mapping[str, str] = field(default_factory=dict)
    home_base_room: Optional[str] = None
    scripted_evidence: Optional[Tuple[Union["Observation", "SenseResult"],
                                      ...]] = None
    """The ambient stream as the beliefs should CONSUME it, time-ordered.

    For a room-visit bank this holds one :class:`SenseResult` per
    inspected receptacle per visit — positive sightings and exclusions in
    one event — while ``scripted_observations`` keeps only the positive
    half for recency readouts. ``None`` (glimpse banks, hand-built
    fixtures) means the two streams coincide: consume
    ``scripted_observations``. Use :meth:`evidence_stream`, which hides
    the distinction.
    """

    def __post_init__(self) -> None:
        if self.budget_per_day < 0:
            raise ValueError(f"Episode {self.episode_id}: negative budget_per_day")
        recs = set(self.receptacle_ids)
        unknown = set(self.unsensable_receptacle_ids) - recs
        if unknown:
            raise ValueError(
                f"Episode {self.episode_id}: unsensable_receptacle_ids "
                f"{sorted(unknown)} not in receptacle_ids")
        unknown_roomed = set(self.receptacle_rooms) - recs
        if unknown_roomed:
            raise ValueError(
                f"Episode {self.episode_id}: receptacle_rooms keys "
                f"{sorted(unknown_roomed)} not in receptacle_ids")
        if (self.home_base_room is not None
                and self.home_base_room not in set(
                    self.receptacle_rooms.values())):
            raise ValueError(
                f"Episode {self.episode_id}: home_base_room "
                f"{self.home_base_room!r} is not a room of any receptacle")
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

    def evidence_stream(self) -> Tuple[Union["Observation", "SenseResult"],
                                       ...]:
        """The ambient evidence to feed beliefs, in time order.

        Every consumer that replays the passive stream (harness, passive
        evaluation, belief traces, off-policy replay) goes through this
        one accessor so positive-only and visit-based banks cannot
        diverge in delivery order or content.
        """
        if self.scripted_evidence is not None:
            return self.scripted_evidence
        return self.scripted_observations

    def agent_view(self, room_change_cost: float = 0.0,
                   robot_position: Optional[RobotPosition] = None
                   ) -> EpisodeContext:
        """The narrowed, ground-truth-free view handed to agents.

        ``robot_position`` is the harness's live position tracker; the
        default (a fresh holder at the home base) serves consumers that
        replay without position tracking, for whom every sense then
        costs 1 + c from any room other than the home base — pass the
        tracker for real cost accounting."""
        return EpisodeContext(
            episode_id=self.episode_id,
            household_id=self.household_id,
            receptacle_ids=self.receptacle_ids,
            object_classes=self.object_classes,
            budget_per_day=self.budget_per_day,
            n_days=self.n_days,
            unsensable_receptacle_ids=self.unsensable_receptacle_ids,
            receptacle_rooms=self.receptacle_rooms,
            home_base_room=self.home_base_room,
            room_change_cost=room_change_cost,
            robot_position=(robot_position if robot_position is not None
                            else RobotPosition(room=self.home_base_room)))
