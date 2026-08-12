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
``ON_PERSON`` stays sensable — the robot may look at what a resident who
is HOME is carrying, and while they are away their carried objects are
OUT_OF_HOUSE by the projection above, so sensing ON_PERSON never leaks
information about an absent person.

Generated stream and questions (all seeded):

* initial tour (optional, ``--no-initial-tour`` to drop): every object's
  location at t=0. WITH the tour, a frozen belief starts from a perfect
  snapshot and scores the world's stationarity (~0.6 on hh_001) with zero
  learning; WITHOUT it, never-sensed objects sit at the uniform-fallback
  chance floor (~1/n_receptacles) and every point of accuracy must be
  earned through sensing.
* scripted sightings: ``--sightings-per-day`` per day, each a uniformly
  chosen object seen at a uniform time inside the awake window
  (08:00-22:00) at its true location — drive-by observations.
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
import pathlib
import random
from typing import Any, Dict, List, Tuple

import yaml

from baselines.bank import JsonlBank
from baselines.cli import _derived_rng
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

OUT_OF_HOUSE = "OUT_OF_HOUSE"
ON_PERSON = "ON_PERSON"
AWAKE_WINDOW_S = (8 * 3600, 22 * 3600)


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
    horizon = n_days * DAY_SECONDS
    for obj, segments in raw.items():
        points: List[Tuple[int, str]] = []
        for i, (t0, location) in enumerate(segments):
            t1 = segments[i + 1][0] if i + 1 < len(segments) else horizon
            for t, receptacle in _project_segment(location, t0, t1, away):
                if not points or points[-1][1] != receptacle:
                    points.append((t, receptacle))
                    if (obj, t) not in causes:
                        # A synthesized boundary: the carrier left/returned.
                        causes[(obj, t)] = ("person_departure"
                                            if receptacle == OUT_OF_HOUSE
                                            else "person_return") if t else ""
        truth[obj] = points
    return truth, n_days, causes


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
                   pool: List[str]) -> Tuple[str, int]:
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
        return (pool.pop(),
                day * DAY_SECONDS + rng.randrange(*AWAKE_WINDOW_S))
    # naturalistic: popularity-weighted object, repeat bias, post-move timing
    if recent and rng.random() < REPEAT_PROBABILITY:
        obj = rng.choice(recent[-3:])
    else:
        weights = [1 + len(truth[o]) - 1 for o in objects]
        obj = rng.choices(objects, weights=weights, k=1)[0]
    window = (day * DAY_SECONDS + AWAKE_WINDOW_S[0],
              day * DAY_SECONDS + AWAKE_WINDOW_S[1])
    moves_today = [t for t, _ in truth[obj] if window[0] <= t < window[1]]
    if moves_today and rng.random() < POST_MOVE_PROBABILITY:
        t = rng.choice(moves_today) + rng.randrange(*POST_MOVE_LAG_S)
        t = min(t, window[1] - 1)
    else:
        t = rng.randrange(*window)
    return obj, t


def export(timeline: pathlib.Path, spec_path: pathlib.Path, out: pathlib.Path,
           seed: int, sightings_per_day: int, questions_per_day: int,
           first_question_day: int, budget_per_day: int,
           query_mode: str = "uniform",
           initial_tour: bool = True) -> JsonlBank:
    """Write the bank JSONL and return its loader (which re-validates it)."""
    spec = yaml.safe_load(spec_path.read_text())
    # New-format specs (object_motions.yaml) name it `source_persona`; the
    # retired schedule specs said `source_profile`. Accept either.
    persona_ref = spec.get("source_persona") or spec["source_profile"]
    profile = yaml.safe_load(
        (spec_path.parent / persona_ref).resolve().read_text())
    object_classes = {o["id"]: o["class"] for o in profile["object_inventory"]}
    receptacles = [r["id"] for r in spec["receptacles"]] + [ON_PERSON, OUT_OF_HOUSE]

    truth, n_days, causes = load_truth(timeline)
    episode_id = f"{spec['household']}_{timeline.name}"
    # Sightings and questions draw from SEPARATE seeded generators so the
    # question set is invariant under changes to the sighting rate (and
    # vice versa) — each axis can be swept without perturbing the other.
    rng_sightings = _derived_rng(seed, "sightings", episode_id)
    rng_questions = _derived_rng(seed, "questions", query_mode, episode_id)
    objects = sorted(object_classes)

    if query_mode not in ("uniform", "naturalistic"):
        raise ValueError(f"unknown query_mode {query_mode!r}")
    header: Dict[str, Any] = {
        "kind": "episode_header", "episode_id": episode_id,
        "household_id": spec["household"], "receptacle_ids": receptacles,
        "object_classes": object_classes, "query_mode": query_mode,
        "budget_per_day": budget_per_day, "n_days": n_days}
    if "household_type" in spec:
        # Optional metadata consumed by the healthcheck's stratified
        # discriminative gate; absent from older schedule specs.
        header["household_type"] = str(spec["household_type"])
    header["unsensable_receptacles"] = [OUT_OF_HOUSE]
    rows: List[Dict[str, Any]] = [header]
    unobserved = 0
    for obj in objects:
        for t, receptacle in truth[obj]:
            row = {"kind": "truth", "episode_id": episode_id,
                   "object_id": obj, "t": t, "receptacle_id": receptacle}
            if causes.get((obj, t)):
                row["cause"] = causes[(obj, t)]   # provenance; loader ignores
            rows.append(row)
        if initial_tour and truth[obj][0][1] != OUT_OF_HOUSE:
            rows.append({"kind": "observation", "episode_id": episode_id,
                         "object_id": obj, "receptacle_id": truth[obj][0][1],
                         "t": 0, "source": "initial_tour"})
    for day in range(n_days):
        for _ in range(sightings_per_day):
            obj = rng_sightings.choice(objects)
            t = day * DAY_SECONDS + rng_sightings.randrange(*AWAKE_WINDOW_S)
            where = truth_at(truth[obj], t)
            if where == OUT_OF_HOUSE:
                unobserved += 1      # you cannot sight what is not there
                continue
            rows.append({"kind": "observation", "episode_id": episode_id,
                         "object_id": obj, "t": t, "source": "scripted",
                         "receptacle_id": where})
    if unobserved:
        logger.info("dropped %d sightings of out-of-house objects "
                    "(unobservable)", unobserved)
    question_number = 0
    recent: List[str] = []
    for day in range(first_question_day, n_days):
        pool: List[str] = []          # uniform mode: fresh no-repeat pool daily
        for _ in range(questions_per_day):
            obj, t = _draw_question(query_mode, day, objects, truth, recent,
                                    rng_questions, pool)
            recent.append(obj)
            rows.append({"kind": "question", "episode_id": episode_id,
                         "question_id": f"q{question_number:04d}",
                         "object_id": obj, "t_query": t, "day_index": day})
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
    parser.add_argument("--no-initial-tour", action="store_true",
                        help="omit the t=0 full snapshot; agents start blind")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    export(args.timeline, args.spec, args.out, args.seed,
           args.sightings_per_day, args.questions_per_day,
           args.first_question_day, args.budget_per_day, args.query_mode,
           initial_tour=not args.no_initial_tour)


if __name__ == "__main__":
    main()
