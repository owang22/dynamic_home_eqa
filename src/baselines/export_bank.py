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
* ``person:<anyone>``  -> pseudo-receptacle ``ON_PERSON``

Both pseudo-receptacles join ``receptacle_ids``, so agents may predict and
sense them like any other ("is it on somebody / out of the house" are
legitimate answers and legitimate looks).

Generated stream and questions (all seeded):

* initial tour: every object's location at t=0.
* scripted sightings: ``--sightings-per-day`` per day, each a uniformly
  chosen object seen at a uniform time inside the awake window
  (08:00-22:00) at its true location — drive-by observations.
* questions: ``--questions-per-day`` per day from ``--first-question-day``
  on, uniform object and awake-window time.

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
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

OUT_OF_HOUSE = "OUT_OF_HOUSE"
ON_PERSON = "ON_PERSON"
AWAKE_WINDOW_S = (8 * 3600, 22 * 3600)


def project(location: str) -> str:
    """Timeline location -> bank receptacle (see module docstring)."""
    if location == "ELSEWHERE":
        return OUT_OF_HOUSE
    if location.startswith("person:"):
        return ON_PERSON
    return location


def load_truth(timeline: pathlib.Path
               ) -> Tuple[Dict[str, List[Tuple[int, str]]], int]:
    """(object -> projected change-points in seconds, n_days) from a timeline.

    Initial positions come from the first hourly row; movements from
    events.jsonl. Consecutive change-points that project to the same
    receptacle are merged.
    """
    with open(timeline / "hourly.csv") as f:
        rows = list(csv.DictReader(f))
    objects = [k for k in rows[0] if k not in ("t", "stamp")]
    n_days = (int(rows[-1]["t"]) // (24 * 60)) + 1

    truth: Dict[str, List[Tuple[int, str]]] = {
        obj: [(0, project(rows[0][obj]))] for obj in objects}
    with open(timeline / "events.jsonl") as f:
        for line in f:
            e = json.loads(line)
            dest = project(e["to"])
            traj = truth[e["object"]]
            if dest != traj[-1][1]:
                traj.append((e["t"] * 60, dest))
    return truth, n_days


def truth_at(traj: List[Tuple[int, str]], t: int) -> str:
    """Location at time t for a sorted change-point list."""
    location = traj[0][1]
    for change_t, receptacle in traj:
        if change_t > t:
            break
        location = receptacle
    return location


def export(timeline: pathlib.Path, spec_path: pathlib.Path, out: pathlib.Path,
           seed: int, sightings_per_day: int, questions_per_day: int,
           first_question_day: int, budget_per_day: int) -> JsonlBank:
    """Write the bank JSONL and return its loader (which re-validates it)."""
    spec = yaml.safe_load(spec_path.read_text())
    profile = yaml.safe_load(
        (spec_path.parent / spec["source_profile"]).resolve().read_text())
    object_classes = {o["id"]: o["class"] for o in profile["object_inventory"]}
    receptacles = [r["id"] for r in spec["receptacles"]] + [ON_PERSON, OUT_OF_HOUSE]

    truth, n_days = load_truth(timeline)
    episode_id = f"{spec['household']}_{timeline.name}"
    rng = random.Random(seed)
    objects = sorted(object_classes)

    rows: List[Dict[str, Any]] = [{
        "kind": "episode_header", "episode_id": episode_id,
        "household_id": spec["household"], "receptacle_ids": receptacles,
        "object_classes": object_classes,
        "budget_per_day": budget_per_day, "n_days": n_days}]
    for obj in objects:
        for t, receptacle in truth[obj]:
            rows.append({"kind": "truth", "episode_id": episode_id,
                         "object_id": obj, "t": t, "receptacle_id": receptacle})
        rows.append({"kind": "observation", "episode_id": episode_id,
                     "object_id": obj, "receptacle_id": truth[obj][0][1],
                     "t": 0, "source": "initial_tour"})
    for day in range(n_days):
        for _ in range(sightings_per_day):
            obj = rng.choice(objects)
            t = day * DAY_SECONDS + rng.randrange(*AWAKE_WINDOW_S)
            rows.append({"kind": "observation", "episode_id": episode_id,
                         "object_id": obj, "t": t, "source": "scripted",
                         "receptacle_id": truth_at(truth[obj], t)})
    question_number = 0
    for day in range(first_question_day, n_days):
        for _ in range(questions_per_day):
            obj = rng.choice(objects)
            t = day * DAY_SECONDS + rng.randrange(*AWAKE_WINDOW_S)
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
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    export(args.timeline, args.spec, args.out, args.seed,
           args.sightings_per_day, args.questions_per_day,
           args.first_question_day, args.budget_per_day)


if __name__ == "__main__":
    main()
