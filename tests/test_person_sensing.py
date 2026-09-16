"""Person sensing: ON_PERSON observable through the residents.

Resident room trajectories from residents.jsonl, presence listings on
receptacle senses, the person sense (legality, result, cost), the belief
rule (a positive sighting at ON_PERSON; one resident's empty pockets do
not clear ON_PERSON in a two-resident home), solvability on the hh_001
person-sensing bank, the older bank version left untouched, and
anonymization of resident ids. All times are seconds since episode
start.
"""

from __future__ import annotations

import json
import pathlib
import random
from typing import List, Optional

import pytest
import yaml

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.beliefs.last_observation import LastObservation
from baselines.harness import run_episode
from baselines.policies.base import DecisionPolicy
from baselines.types import (AWAY, ON_PERSON, OUT_OF_HOUSE, Action, AnswerNow,
                             Episode, EpisodeContext, Observation,
                             PersonSenseResult, Prediction, Question, Sense,
                             SensePerson, SenseResult)

H = 3600
CONFIGS = pathlib.Path("src/baselines/configs")
HH = pathlib.Path("profiles/households/generated/gpt-5.6-terra/hh_001")
needs_household = pytest.mark.skipif(
    not (HH / "timeline_seed0" / "residents.jsonl").exists(),
    reason="generated household hh_001 not present")

RECEPTACLES = ("counter_k", "desk_o", ON_PERSON, OUT_OF_HOUSE)
ROOMS = {"counter_k": "kitchen", "desk_o": "office"}
RESIDENTS = ("alice_r", "bob_r")


def _episode(person_sensing: bool = True) -> Episode:
    """Two rooms, two residents. alice_r is in the kitchen until 1 h in,
    then out; bob_r sits in the office all day. The keys move from the
    counter into alice_r's pocket at 30 min and leave with her at 1 h."""
    questions = (
        Question("q0", "keys", 2000, 0, "keys"),
        Question("q1", "keys", 4000, 0, "keys"),
        Question("q2", "mug", 5000, 0, "mug"),
    )
    return Episode(
        episode_id="ep", household_id="hh", receptacle_ids=RECEPTACLES,
        object_classes={"keys": "keys", "mug": "mug"},
        initial_observations=(), scripted_observations=(),
        questions_by_day=(questions,), budget_per_day=5,
        trajectories={"keys": ((0, "counter_k"), (1800, ON_PERSON),
                               (3600, OUT_OF_HOUSE)),
                      "mug": ((0, "desk_o"),)},
        unsensable_receptacle_ids=(ON_PERSON, OUT_OF_HOUSE),
        receptacle_rooms=ROOMS, home_base_room="kitchen",
        person_sensing=person_sensing, resident_ids=RESIDENTS,
        resident_rooms={"alice_r": ((0, "kitchen"), (3600, AWAY)),
                        "bob_r": ((0, "office"),)},
        carriers={("keys", 1800): "alice_r"})


class Scripted(DecisionPolicy):
    """Plays a fixed action list per question id, then answers."""

    def __init__(self, plan: dict) -> None:
        self._plan = {q: list(actions) for q, actions in plan.items()}

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        queue = self._plan.get(question.question_id, [])
        return queue.pop(0) if queue else AnswerNow()


def _run(episode: Episode, plan: dict):
    agent = Agent(LastObservation(random.Random(0)), Scripted(plan))
    return list(run_episode(agent, episode))


def _context(person_sensing: bool = True) -> EpisodeContext:
    return _episode(person_sensing).agent_view()


# --------------------------------------------------------------- harness

def test_presence_listing_on_a_receptacle_sense_matches_truth() -> None:
    episode = _episode()
    records = _run(episode, {"q0": [Sense("counter_k"), Sense("desk_o")],
                             "q1": [Sense("counter_k")]})
    q0, q1 = records[0].actions[:2], records[1].actions[:1]
    assert q0[0]["residents_present"] == ["alice_r"]     # kitchen at 2000
    assert q0[1]["residents_present"] == ["bob_r"]       # office at 2000
    assert q1[0]["residents_present"] == []              # alice_r out at 4000
    assert episode.residents_in_room("kitchen", 2000) == ("alice_r",)
    assert episode.residents_in_room("kitchen", 4000) == ()


def test_person_sense_without_a_listing_this_question_raises() -> None:
    with pytest.raises(ValueError, match="before any sense of this question"):
        _run(_episode(), {"q0": [SensePerson("alice_r")]})
    # a listing from ANOTHER question does not carry over
    with pytest.raises(ValueError, match="before any sense of this question"):
        _run(_episode(), {"q0": [Sense("counter_k")],
                          "q1": [SensePerson("alice_r")]})
    # and a bank without person sensing accepts no person sense at all
    with pytest.raises(ValueError, match="person_sensing"):
        _run(_episode(person_sensing=False),
             {"q0": [Sense("counter_k"), SensePerson("alice_r")]})


