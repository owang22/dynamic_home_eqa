"""The budgeted whole-house belief-tracking loop.

One run = one (household, belief, policy, budget, seed, condition) cell.
The agent arrives in an unfamiliar home knowing nothing, walks through every
day of the trace spending at most ``budget`` observations per day, and its
whole-house belief is scored at every hour of every scored day against every
object's true location.

Three choices in here are load-bearing and are the first things a reader
should check.

**Budget is per DAY; scoring is per TIMESTEP.** With ~50 objects, 17 hourly
timesteps per day and a budget of, say, 5, at most 5 of 850 object-instants
per day are freshly observed. Almost every scored instant is therefore far
in time from any observation, so what the number measures is inference from
sparse evidence rather than the freshness of a read-back. A per-timestep
budget would silently turn the experiment into the latter.

**Sensing at hour h happens before scoring at hour h,** so an object looked
at right now is trivially correct. This inflates every spending policy by a
bounded amount, and the inflation is not hidden: ``n_just_sensed`` and
``n_just_sensed_correct`` are emitted per timestep, so both the inclusive
and exclusive accuracies are recoverable from the CSV without a second run.

**The day's budget is spread evenly over the day by the harness, at a phase
drawn fresh each day.** The factorial varies WHAT to look at, not WHEN;
taking the timing away from the policy removes a confound the experiment is
not powered to resolve, and makes budget accounting auditable. The phase
must be RANDOM, though, not fixed: displacement on HOMER+ is concentrated in
the evening (19:00-23:00 runs 12-15% displaced against 4-6% at midday), so a
deterministic even spread makes the budget axis partly an axis of look
timing. Measured, before the phase was randomised: a budget of 2 landed on
11:00 and 19:00 and beat a budget of 5, which landed on 08:00/12:00/15:00/
18:00/22:00 and missed the evening peak. Drawing the phase per day averages
that out over 75 days and 5 seeds.

The cost is that a policy which would rather spend everything at 08:00
cannot express that. WHEN to look is a real second axis on this data — worth
more than the choice of belief model at low budget — and it is left for
future work rather than silently folded in.
"""

from __future__ import annotations

import dataclasses
import math
import random
import zlib
from typing import Dict, List, Optional, Sequence, Tuple

from beliefsim.beliefs import Belief
from beliefsim.policies import AgentView, SensingPolicy
from beliefsim.scoring import brier, log_loss, argmax_tiebroken
from beliefsim.world import HOURS, World, to_seconds

ALL_BUDGET = "all"
"""Sentinel for the unlimited condition: observe every object at every
timestep, i.e. the complete-state regime the superseded pilot ran in. It is
the right-hand end of the sweep, present so the curves show where the
budgeted setting rejoins the one that could not discriminate."""


def allocate(budget: int, n_slots: int, phase: int = 0) -> List[int]:
    """Spread ``budget`` observations over ``n_slots`` timesteps evenly.

    Slot j gets the observations whose index maps to it under
    ``floor((i + 0.5) * n_slots / budget)``, then the whole pattern is
    rotated by ``phase``. The rotation is what keeps the budget axis from
    doubling as a look-timing axis (see the module docstring); the caller
    draws a fresh phase for every day from the cell's seeded generator.
    """
    counts = [0] * n_slots
    for i in range(budget):
        counts[int((i + 0.5) * n_slots / budget)] += 1
    phase %= n_slots
    return counts[-phase:] + counts[:-phase] if phase else counts


@dataclasses.dataclass(frozen=True)
class RunSpec:
    household: str
    belief: str
    policy: str
    budget: object                      # int, or ALL_BUDGET
    seed: int
    condition: str = "open"             # "open" | "heldout"
    heldout: Tuple[str, ...] = ()
    draw: str = ""


def _cell_seed(spec: RunSpec) -> int:
    """Deterministic seed for one cell.

    Built with crc32 over the cell's identity rather than ``hash()`` on a
    tuple of strings: Python salts string hashing per process, so a
    tuple-hash seed would make results depend on PYTHONHASHSEED and quietly
    unreproducible across runs and across the workers of a parallel sweep.
    """
    key = "|".join(str(x) for x in (spec.household, spec.belief, spec.policy,
                                    spec.budget, spec.seed, spec.condition,
                                    spec.draw))
    return zlib.crc32(key.encode()) & 0xFFFFFFFF


def _row_template(spec: RunSpec) -> Dict[str, object]:
    return {"household": spec.household, "belief": spec.belief,
            "policy": spec.policy, "budget": spec.budget, "seed": spec.seed,
            "condition": spec.condition, "draw": spec.draw}


