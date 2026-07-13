"""
QuestionSpec and MCQ builder for Dynamic EQA.

Answer keys come solely from replaying the Change log via env.replay.state_at()
(standalone mode) or from WorldGraph snapshots (PARTNR-integrated mode).
The LLM never determines a correct answer.

Two execution paths:
  Standalone  — uses SceneState + Change list (no Habitat-sim required).
  WorldGraph  — uses (timestamp, WorldGraph) snapshot list; adapter converts
                to SceneState on the fly.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from ..env.deltas import Change, SLOT_ANCHORS, slot_desc, SLOT_DESCRIPTIONS
from ..env.replay import state_at
from ..env.state import SceneState
from .templates import render_question


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class QueryType(str, Enum):
    PRESENCE = "presence"
    LOCATION = "location"
    COUNT    = "count"


@dataclass
class QuestionSpec:
    query_type:      QueryType
    t:               float           # query time (absolute 24h clock)
    object_category: str
    instance_id:     Optional[str]
    target_slot:     Optional[str]
    observed_at:     float = 0.0     # when robot last observed; elapsed = t - observed_at
    difficulty_bin:  str   = ""      # set by difficulty.assign_difficulty_bins()


@dataclass
class MCQuestion:
    spec:          QuestionSpec
    prompt:        str
    options:       list[str]
    correct_index: int
    metadata:      dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def _derive_seed(household_id: str, day: int, *parts: str) -> int:
    key    = f"{household_id}:{day}:{':'.join(parts)}"
    digest = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(digest[:8], "little")


# ---------------------------------------------------------------------------
# MCQ builder
# ---------------------------------------------------------------------------

def build_mcq(
    spec: QuestionSpec,
    initial_state: SceneState,
    changes: list[Change],
    household_id: str,
    day: int,
) -> MCQuestion:
    """Build one MCQuestion.  Correct answer derived from state_at(), never LLM."""
    from .difficulty import staleness_score, zone_churn_score

    state   = state_at(initial_state, changes, spec.t)
    correct = _extract_answer(spec, state)

    distractors, low_dynamic = _generate_distractors(spec, correct, initial_state, changes)

    all_opts = [correct] + distractors
    shuf_seed = _derive_seed(
        household_id, day, spec.query_type.value,
        f"{spec.t:.3f}", str(spec.instance_id or ""),
        str(spec.target_slot or ""), "shuffle",
    )
    rng   = np.random.default_rng(shuf_seed)
    order = rng.permutation(len(all_opts)).tolist()
    options       = [all_opts[i] for i in order]
    correct_index = order.index(0)

    prompt = render_question(spec.query_type.value, spec.object_category, spec.target_slot)

    stale = staleness_score(spec, changes)
    churn = zone_churn_score(spec, changes)
    metadata = {
        "present_time":     round(spec.t, 3),
        "observed_at":      round(spec.observed_at, 3),
        "elapsed":          round(spec.t - spec.observed_at, 3),
        "staleness":        round(stale, 3),
        "zone_churn":       churn,
        "difficulty_score": round(stale * churn, 3),
        "difficulty_bin":   spec.difficulty_bin,
        "query_type":       spec.query_type.value,
        "object_category":  spec.object_category,
        "instance_id":      spec.instance_id,
        "target_slot":      spec.target_slot,
        "day":              day,
        "household_id":     household_id,
        "low_dynamic":      low_dynamic,
    }
    return MCQuestion(
        spec=spec, prompt=prompt, options=options,
        correct_index=correct_index, metadata=metadata,
    )


# ---------------------------------------------------------------------------
# Answer extraction
# ---------------------------------------------------------------------------

def _extract_answer(spec: QuestionSpec, state: SceneState) -> str:
    if spec.query_type == QueryType.PRESENCE:
        present = any(
            inst.category == spec.object_category and inst.current_semantic == spec.target_slot
            for inst in state.instances.values()
        )
        return "Yes" if present else "No"

    if spec.query_type == QueryType.LOCATION:
        inst = state.instances.get(spec.instance_id or "")
        return slot_desc(inst.current_semantic) if inst else "not present"

    if spec.query_type == QueryType.COUNT:
        n = sum(
            1 for inst in state.instances.values()
            if inst.category == spec.object_category and inst.current_semantic == spec.target_slot
        )
        return str(n)

    return "?"


# ---------------------------------------------------------------------------
# Distractor generation
# ---------------------------------------------------------------------------

def _generate_distractors(
    spec: QuestionSpec,
    correct: str,
    initial_state: SceneState,
    changes: list[Change],
) -> tuple[list[str], bool]:
    if spec.query_type == QueryType.PRESENCE:
        return (["No" if correct == "Yes" else "Yes"], False)
    if spec.query_type == QueryType.LOCATION:
        return _location_distractors(spec, correct, initial_state, changes)
    if spec.query_type == QueryType.COUNT:
        return _count_distractors(spec, correct, initial_state, changes)
    return ([], False)


def _location_distractors(
    spec: QuestionSpec,
    correct: str,
    initial_state: SceneState,
    changes: list[Change],
) -> tuple[list[str], bool]:
    candidate_times = sorted({0.0} | {c.t for c in changes})
    distractors: list[str] = []
    for t in candidate_times:
        s    = state_at(initial_state, changes, t)
        inst = s.instances.get(spec.instance_id or "")
        ans  = slot_desc(inst.current_semantic) if inst else "not present"
        if ans != correct and ans not in distractors:
            distractors.append(ans)
        if len(distractors) >= 3:
            break

    low_dynamic = len(distractors) < 3
    if low_dynamic:
        for slot in SLOT_ANCHORS:
            if spec.object_category in SLOT_ANCHORS[slot]["cats"]:
                cand = slot_desc(slot)
                if cand != correct and cand not in distractors:
                    distractors.append(cand)
            if len(distractors) >= 3:
                break

    if len(distractors) < 1:
        distractors.append("not present")
    if len(distractors) < 2:
        for sd in SLOT_DESCRIPTIONS.values():
            if sd != correct and sd not in distractors:
                distractors.append(sd)
                break
    if len(distractors) < 3:
        distractors.append("not present" if "not present" not in distractors else "somewhere else")

    return distractors[:3], low_dynamic


def _count_distractors(
    spec: QuestionSpec,
    correct: str,
    initial_state: SceneState,
    changes: list[Change],
) -> tuple[list[str], bool]:
    correct_n = int(correct)
    candidate_times = sorted({0.0} | {c.t for c in changes})
    distractors: list[str] = []
    for t in candidate_times:
        s = state_at(initial_state, changes, t)
        n = sum(
            1 for inst in s.instances.values()
            if inst.category == spec.object_category and inst.current_semantic == spec.target_slot
        )
        ans = str(n)
        if ans != correct and ans not in distractors:
            distractors.append(ans)
        if len(distractors) >= 3:
            break
    low_dynamic = len(distractors) < 3
    if low_dynamic:
        for delta in [1, -1, 2, 3]:
            ans = str(max(0, correct_n + delta))
            if ans != correct and ans not in distractors:
                distractors.append(ans)
            if len(distractors) >= 3:
                break
    return distractors[:3], low_dynamic


def _dedup(specs: list[QuestionSpec]) -> list[QuestionSpec]:
    seen: set[tuple] = set()
    out:  list[QuestionSpec] = []
    for s in specs:
        key = (s.query_type, round(s.t, 2), s.instance_id, s.target_slot)
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out
