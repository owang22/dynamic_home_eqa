"""Prompts for the tree arm: installation (roots), revision (add_child /
add_root), repair; plus the anonymization helpers for node bodies.

Every sentence here is MECHANICS — what the fields are, how a check is
resolved, which two operations exist — stated in the affirmative. The
prompts carry no advice about how homes work and no prohibitions
(:data:`FORBIDDEN_PROMPT_STRINGS` is what the tests grep the rendered
text for). Word counts and negation-free phrasing are deliberate: the
Phase-2 graph prompts told the model what it could NOT do and it did it
anyway; here the operation list is the whole contract.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from baselines.llm_hypotheses.prompt import (SCHEMA_NOTE,
                                             _EXAMPLE_TOKEN_MAP,
                                             anonymize_hypothesis,
                                             build_anonymization_maps,
                                             deanonymize_hypothesis,
                                             person_sensing_sections,
                                             tour_stamp, vocabulary_tables)
from baselines.types import Episode

FORBIDDEN_PROMPT_STRINGS = (
    "do not", "don't", "never", " not ", "cannot", "edit_leaf", "drop_leaf",
    "set_rest", "NOT FOUND", "not seen", "misplace", "forgot",
    "assumption")
"""Strings no rendered tree prompt may contain: negations, retired
operation names, and world-advice words. ``carry`` is checked as a whole
word by the test (the mandated ON_PERSON sentence says "carrying")."""

FORBIDDEN_WORD_RE = re.compile(r"\b(carry|carried|carries)\b", re.I)

TREE_EXAMPLE_OUTPUT = {
    "nodes": [
        {"node_id": "p_a41c", "parent": None,
         "labels": ["two_adults", "both_commute"],
         "rationale": "two commuters; the home is empty on weekdays",
         "distinguishing_prediction": "keys_x are away from the entry "
                                      "shelf at weekday midday",
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 13.0,
                                  "if_seen": "wrong"},
         "rest": {"class:mug": "cupboard_1", "keys_x": "entry_shelf_1"},
         "activities": [
             {"name": "office_day", "days": "weekday",
              "frequency_per_week": 5, "start_hour": 8.0,
              "duration_h": 9.0,
              "moves": [
                  {"target": "keys_x", "to": "OUT_OF_HOUSE",
                   "chance": "almost_always"}]},
             {"name": "morning_coffee", "days": "both",
              "frequency_per_week": 6, "start_hour": 6.5,
              "duration_h": 0.5,
              "moves": [
                  {"target": "class:mug", "to": "counter_1",
                   "chance": "usually", "duration_h": 4.0}]}]},
        {"node_id": "p_9f02", "parent": None,
         "labels": ["two_adults", "one_at_home"],
         "rationale": "one partner commutes, the other works at the desk",
         "distinguishing_prediction": "keys_x on the entry shelf at "
                                      "weekday midday",
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 13.0,
                                  "if_seen": "right"},
         "rest": {"class:mug": "desk_1"},
         "activities": [
             {"name": "desk_work", "days": "weekday",
              "frequency_per_week": 5, "start_hour": 9.0,
              "duration_h": 7.0,
              "moves": [
                  {"target": "class:mug", "to": "desk_1",
                   "chance": "usually", "duration_h": 12.0}]}]},
    ]
}

TREE_EXAMPLE_OPERATIONS = {
    "operations": [
        {"op": "add_child", "parent": "p_9f02",
         "labels_added": ["evening_gym"],
         "rationale": "the one at home goes out on weekday evenings",
         "distinguishing_prediction": "keys_x away from the entry shelf "
                                      "around 19:00 on weekdays",
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 19.0,
                                  "if_seen": "wrong"},
         "delta": {
             "activities_added": [
                 {"name": "gym", "days": "weekday", "frequency_per_week": 3,
                  "start_hour": 18.0, "duration_h": 2.0,
                  "moves": [{"target": "keys_x", "to": "OUT_OF_HOUSE",
                             "chance": "usually"}]}],
             "moves_changed": [],
             "rest_overrides": {}}},
        {"op": "add_root",
         "body": {"labels": ["one_adult", "shift_work"],
                  "rationale": "one resident on a night shift",
                  "distinguishing_prediction": "keys_x on the entry shelf "
                                               "at weekday midday and gone "
                                               "at midnight",
                  "distinguishing_check": {"target": "keys_x",
                                           "at": "entry_shelf_1",
                                           "days": "weekday", "hour": 23.5,
                                           "if_seen": "wrong"},
                  "rest": {"keys_x": "entry_shelf_1"},
                  "activities": [
                      {"name": "night_shift", "days": "weekday",
                       "frequency_per_week": 4, "start_hour": 22.0,
                       "duration_h": 2.0,
                       "moves": [{"target": "keys_x", "to": "OUT_OF_HOUSE",
                                  "chance": "almost_always"}]}]}},
    ]
}

_ACTIVITY_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "days": {"type": "string", "enum": ["weekday", "weekend", "both"]},
        "frequency_per_week": {"type": "number"},
        "start_hour": {"type": "number"},
        "duration_h": {"type": "number"},
        "moves": {"type": "array", "items": {
            "type": "object",
            "properties": {"target": {"type": "string"},
                           "to": {"type": "string"},
                           "chance": {"type": "string",
                                      "enum": ["rarely", "sometimes",
                                               "usually", "almost_always"]},
                           "duration_h": {"type": "number"}},
            "required": ["target", "to", "chance"]}}},
    "required": ["name", "days", "frequency_per_week", "start_hour",
                 "duration_h", "moves"]}

_CHECK_SCHEMA = {
    "type": "object",
    "properties": {"target": {"type": "string"}, "at": {"type": "string"},
                   "days": {"type": "string",
                            "enum": ["weekday", "weekend", "both"]},
                   "hour": {"type": "number"},
                   "if_seen": {"type": "string", "enum": ["right", "wrong"]}},
    "required": ["target", "at", "days", "hour", "if_seen"]}

_ROOT_BODY_SCHEMA = {
    "type": "object",
    "properties": {
        "node_id": {"type": "string"},
        "parent": {"type": ["string", "null"]},
        "labels": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
        "distinguishing_prediction": {"type": "string"},
        "distinguishing_check": _CHECK_SCHEMA,
        "rest": {"type": "object", "additionalProperties": {"type": "string"}},
        "activities": {"type": "array", "items": _ACTIVITY_SCHEMA}},
    "required": ["labels", "rationale", "distinguishing_check", "rest",
                 "activities"]}

TREE_SCHEMA = {
    "type": "object",
    "properties": {"nodes": {"type": "array", "items": _ROOT_BODY_SCHEMA}},
    "required": ["nodes"]}
"""Guided-decoding schema for the installation tree (salvage stage)."""

TREE_OPERATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "operations": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "enum": ["add_child", "add_root"]},
                "parent": {"type": "string"},
                "labels_added": {"type": "array",
                                 "items": {"type": "string"}},
                "rationale": {"type": "string"},
                "distinguishing_prediction": {"type": "string"},
                "distinguishing_check": _CHECK_SCHEMA,
                "delta": {
                    "type": "object",
                    "properties": {
                        "activities_added": {"type": "array",
                                             "items": _ACTIVITY_SCHEMA},
                        "moves_changed": {"type": "array", "items": {
                            "type": "object",
                            "properties": {
                                "activity": {"type": "string"},
                                "moves": _ACTIVITY_SCHEMA["properties"]["moves"]},
                            "required": ["activity", "moves"]}},
                        "rest_overrides": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}}}},
                "body": _ROOT_BODY_SCHEMA},
            "required": ["op"]}}},
    "required": ["operations"]}
"""Guided-decoding schema for a revision's operation list."""


