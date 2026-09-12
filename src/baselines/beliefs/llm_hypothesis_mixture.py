"""HypothesisMixture over LLM-written hypotheses, loaded per household.

The elicitation run (:mod:`baselines.llm_hypotheses`) writes one JSON
file per household into a directory: ``{"hypotheses": [<hypothesis
dict>, ...]}``, already ID-validated against that household's tables.
This model loads ``<dir>/<household_id>.json`` at reset, builds one
:class:`~baselines.beliefs.hypothesis_program.HypothesisProgramBelief`
particle per hypothesis plus the configured statistical particles
(default: one ``periodic_persistence``), and lets the parent mixture's
sighting-likelihood weighting decide which description was right.

The statistical particle is not decoration: if it ends up carrying the
weight, the LLM contributed nothing, and that is the result. The
matching no-LLM comparison arm is the statistical particle alone.

One spec serves every household in a run because the file is chosen by
``context.household_id``; pointing ``hypotheses_dir`` at a scrambled-
names elicitation output is how the named-vs-scrambled comparison runs
with everything downstream identical.
"""

from __future__ import annotations

import json
import pathlib
import random
from typing import Any, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.hypothesis_mixture import (DEFAULT_ABSENCE_UNIFORMS,
                                                  DEFAULT_ABSENCE_WEIGHT,
                                                  HypothesisMixture)
from baselines.beliefs.hypothesis_program import HypothesisProgramBelief

DEFAULT_STAT_SPECS: Tuple[Mapping[str, Any], ...] = (
    {"name": "periodic_persistence"},)
"""The plain statistical hypothesis that always rides along."""

DEFAULT_HYPOTHESIS_DECAY = 0.99
"""Weight-forgetting factor for hypothesis selection, overriding the
parent's reactive default (0.6, tuned so a disambiguating sense can move
the weights). This mixture answers a different question — which fixed
description of the household was right — and that wants memory measured
in DAYS. Decay is applied per event and the passive diet delivers 30-60
weighted events per day, so the effective memory ``1 / (1 - decay)`` is
~2 events at 0.6 and still under one day at 0.95 — both let a partially
right rival grab the lead for an evening (hh_001 hand-written gate:
2x-lead on only 13/22 late days at 0.95). At 0.99 the memory is a
couple of days: the true hypothesis leads 21/21 late days with weakest
weight 0.945, while sustained regime change can still re-open the
weights within ~100 events. 1.0 (the pure posterior) collapses by day 3
and can never recover from early luck."""


class LLMHypothesisMixture(HypothesisMixture):
    """Mixture of per-household LLM hypotheses + statistical particles.

    ``hypotheses_dir`` holds one ``<household_id>.json`` per household;
    ``stat_specs`` are registry belief specs appended as particles;
    ``label`` overrides the display name so named/scrambled/stat-only
    runs stay distinguishable in result tables.
    """

    def __init__(self, rng: random.Random,
                 hypotheses_dir: pathlib.Path | str,
                 stat_specs: Optional[Sequence[Mapping[str, Any]]] = None,
                 decay: float = DEFAULT_HYPOTHESIS_DECAY,
                 absence_weight: float = DEFAULT_ABSENCE_WEIGHT,
                 absence_uniforms: float = DEFAULT_ABSENCE_UNIFORMS,
                 label: Optional[str] = None,
                 floor_mass: float = 0.0,
                 negative_half_life_h: Optional[float] = None) -> None:
        self._stat_specs = [dict(s) for s in
                            (stat_specs if stat_specs is not None
                             else DEFAULT_STAT_SPECS)]
        # Parent builds the stat particles now; the hypothesis particles
        # join at reset, when the household is known.
        super().__init__(rng, particle_specs=self._stat_specs, decay=decay,
                         absence_weight=absence_weight,
                         absence_uniforms=absence_uniforms,
                         floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        self._dir = pathlib.Path(hypotheses_dir)
        self._label = label

    @property
    def name(self) -> str:
        if self._label:
            return self._label
        return f"LLMHypothesisMixture({self._dir.name})"

    def reset(self, context) -> None:
        path = self._dir / f"{context.household_id}.json"
        if not path.exists():
            raise FileNotFoundError(
                f"{self.name}: no hypotheses file for household "
                f"{context.household_id!r} at {path}")
        payload = json.loads(path.read_text())
        hypotheses = (payload["hypotheses"] if isinstance(payload, Mapping)
                      else payload)
        if not hypotheses:
            raise ValueError(f"{self.name}: {path} holds no hypotheses")
        from baselines.registry import build_registered_belief
        particles = [
            HypothesisProgramBelief(
                random.Random(self._rng.getrandbits(64)), raw)
            for raw in hypotheses]
        particles += [
            build_registered_belief(
                dict(spec), random.Random(self._rng.getrandbits(64)))
            for spec in self._stat_specs]
        self._particles = particles
        super().reset(context)  # resets every particle, re-zeroes weights

    def particle_report(self) -> Mapping[str, Any]:
        """Weights next to what each particle is — the run's log of who
        won, and the fitted numbers of every hypothesis particle."""
        rows = []
        for weight, particle in zip(self.weights, self._particles):
            row: dict = {"particle": particle.name, "weight": weight}
            if isinstance(particle, HypothesisProgramBelief):
                row["fitted"] = particle.fitted_parameters()
            rows.append(row)
        return {"effective_sample_size": self.effective_sample_size,
                "particles": rows}
