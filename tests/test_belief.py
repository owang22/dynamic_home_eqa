"""
M2 tests: BeliefStore, DecayModel, and the negative-observation integration
with EmbodiedWorld. Pure-logic tests run anywhere; the integration tests
that construct a real EmbodiedWorld need habitat_sim and are individually
skipped (not the whole module) when it's unavailable.
"""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from dynamic_home_eqa.embodied.belief import (
    BeliefStore,
    DecayModel,
    ObjectNode,
    aggregate_category_stats,
    calibrate_conformal_theta,
    calibrate_conformal_theta_by_wait,
    fit_decay_models,
)
from dynamic_home_eqa.embodied.posterior import OUTSIDE, TransitionKernel
from dynamic_home_eqa.embodied.types import OracleDetection, Pose

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"
_REAL_SCENE = "102343992"


def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


_needs_habitat_sim = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)

_POSE = Pose(0.0, 0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# DecayModel
# ---------------------------------------------------------------------------

def test_decay_model_validity_is_one_at_zero_elapsed():
    model = DecayModel("book", lambda_per_hour=0.5)
    assert model.validity(0.0) == 1.0


def test_decay_model_validity_decreases_with_elapsed_time():
    model = DecayModel("book", lambda_per_hour=0.5)
    assert model.validity(1.0) > model.validity(5.0) > model.validity(20.0)


def test_decay_model_validity_never_negative_for_negative_elapsed():
    model = DecayModel("book", lambda_per_hour=0.5)
    assert model.validity(-5.0) == 1.0  # clamped, not extrapolated backward


def test_fit_decay_models_uses_inverse_mean_dwell():
    stats = {"book": {"location_changes": 4, "distinct_slots_visited": 3, "mean_dwell_hours": 2.0}}
    models = fit_decay_models(stats)
    assert models["book"].lambda_per_hour == pytest.approx(0.5)


def test_fit_decay_models_falls_back_when_no_dwell_data():
    from dynamic_home_eqa.embodied.belief import DEFAULT_LAMBDA_PER_HOUR
    stats = {"vase": {"location_changes": 1, "distinct_slots_visited": 1, "mean_dwell_hours": None}}
    models = fit_decay_models(stats)
    assert models["vase"].lambda_per_hour == DEFAULT_LAMBDA_PER_HOUR


def test_aggregate_category_stats_weights_by_location_changes():
    day1 = {"book": {"location_changes": 8, "distinct_slots_visited": 3, "mean_dwell_hours": 1.0}}
    day2 = {"book": {"location_changes": 2, "distinct_slots_visited": 2, "mean_dwell_hours": 5.0}}
    merged = aggregate_category_stats([day1, day2])
    # weighted mean: (8*1.0 + 2*5.0) / 10 = 1.8
    assert merged["book"]["mean_dwell_hours"] == pytest.approx(1.8)
    assert merged["book"]["location_changes"] == 10


def test_aggregate_category_stats_ignores_none_dwell_in_weighting():
    day1 = {"book": {"location_changes": 1, "distinct_slots_visited": 1, "mean_dwell_hours": None}}
    day2 = {"book": {"location_changes": 4, "distinct_slots_visited": 2, "mean_dwell_hours": 2.0}}
    merged = aggregate_category_stats([day1, day2])
    assert merged["book"]["mean_dwell_hours"] == pytest.approx(2.0)
    assert merged["book"]["location_changes"] == 5


# ---------------------------------------------------------------------------
# calibrate_conformal_theta (M4 pre-suite: conformal-threshold baseline)
# ---------------------------------------------------------------------------

def _change(t, label, cat, to_semantic="x"):
    return {"t": t, "label": label, "object_category": cat, "to_semantic": to_semantic}


def _single_state_kernel(category="book", lambda_per_hour=0.5):
    """A TransitionKernel whose dest_dist puts all stationary mass on
    OUTSIDE and none on the observed state "x" — under this kernel,
    propagate({"x": 1.0}, dwell)["x"] = exp(-lambda*dwell) exactly, so
    _posterior_validity_at_dwell reduces to the same exponential curve
    DecayModel.validity used to compute directly. This lets these tests
    assert against that same closed form while genuinely exercising the
    TransitionKernel-based calibration path (see calibrate_conformal_
    theta's docstring for why calibration must use kernels, not
    DecayModel, now)."""
    return TransitionKernel(category=category, states=("x", OUTSIDE), lambda_per_hour=lambda_per_hour, dest_dist=(0.0, 1.0))


def test_conformal_theta_achieves_target_coverage_on_calibration_set():
    # 20 dwell events at exactly 2.0h for "book" (lambda=0.5) -> every
    # nonconformity score is identical (exp(-1.0)) — coverage at that exact
    # theta must be 100%, trivially >= any 1-alpha target.
    kernel = _single_state_kernel("book", lambda_per_hour=0.5)
    kernels = {"book": kernel}
    changes = []
    t = 0.0
    for i in range(20):
        changes.append(_change(t, "book_1", "book"))
        t += 2.0
    train_manifests = [{"changes": changes}]

    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.1)
    scores = [math.exp(-0.5 * 2.0)] * 19  # 19 gaps from 20 events
    coverage = sum(1 for s in scores if s >= theta) / len(scores)
    assert coverage >= 0.9


