"""Decides, with a seeded random generator, which situations are active on each
day and which small disturbances happen. The schedule is the ground truth for
the hidden state of the household."""
from __future__ import annotations

import math
import random

START_CHANCE = {"rarely": 1 / 60, "about monthly": 1 / 30,
                "about every two weeks": 1 / 14, "about weekly": 1 / 7}
MAX_ACTIVE = 2


def schedule_situations(situations: list[dict], days: int, seed: int,
                        forced: list[tuple[str, int, int]] = ()) -> list[list[str]]:
    """Returns, for each day, the ids of the situations active that day.
    forced: (situation id, first day, number of days), placed before sampling."""
    rng = random.Random(seed)
    active = [[] for _ in range(days)]
    used_lasting = set()
    for sid, first, length in forced:
        for d in range(first, min(days, first + length)):
            active[d].append(sid)
    by_id = {s["id"]: s for s in situations}
    forced_days = {d for sid, first, length in forced for d in range(first, min(days, first + length))}
    for day in range(days):
        if day in forced_days:          # a forced situation runs alone
            continue
        for s in situations:
            if s["id"] in active[day] or len(active[day]) >= MAX_ACTIVE:
                continue
            if s["kind"] == "lasting":
                if s["id"] in used_lasting or day < days // 3:
                    continue
            if rng.random() >= START_CHANCE[s["how_often"]]:
                continue
            if s["kind"] == "one_off":
                length = 1
            elif s["kind"] == "lasting":
                length = days - day
                used_lasting.add(s["id"])
            else:
                typical = max(1, by_id[s["id"]]["typical_days"])
                length = max(1, typical + rng.randint(-1, 1))
            for d in range(day, min(days, day + length)):
                if d in forced_days:
                    break
                if s["id"] not in active[d]:
                    active[d].append(s["id"])
    return active


def _poisson(rng: random.Random, mean: float) -> int:
    limit, k, p = math.exp(-mean), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def daily_disturbances(disturbances: list[dict], resident: str, day: int,
                       variation: float, seed: int) -> list[tuple[int, str]]:
    """(minute of day, text) for one resident's day. More with higher variation."""
    rng = random.Random(f"{seed}-{resident}-{day}")
    pool = [d["text"] for d in disturbances if d["who"] in (resident, "anyone")]
    if not pool:
        return []
    count = _poisson(rng, 4 * variation)
    picks = [(rng.randint(8 * 60, 21 * 60), rng.choice(pool)) for _ in range(count)]
    return sorted(picks)


def off_routine_today(resident: str, day: int, variation: float, seed: int) -> bool:
    return random.Random(f"{seed}-off-{resident}-{day}").random() < variation
