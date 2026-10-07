"""Routine-driven query stream: questions triggered by household activities.

Replaces the uniform draw over objects and awake instants with queries
tied to the household profile's activities: people ask where the keys are
shortly BEFORE leaving, where the pot is DURING meal prep. Each activity
may carry one ``query_rule``:

.. code-block:: yaml

    background_query_rate: 6        # per day, uniform over objects/awake time
    rules:
      work_away:
        trigger: before             # or during
        offset_minutes: {mean: 20, sd: 8}   # before: minutes ahead of start
        objects: [keys, wallet, backpack]   # object ids or object classes
        resident_weight: {resident_1: 1.0}  # optional; default all equal
      meal_prep:
        trigger: during
        objects: [pot, pan]

Rules are keyed by activity name and match realized activity blocks from
the timeline's ``residents.jsonl``; a block named ``night_sleep__bed_b2``
matches the rule for ``night_sleep`` (the ``__``-suffix carries the
realizer's location variant, not a different activity). ``objects``
entries resolve against the household inventory: an exact object id, else
every object of that class; entries the household lacks resolve to
nothing, and a rule none of whose entries resolve never fires there.

Each day emits exactly ``questions_per_day`` questions: a background
count drawn from ``background_query_rate`` (small and nonzero by default,
so the stream is not fully predictable), the remainder allocated to
rule-triggered candidates weighted by ``resident_weight``. Days on which
no rule matches any activity fall back to all-background. ``before``
timestamps are ``start - N(mean, sd)`` minutes clamped into the day;
``during`` timestamps are uniform inside the activity block.

Every question carries an ``origin`` (``background`` or
``activity:<name>``) into the bank row, and the bank header records
``query_generation: routine_driven`` — the loader refuses origin-tagged
questions in a bank whose header does not declare its generation scheme.

All bank times are seconds since episode start; ``residents.jsonl``
times are minutes.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import random
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import yaml

from baselines.types import DAY_SECONDS

DEFAULT_BACKGROUND_QUERY_RATE = 6.0
"""Background questions per day when the rules file names none: small
and nonzero, so routine-driven streams keep an unpredictable floor."""

TRIGGERS = ("before", "during")


@dataclasses.dataclass(frozen=True)
class QueryRule:
    """One activity's query rule (see the module docstring)."""

    activity: str
    trigger: str
    objects: Tuple[str, ...]                 # object ids or classes
    offset_mean_min: float = 0.0             # before-trigger lead time
    offset_sd_min: float = 0.0
    resident_weight: Mapping[str, float] = dataclasses.field(
        default_factory=dict)

    def __post_init__(self) -> None:
        if self.trigger not in TRIGGERS:
            raise ValueError(f"query_rule[{self.activity}]: trigger "
                             f"{self.trigger!r} not in {TRIGGERS}")
        if not self.objects:
            raise ValueError(f"query_rule[{self.activity}]: empty objects")
        if self.trigger == "before" and self.offset_sd_min < 0:
            raise ValueError(f"query_rule[{self.activity}]: negative sd")
        if any(w < 0 for w in self.resident_weight.values()):
            raise ValueError(f"query_rule[{self.activity}]: negative "
                             f"resident weight")


@dataclasses.dataclass(frozen=True)
class QueryRuleSet:
    """Every rule plus the background rate, as loaded from YAML."""

    rules: Mapping[str, QueryRule]           # keyed by activity name
    background_query_rate: float = DEFAULT_BACKGROUND_QUERY_RATE

    def __post_init__(self) -> None:
        if self.background_query_rate < 0:
            raise ValueError(f"background_query_rate "
                             f"{self.background_query_rate} must be >= 0")

    def rule_for(self, activity: str) -> Optional[QueryRule]:
        """The rule matching a realized activity block name: exact name
        first, else the base name before a ``__`` variant suffix."""
        rule = self.rules.get(activity)
        if rule is not None:
            return rule
        return self.rules.get(activity.split("__", 1)[0])


def load_query_rules(path: pathlib.Path) -> QueryRuleSet:
    """Parse a rules YAML; unknown keys anywhere are an error."""
    raw = yaml.safe_load(path.read_text())
    unknown = set(raw) - {"rules", "background_query_rate"}
    if unknown:
        raise ValueError(f"{path}: unknown keys {sorted(unknown)}")
    rules: Dict[str, QueryRule] = {}
    for activity, spec in (raw.get("rules") or {}).items():
        bad = set(spec) - {"trigger", "offset_minutes", "objects",
                           "resident_weight"}
        if bad:
            raise ValueError(f"{path}: rule {activity!r} has unknown keys "
                             f"{sorted(bad)}")
        offset = spec.get("offset_minutes") or {}
        rules[str(activity)] = QueryRule(
            activity=str(activity), trigger=str(spec["trigger"]),
            objects=tuple(str(o) for o in spec["objects"]),
            offset_mean_min=float(offset.get("mean", 0.0)),
            offset_sd_min=float(offset.get("sd", 0.0)),
            resident_weight={str(k): float(v) for k, v in
                             (spec.get("resident_weight") or {}).items()})
    rate = float(raw.get("background_query_rate",
                         DEFAULT_BACKGROUND_QUERY_RATE))
    return QueryRuleSet(rules=rules, background_query_rate=rate)


