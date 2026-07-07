"""
Tests for embodied/posterior.py's TransitionKernel, fit_transition_kernels,
and PosteriorBeliefStore's pure-belief-math surface (no habitat_sim needed
— only update_from_snapshot/update_from_result touch a real EmbodiedWorld;
see test_posterior_discovery.py for that end-to-end path).

Required by the M2 phase spec: kernel row-sum-to-1, convergence to
stationary distribution, backoff test (zero-event category gets exactly
the pooled kernel).
"""
from __future__ import annotations

import math

import pytest

from dynamic_home_eqa.embodied.posterior import (
    OUTSIDE,
    HierarchicalStat,
    PosteriorBeliefStore,
    TransitionKernel,
    fit_state_transition_kernels,
    fit_transition_kernels,
    shrink_hierarchical,
    shrink_hierarchical_with_llm,
)
from dynamic_home_eqa.embodied.types import OracleDetection, Pose


def _make_kernel(states=("a", "b", OUTSIDE), lam=0.5, dest=(0.5, 0.3, 0.2)) -> TransitionKernel:
    return TransitionKernel(category="test", states=states, lambda_per_hour=lam, dest_dist=dest)


# ---------------------------------------------------------------------------
# Kernel correctness (required tests)
# ---------------------------------------------------------------------------

def test_matrix_rows_sum_to_one():
    kernel = _make_kernel()
    matrix = kernel.matrix_at(0.25)
    for row in matrix:
        assert abs(sum(row) - 1.0) < 1e-9


def test_matrix_rows_sum_to_one_for_various_step_sizes():
    kernel = _make_kernel()
    for step in (0.01, 0.25, 1.0, 5.0, 24.0):
        matrix = kernel.matrix_at(step)
        for row in matrix:
            assert abs(sum(row) - 1.0) < 1e-9


