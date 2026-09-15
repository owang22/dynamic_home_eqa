"""The tree arm (Phase 3), offline: inheritance and label rules, root
distinctness, node and subtree pruning, rest_overrides as pseudo-counts,
the two-operation contract, tour-seen vocabulary, beta = 0 equivalence,
the anomaly bucket, belief-side computation from evidence only, prompt
hygiene, away-move absence credit, and a dead-code check."""

from __future__ import annotations

import ast
import json
import pathlib
import random
import re

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.beliefs.hypothesis_program import HypothesisProgramBelief
from baselines.beliefs.llm_hypothesis_mixture import ReaskConfig
from baselines.beliefs.tree_hypothesis_mixture import TreeHypothesisMixture
from baselines.harness import run_episode
from baselines.llm_hypotheses.hypothesis_tree import (
    HypothesisTree, apply_operations, label_recovered, label_weights,
    parse_tree, settled_labels, subtree_weights)
from baselines.llm_hypotheses.tree_prompt import (FORBIDDEN_PROMPT_STRINGS,
                                                  FORBIDDEN_WORD_RE,
                                                  tree_revision_prompt,
                                                  tree_tour_start_prompt)
from baselines.policies.label_disambiguation import LabelDisambiguationSense
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import DAY_SECONDS, EpisodeContext, Observation, SenseResult

H = 3600
RECS = ("desk", "kitchen_table", "shelf", "hamper", "OUT_OF_HOUSE", "ON_PERSON")
OBJECTS = {"laptop_1": "laptop", "mug_1": "mug", "towel_1": "towel",
           "mug_2": "mug", "keys_1": "keys"}
SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "baselines"


def _ctx(n_days: int = 28) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh_test", receptacle_ids=RECS,
        object_classes=OBJECTS, budget_per_day=2, n_days=n_days,
        unsensable_receptacle_ids=("OUT_OF_HOUSE", "ON_PERSON"))


def _obs(obj, rec, day, hour):
    return Observation(object_id=obj, object_class=OBJECTS[obj],
                       receptacle_id=rec, t=int(day * DAY_SECONDS + hour * H),
                       source="scripted")


def _check(rest="desk", if_seen="right"):
    return {"target": "laptop_1", "at": rest, "days": "weekday",
            "hour": 13.0, "if_seen": if_seen}


OFFICE = {"name": "office", "days": "weekday", "frequency_per_week": 5,
          "start_hour": 9.0, "duration_h": 8.0,
          "moves": [{"target": "laptop_1", "to": "OUT_OF_HOUSE",
                     "chance": "usually"}]}
COFFEE = {"name": "coffee", "days": "both", "frequency_per_week": 6,
          "start_hour": 7.0, "duration_h": 1.0,
          "moves": [{"target": "class:mug", "to": "kitchen_table",
                     "chance": "usually"}]}


def _root(node_id, labels, rest, activities=()):
    return {"node_id": node_id, "parent": None, "labels": list(labels),
            "rationale": "/".join(labels), "distinguishing_prediction": "x",
            "distinguishing_check": _check(rest),
            "rest": {"laptop_1": rest, "class:mug": "shelf"},
            "activities": [json.loads(json.dumps(a)) for a in activities]}


THREE_ROOTS = [
    _root("p_0001", ["solo", "works_away"], "desk", [OFFICE]),
    _root("p_0002", ["solo", "works_from_home"], "kitchen_table"),
    _root("p_0003", ["couple", "works_away"], "shelf"),
]


def _payload(nodes=THREE_ROOTS, vocabulary=None):
    out = {"nodes": json.loads(json.dumps(nodes))}
    if vocabulary is not None:
        out["vocabulary"] = vocabulary
    return out


def _tree(nodes=THREE_ROOTS) -> HypothesisTree:
    result = parse_tree(_payload(nodes), OBJECTS, RECS)
    assert result.tree is not None, result.problems
    return result.tree


def _child(parent, labels_added, delta, check=None):
    return {"op": "add_child", "parent": parent, "labels_added": labels_added,
            "rationale": "child", "distinguishing_prediction": "y",
            "distinguishing_check": check or _check("kitchen_table"),
            "delta": delta}


class _OpsElicitor:
    """Fake tree elicitor: applies a fixed operation list per call."""

    def __init__(self, operations):
        self.operations = operations
        self.calls = []

    def __call__(self, report, tree, context):
        self.calls.append(report)
        return apply_operations(tree, self.operations, OBJECTS, RECS,
                                unsensable=("OUT_OF_HOUSE", "ON_PERSON"))


