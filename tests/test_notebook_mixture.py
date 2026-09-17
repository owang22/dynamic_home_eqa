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
import time
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
        self.decide_action, self.decide_target = "answer", ""

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
                else "fork" if schema is nm.FORK_SCHEMA
                else "decide" if schema is nm.DECIDE_SCHEMA
                else "birth" if schema is nm.BIRTH_SCHEMA else "other")
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
        elif kind == "decide":
            payload = {"action": self.decide_action, "target": self.decide_target,
                       "why": "dispatcher says so", "note": "plan: save looks"}
        elif kind == "birth":
            payload = {"guess": "fresh guess",
                       "beliefs": f"anchor: {RECS[3]}\nFresh contrasting document."}
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
    # only a01 gets the scripted follow-up
    user, may_fork = brain._follow_up_prompt("a01", "look at counter_k: (nothing)",
                                             {}, -0.1)
    parsed = brain._calls("follow_up", [("a01", user)], nm.FOLLOWUP_SCHEMA,
                          nm.FOLLOWUP_MAX_TOKENS, 0)["a01"]
    brain._apply_follow_up("a01", parsed, user, may_fork, -0.1, None, 0)
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


# ------------------------------------------------ 6 notebook_voi / llmDecide


def _voi_brain(stub, tmp_path=None, **over) -> NotebookMixtureBrain:
    cfg = dataclasses.replace(nm.NOTEBOOK_VOI, **over)
    brain = NotebookMixtureBrain(stub, log_dir=tmp_path, config=cfg)
    brain.reset(_context())
    return brain


def test_configs_are_the_documented_variants():
    assert nm.CONFIGS["notebook_mixture"] == nm.NotebookConfig()
    v = nm.CONFIGS["notebook_voi"]
    assert (v.look_rule, v.beta, v.invalid_look, v.review,
            v.use_it_or_lose_it) == ("voi", 0.3, "neutral", "top_fresh", True)
    assert (v.population_cap, v.followup_min_weight, v.max_looks_per_question) == (5, 0.05, 3)
    d = nm.CONFIGS["notebook_llmDecide"]
    assert d == dataclasses.replace(v, look_rule="llm", tell_questions_per_day=False,
                                    label="notebook_llmDecide")


def test_beta_tempers_the_weight_update():
    pop = Population()
    pop.add_initial([("g", "A"), ("g", "B")], 0)
    pop.update_log_weights({"a01": 0.0, "a02": -4.0}, 1, "x", beta=0.5)
    w = pop.weights
    assert abs(w["a01"] / w["a02"] - math.exp(2.0)) < 1e-9
    assert pop.events[-1]["beta"] == 0.5