def test_convergence_to_stationary_distribution_via_matrix_power():
    kernel = _make_kernel()
    matrix = kernel.matrix_at(0.25)
    n = len(kernel.states)

    # Iterate the discrete 0.25h-step matrix many times (matrix power) —
    # should converge to dest_dist regardless of starting row.
    power = [row[:] for row in matrix]
    for _ in range(200):
        power = [
            [sum(power[i][k] * matrix[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)
        ]
    for i in range(n):
        for j in range(n):
            assert abs(power[i][j] - kernel.dest_dist[j]) < 1e-6


def test_convergence_to_stationary_distribution_via_propagate():
    kernel = _make_kernel()
    posterior = {"a": 1.0, "b": 0.0, OUTSIDE: 0.0}
    converged = kernel.propagate(posterior, elapsed_hours=1000.0)
    for state, expected in kernel.stationary_distribution().items():
        assert abs(converged[state] - expected) < 1e-6


def test_propagate_matches_repeated_0_25h_matrix_application():
    """propagate()'s closed form must agree with actually iterating the
    explicit 0.25h-step matrix (see module docstring's derivation)."""
    kernel = _make_kernel()
    matrix = kernel.matrix_at(0.25)
    states = kernel.states
    n = len(states)

    posterior = {"a": 0.7, "b": 0.2, OUTSIDE: 0.1}
    row = [posterior[s] for s in states]
    for _ in range(8):  # 8 steps of 0.25h = 2.0h
        row = [sum(row[i] * matrix[i][j] for i in range(n)) for j in range(n)]

    closed_form = kernel.propagate(posterior, elapsed_hours=2.0)
    for j, s in enumerate(states):
        assert abs(row[j] - closed_form[s]) < 1e-9


def test_propagate_preserves_total_probability():
    kernel = _make_kernel()
    posterior = {"a": 0.6, "b": 0.1, OUTSIDE: 0.3}
    for elapsed in (0.0, 0.1, 1.0, 10.0):
        propagated = kernel.propagate(posterior, elapsed)
        assert abs(sum(propagated.values()) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Hierarchical backoff (required test)
# ---------------------------------------------------------------------------

def _stats(location_changes, mean_dwell_hours):
    return {"location_changes": location_changes, "mean_dwell_hours": mean_dwell_hours}


def test_zero_event_category_gets_exactly_the_pooled_kernel():
    train_manifests = [{"changes": [
        {"object_category": "book", "to_semantic": "living_room.shelf", "t": 1.0},
        {"object_category": "book", "to_semantic": "office.desk", "t": 5.0},
        {"object_category": "cup", "to_semantic": "kitchen.counter", "t": 2.0},
    ]}]
    category_stats = {
        "book": _stats(location_changes=10, mean_dwell_hours=4.0),
        "cup": _stats(location_changes=5, mean_dwell_hours=2.0),
        # "vase" has anchor history (some other day/scene knows of a vase
        # anchor) but zero events in these particular train_manifests.
    }
    anchor_history = {
        "book": {"living_room.shelf", "office.desk"},
        "cup": {"kitchen.counter"},
        "vase": {"dining.table"},
    }

    kernels = fit_transition_kernels(train_manifests, category_stats, anchor_history, prior_strength=3.0)

    # Build the pooled kernel independently (own_weight=0 case) to compare against.
    zero_stats = {**category_stats}  # "vase" absent -> location_changes defaults to 0
    pooled_only = fit_transition_kernels(
        train_manifests, category_stats, {"vase": anchor_history["vase"]}, prior_strength=3.0,
    )["vase"]

    vase_kernel = kernels["vase"]
    assert vase_kernel.lambda_per_hour == pytest.approx(pooled_only.lambda_per_hour)
    assert vase_kernel.dest_dist == pytest.approx(pooled_only.dest_dist)


# ---------------------------------------------------------------------------
# shrink_hierarchical (D1: kernel generalization — scene -> profile -> global)
# ---------------------------------------------------------------------------

def test_zero_weight_scene_falls_back_exactly_to_profile():
    scene = HierarchicalStat(value=999.0, weight=0.0)  # value irrelevant at weight=0
    profile = HierarchicalStat(value=0.4, weight=5.0)
    global_ = HierarchicalStat(value=0.9, weight=100.0)
    result = shrink_hierarchical(scene, profile, global_, prior_strength=3.0)
    expected_profile_backed_off = (5.0 * 0.4 + 3.0 * 0.9) / (5.0 + 3.0)
    assert result == pytest.approx(expected_profile_backed_off)


def test_zero_weight_scene_and_profile_falls_back_exactly_to_global():
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=0.7, weight=50.0)
    result = shrink_hierarchical(scene, profile, global_, prior_strength=3.0)
    assert result == pytest.approx(0.7)


def test_scene_with_strong_weight_stays_close_to_its_own_value():
    scene = HierarchicalStat(value=0.1, weight=1000.0)
    profile = HierarchicalStat(value=0.9, weight=5.0)
    global_ = HierarchicalStat(value=0.5, weight=50.0)
    result = shrink_hierarchical(scene, profile, global_, prior_strength=3.0)
    assert result == pytest.approx(0.1, abs=0.01)


def test_shrink_hierarchical_matches_two_nested_shrink_calls():
    from dynamic_home_eqa.embodied.posterior import _shrink

    scene = HierarchicalStat(value=0.2, weight=4.0)
    profile = HierarchicalStat(value=0.5, weight=8.0)
    global_ = HierarchicalStat(value=0.8, weight=200.0)
    prior_strength = 2.5

    expected_profile = _shrink(profile.value, global_.value, profile.weight, prior_strength)
    expected = _shrink(scene.value, expected_profile, scene.weight, prior_strength)
    assert shrink_hierarchical(scene, profile, global_, prior_strength) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# shrink_hierarchical_with_llm (L1 T1: LLM as the 4th, bottom backoff level)
# ---------------------------------------------------------------------------

def test_zero_concentration_is_the_do_no_harm_floor():
    """concentration=0 (llm.weight=0) must make this function IDENTICAL
    to shrink_hierarchical on a cell with real data at every other level
    — a concentration=0 LLM prior is mathematically inert, not merely
    small. This is T1's own required do-no-harm property, tested here
    directly rather than only inferred from T2's later ablation."""
    scene = HierarchicalStat(value=0.2, weight=4.0)
    profile = HierarchicalStat(value=0.5, weight=8.0)
    global_ = HierarchicalStat(value=0.8, weight=200.0)
    llm = HierarchicalStat(value=0.99, weight=0.0)  # value irrelevant at weight=0
    prior_strength = 3.0

    with_llm = shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength)
    without_llm = shrink_hierarchical(scene, profile, global_, prior_strength)
    assert with_llm == pytest.approx(without_llm)


def test_zero_global_weight_falls_back_exactly_to_llm_value():
    """The zero-data limit: a category with no real events anywhere in
    the pool (global.weight=0) must back off to EXACTLY the LLM's
    elicited value — not blended with anything else — for any positive
    concentration."""
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=999.0, weight=0.0)
    llm = HierarchicalStat(value=0.63, weight=5.0)
    result = shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength=3.0)
    assert result == pytest.approx(0.63)


def test_zero_global_weight_limit_holds_at_any_positive_concentration():
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=999.0, weight=0.0)
    llm = HierarchicalStat(value=0.4, weight=500.0)  # high concentration, same limit
    result = shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength=3.0)
    assert result == pytest.approx(0.4)


