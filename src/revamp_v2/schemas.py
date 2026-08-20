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

from prompts import (ACTIVITY_VOCAB, CARRIED_CLASSES, DAY_ABBREV,
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
        "required": ["household_id", "household_type", "residents",
                     "relationships", "home_layout_notes",
                     "daily_life_summary", "object_inventory", "quirks"],
        "properties": {
            "household_id": {"const": household_id},
            "household_type": {"const": household_type},
            "residents": {"type": "array", "minItems": n_residents,
                          "maxItems": n_residents, "items": resident},
            "relationships": {"type": "string", "maxLength": 900},
            "home_layout_notes": {"type": "string", "maxLength": 900},
            # Floor stays low and lets the persona prompt's own "object
            # counts should match household size" do the scaling (measured:
            # 8 objects for a solo home, 25 for a family of four). Forcing
            # a higher floor was tried and reverted — it does not make the
            # persona richer so much as it makes the L2 program harder to
            # get right, and every extra object is another chance for the
            # reachability lint to reject the whole program.
            # Declared BEFORE the inventory: what this household DOES
            # should choose what it owns. Written after, the objects were
            # picked first and the routine then described around them.
            "daily_life_summary": {"type": "string", "maxLength": 1200},
            "object_inventory": {"type": "array", "minItems": 8,
                                 "maxItems": 40, "items": obj},
            "quirks": {"type": "string", "maxLength": 600},
        },
    }



