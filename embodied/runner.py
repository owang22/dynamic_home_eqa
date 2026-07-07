"""
runner.py — QuestionEpisodeRunner: episode protocol, scoring, logging.

This is scoring code: it is the one layer allowed to import ground_truth.py
(see that module's docstring and tests/test_embodied_layout.py, which
enforces the import boundary by inspection, not just convention).

Episode protocol:
  1. Patrol: visit every room centroid via shortest paths, sweeping through
     a full turn at each, so beliefs populate before any question is asked.
     Deterministic given the world's own seeding (scene + day + variant).
     A room whose centroid is unreachable from the agent's current pose
     (confirmed on a real scene: a multi-story house whose navmesh has no
     modeled stair connectivity between floors, splitting it into several
     disconnected islands) is skipped, not treated as an error — the agent
     genuinely cannot patrol a floor it has no way to walk to. This is
     logged so it's visible, not silent.
  2. Dock at the last patrol pose; fast-forward the clock by `wait_hours`
     while trace events keep applying underneath (the agent observes
     nothing during this time — it is genuinely "elsewhere").
  3. A question arrives; the policy loop runs until it returns a Choice or
     Abstain, executing any ResensePlan in between (which itself refreshes
     beliefs en route — see types.ActionResult). A resense target
     unreachable from the agent's current pose is likewise skipped, not
     fatal — a policy (e.g. AlwaysResense) that doesn't itself check
     travel_time_to before proposing a target relies on the runner to
     handle this gracefully.
  4. Score against ground truth at REPORT time (when the answer was
     produced, after any resense travel), not question-arrival time. The
     question's option set is fixed at generation time, but which option
     index is correct is re-derived here from true_anchor() at report
     time — the object may have moved again since the question arrived.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Union

from .belief import BeliefStore
from .ground_truth import true_anchor, true_state
from .policy import ResensePlan
from .scoring import Abstain, Choice, ScoringConfig, brier_score
from .types import Goto, Pose, Rotate, UnreachableError

if TYPE_CHECKING:
    from .question import MCQQuestion


@dataclass(frozen=True)
class EpisodeConfig:
    patrol_start: float = 6.0
    wait_hours:   float = 1.0
    patrol_turn_steps: int = 8   # number of Rotate() calls per full sweep (2*pi / steps each)
    # Hard cap on policy invocations per question, independent of any
    # individual policy's own termination logic. A policy that keeps
    # re-issuing a ResensePlan without ever converging to an answer (a real
    # bug found here — see world.py's _sense_here docstring — ran for 6.6
    # hours and consumed 162 GB of RAM before being killed) must not be
    # able to hang an episode indefinitely; this forces an answer from
    # whatever is currently believed once the cap is hit, and logs that it
    # happened, rather than trusting every future policy to self-terminate.
    max_policy_invocations: int = 20
    scoring: ScoringConfig = field(default_factory=ScoringConfig)


@dataclass
class EpisodeResult:
    question:            "MCQQuestion"
    answer:              Union[Choice, Abstain]
    correct_index:       Optional[int]   # ground truth's option index at REPORT time, or None if unrepresentable
    correct:             Optional[bool]  # None if abstained or the question was unanswerable (excluded from accuracy)
    abstained:           bool
    confidence:          Optional[float]  # the Choice's confidence, or None if abstained
    brier:               float
    answer_latency_s:    float
    distance_traveled_m: float
    policy_invocations:  int
    log:                 list = field(default_factory=list)


def _snapshot_path_distance(start_pose: Pose, result) -> float:
    """Euclidean distance summed across an ActionResult's snapshot poses,
    prefixed by the pose the action started from — an approximation of
    path length (straight segments between sense samples, not the true
    navmesh path), adequate for episode-level distance-traveled reporting."""
    poses = [start_pose] + [s.pose for s in result.snapshots]
    total = 0.0
    for a, b in zip(poses, poses[1:]):
        total += ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5
    return total


class QuestionEpisodeRunner:
    def __init__(self, world, belief: BeliefStore, policy, episode_config: Optional[EpisodeConfig] = None) -> None:
        self.world = world
        self.belief = belief
        self.policy = policy
        self.episode_config = episode_config or EpisodeConfig()
        self.log: list[dict] = []

    def _log(self, kind: str, **fields) -> None:
        self.log.append({"kind": kind, "t": self.world.t, **fields})

    # -- episode phases -----------------------------------------------------

    def patrol(self) -> None:
        """Visit every room centroid (general environmental coverage, per
        the phase spec) AND every distinct real per-scene anchor via its
        validated viewpoint (see sensor.viewpoint_for, M1). Room-centroid-
        only patrol proved too weak on a real, furnished HSSD scene: the
        exact geometric center of a room is routinely out of sensor range
        or wall-occluded from where objects actually sit near furniture —
        confirmed directly (a room's centroid saw nothing in-range, or saw
        candidates 100% blocked by a wall, while that same anchor's
        purpose-built viewpoint sees it fine). Visiting anchors closes that
        gap without discarding the room sweep, which still gives general
        peripheral coverage and lets the agent orient in open floor space.
        A room or anchor unreachable from the current pose (this scene's
        navmesh splits into disconnected islands) is skipped, not fatal.
        """
        self.world.advance_to(self.episode_config.patrol_start)
        self._log("patrol_start")

        step_angle = 2 * math.pi / self.episode_config.patrol_turn_steps

        for room in sorted(self.world._room_centroids):
            pose = self.world.room_centroid_pose(room)
            if pose is None:
                continue
            try:
                result = self.world.execute(Goto(target=pose.position))
            except UnreachableError:
                self._log("patrol_room_unreachable", room=room)
                continue
            self._log("goto", room=room, final_pose=result.final_pose.position, n_snapshots=len(result.snapshots))
            self.belief.update_from_result(result, self.world)

            for _ in range(self.episode_config.patrol_turn_steps):
                result = self.world.execute(Rotate(delta_yaw_rad=step_angle))
                self._log("rotate", room=room, yaw=result.final_pose.yaw_rad)
                self.belief.update_from_result(result, self.world)

        visited_positions: set[tuple] = set()
        for anchor in sorted(self.world._anchor_positions):
            vp = self.world.viewpoint_for(anchor)
            if vp is None:
                continue
            key = (round(vp.x, 2), round(vp.y, 2), round(vp.z, 2))
            if key in visited_positions:
                continue  # several anchors can share one real position/viewpoint
            visited_positions.add(key)
            try:
                result = self.world.execute(Goto(target=vp.position, face_yaw_rad=vp.yaw_rad))
            except UnreachableError:
                self._log("patrol_anchor_unreachable", anchor=anchor)
                continue
            self._log("goto_anchor", anchor=anchor, final_pose=result.final_pose.position,
                      n_snapshots=len(result.snapshots))
            self.belief.update_from_result(result, self.world)
        self._log("patrol_end")

    def dock_and_wait(self, wait_hours: Optional[float] = None) -> None:
        hours = wait_hours if wait_hours is not None else self.episode_config.wait_hours
        target_t = self.world.t + hours
        self.world.advance_to(target_t)
        self._log("wait", waited_hours=hours)

    # -- scoring --------------------------------------------------------------

    def _score(self, question: "MCQQuestion", answer: Union[Choice, Abstain]) -> tuple[Optional[int], Optional[bool], Optional[float], float]:
        report_t = self.world.t
        # M3 (state-change dynamics): a state question's truth comes from
        # true_state(underlying_label, state_variable, ...), not
        # true_anchor(question.label, ...) — question.label/category are
        # synthetic belief-store keys for a state question, not a real
        # instance id (see question.generate_state_question's docstring).
        if question.question_type == "state":
            truth = true_state(question.underlying_label, question.state_variable,
                                report_t, self.world.initial_state, self.world.changes)
        else:
            truth = true_anchor(question.label, report_t, self.world.initial_state, self.world.changes)
        correct_index = question.options.index(truth) if truth is not None and truth in question.options else None

        brier = brier_score(answer, correct_index, len(question.options), self.episode_config.scoring)

        if isinstance(answer, Abstain) or correct_index is None:
            correct = None
            confidence = None
        else:
            correct = (answer.option_index == correct_index)
            confidence = answer.confidence

        self._log("answer", answer_type=type(answer).__name__, truth=truth,
                  correct_index=correct_index, correct=correct, brier=brier)
        return correct_index, correct, confidence, brier

    def _forced_answer(self, question: "MCQQuestion") -> Union[Choice, Abstain]:
        """Answer built from whatever is currently believed, at full
        confidence — used only when a policy cannot make further progress
        (invocation cap hit, or every proposed resense target confirmed
        unreachable). Not a policy decision; a runner-level safety net."""
        anchor = self.belief.believed_anchor(question.label)
        if anchor is None or anchor not in question.options:
            return Abstain()
        return Choice(option_index=question.options.index(anchor), confidence=1.0)

    # -- question loop -------------------------------------------------------

    def run_question(self, question: "MCQQuestion") -> EpisodeResult:
        ask_t = self.world.t
        distance = 0.0
        invocations = 0
        unreachable_targets: set[str] = set()
        self._log("question_asked", label=question.label, category=question.category,
                   hazard_class=question.hazard_class, options=question.options)

        while True:
            invocations += 1
            pose_at_decision = self.world.pose

            def travel_time_to(anchor: str, _pose=pose_at_decision) -> float:
                vp = self.world.viewpoint_for(anchor)
                if vp is None:
                    return float("inf")
                real_cost = self.world.geodesic_time(_pose.position, vp.position)
                cost_model = self.world.config.cost_model
                if cost_model.mode == "flat" and math.isfinite(real_cost):
                    # Reachability structure (inf vs finite) is preserved;
                    # only the finite value reported to the policy changes.
                    # Actual simulated travel (self.world.execute(Goto(...))
                    # below) always uses real_cost's own geodesic path,
                    # regardless of this policy-facing substitution.
                    return cost_model.flat_leg_seconds
                return real_cost

            decision = self.policy.act(
                self.belief, question, self.world.pose, self.world.t, self.world.config, travel_time_to,
            )
            self._log("decision", invocation=invocations, decision_type=type(decision).__name__,
                      decision=getattr(decision, "option_index", None) or getattr(decision, "targets", None))

            if invocations >= self.episode_config.max_policy_invocations and isinstance(decision, ResensePlan):
                self._log("max_invocations_reached", forced_answer=True)
                decision = self._forced_answer(question)

            if isinstance(decision, (Choice, Abstain)):
                report_t = self.world.t
                correct_index, correct, confidence, brier = self._score(question, decision)
                return EpisodeResult(
                    question=question,
                    answer=decision,
                    correct_index=correct_index,
                    correct=correct,
                    abstained=isinstance(decision, Abstain),
                    confidence=confidence,
                    brier=brier,
                    answer_latency_s=(report_t - ask_t) * 3600.0,
                    distance_traveled_m=distance,
                    policy_invocations=invocations,
                    log=list(self.log),
                )

            assert isinstance(decision, ResensePlan)
            made_progress = False
            for anchor in decision.targets:
                if anchor in unreachable_targets:
                    continue  # already confirmed unreachable this question; don't retry it
                vp = self.world.viewpoint_for(anchor)
                if vp is None:
                    self._log("resense_skip_no_viewpoint", anchor=anchor)
                    unreachable_targets.add(anchor)
                    continue
                start_pose = self.world.pose
                try:
                    result = self.world.execute(Goto(target=vp.position, face_yaw_rad=vp.yaw_rad))
                except UnreachableError:
                    # A policy (e.g. AlwaysResense) doesn't itself check
                    # travel_time_to before proposing a target — the runner
                    # must not retry the identical unreachable target every
                    # invocation, or a policy that keeps proposing it would
                    # spin until max_policy_invocations forces an answer,
                    # wasting every one of those invocations pointlessly.
                    self._log("resense_unreachable", anchor=anchor)
                    unreachable_targets.add(anchor)
                    continue
                made_progress = True
                distance += _snapshot_path_distance(start_pose, result)
                self._log("goto_resense", anchor=anchor, final_pose=result.final_pose.position,
                          n_snapshots=len(result.snapshots))
                self.belief.update_from_result(result, self.world)

            if not made_progress:
                # Every target in this plan was already known-unreachable —
                # the policy cannot make progress; force an answer now
                # rather than burning the remaining invocation budget.
                decision = self._forced_answer(question)
                report_t = self.world.t
                correct_index, correct, confidence, brier = self._score(question, decision)
                return EpisodeResult(
                    question=question,
                    answer=decision,
                    correct_index=correct_index,
                    correct=correct,
                    abstained=isinstance(decision, Abstain),
                    confidence=confidence,
                    brier=brier,
                    answer_latency_s=(report_t - ask_t) * 3600.0,
                    distance_traveled_m=distance,
                    policy_invocations=invocations,
                    log=list(self.log),
                )
