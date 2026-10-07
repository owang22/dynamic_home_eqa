"""Archetypes, overlays, and consistency rules for household selection.

Households are enumerated as WHOLE UNITS: an archetype fixes who lives
there and what each person does; an overlay swaps the work schedule of
named residents; a variant re-draws timings, ages and the specific job
while keeping both fixed. Nothing is assembled from independently
sampled attributes — that produced households nobody would believe.

The archetype list is the 10 human-written types from the storyfirst
control file (old_profiles/revamp_v2/control.yaml, commit 571638f3) —
TYPES ONLY: names, member structure, roles. No generated content is
reused. One of the 10, night_shift_worker_solo, was already
working_professional_solo plus a night_shift overlay, so it is MERGED
into that overlay cell rather than kept as an archetype (noted in the
slot summary). researcher_household is the planned addition; the two
proposed additions from the structural audit (no single-senior home, no
three-generation home in the base 10) are single_senior_solo and
multigenerational_family.

This module is the single authority on validity: the sampler builds
records from these specs and `violations()` re-checks them, and
validate.py will hold realized timelines against the same fields.
"""
from __future__ import annotations

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "profiles" / "households"

# ------------------------------------------------------------ residents --
# A resident spec: role, age range (point age sampled per variant),
# employment, schedule_type, occupation_category (the LLM picks the
# specific job title inside it), wfh flag (works from home: daytime
# timings, but occupancy stays home — generation states it).

def _r(role, ages, employment, schedule="none", occupation=None,
       wfh=False):
    return {"role": role, "age_range": list(ages),
            "employment": employment, "schedule_type": schedule,
            "occupation_category": occupation, "wfh": wfh}


EMPLOYMENT = ("full_time", "part_time", "nonworking_adult", "retired",
              "student", "school_child", "preschool_child")
SCHEDULE_TYPES = ("fixed_daytime", "fixed_evening", "fixed_night_shift",
                  "rotating_shift", "irregular_gig", "irregular_academic",
                  "none")
OCCUPATIONS = ("office_professional", "healthcare", "service_or_trade",
               "education", "tech", "retail_food_service",
               "skilled_manual", "academic_research", "creative")

ARCHETYPES = {
    # ---- the storyfirst 10, minus the merged night-shift solo ----
    "working_professional_solo": [
        _r("adult", (26, 44), "full_time", "fixed_daytime",
           "office_professional")],
    "working_couple_no_children": [
        _r("adult", (27, 45), "full_time", "fixed_daytime",
           "office_professional"),
        _r("adult", (27, 45), "full_time", "fixed_daytime",
           "service_or_trade")],
    "retired_couple": [
        _r("adult", (66, 80), "retired"),
        _r("adult", (66, 80), "retired")],
    "family_teen_and_child": [
        _r("adult", (38, 50), "full_time", "fixed_daytime",
           "office_professional"),
        _r("adult", (38, 50), "full_time", "fixed_daytime", "education"),
        _r("teen", (15, 17), "student"),
        _r("child", (7, 10), "school_child")],
    "couple_with_toddler": [
        _r("adult", (28, 40), "full_time", "fixed_daytime", "tech"),
        _r("adult", (28, 40), "part_time", "fixed_daytime", "healthcare"),
        _r("child", (1, 3), "preschool_child")],
    "single_parent_teens": [
        _r("adult", (40, 52), "full_time", "fixed_daytime", "healthcare"),
        _r("teen", (14, 17), "student"),
        _r("teen", (14, 17), "student")],
    "single_adult_wfh": [
        _r("adult", (28, 45), "full_time", "fixed_daytime", "tech",
           wfh=True)],
    "remote_worker_couple": [
        _r("adult", (28, 45), "full_time", "fixed_daytime", "tech",
           wfh=True),
        _r("adult", (28, 45), "full_time", "fixed_daytime", "creative",
           wfh=True)],
    "college_roommates": [
        _r("adult", (19, 23), "student"),
        _r("adult", (19, 23), "student"),
        _r("adult", (19, 23), "student", "fixed_evening",
           "retail_food_service")],   # one roommate works evenings
    # ---- planned addition ----
    "researcher_household": [
        _r("adult", (26, 38), "full_time", "irregular_academic",
           "academic_research")],
    # ---- proposed additions from the structural audit ----
    "single_senior_solo": [
        _r("adult", (70, 84), "retired")],
    "multigenerational_family": [
        _r("adult", (68, 80), "retired"),
        _r("adult", (36, 48), "full_time", "fixed_daytime",
           "skilled_manual"),
        _r("adult", (34, 46), "part_time", "fixed_daytime",
           "retail_food_service"),
        _r("teen", (13, 16), "student"),
        _r("child", (6, 9), "school_child")],
}

