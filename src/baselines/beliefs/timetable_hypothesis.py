"""Timetable hypotheses: the LLM authors a full weekly model per object
(or class) as ordered BLOCKS, with no rest state.

The tree/graph/flat arms all write "rest map + activity moves": a
default location and a few displacements. The treeLongLeaf arm drops
the default. A hypothesis says, for each target it covers, where the
object is across the week as a list of blocks::

    {"days": "weekday" | "weekend" | "both", "from": 8.5, "to": 17.5,
     "at": "<receptacle id>", "chance": "rarely|sometimes|usually|almost_always"}

Later blocks override earlier ones ("at the desk all day; 9-17 out"
is two blocks in that order). Hours no block covers fall through to
the robot's own sighting statistics for that object (the same fallback
the flat converter uses for an object it never mentions). Class targets
(``class:mug``) apply to every object of the class, including objects
registered after the hypothesis was written.

What the sightings refine: each block's chance is a Beta with the
label's prior (:data:`~baselines.beliefs.hypothesis_program.
CHANCE_PRIOR_STRENGTH`), updated by sightings inside the block — a
sighting at ``at`` is a success, one elsewhere a discounted failure —
with credit shared down the priority stack (a lower block learns only
from the probability that reaches it). And each block's WHERE is a
Dirichlet: the stated ``at`` enters as a decaying pseudo-count
(:data:`~baselines.beliefs.hypothesis_program.REST_PRIOR_COUNT`, the
rest map's rule) and every sighting inside the block's hours adds to
the receptacle it was at, so a block that says "usually the counter"
for an object that in fact cycles counter / sink / table learns that
split within days — a document is a time-conditioned frequency model
whose starting counts are the author's, never a worse one than plain
frequency counts. (Without this, the first library run sank every
document under the statistical particle by day 3.) Block edges are soft
(:data:`EDGE_SD_H`) and fixed: the hours are the author's. An away
block (OUT_OF_HOUSE / ON_PERSON) earns :data:`~baselines.beliefs.
hypothesis_program.ABSENCE_SUCCESS_CREDIT` from an empty look at the
receptacle the block overrides — where the object would be if it were
not away.

Prediction at ``t``: walk the matching blocks from the highest
priority down; block ``b`` claims ``edge(b, t) * chance(b)`` of what
reaches it; the remainder reaches the next block; what reaches the
bottom goes to the fallback. So a hypothesis is a complete, readable
answer to "where is X at hour h on a weekday", and every number in it
is one the sightings can move.
"""

from __future__ import annotations

import dataclasses
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.hypothesis_program import (
    ABSENCE_SUCCESS_CREDIT, AWAY_DESTINATIONS, CHANCE_PRIOR_STRENGTH,
    CHECK_DIRECTIONS, CLASS_PREFIX, DAY_KINDS, FAILURE_WEIGHT, ORDINAL_CENTERS,
    REST_HALF_LIFE_H, REST_PRIOR_COUNT, REST_PRIOR_HALF_LIFE_H,
    DistinguishingCheck, Hypothesis, HypothesisProgramBelief,
    HypothesisValidationError, _phi, _resolve_target)
def _is_weekend(day_index: int) -> bool:
    """Saturday / Sunday under the bank's day-0 weekday (protocol_text keeps
    it; banks without one keep the old day 0 = Monday convention)."""
    from baselines.llm_hypotheses.protocol_text import weekday_index
    return weekday_index(int(day_index)) in (5, 6)


from baselines.types import DAY_SECONDS, Prediction

EDGE_SD_H = 0.5
"""Softness of a block's edges, in hours."""
MIN_BLOCK_WEIGHT = 0.05
import os as _os
INTERIOR_ONLY = float(_os.environ.get("TIMETABLE_INTERIOR_MIN_EDGE", "0"))
"""Variant knob (confidence study): a sighting refines a block's chance and
WHERE only when its edge weight is at least this (0 = the original rule: any
sighting inside the soft window counts). With a patrol on the hour, the pass
at a window's start otherwise re-teaches every in-use window its resting spot."""
PRIOR_DECAYS = _os.environ.get("TIMETABLE_PRIOR_DECAYS", "1") != "0"
"""Variant knob: whether the author's stated spot fades with absolute time
(the original rule) or only against sightings."""
"""Edge weight below which a sighting teaches a block nothing."""
MAX_CLAIMED_MASS = 0.95
"""Cap on the mass the blocks claim together, so the fallback (and the
floor) always keep a share: a hypothesis is never certain."""


