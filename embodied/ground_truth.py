"""
ground_truth.py — the ONLY module allowed to answer "where is this label
really, right now, independent of what the agent believes".

Scoring code (QuestionEpisodeRunner) imports this to grade an Answer at
report time. EmbodiedWorld, BeliefStore, and every DecisionPolicy must NOT
import it — an agent that could read true state would trivially "solve" the
resense-vs-answer-from-memory decision this whole phase exists to study.
tests/test_embodied_layout.py enforces this by inspecting the import graph
of world.py/sensor.py/belief.py/policy.py, not just by convention.
"""
from __future__ import annotations

from typing import Optional

from ..env.deltas import Change
from ..env.replay import state_at
from ..env.state import SceneState


def true_anchor(
    label: str,
    t: float,
    initial_state: SceneState,
    changes: list[Change],
) -> Optional[str]:
    """The label's real current_semantic slot at time t.

    Replays `changes` from `initial_state` up to t (env.replay.state_at) —
    the identical trusted replay the trace-integrity validator and every
    other manifest consumer use, so ground truth here is the same ground
    truth everywhere else in the project, not an independent reimplementation
    that could quietly disagree.

    Returns None if the label does not exist at t (not yet inserted, e.g. a
    volatile/Tier-3 label before its insert_new event has fired).
    """
    state = state_at(initial_state, changes, t)
    inst = state.instances.get(label)
    return inst.current_semantic if inst is not None else None


def true_state(
    label: str,
    variable: str,
    t: float,
    initial_state: SceneState,
    changes: list[Change],
) -> Optional[str]:
    """The label's real current value of `variable` at time t (M3:
    state-change dynamics) — the state-axis counterpart of true_anchor,
    same replay mechanism (env.replay.state_at), same "one ground truth
    everywhere" guarantee.

    Returns None if the label doesn't exist at t, or has no tracked value
    for `variable` (e.g. a category state_rules.py never wired a trigger
    for — see env/deltas.py's STATE_VARIABLES).
    """
    state = state_at(initial_state, changes, t)
    inst = state.instances.get(label)
    return inst.states.get(variable) if inst is not None else None
