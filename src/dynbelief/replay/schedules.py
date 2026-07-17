"""Stage 0.6 — fixed observation schedules: sequences of (t_min, vp_id)."""
from __future__ import annotations

import random


def round_robin(viewpoints, period_min: int, t0: int, t1: int) -> list[tuple[int, str]]:
    """Visit viewpoints in a fixed cycle, one visit every period_min."""
    ids = viewpoints.ids()
    out = []
    i = 0
    t = t0
    while t < t1:
        out.append((t, ids[i % len(ids)]))
        i += 1
        t += period_min
    return out


def random_uniform(viewpoints, rate_per_hour: float, t0: int, t1: int,
                   seed: int) -> list[tuple[int, str]]:
    """Poisson-process visit times, viewpoint uniform at random."""
    rng = random.Random(seed)
    ids = viewpoints.ids()
    out = []
    t = float(t0)
    while True:
        t += rng.expovariate(rate_per_hour / 60.0)
        if t >= t1:
            break
        out.append((int(t), rng.choice(ids)))
    return out
