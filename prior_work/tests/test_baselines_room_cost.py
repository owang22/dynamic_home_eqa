"""Room-change travel cost: position tracking, pricing, and budget refusal.

The model under test: a sense costs 1.0 when the target receptacle is in
the room the robot already stands in and ``1 + c`` otherwise, where the
robot's room is ``home_base_room`` at the start of every day, moves with
every ambient room visit delivered up to ``t_query``, and moves with
every receptacle it actively senses. At ``c = 0`` this must be the
flat-budget model the package had before, exactly.

The fixture (``write_room_cost_bank``) makes each of those clauses
observable on its own: the kitchen is the home base, a day-0 visit puts
the robot in the study and a day-1 visit puts it in the hall, and truth
is static so nothing here depends on belief dynamics.
"""

from __future__ import annotations

import pathlib
import random
from typing import List, Optional, Tuple

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_room_cost_bank
from baselines.beliefs.last_observation import LastObservation
from baselines.harness import QuestionRecord, run_episode
from baselines.policies.base import DecisionPolicy
from baselines.policies.never_sense import NeverSense
from baselines.policies.sequential_search import SequentialSearch
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import (Action, AnswerNow, DAY_SECONDS, Episode,
                             EpisodeContext, Prediction, Question,
                             RobotPosition, Sense, SenseResult)


@pytest.fixture
def episode(tmp_path: pathlib.Path) -> Episode:
    bank = write_room_cost_bank(tmp_path / "room_cost_bank.jsonl")
    return next(bank.episodes())


def _agent(policy: DecisionPolicy) -> Agent:
    return Agent(belief=LastObservation(random.Random(0)), policy=policy)


class ScriptedSenses(DecisionPolicy):
    """Senses a fixed list of receptacles for every question, in order,
    then answers. Deliberately blind to budget and cost: the harness must
    be the thing that refuses what cannot be afforded."""

    def __init__(self, targets: Tuple[str, ...]) -> None:
        self._targets = targets
        self._question_id: Optional[str] = None
        self._i = 0
        self.seen_budgets: List[float] = []
        self.context: Optional[EpisodeContext] = None

    def reset(self, context: EpisodeContext) -> None:
        self.context = context
        self._question_id = None
        self._i = 0

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._i = 0
        self.seen_budgets.append(budget_remaining)
        if self._i >= len(self._targets):
            return AnswerNow()
        target = self._targets[self._i]
        self._i += 1
        return Sense(receptacle_id=target)


# ---------------------------------------------------------------- cost rule

@pytest.mark.parametrize("c", [0.0, 0.25, 0.5, 1.0, 2.0])
def test_cost_is_one_in_room_and_one_plus_c_elsewhere(episode: Episode,
                                                      c: float) -> None:
    """The whole cost model, read straight off the context."""
    position = RobotPosition(room="kitchen")
    context = episode.agent_view(c, position)
    # counter_k, sink_k, table_k are the kitchen; desk_s and hook_h are not.
    assert context.sense_cost("counter_k") == 1.0
    assert context.sense_cost("sink_k") == 1.0
    assert context.sense_cost("desk_s") == pytest.approx(1.0 + c)
    assert context.sense_cost("hook_h") == pytest.approx(1.0 + c)
    position.room = "study"
    assert context.sense_cost("desk_s") == 1.0
    assert context.sense_cost("counter_k") == pytest.approx(1.0 + c)


def test_bank_without_rooms_costs_one_everywhere(tmp_path: pathlib.Path
                                                 ) -> None:
    """A bank carrying no room map degenerates to the flat model, even at
    a large c: there is no notion of "elsewhere" to charge for."""
    from baselines.bank import write_synthetic_bank

    ep = next(write_synthetic_bank(tmp_path / "b.jsonl").episodes())
    context = ep.agent_view(2.0, RobotPosition(room=None))
    assert all(context.sense_cost(r) == 1.0
               for r in context.sensable_receptacle_ids)


