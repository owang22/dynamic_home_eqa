"""The notebook mixture, offline: a stub client stands in for the served
model. Look scoring by hand (receptacle look, person sense, the absent
term, the p_min floor), question-forecast renormalization, the fork
weight split, the population cap, the end-of-day review rule, every
branch of the look rule, the notebook's edit rules and size caps,
prompt hygiene, and a full stub run over two days of the cold-start
bank that writes every output file."""

from __future__ import annotations

import dataclasses
import json
import math
import pathlib
import random
from typing import Dict, List, Optional

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.harness import run_episode
from baselines.llm_hypotheses import notebook_mixture as nm
from baselines.llm_hypotheses.notebook_mixture import (
    BELIEFS_MAX_WORDS, P_MIN, POPULATION_CAP, SCRATCH_MAX_WORDS,
    BeliefsEditRejected, BeliefsTooLong, Notebook, NotebookMixtureBelief,
    NotebookMixtureBrain, NotebookMixturePolicy, Population, ScratchTooLong,
    look_score, normalize_question_forecast)
from baselines.types import (AWAY, DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE,
                             Episode, EpisodeContext, PersonSenseResult,
                             Question, RobotPosition, Sense, SensePerson,
                             SenseResult)

H = 3600
COLD_START_BANK = pathlib.Path(
    "banks/baselines/cold_start/"
    "households__generated__gpt-5.6-terra__hh_001_bank.jsonl")
needs_bank = pytest.mark.skipif(not COLD_START_BANK.exists(),
                                reason="cold-start bank not exported")

RECS = ("counter_k", "table_k", "desk_o", "shelf_o", ON_PERSON, OUT_OF_HOUSE)
ROOMS = {"counter_k": "kitchen", "table_k": "kitchen", "desk_o": "office",
         "shelf_o": "office"}
RESIDENTS = ("alice", "bob")
OBJECTS = {"keys": "keys", "mug": "mug", "book": "book"}


def _context(person_sensing: bool = True) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        budget_per_day=4, n_days=2, object_classes=OBJECTS,
        unsensable_receptacle_ids=(ON_PERSON, OUT_OF_HOUSE),
        receptacle_rooms=ROOMS, home_base_room="kitchen",
        robot_position=RobotPosition(room="kitchen"),
        resident_ids=RESIDENTS, person_sensing=person_sensing)


class _Stub:
    """A client whose replies come from the notebook it is shown.

    The initial call writes documents ``anchor: <receptacle>``; a
    question forecast puts most of its mass on the notebook's anchor
    (``ON_PERSON`` anchors name a carrier and room); a look forecast
    says the queried-looking objects are there with p 0.5; a follow-up
    writes scratch and forks with probability ``fork_p``. ``script``
    overrides replies in order (dicts, dumped to JSON)."""

    def __init__(self, anchors=("counter_k", "desk_o", ON_PERSON, OUT_OF_HOUSE),
                 fork_p: float = 0.0, seed: int = 0, script=None,
                 carrier: str = "alice", carrier_room: str = "office"):
        self.anchors = list(anchors)
        self.fork_p = fork_p
        self.rng = random.Random(seed)
        self.prompts: List[str] = []
        self.schemas: List[str] = []
        self.script = list(script or [])
        self.carrier, self.carrier_room = carrier, carrier_room

    @staticmethod
    def _anchor(user: str) -> Optional[str]:
        head = user.split("## BELIEFS\n", 1)
        if len(head) < 2:
            return None
        line = head[1].split("\n", 1)[0]
        return line.split("anchor: ", 1)[1].strip() if "anchor: " in line else None

    def generate(self, system, user, seed, temperature, max_tokens,
                 reasoning_effort="medium", schema=None, keep_content=False):
        self.prompts.append(user)
        kind = ("initial" if schema is nm.INITIAL_SCHEMA
                else "question" if schema is nm.QUESTION_FORECAST_SCHEMA
                else "look" if schema is nm.LOOK_FORECAST_SCHEMA
                else "follow_up" if schema is nm.FOLLOWUP_SCHEMA
                else "fork" if schema is nm.FORK_SCHEMA else "other")
        self.schemas.append(kind)
        if self.script:
            payload = self.script.pop(0)
        elif kind == "initial":
            payload = {"documents": [
                {"guess": f"guess {i}", "beliefs": f"anchor: {a}\nEverything "
                                                   f"rests at {a}."}
                for i, a in enumerate(self.anchors)]}
        elif kind == "question":
            a = self._anchor(user) or RECS[0]
            payload = {"spots": [{"spot": a, "p": 0.7}], "why": "anchor"}
            if a == ON_PERSON:
                payload["carrier"] = self.carrier
                payload["carrier_room"] = self.carrier_room
        elif kind == "look":
            objs = [line.strip().split(" ")[0]
                    for line in user.split("OBJECTS")[1].split("\n\n")[0]
                    .split("\n")[1:] if line.strip()]
            payload = {"objects": [{"object": o, "p": 0.5} for o in objs[:2]]}
        elif kind == "follow_up":
            payload = {"scratch": "saw something"}
            if self.rng.random() < self.fork_p:
                a = self.rng.choice(self.anchors)
                payload["fork"] = {"beliefs": f"anchor: {a}\nMoved my anchor.",
                                   "why": "the look disagreed"}
        elif kind == "fork":
            a = self._anchor(user) or RECS[1]
            payload = {"beliefs": f"anchor: {a}\nReviewed.", "why": "review"}
        else:
            payload = {"scratch": "trimmed"}
        return {"payload": json.dumps(payload), "think": "", "prompt_tokens": 10,
                "completion_tokens": 5, "generation_seconds": 0.1,
                "cached": False, "finish_reason": "stop"}