def test_higher_concentration_pulls_the_backed_off_value_closer_to_llm():
    """Not an exact limit (global.weight > 0 here) — concentration
    controls how fast real data overrides the LLM prior, so a higher
    concentration should monotonically pull the global-level result
    closer to llm.value, never further from it."""
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=0.1, weight=10.0)
    llm_value = 0.9

    low = shrink_hierarchical_with_llm(scene, profile, global_, HierarchicalStat(llm_value, weight=1.0))
    mid = shrink_hierarchical_with_llm(scene, profile, global_, HierarchicalStat(llm_value, weight=10.0))
    high = shrink_hierarchical_with_llm(scene, profile, global_, HierarchicalStat(llm_value, weight=1000.0))

    assert global_.value < low < mid < high < llm_value + 1e-9
    assert high == pytest.approx(llm_value, abs=0.02)  # near-total override at high concentration


def test_strong_global_weight_stays_close_to_its_own_value_regardless_of_llm():
    """The other half of do-no-harm: even a high-concentration LLM prior
    must not meaningfully move a cell where global already has abundant
    real data — this is what T2's ablation checks at the belief-store
    level; this is the same property checked directly on the backoff
    math alone."""
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=0.7, weight=5000.0)
    llm = HierarchicalStat(value=0.1, weight=50.0)
    result = shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength=3.0)
    assert result == pytest.approx(0.7, abs=0.01)


def test_matches_shrink_hierarchical_with_llm_backed_off_global_substituted():
    from dynamic_home_eqa.embodied.posterior import _shrink

    scene = HierarchicalStat(value=0.2, weight=4.0)
    profile = HierarchicalStat(value=0.5, weight=8.0)
    global_ = HierarchicalStat(value=0.8, weight=20.0)
    llm = HierarchicalStat(value=0.3, weight=15.0)
    prior_strength = 2.5

    global_backed_off = _shrink(global_.value, llm.value, global_.weight, llm.weight)
    expected_profile = _shrink(profile.value, global_backed_off, profile.weight, prior_strength)
    expected = _shrink(scene.value, expected_profile, scene.weight, prior_strength)
    assert shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength) == pytest.approx(expected)


def test_both_global_and_llm_weight_zero_raises_rather_than_silently_guessing():
    """A cell with no real data anywhere AND no LLM prior configured has
    nothing to base an estimate on — this must fail loudly (guards
    fatal), not return an arbitrary or NaN value."""
    scene = HierarchicalStat(value=999.0, weight=0.0)
    profile = HierarchicalStat(value=999.0, weight=0.0)
    global_ = HierarchicalStat(value=999.0, weight=0.0)
    llm = HierarchicalStat(value=999.0, weight=0.0)
    with pytest.raises(ZeroDivisionError):
        shrink_hierarchical_with_llm(scene, profile, global_, llm, prior_strength=3.0)


def test_category_with_more_events_shrinks_less_toward_pooled():
    """A category with many observed events should end up closer to its
    own empirical lambda than a category with few, both starting from the
    same own_lambda but different weights."""
    from dynamic_home_eqa.embodied.posterior import _pooled_lambda, _shrink

    pooled = 0.1
    own = 0.9
    shrunk_few = _shrink(own, pooled, own_weight=1, prior_strength=3.0)
    shrunk_many = _shrink(own, pooled, own_weight=100, prior_strength=3.0)
    assert abs(shrunk_many - own) < abs(shrunk_few - own)
    assert abs(shrunk_few - pooled) < abs(shrunk_many - pooled)


# ---------------------------------------------------------------------------
# PosteriorBeliefStore pure-belief-math (no habitat_sim)
# ---------------------------------------------------------------------------

def _store_with_kernel(kernel: TransitionKernel) -> PosteriorBeliefStore:
    return PosteriorBeliefStore(kernels={kernel.category: kernel})


def test_positive_observation_collapses_posterior_to_one_hot():
    kernel = _make_kernel(states=("a", "b", OUTSIDE))
    store = _store_with_kernel(kernel)
    detection = OracleDetection(label="obj_1", category="test", world_pos=(0, 0, 0), anchor="a", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))

    assert store.believed_anchor("obj_1", 1.0) == "a"
    assert store.validity("obj_1", 1.0) == pytest.approx(1.0)