def test_home_base_is_the_room_with_most_receptacles(episode: Episode) -> None:
    assert episode.home_base_room == "kitchen"          # 3 vs 1 and 1
    assert episode.receptacle_rooms["desk_s"] == "study"
    assert "OUT_OF_HOUSE" not in episode.receptacle_rooms


def test_home_base_ties_break_by_room_id_sort_order() -> None:
    from baselines.export_bank import home_base_room

    assert home_base_room({"a1": "zulu", "a2": "alpha"}) == "alpha"
    assert home_base_room({"a1": "zulu", "a2": "zulu", "a3": "alpha"}) == "zulu"


# ----------------------------------------------------------- position moves

def _run(episode: Episode, policy: DecisionPolicy,
         c: float) -> List[QuestionRecord]:
    return list(run_episode(_agent(policy), episode, room_change_cost=c))


def test_passive_visit_before_t_query_moves_position(episode: Episode) -> None:
    """The day-0 11:00 visit is to the study, so the 12:00 question finds
    the robot there rather than at its kitchen home base."""
    records = _run(episode, NeverSense(), 0.5)
    assert records[0].robot_room_at_query == "study"


def test_position_resets_at_day_start(episode: Episode) -> None:
    """Day 0 ends with the robot in the study (the day-0 visit) — yet the
    day-1 questions must not inherit it. Day 1's own 11:00 visit is to the
    hall, which is where day 1's questions find it: neither the study nor
    a stale kitchen, so the reset and the day-1 visit are both visible."""
    records = _run(episode, NeverSense(), 0.5)
    assert [r.robot_room_at_query for r in records] == [
        "study", "study", "hall", "hall"]

    # Without any visit at all the reset is what remains: strip the visit
    # rows and every question sits at the home base, on both days.
    import dataclasses
    quiet = dataclasses.replace(episode, scripted_evidence=(),
                                scripted_observations=())
    assert [r.robot_room_at_query for r in _run(quiet, NeverSense(), 0.5)] == [
        "kitchen"] * 4


def test_active_sense_moves_position(episode: Episode) -> None:
    """First sense is priced from the study (where the patrol left the
    robot), the second from wherever the first one took it."""
    policy = ScriptedSenses(("hook_h", "counter_k", "sink_k"))
    records = _run(episode, policy, 0.5)
    senses = [a for a in records[0].actions if a["type"] == "sense"]
    assert [a["receptacle_id"] for a in senses] == ["hook_h", "counter_k",
                                                    "sink_k"]
    # study -> hall (1.5), hall -> kitchen (1.5), kitchen -> kitchen (1.0).
    assert [a["cost"] for a in senses] == [1.5, 1.5, 1.0]
    assert [a["same_room"] for a in senses] == [False, False, True]
    assert records[0].n_senses == 3
    assert records[0].same_room_senses == 1
    assert records[0].budget_spent == pytest.approx(4.0)


@pytest.mark.parametrize("c", [0.0, 0.25, 0.5, 1.0, 2.0])
def test_same_room_senses_cost_one_at_every_c(episode: Episode,
                                              c: float) -> None:
    """Three kitchen receptacles in a row: only the first pays travel.

    How many of the three the budget of 4 actually affords depends on c
    (at c = 2 the trip alone costs 3), so the claim is about the shape of
    the price list, not its length."""
    policy = ScriptedSenses(("counter_k", "sink_k", "table_k"))
    records = _run(episode, policy, c)
    costs = [a["cost"] for a in records[0].actions if a["type"] == "sense"]
    assert costs[0] == pytest.approx(1.0 + c)     # study -> kitchen
    assert costs[1:] == pytest.approx([1.0] * (len(costs) - 1))


# ------------------------------------------------------------ budget refusal

def test_harness_refuses_a_sense_it_cannot_afford_and_logs_it(
        episode: Episode) -> None:
    """Budget 4 with c = 2: the first cross-room sense costs 3, leaving 1,
    which cannot cover a second cross-room sense of cost 3. The harness
    refuses it — it does not part-charge, and it does not wait for the
    budget to reach zero first."""
    policy = ScriptedSenses(("hook_h", "desk_s"))
    records = _run(episode, policy, 2.0)
    first = records[0]
    assert first.n_senses == 1
    assert first.budget_spent == pytest.approx(3.0)
    assert first.budget_after == pytest.approx(1.0)
    assert first.forced_answer is True
    refusal = first.actions[-1]
    assert refusal == {"type": "forced_answer", "refused_sense": "desk_s",
                       "cost": 3.0, "budget_remaining": 1.0}


