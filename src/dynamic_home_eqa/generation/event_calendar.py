"""Deterministic episodic-event calendar — the explicit source of day-to-day
variety in generated households.

Why this exists (stage1c postmortem): asking the day-plan LLM to "be varied
but mostly ordinary" made variety a property of model temperament — it mode-
collapsed onto one dramatic motif when we accidentally primed it (a storm and
power cut nearly every day), and after the prompt was de-primed it produced
near-verbatim ordinary days punctuated by an occupant spontaneously changing
occupation. Variety is now DATA: a sparse, seeded calendar sampled once per
household decides which days carry a notable event and what it is; the day
planner just renders it. What should repeat (routines) comes from the routine
charter; what should vary (events) comes from here; the model improvises
neither.

Prefix-stable by construction: day k's outcome depends only on days 0..k of
the same household, so extending an episode's horizon never rewrites the
days already generated.
"""
from __future__ import annotations

import random

from .cache import make_seed

# (type, base weight, weekend-multiplier, needs_occupant, template)
_EVENT_TYPES = [
    ("friend_visit", 0.30, 1.6, False,
     "A friend drops by in the {when}; the shared spaces get a quick tidy "
     "beforehand and everyone drifts through to say hello."),
    ("dinner_party", 0.15, 2.5, False,
     "The household hosts a small dinner {when}: extra cooking, the table "
     "set properly, and a late cleanup."),
    ("sick_day", 0.20, 0.7, True,
     "{who} is unwell today — stays home resting, eats lightly, and skips "
     "their usual obligations."),
    ("repair_visit", 0.15, 0.3, False,
     "A repair technician is scheduled mid-morning; someone stays home to "
     "let them in and works around the visit."),
    ("day_trip", 0.20, 1.8, True,
     "{who} is out of the house most of the day on a trip/errand marathon "
     "and only returns toward the evening."),
]
_P_EVENT = 0.10       # per-eligible-day chance of any event (~2-3 per 5 weeks)
_MIN_GAP_DAYS = 3     # notable events never land on consecutive/nearby days


def event_for_day(household_id: str, day: int, persona: dict) -> dict | None:
    """The event scheduled for `day`, or None (an ordinary day — the norm).

    Deterministic in (household_id, day): replays the seeded scan from day 0
    so the min-gap constraint holds across the whole horizon prefix.
    """
    names = [o.get("name") for o in persona.get("occupants", []) if o.get("name")]
    adults = [o.get("name") for o in persona.get("occupants", [])
              if o.get("age_band", "adult") in ("adult", "senior") and o.get("name")]
    last = -(_MIN_GAP_DAYS + 1)
    result = None
    for d in range(day + 1):
        rng = random.Random(make_seed(household_id, d, "event_calendar", 0))
        fires = rng.random() < _P_EVENT and (d - last) > _MIN_GAP_DAYS
        if not fires:
            continue
        last = d
        if d != day:
            continue
        weekend = d % 7 >= 5
        weights = [w * (wm if weekend else 1.0)
                   for (_t, w, wm, _n, _tpl) in _EVENT_TYPES]
        etype, _w, _wm, needs_occ, tpl = rng.choices(_EVENT_TYPES, weights=weights)[0]
        who = rng.choice(names if etype == "sick_day" else (adults or names)) if needs_occ else None
        note = tpl.format(who=who, when="evening" if not weekend else "afternoon")
        result = {"type": etype, "occupant": who, "note": note}
    return result
