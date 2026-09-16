"""Export a simulated household timeline into the baselines bank format.

Bridges the revamp_v1 world (profiles/revamp_v1 timelines: minute-level
events over named receptacles, plus the two virtual locations ELSEWHERE and
``person:<resident>``) into the JSONL episode-bank schema documented in
:mod:`baselines.bank`. Everything the baseline stack needs but the
simulator does not provide — an observation stream and a question set — is
generated here, deterministically from a seed.

Location projection (the scorer does exact receptacle match, so virtual
locations must become receptacles):

* ``ELSEWHERE``        -> pseudo-receptacle ``OUT_OF_HOUSE``
* ``person:<anyone>``  -> ``ON_PERSON`` while that resident is home, but
  ``OUT_OF_HOUSE`` while they are away (from residents.jsonl blocks at
  ELSEWHERE): a phone in her pocket at work is out of the house, full
  stop. Timelines without residents.jsonl fall back to always-ON_PERSON.

Both pseudo-receptacles join ``receptacle_ids`` as legitimate ANSWERS,
but ``OUT_OF_HOUSE`` is declared UNSENSABLE in the episode header: the
robot cannot look outside the house, so "it's out" can only be inferred
(by exclusion of every sensable receptacle) or guessed — never observed.
For the same reason neither the initial tour nor drive-by sightings ever
report an object whose true location is unsensable (you cannot see what
is not there); such sightings are dropped and the drop count logged.
``ON_PERSON`` is unsensable as a RECEPTACLE (since 2026-09-14): a look
inspects a receptacle the robot can stand next to, and a person is not
one. Before this, ON_PERSON sat in a pseudo-room the active policy could
target and so returned pocket contents without the robot locating
anyone. Neither the tour nor a drive-by sighting reports an object at
either token.

With ``person_sensing`` (2026-09-15) ``ON_PERSON`` becomes observable
the way receptacles are, in two steps: a look at a receptacle also lists
the residents in that room, and a policy may then spend a sense on a
listed resident, which returns everything they carry. To support that
the bank carries, harness-side only: a ``resident`` row stream per
resident — ``(t, room-or-AWAY)`` change-points from residents.jsonl
(the block's ``at`` receptacle mapped to its room; ELSEWHERE is AWAY;
before a resident's first block they are in the room of that first
block) — and a ``carrier`` on every ``ON_PERSON`` truth row naming the
resident. Truth labels are unchanged: ``ON_PERSON`` still means carried
by someone who is home, ``OUT_OF_HOUSE`` everything else. A bank
without the header field is exported byte-for-byte as before.

Generated stream and questions (all seeded):

* initial tour (optional, ``--no-initial-tour`` to drop): every
  sensable object's location at the TOUR INSTANT — the moment the robot
  is installed. ``--tour-start day0`` (the original convention) puts it
  at t=0, Monday 00:00, when the simulator has just placed every object
  at its declared home, so the tour hands the agent the rest map for
  free. ``--tour-start random`` draws the instant per seed
  (``_derived_rng(seed, "tour", episode_id)``): a day uniform in
  ``[0, --tour-max-day]`` and a moment uniform in that day's awake
  time, so the tour catches the home mid-life (mugs at the sink, keys
  out with their owner) and the weekday/hour of installation vary
  across seeds. Nothing the robot could not have seen is exported:
  room visits, drive-by sightings and questions before the tour are
  dropped, and the header records ``tour_t``. The clock is NOT
  re-based — day 0 stays Monday 00:00 — so a random tour costs up to
  ``tour_max_day`` days of evidence and questions. WITH the tour, a
  frozen belief starts from a snapshot and scores the world's
  stationarity (~0.6 on hh_001 under ``day0``) with zero learning;
  WITHOUT it, never-sensed objects sit at the uniform-fallback chance
  floor (~1/n_receptacles) and every point of accuracy must be earned
  through sensing.
* scripted sightings: ``--sightings-per-day`` per day, each a uniformly
  chosen object seen at a uniform instant inside the household's OWN awake
  time (non-sleep resident blocks; see :func:`awake_spans`) at its true
  location — drive-by observations.
* questions: ``--questions-per-day`` per day from ``--first-question-day``
  on. The query schedule is a controlled experimental axis
  (``--query-mode``), because a generator whose timing/content correlates
  with the dynamics is an uncontrolled lever on every result:

  - ``uniform`` — object and time drawn independently of the dynamics
    (objects WITHOUT replacement from a per-day shuffled pool — uniform in
    expectation with per-object repeats capped at ceil(questions/objects),
    so no single displaced object can dominate a day by draw luck — time
    uniform in the awake window). The clean scientific condition; headline
    results belong here.
  - ``naturalistic`` — the realistic condition, deliberately correlated
    with the dynamics in three documented ways: object choice is
    popularity-weighted (weight 1 + number of true movements — busy
    objects get asked about more), with probability 0.3 the question
    re-asks one of the last 3 queried objects (people re-ask about the
    same things), and with probability 0.5 the time is placed 5-60
    minutes AFTER one of the object's true movements that day (people
    notice things right after they move) instead of uniformly.

  The chosen mode is recorded in the episode header (``query_mode``).

Times in the timeline are minutes; the bank uses seconds (x60).

Usage:
  python -m baselines.export_bank \
      --timeline profiles/revamp_v1/claude-fable-5/timelines/hh_001_seed0 \
      --spec profiles/revamp_v1/claude-fable-5/schedules/hh_001_schedule.yaml \
      --seed 0 --out banks/baselines/hh_001_seed0_bank.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import pathlib
import random
from typing import Any, Dict, List, Mapping, Optional, Tuple

import yaml

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng
from baselines.types import AWAY, DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE

logger = logging.getLogger(__name__)

UNSENSABLE = (OUT_OF_HOUSE, ON_PERSON)
"""Locations a look can never inspect: outside the house, and on a
person. Declared in every bank header; sightings there are never
exported."""
AWAKE_WINDOW_S = (8 * 3600, 22 * 3600)
"""Fallback awake window (seconds into the day) for timelines that carry no
resident blocks. Real households use their OWN awake time — see
:func:`awake_spans`."""

SLEEP_KEYWORDS = ("sleep", "nap")
"""Activity-name substrings that mark a resident as asleep."""


def _away_intervals(timeline: pathlib.Path) -> Dict[str, List[Tuple[int, int]]]:
    """resident -> merged [t0, t1) seconds intervals spent at ELSEWHERE.

    Read from residents.jsonl (realized activity blocks); an absent file
    means no away information, i.e. carried objects always project to
    ON_PERSON (the pre-person-coupling behaviour, kept for stub timelines).
    """
    path = timeline / "residents.jsonl"
    if not path.exists():
        return {}
    raw: Dict[str, List[Tuple[int, int]]] = {}
    with open(path) as f:
        for line in f:
            b = json.loads(line)
            if b.get("at") == "ELSEWHERE":
                raw.setdefault(str(b["resident"]), []).append(
                    (int(b["t0"]) * 60, int(b["t1"]) * 60))
    merged: Dict[str, List[Tuple[int, int]]] = {}
    for res, spans in raw.items():
        spans.sort()
        out: List[Tuple[int, int]] = []
        for t0, t1 in spans:
            if out and t0 <= out[-1][1]:
                out[-1] = (out[-1][0], max(out[-1][1], t1))
            else:
                out.append((t0, t1))
        merged[res] = out
    return merged


def awake_spans(timeline: pathlib.Path, n_days: int
                ) -> Dict[int, List[Tuple[int, int]]]:
    """day -> merged [t0, t1) second spans when SOMEONE in the house is up.

    Questions and drive-by sightings are drawn from these spans rather than
    a fixed clock window. A fixed window is not household-agnostic: for a
    night-shift resident, 08:00-22:00 is mostly blackout sleep, and a
    question asked five hours into a sleep is degenerate — nothing has
    moved since she lay down, so every belief scores alike and sensing has
    nothing to buy. Drawing from awake time asks about the world while it
    is actually in motion.

    Falls back to :data:`AWAKE_WINDOW_S` per day when the timeline has no
    ``residents.jsonl`` (stub timelines in tests).
    """
    path = timeline / "residents.jsonl"
    per_day: Dict[int, List[Tuple[int, int]]] = {}
    if not path.exists():
        return {d: [(d * DAY_SECONDS + AWAKE_WINDOW_S[0],
                     d * DAY_SECONDS + AWAKE_WINDOW_S[1])]
                for d in range(n_days)}
    spans: List[Tuple[int, int]] = []
    with open(path) as f:
        for line in f:
            b = json.loads(line)
            if any(k in str(b["activity"]) for k in SLEEP_KEYWORDS):
                continue
            spans.append((int(b["t0"]) * 60, int(b["t1"]) * 60))
    spans.sort()
    merged: List[Tuple[int, int]] = []
    for t0, t1 in spans:
        if merged and t0 <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], t1))
        else:
            merged.append((t0, t1))
    for d in range(n_days):
        lo, hi = d * DAY_SECONDS, (d + 1) * DAY_SECONDS
        clipped = [(max(t0, lo), min(t1, hi)) for t0, t1 in merged
                   if t0 < hi and t1 > lo]
        per_day[d] = [(a, b) for a, b in clipped if b > a + 60]
    return per_day


def draw_time(spans: List[Tuple[int, int]], day: int,
              rng: random.Random) -> int:
    """A uniform instant inside ``spans`` (length-weighted); the fixed
    window when a day has no awake span (e.g. a 24 h absence)."""
    total = sum(b - a for a, b in spans)
    if not total:
        return day * DAY_SECONDS + rng.randrange(*AWAKE_WINDOW_S)
    offset = rng.randrange(total)
    for a, b in spans:
        if offset < b - a:
            return a + offset
        offset -= b - a
    return spans[-1][1] - 1


def _project_segment(location: str, t0: int, t1: int,
                     away: Dict[str, List[Tuple[int, int]]]
                     ) -> List[Tuple[int, str]]:
    """Projected change-points for one raw-location dwell [t0, t1)."""
    if location == "ELSEWHERE":
        return [(t0, OUT_OF_HOUSE)]
    if not location.startswith("person:"):
        return [(t0, location)]
    # Carried: ON_PERSON at home, OUT_OF_HOUSE while the carrier is away.
    points = [(t0, ON_PERSON)]
    for a0, a1 in away.get(location.split(":", 1)[1], []):
        lo, hi = max(t0, a0), min(t1, a1)
        if lo < hi:
            if lo == t0:
                points[0] = (t0, OUT_OF_HOUSE)
            else:
                points.append((lo, OUT_OF_HOUSE))
            if hi < t1:
                points.append((hi, ON_PERSON))
    return sorted(points)


def load_truth(timeline: pathlib.Path
               ) -> Tuple[Dict[str, List[Tuple[int, str]]], int,
                          Dict[Tuple[str, int], str]]:
    """(object -> projected change-points in seconds, n_days, causes) from a
    timeline; causes maps (object, t) -> the "by" tag of the event behind
    the change (activity:name / tidy:name / misplace / person_departure /
    person_return), for provenance in the bank and visualizations.

    Initial positions come from the first hourly row; movements from
    events.jsonl; person-carried dwells are split by the carrier's away
    intervals. Consecutive same-receptacle change-points are merged.
    """
    truth, n_days, causes, _ = load_truth_with_carriers(timeline)
    return truth, n_days, causes


def load_truth_with_carriers(timeline: pathlib.Path
                             ) -> Tuple[Dict[str, List[Tuple[int, str]]], int,
                                        Dict[Tuple[str, int], str],
                                        Dict[Tuple[str, int], str]]:
    """:func:`load_truth` plus ``carriers``: (object, t) of every
    ``ON_PERSON`` change-point -> the resident carrying the object from
    then on (the ``person:<resident>`` of the raw dwell). Feeds the
    ``carrier`` field of person-sensing banks."""
    with open(timeline / "hourly.csv") as f:
        rows = list(csv.DictReader(f))
    objects = [k for k in rows[0] if k not in ("t", "stamp")]
    n_days = (int(rows[-1]["t"]) // (24 * 60)) + 1
    away = _away_intervals(timeline)

    raw: Dict[str, List[Tuple[int, str]]] = {
        obj: [(0, rows[0][obj])] for obj in objects}
    causes: Dict[Tuple[str, int], str] = {}
    with open(timeline / "events.jsonl") as f:
        for line in f:
            e = json.loads(line)
            traj = raw[e["object"]]
            if e["to"] != traj[-1][1]:
                traj.append((e["t"] * 60, str(e["to"])))
                causes[(e["object"], e["t"] * 60)] = str(e.get("by", ""))

    truth: Dict[str, List[Tuple[int, str]]] = {}
    carriers: Dict[Tuple[str, int], str] = {}
    horizon = n_days * DAY_SECONDS
    for obj, segments in raw.items():
        points: List[Tuple[int, str]] = []
        for i, (t0, location) in enumerate(segments):
            t1 = segments[i + 1][0] if i + 1 < len(segments) else horizon
            for t, receptacle in _project_segment(location, t0, t1, away):
                if not points or points[-1][1] != receptacle:
                    points.append((t, receptacle))
                    if receptacle == ON_PERSON:
                        carriers[(obj, t)] = location.split(":", 1)[1]
                    if (obj, t) not in causes:
                        # A synthesized boundary: the carrier left/returned.
                        causes[(obj, t)] = ("person_departure"
                                            if receptacle == OUT_OF_HOUSE
                                            else "person_return") if t else ""
        truth[obj] = points
    return truth, n_days, causes, carriers


def resident_room_trajectories(spec_path: pathlib.Path,
                               timeline: pathlib.Path
                               ) -> Dict[str, List[Tuple[int, str]]]:
    """resident -> ``(t, room)`` change-points (seconds, from t=0) with
    :data:`~baselines.types.AWAY` while out, from residents.jsonl through
    :func:`~baselines.room_observations._resident_room_lookup` (a
    block's ``at`` receptacle names its room; ELSEWHERE is away). Before
    a resident's first block they are in the room of that first block;
    consecutive same-room points are merged."""
    from baselines.room_observations import (RoomMap, _resident_room_lookup,
                                             residents_of)

    room_map = RoomMap.from_spec(spec_path)
    out: Dict[str, List[Tuple[int, str]]] = {}
    for resident in residents_of(timeline):
        blocks = _resident_room_lookup(timeline, resident, room_map)
        points: List[Tuple[int, str]] = []
        first_room = blocks[0][2]
        points.append((0, AWAY if first_room is None else first_room))
        for t0, _, room in blocks:
            label = AWAY if room is None else room
            if points[-1][1] != label:
                points.append((max(t0, 0), label))
        out[resident] = points
    return out


DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def stamp(t: int) -> str:
    """``d03 Thu 14:20`` for a bank time in seconds (day 0 is a Monday)."""
    day, rem = divmod(int(t), DAY_SECONDS)
    return f"d{day:02d} {DAY_NAMES[day % 7]} {rem // 3600:02d}:{rem % 3600 // 60:02d}"


def draw_tour_instant(tour_start: str, tour_max_day: int, n_days: int,
                      awake: Dict[int, List[Tuple[int, int]]],
                      rng: random.Random) -> int:
    """The bank time (seconds) at which the robot is installed and does
    its walkthrough. ``day0`` is t=0; ``random`` picks a day uniformly
    in ``[0, tour_max_day]`` and an instant uniformly in that day's
    awake time (:func:`draw_time`), from a generator seeded for the tour
    alone so sighting and question streams are unaffected by the choice.
    """
    if tour_start == "day0":
        return 0
    if tour_start != "random":
        raise ValueError(f"unknown tour_start {tour_start!r}")
    if not 0 <= tour_max_day < n_days:
        raise ValueError(f"tour_max_day {tour_max_day} outside "
                         f"[0, {n_days - 1}]")
    day = rng.randint(0, tour_max_day)
    return draw_time(awake[day], day, rng)


def truth_at(traj: List[Tuple[int, str]], t: int) -> str:
    """Location at time t for a sorted change-point list."""
    location = traj[0][1]
    for change_t, receptacle in traj:
        if change_t > t:
            break
        location = receptacle
    return location


REPEAT_PROBABILITY = 0.3
POST_MOVE_PROBABILITY = 0.5
POST_MOVE_LAG_S = (5 * 60, 60 * 60)


def _draw_question(mode: str, day: int, objects: List[str],
                   truth: Dict[str, List[Tuple[int, str]]],
                   recent: List[str], rng: random.Random,
                   pool: List[str],
                   spans: List[Tuple[int, int]]) -> Tuple[str, int]:
    """(object, t_query) for one question under the given query mode.

    Uniform mode draws objects WITHOUT replacement from ``pool`` (refilled
    with a fresh shuffle when empty, reset each day by the caller): every
    object is asked either floor or ceil of questions_per_day/n_objects
    times per day. Plain with-replacement sampling over few objects
    guarantees repeat lotteries — a day that happens to draw one displaced
    object 4-5 times swings that day's accuracy by whole tenths — which
    caps per-object repeats while keeping the draw uniform in expectation.
    """
    if mode == "uniform":
        if not pool:
            pool += rng.sample(objects, len(objects))
        return pool.pop(), draw_time(spans, day, rng)
    # naturalistic: popularity-weighted object, repeat bias, post-move timing
    if recent and rng.random() < REPEAT_PROBABILITY:
        obj = rng.choice(recent[-3:])
    else:
        weights = [1 + len(truth[o]) - 1 for o in objects]
        obj = rng.choices(objects, weights=weights, k=1)[0]
    lo = spans[0][0] if spans else day * DAY_SECONDS + AWAKE_WINDOW_S[0]
    hi = spans[-1][1] if spans else day * DAY_SECONDS + AWAKE_WINDOW_S[1]
    moves_today = [t for t, _ in truth[obj] if lo <= t < hi]
    if moves_today and rng.random() < POST_MOVE_PROBABILITY:
        t = min(rng.choice(moves_today) + rng.randrange(*POST_MOVE_LAG_S),
                hi - 1)
    else:
        t = draw_time(spans, day, rng)
    return obj, t



def _room_visit_rows(spec_path: pathlib.Path, timeline: pathlib.Path,
                     truth: Dict[str, List[Tuple[int, str]]], n_days: int,
                     awake: Dict[int, List[Tuple[int, int]]],
                     episode_id: str, patrol: str, visits_per_day: int,
                     seed: int) -> List[Dict[str, Any]]:
    """Observation rows produced by a room-visit patrol.

    Each visit is written as one ``room_visit`` row whose ``contents``
    map every inspected receptacle (empty ones included) to the objects
    found in it. The loader replays a visit to the beliefs as one sense
    result per receptacle, so a visit delivers positive sightings AND
    exclusions through the machinery the belief base class already has.
    """
    from baselines.room_observations import (RoomMap, build_schedules,
                                             realize)

    if visits_per_day < 0:
        raise ValueError(f"visits_per_day {visits_per_day} must be >= 0")
    if visits_per_day == 0:
        # No patrol at all (the cold-start recipe): the ambient stream is
        # empty and every sighting a policy ever holds is one it paid for.
        logger.info("patrol %s: visits_per_day=0, no ambient sightings",
                    patrol)
        return []
    room_map = RoomMap.from_spec(spec_path)
    schedules = build_schedules(room_map, n_days, awake, timeline,
                                visits_per_day, seed)
    if patrol not in schedules:
        raise ValueError(f"unknown patrol {patrol!r}; "
                         f"known: {sorted(schedules)}")
    visits = schedules[patrol]
    stream = realize(visits, room_map, truth, episode_id,
                     _away_intervals(timeline))
    logger.info("patrol %s: %d visits -> %d sightings (%.2f per object-day)",
                patrol, len(visits), len(stream.sightings),
                len(stream.sightings) / max(1, len(truth) * n_days))
    return stream.visit_rows


def _receptacle_rooms(spec_path: pathlib.Path,
                      receptacles: List[str]) -> Optional[Dict[str, str]]:
    """receptacle -> room for every in-house receptacle, from the spec.

    Uses the same :class:`~baselines.room_observations.RoomMap` the
    room-visit patrols are built from, so the header's rooms and the
    ambient stream's rooms can never disagree. Neither ON_PERSON nor
    OUT_OF_HOUSE appears: both are unsensable and belong to no room.
    Specs whose receptacles carry no ``room`` field (old glimpse-era
    schedule specs) yield None: the bank simply carries no room map.
    """
    from baselines.room_observations import RoomMap

    try:
        room_map = RoomMap.from_spec(spec_path)
    except ValueError:
        logger.info("spec %s has receptacles without rooms; bank will "
                    "carry no room map", spec_path)
        return None
    # ON_PERSON's pseudo-room is a scheduling device for the follow-person
    # patrol, not a place the robot can stand next to: it stays out of the
    # header, so no policy can target it.
    return {r: room_map.room_by_receptacle[r] for r in receptacles
            if r in room_map.room_by_receptacle and r != ON_PERSON}


def home_base_room(receptacle_rooms: Dict[str, str]) -> str:
    """The room with the most receptacles, ties broken by room id sort
    order — where the robot starts each day."""
    counts: Dict[str, int] = {}
    for room in receptacle_rooms.values():
        counts[room] = counts.get(room, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


PREMISES_BY_HOUSEHOLD_TYPE: Dict[str, Dict[str, str]] = {
    "working_professional_solo": {"composition": "solo",
                                  "work_pattern": "works_away"},
    "single_adult_wfh": {"composition": "solo",
                         "work_pattern": "works_from_home"},
    "single_senior_solo": {"composition": "solo",
                           "work_pattern": "no_fixed_work"},
    "working_couple_no_children": {"composition": "couple",
                                   "work_pattern": "works_away"},
    "remote_worker_couple": {"composition": "couple",
                             "work_pattern": "works_from_home"},
    "retired_couple": {"composition": "couple",
                       "work_pattern": "no_fixed_work"},
    "couple_with_toddler": {"composition": "family_with_children",
                            "work_pattern": "works_away"},
    "family_teen_and_child": {"composition": "family_with_children",
                              "work_pattern": "works_away"},
    "single_parent_teens": {"composition": "family_with_children",
                            "work_pattern": "works_away"},
    "college_roommates": {"composition": "roommates",
                          "work_pattern": "no_fixed_work"},
    "multigenerational_family": {"composition": "multigenerational",
                                 "work_pattern": "works_away"},
    "researcher_household": {"composition": "couple",
                             "work_pattern": "works_away"},
}
"""Ground-truth premise labels per generated household type: what the
generator assumed about composition and the primary work pattern. The
schedule suffix of a type (``__night_shift``, ``__rotating_shift``,
``__irregular_gig``, ``__opposite_schedules``) overrides the work
pattern (see :func:`premise_labels`). A persona or spec may also state
``premises`` explicitly, which wins."""

_SUFFIX_WORK_PATTERN = {
    "night_shift": "shift_work", "rotating_shift": "shift_work",
    "irregular_gig": "no_fixed_work",
    "opposite_schedules": "opposite_schedules"}


def premise_labels(spec: Mapping[str, Any],
                   profile: Mapping[str, Any]) -> Dict[str, str]:
    """The bank's ground-truth premise labels: explicit ``premises`` on
    the spec or persona if present, else derived from the household
    type. Empty when nothing is known."""
    explicit = spec.get("premises") or profile.get("premises")
    if isinstance(explicit, Mapping) and explicit:
        return {str(k): str(v) for k, v in explicit.items()}
    household_type = str(spec.get("household_type")
                         or profile.get("household_type") or "")
    if not household_type:
        return {}
    base, _, suffix = household_type.partition("__")
    labels = dict(PREMISES_BY_HOUSEHOLD_TYPE.get(base, {}))
    if suffix in _SUFFIX_WORK_PATTERN and labels:
        labels["work_pattern"] = _SUFFIX_WORK_PATTERN[suffix]
    return labels


def export(timeline: pathlib.Path, spec_path: pathlib.Path, out: pathlib.Path,
           seed: int, sightings_per_day: int, questions_per_day: int,
           first_question_day: int, budget_per_day: int,
           query_mode: str = "uniform",
           initial_tour: bool = True,
           tour_start: str = "day0",
           tour_max_day: int = 1,
           sightings_per_object_day: Optional[float] = None,
           budget_per_sensable_receptacle: Optional[float] = None,
           observation_model: str = "glimpse",
           patrol: str = "round_robin_patrol",
           visits_per_day: int = 8,
           query_generation: str = "uniform",
           query_rules: Optional[pathlib.Path] = None,
           person_sensing: bool = False) -> JsonlBank:
    """Write the bank JSONL and return its loader (which re-validates it).

    ``person_sensing`` writes the bank version on which a policy can look
    at a resident (module docstring): the header declares it with the
    roster, every ``ON_PERSON`` truth row names its carrier, and one
    ``resident`` row stream per resident carries the room trajectory.
    Off (the default) nothing about the file changes.

    ``observation_model`` selects how the ambient stream is produced:

    * ``glimpse`` (the original) draws one random object at one random
      awake instant, ``sightings_per_day`` times — an omniscient but
      extremely sparse observer with no spatial structure. Over a
      30-50-object inventory it delivers well under one sighting per
      object per DAY, so most beliefs run on days-old evidence.
    * ``room_visit`` runs a patrol schedule from
      :mod:`baselines.room_observations`: each visit reveals every
      receptacle in one room at once, which is both physically grounded
      and far more informative per event (a visit yields several
      sightings, and the same primitive serves an active policy's paid
      sense). ``patrol`` names the schedule and ``visits_per_day`` its
      budget where the schedule takes one.

    ``query_generation`` selects how questions are produced and is
    recorded in the episode header:

    * ``uniform`` — the existing machinery (``query_mode`` picks its
      uniform or naturalistic flavour), unchanged.
    * ``routine_driven`` — questions triggered by the timeline's realized
      activities under the rules of ``query_rules`` (a YAML file, see
      :mod:`baselines.query_stream`), plus a small background rate.
      ``query_mode`` is ignored. Each question row carries an ``origin``.

    ``tour_start`` places the installation tour: ``day0`` at t=0 (every
    object at its home), ``random`` at a per-seed awake instant on a day
    in ``[0, tour_max_day]`` (see the module docstring). Evidence and
    questions before the tour instant are not exported.

    ``sightings_per_object_day`` and ``budget_per_sensable_receptacle``,
    when set, REPLACE the corresponding absolute setting with a rule
    scaled to the household's size:
    ``sightings_per_day = ceil(rate * n_objects)`` and
    ``budget_per_day = ceil(rate * n_sensable_receptacles)``. A flat
    absolute rate is not household-agnostic — the same 10 sightings/day
    is 0.6 per object in a 17-object house and 0.19 in a 53-object one,
    so beliefs in the large house never accumulate enough evidence per
    object to differ from each other. Scaling rules keep the per-object
    evidence budget (and the per-receptacle search budget) constant
    across household sizes, which is what makes gate readings comparable
    across a fleet.
    """
    spec = yaml.safe_load(spec_path.read_text())
    # New-format specs (object_motions.yaml) name it `source_persona`; the
    # retired schedule specs said `source_profile`. Accept either.
    persona_ref = spec.get("source_persona") or spec["source_profile"]
    profile = yaml.safe_load(
        (spec_path.parent / persona_ref).resolve().read_text())
    object_classes = {o["id"]: o["class"] for o in profile["object_inventory"]}
    receptacles = [r["id"] for r in spec["receptacles"]] + [ON_PERSON, OUT_OF_HOUSE]
    if sightings_per_object_day is not None:
        sightings_per_day = math.ceil(
            sightings_per_object_day * len(object_classes))
    if budget_per_sensable_receptacle is not None:
        # OUT_OF_HOUSE and ON_PERSON are unsensable; every other
        # receptacle is a target.
        budget_per_day = math.ceil(
            budget_per_sensable_receptacle * (len(receptacles) - len(UNSENSABLE)))
    logger.info("export sizing: %d objects, %d receptacles -> %d "
                "sightings/day, budget %d/day", len(object_classes),
                len(receptacles), sightings_per_day, budget_per_day)

    truth, n_days, causes, carriers = load_truth_with_carriers(timeline)
    awake = awake_spans(timeline, n_days)
    episode_id = f"{spec['household']}_{timeline.name}"
    resident_rooms: Dict[str, List[Tuple[int, str]]] = {}
    if person_sensing:
        resident_rooms = resident_room_trajectories(spec_path, timeline)
        if not resident_rooms:
            raise ValueError(f"{timeline}: person_sensing needs "
                             f"residents.jsonl")
    tour_t = draw_tour_instant(tour_start, tour_max_day, n_days, awake,
                               _derived_rng(seed, "tour", episode_id))
    logger.info("tour instant: %s (t=%d)", stamp(tour_t), tour_t)
    # Sightings and questions draw from SEPARATE seeded generators so the
    # question set is invariant under changes to the sighting rate (and
    # vice versa) — each axis can be swept without perturbing the other.
    rng_sightings = _derived_rng(seed, "sightings", episode_id)
    rng_questions = _derived_rng(seed, "questions", query_mode, episode_id)
    objects = sorted(object_classes)

    if query_mode not in ("uniform", "naturalistic"):
        raise ValueError(f"unknown query_mode {query_mode!r}")
    if query_generation not in ("uniform", "routine_driven"):
        raise ValueError(f"unknown query_generation {query_generation!r}")
    rule_set = None
    if query_generation == "routine_driven":
        from baselines.query_stream import load_query_rules
        if query_rules is None:
            raise ValueError("query_generation=routine_driven needs a "
                             "query_rules file")
        rule_set = load_query_rules(query_rules)
    header: Dict[str, Any] = {
        "kind": "episode_header", "episode_id": episode_id,
        "household_id": spec["household"], "receptacle_ids": receptacles,
        "object_classes": object_classes, "query_mode": query_mode,
        "query_generation": query_generation,
        "budget_per_day": budget_per_day, "n_days": n_days,
        "observation_model": observation_model,
        "tour_start": tour_start, "tour_t": tour_t,
        "first_question_day": first_question_day}
    if rule_set is not None:
        header["query_rules_file"] = str(query_rules)
        header["background_query_rate"] = rule_set.background_query_rate
    if observation_model == "room_visit":
        header["patrol"] = patrol
        header["visits_per_day"] = visits_per_day
    if "household_type" in spec:
        # Optional metadata consumed by the healthcheck's stratified
        # discriminative gate; absent from older schedule specs.
        header["household_type"] = str(spec["household_type"])
    premises = premise_labels(spec, profile)
    if premises:
        header["premises"] = premises
    header["unsensable_receptacles"] = list(UNSENSABLE)
    receptacle_rooms = _receptacle_rooms(spec_path, receptacles)
    if receptacle_rooms is not None:
        header["receptacle_rooms"] = receptacle_rooms
        header["home_base_room"] = home_base_room(receptacle_rooms)
    if person_sensing:
        header["person_sensing"] = True
        header["resident_ids"] = sorted(resident_rooms)
    rows: List[Dict[str, Any]] = [header]
    unobserved = 0
    for obj in objects:
        for t, receptacle in truth[obj]:
            row = {"kind": "truth", "episode_id": episode_id,
                   "object_id": obj, "t": t, "receptacle_id": receptacle}
            if causes.get((obj, t)):
                row["cause"] = causes[(obj, t)]   # provenance; loader ignores
            if person_sensing and receptacle == ON_PERSON:
                row["carrier"] = carriers[(obj, t)]
            rows.append(row)
        if initial_tour:
            where = truth_at(truth[obj], tour_t)
            if where in UNSENSABLE:
                unobserved += 1  # out, or in a pocket, when the robot arrived
            else:
                rows.append({"kind": "observation", "episode_id": episode_id,
                             "object_id": obj, "receptacle_id": where,
                             "t": tour_t, "source": "initial_tour"})
    for resident in sorted(resident_rooms):
        for t, room in resident_rooms[resident]:
            rows.append({"kind": "resident", "episode_id": episode_id,
                         "resident_id": resident, "t": t, "room": room})
    if observation_model == "room_visit":
        visit_rows = _room_visit_rows(spec_path, timeline, truth, n_days,
                                      awake, episode_id, patrol,
                                      visits_per_day, seed)
        before_tour = sum(1 for r in visit_rows if r["t"] < tour_t)
        rows += [r for r in visit_rows if r["t"] >= tour_t]
        if before_tour:
            logger.info("dropped %d room visits before the tour", before_tour)
    elif observation_model == "glimpse":
        for day in range(n_days):
            for _ in range(sightings_per_day):
                obj = rng_sightings.choice(objects)
                t = draw_time(awake[day], day, rng_sightings)
                if t < tour_t:
                    continue  # the robot was not installed yet
                where = truth_at(truth[obj], t)
                if where in UNSENSABLE:
                    unobserved += 1  # you cannot sight what is not there
                    continue
                rows.append({"kind": "observation", "episode_id": episode_id,
                             "object_id": obj, "t": t, "source": "scripted",
                             "receptacle_id": where})
    else:
        raise ValueError(f"unknown observation_model {observation_model!r}")
    if unobserved:
        logger.info("dropped %d sightings of out-of-house or carried "
                    "objects (unobservable)", unobserved)
    question_number = 0
    if rule_set is not None:
        from baselines.query_stream import (activity_instances,
                                            routine_questions)
        rng_routine = _derived_rng(seed, "questions", "routine_driven",
                                   episode_id)
        stream = routine_questions(
            activity_instances(timeline), rule_set, object_classes, awake,
            n_days, first_question_day, questions_per_day, rng_routine)
        for obj, t, origin in stream:
            if t < tour_t:
                continue
            rows.append({"kind": "question", "episode_id": episode_id,
                         "question_id": f"q{question_number:04d}",
                         "object_id": obj,
                         "object_class": object_classes[obj],
                         "t_query": t, "day_index": t // DAY_SECONDS,
                         "origin": origin})
            question_number += 1
    else:
        recent: List[str] = []
        for day in range(first_question_day, n_days):
            pool: List[str] = []      # uniform mode: fresh no-repeat pool daily
            for _ in range(questions_per_day):
                obj, t = _draw_question(query_mode, day, objects, truth,
                                        recent, rng_questions, pool,
                                        awake[day])
                recent.append(obj)
                if t < tour_t:
                    continue  # drawn (so later seeds' streams stay put), not asked
                rows.append({"kind": "question", "episode_id": episode_id,
                             "question_id": f"q{question_number:04d}",
                             "object_id": obj,
                             "object_class": object_classes[obj],
                             "t_query": t, "day_index": day})
                question_number += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    bank = JsonlBank(path=out)
    episode = next(bank.episodes())  # validate through the real loader
    logger.info("exported %s: %d objects, %d days, %d questions -> %s",
                episode.episode_id, len(episode.object_classes),
                episode.n_days,
                sum(len(d) for d in episode.questions_by_day), out)
    return bank


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=pathlib.Path, required=True)
    parser.add_argument("--spec", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--sightings-per-day", type=int, default=3)
    parser.add_argument("--questions-per-day", type=int, default=4)
    parser.add_argument("--first-question-day", type=int, default=3)
    parser.add_argument("--budget-per-day", type=int, default=2)
    parser.add_argument("--query-mode", default="uniform",
                        choices=("uniform", "naturalistic"))
    parser.add_argument("--query-generation", default="uniform",
                        choices=("uniform", "routine_driven"))
    parser.add_argument("--query-rules", type=pathlib.Path, default=None,
                        help="rules YAML for --query-generation "
                             "routine_driven (see baselines.query_stream)")
    parser.add_argument("--no-initial-tour", action="store_true",
                        help="omit the installation snapshot; agents start "
                             "blind")
    parser.add_argument("--tour-start", default="day0",
                        choices=("day0", "random"),
                        help="tour at t=0 (objects at their homes) or at a "
                             "per-seed random awake instant on a day in "
                             "[0, --tour-max-day]")
    parser.add_argument("--tour-max-day", type=int, default=1,
                        help="latest day the random tour may fall on; "
                             "evidence and questions before the tour are "
                             "not exported, so each day here costs a day "
                             "of episode")
    parser.add_argument("--observation-model", default="glimpse",
                        choices=("glimpse", "room_visit"))
    parser.add_argument("--patrol", default="round_robin_patrol",
                        help="patrol schedule for --observation-model "
                             "room_visit (see baselines.room_observations)")
    parser.add_argument("--visits-per-day", type=int, default=8)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    export(args.timeline, args.spec, args.out, args.seed,
           args.sightings_per_day, args.questions_per_day,
           args.first_question_day, args.budget_per_day, args.query_mode,
           initial_tour=not args.no_initial_tour,
           tour_start=args.tour_start, tour_max_day=args.tour_max_day,
           observation_model=args.observation_model, patrol=args.patrol,
           visits_per_day=args.visits_per_day,
           query_generation=args.query_generation,
           query_rules=args.query_rules)


if __name__ == "__main__":
    main()
