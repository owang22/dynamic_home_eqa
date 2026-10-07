"""Day-budget active probe: the per-episode machinery wrapped in a DAY LOOP
with a SHARED sensing budget B (day-budget brief, Sections 1-4).

Why: under per-episode budgets, look savings expire at episode end. Under a
shared daily budget they carry forward — looks not spent on the stable chair
at 10am remain available for the displaced mug at 6pm — so look-efficiency
(the one robust per-episode win, F2) becomes causally upstream of day-level
accuracy. The drain mechanism: truly-elsewhere queries cost an exhaustive
checklist its full support every time, while predictive abstention answers
them in ~1 look; predictive abstention is the ENGINE of the day-budget result
(tested directly by the P4 ablation).

Mechanics:
  - A day starts with a full wake-up snapshot observation (all objects), so
    early queries are answerable; within the day, an object's last-seen is
    whatever earlier sensing or that snapshot provided (t_seen is NOT
    injected).
  - Queries arrive sequentially at scheduled times; every SENSE decrements
    the shared B_remaining; at 0 the policy must answer from belief (forced
    answer_now) for the rest of the day.
  - A PRESENT sense result feeds the belief as a real observation (finding
    the object in a room reveals where it sits). ABSENT results are
    time-local: they condition the current query via episode memory but are
    not persisted across queries (a negative at 10am says nothing binding
    about 6pm).
  - Days are independent (budget does not roll over); the belief's learned
    routine parameters persist across days (reset() contract), matching the
    ambient-stream learning convention.
"""
from __future__ import annotations

import copy
import math

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.active.policies import _absent, voi_step
from dynbelief.active.room_belief import (ELSEWHERE, condition_absent,
                                          room_belief, sensable_rooms,
                                          true_room_at)


# ── schedule generation (Section 4: policy-independent, paired, cold) ───────