def test_refusal_happens_with_budget_left_over(episode: Episode) -> None:
    """The old rule was "refuse at zero"; the new one is "refuse what you
    cannot afford", and the two differ exactly here — budget strictly
    positive, sense strictly unaffordable."""
    policy = ScriptedSenses(("hook_h", "desk_s"))
    record = _run(episode, policy, 2.0)[0]
    assert record.budget_after > 0.0 and record.forced_answer


def test_fractional_budget_question_terminates(episode: Episode) -> None:
    """A policy that never stops asking, against a budget that never lands
    on zero. Starting in the study with 4 units at c = 0.25, the tour
    hall -> study -> kitchen costs 1.25 three times over and leaves 0.25,
    which affords nothing: the question must end on that refusal rather
    than grind on a fractional remainder. The sense-step cap is the second
    guarantee — it bounds the loop by the number of sensable receptacles
    however the arithmetic falls."""
    everywhere = ("hook_h", "desk_s", "counter_k", "sink_k", "table_k") * 4
    records = _run(episode, ScriptedSenses(everywhere), 0.25)
    assert len(records) == 4                       # every question resolved
    first = records[0]
    assert first.n_senses == 3
    assert first.forced_answer
    assert first.budget_after == pytest.approx(0.25)
    assert 0.0 < first.budget_after < 1.0          # never reaches zero
    n_sensable = len(episode.receptacle_ids) - len(
        episode.unsensable_receptacle_ids)
    assert all(r.n_senses <= n_sensable for r in records)


def test_step_cap_bounds_a_policy_that_resenses(episode: Episode) -> None:
    """The loop bound is the sensable-receptacle count, not the budget, so
    even a policy that re-senses one receptacle forever terminates."""
    records = _run(episode, ScriptedSenses(("counter_k",) * 50), 0.0)
    assert len(records) == 4
    n_sensable = len(episode.receptacle_ids) - len(
        episode.unsensable_receptacle_ids)
    assert records[0].n_senses <= n_sensable
    assert records[0].forced_answer


# ---------------------------------------------------------- c = 0 regression

@pytest.mark.parametrize("policy_factory", [
    lambda: NeverSense(),
    lambda: SequentialSearch(random.Random(1)),
    lambda: VoIThresholdSense(random.Random(1), lam=0.05),
])
def test_c_zero_is_the_flat_model(episode: Episode,
                                  policy_factory: object) -> None:
    """At c = 0 every sense costs 1, so spend equals the sense count and
    the whole model is the pre-existing flat accounting."""
    assert callable(policy_factory)
    records = _run(episode, policy_factory(), 0.0)
    for r in records:
        assert r.budget_spent == float(r.n_senses)
        assert all(a["cost"] == 1.0 for a in r.actions
                   if a["type"] == "sense")


# ------------------------------------------------------------- policy access

def test_voi_policy_prices_by_value_per_cost(episode: Episode) -> None:
    """The cost-aware rule in isolation: with two candidates of equal voi
    the policy must prefer the one in the room it already stands in, and
    at c = 0 it must be indifferent (falling back to the p(r) tie-break)."""
    position = RobotPosition(room="kitchen")
    policy = VoIThresholdSense(random.Random(0), lam=0.01)
    policy.reset(episode.agent_view(1.0, position))
    prediction = Prediction(
        distribution={"counter_k": 0.4, "desk_s": 0.4, "sink_k": 0.1,
                      "table_k": 0.05, "hook_h": 0.05},
        argmax="counter_k")
    question = Question(question_id="q", object_id="mug_k", t_query=0,
                        day_index=0)
    action = policy.decide(question, prediction, 10.0, 0)
    assert action == Sense(receptacle_id="counter_k")   # same voi, half cost

    position.room = "study"
    policy.reset(episode.agent_view(1.0, position))
    assert policy.decide(question, prediction, 10.0, 0) == Sense(
        receptacle_id="desk_s")