def test_conformal_theta_is_the_alpha_quantile_of_nonconformity_scores():
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=1.0)}
    # Cumulative timestamps 0,1,3,6,...  -> consecutive gaps 1,2,3,...,10h,
    # 10 distinct dwell times -> 10 distinct nonconformity scores.
    dwells = list(range(1, 11))
    ts = [0.0]
    for d in dwells:
        ts.append(ts[-1] + d)
    changes = [_change(t, "book_1", "book") for t in ts]
    train_manifests = [{"changes": changes}]

    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.2)
    scores = sorted(math.exp(-1.0 * dwell) for dwell in dwells)
    # alpha=0.2, n=10 -> idx = ceil(0.2*10)-1 = 1 (0-indexed 2nd-smallest score).
    assert theta == pytest.approx(scores[1])


def test_conformal_theta_ignores_categories_without_a_fitted_kernel():
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=0.5)}
    changes = [
        _change(0.0, "book_1", "book"), _change(2.0, "book_1", "book"),
        _change(0.0, "vase_1", "vase"), _change(1.0, "vase_1", "vase"),  # "vase" uncalibrated
    ]
    train_manifests = [{"changes": changes}]
    # Should not raise (KeyError) despite "vase" having no fitted kernel.
    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.1)
    assert 0.0 <= theta <= 1.0


def test_conformal_theta_falls_back_with_insufficient_calibration_data():
    from dynamic_home_eqa.embodied.policy import DecayThresholdConfig
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=0.5)}
    train_manifests = [{"changes": [_change(0.0, "book_1", "book")]}]  # 1 event -> 0 gaps
    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.1)
    assert theta == DecayThresholdConfig().theta


def test_conformal_theta_uses_posterior_space_not_decay_model_space():
    """The regression test for the space-mismatch bug itself: a kernel
    whose stationary distribution keeps most of its mass on the observed
    state (unlike _single_state_kernel's all-mass-on-OUTSIDE fixture)
    must calibrate a theta well above what DecayModel.validity's plain
    exp(-lambda*dwell) would have produced for the same lambda — proof
    calibration is genuinely reading the kernel's dest_dist, not silently
    falling back to a DecayModel-equivalent curve."""
    sticky_kernel = TransitionKernel(
        category="wardrobe", states=("closed", "open"), lambda_per_hour=1.5, dest_dist=(0.85, 0.15),
    )
    kernels = {"wardrobe": sticky_kernel}
    changes = [
        _change(0.0, "wardrobe_1", "wardrobe", to_semantic="closed"),
        _change(1.0, "wardrobe_1", "wardrobe", to_semantic="closed"),
    ]
    train_manifests = [{"changes": changes}]

    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.1)
    naive_decay_model_theta = math.exp(-1.5 * 1.0)
    assert theta > naive_decay_model_theta


# ---------------------------------------------------------------------------
# calibrate_conformal_theta_by_wait (coverage-repair phase: Mondrian fix)
# ---------------------------------------------------------------------------

def test_by_wait_scores_at_the_buckets_own_wait_not_each_events_natural_dwell():
    # Every event shares the same (category, start_state) pair, so its
    # score is entirely determined by (kernel, w) — deliberately varying
    # and mostly SHORT natural dwells (0.1-0.3h) to prove the bucket's
    # theta at w=4.0 reflects validity AT elapsed=4.0h, not at these
    # events' own (much shorter) dwell times. An earlier, incorrect
    # version of this function scored events at their own dwell and
    # would have produced a theta near exp(-lambda*0.2), not exp(-lambda*4.0).
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=1.0)}
    changes = []
    t = 0.0
    for dwell in (0.1, 0.15, 0.2, 0.25, 0.3, 0.12, 0.18, 0.22, 0.28, 0.14):
        changes += [_change(t, "book_1", "book"), _change(t + dwell, "book_1", "book")]
        t += dwell + 0.01

    train_manifests = [{"changes": changes}]
    thetas = calibrate_conformal_theta_by_wait(train_manifests, kernels, wait_buckets=(0.25, 4.0), alpha=0.1)

    assert thetas[0.25] == pytest.approx(math.exp(-1.0 * 0.25), abs=1e-6)
    assert thetas[4.0] == pytest.approx(math.exp(-1.0 * 4.0), abs=1e-6)
    assert thetas[0.25] > thetas[4.0]


