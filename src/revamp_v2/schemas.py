"""Guided-JSON schemas for the revamp_v2 LLM calls.

Split out of prompts.py (which owns every LLM-facing STRING) so each file
stays inside the complexity budget: this module owns only the machine-side
contract — what shape a response may take.

Two constraints the schemas deliberately do NOT express, because the
xgrammar guided-decoding backend rejects the keyword outright ("Grammar
error: Unimplemented keys"), leaving them to validate.check_referential:
uniqueItems on a block's weekday list, and dist probabilities summing to 1.
Everything else enumerable IS enum-constrained here, so the model cannot
emit an id that does not exist.
"""
from __future__ import annotations

from prompts import (ACTIVITY_VOCAB, DAY_ABBREV,
                     JITTER_CLASS_NAMES, NAME_PATTERN, TIME_PATTERN)


def _insert_after(props: dict, anchor: str, **extra) -> dict:
    """Splice `extra` in directly after `anchor`.

    Property order is GENERATION order under guided decoding, so a field
    appended with `dict(props, x=...)` lands last — which is a decision
    about when the model gets to think about it, not a formatting detail.
    """
    out: dict = {}
    for k, v in props.items():
        out[k] = v
        if k == anchor:
            out.update(extra)
    return out


def build_persona_schema(household_id: str, household_type: str,
                         n_residents: int, vocabulary: list[str]) -> dict:
    resident_ids = [f"resident_{i + 1}" for i in range(n_residents)]
    resident = {
        "type": "object", "additionalProperties": False,
        "required": ["id", "name", "age", "occupation", "personality",
                     "habits"],
        "properties": {
            "id": {"enum": resident_ids},
            "name": {"type": "string", "minLength": 2, "maxLength": 60},
            "age": {"type": "integer", "minimum": 0, "maximum": 100},
            "occupation": {"type": "string", "maxLength": 120},
            "personality": {"type": "string", "maxLength": 300},
            "habits": {"type": "array", "minItems": 5, "maxItems": 8,
                       "items": {"type": "string", "maxLength": 300}},
        },
    }
    obj = {
        "type": "object", "additionalProperties": False,
        "required": ["id", "class", "role", "owner"],
        "properties": {
            "id": {"type": "string", "pattern": r"^[a-z][a-z0-9_]{2,39}$"},
            "class": {"enum": vocabulary},
            # `role` is what L2 reads to decide this object's home and its
            # every rule, so it is written BEFORE the owner rather than
            # after: what a thing is for should pick who keeps it.
            "role": {"type": "string", "maxLength": 300},
            "owner": {"enum": resident_ids + ["shared"]},
        },
    }
    return {
        "type": "object", "additionalProperties": False,
        "required": ["reasoning", "household_id", "household_type",
                     "residents", "relationships", "home_layout_notes",
                     "daily_life_summary", "quirks", "object_inventory"],
        "properties": {
            # Reasoning INSIDE guided decoding. The guided path sends
            # enable_thinking=False (the JSON grammar suppresses a think
            # block anyway), so without this the persona is written with
            # no deliberation at all — every other field is a first-token
            # commitment. Property order IS generation order, so a field
            # declared first is genuinely written first and everything
            # after it is conditioned on it. This is `cites` generalized
            # from one clause to the whole household.
            "reasoning": {"type": "string", "maxLength": 2000},
            "household_id": {"const": household_id},
            "household_type": {"const": household_type},
            "residents": {"type": "array", "minItems": n_residents,
                          "maxItems": n_residents, "items": resident},
            "relationships": {"type": "string", "maxLength": 900},
            "home_layout_notes": {"type": "string", "maxLength": 900},
            "daily_life_summary": {"type": "string", "maxLength": 1200},
            "quirks": {"type": "string", "maxLength": 600},
            # LAST, deliberately: everything above describes what this
            # household IS and DOES, and the inventory is chosen with all
            # of it already written. Declared earlier, the objects were
            # picked first and the life was then described around them —
            # which is also how a home ends up with a laptop and a
            # medication bottle but no plates.
            "object_inventory": {"type": "array", "minItems": 8,
                                 "maxItems": 60, "items": obj},
        },
    }