def test_negative_observation_zeroes_and_renormalizes():
    kernel = _make_kernel(states=("a", "b", OUTSIDE), lam=0.0, dest=(0.5, 0.3, 0.2))
    store = _store_with_kernel(kernel)
    detection = OracleDetection(label="obj_1", category="test", world_pos=(0, 0, 0), anchor="a", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))
    # Force a mixed posterior (bypassing the one-hot collapse a positive
    # detection produces) to exercise the ordinary zero-and-renormalize
    # path, not the "every state already zero" degenerate fallback below.
    store.nodes["obj_1"].posterior = {"a": 0.5, "b": 0.3, OUTSIDE: 0.2}
    store.nodes["obj_1"].last_updated_t = 1.0

    store.observe_negative("obj_1", "a", t=1.0)
    node = store.nodes["obj_1"]
    assert node.posterior["a"] == 0.0
    assert abs(sum(node.posterior.values()) - 1.0) < 1e-9
    # b and OUTSIDE keep their relative proportion (0.3 : 0.2).
    assert node.posterior["b"] == pytest.approx(0.3 / 0.5)
    assert node.posterior[OUTSIDE] == pytest.approx(0.2 / 0.5)
    assert node.last_update_was_positive is False


def test_negative_observation_falls_back_to_stationary_dist_when_everything_zeroed():
    """If a negative observation would zero out the entire posterior (only
    possible when nothing else had any mass), fall back to the kernel's
    own stationary distribution rather than leaving an undefined all-zero
    posterior."""
    kernel = _make_kernel(states=("a", "b", OUTSIDE), lam=0.0, dest=(0.5, 0.3, 0.2))
    store = _store_with_kernel(kernel)
    detection = OracleDetection(label="obj_1", category="test", world_pos=(0, 0, 0), anchor="a", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))  # posterior = {a:1, b:0, OUTSIDE:0}

    store.observe_negative("obj_1", "a", t=1.0)
    node = store.nodes["obj_1"]
    assert node.posterior == pytest.approx({"a": 0.5, "b": 0.3, OUTSIDE: 0.2})


def test_top_candidates_excludes_outside_and_zero_mass_and_ranks_by_value_density():
    kernel = _make_kernel(states=("a", "b", OUTSIDE), lam=0.0, dest=(0.0, 0.0, 1.0))
    store = _store_with_kernel(kernel)
    detection = OracleDetection(label="obj_1", category="test", world_pos=(0, 0, 0), anchor="a", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))
    # Force a mixed posterior via a synthetic node edit (bypassing the
    # observation API) to test ranking directly.
    store.nodes["obj_1"].posterior = {"a": 0.6, "b": 0.4, OUTSIDE: 0.0}

    travel_cost = {"a": 10.0, "b": 1.0}.get
    top = store.top_candidates("obj_1", 1.0, travel_time_to=travel_cost, k=3)
    # b has lower mass but much lower travel cost -> higher value density.
    assert top[0] == "b"
    assert OUTSIDE not in top


def test_top_candidates_empty_when_nothing_believed():
    kernel = _make_kernel()
    store = _store_with_kernel(kernel)
    assert store.top_candidates("never_seen", 1.0, travel_time_to=lambda a: 1.0) == ()


# ---------------------------------------------------------------------------
# fit_state_transition_kernels (M3: state-change dynamics)
# ---------------------------------------------------------------------------

def _state_change(t, category, variable, to_state):
    return {
        "t": t, "label": f"{category}_1", "change_type": "state_change",
        "object_category": category, "state_variable": variable, "to_state": to_state,
    }


def test_state_kernel_has_no_outside_state():
    train_manifests = [{"changes": [_state_change(1.0, "tv", "power", "powered")]}]
    stats = {"tv::power": {"location_changes": 1, "mean_dwell_hours": 2.0}}
    domains = {"tv::power": ("unpowered", "powered")}
    kernels = fit_state_transition_kernels(train_manifests, stats, domains)
    assert OUTSIDE not in kernels["tv::power"].states
    assert kernels["tv::power"].states == ("unpowered", "powered")


def test_state_kernel_dest_dist_sums_to_one():
    train_manifests = [{"changes": [
        _state_change(1.0, "tv", "power", "powered"),
        _state_change(2.0, "tv", "power", "unpowered"),
        _state_change(3.0, "tv", "power", "powered"),
    ]}]
    stats = {"tv::power": {"location_changes": 3, "mean_dwell_hours": 1.0}}
    domains = {"tv::power": ("unpowered", "powered")}
    kernels = fit_state_transition_kernels(train_manifests, stats, domains)
    assert abs(sum(kernels["tv::power"].dest_dist) - 1.0) < 1e-9