# ------------------------------------------------------------ 1 scoring


def test_receptacle_look_score_by_hand():
    objects = ["keys", "mug", "book"]
    # agent A: keys 0.8 there, mug 0.3, book left out; look finds keys only
    a = look_score({"keys": 0.8, "mug": 0.3}, ("keys",), objects)
    assert a == pytest.approx(math.log(0.8) + math.log(0.7) + math.log(1 - P_MIN))
    # agent B: mug 0.9 (absent), keys left out (present -> floor)
    b = look_score({"mug": 0.9}, ("keys",), objects)
    assert b == pytest.approx(math.log(P_MIN) + math.log(0.1) + math.log(1 - P_MIN))
    assert a > b


def test_person_sense_score_and_the_floor_on_both_ends():
    objects = ["keys", "mug"]
    # alice carries the keys; p=1.0 on keys and 0.0 on mug is read inside
    # [P_MIN, 1 - P_MIN], so a confident agent scores finite
    s = look_score({"keys": 1.0, "mug": 0.0}, ("keys",), objects)
    assert s == pytest.approx(2 * math.log(1 - P_MIN))
    # a confident miss costs log P_MIN per object, never -inf
    s = look_score({"keys": 0.0, "mug": 1.0}, ("keys",), objects)
    assert s == pytest.approx(2 * math.log(P_MIN))
    # empty pockets: every object absent, an empty forecast is right
    s = look_score({}, (), objects)
    assert s == pytest.approx(2 * math.log(1 - P_MIN))


def test_weight_update_from_two_hand_scores():
    pop = Population()
    pop.add_initial([("g", "A"), ("g", "B")], 0)
    scores = {"a01": math.log(0.8) + math.log(0.7),
              "a02": math.log(P_MIN) + math.log(0.1)}
    w = pop.update_log_weights(scores, 10, "counter_k")
    la, lb = math.exp(scores["a01"]), math.exp(scores["a02"])
    assert w["a01"] == pytest.approx(la / (la + lb))
    assert w["a02"] == pytest.approx(lb / (la + lb))
    assert sum(w.values()) == pytest.approx(1.0)


def test_question_forecast_renormalizes_with_omitted_spots():
    dist = normalize_question_forecast({"counter_k": 0.7, "desk_o": 0.2}, RECS)
    z = 0.7 + 0.2 + 4 * P_MIN
    assert dist["counter_k"] == pytest.approx(0.7 / z)
    assert dist["desk_o"] == pytest.approx(0.2 / z)
    for s in ("table_k", "shelf_o", ON_PERSON, OUT_OF_HOUSE):
        assert dist[s] == pytest.approx(P_MIN / z)
    assert sum(dist.values()) == pytest.approx(1.0)
    # an empty forecast is uniform
    empty = normalize_question_forecast({}, RECS)
    assert all(p == pytest.approx(1 / len(RECS)) for p in empty.values())