def make_schedule(world, day, targets, stratum_of, seed, q_per_day=10,
                  frac_transition=0.6):
    """Q queries for one day: stratified targets (stable share preserved —
    stable objects are what a good allocator SKIPS, so they are load-bearing),
    ~60% of times transition-adjacent (5-90 min after a routine transition
    that day), rest uniform. Fixed before any policy runs; identical across
    policies within a seed."""
    rng = np.random.default_rng(seed * 100003 + day)
    day0 = day * MIN_PER_DAY
    # stratified target draw, proportional to the pool mix
    strata = ("static", "occasional", "dynamic")
    pools = {s: [o for o in targets if stratum_of[o] == s] for s in strata}
    weights = np.array([len(pools[s]) for s in strata], dtype=float)
    weights /= weights.sum()
    picks = []
    for _ in range(q_per_day):
        s = rng.choice(len(strata), p=weights)
        picks.append(rng.choice(pools[strata[s]]))
    # times: transition-adjacent (after a real human event this day) vs uniform
    trans = sorted(t % MIN_PER_DAY for t in world.change_times()
                   if t // MIN_PER_DAY == day)
    times = []
    for _ in range(q_per_day):
        if trans and rng.random() < frac_transition:
            base = trans[rng.integers(len(trans))]
            t = base + rng.integers(5, 91)
        else:
            t = rng.integers(7 * 60, 23 * 60)
        times.append(day0 + min(int(t), MIN_PER_DAY - 1))
    order = np.argsort(times)
    return [(int(times[i]), int(picks[i])) for i in order]


# ── day policies: one family (order-by-belief), differing in stopping ───────
# Interface: policy(world, belief, obj, t_query, memory, ctx) where ctx carries
# {B_remaining, q_index, Q, per_query_cap}. Return ("ANSWER", lbl)|("SENSE", room).

_SUPPORT_EPS = 1e-3   # unsensed room mass below this = support exhausted


def _residual_answer(world, belief, obj, t_query, memory):
    p = condition_absent(room_belief(world, belief, obj, t_query), _absent(memory))
    return max(p, key=p.get)


def day_answer_now(world, belief, obj, t_query, memory, ctx):
    return ("ANSWER", _residual_answer(world, belief, obj, t_query, memory))


def make_day_checklist(per_query_cap=None):
    """greedy_checklist (cap=None): sense belief-ranked until PRESENT, support
    exhausted, or the shared budget runs dry — first-come-first-served, no
    rationing (the strawman drain). rationed_checklist (cap=floor(B/Q)): the
    FAIR exhaustive baseline — uniform rationing; the claim only has teeth
    against this one."""
    def policy(world, belief, obj, t_query, memory, ctx):
        p0 = room_belief(world, belief, obj, t_query)
        unsensed = [r for r in sensable_rooms(world) if r not in memory]
        cap = ctx["per_query_cap"] if per_query_cap == "ration" else None
        if cap is not None and len(memory) >= cap:
            return ("ANSWER", _residual_answer(world, belief, obj, t_query, memory))
        if not unsensed or sum(p0[r] for r in unsensed) < _SUPPORT_EPS:
            return ("ANSWER", _residual_answer(world, belief, obj, t_query, memory))
        return ("SENSE", max(unsensed, key=lambda r: p0[r]))
    return policy


def make_day_voi_fixed(cost):
    def policy(world, belief, obj, t_query, memory, ctx):
        return voi_step(world, belief, obj, t_query, memory, cost)
    return policy


def make_day_voi_adaptive(c0=0.05, e_looks=1.0):
    """Shadow-price heuristic (NOT RL): the price of a look rises as budget
    depletes relative to remaining demand, falls as savings accumulate.
      c_t = c0 * (queries_remaining * E[looks]) / max(B_remaining, 1)
    With B_remaining == queries_remaining * E[looks] the price is exactly c0;
    spend faster and looks get more expensive."""
    def policy(world, belief, obj, t_query, memory, ctx):
        q_rem = max(1, ctx["Q"] - ctx["q_index"])
        c_t = c0 * (q_rem * e_looks) / max(ctx["B_remaining"], 1)
        return voi_step(world, belief, obj, t_query, memory, c_t)
    return policy


def make_day_oracle(alloc):
    """oracle_allocator: per-day headroom upper bound. `alloc` maps
    q_index -> look cap, precomputed from true difficulties (see
    oracle_allocation)."""
    def policy(world, belief, obj, t_query, memory, ctx):
        cap = alloc.get(ctx["q_index"], 0)
        p0 = room_belief(world, belief, obj, t_query)
        unsensed = [r for r in sensable_rooms(world) if r not in memory]
        if len(memory) >= cap or not unsensed or \
                sum(p0[r] for r in unsensed) < _SUPPORT_EPS:
            return ("ANSWER", _residual_answer(world, belief, obj, t_query, memory))
        return ("SENSE", max(unsensed, key=lambda r: p0[r]))
    return policy


def oracle_allocation(world, belief, schedule, B):
    """Greedy marginal-value allocation knowing each query's true difficulty:
    looks-to-find = rank of the true room in the belief order at query time
    (∞ for truly-elsewhere → allocate 0, answer from belief). Value ratio =
    (1 - answer_now_correct) / looks_to_find; allocate whole queries by
    descending ratio until B runs out. A heuristic upper bound (belief state
    approximated by the snapshot-fed belief, ignoring cross-query coupling)."""
    cands = []
    for qi, (tq, obj) in enumerate(schedule):
        belief.objects = [obj]
        p = room_belief(world, belief, obj, tq)
        true_r = true_room_at(world, obj, tq)
        top = max(p, key=p.get)
        acc_now = 1.0 if top == true_r else 0.0
        if true_r == ELSEWHERE:
            continue                      # unfindable: 0 looks, answer from belief
        order = sorted(sensable_rooms(world), key=lambda r: -p[r])
        ltf = order.index(true_r) + 1
        gain = 1.0 - acc_now
        if gain > 0:
            cands.append((gain / ltf, qi, ltf))
    alloc: dict[int, int] = {}
    rem = B
    for ratio, qi, ltf in sorted(cands, reverse=True):
        if ltf <= rem:
            alloc[qi] = ltf
            rem -= ltf
    return alloc


# ── the day runner ───────────────────────────────────────────────────────────

def run_day(world, belief, day, schedule, policy, B) -> list[dict]:
    """Run one day's Q queries sequentially under shared budget B. Returns
    per-query log rows (Section 2)."""
    day0 = day * MIN_PER_DAY
    belief.reset(world.objects(), world.receptacles(), day0)
    belief.observe(day0, world.state_at(day0))          # wake-up snapshot
    last_obs = {o: day0 for o in world.objects()}
    B_rem = B
    Q = len(schedule)
    rows = []
    for qi, (tq, obj) in enumerate(schedule):
        belief.objects = [obj]                           # scope prediction reads
        memory: dict[str, str] = {}
        true_ans = true_room_at(world, obj, tq)
        forced = B_rem <= 0
        looks = 0
        ctx = {"B_remaining": B_rem, "q_index": qi, "Q": Q,
               "per_query_cap": max(0, B // Q)}
        while True:
            ctx["B_remaining"] = B_rem
            if B_rem <= 0:
                final = _residual_answer(world, belief, obj, tq, memory)
                break
            act, label = policy(world, belief, obj, tq, memory, ctx)
            if act == "ANSWER":
                final = label
                break
            if label in memory:                          # spent look is spent
                final = _residual_answer(world, belief, obj, tq, memory)
                break
            present = (true_ans != ELSEWHERE and true_ans == label)
            memory[label] = "PRESENT" if present else "ABSENT"
            B_rem -= 1
            looks += 1
            if present:
                final = label
                belief.observe(tq, {obj: (world.true_parent(obj, tq), {})})
                last_obs[obj] = tq
                break
        rows.append({
            "q_index": qi, "t_query": tq, "obj": obj, "day": day,
            "true_answer": true_ans, "is_elsewhere": int(true_ans == ELSEWHERE),
            "final_answer": final, "correct": int(final == true_ans),
            "answered_elsewhere": int(final == ELSEWHERE),
            "looks_spent": looks, "B_remaining_after": B_rem,
            "was_forced_answer_now": int(forced),
            "staleness_min": tq - last_obs.get(obj, day0),
            "n_rooms": len(sensable_rooms(world)),
        })
    return rows