def test_person_sense_returns_the_carried_objects_and_costs_one() -> None:
    episode = _episode()
    records = _run(episode, {"q0": [Sense("desk_o"), Sense("counter_k"),
                                    SensePerson("alice_r")]})
    record = records[0]
    person = record.actions[2]
    assert person == {"type": "sense_person", "resident_id": "alice_r",
                      "room": "kitchen", "contents": ["keys"], "cost": 1.0}
    assert tuple(person["contents"]) == episode.carried_objects("alice_r", 2000)
    assert episode.carried_by("keys", 2000) == "alice_r"
    assert episode.carried_by("keys", 100) is None
    assert record.budget_spent == 3.0 and record.n_senses == 3
    # found on a resident at query time: the answer is ON_PERSON
    assert record.answer_receptacle == ON_PERSON and record.correct
    # the robot stays where it was: the next receptacle sense from the
    # kitchen prices as same-room
    records = _run(episode, {"q2": [Sense("desk_o"), SensePerson("bob_r"),
                                    Sense("counter_k")]})
    assert records[2].actions[1]["contents"] == []      # bob_r carries nothing
    assert records[2].actions[2]["same_room"] is False  # still in the office


# --------------------------------------------------------------- beliefs

def test_belief_records_a_person_sighting_at_on_person() -> None:
    belief = LastObservation(random.Random(0))
    belief.reset(_context())
    belief.ensure_object("keys", "keys")
    belief.update(SenseResult("counter_k", 2000, (), residents_present=("alice_r",)))
    belief.update(PersonSenseResult(receptacle_id=ON_PERSON, t=2000,
                                    contents=("keys",), resident_id="alice_r",
                                    room="kitchen"))
    assert belief.predict("keys", 2000).argmax == ON_PERSON
    assert belief.person_sightings() == {(2000, "keys"): ("alice_r", "kitchen")}
    assert belief.presence_listings() == {2000: {"counter_k": ("alice_r",)}}


def test_one_resident_cleared_does_not_suppress_on_person_with_two() -> None:
    belief = LastObservation(random.Random(0))
    belief.reset(_context())
    belief.update(Observation("keys", "keys", "counter_k", 0, "scripted"))
    t = 2000
    belief.update(SenseResult("counter_k", t, ()))
    belief.update(PersonSenseResult(receptacle_id=ON_PERSON, t=t,
                                    contents=(), resident_id="alice_r"))
    assert ON_PERSON not in belief.negative_factors("keys", t)
    assert belief.on_person_cleared_at("keys", t) is None
    # bob_r cleared at the same instant: now ON_PERSON is an empty look
    belief.update(PersonSenseResult(receptacle_id=ON_PERSON, t=t,
                                    contents=(), resident_id="bob_r"))
    assert belief.negative_factors("keys", t)[ON_PERSON] == 0.0
    assert belief.on_person_cleared_at("keys", t) == t
    # every sensable receptacle and ON_PERSON empty: OUT_OF_HOUSE remains
    belief.update(SenseResult("desk_o", t, ()))
    assert belief.predict("keys", t).argmax == OUT_OF_HOUSE


def test_a_full_sweep_listing_nobody_clears_an_absent_resident() -> None:
    belief = LastObservation(random.Random(0))
    belief.reset(_context())
    belief.update(Observation("keys", "keys", "counter_k", 0, "scripted"))
    t = 4000                                   # alice_r is out
    belief.update(SenseResult("counter_k", t, (), residents_present=()))
    belief.update(SenseResult("desk_o", t, (), residents_present=("bob_r",)))
    assert belief.residents_home_at(t) == ("bob_r",)
    assert belief.on_person_cleared_at("keys", t) is None
    belief.update(PersonSenseResult(receptacle_id=ON_PERSON, t=t,
                                    contents=(), resident_id="bob_r"))
    assert belief.on_person_cleared_at("keys", t) == t
    assert belief.predict("keys", t).argmax == OUT_OF_HOUSE


# ------------------------------------------------------- real household

def _source():
    from baselines.fleet import discover_households
    return next(s for s in discover_households((HH.parents[1],))
                if s.slug == str(HH))


def _hh_001(config: str, tmp_path: pathlib.Path) -> Episode:
    from baselines.fleet import export_one, load_fleet_config
    cfg, _ = load_fleet_config(CONFIGS / config)
    bank_path = tmp_path / f"{config}_bank.jsonl"
    export_one(_source(), cfg, bank_path)
    return next(JsonlBank(path=bank_path).episodes())


