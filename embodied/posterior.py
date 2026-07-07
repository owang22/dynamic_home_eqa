"""
posterior.py — M2: posterior-over-anchors belief and its transition kernel.

Replaces belief.py's single-last-known-anchor + exponential-decay model
with a categorical distribution over (known anchors + OUTSIDE) per label.
A positive observation collapses the posterior to a one-hot at the
observed anchor; a negative observation (checked an anchor, found nothing)
zeroes that state and renormalizes the rest — the mechanism that lets
search-based resensing actually narrow down *where* an object went, not
just notice that it isn't where it used to be (belief.py's ceiling).

validity()/believed_anchor() are kept as compatibility views recomputed
from the posterior (max non-OUTSIDE mass / its argmax), so every M1 policy
that only calls those two methods (plus the new top_candidates()) works
unchanged against this richer store — see policy.py's docstring.

Temporal propagation model: a renewal process per category. At any elapsed
time Δt since the belief was last touched, mass migrates from wherever it
currently sits toward the category's fitted dest_dist (P(destination |
some move happened)) at rate lambda_per_hour (the same exponential-survival
rate belief.DecayModel already fits — P(no move) = exp(-lambda*Δt)):

    posterior_after(s) = alpha(Δt) * posterior_before(s) + (1-alpha(Δt)) * dest_dist(s)
    alpha(Δt) = exp(-lambda_per_hour * Δt)

This composes exactly under repeated application (alpha(t1)*alpha(t2) =
alpha(t1+t2), since renewal-process transition matrices with the same
dest_dist multiply by multiplying their alpha — see TransitionKernel's
docstring for the derivation) — the same discrete-time transition matrix a
0.25h step would give, applied any number of times, converging to
dest_dist as its stationary distribution. propagate() below evaluates the
closed form directly for whatever Δt is actually needed (exact, not an
approximation of iterating a matrix), while matrix_at() exposes the
explicit 0.25h-step matrix the phase spec asks for so it can be tested
directly (row-sum-to-1, convergence to the same stationary distribution).

Four train days is thin for fitting a full |states|x|states| transition
matrix per category (up to ~10x10 parameters against a handful of events).
fit_transition_kernels uses hierarchical backoff on both renewal-process
factors instead of raw per-category MLE counts:
  - lambda_per_hour: shrunk toward the pooled (all-category) empirical
    rate, weighted by the category's own observed location-change count.
  - dest_dist: computed over CANONICAL_ROOMS (the one vocabulary shared
    across categories whose real anchor sets are otherwise disjoint —
    kitchen categories don't have bedroom anchors to pool with), shrunk
    toward the pooled cross-category room distribution the same way, then
    redistributed uniformly across the category's own known anchors within
    each room (no data to prefer one same-room anchor over another).
A category with zero observed events gets EXACTLY the pooled kernel in
both factors (shrinkage weight 0 collapses to the pooled value) — this is
the required backoff property, not an incidental one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional, TYPE_CHECKING

from ..rooms import CANONICAL_ROOMS, slot_room
from .belief import DEFAULT_LAMBDA_PER_HOUR, TransitionRecord
from .types import OracleDetection, Pose, SenseSnapshot

if TYPE_CHECKING:
    from .world import EmbodiedWorld

# Same sentinel question.py's MCQ generator uses for "not in the house" —
# sharing it means a posterior's OUTSIDE state lines up with the MCQ option
# built for it, with no translation layer between the two.
OUTSIDE = "OUTSIDE"

_DEFAULT_PROPAGATION_STEP_HOURS = 0.25
_DEFAULT_PRIOR_STRENGTH = 3.0


def _shrink(own_value: float, pooled_value: float, own_weight: float, prior_strength: float) -> float:
    """Weighted shrinkage of a per-category empirical statistic toward a
    pooled cross-category statistic. own_weight=0 returns exactly
    pooled_value; own_weight >> prior_strength returns close to own_value.
    Applied elementwise to a whole distribution, this is a Dirichlet-style
    backoff (the shrunk vector stays normalized automatically, since both
    inputs already sum to 1 — see fit_transition_kernels)."""
    return (own_weight * own_value + prior_strength * pooled_value) / (own_weight + prior_strength)


@dataclass(frozen=True)
class HierarchicalStat:
    """One backoff level's own empirical value and its weight (e.g. a
    location_changes count) — the input shrink_hierarchical shrinks
    toward the next level up. weight=0 means "no data at this level",
    the case shrink_hierarchical must reduce to the next level's value
    exactly."""
    value:  float
    weight: float


def shrink_hierarchical(
    scene: HierarchicalStat, profile: HierarchicalStat, global_: HierarchicalStat,
    prior_strength: float = _DEFAULT_PRIOR_STRENGTH,
) -> float:
    """D1 (kernel generalization): 3-level count-weighted backoff, scene ->
    profile -> global, reusing _shrink's own weighted-average rule at each
    level — no new smoothing math, the same mechanism fit_transition_
    kernels already uses for its 2-level own-category-vs-scene-pooled
    backoff, nested one level further so a category with thin or no data
    in THIS scene can still draw on other scenes sharing its household
    profile before falling all the way back to the global pool.

    profile first backs off toward global (a profile with zero of its own
    events reduces to EXACTLY the global value — _shrink(x, g, 0, p) = g
    for any x), then scene backs off toward that already-backed-off
    profile value (a scene with zero of its own events reduces to
    EXACTLY the profile value, which may itself already equal the global
    value). Both fallbacks are exact, not approximate, by construction of
    _shrink's own weight=0 case — see this function's own tests."""
    profile_backed_off = _shrink(profile.value, global_.value, profile.weight, prior_strength)
    return _shrink(scene.value, profile_backed_off, scene.weight, prior_strength)


def _normalize_with_laplace(counts: dict[str, int], keys: tuple[str, ...], alpha: float = 1.0) -> dict[str, float]:
    total = sum(counts.get(k, 0) for k in keys) + alpha * len(keys)
    return {k: (counts.get(k, 0) + alpha) / total for k in keys}


# ---------------------------------------------------------------------------
# TransitionKernel
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TransitionKernel:
    category:        str
    states:          tuple[str, ...]     # this category's known anchors (sorted) + OUTSIDE
    lambda_per_hour: float
    dest_dist:       tuple[float, ...]   # parallel to states; P(destination | a move happens); sums to 1

    def matrix_at(self, step_hours: float = _DEFAULT_PROPAGATION_STEP_HOURS) -> tuple[tuple[float, ...], ...]:
        """Explicit row-stochastic transition matrix for one discrete step
        of step_hours: a renewal-process matrix P(i,j) = alpha*1{i=j} +
        (1-alpha)*dest_dist[j], alpha = exp(-lambda*step_hours). Exists for
        the kernel's own correctness tests; propagate() below uses the
        closed form directly rather than iterating this matrix."""
        alpha = math.exp(-self.lambda_per_hour * max(0.0, step_hours))
        n = len(self.states)
        return tuple(
            tuple(alpha * (1.0 if i == j else 0.0) + (1 - alpha) * self.dest_dist[j] for j in range(n))
            for i in range(n)
        )

    def propagate(self, posterior: dict[str, float], elapsed_hours: float) -> dict[str, float]:
        """Exact closed-form propagation for any elapsed_hours (not just a
        multiple of the 0.25h step) — see module docstring for why this is
        exact, not an approximation."""
        alpha = math.exp(-self.lambda_per_hour * max(0.0, elapsed_hours))
        return {
            s: alpha * posterior.get(s, 0.0) + (1 - alpha) * self.dest_dist[i]
            for i, s in enumerate(self.states)
        }

    def stationary_distribution(self) -> dict[str, float]:
        """This renewal chain's unique stationary distribution is dest_dist
        itself — also what propagate() converges to as elapsed_hours grows
        without bound, regardless of starting posterior."""
        return dict(zip(self.states, self.dest_dist))


def _pooled_lambda(category_stats: dict[str, dict]) -> float:
    weighted_sum = 0.0
    total_weight = 0.0
    for stats in category_stats.values():
        dwell = stats.get("mean_dwell_hours")
        if dwell and dwell > 0:
            weight = stats.get("location_changes", 0)
            weighted_sum += weight * (1.0 / dwell)
            total_weight += weight
    return (weighted_sum / total_weight) if total_weight > 0 else DEFAULT_LAMBDA_PER_HOUR


def _room_counts(changes: list[dict], category: Optional[str] = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in changes:
        if category is not None and c["object_category"] != category:
            continue
        room = slot_room(c["to_semantic"]) or "outdoor"
        counts[room] = counts.get(room, 0) + 1
    return counts


def fit_transition_kernels(
    train_manifests: list[dict],
    category_stats: dict[str, dict],
    anchor_history: dict[str, set[str]],
    prior_strength: float = _DEFAULT_PRIOR_STRENGTH,
) -> dict[str, TransitionKernel]:
    """One TransitionKernel per category in anchor_history, per the
    hierarchical-backoff scheme in this module's docstring."""
    all_changes = [c for m in train_manifests for c in m["changes"]]
    pooled_lambda = _pooled_lambda(category_stats)
    pooled_room_dist = _normalize_with_laplace(_room_counts(all_changes), CANONICAL_ROOMS)

    kernels: dict[str, TransitionKernel] = {}
    for category, anchors in anchor_history.items():
        states = tuple(sorted(anchors)) + (OUTSIDE,)
        state_room = {a: (slot_room(a) or "outdoor") for a in anchors}
        state_room[OUTSIDE] = "outdoor"

        stats = category_stats.get(category, {})
        own_weight = float(stats.get("location_changes", 0))
        dwell = stats.get("mean_dwell_hours")
        own_lambda = (1.0 / dwell) if dwell and dwell > 0 else pooled_lambda
        lam = _shrink(own_lambda, pooled_lambda, own_weight, prior_strength)

        own_room_dist = _normalize_with_laplace(_room_counts(all_changes, category), CANONICAL_ROOMS)
        shrunk_room_dist = {
            room: _shrink(own_room_dist[room], pooled_room_dist[room], own_weight, prior_strength)
            for room in CANONICAL_ROOMS
        }

        anchors_per_room: dict[str, list[str]] = {}
        for a in anchors:
            anchors_per_room.setdefault(state_room[a], []).append(a)

        dest_dist = []
        for s in states:
            room = state_room[s]
            if s == OUTSIDE:
                dest_dist.append(shrunk_room_dist["outdoor"])
            else:
                n_in_room = len(anchors_per_room.get(room, []))
                dest_dist.append(shrunk_room_dist[room] / n_in_room if n_in_room else 0.0)
        total = sum(dest_dist)
        dest_dist = [d / total for d in dest_dist] if total > 0 else [1.0 / len(states)] * len(states)

        kernels[category] = TransitionKernel(
            category=category, states=states, lambda_per_hour=lam, dest_dist=tuple(dest_dist),
        )
    return kernels