@dataclasses.dataclass(frozen=True)
class ActivityInstance:
    """One realized activity block, in bank seconds."""

    activity: str
    resident: str
    t0: int
    t1: int


def activity_instances(timeline: pathlib.Path) -> List[ActivityInstance]:
    """Realized activity blocks from ``residents.jsonl`` (minutes -> s),
    sorted by start. Empty when the timeline carries none (stub
    timelines): every question then falls back to background."""
    path = timeline / "residents.jsonl"
    if not path.exists():
        return []
    out: List[ActivityInstance] = []
    with open(path) as f:
        for line in f:
            b = json.loads(line)
            out.append(ActivityInstance(
                activity=str(b["activity"]), resident=str(b["resident"]),
                t0=int(b["t0"]) * 60, t1=int(b["t1"]) * 60))
    return sorted(out, key=lambda a: a.t0)


def resolve_objects(entries: Sequence[str],
                    object_classes: Mapping[str, str]) -> Tuple[str, ...]:
    """Expand rule object entries against one household's inventory:
    exact ids stay, class names become every object of that class,
    entries the household lacks vanish."""
    out: List[str] = []
    for entry in entries:
        if entry in object_classes:
            out.append(entry)
        else:
            out.extend(sorted(o for o, c in object_classes.items()
                              if c == entry))
    seen: Dict[str, None] = {}
    for o in out:
        seen.setdefault(o)
    return tuple(seen)


def _instance_weight(rule: QueryRule, instance: ActivityInstance) -> float:
    if not rule.resident_weight:
        return 1.0
    return rule.resident_weight.get(instance.resident, 0.0)


def _background_count(rate: float, cap: int, rng: random.Random) -> int:
    """Integer draw with mean ``rate``: floor plus a Bernoulli fraction,
    capped at the day's question budget."""
    k = int(rate) + (1 if rng.random() < rate - int(rate) else 0)
    return min(k, cap)


def _clamp_to_day(t: int, day: int) -> int:
    return max(day * DAY_SECONDS, min((day + 1) * DAY_SECONDS - 1, t))


def routine_questions(
        instances: Sequence[ActivityInstance],
        rule_set: QueryRuleSet,
        object_classes: Mapping[str, str],
        awake: Mapping[int, List[Tuple[int, int]]],
        n_days: int, first_question_day: int, questions_per_day: int,
        rng: random.Random) -> List[Tuple[str, int, str]]:
    """The full routine-driven stream: ``(object_id, t_query, origin)``
    triples, day by day (see the module docstring for the per-day
    arithmetic). Deterministic given the seeded generator."""
    from baselines.export_bank import draw_time

    all_objects = sorted(object_classes)
    if not all_objects:
        raise ValueError("routine_questions: empty object inventory")
    candidates_by_day: Dict[int, List[Tuple[QueryRule, ActivityInstance,
                                            Tuple[str, ...]]]] = {}
    for instance in instances:
        rule = rule_set.rule_for(instance.activity)
        if rule is None:
            continue
        objects = resolve_objects(rule.objects, object_classes)
        if not objects or _instance_weight(rule, instance) <= 0:
            continue
        day = instance.t0 // DAY_SECONDS
        candidates_by_day.setdefault(day, []).append(
            (rule, instance, objects))

    out: List[Tuple[str, int, str]] = []
    for day in range(first_question_day, n_days):
        candidates = candidates_by_day.get(day, [])
        n_background = _background_count(rule_set.background_query_rate,
                                         questions_per_day, rng)
        if not candidates:
            n_background = questions_per_day
        for _ in range(questions_per_day - n_background):
            weights = [_instance_weight(rule, inst)
                       for rule, inst, _ in candidates]
            rule, instance, objects = rng.choices(candidates,
                                                  weights=weights, k=1)[0]
            obj = rng.choice(objects)
            if rule.trigger == "before":
                offset_s = rng.gauss(rule.offset_mean_min,
                                     rule.offset_sd_min) * 60.0
                t = _clamp_to_day(int(instance.t0 - offset_s), day)
            else:
                t = _clamp_to_day(
                    instance.t0 + rng.randrange(
                        max(1, instance.t1 - instance.t0)), day)
            out.append((obj, t, f"activity:{rule.activity}"))
        for _ in range(n_background):
            t = draw_time(awake.get(day, []), day, rng)
            out.append((rng.choice(all_objects), t, "background"))
    return out
