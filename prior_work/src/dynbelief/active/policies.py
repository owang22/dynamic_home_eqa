"""Action policies. Common interface:

    act(world, belief, obj, t_query, memory) -> ("ANSWER", label) | ("SENSE", room)

`memory` is the episode's sense record: {room: "PRESENT"|"ABSENT"}. The engine
(episode.py) drives the loop, applies SENSE against ground truth, and enforces
max_looks; policies never re-sense a room in `memory` (a spent look is spent).

ONE-FAMILY FRAMING (day-budget brief 0b): with per-object MARGINAL beliefs,
ABSENT-conditioning is zero-out-and-renormalize, which preserves the relative
order of unsensed rooms — so every sensible policy senses in the SAME
belief-ranked order and they differ only in their STOPPING THRESHOLD. The
exhaustive checklist is the threshold->inf endpoint; voi at each cost_per_look
is another point on the same curve; the belief tier picks which curve you are
on. (predictive_search below is the retired proof artifact of the order tie —
identical to the checklist in 810/810 episodes.)
"""
from __future__ import annotations

from dynbelief.active.room_belief import (ELSEWHERE, condition_absent,
                                          room_belief, sensable_rooms)


def _absent(memory) -> set:
    return {r for r, res in memory.items() if res == "ABSENT"}


# ── a. answer_now — pure prediction, zero looks (the passive Stage-1 read) ──
def answer_now(world, belief, obj, t_query, memory):
    p = room_belief(world, belief, obj, t_query)
    return ("ANSWER", max(p, key=p.get))


# ── b. sense_once_then_answer — one look at the top room, then answer ───────
def sense_once(world, belief, obj, t_query, memory):
    p = room_belief(world, belief, obj, t_query)
    if not memory:  # first move: sense the single highest-belief ROOM (not elsewhere)
        rooms = {r: p[r] for r in sensable_rooms(world)}
        return ("SENSE", max(rooms, key=rooms.get))
    # after the one look: PRESENT short-circuits in the engine; here we answer
    q = condition_absent(p, _absent(memory))
    return ("ANSWER", max(q, key=q.get))


# ── c. sense_until_confident — checklist ELIMINATION, no re-prediction ──────
def make_sense_until_confident(confidence: float | None = None):
    """Ranks C by the INITIAL belief and senses down the list to FIND the
    object, treating a negative purely as elimination (cross the room off) — it
    never re-runs the routine model. PRESENT → answer (engine commits); else
    keep sensing the next-highest INITIAL-belief room until budget. Reaches
    ELSEWHERE only by exhausting looks and finding nothing, never by
    prediction. Because it verifies by sensing, it spends a look even on a
    peaked (stable-object) belief — that is the OVER-SENSING the brief wants
    surfaced, the dual of voi's zero-look discrimination. `confidence`
    (default off) optionally lets a near-certain belief skip sensing."""
    def policy(world, belief, obj, t_query, memory):
        p0 = room_belief(world, belief, obj, t_query)          # INITIAL ranking, fixed
        rooms = sensable_rooms(world)
        absent = _absent(memory)
        resid = {r: p0[r] for r in rooms if r not in absent}   # elimination residual
        resid[ELSEWHERE] = p0[ELSEWHERE]
        s = sum(resid.values()) or 1.0
        resid = {k: v / s for k, v in resid.items()}
        top = max(resid, key=resid.get)
        unsensed = [r for r in rooms if r not in memory]
        if not unsensed:                                       # nothing left → answer residual
            return ("ANSWER", top)
        if confidence is not None and top != ELSEWHERE and resid[top] >= confidence:
            return ("ANSWER", top)
        return ("SENSE", max(unsensed, key=lambda r: p0[r]))   # verify next-highest room
    return policy


# ── d. voi_predictive — routine re-prediction + myopic value-of-information ─
def make_voi_predictive(cost_per_look: float = 0.05):
    """Keeps episode memory AND re-runs the predictive belief conditioned on
    every result so far (positives short-circuit in the engine; negatives via
    condition_absent on the tier's own predictive distribution). Myopic VoI:
    answer (a room OR ELSEWHERE) when no single look's expected accuracy gain
    beats its cost; else sense the room with the highest expected gain. On a
    stable object the belief is peaked so every VoI is tiny → it answers with
    zero looks; on a dynamic object mass is spread → it senses. Its routine-
    conditioned elsewhere-mass lets it ANSWER ELSEWHERE without exhaustive
    sensing — which c structurally cannot do."""
    def policy(world, belief, obj, t_query, memory):
        return voi_step(world, belief, obj, t_query, memory, cost_per_look)
    return policy


def voi_step(world, belief, obj, t_query, memory, cost_per_look):
    """One myopic-VoI decision at price `cost_per_look` — shared by voi_fixed
    (constant price) and the day-budget voi_adaptive (shadow price recomputed
    per call)."""
    p = condition_absent(room_belief(world, belief, obj, t_query), _absent(memory))
    acc_now = max(p.values())                       # answer-now accuracy = top mass
    best_room, best_voi = None, 0.0
    for L in sensable_rooms(world):
        if L in memory:
            continue
        pL = p[L]
        # ABSENT branch: zero L, renormalize, answer residual argmax
        resid = condition_absent(p, {L})
        acc_absent = max(resid.values())
        e_acc = pL * 1.0 + (1.0 - pL) * acc_absent   # PRESENT→answer L (correct)
        voi = e_acc - acc_now
        if voi > best_voi:
            best_voi, best_room = voi, L
    if best_room is None or best_voi <= cost_per_look:
        return ("ANSWER", max(p, key=p.get))         # a room OR elsewhere
    return ("SENSE", best_room)


def make_predictive_search():
    """2x2 control (Oliver's redesign): sense-until-found like the checklist,
    but ORDER sensing by the RE-PREDICTED (negatively-conditioned) belief
    rather than the fixed initial ranking. Isolates search ORDERING at
    identical stopping. NOTE: for a single object with fixed t_query and hard
    presence sensing, Bayesian conditioning on ABSENT is zero-out+renormalize,
    which preserves the relative order of the remaining rooms — so this is
    EXPECTED to tie the checklist. Running it makes that tie (or its absence)
    an empirical result rather than an assertion."""
    def policy(world, belief, obj, t_query, memory):
        p = condition_absent(room_belief(world, belief, obj, t_query), _absent(memory))
        unsensed = [r for r in sensable_rooms(world) if r not in memory]
        if not unsensed:
            return ("ANSWER", max(p, key=p.get))
        return ("SENSE", max(unsensed, key=lambda r: p[r]))
    return policy


POLICIES = {
    "answer_now": answer_now,
    "sense_once": sense_once,
    "sense_until_confident": make_sense_until_confident(),
    "voi_predictive": make_voi_predictive(),
    # predictive_search deliberately NOT registered: provably identical to
    # sense_until_confident (F1 proof artifact — see make_predictive_search).
}
