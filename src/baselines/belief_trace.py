"""Belief traces for the viewer: what each model believes, at every moment.

The run log answers "what did the agent answer at question times". This
module answers the question a human scrubbing a timeline actually asks —
*where does the model think this object is right now, and where is it
really?* — for EVERY object, at EVERY moment, so the viewer can compare
belief against truth at any slider position rather than only at the
instants the bank happened to ask about.

The observation diet is PASSIVE (never_sense): the initial tour plus the
bank's scripted sightings, delivered in time order. No sensing, no
questions — this is the belief itself, not an agent's answers, so the
picture is not shaped by which objects a policy chose to look at.

A belief's argmax is piecewise-constant in time but does NOT only change
when evidence arrives: decayed-count models re-weight continuously, the
timetable switches bins on the hour, and hazard models decay with
elapsed time. So predictions are sampled on a fixed grid
(``grid_minutes``, default 15) and run-length encoded into segments,
which is both exact at grid resolution and small on disk (a stable
belief costs one segment, not 2 000 samples).

Output (``belief_trace.json``, one per household; times are MINUTES from
episode start, matching the viewer's trace.json convention — everywhere
else in this package times are seconds):

    {"household", "episode_id", "days", "grid_minutes", "bank",
     "bank_manifest_hash", "seed", "objects", "receptacles",
     "object_classes",
     "truth":  {object_id: [[t0, t1, receptacle], ...]},
     "sightings": {object_id: [[minute, receptacle], ...]},
     "models": [{"name", "display", "panel": "frozen"|"candidate",
                 "objects": {object_id: [[t0, t1, receptacle,
                                          confidence], ...]}}]}

``sightings`` is the evidence itself — every observation the passive diet
delivers, the initial tour included — which is what makes a belief
readable rather than merely visible: a model is not "wrong" so much as
working from a sighting that is by now six hours stale, and the viewer
can only say so if it knows when the object was last actually seen.
Sense results never appear (nothing senses here), so this is exactly the
input every model in the file saw.

Truth segments come from the BANK (projected receptacles, including the
``OUT_OF_HOUSE`` / ``ON_PERSON`` pseudo-receptacles), not from the
spatialized timeline, so "correct" in the viewer means exactly what it
means in the harness: identical receptacle ids, exact match.

Usage:
  python -m baselines.belief_trace --bank banks/baselines/fleet/x_bank.jsonl \\
      --out profiles/.../timeline_seed0/belief_trace.json
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng
from baselines.healthcheck import BELIEF_PANEL
from baselines.passive_eval import PassiveProtocolConfig
from baselines.registry import (BELIEF_REGISTRY, CANDIDATE_SLATE,
                                build_registered_belief)
from baselines.routine_oracle import DEFAULT_ORACLE_SEEDS
from baselines.types import DAY_SECONDS, Episode, Observation

logger = logging.getLogger(__name__)

DEFAULT_GRID_MINUTES = 15
"""Sampling grid for belief argmax. 15 min keeps every artifact under a
few hundred KB while being finer than the viewer's 5-min slider is
readable at; belief changes between grid points are invisible anyway."""

Segment = List[Any]        # [t0_min, t1_min, receptacle, confidence?]


def _rle(samples: Sequence[Tuple[int, str, float]],
         end_minute: int) -> List[Segment]:
    """Run-length encode (minute, receptacle, confidence) samples.

    A new segment starts whenever the receptacle changes; the confidence
    recorded is the one at the segment's start. The final segment runs to
    ``end_minute`` so every timeline is covered with no gap.
    """
    segments: List[Segment] = []
    for minute, receptacle, confidence in samples:
        if segments and segments[-1][2] == receptacle:
            continue
        if segments:
            segments[-1][1] = minute
        segments.append([minute, end_minute, receptacle,
                         round(confidence, 4)])
    return segments


def _truth_segments(episode: Episode, object_id: str,
                    end_minute: int) -> List[Segment]:
    """The bank's own piecewise-constant truth, in minutes."""
    trajectory = episode.trajectories[object_id]
    segments: List[Segment] = []
    for i, (t, receptacle) in enumerate(trajectory):
        t1 = (trajectory[i + 1][0] // 60 if i + 1 < len(trajectory)
              else end_minute)
        if segments and segments[-1][2] == receptacle:
            segments[-1][1] = t1
            continue
        segments.append([t // 60, t1, receptacle])
    return segments


def sighting_stream(episode: Episode) -> Dict[str, List[List[Any]]]:
    """object_id -> [[minute, receptacle], ...] for the passive diet.

    The initial tour (t=0) and the scripted sightings, in time order —
    the complete evidence every model in the trace consumed. Objects that
    are never sighted (out of the house for the whole tour, never drawn)
    map to an empty list rather than being absent, so the viewer can say
    "never seen" without a missing-key check.
    """
    stream: Dict[str, List[List[Any]]] = {
        object_id: [] for object_id in episode.object_classes}
    for observation in (*episode.initial_observations,
                        *episode.scripted_observations):
        # Round the second UP to a minute. A belief sampled at grid minute
        # m has consumed exactly the observations with t <= m * 60, so
        # flooring would advertise a sighting one grid step before the
        # models in this same file could act on it — and the viewer would
        # show "last seen: shelf" beside a belief that had not yet heard.
        stream[observation.object_id].append(
            [-(-observation.t // 60), observation.receptacle_id])
    for entries in stream.values():
        entries.sort(key=lambda e: e[0])
    return stream


def trace_one_model(episode: Episode, spec: Dict[str, Any], seed: int,
                    grid_minutes: int) -> Dict[str, List[Segment]]:
    """One model's belief segments for every object, passive diet.

    Walks the grid once, feeding each scripted sighting when its time
    arrives, and samples every object's argmax at every grid point with
    ``predict_readonly`` (tie-break draws must not depend on which
    object happens to be sampled first).
    """
    rng = _derived_rng(seed, "belief_trace", str(spec["name"]),
                       episode.episode_id)
    belief = build_registered_belief(dict(spec), rng)
    belief.reset(episode.agent_view())
    for observation in episode.initial_observations:
        belief.update(observation)

    end_minute = episode.n_days * DAY_SECONDS // 60
    objects = sorted(episode.object_classes)
    samples: Dict[str, List[Tuple[int, str, float]]] = {o: [] for o in objects}
    cursor = 0
    evidence = episode.evidence_stream()
    for minute in range(0, end_minute + 1, grid_minutes):
        t = minute * 60
        while cursor < len(evidence) and evidence[cursor].t <= t:
            belief.update(evidence[cursor])
            cursor += 1
        for object_id in objects:
            prediction = belief.predict_readonly(object_id, t)
            samples[object_id].append(
                (minute, prediction.argmax, prediction.confidence))
    return {o: _rle(samples[o], end_minute) for o in objects}


def build_trace(bank_path: pathlib.Path, seed: int, grid_minutes: int,
                specs: Sequence[Dict[str, Any]],
                timeline: Optional[pathlib.Path] = None,
                spec_path: Optional[pathlib.Path] = None,
                patrol_visits_per_day: int = 6,
                oracle_seeds: int = 0) -> Dict[str, Any]:
    """The full belief_trace payload for a single-episode bank.

    With ``timeline`` and ``spec_path`` given, two extra viewer sections
    are computed from the raw household (they need schedules re-realized,
    which a bank alone cannot provide): ``patrols`` (every schedule at a
    shared visit budget, with house-wide accuracy series per panel model)
    and ``budget_sweep`` (question-set accuracy per model per
    observation budget).
    """
    episodes = list(JsonlBank(path=bank_path).episodes())
    if len(episodes) != 1:
        raise ValueError(
            f"{bank_path}: belief traces expect exactly one episode, "
            f"found {len(episodes)}")
    episode = episodes[0]
    end_minute = episode.n_days * DAY_SECONDS // 60
    models: List[Dict[str, Any]] = []
    for spec in specs:
        name = str(spec["name"])
        display = build_registered_belief(
            dict(spec), _derived_rng(seed, "name")).name
        models.append({
            "name": name, "display": display,
            "panel": BELIEF_REGISTRY[name].panel,
            "objects": trace_one_model(episode, dict(spec), seed,
                                       grid_minutes)})
        logger.info("belief trace: %s done", display)
    payload: Dict[str, Any] = {
        "household": episode.household_id,
        "household_type": episode.household_type,
        "episode_id": episode.episode_id,
        "days": episode.n_days,
        "grid_minutes": grid_minutes,
        "bank": str(bank_path),
        "bank_manifest_hash": JsonlBank(path=bank_path).manifest_hash,
        "seed": seed,
        "objects": sorted(episode.object_classes),
        "object_classes": dict(episode.object_classes),
        "receptacles": list(episode.receptacle_ids),
        "unsensable_receptacles": list(episode.unsensable_receptacle_ids),
        "truth": {o: _truth_segments(episode, o, end_minute)
                  for o in sorted(episode.object_classes)},
        "sightings": sighting_stream(episode),
        "models": models,
    }
    if timeline is not None and spec_path is not None:
        payload["patrols"] = build_patrol_section(
            episode, timeline, spec_path, seed, patrol_visits_per_day)
        payload["budget_sweep"] = build_budget_sweep(
            episode, timeline, spec_path, seed, list(specs),
            oracle_seeds=oracle_seeds)
    return payload


def resolve_specs(include_candidates: bool) -> Tuple[Dict[str, Any], ...]:
    """Panel specs, optionally plus the candidate slate."""
    return ((*BELIEF_PANEL, *CANDIDATE_SLATE) if include_candidates
            else tuple(BELIEF_PANEL))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--grid-minutes", type=int,
                        default=DEFAULT_GRID_MINUTES)
    parser.add_argument("--candidates", action="store_true",
                        help="also trace the candidate belief slate")
    parser.add_argument("--timeline", type=pathlib.Path, default=None,
                        help="household timeline dir; with --spec, adds the "
                             "patrol-comparison and budget-sweep sections")
    parser.add_argument("--spec", type=pathlib.Path, default=None,
                        help="program/motions spec with receptacle rooms")
    parser.add_argument("--patrol-visits-per-day", type=int, default=6)
    parser.add_argument("--oracle-seeds", type=int,
                        default=DEFAULT_ORACLE_SEEDS,
                        help="Monte-Carlo realizations behind the budget "
                             "sweep's routine oracle (0 disables it)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    payload = build_trace(args.bank, args.seed, args.grid_minutes,
                          resolve_specs(args.candidates),
                          timeline=args.timeline, spec_path=args.spec,
                          patrol_visits_per_day=args.patrol_visits_per_day,
                          oracle_seeds=args.oracle_seeds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload) + "\n")
    size_kb = args.out.stat().st_size / 1024
    print(f"belief trace: {len(payload['models'])} models x "
          f"{len(payload['objects'])} objects -> {args.out} ({size_kb:.0f} KB)")




# ---------------------------------------------------------------------------
# Patrol-schedule comparison and observation-budget sweep (viewer sections)
# ---------------------------------------------------------------------------

PATROL_MODELS: Tuple[Dict[str, Any], ...] = tuple(BELIEF_PANEL)
"""Models traced per patrol schedule: the frozen panel. The candidate
slate stays out of the per-schedule traces to bound artifact size; the
budget sweep below covers every registered model."""

SWEEP_VISIT_BUDGETS = (1, 2, 3, 4, 6, 8, 12, 24)
"""Room visits per day swept for the accuracy-vs-observation-budget
curves. The top end is deliberately far past any realistic patrol so the
curves can show convergence when evidence saturates."""

ACCURACY_GRID_MINUTES = 60
"""Sampling grid for house-wide accuracy series (share of all objects the
model localizes correctly). Coarser than the belief segments: these are
plot points, not lookups."""

RECENCY_CONFIG = PassiveProtocolConfig()
"""Recency binning for the budget sweep's accuracy-by-recency strata:
the passive protocol's own bins, reused so the sweep, the bake-off, and
any passive-eval table stratify time-since-last-sighting identically."""


def _accuracy_series(episode: "Episode", spec: Dict[str, Any], seed: int,
                     evidence: Sequence[Any]) -> List[float]:
    """House-wide accuracy over time for one model on one evidence stream.

    Each point is the share of ALL objects whose predicted receptacle
    matches ground truth at that instant, sampled every
    :data:`ACCURACY_GRID_MINUTES`. The evidence stream is whatever the
    caller realized (a patrol schedule at some budget), delivered in time
    order exactly as the harness would.
    """
    rng = _derived_rng(seed, "belief_trace", str(spec["name"]),
                       episode.episode_id)
    belief = build_registered_belief(dict(spec), rng)
    belief.reset(episode.agent_view())
    for observation in episode.initial_observations:
        belief.update(observation)
    objects = sorted(episode.object_classes)
    series: List[float] = []
    cursor = 0
    end_minute = episode.n_days * DAY_SECONDS // 60
    for minute in range(0, end_minute + 1, ACCURACY_GRID_MINUTES):
        t = minute * 60
        while cursor < len(evidence) and evidence[cursor].t <= t:
            belief.update(evidence[cursor])
            cursor += 1
        right = sum(
            belief.predict_readonly(o, t).argmax
            == episode.true_location(o, t) for o in objects)
        series.append(round(right / len(objects), 4))
    return series


def _question_scores(episode: "Episode", spec: Dict[str, Any], seed: int,
                     evidence: Sequence[Any]
                     ) -> Tuple[float, Dict[str, Dict[str, Any]]]:
    """(overall accuracy, accuracy by recency bin) on the bank's questions.

    Recency is time since the belief's last sighting of the queried
    object, binned with the passive protocol's bins
    (:data:`RECENCY_CONFIG`) so the sweep's strata line up with the
    bake-off's recency tables. Each bin carries its question count —
    thin bins are where accuracy-by-recency tables usually mislead, so
    the count travels with the number.
    """
    rng = _derived_rng(seed, "belief_trace", str(spec["name"]),
                       episode.episode_id)
    belief = build_registered_belief(dict(spec), rng)
    belief.reset(episode.agent_view())
    last_sighting: Dict[str, int] = {}

    def saw(object_id: str, t: int) -> None:
        last_sighting[object_id] = max(last_sighting.get(object_id, t), t)

    for observation in episode.initial_observations:
        belief.update(observation)
        saw(observation.object_id, observation.t)
    cursor = 0
    hits = total = 0
    bin_hits: Dict[str, int] = {}
    bin_totals: Dict[str, int] = {}
    for day in episode.questions_by_day:
        for question in day:
            while (cursor < len(evidence)
                   and evidence[cursor].t <= question.t_query):
                event = evidence[cursor]
                belief.update(event)
                if isinstance(event, Observation):
                    saw(event.object_id, event.t)
                else:               # a room visit's per-receptacle result
                    for object_id in event.contents:
                        saw(object_id, event.t)
                cursor += 1
            prediction = belief.predict_readonly(question.object_id,
                                                 question.t_query)
            correct = prediction.argmax == episode.true_location(
                question.object_id, question.t_query)
            since = (question.t_query - last_sighting[question.object_id]
                     if question.object_id in last_sighting else None)
            label = RECENCY_CONFIG.recency_bin(since)
            hits += correct
            total += 1
            bin_hits[label] = bin_hits.get(label, 0) + correct
            bin_totals[label] = bin_totals.get(label, 0) + 1
    recency = {label: {"n": bin_totals[label],
                       "accuracy": round(bin_hits[label]
                                         / bin_totals[label], 4)}
               for label in RECENCY_CONFIG.recency_bin_labels()
               if label in bin_totals}
    return (round(hits / total, 4) if total else 0.0), recency


def _sense_events(stream: Any) -> List[Any]:
    """A realized stream's per-receptacle sense results, in time order —
    the form the beliefs consume (positives and exclusions alike)."""
    from baselines.types import SenseResult

    events: List[Any] = []
    for row in stream.visit_rows:
        t = int(str(row["t"]))
        contents = row["contents"]
        assert isinstance(contents, dict)
        for receptacle, objs in sorted(contents.items()):
            events.append(SenseResult(receptacle_id=str(receptacle), t=t,
                                      contents=tuple(str(o) for o in objs)))
    events.sort(key=lambda e: e.t)
    return events


def _json_finite(stats: Dict[str, float]) -> Dict[str, Any]:
    """Stats with non-finite values replaced by None: ``inf`` (a schedule
    that never revisits, an object never sighted twice) is representable
    in Python's json output but not in JSON itself, and the viewer's
    JSON.parse would reject the whole artifact."""
    import math
    return {k: (v if isinstance(v, str) or math.isfinite(v) else None)
            for k, v in stats.items()}


def build_patrol_section(episode: "Episode", timeline: pathlib.Path,
                         spec_path: pathlib.Path, seed: int,
                         visits_per_day: int) -> Dict[str, Any]:
    """Per-schedule visit timelines + house-wide accuracy series.

    The three budget-taking schedules run at the shared visit budget,
    but ``morning_evening_sweep`` and ``stationed_observer`` set their
    own visit counts by construction — so the schedules differ in
    OBSERVATION VOLUME as well as route shape, and a raw accuracy
    comparison across them confounds the two. Each schedule therefore
    carries its realized stream statistics (``stats``: visits and
    sightings per day among them, from
    :func:`~baselines.room_observations.stream_stats`), and accuracy
    must be read against realized volume, not schedule name alone.
    """
    from baselines.export_bank import (_away_intervals, awake_spans,
                                       load_truth)
    from baselines.room_observations import (RoomMap, build_schedules,
                                             realize, stream_stats)

    room_map = RoomMap.from_spec(spec_path)
    truth, n_days, _ = load_truth(timeline)
    awake = awake_spans(timeline, n_days)
    away = _away_intervals(timeline)
    schedules = build_schedules(room_map, n_days, awake, timeline,
                                visits_per_day, seed)
    section: Dict[str, Any] = {
        "visits_per_day": visits_per_day,
        "accuracy_grid_minutes": ACCURACY_GRID_MINUTES,
        "models": [str(m["name"]) for m in PATROL_MODELS],
        "schedules": {},
    }
    for name, visits in sorted(schedules.items()):
        stream = realize(visits, room_map, truth, "trace", away)
        evidence = _sense_events(stream)
        section["schedules"][name] = {
            "visits": [[v.t // 60, v.room] for v in visits],
            "stats": _json_finite(stream_stats(stream, visits, truth,
                                               n_days)),
            "accuracy": {
                str(m["name"]): _accuracy_series(episode, dict(m), seed,
                                                 evidence)
                for m in PATROL_MODELS},
        }
        logger.info("patrol section: %s done", name)
    return section


def build_budget_sweep(episode: "Episode", timeline: pathlib.Path,
                       spec_path: pathlib.Path, seed: int,
                       specs: Sequence[Dict[str, Any]],
                       oracle_seeds: int = 0) -> Dict[str, Any]:
    """Question-set accuracy per model per observation budget.

    One round-robin patrol per budget level; every model consumes the
    identical stream at each level, so the curves are comparable point
    by point. This is the floor/separation/convergence picture: at tiny
    budgets every model sits near the same floor, models separate as
    evidence grows, and saturate when everything is fresh.

    ``recency`` stratifies each model's accuracy at each budget by time
    since the queried object was last sighted (bins + counts from
    :data:`RECENCY_CONFIG`).

    With ``oracle_seeds`` > 0, the sweep also carries the Monte-Carlo
    routine oracle (see :mod:`baselines.routine_oracle`): perfect
    routine knowledge, no observations, so its accuracy is a single
    budget-independent number. ``headroom_per_budget`` is oracle minus
    the best model at each budget — the share of residual error
    explainable by routine knowledge alone. It is NOT a hard ceiling:
    negative values mean observation-fed models beat routine knowledge
    there, i.e. recency is carrying the load.
    """
    from baselines.export_bank import (_away_intervals, awake_spans,
                                       load_truth)
    from baselines.room_observations import (RoomMap, realize,
                                             round_robin_patrol)
    from baselines.routine_oracle import build_oracle_section

    room_map = RoomMap.from_spec(spec_path)
    truth, n_days, _ = load_truth(timeline)
    awake = awake_spans(timeline, n_days)
    away = _away_intervals(timeline)
    accuracy: Dict[str, List[float]] = {str(m["name"]): [] for m in specs}
    recency: Dict[str, List[Dict[str, Dict[str, Any]]]] = {
        str(m["name"]): [] for m in specs}
    for budget in SWEEP_VISIT_BUDGETS:
        visits = round_robin_patrol(room_map, n_days, awake, budget, seed)
        evidence = _sense_events(
            realize(visits, room_map, truth, "trace", away))
        for model in specs:
            overall, by_bin = _question_scores(episode, dict(model), seed,
                                               evidence)
            accuracy[str(model["name"])].append(overall)
            recency[str(model["name"])].append(by_bin)
        logger.info("budget sweep: %d visits/day done", budget)
    sweep: Dict[str, Any] = {
        "visit_budgets": list(SWEEP_VISIT_BUDGETS),
        "patrol": "round_robin_patrol",
        "n_questions": sum(len(d) for d in episode.questions_by_day),
        "accuracy": accuracy,
        "recency_bins": list(RECENCY_CONFIG.recency_bin_labels()),
        "recency": recency,
    }
    if oracle_seeds > 0:
        oracle = build_oracle_section(timeline, episode, oracle_seeds)
        if oracle is not None:
            oracle["headroom_per_budget"] = [
                round(oracle["accuracy"]
                      - max(accuracy[m][i] for m in accuracy), 4)
                for i in range(len(SWEEP_VISIT_BUDGETS))]
            sweep["oracle"] = oracle
    return sweep


if __name__ == "__main__":
    main()
