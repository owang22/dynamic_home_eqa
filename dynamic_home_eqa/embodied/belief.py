"""
belief.py — BeliefStore: a timestamped, decaying map of where the agent
believes each object instance currently is.

No prior decay_map module exists in this repo (checked before writing this
one) — ObjectNode / Observation / DecayModel are built fresh here, not
ported from anything, despite sharing names with what a mature version of
this idea would eventually look like.

DecayModel is an exponential survival model: validity(elapsed_hours) is the
probability the object has NOT moved since it was last observed, memoryless
(P(survive a+b | survived a) = P(survive b)) — a defensible default given
the generator has no per-object schedule, only aggregate per-category
hazard statistics (generation/exports.py's category_location_change_stats).
lambda_per_hour = 1 / mean_dwell_hours is fit from real generated days
(fit_decay_models), never hand-tuned in this module.

Negative observations are the correctness-critical piece: a sense() that
covers a believed instance's stored anchor but doesn't detect it there must
drive validity to 0 and mark the node displaced — otherwise an agent
looking straight at an empty table would still trust a stale belief. See
update_from_snapshot.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .types import OracleDetection, Pose, SenseSnapshot

if TYPE_CHECKING:
    from .world import EmbodiedWorld

DEFAULT_LAMBDA_PER_HOUR = 1.0 / 4.0  # conservative fallback: ~4h mean dwell time


# ---------------------------------------------------------------------------
# DecayModel
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DecayModel:
    category: str
    lambda_per_hour: float

    def validity(self, elapsed_hours: float) -> float:
        """P(no move occurred in `elapsed_hours`) — exponential survival."""
        return math.exp(-self.lambda_per_hour * max(0.0, elapsed_hours))


def fit_decay_models(category_stats: dict[str, dict]) -> dict[str, DecayModel]:
    """One DecayModel per category from generation/exports.py's
    category_location_change_stats output (or aggregate_category_stats'
    merge of several days — see the calibration protocol). A category with
    no measurable dwell time (mean_dwell_hours is None — fewer than two
    location changes observed for it) falls back to DEFAULT_LAMBDA_PER_HOUR,
    not a zero or infinite rate."""
    models = {}
    for cat, stats in category_stats.items():
        dwell = stats.get("mean_dwell_hours")
        lam = (1.0 / dwell) if dwell and dwell > 0 else DEFAULT_LAMBDA_PER_HOUR
        models[cat] = DecayModel(category=cat, lambda_per_hour=lam)
    return models


def aggregate_category_stats(days: list[dict[str, dict]]) -> dict[str, dict]:
    """Merge category_location_change_stats from several days (the
    calibration protocol's train split) into one view per category:
    location_changes summed, distinct_slots_visited summed, mean_dwell_hours
    a changes-weighted mean across days that had any (so a single very
    short day doesn't get equal say with a day that had many observations
    of that category)."""
    totals: dict[str, dict] = {}
    for day_stats in days:
        for cat, stats in day_stats.items():
            agg = totals.setdefault(cat, {"location_changes": 0, "distinct_slots_visited": 0,
                                          "_dwell_weighted_sum": 0.0, "_dwell_weight": 0})
            agg["location_changes"] += stats["location_changes"]
            agg["distinct_slots_visited"] = max(agg["distinct_slots_visited"], stats["distinct_slots_visited"])
            if stats.get("mean_dwell_hours") is not None:
                weight = stats["location_changes"]
                agg["_dwell_weighted_sum"] += stats["mean_dwell_hours"] * weight
                agg["_dwell_weight"] += weight

    out: dict[str, dict] = {}
    for cat, agg in totals.items():
        mean_dwell = (agg["_dwell_weighted_sum"] / agg["_dwell_weight"]) if agg["_dwell_weight"] > 0 else None
        out[cat] = {
            "location_changes": agg["location_changes"],
            "distinct_slots_visited": agg["distinct_slots_visited"],
            "mean_dwell_hours": mean_dwell,
        }
    return out


def _event_key(c: dict) -> str:
    """The category-like key an event's dwell time should be attributed to:
    the synthetic "{category}::{variable}" key for a state_change event
    (matching how state decay_models/kernels are keyed — see posterior.py's
    module docstring), or the bare object_category for a location event.
    Getting this wrong is silent, not a crash: calibrate_conformal_theta's
    `if cat in decay_models` filter just finds zero matching events and
    falls back to the uncalibrated default, which is exactly what happened
    before this fix (state-axis conformal_decay_threshold was silently
    identical to plain decay_threshold — see the Suite Buildout phase B2
    conformal coverage check that caught it)."""
    if c.get("change_type") == "state_change":
        return f"{c['object_category']}::{c['state_variable']}"
    return c["object_category"]


def _event_value(c: dict) -> str:
    """The belief-store state value a change event establishes as current:
    to_state for a state_change event, to_semantic for a location event —
    whichever of TransitionKernel.states this event's category/key
    enumerates. This is the state a dwell interval's nonconformity score
    gets scored against (see dwell_events / calibrate_conformal_theta):
    the interval between two consecutive events is, by construction, a
    period where the EARLIER event's value stayed true."""
    if c.get("change_type") == "state_change":
        return c["to_state"]
    return c["to_semantic"]


def dwell_events(changes: list[dict]) -> list[tuple[str, str, float]]:
    """[(key, start_state, dwell_hours), ...] — one entry per gap between
    consecutive events for the same (label, key) pair, tagged with the
    value the EARLIER event established (the value that stayed true for
    the whole gap). Grouping by key as well as label (not label alone)
    keeps a label's location-dwell events and state-dwell events from
    ever being gapped against each other — not currently possible
    (Tier-1 stateful furniture never gets a location event), but the
    honest invariant to enforce rather than assume. Same computation
    category_location_change_stats' mean_dwell_hours is built from, but
    returning every individual sample rather than folding straight to a
    mean — calibrate_conformal_theta needs the empirical distribution,
    not just its average."""
    by_label_key: dict[tuple[str, str], list[dict]] = {}
    for c in changes:
        by_label_key.setdefault((c["label"], _event_key(c)), []).append(c)
    events: list[tuple[str, str, float]] = []
    for (_label, key), evs in by_label_key.items():
        evs = sorted(evs, key=lambda c: c["t"])
        for i in range(len(evs) - 1):
            events.append((key, _event_value(evs[i]), evs[i + 1]["t"] - evs[i]["t"]))
    return events


def _posterior_validity_at_dwell(kernel: "TransitionKernel", start_state: str, dwell_hours: float) -> float:
    """The value PosteriorBeliefStore.validity() would report dwell_hours
    after a fresh, fully-confirmed observation of start_state under this
    exact kernel, assuming no intervening observation — exactly the
    assumption a dwell event's gap represents (nothing else touched this
    label's belief between the two events). Max propagated mass among
    non-OUTSIDE states, mirroring PosteriorBeliefStore.validity()'s own
    definition (posterior.py) so calibration and deployment score the
    identical statistic — see calibrate_conformal_theta's docstring for
    why this identity is the one thing a conformal guarantee can't do
    without."""
    from .posterior import OUTSIDE

    initial = {s: (1.0 if s == start_state else 0.0) for s in kernel.states}
    propagated = kernel.propagate(initial, dwell_hours)
    candidates = {s: p for s, p in propagated.items() if s != OUTSIDE}
    return max(candidates.values()) if candidates else 0.0


def calibrate_conformal_theta(
    train_manifests: list[dict], kernels: dict[str, "TransitionKernel"], alpha: float = 0.1,
) -> float:
    """Split-conformal calibration of DecayThreshold's theta (M4 pre-suite
    baseline check — the M2 spec's conformal-threshold variant): the
    largest (least conservative) threshold such that "validity(elapsed)
    >= theta" is empirically correct at least (1-alpha) of the time on
    pooled train-day dwell-time samples, instead of DecayThresholdConfig's
    hand-picked default.

    Nonconformity score per historical dwell event (key, start_state,
    dwell_hours): _posterior_validity_at_dwell(kernels[key], start_state,
    dwell_hours) — the SAME closed-form kernel propagation every deployed
    validity/threshold/VOI policy consults via PosteriorBeliefStore.
    validity() (posterior.py), not a separate parametric proxy. This
    replaced an earlier version that scored calibration events with
    DecayModel.validity(elapsed) = exp(-lambda*elapsed) — a plain
    decay-to-zero curve — while every deployed policy thresholds against
    PosteriorBeliefStore.validity(), which converges to the fitted
    kernel's own (possibly far-from-zero) stationary dest_dist instead.
    Calibrating against one statistic and deploying against a different
    one breaks the conformal guarantee regardless of how carefully theta
    itself is computed — the guarantee is a statement about quantiles of
    ONE distribution. The mismatch was invisible on the location axis
    (many-anchor posteriors decay low enough within the swept wait-hours
    range for the two curves to cross the same thresholds) but made
    conformal_decay_threshold byte-for-byte identical to plain
    decay_threshold on the state axis (a 2-value, sticky kernel whose
    real posterior validity never dropped anywhere near either curve's
    calibrated theta) — see the Suite Buildout phase B2 conformal
    coverage check that surfaced it.

    Keys absent from kernels contribute no calibration events (nothing to
    score them with — see fit_transition_kernels / fit_state_transition_
    kernels). Falls back to DecayThresholdConfig's own default if there
    are fewer than 2 calibration events (not enough to calibrate against).
    """
    from .policy import DecayThresholdConfig

    events = [c for m in train_manifests for c in dwell_events(m["changes"])]
    scores = sorted(
        _posterior_validity_at_dwell(kernels[key], start_state, dwell)
        for key, start_state, dwell in events if key in kernels
    )
    return _alpha_quantile(scores, alpha, fallback=DecayThresholdConfig().theta)


def _alpha_quantile(scores: list[float], alpha: float, fallback: float) -> float:
    """The alpha-quantile (lower/conservative empirical quantile, the
    standard finite-sample split-conformal convention) of a sorted-or-not
    list of nonconformity scores, or `fallback` if there are fewer than 2
    (not enough to calibrate against). Shared by calibrate_conformal_theta
    and calibrate_conformal_theta_by_wait so both use one quantile rule."""
    scores = sorted(scores)
    if len(scores) < 2:
        return fallback
    idx = max(0, min(len(scores) - 1, math.ceil(alpha * len(scores)) - 1))
    return scores[idx]


def calibrate_conformal_theta_by_wait(
    train_manifests: list[dict],
    kernels: dict[str, "TransitionKernel"],
    wait_buckets: tuple[float, ...],
    alpha: float = 0.1,
) -> dict[float, float]:
    """Group-conditional (Mondrian) conformal calibration: one theta per
    wait_hours bucket, instead of calibrate_conformal_theta's single
    pooled theta — the fix for the coverage-repair phase's finding that a
    global theta collapses realized coverage as wait_hours grows (a
    dwell-time covariate shift: deployment asks about validity at fixed
    swept wait_hours, but a global theta is calibrated from ALL natural
    calibration dwell events pooled together, the large majority of which
    are much shorter than the longer swept waits — e.g. on the frozen
    scene's location train days, 82% of natural dwell events are already
    over by wait=4h, so a global quantile is dominated by short-dwell
    behavior and badly miscalibrated for that wait).

    Critically, each event's nonconformity score is evaluated AT THE
    BUCKET'S OWN wait_hours value — _posterior_validity_at_dwell(kernel,
    start_state, w), not at the event's own natural dwell_hours. Scoring
    at the event's own dwell (an earlier version of this function did
    exactly that) reproduces the same calibration-vs-deployment space
    mismatch the kernel-based rewrite of calibrate_conformal_theta was
    built to eliminate, just re-introduced per-bucket instead of
    globally: deployment always queries validity at a FIXED elapsed
    time (the current wait_hours), so calibration must score every event
    at that same fixed time to share one measurement space. Every
    calibration event (from every category/state, not a dwell-matched
    subset) contributes one score per bucket; only the elapsed time
    changes between buckets. A bucket with fewer than 2 events (i.e. no
    fitted kernels matched anything) falls back to the pooled/global
    theta (calibrate_conformal_theta).

    Because _posterior_validity_at_dwell(kernel, start_state, w) depends
    only on (kernel, start_state, w) — not on any individual event's own
    dwell_hours — events sharing a (key, start_state) pair contribute
    identical scores; the quantile's real resolution is the number of
    DISTINCT (key, start_state) pairs seen, not the raw event count. This
    is a structural property of scoring against a fitted kernel, not a
    bug, and is reported alongside the fix (see scripts/conformal_
    coverage_check.py's per-bucket verification, which also reports it).
    """
    events = [c for m in train_manifests for c in dwell_events(m["changes"])]
    global_theta = calibrate_conformal_theta(train_manifests, kernels, alpha=alpha)
    thetas: dict[float, float] = {}
    for w in wait_buckets:
        scores = [
            _posterior_validity_at_dwell(kernels[key], start_state, w)
            for key, start_state, _dwell in events if key in kernels
        ]
        thetas[w] = _alpha_quantile(scores, alpha, fallback=global_theta)
    return thetas


# ---------------------------------------------------------------------------
# ObjectNode / Observation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Observation:
    t:      float
    pose:   Pose
    anchor: str


@dataclass
class ObjectNode:
    label:    str
    category: str
    observations: list[Observation] = field(default_factory=list)
    # Set by a negative observation (sensed the believed anchor, found
    # nothing there); cleared by any subsequent positive detection.
    displaced: bool = False

    @property
    def last_observation(self) -> Optional[Observation]:
        return self.observations[-1] if self.observations else None

    @property
    def believed_anchor(self) -> Optional[str]:
        obs = self.last_observation
        return obs.anchor if obs is not None else None


@dataclass(frozen=True)
class TransitionRecord:
    """Logged when a new detection's anchor differs from the node's
    previously believed anchor — for later hazard-rate / calibration
    analysis, not consumed by the belief mechanism itself."""
    label:       str
    t:           float
    from_anchor: str
    to_anchor:   str


# ---------------------------------------------------------------------------
# BeliefStore
# ---------------------------------------------------------------------------

class BeliefStore:
    def __init__(self, decay_models: dict[str, DecayModel]) -> None:
        self.decay_models = decay_models
        self.nodes: dict[str, ObjectNode] = {}
        self.transition_log: list[TransitionRecord] = []

    def _model_for(self, category: str) -> DecayModel:
        return self.decay_models.get(category) or DecayModel(category, DEFAULT_LAMBDA_PER_HOUR)

    def observe_detection(self, detection: OracleDetection, pose: Pose) -> None:
        """Record a positive detection: the instance was seen at
        detection.anchor at detection.t. Un-displaces the node (a fresh
        sighting supersedes any earlier negative observation) and logs a
        transition if the anchor changed since the last belief."""
        node = self.nodes.get(detection.label)
        if node is None:
            node = ObjectNode(label=detection.label, category=detection.category)
            self.nodes[detection.label] = node
        else:
            prior_anchor = node.believed_anchor
            if prior_anchor is not None and prior_anchor != detection.anchor:
                self.transition_log.append(TransitionRecord(
                    label=detection.label, t=detection.t,
                    from_anchor=prior_anchor, to_anchor=detection.anchor,
                ))
        node.observations.append(Observation(t=detection.t, pose=pose, anchor=detection.anchor))
        node.displaced = False

    def observe_negative(self, label: str, t: float) -> None:
        """A sense() covered this label's believed anchor and did not
        detect it there. Drives validity to 0 (via `displaced`) — the
        belief becomes "not where I thought, location unknown" rather than
        silently continuing to trust a stale anchor. No-op if nothing is
        believed about this label yet (nothing to invalidate)."""
        node = self.nodes.get(label)
        if node is None:
            return
        node.displaced = True

    def validity(self, label: str, t: float) -> float:
        """P(the believed anchor is still current) at time t. 0.0 if
        nothing is believed, or the node was displaced by a negative
        observation with no positive re-sighting since."""
        node = self.nodes.get(label)
        if node is None or node.believed_anchor is None or node.displaced:
            return 0.0
        elapsed = t - node.last_observation.t
        return self._model_for(node.category).validity(elapsed)

    def elapsed_since_update(self, label: str, t: float) -> Optional[float]:
        """Hours since label's last (positive) observation, or None if
        never observed — the covariate DecayThreshold's Mondrian
        (per-wait-bucket theta) mode needs to pick the calibration bucket
        matching the CURRENT decision, mirroring validity()'s own elapsed
        computation above."""
        node = self.nodes.get(label)
        if node is None or node.last_observation is None:
            return None
        return t - node.last_observation.t

    def believed_anchor(self, label: str, t: Optional[float] = None) -> Optional[str]:
        """The currently-believed anchor, or None if nothing is believed or
        the node is displaced (belief store has no candidate anchor at all
        after a negative observation, by design — see module docstring).
        t is accepted (and ignored) for interface parity with
        posterior.PosteriorBeliefStore's time-aware compatibility view —
        this store's single-anchor belief was never time-propagated here
        in the first place (only validity() incorporates time)."""
        node = self.nodes.get(label)
        if node is None or node.displaced:
            return None
        return node.believed_anchor

    def known_labels(self) -> list[str]:
        return list(self.nodes.keys())

    def top_candidates(self, label: str, t: float, travel_time_to=None, k: int = 3) -> tuple[str, ...]:
        """Compatibility view for policy.py's search-ranking call site: this
        store has only ever tracked one candidate anchor at a time, so the
        "ranked search list" is that one anchor, or empty if nothing is
        believed."""
        anchor = self.believed_anchor(label)
        return (anchor,) if anchor is not None else ()

    # -- integration with EmbodiedWorld -----------------------------------

    def update_from_snapshot(self, snapshot: SenseSnapshot, world: "EmbodiedWorld") -> None:
        """Apply one sense snapshot: positive detections update/create
        nodes; any label already believed whose stored anchor *would have
        been visible* from this snapshot's pose, but which the snapshot did
        not detect, gets a negative observation. "Would have been visible"
        is re-evaluated against the believed anchor's own world position
        (not the object's real position — the agent has no access to real
        position, only its belief and the geometry oracle), so a negative
        observation only fires when the agent had a genuine, unobstructed
        line of sight to where it thought the object was.
        """
        from .sensor import is_visible

        detected_labels = {d.label for d in snapshot.detections}
        for detection in snapshot.detections:
            self.observe_detection(detection, snapshot.pose)

        eye_pos = (snapshot.pose.x, snapshot.pose.y + world.config.sensor.eye_height_m, snapshot.pose.z)
        for label, node in self.nodes.items():
            if label in detected_labels or node.displaced:
                continue
            believed = node.believed_anchor
            if believed is None:
                continue
            believed_pos = world._resolve_slot_position(label, believed)
            if believed_pos is None:
                continue
            if is_visible(world._sim, eye_pos, snapshot.pose.yaw_rad, believed_pos, world.config.sensor):
                self.observe_negative(label, snapshot.t)

    def update_from_result(self, result, world: "EmbodiedWorld") -> None:
        """Apply every snapshot in an ActionResult, in order — the
        mechanism that makes opportunistic en-route belief refresh
        automatic (see types.ActionResult's docstring)."""
        for snapshot in result.snapshots:
            self.update_from_snapshot(snapshot, world)