def _state_value_counts(changes: list[dict], key: str) -> dict[str, int]:
    """{to_state: count} for change_type == "state_change" events whose
    "{object_category}::{state_variable}" matches `key`."""
    counts: dict[str, int] = {}
    for c in changes:
        if c.get("change_type") != "state_change":
            continue
        if f"{c['object_category']}::{c['state_variable']}" != key:
            continue
        counts[c["to_state"]] = counts.get(c["to_state"], 0) + 1
    return counts


def fit_state_transition_kernels(
    train_manifests: list[dict],
    category_stats: dict[str, dict],
    variable_domains: dict[str, tuple[str, ...]],
    prior_strength: float = _DEFAULT_PRIOR_STRENGTH,
) -> dict[str, TransitionKernel]:
    """State-axis counterpart of fit_transition_kernels (M3: state-change
    dynamics) — same hierarchical-backoff scheme for lambda_per_hour, but a
    much simpler dest_dist: a state variable's domain is already the full
    set of legal values (env/deltas.py's STATE_VARIABLES), not an open-
    ended set of real anchors clustered by room, so dest_dist is just the
    Laplace-smoothed, shrunk-toward-pooled distribution over to_state
    counts directly — no room-pooling/redistribution step (which assumes
    "state" means "location slot", the assumption fit_transition_kernels
    makes and this function exists specifically to avoid).

    category_stats keys and variable_domains keys are both
    "{category}::{state_variable}" (e.g. "tv::power" — see
    generation.exports.category_state_flip_stats / attribution.
    state_category_stats_from_train). variable_domains maps that key to
    its variable's legal values tuple (STATE_VARIABLES[variable]["values"]).
    """
    all_changes = [c for m in train_manifests for c in m["changes"]]
    pooled_lambda = _pooled_lambda(category_stats)

    all_counts_by_key = {key: _state_value_counts(all_changes, key) for key in variable_domains}
    pooled_counts: dict[str, int] = {}
    for counts in all_counts_by_key.values():
        for value, n in counts.items():
            pooled_counts[value] = pooled_counts.get(value, 0) + n

    kernels: dict[str, TransitionKernel] = {}
    for key, domain in variable_domains.items():
        states = domain  # no OUTSIDE — a state variable has no "removed" concept
        stats = category_stats.get(key, {})
        own_weight = float(stats.get("location_changes", 0))
        dwell = stats.get("mean_dwell_hours")
        own_lambda = (1.0 / dwell) if dwell and dwell > 0 else pooled_lambda
        lam = _shrink(own_lambda, pooled_lambda, own_weight, prior_strength)

        own_dist = _normalize_with_laplace(all_counts_by_key[key], states)
        pooled_dist = _normalize_with_laplace(pooled_counts, states)
        dest_dist = tuple(
            _shrink(own_dist[s], pooled_dist[s], own_weight, prior_strength) for s in states
        )
        total = sum(dest_dist)
        dest_dist = tuple(d / total for d in dest_dist) if total > 0 else tuple(1.0 / len(states) for _ in states)

        kernels[key] = TransitionKernel(category=key, states=states, lambda_per_hour=lam, dest_dist=dest_dist)
    return kernels