# --------------------------------------------------------- 2 population


def test_fork_splits_the_parent_weight_in_half_only():
    pop = Population()
    pop.add_initial([("g", "A"), ("g", "B"), ("g", "C")], 0)
    pop.update_log_weights({"a01": math.log(2), "a02": 0.0, "a03": 0.0}, 1, "x")
    before = pop.weights
    child, retired = pop.fork("a01", "A'", "changed", 2)
    after = pop.weights
    assert retired is None and child.parent_id == "a01"
    assert after["a01"] == pytest.approx(before["a01"] / 2)
    assert after[child.agent_id] == pytest.approx(before["a01"] / 2)
    assert after["a02"] == pytest.approx(before["a02"])
    assert after["a03"] == pytest.approx(before["a03"])
    assert sum(after.values()) == pytest.approx(1.0)
    assert child.notebook.scratch == pop.agents["a01"].notebook.scratch


def test_cap_retires_the_lowest_weight_agent_other_than_the_fork():
    pop = Population(cap=POPULATION_CAP)
    pop.add_initial([("g", f"doc {i}") for i in range(POPULATION_CAP)], 0)
    # make a03 the lightest by far, then fork a03 itself: its child is
    # lighter still but is spared, so a03 goes
    pop.update_log_weights({f"a{i:02d}": (-5.0 if i == 3 else 0.0)
                            for i in range(1, POPULATION_CAP + 1)}, 1, "x")
    child, retired = pop.fork("a03", "new", "why", 2)
    assert pop.size == POPULATION_CAP
    assert retired is not None and retired.agent_id == "a03"
    assert child.agent_id in pop.agents and "a03" in pop.retired
    assert sum(pop.weights.values()) == pytest.approx(1.0)
    assert pop.retired["a03"].retired_reason == "population cap"


def test_end_of_day_review_fires_only_below_equal_share():
    pop = Population()
    pop.add_initial([("g", "A"), ("g", "B"), ("g", "C")], 0)
    assert pop.review_candidate() is None          # all exactly 1/N
    pop.update_log_weights({"a01": 0.0, "a02": 0.0, "a03": -0.01}, 1, "x")
    assert pop.review_candidate() == "a03"
    pop.update_log_weights({"a01": -0.5, "a02": 0.0, "a03": 0.51}, 2, "x")
    assert pop.review_candidate() == "a01"


# ---------------------------------------------------------- 3 look rule


def _brain(stub, tmp_path=None, **kw) -> NotebookMixtureBrain:
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path, **kw)
    brain.reset(_context())
    return brain


def _forecast(top: str, carrier=None, carrier_room=None, dist=None) -> Dict:
    d = dist or normalize_question_forecast({top: 0.9}, RECS)
    return {"dist": d, "top": top, "carrier": carrier,
            "carrier_room": carrier_room}


def test_look_rule_receptacle_branch():
    brain = _brain(_Stub())
    brain._question_key = ("keys", 100)
    assert brain.choose_look(_forecast("counter_k")) == {
        "receptacle": "counter_k", "room": "kitchen"}
    brain._sensed_this_question = ["counter_k"]
    assert brain.choose_look(_forecast("counter_k")) is None


def test_look_rule_located_carrier_is_a_person_sense():
    brain = _brain(_Stub())
    brain._question_key = ("keys", 100)
    brain._listed_this_question = {"alice": "office"}
    assert brain.choose_look(_forecast(ON_PERSON, "alice", "kitchen")) == {
        "resident": "alice", "room": "office"}
    # an already-looked-at resident gives nothing
    brain._sensed_this_question = ["alice"]
    assert brain.choose_look(_forecast(ON_PERSON, "alice", "nowhere")) is None


