"""
sampling.py — frozen-label sampling rule (navmesh-connectivity phase, D3).

A frozen label set must satisfy two independent correctness properties, not
just "moved at least once in the eval day" (the property FROZEN_LABELS was
originally computed from):

  1. Exists at patrol_start — the M1 gate's 80% abstain rate was half
     explained by 5 of 10 labels not existing yet at patrol_start=6.0 (an
     insert_new event later that day) — current_instances() at patrol time
     silently skipped them, so no policy could ever have sensed them.
  2. Every historical anchor position is geodesically reachable from the
     agent's start pose — the other half of the abstain rate: 4 of the 5
     labels that DID exist sat on navmesh islands the start pose could
     never reach (fixed for the dominant island by the D1 navmesh climb
     fix, but a label could still have moved through a slot on the one
     remaining disqualified fragment on some other day).

Chosen resolution (patrol_start stays fixed at 6.0, not moved later): the
episode's framing is "agent patrols in the morning, is asked questions
later after decay" — moving patrol_start past the last insert_new event
would flatten that structure into "patrol after everything already
happened". Filtering candidates by existence at the fixed patrol_start
preserves the framing at the cost of a smaller eligible label pool.

This is a sampling-correctness rule, not result filtering — it changes
which labels are eligible to be asked about at all, decided once before any
experiment runs, the same way reachability.check_reachability_invariant
rejects a whole scene before any experiment runs.

A third property (D1: kernel generalization) joined these two: every
historical anchor must resolve to a known semantic slot type (rooms.
slot_room), not just be reachable. An anchor rooms.slot_room can't place
in any canonical room would silently drop out of a kernel's room-pooling
step at belief-fitting time with nothing to notice it — the same class of
silent failure the other two properties exist to catch, at the same
qualification-time point rather than downstream.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..rooms import unmapped_slots
from .config import AgentConfig
from .world import EmbodiedWorld


@dataclass
class LabelQualification:
    label: str
    exists_at_patrol_start: bool
    historical_slots: tuple[str, ...]
    unreachable_slots: tuple[str, ...]
    unmapped_slots: tuple[str, ...] = ()

    @property
    def qualifies(self) -> bool:
        return self.exists_at_patrol_start and not self.unreachable_slots and not self.unmapped_slots

    def reason(self) -> str:
        if self.qualifies:
            return "qualifies"
        reasons = []
        if not self.exists_at_patrol_start:
            reasons.append("does not exist at patrol_start")
        if self.unreachable_slots:
            reasons.append(f"unreachable historical slot(s): {', '.join(self.unreachable_slots)}")
        if self.unmapped_slots:
            reasons.append(f"unmapped historical slot(s) (no resolvable room): {', '.join(self.unmapped_slots)}")
        return "; ".join(reasons)


def _all_slots_for_label(label: str, manifests: list[dict]) -> set[str]:
    """Every from_semantic/to_semantic this instance_id has ever occupied
    across the given manifests — both endpoints of a move, since a belief
    could plausibly anchor on either side of it at some point in time."""
    slots: set[str] = set()
    for m in manifests:
        for c in m["changes"]:
            if c["label"] == label:
                # from_semantic is None for an insert_new event (nothing to
                # move from) — not a slot to check reachability for.
                if c["from_semantic"] is not None:
                    slots.add(c["from_semantic"])
                if c["to_semantic"] is not None:
                    slots.add(c["to_semantic"])
    return slots


def candidate_labels(eval_manifest: dict) -> tuple[str, ...]:
    """Every label with at least one change event in the eval day — the
    same "dynamic label" property FROZEN_LABELS was originally computed
    from, before this rule adds the existence/reachability filters."""
    return tuple(sorted({c["label"] for c in eval_manifest["changes"]}))


def qualify_labels(
    scene: str,
    eval_result: dict,
    eval_manifest: dict,
    history_manifests: list[dict],
    patrol_start: float,
    config: Optional[AgentConfig] = None,
) -> list[LabelQualification]:
    """Evaluate every candidate label in eval_manifest against all three
    sampling-correctness properties, using a real EmbodiedWorld so the
    exact navmesh config, anchor filtering, and start-pose selection the
    actual experiment uses is what qualifies the label set — not a
    parallel, potentially-drifted reimplementation of that logic."""
    world = EmbodiedWorld(scene, eval_result, eval_manifest, config=config)
    try:
        world.advance_to(patrol_start)
        existing_at_patrol = set(world.current_instances().keys())

        results = []
        for label in candidate_labels(eval_manifest):
            slots = _all_slots_for_label(label, history_manifests)
            unreachable = []
            for slot in sorted(slots):
                pos = world._resolve_slot_position(label, slot)
                if pos is None:
                    continue  # outdoor/away — outside the sensable volume by construction, not a reachability failure
                if world.geodesic_time(world.pose.position, pos) == float("inf"):
                    unreachable.append(slot)
            results.append(LabelQualification(
                label=label,
                exists_at_patrol_start=label in existing_at_patrol,
                historical_slots=tuple(sorted(slots)),
                unreachable_slots=tuple(unreachable),
                unmapped_slots=tuple(unmapped_slots(slots)),
            ))
        return results
    finally:
        world.close()
