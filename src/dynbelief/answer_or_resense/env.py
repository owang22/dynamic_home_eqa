"""Answer-or-Resense environment — calibration under a scarce-sensing loop.

Per query (object o, time t) the arm takes ONE action:
  ANSWER(loc)  -> reward +1 if correct else WRONG (0 or -1, swept)
  RESENSE      -> reward r (0<r<1, swept), consumes 1 of today's budget B, and
                  the TRUE current location is appended to the arm's observation
                  history (its ONLY source of data in scarce mode). Resense
                  replaces answering — no resense-then-answer this round.
  Budget exhausted -> RESENSE unavailable, must answer.

Scarce-sensing (primary): the arm starts with ZERO observations; everything it
learns comes from its own resenses — curiosity is the only teacher. Warm-start
control: day-0 full snapshot, then scarce.

Typical/atypical is tested at TWO levels:
  HOUSEHOLD (primary, matches the pre-registration): the `typ` bank
    (version22_typ, 6 conventional-placement households) vs the `conf` bank
    (version22 + version22b, 24 idiosyncratic households).
  OBJECT (secondary, paired within household): the cfg targets are the
    regime-flipped ATYPICAL objects; matched conventional objects (plate, fork,
    bowl, remote...) in the same household are the TYPICAL queries. Statistically
    stronger (household variance cancels) but a different unit of atypicality —
    and note this split previously suffered a query-ordering confound, fixed in
    household_queries() below.

PHASE LESSON (mandatory, from HUMP_DIAGNOSIS.md): window start days are STAGGERED
— household i starts its N-day run at calendar-day offset (i*3)%7, so day-of-week
phase is balanced across the pool and no Monday-alignment artifact can recur.

Every query row logs: action, reward, correctness, the COUNTERFACTUAL correctness
of the answer the arm would have given had it answered (computable in replay —
the calibration-in-action metric), the arm's internal confidence, and (LLM arms)
its verbalized confidence.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

from dynbelief.h2 import core
from dynbelief.experiments.streams import true_parent_at
import dynbelief.reflect.run as R

N_DAYS = 14
# conventional-object preference list for the TYPICAL half of the query mix
_TYPICAL_POOL = ["plate", "fork", "bowl", "remote", "coffee_mug", "keys", "phone",
                 "laptop", "coffee_mug_b", "tote_bag", "spoon"]


@dataclass
class Query:
    day: int          # day index within the run (0..N_DAYS-1)
    t: int            # absolute minutes in the bank timeline
    obj: str
    kind: str         # "typical" | "atypical"


@dataclass
class EnvState:
    """Per-arm mutable state: the self-gathered observation history."""
    history: list = field(default_factory=list)   # [(t, obj, receptacle)]
    budget_left: int = 0


def household_queries(hh_idx: int, hh: str, cfg: dict, h: dict, Q: int,
                      seed: int = 20260724) -> list[Query]:
    """The fixed query stream for one household: Q/day for N_DAYS, half atypical
    (cfg targets, round-robin) and half typical (conventional objects present in
    the household, excluding targets). Hours seeded U[8,21]. STAGGERED start:
    calendar offset (hh_idx*3)%7."""
    rng = np.random.default_rng(seed + hh_idx)
    offset = (hh_idx * 3) % 7
    atyp = [o for (o, _hr) in cfg["targets"]]
    objs_present = set(h["by_obj"]) | set(h["init"])
    typ = [o for o in _TYPICAL_POOL if o in objs_present and o not in atyp]
    typ = typ[:max(2, Q // 2)]
    out = []
    a_pool, t_pool = [], []
    for d in range(N_DAYS):
        cal_day = offset + d
        n_a = Q // 2
        n_t = Q - n_a
        picks = []
        for _ in range(n_a):
            if not a_pool:
                a_pool = list(atyp); rng.shuffle(a_pool)
            picks.append((a_pool.pop(), "atypical"))
        for _ in range(n_t):
            if not t_pool:
                t_pool = list(typ); rng.shuffle(t_pool)
            picks.append((t_pool.pop(), "typical"))
        # SHUFFLE before assigning hours. Without this, picks is built as
        # [atypical x n_a, then typical x n_t] and zipping it against SORTED hours
        # hands every atypical query an earlier hour than every typical one
        # (measured: mean hour 11.5 vs 17.5). Because the daily resense budget is
        # consumed in time order, atypical objects then got systematic first claim
        # on it every day — confounding the typical/atypical comparison. Shuffling
        # interleaves the two kinds so the budget is allocated by confidence, not
        # by query kind.
        rng.shuffle(picks)
        hours = sorted(rng.uniform(8, 21, size=len(picks)))
        for (obj, kind), hr in zip(picks, hours):
            out.append(Query(day=d, t=int(cal_day * 1440 + hr * 60), obj=obj, kind=kind))
    return out


def true_loc(h, obj, t):
    return true_parent_at(h["by_obj"], h["init"], obj, t)


def warm_snapshot(h, offset_day: int):
    """Day-0 full snapshot (warm-start control): every object's true location at
    the window start."""
    t0 = offset_day * 1440
    return [(t0, o, true_loc(h, o, t0)) for o in sorted(set(h["by_obj"]) | set(h["init"]))]


def run_episode(arm, hh_idx: int, hh: str, cfg: dict, h: dict,
                Q: int, B: int, r_resense: float, wrong: float,
                warm: bool = False) -> list[dict]:
    """Simulate one arm on one household. Returns per-query rows."""
    queries = household_queries(hh_idx, hh, cfg, h, Q)
    offset = (hh_idx * 3) % 7
    st = EnvState()
    if warm:
        st.history = warm_snapshot(h, offset)
    arm.reset(hh, h, st)
    rows, cur_day = [], -1
    for q in queries:
        if q.day != cur_day:
            cur_day = q.day
            st.budget_left = B
            arm.new_day(q.day, st)
        truth = true_loc(h, q.obj, q.t)
        # the arm's answer belief is computed EITHER WAY (counterfactual scoring)
        decision = arm.decide(q, st, r_resense=r_resense, wrong=wrong)
        pred = decision["pred"]
        cf_correct = int(pred == truth)              # what answering would score
        if decision["action"] == "resense" and st.budget_left > 0:
            st.budget_left -= 1
            st.history.append((q.t, q.obj, truth))   # the corrective feedback
            action, reward, correct = "resense", r_resense, None
            arm.observe(q, truth, st)
        else:
            action = "answer"
            correct = cf_correct
            reward = 1.0 if correct else wrong
        rows.append({"hh": hh, "day": q.day, "t": q.t, "obj": q.obj, "kind": q.kind,
                     "offset": offset, "action": action, "pred": pred,
                     "true": truth, "correct": correct, "cf_correct": cf_correct,
                     "reward": reward, "conf": decision.get("conf"),
                     "verbal_conf": decision.get("verbal_conf"),
                     "budget_left": st.budget_left, "warm": int(warm)})
    return rows