BEDROOMS = {                       # fixed per archetype, not sampled
    "working_professional_solo": 1, "working_couple_no_children": 2,
    "retired_couple": 2, "family_teen_and_child": 3,
    "couple_with_toddler": 2, "single_parent_teens": 3,
    "single_adult_wfh": 1, "remote_worker_couple": 2,
    "college_roommates": 3, "researcher_household": 1,
    "single_senior_solo": 1, "multigenerational_family": 4,
}

# ------------------------------------------------------------- overlays --
# overlay -> {archetype: [resident indices whose schedule changes]}.
# Only believable pairs appear; the slot summary lists the ruled-out
# pairs with reasons.
OVERLAYS = {
    "night_shift": {
        # the merged old night_shift_worker_solo archetype
        "working_professional_solo": [0],
        "working_couple_no_children": [1],
    },
    "rotating_shift": {
        "single_parent_teens": [0],
    },
    "opposite_schedules": {
        "working_couple_no_children": [0, 1],   # [day, night] pair
    },
    "irregular_gig": {
        "working_professional_solo": [0],
        "college_roommates": [2],       # the working roommate goes gig
    },
}

# what an overlay does to a targeted resident
def apply_overlay(residents: list[dict], overlay: str,
                  targets: list[int]) -> None:
    if overlay == "night_shift":
        for i in targets:
            residents[i]["schedule_type"] = "fixed_night_shift"
            residents[i]["occupation_category"] = "healthcare"
            residents[i]["wfh"] = False
    elif overlay == "rotating_shift":
        for i in targets:
            residents[i]["schedule_type"] = "rotating_shift"
            residents[i]["occupation_category"] = "healthcare"
            residents[i]["wfh"] = False
    elif overlay == "opposite_schedules":
        day, night = targets
        residents[day]["schedule_type"] = "fixed_daytime"
        residents[night]["schedule_type"] = "fixed_night_shift"
        residents[night]["occupation_category"] = "skilled_manual"
        residents[night]["wfh"] = False
    elif overlay == "irregular_gig":
        for i in targets:
            residents[i]["schedule_type"] = "irregular_gig"
            residents[i]["employment"] = "part_time"
            residents[i]["occupation_category"] = "service_or_trade"
            residents[i]["wfh"] = False
    else:
        raise ValueError(overlay)


RULED_OUT = [
    ("retired_couple / single_senior_solo x any work overlay",
     "nobody is employed; there is no schedule to overlay"),
    ("single_adult_wfh / remote_worker_couple x night_shift or "
     "opposite_schedules",
     "remote work decouples work hours from leaving the house, so the "
     "overlay barely changes what a robot in the home observes"),
    ("researcher_household x any overlay",
     "its schedule is already the irregular_academic condition; "
     "stacking another schedule double-treats one home"),
    ("college_roommates x rotating_shift",
     "a fixed rotation implies stable shift employment, not believable "
     "for full-time students; irregular_gig covers them instead"),
    ("couple_with_toddler x opposite_schedules",
     "believable (tag-team childcare) but not chosen: the toddler adds "
     "a second unusual signal and the overlay budget is 5-6 cells"),
    ("family_teen_and_child x night_shift",
     "believable but not chosen for the same single-factor reason"),
]

MERGE_NOTES = [
    "night_shift_worker_solo (old hh_010) is working_professional_solo "
    "plus a night_shift overlay — merged into that overlay cell, not "
    "kept as an archetype.",
]

# which ATUS schedule component a schedule_type samples timing from
ATUS_SCHEDULE_FOR = {
    "fixed_daytime": ("daytime",),
    "fixed_evening": ("evening",),
    "fixed_night_shift": ("night",),
    "rotating_shift": ("daytime", "evening", "night"),
    "irregular_gig": ("split_irregular", "daytime"),
    "irregular_academic": ("split_irregular", "daytime"),
    "none": ("non_workday",),
}