def _mixture(tmp_path, payload, reask=None, elicitor=None, **kw):
    d = tmp_path / "tree"
    d.mkdir(exist_ok=True)
    (d / "hh_test.json").write_text(json.dumps(payload))
    m = TreeHypothesisMixture(random.Random(0), d, reask=reask,
                              elicitor=elicitor, **kw)
    m.reset(_ctx())
    return m


# ---------------------------------------------- 1 inheritance and labels

def test_child_inherits_and_labels_must_strictly_extend_the_parent():
    tree = _tree()
    ops = [_child("p_0001", ["evening_gym"],
                  {"activities_added": [COFFEE], "rest_overrides": {"towel_1": "hamper"}})]
    result = apply_operations(tree, ops, OBJECTS, RECS)
    assert result.tree is not None, result.problems
    child_id = result.applied[0]["node_id"]
    body = result.tree.materialize(child_id)
    assert body["labels"] == ["solo", "works_away", "evening_gym"]
    assert [a["name"] for a in body["activities"]] == ["office", "coffee"]
    assert body["rest"] == {"laptop_1": "desk", "class:mug": "shelf",
                            "towel_1": "hamper"}
    # Parent body is byte-identical to before.
    assert result.tree.materialize("p_0001") == tree.materialize("p_0001")
    # A child that adds no new label is rejected whole.
    bad = apply_operations(tree, [_child("p_0001", ["solo"],
                                         {"activities_added": [COFFEE]})],
                           OBJECTS, RECS)
    assert bad.tree is None and bad.rejected and "adds nothing" in bad.problems[0]
    # In a file, a child whose labels drop one of the parent's is dropped.
    nodes = THREE_ROOTS + [{"node_id": "p_0009", "parent": "p_0001",
                            "labels": ["works_away", "gym"], "rationale": "r",
                            "distinguishing_check": _check(),
                            "rest_overrides": {}, "activities": [COFFEE]}]
    parsed = parse_tree(_payload(nodes), OBJECTS, RECS)
    assert parsed.tree is not None and len(parsed.tree.nodes) == 3
    assert "contain every label" in parsed.dropped[0]["error"]
    # moves_changed replaces an inherited activity's moves.
    ops = [_child("p_0001", ["laptop_stays"],
                  {"moves_changed": [{"activity": "office", "moves": [
                      {"target": "laptop_1", "to": "desk", "chance": "usually"}]}]})]
    result = apply_operations(tree, ops, OBJECTS, RECS)
    assert result.tree is not None, result.problems
    body = result.tree.materialize(result.applied[0]["node_id"])
    assert body["activities"][0]["moves"][0]["to"] == "desk"


# ------------------------------------------------- 2 distinct root labels

def test_add_root_with_an_existing_label_set_is_rejected():
    tree = _tree()
    dup = {"op": "add_root", "body": _root("p_9999", ["works_away", "solo"],
                                          "hamper")}
    result = apply_operations(tree, [dup], OBJECTS, RECS)
    assert result.tree is None
    assert "same label set as node p_0001" in result.problems[0]
    assert result.rejected[0]["op"] == "add_root"
    fresh = {"op": "add_root", "body": _root("p_9999", ["retired"], "hamper")}
    result = apply_operations(tree, [fresh], OBJECTS, RECS)
    assert result.tree is not None and len(result.tree.nodes) == 4
    # Same rule at elicitation: two roots with one label set -> one kept.
    nodes = THREE_ROOTS + [_root("p_0004", ["works_away", "solo"], "hamper")]
    parsed = parse_tree(_payload(nodes), OBJECTS, RECS, roots_only=True)
    assert parsed.tree is not None and len(parsed.tree.nodes) == 3
    assert "same label set" in parsed.dropped[0]["error"]


# ------------------------------------------- 3 node prune re-parents