def test_look_rule_unlocated_carrier_looks_in_its_room_never_at_the_person():
    brain = _brain(_Stub())
    brain._question_key = ("keys", 100)
    dist = normalize_question_forecast(
        {ON_PERSON: 0.6, "shelf_o": 0.3, "desk_o": 0.1}, RECS)
    look = brain.choose_look(_forecast(ON_PERSON, "alice", "office", dist))
    assert look == {"receptacle": "shelf_o", "room": "office"}
    # every receptacle in that room already looked at -> nothing
    brain._sensed_this_question = ["shelf_o", "desk_o"]
    assert brain.choose_look(_forecast(ON_PERSON, "alice", "office", dist)) is None
    # an unknown room -> nothing
    assert brain.choose_look(_forecast(ON_PERSON, "alice", "garage")) is None


def test_look_rule_out_of_house_falls_through_to_the_second_agent():
    stub = _Stub(anchors=(OUT_OF_HOUSE, "desk_o"))
    brain = _brain(stub)
    # weights equal; force the draw order (first agent OUT_OF_HOUSE)
    brain._rng = random.Random(0)
    brain._rng.choices = lambda ids, weights, k: ["a01", "a02"]
    decision = brain.decide("keys", 100)
    assert decision["action"] == "sense" and decision["receptacle"] == "desk_o"
    assert decision["look_by"] == "a02"
    # both away: nothing legal, answer
    stub2 = _Stub(anchors=(OUT_OF_HOUSE, OUT_OF_HOUSE))
    brain2 = _brain(stub2)
    assert brain2.decide("keys", 100)["action"] == "answer"


def test_agreement_and_zero_budget_answer():
    stub = _Stub(anchors=("counter_k", "counter_k"))
    brain = _brain(stub)
    d = brain.decide("keys", 100)
    assert d["action"] == "answer" and d["reason"] == "agreement"
    stub = _Stub(anchors=("counter_k", "desk_o"))
    brain = _brain(stub)
    brain._new_day(100)
    brain.spent_today = 4.0
    d = brain.decide("keys", 100)
    assert d["action"] == "answer" and d["reason"] == "no budget"


def _episode(person_sensing: bool = True, budget: int = 4) -> Episode:
    questions = tuple(Question(f"q{i}", "keys", 1000 + i * 1000, 0, "keys")
                      for i in range(3))
    return Episode(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes=OBJECTS, initial_observations=(),
        scripted_observations=(), questions_by_day=(questions,),
        budget_per_day=budget,
        trajectories={"keys": ((0, "table_k"),), "mug": ((0, "desk_o"),),
                      "book": ((0, ON_PERSON),)},
        unsensable_receptacle_ids=(ON_PERSON, OUT_OF_HOUSE),
        receptacle_rooms=ROOMS, home_base_room="kitchen",
        person_sensing=person_sensing, resident_ids=RESIDENTS,
        resident_rooms={"alice": ((0, "office"),), "bob": ((0, AWAY),)},
        carriers={("book", 0): "alice"})


def test_repeated_disagreement_keeps_looking_until_agreement_or_budget(tmp_path):
    # Two agents that always disagree (anchors on different receptacles
    # that never hold the keys): the first question looks until the
    # day's budget is gone, then answers; later questions answer at once.
    stub = _Stub(anchors=("counter_k", "desk_o", "shelf_o"))
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path)
    # a random draw can pick the same agent twice (agreement); rotate
    # the pairs so every round is a disagreement between fresh anchors
    rounds = iter(range(10 ** 6))
    brain._rng.choices = lambda ids, weights, k: (
        lambda i: [ids[i % len(ids)], ids[(i + 1) % len(ids)]])(next(rounds))
    belief = NotebookMixtureBelief(random.Random(0), brain)
    episode = _episode(budget=3)
    records = list(run_episode(Agent(belief, NotebookMixturePolicy(brain)),
                               episode))
    assert records[0].n_senses == 3 and records[0].budget_after == 0
    assert all(r.n_senses == 0 for r in records[1:])
    assert brain.budget_exhausted_at[0] is not None
    # a person sense was never attempted: nobody was listed by a look at
    # alice's office... unless the office was looked at; either way the
    # harness would have raised on an unlisted resident
    for a in records[0].actions:
        if a["type"] == "sense_person":
            assert a["resident_id"] == "alice"


