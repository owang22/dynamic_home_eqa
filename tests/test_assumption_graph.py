"""The graph arm: rollup and entropy, edit scoping through a rebuild,
the birth rule, automatic pruning, the uncovered bank, add_assumption
coverage, re-parenting, beta = 0 equivalence, and leaf-id substitution.
Everything runs offline against a fake elicitor. Times are seconds
since episode start; day 0 is Monday."""

from __future__ import annotations

import json
import math
import random

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.beliefs.hypothesis_program import HypothesisProgramBelief
from baselines.beliefs.llm_hypothesis_mixture import (LLMHypothesisMixture,
                                                      ReaskConfig)
from baselines.harness import run_episode
from baselines.llm_hypotheses.assumption_graph import (
    LEAF_ID_RE, AssumptionGraph, apply_operations, live_values,
    node_entropy, parse_graph, premise_recovered, value_weight,
    value_weights)
from baselines.policies.assumption_disambiguation import (
    AssumptionDisambiguationSense)
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import DAY_SECONDS, EpisodeContext, Observation

H = 3600
RECS = ("desk", "kitchen_table", "shelf", "hamper", "OUT_OF_HOUSE")
OBJECTS = {"laptop_1": "laptop", "mug_1": "mug", "towel_1": "towel",
           "mug_2": "mug", "keys_1": "keys"}


def _ctx(n_days: int = 28) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh_test", receptacle_ids=RECS,
        object_classes=OBJECTS, budget_per_day=2, n_days=n_days,
        unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def _obs(obj, rec, day, hour):
    return Observation(object_id=obj, object_class=OBJECTS[obj],
                       receptacle_id=rec, t=int(day * DAY_SECONDS + hour * H),
                       source="scripted")


def _leaf(leaf_id, composition, pattern, rest, activities=()):
    return {"leaf_id": leaf_id,
            "assumes": {"composition": composition,
                        "weekday_pattern": pattern},
            "rationale": f"{composition}/{pattern}",
            "distinguishing_prediction": "laptop on the desk at 13:00",
            "distinguishing_check": {"target": "laptop_1", "at": rest,
                                     "days": "weekday", "hour": 13.0},
            "rest": {"laptop_1": rest, "class:mug": "shelf"},
            "activities": list(activities)}


ASSUMPTIONS = {
    "composition": {"question": "how many people live here",
                    "values": {"solo": "one adult", "couple": "two adults"}},
    "weekday_pattern": {"question": "where is the resident on weekdays",
                        "values": {"works_away": "out 9 to 6",
                                   "works_from_home": "at home working"}},
}


def _envelope(leaves):
    return {"assumptions": json.loads(json.dumps(ASSUMPTIONS)),
            "leaves": leaves}


FOUR_LEAVES = [
    _leaf("p_0001", "solo", "works_away", "desk"),
    _leaf("p_0002", "solo", "works_from_home", "kitchen_table"),
    _leaf("p_0003", "couple", "works_away", "shelf"),
    _leaf("p_0004", "couple", "works_from_home", "hamper"),
]


def _graph(leaves=FOUR_LEAVES) -> AssumptionGraph:
    result = parse_graph(_envelope(leaves), OBJECTS, RECS)
    assert result.graph is not None, result.problems
    return result.graph


class _OpsElicitor:
    """Fake graph elicitor: applies a fixed operation list once."""

    def __init__(self, operations):
        self.operations = operations
        self.calls = []

    def __call__(self, report, graph, context):
        self.calls.append(report)
        return apply_operations(graph, self.operations,
                                report["leaf_weights"], OBJECTS, RECS)


def _mixture(tmp_path, envelope, reask=None, elicitor=None, **kw):
    d = tmp_path / "graph"
    d.mkdir(exist_ok=True)
    (d / "hh_test.json").write_text(json.dumps(envelope))
    m = LLMHypothesisMixture(random.Random(0), d, reask=reask,
                             elicitor=elicitor, **kw)
    m.reset(_ctx())
    return m


# --------------------------------------------------------------- 1 rollup

