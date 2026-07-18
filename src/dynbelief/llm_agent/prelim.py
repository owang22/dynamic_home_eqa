"""LLM-agent episodes, v2 — RECEPTACLE granularity, varied observation/query
times, calendar-aware prompts.

Changes from v1 (design review):
  - Answers are room.receptacle labels (e.g. kitchen.table_1), not rooms:
    within-room moves (kitchen.counter_tucked -> kitchen.table_1) now count.
    ELSEWHERE stays its own answer category. Room-level correctness is
    logged as a secondary metric.
  - t_snap is no longer pinned to 08:00: banks sample (t_snap, t_query)
    pairs across days and times of day (incl. cross-day overnight gaps), so
    absolute time and elapsed time both vary.
  - Prompts carry calendar context (day-of-week + clock for last-seen and
    now) and instruct the agent to reason about the household activities
    occurring in the gap (meals, work/school, tidying, evenings, weekends)
    and how they move objects.

One decision per episode: answer from memory (with confidence) or resense
the target (pays a look; returns the true receptacle). `answer` is required
either way (counterfactual scoring).
"""
from __future__ import annotations

import json

from dynamic_home_eqa import rooms as _rooms
from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs.base import object_class

ELSEWHERE = "elsewhere"
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
         "Sunday"]


def _when(t_min: int) -> str:
    """Calendar-aware clock: 'Wednesday 08:00' (day 0 = Monday, the
    generator's calendar)."""
    d = (t_min // MIN_PER_DAY) % 7
    return f"{_DAYS[d]} {(t_min % MIN_PER_DAY) // 60:02d}:{t_min % 60:02d}"


def receptacle_options(world) -> list[str]:
    """All receptacle labels + ELSEWHERE — the full closed answer/sense set."""
    labels = sorted(world.recep_label[r]
                    for r in world.receptacles(include_elsewhere=False))
    return labels + [ELSEWHERE]


def true_receptacle(world, obj: int, t: int) -> str:
    pid = world.true_parent(obj, t)
    return ELSEWHERE if pid == ELSEWHERE_ID else world.recep_label[pid]


def room_of_label(world, label: str) -> str:
    if label == ELSEWHERE:
        return ELSEWHERE
    for rid, lbl in world.recep_label.items():
        if lbl == label:
            return world.room_of(rid) or ELSEWHERE
    return ELSEWHERE


def memory_table(world, t_snap: int, show_times: bool,
                 omit_obj: int | None = None) -> str:
    lines = []
    stamp = f" (last seen {_when(t_snap)})" if show_times else ""
    for obj in sorted(world.objects(), key=lambda o: world.obj_label[o]):
        if obj == omit_obj:
            continue
        rec = true_receptacle(world, obj, t_snap)
        loc = "not in any room (away/put away)" if rec == ELSEWHERE else rec
        lines.append(f"- {world.obj_label[obj]}: {loc}{stamp}")
    return "\n".join(lines)


def build_prompt(world, obj, t_snap, t_query, variant: str, household_desc: str):
    label = world.obj_label[obj]
    options = receptacle_options(world)
    props = {
        "reason": {"type": "string", "maxLength": 300},
        "action": {"type": "string",
                   "enum": (["answer"] if variant == "A0"
                            else ["answer", "resense"])},
        "answer": {"type": "string", "enum": options},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    }
    req = ["reason", "action", "answer", "confidence"]
    if variant == "A3":
        props = {"reason": props["reason"],
                 "est_p_moved": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                 **{k: props[k] for k in ("action", "answer", "confidence")}}
        req = ["reason", "est_p_moved", "action", "answer", "confidence"]
    schema = {"type": "object", "additionalProperties": False,
              "required": req, "properties": props}

    base = (
        "You are a household robot's decision module. Answer location "
        "questions about objects, at the level of the exact spot: answers "
        "are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first "
        "counter in the kitchen; a *_tucked label is the tucked-in position "
        "at that furniture). 'elsewhere' means the object is in no listed "
        "spot (taken out of the house, or put away out of sight). "
        "Residents move objects as they live their day: think about which "
        "household activities plausibly happened in the relevant time span "
        "— meals, work or school hours, tidying, evening wind-down, weekend "
        "rhythms — and how those activities move objects of this kind. ")
    if variant == "A0":
        system = base + "You have no memory of this house; use general knowledge only."
    elif variant in ("A1", "A2", "A2x"):
        system = base + (
            "You have a memory of past observations. Either ANSWER from "
            "memory (action='answer') or RESENSE the object "
            "(action='resense') — resensing costs one look from a limited "
            "daily sensing budget and returns the object's true current "
            "location. Either way, fill 'answer' with your best guess of "
            "the CURRENT location.")
    elif variant == "A3":
        system = base + (
            "You have a memory of past observations, possibly stale. Work "
            "step by step: (1) from the object's kind, when it was last "
            "seen, the current time, and the household activities likely to "
            "have occurred in between, estimate est_p_moved — the "
            "probability it is no longer at the remembered spot; (2) if "
            "est_p_moved is high enough that a wrong answer is likely, "
            "RESENSE (costs 1 of 5 remaining looks today, 10 questions "
            "today); otherwise ANSWER from memory; (3) fill 'answer' with "
            "your best guess either way and calibrate 'confidence'.")
    else:
        raise ValueError(variant)

    parts = [f"Household: {household_desc}"]
    if variant != "A0":
        show_times = variant in ("A2", "A2x", "A3")
        omit = obj if variant == "A2x" else None
        parts.append("Your memory of the house:\n"
                     + memory_table(world, t_snap, show_times, omit_obj=omit))
        if show_times:
            parts.append(f"Current time: {_when(t_query)}")
    parts.append(f"Question: where is {label} right now? Answer with one of "
                 f"the location labels, or 'elsewhere'.")
    return system, "\n\n".join(parts), schema


def run_episode(client, world, obj, t_snap, t_query, variant, household_desc,
                seed):
    system, user, schema = build_prompt(world, obj, t_snap, t_query, variant,
                                        household_desc)
    raw = client.generate(system, user, schema, seed=seed, temperature=0.2)
    r = json.loads(raw)
    r.setdefault("est_p_moved", None)
    true_rec = true_receptacle(world, obj, t_query)
    snap_rec = true_receptacle(world, obj, t_snap)
    true_room = room_of_label(world, true_rec)
    ans_room = room_of_label(world, r["answer"])
    return {
        "variant": variant, "obj": obj, "label": world.obj_label[obj],
        "cls": object_class(world.obj_label[obj]),
        "t_snap": t_snap, "t_query": t_query,
        "dt_min": t_query - t_snap,
        "snap_dow": (t_snap // MIN_PER_DAY) % 7,
        "query_dow": (t_query // MIN_PER_DAY) % 7,
        "action": r["action"], "answer": r["answer"],
        "est_p_moved": r["est_p_moved"],
        "confidence": float(r["confidence"]), "reason": r["reason"],
        "true_answer": true_rec,
        "answer_correct": int(r["answer"] == true_rec),
        "room_correct": int(ans_room == true_room
                            or (ans_room != ELSEWHERE and true_room != ELSEWHERE
                                and _rooms.rooms_match(ans_room, true_room))),
        "moved_since_snap": int(true_rec != snap_rec),
        "memory_rec": snap_rec,
        "prompt_full": system + "\n\n---\n\n" + user,
        "raw_response": raw,
    }
