"""One LLM-written household hypothesis, converted into a belief model.

A hypothesis is a set of ACTIVITIES ("dinner, weekdays, around 19:30 for
an hour, usually moves mug_mara to kitchen_table_k1 and leaves it
there"), plus a REST map saying where objects sit when nothing is going
on. :func:`parse_hypothesis` turns the JSON an LLM (or a test) writes
into a validated :class:`Hypothesis`; :class:`HypothesisProgramBelief`
is the converter proper — it turns that description into a
:class:`~baselines.beliefs.base.BeliefModel` whose ``predict`` answers
p(receptacle | object, t), so a :class:`~baselines.beliefs.
hypothesis_mixture.HypothesisMixture` can weigh several hypotheses
against each other on the sighting stream.

Everything the description states is a PRIOR, never a fact; sightings
move every number:

* the rest location is a Dirichlet prior of :data:`REST_PRIOR_COUNT`
  pseudo-sightings on the stated receptacle, competing with decayed
  real off-window sightings (half-life :data:`REST_HALF_LIFE_H`);
* each move rule's chance label ("rarely" … "almost_always") maps to a
  Beta prior of strength :data:`CHANCE_PRIOR_STRENGTH` centred on
  :data:`ORDINAL_CENTERS`, updated by in-window sightings that land on
  (success) or off (failure, discounted by :data:`FAILURE_WEIGHT`) the
  rule's destination;
* each activity's start hour is a Normal prior (sd
  :data:`START_HOUR_PRIOR_SD_H`) updated conjugately by the times of
  confirming sightings.

Numbers the LLM may state directly (times, days-per-week frequencies)
are the ones sightings correct quickly; probabilities arrive only as
ordinal labels because LLMs rank reliably and give magnitudes
unreliably.

Prediction semantics for object O at time t, under one hypothesis: each
rule moving O contributes ``p(activity happens today) * p(t inside the
rule's active window) * E[chance]`` on its destination; the active
window has Gaussian edges (posterior start-hour uncertainty plus
:data:`WINDOW_EDGE_SD_H`), runs for the stated duration when the object
is ``returned`` afterwards and until midnight when it is ``left``.
Displaced mass is capped at :data:`MAX_DISPLACED_MASS`; the remainder
sits on the rest distribution. Objects the hypothesis never mentions
fall back to the base class's frequency/cold-start behaviour, so an
incomplete description degrades to a statistical model instead of
breaking.

Deliberate v1 simplifications (documented, not hidden): an object
``left`` out overnight is back at rest the next morning unless the
activity recurs; the days-per-week frequency is used as stated (the
chance Beta absorbs occurrence error); misplacement noise is left to
the floor mix and the rest Dirichlet.

Day convention (matches the banks and ``timetable.py``): day 0 is
Monday, weekend days are ``day % 7 in WEEKEND_DAYS``. All times are
seconds since episode start.
"""

from __future__ import annotations

import dataclasses
import math
import random
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Tuple,
                    Union)

from baselines.beliefs.base import (DEFAULT_FLOOR_MASS,
                                    DEFAULT_FREQUENCY_ALPHA, BeliefModel)
from baselines.types import DAY_SECONDS, Prediction

ORDINAL_CENTERS: Mapping[str, float] = {
    "rarely": 0.10, "sometimes": 0.35, "usually": 0.70,
    "almost_always": 0.90}
"""Prior center of each chance label. Labels, not numbers, because an
object sighted a dozen times a month gives the fit almost nothing to
correct a stated magnitude with — but plenty to correct a rank."""

CHANCE_PRIOR_STRENGTH = 2.0
"""Beta pseudo-count behind a chance label: two confirming sightings
outweigh the label, which is as loose as a prior can be while still
ordering fresh hypotheses."""

FAILURE_WEIGHT = 0.5
"""Discount on failure evidence against a chance: seeing the object
elsewhere during the window is ambiguous (already returned, moved by
something else), seeing it at the destination is not."""

REST_PRIOR_COUNT = 3.0
"""Pseudo-sightings on a stated rest receptacle. Half a day of
room-visit sightings elsewhere outvotes it."""

