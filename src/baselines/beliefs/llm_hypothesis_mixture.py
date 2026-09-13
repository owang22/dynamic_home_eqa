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
``context.household_id``; pointing ``hypotheses_dir`` at an anonymized
elicitation output is how the named-vs-anonymized comparison runs with
everything downstream identical.

**Re-asking.** Three layers act on the hypotheses; only the last calls
the LLM. Every sighting reweights the particles (the parent's job) and
lets each particle refit its own numbers (the converter's job). Then,
occasionally, the LLM is asked to REVISE the set — triggered by
prediction quality, never by weight spread: weights collapsing onto one
hypothesis means that hypothesis is winning, which is the system
working. The trigger is a running mean of ``log p_mixture(sighting)``
over the last :attr:`ReaskConfig.window` sightings falling below
:attr:`ReaskConfig.threshold`; if that is poor, no hypothesis explains
what is happening. Fixed asks also fire early (:attr:`ReaskConfig.
scheduled_days`), since hypotheses written off one tour are thin. Total
calls are capped and every event is logged in ``reask_events``.

A revision keeps the household's evidence: revised particles are rebuilt
and every event seen so far is replayed into them, so their numbers are
fitted rather than fresh; a hypothesis that keeps its id keeps its log
weight, a new one enters at the mean log weight. The ``elicitor`` is a
callable ``(report, previous_hypotheses, context) -> hypotheses`` so the
belief stays testable without a server.
"""

from __future__ import annotations

import collections
import dataclasses
import json
import math
import pathlib
import random
from typing import (Any, Callable, Deque, Dict, List, Mapping, Optional,
                    Sequence, Tuple, Union)

from baselines.beliefs.hypothesis_mixture import (DEFAULT_ABSENCE_UNIFORMS,
                                                  DEFAULT_ABSENCE_WEIGHT,
                                                  HypothesisMixture)
from baselines.beliefs.hypothesis_program import (CHANCE_PRIOR_STRENGTH,
                                                   HypothesisProgramBelief)
from baselines.types import DAY_SECONDS, Observation, SenseResult

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


@dataclasses.dataclass(frozen=True)
class ReaskConfig:
    """When the LLM is asked to revise. All knobs are configurable; the
    defaults are set once, a priori, and recorded in the run log.

    ``window``: sightings in the running prediction-quality mean.
    ``threshold``: mean ``log p_mixture(sighting)`` below which the set
    is judged not to explain what is happening (−2.3 is p ≈ 0.10 — the
    mixture assigning the sighted receptacle a tenth of its mass, on
    average, over a day of sightings).
    ``scheduled_days``: fixed early asks, fired at the first sighting on
    or after each listed day.
    ``max_calls``: hard cap per household on LLM revisions.
    ``min_gap``: sightings that must pass after a revision before the
    quality trigger may fire again (the window refills first).
    """

    window: int = 40
    threshold: float = -2.3
    scheduled_days: Tuple[int, ...] = (3, 7)
    max_calls: int = 4
    min_gap: int = 40

    def __post_init__(self) -> None:
        if self.window < 1 or self.min_gap < 0 or self.max_calls < 0:
            raise ValueError("ReaskConfig: window >= 1, min_gap >= 0, "
                             "max_calls >= 0")


Elicitor = Callable[[Mapping[str, Any], List[dict], Any], List[dict]]
"""``(revision_report, previous_hypotheses, context) -> revised
hypotheses`` — validated, real-id dicts. Returning the previous list
unchanged is the correct response to a failed call."""

RULE_MIN_EVIDENCE = 2.0
"""Weighted sightings a rule needs before it is reported as held or
failed (one label's worth of prior strength, so the verdict is the
data's, not the prior's)."""

RULE_HELD_CHANCE = 0.5
RULE_FAILED_CHANCE = 0.2
CHECK_WINDOW_H = 1.5
"""Half-width, in hours, around a distinguishing check's hour within
which a sighting of its target counts as a test of it."""


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
                 reask: Optional[ReaskConfig] = None,
                 elicitor: Optional[Elicitor] = None,
                 floor_mass: float = 0.0,
                 negative_half_life_h: Optional[float] = None) -> None:
        self._stat_specs = [dict(s) for s in
                            (stat_specs if stat_specs is not None
                             else DEFAULT_STAT_SPECS)]
        self._reask = reask
        self._elicitor = elicitor
        self._raw_hypotheses: List[dict] = []
        self._evidence_log: List[Union[Observation, SenseResult]] = []
        self._sighting_log: List[Dict[str, Any]] = []
        self._recent: Deque[float] = collections.deque(
            maxlen=(reask.window if reask else 1))
        self._fired_days: set = set()
        self._last_reask_index = -10 ** 9
        self.reask_events: List[Dict[str, Any]] = []
        self.calls_made = 0
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
        self._raw_hypotheses = [dict(h) for h in hypotheses]
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
        self._evidence_log = []
        self._sighting_log = []
        self._recent.clear()
        self._fired_days = set()
        self._last_reask_index = -10 ** 9
        self.reask_events = []
        self.calls_made = 0

    # ------------------------------------------------------------ re-asking

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        """Log the mixture's own forecast of every positive sighting
        before the parent applies it, then consider a revision."""
        self._evidence_log.append(evidence)
        if isinstance(evidence, Observation):
            pairs = [(evidence.object_id, evidence.receptacle_id)]
        else:
            pairs = [(obj, evidence.receptacle_id)
                     for obj in evidence.contents]
        for obj, receptacle in pairs:
            if obj in self._objects:
                forecast = self.predict_readonly(obj, evidence.t)
                p = forecast.distribution.get(receptacle, 0.0)
                self._sighting_log.append({
                    "t": evidence.t, "object": obj, "actual": receptacle,
                    "predicted": forecast.argmax, "p_actual": p})
                self._recent.append(math.log(max(p, 1e-12)))
            else:
                # First sighting of a new object: no forecast to score.
                self._sighting_log.append({
                    "t": evidence.t, "object": obj, "actual": receptacle,
                    "predicted": None, "p_actual": None})
        super().update(evidence)
        self._maybe_reask(evidence.t)

    @property
    def recent_quality(self) -> Optional[float]:
        """Running mean of ``log p_mixture(sighting)`` over the window,
        None until the window is full."""
        if self._reask is None or len(self._recent) < self._reask.window:
            return None
        return sum(self._recent) / len(self._recent)

    def _maybe_reask(self, t: int) -> None:
        cfg = self._reask
        if cfg is None or self._elicitor is None:
            return
        if self.calls_made >= cfg.max_calls:
            return
        day = t // DAY_SECONDS
        reason = None
        for scheduled in cfg.scheduled_days:
            if day >= scheduled and scheduled not in self._fired_days:
                self._fired_days.add(scheduled)
                reason = f"scheduled day {scheduled}"
                break
        if reason is None:
            quality = self.recent_quality
            since = len(self._sighting_log) - self._last_reask_index
            if (quality is not None and quality < cfg.threshold
                    and since >= cfg.min_gap):
                reason = f"quality {quality:.2f} < {cfg.threshold}"
        if reason is None:
            return
        self._revise(t, reason)

    def _revise(self, t: int, reason: str) -> None:
        report = self.revision_report(t)
        before = {"quality": self.recent_quality,
                  "weights": dict(zip(
                      [p.name for p in self._particles], self.weights)),
                  "n_hypotheses": len(self._raw_hypotheses)}
        self.calls_made += 1
        revised = self._elicitor(report, [dict(h) for h in self._raw_hypotheses],
                                 self._context)
        changed = revised is not None and revised != self._raw_hypotheses
        if changed:
            self._rebuild(revised)
        self._last_reask_index = len(self._sighting_log)
        self._recent.clear()
        self.reask_events.append({
            "t": t, "day": t // DAY_SECONDS, "reason": reason,
            "call_index": self.calls_made, "before": before,
            "changed": changed,
            "n_hypotheses_after": len(self._raw_hypotheses),
            "hypothesis_ids_after": [h.get("hypothesis_id")
                                     for h in self._raw_hypotheses]})

    def _rebuild(self, revised: List[dict]) -> None:
        """Swap in the revised hypothesis set, keeping every stat particle
        and every bit of evidence: revised particles replay the full
        event log, a kept id keeps its log weight, a new id enters at
        the mean log weight of the hypothesis particles."""
        old_weight = {}
        n_hyp = len(self._raw_hypotheses)
        for particle, lw in zip(self._particles[:n_hyp], self._log_weights):
            old_weight[particle.name] = lw
        hyp_weights = list(self._log_weights[:n_hyp]) or [0.0]
        mean_lw = sum(hyp_weights) / len(hyp_weights)
        stat_particles = self._particles[n_hyp:]
        stat_weights = self._log_weights[n_hyp:]
        stat_presence = self.presence_totals[n_hyp:]
        stat_absence = self.absence_totals[n_hyp:]
        new_particles: List[HypothesisProgramBelief] = []
        new_weights: List[float] = []
        for raw in revised:
            particle = HypothesisProgramBelief(
                random.Random(self._rng.getrandbits(64)), raw)
            particle.reset(self._context)
            for obj, cls in self._objects.items():
                particle.ensure_object(obj, cls)
            for event in self._evidence_log:
                particle.update(event)
            new_particles.append(particle)
            new_weights.append(old_weight.get(particle.name, mean_lw))
        self._raw_hypotheses = [dict(h) for h in revised]
        self._particles = new_particles + list(stat_particles)
        self._log_weights = new_weights + list(stat_weights)
        top = max(self._log_weights)
        self._log_weights = [lw - top for lw in self._log_weights]
        self.presence_totals = [0.0] * len(new_particles) + list(stat_presence)
        self.absence_totals = [0.0] * len(new_particles) + list(stat_absence)

    # -------------------------------------------------------------- report

    def revision_report(self, t: int) -> Dict[str, Any]:
        """Everything the revision prompt needs, from the belief's own
        records: weights, the mixture's worst objects, rules that held
        and failed, uncovered objects, per-object statistics, and each
        hypothesis's distinguishing-prediction verdict. Real ids."""
        from baselines.llm_hypotheses.prompt import per_object_statistics
        n_hyp = len(self._raw_hypotheses)
        weights = self.weights
        hyp_particles = [p for p in self._particles[:n_hyp]
                         if isinstance(p, HypothesisProgramBelief)]
        sightings = [(row["t"], row["object"], row["actual"])
                     for row in self._sighting_log]
        hypotheses = []
        for particle, weight in zip(hyp_particles, weights):
            hyp = particle.hypothesis
            hypotheses.append({
                "hypothesis_id": hyp.hypothesis_id, "weight": weight,
                "distinguishing_prediction": hyp.distinguishing_prediction,
                "verdict": self._check_verdict(hyp.distinguishing_check,
                                               sightings)})
        since = self._sighting_log[max(0, self._last_reask_index):]
        misses: Dict[Tuple[str, str, str], List[int]] = collections.defaultdict(list)
        for row in since:
            if row["predicted"] is not None and row["predicted"] != row["actual"]:
                misses[(row["object"], row["predicted"], row["actual"])].append(row["t"])
        worst = sorted(misses.items(), key=lambda kv: -len(kv[1]))[:12]
        worst_objects = [{
            "object": obj, "predicted": pred, "actual": act,
            "count": len(ts), "example_day": ts[0] // DAY_SECONDS,
            "example_hour": (ts[0] % DAY_SECONDS) // 3600}
            for (obj, pred, act), ts in worst]
        held, failed = [], []
        for particle in hyp_particles:
            fitted = particle.fitted_parameters()
            for rule in fitted["rules"]:
                if rule["evidence"] < RULE_MIN_EVIDENCE:
                    continue
                row = {"hypothesis_id": fitted["hypothesis_id"], **rule}
                if rule["fitted_chance"] >= RULE_HELD_CHANCE:
                    held.append(row)
                elif rule["fitted_chance"] <= RULE_FAILED_CHANCE:
                    failed.append(row)
        held.sort(key=lambda r: -r["evidence"]); failed.sort(key=lambda r: -r["evidence"])
        covered: set = set()
        for particle in hyp_particles:
            covered |= particle.hypothesis.covered_objects()
        # The LLM was given the full object table; report against it,
        # so an object never yet sighted still shows up as uncovered.
        table = (self._context.object_classes if self._context is not None
                 and self._context.object_classes else self._objects)
        uncovered = []
        for obj in sorted(table):
            if obj in covered:
                continue
            recs = collections.Counter(a for tt, o, a in sightings if o == obj)
            if not recs:
                summary = "never sighted"
            else:
                modal, n = recs.most_common(1)[0]
                summary = (f"seen {sum(recs.values())}x, mostly {modal} "
                           f"({n}); {len(recs)} receptacle"
                           f"{'s' if len(recs) != 1 else ''}")
            uncovered.append({"object": obj, "summary": summary})
        return {
            "day": t // DAY_SECONDS, "t": t,
            "hypotheses": hypotheses, "worst_objects": worst_objects,
            "rules_held": held[:15], "rules_failed": failed[:15],
            "uncovered_objects": uncovered,
            "statistics": per_object_statistics(
                sorted(table), sightings, t),
            "recent_quality": self.recent_quality}

    @staticmethod
    def _check_verdict(check, sightings: Sequence[Tuple[int, str, str]]
                       ) -> Optional[str]:
        """"came true k/n" for a structured distinguishing check, judged
        on the target's sightings within CHECK_WINDOW_H of its hour on
        matching days; None without a check."""
        if check is None:
            return None
        hits = total = 0
        for t, obj, rec in sightings:
            if obj != check.target:
                continue
            day = t // DAY_SECONDS
            weekend = day % 7 in (5, 6)
            if check.days == "weekday" and weekend:
                continue
            if check.days == "weekend" and not weekend:
                continue
            hour = (t % DAY_SECONDS) / 3600.0
            if abs(hour - check.hour) > CHECK_WINDOW_H:
                continue
            total += 1
            hits += int(rec == check.at)
        if total == 0:
            return "not yet tested (no sightings of the target in that window)"
        return f"came true {hits}/{total} times"

    def reask_diagnostics(self) -> Dict[str, Any]:
        """The run's record of the re-asking layer: every event, the
        call count, and the per-sighting quality series."""
        return {"calls_made": self.calls_made,
                "config": dataclasses.asdict(self._reask) if self._reask else None,
                "events": list(self.reask_events),
                "sighting_quality": [
                    {"t": r["t"], "p": r["p_actual"]}
                    for r in self._sighting_log if r["p_actual"] is not None]}

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