def build_program_schema(household_id: str, resident_ids: list[str],
                         object_ids: list[str], receptacle_ids: list[str],
                         days: int, params: dict,
                         scheduled_activities: list[str] | None = None
                         ) -> dict:
    """The L2 contract. Every id is enum-constrained and every probability
    bounded, so the model cannot name something that does not exist.

    Two shapes carry most of the weight, both for the same reason: the
    generator reliably drops items from a list it has to keep in sync with
    another one. `sleep_schedule` is one entry per RESIDENT and
    `object_rules` one entry per OBJECT (home, drift and rules together),
    so "everybody sleeps" and "every object's fate is decided" are
    structural rather than something a validator catches afterwards.
    """
    locations = receptacle_ids + ["ELSEWHERE"] + \
        [f"person:{r}" for r in resident_ids]
    prob = {"type": "number", "minimum": 0.0, "maximum": 1.0}
    # Guided decoding emits properties in DECLARATION order — verified on
    # 12,226 generated rules, zero deviations — so a justification declared
    # last is written AFTER the choice it claims to explain and cannot have
    # informed it. Every `cites` below is therefore declared first in its
    # object. `maxLength` is genuinely enforced by xgrammar (max observed
    # was exactly the 200 cap, never over), unlike `dependentRequired`, and
    # it is the only lever that protects the token budget: truncating after
    # generation reclaims nothing, the tokens are already spent.
    cites = {"type": "string", "maxLength": 120}
    rule_cites = {"type": "string", "maxLength": 100}

    block_core = {
        "cites": cites,
        "resident": {"enum": resident_ids},
        "activity": {"enum": ACTIVITY_VOCAB},
        # Sleep is declared, not inferred from the activity's name: both
        # export_bank and the v1 simulator detect sleep by substring, while
        # the model names a block for what it MEANS ("morning_rest"). It
        # answers a boolean; expand_calendar guarantees the name.
        # Declared BEFORE skip_p: choosing skip_p first produced sleep
        # blocks marked skippable ("a resident does not skip sleeping"),
        # which is much harder to write once sleep is already committed.
        "sleep": {"type": "boolean"},
        "start": {"type": "string", "pattern": TIME_PATTERN},
        "end": {"type": "string", "pattern": TIME_PATTERN},
        "at": {"enum": receptacle_ids + ["ELSEWHERE"]},
        "jitter": {"enum": JITTER_CLASS_NAMES},
        "skip_p": {"type": "number", "minimum": 0.0,
                   "maximum": params["skip"]["max_skip_p"]},
        "note": {"type": "string", "maxLength": 200},
    }
    # No `uniqueItems` on `days`: xgrammar rejects the keyword outright
    # ("Grammar error: Unimplemented keys"), so validate.check_referential
    # catches a repeated weekday instead.
    weekly_block = {
        "type": "object", "additionalProperties": False,
        "required": ["resident", "activity", "days", "start", "end", "at",
                     "jitter", "skip_p", "sleep", "cites"],
        "properties": _insert_after(block_core, "sleep", days={
            "type": "array", "minItems": 1, "maxItems": 7,
            "items": {"enum": DAY_ABBREV}}),
    }
    # After-only rules (the v3 object semantics): while an activity is
    # underway the object is simply WITH the resident using it — the
    # expander synthesizes that leg — so the model authors only where the
    # object LANDS when the activity ends, always as a distribution.
    # "NO_OP" is a first-class outcome: the mass on it is the chance this
    # firing leaves the object where it is (for a rarely-handled object,
    # most of the mass). dest/p/else and the during phase are gone from
    # the grammar entirely — unwritable beats advised-against.
    rule = {
        "type": "object", "additionalProperties": False,
        "required": ["cites", "activity", "phase", "dist"],
        "properties": {
            # Order is background -> reasoning -> decision: `cites` first,
            # then the activity it licenses, then the outcome distribution.
            # When the calendar is authored FIRST (the split pipeline),
            # the enum is pinned to activities it actually schedules — an
            # orphaned rule becomes unwritable, the same grammar trick
            # that killed vacuous special-event drops.
            "cites": rule_cites,
            "activity": {"enum": (scheduled_activities or ACTIVITY_VOCAB)},
            "phase": {"const": "after"},
            "only_from": {"type": "array", "minItems": 1, "maxItems": 8,
                          "items": {"enum": locations}},
            "dist": {"type": "array", "minItems": 2, "maxItems": 6,
                     "items": {"type": "object",
                               "additionalProperties": False,
                               "required": ["dest", "p"],
                               "properties": {
                                   "dest": {"enum": locations + ["NO_OP"]},
                                   "p": prob}}},
            # Authoring-order hint: the model never writes it (order is
            # derived), the revamp_v1 translation uses it to reproduce that
            # world's per-activity rule order, which its RNG depends on.
            "seq": {"type": "integer", "minimum": 0},
        },
    }

    def object_rule(only: str | None = None) -> dict:
        # ONE shape for every object. The old static/mobile oneOf (and the
        # `motion: rarely_moved` flag) is retired: with NO_OP a rarely
        # moved object is a dist with most of its mass on NO_OP — a
        # probability statement instead of a special case. `rules: []`
        # stays legal for an object genuinely nothing touches.
        # `misplace_set` is gone too: drift lands near wherever the owner
        # actually is (the expander derives candidate spots from the
        # household's own occupied rooms); the model authors only the RATE.
        return {
            "type": "object", "additionalProperties": False,
            "required": ["object", "cites", "home", "rules"],
            "properties": {
                "object": {"const": only} if only else {"enum": object_ids},
                "cites": cites,
                "home": {"enum": locations},
                "p_misplace": prob,
                "rules": {"type": "array", "minItems": 0, "maxItems": 8,
                          "items": rule},
            },
        }

    activity = {
        "type": "object", "additionalProperties": False,
        "required": ["name"],
        "properties": {
            "name": {"enum": ACTIVITY_VOCAB},
            "reset_all": {
                "type": "object", "additionalProperties": False,
                "required": ["p"],
                "properties": {"p": prob,
                               "objects": {"type": "array", "minItems": 1,
                                           "items": {"enum": object_ids}}}},
            "fragment": {
                "type": "object", "additionalProperties": False,
                "required": ["mean_bouts"],
                "properties": {"mean_bouts": {
                    "type": "number",
                    "minimum": params["fragmentation"]["min_mean_bouts"],
                    "maximum": params["fragmentation"]["max_mean_bouts"]}}},
            "cites": cites,
        },
    }
    js = params["jitter_scale"]
    return {
        "type": "object", "additionalProperties": False,
        # arc_events (special events) moved to their OWN call
        # (build_special_schema): they are authored AFTER the calendar
        # exists, conditioned on it, so the drop enum can be pinned to
        # activities that actually run.
        "required": ["household", "source_persona", "days", "day0",
                     "residents", "sleep_schedule", "weekly_blocks",
                     "object_rules", "activities"],
        "properties": {
            "household": {"const": household_id},
            "source_persona": {"const": "persona.yaml"},
            "days": {"const": days},
            "day0": {"const": "Monday"},
            # Slot i is pinned to resident i, exactly as object_rules pins
            # slot i to object i. Left as a plain enum, a five-person
            # household came back as
            # [resident_1, resident_1, resident_1, resident_2, resident_2]
            # — the right LENGTH, three people missing — and the same in
            # sleep_schedule, so "everybody sleeps, once each" failed for
            # reasons no prompt wording fixes.
            "residents": {
                "type": "array", "minItems": len(resident_ids),
                "maxItems": len(resident_ids), "items": False,
                "prefixItems": [
                    {"type": "object", "additionalProperties": False,
                     "required": ["id", "jitter_scale"],
                     "properties": {
                         "id": {"const": rid},
                         "jitter_scale": {"type": "number",
                                          "minimum": js["min"],
                                          "maximum": js["max"]},
                         "cites": cites}}
                    for rid in resident_ids]},
            # One sleep block per resident, structurally — same pinning.
            "sleep_schedule": {
                "type": "array", "minItems": len(resident_ids),
                "maxItems": len(resident_ids), "items": False,
                "prefixItems": [
                    {"type": "object", "additionalProperties": False,
                     "required": ["resident", "activity", "days",
                                  "start", "end", "at", "jitter"],
                     "properties": {
                         "resident": {"const": rid},
                         "activity": {"enum": ACTIVITY_VOCAB},
                         "days": {"type": "array", "minItems": 1,
                                  "maxItems": 7,
                                  "items": {"enum": DAY_ABBREV}},
                         "start": {"type": "string",
                                   "pattern": TIME_PATTERN},
                         "end": {"type": "string",
                                 "pattern": TIME_PATTERN},
                         "at": {"enum": receptacle_ids},
                         "jitter": {"enum": JITTER_CLASS_NAMES},
                         "cites": cites}}
                    for rid in resident_ids]},
            # Sleep has its own section, so this floor covers waking life.
            "weekly_blocks": {"type": "array", "minItems": 2, "maxItems": 80,
                              "items": weekly_block},
            # `prefixItems` pins slot i to object i, so the array cannot
            # name one object twice and silently drop another — which is
            # exactly what a 40-object household did, every attempt, when
            # only the LENGTH was fixed. The model now answers "what
            # happens to THIS object" forty times, in a fixed order,
            # instead of having to keep its own tally.
            "object_rules": {"type": "array", "minItems": len(object_ids),
                             "maxItems": len(object_ids),
                             "prefixItems": [object_rule(o)
                                             for o in object_ids],
                             "items": False},
            "activities": {"type": "array", "minItems": 1, "maxItems": 40,
                           "items": activity},
        },
    }