REST_HALF_LIFE_H = 72.0
"""Decay half-life of real sightings in the rest estimate: rest
locations are stable, so remember days, not hours."""

START_HOUR_PRIOR_SD_H = 1.5
"""Prior sd on a stated start hour ("dinner around 19:30" means it)."""

START_OBS_SD_H = 0.75
"""Assumed sd of one confirming sighting's time around the true start."""

START_GATE_SD_H = 1.5
"""How far from the current start estimate a confirming sighting still
teaches about the START. A sighting deep inside the window says the
activity is ongoing, not when it began; without this gate, midday
sightings of an all-day activity drag the fitted start toward noon and
erode the window that explained them. The update weight is scaled by
``exp(-((hour - mu) / gate)^2 / 2)``."""

WINDOW_EDGE_SD_H = 0.5
"""Base softness of the active window's edges, added in quadrature to
the start-hour posterior sd."""

MAX_DISPLACED_MASS = 0.95
"""Cap on total activity-displaced probability, so the rest location is
never impossible."""

MIN_WINDOW_WEIGHT = 0.05
"""In-window probability below which a sighting teaches a rule nothing
(skip the Beta/start-hour update rather than accumulate noise)."""

WEEKEND_DAYS = (5, 6)
"""``day_index % 7`` of Saturday and Sunday (day 0 = Monday)."""

DAY_KINDS = ("weekday", "weekend", "both")
AFTER_KINDS = ("returned", "left")
CLASS_PREFIX = "class:"
_MATCHING_DAYS = {"weekday": 5.0, "weekend": 2.0, "both": 7.0}
_SQRT2 = math.sqrt(2.0)


class HypothesisValidationError(ValueError):
    """A hypothesis referenced strings outside the valid vocabulary.

    ``bad_strings`` lists the exact offending values, because the
    elicitation repair round names them verbatim back to the LLM."""

    def __init__(self, message: str, bad_strings: Sequence[str]) -> None:
        super().__init__(f"{message}: {sorted(set(bad_strings))}")
        self.bad_strings: Tuple[str, ...] = tuple(sorted(set(bad_strings)))


@dataclasses.dataclass(frozen=True)
class MoveRule:
    """During its activity, ``targets`` are at ``to`` with the labelled
    chance; ``after`` says whether they go back to rest when it ends."""

    targets: Tuple[str, ...]     # resolved object_ids, never classes
    raw_target: str              # what the description said (id or class:x)
    to: str
    chance: str                  # key of ORDINAL_CENTERS
    after: str                   # "returned" | "left"


@dataclasses.dataclass(frozen=True)
class Activity:
    name: str
    days: str                    # "weekday" | "weekend" | "both"
    frequency_per_week: float    # times per week, on matching days
    start_hour: float            # local hour of day, 0-24
    duration_h: float
    moves: Tuple[MoveRule, ...]

    def occurrence_probability(self) -> float:
        """P(the activity happens on one matching day), from the stated
        weekly frequency over the matching-day count."""
        return max(0.0, min(1.0, self.frequency_per_week
                            / _MATCHING_DAYS[self.days]))

    def matches_day(self, day_index: int) -> bool:
        weekend = day_index % 7 in WEEKEND_DAYS
        return (self.days == "both" or (self.days == "weekend") == weekend)


@dataclasses.dataclass(frozen=True)
class Hypothesis:
    """One validated household description, IDs fully resolved."""

    hypothesis_id: str
    rationale: str
    rest: Mapping[str, str]      # object_id -> receptacle_id
    activities: Tuple[Activity, ...]


def _resolve_target(raw: str, object_classes: Mapping[str, str]
                    ) -> Optional[Tuple[str, ...]]:
    """Object ids a target names: the id itself, or every object of a
    ``class:<name>`` target. None when nothing matches (invalid)."""
    if raw.startswith(CLASS_PREFIX):
        cls = raw[len(CLASS_PREFIX):]
        ids = tuple(sorted(o for o, c in object_classes.items() if c == cls))
        return ids or None
    return (raw,) if raw in object_classes else None