def test_blank_look_forecast_is_scored_at_the_population_average(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k"))
    brain = _voi_brain(stub, tmp_path)
    brain.decide("keys", 100)
    # two valid forecasts and one blank, scored by hand
    look = {"receptacle": "counter_k", "room": "kitchen", "t": 100,
            "forecasts": {"a01": {"keys": 0.9}, "a02": {"keys": 0.5},
                          "a03": {}},
            "invalid": ["a03"],
            "weights_before": {"a01": 0.5, "a02": 0.25, "a03": 0.25}}
    brain._look_procedure(look, "counter_k", "kitchen", ("keys",), (), "line",
                          100)
    row = json.loads((tmp_path / "looks.jsonl").read_text().splitlines()[-1])
    s1 = nm.look_score({"keys": 0.9}, ("keys",), brain._known_objects())
    s2 = nm.look_score({"keys": 0.5}, ("keys",), brain._known_objects())
    assert abs(row["scores"]["a03"] - (0.5 * s1 + 0.25 * s2) / 0.75) < 1e-3
    assert row["neutral_scored"] and row["invalid"] == ["a03"]
    assert row["beta"] == 0.3
    # the blank agent's follow-up says so
    blank_prompt = [p for p in stub.prompts if "was blank" in p]
    assert blank_prompt and "population's average" in blank_prompt[0]


def test_voi_rule_looks_at_the_best_receptacle_and_stops_below_lambda():
    # Two agents split between two receptacles: the mixture is ~0.45 /
    # 0.45, one look is worth ~0.45, far above lambda -> look at one of them.
    stub = _Stub(anchors=("counter_k", "desk_o"))
    brain = _voi_brain(stub, use_it_or_lose_it=False)
    d = brain.decide("keys", 100)
    assert d["action"] == "sense" and d["receptacle"] in ("counter_k", "desk_o")
    assert d["reason"].startswith("voi") and d["voi"]["best"] == d["receptacle"]
    assert "draw" not in d
    # Everyone agrees at 0.9: the best look gains ~0.1 - still above 0.05;
    # raise lambda and it answers.
    stub = _Stub(anchors=("counter_k", "counter_k"))
    brain = _voi_brain(stub, use_it_or_lose_it=False, voi_lambda=0.5)
    d = brain.decide("keys", 100)
    assert d["action"] == "answer" and "below 0.5" in d["reason"]


def test_use_it_or_lose_it_spends_spare_looks():
    stub = _Stub(anchors=("counter_k", "counter_k"))
    # lambda so high the voi rule alone would never look; 4 looks left,
    # 2 questions per day and this is the first -> 1 question left -> spend.
    brain = _voi_brain(stub, voi_lambda=5.0, questions_per_day=2.0)
    d = brain.decide("keys", 100)
    assert d["action"] == "sense" and d["reason"].startswith("spare looks")
    # with more questions left than looks, no spare
    brain = _voi_brain(stub, voi_lambda=5.0, questions_per_day=30.0)
    d = brain.decide("keys", 100)
    assert d["action"] == "answer"


def test_voi_candidates_include_a_listed_resident_for_on_person():
    stub = _Stub(anchors=(ON_PERSON, ON_PERSON), carrier="alice",
                 carrier_room="office")
    brain = _voi_brain(stub, use_it_or_lose_it=False, voi_lambda=0.01)
    brain.decide("keys", 100)
    brain._listed_this_question["alice"] = "office"
    d = brain.decide("keys", 100)
    # ON_PERSON at ~0.86 for everyone: a look there gains the runner-up's
    # share (~0.03, the miss case) - the best available, above 0.01.
    assert d["action"] == "sense" and d["resident"] == "alice"
    assert d["voi"]["best"] == ON_PERSON


def test_llm_decide_reads_the_verdict_and_falls_back_on_an_illegal_target():
    stub = _Stub(anchors=("counter_k", "desk_o"))
    brain = _voi_brain(stub, look_rule="llm", use_it_or_lose_it=False,
                       tell_questions_per_day=False)
    stub.decide_action, stub.decide_target = "answer", ""
    d = brain.decide("keys", 100)
    assert d["action"] == "answer" and d["reason"].startswith("dispatcher:")
    briefing = [p for p in stub.prompts if "VALUE OF INFORMATION" in p][-1]
    for line in ("QUESTION: where is keys", "looks left 4 of 4",
                 "questions so far today 1;", "PREVIOUS DAYS: none yet",
                 "PANEL FORECAST",
                 "AGENTS' TOP SPOTS", "LEGAL LOOK TARGETS NOW",
                 "TODAY'S LEDGER", "(first decision of the day)",
                 "YOUR NOTE:\n(empty)", "At most 3 looks per question"):
        assert line in briefing, line
    assert "0.05" not in briefing and "threshold" not in briefing
    assert "about 24" not in briefing
    stub.decide_action, stub.decide_target = "look", "desk_o"
    d = brain.decide("keys", 200)
    assert d["action"] == "sense" and d["receptacle"] == "desk_o"
    assert d["dispatch"]["target"] == "desk_o"
    # the note persisted and the ledger carries the earlier decision
    briefing = [p for p in stub.prompts if "VALUE OF INFORMATION" in p][-1]
    assert "YOUR NOTE:\nplan: save looks" in briefing
    assert "keys: sure" in briefing and "-> answered" in briefing
    assert d["dispatch"]["note"] == "plan: save looks"
    stub.decide_action, stub.decide_target = "look", "no_such_place"
    d = brain.decide("keys", 300)
    assert d["action"] == "sense" and d["receptacle"] == d["voi"]["best"]
    assert d["dispatch_corrected"] == "no_such_place"
    assert brain.decide_corrected == 1
    # the next day the briefing carries yesterday's counts and a fresh ledger
    brain.decide("keys", DAY_SECONDS + 100)
    briefing = [p for p in stub.prompts if "VALUE OF INFORMATION" in p][-1]
    assert "PREVIOUS DAYS: Mon 3 questions, 0 looks used" in briefing
    assert "(first decision of the day)" in briefing


def test_top_fresh_review_skips_without_looks_and_otherwise_forks_top_births_fresh(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k"))
    # review_every_looks 0: nightly whenever there were looks; agents born
    # on day 0 are in their grace period at the day-0 review, so run the
    # review as day 1 to exercise the retirement.
    brain = _voi_brain(stub, tmp_path, review_every_looks=0)
    brain.decide("keys", 100)
    brain._end_of_day_review(0)
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    review = [e for e in events if e["event"] == "review"][-1]
    assert review["skipped"] == "no looks since the last review" and review["candidate"] is None
    assert brain.population.size == 3
    brain.day = 1
    # one look today: a01 wins it
    look = {"receptacle": "counter_k", "room": "kitchen", "t": 100,
            "forecasts": {"a01": {"keys": 0.9}, "a02": {"keys": 0.1},
                          "a03": {"keys": 0.3}},
            "invalid": [], "weights_before": brain.population.weights}
    brain._today_look_lines.append("d00 Mon 00:01 look at counter_k: keys")
    brain._look_procedure(look, "counter_k", "kitchen", ("keys",), (), "line",
                          100)
    assert brain.population.top() == "a01" and brain.population.lowest() == "a02"
    brain._end_of_day_review(1)
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    review = [e for e in events if e["event"] == "review"][-1]
    assert review["candidate"] == "a01" and review["retire"] == "a02"
    kinds = [e["event"] for e in events]
    assert "retire" in kinds
    births = [e for e in events if e["event"] == "birth" and e.get("origin") == "review"]
    assert len(births) == 1
    pop = brain.population
    fresh = births[0]["agent"]
    assert fresh in pop.agents and "a02" in pop.retired
    # fair entry: the newcomer holds exactly 1/N
    assert abs(pop.weights[fresh] - 1.0 / pop.size) < 1e-9
    assert abs(sum(pop.weights.values()) - 1.0) < 1e-9
    # the fork of the top agent exists with half of a real weight
    forks = [e for e in events if e["event"] == "fork"]
    assert forks and forks[-1]["parent"] == "a01"
    birth_prompt = [p for p in stub.prompts if "CONTRASTS" in p][-1]
    assert "LOOKS SINCE THE LAST REVIEW" in birth_prompt and "counter_k: keys" in birth_prompt


def test_scratch_versions_are_logged_at_birth_fork_and_follow_up(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o"), fork_p=1.0)
    brain = _voi_brain(stub, tmp_path, fork_gate=False)
    brain.decide("keys", 100)
    look = {"receptacle": "counter_k", "room": "kitchen", "t": 100,
            "forecasts": {"a01": {"keys": 0.9}, "a02": {"keys": 0.1}},
            "invalid": [], "weights_before": brain.population.weights}
    brain._look_procedure(look, "counter_k", "kitchen", ("keys",), (), "line",
                          100)
    rows = [json.loads(l) for l in (tmp_path / "scratch_versions.jsonl").read_text().splitlines()]
    origins = [(r["agent"], r["origin"]) for r in rows]
    assert origins[:2] == [("a01", "birth"), ("a02", "birth")]
    assert ("a01", "follow_up") in origins and ("a02", "follow_up") in origins
    assert any(o.startswith("fork:follow_up") for _, o in origins)
    for r in rows:
        assert set(r) == {"agent", "t", "stamp", "origin", "words", "scratch"}
    followups = [r for r in rows if r["origin"] == "follow_up"]
    assert all(r["scratch"] == "saw something" for r in followups)


@needs_bank
@pytest.mark.parametrize("kind", ["notebook_voi", "notebook_llmDecide"])
def test_full_stub_run_of_the_variants(tmp_path, kind):
    episode = next(JsonlBank(path=COLD_START_BANK).episodes())
    episode = dataclasses.replace(episode,
                                  questions_by_day=episode.questions_by_day[:2])
    recs = episode.agent_view().sensable_receptacle_ids
    stub = _Stub(anchors=(recs[0], recs[5], ON_PERSON, OUT_OF_HOUSE),
                 fork_p=0.15, carrier=episode.resident_ids[0],
                 carrier_room=episode.receptacle_rooms[recs[0]])
    stub.decide_action, stub.decide_target = "look", "somewhere_illegal"
    out = tmp_path / "arm"
    cfg = dataclasses.replace(nm.CONFIGS[kind], questions_per_day=float(
        len(episode.questions_by_day[0])))
    brain = NotebookMixtureBrain(stub, log_dir=out, config=cfg)
    belief = NotebookMixtureBelief(random.Random(0), brain)
    records = list(run_episode(Agent(belief, NotebookMixturePolicy(brain)),
                               episode))
    brain.finish()
    assert len(records) == sum(len(d) for d in episode.questions_by_day)
    by_day: Dict[int, float] = {}
    for r in records:
        by_day[r.day_index] = by_day.get(r.day_index, 0.0) + r.budget_spent
    assert all(v <= episode.budget_per_day for v in by_day.values())
    assert brain.n_looks > 0
    diag = brain.diagnostics()
    assert diag["config"]["label"] == kind
    assert set(diag["looks_per_day"]) <= {"0", "1"}
    events = [json.loads(l) for l in (out / "population.jsonl").read_text().splitlines()]
    reviews = [e for e in events if e["event"] == "review"]
    assert len(reviews) == 2 and all(r["mode"] == "top_fresh" for r in reviews)
    ran = [r for r in reviews if not r.get("skipped")]
    if ran:
        assert any(e["event"] == "birth" and e.get("origin") == "review"
                   for e in events)
        assert any(e["event"] == "retire" for e in events)
    rows = [json.loads(l) for l in (out / "scratch_versions.jsonl").read_text().splitlines()]
    assert rows and {r["origin"] for r in rows} >= {"birth"}
    calls = [json.loads(l) for l in (out / "calls.jsonl").read_text().splitlines()]
    types = {c["type"] for c in calls}
    if kind == "notebook_llmDecide":
        assert "decide" in types and brain.decide_corrected > 0
        dec = [json.loads(l) for l in (out / "decisions.jsonl").read_text().splitlines()]
        assert dec and all("VALUE OF INFORMATION" in d["briefing"] for d in dec)
        assert len(dec) == sum(1 for c in calls if c["type"] == "decide")
    else:
        assert "decide" not in types
    fc = [json.loads(l) for l in (out / "forecasts.jsonl").read_text().splitlines()]
    assert all("voi" in r for r in fc if r["reason"] != "no budget")


def _one_look(brain, forecasts, found=("keys",)):
    look = {"receptacle": "counter_k", "room": "kitchen", "t": 100,
            "forecasts": forecasts, "invalid": [],
            "weights_before": brain.population.weights}
    brain._look_procedure(look, "counter_k", "kitchen", tuple(found), (),
                          "line", 100)


def test_fork_gate_admits_only_below_average_scorers_once_a_day(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o"), fork_p=1.0)
    brain = _voi_brain(stub, tmp_path)
    brain.decide("keys", 100)
    # a01 predicts the look well, a02 badly: only a02's fork is accepted
    _one_look(brain, {"a01": {"keys": 0.9}, "a02": {"keys": 0.1}})
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    forks = [e for e in events if e["event"] == "fork"]
    gated = [e for e in events if e["event"] == "fork_gated"]
    assert [f["parent"] for f in forks] == ["a02"]
    assert [g["parent"] for g in gated] == ["a01"] and brain.forks_gated == 1
    winner_prompt = [p for p in stub.prompts if "no fork this time" in p]
    assert winner_prompt and "above it" in winner_prompt[0]
    loser_prompt = [p for p in stub.prompts if "You may propose a FORK" in p and "below it" in p]
    assert loser_prompt and "lost credibility" in loser_prompt[0]
    # a02 already forked today: a second bad look gates it again; its
    # child a03 (below average, never forked) is the only fork
    _one_look(brain, {"a01": {"keys": 0.9}, "a02": {"keys": 0.1}, "a03": {"keys": 0.5}})
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    assert [e["parent"] for e in events if e["event"] == "fork"] == ["a02", "a03"]
    assert [e["parent"] for e in events if e["event"] == "fork_gated"] == ["a01", "a01", "a02"]
    # every follow-up shows the panel's scoreboard with the agent marked
    boards = [p for p in stub.prompts if "PANEL SCORES on this look" in p]
    assert len(boards) == 5 and all("(you)" in b for b in boards)


def test_review_waits_for_enough_looks_and_spares_the_newborn(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k"))
    brain = _voi_brain(stub, tmp_path, review_every_looks=2)
    brain.decide("keys", 100)
    _one_look(brain, {"a01": {"keys": 0.9}, "a02": {"keys": 0.1}, "a03": {"keys": 0.3}})
    brain._end_of_day_review(0)
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    review = [e for e in events if e["event"] == "review"][-1]
    assert review["skipped"].startswith("1 looks since the last review, review at 2")
    assert brain.looks_since_review == 1
    # a second look: the review runs, but on day 0 every agent was born
    # today, so nobody is eligible for retirement - fork + fresh birth only
    brain.day = 0
    _one_look(brain, {"a01": {"keys": 0.9}, "a02": {"keys": 0.1}, "a03": {"keys": 0.3}})
    n_before = brain.population.size
    brain._end_of_day_review(0)
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    review = [e for e in events if e["event"] == "review"][-1]
    assert review["candidate"] == "a01" and review["retire"] is None
    assert not any(e["event"] == "retire" for e in events)
    assert brain.population.size == n_before + 2 and brain.looks_since_review == 0
    newborn = [e for e in events if e["event"] == "birth" and e.get("origin") == "review"][-1]["agent"]
    # next cycle: two more looks; the newborn and the fork (born at the
    # review) are eligible now, a02 is still the lowest
    brain.day = 1
    fc = {a: {"keys": 0.5} for a in brain.population.agents}; fc["a02"] = {"keys": 0.05}
    _one_look(brain, fc); _one_look(brain, fc)
    brain._end_of_day_review(1)
    events = [json.loads(l) for l in (tmp_path / "population.jsonl").read_text().splitlines()]
    review = [e for e in events if e["event"] == "review"][-1]
    assert review["retire"] == "a02"
    assert newborn in brain.population.agents


def test_parallel_calls_are_accounted_in_agent_order(tmp_path):
    import threading
    class _Slow(_Stub):
        # later agents reply first, so order in the log must come from the
        # brain, not from arrival
        def generate(self, system, user, *a, **kw):
            n = len(self.prompts)
            with self._lock:
                self.prompts.append(user)
            time.sleep(0.05 * (4 - min(n, 3)))
            return super().generate(system, user, *a, **kw)
    stub = _Slow(anchors=("counter_k", "desk_o", "table_k", "shelf_o"))
    stub._lock = threading.Lock()
    brain = _voi_brain(stub, tmp_path, parallel=8)
    started = time.monotonic()
    d = brain.decide("keys", 100)
    assert set(d["distribution"]) == set(RECS)
    calls = [json.loads(l) for l in (tmp_path / "calls.jsonl").read_text().splitlines()]
    qf = [c["agent"] for c in calls if c["type"] == "question_forecast"]
    assert qf == ["a01", "a02", "a03", "a04"]
    assert [c["n"] for c in calls] == list(range(1, len(calls) + 1))
    # the four slow replies overlapped (sequential would be >= 0.2+0.15+0.1+0.05 s)
    assert time.monotonic() - started < 0.45


def test_skip_below_drops_negligible_agents_from_questions_not_looks(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k"))
    brain = _voi_brain(stub, tmp_path, skip_below=0.05)
    brain.decide("keys", 100)
    brain.population.update_log_weights({"a01": 0.0, "a02": 0.0, "a03": -6.0}, 100, "x")
    assert brain.population.weights["a03"] < 0.05
    d = brain.decide("keys", 200)
    fc = [json.loads(l) for l in (tmp_path / "forecasts.jsonl").read_text().splitlines()][-1]
    assert set(fc["forecasts"]) == {"a01", "a02"} and fc["skipped"] == ["a03"]
    assert abs(sum(d["distribution"].values()) - 1.0) < 1e-6
    # a look still asks and grades everyone
    brain.note_sense("counter_k")
    assert set(brain._pending_look["forecasts"]) == {"a01", "a02", "a03"}


def test_per_question_look_cap_and_follow_up_set(tmp_path):
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k", "shelf_o"))
    brain = _voi_brain(stub, tmp_path, use_it_or_lose_it=False, voi_lambda=0.0,
                       max_looks_per_question=2, beta=1.0)
    brain.decide("keys", 100)
    brain._sensed_this_question = ["counter_k", "desk_o"]
    d = brain.decide("keys", 100)
    assert d["action"] == "answer" and d["reason"] == "question look cap 2"
    # follow-up set: everyone at >= 5% or in the top 3
    w = {"a01": 0.6, "a02": 0.3, "a03": 0.06, "a04": 0.04}
    assert brain._follow_up_set(w) == ["a01", "a02", "a03"]
    w = {"a01": 0.97, "a02": 0.01, "a03": 0.01, "a04": 0.01}
    assert brain._follow_up_set(w) == ["a01", "a02", "a03"]
    # after a look only the active set gets a follow-up call; all are graded
    _one_look(brain, {"a01": {"keys": 0.9}, "a02": {"keys": 0.5},
                      "a03": {"keys": 0.1}, "a04": {"keys": 0.01}})
    look = json.loads((tmp_path / "looks.jsonl").read_text().splitlines()[-1])
    assert set(look["scores"]) == {"a01", "a02", "a03", "a04"}
    assert len(look["follow_ups"]) == 3
    calls = [json.loads(l) for l in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert sorted(c["agent"] for c in calls if c["type"] == "follow_up") == sorted(look["follow_ups"])


def test_population_cap_from_config():
    stub = _Stub(anchors=("counter_k", "desk_o", "table_k", "shelf_o"))
    brain = _voi_brain(stub, population_cap=5)
    assert brain.population.cap == 5
