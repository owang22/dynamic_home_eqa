"""Room-visit observation model and patrol schedules.

Replaces the random-glimpse observation process (one random object at one
random instant) with a physically grounded primitive: a ROOM VISIT at time
t reveals the contents of every receptacle in that room at that instant.
Positive evidence (object X is at receptacle R) and implicit negative
evidence (no other object is in this room's receptacles right now) both
fall out of the same event. The passive stream becomes a fixed,
agent-independent schedule of room visits; an active sense is one extra
room visit chosen by the policy. Both halves of the study then share one
observation primitive.

Precedent: this mirrors how long-term-autonomy deployments actually
observed their environments. The STRANDS project robots patrolled a fixed
set of topological nodes on schedules and built FreMEn models from what
each visit revealed; Santos et al. (RA-L 2016) and Krajnik et al.
(ECMR 2015) studied exactly the question of which node to visit when,
comparing uniform, round-robin, random, and information-driven revisit
schedules. The schedule family below covers the non-adaptive members of
that design space (adaptive/information-driven scheduling is an ACTIVE
policy in this codebase, not a scripted stream, so it is deliberately
absent here).

Patrol schedules provided (all deterministic given a seed):

* ``morning_evening_sweep`` -- every room, in fixed order, at two fixed
  clock times. The "tidying robot does its rounds" story; dense, evenly
  aged evidence.
* ``round_robin_patrol`` -- one room per slot at N evenly spaced times
  across awake hours, cycling rooms in order. The classic deployment
  patrol; same total visit count as ``random_room_walk`` but with bounded
  revisit gaps.
* ``random_room_walk`` -- one uniformly random room at a uniformly random
  awake instant, N times per day. The control closest to the retired
  glimpse model, but room-bundled.
* ``stationed_observer`` -- the robot idles in a home-base room, sampling
  it every ``station_interval_s`` during awake hours, with a few excursion
  visits to random other rooms per day. Models a mostly-parked assistant;
  produces heavily skewed evidence age across rooms, which is the
  interesting stress case for staleness-driven active policies.
* ``follow_the_person`` -- N visits per day to whichever room the followed
  resident currently occupies (resident blocks are anchored at
  receptacles, so their room is derivable). Models a companion robot;
  evidence correlates with activity, which is where routine structure
  should become visible to belief models.

All times are seconds since episode start; a day is 86 400 s.

Standalone comparison of the schedules on one household:

    python -m baselines.room_observations <timeline_dir> <spec.yaml>
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import pathlib
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import yaml

from baselines.export_bank import (ON_PERSON, OUT_OF_HOUSE, _away_intervals,
                                   awake_spans, draw_time, load_truth,
                                   truth_at)
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

PERSON_CHECK_ROOM = "person_check"
"""Pseudo-room whose only receptacle is ON_PERSON. Visitable only while
the followed resident is home; OUT_OF_HOUSE belongs to no room and is
never visitable, preserving the existing unsensability rule."""

_H = 3600


# ---------------------------------------------------------------------------
# Room structure
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RoomMap:
    """Receptacle-to-room structure for one household.

    ``rooms`` preserves spec order (stable across runs); ``by_room`` maps
    room -> tuple of receptacle ids. ON_PERSON belongs to the pseudo-room
    :data:`PERSON_CHECK_ROOM`; OUT_OF_HOUSE belongs to no room.
    """

    by_room: Dict[str, Tuple[str, ...]]
    rooms: Tuple[str, ...]
    room_by_receptacle: Dict[str, str]

    @staticmethod
    def from_spec(spec_path: pathlib.Path) -> "RoomMap":
        """Build from a program/motions spec's ``receptacles`` list."""
        spec = yaml.safe_load(spec_path.read_text())
        by_room: Dict[str, List[str]] = collections.OrderedDict()
        for entry in spec["receptacles"]:
            if "room" not in entry:
                raise ValueError(
                    f"{spec_path}: receptacle {entry.get('id')!r} has no "
                    f"'room'; the room-visit observation model needs one")
            by_room.setdefault(str(entry["room"]), []).append(str(entry["id"]))
        by_room[PERSON_CHECK_ROOM] = [ON_PERSON]
        return RoomMap(
            by_room={k: tuple(v) for k, v in by_room.items()},
            rooms=tuple(by_room),
            room_by_receptacle={r: room for room, rs in by_room.items()
                                for r in rs})

    @property
    def physical_rooms(self) -> Tuple[str, ...]:
        """Rooms a patrol may visit (everything but the person pseudo-room)."""
        return tuple(r for r in self.rooms if r != PERSON_CHECK_ROOM)

    def room_of(self, receptacle_id: str) -> Optional[str]:
        """The room holding ``receptacle_id``, or None (e.g. OUT_OF_HOUSE)."""
        return self.room_by_receptacle.get(receptacle_id)