def parse_hypothesis(raw: Mapping[str, Any],
                     object_classes: Mapping[str, str],
                     receptacle_ids: Sequence[str]) -> Hypothesis:
    """Validate one raw hypothesis dict against the household vocabulary.

    Strict by design: any object, class, or receptacle string outside
    the tables raises :class:`HypothesisValidationError` carrying the
    exact offending strings — no fuzzy matching anywhere, because a
    guessed correction silently corrupts everything downstream. Shape
    errors (missing fields, unknown labels, out-of-range numbers) raise
    the same type so the repair round handles one failure mode.
    """
    recs = set(receptacle_ids)
    bad: List[str] = []

    def _field(m: Mapping[str, Any], key: str, kind: str) -> Any:
        if key not in m:
            raise HypothesisValidationError(
                f"missing field {key!r} in {kind}", [key])
        return m[key]

    rest: Dict[str, str] = {}
    for target, receptacle in dict(raw.get("rest", {})).items():
        ids = _resolve_target(str(target), object_classes)
        if ids is None:
            bad.append(str(target))
            continue
        if str(receptacle) not in recs:
            bad.append(str(receptacle))
            continue
        for obj in ids:
            rest.setdefault(obj, str(receptacle))

    activities: List[Activity] = []
    for act in raw.get("activities", ()):
        days = str(_field(act, "days", "activity"))
        if days not in DAY_KINDS:
            raise HypothesisValidationError(
                f"activity {act.get('name')!r}: days must be one of "
                f"{DAY_KINDS}", [days])
        try:
            freq = float(_field(act, "frequency_per_week", "activity"))
            start = float(_field(act, "start_hour", "activity"))
            duration = float(_field(act, "duration_h", "activity"))
        except (TypeError, ValueError):
            raise HypothesisValidationError(
                f"activity {act.get('name')!r}: frequency_per_week, "
                f"start_hour, duration_h must be numbers",
                [str(act.get(k)) for k in ("frequency_per_week",
                                           "start_hour", "duration_h")])
        if not 0.0 <= start < 24.0 or duration <= 0.0 or freq < 0.0:
            raise HypothesisValidationError(
                f"activity {act.get('name')!r}: start_hour in [0, 24), "
                f"duration_h > 0, frequency_per_week >= 0",
                [f"start_hour={start}", f"duration_h={duration}",
                 f"frequency_per_week={freq}"])
        moves: List[MoveRule] = []
        for move in act.get("moves", ()):
            target = str(_field(move, "target", "move"))
            to = str(_field(move, "to", "move"))
            chance = str(_field(move, "chance", "move"))
            after = str(_field(move, "after", "move"))
            if chance not in ORDINAL_CENTERS:
                raise HypothesisValidationError(
                    f"move of {target!r}: chance must be one of "
                    f"{tuple(ORDINAL_CENTERS)}", [chance])
            if after not in AFTER_KINDS:
                raise HypothesisValidationError(
                    f"move of {target!r}: after must be one of "
                    f"{AFTER_KINDS}", [after])
            ids = _resolve_target(target, object_classes)
            if ids is None:
                bad.append(target)
                continue
            if to not in recs:
                bad.append(to)
                continue
            moves.append(MoveRule(targets=ids, raw_target=target, to=to,
                                  chance=chance, after=after))
        activities.append(Activity(
            name=str(act.get("name", f"activity_{len(activities)}")),
            days=days, frequency_per_week=freq, start_hour=start,
            duration_h=duration, moves=tuple(moves)))

    if bad:
        raise HypothesisValidationError(
            "unknown object/class/receptacle ids", bad)
    return Hypothesis(
        hypothesis_id=str(raw.get("hypothesis_id", "h?")),
        rationale=str(raw.get("rationale", "")),
        rest=rest, activities=tuple(activities))


def _phi(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / _SQRT2))


@dataclasses.dataclass
class _RuleState:
    """Learned state of one (activity, move) pair: the chance Beta and a
    backreference; the start-hour posterior lives on _ActivityState."""

    activity_index: int
    rule: MoveRule
    success: float
    failure: float

    @property
    def chance_mean(self) -> float:
        return self.success / (self.success + self.failure)


