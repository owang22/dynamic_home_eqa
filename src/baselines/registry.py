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
from baselines.beliefs.expiring_exclusion import \
    ExpiringExclusionLastObservation
from baselines.beliefs.hierarchy_backoff import (HierarchyBackoff,
                                                 HierarchyBackoffConfig)
from baselines.beliefs.last_observation import LastObservation
from baselines.beliefs.llm_belief import (LLMBelief, LLMBeliefConfig,
                                          PromptCache)
from baselines.beliefs.markov1 import Markov1, Markov1Config
from baselines.beliefs.most_frequent import MostFrequentLocation
from baselines.beliefs.periodic_persistence import (PeriodicPersistence,
                                                    PeriodicPersistenceConfig)
from baselines.beliefs.perpetua_belief import (PerpetuaBelief,
                                               PerpetuaConfig,
                                               PerpetuaStarBelief,
                                               PerpetuaStarConfig)
from baselines.beliefs.smoothed_recency import (SmoothedRecency,
                                                SmoothedRecencyConfig)
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


def _build_last_observation_expiring(spec: Dict[str, Any],
                                     rng: random.Random) -> BeliefModel:
    return ExpiringExclusionLastObservation(
        rng, expiry_h=float(spec["expiry_h"]), exclusion_floor=_floor(spec))


def _build_llm(spec: Dict[str, Any], rng: random.Random) -> BeliefModel:
    """The LLM belief answers from a :class:`PromptCache` filled by an
    offline generation run (``baselines.llm_floor``); the driver puts the
    cache object into the spec under ``cache``. Without one the model
    records prompts and answers as LastObs (collect mode)."""
    d = LLMBeliefConfig
    cfg = LLMBeliefConfig(
        model=str(spec.get("model", d.model)),
        max_history=int(spec.get("max_history", d.max_history)),
        max_ranking=int(spec.get("max_ranking", d.max_ranking)),
        geometric_ratio=float(spec.get("geometric_ratio", d.geometric_ratio)),
        hour_bucket_s=int(spec.get("hour_bucket_s", d.hour_bucket_s)))
    cache = spec.get("cache") or PromptCache(collect=True)
    return LLMBelief(rng, cfg, cache, rooms=spec.get("rooms"))


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


def _build_smoothed_recency(spec: Dict[str, Any],
                            rng: random.Random) -> BeliefModel:
    d = SmoothedRecencyConfig
    cfg = SmoothedRecencyConfig(
        smoothing_half_life_h=float(spec.get("smoothing_half_life_h",
                                             d.smoothing_half_life_h)),
        frequency_half_life_h=float(spec.get("frequency_half_life_h",
                                             d.frequency_half_life_h)))
    return SmoothedRecency(rng, cfg, exclusion_floor=_floor(spec))


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


def _perpetua_common(spec: Dict[str, Any], d: Any) -> Dict[str, Any]:
    """Config fields shared by Perpetua and Perpetua*, from the spec."""
    return dict(
        family=str(spec.get("family", d.family)),
        p_m=float(spec.get("p_m", d.p_m)), p_f=float(spec.get("p_f", d.p_f)),
        k_range=tuple(int(k) for k in spec.get("k_range", d.k_range)),
        em_max_iter=int(spec.get("em_max_iter", d.em_max_iter)),
        em_tol=float(spec.get("em_tol", d.em_tol)),
        prune_threshold=float(spec.get("prune_threshold", d.prune_threshold)),
        refit_every_days=int(spec.get("refit_every_days", d.refit_every_days)),
        min_segments=int(spec.get("min_segments", d.min_segments)),
        fallback_median_h=float(spec.get("fallback_median_h",
                                         d.fallback_median_h)),
        eps=float(spec.get("eps", d.eps)))


def _build_perpetua(spec: Dict[str, Any], rng: random.Random) -> BeliefModel:
    d = PerpetuaConfig
    cfg = PerpetuaConfig(
        **_perpetua_common(spec, d),
        delta_low=float(spec.get("delta_low", d.delta_low)),
        delta_high=float(spec.get("delta_high", d.delta_high)),
        num_steps=int(spec.get("num_steps", d.num_steps)))
    return PerpetuaBelief(rng, cfg, exclusion_floor=_floor(spec))


def _build_perpetua_star(spec: Dict[str, Any],
                         rng: random.Random) -> BeliefModel:
    d = PerpetuaStarConfig
    cfg = PerpetuaStarConfig(
        **_perpetua_common(spec, d),
        gamma=float(spec.get("gamma", d.gamma)),
        alpha0_per_h=float(spec.get("alpha0_per_h", d.alpha0_per_h)),
        switching_prior=str(spec.get("switching_prior", d.switching_prior)),
        prior_bin_hours=int(spec.get("prior_bin_hours", d.prior_bin_hours)),
        prior_half_life_h=float(spec.get("prior_half_life_h",
                                         d.prior_half_life_h)),
        prior_pseudocount=float(spec.get("prior_pseudocount",
                                         d.prior_pseudocount)),
        reset_mode=str(spec.get("reset_mode", d.reset_mode)))
    return PerpetuaStarBelief(rng, cfg, exclusion_floor=_floor(spec))


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
        BeliefEntry("smoothed_recency", "candidate",
                    _build_smoothed_recency),
        BeliefEntry("perpetua", "candidate", _build_perpetua),
        BeliefEntry("perpetua_star", "candidate", _build_perpetua_star),
        BeliefEntry("last_observation_expiring", "candidate",
                    _build_last_observation_expiring),
        BeliefEntry("llm", "candidate", _build_llm),
    )
}
"""All buildable belief models, keyed by config name."""

CANDIDATE_SLATE: Tuple[Dict[str, Any], ...] = (
    {"name": "markov1"},
    {"name": "periodic_persistence"},
    {"name": "daytype_mixture"},
    {"name": "hierarchy_backoff"},
    {"name": "smoothed_recency"},
    {"name": "perpetua"},
    {"name": "perpetua_star"},
    {"name": "perpetua_star", "switching_prior": "flat"},
)
"""The bake-off candidate belief specs, at their fixed a-priori defaults.
The second ``perpetua_star`` entry is the flat-switching-prior ablation
(distinct display name ``PerpetuaStarFlat``)."""


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