def test_rollup_sums_leaf_weights_and_entropy_matches_hand_computation():
    graph = _graph()
    w = {"p_0001": 0.5, "p_0002": 0.3, "p_0003": 0.15, "p_0004": 0.05}
    assert value_weight(graph, w, "composition", "solo") == pytest.approx(0.8)
    assert value_weight(graph, w, "composition", "couple") == pytest.approx(0.2)
    assert value_weights(graph, w, "weekday_pattern") == pytest.approx(
        {"works_away": 0.65, "works_from_home": 0.35})
    expected = -(0.8 * math.log(0.8) + 0.2 * math.log(0.2))
    assert node_entropy(graph, w, "composition") == pytest.approx(expected)
    # Statistical particles are not in the map; weights renormalize
    # among leaves, so scaling every leaf weight changes nothing.
    half = {k: v * 0.5 for k, v in w.items()}
    assert value_weight(graph, half, "composition", "solo") == pytest.approx(0.8)
    assert live_values(graph, w, 0.10) == {
        "composition": ["solo", "couple"],
        "weekday_pattern": ["works_away", "works_from_home"]}
    assert live_values(graph, w, 0.25)["composition"] == ["solo"]


# ------------------------------------------------- 2 edit scoping, rebuild

WORK = {"name": "work", "days": "weekday", "frequency_per_week": 5,
        "start_hour": 9.0, "duration_h": 8.0,
        "moves": [{"target": "laptop_1", "to": "kitchen_table",
                   "chance": "usually"}]}


def test_edit_leaf_leaves_other_leaves_byte_identical_and_keeps_weights(
        tmp_path):
    # Rest stays as stored (rest edits are rejected); the edit adds an
    # activity, which is the kind of change the LLM is allowed to make.
    edited = _leaf("p_0002", "solo", "works_from_home", "kitchen_table",
                   activities=[WORK])
    elicitor = _OpsElicitor([{"op": "edit_leaf", "leaf_id": "p_0002",
                              "body": edited}])
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(2,), max_calls=1,
                             new_class_triggers=False), elicitor)
    for day in range(2):
        for hour in (8, 12, 18):
            m.update(_obs("laptop_1", "desk", day, hour))
    before_bodies = {h["leaf_id"]: json.dumps(h, sort_keys=True)
                     for h in m._raw_hypotheses}
    before_lw = dict(zip([h["leaf_id"] for h in m._raw_hypotheses],
                         m._log_weights))
    m.update(_obs("laptop_1", "desk", 2, 8))          # fires the ask
    assert m.reask_events[-1]["changed"] is True
    assert m.reask_events[-1]["trigger"] == "scheduled"
    after_bodies = {h["leaf_id"]: json.dumps(h, sort_keys=True)
                    for h in m._raw_hypotheses}
    for lid in ("p_0001", "p_0003", "p_0004"):
        assert after_bodies[lid] == before_bodies[lid]
    assert after_bodies["p_0002"] != before_bodies["p_0002"]
    # Log weights of untouched leaves survive the rebuild: the gaps
    # between them are unchanged (rebuild renormalizes by the max, and
    # one more sighting was applied before the ask fired).
    after_lw = dict(zip([h["leaf_id"] for h in m._raw_hypotheses],
                        m._log_weights))
    gap_before = before_lw["p_0001"] - before_lw["p_0003"]
    gap_after = after_lw["p_0001"] - after_lw["p_0003"]
    assert gap_after == pytest.approx(gap_before, abs=0.6)
    # The edited leaf kept its identity and thus its weight slot.
    assert "p_0002" in after_lw
    assert m.edit_log and m.edit_log[0]["op"] == "edit_leaf"
    assert m.edit_log[0]["trigger"] == "scheduled"


# ------------------------------------------------------------ 3 birth rule