def test_by_wait_quantile_reflects_multiple_distinct_categories():
    # Two categories with different lambdas both contribute events; at a
    # fixed wait_hours, each category's score is a distinct constant
    # (score depends only on kernel+state+w — see the function's own
    # docstring), so the bucket's theta must be one of exactly those two
    # values, not some independently-derived number.
    fast = _single_state_kernel("fast_cat", lambda_per_hour=4.0)   # decays quickly
    slow = _single_state_kernel("slow_cat", lambda_per_hour=0.1)   # decays slowly
    kernels = {"fast_cat": fast, "slow_cat": slow}
    changes = [
        _change(0.0, "fast_1", "fast_cat"), _change(1.0, "fast_1", "fast_cat"),
        _change(0.0, "slow_1", "slow_cat"), _change(1.0, "slow_1", "slow_cat"),
    ]
    train_manifests = [{"changes": changes}]

    w = 2.0
    thetas = calibrate_conformal_theta_by_wait(train_manifests, kernels, wait_buckets=(w,), alpha=0.1)
    fast_score = math.exp(-4.0 * w)
    slow_score = math.exp(-0.1 * w)
    assert thetas[w] == pytest.approx(min(fast_score, slow_score))  # alpha=0.1, n=2 -> the smaller score


def test_by_wait_falls_back_to_global_theta_with_insufficient_calibration_data():
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=0.5)}
    train_manifests = [{"changes": [_change(0.0, "book_1", "book")]}]  # 1 event -> 0 gaps
    thetas = calibrate_conformal_theta_by_wait(train_manifests, kernels, wait_buckets=(1.0, 4.0), alpha=0.1)
    global_theta = calibrate_conformal_theta(train_manifests, kernels, alpha=0.1)
    assert thetas[1.0] == pytest.approx(global_theta)
    assert thetas[4.0] == pytest.approx(global_theta)


def test_by_wait_returns_one_theta_per_requested_bucket():
    kernels = {"book": _single_state_kernel("book", lambda_per_hour=0.5)}
    changes = [_change(0.0, "book_1", "book"), _change(1.0, "book_1", "book")]
    train_manifests = [{"changes": changes}]
    thetas = calibrate_conformal_theta_by_wait(train_manifests, kernels, wait_buckets=(0.25, 0.5, 1.0, 2.0, 4.0), alpha=0.1)
    assert set(thetas.keys()) == {0.25, 0.5, 1.0, 2.0, 4.0}


# ---------------------------------------------------------------------------
# BeliefStore — pure logic (no world/habitat_sim)
# ---------------------------------------------------------------------------

def _detection(label="book_1", category="book", anchor="shelf", t=1.0):
    return OracleDetection(label=label, category=category, world_pos=(0.0, 0.0, 0.0), anchor=anchor, t=t)


def test_observe_detection_creates_a_node():
    store = BeliefStore(decay_models={})
    store.observe_detection(_detection(), _POSE)
    assert store.believed_anchor("book_1") == "shelf"


def test_observe_detection_logs_transition_on_anchor_change():
    store = BeliefStore(decay_models={})
    store.observe_detection(_detection(anchor="shelf", t=1.0), _POSE)
    store.observe_detection(_detection(anchor="table", t=5.0), _POSE)
    assert len(store.transition_log) == 1
    assert store.transition_log[0].from_anchor == "shelf"
    assert store.transition_log[0].to_anchor == "table"


def test_observe_detection_no_transition_when_anchor_unchanged():
    store = BeliefStore(decay_models={})
    store.observe_detection(_detection(anchor="shelf", t=1.0), _POSE)
    store.observe_detection(_detection(anchor="shelf", t=5.0), _POSE)
    assert len(store.transition_log) == 0


def test_validity_is_zero_for_unknown_label():
    store = BeliefStore(decay_models={})
    assert store.validity("nonexistent", t=10.0) == 0.0


def test_validity_decays_from_last_observation_time():
    store = BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=1.0)})
    store.observe_detection(_detection(t=1.0), _POSE)
    v_soon = store.validity("book_1", t=1.5)
    v_later = store.validity("book_1", t=10.0)
    assert 1.0 > v_soon > v_later > 0.0


def test_observe_negative_marks_displaced_and_zeroes_validity():
    store = BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=0.1)})
    store.observe_detection(_detection(t=1.0), _POSE)
    assert store.validity("book_1", t=1.1) > 0.0

    store.observe_negative("book_1", t=2.0)
    assert store.validity("book_1", t=2.0) == 0.0
    assert store.believed_anchor("book_1") is None


