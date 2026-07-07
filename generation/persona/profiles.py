"""Household type labels for CLI/prompting convenience.

These carry no hand-authored events — the persona stage generates everything
downstream from just the label (+ optional demographic_notes), so this list
is free to grow without touching any other code. Deliberately spans age_band
(toddler through senior), household size (1 to 4 occupants), and schedule
shape (office commuter, shift worker, retired, student) rather than
variations on one "adult who works" template.
"""
from __future__ import annotations

HOUSEHOLD_PROFILES: list[str] = [
    # --- Single-occupant ---
    "single_professional_commuter",
    "single_remote_worker",
    "single_retiree",
    "college_student_alone",
    "night_shift_worker_alone",

    # --- Couples, no kids ---
    "work_from_home_adult",
    "young_professional_couple",
    "retired_couple",
    "empty_nesters",

    # --- Families with young kids ---
    "family_with_toddler",
    "family_with_kids",
    "single_parent_young_kids",

    # --- Families with older kids ---
    "family_with_teens",
    "single_parent_teens",

    # --- Shared / multigenerational ---
    "roommates_shared_house",
    "college_students_shared_house",
    "multigenerational_household",
]
