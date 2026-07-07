"""
State replay for the HSSD day generator.

generate_day() returns a Change log with per-change timestamps but only the
final SceneState.  Questions need state at arbitrary T, so state_at() replays
the change log forward from the day's initial snapshot.
"""
from __future__ import annotations

import copy
from typing import Optional

from .deltas import Change
from .inventory import load_scene_state
from .state import SceneState, ObjectInstance


def state_at(
    initial_state: SceneState,
    changes: list[Change],
    t: float,
) -> SceneState:
    """Reconstruct scene state at time t.

    Applies every committed change with timestamp <= t to a deep copy of the
    day's initial state, in timestamp order.  The initial state must be the
    snapshot captured at the start of generate_day() — do not pass the final
    (post-day) state and un-apply changes; snapshot it directly.
    """
    state = copy.deepcopy(initial_state)
    for c in sorted(changes, key=lambda x: x.t):
        if c.t > t:
            break
        if c.change_type == "move_existing":
            inst = state.instances.get(c.instance_id)
            if inst is not None:
                inst.current_semantic = c.to_semantic
                inst.last_moved_at    = c.t
        elif c.change_type == "insert_new":
            state.instances[c.instance_id] = ObjectInstance(
                instance_id=c.instance_id,
                category=c.object_category,
                current_semantic=c.to_semantic,
                last_moved_at=c.t,
            )
        elif c.change_type == "remove":
            state.instances.pop(c.instance_id, None)
        elif c.change_type == "state_change":
            inst = state.instances.get(c.instance_id)
            if inst is not None:
                inst.states[c.state_variable] = c.to_state
    return state


def initial_state_and_changes_from_manifest(manifest: dict) -> tuple[SceneState, list[Change]]:
    """Build (t=0 SceneState, Change list) from a manifest.json dict.

    Shared by every manifest consumer (qa/gen_questions.py, agents/harness.py,
    the embodied-agent world) so the manifest -> replay-state conversion has
    one implementation, not three copies that could quietly drift apart.

    For each move_existing change belonging to a real-instance-backed label
    (see generation/manifest.py's insert-once contract: such a label's
    every event, including its first, is move_existing), the FIRST
    occurrence sets the object's starting semantic slot — correcting the
    HSSD inventory default load_scene_state() guesses from category alone.

    Labels that have an insert_new event anywhere in `changes` are volatile
    (Tier 3, no real starting instance — insert-once guarantees their
    genuine first-ever event is insert_new) and must NOT be seeded into the
    t=0 state at all: they don't exist until that event fires, and
    state_at() already creates them at exactly that moment during replay.
    Seeding them here from a *later* move_existing event's from_semantic
    would make them appear to exist before their insert_new event — the
    same "object exists before anyone created it" bug the insert-once
    invariant exists to rule out.

    Operates on a deep copy of load_scene_state()'s result: that function is
    lru_cache'd per scene_id, so mutating its returned SceneState in place
    would corrupt the shared cached object for every other caller reusing
    the same scene_id (every subsequent manifest for that scene, in the
    same process, silently inheriting a prior call's per-label mutations).
    """
    import copy as _copy

    state = _copy.deepcopy(load_scene_state(manifest["scene_id"]))
    volatile_labels = {
        entry["label"] for entry in manifest.get("changes", [])
        if entry["change_type"] == "insert_new"
    }
    initialized: set[str] = set()

    for entry in manifest.get("changes", []):
        if entry["change_type"] != "move_existing":
            continue
        label = entry["label"]
        if label in initialized or label in volatile_labels:
            continue
        initialized.add(label)
        from_sem = entry.get("from_semantic") or ""
        if label in state.instances:
            state.instances[label].current_semantic = from_sem
        else:
            state.instances[label] = ObjectInstance(
                instance_id=label, category=entry["object_category"], current_semantic=from_sem,
            )

    profile = manifest.get("resident_profile", "manifest")
    changes = [
        Change(
            activity=profile, phase="enter",
            instance_id=entry["label"],
            change_type=entry["change_type"],
            object_category=entry["object_category"],
            from_semantic=entry.get("from_semantic") or "",
            to_semantic=entry.get("to_semantic") or "",
            reason=entry.get("reason", ""),
            t=float(entry["t"]),
            state_variable=entry.get("state_variable"),
            from_state=entry.get("from_state"),
            to_state=entry.get("to_state"),
        )
        for entry in manifest.get("changes", [])
    ]
    return state, changes


def last_observation_before(
    changes: list[Change],
    instance_id: str,
    t: float,
) -> Optional[float]:
    """Timestamp of the most recent change to instance_id strictly before t.

    Returns None if the instance never changed before t.  Used for the
    'staleness' difficulty axis — distinct from 'time since the agent last
    observed', which the harness owns.
    """
    relevant = [c.t for c in changes if c.instance_id == instance_id and c.t < t]
    return max(relevant) if relevant else None