@dataclasses.dataclass
class _ActivityState:
    """Normal posterior on the activity's start hour."""

    mu: float
    var: float

    def observe(self, hour: float, weight: float) -> None:
        """Conjugate update with one confirming sighting time, its
        precision scaled by ``weight`` (the attribution probability)."""
        obs_var = START_OBS_SD_H ** 2 / max(weight, 1e-9)
        var = 1.0 / (1.0 / self.var + 1.0 / obs_var)
        self.mu = var * (self.mu / self.var + hour / obs_var)
        self.var = var


class HypothesisProgramBelief(BeliefModel):
    """The converter: one :class:`Hypothesis` as a runnable belief.

    ``predict`` composes displaced mass from the hypothesis's rules with
    a rest distribution fitted from off-window sightings (module
    docstring). ``fitted_parameters`` exposes every number the sightings
    moved, so runs can log what the LLM wrote and what the fit made of
    it separately.

    The hypothesis is written against the household's object table, so
    reset reads ``context.object_classes`` to expand class targets —
    the same privileged-but-legitimate access the oracle belief takes:
    the table was in the LLM's prompt, hiding it from the converter
    would be theatre.
    """

    def __init__(self, rng: random.Random,
                 hypothesis_raw: Mapping[str, Any],
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None,
                 frequency_alpha: float = DEFAULT_FREQUENCY_ALPHA) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h,
                         frequency_alpha=frequency_alpha)
        self._raw = dict(hypothesis_raw)
        self._hypothesis: Optional[Hypothesis] = None
        self._rule_states: List[_RuleState] = []
        self._activity_states: List[_ActivityState] = []
        # object_id -> indices into _rule_states
        self._rules_of: Dict[str, List[int]] = {}

    @property
    def name(self) -> str:
        return f"HypothesisProgram({self._raw.get('hypothesis_id', 'h?')})"

    @property
    def hypothesis(self) -> Hypothesis:
        if self._hypothesis is None:
            raise RuntimeError(f"{self.name}: hypothesis before reset()")
        return self._hypothesis

    def reset(self, context) -> None:
        super().reset(context)
        self._hypothesis = parse_hypothesis(
            self._raw, context.object_classes, context.receptacle_ids)
        self._rule_states = []
        self._activity_states = []
        self._rules_of = {}
        for ai, activity in enumerate(self._hypothesis.activities):
            self._activity_states.append(_ActivityState(
                mu=activity.start_hour, var=START_HOUR_PRIOR_SD_H ** 2))
            for rule in activity.moves:
                center = ORDINAL_CENTERS[rule.chance]
                state = _RuleState(
                    activity_index=ai, rule=rule,
                    success=center * CHANCE_PRIOR_STRENGTH,
                    failure=(1.0 - center) * CHANCE_PRIOR_STRENGTH)
                index = len(self._rule_states)
                self._rule_states.append(state)
                for obj in rule.targets:
                    self._rules_of.setdefault(obj, []).append(index)

    # ------------------------------------------------------------- windows

    def _window_probability(self, state: _RuleState, t: int) -> float:
        """P(the rule's object is displaced at ``t`` | activity happened
        today): Gaussian-edged membership of the active window."""
        activity = self.hypothesis.activities[state.activity_index]
        if not activity.matches_day(t // DAY_SECONDS):
            return 0.0
        hour = (t % DAY_SECONDS) / 3600.0
        post = self._activity_states[state.activity_index]
        sd = math.sqrt(post.var + WINDOW_EDGE_SD_H ** 2)
        rise = _phi((hour - post.mu) / sd)
        if state.rule.after == "left":
            return rise  # out until midnight; back at rest next morning
        fall = _phi((hour - (post.mu + activity.duration_h)) / sd)
        return rise * (1.0 - fall)

    def _displacement(self, state: _RuleState, t: int) -> float:
        """P(object at the rule's destination because of this rule)."""
        activity = self.hypothesis.activities[state.activity_index]
        return (activity.occurrence_probability()
                * self._window_probability(state, t) * state.chance_mean)

    # ------------------------------------------------------------ learning

    def _add_sighting(self, object_id: str, t: int,
                      receptacle_id: str) -> None:
        super()._add_sighting(object_id, t, receptacle_id)
        if self._hypothesis is None:
            return
        hour = (t % DAY_SECONDS) / 3600.0
        for index in self._rules_of.get(object_id, ()):
            state = self._rule_states[index]
            activity = self.hypothesis.activities[state.activity_index]
            weight = (activity.occurrence_probability()
                      * self._window_probability(state, t))
            if weight < MIN_WINDOW_WEIGHT:
                continue
            if receptacle_id == state.rule.to:
                state.success += weight
                post = self._activity_states[state.activity_index]
                gate = math.exp(-0.5 * ((hour - post.mu)
                                        / START_GATE_SD_H) ** 2)
                if gate > 1e-3:
                    post.observe(hour, weight * gate)
            else:
                state.failure += weight * FAILURE_WEIGHT

    # ---------------------------------------------------------- prediction

    def _rest_distribution(self, object_id: str,
                           history: List[Tuple[int, str]],
                           t: int) -> Dict[str, float]:
        """Dirichlet mean over receptacles: the stated rest's pseudo-count
        plus decayed off-window sightings (a sighting explained by a rule
        counts toward rest only with its unexplained share)."""
        counts: Dict[str, float] = {}
        stated = self.hypothesis.rest.get(object_id)
        if stated is not None:
            counts[stated] = REST_PRIOR_COUNT
        half_life_s = REST_HALF_LIFE_H * 3600.0
        for ot, receptacle in history:
            explained = max(
                (self._displacement(self._rule_states[i], ot)
                 for i in self._rules_of.get(object_id, ())
                 if self._rule_states[i].rule.to == receptacle),
                default=0.0)
            decay = 2.0 ** (-max(0, t - ot) / half_life_s)
            counts[receptacle] = (counts.get(receptacle, 0.0)
                                  + (1.0 - explained) * decay)
        return self.dirichlet_mean(counts)

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        rule_indices = self._rules_of.get(object_id, ())
        stated_rest = self.hypothesis.rest.get(object_id)
        if not rule_indices and stated_rest is None:
            # Not covered by the description: base statistical behaviour.
            if history:
                counts = self._weighted_counts(
                    history, t, REST_HALF_LIFE_H * 3600.0)
                return self.dirichlet_normalized(counts, history)
            return self._cold_start(object_id, t)
        displaced: Dict[str, float] = {}
        for index in rule_indices:
            state = self._rule_states[index]
            p = self._displacement(state, t)
            displaced[state.rule.to] = displaced.get(state.rule.to, 0.0) + p
        total = sum(displaced.values())
        if total > MAX_DISPLACED_MASS:
            scale = MAX_DISPLACED_MASS / total
            displaced = {r: p * scale for r, p in displaced.items()}
            total = MAX_DISPLACED_MASS
        rest = self._rest_distribution(object_id, history, t)
        dist = {r: (1.0 - total) * p for r, p in rest.items()}
        for receptacle, p in displaced.items():
            dist[receptacle] = dist.get(receptacle, 0.0) + p
        return self._frequency_prediction(dist, history)

    # ----------------------------------------------------------- reporting

    def fitted_parameters(self) -> Dict[str, Any]:
        """Every number the sightings moved, next to what was stated —
        the converter's half of the two-sided log the run keeps."""
        rules = []
        for state in self._rule_states:
            activity = self.hypothesis.activities[state.activity_index]
            rules.append({
                "activity": activity.name,
                "target": state.rule.raw_target,
                "to": state.rule.to,
                "stated_chance": state.rule.chance,
                "prior_chance": ORDINAL_CENTERS[state.rule.chance],
                "fitted_chance": state.chance_mean,
                "evidence": state.success + state.failure
                - CHANCE_PRIOR_STRENGTH})
        starts = [{
            "activity": activity.name,
            "stated_start_hour": activity.start_hour,
            "fitted_start_hour": post.mu,
            "posterior_sd_h": math.sqrt(post.var)}
            for activity, post in zip(self.hypothesis.activities,
                                      self._activity_states)]
        return {"hypothesis_id": self.hypothesis.hypothesis_id,
                "rules": rules, "start_hours": starts}