def test_person_sense_only_after_a_listing(tmp_path):
    # Agent 1 believes ON_PERSON (carrier alice, in the office); agent 2
    # believes counter_k. Draw order forced: agent 1 first. Its first
    # look must be a receptacle in the office (alice unlocated), which
    # lists alice; the next round may then look at alice herself.
    stub = _Stub(anchors=(ON_PERSON, "counter_k"))
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path)
    brain._rng.choices = lambda ids, weights, k: ["a01", "a02"]
    belief = NotebookMixtureBelief(random.Random(0), brain)
    episode = _episode(budget=4)
    records = list(run_episode(Agent(belief, NotebookMixturePolicy(brain)),
                               episode))
    kinds = [(a["type"], a.get("receptacle_id") or a.get("resident_id"))
             for a in records[0].actions]
    assert kinds[0][0] == "sense" and ROOMS[kinds[0][1]] == "office"
    person = [k for k in kinds if k[0] == "sense_person"]
    assert person and person[0][1] == "alice"
    assert kinds.index(person[0]) > 0


# ---------------------------------------------------------- 4 notebook


def test_beliefs_edit_is_rejected_and_scratch_edit_accepted():
    nb = Notebook("rest: keys at counter", "")
    with pytest.raises(BeliefsEditRejected):
        nb.beliefs = "rest: keys at desk"
    nb.scratch = "saw the keys at the counter at 9"
    assert nb.scratch.startswith("saw the keys")
    assert nb.beliefs == "rest: keys at counter"


def test_size_caps_enforce_trim_or_fork(tmp_path):
    nb = Notebook("x", "")
    with pytest.raises(ScratchTooLong):
        nb.scratch = " ".join(["w"] * (SCRATCH_MAX_WORDS + 1))
    nb.scratch = " ".join(["w"] * SCRATCH_MAX_WORDS)
    with pytest.raises(BeliefsTooLong):
        Notebook(" ".join(["w"] * (BELIEFS_MAX_WORDS + 1)))
    pop = Population()
    pop.add_initial([("g", "A")], 0)
    with pytest.raises(BeliefsTooLong):
        pop.fork("a01", " ".join(["w"] * (BELIEFS_MAX_WORDS + 1)), "why", 1)
    assert pop.size == 1 and pop.weights["a01"] == pytest.approx(1.0)
    # The brain: an over-cap scratch gets one trim retry, then is cut at
    # the cap; an over-cap fork gets one condensed-rewrite retry, then
    # is rejected.
    long_scratch = " ".join(["s"] * (SCRATCH_MAX_WORDS + 5))
    long_beliefs = " ".join(["b"] * (BELIEFS_MAX_WORDS + 5))
    stub = _Stub(anchors=("counter_k", "desk_o"), script=[
        None,                                     # initial (default)
        {"scratch": long_scratch,
         "fork": {"beliefs": long_beliefs, "why": "big"}},   # follow-up
        {"scratch": long_scratch},                # trim retry, still long
        {"beliefs": long_beliefs, "why": "big"},  # condensed retry, still long
    ])
    stub.script[0] = {"documents": [
        {"guess": str(i), "beliefs": f"anchor: {a}"}
        for i, a in enumerate(("counter_k", "desk_o", "shelf_o", "table_k"))]}
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path)
    brain.reset(_context())
    brain._ensure_started(0)
    look = {"receptacle": "counter_k", "room": "kitchen", "t": 0,
            "forecasts": {a: {} for a in brain.population.agents},
            "weights_before": brain.population.weights}
    brain._question_key = ("keys", 0)
    # only a01 gets the scripted follow-up; a02's uses the default reply
    brain._follow_up("a01", look, "look at counter_k: (nothing)", {}, -0.1, 0)
    a01 = brain.population.agents["a01"]
    assert len(a01.notebook.scratch.split()) == SCRATCH_MAX_WORDS
    assert brain.scratch_truncated == 1
    assert brain.forks_rejected == 1 and brain.population.size == 4


# ----------------------------------------------------- 5 prompt hygiene


