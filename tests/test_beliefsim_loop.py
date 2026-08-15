"""Budget accounting, leakage, and world construction.

These are the tests that guard the experiment's validity rather than its
correctness in the ordinary sense: a policy that overspends, or that can
reach ground truth, produces numbers that look fine and mean nothing.
"""

from __future__ import annotations

import collections
import dataclasses
import pathlib
import random

import pytest

from beliefsim.beliefs import make_belief
from beliefsim.loop import (ALL_BUDGET, RunSpec, _check_picks, _cell_seed,
                            allocate, run_cell)
from beliefsim.policies import (POLICY_FACTORIES, AgentView, SensingPolicy,
                                make_policy)
from beliefsim.world import HOURS, load_world

TRACES = pathlib.Path("data/homer_traces")


@pytest.fixture(scope="module")
def world():
    return load_world(TRACES, "C")          # the smallest household


# ----------------------------------------------------------------- world

def test_train_and_test_days_do_not_collide(world):
    """The canonical trace numbers each split from zero. Keying state by the
    raw day index merges the two splits' change-points for days 0-9."""
    assert not set(world.learn_days) & set(world.score_days)
    assert min(world.score_days) > max(world.learn_days)


def test_state_defined_everywhere_scored(world):
    for obj in world.objects:
        for day in world.score_days:
            for hour in HOURS:
                assert world.location(obj, day, hour) in world.receptacles


def test_habitual_is_the_learning_period_mode(world):
    obj = world.objects[0]
    counts = {}
    for day in world.learn_days:
        for hour in HOURS:
            rec = world.location(obj, day, hour)
            counts[rec] = counts.get(rec, 0) + 1
    assert world.habitual(obj) == max(counts, key=lambda r: counts[r])


# ---------------------------------------------------------------- budget

@pytest.mark.parametrize("budget", [0, 1, 2, 5, 10, 17, 25, 50, 137])
def test_allocation_spends_exactly_the_budget(budget):
    counts = allocate(budget, len(HOURS))
    assert sum(counts) == budget
    assert len(counts) == len(HOURS)
    assert all(c >= 0 for c in counts)


def test_allocation_is_spread_not_front_loaded():
    assert allocate(1, len(HOURS)).index(1) == len(HOURS) // 2
    # No slot may hoard more than one extra look over any other.
    counts = allocate(25, len(HOURS))
    assert max(counts) - min(counts) <= 1


@pytest.mark.parametrize("budget", [1, 2, 5, 25])
def test_allocation_phase_rotates_without_changing_the_spend(budget):
    base = allocate(budget, len(HOURS))
    for phase in range(len(HOURS)):
        rotated = allocate(budget, len(HOURS), phase=phase)
        assert sum(rotated) == budget
        assert sorted(rotated) == sorted(base)
    assert len({tuple(allocate(budget, len(HOURS), phase=p))
                for p in range(len(HOURS))}) > 1


def test_look_hours_vary_across_days(world):
    """Displacement on HOMER+ peaks in the evening, so a fixed look schedule
    would make the budget axis partly a look-timing axis: a budget of 2 that
    lands on 19:00 beats a budget of 5 that misses it."""
    spec = RunSpec("C", "uniform", "round_robin", 2, 0)
    rows = run_cell(world, make_belief("uniform"), make_policy("round_robin"),
                    spec)
    sensed_hours = collections.Counter(
        r["hour"] for r in rows if r["n_just_sensed"] > 0)
    assert len(sensed_hours) > 2, sensed_hours


@pytest.mark.parametrize("policy_name", sorted(POLICY_FACTORIES))
@pytest.mark.parametrize("budget", [0, 1, 5, 25])
def test_daily_spend_never_exceeds_budget(world, policy_name, budget):
    spec = RunSpec("C", "most_frequent", policy_name, budget, 0)
    rows = run_cell(world, make_belief("most_frequent"),
                    make_policy(policy_name), spec)
    by_day = {}
    for r in rows:
        by_day[r["day"]] = max(by_day.get(r["day"], 0), r["senses_today"])
    assert by_day, "no scored rows"
    assert max(by_day.values()) <= budget
    if policy_name == "never_sense":
        assert max(by_day.values()) == 0
    elif budget > 0:
        # An informed policy must actually spend, or the budget axis is inert.
        assert max(by_day.values()) == budget