def example_text(example: Mapping[str, Any], anonymized: bool) -> str:
    text = json.dumps(example, indent=1)
    if anonymized:
        for token in sorted(_EXAMPLE_TOKEN_MAP, key=len, reverse=True):
            text = text.replace(token, _EXAMPLE_TOKEN_MAP[token])
    return text


# ------------------------------------------------------- anonymization

def _translate_node(node: Mapping[str, Any], fn) -> dict:
    """Apply a hypothesis translator to a node's id-bearing fields."""
    out = dict(node)
    body = {"rest": node.get("rest") or {},
            "activities": node.get("activities") or [],
            "distinguishing_check": node.get("distinguishing_check")}
    done = fn(body)
    if "rest" in node:
        out["rest"] = done["rest"]
    out["activities"] = done["activities"]
    if node.get("distinguishing_check"):
        out["distinguishing_check"] = done["distinguishing_check"]
    if node.get("rest_overrides"):
        out["rest_overrides"] = fn({"rest": node["rest_overrides"],
                                    "activities": []})["rest"]
    if node.get("moves_changed"):
        out["moves_changed"] = [
            {"activity": c.get("activity"),
             "moves": fn({"rest": {}, "activities": [
                 {"moves": c.get("moves", [])}]})["activities"][0]["moves"]}
            for c in node["moves_changed"]]
    return out


