"""Guided-decoding schema for the persona stage."""
from __future__ import annotations

# Coarse age knob: an enum, not a raw age number, because behavior differences
# that matter for this pipeline (is this occupant even at school, do they nap,
# do they work) are step-function by band, not continuous by year. An enum
# also means the persona and activity-trace prompts can key off a fixed,
# guaranteed-valid set of bands rather than parsing a free-text age.
AGE_BANDS: list[str] = ["toddler", "young_child", "older_child", "teen", "adult", "senior"]

PERSONA_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "occupants": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name":         {"type": "string"},
                    "age_band":     {"type": "string", "enum": AGE_BANDS,
                                     "description": (
                                         "toddler (1-4, home/daycare, naps), young_child (5-9, "
                                         "grade school), older_child (10-12, grade school, more "
                                         "independence), teen (13-18, school + activities/job), "
                                         "adult (18-64, work), senior (65+, often retired)."
                                     )},
                    "role":         {"type": "string",
                                     "description": "e.g. 'adult_wfh', 'child_school', 'adult_offsite'"},
                    "typical_wake": {"type": "number", "minimum": 4.0, "maximum": 11.0,
                                     "description": "Typical wake hour, 24h float, morning-side (e.g. 7.5)."},
                    "typical_sleep": {"type": "number", "minimum": 17.0, "maximum": 26.0,
                                      "description": (
                                          "Typical bedtime hour, 24h float, evening/night-side: "
                                          "21.0 = 9pm, 22.5 = 10:30pm, 24.5 = 12:30am. Never a "
                                          "morning-looking number like 9 for a 9pm bedtime — the "
                                          "range is bounded to make that mistake structurally "
                                          "impossible, but reason in 24h time throughout."
                                      )},
                    "habits":       {"type": "string",
                                     "description": (
                                         "One line on what makes this occupant's day different from "
                                         "another occupant with a similar role in the same household — "
                                         "a specific job/school detail, a hobby, a routine quirk. "
                                         "Required even when there's only one occupant; becomes load-"
                                         "bearing when two occupants share a role (e.g. two working "
                                         "adults) so their generated days don't converge to the same "
                                         "schedule with only cosmetic differences."
                                     )},
                    "tidiness":     {"type": "number", "minimum": 0.0, "maximum": 1.0,
                                     "description": (
                                         "0=very untidy, 1=very tidy. Per-occupant, not a household "
                                         "average — a tidy parent and a messy teenager under the same "
                                         "roof is normal; give each occupant their own value rather "
                                         "than collapsing the household to one number. Scales this "
                                         "occupant's cleanup probability downstream."
                                     )},
                    "owned_items":  {"type": "array",
                                     "items": {"type": "string",
                                               "enum": ["phone", "wallet", "keys", "laptop",
                                                        "backpack", "sunglasses", "headphones",
                                                        "medicine"]},
                                     "description": (
                                         "The carried personal items THIS occupant owns and moves "
                                         "around. Give each person their own, age-appropriately: a "
                                         "working adult typically phone/wallet/keys/laptop (+ maybe "
                                         "sunglasses), a teen phone/laptop/headphones/backpack, a "
                                         "school-age child a backpack (maybe a phone), a senior "
                                         "phone/wallet/keys/medicine, a toddler none. Only the "
                                         "owner moves their own item, so don't hand a toddler a "
                                         "laptop or give the whole family one shared phone."
                                     )},
                    "bedroom_index": {"type": "integer", "minimum": 1, "maximum": 6,
                                      "description": (
                                          "Which bedroom this occupant sleeps in, as a 1-based index. "
                                          "A couple shares one index; each child gets their own. So "
                                          "two parents + two kids => parents both 1, kids 2 and 3. "
                                          "Resolved to the scene's real bedroom_N at placement time."
                                      )},
                },
                "required": ["name", "age_band", "role", "typical_wake", "typical_sleep",
                             "habits", "tidiness", "owned_items", "bedroom_index"],
            },
            "minItems": 1,
            "maxItems": 4,
        },
        "household_type": {"type": "string"},
        "schedule_notes": {"type": "string",
                           "description": "Brief natural language notes on household rhythms."},
    },
    "required": ["occupants", "household_type"],
}