def test_add_assumption_value_births_only_against_live_values():
    graph = _graph()
    op = [{"op": "add_assumption_value", "assumption": "composition",
           "value": "family", "description": "with a child"}]
    live = {"p_0001": 0.5, "p_0002": 0.3, "p_0003": 0.15, "p_0004": 0.05}
    result = apply_operations(graph, op, live, OBJECTS, RECS)
    assert result.graph is not None, result.problems
    cells = sorted(b["assumes"]["weekday_pattern"] for b in result.births)
    assert cells == ["works_away", "works_from_home"]
    # Now works_from_home is dead (0.01 + 0.0 < 0.10): no crossed leaf.
    dead = {"p_0001": 0.89, "p_0002": 0.01, "p_0003": 0.10, "p_0004": 0.0}
    result = apply_operations(graph, op, dead, OBJECTS, RECS)
    assert result.graph is not None, result.problems
    assert [b["assumes"]["weekday_pattern"] for b in result.births] == [
        "works_away"]
    skipped = [s for s in result.skipped_births
               if s.get("value") == "works_from_home"]
    assert skipped and "live floor" in skipped[0]["reason"]
    # Born leaves have fresh opaque ids and the template's body.
    born = result.births[0]
    assert LEAF_ID_RE.match(born["leaf_id"]) and born["template"] == "p_0001"
    assert result.graph.leaf("p_0001")["rest"] == \
        result.graph.leaf(born["leaf_id"])["rest"]


# --------------------------------------------------------------- 4 pruning

def test_automatic_pruning_fires_after_days_and_keeps_three(tmp_path):
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(), max_calls=0,
                             new_class_triggers=False), None,
                 leaf_weight_floor=0.02, leaf_prune_days=3)
    # Only p_0001 puts the laptop on the desk; the others sink.
    for day in range(8):
        for hour in (8, 12, 18):
            m.update(_obs("laptop_1", "desk", day, hour))
    assert m.prune_log, "nothing was pruned"
    assert m.prune_log[0]["day"] - m.prune_log[0]["below_since_day"] >= 3
    assert m.n_hypotheses == 3
    assert "p_0001" in [h["leaf_id"] for h in m._raw_hypotheses]
    assert len(m.graph.leaves) == 3
    assert len(m.particles) == 3 + 1     # plus the statistical particle
    # Pruning keeps the leaf count at 3 however long it runs.
    for day in range(8, 16):
        m.update(_obs("laptop_1", "desk", day, 12))
    assert m.n_hypotheses == 3
    assert m.graph_diagnostics()["leaf_count_trace"]["15"] == 3


# --------------------------------------------------------- 5 uncovered bank

def test_new_class_enters_bank_but_new_object_of_modeled_class_does_not(
        tmp_path):
    rec = _OpsElicitor([])
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(),
                             uncovered_bank_max=4, uncovered_bank_ramp=False),
                 rec)
    m.update(_obs("mug_2", "shelf", 0, 9))       # class:mug is modeled
    assert m.uncovered_bank == []
    m.update(_obs("towel_1", "hamper", 0, 10))   # towel: no leaf mentions it
    assert [b["class"] for b in m.uncovered_bank] == ["towel"]
    m.update(_obs("keys_1", "desk", 0, 11))
    assert [b["class"] for b in m.uncovered_bank] == ["towel", "keys"]
    assert m.reask_events == []                  # bank 2 < max 4, no ramp


def test_uncovered_bank_fires_with_ramp_and_records_trigger(tmp_path):
    rec = _OpsElicitor([])
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(),
                             uncovered_bank_max=4, uncovered_bank_ramp=True),
                 rec)
    cfg = m._reask
    assert cfg.bank_threshold(0, 28) == 2.0
    assert cfg.bank_threshold(27, 28) == 4.0
    m.update(_obs("towel_1", "hamper", 0, 10))
    assert m.reask_events == []
    m.update(_obs("keys_1", "desk", 0, 11))      # day 0: bar is 2
    assert m.reask_events[-1]["trigger"] == "uncovered"
    assert rec.calls[0]["trigger"] == "uncovered"
    assert [b["class"] for b in rec.calls[0]["uncovered_bank"]] == [
        "towel", "keys"]
    assert m.uncovered_bank == []                # cleared by the call


# ------------------------------------------------- 6 add_assumption coverage