def build_calendar_schema(household_id: str, resident_ids: list[str],
                          receptacle_ids: list[str], days: int,
                          params: dict) -> dict:
    """Stage 1 of the split pipeline: the schedule alone — the program
    schema with object_rules carved out. One source of truth: carved from
    build_program_schema rather than restated."""
    full = build_program_schema(household_id, resident_ids, ["_none_"],
                                receptacle_ids, days, params)
    props = {k: v for k, v in full["properties"].items()
             if k != "object_rules"}
    return dict(full, properties=props,
                required=[k for k in full["required"] if k != "object_rules"])


def build_objects_schema(household_id: str, resident_ids: list[str],
                         object_ids: list[str], receptacle_ids: list[str],
                         days: int, params: dict,
                         scheduled_activities: list[str]) -> dict:
    """Stage 2: object_rules alone, with the rule activity enum PINNED to
    what stage 1 actually scheduled."""
    full = build_program_schema(household_id, resident_ids, object_ids,
                                receptacle_ids, days, params,
                                scheduled_activities=sorted(
                                    set(scheduled_activities)))
    return {"type": "object", "additionalProperties": False,
            "required": ["object_rules"],
            "properties": {"object_rules":
                           full["properties"]["object_rules"]}}


def build_special_schema(days: int, scheduled_activities: list[str],
                         resident_ids: list[str],
                         receptacle_ids: list[str], object_ids: list[str],
                         params: dict) -> dict:
    """The special-events contract — its OWN call, made AFTER the routine
    program is accepted, so it conditions on the calendar that actually
    exists: `drop` is enum-pinned to activities the program schedules
    (a vacuous or unknown drop is unwritable, retiring the single largest
    historical source of rejected programs), while `add` may introduce any
    vocabulary activity (an appointment the routine never runs is exactly
    the point of an exception)."""
    locations = receptacle_ids + ["ELSEWHERE"] + \
        [f"person:{r}" for r in resident_ids]
    prob = {"type": "number", "minimum": 0.0, "maximum": 1.0}
    add_block = {
        "type": "object", "additionalProperties": False,
        "required": ["cites", "resident", "activity", "start", "at",
                     "jitter"],
        "properties": {
            "cites": {"type": "string", "maxLength": 120},
            "resident": {"enum": resident_ids},
            "activity": {"enum": ACTIVITY_VOCAB},
            "start": {"type": "string", "pattern": TIME_PATTERN},
            "end": {"type": "string", "pattern": TIME_PATTERN},
            "at": {"enum": receptacle_ids + ["ELSEWHERE"]},
            "jitter": {"enum": JITTER_CLASS_NAMES},
            "note": {"type": "string", "maxLength": 200},
        },
    }
    override_rule = {
        "type": "object", "additionalProperties": False,
        "required": ["object", "dist"],
        "properties": {
            "object": {"enum": object_ids},
            "dist": {"type": "array", "minItems": 2, "maxItems": 6,
                     "items": {"type": "object",
                               "additionalProperties": False,
                               "required": ["dest", "p"],
                               "properties": {
                                   "dest": {"enum": locations + ["NO_OP"]},
                                   "p": prob}}},
        },
    }
    event = {
        "type": "object", "additionalProperties": False,
        "required": ["note", "day", "patch"],
        "properties": {
            # note first: the beat is the reason the patch exists.
            "note": {"type": "string", "minLength": 1, "maxLength": 300},
            "day": {"type": "integer", "minimum": 0, "maximum": days - 1},
            "patch": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "drop": {"type": "array", "minItems": 1,
                             "items": {"enum": (scheduled_activities
                                                or ACTIVITY_VOCAB)}},
                    "add": {"type": "array", "minItems": 1,
                            "items": add_block},
                    "after_override": {
                        "type": "array", "minItems": 1,
                        "items": {"type": "object",
                                  "additionalProperties": False,
                                  "required": ["activity", "rule"],
                                  "properties": {
                                      "activity": {
                                          "enum": (scheduled_activities
                                                   or ACTIVITY_VOCAB)},
                                      "rule": override_rule}}},
                },
            },
        },
    }
    return {"type": "object", "additionalProperties": False,
            "required": ["special_events"],
            "properties": {"special_events": {
                "type": "array", "minItems": 4, "maxItems": 8,
                "items": event}}}


def build_leak_schema(household_types: list[str]) -> dict:
    return {
        "type": "object", "additionalProperties": False,
        "required": ["predicted_type", "confidence", "reason"],
        "properties": {
            "predicted_type": {"enum": household_types},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "reason": {"type": "string", "maxLength": 300},
        },
    }