def test_voi_threshold_scales_with_cost(episode: Episode) -> None:
    """``voi >= lambda * cost``: a candidate worth sensing from inside its
    room can be not worth the trip from outside it."""
    prediction = Prediction(
        distribution={"desk_s": 0.5, "counter_k": 0.3, "sink_k": 0.1,
                      "table_k": 0.05, "hook_h": 0.05}, argmax="desk_s")
    question = Question(question_id="q", object_id="keys_s", t_query=0,
                        day_index=0)
    from baselines.policies.voi_sense import value_of_information

    voi = value_of_information(prediction.distribution, ["desk_s"])["desk_s"]
    lam = voi / 1.5           # affordable at cost 1, not at cost 2
    inside = VoIThresholdSense(random.Random(0), lam=lam)
    inside.reset(episode.agent_view(1.0, RobotPosition(room="study")))
    assert inside.decide(question, prediction, 10.0, 0) == Sense(
        receptacle_id="desk_s")

    outside = VoIThresholdSense(random.Random(0), lam=lam)
    outside.reset(episode.agent_view(1.0, RobotPosition(room="kitchen")))
    # From the kitchen desk_s costs 2, so its rate halves and drops below
    # lambda; the kitchen candidates are worth less voi than desk_s but
    # are priced at 1 — the policy answers only if neither clears lambda.
    chosen = outside.decide(question, prediction, 10.0, 0)
    assert chosen != Sense(receptacle_id="desk_s")


def test_position_is_live_inside_the_policy_context(episode: Episode) -> None:
    """Policies hold the context, not a snapshot of the price: the harness
    moves the robot and the SAME context must report the new prices."""
    policy = ScriptedSenses(("hook_h",))
    _run(episode, policy, 0.5)
    context = policy.context
    assert context is not None
    # After the run the robot stands where its last sense took it (hall on
    # the final question), and the context reflects that live.
    assert context.robot_position.room == "hall"
    assert context.sense_cost("hook_h") == 1.0
    assert context.sense_cost("counter_k") == 1.5


# --------------------------------------------------------------- bank schema

def test_loader_rejects_rooms_without_a_home_base(tmp_path: pathlib.Path
                                                  ) -> None:
    import json

    from baselines.bank import BankFormatError

    path = tmp_path / "bad.jsonl"
    header = json.loads(
        (write_room_cost_bank(tmp_path / "ok.jsonl").path).read_text()
        .splitlines()[0])
    del header["home_base_room"]
    path.write_text(json.dumps(header) + "\n")
    with pytest.raises(BankFormatError, match="home_base_room"):
        list(JsonlBank(path=path).episodes())


def test_loader_rejects_unknown_roomed_receptacle(tmp_path: pathlib.Path
                                                  ) -> None:
    import json

    from baselines.bank import BankFormatError

    path = tmp_path / "bad.jsonl"
    header = json.loads(
        (write_room_cost_bank(tmp_path / "ok.jsonl").path).read_text()
        .splitlines()[0])
    header["receptacle_rooms"]["nowhere_x"] = "kitchen"
    path.write_text(json.dumps(header) + "\n")
    with pytest.raises(BankFormatError, match="receptacle_rooms"):
        list(JsonlBank(path=path).episodes())


def test_day_boundary_is_inclusive_of_its_own_visits(episode: Episode) -> None:
    """A visit at exactly t = day start belongs to the new day: it happens
    after the reset, not before it."""
    import dataclasses

    visit = SenseResult(receptacle_id="hook_h", t=DAY_SECONDS, contents=())
    shifted = dataclasses.replace(episode, scripted_evidence=(visit,))
    records = _run(shifted, NeverSense(), 0.5)
    assert [r.robot_room_at_query for r in records] == [
        "kitchen", "kitchen", "hall", "hall"]
