"""Unsensable receptacles: legal answers Sense may never target.

The core property: with OUT_OF_HOUSE unsensable, "it's out" can only be
inferred. Unlimited-budget SequentialSearch sweeps every sensable
receptacle, misses everywhere, the exclusion redistribution concentrates
all mass on the unsensable remainder, and the exhaustion branch answers
it — so the solvability invariant survives with a single unsensable
receptacle, while real budgets must pay the full sweep (or guess).
"""

from __future__ import annotations

import json
import pathlib

import pytest

from baselines.bank import JsonlBank
from baselines.cli import build_agent
from baselines.harness import run_episode
from baselines.types import Sense

OUT = "OUT_OF_HOUSE"
BELIEFS = ("last_observation", "most_frequent", "timetable")


def _elimination_bank(path: pathlib.Path) -> JsonlBank:
    """Keys silently leave the house before the query day; a decoy stays
    at the keys' favored receptacle so the first sense is a non-empty miss."""
    rows = [
        {"kind": "episode_header", "episode_id": "ep", "household_id": "hh",
         "receptacle_ids": ["a", "b", "c", OUT],
         "unsensable_receptacles": [OUT],
         "object_classes": {"keys": "keys", "decoy": "coin"},
         "budget_per_day": 8, "n_days": 2},
        {"kind": "truth", "episode_id": "ep", "object_id": "decoy",
         "t": 0, "receptacle_id": "a"},
        {"kind": "truth", "episode_id": "ep", "object_id": "keys",
         "t": 0, "receptacle_id": "a"},
        {"kind": "truth", "episode_id": "ep", "object_id": "keys",
         "t": 30 * 3600, "receptacle_id": OUT},
        {"kind": "observation", "episode_id": "ep", "object_id": "keys",
         "t": 0, "receptacle_id": "a", "source": "initial_tour"},
        {"kind": "observation", "episode_id": "ep", "object_id": "decoy",
         "t": 0, "receptacle_id": "a", "source": "initial_tour"},
        {"kind": "question", "episode_id": "ep", "question_id": "q_keys",
         "object_id": "keys", "t_query": 36 * 3600, "day_index": 1},
        {"kind": "question", "episode_id": "ep", "question_id": "q_decoy",
         "object_id": "decoy", "t_query": 37 * 3600, "day_index": 1},
    ]
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return JsonlBank(path=path)


def test_context_exposes_sensable_set(tmp_path: pathlib.Path) -> None:
    episode = next(_elimination_bank(tmp_path / "b.jsonl").episodes())
    assert episode.unsensable_receptacle_ids == (OUT,)
    view = episode.agent_view()
    assert view.sensable_receptacle_ids == ("a", "b", "c")


@pytest.mark.parametrize("belief", BELIEFS)
def test_out_of_house_is_answered_by_elimination(
        belief: str, tmp_path: pathlib.Path) -> None:
    episode = next(_elimination_bank(tmp_path / "b.jsonl").episodes())
    agent = build_agent({"name": belief}, {"name": "sequential_search"},
                        seed=0, episode_id=episode.episode_id)
    records = {r.question_id: r for r in run_episode(agent, episode)}
    keys = records["q_keys"]
    # The full sensable sweep (3 receptacles), never a sense of OUT, then
    # the exclusion-updated belief holds all mass on OUT and answers it.
    assert keys.answer_receptacle == OUT and keys.correct
    assert keys.budget_spent == 3
    sensed = [a["receptacle_id"] for a in keys.actions if a["type"] == "sense"]
    assert OUT not in sensed and sorted(sensed) == ["a", "b", "c"]
    assert records["q_decoy"].correct
    assert records["q_decoy"].budget_spent == 1


def test_harness_raises_on_unsensable_sense(tmp_path: pathlib.Path) -> None:
    from baselines.agent import Agent
    from baselines.beliefs import LastObservation
    from baselines.policies.base import DecisionPolicy
    from baselines.types import Action, Prediction, Question
    import random

    class _OutSensor(DecisionPolicy):
        def decide(self, question: Question, prediction: Prediction,
                   budget_remaining: int, t: int,
                   last_sense: object = None) -> Action:
            return Sense(receptacle_id=OUT)

    episode = next(_elimination_bank(tmp_path / "b.jsonl").episodes())
    agent = Agent(belief=LastObservation(random.Random(0)),
                  policy=_OutSensor())
    with pytest.raises(ValueError, match="unsensable"):
        list(run_episode(agent, episode))


def test_exporter_projects_person_away_and_drops_absent_sightings(
        tmp_path: pathlib.Path) -> None:
    from baselines.export_bank import export

    timeline = tmp_path / "timeline"
    timeline.mkdir()
    (timeline / "hourly.csv").write_text(
        "t,stamp,obj_a,obj_p\n" + "\n".join(
            f"{h * 60},d{h // 24:02d} Mon {h % 24:02d}:00,rec_1,person:r1"
            for h in range(4 * 24)) + "\n")
    (timeline / "events.jsonl").write_text("")
    # r1 is away (ELSEWHERE) 10:00-19:00 every day.
    (timeline / "residents.jsonl").write_text("\n".join(
        json.dumps({"resident": "r1", "activity": "shift",
                    "t0": d * 1440 + 600, "t1": d * 1440 + 1140,
                    "at": "ELSEWHERE"}) for d in range(4)) + "\n")
    spec = tmp_path / "spec.yaml"
    spec.write_text(
        "household: hh_test\n"
        "source_profile: profile.yaml\n"
        "receptacles:\n  - {id: rec_1, room: a}\n  - {id: rec_2, room: b}\n")
    (tmp_path / "profile.yaml").write_text(
        "object_inventory:\n"
        "  - {id: obj_a, class: mug}\n  - {id: obj_p, class: phone}\n")

    bank = export(timeline, spec, tmp_path / "bank.jsonl", seed=1,
                  sightings_per_day=8, questions_per_day=10,
                  first_question_day=1, budget_per_day=2,
                  query_mode="uniform")
    episode = next(bank.episodes())
    assert episode.unsensable_receptacle_ids == (OUT,)
    # The carried phone is OUT while r1 is away, ON_PERSON otherwise.
    assert episode.true_location("obj_p", 9 * 3600) == "ON_PERSON"
    assert episode.true_location("obj_p", 12 * 3600) == OUT
    assert episode.true_location("obj_p", 20 * 3600) == "ON_PERSON"
    # No observation ever reports an out-of-house object.
    for obs in episode.initial_observations + episode.scripted_observations:
        assert obs.receptacle_id != OUT
