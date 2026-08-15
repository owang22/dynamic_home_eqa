"""Sensing policies: given a belief and a budget, choose what to look at.

This is a NEW interface, not ``baselines.policies.base.DecisionPolicy``.
That one is ``decide(question, prediction, budget_remaining, t,
last_sense) -> AnswerNow | Sense``: it is driven by a question, it chooses a
RECEPTACLE to open in service of localizing one named object, and it
terminates by committing an answer. The budgeted whole-house loop has no
questions at all — the agent must maintain a belief over every object at
every timestep and decide, unprompted, which object to spend a look on.
There is no question to hang the old signature on and no answer to commit,
so the two cannot be reconciled by adapting arguments. The sense-or-answer
interface remains correct for its own study and is untouched.

What the policies CAN see is fixed by :class:`AgentView`, which holds no
reference to :class:`beliefsim.world.World`. A policy can read its own
belief and its own observation history; it has no accessor for ground
truth, for the future, or for objects outside the sensable set. That is
enforced structurally rather than by convention, and asserted in
``tests/test_beliefsim_leakage.py``.
"""

from __future__ import annotations

import abc
import dataclasses
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from beliefsim.beliefs import Belief


@dataclasses.dataclass(frozen=True)
class AgentView:
    """Everything a policy may know at one decision point.

    Deliberately not a view onto the world: ``sensable`` is the set of
    objects the harness will accept, ``t`` is now, and the belief answers
    only about times up to now. Nothing here can be dereferenced into
    ground truth.
    """

    t: int
    sensable: Tuple[str, ...]
    receptacles: Tuple[str, ...]
    belief: Belief
    last_observed: Dict[str, Optional[int]]

    def staleness(self, object_id: str) -> float:
        """Seconds since the object was last observed; ``inf`` if never.

        Never-observed objects sort ahead of every observed one under a
        staleness rule, which is the intended behaviour: an object the agent
        has no evidence about is maximally stale.
        """
        last = self.last_observed.get(object_id)
        return math.inf if last is None else float(self.t - last)

    def entropy(self, object_id: str) -> float:
        """Shannon entropy of the current belief, in nats."""
        total = 0.0
        for p in self.belief.distribution(object_id, self.t).values():
            if p > 0.0:
                total -= p * math.log(p)
        return total


class SensingPolicy(abc.ABC):
    """Choose which objects to observe at one timestep.

    ``select`` must return at most ``n`` distinct object ids drawn from
    ``view.sensable``. Returning fewer is allowed (a policy may decline to
    spend); returning more, duplicates, or anything outside the sensable set
    is a harness error, not a silently-truncated request — a policy that
    overspends its budget is the one bug that would invalidate the whole
    experiment.
    """

    name: str = "policy"

    def reset(self, objects: Sequence[str], rng: random.Random) -> None:
        self._rng = rng

    @abc.abstractmethod
    def select(self, view: AgentView, n: int) -> Sequence[str]:
        ...

    def _top_n(self, view: AgentView, n: int, key) -> List[str]:
        """The n objects with the largest ``key``, ties broken by the
        policy's seeded generator.

        Ties are the common case at low budget, where most objects share an
        identical (infinite) staleness or an identical uniform entropy.
        Breaking them by id order would make the policy a disguised
        round-robin over the alphabet, which is the same class of artefact
        that produced the pilot's spurious uniform baseline.
        """
        if n >= len(view.sensable):
            # Saturated: every sensable object is selected whatever the key
            # says. Short-circuiting here is not an approximation, it is the
            # same answer without evaluating an entropy per object per
            # timestep — the dominant cost of the unlimited-budget cells.
            return list(view.sensable)
        ordered = list(view.sensable)
        self._rng.shuffle(ordered)
        ordered.sort(key=key, reverse=True)
        return ordered[:n]


class NeverSense(SensingPolicy):
    """Spend nothing. The reference point for marginal value per sense."""

    name = "never_sense"

    def select(self, view: AgentView, n: int) -> Sequence[str]:
        return ()


class RandomPolicy(SensingPolicy):
    """Uniform sample without replacement. The budget-allocation floor:
    any informed policy has to beat spending looks at random."""

    name = "random"

    def select(self, view: AgentView, n: int) -> Sequence[str]:
        n = min(n, len(view.sensable))
        return self._rng.sample(list(view.sensable), n)


class RoundRobin(SensingPolicy):
    """Cycle through the objects in a fixed order — maximal coverage.

    Expected to be strong at high budget, where the cycle completes often
    enough to keep every object fresh, and to collapse at low budget, where
    it cannot. That collapse is a property of the budget, not a result: it
    is the shape the comparison is measured against.
    """

    name = "round_robin"

    def reset(self, objects, rng) -> None:
        super().reset(objects, rng)
        # A fixed but seed-dependent order: a policy that always starts at
        # the alphabetically-first object would systematically favour
        # whichever objects sort early whenever the budget cannot complete
        # a cycle.
        self._order = list(objects)
        rng.shuffle(self._order)
        self._cursor = 0

    def select(self, view: AgentView, n: int) -> Sequence[str]:
        allowed = set(view.sensable)
        picks: List[str] = []
        for _ in range(len(self._order)):
            if len(picks) >= n:
                break
            obj = self._order[self._cursor % len(self._order)]
            self._cursor += 1
            if obj in allowed:
                picks.append(obj)
        return picks


class StalenessFirst(SensingPolicy):
    """Look at whatever has gone unobserved longest.

    Coverage-driven like round-robin, but adaptive: it re-prioritizes after
    every observation instead of following a fixed cycle. On a world with no
    per-object differences in volatility the two are nearly equivalent; they
    separate when some objects move far more than others.
    """

    name = "staleness_first"

    def select(self, view: AgentView, n: int) -> Sequence[str]:
        return self._top_n(view, n, key=view.staleness)


class EntropyFirst(SensingPolicy):
    """Look where the belief is least certain.

    The uncertainty-driven competitor, and the policy half of the
    FreMEn + entropy-first system the STRANDS line of work established for
    scheduling a robot's observations. It is only as good as the belief's
    calibration, which is why the Brier and log-loss columns are reported
    beside accuracy: a belief whose uncertainty is meaningless makes this
    policy no better than random, and top-1 accuracy alone cannot show that.
    """

    name = "entropy_first"

    def select(self, view: AgentView, n: int) -> Sequence[str]:
        return self._top_n(view, n, key=view.entropy)


POLICY_FACTORIES = {
    "never_sense": NeverSense,
    "random": RandomPolicy,
    "round_robin": RoundRobin,
    "staleness_first": StalenessFirst,
    "entropy_first": EntropyFirst,
}
"""The non-LLM arm of the policy axis. ``ours`` joins here."""


def make_policy(name: str) -> SensingPolicy:
    return POLICY_FACTORIES[name]()