@dataclasses.dataclass(frozen=True)
class Block:
    days: str
    start: float
    end: float
    at: str
    chance: str

    def matches_day(self, day_index: int) -> bool:
        weekend = _is_weekend(day_index)
        return self.days == "both" or (self.days == "weekend") == weekend

    def edge_weight(self, t: int) -> float:
        """Soft membership of the instant in [start, end)."""
        if not self.matches_day(t // DAY_SECONDS):
            return 0.0
        hour = (t % DAY_SECONDS) / 3600.0
        rise = _phi((hour - self.start) / EDGE_SD_H) if self.start > 0 else 1.0
        fall = _phi((hour - self.end) / EDGE_SD_H) if self.end < 24 else 0.0
        return rise * (1.0 - fall)

    def label(self) -> str:
        return f"{self.days} {self.start:g}-{self.end:g}h"


@dataclasses.dataclass(frozen=True)
class Claim:
    """A falsifiable statement the document makes: between ``start`` and
    ``end`` on ``days``, ``target`` is at ``expect`` — an in-home
    receptacle, or an away token. Resolution (:func:`resolve_claim`):
    an in-home claim is FOR when a look at ``expect`` finds the target,
    AGAINST when that look is empty or the target is sighted anywhere
    else; an away claim is AGAINST when the target is sighted anywhere
    in the house, and WEAKLY FOR (half weight) when a look at the
    receptacle the document would otherwise put it at finds nothing."""

    text: str
    target: str
    expect: str
    days: str
    start: float
    end: float

    def in_window(self, t: int) -> bool:
        day = t // DAY_SECONDS
        weekend = _is_weekend(day)
        if self.days == "weekday" and weekend:
            return False
        if self.days == "weekend" and not weekend:
            return False
        hour = (t % DAY_SECONDS) / 3600.0
        return self.start <= hour < self.end


def resolve_claim(claim: Claim, looks: Sequence[Tuple[int, str, Tuple[str, ...]]],
                  underlying: Optional[str] = None) -> List[Tuple[int, float]]:
    """``(t, score)`` per resolving look: +1 for, -1 against, +0.5 weak
    for. ``underlying`` is where the document puts the target when it is
    in the house (used by away claims)."""
    out: List[Tuple[int, float]] = []
    away = claim.expect in AWAY_DESTINATIONS
    for t, receptacle, contents in looks:
        if not claim.in_window(t):
            continue
        seen_here = claim.target in contents
        if away:
            if seen_here:
                out.append((t, -1.0))
            elif underlying is not None and receptacle == underlying:
                out.append((t, 0.5))
            continue
        if receptacle == claim.expect:
            out.append((t, 1.0 if seen_here else -1.0))
        elif seen_here:
            out.append((t, -1.0))
    return out


@dataclasses.dataclass(frozen=True)
class TimetableHypothesis(Hypothesis):
    """A :class:`Hypothesis` whose content is ``targets`` (raw target ->
    blocks in priority order) instead of rest + activities; the base
    fields stay so the mixture's report code reads it unchanged."""

    targets: Mapping[str, Tuple[Block, ...]] = dataclasses.field(
        default_factory=dict)
    resolved: Mapping[str, Tuple[str, ...]] = dataclasses.field(
        default_factory=dict)      # raw target -> object ids at parse time
    claims: Tuple[Claim, ...] = ()

    def covered_objects(self) -> frozenset:
        out = set()
        for ids in self.resolved.values():
            out.update(ids)
        return frozenset(out)


def parse_timetable(raw: Mapping[str, Any], object_classes: Mapping[str, str],
                    receptacle_ids: Sequence[str],
                    unsensable: Sequence[str] = ()) -> TimetableHypothesis:
    """Strict validation of ``{"targets": {...}, "distinguishing_check":
    {...}}`` plus the id/prose fields, in the caller's vocabulary. Every
    unknown string is reported verbatim (:class:`HypothesisValidationError`)."""
    recs = set(receptacle_ids)
    bad: List[str] = []
    targets_raw = raw.get("targets")
    if not isinstance(targets_raw, Mapping) or not targets_raw:
        raise HypothesisValidationError(
            "`targets` must map object ids or class:<name> to a non-empty "
            "list of blocks", ["targets"])
    targets: Dict[str, Tuple[Block, ...]] = {}
    resolved: Dict[str, Tuple[str, ...]] = {}
    for target, blocks_raw in targets_raw.items():
        target = str(target)
        ids = _resolve_target(target, object_classes)
        if ids is None:
            bad.append(target)
            continue
        if not isinstance(blocks_raw, (list, tuple)) or not blocks_raw:
            raise HypothesisValidationError(
                f"target {target!r}: blocks must be a non-empty list",
                [target])
        blocks: List[Block] = []
        for b in blocks_raw:
            if not isinstance(b, Mapping):
                raise HypothesisValidationError(
                    f"target {target!r}: each block is an object", [str(b)[:60]])
            days = str(b.get("days", "both"))
            if days not in DAY_KINDS:
                raise HypothesisValidationError(
                    f"target {target!r}: days must be one of {DAY_KINDS}", [days])
            try:
                start = float(b.get("from", 0.0))
                end = float(b.get("to", 24.0))
            except (TypeError, ValueError):
                raise HypothesisValidationError(
                    f"target {target!r}: from/to must be numbers",
                    [str(b.get("from")), str(b.get("to"))])
            if not (0.0 <= start < end <= 24.0):
                raise HypothesisValidationError(
                    f"target {target!r}: 0 <= from < to <= 24",
                    [f"from={start:g}", f"to={end:g}"])
            chance = str(b.get("chance", ""))
            if chance not in ORDINAL_CENTERS:
                raise HypothesisValidationError(
                    f"target {target!r}: chance must be one of "
                    f"{tuple(ORDINAL_CENTERS)}", [chance])
            at = str(b.get("at", ""))
            if at not in recs:
                bad.append(at)
                continue
            blocks.append(Block(days=days, start=start, end=end, at=at,
                                chance=chance))
        targets[target] = tuple(blocks)
        resolved[target] = ids
    claims: List[Claim] = []
    for c in raw.get("claims") or ():
        if not isinstance(c, Mapping):
            raise HypothesisValidationError("each claim is an object",
                                            [str(c)[:60]])
        target = str(c.get("target", ""))
        expect = str(c.get("expect", ""))
        days = str(c.get("days", "both"))
        ids = _resolve_target(target, object_classes)
        if ids is None or len(ids) != 1:
            bad.append(target)
            continue
        if expect not in recs:
            bad.append(expect)
            continue
        if days not in DAY_KINDS:
            raise HypothesisValidationError(
                f"claim {c.get('claim', '')!r}: days in weekday|weekend|both",
                [days])
        try:
            start = float(c.get("from", 0.0)); end = float(c.get("to", 24.0))
        except (TypeError, ValueError):
            raise HypothesisValidationError(
                f"claim {c.get('claim', '')!r}: from/to must be numbers",
                [str(c.get("from")), str(c.get("to"))])
        if not (0.0 <= start < end <= 24.0):
            raise HypothesisValidationError(
                f"claim {c.get('claim', '')!r}: 0 <= from < to <= 24",
                [f"from={start:g}", f"to={end:g}"])
        claims.append(Claim(text=str(c.get("claim", "")), target=ids[0],
                            expect=expect, days=days, start=start, end=end))
    check: Optional[DistinguishingCheck] = None
    raw_check = raw.get("distinguishing_check")
    if not raw_check and claims:
        # The first in-home claim doubles as the legacy check, so the
        # mixture's check-outcome machinery keeps working.
        first = next((c for c in claims if c.expect not in AWAY_DESTINATIONS), None)
        if first is not None:
            check = DistinguishingCheck(
                target=first.target, at=first.expect, days=first.days,
                hour=(first.start + first.end) / 2.0, if_seen="right")
    if isinstance(raw_check, Mapping) and raw_check:
        target = str(raw_check.get("target", ""))
        at = str(raw_check.get("at", ""))
        days = str(raw_check.get("days", "both"))
        if_seen = str(raw_check.get("if_seen", "right"))
        ids = _resolve_target(target, object_classes)
        if ids is None or len(ids) != 1:
            bad.append(target)
        elif at not in recs:
            bad.append(at)
        elif at in set(unsensable):
            raise HypothesisValidationError(
                f"distinguishing_check.at must be a receptacle a look can "
                f"resolve, not {at}", [at])
        elif days not in DAY_KINDS or if_seen not in CHECK_DIRECTIONS:
            raise HypothesisValidationError(
                "distinguishing_check: days in weekday|weekend|both, "
                "if_seen in right|wrong", [days, if_seen])
        else:
            try:
                hour = float(raw_check.get("hour"))
            except (TypeError, ValueError):
                raise HypothesisValidationError(
                    "distinguishing_check.hour must be a number",
                    [str(raw_check.get("hour"))])
            check = DistinguishingCheck(target=ids[0], at=at, days=days,
                                        hour=hour, if_seen=if_seen)
    if bad:
        raise HypothesisValidationError(
            "unknown object/class/receptacle ids", bad)
    return TimetableHypothesis(
        hypothesis_id=str(raw.get("hypothesis_id", "h?")),
        rationale=str(raw.get("prose", raw.get("rationale", ""))),
        rest={}, activities=(),
        distinguishing_prediction=str(raw.get("title", "")),
        distinguishing_check=check, targets=targets, resolved=resolved,
        claims=tuple(claims))


@dataclasses.dataclass
class _BlockState:
    target: str          # raw target
    block: Block
    success: float
    failure: float
    priority: int        # index within the target's list (higher wins)
    where: Dict[str, Dict[str, List[Tuple[int, float]]]] = dataclasses.field(
        default_factory=dict)
    """Per object the block covers: receptacle -> [(t, weight)] of
    sightings inside the block's hours, for the where-Dirichlet."""

    @property
    def chance_mean(self) -> float:
        return self.success / (self.success + self.failure)

    def where_distribution(self, object_id: str, t: int,
                           dirichlet_mean) -> Dict[str, float]:
        counts: Dict[str, float] = {
            self.block.at: REST_PRIOR_COUNT * (2.0 ** (
                -max(0, t) / (REST_PRIOR_HALF_LIFE_H * 3600.0)) if PRIOR_DECAYS else 1.0)}
        half = REST_HALF_LIFE_H * 3600.0
        for receptacle, rows in self.where.get(object_id, {}).items():
            for ot, w in rows:
                counts[receptacle] = (counts.get(receptacle, 0.0)
                                      + w * 2.0 ** (-max(0, t - ot) / half))
        return dirichlet_mean(counts)


class TimetableBelief(HypothesisProgramBelief):
    """One timetable hypothesis as a particle. Subclasses the program
    belief so the mixture's ``isinstance`` checks and report code apply;
    everything the program belief did with rest and activities is
    replaced here."""

    def reset(self, context) -> None:
        # Skip the program belief's reset (it parses rest/activities);
        # run the base belief's, then our own parse.
        super(HypothesisProgramBelief, self).reset(context)
        table = (self._vocabulary if self._vocabulary is not None
                 else context.object_classes)
        self._hypothesis = parse_timetable(
            self._raw, table, context.receptacle_ids,
            unsensable=tuple(context.unsensable_receptacle_ids))
        self._states: List[_BlockState] = []
        self._states_of: Dict[str, List[int]] = {}     # object -> indices
        self._tour_times = set()
        self._rule_states = []                         # unused; kept for isinstance callers
        for target, blocks in self.hypothesis.targets.items():
            for priority, block in enumerate(blocks):
                center = ORDINAL_CENTERS[block.chance]
                self._states.append(_BlockState(
                    target=target, block=block,
                    success=center * CHANCE_PRIOR_STRENGTH,
                    failure=(1.0 - center) * CHANCE_PRIOR_STRENGTH,
                    priority=priority))
                index = len(self._states) - 1
                for obj in self.hypothesis.resolved[target]:
                    self._states_of.setdefault(obj, []).append(index)

    @property
    def hypothesis(self) -> TimetableHypothesis:   # type: ignore[override]
        if self._hypothesis is None:
            raise RuntimeError(f"{self.name}: hypothesis before reset()")
        return self._hypothesis   # type: ignore[return-value]

    def _register_object(self, object_id: str, object_class: str) -> None:
        super(HypothesisProgramBelief, self)._register_object(object_id,
                                                              object_class)
        if self._hypothesis is None or not object_class:
            return
        wanted = CLASS_PREFIX + object_class
        for index, state in enumerate(self._states):
            if state.target == wanted and index not in self._states_of.get(
                    object_id, []):
                self._states_of.setdefault(object_id, []).append(index)

    # ---------------------------------------------------------- stacking

    def _stack(self, object_id: str, t: int) -> List[Tuple[int, float]]:
        """Matching block indices for the object at ``t``, highest
        priority first, each with the share of probability that reaches
        it. Targets are stacked in the order they were declared, blocks
        within a target by position; the object's own id outranks its
        class."""
        indices = self._states_of.get(object_id, ())
        own = [i for i in indices if not self._states[i].target.startswith(CLASS_PREFIX)]
        cls = [i for i in indices if self._states[i].target.startswith(CLASS_PREFIX)]
        ordered = sorted(own, key=lambda i: -self._states[i].priority) + \
            sorted(cls, key=lambda i: -self._states[i].priority)
        out: List[Tuple[int, float]] = []
        reach = 1.0
        for i in ordered:
            w = self._states[i].block.edge_weight(t)
            if w < MIN_BLOCK_WEIGHT:
                continue
            out.append((i, reach))
            reach *= 1.0 - w * self._states[i].chance_mean
        return out

    def _underlying(self, object_id: str, index: int, t: int) -> Optional[str]:
        """The in-home receptacle the block at ``index`` overrides at
        ``t``: the next matching non-away block down the stack."""
        below = False
        for i, _ in self._stack(object_id, t):
            if i == index:
                below = True
                continue
            if below and self._states[i].block.at not in AWAY_DESTINATIONS:
                return self._states[i].block.at
        return None

    # ------------------------------------------------------------ learning

    def update(self, evidence) -> None:
        if getattr(evidence, "source", None) == "initial_tour":
            self._tour_times.add(evidence.t)
        if self._hypothesis is not None and hasattr(evidence, "contents"):
            self._credit_absence(evidence.receptacle_id,
                                 set(evidence.contents), evidence.t)
        super(HypothesisProgramBelief, self).update(evidence)

    def _credit_absence(self, receptacle_id: str, present: set,
                        t: int) -> None:
        for obj in list(self._states_of):
            if obj in present:
                continue
            for index, reach in self._stack(obj, t):
                state = self._states[index]
                if state.block.at not in AWAY_DESTINATIONS:
                    continue
                if self._underlying(obj, index, t) == receptacle_id:
                    w = state.block.edge_weight(t) * reach
                    state.success += ABSENCE_SUCCESS_CREDIT * w

    def _add_sighting(self, object_id: str, t: int,
                      receptacle_id: str) -> None:
        super(HypothesisProgramBelief, self)._add_sighting(object_id, t,
                                                           receptacle_id)
        if self._hypothesis is None:
            return
        for index, reach in self._stack(object_id, t):
            state = self._states[index]
            w = state.block.edge_weight(t) * reach
            if w < MIN_BLOCK_WEIGHT or state.block.edge_weight(t) < INTERIOR_ONLY:
                continue
            if receptacle_id == state.block.at:
                state.success += w
            else:
                state.failure += w * FAILURE_WEIGHT
            state.where.setdefault(object_id, {}).setdefault(
                receptacle_id, []).append((t, w))

    # ---------------------------------------------------------- prediction

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        stack = self._stack(object_id, t)
        if not stack:
            if history:
                counts = self._weighted_counts(history, t,
                                               REST_HALF_LIFE_H * 3600.0)
                return self.dirichlet_normalized(counts, history)
            return self._cold_start(object_id, t)
        claimed: Dict[str, float] = {}
        reach = 1.0
        for index, _ in stack:
            state = self._states[index]
            m = state.block.edge_weight(t) * state.chance_mean
            for receptacle, p in state.where_distribution(
                    object_id, t, self.dirichlet_mean).items():
                claimed[receptacle] = claimed.get(receptacle, 0.0) + reach * m * p
            reach *= 1.0 - m
        total = sum(claimed.values())
        if total > MAX_CLAIMED_MASS:
            scale = MAX_CLAIMED_MASS / total
            claimed = {r: p * scale for r, p in claimed.items()}
            total = MAX_CLAIMED_MASS
        if history:
            counts = self._weighted_counts(history, t, REST_HALF_LIFE_H * 3600.0)
            fallback = self.dirichlet_mean(counts)
        else:
            fallback = self._cold_start(object_id, t).distribution
        dist = {r: (1.0 - total) * p for r, p in fallback.items()}
        for r, p in claimed.items():
            dist[r] = dist.get(r, 0.0) + p
        return self._frequency_prediction(dist, history)

    def underlying_receptacle(self, object_id: str, t: int) -> Optional[str]:
        """Where the document puts the object when it is in the house at
        ``t``: the highest-priority matching in-home block."""
        for i, _ in self._stack(object_id, t):
            if self._states[i].block.at not in AWAY_DESTINATIONS:
                return self._states[i].block.at
        return None

    def claim_tallies(self, looks: Sequence[Tuple[int, str, Tuple[str, ...]]]
                      ) -> List[Dict[str, Any]]:
        """Per claim: for / against / weak-for counts over the look log."""
        out = []
        for claim in self.hypothesis.claims:
            rows = []
            for t, receptacle, contents in looks:
                if not claim.in_window(t):
                    continue
                under = (self.underlying_receptacle(claim.target, t)
                         if claim.expect in AWAY_DESTINATIONS else None)
                rows += resolve_claim(claim, [(t, receptacle, contents)], under)
            out.append({"claim": claim.text, "target": claim.target,
                        "expect": claim.expect, "days": claim.days,
                        "from": claim.start, "to": claim.end,
                        "for": sum(1 for _, s in rows if s == 1.0),
                        "against": sum(1 for _, s in rows if s == -1.0),
                        "weak_for": sum(1 for _, s in rows if s == 0.5)})
        return out

    def explain(self, object_id: str, t: int) -> str:
        stack = self._stack(object_id, t)
        if not stack:
            return "fallback"
        top = self._states[stack[0][0]]
        return f"block {top.target} {top.block.label()} -> {top.block.at}"

    def fitted_parameters(self) -> Dict[str, Any]:
        """Every block's stated and fitted chance, in the shape the
        mixture's rules-held/failed report reads."""
        rules = []
        for state in self._states:
            rules.append({
                "activity": state.block.label(),
                "target": state.target, "to": state.block.at,
                "stated_chance": state.block.chance,
                "duration_h": state.block.end - state.block.start,
                "prior_chance": ORDINAL_CENTERS[state.block.chance],
                "fitted_chance": state.chance_mean,
                "evidence": state.success + state.failure
                - CHANCE_PRIOR_STRENGTH})
        return {"hypothesis_id": self.hypothesis.hypothesis_id,
                "rules": rules, "start_hours": []}


__all__ = ["Block", "Claim", "EDGE_SD_H", "MAX_CLAIMED_MASS",
           "MIN_BLOCK_WEIGHT", "TimetableBelief", "TimetableHypothesis",
           "parse_timetable", "resolve_claim"]