def anonymize_tree(payload: Mapping[str, Any], omap, rmap, cmap) -> dict:
    fn = lambda b: anonymize_hypothesis(b, omap, rmap, cmap)
    return {"nodes": [_translate_node(n, fn) for n in payload.get("nodes", ())]}


def deanonymize_tree(payload: Mapping[str, Any], omap, rmap, cmap) -> dict:
    fn = lambda b: deanonymize_hypothesis(b, omap, rmap, cmap)
    return {"nodes": [_translate_node(n, fn) for n in payload.get("nodes", ())]}


def deanonymize_tree_operations(operations: Sequence[Mapping[str, Any]],
                                omap, rmap, cmap) -> List[dict]:
    fn = lambda b: deanonymize_hypothesis(b, omap, rmap, cmap)
    out = []
    for op in operations:
        op = dict(op)
        if isinstance(op.get("body"), Mapping):
            op["body"] = _translate_node(op["body"], fn)
        if isinstance(op.get("distinguishing_check"), Mapping):
            op["distinguishing_check"] = fn(
                {"rest": {}, "activities": [],
                 "distinguishing_check": op["distinguishing_check"]}
            )["distinguishing_check"]
        if isinstance(op.get("delta"), Mapping):
            delta = dict(op["delta"])
            node = _translate_node(
                {"activities": delta.get("activities_added") or [],
                 "rest_overrides": delta.get("rest_overrides") or {},
                 "moves_changed": delta.get("moves_changed") or []}, fn)
            delta["activities_added"] = node["activities"]
            if delta.get("rest_overrides"):
                delta["rest_overrides"] = node["rest_overrides"]
            if delta.get("moves_changed"):
                delta["moves_changed"] = node["moves_changed"]
            op["delta"] = delta
        out.append(op)
    return out


# ------------------------------------------------------------- prompts

MECHANICS = """How the fields work:

- A node is one full description of the home's weekly routine: a `rest` map (where each object, or `class:<name>`, sits when nothing is happening) and a list of ACTIVITIES. An activity has a name, `days` (weekday, weekend, or both), `start_hour` (a number), `duration_h`, `frequency_per_week`, and `moves`: which object or class goes to which receptacle, with a `chance` (one of rarely, sometimes, usually, almost_always) and, when it differs from the activity's, its own `duration_h` — how long the object stays where the activity put it.
- `labels` are short free-text tags for the facts about the household this node assumes (for example who lives here, or where the primary resident is on weekdays). Each node has a different label set from every other node.
- `distinguishing_check` is {"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>, "if_seen": right|wrong}: a look at `at` around that hour that finds the target resolves the node as `if_seen`; an empty look resolves it the other way. A move whose destination is `OUT_OF_HOUSE` or `ON_PERSON` is supported by empty looks at the object's rest receptacle inside the move's window and weakened by looks that find it there; its check names that rest receptacle with `if_seen: wrong`.
- Times and weekly frequencies are numbers with your best guess; the sightings adjust them. Chances are the four labels above.
- Identifiers come from the tables, exactly as printed; each JSON field holds the bare id.
- `node_id` is an opaque token: `p_` followed by 4 hex characters chosen at random."""