def test_add_assumption_without_full_edit_leaf_coverage_is_rejected_whole():
    graph = _graph()
    new_assumption = {"op": "add_assumption", "assumption": "pets",
                      "question": "is there a pet",
                      "values": {"dog": "a dog", "none": "no pet"}}

    def edit(leaf_id, pet):
        body = dict(graph.leaf(leaf_id))
        body["assumes"] = {**body["assumes"], "pets": pet}
        return {"op": "edit_leaf", "leaf_id": leaf_id, "body": body}

    partial = [new_assumption, edit("p_0001", "dog"), edit("p_0002", "none")]
    result = apply_operations(graph, partial, {}, OBJECTS, RECS)
    assert result.graph is None
    assert any("p_0003" in p and "p_0004" in p for p in result.problems)
    assert result.applied == []
    full = [new_assumption] + [edit(lid, "none")
                               for lid in ("p_0001", "p_0002", "p_0003",
                                           "p_0004")]
    result = apply_operations(graph, full, {}, OBJECTS, RECS)
    assert result.graph is not None, result.problems
    assert list(result.graph.assumptions) == ["composition",
                                              "weekday_pattern", "pets"]
    assert all(leaf["assumes"]["pets"] == "none"
               for leaf in result.graph.leaves)


# ------------------------------------------------------------- 7 re-parent

def test_reparented_leaf_keeps_its_weight_because_leaf_id_is_unchanged(
        tmp_path):
    # Move p_0001 (the winner) from solo to couple; its body is otherwise
    # identical. Its log weight must ride along with the id.
    moved = dict(FOUR_LEAVES[0])
    moved["assumes"] = {"composition": "couple",
                        "weekday_pattern": "works_away"}
    ops = [{"op": "edit_leaf", "leaf_id": "p_0001", "body": moved}]
    # Three leaves: the (couple, works_away) cell is free for p_0001.
    m = _mixture(tmp_path, _envelope([FOUR_LEAVES[0], FOUR_LEAVES[1],
                                      FOUR_LEAVES[3]]),
                 ReaskConfig(window=1000, scheduled_days=(2,), max_calls=1,
                             new_class_triggers=False), _OpsElicitor(ops))
    for day in range(2):
        for hour in (8, 12, 18):
            m.update(_obs("laptop_1", "desk", day, hour))
    w_before = m.leaf_weights
    assert max(w_before, key=w_before.get) == "p_0001"
    m.update(_obs("laptop_1", "desk", 2, 8))
    assert m.reask_events[-1]["changed"] is True
    w_after = m.leaf_weights
    assert max(w_after, key=w_after.get) == "p_0001"
    assert w_after["p_0001"] >= w_before["p_0001"] - 0.05
    assert m.graph.leaf("p_0001")["assumes"]["composition"] == "couple"
    assert m.assumption_weights["composition"]["values"]["couple"] > 0.5


# ------------------------------------------------------------- 8 beta = 0