def build_program_schema(household_id: str, resident_ids: list[str],
                         object_ids: list[str], receptacle_ids: list[str],
                         days: int, params: dict,
                         object_owners: dict | None = None,
                         object_classes: dict | None = None) -> dict:
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
    arc_block = {
        "type": "object", "additionalProperties": False,
        "required": ["resident", "activity", "start", "at", "jitter"],
        "properties": dict(block_core),
    }

    rule = {
        "type": "object", "additionalProperties": False,
        "required": ["activity", "phase", "cites"],
        "properties": {
            # Order is background -> reasoning -> decision. `cites` is
            # required (optional, it appeared on 20.5% of rules, and the
            # no-op legs were the ones that skipped it) and sits after the
            # activity it licenses but BEFORE every choice it is supposed
            # to inform — declared last, it was a post-hoc caption on a
            # destination already fixed.
            "activity": {"enum": ACTIVITY_VOCAB},
            "phase": {"enum": ["during", "after"]},
            "cites": rule_cites,
            # Origin before destination, so a rule is authored as "from X
            # to Y" rather than a bare Y. Declared after `dest`, this only
            # gated a journey whose end had already been chosen.
            "only_from": {"type": "array", "minItems": 1, "maxItems": 8,
                          "items": {"enum": locations}},
            "dest": {"enum": locations},
            "p": prob,
            "else": {"enum": locations},
            "dist": {"type": "array", "minItems": 2, "maxItems": 5,
                     "items": {"type": "object",
                               "additionalProperties": False,
                               "required": ["dest", "p"],
                               "properties": {"dest": {"enum": locations},
                                              "p": prob}}},
            # Authoring-order hint: the model never writes it (order is
            # derived), the revamp_v1 translation uses it to reproduce that
            # world's per-activity rule order, which its RNG depends on.
            "seq": {"type": "integer", "minimum": 0},
            "cites": cites,
        },
    }

    def object_entry(lo: int, hi: int, only: str | None = None) -> dict:
        # One shape for every object. Carrying is a CHOICE the model makes
        # by homing an item at `person:<owner>` (the prompt encourages it
        # for pocket items where the persona supports it) — an earlier
        # design PINNED pocket items to their owner with mandatory pick-up
        # legs and mandatory drift, and overshot: wallets and glasses rode
        # their owners for 21 straight days without one put-down, tracing
        # zero receptacle changes. Structure forces what must ALWAYS hold;
        # who carries what, and when, is judgment.
        return {
            "type": "object", "additionalProperties": False,
            "required": (["object", "cites", "home", "motion", "rules"]
                         if lo == 0 else ["object", "cites", "home", "rules"]),
            "properties": {
                "object": {"const": only} if only else {"enum": object_ids},
                # Before `home`, which is the most consequential field in
                # the entry: it defines what counts as movement at all, and
                # was previously chosen with nothing reasoned in front of
                # it.
                "cites": cites,
                "home": {"enum": locations},
                # Staying put has to be something the model can SAY. Left
                # as the mere absence of rules, `rules: []` was chosen 0
                # times in 180 object entries: an absence is not an option
                # a generator picks. Asked instead to declare
                # `motion: rarely_moved`, it has a name for the honest
                # answer and stops faking movement to avoid the empty
                # array. NOTE: today this is still exactly "never" in
                # L3 — validate.py rejects p_misplace on a static and the
                # expander strips it — so the name currently buys honesty
                # and auditability, not motion. Giving `rarely` real
                # occasional displacement is a separate L3 change.
                **({"motion": {"const": "rarely_moved"}} if lo == 0 else {}),
                "p_misplace": prob,
                "misplace_set": {"type": "array", "minItems": 1,
                                 "maxItems": 6,
                                 "items": {"enum": receptacle_ids}},
                # For a moving object the first two rules are pinned to
                # the two legs of a journey: a `during` rule that takes it
                # somewhere when an activity starts, and an `after` rule
                # that says where it is left. Unpinned, the model wrote two
                # "put it back home" rules and the object never moved.
                "rules": ({"type": "array", "minItems": lo, "maxItems": hi,
                           "items": rule}
                          if lo == 0 else
                          {"type": "array", "minItems": lo, "maxItems": hi,
                           "prefixItems": [
                               dict(rule,
                                    required=rule["required"] + ["only_from"],
                                    properties=dict(
                                        rule["properties"],
                                        phase={"const": "during"})),
                               dict(rule, properties=dict(
                                   rule["properties"],
                                   phase={"const": "after"}))],
                           "items": rule}),
            },
        }

    # An object either never moves (no rules) or has AT LEAST TWO rules —
    # one taking it away from home, one bringing it back. A single rule is
    # almost always a homing rule pointing at the object's own home, which
    # reads as movement and is not: measured on a real generation, a third
    # of a 25-object household came back that way.
    def object_rule(only: str | None = None) -> dict:
        # A phone or a wallet that never moves is a broken household, not a
        # static object — no persona licenses it, so the static shape is
        # simply not offered for the classes people carry.
        if (object_classes or {}).get(only) in CARRIED_CLASSES:
            return object_entry(2, 8, only)
        return {"oneOf": [object_entry(0, 0, only), object_entry(2, 8, only)]}

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
    arc_event = {
        "type": "object", "additionalProperties": False,
        "required": ["day", "patch", "note"],
        "properties": {
            "day": {"type": "integer", "minimum": 0, "maximum": days - 1},
            "note": {"type": "string", "minLength": 1, "maxLength": 300},
            "patch": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "drop": {"type": "array", "minItems": 1,
                             "items": {"enum": ACTIVITY_VOCAB}},
                    "add": {"type": "array", "minItems": 1,
                            "items": arc_block},
                    "after_override": {
                        "type": "array", "minItems": 1,
                        "items": {"type": "object",
                                  "additionalProperties": False,
                                  "required": ["activity", "rule"],
                                  "properties": {
                                      "activity": {"enum": ACTIVITY_VOCAB},
                                      "rule": dict(
                                          rule,
                                          required=["object", "activity",
                                                    "phase"],
                                          properties=dict(
                                              rule["properties"],
                                              object={"enum": object_ids}))}}},
                },
            },
        },
    }

    js = params["jitter_scale"]
    return {
        "type": "object", "additionalProperties": False,
        "required": ["household", "source_persona", "days", "day0",
                     "residents", "sleep_schedule", "weekly_blocks",
                     "object_rules", "activities", "arc_events"],
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
            "arc_events": {"type": "array", "minItems": 4, "maxItems": 8,
                           "items": arc_event},
        },
    }


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