def bucket_changes_by_time_of_day(train_manifests: list[dict], n_buckets: int = 4) -> list[list[dict]]:
    """Splits every manifest's changes into n_buckets equal-width buckets of
    the day (bucket = int(t % 24 / (24/n_buckets))) — the same bucketing
    fit_transition_kernels_by_time_of_day fits kernels on, exposed
    separately so a caller can also compute per-bucket category_stats
    (generation.exports.category_location_change_stats) from the identical
    partition, e.g. for the schedule-only tod_prior baseline (see
    TimeOfDayBeliefStore) rather than reimplementing this split."""
    bucket_width = 24.0 / n_buckets
    per_bucket_changes: list[list[dict]] = [[] for _ in range(n_buckets)]
    for m in train_manifests:
        for c in m["changes"]:
            bucket = int((c["t"] % 24.0) / bucket_width) % n_buckets
            per_bucket_changes[bucket].append(c)
    return per_bucket_changes


def fit_transition_kernels_by_time_of_day(
    train_manifests: list[dict],
    category_stats_by_bucket: list[dict[str, dict]],
    anchor_history: dict[str, set[str]],
    n_buckets: int = 4,
    prior_strength: float = _DEFAULT_PRIOR_STRENGTH,
) -> dict[str, tuple[TransitionKernel, ...]]:
    """Variant A: time-of-day inhomogeneous kernels — a bucketed schedule
    prior, NOT a FreMEn (Frequency Map Enhancement) fit (no frequency-domain
    estimation happens anywhere here — see TimeOfDayBeliefStore's own
    docstring for why this baseline was renamed away from "fremen"). One
    TransitionKernel per (category, bucket) instead of one per category —
    a category's destination distribution and hazard rate can genuinely
    differ between, e.g., an overnight bucket (very little movement) and a
    daytime bucket. Fits an independent kernel per bucket
    (bucket_changes_by_time_of_day) with the same hierarchical backoff as
    fit_transition_kernels (pooled across categories WITHIN that bucket
    only — an overnight bucket's pooled rate should not be diluted by
    daytime activity from other categories). TimeOfDayBeliefStore is this
    variant's consumer: a zero-live-sensing baseline that predicts straight
    from whichever bucket's dest_dist the query time falls into.
    """
    per_bucket_changes = bucket_changes_by_time_of_day(train_manifests, n_buckets)

    result: dict[str, list[TransitionKernel]] = {cat: [] for cat in anchor_history}
    for bucket in range(n_buckets):
        bucket_manifest = [{"changes": per_bucket_changes[bucket]}]
        stats = category_stats_by_bucket[bucket] if bucket < len(category_stats_by_bucket) else {}
        bucket_kernels = fit_transition_kernels(bucket_manifest, stats, anchor_history, prior_strength)
        for cat in anchor_history:
            result[cat].append(bucket_kernels[cat])
    return {cat: tuple(kernels) for cat, kernels in result.items()}