def test_beta_zero_reproduces_the_myopic_voi_policy_exactly(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    recs = list(episode.receptacle_ids)
    leaves = [
        {"leaf_id": "p_a001",
         "assumes": {"composition": "solo", "weekday_pattern": "works_away"},
         "rationale": "a", "rest": {"keys_shift": recs[0]}, "activities": []},
        {"leaf_id": "p_a002",
         "assumes": {"composition": "solo",
                     "weekday_pattern": "works_from_home"},
         "rationale": "b", "rest": {"keys_shift": recs[1]}, "activities": []},
        {"leaf_id": "p_a003",
         "assumes": {"composition": "couple", "weekday_pattern": "works_away"},
         "rationale": "c", "rest": {"badge_shift": recs[2]}, "activities": []},
    ]
    d = tmp_path / "graph"
    d.mkdir()
    (d / f"{episode.household_id}.json").write_text(
        json.dumps(_envelope(leaves)))

    def records(policy_kind: str):
        belief = LLMHypothesisMixture(random.Random(7), d)
        rng = random.Random(13)
        policy = (VoIThresholdSense(rng, lam=0.05)
                  if policy_kind == "myopic" else
                  AssumptionDisambiguationSense(rng, lam=0.05,
                                                belief=belief, beta=0.0))
        return list(run_episode(Agent(belief=belief, policy=policy), episode))

    myopic = records("myopic")
    targeted = records("assumption")
    assert len(myopic) == len(targeted)
    for a, b in zip(myopic, targeted):
        assert a.actions == b.actions
        assert a.answer_receptacle == b.answer_receptacle
        assert a.correct == b.correct
        assert a.budget_spent == b.budget_spent


def test_positive_beta_bonus_targets_only_relevant_assumptions(tmp_path):
    from baselines.policies.assumption_disambiguation import (
        assumption_bonus, relevance)
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES))
    dists = m.value_distributions("laptop_1", int(13 * H))
    # composition and weekday_pattern both split the laptop's location
    # across values, so both are relevant and the bonus is positive.
    assert relevance(dists["composition"]) > 0.0
    assert assumption_bonus(dists, "desk") > 0.0
    # An object every leaf agrees about (mugs rest on the shelf under
    # every leaf) gives zero relevance everywhere: no bonus.
    agreed = m.value_distributions("mug_1", int(13 * H))
    assert all(relevance(per_value) == pytest.approx(0.0, abs=1e-9)
               for per_value in agreed.values())
    assert assumption_bonus(agreed, "shelf") == pytest.approx(0.0, abs=1e-9)


# ------------------------------------------------- 9 leaf id substitution

def test_path_derived_leaf_ids_are_replaced_and_logged():
    leaves = [
        _leaf("composition/solo/works_away", "solo", "works_away", "desk"),
        _leaf("p_0002", "solo", "works_from_home", "kitchen_table"),
        _leaf("p_0002", "couple", "works_away", "shelf"),       # duplicate
    ]
    result = parse_graph(_envelope(leaves), OBJECTS, RECS)
    assert result.graph is not None, result.problems
    ids = result.graph.leaf_ids()
    assert all(LEAF_ID_RE.match(i) for i in ids) and len(set(ids)) == 3
    subs = {s["given"]: s for s in result.substitutions}
    assert subs["composition/solo/works_away"]["reason"].startswith("not an")
    assert subs["p_0002"]["reason"] == "duplicate"
    assert result.graph.leaves[0]["hypothesis_id"] == ids[0]
    # Deterministic: the same envelope gets the same substitutes.
    again = parse_graph(_envelope(leaves), OBJECTS, RECS)
    assert again.graph.leaf_ids() == ids


def test_parser_rules_drop_partial_and_duplicate_cells_and_caps():
    partial = _leaf("p_0009", "solo", "works_away", "desk")
    partial["assumes"] = {"composition": "solo"}
    result = parse_graph(_envelope(FOUR_LEAVES + [partial]), OBJECTS, RECS)
    assert result.graph is not None and len(result.graph.leaves) == 4
    assert result.dropped[0]["bad_strings"] == ["weekday_pattern"]
    too_many = [_leaf(f"p_{i:04x}", "solo", "works_away", "desk")
                for i in range(13)]
    result = parse_graph(_envelope(too_many), OBJECTS, RECS)
    assert result.graph is None
    assert any("exceeds the cap" in p for p in result.problems)
    leaked = _envelope(FOUR_LEAVES)
    leaked["assumptions"]["composition"]["values"]["solo"] = "keeps laptop_1"
    result = parse_graph(leaked, OBJECTS, RECS)
    assert result.graph is None and any("must not name" in p
                                        for p in result.problems)


# ---------------------------------------------------------------- report

def test_revision_report_carries_assumptions_bank_and_leaf_weights(
        tmp_path):
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(), max_calls=0),
                 None)
    for day in range(3):
        m.update(_obs("laptop_1", "desk", day, 13))
        m.update(_obs("towel_1", "hamper", day, 8))
    report = m.revision_report(int(3 * DAY_SECONDS))
    assert set(report["assumptions"]) == {"composition", "weekday_pattern"}
    assert report["assumptions"]["composition"]["values"]["solo"] > 0.5
    assert report["hypotheses"][0]["assumes"]["composition"] == "solo"
    assert [b["class"] for b in report["uncovered_bank"]] == ["towel"]
    assert set(report["leaf_weights"]) == {"p_0001", "p_0002", "p_0003",
                                           "p_0004"}
    trace = m.graph_diagnostics()["assumption_trace"]
    assert set(trace) == {"0", "1", "2"}
    names = [p.name for p in m.particles]
    assert names[0] == "HypothesisProgram(p_0001)"
    assert isinstance(m.particles[0], HypothesisProgramBelief)


