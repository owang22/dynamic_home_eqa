"""
policy.py — DecisionPolicy: answer now, or go resense first?

The research object of this whole phase. Every policy shares the identical
shell (`act`) and never imports habitat_sim or EmbodiedWorld — they see the
belief store, the question, the agent's own pose/clock, and geodesic travel
time as a callback (`travel_time_to`), never geometry directly. This keeps
the decision logic testable with a synthetic BeliefStore and no simulator.

ResensePlan names anchor *slots* to visit, not concrete world poses —
resolving an anchor to an actual navigable viewpoint is EmbodiedWorld's job
(viewpoint_for), which the runner calls, keeping policies geometry-free.

Answers are scoring.Choice | scoring.Abstain (an MCQQuestion's options, not
a bare predicted anchor string) — see scoring.py's module docstring for why
exact-match scoring on a bare anchor made the resense-vs-answer decision
structurally undecidable whenever an object had moved (refuting a belief
and confidently repeating it scored identically). The resense DECISION
logic in every policy below is unchanged from before that fix; only how
each policy expresses its final answer changed.

M2 (posterior-over-anchors belief, see posterior.py) upgrades WHICH anchor
a resense plan visits, not whether to resense at all: every policy below
now builds its ResensePlan via _search_targets, which calls
belief.top_candidates() for a single best-ranked, reachable candidate
(posterior-mass-per-travel-second) instead of just the single last-known
anchor — and returns empty once _MAX_SEARCH_ANCHORS distinct anchors have
already been ruled out for this label (a "no mutable per-episode state"
search depth cap: see _n_ruled_out, which counts already-zeroed posterior
states as a proxy for "already checked and not found there"). Returning
one target at a time, not a fixed multi-anchor plan, is what makes search
"replanned after each observation" rather than a plan fixed at proposal
time: the runner's existing per-invocation policy loop already re-invokes
act() after every resense leg, so the next top_candidates() call sees the
updated (post-observation) posterior and current pose for free — no
runner change needed. Against belief.BeliefStore (M1, single-anchor
belief, no posterior to search), top_candidates() degrades to that one
anchor and _n_ruled_out is always 0, so the resense-vs-answer DECISION
boundary every policy implements is byte-for-byte the same regardless of
which belief store is plugged in; only the executed search gets richer
under posterior.PosteriorBeliefStore.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING, Union

from .belief import BeliefStore, DecayModel
from .config import AgentConfig
from .scoring import Abstain, Choice

if TYPE_CHECKING:
    from .question import MCQQuestion

# Must comfortably exceed one sense action's own time cost (sense_duration_s,
# default 1.0s => ~2.8e-4 hours), or a label detected in an *en-route* Goto
# snapshot (which costs zero additional time) rather than the final arrival
# snapshot would look "not just observed" once the arrival snapshot's own
# sense_duration_s cost has ticked the clock forward past it — a real
# failure mode: this under-shot at 1e-4 (below sense_duration_s's own
# footprint), which combined with a separate off-by-one-step timestamp bug
# (fixed in world.py's _sense_here) caused a policy to never recognize its
# own resense and loop forever. 5 seconds is small next to any realistic
# wait_hours gap between questions (>= minutes) but safely covers a single
# sense action's cost.
_JUST_OBSERVED_EPSILON_HOURS = 5.0 / 3600.0

# Hard cap on how many distinct anchors one search-resense may visit for a
# single label, matching the phase spec's "greedy plan up to 3 anchors" —
# without this, a category with many known anchors and a long enough
# episode could search all of them.
_MAX_SEARCH_ANCHORS = 3


def classify_hazard(category: str, decay_models: dict[str, DecayModel]) -> str:
    """"volatile" if category's fitted hazard rate is at or above the
    median across all fitted categories, else "stable". Median-split
    rather than a fixed threshold so this adapts to whatever the actual
    fitted rate distribution looks like for a given calibration run,
    instead of a number picked without seeing real data."""
    if not decay_models:
        return "stable"
    rates = sorted(m.lambda_per_hour for m in decay_models.values())
    median = rates[len(rates) // 2]
    model = decay_models.get(category)
    rate = model.lambda_per_hour if model else median
    return "volatile" if rate >= median else "stable"


@dataclass(frozen=True)
class ResensePlan:
    targets: tuple[str, ...]   # anchor slots to visit, in order


Decision = Union[Choice, Abstain, ResensePlan]
TravelTimeFn = Callable[[str], float]  # anchor slot -> estimated seconds from current pose


def _just_resensed(belief: BeliefStore, label: str, t: float) -> bool:
    """True if `label` was observed (positively OR negatively) at
    essentially this exact instant — without any mutable per-episode state
    in the policy itself (policies stay stateless dataclasses; this state
    lives in the belief store's own timestamps). Works against either
    belief store: posterior.PosteriorObjectNode tracks last_updated_t
    directly (touched by both positive and negative observations);
    belief.ObjectNode only timestamps positive observations via
    last_observation.

    Do not use this alone to decide "stop searching, answer now" — a
    negative (refuting) observation is also "just resensed" but should
    continue a multi-candidate search, not end it. See _just_confirmed."""
    node = belief.nodes.get(label)
    if node is None:
        return False
    last_t = getattr(node, "last_updated_t", None)
    if last_t is None:
        if node.last_observation is None:
            return False
        last_t = node.last_observation.t
    return abs(t - last_t) < _JUST_OBSERVED_EPSILON_HOURS


def _just_confirmed(belief: BeliefStore, label: str, t: float) -> bool:
    """True only if the belief was POSITIVELY confirmed at essentially
    this instant — as opposed to _just_resensed, which is also true right
    after a negative (ruling-out) observation. Search policies must tell
    these apart: a confirmation means stop and answer; a refutation means
    keep searching if depth allows (see _search_targets)."""
    node = belief.nodes.get(label)
    if node is None:
        return False
    confirmed = getattr(node, "last_update_was_positive", None)
    if confirmed is None:
        # belief.BeliefStore (M1): last_observation.t is only ever set by
        # a positive detection (observe_negative doesn't touch it there),
        # so _just_resensed already means "just confirmed" for that store.
        return _just_resensed(belief, label, t)
    return confirmed and _just_resensed(belief, label, t)


def _n_ruled_out(belief: BeliefStore, label: str, t: float) -> int:
    """How many candidate anchor states currently have ~zero posterior
    mass for this label — a proxy for "already checked and not found
    there", used to cap greedy search at _MAX_SEARCH_ANCHORS distinct
    anchors. Always 0 against belief.BeliefStore (no posterior to
    inspect — its single believed_anchor is either known or not)."""
    node = belief.nodes.get(label)
    if node is None or not hasattr(node, "propagated"):
        return 0
    propagated = node.propagated(t)
    return sum(1 for state, mass in propagated.items() if state != "OUTSIDE" and mass <= 1e-9)


def _search_targets(belief: BeliefStore, label: str, t: float, travel_time_to: "TravelTimeFn") -> tuple[str, ...]:
    """The next resense target to visit: a single best-ranked, reachable
    candidate from belief.top_candidates, or empty once
    _MAX_SEARCH_ANCHORS distinct anchors have already been ruled out for
    this label. One target at a time (not the full ranked list) is what
    lets the runner's existing per-invocation policy loop provide real
    replanning after each observation — see this module's docstring."""
    if _n_ruled_out(belief, label, t) >= _MAX_SEARCH_ANCHORS:
        return ()
    return belief.top_candidates(label, t, travel_time_to, k=1)[:1]


def _continue_or_answer(belief: BeliefStore, question: "MCQQuestion", label: str, t: float,
                        travel_time_to: "TravelTimeFn", confidence: float) -> "Decision":
    """After a resense decision has been made (this policy wants to
    resense, or just did): if the belief was JUST positively confirmed,
    stop and answer at full confidence. Otherwise, continue the search if
    any untried candidate remains (bounded by _MAX_SEARCH_ANCHORS), else
    answer with whatever confidence the current (possibly renormalized
    after ruling candidates out) belief supports. This is the one place
    that fixes a real bug in the naive version of this idea: checking
    "_just_resensed" alone would also be true right after a REFUTING
    (negative) leg, stopping the search one candidate too early instead of
    trying the next-best one."""
    if _just_confirmed(belief, label, t):
        return _answer_from_belief(belief, question, label, t, confidence=1.0)
    targets = _search_targets(belief, label, t, travel_time_to)
    if targets:
        return ResensePlan(targets=targets)
    return _answer_from_belief(belief, question, label, t, confidence=confidence)


def _option_index_for_anchor(question: "MCQQuestion", anchor: Optional[str]) -> Optional[int]:
    """The option index matching a believed anchor string, or None if
    there's no belief or the belief doesn't correspond to any fixed
    option (the policy has *some* belief but this MCQ can't express it —
    treated the same as no belief: nothing to confidently choose)."""
    if anchor is None:
        return None
    try:
        return question.options.index(anchor)
    except ValueError:
        return None


def _answer_from_belief(belief: BeliefStore, question: "MCQQuestion", label: str,
                        t: float, confidence: float) -> Union[Choice, Abstain]:
    """Choice at the option matching the current believed anchor (belief's
    compatibility view, propagated to t), at the given confidence, or
    Abstain if nothing is believed (or the belief isn't representable
    among this question's options)."""
    idx = _option_index_for_anchor(question, belief.believed_anchor(label, t))
    if idx is None:
        return Abstain()
    return Choice(option_index=idx, confidence=confidence)


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------

class AnswerImmediately:
    """Floor: never move. Not decay-aware, so confidence is simply "fully
    confident if I believe anything expressible, otherwise abstain" —
    matching its pre-scoring-fix behavior of always trusting the current
    belief outright."""

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        return _answer_from_belief(belief, question, question.label, t, confidence=1.0)


class AlwaysResense:
    """Ceiling: always search before answering (best achievable accuracy
    given the sensor model and search depth cap, worst latency)."""

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is None:
            return _answer_from_belief(belief, question, question.label, t, confidence=1.0)
        return _continue_or_answer(belief, question, question.label, t, travel_time_to, confidence=1.0)


class CoverageStop:
    """Renamed from ConfidenceStop (2026-07-07): "confidence" implied a
    confidence model, and this policy's confidence is the constant 1.0 —
    the name should say what it mechanically is. In the paper this maps to
    literature confidence-stopping (GraphEQA/MemoryEQA-style) under
    perfect perception and perfect memory, an a-fortiori comparison, not a
    literal reimplementation of any one paper's stopping rule.

    The literature's stopping rule with the time term removed: resense
    iff the instance isn't currently believed at all; otherwise answer
    regardless of how stale the belief is. Confidence is always 1.0 when
    it answers — this policy has no uncertainty notion at all, by design
    (it is the literature baseline, not a strawman); its resulting
    miscalibration (high confidence regardless of true staleness) is an
    expected, reportable result, not a bug to quietly soften.

    "Not believed at all" previously had a dead branch here that always
    abstained instead of searching — found (see results/reports/
    INDEX.md's history) to make this policy structurally identical to
    AnswerImmediately on every input, contributing nothing as a second
    comparison point. Fixed to the literal instruction: when nothing is
    believed, this now travels to the most plausible known candidate and
    senses before answering (reusing _continue_or_answer, the exact same
    goto/sense/search-depth-cap machinery every other search policy in
    this module already uses).

    PROVEN STILL DEGENERATE (verified, not assumed — see
    tests/test_coverage_stop.py's TestStructuralInvariant): every
    believed_anchor() implementation in this codebase (belief.BeliefStore,
    posterior.PosteriorBeliefStore, posterior.TimeOfDayBeliefStore) derives
    "is anything believed" from the SAME propagated posterior and the SAME
    >1e-9 survival threshold that top_candidates()/_search_targets() uses
    to decide "is there anything to search for" — believed_anchor's check
    is the ARGMAX of the identical per-candidate values top_candidates
    filters, so whenever believed_anchor returns None, top_candidates is
    mathematically guaranteed to return empty too (an argmax below
    threshold implies every candidate is below threshold). So this fix,
    though real (it changes what the "not believed" branch does), can
    never actually execute a search: _continue_or_answer's search-target
    lookup is empty in exactly the cases where anchor was None, every
    time, by construction, not merely on this pool's data. Reusing the
    EXISTING goto/sense machinery therefore cannot produce a
    non-degenerate literature baseline under the current belief-store
    interface — that would need a NEW candidate-selection path not gated
    by the survival threshold (e.g., an unconditional last-positively-
    confirmed-anchor fallback), which is a bigger change than "reuse
    existing machinery" and is intentionally not built here. No decay
    model, no posterior-validity gate, no cost/benefit anywhere in this
    decision either way: unlike DecayThreshold/DecayVoi, CoverageStop's
    choice of WHETHER to search depends only on whether anything is
    currently believed, never on how stale or how costly reaching it
    would be — it just turns out "search when nothing is believed" and
    "nothing to search for" coincide exactly."""

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is not None:
            return _answer_from_belief(belief, question, question.label, t, confidence=1.0)
        return _continue_or_answer(belief, question, question.label, t, travel_time_to, confidence=1.0)


@dataclass(frozen=True)
class DecayThresholdConfig:
    theta: float = 0.5
    # Mondrian (group-conditional) conformal mode (Suite Buildout coverage-
    # repair phase): {wait_hours_bucket: theta}, one theta per swept
    # wait_hours value, calibrated by belief.calibrate_conformal_theta_by_
    # wait. When set, DecayThreshold looks up the bucket nearest the
    # CURRENT elapsed-since-last-update time instead of using the single
    # scalar `theta` above — a global theta was found to badly
    # miscalibrate long-wait decisions (dwell-time covariate shift; see
    # that function's own docstring). None (the default) preserves every
    # prior milestone's exact behavior — plain decay_threshold never sets
    # this.
    theta_by_wait: Optional[dict[float, float]] = None


class DecayThreshold:
    def __init__(self, config: Optional[DecayThresholdConfig] = None) -> None:
        self.policy_config = config or DecayThresholdConfig()

    def _theta_for(self, belief: BeliefStore, label: str, t: float) -> float:
        if self.policy_config.theta_by_wait is None:
            return self.policy_config.theta
        elapsed = belief.elapsed_since_update(label, t)
        if elapsed is None:
            return self.policy_config.theta
        bucket = min(self.policy_config.theta_by_wait, key=lambda w: abs(w - elapsed))
        return self.policy_config.theta_by_wait[bucket]

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is None:
            return Abstain()
        validity = belief.validity(question.label, t)
        theta = self._theta_for(belief, question.label, t)
        if validity < theta:
            return _continue_or_answer(belief, question, question.label, t, travel_time_to, confidence=validity)
        return _answer_from_belief(belief, question, question.label, t, confidence=validity)


@dataclass(frozen=True)
class DecayVoiConfig:
    latency_weight: float = 1.0 / 3600.0  # accuracy-units penalty per second of travel


class DecayVoi:
    """Resense iff expected accuracy gain from re-observation exceeds
    latency_weight * travel_time. Gain is computed against what confidence
    would be at arrival time if we *don't* resense (belief.validity at
    t + travel_time) vs. the certainty a fresh observation gives (1.0) —
    so a long trip that lets the belief decay further before we'd even get
    there is correctly charged for that additional decay, not just its
    own travel cost."""

    def __init__(self, config: Optional[DecayVoiConfig] = None) -> None:
        self.policy_config = config or DecayVoiConfig()

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is None:
            return Abstain()
        if _just_confirmed(belief, question.label, t):
            return _answer_from_belief(belief, question, question.label, t,
                                       confidence=belief.validity(question.label, t))

        # Cost/benefit uses the top believed anchor's own travel time as
        # the representative trip cost — the VoI decision boundary is
        # unchanged from before search existed; only what gets visited if
        # the trip is taken (below) is upgraded to a search.
        travel_seconds = travel_time_to(anchor)
        if not math.isfinite(travel_seconds):
            return _answer_from_belief(belief, question, question.label, t,
                                       confidence=belief.validity(question.label, t))

        arrival_t = t + travel_seconds / 3600.0
        validity_if_no_resense = belief.validity(question.label, arrival_t)
        gain = 1.0 - validity_if_no_resense
        cost = self.policy_config.latency_weight * travel_seconds

        if gain > cost:
            return _continue_or_answer(belief, question, question.label, t, travel_time_to,
                                       confidence=belief.validity(question.label, t))
        return _answer_from_belief(belief, question, question.label, t,
                                   confidence=belief.validity(question.label, t))


class DecayVoiRouting(DecayVoi):
    """Same value-of-information test as DecayVoi, extended (in a future
    multi-object-question phase — see experiment E3) to choose among
    candidate routes by crediting en-route refresh of other
    question-relevant beliefs. This phase's questions are single-label, so
    there is nothing to route among yet — this is currently a named,
    separate class (not a DecayVoi alias) so E3's multi-object routing
    logic has its own place to live without disturbing DecayVoi's simpler
    behavior, but its actual decision rule today is identical to DecayVoi's.
    Documented here rather than silently passed off as a complete
    implementation."""


def _deterministic_unit_interval(seed: int, label: str, t: float) -> float:
    """A reproducible pseudo-random float in [0, 1), derived by hashing
    (seed, label, t) rather than drawing from a stateful RNG object — keeps
    RandomResense a stateless frozen-config policy like every other class
    in this module (see _n_ruled_out's docstring for why that matters: no
    mutable per-episode state anywhere in a policy)."""
    key = f"{seed}:{label}:{t!r}"
    digest = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(digest[:8], "little") / 2 ** 64


@dataclass(frozen=True)
class RandomResenseConfig:
    """p_resense: probability of attempting a resense at each decision
    point where something is already believed, independent of category,
    staleness, or cost. Calibrated (not guessed) so this policy's realized
    mean travel distance matches decay_voi's ~2.2m on the same scene —
    see results/reports/budget_matched_random.md for the calibration run
    and the value this defaults to. seed makes the draw reproducible."""
    p_resense: float
    seed: int = 0


class RandomResense:
    """Control baseline for E2: a travel-budget-matched null model for
    decay_voi's *selectivity*. Resenses with fixed probability p_resense
    at each decision point rather than weighing expected gain against
    cost — so any accuracy gap between this policy and decay_voi at
    matched average travel distance is attributable to WHICH resenses
    decay_voi chooses, not merely how many trips it takes. Uses the same
    belief.validity()-based confidence as decay_voi (not a flat 1.0) so
    the comparison isolates the resense-selection rule, not confidence
    calibration."""

    def __init__(self, config: RandomResenseConfig) -> None:
        self.policy_config = config

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is None:
            return Abstain()
        if _just_confirmed(belief, question.label, t):
            return _answer_from_belief(belief, question, question.label, t,
                                       confidence=belief.validity(question.label, t))
        roll = _deterministic_unit_interval(self.policy_config.seed, question.label, t)
        if roll < self.policy_config.p_resense:
            return _continue_or_answer(belief, question, question.label, t, travel_time_to,
                                       confidence=belief.validity(question.label, t))
        return _answer_from_belief(belief, question, question.label, t,
                                   confidence=belief.validity(question.label, t))


@dataclass(frozen=True)
class TimeOnlyThresholdConfig:
    """threshold_hours: resense iff elapsed time since the belief was last
    (positively) observed exceeds this fixed cutoff — no reference to
    category, fitted decay rate, or posterior validity anywhere in the
    decision. 1.0 hour is an untuned, round-number default: tuning it
    against this pool's data would defeat the point of a cheap,
    category-blind competitor to DecayThreshold's calibrated theta."""
    threshold_hours: float = 1.0


class TimeOnlyThreshold:
    """Control baseline for E2: resense iff observation age exceeds a
    fixed threshold, category-blind. Unlike DecayThreshold (which compares
    a fitted per-category validity to theta), this policy never consults
    the decay-model machinery for its decision at all — only a raw
    elapsed-time comparison. Confidence is a flat 1.0 when it answers,
    matching CoverageStop's convention for a policy with no calibration
    model of its own: this is a "clock only" baseline, not a strawman."""

    def __init__(self, config: Optional[TimeOnlyThresholdConfig] = None) -> None:
        self.policy_config = config or TimeOnlyThresholdConfig()

    def act(self, belief: BeliefStore, question: "MCQQuestion", pose, t: float,
            config: AgentConfig, travel_time_to: TravelTimeFn) -> Decision:
        anchor = belief.believed_anchor(question.label, t)
        if anchor is None:
            return Abstain()
        elapsed = belief.elapsed_since_update(question.label, t)
        stale = elapsed is None or elapsed > self.policy_config.threshold_hours
        if stale:
            return _continue_or_answer(belief, question, question.label, t, travel_time_to, confidence=1.0)
        return _answer_from_belief(belief, question, question.label, t, confidence=1.0)
