"""One active-probe episode: inject a single t_seen observation, then run the
policy's answer-or-sense loop at t_query under a per-scene look budget.

Not embodied: SENSE returns PRESENT/ABSENT ground truth for a room at t_query
(via ReplayWorld), costs one look, and is first-class evidence. The episode is
self-contained from its injected observation — no cross-day belief continuity.
"""
from __future__ import annotations

import math

from dynbelief.active.room_belief import ELSEWHERE, sensable_rooms, true_room_at


def max_looks_for(world) -> int:
    """Per-scene budget = ceil(0.5 * n_rooms), strictly < n_rooms — the core
    tradeoff knob. If the agent could sense every room it would always find the
    object and the predictive belief would never matter."""
    n = len(sensable_rooms(world))
    return max(1, min(n - 1, math.ceil(0.5 * n)))


def run_episode(world, belief, obj, t_seen, t_query, policy,
                distance_weight: float = 0.0) -> dict:
    """Play one episode. Returns the per-episode log row (brief Section 4)."""
    day0 = t_seen - (t_seen % 1440)
    belief.reset(world.objects(), world.receptacles(), day0)
    belief.objects = [obj]                      # scope prediction to the target
    belief.observe(t_seen, {obj: (world.true_parent(obj, t_seen), {})})

    rooms = sensable_rooms(world)
    true_ans = true_room_at(world, obj, t_query)
    budget = max_looks_for(world)
    memory: dict[str, str] = {}
    sense_trace: list = []
    looks, cost = 0, 0.0
    last = world.room_of(world.true_parent(obj, t_seen)) or rooms[0]

    while True:
        act, label = policy(world, belief, obj, t_query, memory)
        if act == "ANSWER":
            final = label
            break
        # SENSE(label): ground-truth room occupancy at t_query
        if label in memory or looks >= budget:
            # policy tried to re-sense or overspend — force an answer from the
            # policy's own answer branch by marking budget exhausted
            from dynbelief.active.policies import answer_now
            # answer under current (unconditioned-by-engine) belief; policies
            # that track memory already fold negatives in themselves
            _, final = _forced_answer(world, belief, obj, t_query, memory)
            break
        present = (true_ans != ELSEWHERE and true_ans == label)
        memory[label] = "PRESENT" if present else "ABSENT"
        sense_trace.append((label, memory[label]))
        step_cost = 1.0 + distance_weight * _room_dist(world, last, label)
        looks += 1
        cost += step_cost
        last = label
        if present:                              # found it — commit immediately
            final = label
            break
        if looks >= budget:                      # budget spent — must answer now
            act2, label2 = policy(world, belief, obj, t_query, memory)
            final = label2 if act2 == "ANSWER" else _forced_answer(
                world, belief, obj, t_query, memory)[1]
            break

    n_trans = len([t for t in world.change_times(obj) if t_seen < t <= t_query])
    return {
        "obj": obj, "t_seen": t_seen, "t_query": t_query,
        "true_answer": true_ans, "is_elsewhere": int(true_ans == ELSEWHERE),
        "final_answer": final, "correct": int(final == true_ans),
        "answered_elsewhere": int(final == ELSEWHERE),
        "looks_spent": looks, "look_cost": round(cost, 3),
        "sense_trace": sense_trace, "n_transitions_in_interval": n_trans,
        "n_rooms": len(rooms), "max_looks": budget,
    }


def _forced_answer(world, belief, obj, t_query, memory):
    from dynbelief.active.room_belief import condition_absent, room_belief
    p = condition_absent(room_belief(world, belief, obj, t_query),
                         {r for r, v in memory.items() if v == "ABSENT"})
    return ("ANSWER", max(p, key=p.get))


def _room_dist(world, a: str, b: str) -> float:
    """Room-distance proxy for the optional distance_weight tie-break cost.
    Cheap ordinal proxy (index gap in the sorted room list) — a real
    scene-graph distance would slot in here; the primary result runs with
    distance_weight=0 so this is unused there."""
    if a == b:
        return 0.0
    rooms = sensable_rooms(world)
    try:
        return abs(rooms.index(a) - rooms.index(b)) / max(1, len(rooms) - 1)
    except ValueError:
        return 1.0
