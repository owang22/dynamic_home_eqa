"""The simulated lab: places, props, hidden rules, and what the dog sees. See DESIGN.md.

    world = make_world(seed)          # everything about one lab, fixed by the seed
    world.truth[day][prop]            # place id, or None when the prop is out of the lab (days 1..N_DAYS)
    look(world, day, place)           # what the dog reports at a place: scenery + props seen (10% misses)
"""
from __future__ import annotations

import datetime
import hashlib
import random
from dataclasses import dataclass, field

N_DAYS = 30
CHANGE_DAY = 16          # Monday of week 4
START = datetime.date(2026, 10, 19)  # a Monday
MISS = 0.10
NOISE_MOVE = 0.07
NOISE_AWAY = 0.03
CLEAN_P = 0.35
N_QUESTIONS = 3
PATROL_OTHER = 4

PLACES = {
    "dock": ("floor by the lab door, where the dog starts", ["tape cross on the floor"]),
    "under_desk_1": ("under desk 1, by the window", ["power strip", "foot rest"]),
    "under_desk_2": ("under desk 2", ["cable bundle"]),
    "under_desk_3": ("under desk 3, by the printer", ["paper recycling bin"]),
    "chair_1": ("seat of the black office chair at desk 1", []),
    "stool": ("seat of the grey stool by the workbench", []),
    "low_shelf_A": ("bottom shelf of bookcase A", ["binders"]),
    "low_shelf_B": ("bottom shelf of the metal rack B", ["box of spare cables"]),
    "sink_floor": ("floor next to the sink", ["floor mat"]),
    "cabinet_aisle": ("floor of the cabinet aisle", []),
    "cart_tray": ("bottom tray of the rolling cart", ["toolbox"]),
    "bench_low": ("low shelf under the workbench", ["soldering station box"]),
    "corner_floor": ("floor in the corner by the stacked boxes", ["stacked cardboard boxes"]),
    "sofa": ("seat of the small sofa by the wall", ["cushion"]),
}
PROP_PLACES = [p for p in PLACES if p != "dock"]
PROPS = {
    "mug": "white mug with a blue stripe",
    "bucket": "blue plastic bucket",
    "toy_dog": "stuffed toy dog",
    "cables_box": "cardboard box labelled CABLES",
    "backpack": "black backpack",
    "umbrella": "red umbrella",
    "bottle": "green water bottle",
}
SIGN = "yellow wet-floor sign"
RULE_TYPES = ["weekday", "cue", "fixed", "friday", "away", "random", "rotation"]
CHANGING = {"weekday", "fixed"}


def date_of(day: int) -> datetime.date:
    """Lab day 1 is START; lab days are weekdays only."""
    weeks, k = divmod(day - 1, 5)
    return START + datetime.timedelta(days=7 * weeks + k)


def weekday(day: int) -> str:
    return date_of(day).strftime("%A")


@dataclass
class World:
    seed: int
    rules: dict            # prop -> {"type", "places": [...], "after": {...} (new regime from CHANGE_DAY) or None}
    cleaning: list         # cleaning[day] True when the wet-floor sign is at the dock that day (index 0 unused)
    truth: list            # truth[day][prop] -> place or None
    noise: list            # noise[day][prop] -> "moved" / "away" / None (which days broke the rule)
    questions: list        # questions[day] -> props searched that day
    patrol: list           # patrol[day] -> places on the patrol (dock first)
    rule_text: dict = field(default_factory=dict)   # prop -> plain statement of each regime, for the grader


def _rule_place(rule: dict, day: int, cleaning: list):
    t, P = rule["type"], rule["places"]
    wd = date_of(day).weekday()  # 0 = Monday
    if t == "weekday":
        return P[0] if wd in (0, 2, 4) else P[1]
    if t == "cue":
        return P[0] if day > 1 and cleaning[day - 1] else P[1]
    if t == "fixed":
        return P[0]
    if t == "friday":
        return P[0] if wd == 4 else P[1]
    if t == "away":
        return None if wd in (1, 3) else P[0]
    if t == "random":
        return None  # drawn by the caller
    if t == "rotation":
        return P[(day - 1) % 3]
    raise ValueError(t)


def describe(t: str, P: list) -> str:
    P = P + [None] * 3
    return {
        "weekday": lambda: f"at {P[0]} on Monday, Wednesday and Friday; at {P[1]} on Tuesday and Thursday",
        "cue": lambda: f"at {P[0]} on the lab day after a day when the wet-floor sign was at the dock; otherwise at {P[1]}",
        "fixed": lambda: f"always at {P[0]}",
        "friday": lambda: f"at {P[0]} on Fridays; otherwise at {P[1]}",
        "away": lambda: f"out of the lab on Tuesday and Thursday; otherwise at {P[0]}",
        "random": lambda: f"at one of {P[0]}, {P[1]}, {P[2]} at random each day (no pattern among them)",
        "rotation": lambda: f"rotates {P[0]} -> {P[1]} -> {P[2]} -> {P[0]} ..., one step each lab day (weekends do not count)",
    }[t]()