@needs_household
def test_resident_room_trajectory_matches_residents_jsonl(
        tmp_path: pathlib.Path) -> None:
    episode = _hh_001("cold_start.yaml", tmp_path)
    assert episode.person_sensing and episode.resident_ids == ("resident_1",)
    spec = yaml.safe_load(_source().spec.read_text())
    room_of = {str(r["id"]): str(r["room"]) for r in spec["receptacles"]}
    with open(HH / "timeline_seed0" / "residents.jsonl") as f:
        blocks = sorted((int(b["t0"]) * 60, int(b["t1"]) * 60, str(b["at"]))
                        for b in map(json.loads, f))
    away = 0
    for t0, t1, at in blocks:
        expect = None if at == "ELSEWHERE" else room_of[at]
        away += expect is None
        for t in (t0, (t0 + t1) // 2, t1 - 1):
            assert episode.resident_room("resident_1", t) == expect, (t, at)
    assert away > 0
    # before the first block: the room of that first block
    first_t0, _, first_at = blocks[0]
    assert first_t0 > 0
    assert episode.resident_room("resident_1", 0) == room_of[first_at]
    assert episode.resident_room("resident_1", first_t0 - 1) == room_of[first_at]
    # every ON_PERSON change-point has its carrier at home
    for obj, traj in episode.trajectories.items():
        for t, rec in traj:
            if rec == ON_PERSON:
                assert episode.resident_room(episode.carried_by(obj, t), t)


@needs_household
def test_solvable_is_one_on_the_hh_001_person_sensing_bank(
        tmp_path: pathlib.Path) -> None:
    from baselines.healthcheck import (BELIEF_PANEL, UNLIMITED_BUDGET,
                                       _SEARCH, run_cell)
    _hh_001("cold_start.yaml", tmp_path)
    bank = JsonlBank(path=tmp_path / "cold_start.yaml_bank.jsonl")
    for spec in BELIEF_PANEL:
        records = run_cell(bank, spec, _SEARCH, 0, budget=UNLIMITED_BUDGET)
        assert all(r.correct for r in records), spec["name"]
    person = [a for r in records for a in r.actions
              if a["type"] == "sense_person"]
    assert person and all(a["cost"] == 1.0 for a in person)


@needs_household
def test_a_bank_without_person_sensing_is_the_old_bank(
        tmp_path: pathlib.Path) -> None:
    """The fleet.yaml export carries none of the new rows or fields and
    its run records none of the new keys. (Byte identity of the export
    and of run logs against the pre-change tree was verified with git
    stash when person sensing landed; test_baselines_cold_start keeps
    the export identical to a direct export() call.)"""
    episode = _hh_001("fleet.yaml", tmp_path)
    rows = [json.loads(l) for l in open(tmp_path / "fleet.yaml_bank.jsonl")]
    assert "person_sensing" not in rows[0] and "resident_ids" not in rows[0]
    assert not [r for r in rows if r["kind"] == "resident"]
    assert not [r for r in rows if "carrier" in r]
    assert not episode.person_sensing and episode.resident_ids == ()
    for item in episode.evidence_stream()[:50]:
        if isinstance(item, SenseResult):
            assert item.residents_present == ()
    from baselines.cli import build_agent
    import dataclasses
    short = dataclasses.replace(
        episode, questions_by_day=(episode.questions_by_day[0],)
        + tuple(() for _ in episode.questions_by_day[1:]))
    agent = build_agent({"name": "last_observation"},
                        {"name": "sequential_search"}, seed=0,
                        episode_id=episode.episode_id)
    for record in run_episode(agent, short):
        for action in record.actions:
            assert action["type"] != "sense_person"
            assert "residents_present" not in action


# ---------------------------------------------------------- anonymization

def test_anonymized_prompts_contain_no_real_resident_ids() -> None:
    from baselines.llm_hypotheses.log_reader import LogReaderBrain
    from baselines.llm_hypotheses.prompt import (build_anonymization_maps,
                                                 crossref_table,
                                                 person_sensing_sections,
                                                 vocabulary_tables)
    episode = _episode()
    omap, rmap, cmap = build_anonymization_maps(episode)
    assert rmap["alice_r"] == "person_1" and rmap["bob_r"] == "person_2"
    tables = vocabulary_tables(episode, omap, rmap, cmap)
    report = {"person_sensing": True,
              "person_sightings": [{"t": 2000, "object": "keys",
                                    "resident": "alice_r", "room": "kitchen"}],
              "person_looks": [{"t": 2000, "resident": "alice_r",
                                "room": "kitchen", "contents": ["keys"]}],
              "presence": [{"t": 2000, "room": "kitchen",
                            "residents": ["alice_r"]}]}
    sections = person_sensing_sections(report, omap, rmap)
    brain = LogReaderBrain(client=None, omap=omap, rmap=rmap, cmap=cmap)
    brain.reset(episode.agent_view())
    brain.observe(SenseResult("counter_k", 2000, (), residents_present=("alice_r",)))
    brain.observe(PersonSenseResult(receptacle_id=ON_PERSON, t=2000,
                                    contents=("keys",), resident_id="alice_r",
                                    room="kitchen"))
    prefix = brain._stable_prefix() + "\n".join(brain.log)
    for text in (tables, sections, prefix):
        assert "alice_r" not in text and "bob_r" not in text
        assert "person_1" in text
    assert "look person_1 in kitchen: object_1" in "\n".join(brain.log)
    assert "residents here: person_1" in "\n".join(brain.log)
    assert "| person_1 | alice_r |" in crossref_table(episode, omap, rmap, cmap)
    token = rmap[ON_PERSON]
    assert f"PERSON SIGHTINGS (time, object, {token}, resident, room)" in sections
    assert f"object_1 {token} person_1 kitchen" in sections