def test_node_prune_reparents_children_with_bodies_and_weights_intact(tmp_path):
    nodes = THREE_ROOTS + [
        {"node_id": "p_0010", "parent": "p_0003", "labels": ["couple", "works_away", "gym"],
         "rationale": "r", "distinguishing_check": _check("shelf"),
         "rest_overrides": {"towel_1": "hamper"}, "activities": [COFFEE]},
        {"node_id": "p_0011", "parent": "p_0010",
         "labels": ["couple", "works_away", "gym", "late"],
         "rationale": "r", "distinguishing_check": _check("shelf"),
         "rest_overrides": {}, "activities": [OFFICE]}]
    m = _mixture(tmp_path, _payload(nodes), leaf_weight_floor=0.02,
                 leaf_prune_days=1)
    before = m.tree.materialize("p_0011")
    # Starve the middle node by hand (its child keeps a normal weight, so
    # the subtree rule stays quiet and the node rule fires).
    for day in range(3):
        keys = [m._particle_key(h) for h in m._raw_hypotheses]
        if "p_0010" in keys:
            m._log_weights[keys.index("p_0010")] = -50.0
        m.update(_obs("mug_1", "shelf", day, 9))     # every node agrees
    assert "p_0010" in [r["node_id"] for r in m.prune_log], m.prune_log
    assert not m.tree.has("p_0010")
    child = m.tree.node("p_0011")
    assert child["parent"] == "p_0003"
    assert child["labels"] == ["couple", "works_away", "gym", "late"]
    after = m.tree.materialize("p_0011")
    assert after == before
    assert m.reparent_log[0]["child"] == "p_0011"
    assert "p_0011" in m.leaf_weights and "p_0010" not in m.leaf_weights
    # The particle for p_0011 was kept, so its raw body still matches.
    raw = next(h for h in m._raw_hypotheses if h["node_id"] == "p_0011")
    assert raw["rest"] == after["rest"]


# ------------------------------------------------- 4 subtree prune

def test_subtree_prune_removes_a_starved_subtree_and_keeps_three(tmp_path):
    nodes = THREE_ROOTS + [
        _root("p_0004", ["retired"], "hamper"),
        {"node_id": "p_0010", "parent": "p_0004", "labels": ["retired", "gym"],
         "rationale": "r", "distinguishing_check": _check("hamper"),
         "rest_overrides": {}, "activities": [COFFEE]}]
    m = _mixture(tmp_path, _payload(nodes), leaf_weight_floor=0.02,
                 leaf_prune_days=2)
    for day in range(5):
        keys = [m._particle_key(h) for h in m._raw_hypotheses]
        for nid in ("p_0004", "p_0010"):
            if nid in keys:
                m._log_weights[keys.index(nid)] = -60.0
        m.update(_obs("laptop_1", "desk", day, 9))
    kinds = {r["node_id"]: r["kind"] for r in m.prune_log}
    assert kinds.get("p_0004") == "subtree" and kinds.get("p_0010") == "subtree"
    assert set(m.tree.node_ids()) == {"p_0001", "p_0002", "p_0003"}
    # Never below three: starve everything, nothing more goes.
    for day in range(5, 12):
        m._log_weights[:3] = [-60.0, -60.0, -60.0]
        m.update(_obs("laptop_1", "desk", day, 9))
    assert len(m.tree.nodes) == 3


# ------------------------------------------- 5 rest_overrides pseudo-counts

def test_rest_overrides_change_only_the_stated_rest_prior():
    tree = _tree()
    ops = [_child("p_0001", ["towel_in_hamper"],
                  {"rest_overrides": {"towel_1": "hamper"}})]
    child_tree = apply_operations(tree, ops, OBJECTS, RECS).tree
    child_id = child_tree.node_ids()[-1]
    body = child_tree.materialize(child_id)
    model = HypothesisProgramBelief(random.Random(0), body)
    model.reset(_ctx())
    t0 = 0
    assert model.predict_readonly("towel_1", t0).argmax == "hamper"
    # A handful of sightings on the shelf outvote the override: it is a
    # pseudo-count of 3 decaying with a 72 h half-life, nothing more.
    for day in range(3):
        for hour in (8, 13, 19):
            model.update(_obs("towel_1", "shelf", day, hour))
    assert model.predict_readonly("towel_1", 3 * DAY_SECONDS).argmax == "shelf"
    # And the file form: a root with `rest_overrides` is dropped, a child
    # with `rest` is dropped.
    nodes = THREE_ROOTS + [{"node_id": "p_0012", "parent": "p_0001",
                            "labels": ["solo", "works_away", "x"],
                            "rationale": "r", "distinguishing_check": _check(),
                            "rest": {"towel_1": "hamper"}, "activities": []}]
    parsed = parse_tree(_payload(nodes), OBJECTS, RECS)
    assert "rest_overrides" in parsed.dropped[0]["error"]


# ---------------------------------------------- 6 two operations only