def test_unlimited_budget_observes_every_object_every_timestep(world):
    spec = RunSpec("C", "last_observation", "round_robin", ALL_BUDGET, 0)
    rows = run_cell(world, make_belief("last_observation"),
                    make_policy("round_robin"), spec)
    for r in rows:
        assert r["n_just_sensed"] == r["n"]
        assert r["n_not_sensed"] == 0
    # Complete observability at the scored instant is perfect localization;
    # anything less means the sighting short-circuit is not shared by every
    # belief and the just-sensed column is not comparable across methods.
    assert all(r["n_correct"] == r["n"] for r in rows)


def test_cell_seed_is_stable_across_processes():
    """crc32, not hash(): Python salts string hashing per process, so a
    tuple-hash seed would make a parallel sweep unreproducible."""
    spec = RunSpec("A", "fremen", "random", 5, 3)
    assert _cell_seed(spec) == _cell_seed(dataclasses.replace(spec))
    assert _cell_seed(spec) != _cell_seed(dataclasses.replace(spec, seed=4))


# --------------------------------------------------------------- leakage

class _Cheater(SensingPolicy):
    """A policy that tries to reach ground truth through its view."""

    name = "cheater"

    def select(self, view, n):
        assert not hasattr(view, "world")
        assert not any("world" in f.name or "truth" in f.name
                       for f in dataclasses.fields(view))
        # The belief is reachable, but it only knows what was observed.
        for obj in view.sensable:
            assert not hasattr(view.belief, "location")
        return list(view.sensable)[:n]


class _Overspender(SensingPolicy):
    name = "overspender"

    def select(self, view, n):
        return list(view.sensable)[:n + 1]


class _Trespasser(SensingPolicy):
    name = "trespasser"

    def select(self, view, n):
        return ["definitely-not-a-sensable-object"][:n]


class _Duplicator(SensingPolicy):
    name = "duplicator"

    def select(self, view, n):
        return [view.sensable[0]] * n


def test_agent_view_exposes_no_ground_truth(world):
    spec = RunSpec("C", "uniform", "cheater", 5, 0)
    run_cell(world, make_belief("uniform"), _Cheater(), spec)


@pytest.mark.parametrize("policy,message,budget", [
    (_Overspender(), "budget", 5),
    (_Trespasser(), "unsensable", 5),
    # 25 puts two looks in some slots; a duplicate needs a slot with n > 1.
    (_Duplicator(), "duplicate", 25),
])
def test_budget_and_access_violations_are_errors_not_truncations(
        world, policy, message, budget):
    spec = RunSpec("C", "uniform", policy.name, budget, 0)
    with pytest.raises(ValueError, match=message):
        run_cell(world, make_belief("uniform"), policy, spec)


def test_held_out_objects_are_unreachable_by_any_policy(world):
    held = tuple(world.objects[:2])
    for policy_name in sorted(POLICY_FACTORIES):
        spec = RunSpec("C", "most_frequent", policy_name, 25, 0,
                       condition="heldout", heldout=held, draw="0")
        rows = run_cell(world, make_belief("most_frequent"),
                        make_policy(policy_name), spec)
        heldout_rows = [r for r in rows if r["group"] == "heldout"]
        assert heldout_rows
        # Never observed => never just-sensed, and staleness stays undefined.
        assert all(r["n_just_sensed"] == 0 for r in heldout_rows)
        assert all(r["n_never_observed"] == r["n"] for r in heldout_rows)


def test_belief_never_sees_an_unobserved_object(world):
    """The agent's knowledge is exactly what it paid for: with no budget,
    every belief is still at its prior."""
    for name in ("last_observation", "most_frequent", "timetable", "fremen",
                 "pooled_class"):
        belief = make_belief(name)
        belief.reset(world.objects, world.receptacles, world.object_classes,
                     random.Random(0))
        dist = belief.distribution(world.objects[0], 0)
        assert len(set(round(p, 12) for p in dist.values())) == 1, name
        assert abs(sum(dist.values()) - 1.0) < 1e-9, name
