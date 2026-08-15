"""Belief models behind one harness-facing seam.

The seam is :class:`Belief`: reset, absorb one observation, answer with a
distribution over receptacles at an arbitrary time. Three families plug
into it.

* :class:`BaselineBelief` adapts ``baselines.beliefs.base.BeliefModel``
  UNCHANGED — last-observation, most-frequent and timetable are the exact
  classes the sense-or-answer study uses, constructed here and fed
  ``Observation`` records. Our own method is wired the same way when it
  arrives, which is why the adapter exists rather than a reimplementation.
* :class:`FremenBelief` adapts the batch-fit spectral model in
  ``homer.fremen``. Batch models cannot absorb observations incrementally,
  so it refits from its accumulated history, at most once per simulated
  day (see :data:`REFIT_EVERY_DAYS`).
* :class:`PooledClassBelief` is the cross-object competitor, reimplemented
  for this setting; the deviation from the pilot's ``homer.baselines.Pooled``
  is documented on the class.

Decay is OFF for most-frequent and timetable here, diverging from the
frozen 24 h half-life the sense-or-answer panel uses. That half-life exists
because our generated banks drift, so old sightings must be allowed to die.
HOMER+ does not drift: each day is an independent sample from one fixed
schedule distribution (the flat learning curves in
``superseded/homer_pilot_2026_08/`` are the direct evidence — accuracy is
within two points of its final value after four days). Under a sensing
budget, evidence is the scarce resource; discarding it on a half-life would
handicap exactly the models the experiment is trying to give their best
shot, and would collapse most-frequent onto last-observation.
"""

from __future__ import annotations

import collections
import math
import random
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs import (BeliefModel, LastObservation,
                               MostFrequentLocation, TimetableConfig,
                               TimetableLookup)
from baselines.types import EpisodeContext, Observation
from beliefsim.world import SECONDS_PER_DAY
from homer.fremen import Fremen

REFIT_EVERY_DAYS = 1
"""How often a batch-fit belief rebuilds itself. One simulated day is the
coarsest interval that keeps the model current at every scored timestep
while making the cost proportional to days rather than to timesteps; a
full refit at every timestep would dominate the runtime of the sweep and
change no result, since no new observation arrives between a day's last
sense and the next day's first."""

FREMEN_ORDER = 2
"""Number of spectral components, as in the pilot and the FreMEn paper's
default order selection."""


class Belief:
    """Interface: accumulate observations, answer with a distribution.

    ``distribution`` must return a normalized mapping over a subset of the
    receptacle vocabulary and must never return empty — an agent that has
    observed nothing still holds a belief, and it is the uniform prior.
    """

    name: str = "belief"

    def reset(self, objects: Sequence[str], receptacles: Sequence[str],
              object_classes: Mapping[str, str], rng: random.Random) -> None:
        raise NotImplementedError

    def observe(self, object_id: str, t: int, receptacle_id: str) -> None:
        raise NotImplementedError

    def distribution(self, object_id: str, t: int) -> Dict[str, float]:
        raise NotImplementedError


class _ExactSighting:
    """Mixin: an observation AT the query instant is ground truth at that
    instant, and no model prior may outvote it.

    ``baselines.beliefs.base.BeliefModel.predict`` already does this, so
    without the mixin the adapted models would win every just-sensed object
    outright while the batch-fit models had to infer their way back to a
    location they had just been told. That asymmetry is not a modelling
    difference, it is a difference in which class happens to implement the
    short-circuit, and at unlimited budget it is worth the entire gap
    between 1.000 and 0.956.
    """

    def _reset_sightings(self) -> None:
        self._last_sighting: Dict[str, Tuple[int, str]] = {}

    def _record_sighting(self, object_id: str, t: int,
                         receptacle_id: str) -> None:
        self._last_sighting[object_id] = (t, receptacle_id)

    def _sighting_now(self, object_id: str,
                      t: int) -> Optional[Dict[str, float]]:
        seen = self._last_sighting.get(object_id)
        return {seen[1]: 1.0} if seen is not None and seen[0] == t else None