AGE_BANDS = ((15, 24, "15-24"), (25, 44, "25-44"),
             (45, 64, "45-64"), (65, 200, "65+"))


def age_band(age: int) -> str:
    for lo, hi, name in AGE_BANDS:
        if lo <= age <= hi:
            return name
    return "under-15"


# ------------------------------------------------------------ validity --

def violations(rec: dict) -> list[str]:
    out: list[str] = []
    cell_arch = rec.get("archetype")
    if cell_arch not in ARCHETYPES:
        return [f"archetype: {cell_arch!r}"]
    overlay = rec.get("overlay")
    if overlay is not None and (
            overlay not in OVERLAYS
            or cell_arch not in OVERLAYS[overlay]):
        out.append(f"overlay {overlay!r} not defined for {cell_arch}")
        return out
    spec = [dict(s) for s in ARCHETYPES[cell_arch]]
    if overlay:
        apply_overlay(spec, overlay, OVERLAYS[overlay][cell_arch])
    residents = rec.get("residents_detail") or []
    if len(residents) != len(spec):
        out.append(f"{len(residents)} residents, spec has {len(spec)}")
        return out
    for i, (r, s) in enumerate(zip(residents, spec)):
        rid = f"resident_{i + 1}"
        for field in ("role", "employment", "schedule_type", "wfh"):
            if r.get(field) != s[field]:
                out.append(f"{rid}: {field} {r.get(field)!r} != spec "
                           f"{s[field]!r}")
        if r.get("occupation_category") != s["occupation_category"]:
            out.append(f"{rid}: occupation_category departs from spec")
        age = r.get("age")
        lo, hi = s["age_range"]
        if not isinstance(age, int) or not lo <= age <= hi:
            out.append(f"{rid}: age {age!r} outside {lo}-{hi}")
        needs_timing = r.get("role") != "child"
        if needs_timing and not r.get("timing"):
            out.append(f"{rid}: no sampled timing numbers")
        if r.get("employment") in ("full_time", "part_time") and (
                r.get("schedule_type") == "none"):
            out.append(f"{rid}: employed but schedule none")
    if rec.get("bedrooms") != BEDROOMS[cell_arch]:
        out.append(f"bedrooms {rec.get('bedrooms')!r} != "
                   f"{BEDROOMS[cell_arch]} for {cell_arch}")
    if rec.get("variant") not in (1, 2, 3):
        out.append(f"variant: {rec.get('variant')!r}")
    return out


# ---------------------------------------------------------- group tags --

def tags_for(rec: dict) -> list[str]:
    res = rec["residents_detail"]
    t = []
    ages = [r["age"] for r in res]
    if len(res) == 1:
        t.append("single_occupant")
    if any(a >= 65 for a in ages):
        t.append("has_senior")
    if any(r["role"] == "child" for r in res):
        t.append("has_young_children")
    if any(r["role"] == "teen" for r in res):
        t.append("has_teenagers")
    if rec["archetype"] == "multigenerational_family":
        t.append("multigenerational")
    if any(r["wfh"] for r in res):
        t.append("wfh_household")
    if all(r["employment"] in ("student", "part_time") for r in res
           if r["role"] == "adult") and any(
               r["employment"] == "student" for r in res):
        t.append("student_household")
    scheds = {r["schedule_type"] for r in res}
    if rec.get("overlay") == "opposite_schedules":
        # the night schedule is a CONSTITUENT of the opposite pair, not
        # an independent quirk — tag only the pair
        t.append("opposite_schedules")
    elif "fixed_night_shift" in scheds:
        t.append("night_shift")
    if "rotating_shift" in scheds:
        t.append("rotating_shift")
    if "irregular_gig" in scheds:
        t.append("irregular_gig")
    if "irregular_academic" in scheds:
        t.append("irregular_academic")
    return t


# overlays and overlay-equivalent schedules count as "unusual"; the
# college_roommates evening job is part of its own archetype and does not
UNUSUAL_TAGS = ("night_shift", "rotating_shift", "opposite_schedules",
                "irregular_gig")