def test_any_other_operation_rejects_the_response_whole(tmp_path):
    tree = _tree()
    for op in ({"op": "edit_leaf", "leaf_id": "p_0001", "body": {}},
               {"op": "drop_leaf", "leaf_id": "p_0001"},
               {"op": "set_rest", "node_id": "p_0001", "rest": {}},
               {"op": "add_assumption", "assumption": "x", "values": {}}):
        good = _child("p_0001", ["gym"], {"activities_added": [COFFEE]})
        result = apply_operations(tree, [good, op], OBJECTS, RECS)
        assert result.tree is None
        assert result.applied == []
        assert [r["op"] for r in result.rejected] == ["add_child", op["op"]]
        assert "add_child and add_root" in result.rejected[0]["reason"]
    # Through the mixture: logged in rejected_ops, tree unchanged.
    rec = _OpsElicitor([{"op": "drop_leaf", "leaf_id": "p_0001"}])
    m = _mixture(tmp_path, _payload(),
                 ReaskConfig(window=1000, scheduled_days=(1,), max_calls=1,
                             new_class_triggers=False), rec)
    m.update(_obs("laptop_1", "desk", 1, 9))
    assert m.reask_events[-1]["changed"] is False
    assert m.rejected_ops and m.rejected_ops[0]["op"] == "drop_leaf"
    assert m.tree.node_ids() == ["p_0001", "p_0002", "p_0003"]


# ------------------------------------------ 7 vocabulary = tour-seen only