def test_premise_recovery_matches_synonyms():
    graph = _graph()
    hit = premise_recovered(graph, {"composition": "solo",
                                    "work_pattern": "works_away"})
    assert hit == {"composition": "composition=solo",
                   "work_pattern": "weekday_pattern=works_away"}
    miss = premise_recovered(graph, {"composition": "roommates"})
    assert miss == {"composition": None}


def test_flat_file_still_loads_as_the_flat_arm(tmp_path):
    d = tmp_path / "flat"
    d.mkdir()
    (d / "hh_test.json").write_text(json.dumps({"hypotheses": [
        {"hypothesis_id": "h1", "rationale": "r",
         "rest": {"laptop_1": "desk"}, "activities": []}]}))
    m = LLMHypothesisMixture(random.Random(0), d)
    m.reset(_ctx())
    assert not m.is_graph and m.assumption_weights == {}
    assert m.value_distributions("laptop_1", 0) == {}
    assert [p.name for p in m.particles][0] == "HypothesisProgram(h1)"


# ------------------------------------------------ phase 1: what the LLM may not do

def test_drop_leaf_is_rejected_and_logged_and_only_prune_removes_leaves(
        tmp_path):
    ops = [{"op": "drop_leaf", "leaf_id": "p_0003", "reason": "dead"},
           {"op": "edit_leaf", "leaf_id": "p_0002",
            "body": _leaf("p_0002", "solo", "works_from_home",
                          "kitchen_table", activities=[WORK])}]
    graph = _graph()
    result = apply_operations(graph, ops, {}, OBJECTS, RECS)
    assert result.graph is not None, result.problems
    assert len(result.graph.leaves) == 4          # nothing removed
    assert result.rejected and result.rejected[0]["op"] == "drop_leaf"
    assert "automatic prune" in result.rejected[0]["reason"]
    assert [a["op"] for a in result.applied] == ["edit_leaf"]
    # Through the mixture: the rejection lands in rejected_ops and the
    # leaf count moves only when the automatic prune fires.
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(2,), max_calls=1,
                             new_class_triggers=False), _OpsElicitor(ops),
                 leaf_prune_days=3)
    for day in range(3):
        for hour in (8, 12, 18):
            m.update(_obs("laptop_1", "desk", day, hour))
    assert m.rejected_ops and m.rejected_ops[0]["op"] == "drop_leaf"
    assert m.n_hypotheses == 4
    for day in range(3, 9):
        m.update(_obs("laptop_1", "desk", day, 12))
    assert m.n_hypotheses == 3 and m.prune_log


def test_edit_leaf_with_any_rest_change_is_rejected_whole():
    graph = _graph()
    changed = _leaf("p_0002", "solo", "works_from_home", "shelf")   # rest moved
    ops = [{"op": "edit_leaf", "leaf_id": "p_0002", "body": changed},
           {"op": "add_assumption_value", "assumption": "composition",
            "value": "family", "description": "kids"}]
    result = apply_operations(graph, ops, {}, OBJECTS, RECS)
    assert result.graph is None
    assert any("rest is fit from sightings" in p and "laptop_1" in p
               for p in result.problems)
    # The rest map written as a list of {target, at} but equal in content
    # is not a change.
    same = _leaf("p_0002", "solo", "works_from_home", "kitchen_table")
    same["rest"] = [{"target": "laptop_1", "at": "kitchen_table"},
                    {"target": "class:mug", "at": "shelf"}]
    result = apply_operations(graph, [{"op": "edit_leaf", "leaf_id": "p_0002",
                                       "body": same}], {}, OBJECTS, RECS)
    assert result.graph is not None, result.problems