@dataclass(frozen=True)
class RoomVisit:
    """One scheduled visit: the robot is in ``room`` at instant ``t``."""

    t: int
    room: str


def _offset_into_spans(spans: Sequence[Tuple[int, int]], offset: int) -> int:
    """Map an offset along concatenated spans back to an absolute time."""
    for a, b in spans:
        if offset < b - a:
            return a + offset
        offset -= b - a
    return spans[-1][1] - 1


def _spans_for(awake: Dict[int, List[Tuple[int, int]]],
               day: int) -> List[Tuple[int, int]]:
    """The day's awake spans, falling back to a plain daytime window when a
    day has none (e.g. a 24 h whole-household absence)."""
    spans = awake.get(day) or []
    if spans:
        return spans
    return [(day * DAY_SECONDS + 8 * _H, day * DAY_SECONDS + 22 * _H)]


# ---------------------------------------------------------------------------
# Patrol schedules
# ---------------------------------------------------------------------------

def morning_evening_sweep(room_map: RoomMap, n_days: int,
                          sweep_hours: Sequence[int] = (9, 19),
                          minutes_per_room: int = 2) -> List[RoomVisit]:
    """Full-house sweeps at fixed clock times, rooms in spec order.

    Successive rooms within one sweep are minutes apart, modelling a single
    continuous pass rather than teleportation; the offset also keeps visit
    timestamps distinct, which downstream ordering relies on.
    """
    visits = [RoomVisit(t=day * DAY_SECONDS + hour * _H
                        + i * minutes_per_room * 60, room=room)
              for day in range(n_days)
              for hour in sweep_hours
              for i, room in enumerate(room_map.physical_rooms)]
    return sorted(visits, key=lambda v: v.t)


def round_robin_patrol(room_map: RoomMap, n_days: int,
                       awake: Dict[int, List[Tuple[int, int]]],
                       visits_per_day: int, seed: int) -> List[RoomVisit]:
    """One room per slot, cycling rooms in order, at evenly spaced awake
    times with small seeded jitter so slot times are not clock-aligned
    across households. Revisit gaps are bounded: every room is seen at
    least once per ceil(n_rooms / visits_per_day) days.
    """
    rng = random.Random(seed)
    physical = room_map.physical_rooms
    visits: List[RoomVisit] = []
    cursor = 0
    for day in range(n_days):
        spans = _spans_for(awake, day)
        total = sum(b - a for a, b in spans)
        for slot in range(visits_per_day):
            offset = (total * (2 * slot + 1)) // (2 * visits_per_day)
            offset = max(0, min(total - 1, offset + rng.randrange(-600, 601)))
            visits.append(RoomVisit(t=_offset_into_spans(spans, offset),
                                    room=physical[cursor % len(physical)]))
            cursor += 1
    return sorted(visits, key=lambda v: v.t)


def random_room_walk(room_map: RoomMap, n_days: int,
                     awake: Dict[int, List[Tuple[int, int]]],
                     visits_per_day: int, seed: int) -> List[RoomVisit]:
    """Uniform random room at a uniform awake instant. The control
    schedule: closest surviving relative of the retired glimpse model."""
    rng = random.Random(seed)
    physical = room_map.physical_rooms
    visits = [RoomVisit(t=draw_time(_spans_for(awake, day), day, rng),
                        room=rng.choice(physical))
              for day in range(n_days) for _ in range(visits_per_day)]
    return sorted(visits, key=lambda v: v.t)


