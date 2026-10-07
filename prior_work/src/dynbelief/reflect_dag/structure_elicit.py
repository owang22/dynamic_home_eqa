"""Change 1 (elicitation side) — the LLM authors the activity structure.

Two-level structure proposal, from the SPARSE diagnostic digest (never the full
stream):
  1. persona (as the current reflection already does), then
  2. conditioned on it: the household's daily activities (fixed vocab) and, for
     each, which OBSERVED objects it moves.

The statistical channel (activity_graph.ActivityTiedRates) fits the parameters;
this file only decides STRUCTURE. Three sources, for the ablation ladder:
  - llm       : the LLM proposes the activity->object tying (the real arm).
  - oracle    : the ground-truth tying read off the profile (upper bound on
                structure quality; isolates parameter-fit from structure error).
  - scrambled : objects randomly reassigned to WRONG activities (the
                graceful-degradation control — a wrong tying should merely pool
                the wrong events => worse fit, never a crash).
"""
from __future__ import annotations

import json
import random
import re

from dynbelief.profiles.schema import load_profile
from dynbelief.reflect_dag.activity_graph import ACTIVITY_VOCAB, ActivityStructure

# ── profile-activity -> vocab keyword map (for the oracle) ───────────────────
_KW = [
    ("sleep", ["sleep", "nap", "bedtime"]),
    ("meal", ["breakfast", "lunch", "dinner", "brunch", "meal", "feeding", "eat",
              "twins_breakfast", "twins_lunch", "twins_dinner"]),
    ("work_departure", ["leave", "commute", "away_", "return_", "school_run",
                        "shift", "office", "work", "desk_work", "wfh", "prep_session",
                        "accounts", "grading", "desk", "care_round", "plant_round"]),
    ("errand", ["errand", "shopping", "supply_run", "library", "pharmacy", "market",
                "delivery", "trip", "groupride"]),
    ("exercise", ["walk", "swim", "gym", "fitness", "yoga", "run", "fetch", "play",
                  "park", "ride", "maintenance", "lake", "observing", "throwing",
                  "glazing", "diy", "repotting", "yard"]),
    ("leisure", ["tv", "leisure", "reading", "knit", "game", "stream", "painting",
                 "craft", "lessons", "settle", "recliner", "couch", "video_call",
                 "story", "fort", "circle", "session", "check"]),
]


def _to_vocab(activity_name: str) -> str:
    a = activity_name.lower()
    for vocab, kws in _KW:
        if any(k in a for k in kws):
            return vocab
    return "leisure"          # default bucket


def oracle_structure(base_profile: str, observed_objects: set[str],
                     manual_dir) -> ActivityStructure:
    """Ground-truth tying from the profile: map each profile activity to the
    vocab and collect the objects it moves (restricted to OBSERVED objects)."""
    ch = load_profile(f"{manual_dir}/{base_profile}.yaml")
    act_objs: dict[str, list[str]] = {v: [] for v in ACTIVITY_VOCAB}
    for name, a in ch.activities.items():
        v = _to_vocab(name)
        for o in a.objects:
            if o in observed_objects and o not in act_objs[v]:
                act_objs[v].append(o)
    return ActivityStructure(persona=base_profile,
                             activity_objects={k: v for k, v in act_objs.items() if v},
                             source="oracle")


def scramble_structure(struct: ActivityStructure, seed: int) -> ActivityStructure:
    """Reassign every object to a UNIFORMLY RANDOM activity (control: wrong
    tying). Keeps the same set of objects and activity vocabulary."""
    rng = random.Random(seed)
    objs = [o for v in struct.activity_objects.values() for o in v]
    acts = list(struct.activity_objects) or ACTIVITY_VOCAB
    scr: dict[str, list[str]] = {a: [] for a in acts}
    for o in objs:
        scr[rng.choice(acts)].append(o)
    return ActivityStructure(persona=struct.persona,
                             activity_objects={k: v for k, v in scr.items() if v},
                             atypical_activities=struct.atypical_activities,
                             source="scrambled")


# ── LLM structure proposal ───────────────────────────────────────────────────

STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "activities": {"type": "array", "items": {"type": "object", "properties": {
            "activity": {"type": "string", "enum": ACTIVITY_VOCAB},
            "objects": {"type": "array", "items": {"type": "string"}},
            "atypical": {"type": "boolean"}},
            "required": ["activity", "objects", "atypical"]}}},
    "required": ["activities"]}

_SYS = (
    "You infer the ACTIVITY STRUCTURE of a household you are building a memory of. "
    "You are given the inferred persona and a sparse digest of diagnostic object "
    "sightings. Day 0 is Monday; days 5-6 are the weekend. Decompose the household's "
    "routine into activities from this fixed vocabulary: "
    + ", ".join(ACTIVITY_VOCAB) + ". For EACH activity the household actually has, "
    "list which of the OBSERVED objects that activity moves (an object belongs to at "
    "most one activity — its primary one). Mark 'atypical': true when the persona "
    "makes this activity's object placements NON-STANDARD (e.g. a night-shift 'sleep' "
    "at midday, a 'work_departure' that never happens because they work from home, a "
    "mug that lives at a craft desk). Only include activities the evidence supports; "
    "omit the rest. Use ONLY object names from the provided list.")


def llm_structure(client, persona: str, digest: str, observed_objects: list[str],
                  seed: int = 7) -> ActivityStructure:
    user = (f"Inferred persona: {persona}\n\n{digest}\n\n"
            f"Observed objects: {', '.join(sorted(observed_objects))}.\n\n"
            f"List the household's activities and the objects each moves.")
    try:
        out = json.loads(client.generate(_SYS, user, STRUCTURE_SCHEMA,
                                         seed=seed, temperature=0.0, max_tokens=1024))
        allowed = set(observed_objects)
        act_objs: dict[str, list[str]] = {}
        atys: list[str] = []
        for a in out.get("activities", []):
            act = a.get("activity")
            if act not in ACTIVITY_VOCAB:
                continue
            objs = [o for o in a.get("objects", []) if o in allowed]
            if objs:
                act_objs.setdefault(act, [])
                act_objs[act] += [o for o in objs if o not in act_objs[act]]
                if a.get("atypical"):
                    atys.append(act)
        return ActivityStructure(persona=persona, activity_objects=act_objs,
                                 atypical_activities=sorted(set(atys)), source="llm")
    except Exception:
        return ActivityStructure(persona=persona, activity_objects={}, source="llm")