def test_state_kernel_dest_dist_reflects_observed_value_skew():
    # "powered" appears 3x as often as "unpowered" in the training data.
    train_manifests = [{"changes": [
        _state_change(t, "tv", "power", "powered") for t in range(6)
    ] + [_state_change(6.0, "tv", "power", "unpowered")]}]
    stats = {"tv::power": {"location_changes": 7, "mean_dwell_hours": 1.0}}
    domains = {"tv::power": ("unpowered", "powered")}
    kernels = fit_state_transition_kernels(train_manifests, stats, domains, prior_strength=0.1)
    dest = dict(zip(kernels["tv::power"].states, kernels["tv::power"].dest_dist))
    assert dest["powered"] > dest["unpowered"]


def test_zero_event_state_variable_gets_exactly_the_pooled_kernel():
    train_manifests = [{"changes": [
        _state_change(1.0, "tv", "power", "powered"),
        _state_change(2.0, "tv", "power", "unpowered"),
    ]}]
    stats = {"tv::power": {"location_changes": 2, "mean_dwell_hours": 1.0}}
    domains = {"tv::power": ("unpowered", "powered"), "fridge::door": ("closed", "open")}
    # "fridge::door" has zero events in train_manifests and zero own_weight
    # in stats (absent -> defaults to 0) -> must collapse to the pooled kernel.
    kernels = fit_state_transition_kernels(train_manifests, stats, domains, prior_strength=3.0)
    pooled_only = fit_state_transition_kernels(
        train_manifests, stats, {"fridge::door": domains["fridge::door"]}, prior_strength=3.0,
    )["fridge::door"]
    assert kernels["fridge::door"].lambda_per_hour == pytest.approx(pooled_only.lambda_per_hour)
    assert kernels["fridge::door"].dest_dist == pytest.approx(pooled_only.dest_dist)


def test_top_candidates_routes_to_resense_anchor_for_state_categories():
    kernel = TransitionKernel(category="fridge::door", states=("closed", "open"),
                               lambda_per_hour=0.5, dest_dist=(0.5, 0.5))
    store = PosteriorBeliefStore({"fridge::door": kernel}, resense_anchors={"fridge::door": "fridge"})
    detection = OracleDetection(label="fridge_1::door", category="fridge::door",
                                 world_pos=(0, 0, 0), anchor="closed", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))

    # travel_time_to would return inf for "open"/"closed" (not real places)
    # but must resolve for "fridge" (the resense anchor) — confirms
    # top_candidates never tries to rank the value labels as targets.
    travel_time_to = {"fridge": 5.0}.get
    top = store.top_candidates("fridge_1::door", 1.0, travel_time_to=lambda a: travel_time_to(a) or float("inf"))
    assert top == ("fridge",)


def test_top_candidates_resense_anchor_empty_when_unreachable():
    kernel = TransitionKernel(category="fridge::door", states=("closed", "open"),
                               lambda_per_hour=0.5, dest_dist=(0.5, 0.5))
    store = PosteriorBeliefStore({"fridge::door": kernel}, resense_anchors={"fridge::door": "fridge"})
    detection = OracleDetection(label="fridge_1::door", category="fridge::door",
                                 world_pos=(0, 0, 0), anchor="closed", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))
    top = store.top_candidates("fridge_1::door", 1.0, travel_time_to=lambda a: float("inf"))
    assert top == ()


def test_top_candidates_without_resense_anchors_is_unaffected():
    # Default (no resense_anchors) must behave exactly as before this fix.
    kernel = _make_kernel(states=("a", "b", OUTSIDE), lam=0.0, dest=(0.0, 0.0, 1.0))
    store = _store_with_kernel(kernel)
    detection = OracleDetection(label="obj_1", category="test", world_pos=(0, 0, 0), anchor="a", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))
    store.nodes["obj_1"].posterior = {"a": 0.6, "b": 0.4, OUTSIDE: 0.0}
    top = store.top_candidates("obj_1", 1.0, travel_time_to={"a": 10.0, "b": 1.0}.get, k=3)
    assert top[0] == "b"


def test_state_kernel_usable_by_posterior_belief_store():
    train_manifests = [{"changes": [_state_change(1.0, "tv", "power", "powered")]}]
    stats = {"tv::power": {"location_changes": 1, "mean_dwell_hours": 2.0}}
    domains = {"tv::power": ("unpowered", "powered")}
    kernels = fit_state_transition_kernels(train_manifests, stats, domains)
    store = PosteriorBeliefStore(kernels)
    detection = OracleDetection(label="tv_1::power", category="tv::power",
                                 world_pos=(0, 0, 0), anchor="powered", t=1.0)
    store.observe_detection(detection, Pose(0, 0, 0, 0))
    assert store.believed_anchor("tv_1::power", 1.0) == "powered"
