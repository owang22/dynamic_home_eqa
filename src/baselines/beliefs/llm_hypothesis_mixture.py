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

**Graph arm.** When the household file is an assumption-graph envelope
(:mod:`baselines.llm_hypotheses.assumption_graph`), the same mixture
holds the graph alongside the leaf bodies: leaves are the particles,
weights roll up to assumption values, revisions arrive as OPERATIONS
(the ``elicitor`` is then ``(report, graph, context) -> OperationResult``)
and leaves not mentioned keep their bodies and therefore their weights
through :meth:`_rebuild`, which keys on ``leaf_id``. Two more trigger
sources join the scheduled days (checked in this order): the UNCOVERED
BANK — first sightings of classes no live leaf models, fired when the
bank reaches a threshold that ramps with the day — and the prediction-
quality trigger as before. Leaves whose weight stays under
``leaf_weight_floor`` for ``leaf_prune_days`` are pruned automatically
(never below 3 leaves), with no LLM call. The flat arm is untouched: a
flat file loads exactly as before.
"""

from __future__ import annotations

import collections
import dataclasses
import json
import math
import pathlib
import random
from typing import (TYPE_CHECKING, Any, Callable, Deque, Dict, List, Mapping,
                    Optional, Sequence, Tuple, Union)

from baselines.beliefs.hypothesis_mixture import (DEFAULT_ABSENCE_UNIFORMS,
                                                  DEFAULT_ABSENCE_WEIGHT,
                                                  HypothesisMixture)
from baselines.beliefs.hypothesis_program import (CHANCE_PRIOR_STRENGTH,
                                                   CLASS_PREFIX,
                                                   HypothesisProgramBelief)
from baselines.types import DAY_SECONDS, Observation, SenseResult

if TYPE_CHECKING:
    from baselines.llm_hypotheses.assumption_graph import AssumptionGraph

DEFAULT_LEAF_WEIGHT_FLOOR = 0.02
DEFAULT_LEAF_PRUNE_DAYS = 3
MIN_LEAVES_AFTER_PRUNE = 3
UNCOVERED_BANK_START = 2
"""Bank size that fires on day 0 when the ramp is on; it rises linearly
to ``ReaskConfig.uncovered_bank_max`` by the last day."""

DEFAULT_STAT_SPECS: Tuple[Mapping[str, Any], ...] = (
    {"name": "most_frequent", "half_life_h": 72.0},)
"""The plain statistical hypothesis that always rides along: most-
frequent location with a 72 h half-life, the best-scoring statistical
model on the slate (pooled hh_001+hh_002, merged scoring: log-loss 1.52
against periodic_persistence's 2.10 at equal top-1) and the same decay
the converter's own fallback uses. Also the no-LLM comparison arm."""

DEFAULT_LLM_ABSENCE_WEIGHT = 1.0
"""Absence half of the sighting likelihood at FULL weight for this
mixture (the parent keeps 0.25). Absence is the only channel through
which a "left the house" prediction can earn credit — nothing is ever
sighted at OUT_OF_HOUSE — and the measured weights had been collapsing
onto the one hypothesis that never predicted it. Set here, not on the
parent, so the disambiguation studies keep their default."""

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
    ``new_class_triggers``: fire on first sightings of classes no live
    hypothesis models (the uncovered bank).
    ``uncovered_bank_max``: surprises accumulated before firing.
    ``uncovered_bank_ramp``: raise the bar linearly with the day index,
    from :data:`UNCOVERED_BANK_START` on day 0 to ``uncovered_bank_max``
    on the last day, so early days fire readily and late days do not.
    """

    window: int = 40
    threshold: float = -2.3
    scheduled_days: Tuple[int, ...] = (3, 7)
    max_calls: int = 4
    min_gap: int = 40
    new_class_triggers: bool = True
    uncovered_bank_max: int = 4
    uncovered_bank_ramp: bool = True
    settled_weight: float = 0.9
    """Rolled-up weight at which an assumption's top value closes the
    node to revision operations (graph arm)."""
    anomaly_p: float = 0.05
    """Anomaly bucket: a sighting no live leaf gave more than this
    probability enters the bucket (graph arm)."""
    anomaly_repeats: int = 3
    """Bucket key ``(object, receptacle, 2-hour bin)`` recurrences that
    fire a diversify call; single occurrences never fire. 0 disables."""

    def __post_init__(self) -> None:
        if self.window < 1 or self.min_gap < 0 or self.max_calls < 0:
            raise ValueError("ReaskConfig: window >= 1, min_gap >= 0, "
                             "max_calls >= 0")
        if self.uncovered_bank_max < 1:
            raise ValueError("ReaskConfig: uncovered_bank_max >= 1")

    def bank_threshold(self, day: int, n_days: int) -> float:
        """Bank size at which the uncovered trigger fires on ``day``."""
        if not self.uncovered_bank_ramp:
            return float(self.uncovered_bank_max)
        span = max(1, n_days - 1)
        frac = min(1.0, max(0.0, day / span))
        return (UNCOVERED_BANK_START
                + (self.uncovered_bank_max - UNCOVERED_BANK_START) * frac)


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
                 absence_weight: float = DEFAULT_LLM_ABSENCE_WEIGHT,
                 absence_uniforms: float = DEFAULT_ABSENCE_UNIFORMS,
                 label: Optional[str] = None,
                 reask: Optional[ReaskConfig] = None,
                 elicitor: Optional[Elicitor] = None,
                 floor_mass: float = 0.0,
                 negative_half_life_h: Optional[float] = None,
                 leaf_weight_floor: float = DEFAULT_LEAF_WEIGHT_FLOOR,
                 leaf_prune_days: int = DEFAULT_LEAF_PRUNE_DAYS) -> None:
        self._stat_specs = [dict(s) for s in
                            (stat_specs if stat_specs is not None
                             else DEFAULT_STAT_SPECS)]
        self._reask = reask
        self._elicitor = elicitor
        self._raw_hypotheses: List[dict] = []
        self._vocabulary: Optional[Dict[str, str]] = None
        self._graph: Optional["AssumptionGraph"] = None   # graph mode
        self._leaf_weight_floor = float(leaf_weight_floor)
        self._leaf_prune_days = int(leaf_prune_days)
        self._evidence_log: List[Union[Observation, SenseResult]] = []
        self._sighting_log: List[Dict[str, Any]] = []
        self._recent: Deque[float] = collections.deque(
            maxlen=(reask.window if reask else 1))
        self._fired_days: set = set()
        self._last_reask_index = -10 ** 9
        self.reask_events: List[Dict[str, Any]] = []
        self.calls_made = 0
        self._sighted: set = set()
        self._uncovered_bank: List[Dict[str, Any]] = []
        self._below_since: Dict[str, int] = {}
        self.edit_log: List[Dict[str, Any]] = []
        self.prune_log: List[Dict[str, Any]] = []
        self.birth_log: List[Dict[str, Any]] = []
        self.rejected_ops: List[Dict[str, Any]] = []
        self.check_outcomes: List[Dict[str, Any]] = []
        self._look_log: List[Tuple[int, str, Tuple[str, ...]]] = []
        self._anomaly_bucket: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
        self.bucket_trace: List[Dict[str, Any]] = []
        self._assumption_trace: Dict[int, Dict[str, Any]] = {}
        self._leaf_count_trace: Dict[int, int] = {}
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
        hypotheses = self._load_payload(payload)
        if not hypotheses:
            raise ValueError(f"{self.name}: {path} holds no hypotheses")
        # The objects the LLM had been shown when it wrote the file. A
        # file without one (hand-written, or pre-leak-fix) falls back to
        # the context's full table.
        self._vocabulary = (dict(payload.get("vocabulary"))
                            if isinstance(payload, Mapping)
                            and payload.get("vocabulary") else None)
        from baselines.registry import build_registered_belief
        self._raw_hypotheses = [dict(h) for h in hypotheses]
        particles = [
            self._make_particle(raw, random.Random(self._rng.getrandbits(64)),
                                self._vocabulary)
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
        self._sighted = set()
        self._uncovered_bank = []
        self._below_since = {}
        self.edit_log = []
        self.prune_log = []
        self.birth_log = []
        self.rejected_ops = []
        self.check_outcomes = []
        self._look_log = []
        self._anomaly_bucket = {}
        self.bucket_trace = []
        self._assumption_trace = {}
        self._leaf_count_trace = {}

    def _make_particle(self, raw: Mapping[str, Any], rng: random.Random,
                       vocabulary: Optional[Mapping[str, str]]):
        """One particle for a raw hypothesis dict (subclasses swap the
        converter)."""
        return HypothesisProgramBelief(rng, raw, vocabulary=vocabulary)

    def _load_payload(self, payload: Any) -> List[dict]:
        """The hypothesis bodies a household file holds: graph leaves,
        or the flat list. (The tree mixture overrides this.)"""
        from baselines.llm_hypotheses.assumption_graph import (
            AssumptionGraph, is_graph_payload)
        if is_graph_payload(payload):
            self._graph = AssumptionGraph.from_json(payload)
            return self._graph.leaf_bodies()
        self._graph = None
        return (payload["hypotheses"] if isinstance(payload, Mapping)
                else payload)

    @property
    def known_objects(self) -> Dict[str, str]:
        """The object table the LLM may be shown now: what it was shown at
        elicitation plus every object registered since (sighted, or
        asked about)."""
        if self._vocabulary is None:
            # No vocabulary on file (hand-written or pre-leak-fix): the
            # converter fell back to the context table, so the report
            # does too — the old, leaky behaviour, kept for such files.
            table = dict(self._context.object_classes) if (
                self._context is not None and self._context.object_classes
            ) else {}
        else:
            table = dict(self._vocabulary)
        table.update({o: c for o, c in self._objects.items()
                      if o not in table})
        return table

    @property
    def graph(self) -> Optional["AssumptionGraph"]:
        """The assumption graph (None for a flat file)."""
        return self._graph

    @property
    def is_graph(self) -> bool:
        return self._graph is not None

    @property
    def n_hypotheses(self) -> int:
        return len(self._raw_hypotheses)

    @property
    def leaf_weights(self) -> Dict[str, float]:
        """Mixture weight per hypothesis particle, keyed by leaf id
        (graph) or hypothesis id (flat); statistical particles excluded
        and their weight left outside the map."""
        weights = self.weights
        return {self._particle_key(raw): weights[i]
                for i, raw in enumerate(self._raw_hypotheses)}

    @staticmethod
    def _particle_key(raw: Mapping[str, Any]) -> str:
        return str(raw.get("leaf_id") or raw.get("node_id")
                   or raw.get("hypothesis_id"))

    @property
    def has_structure(self) -> bool:
        """Graph or tree mode: the modes with automatic pruning, check
        outcomes and the anomaly bucket. False for a flat file."""
        return self._graph is not None

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
        classes = ({evidence.object_id: evidence.object_class}
                   if isinstance(evidence, Observation)
                   else dict(evidence.object_classes))
        if isinstance(evidence, SenseResult):
            self._look_log.append((evidence.t, evidence.receptacle_id,
                                   tuple(evidence.contents)))
        else:
            self._look_log.append((evidence.t, evidence.receptacle_id,
                                   (evidence.object_id,)))
        for obj, receptacle in pairs:
            if obj in self._objects:
                forecast = self.predict_readonly(obj, evidence.t)
                p = forecast.distribution.get(receptacle, 0.0)
                self._sighting_log.append({
                    "t": evidence.t, "object": obj, "actual": receptacle,
                    "predicted": forecast.argmax, "p_actual": p})
                self._recent.append(math.log(max(p, 1e-12)))
                self._bucket_sighting(obj, receptacle, evidence.t)
            else:
                # First sighting of a new object: no forecast to score,
                # but the leaves can still say whether they expected it
                # there (cold-start / class prior), so the bucket sees it.
                self._sighting_log.append({
                    "t": evidence.t, "object": obj, "actual": receptacle,
                    "predicted": None, "p_actual": None})
                self.ensure_object(obj, classes.get(obj, ""))
                self._bucket_sighting(obj, receptacle, evidence.t)
            if obj not in self._sighted:
                self._sighted.add(obj)
                self._consider_uncovered(obj, classes.get(obj, ""),
                                         evidence.t)
        super().update(evidence)
        self._maybe_reask(evidence.t)
        day = evidence.t // DAY_SECONDS
        if self.has_structure:
            self._prune(evidence.t)
            self._record_check_outcomes(evidence.t)
        if self._graph is not None:
            from baselines.llm_hypotheses.assumption_graph import (
                assumption_summary)
            self._assumption_trace[day] = assumption_summary(
                self._graph, self.leaf_weights)
        self._leaf_count_trace[day] = len(self._raw_hypotheses)

    # ------------------------------------------------------- anomaly bucket

    def _bucket_sighting(self, obj: str, receptacle: str, t: int) -> None:
        """Graph arm: a sighting that no LIVE leaf predicted (max over
        leaves below ``anomaly_p``) enters the bucket under its
        ``(object, receptacle, 2-hour bin)`` key. The max, not the
        mixture average: a low average with one leaf fitting well is a
        weighting problem, not a structure problem."""
        cfg = self._reask
        if (cfg is None or not self.has_structure or cfg.anomaly_repeats <= 0
                or not self._raw_hypotheses):
            return
        n_hyp = len(self._raw_hypotheses)
        masses = self._claimed_mass(obj, receptacle, t)[:n_hyp]
        top = max(masses) if masses else 0.0
        if top >= cfg.anomaly_p:
            return
        key = (obj, receptacle, int((t % DAY_SECONDS) // 7200))
        row = self._anomaly_bucket.setdefault(
            key, {"object": obj, "receptacle": receptacle, "hour_bin": key[2],
                  "count": 0, "max_p": 0.0, "first_t": t})
        row["count"] += 1
        row["max_p"] = max(row["max_p"], top)
        self.bucket_trace.append({"t": t, "day": t // DAY_SECONDS,
                                  "key": list(key), "count": row["count"],
                                  "max_p": top,
                                  "bucket_size": len(self._anomaly_bucket)})

    @property
    def anomaly_bucket(self) -> List[Dict[str, Any]]:
        return sorted((dict(r) for r in self._anomaly_bucket.values()),
                      key=lambda r: (-r["count"], r["first_t"]))

    @property
    def anomaly_bucket_fired(self) -> List[Dict[str, Any]]:
        """Bucket keys that reached ``anomaly_repeats`` — the only ones a
        revision prompt may show. One-off sightings stay in the bucket
        (and in ``bucket_at_fire`` for the log) but never reach the
        model: it would explain them."""
        cfg = self._reask
        bar = cfg.anomaly_repeats if cfg is not None else 1
        return [r for r in self.anomaly_bucket if r["count"] >= max(1, bar)]

    def _anomaly_ready(self) -> Optional[Dict[str, Any]]:
        cfg = self._reask
        if cfg is None or cfg.anomaly_repeats <= 0:
            return None
        for row in self.anomaly_bucket:
            if row["count"] >= cfg.anomaly_repeats:
                return row
        return None

    # ------------------------------------------------------- uncovered bank

    def _modeled_classes(self) -> set:
        """Classes some live hypothesis says anything about: the class of
        any object it covers (rest or move), or a ``class:`` target."""
        table = self.known_objects
        classes: set = set()
        n_hyp = len(self._raw_hypotheses)
        for raw, particle in zip(self._raw_hypotheses,
                                 self._particles[:n_hyp]):
            if isinstance(particle, HypothesisProgramBelief) \
                    and particle._hypothesis is not None:
                for obj in particle.hypothesis.covered_objects():
                    if obj in table:
                        classes.add(table[obj])
            rest = raw.get("rest")
            keys = (list(rest) if isinstance(rest, Mapping) else
                    [e.get("target", "") for e in rest]
                    if isinstance(rest, (list, tuple)) else [])
            for act in raw.get("activities", ()):
                keys += [str(m.get("target", "")) for m in act.get("moves", ())]
            for key in keys:
                key = str(key)
                if key.startswith(CLASS_PREFIX):
                    classes.add(key[len(CLASS_PREFIX):])
                elif key in table:
                    classes.add(table[key])
        return classes

    def _consider_uncovered(self, obj: str, cls: str, t: int) -> None:
        """First sighting of ``obj``: enter the bank if its class is one
        no live hypothesis models. A new object of a modeled class does
        not enter."""
        cfg = self._reask
        if cfg is None or not cfg.new_class_triggers or not cls:
            return
        if cls in self._modeled_classes():
            return
        if any(row["class"] == cls for row in self._uncovered_bank):
            return   # the class is already banked; one entry per class
        self._uncovered_bank.append({"object": obj, "class": cls, "t": t,
                                     "day": t // DAY_SECONDS})

    @property
    def uncovered_bank(self) -> List[Dict[str, Any]]:
        return [dict(row) for row in self._uncovered_bank]

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
        trigger = None
        for scheduled in cfg.scheduled_days:
            if day >= scheduled and scheduled not in self._fired_days:
                self._fired_days.add(scheduled)
                reason, trigger = f"scheduled day {scheduled}", "scheduled"
                break
        if reason is None and cfg.new_class_triggers and self._uncovered_bank:
            n_days = (self._context.n_days if self._context is not None
                      else 28)
            bar = cfg.bank_threshold(day, n_days)
            if len(self._uncovered_bank) >= bar:
                reason = (f"uncovered bank {len(self._uncovered_bank)} >= "
                          f"{bar:.1f}")
                trigger = "uncovered"
        since = len(self._sighting_log) - self._last_reask_index
        if reason is None and since >= cfg.min_gap:
            hot = self._anomaly_ready()
            if hot is not None:
                reason = (f"anomaly {hot['object']}@{hot['receptacle']} "
                          f"bin {hot['hour_bin']} x{hot['count']}")
                trigger = "anomaly"
        if reason is None:
            quality = self.recent_quality
            if (quality is not None and quality < cfg.threshold
                    and since >= cfg.min_gap):
                reason = f"quality {quality:.2f} < {cfg.threshold}"
                trigger = "quality"
        if reason is None:
            return
        self._revise(t, reason, trigger or "scheduled")

    CALL_TYPE_OF_TRIGGER = {"scheduled": "repair", "quality": "repair",
                            "anomaly": "diversify", "uncovered": "diversify"}
    """Which revision call a trigger fires (graph arm, when the elicitor
    honours call types): repair edits what exists, diversify only adds."""

    def _revise(self, t: int, reason: str, trigger: str = "scheduled") -> None:
        report = self.revision_report(t)
        report["trigger"] = trigger
        report["reason"] = reason
        report["call_type"] = self.CALL_TYPE_OF_TRIGGER.get(trigger, "repair")
        report["anomaly_firing"] = (self._anomaly_ready()
                                    if trigger == "anomaly" else None)
        before = {"quality": self.recent_quality,
                  "weights": dict(zip(
                      [p.name for p in self._particles], self.weights)),
                  "n_hypotheses": len(self._raw_hypotheses),
                  "uncovered_bank": self.uncovered_bank}
        self.calls_made += 1
        assert self._elicitor is not None
        event: Dict[str, Any] = {
            "t": t, "day": t // DAY_SECONDS, "reason": reason,
            "trigger": trigger, "call_index": self.calls_made,
            "before": before}
        changed = self._apply_revision(report, t, trigger, event)
        self._last_reask_index = len(self._sighting_log)
        self._recent.clear()
        self._uncovered_bank = []
        event["bucket_at_fire"] = self.anomaly_bucket
        self._anomaly_bucket = {}
        event.update({
            "changed": changed,
            "n_hypotheses_after": len(self._raw_hypotheses),
            "hypothesis_ids_after": [self._particle_key(h)
                                     for h in self._raw_hypotheses]})
        self.reask_events.append(event)

    def _apply_revision(self, report: Dict[str, Any], t: int, trigger: str,
                        event: Dict[str, Any]) -> bool:
        """Call the elicitor and install what it returns; True when the
        hypothesis set changed. Graph mode applies operations, flat mode
        swaps the list. (The tree mixture overrides this.)"""
        assert self._elicitor is not None
        if self._graph is not None:
            result = self._elicitor(report, self._graph, self._context)
            graph = getattr(result, "graph", None)
            applied = list(getattr(result, "applied", []))
            births = list(getattr(result, "births", []))
            changed = graph is not None and bool(applied or births)
            stamp = {"t": t, "day": t // DAY_SECONDS, "trigger": trigger,
                     "call_index": self.calls_made}
            if changed:
                self._graph = graph
                self._rebuild(graph.leaf_bodies())
                self.edit_log += [{**stamp, **op} for op in applied]
                self.birth_log += [{**stamp, "kind": "born", **b}
                                   for b in births]
                self.birth_log += [{**stamp, "kind": "skipped", **b}
                                   for b in getattr(result, "skipped_births",
                                                    [])]
            event["problems"] = list(getattr(result, "problems", []))
            event["operations"] = len(getattr(result, "operations", []))
            rejected = list(getattr(result, "rejected", []))
            self.rejected_ops += [{"t": t, "day": t // DAY_SECONDS,
                                   "trigger": trigger,
                                   "call_index": self.calls_made, **r}
                                  for r in rejected]
            event["rejected"] = len(rejected)
            event["call_type"] = report["call_type"]
            if trigger == "anomaly":
                event["anomaly_key"] = report["anomaly_firing"]
            event["assumptions_after"] = (
                list(self._graph.assumptions) if self._graph else [])
            return changed
        revised = self._elicitor(
            report, [dict(h) for h in self._raw_hypotheses], self._context)
        changed = revised is not None and revised != self._raw_hypotheses
        if changed:
            self._rebuild(revised)
        return changed

    # -------------------------------------------------------------- pruning

    def _prune(self, t: int) -> None:
        """Drop leaves whose weight has sat below the floor for
        ``leaf_prune_days`` consecutive days, never below
        :data:`MIN_LEAVES_AFTER_PRUNE` leaves. No LLM call; logged."""
        if self._graph is None or self._leaf_prune_days <= 0:
            return
        day = t // DAY_SECONDS
        weights = self.weights
        n_hyp = len(self._raw_hypotheses)
        victims: List[int] = []
        for i in range(n_hyp):
            key = self._particle_key(self._raw_hypotheses[i])
            if weights[i] < self._leaf_weight_floor:
                since = self._below_since.setdefault(key, day)
                if day - since >= self._leaf_prune_days:
                    victims.append(i)
            else:
                self._below_since.pop(key, None)
        if not victims:
            return
        # Lowest weight first, and stop when the floor count is reached.
        victims.sort(key=lambda i: weights[i])
        keep = set(range(len(self._particles)))
        hyp_indices = set(range(n_hyp))
        for i in victims:
            if len(keep & hyp_indices) <= MIN_LEAVES_AFTER_PRUNE:
                break
            keep.discard(i)
            key = self._particle_key(self._raw_hypotheses[i])
            self.prune_log.append({
                "t": t, "day": day, "leaf_id": key, "weight": weights[i],
                "below_since_day": self._below_since.get(key)})
            self._below_since.pop(key, None)
        if len(keep) == len(self._particles):
            return
        pruned = {self._particle_key(self._raw_hypotheses[i])
                  for i in range(n_hyp) if i not in keep}
        self._graph.leaves = [l for l in self._graph.leaves
                              if l["leaf_id"] not in pruned]
        self._remove_hypothesis_particles(pruned)

    def _remove_hypothesis_particles(self, pruned: set) -> None:
        """Drop the hypothesis particles with these keys, keeping every
        other particle's weight slot and totals in order."""
        n_hyp = len(self._raw_hypotheses)
        keep = [i for i in range(len(self._particles))
                if i >= n_hyp
                or self._particle_key(self._raw_hypotheses[i]) not in pruned]
        self._particles = [self._particles[i] for i in keep]
        self._log_weights = [self._log_weights[i] for i in keep]
        self.presence_totals = [self.presence_totals[i] for i in keep]
        self.absence_totals = [self.absence_totals[i] for i in keep]
        self._raw_hypotheses = [h for h in self._raw_hypotheses
                                if self._particle_key(h) not in pruned]
        for key in pruned:
            self._below_since.pop(key, None)
        top = max(self._log_weights)
        self._log_weights = [lw - top for lw in self._log_weights]

    def _rebuild(self, revised: List[dict]) -> None:
        """Swap in the revised hypothesis set, keeping every stat particle
        and every bit of evidence: revised particles replay the full
        event log, a kept id keeps its log weight, a new id enters at
        the mean log weight of the hypothesis particles."""
        old_weight = {}
        n_hyp = len(self._raw_hypotheses)
        for raw, lw in zip(self._raw_hypotheses, self._log_weights[:n_hyp]):
            old_weight[self._particle_key(raw)] = lw
        hyp_weights = list(self._log_weights[:n_hyp]) or [0.0]
        mean_lw = sum(hyp_weights) / len(hyp_weights)
        stat_particles = self._particles[n_hyp:]
        stat_weights = self._log_weights[n_hyp:]
        stat_presence = self.presence_totals[n_hyp:]
        stat_absence = self.absence_totals[n_hyp:]
        new_particles: List[HypothesisProgramBelief] = []
        new_weights: List[float] = []
        for raw in revised:
            particle = self._make_particle(
                raw, random.Random(self._rng.getrandbits(64)),
                self.known_objects)
            particle.reset(self._context)
            for obj, cls in self._objects.items():
                particle.ensure_object(obj, cls)
            for event in self._evidence_log:
                particle.update(event)
            new_particles.append(particle)
            new_weights.append(old_weight.get(self._particle_key(raw),
                                              mean_lw))
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
        for raw, particle, weight in zip(self._raw_hypotheses, hyp_particles,
                                         weights):
            hyp = particle.hypothesis
            hypotheses.append({
                "hypothesis_id": hyp.hypothesis_id, "weight": weight,
                "assumes": dict(raw.get("assumes", {})),
                "distinguishing_prediction": hyp.distinguishing_prediction,
                "verdict": self._check_verdict(hyp.distinguishing_check,
                                               self._look_log)})
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
        # Report against the objects the LLM has been shown — never the
        # bank's inventory, which would name objects it has not seen.
        table = self.known_objects
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
        stat_weight = float(sum(weights[n_hyp:])) if len(weights) > n_hyp else None
        return {
            "day": t // DAY_SECONDS, "t": t,
            "hypotheses": hypotheses, "worst_objects": worst_objects,
            "statistical_weight": stat_weight,
            "rules_held": held[:15], "rules_failed": failed[:15],
            "uncovered_objects": uncovered,
            "uncovered_bank": self.uncovered_bank,
            "assumptions": self.assumption_weights,
            "settled": self.settled_assumptions,
            "leaf_weights": self.leaf_weights,
            "anomaly_bucket": self.anomaly_bucket_fired,
            "check_outcomes": self.check_outcomes[-40:],
            "away_window_looks": self.away_window_looks(),
            "known_objects": self.known_objects,
            "statistics": per_object_statistics(
                sorted(table), sightings, t),
            "recent_quality": self.recent_quality}

    # ---------------------------------------------------------------- graph

    def away_window_looks(self) -> List[Dict[str, Any]]:
        """Per object with a move ending out of the house in any live
        leaf: looks at its stated rest receptacle inside that move's
        window, split into empty and found. The absence evidence the
        positive-only statistics cannot show."""
        from baselines.beliefs.hypothesis_program import AWAY_DESTINATIONS
        n_hyp = len(self._raw_hypotheses)
        windows: Dict[str, Dict[str, Any]] = {}
        for particle in self._particles[:n_hyp]:
            if not isinstance(particle, HypothesisProgramBelief) \
                    or particle._hypothesis is None:
                continue
            hyp = particle.hypothesis
            for activity in hyp.activities:
                for rule in activity.moves:
                    if rule.to not in AWAY_DESTINATIONS:
                        continue
                    for obj in rule.targets:
                        rest = hyp.rest.get(obj)
                        if rest is None:
                            continue
                        row = windows.setdefault(obj, {
                            "object": obj, "rest": rest, "spans": set()})
                        end = min(24.0, activity.start_hour + rule.duration_h)
                        row["spans"].add((activity.days, activity.start_hour,
                                          end))
        # Where each object has actually been sighted most: the model
        # reasons from that receptacle, so the looks there inside the
        # window are the decisive number, whatever rest was stated.
        modal: Dict[str, str] = {}
        seen: Dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        for row in self._sighting_log:
            seen[row["object"]][row["actual"]] += 1
        for obj, counter in seen.items():
            modal[obj] = counter.most_common(1)[0][0]
        out = []
        for obj, row in sorted(windows.items()):
            places = [row["rest"]]
            if modal.get(obj) and modal[obj] != row["rest"]:
                places.append(modal[obj])
            tallies = {p: [0, 0] for p in places}      # empty, found
            for t, receptacle, contents in self._look_log:
                if receptacle not in tallies:
                    continue
                day = t // DAY_SECONDS
                weekend = day % 7 in (5, 6)
                hour = (t % DAY_SECONDS) / 3600.0
                inside = any(
                    (days == "both" or (days == "weekend") == weekend)
                    and start <= hour < end
                    for days, start, end in row["spans"])
                if not inside:
                    continue
                tallies[receptacle][1 if obj in contents else 0] += 1
            spans = "; ".join(f"{d} {s:04.1f}-{e:04.1f}h"
                              for d, s, e in sorted(row["spans"]))
            out.append({"object": obj, "rest": row["rest"],
                        "empty": tallies[row["rest"]][0],
                        "found": tallies[row["rest"]][1],
                        "modal": modal.get(obj),
                        "modal_empty": (tallies[modal[obj]][0]
                                        if modal.get(obj) in tallies else None),
                        "modal_found": (tallies[modal[obj]][1]
                                        if modal.get(obj) in tallies else None),
                        "windows": spans})
        return out

    @property
    def settled_assumptions(self) -> Dict[str, str]:
        """Assumptions closed to revision: top value at or above
        ``ReaskConfig.settled_weight``. Empty for a flat file."""
        if self._graph is None:
            return {}
        from baselines.llm_hypotheses.assumption_graph import (
            settled_assumptions)
        floor = self._reask.settled_weight if self._reask else 0.9
        return settled_assumptions(self._graph, self.leaf_weights, floor)

    def weight_spread(self) -> Dict[str, float]:
        """How much of the final log-weight spread across hypothesis
        particles came from presence versus absence terms: max minus min
        of each cumulative total."""
        n_hyp = len(self._raw_hypotheses)
        pres = self.presence_totals[:n_hyp] or [0.0]
        absn = self.absence_totals[:n_hyp] or [0.0]
        return {"presence": max(pres) - min(pres),
                "absence": max(absn) - min(absn)}

    @property
    def assumption_weights(self) -> Dict[str, Dict[str, Any]]:
        """Per assumption: question, rolled-up value weights, entropy.
        Empty for a flat file. Read-only; the policy reads this."""
        if self._graph is None:
            return {}
        from baselines.llm_hypotheses.assumption_graph import (
            assumption_summary)
        return assumption_summary(self._graph, self.leaf_weights)

    def value_distributions(self, object_id: str, t: int
                            ) -> Dict[str, Dict[str, Tuple[float, Dict[str, float]]]]:
        """For the policy: per assumption, per value, ``(rolled-up weight,
        the leaves' weighted predictive distribution for object_id at t
        under that value)``. Leaf distributions are read once; no
        generator is perturbed."""
        if self._graph is None:
            return {}
        n_hyp = len(self._raw_hypotheses)
        dists = self.particle_distributions(object_id, t)[:n_hyp]
        leaf_w = self.leaf_weights
        total = sum(leaf_w.values()) or 1.0
        out: Dict[str, Dict[str, Tuple[float, Dict[str, float]]]] = {}
        for name, assumption in self._graph.assumptions.items():
            per_value: Dict[str, Tuple[float, Dict[str, float]]] = {}
            for value in assumption.values:
                mass = 0.0
                mixed: Dict[str, float] = {}
                for raw, dist in zip(self._raw_hypotheses, dists):
                    if raw.get("assumes", {}).get(name) != value:
                        continue
                    w = leaf_w[self._particle_key(raw)] / total
                    mass += w
                    for rec, p in dist.items():
                        mixed[rec] = mixed.get(rec, 0.0) + w * p
                if mass > 0.0:
                    mixed = {r: p / mass for r, p in mixed.items()}
                per_value[value] = (mass, mixed)
            out[name] = per_value
        return out

    def graph_diagnostics(self) -> Dict[str, Any]:
        """The graph arm's per-episode record: assumption trace, edit
        log, prune log, birth log, leaf count trace, final graph."""
        return {
            "is_graph": self._graph is not None,
            "assumption_trace": {str(d): v for d, v in
                                 sorted(self._assumption_trace.items())},
            "leaf_count_trace": {str(d): n for d, n in
                                 sorted(self._leaf_count_trace.items())},
            "edit_log": list(self.edit_log),
            "prune_log": list(self.prune_log),
            "birth_log": list(self.birth_log),
            "rejected_ops": list(self.rejected_ops),
            "check_outcomes": list(self.check_outcomes),
            "bucket_trace": list(self.bucket_trace),
            "weight_spread": self.weight_spread(),
            "settled": self.settled_assumptions,
            "uncovered_bank": self.uncovered_bank,
            "final_graph": self._graph.to_json() if self._graph else None,
            "leaf_weight_floor": self._leaf_weight_floor,
            "leaf_prune_days": self._leaf_prune_days}

    @staticmethod
    def check_resolutions(check, looks: Sequence[Tuple[int, str, Tuple[str, ...]]]
                          ) -> List[Tuple[int, bool]]:
        """Every resolution of a distinguishing check: ``(t, in_favour)``
        for each look at ``check.at`` within CHECK_WINDOW_H of its hour on
        matching days. Finding the target resolves in the ``if_seen``
        direction, an empty look the other way. A sighting of the target
        anywhere else inside the window counts as an empty look at ``at``
        (it is demonstrably elsewhere), which is how positive-only banks
        resolve checks at all."""
        if check is None:
            return []
        out: List[Tuple[int, bool]] = []
        for t, receptacle, contents in looks:
            # A look at `at` resolves by found / empty; a look elsewhere
            # that contains the target proves it is not at `at`.
            elsewhere = receptacle != check.at
            if elsewhere and check.target not in contents:
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
            found = (check.target in contents) and not elsewhere
            in_favour = found == (check.if_seen == "right")
            out.append((t, in_favour))
        return out

    @classmethod
    def _check_verdict(cls, check, looks) -> Optional[str]:
        """"resolved in favour k/n" for a structured distinguishing
        check; None without a check."""
        if check is None:
            return None
        rows = cls.check_resolutions(check, looks)
        if not rows:
            return "not yet tested (no look at that receptacle in the window)"
        hits = sum(1 for _, ok in rows if ok)
        return f"came true {hits}/{len(rows)} times"

    def _record_check_outcomes(self, t: int) -> None:
        """Append every new check resolution since the last call to
        ``check_outcomes`` (leaf, day, direction)."""
        n_hyp = len(self._raw_hypotheses)
        seen = {(r["leaf_id"], r["t"]) for r in self.check_outcomes}
        for raw, particle in zip(self._raw_hypotheses, self._particles[:n_hyp]):
            if not isinstance(particle, HypothesisProgramBelief) \
                    or particle._hypothesis is None:
                continue
            check = particle.hypothesis.distinguishing_check
            for tt, ok in self.check_resolutions(check, self._look_log):
                key = (self._particle_key(raw), tt)
                if key in seen:
                    continue
                seen.add(key)
                self.check_outcomes.append({
                    "leaf_id": key[0], "t": tt, "day": tt // DAY_SECONDS,
                    "in_favour": ok, "target": check.target, "at": check.at,
                    "if_seen": check.if_seen})

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