def make_world(seed: int) -> World:
    rng = random.Random(f"lab-{seed}")
    props = list(PROPS)
    rng.shuffle(props)
    rules, rule_text = {}, {}
    for prop, t in zip(props, RULE_TYPES):
        n = {"weekday": 2, "cue": 2, "fixed": 1, "friday": 2, "away": 1, "random": 3, "rotation": 3}[t]
        places = rng.sample(PROP_PLACES, n)
        after = None
        if t in CHANGING:
            after = {"type": t, "places": rng.sample([p for p in PROP_PLACES if p not in places], n)}
        rules[prop] = {"type": t, "places": places, "after": after}
        rule_text[prop] = {"before": describe(t, places), "after": describe(t, after["places"]) if after else None}
    cleaning = [False] + [rng.random() < CLEAN_P for _ in range(N_DAYS)]
    truth, noise = [None], [None]
    for day in range(1, N_DAYS + 1):
        tday, nday = {}, {}
        for prop in PROPS:
            r = rules[prop]
            if r["after"] and day >= CHANGE_DAY:
                r = r["after"]
            place = rng.choice(r["places"]) if r["type"] == "random" else _rule_place(r, day, cleaning)
            u = rng.random()
            nday[prop] = None
            if u < NOISE_AWAY:
                place, nday[prop] = None, "away"
            elif u < NOISE_AWAY + NOISE_MOVE:
                place, nday[prop] = rng.choice([p for p in PROP_PLACES if p != place]), "moved"
            tday[prop] = place
        truth.append(tday)
        noise.append(nday)
    questions = [None] + [rng.sample(list(PROPS), N_QUESTIONS) for _ in range(N_DAYS)]
    route = PROP_PLACES[:]
    rng.shuffle(route)
    patrol = [None]
    for day in range(1, N_DAYS + 1):
        k = (day - 1) * PATROL_OTHER
        patrol.append(["dock"] + [route[(k + i) % len(route)] for i in range(PATROL_OTHER)])
    return World(seed, rules, cleaning, truth, noise, questions, patrol, rule_text)


def missed(world: World, day: int, place: str, prop: str) -> bool:
    """Whether the camera misses this prop at this place today. Fixed per (lab, day, place, prop), so every
    method that looks there that day gets the same answer."""
    h = hashlib.sha256(f"{world.seed}|{day}|{place}|{prop}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 2**32 < MISS


def look(world: World, day: int, place: str) -> list[str]:
    """Prop ids seen at the place (the scenery is added when shown to a method)."""
    seen = [p for p, at in world.truth[day].items() if at == place and not missed(world, day, place, p)]
    if place == "dock" and world.cleaning[day]:
        seen.append("SIGN")
    return sorted(seen)


def rule_now(world: World, prop: str, day: int) -> dict:
    r = world.rules[prop]
    return r["after"] if r["after"] and day >= CHANGE_DAY else r


def experimenter_sheet(world: World) -> str:
    """The day-by-day script for running this lab's routine for real."""
    lines = [f"# Experimenter sheet, simulated lab {world.seed}", "",
             "Set these each morning before the dog's first search. 'out' = take it out of the lab for the day.",
             f"Put the {SIGN} at the dock on days marked 'clean'. Rules (do not show the agent):", ""]
    for prop in PROPS:
        rt = world.rule_text[prop]
        lines.append(f"- **{prop}** ({PROPS[prop]}): {rt['before']}" + (f"; from day {CHANGE_DAY}: {rt['after']}" if rt["after"] else ""))
    lines += ["", "| day | date | clean | " + " | ".join(PROPS) + " | searched |", "|---" * (len(PROPS) + 4) + "|"]
    for day in range(1, N_DAYS + 1):
        cells = []
        for prop in PROPS:
            at = world.truth[day][prop] or "out"
            cells.append(at + ("*" if world.noise[day][prop] else ""))
        lines.append(f"| {day} | {weekday(day)[:3]} {date_of(day).isoformat()} | {'clean' if world.cleaning[day] else ''} | "
                     + " | ".join(cells) + f" | {', '.join(world.questions[day])} |")
    lines += ["", "\\* = off-rule that day (a person put it somewhere else, or took it out)."]
    return "\n".join(lines) + "\n"