class UniformBelief(Belief):
    """Floor: the prior, never updated.

    Retained as a live control because the pilot's version of it was the
    source of a reported-but-artefactual result (see
    ``superseded/homer_pilot_2026_08/``). Under the seeded tie-break in
    ``beliefsim.scoring`` it must score 1/|R|, which makes it an end-to-end
    check on the scoring path rather than a decorative row.
    """

    name = "uniform"

    def reset(self, objects, receptacles, object_classes, rng) -> None:
        self._dist = {r: 1.0 / len(receptacles) for r in receptacles}

    def observe(self, object_id, t, receptacle_id) -> None:
        pass

    def distribution(self, object_id, t) -> Dict[str, float]:
        return self._dist


class BaselineBelief(Belief):
    """Adapter over an unmodified ``baselines.beliefs`` model.

    Observations are delivered as :class:`~baselines.types.Observation`
    (a positive sighting), never as ``SenseResult``: object-level sensing
    reveals one object's location and says nothing about any other object,
    so there is no negative evidence to record. The exclusion machinery in
    the base class therefore stays inert here, and will become live if and
    when the receptacle-level observation model is added.
    """

    def __init__(self, name: str,
                 factory: Callable[[random.Random], BeliefModel]) -> None:
        self.name = name
        self._factory = factory

    def reset(self, objects, receptacles, object_classes, rng) -> None:
        self._classes = dict(object_classes)
        self._model = self._factory(rng)
        self._model.reset(EpisodeContext(
            episode_id="beliefsim", household_id="",
            receptacle_ids=tuple(receptacles),
            object_classes=self._classes,
            budget_per_day=0, n_days=0))

    def observe(self, object_id, t, receptacle_id) -> None:
        self._model.update(Observation(
            object_id=object_id, object_class=self._classes[object_id],
            receptacle_id=receptacle_id, t=t, source="sense"))

    def distribution(self, object_id, t) -> Dict[str, float]:
        # predict_readonly so that querying the belief — which the scorer and
        # the entropy policy both do, for every object at every timestep —
        # cannot consume the model's tie-break randomness and thereby change
        # what the agent would have done.
        return dict(self._model.predict_readonly(object_id, t).distribution)


