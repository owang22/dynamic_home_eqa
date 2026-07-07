"""
Eval harness for Dynamic EQA.

Loads (manifest.json + questions.json) pairs, builds Observations, runs agent
trials, and computes metrics.

Two backends:
  Standalone  — uses SceneState + Change replay (no Habitat-sim).
  PARTNR      — uses WorldGraph snapshots from a running PARTNR episode.
                Pass world_graph_snapshots={(t, wg)} to run_trial / run_eval.

Batched LLM path: LLMAgent.batch_act() processes all initial observations in
one vLLM call, then a second call for granted resenses, avoiding 14k sequential
HTTP round-trips.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Optional

# Allow running as a script from any working directory
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from dynamic_home_eqa.env.state import SceneState
from dynamic_home_eqa.env.deltas import Change, slot_desc
from dynamic_home_eqa.env.replay import state_at
from dynamic_home_eqa.agents.protocol import Agent, Decision, DecisionKind, Observation


# ---------------------------------------------------------------------------
# Slot → region mapping
# ---------------------------------------------------------------------------

_SLOT_REGION: dict[str, str] = {
    "dining.table":               "dining",
    "dining.table_pulled_out":    "dining",
    "dining.table_tucked":        "dining",
    "kitchen.counter":            "kitchen",
    "kitchen.counter_tucked":     "kitchen",
    "kitchen.counter_pulled_out": "kitchen",
    "kitchen.cabinet":            "kitchen",
    "living_room.sofa":           "living_room",
    "living_room.open_floor":     "living_room",
    "living_room.corner":         "living_room",
    "living_room.window_sill":    "living_room",
    "living_room.shelf":          "living_room",
    "office.desk":                "office",
    "office.shelf":               "office",
    "bedroom.bed":                "bedroom",
    "bedroom.nightstand":         "bedroom",
}

_REGION_CHANGE_RATES: dict[str, dict] = {
    "dining":      {8: 0.80, 12: 0.75, 18: 0.70, "default": 0.30},
    "kitchen":     {8: 0.45, 10: 0.60, 12: 0.50, 18: 0.65, "default": 0.25},
    "living_room": {18: 0.55, 20: 0.65, "default": 0.15},
    "office":      {9: 0.70, 10: 0.70,            "default": 0.20},
    "bedroom":     {8: 0.60, 22: 0.55,            "default": 0.10},
}


def _region(target_slot: Optional[str], obj_cat: str) -> str:
    if target_slot and target_slot in _SLOT_REGION:
        return _SLOT_REGION[target_slot]
    if target_slot:
        base = target_slot.split("_pulled_out")[0].split("_tucked")[0]
        return _SLOT_REGION.get(base, base)
    return obj_cat


def _region_prior(region: str, hour: int) -> dict:
    row  = _REGION_CHANGE_RATES.get(region, {})
    rate = float(row.get(hour, row.get("default", 0.10)))
    return {"typical_change_rate": rate}


# ---------------------------------------------------------------------------
# Manifest → SceneState + Change list
# ---------------------------------------------------------------------------

def _env_from_manifest(manifest: dict) -> tuple[SceneState, list[Change]]:
    from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest
    return initial_state_and_changes_from_manifest(manifest)


# ---------------------------------------------------------------------------
# State → observed_states slice
# ---------------------------------------------------------------------------

def _observed_states(
    snapshot: SceneState,
    region: str,
    query_type: str,
    obj_cat: str,
    target_slot: Optional[str],
    instance_id: Optional[str],
) -> dict[str, str]:
    if query_type == "location" and instance_id:
        inst = snapshot.instances.get(instance_id)
        return {instance_id: inst.current_semantic} if inst else {instance_id: "not_present"}
    return {
        iid: inst.current_semantic
        for iid, inst in snapshot.instances.items()
        if inst.category == obj_cat
        and _SLOT_REGION.get(inst.current_semantic, "") == region
    }


def _answer_text(
    snapshot: SceneState,
    query_type: str,
    obj_cat: str,
    target_slot: Optional[str],
    instance_id: Optional[str],
) -> str:
    if query_type == "presence":
        present = any(
            i.category == obj_cat and i.current_semantic == target_slot
            for i in snapshot.instances.values()
        )
        return "Yes" if present else "No"
    if query_type == "location":
        inst = snapshot.instances.get(instance_id or "")
        return slot_desc(inst.current_semantic) if inst else "not present"
    if query_type == "count":
        n = sum(
            1 for i in snapshot.instances.values()
            if i.category == obj_cat and i.current_semantic == target_slot
        )
        return str(n)
    return "?"


def _option_index(answer: str, options: list[str]) -> int:
    try:
        return options.index(answer)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Observation builder
# ---------------------------------------------------------------------------

def make_observation(
    question: dict,
    manifest: dict,
    initial_state: SceneState,
    changes: list[Change],
    observed_at: float,
    remaining_budget: int,
    with_prior: bool,
    questions_remaining: int = 0,
    world_graph=None,
) -> Observation:
    meta        = question["metadata"]
    query_type  = meta["query_type"]
    obj_cat     = meta["object_category"]
    target_slot = meta.get("target_slot")
    instance_id = meta.get("instance_id")
    query_time  = float(meta["present_time"])
    options     = question["options"]
    hour        = int(float(meta.get("observed_at", query_time - 1.0)))
    rgn         = _region(target_slot, obj_cat)

    snapshot   = state_at(initial_state, changes, observed_at)
    obs_states = _observed_states(snapshot, rgn, query_type, obj_cat, target_slot, instance_id)
    answer     = _answer_text(snapshot, query_type, obj_cat, target_slot, instance_id)
    obs_idx    = _option_index(answer, options)
    prior      = _region_prior(rgn, hour) if with_prior else None

    return Observation(
        region=rgn,
        observed_states=obs_states,
        observed_at=observed_at,
        query_time=query_time,
        household_type=manifest.get("resident_profile", ""),
        prompt=question["prompt"],
        options=options,
        remaining_budget=remaining_budget,
        time_of_day=query_time,
        region_prior=prior,
        questions_remaining=questions_remaining,
        observed_option_index=obs_idx,
        world_graph=world_graph,
    )


# ---------------------------------------------------------------------------
# Trial result + metrics
# ---------------------------------------------------------------------------

@dataclass
class TrialResult:
    prompt:        str
    query_type:    str
    difficulty:    str
    region:        str
    correct:       bool
    option_index:  int
    correct_index: int
    confidence:    float
    resense_count: int
    delta:         float
    low_dynamic:   bool


@dataclass
class EvalMetrics:
    n_trials:       int = 0
    n_correct:      int = 0
    total_resenses: int = 0
    results: list[TrialResult] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.n_correct / self.n_trials if self.n_trials else 0.0

    @property
    def resense_rate(self) -> float:
        return self.total_resenses / self.n_trials if self.n_trials else 0.0

    def accuracy_by(self, key: str) -> dict[str, float]:
        groups: dict[str, list[bool]] = {}
        for r in self.results:
            v = str(getattr(r, key, "?"))
            groups.setdefault(v, []).append(r.correct)
        return {k: sum(v) / len(v) for k, v in groups.items()}

    def print_summary(self, label: str = "") -> None:
        tag = f"[{label}]  " if label else ""
        print(f"\n{tag}accuracy={self.accuracy:.1%}  ({self.n_correct}/{self.n_trials})"
              f"  resense_rate={self.resense_rate:.1%}")
        for key in ("difficulty", "query_type"):
            bd = self.accuracy_by(key)
            print("  by " + key + ": " +
                  "  ".join(f"{k}={v:.0%}" for k, v in sorted(bd.items())))


# ---------------------------------------------------------------------------
# Trial runner (single question)
# ---------------------------------------------------------------------------

def run_trial(
    agent: Agent,
    question: dict,
    manifest: dict,
    initial_state: SceneState,
    changes: list[Change],
    remaining_budget: int = 0,
    questions_remaining: int = 1,
    with_prior: bool = True,
    world_graph=None,
) -> tuple[TrialResult, int]:
    meta        = question["metadata"]
    query_time  = float(meta["present_time"])
    observed_at = float(meta.get("observed_at", query_time - 1.0))
    rgn         = _region(meta.get("target_slot"), meta["object_category"])

    assert observed_at < query_time, (
        f"observed_at ({observed_at}) must be before query_time ({query_time})"
    )

    obs = make_observation(
        question, manifest, initial_state, changes,
        observed_at=observed_at,
        remaining_budget=remaining_budget,
        with_prior=with_prior,
        questions_remaining=questions_remaining,
        world_graph=world_graph,
    )

    resenses_spent = 0
    decision = agent.act(obs)

    if decision.kind == DecisionKind.RESENSE and remaining_budget > 0:
        resenses_spent = 1
        obs = make_observation(
            question, manifest, initial_state, changes,
            observed_at=query_time,
            remaining_budget=remaining_budget - 1,
            with_prior=with_prior,
            questions_remaining=questions_remaining,
        )
        decision = agent.act(obs)

    if decision.kind != DecisionKind.ANSWER:
        decision = Decision(
            kind=DecisionKind.ANSWER,
            option_index=obs.observed_option_index,
            confidence=0.0,
        )

    correct = (decision.option_index == question["correct_index"])

    return TrialResult(
        prompt=question["prompt"],
        query_type=meta["query_type"],
        difficulty=meta.get("difficulty_bin", ""),
        region=rgn,
        correct=correct,
        option_index=decision.option_index or 0,
        correct_index=question["correct_index"],
        confidence=decision.confidence or 0.0,
        resense_count=resenses_spent,
        delta=query_time - observed_at,
        low_dynamic=meta.get("low_dynamic", False),
    ), resenses_spent


# ---------------------------------------------------------------------------
# Batch evaluator
# ---------------------------------------------------------------------------

def run_eval(
    agent: Agent,
    results_dir: pathlib.Path,
    total_budget: int = 10,
    with_prior: bool = True,
) -> EvalMetrics:
    """Run agent over all (manifest + questions) pairs under results_dir."""
    trials: list[tuple[dict, SceneState, list[Change], dict]] = []
    for q_path in sorted(pathlib.Path(results_dir).glob("*/questions.json")):
        mpath = q_path.parent / "manifest.json"
        if not mpath.exists():
            continue
        manifest  = json.loads(mpath.read_text())
        questions = json.loads(q_path.read_text())["questions"]
        initial_state, changes = _env_from_manifest(manifest)
        for question in questions:
            trials.append((manifest, initial_state, changes, question))

    # Use two-phase batch eval for LLM agents
    try:
        from dynamic_home_eqa.agents.llm_agent import LLMAgent
        is_llm = isinstance(agent, LLMAgent)
    except ImportError:
        is_llm = False

    if is_llm:
        return _run_eval_llm_batched(agent, trials, total_budget, with_prior)

    metrics = EvalMetrics()
    remaining_budget = total_budget

    for i, (manifest, initial_state, changes, question) in enumerate(trials):
        result, spent = run_trial(
            agent, question, manifest, initial_state, changes,
            remaining_budget=remaining_budget,
            questions_remaining=len(trials) - i,
            with_prior=with_prior,
        )
        remaining_budget    -= spent
        metrics.n_trials    += 1
        metrics.n_correct   += int(result.correct)
        metrics.total_resenses += result.resense_count
        metrics.results.append(result)

    return metrics


def _run_eval_llm_batched(
    agent,
    trials: list[tuple[dict, SceneState, list[Change], dict]],
    total_budget: int,
    with_prior: bool,
) -> EvalMetrics:
    """Two-phase batched eval: one vLLM call for all initial obs, one for resenses."""
    n = len(trials)
    budget_rate_approx = total_budget / max(n, 1)

    print(f"  Building {n} initial observations …", flush=True)
    initial_obs: list[Observation] = []
    for i, (manifest, initial_state, changes, question) in enumerate(trials):
        approx_remaining = max(0, int(total_budget - i * budget_rate_approx))
        observed_at = float(question["metadata"].get(
            "observed_at", float(question["metadata"]["present_time"]) - 1.0
        ))
        obs = make_observation(
            question, manifest, initial_state, changes,
            observed_at=observed_at,
            remaining_budget=approx_remaining,
            with_prior=with_prior,
            questions_remaining=n - i,
        )
        initial_obs.append(obs)

    print(f"  Phase 1: batch LLM call ({n} prompts) …", flush=True)
    decisions_1 = agent.batch_act(initial_obs)

    # Assign resense tokens in question order (first-come, first-served)
    budget_remaining = total_budget
    got_resense: list[bool] = []
    for d in decisions_1:
        if d.kind == DecisionKind.RESENSE and budget_remaining > 0:
            got_resense.append(True)
            budget_remaining -= 1
        else:
            got_resense.append(False)
    n_resense = sum(got_resense)
    print(f"  {n_resense} resense requests granted (budget={total_budget}).", flush=True)

    # Build fresh observations for resense-granted questions
    resense_indices: list[int] = []
    resense_obs:     list[Observation] = []
    for i, (manifest, initial_state, changes, question) in enumerate(trials):
        if not got_resense[i]:
            continue
        qt = float(question["metadata"]["present_time"])
        obs = make_observation(
            question, manifest, initial_state, changes,
            observed_at=qt,
            remaining_budget=0,
            with_prior=with_prior,
            questions_remaining=1,
        )
        resense_indices.append(i)
        resense_obs.append(obs)

    decisions_2: dict[int, Decision] = {}
    if resense_obs:
        print(f"  Phase 2: batch LLM call ({len(resense_obs)} resense prompts) …", flush=True)
        for idx, d in zip(resense_indices, agent.batch_act(resense_obs)):
            decisions_2[idx] = d

    # Assemble results
    metrics = EvalMetrics()
    for i, (manifest, initial_state, changes, question) in enumerate(trials):
        meta        = question["metadata"]
        query_time  = float(meta["present_time"])
        observed_at = float(meta.get("observed_at", query_time - 1.0))
        rgn         = _region(meta.get("target_slot"), meta["object_category"])

        if got_resense[i]:
            final_decision = decisions_2[i]
            obs_used       = resense_obs[resense_indices.index(i)]
            resense_count  = 1
        else:
            final_decision = decisions_1[i]
            obs_used       = initial_obs[i]
            resense_count  = 0

        if final_decision.kind != DecisionKind.ANSWER:
            final_decision = Decision(
                kind=DecisionKind.ANSWER,
                option_index=obs_used.observed_option_index,
                confidence=0.0,
            )

        correct = (final_decision.option_index == question["correct_index"])
        metrics.n_trials       += 1
        metrics.n_correct      += int(correct)
        metrics.total_resenses += resense_count
        metrics.results.append(TrialResult(
            prompt=question["prompt"],
            query_type=meta["query_type"],
            difficulty=meta.get("difficulty_bin", ""),
            region=rgn,
            correct=correct,
            option_index=final_decision.option_index or 0,
            correct_index=question["correct_index"],
            confidence=final_decision.confidence or 0.0,
            resense_count=resense_count,
            delta=query_time - observed_at,
            low_dynamic=meta.get("low_dynamic", False),
        ))

    return metrics