def test_positive_detection_after_negative_uneffaces_displaced_flag():
    store = BeliefStore(decay_models={})
    store.observe_detection(_detection(anchor="shelf", t=1.0), _POSE)
    store.observe_negative("book_1", t=2.0)
    assert store.believed_anchor("book_1") is None

    store.observe_detection(_detection(anchor="table", t=3.0), _POSE)
    assert store.believed_anchor("book_1") == "table"


def test_observe_negative_on_unknown_label_is_a_noop():
    store = BeliefStore(decay_models={})
    store.observe_negative("nonexistent", t=5.0)  # must not raise
    assert store.known_labels() == []


def test_known_labels_lists_every_observed_label():
    store = BeliefStore(decay_models={})
    store.observe_detection(_detection(label="book_1"), _POSE)
    store.observe_detection(_detection(label="cup_1", category="cup"), _POSE)
    assert set(store.known_labels()) == {"book_1", "cup_1"}


# ---------------------------------------------------------------------------
# Integration with EmbodiedWorld: patrol population + negative observation
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_day():
    result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    return result, manifest


@pytest.fixture
def world(real_day):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    result, manifest = real_day
    w = EmbodiedWorld(_REAL_SCENE, result, manifest)
    yield w
    w.close()


@_needs_habitat_sim
def test_patrol_populates_beliefs_for_visible_instances(world):
    # Uses the production QuestionEpisodeRunner.patrol(), not a hand-rolled
    # room loop — this scene's navmesh is split across several disconnected
    # islands (confirmed: a multi-story house with no modeled stair
    # connectivity), so a room unreachable from the agent's starting island
    # must be skipped, not treated as an error. patrol() already handles
    # this; a bespoke loop here previously didn't, and silently "succeeded"
    # by teleporting through disconnected space before that bug was fixed.
    from dynamic_home_eqa.embodied.runner import EpisodeConfig, QuestionEpisodeRunner

    store = BeliefStore(decay_models={})
    runner = QuestionEpisodeRunner(world, store, policy=None, episode_config=EpisodeConfig(patrol_start=8.0))
    runner.patrol()

    assert store.known_labels(), "patrol should observe at least some instances on the reachable island(s)"


@_needs_habitat_sim
def test_negative_observation_when_instance_moved_while_agent_elsewhere(world):
    from dynamic_home_eqa.embodied.types import Goto

    store = BeliefStore(decay_models={})

    # Find a label with a known first-event anchor whose viewpoint is
    # actually reachable from the agent's current (default) pose — this
    # scene's navmesh splits into several disconnected islands (confirmed:
    # a multi-story house with no modeled stair connectivity), so not every
    # anchor is reachable from wherever the agent starts. world.changes
    # already carries resolved slots (manifest.json's
    # from_semantic/to_semantic).
    by_label: dict[str, list] = {}
    for ch in world.changes:
        by_label.setdefault(ch.instance_id, []).append(ch)

    label = first_anchor = move_t = vp = None
    for cand_label, events in sorted(by_label.items()):
        events = sorted(events, key=lambda c: c.t)
        if not events or not events[0].from_semantic:
            continue
        cand_anchor = events[0].from_semantic
        if cand_anchor not in world._anchor_positions:
            continue
        cand_vp = world.viewpoint_for(cand_anchor)
        if cand_vp is None:
            continue
        if world.geodesic_time(world.pose.position, cand_vp.position) == float("inf"):
            continue  # unreachable from the default start — try another label
        label, first_anchor, move_t, vp = cand_label, cand_anchor, events[0].t, cand_vp
        break

    if label is None:
        pytest.skip("no dynamic label in this fixture has a reachable first-anchor viewpoint")

    world.advance_to(max(0.0, move_t - 0.5))
    result = world.execute(Goto(target=vp.position, face_yaw_rad=vp.yaw_rad))
    store.update_from_result(result, world)
    if label not in store.known_labels():
        pytest.skip(f"{label} was not visible from its own first-anchor viewpoint before the move")

    # Advance past the move without observing (agent stays put "elsewhere").
    world.advance_to(move_t + 0.5)

    # Now look at the OLD anchor again — the object has since moved away.
    result2 = world.execute(Goto(target=vp.position, face_yaw_rad=vp.yaw_rad))
    store.update_from_result(result2, world)

    assert store.believed_anchor(label) is None, (
        f"{label} should be marked displaced after staring at its stale anchor "
        f"post-move, got believed_anchor={store.believed_anchor(label)!r}"
    )
