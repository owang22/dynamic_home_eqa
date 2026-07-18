"""Episode-bank builder v2 — varied (t_snap, t_query) across ALL days.

Design (review round): the sim has many days per scene-household but few
moves per day, so questions are PROPORTIONED ACROSS DAYS rather than piled
onto one; observation and query times both vary (mix of Δt and absolute
time-of-day/day-of-week, including overnight cross-day gaps); and the bank
carries two labeled components:
  - uniform: seeded target x (t_snap, t_query) draws — the natural marginal.
  - moved: importance-sampled around true transitions (t_snap shortly
    before, t_query after, verified receptacle-changed) — the punchline
    population, kept labeled so aggregates are never silently mixed.
"""
from __future__ import annotations

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.eqa.analysis import volatility_table
from dynbelief.llm_agent.prelim import true_receptacle

_SNAP_HOURS = [8, 10, 13, 16, 19]
_DTS_MIN = [60, 120, 240, 480, 780, 1200, 1560]   # 1h .. 26h (cross-day)


def build_bank(world, seed: int = 7, uniform_per_day: int = 2,
               moved_per_day: int = 2) -> list[dict]:
    """Episode specs: {obj, t_snap, t_query, component, stratum}."""
    rng = np.random.default_rng(seed)
    vol = {r["obj_id"]: r["tercile"] for r in volatility_table(world)}
    objs = list(world.objects())
    days = [d for d in world.days]
    day_set = set(days)
    specs = []
    for day in days:
        d0 = day * MIN_PER_DAY
        # uniform component — stratified target, random snap/dt
        for _ in range(uniform_per_day):
            st = ["static", "occasional", "dynamic"][rng.integers(3)]
            pool = [o for o in objs if vol[o] == st] or objs
            obj = int(pool[rng.integers(len(pool))])
            t_snap = d0 + int(_SNAP_HOURS[rng.integers(len(_SNAP_HOURS))]) * 60
            dt = int(_DTS_MIN[rng.integers(len(_DTS_MIN))])
            t_query = t_snap + dt
            q_day = t_query // MIN_PER_DAY
            if q_day != day and (q_day not in day_set):
                t_query = d0 + 21 * 60 + int(rng.integers(0, 60))
            if t_query % MIN_PER_DAY > 23 * 60:
                t_query = (t_query // MIN_PER_DAY) * MIN_PER_DAY + 22 * 60
            if t_query <= t_snap:
                continue
            specs.append({"obj": obj, "t_snap": int(t_snap),
                          "t_query": int(t_query), "component": "uniform",
                          "stratum": vol[obj]})
        # moved component — sample around this day's true transitions
        day_events = [(t, o) for o in objs
                      for t in world.change_times(o)
                      if t // MIN_PER_DAY == day and t % MIN_PER_DAY > 8 * 60]
        rng.shuffle(day_events)
        got = 0
        for t_star, obj in day_events:
            if got >= moved_per_day:
                break
            t_snap = max(d0 + 7 * 60, t_star - int(rng.integers(30, 240)))
            t_query = min(d0 + 22 * 60, t_star + int(rng.integers(30, 360)))
            if t_query <= t_snap:
                continue
            if true_receptacle(world, obj, t_snap) == true_receptacle(world, obj, t_query):
                continue        # moved and returned — not a displaced episode
            specs.append({"obj": int(obj), "t_snap": int(t_snap),
                          "t_query": int(t_query), "component": "moved",
                          "stratum": vol[obj]})
            got += 1
    return specs