def stationed_observer(room_map: RoomMap, n_days: int,
                       awake: Dict[int, List[Tuple[int, int]]],
                       home_room: str, station_interval_s: int,
                       excursions_per_day: int, seed: int) -> List[RoomVisit]:
    """Home-base sampling plus a few random excursions.

    The home room is observed every ``station_interval_s`` of awake time;
    ``excursions_per_day`` visits go to uniformly random other rooms. The
    resulting evidence-age skew (fresh at home, stale elsewhere) is the
    stress case for staleness-driven policies.
    """
    if home_room not in room_map.by_room or home_room == PERSON_CHECK_ROOM:
        raise ValueError(f"unknown home_room {home_room!r}")
    rng = random.Random(seed)
    others = [r for r in room_map.physical_rooms if r != home_room]
    visits: List[RoomVisit] = []
    for day in range(n_days):
        spans = _spans_for(awake, day)
        for a, b in spans:
            for t in range(a, b, station_interval_s):
                visits.append(RoomVisit(t=t, room=home_room))
        for _ in range(excursions_per_day):
            visits.append(RoomVisit(t=draw_time(spans, day, rng),
                                    room=rng.choice(others)))
    return sorted(visits, key=lambda v: v.t)


def _resident_room_lookup(timeline: pathlib.Path, resident: str,
                          room_map: RoomMap
                          ) -> List[Tuple[int, int, Optional[str]]]:
    """Sorted (t0, t1, room-or-None) blocks for ONE resident.

    Restricting to a single resident is required for determinism: with
    several residents the blocks overlap, and "the active block" would
    otherwise depend on file order rather than on who is being followed.
    ``None`` marks a block spent away from home.
    """
    blocks: List[Tuple[int, int, Optional[str]]] = []
    with open(timeline / "residents.jsonl") as f:
        for line in f:
            b = json.loads(line)
            if str(b["resident"]) != resident:
                continue
            at = str(b["at"])
            blocks.append((int(b["t0"]) * 60, int(b["t1"]) * 60,
                           None if at == "ELSEWHERE" else room_map.room_of(at)))
    if not blocks:
        raise ValueError(f"{timeline}: no blocks for resident {resident!r}")
    return sorted(blocks)


def follow_the_person(room_map: RoomMap, n_days: int,
                      awake: Dict[int, List[Tuple[int, int]]],
                      timeline: pathlib.Path, visits_per_day: int,
                      seed: int, resident: Optional[str] = None,
                      check_person: bool = True) -> List[RoomVisit]:
    """Visits the room the followed resident occupies at each sampled time.

    Resident blocks are anchored at receptacles, so the occupied room is
    that receptacle's room. Sampled instants where the resident is away
    fall back to a random room: the companion robot wanders when its
    person is out. With ``check_person``, each at-home visit is paired with
    a person-check visit at the same instant, so carried objects are
    observed exactly when the robot is with the carrier.
    """
    rng = random.Random(seed)
    followed = resident or _first_resident(timeline)
    blocks = _resident_room_lookup(timeline, followed, room_map)
    physical = room_map.physical_rooms

    def room_at(t: int) -> Optional[str]:
        return next((room for t0, t1, room in blocks if t0 <= t < t1), None)

    visits: List[RoomVisit] = []
    for day in range(n_days):
        for _ in range(visits_per_day):
            t = draw_time(_spans_for(awake, day), day, rng)
            room = room_at(t)
            if room is None:
                visits.append(RoomVisit(t=t, room=rng.choice(physical)))
                continue
            visits.append(RoomVisit(t=t, room=room))
            if check_person:
                visits.append(RoomVisit(t=t, room=PERSON_CHECK_ROOM))
    return sorted(visits, key=lambda v: v.t)


def _first_resident(timeline: pathlib.Path) -> str:
    """The lowest-numbered resident id in the timeline (stable default)."""
    with open(timeline / "residents.jsonl") as f:
        residents = {str(json.loads(line)["resident"]) for line in f}
    return sorted(residents)[0]