def tree_tour_start_prompt(episode: Episode, anonymized: bool = False
                           ) -> Tuple[str, dict]:
    """The installation prompt: tables with the tour's sightings, the
    tour time, the mechanics, and a request for 3 to 5 ROOT nodes."""
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap, tour=True)
    mechanics = MECHANICS
    if anonymized:
        mechanics = (mechanics.replace("`OUT_OF_HOUSE`", f"`{rmap['OUT_OF_HOUSE']}`")
                     .replace("`ON_PERSON`", f"`{rmap['ON_PERSON']}`"))
    user = f"""A home robot has just been installed. Its only observation so far is one walkthrough of the home at {tour_stamp(episode.tour_t)}. Below are the home's receptacles and the objects the walkthrough saw, each with where it was. The home may hold further objects the walkthrough missed; those join your `class:<name>` rules and rest entries automatically once the robot meets them, so the ids below are the complete vocabulary for now.

{tables}

Write 3 to 5 competing ROOT nodes for this home's weekly routine. Each root is a complete description with its own `labels`, `rationale`, `distinguishing_prediction`, `distinguishing_check`, `rest` and `activities`, and every pair of roots differs in its label set and in something the robot's looks can settle. Give every object a rest entry (directly or through its class). Later, as sightings arrive, you will be shown how each node did and asked to refine the tree by adding children under the nodes the evidence favours.

{mechanics}

Think it through, then end your reply with one json object of the form {{"nodes": [...]}} in which every node has "parent": null. {SCHEMA_NOTE}

{example_text(TREE_EXAMPLE_OUTPUT, anonymized)}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}


def _history_text(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return "check untested so far"
    hits = sum(1 for r in rows if r["in_favour"])
    return f"check came true {hits}/{len(rows)} times"


def tree_revision_prompt(report: Mapping[str, Any], tables: str,
                         tree_json: str, omap: Mapping[str, str] | None = None,
                         rmap: Mapping[str, str] | None = None) -> str:
    """The tree arm's revision prompt (module docstring): tree with
    weights and check history, settled labels, the anomaly keys at
    threshold, rules held and failed per node, statistics, the tables,
    the current tree as JSON, the two operations."""
    o = omap or {}
    r = rmap or {}
    def obj(x): return o.get(x, x)
    def rec(x): return r.get(x, x)
    day = report["day"]
    nodes = report.get("tree_nodes", [])
    tree_lines = []
    for n in nodes:
        indent = "  " * (1 + n.get("depth", 0))
        parent = f"child of {n['parent']}" if n.get("parent") else "root"
        tree_lines.append(
            f"{indent}{n['node_id']} ({parent}; labels {', '.join(n['labels'])}): "
            f"weight {n['weight']:.2f}, subtree {n['subtree_weight']:.2f}; "
            f"{_history_text(n.get('check_history', []))}")
    tree_text = "\n".join(tree_lines) or "  (empty)"
    settled = report.get("settled_labels", {})
    settled_text = ", ".join(f"{l} ({w:.2f})" for l, w in settled.items()) \
        or "(none yet)"
    label_text = ", ".join(f"{l} {w:.2f}" for l, w in
                           report.get("label_weights", {}).items()) or "(none)"
    if report.get("statistical_weight") is not None:
        stat = (f"A plain statistical model (each object where it was most "
                f"often seen) competes for the same weight and holds "
                f"{report['statistical_weight']:.2f} of the mixture.")
    else:
        stat = ""
    bucket = "\n".join(
        f"  {obj(b['object'])} seen at {rec(b['receptacle'])} around "
        f"{b['hour_bin'] * 2:02d}:00-{b['hour_bin'] * 2 + 2:02d}:00 on "
        f"{b['count']} occasions; the best node gave it {b['max_p']:.2f}"
        for b in report.get("anomaly_bucket", [])) or "  (empty)"
    held = "\n".join(
        f"  {h['hypothesis_id']}/{h['activity']}: {obj(h['target'])} -> "
        f"{rec(h['to'])} held ({h['fitted_chance']:.2f} on "
        f"{h['evidence']:.0f} sightings)"
        for h in report["rules_held"]) or "  (none yet)"
    failed = "\n".join(
        f"  {h['hypothesis_id']}/{h['activity']}: {obj(h['target'])} -> "
        f"{rec(h['to'])} failed ({h['fitted_chance']:.2f} on "
        f"{h['evidence']:.0f} sightings)"
        for h in report["rules_failed"]) or "  (none)"
    misses = "\n".join(
        f"  {obj(m['object'])}: predicted {rec(m['predicted'])}, actually "
        f"{rec(m['actual'])} — {m['count']}x, e.g. day {m['example_day']} "
        f"{m['example_hour']:02d}:00"
        for m in report["worst_objects"]) or "  (none)"
    uncovered = "\n".join(
        f"  {obj(u['object'])}: {u['summary']}"
        for u in report["uncovered_objects"]) or "  (none)"
    def _away_line(a: Mapping[str, Any]) -> str:
        line = (f"  {obj(a['object'])} during {a['windows']}: looks at its "
                f"stated rest {rec(a['rest'])} empty {a['empty']}, found "
                f"{a['found']}")
        if a.get("modal_empty") is not None:
            line += (f"; looks at {rec(a['modal'])}, where it is sighted "
                     f"most, empty {a['modal_empty']}, found "
                     f"{a['modal_found']}")
        return line
    away_looks = "\n".join(_away_line(a) for a in
                            report.get("away_window_looks", [])) or "  (none)"
    people = person_sensing_sections(report, o, r)
    people = f"\n{people}\n" if people else ""
    trigger = report.get("trigger", "scheduled")
    mechanics = MECHANICS
    if r:
        mechanics = (mechanics.replace("`OUT_OF_HOUSE`", f"`{rec('OUT_OF_HOUSE')}`")
                     .replace("`ON_PERSON`", f"`{rec('ON_PERSON')}`"))
    return f"""It is now day {day}. The robot has been watching since the tree was written; here is how each node did. Refine the tree with OPERATIONS: add a child under a node to state a more specific version of it, or add a new root for a routine the tree lacks. Every existing node stays exactly as it is, with the weight it has earned, and competes with the new ones.