def run_cell(world: World, belief: Belief, policy: SensingPolicy,
             spec: RunSpec) -> List[Dict[str, object]]:
    """Simulate one cell; return one aggregate row per (timestep, group).

    Rows carry SUMS and COUNTS rather than ratios so that every downstream
    average is a weighted one computed by
    :func:`beliefsim.scoring.aggregate_ratio`. Emitting per-timestep means
    instead would silently make every aggregate a macro-average over
    timesteps, which is the failure mode documented in
    ``superseded/homer_pilot_2026_08/``.
    """
    rng = random.Random(_cell_seed(spec))
    belief.reset(world.objects, world.receptacles, world.object_classes,
                 random.Random(rng.randrange(2 ** 32)))
    policy.reset(world.objects, random.Random(rng.randrange(2 ** 32)))
    score_rng = random.Random(rng.randrange(2 ** 32))

    held = set(spec.heldout)
    sensable = tuple(o for o in world.objects if o not in held)
    last_observed: Dict[str, Optional[int]] = {o: None for o in world.objects}

    groups: Tuple[Tuple[str, Tuple[str, ...]], ...]
    if spec.condition == "heldout":
        # Held-out objects are scored on their own because they are the
        # controlled transfer condition; the observable objects are scored
        # alongside so the two are comparable within one run.
        groups = (("observable", sensable),
                  ("heldout", tuple(sorted(held))))
    else:
        groups = (("all", world.objects),)

    n_slots = len(HOURS)
    unlimited = spec.budget == ALL_BUDGET
    schedule_rng = random.Random(rng.randrange(2 ** 32))

    rows: List[Dict[str, object]] = []
    template = _row_template(spec)
    scored_days = set(world.score_days)

    for day in tuple(world.learn_days) + tuple(world.score_days):
        per_slot = ([len(sensable)] * n_slots if unlimited else
                    allocate(int(spec.budget), n_slots,
                             phase=schedule_rng.randrange(n_slots)))
        spent_today = 0
        for slot, hour in enumerate(HOURS):
            t = to_seconds(day, hour)
            n = per_slot[slot]
            picks: Sequence[str] = ()
            if n > 0:
                view = AgentView(t=t, sensable=sensable,
                                 receptacles=world.receptacles,
                                 belief=belief, last_observed=last_observed)
                picks = policy.select(view, n)
                _check_picks(picks, n, sensable, policy)
                for obj in picks:
                    belief.observe(obj, t, world.location(obj, day, hour))
                    last_observed[obj] = t
                spent_today += len(picks)
            if day not in scored_days:
                continue
            just_sensed = set(picks)
            for group_name, group_objects in groups:
                row = dict(template)
                row.update({"day": day, "hour": hour, "group": group_name,
                            "senses_today": spent_today})
                row.update(_score_group(world, belief, group_objects, day,
                                        hour, t, just_sensed, last_observed,
                                        score_rng))
                rows.append(row)
    return rows


def _check_picks(picks: Sequence[str], n: int, sensable: Sequence[str],
                 policy: SensingPolicy) -> None:
    """Budget and access enforcement. A policy that overspends or reaches an
    unsensable object invalidates its whole column, so this is an error
    rather than a truncation."""
    if len(picks) > n:
        raise ValueError(f"{policy.name}: selected {len(picks)} objects with "
                         f"a budget of {n}")
    if len(set(picks)) != len(picks):
        raise ValueError(f"{policy.name}: duplicate selections {picks}")
    outside = set(picks) - set(sensable)
    if outside:
        raise ValueError(f"{policy.name}: selected unsensable objects "
                         f"{sorted(outside)}")


def _score_group(world: World, belief: Belief, objects: Sequence[str],
                 day: int, hour: int, t: int, just_sensed: set,
                 last_observed: Dict[str, Optional[int]],
                 rng: random.Random) -> Dict[str, object]:
    receptacles = world.receptacles
    acc = {"n": 0, "n_correct": 0, "n_displaced": 0, "n_displaced_correct": 0,
           "n_just_sensed": 0, "n_just_sensed_correct": 0,
           "n_not_sensed": 0, "n_not_sensed_correct": 0,
           "n_displaced_not_sensed": 0, "n_displaced_not_sensed_correct": 0,
           "brier_sum": 0.0, "log_loss_sum": 0.0, "staleness_sum": 0.0,
           "n_never_observed": 0}
    for obj in objects:
        truth = world.location(obj, day, hour)
        dist = belief.distribution(obj, t)
        correct = int(argmax_tiebroken(dist, rng) == truth)
        acc["n"] += 1
        acc["n_correct"] += correct
        displaced = world.is_displaced(obj, day, hour)
        if displaced:
            acc["n_displaced"] += 1
            acc["n_displaced_correct"] += correct
            # The strictest reading of the primary metric: displaced AND not
            # being looked at right now. Counted here rather than derived
            # downstream, because the two exclusions overlap per object and a
            # row-level subtraction can only bound the result.
            if obj not in just_sensed:
                acc["n_displaced_not_sensed"] += 1
                acc["n_displaced_not_sensed_correct"] += correct
        if obj in just_sensed:
            acc["n_just_sensed"] += 1
            acc["n_just_sensed_correct"] += correct
        else:
            acc["n_not_sensed"] += 1
            acc["n_not_sensed_correct"] += correct
        acc["brier_sum"] += brier(dist, truth, receptacles)
        acc["log_loss_sum"] += log_loss(dist, truth)
        last = last_observed.get(obj)
        if last is None:
            acc["n_never_observed"] += 1
        else:
            # Staleness in hours, averaged only over objects that have ever
            # been observed; a never-observed object has undefined (not
            # infinite) staleness and would otherwise destroy the mean.
            acc["staleness_sum"] += (t - last) / 3600.0
    return acc


ROW_FIELDS = ("household", "belief", "policy", "budget", "seed", "condition",
              "draw", "day", "hour", "group", "senses_today", "n",
              "n_correct", "n_displaced", "n_displaced_correct",
              "n_just_sensed", "n_just_sensed_correct", "n_not_sensed",
              "n_not_sensed_correct", "n_displaced_not_sensed",
              "n_displaced_not_sensed_correct", "brier_sum", "log_loss_sum",
              "staleness_sum", "n_never_observed")
