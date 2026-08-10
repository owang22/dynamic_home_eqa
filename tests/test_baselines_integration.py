"""Integration: the full belief x policy grid on the synthetic fixture bank.

The fixture is constructed (see baselines.bank.write_synthetic_bank) so
that exact accuracies are derivable by hand:

* mug_static: seen once on the tour at counter_k, never moves ->
  every belief scores 3/3 on its questions.
* keys_periodic: sighted desk@10:00 x4 and entry@20:00 x4 (plus the tour
  entry@0). Questions hit 10:05 (truth desk) and 20:05 (truth entry) on
  days 4-6.
    - LastObservation: last sighting is entry@day3 20:00 -> right only at
      20:05 -> 3/6.
    - MostFrequentLocation: entry counts 5 vs desk 4 -> entry -> 3/6.
    - TimetableLookup(1h bins): 10:00 bin says desk, 20:00 bin says entry
      -> 6/6.
* laptop_mover: desk until day 3 noon, then shelf; sighted desk x2 (+tour)
  and shelf x1 after the move. Questions (days 4-6, truth shelf):
    - LastObservation: shelf -> 3/3.
    - MostFrequentLocation: desk 3 vs shelf 1 -> desk -> 0/3.
    - TimetableLookup: 12:00 bin empty -> most-frequent fallback -> 0/3.

Totals over the 12 questions: LastObservation 9/12 = 0.75,
MostFrequentLocation 6/12 = 0.50, TimetableLookup 9/12 = 0.75 — with the
required orderings (timetable beats most-frequent on the periodic object;
last-observation beats most-frequent on the mover).
"""

from __future__ import annotations

import pathlib
import random
from typing import Dict, List

import pytest

from baselines.agent import Agent
from baselines.bank import write_synthetic_bank
from baselines.beliefs import (LastObservation, MostFrequentLocation,
                               TimetableConfig, TimetableLookup)
from baselines.beliefs.base import BeliefModel
from baselines.harness import QuestionRecord, run_episode
from baselines.policies import (AlwaysSense, FixedSchedule,
                                FixedScheduleConfig, NeverSense)
from baselines.policies.base import DecisionPolicy


def _beliefs(seed: int) -> Dict[str, BeliefModel]:
    return {
        "last": LastObservation(random.Random(seed)),
        "freq": MostFrequentLocation(random.Random(seed)),
        "timetable": TimetableLookup(
            random.Random(seed), TimetableConfig(bin_hours=1, day_scheme="all")),
    }


def _policies() -> Dict[str, DecisionPolicy]:
    return {
        "never": NeverSense(),
        "always": AlwaysSense(),
        "fixed": FixedSchedule(FixedScheduleConfig(
            rotation=("counter_k", "desk_o", "entry_e", "shelf_l"),
            every_hours=6)),
    }


def _accuracy(records: List[QuestionRecord],
              object_id: str | None = None) -> float:
    rs = [r for r in records if object_id is None or r.object_id == object_id]
    return sum(r.correct for r in rs) / len(rs)


@pytest.fixture(scope="module")
def grid_records(tmp_path_factory: pytest.TempPathFactory
                 ) -> Dict[str, Dict[str, List[QuestionRecord]]]:
    bank = write_synthetic_bank(
        tmp_path_factory.mktemp("bank") / "bank.jsonl")
    episode = next(bank.episodes())
    out: Dict[str, Dict[str, List[QuestionRecord]]] = {}
    for bname in ("last", "freq", "timetable"):
        out[bname] = {}
        for pname in ("never", "always", "fixed"):
            agent = Agent(belief=_beliefs(0)[bname],
                          policy=_policies()[pname])
            out[bname][pname] = list(run_episode(agent, episode))
    return out


def test_known_overall_accuracies(
        grid_records: Dict[str, Dict[str, List[QuestionRecord]]]) -> None:
    assert _accuracy(grid_records["last"]["never"]) == pytest.approx(0.75)
    assert _accuracy(grid_records["freq"]["never"]) == pytest.approx(0.50)
    assert _accuracy(grid_records["timetable"]["never"]) == pytest.approx(0.75)


def test_static_object_is_perfect_for_every_belief(
        grid_records: Dict[str, Dict[str, List[QuestionRecord]]]) -> None:
    for bname in grid_records:
        assert _accuracy(grid_records[bname]["never"], "mug_static") == 1.0


def test_timetable_beats_most_frequent_on_the_periodic_object(
        grid_records: Dict[str, Dict[str, List[QuestionRecord]]]) -> None:
    tt = _accuracy(grid_records["timetable"]["never"], "keys_periodic")
    freq = _accuracy(grid_records["freq"]["never"], "keys_periodic")
    assert tt == pytest.approx(1.0)
    assert freq == pytest.approx(0.5)
    assert tt > freq


def test_last_observation_beats_most_frequent_on_the_mover(
        grid_records: Dict[str, Dict[str, List[QuestionRecord]]]) -> None:
    last = _accuracy(grid_records["last"]["never"], "laptop_mover")
    freq = _accuracy(grid_records["freq"]["never"], "laptop_mover")
    assert last == pytest.approx(1.0)
    assert freq == pytest.approx(0.0)


def test_always_sense_never_hurts_any_belief(
        grid_records: Dict[str, Dict[str, List[QuestionRecord]]]) -> None:
    # Sensing the predicted receptacle either confirms (object present) or
    # yields no positive evidence about the queried object; with these
    # beliefs the answer can only stay or improve. A violation means the
    # harness corrupted the information flow.
    for bname in grid_records:
        assert (_accuracy(grid_records[bname]["always"])
                >= _accuracy(grid_records[bname]["never"]))


def test_loader_round_trip_preserves_question_count(
        tmp_path: pathlib.Path) -> None:
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    episode = next(bank.episodes())
    assert sum(len(day) for day in episode.questions_by_day) == 12
    assert episode.receptacle_ids == ("counter_k", "desk_o", "entry_e", "shelf_l")
    assert episode.budget_per_day == 2