class FremenBelief(_ExactSighting, Belief):
    """Spectral occupancy model refit from the agent's own observations.

    This is closer to FreMEn's intended setting than the pilot was. The
    paper's robot observes a cell only when it visits, and the model exists
    precisely to extrapolate from sparse, irregular visits; the pilot fed it
    complete state on a regular grid, where the spectral machinery had
    nothing to do. Here the sampling times ARE the agent's sense times, so
    the projection runs on exactly the irregular history FreMEn was designed
    for.

    Fallback for an object the spectral fit cannot use — fewer than two
    observations, so there is no residual to project — is that object's own
    sighting histogram, and uniform only when it has never been seen at all.
    Falling straight through to uniform instead would discard the one
    observation the agent paid for and turn FreMEn into a strawman at
    exactly the low budgets the experiment is about: measured at 0.37
    against 0.92 for a model that simply remembers where it last looked.
    """

    name = "fremen"

    def __init__(self, order: int = FREMEN_ORDER) -> None:
        self._order = order

    def reset(self, objects, receptacles, object_classes, rng) -> None:
        self._receptacles = list(receptacles)
        self._uniform = {r: 1.0 / len(receptacles) for r in receptacles}
        # object -> day -> {hour: receptacle}, the shape homer.fremen wants.
        self._obs: Dict[str, Dict[int, Dict[int, str]]] = \
            collections.defaultdict(dict)
        self._counts: Dict[str, collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._reset_sightings()
        self._model: Optional[Fremen] = None
        self._fitted_at_day = -1
        self._dirty = False

    def observe(self, object_id, t, receptacle_id) -> None:
        day = t // SECONDS_PER_DAY
        hour = (t % SECONDS_PER_DAY) // 3600
        self._obs[object_id].setdefault(day, {})[hour] = receptacle_id
        self._counts[object_id][receptacle_id] += 1
        self._record_sighting(object_id, t, receptacle_id)
        self._dirty = True

    def _histogram(self, object_id: str) -> Dict[str, float]:
        counts = self._counts.get(object_id)
        if not counts:
            return self._uniform
        total = float(sum(counts.values()))
        return {r: c / total for r, c in counts.items()}

    def _refit(self, day: int) -> None:
        max_day = max((d for byday in self._obs.values() for d in byday),
                      default=0)
        occupancy = {
            obj: [byday.get(d, {}) for d in range(max_day + 1)]
            for obj, byday in self._obs.items()
            # A single observation defines no residual to project onto; the
            # spectral fit needs at least two sample times to have a step.
            if sum(len(v) for v in byday.values()) >= 2}
        model = Fremen(order=self._order)
        model.fit(occupancy, self._receptacles, initial={}, heldout=())
        self._model = model
        self._fitted_at_day = day
        self._dirty = False

    def distribution(self, object_id, t) -> Dict[str, float]:
        now = self._sighting_now(object_id, t)
        if now is not None:
            return now
        day = t // SECONDS_PER_DAY
        if self._dirty and day - self._fitted_at_day >= REFIT_EVERY_DAYS:
            self._refit(day)
        if self._model is None:
            return self._histogram(object_id)
        minutes = float((t % SECONDS_PER_DAY) // 60)
        dist = self._model.predict(object_id, minutes)
        return dist or self._histogram(object_id)


class PooledClassBelief(_ExactSighting, Belief):
    """Cross-object model: back off from the object to its class to the house.

    Structure shared across objects, with no persona representation — the
    statistical answer to "world knowledge should help you guess about a
    thing you have barely seen". An object with few observations borrows the
    hour-conditional habits of other objects of the SAME CLASS (HOMER+
    object ids are ``class#instance``, and classes recur within and across
    households), and a class with no observations borrows the house-wide
    receptacle popularity at that hour.

    Deviation from the pilot's ``homer.baselines.Pooled``, which conditioned
    on the object's initial placement: there is no initial placement in this
    setting. The robot arrives in an unfamiliar home and is given nothing;
    the only key available for pooling before an object has been seen is its
    class. This is also the stronger competitor — the pilot's version had to
    be told where the object started, and still lost to the shared fallback.

    The backoff chain has four levels, and the third one matters more than
    the pooling does:

        object at this hour -> object at any hour -> class at this hour
        -> house at this hour

    Omitting "object at any hour" costs the model almost everything at low
    budget. An object seen three times in seventy days has an empty cell at
    whatever hour it is queried, so a three-level chain discards its own
    three observations and answers from the class — measured at 0.44
    against 0.92 for a model that simply counts. That is a defect in the
    competitor, not a finding about pooling, and the fix is the standard
    hierarchy rather than a tuning choice.

    Smoothing is an m-estimate at each level. Both constants were chosen by
    sweeping {1, 2, 5, 12} x {1, 2, 5} and taking the value that maximises
    THIS MODEL's own accuracy — the competitor is given its best shot, and
    the full sweep is in ``src/beliefsim/README.md``. Selecting on the same
    data that is reported is mild overfitting, in the competitor's favour,
    which can only make a later claim against it more conservative. The
    class weight is the one that matters: at 5 it swamps a barely-observed
    object's own evidence and costs 0.32 accuracy at budget 1.

    At these weights an object with its own history answers almost entirely
    from that history, and the class prior takes over only for an object
    that has never been seen. That is the intended behaviour of a backoff
    model, and it is also a finding: on HOMER+ there is nothing to gain from
    borrowing across same-class objects once an object has been observed
    even once.
    """

    name = "pooled_class"
    M_OBJECT = 1.0
    M_CLASS = 1.0

    def reset(self, objects, receptacles, object_classes, rng) -> None:
        self._receptacles = list(receptacles)
        self._classes = dict(object_classes)
        self._own: Dict[Tuple[str, int], collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._own_all: Dict[str, collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._cls: Dict[Tuple[str, int], collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._cls_all: Dict[str, collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._house: Dict[int, collections.Counter] = \
            collections.defaultdict(collections.Counter)
        self._house_all: collections.Counter = collections.Counter()
        self._reset_sightings()

    def observe(self, object_id, t, receptacle_id) -> None:
        hour = (t % SECONDS_PER_DAY) // 3600
        cls = self._classes[object_id]
        self._own[(object_id, hour)][receptacle_id] += 1
        self._own_all[object_id][receptacle_id] += 1
        self._cls[(cls, hour)][receptacle_id] += 1
        self._cls_all[cls][receptacle_id] += 1
        self._house[hour][receptacle_id] += 1
        self._house_all[receptacle_id] += 1
        self._record_sighting(object_id, t, receptacle_id)

    @staticmethod
    def _norm(weights: Mapping[str, float]) -> Dict[str, float]:
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    def distribution(self, object_id, t) -> Dict[str, float]:
        now = self._sighting_now(object_id, t)
        if now is not None:
            return now
        hour = (t % SECONDS_PER_DAY) // 3600
        cls = self._classes[object_id]
        # House level: hour cell, smoothed toward the all-hours popularity,
        # with a flat floor so every receptacle keeps nonzero mass.
        n_all = sum(self._house_all.values()) or 1
        house = self._norm({
            r: (self._house[hour].get(r, 0)
                + 5.0 * self._house_all.get(r, 0) / n_all
                + 1.0 / len(self._receptacles))
            for r in self._receptacles})
        # Class level: this class's hour cell over the house prior.
        cls_counts = self._cls.get((cls, hour), {})
        class_level = self._norm({
            r: cls_counts.get(r, 0) + self.M_CLASS * house[r]
            for r in self._receptacles})
        # Object-habit level: everything this object has ever been seen
        # doing, at any hour, over the class prior. This is the level that
        # keeps a barely-observed object's own evidence in play.
        own_all = self._own_all.get(object_id, {})
        habit = self._norm({
            r: own_all.get(r, 0) + self.M_CLASS * class_level[r]
            for r in self._receptacles})
        # Object-hour level: this object's own hour cell over its habit.
        own = self._own.get((object_id, hour), {})
        return self._norm({
            r: own.get(r, 0) + self.M_OBJECT * habit[r]
            for r in self._receptacles})


def _timetable(rng: random.Random) -> BeliefModel:
    # bin_hours=1 matches the hourly grid the experiment scores on;
    # day_scheme="all" because HOMER+ has no weekday structure to condition
    # on (reports/homer_spectra/) and per-day bins would only shard the
    # already-scarce observations by seven.
    return TimetableLookup(rng, TimetableConfig(bin_hours=1,
                                                day_scheme="all"))


BELIEF_FACTORIES: Dict[str, Callable[[], Belief]] = {
    "uniform": UniformBelief,
    "last_observation": lambda: BaselineBelief("last_observation",
                                               LastObservation),
    "most_frequent": lambda: BaselineBelief("most_frequent",
                                            MostFrequentLocation),
    "timetable": lambda: BaselineBelief("timetable", _timetable),
    "fremen": FremenBelief,
    "pooled_class": PooledClassBelief,
}
"""The non-LLM arm of the factorial. ``ours`` and ``llm_raw`` join here."""


def make_belief(name: str) -> Belief:
    return BELIEF_FACTORIES[name]()