# ---------------------------------------------------------------------------
# PosteriorObjectNode / PosteriorBeliefStore
# ---------------------------------------------------------------------------

@dataclass
class PosteriorObjectNode:
    label:          str
    category:       str
    kernel:         TransitionKernel
    posterior:      dict[str, float]
    last_updated_t: float
    # True if the most recent update was a positive detection (belief
    # collapsed to a confirmed anchor); False if it was a negative
    # observation (a candidate zeroed, mass renormalized across the
    # rest). policy.py's search logic needs to tell these apart: a
    # confirmation means stop and answer, a refutation means keep
    # searching if depth allows — both touch last_updated_t identically,
    # so that timestamp alone can't distinguish them (see policy.py's
    # _just_confirmed).
    last_update_was_positive: bool = False

    def propagated(self, t: float) -> dict[str, float]:
        elapsed = max(0.0, t - self.last_updated_t)
        return self.kernel.propagate(self.posterior, elapsed)


class PosteriorBeliefStore:
    """Drop-in replacement for belief.BeliefStore exposing the same public
    surface every policy calls (observe_detection, believed_anchor,
    validity, known_labels, update_from_snapshot, update_from_result) plus
    top_candidates(), the search-ranking method policy.py's resensing
    logic uses when it's available (see policy._search_targets).

    resense_anchors (M3: state-change dynamics): {category: real navmesh
    anchor} for categories whose belief "states" are value labels
    ("open"/"closed"), not navigable places — top_candidates() below
    cannot rank those as travel targets (travel_time_to("open") is always
    inf, since "open" resolves to no real position), so a category listed
    here instead always resenses that ONE fixed real anchor (the
    underlying furniture's own location — observing it directly reveals
    its current value, so there is never a reason to rank multiple
    candidates the way location search does). Absent/None for location
    categories, which keep today's value-ranking behavior unchanged."""

    def __init__(
        self, kernels: dict[str, TransitionKernel], resense_anchors: Optional[dict[str, str]] = None,
    ) -> None:
        self.kernels = kernels
        self.resense_anchors = resense_anchors or {}
        self.nodes: dict[str, PosteriorObjectNode] = {}
        self.transition_log: list[TransitionRecord] = []

    def _kernel_for(self, category: str) -> Optional[TransitionKernel]:
        return self.kernels.get(category)

    def observe_detection(self, detection: OracleDetection, pose: Pose) -> None:
        kernel = self._kernel_for(detection.category)
        if kernel is None:
            return  # no fitted kernel for this category — nothing to maintain a posterior over
        node = self.nodes.get(detection.label)
        if node is None:
            node = PosteriorObjectNode(
                label=detection.label, category=detection.category, kernel=kernel,
                posterior={s: 0.0 for s in kernel.states}, last_updated_t=detection.t,
            )
            self.nodes[detection.label] = node
        else:
            prior_anchor = self.believed_anchor(detection.label, node.last_updated_t)
            if prior_anchor is not None and prior_anchor != detection.anchor:
                self.transition_log.append(TransitionRecord(
                    label=detection.label, t=detection.t,
                    from_anchor=prior_anchor, to_anchor=detection.anchor,
                ))
        # A positive detection is ground truth for this instant — collapse
        # to a one-hot at the observed anchor regardless of what the
        # propagated posterior said.
        collapsed = {s: 0.0 for s in node.kernel.states}
        collapsed[detection.anchor] = 1.0  # adds a foreign key if not in kernel.states — see module note below
        node.posterior = collapsed
        node.last_updated_t = detection.t
        node.last_update_was_positive = True

    def observe_negative(self, label: str, anchor: str, t: float) -> None:
        """Checked `anchor` for `label`, did not find it there — zero that
        state's posterior mass and renormalize the rest. No-op if nothing
        is believed about this label yet."""
        node = self.nodes.get(label)
        if node is None:
            return
        propagated = node.propagated(t)
        if anchor in propagated:
            propagated[anchor] = 0.0
        total = sum(propagated.values())
        if total > 1e-12:
            propagated = {s: p / total for s, p in propagated.items()}
        else:
            # Every state zeroed — fall back to the kernel's own stationary
            # distribution rather than an undefined all-zero posterior.
            propagated = dict(zip(node.kernel.states, node.kernel.dest_dist))
        node.posterior = propagated
        node.last_updated_t = t
        node.last_update_was_positive = False

    def validity(self, label: str, t: float) -> float:
        """Compatibility view: max posterior mass among non-OUTSIDE states
        at time t. 0.0 if nothing is believed."""
        node = self.nodes.get(label)
        if node is None:
            return 0.0
        posterior = node.propagated(t)
        candidates = {s: p for s, p in posterior.items() if s != OUTSIDE}
        return max(candidates.values()) if candidates else 0.0

    def elapsed_since_update(self, label: str, t: float) -> Optional[float]:
        """Hours since label's last update (positive or negative), or None
        if never observed — see belief.BeliefStore.elapsed_since_update's
        docstring for why DecayThreshold's Mondrian theta mode needs this."""
        node = self.nodes.get(label)
        if node is None:
            return None
        return t - node.last_updated_t

    def believed_anchor(self, label: str, t: Optional[float] = None) -> Optional[str]:
        """Compatibility view: the argmax non-OUTSIDE state. If t is given,
        propagates to t first (so a long enough wait can correctly shift
        the top candidate, or let OUTSIDE dominate so completely that
        nothing qualifies); if t is omitted, uses the posterior as of its
        last update with no further propagation (matches belief.BeliefStore's
        own non-time-aware believed_anchor for callers that don't pass t)."""
        node = self.nodes.get(label)
        if node is None:
            return None
        posterior = node.propagated(t) if t is not None else node.posterior
        candidates = {s: p for s, p in posterior.items() if s != OUTSIDE}
        if not candidates:
            return None
        best_state, best_mass = max(candidates.items(), key=lambda kv: kv[1])
        return best_state if best_mass > 1e-9 else None

    def known_labels(self) -> list[str]:
        return list(self.nodes.keys())

    def top_candidates(self, label: str, t: float, travel_time_to: Callable[[str], float], k: int = 3) -> tuple[str, ...]:
        """Up to k reachable anchor states (never OUTSIDE — not a literal
        navigable target) ranked by posterior-mass-per-travel-second,
        excluding states with negligible propagated mass. The search-
        resensing target list — see policy.py's docstring.

        For a category in resense_anchors (M3: state-change dynamics),
        this returns that one fixed real anchor instead — see this
        class's docstring for why value-ranking is meaningless there."""
        node = self.nodes.get(label)
        if node is None:
            return ()
        resense_anchor = self.resense_anchors.get(node.category)
        if resense_anchor is not None:
            travel_s = travel_time_to(resense_anchor)
            return (resense_anchor,) if math.isfinite(travel_s) else ()

        posterior = node.propagated(t)
        scored: list[tuple[float, str]] = []
        for state, mass in posterior.items():
            if state == OUTSIDE or mass <= 1e-9:
                continue
            travel_s = travel_time_to(state)
            if not math.isfinite(travel_s):
                continue
            travel_s = max(travel_s, 1e-3)  # avoid divide-by-zero for a zero-distance target
            scored.append((mass / travel_s, state))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return tuple(state for _, state in scored[:k])

    # -- integration with EmbodiedWorld -----------------------------------

    def update_from_snapshot(self, snapshot: SenseSnapshot, world: "EmbodiedWorld") -> None:
        from .sensor import is_visible

        detected_labels = {d.label for d in snapshot.detections}
        for detection in snapshot.detections:
            self.observe_detection(detection, snapshot.pose)

        eye_pos = (snapshot.pose.x, snapshot.pose.y + world.config.sensor.eye_height_m, snapshot.pose.z)
        for label, node in list(self.nodes.items()):
            if label in detected_labels:
                continue
            # Every candidate anchor state whose resolved position was
            # actually visible from this pose gets checked, not just the
            # current top belief — a categorical posterior can accumulate
            # negative evidence against several candidates from one
            # vantage point (e.g. two known anchors for this category
            # visible in the same glance).
            for state in node.kernel.states:
                if state == OUTSIDE:
                    continue
                pos = world._resolve_slot_position(label, state)
                if pos is None:
                    continue
                if is_visible(world._sim, eye_pos, snapshot.pose.yaw_rad, pos, world.config.sensor):
                    self.observe_negative(label, state, snapshot.t)

    def update_from_result(self, result, world: "EmbodiedWorld") -> None:
        for snapshot in result.snapshots:
            self.update_from_snapshot(snapshot, world)


