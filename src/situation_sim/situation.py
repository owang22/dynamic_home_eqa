"""Day situation sampler: the hidden causes active on each day.

Two kinds of cause:
  * external events from ``events.yaml`` (household- or resident-scoped)
  * internal resident states (energy, hurriedness, distraction), resampled
    daily with carryover, and counted as an ACTIVE cause only in their
    extreme band (low energy, running late, distracted). Mild states still
    scale whim size but are not listed as causes.

Nothing here depends on the day index except the weekday/weekend split of
event rates and schedules.
"""
from __future__ import annotations

import pathlib
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

import yaml

from situation_sim.household import Household

WEEKDAYS = ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKEND = {"Saturday", "Sunday"}

# Internal state dynamics (judgment defaults, recorded in hidden_state.json)
STATE_CARRYOVER = 0.5      # weight of yesterday's value
STATE_NOISE_SD = 0.22
THRESH_LOW_ENERGY = 0.30
THRESH_HURRIED = 0.68
THRESH_DISTRACTED = 0.68


def load_events(path: Optional[pathlib.Path] = None) -> Dict[str, dict]:
    path = path or pathlib.Path(__file__).with_name("events.yaml")
    with open(path) as f:
        return yaml.safe_load(f)["events"]


@dataclass
class Cause:
    id: str                    # e.g. "rain", "late_work:resident_1", "low_energy:resident_2"
    kind: str                  # "event" | "internal"
    event: Optional[str]       # event type name for events
    resident: Optional[str]    # None for household scope
    words: str                 # plain words for the trace


@dataclass
class DaySituation:
    day_index: int
    weekday: str
    is_weekend: bool
    causes: List[Cause]
    states: Dict[str, Dict[str, float]]   # resident -> {energy, hurriedness, distraction}
    flags: Dict[str, List[str]] = field(default_factory=dict)  # resident -> active internal flags

    def events_for(self, resident: str) -> List[Cause]:
        """Event causes that apply to this resident (household ones and their own)."""
        return [c for c in self.causes if c.kind == "event"
                and (c.resident is None or c.resident == resident)]

    def has_flag(self, resident: str, flag: str) -> bool:
        return flag in self.flags.get(resident, [])

    def to_json(self) -> dict:
        return {"day_index": self.day_index, "weekday": self.weekday,
                "is_weekend": self.is_weekend,
                "causes": [asdict(c) for c in self.causes],
                "states": self.states, "flags": self.flags}


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def sample_situations(hh: Household, seed: int, n_days: int,
                      events: Dict[str, dict]) -> List[DaySituation]:
    rng = random.Random(f"situation:{seed}")
    days: List[DaySituation] = []
    prev: Dict[str, Dict[str, float]] = {}
    residents = sorted(hh.residents.values(), key=lambda r: r.id)
    for d in range(n_days):
        weekday = WEEKDAYS[d % len(WEEKDAYS)]
        is_we = weekday in WEEKEND
        rate_key = "weekend" if is_we else "weekday"
        causes: List[Cause] = []

        # --- external events (iterate in sorted order for determinism) ----
        for ename in sorted(events):
            ev = events[ename]
            p = ev["p_day"][rate_key]
            if ev["scope"] == "household":
                if rng.random() < p:
                    causes.append(Cause(ename, "event", ename, None, ev["description"]))
            else:
                for r in residents:
                    if r.role in ev.get("roles", []) and rng.random() < p:
                        causes.append(Cause(f"{ename}:{r.id}", "event", ename, r.id,
                                            f"{r.name.capitalize()}: {ev['description']}"))
        # a resident off sick is not also working late
        sick = {c.resident for c in causes if c.event == "sick_day"}
        causes = [c for c in causes if not (c.event == "late_work" and c.resident in sick)]

        # --- internal states with carryover ------------------------------
        states: Dict[str, Dict[str, float]] = {}
        flags: Dict[str, List[str]] = {}
        for r in residents:
            base = {"energy": r.base_energy, "hurriedness": r.base_hurry,
                    "distraction": r.base_distraction}
            st = {}
            for k in sorted(base):
                yesterday = prev.get(r.id, base)[k]
                x = (STATE_CARRYOVER * yesterday + (1 - STATE_CARRYOVER) * base[k]
                     + rng.gauss(0, STATE_NOISE_SD))
                st[k] = x
            # event nudges (e.g. a sick day drains energy)
            for c in causes:
                if c.kind == "event" and (c.resident is None or c.resident == r.id):
                    for k, dv in sorted(events[c.event].get("internal", {}).items()):
                        st[k] += dv
            st = {k: round(_clamp(v), 3) for k, v in st.items()}
            states[r.id] = st
            fl = []
            nm = r.name.capitalize()
            if st["energy"] < THRESH_LOW_ENERGY:
                fl.append("low_energy")
                causes.append(Cause(f"low_energy:{r.id}", "internal", None, r.id,
                                    f"{nm} has low energy ({st['energy']:.2f}): leaves things where they were used instead of putting them back"))
            if st["hurriedness"] > THRESH_HURRIED:
                fl.append("running_late")
                causes.append(Cause(f"running_late:{r.id}", "internal", None, r.id,
                                    f"{nm} is running late all day ({st['hurriedness']:.2f}): rushed putdowns, things dumped at the door, more whim"))
            if st["distraction"] > THRESH_DISTRACTED:
                fl.append("distracted")
                causes.append(Cause(f"distracted:{r.id}", "internal", None, r.id,
                                    f"{nm} is distracted ({st['distraction']:.2f}): carries things into the next room absent-mindedly, more likely to forget pocket items"))
            flags[r.id] = fl
        prev = states
        days.append(DaySituation(d, weekday, is_we, causes, states, flags))
    return days