This call was triggered by: {trigger}.

THE TREE (weight = share of the node weight this node earns from the sightings; subtree = this node plus its descendants):
{tree_text}
Label weights (share of node weight held by nodes with each label): {label_text}
Settled labels (at or above {report.get('settled_floor', 0.9):.2f}): {settled_text}
{stat}

REPEATED SIGHTINGS THE TREE MISSED (each seen on 3 or more occasions with every node giving it under 0.05):
{bucket}

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was, since the last revision:
{misses}

RULES THAT HELD UP (object was where the rule said, during its activity; tagged node/activity):
{held}

RULES THAT FAILED (object was elsewhere during the rule's activity; tagged node/activity):
{failed}

OBJECTS OUTSIDE EVERY NODE (no rule and no rest entry mentions them), with what the sightings show:
{uncovered}

{report['statistics']}

EMPTY LOOKS DURING MODELED AWAY WINDOWS (for each object some node sends out of the house: looks inside that window at its stated rest, and at the receptacle it is sighted at most, that found nothing versus looks that found it; only positive sightings appear in the statistics above, so this is the evidence for a move ending out of the house):
{away_looks}
{people}
The valid identifiers are these, exactly as printed:

{tables}

THE CURRENT TREE AS JSON:

{tree_json}

{mechanics}

The two operations:
  {{"op": "add_child", "parent": "p_xxxx", "labels_added": ["<new label>"], "rationale": "...", "distinguishing_prediction": "...", "distinguishing_check": {{...}}, "delta": {{"activities_added": [...complete activities...], "moves_changed": [{{"activity": "<inherited activity name>", "moves": [...its complete new move list...]}}], "rest_overrides": {{"<object or class:name>": "<receptacle>"}}}}}}
    The child holds every label of its parent plus `labels_added`, inherits the parent's rest and activities, and applies the delta on top: `activities_added` are appended, `moves_changed` replaces the moves of the named inherited activity, `rest_overrides` changes the stated rest of the listed objects (a stated rest is a starting guess that the sightings outvote within days). A child adds at least one label and at least one change.
  {{"op": "add_root", "body": {{"labels": [...], "rationale": "...", "distinguishing_prediction": "...", "distinguishing_check": {{...}}, "rest": {{...}}, "activities": [...]}}}}
    A root is a complete description with a label set distinct from every existing node's.
The tree holds at most 12 nodes; nodes that stop earning weight are pruned automatically, and a pruned node's children move up to its parent with their bodies intact.

Read the evidence at the level it points to: a failed rule inside one node calls for a child of that node with `moves_changed`; a repeated sighting every node misses calls for a child with an `activities_added` under the best-placed node, or a new root when the routine fits none of them; a label whose weight has settled is a fact to build on. Think about what the mismatches imply, then end your reply with ONE json object of the form {{"operations": [...]}}. {SCHEMA_NOTE}

{example_text(TREE_EXAMPLE_OPERATIONS, bool(r))}"""


def tree_repair_prompt(problems: Sequence[str], tables: str, raw_json: str,
                       kind: str = "tree") -> str:
    """Repair round for an installation tree or an operation list: the
    exact problems, the tables, the previous JSON, and a request to
    reprint the whole object corrected."""
    listed = "\n".join(f"- {p}" for p in problems) or "- (none)"
    what = ("the COMPLETE corrected tree (every root)" if kind == "tree"
            else "the COMPLETE corrected operation list")
    return f"""Your previous output had these problems:

{listed}

The valid identifiers are these, exactly as printed:

{tables}

Here is your previous JSON:

{raw_json}

Reprint {what}, same shape, with every problem listed above fixed: replace invalid strings with identifiers from the tables (or remove the entry when nothing valid expresses it), keep node ids opaque (p_ plus 4 hex characters), keep every label set distinct, and stay within the caps. Keep the parts that were already valid as they are. End your reply with the JSON object only."""


__all__ = [
    "FORBIDDEN_PROMPT_STRINGS", "FORBIDDEN_WORD_RE", "MECHANICS",
    "TREE_EXAMPLE_OPERATIONS", "TREE_EXAMPLE_OUTPUT", "TREE_OPERATIONS_SCHEMA",
    "TREE_SCHEMA", "anonymize_tree", "deanonymize_tree",
    "deanonymize_tree_operations", "example_text", "tree_repair_prompt",
    "tree_revision_prompt", "tree_tour_start_prompt",
]