# ---------------------------------------------------------------------------
# TimeOfDayBeliefStore — the schedule-only (zero live sensing) baseline
# ---------------------------------------------------------------------------

class TimeOfDayBeliefStore:
    """Pure schedule-based belief: predicts a label's anchor purely from the
    fitted time-of-day-bucketed transition kernel's dest_dist
    (fit_transition_kernels_by_time_of_day) for whichever bucket the query
    time falls in — never updated from real sensing at all. This is the
    tod_prior baseline: how much a fitted schedule alone predicts with zero
    live observation, as the floor a resensing policy must beat to justify
    sensing at all.

    Named for what it actually is — a discrete time-of-day bucket lookup —
    not "FreMEn" (Frequency Map Enhancement), which this class was
    originally (mis)named after despite doing no frequency-domain
    estimation anywhere: no Fourier fit, no periodicity model, just
    n_buckets independent per-bucket kernels (see
    fit_transition_kernels_by_time_of_day). A genuine Fourier-fit FreMEn
    baseline — fitting a small number of dominant frequencies to the
    per-category occupancy signal rather than discrete buckets — is
    deferred to the external-comparisons phase; this class is not it and
    should not be cited as it, hence the rename (was FremenBeliefStore /
    policy label "fremen_predict").

    observe_detection/observe_negative record only a label's category
    (the only way this interface has to learn it) — the observation itself
    never touches the prediction, by design; that's the point of a
    zero-live-sensing floor. So this store is only ever paired with a
    non-resensing policy (AnswerImmediately, as tod_prior) — it has no
    `nodes` attribute (unlike BeliefStore/PosteriorBeliefStore), so a
    search-capable policy that inspects belief.nodes directly (see
    policy._just_resensed/_search_targets) would raise AttributeError
    rather than silently degrade; tod_prior IS AnswerImmediately's
    already-existing decision rule pointed at this store, not a new policy
    class, since the mechanism under test is the belief source, not the
    decision rule.
    """

    def __init__(self, bucketed_kernels: dict[str, tuple[TransitionKernel, ...]], n_buckets: int = 4) -> None:
        self.bucketed_kernels = bucketed_kernels
        self.n_buckets = n_buckets
        self._label_category: dict[str, str] = {}

    def _bucket(self, t: float) -> int:
        bucket_width = 24.0 / self.n_buckets
        return int((t % 24.0) / bucket_width) % self.n_buckets

    def _kernel_for(self, label: str, t: float) -> Optional[TransitionKernel]:
        category = self._label_category.get(label)
        if category is None:
            return None
        kernels = self.bucketed_kernels.get(category)
        if not kernels:
            return None
        return kernels[self._bucket(t)]

    def observe_detection(self, detection: OracleDetection, pose: Pose) -> None:
        self._label_category[detection.label] = detection.category

    def observe_negative(self, label: str, anchor: str, t: float) -> None:
        pass  # the schedule prior ignores negative observations by design

    def believed_anchor(self, label: str, t: Optional[float] = None) -> Optional[str]:
        kernel = self._kernel_for(label, t if t is not None else 0.0)
        if kernel is None:
            return None
        candidates = {s: p for s, p in zip(kernel.states, kernel.dest_dist) if s != OUTSIDE}
        if not candidates:
            return None
        best_state, best_mass = max(candidates.items(), key=lambda kv: kv[1])
        return best_state if best_mass > 1e-9 else None

    def validity(self, label: str, t: float) -> float:
        kernel = self._kernel_for(label, t)
        if kernel is None:
            return 0.0
        candidates = [p for s, p in zip(kernel.states, kernel.dest_dist) if s != OUTSIDE]
        return max(candidates) if candidates else 0.0

    def known_labels(self) -> list[str]:
        return list(self._label_category.keys())

    def top_candidates(self, label: str, t: float, travel_time_to: Callable[[str], float], k: int = 3) -> tuple[str, ...]:
        """Interface parity only — tod_prior (AnswerImmediately) never
        calls this, since it never resenses. Ranked the same way
        PosteriorBeliefStore.top_candidates is, from whichever bucket's
        prior currently applies (there is no observation that could ever
        move this store off that prior)."""
        kernel = self._kernel_for(label, t)
        if kernel is None:
            return ()
        scored: list[tuple[float, str]] = []
        for state, mass in zip(kernel.states, kernel.dest_dist):
            if state == OUTSIDE or mass <= 1e-9:
                continue
            travel_s = travel_time_to(state)
            if not math.isfinite(travel_s):
                continue
            travel_s = max(travel_s, 1e-3)
            scored.append((mass / travel_s, state))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return tuple(state for _, state in scored[:k])

    def update_from_snapshot(self, snapshot: SenseSnapshot, world: "EmbodiedWorld") -> None:
        for detection in snapshot.detections:
            self.observe_detection(detection, snapshot.pose)

    def update_from_result(self, result, world: "EmbodiedWorld") -> None:
        for snapshot in result.snapshots:
            self.update_from_snapshot(snapshot, world)