def test_check_must_name_in_home_receptacle_and_resolves_by_direction(
        tmp_path):
    from baselines.beliefs.hypothesis_program import (
        HypothesisValidationError, parse_hypothesis)
    from baselines.types import SenseResult
    away = _leaf("p_0009", "solo", "works_away", "desk")
    away["distinguishing_check"] = {"target": "laptop_1", "at": "OUT_OF_HOUSE",
                                    "days": "weekday", "hour": 13.0}
    with pytest.raises(HypothesisValidationError) as err:
        parse_hypothesis(away, OBJECTS, RECS, unsensable=("OUT_OF_HOUSE",))
    assert err.value.bad_strings == ("OUT_OF_HOUSE",)
    parse_hypothesis(away, OBJECTS, RECS)          # flat arm: still lax
    # if_seen: wrong at the rest — an empty look is in favour, a find is not.
    leaf = _leaf("p_0001", "solo", "works_away", "desk")
    leaf["distinguishing_check"] = {"target": "laptop_1", "at": "desk",
                                    "days": "weekday", "hour": 13.0,
                                    "if_seen": "wrong"}
    m = _mixture(tmp_path, _envelope([leaf] + FOUR_LEAVES[1:]))
    def look(day, hour, contents):
        return SenseResult(receptacle_id="desk",
                           t=int(day * DAY_SECONDS + hour * H),
                           contents=tuple(contents),
                           object_classes={o: OBJECTS[o] for o in contents})
    m.update(look(0, 13, []))                      # Monday 13:00, empty
    m.update(look(1, 13, ["laptop_1"]))            # Tuesday 13:00, found
    m.update(look(5, 13, []))                      # Saturday: not a weekday
    m.update(look(2, 20, []))                      # outside the hour window
    rows = [r for r in m.check_outcomes if r["leaf_id"] == "p_0001"]
    assert [(r["day"], r["in_favour"]) for r in rows] == [(0, True), (1, False)]
    report = m.revision_report(int(3 * DAY_SECONDS))
    verdict = {h["hypothesis_id"]: h["verdict"] for h in report["hypotheses"]}
    assert verdict["p_0001"] == "came true 1/2 times"


def test_empty_look_at_rest_credits_an_away_move():
    from baselines.beliefs.hypothesis_program import HypothesisProgramBelief
    from baselines.types import SenseResult
    raw = {"hypothesis_id": "h", "rationale": "r",
           "rest": {"laptop_1": "desk"},
           "activities": [{"name": "office", "days": "weekday",
                           "frequency_per_week": 5, "start_hour": 9.0,
                           "duration_h": 8.0,
                           "moves": [{"target": "laptop_1",
                                      "to": "OUT_OF_HOUSE",
                                      "chance": "usually"}]}]}
    model = HypothesisProgramBelief(random.Random(0), raw)
    model.reset(_ctx())
    state = model._rule_states[0]
    s0, f0 = state.success, state.failure
    t = int(0 * DAY_SECONDS + 13 * H)               # Monday, mid-window
    model.update(SenseResult(receptacle_id="desk", t=t, contents=(),
                             object_classes={}))
    assert state.success - s0 == pytest.approx(0.5, abs=0.02)
    assert state.failure == f0
    # An empty look elsewhere, or outside the window, credits nothing.
    model.update(SenseResult(receptacle_id="shelf", t=t, contents=(),
                             object_classes={}))
    model.update(SenseResult(receptacle_id="desk",
                             t=int(0 * DAY_SECONDS + 22 * H), contents=(),
                             object_classes={}))
    assert state.success - s0 == pytest.approx(0.5, abs=0.02)