def test_tables_show_tour_seen_objects_only_and_unseen_delta_is_rejected(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    seen = {o.object_id for o in episode.initial_observations}
    user, _ = tree_tour_start_prompt(episode)
    for obj in episode.object_classes:
        assert (obj in user) == (obj in seen), obj
    # A delta naming an object the robot has not seen is rejected whole.
    vocab = {"laptop_1": "laptop", "mug_1": "mug"}
    rec = _OpsElicitor([_child("p_0001", ["gym"], {"rest_overrides": {"keys_1": "shelf"}})])

    class _KnownOnly(_OpsElicitor):
        def __call__(self, report, tree, context):
            self.calls.append(report)
            return apply_operations(tree, self.operations,
                                    report["known_objects"], RECS)
    rec = _KnownOnly(rec.operations)
    nodes = [_root("p_0001", ["a"], "desk"), _root("p_0002", ["b"], "shelf"),
             _root("p_0003", ["c"], "hamper")]
    for n in nodes:
        n["rest"] = {"laptop_1": n["rest"]["laptop_1"], "class:mug": "shelf"}
    m = _mixture(tmp_path, _payload(nodes, vocabulary=vocab),
                 ReaskConfig(window=1000, scheduled_days=(1,), max_calls=1,
                             new_class_triggers=False), rec)
    m.update(_obs("laptop_1", "desk", 1, 9))
    assert rec.calls[-1]["known_objects"] == vocab
    assert m.reask_events[-1]["changed"] is False
    assert "keys_1" in m.rejected_ops[0]["reason"]
    assert "keys_1" not in rec.calls[-1]["statistics"]


# ------------------------------------------------- 8 beta = 0 exactness

def test_beta_zero_reproduces_the_myopic_voi_policy_exactly(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    recs = list(episode.receptacle_ids)
    nodes = [
        {"node_id": "p_a001", "parent": None, "labels": ["a"], "rationale": "a",
         "rest": {"keys_shift": recs[0]}, "activities": []},
        {"node_id": "p_a002", "parent": None, "labels": ["b"], "rationale": "b",
         "rest": {"keys_shift": recs[1]}, "activities": []},
        {"node_id": "p_a003", "parent": None, "labels": ["c"], "rationale": "c",
         "rest": {"badge_shift": recs[2]}, "activities": []},
    ]
    d = tmp_path / "tree"
    d.mkdir()
    (d / f"{episode.household_id}.json").write_text(json.dumps({"nodes": nodes}))

    def records(kind):
        belief = TreeHypothesisMixture(random.Random(7), d)
        rng = random.Random(13)
        policy = (VoIThresholdSense(rng, lam=0.05) if kind == "myopic" else
                  LabelDisambiguationSense(rng, lam=0.05, belief=belief, beta=0.0))
        return list(run_episode(Agent(belief=belief, policy=policy), episode))

    myopic, targeted = records("myopic"), records("label")
    assert len(myopic) == len(targeted)
    for a, b in zip(myopic, targeted):
        assert a.actions == b.actions
        assert a.answer_receptacle == b.answer_receptacle
        assert a.budget_spent == b.budget_spent
    # A positive beta is computed from the label split and is finite.
    belief = TreeHypothesisMixture(random.Random(7), d)
    belief.reset(episode.agent_view())
    dists = belief.label_distributions("keys_shift", 3600)
    assert set(dists) == {"a", "b", "c"}
    share, with_, without = dists["a"]
    assert share == pytest.approx(1 / 3, abs=1e-6)
    assert with_[recs[0]] > without.get(recs[0], 0.0)


# ------------------------------------------------- 9 anomaly bucket

def test_anomaly_bucket_fires_on_third_repeat_in_tree_mode(tmp_path):
    rec = _OpsElicitor([])
    m = _mixture(tmp_path, _payload(),
                 ReaskConfig(window=1000, scheduled_days=(),
                             new_class_triggers=False, min_gap=0,
                             anomaly_p=0.2, anomaly_repeats=3), rec)
    for i in range(40):
        m.update(_obs("mug_1", "shelf", i // 8, 6 + (i % 8) * 2))
    assert m.bucket_trace == []
    m.update(_obs("mug_1", "hamper", 5, 9))
    m.update(_obs("mug_1", "hamper", 6, 9))
    assert m.reask_events == []
    m.update(_obs("mug_1", "hamper", 7, 9))
    assert m.reask_events[-1]["trigger"] == "anomaly"
    assert rec.calls[-1]["anomaly_firing"]["count"] == 3
    assert rec.calls[-1]["anomaly_bucket"][0]["object"] == "mug_1"
    assert m.anomaly_bucket == []
    # The report carries the tree, labels and settled floor.
    report = rec.calls[-1]
    assert {n["node_id"] for n in report["tree_nodes"]} == {"p_0001", "p_0002", "p_0003"}
    assert set(report["label_weights"]) == {"solo", "works_away", "works_from_home", "couple"}


# ------------------------------------ 10 belief side reads evidence only

def test_belief_side_computes_from_evidence_only():
    """No belief-side module touches the episode or the truth: checks,
    absence credit, the bucket and the report all come from Observation
    and SenseResult events."""
    for rel in ("beliefs/tree_hypothesis_mixture.py",
                "beliefs/llm_hypothesis_mixture.py",
                "llm_hypotheses/hypothesis_tree.py",
                "policies/label_disambiguation.py"):
        text = (SRC / rel).read_text()
        assert "episode." not in text, rel
        assert "truth" not in text, rel
        assert "true_location" not in text, rel
    # And dynamically: a check resolves from a SenseResult alone.
    tree = _tree()
    body = tree.materialize("p_0001")           # check: laptop at desk 13h
    m = TreeHypothesisMixture.__new__(TreeHypothesisMixture)
    from baselines.beliefs.hypothesis_program import parse_hypothesis
    hyp = parse_hypothesis(body, OBJECTS, RECS)
    t = int(1 * DAY_SECONDS + 13 * H)
    rows = TreeHypothesisMixture.check_resolutions(
        hyp.distinguishing_check, [(t, "desk", ("laptop_1",))])
    assert rows == [(t, True)]
    rows = TreeHypothesisMixture.check_resolutions(
        hyp.distinguishing_check, [(t, "desk", ())])
    assert rows == [(t, False)]


# ---------------------------------------------- 11 prompt hygiene

def test_prompts_carry_no_negations_or_forbidden_words_and_stay_short(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    user, _ = tree_tour_start_prompt(episode)
    rec = _OpsElicitor([])
    m = _mixture(tmp_path, _payload(),
                 ReaskConfig(window=1000, scheduled_days=(2,), max_calls=1,
                             new_class_triggers=False), rec)
    for day in range(3):
        m.update(_obs("laptop_1", "desk", day, 9))
        m.update(SenseResult(receptacle_id="kitchen_table",
                             t=int(day * DAY_SECONDS + 13 * H), contents=(),
                             object_classes={}))
    report = rec.calls[-1]
    from baselines.llm_hypotheses.prompt import vocabulary_tables
    tables = vocabulary_tables(episode, objects=dict(OBJECTS))
    revision = tree_revision_prompt(report, tables,
                                    json.dumps(m.tree.to_json(), indent=1))
    from baselines.llm_hypotheses.prompt import AWAY_SENTENCES
    for text, name in ((user, "installation"), (revision, "revision")):
        # The two mandated ON_PERSON / OUT_OF_HOUSE sentences are the
        # brief's own words and are exempt from the negation check.
        assert AWAY_SENTENCES in text, name
        low = text.replace(AWAY_SENTENCES, "").lower()
        for bad in FORBIDDEN_PROMPT_STRINGS:
            assert bad.lower() not in low, (name, bad)
        assert not FORBIDDEN_WORD_RE.search(text), name
        assert "ON_PERSON" in text and "OUT_OF_HOUSE" in text
        assert len(text.split()) < 2500, (name, len(text.split()))
    assert "add_child" in revision and "add_root" in revision
    assert "untested so far" in revision or "came true" in revision


# ----------------------------------------- 12 away-move absence credit

def test_empty_look_at_rest_credits_a_child_away_move():
    tree = _tree()
    ops = [_child("p_0002", ["evening_out"],
                  {"activities_added": [{"name": "gym", "days": "weekday",
                                         "frequency_per_week": 5,
                                         "start_hour": 18.0, "duration_h": 2.0,
                                         "moves": [{"target": "laptop_1",
                                                    "to": "ON_PERSON",
                                                    "chance": "usually"}]}]},
                  check=_check("kitchen_table", "wrong"))]
    result = apply_operations(tree, ops, OBJECTS, RECS)
    assert result.tree is not None, result.problems
    body = result.tree.materialize(result.applied[0]["node_id"])
    model = HypothesisProgramBelief(random.Random(0), body)
    model.reset(_ctx())
    state = model._rule_states[-1]
    s0, f0 = state.success, state.failure
    t = int(0 * DAY_SECONDS + 19 * H)          # Monday, inside 18-20h
    model.update(SenseResult(receptacle_id="kitchen_table", t=t, contents=(),
                             object_classes={}))
    # Half a sighting's credit times the (soft-edged) window weight: the
    # two-hour window with a 1.5 h start-hour prior gives ~0.5 at 19:00.
    assert 0.15 < state.success - s0 < 0.5 and state.failure == f0
    gained = state.success - s0
    # An empty look elsewhere, or outside the window, credits nothing.
    model.update(SenseResult(receptacle_id="shelf", t=t, contents=(),
                             object_classes={}))
    model.update(SenseResult(receptacle_id="kitchen_table",
                             t=int(0 * DAY_SECONDS + 3 * H), contents=(),
                             object_classes={}))
    assert state.success - s0 == pytest.approx(gained)
    # A check at an away token is rejected at parse time.
    bad = _child("p_0002", ["x"], {"activities_added": [COFFEE]},
                 check={"target": "laptop_1", "at": "ON_PERSON", "days": "both",
                        "hour": 19.0, "if_seen": "right"})
    result = apply_operations(tree, [bad], OBJECTS, RECS,
                              unsensable=("OUT_OF_HOUSE", "ON_PERSON"))
    assert result.tree is None and "ON_PERSON" in result.problems[0]


# ---------------------------------------------------- 13 dead code

def test_tree_modules_define_no_unreferenced_functions():
    """Every top-level function and method of the tree modules is
    referenced somewhere in src/ or tests/ other than its definition."""
    modules = ["llm_hypotheses/hypothesis_tree.py",
               "llm_hypotheses/tree_prompt.py",
               "beliefs/tree_hypothesis_mixture.py",
               "policies/label_disambiguation.py"]
    corpus = ""
    for path in list(SRC.rglob("*.py")) + list((SRC.parents[1] / "tests").rglob("*.py")):
        corpus += path.read_text() + "\n"
    unreferenced = []
    for rel in modules:
        tree = ast.parse((SRC / rel).read_text())
        names = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("__"):
                    continue
                names.append(node.name)
        for name in names:
            hits = len(re.findall(rf"\b{re.escape(name)}\b", corpus))
            if hits < 2:
                unreferenced.append(f"{rel}:{name}")
    assert not unreferenced, unreferenced


def test_label_recovery_and_settled_labels_are_name_matched():
    tree = _tree()
    w = {"p_0001": 0.8, "p_0002": 0.15, "p_0003": 0.05}
    lw = label_weights(tree, w)
    assert lw["solo"] == pytest.approx(0.95) and lw["works_away"] == pytest.approx(0.85)
    assert set(settled_labels(tree, w)) == {"solo"}
    rec = label_recovered(tree, w, {"composition": "solo",
                                    "work_pattern": "works_away"})
    assert rec["composition"]["label"] == "solo"
    assert rec["work_pattern"]["label"] == "works_away"
    assert rec["work_pattern"]["weight"] == pytest.approx(0.85)
    assert label_recovered(None, w, {"composition": "solo"}) == {"composition": None}
    assert subtree_weights(tree, w)["p_0001"] == pytest.approx(0.8)
