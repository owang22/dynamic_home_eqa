"""Belief-model registry: every buildable belief, tagged by panel status.

The healthcheck's instrument panel is FROZEN: its membership, thresholds,
and the 24 h count half-life are fixed so gate verdicts stay comparable
across banks and time. New belief models therefore register here as
``candidate`` members: they are buildable from configs and runnable in the
bake-off, but the healthcheck refuses to run any belief whose registry tag
is not ``frozen`` (asserted at panel-construction time, see
:func:`assert_frozen_panel`).

``build_belief`` in :mod:`baselines.cli` delegates to this registry, so a
model registered here is immediately available to every entry point
without further wiring.
"""

from __future__ import annotations

import dataclasses
import random
from typing import Any, Callable, Dict, Mapping, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.beliefs.daytype_mixture import (DaytypeMixture,
                                               DaytypeMixtureConfig)
from baselines.beliefs.hierarchy_backoff import (HierarchyBackoff,
                                                 HierarchyBackoffConfig)
from baselines.beliefs.last_observation import LastObservation
from baselines.beliefs.markov1 import Markov1, Markov1Config
from baselines.beliefs.most_frequent import MostFrequentLocation
from baselines.beliefs.periodic_persistence import (PeriodicPersistence,
                                                    PeriodicPersistenceConfig)
from baselines.beliefs.timetable import TimetableConfig, TimetableLookup

PANEL_TAGS = ("frozen", "candidate")
"""Legal panel tags: ``frozen`` members may appear in the healthcheck's
instrument panel; ``candidate`` members may not."""

_Builder = Callable[[Dict[str, Any], random.Random], BeliefModel]


@dataclasses.dataclass(frozen=True)
class BeliefEntry:
    """One registered belief model: its panel tag and its builder."""

    name: str
    panel: str            # "frozen" | "candidate"
    build: _Builder

    def __post_init__(self) -> None:
        if self.panel not in PANEL_TAGS:
            raise ValueError(
                f"BeliefEntry({self.name}): panel {self.panel!r} "
                f"not in {PANEL_TAGS}")


def _optional_half_life(spec: Dict[str, Any]) -> float | None:
    raw = spec.get("half_life_h")
    return None if raw is None else float(raw)


def _floor(spec: Dict[str, Any]) -> float:
    return float(spec.get("exclusion_floor", 0.0))


def _build_last_observation(spec: Dict[str, Any],
                            rng: random.Random) -> BeliefModel:
    return LastObservation(rng, exclusion_floor=_floor(spec))


def _build_most_frequent(spec: Dict[str, Any],
                         rng: random.Random) -> BeliefModel:
    return MostFrequentLocation(rng, exclusion_floor=_floor(spec),
                                half_life_h=_optional_half_life(spec))


def _build_timetable(spec: Dict[str, Any], rng: random.Random) -> BeliefModel:
    cfg = TimetableConfig(bin_hours=int(spec.get("bin_hours", 1)),
                          day_scheme=str(spec.get("day_scheme", "all")))
    return TimetableLookup(rng, cfg, exclusion_floor=_floor(spec),
                           half_life_h=_optional_half_life(spec))


def _build_markov1(spec: Dict[str, Any], rng: random.Random) -> BeliefModel:
    cfg = Markov1Config(
        alpha=float(spec.get("alpha", Markov1Config.alpha)),
        mixing_cutoff_h=float(spec.get("mixing_cutoff_h",
                                       Markov1Config.mixing_cutoff_h)),
        half_life_h=float(spec.get("half_life_h", Markov1Config.half_life_h)))
    return Markov1(rng, cfg, exclusion_floor=_floor(spec))


def _build_periodic_persistence(spec: Dict[str, Any],
                                rng: random.Random) -> BeliefModel:
    d = PeriodicPersistenceConfig
    cfg = PeriodicPersistenceConfig(
        min_departures=int(spec.get("min_departures", d.min_departures)),
        bin_hours=int(spec.get("bin_hours", d.bin_hours)),
        half_life_h=float(spec.get("half_life_h", d.half_life_h)))
    return PeriodicPersistence(rng, cfg, exclusion_floor=_floor(spec))


def _build_daytype_mixture(spec: Dict[str, Any],
                           rng: random.Random) -> BeliefModel:
    d = DaytypeMixtureConfig
    cfg = DaytypeMixtureConfig(
        n_types=int(spec.get("n_types", d.n_types)),
        bin_hours=int(spec.get("bin_hours", d.bin_hours)),
        half_life_h=float(spec.get("half_life_h", d.half_life_h)),
        kmeans_seed=int(spec.get("kmeans_seed", d.kmeans_seed)))
    return DaytypeMixture(rng, cfg, exclusion_floor=_floor(spec))


def _build_hierarchy_backoff(spec: Dict[str, Any],
                             rng: random.Random) -> BeliefModel:
    d = HierarchyBackoffConfig
    cfg = HierarchyBackoffConfig(
        object_pseudocount=float(spec.get("object_pseudocount",
                                          d.object_pseudocount)),
        class_pseudocount=float(spec.get("class_pseudocount",
                                         d.class_pseudocount)),
        half_life_h=float(spec.get("half_life_h", d.half_life_h)))
    return HierarchyBackoff(rng, cfg, exclusion_floor=_floor(spec))


BELIEF_REGISTRY: Mapping[str, BeliefEntry] = {
    entry.name: entry for entry in (
        BeliefEntry("last_observation", "frozen", _build_last_observation),
        BeliefEntry("most_frequent", "frozen", _build_most_frequent),
        BeliefEntry("timetable", "frozen", _build_timetable),
        BeliefEntry("markov1", "candidate", _build_markov1),
        BeliefEntry("periodic_persistence", "candidate",
                    _build_periodic_persistence),
        BeliefEntry("daytype_mixture", "candidate", _build_daytype_mixture),
        BeliefEntry("hierarchy_backoff", "candidate",
                    _build_hierarchy_backoff),
    )
}
"""All buildable belief models, keyed by config name."""

CANDIDATE_SLATE: Tuple[Dict[str, Any], ...] = (
    {"name": "markov1"},
    {"name": "periodic_persistence"},
    {"name": "daytype_mixture"},
    {"name": "hierarchy_backoff"},
)
"""The bake-off candidate belief specs, at their fixed a-priori defaults."""


def build_registered_belief(spec: Dict[str, Any],
                            rng: random.Random) -> BeliefModel:
    """Instantiate a belief model from its config spec via the registry."""
    name = str(spec["name"])
    entry = BELIEF_REGISTRY.get(name)
    if entry is None:
        raise ValueError(f"unknown belief {name!r}; registered: "
                         f"{sorted(BELIEF_REGISTRY)}")
    return entry.build(spec, rng)


def assert_frozen_panel(panel: Tuple[Dict[str, Any], ...]) -> None:
    """Raise unless every panel member is registry-tagged ``frozen``.

    The healthcheck calls this before running: a candidate-tagged belief in
    the instrument panel would silently change what the gates measure, so
    it is a hard error, not a warning.
    """
    for spec in panel:
        name = str(spec["name"])
        entry = BELIEF_REGISTRY.get(name)
        if entry is None:
            raise ValueError(
                f"healthcheck panel member {name!r} is not registered")
        if entry.panel != "frozen":
            raise ValueError(
                f"healthcheck panel member {name!r} is tagged "
                f"{entry.panel!r}; the instrument panel is frozen and may "
                f"only contain frozen-tagged beliefs")