def test_operations_naming_a_settled_assumption_are_rejected():
    graph = _graph()
    settled = {"composition": "solo"}
    ops = [{"op": "add_assumption_value", "assumption": "composition",
            "value": "family", "description": "kids"},
           {"op": "add_leaf", "body": _leaf("p_0aaa", "couple",
                                            "works_from_home", "shelf")},
           {"op": "add_assumption_value", "assumption": "weekday_pattern",
            "value": "shift_work", "description": "nights"}]
    result = apply_operations(graph, ops, {"p_0001": 0.95, "p_0002": 0.05},
                              OBJECTS, RECS, settled=settled)
    assert result.graph is not None, result.problems
    assert [r["op"] for r in result.rejected] == ["add_assumption_value",
                                                  "add_leaf"]
    assert all(r["assumption"] == "composition" for r in result.rejected)
    assert [a["op"] for a in result.applied] == ["add_assumption_value"]
    from baselines.llm_hypotheses.assumption_graph import settled_assumptions
    assert settled_assumptions(graph, {"p_0001": 0.95, "p_0002": 0.05}) == {
        "composition": "solo", "weekday_pattern": "works_away"}
    assert settled_assumptions(graph, {"p_0001": 0.5, "p_0002": 0.3,
                                       "p_0003": 0.2}) == {}


# ------------------------------------------------ phase 2: bucket and call types

def test_anomaly_bucket_fires_on_third_repeat_of_one_key_only(tmp_path):
    rec = _OpsElicitor([])
    m = _mixture(tmp_path, _envelope(FOUR_LEAVES),
                 ReaskConfig(window=1000, scheduled_days=(),
                             new_class_triggers=False, min_gap=0,
                             anomaly_p=0.2, anomaly_repeats=3), rec)
    # Every leaf rests mugs on the shelf, and a long shelf history keeps
    # each leaf's rest Dirichlet there: a hamper sighting of mug_1 stays
    # an anomaly for all of them even after it has happened before.
    for i in range(40):
        m.update(_obs("mug_1", "shelf", i // 8, 6 + (i % 8) * 2))
    assert m.bucket_trace == []
    # The rest Dirichlet absorbs each sighting (about 1 count against
    # 3 pseudo-counts plus the decayed history), so repeats must come
    # close together to stay under the threshold: days 5-7 here.
    m.update(_obs("mug_1", "hamper", 5, 9))        # bin 4
    m.update(_obs("mug_1", "hamper", 5, 13))       # bin 6: different key
    m.update(_obs("mug_1", "hamper", 5, 17))       # bin 8: different key
    assert m.reask_events == []
    assert {tuple(r["key"]) for r in m.bucket_trace} == {
        ("mug_1", "hamper", 4), ("mug_1", "hamper", 6),
        ("mug_1", "hamper", 8)}
    m.update(_obs("mug_1", "hamper", 6, 9))        # bin 4 again (2)
    assert m.reask_events == []
    m.update(_obs("mug_1", "hamper", 7, 9))        # bin 4 third time
    assert m.reask_events[-1]["trigger"] == "anomaly"
    assert m.reask_events[-1]["call_type"] == "diversify"
    assert rec.calls[-1]["call_type"] == "diversify"
    assert rec.calls[-1]["anomaly_firing"]["count"] == 3
    assert m.anomaly_bucket == []                  # cleared by the call
    # A sighting some leaf predicts never enters the bucket.
    m.update(_obs("laptop_1", "hamper", 10, 9))    # p_0004 rests it there
    assert m.anomaly_bucket == []


def test_diversify_call_rejects_edit_leaf_but_keeps_additions():
    from baselines.llm_hypotheses.assumption_graph import DIVERSIFY_OPS
    graph = _graph()
    ops = [{"op": "edit_leaf", "leaf_id": "p_0002",
            "body": _leaf("p_0002", "solo", "works_from_home",
                          "kitchen_table", activities=[WORK])},
           {"op": "add_activity", "leaf_id": "p_0001", "activity": WORK}]
    result = apply_operations(graph, ops, {}, OBJECTS, RECS,
                              allowed_ops=DIVERSIFY_OPS)
    assert result.graph is not None, result.problems
    assert [r["op"] for r in result.rejected] == ["edit_leaf"]
    assert [a["op"] for a in result.applied] == ["add_activity"]
    assert result.graph.leaf("p_0001")["activities"][0]["name"] == "work"
    assert result.graph.leaf("p_0002")["activities"] == []
