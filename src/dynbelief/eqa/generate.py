"""Stage 1.1 — MCQ question generator.

Questions are generated from ground-truth logs and keep BOTH a structured
form (ids, times) and an NL string. Format: 4 options, exactly one correct,
scored by exact match on the chosen option index.

Types (per brief; `usual` and `state_now` were removed from scope):
  location_now  "Which receptacle is {obj} in right now?"  true parent @ t_query
  room_now      "Which room is {obj} in right now?"        true room @ t_query
  count_now     "How many {class} are in {room} right now?" (secondary — a
                single t_seen does not parameterize it cleanly; kept out of
                the primary probe sweep)

Distractor policy (brief): wrong options must exist in THIS house and be
plausible — preferred pool is (a) receptacles/rooms where the object has
actually been at other times in the episode, then (b) same-room receptacles
as the true answer, then (c) any other house receptacle/room. The point is
that the question requires CURRENT knowledge; commonsense elimination must
not solve it.

Index balancing: the correct option's position is drawn from a seeded RNG
per qid, giving a uniform position distribution across a question set —
validate_question_set() checks presence-of-truth and index balance.
"""
from __future__ import annotations

import random

from dynbelief import ELSEWHERE_ID


def _nl_label(world, receptacle_id: int) -> str:
    lbl = world.recep_label[receptacle_id]
    return "somewhere else / put away" if receptacle_id == ELSEWHERE_ID else lbl.replace(".", " ").replace("_", " ")


def _historical_parents(world, obj: int, exclude_t: int | None = None) -> list[int]:
    seen = []
    for e in world.events():
        if e["object_id"] == obj and e["parent_id"] not in seen:
            seen.append(e["parent_id"])
    for snap_day in range(world.n_days):
        p = world.true_parent(obj, snap_day * 1440)
        if p not in seen:
            seen.append(p)
    return seen


def _pick_distractors(rng: random.Random, true_answer, preferred: list, pool: list,
                      n: int = 3) -> list:
    """n distinct wrong options: preferred first (shuffled), then pool."""
    out = []
    for cand_list in (preferred, pool):
        cands = [c for c in cand_list if c != true_answer and c not in out]
        rng.shuffle(cands)
        for c in cands:
            if len(out) >= n:
                break
            if c not in out:  # the preferred list itself can repeat entries
                out.append(c)
    return out[:n]


def make_question(world, qtype: str, target_obj: int, t_seen: int, t_query: int,
                  seed: int = 0, count_class: str | None = None,
                  count_room: str | None = None) -> dict:
    assert t_seen < t_query, "t_last_seen must precede t_query"
    qid = f"{qtype}__obj{target_obj}__s{t_seen}__q{t_query}__seed{seed}"
    rng = random.Random(qid)
    obj_label = world.obj_label.get(target_obj, str(target_obj))

    if qtype == "location_now":
        true_answer = world.true_parent(target_obj, t_query)
        preferred = _historical_parents(world, target_obj)
        true_room = world.room_of(true_answer)
        same_room = [r for r in world.receptacles() if world.room_of(r) == true_room]
        pool = world.receptacles()
        distractors = _pick_distractors(rng, true_answer, preferred + same_room, pool)
        options = distractors
        nl = f"Which receptacle is {obj_label} in right now?"
        nl_opts = None
    elif qtype == "room_now":
        parent = world.true_parent(target_obj, t_query)
        true_answer = world.room_of(parent) or "elsewhere"
        visited = []
        for p in _historical_parents(world, target_obj):
            r = world.room_of(p) or "elsewhere"
            if r not in visited:
                visited.append(r)
        pool = world.rooms() + ["elsewhere"]
        distractors = _pick_distractors(rng, true_answer, visited, pool)
        options = distractors
        nl = f"Which room is {obj_label} in right now?"
        nl_opts = options
    elif qtype == "count_now":
        assert count_class and count_room
        from dynbelief.beliefs.base import object_class
        state = world.state_at(t_query)
        true_answer = sum(
            1 for o, (p, _s) in state.items()
            if object_class(world.obj_label[o]) == count_class
            and world.room_of(p) == count_room)
        # numeric distractors near the truth, distinct, non-negative
        cands = [true_answer + d for d in (-2, -1, 1, 2, 3) if true_answer + d >= 0]
        rng.shuffle(cands)
        distractors = cands[:3]
        options = distractors
        nl = f"How many {count_class} are in {count_room} right now?"
        nl_opts = options
    else:
        raise ValueError(qtype)

    if len(options) < 3:  # tiny houses: pad from anything valid
        extra = [x for x in (world.receptacles() if qtype == "location_now"
                             else list(range(0, 10)))
                 if x != true_answer and x not in options]
        options = (options + extra)[:3]

    answer_index = rng.randrange(4)
    full = list(options[:3])
    full.insert(answer_index, true_answer)

    seen_parent = world.true_parent(target_obj, t_seen)
    if qtype == "location_now":
        nl_opts = [_nl_label(world, o) for o in full]
    elif nl_opts is not None:
        nl_opts = [str(o) for o in full]
    q = {
        "qid": qid, "type": qtype, "target_obj": target_obj,
        "t_query": t_query, "t_last_seen": t_seen, "seen_parent": seen_parent,
        "true_answer": true_answer, "options": full, "answer_index": answer_index,
        "nl": nl + " Options: " + "; ".join(f"{i}) {s}" for i, s in enumerate(nl_opts)),
    }
    if qtype == "count_now":
        q["count_class"] = count_class
        q["count_room"] = count_room
    return q


def validate_question_set(questions: list[dict]) -> dict:
    """Presence-of-truth (hard assert) + index-balance report."""
    counts = [0, 0, 0, 0]
    for q in questions:
        assert q["options"][q["answer_index"]] == q["true_answer"], q["qid"]
        assert len(q["options"]) == 4 and len(set(map(str, q["options"]))) == 4, q["qid"]
        counts[q["answer_index"]] += 1
    n = max(1, len(questions))
    balance = [c / n for c in counts]
    return {"n": len(questions), "index_counts": counts, "index_balance": balance,
            "max_index_skew": max(balance) - min(balance)}