def test_prompts_are_positively_phrased(tmp_path):
    from baselines.llm_hypotheses.prompt import AWAY_SENTENCES
    stub = _Stub(anchors=("counter_k", ON_PERSON), fork_p=1.0)
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path)
    brain._rng.choices = lambda ids, weights, k: ids[:2]   # always disagree
    belief = NotebookMixtureBelief(random.Random(0), brain)
    list(run_episode(Agent(belief, NotebookMixturePolicy(brain)), _episode()))
    brain.finish()
    kinds = set(stub.schemas)
    assert {"initial", "question", "look", "follow_up"} <= kinds
    mandated = AWAY_SENTENCES.replace("`", "")
    for text in [nm.SYSTEM_PROMPT] + stub.prompts:
        low = text.replace(mandated, "").replace(nm.MISPLACEMENT_SENTENCE, "")
        # the agents' own notebooks are the model's words, exempt
        low = low.split("YOUR NOTEBOOK")[0].lower() + \
            "".join(part.split("\n\n", 1)[1] if "\n\n" in part else ""
                    for part in low.split("YOUR NOTEBOOK")[1:]).lower()
        for bad in ("do not", "don't", "never", "no more", "cannot",
                    "must not", "avoid"):
            assert bad not in low, (bad, text[:200])


# ------------------------------------------------------- 6 full stub run


@needs_bank
def test_full_stub_run_over_two_days_writes_every_output(tmp_path):
    episode = next(JsonlBank(path=COLD_START_BANK).episodes())
    episode = dataclasses.replace(episode,
                                  questions_by_day=episode.questions_by_day[:2])
    assert episode.n_days == 2 and episode.person_sensing
    recs = episode.agent_view().sensable_receptacle_ids
    stub = _Stub(anchors=(recs[0], recs[5], ON_PERSON, OUT_OF_HOUSE),
                 fork_p=0.15, carrier=episode.resident_ids[0],
                 carrier_room=episode.receptacle_rooms[recs[0]])
    out = tmp_path / "arm"
    brain = NotebookMixtureBrain(stub, log_dir=out)
    belief = NotebookMixtureBelief(random.Random(0), brain)
    records = list(run_episode(Agent(belief, NotebookMixturePolicy(brain)),
                               episode))
    brain.finish()
    assert len(records) == sum(len(d) for d in episode.questions_by_day)
    for r in records:
        assert abs(sum(r.distribution.values()) - 1.0) < 1e-6
        assert set(r.distribution) == set(episode.receptacle_ids)
    by_day: Dict[int, float] = {}
    for r in records:
        by_day[r.day_index] = by_day.get(r.day_index, 0.0) + r.budget_spent
    assert all(v <= episode.budget_per_day for v in by_day.values())
    assert brain.n_looks > 0
    for name in ("looks.jsonl", "forecasts.jsonl", "population.jsonl",
                 "calls.jsonl"):
        rows = [json.loads(l) for l in (out / name).read_text().splitlines()]
        assert rows, name
    looks = [json.loads(l) for l in (out / "looks.jsonl").read_text().splitlines()]
    assert len(looks) == brain.n_looks
    for row in looks:
        assert set(row["forecasts"]) == set(row["scores"])
        assert abs(sum(row["weights_after"].values()) - 1.0) < 1e-5
    events = [json.loads(l) for l in (out / "population.jsonl").read_text().splitlines()]
    kinds = {e["event"] for e in events}
    assert {"birth", "look_update", "review"} <= kinds
    assert sum(1 for e in events if e["event"] == "review") == 2
    calls = [json.loads(l) for l in (out / "calls.jsonl").read_text().splitlines()]
    assert {c["type"] for c in calls} >= {"initial", "question_forecast",
                                          "look_forecast", "follow_up"}
    assert all("prompt_tokens" in c and "seconds" in c for c in calls)
    notebooks = sorted((out / "notebooks").glob("*/v1.md"))
    assert len(notebooks) == len(brain.population.agents) + len(
        brain.population.retired) >= 4
    diag = brain.diagnostics()
    assert set(diag["call_totals"]) == set(nm.CALL_TYPES)
    assert set(diag["budget_exhausted_at"]) == {"0", "1"}
    assert set(diag["population_size_per_day"]) == {"0", "1"}
    if brain.population.n_forks:
        assert "fork" in kinds
        forked = [e for e in events if e["event"] == "fork"][0]
        text = (out / "notebooks" / forked["agent"] / "v1.md").read_text()
        assert f"parent: {forked['parent']}" in text