# ---------------------------------------------------------------------------
# Realization: schedule x ground truth -> observation stream
# ---------------------------------------------------------------------------

@dataclass
class RealizedStream:
    """Bank-ready rows for one schedule.

    ``sightings`` are ordinary observation rows (existing schema, source
    ``scripted``): every object truly inside the visited room's receptacles
    at the visit instant. ``visit_rows`` are the bank rows a room-visit
    export actually writes: each carries ``contents`` — the exact objects
    found in EVERY inspected receptacle, empty receptacles included —
    which is both halves of the evidence at once (the objects listed are
    positive sightings; every known object missing from an inspected
    receptacle was demonstrably not there). The loader replays a visit to
    the beliefs as one sense result per receptacle, so the existing
    negative-evidence machinery in the belief base class applies with no
    new belief code. ``sightings`` is kept for stream statistics and for
    consumers that only need the positive half.
    ``dropped_person_visits`` counts person-checks scheduled while the
    followed resident was away, matching the existing convention that an
    absent person cannot be inspected.
    """

    sightings: List[Dict[str, object]] = field(default_factory=list)
    visit_rows: List[Dict[str, object]] = field(default_factory=list)
    dropped_person_visits: int = 0


def realize(visits: Sequence[RoomVisit], room_map: RoomMap,
            truth: Dict[str, List[Tuple[int, str]]], episode_id: str,
            away: Optional[Dict[str, List[Tuple[int, int]]]] = None
            ) -> RealizedStream:
    """Expand scheduled visits into observation and room_visit rows.

    A visit to room R at time t yields one sighting per object whose true
    receptacle at t lies in R, plus one room_visit row naming R's
    receptacles and the objects found. Objects at OUT_OF_HOUSE are never
    observed anywhere, preserving the unsensability rule.

    A person-check is dropped only when NOBODY is home (from ``away``);
    a check on a resident who is home but carrying nothing is kept, since
    "nothing is on the person right now" is exactly the negative evidence
    the room-visit primitive exists to record.
    """
    stream = RealizedStream()
    objects = sorted(truth)
    for visit in visits:
        if visit.room == PERSON_CHECK_ROOM and _nobody_home(away, visit.t):
            stream.dropped_person_visits += 1
            continue
        receptacles = room_map.by_room[visit.room]
        contents: Dict[str, List[str]] = {r: [] for r in receptacles}
        for obj in objects:
            where = truth_at(truth[obj], visit.t)
            if where in contents and where != OUT_OF_HOUSE:
                contents[where].append(obj)
                stream.sightings.append({
                    "kind": "observation", "episode_id": episode_id,
                    "object_id": obj, "receptacle_id": where,
                    "t": visit.t, "source": "scripted"})
        stream.visit_rows.append({
            "kind": "room_visit", "episode_id": episode_id,
            "t": visit.t, "room": visit.room, "contents": contents})
    return stream


def _nobody_home(away: Optional[Dict[str, List[Tuple[int, int]]]],
                 t: int) -> bool:
    """True when every resident with recorded absences is out at ``t``.

    Without away information (stub timelines) the house counts as
    occupied, matching the exporter's always-ON_PERSON fallback.
    """
    if not away:
        return False
    return all(any(a <= t < b for a, b in spans) for spans in away.values())


# ---------------------------------------------------------------------------
# Standalone comparison of schedules on one household
# ---------------------------------------------------------------------------

