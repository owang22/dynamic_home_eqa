"""Section 2.4 — direct world-knowledge probe.

Ground truth: per-class displacement hazard H_c(dt) = P(an object of class c
is NOT in the same room after dt), estimated over all (t, t+dt) window pairs
on a grid across an episode's days. Displacement (location changed), not
any-transition: it is the quantity a localization agent actually needs, and
the one an LLM can be asked unambiguously.

Elicitation: one guided-JSON call per (household context, class) asking for
the full dt curve at once — a curve per call encourages internally coherent
(monotone-ish) answers and tests the LLM's shape knowledge, not its
call-to-call noise.
"""
from __future__ import annotations

import json

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.beliefs.base import object_class

DT_GRID_MIN = [30, 60, 120, 240, 480, 840]   # 0.5h .. 14h (within-day)


def gt_class_hazards(world, days: list[int], grid_step: int = 30) -> dict:
    """{class: {dt_min: P(room(t+dt) != room(t))}} pooled over instances,
    days, and window starts. Uses room granularity (same lock as everything
    else)."""
    out: dict = {}
    counts: dict = {}
    for obj in world.objects():
        cls = object_class(world.obj_label[obj])
        for day in days:
            d0 = day * MIN_PER_DAY
            for t in range(d0 + 7 * 60, d0 + 22 * 60, grid_step):
                r0 = world.room_of(world.true_parent(obj, t))
                for dt in DT_GRID_MIN:
                    if (t + dt) >= d0 + MIN_PER_DAY:
                        continue
                    r1 = world.room_of(world.true_parent(obj, t + dt))
                    k = (cls, dt)
                    a, n = counts.get(k, (0, 0))
                    counts[k] = (a + (1 if r1 != r0 else 0), n + 1)
    for (cls, dt), (a, n) in counts.items():
        out.setdefault(cls, {})[dt] = a / n if n else float("nan")
    return out


def elicit_class_hazards(client, classes: list[str], household_desc: str,
                         seed: int = 7) -> dict:
    """{class: {dt_min: p}} — the LLM's implied hazard curves."""
    hours = [f"{m/60:g}" for m in DT_GRID_MIN]
    schema = {"type": "object", "additionalProperties": False,
              "required": ["probabilities"],
              "properties": {"probabilities": {
                  "type": "array", "minItems": len(DT_GRID_MIN),
                  "maxItems": len(DT_GRID_MIN),
                  "items": {"type": "number", "minimum": 0.0, "maximum": 1.0}}}}
    system = (
        "You estimate everyday household object dynamics. You will be given an "
        "object class and a household description. Estimate, for each elapsed "
        "time, the probability that a typical object of that class is in a "
        "DIFFERENT ROOM than where it was last seen (moved by the residents "
        "going about their day — not by you). Consider how often such objects "
        "are picked up, used, tidied, or carried. Answer with one probability "
        "per elapsed time, in order.")
    out: dict = {}
    for cls in classes:
        user = (f"Household: {household_desc}\n"
                f"Object class: {cls.replace('_', ' ')}\n"
                f"Elapsed times since last seen (hours): {', '.join(hours)}\n"
                "For each elapsed time, the probability the object is now in a "
                "different room.")
        raw = client.generate(system, user, schema,
                              seed=seed + hash(cls) % 100000, temperature=0.2)
        ps = json.loads(raw)["probabilities"]
        out[cls] = {dt: float(p) for dt, p in zip(DT_GRID_MIN, ps)}
    return out