def stream_stats(stream: RealizedStream, visits: Sequence[RoomVisit],
                 truth: Dict[str, List[Tuple[int, str]]],
                 n_days: int) -> Dict[str, float]:
    """Difficulty-relevant descriptive statistics for one realized stream."""
    per_object = collections.Counter(
        str(s["object_id"]) for s in stream.sightings)
    n_objects = len(truth)
    gaps: List[int] = []
    last_by_room: Dict[str, int] = {}
    for v in visits:
        if v.room in last_by_room:
            gaps.append(v.t - last_by_room[v.room])
        last_by_room[v.room] = v.t
    object_gaps = _object_gap_hours(stream, n_objects)
    return {
        "visits_per_day": round(len(visits) / n_days, 1),
        "sightings_per_day": round(len(stream.sightings) / n_days, 1),
        "per_object_day": round(
            len(stream.sightings) / (n_objects * n_days), 2),
        "never_seen": n_objects - len(per_object),
        "median_room_revisit_h": round(
            sorted(gaps)[len(gaps) // 2] / _H, 1) if gaps else float("inf"),
        "median_object_gap_h": object_gaps,
    }


def _object_gap_hours(stream: RealizedStream, n_objects: int) -> float:
    """Median gap in hours between consecutive sightings of one object —
    the staleness a passive belief actually contends with."""
    times: Dict[str, List[int]] = collections.defaultdict(list)
    for s in stream.sightings:
        times[str(s["object_id"])].append(int(str(s["t"])))
    gaps: List[int] = []
    for ts in times.values():
        ordered = sorted(ts)
        gaps += [ordered[i + 1] - ordered[i] for i in range(len(ordered) - 1)]
    if not gaps:
        return float("inf")
    return round(sorted(gaps)[len(gaps) // 2] / _H, 1)


def busiest_room(timeline: pathlib.Path, room_map: RoomMap) -> str:
    """The room residents spend the most time in — the sensible station for
    a parked assistant, and stable across seeds."""
    occupancy: Dict[str, int] = collections.defaultdict(int)
    with open(timeline / "residents.jsonl") as f:
        for line in f:
            b = json.loads(line)
            room = room_map.room_of(str(b["at"]))
            if room is not None and room != PERSON_CHECK_ROOM:
                occupancy[room] += (int(b["t1"]) - int(b["t0"])) * 60
    return max(occupancy, key=lambda r: occupancy[r])


def build_schedules(room_map: RoomMap, n_days: int,
                    awake: Dict[int, List[Tuple[int, int]]],
                    timeline: pathlib.Path, visits_per_day: int,
                    seed: int) -> Dict[str, List[RoomVisit]]:
    """Every schedule at a shared per-day visit budget, for comparison.

    ``morning_evening_sweep`` and ``stationed_observer`` set their own
    visit counts by construction (a full sweep, a fixed idle interval);
    the other three take ``visits_per_day``.
    """
    return {
        "morning_evening_sweep": morning_evening_sweep(room_map, n_days),
        "round_robin_patrol": round_robin_patrol(
            room_map, n_days, awake, visits_per_day, seed),
        "random_room_walk": random_room_walk(
            room_map, n_days, awake, visits_per_day, seed),
        "stationed_observer": stationed_observer(
            room_map, n_days, awake, busiest_room(timeline, room_map),
            station_interval_s=2 * _H, excursions_per_day=3, seed=seed),
        "follow_the_person": follow_the_person(
            room_map, n_days, awake, timeline, visits_per_day, seed),
    }


def main() -> None:
    """CLI entry point: compare every schedule on one household."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=pathlib.Path)
    parser.add_argument("spec", type=pathlib.Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--visits-per-day", type=int, default=None,
                        help="shared budget for the schedules that take one "
                             "(default: 2 x number of rooms)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")

    room_map = RoomMap.from_spec(args.spec)
    truth, n_days, _ = load_truth(args.timeline)
    awake = awake_spans(args.timeline, n_days)
    away = _away_intervals(args.timeline)
    n_rooms = len(room_map.physical_rooms)
    per_day = args.visits_per_day or 2 * n_rooms

    print(f"{args.timeline.name}: {len(truth)} objects, {n_rooms} rooms, "
          f"{n_days} days (shared budget {per_day} visits/day)")
    schedules = build_schedules(room_map, n_days, awake, args.timeline,
                                per_day, args.seed)
    for name, visits in schedules.items():
        stream = realize(visits, room_map, truth, args.timeline.name, away)
        stats = stream_stats(stream, visits, truth, n_days)
        print(f"  {name:24s} " + "  ".join(
            f"{k}={v}" for k, v in stats.items()))


if __name__ == "__main__":
    main()
