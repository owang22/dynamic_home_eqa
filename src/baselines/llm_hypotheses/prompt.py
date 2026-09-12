"""Prompt construction for hypothesis elicitation, and the name
anonymizer.

Pure functions from an episode to strings, so tests can check the
prompt without a server. One call produces all hypotheses together
(the model needs to see the others to make them differ), reasoning
first, one JSON object last.

The anonymizer is the measurement instrument for the
named-vs-anonymized comparison: it replaces every object, class, and
receptacle name with a neutral numbered token (``object_1``,
``receptacle_1``, ``class_1``) at ONE choke point (the same discipline
as ``dynbelief.reflect.run``), builds the prompt from the anonymized
tables, and the elicitation driver translates the returned hypotheses
back to real IDs before anything downstream sees them.

Anonymized, NOT shuffled: names are removed, never reassigned to the
wrong object. A shuffle would feed the model actively misleading
semantics and measure something else entirely. The mapping is
deterministic (sorted order) and written out as a cross-reference
table by the elicitation driver, so any ``object_7`` in a prompt, log,
or hypothesis can be looked up later.

The model can still read the full sighting timeline under
anonymization, so whatever the named run gains over the anonymized one
comes from knowing what the objects ARE — that difference is the
measurement. No fuzzy matching anywhere: an ID either round-trips
through the maps exactly or the hypothesis fails validation.
"""

from __future__ import annotations

import collections
import json
from typing import Dict, List, Mapping, Tuple

from baselines.beliefs.hypothesis_program import ORDINAL_CENTERS
from baselines.types import DAY_SECONDS, Episode

ORDINAL_CHANCE_LABELS = tuple(ORDINAL_CENTERS)
"""The chance vocabulary, taken from the converter so the prompt, the
guided-decoding grammar, and the validator can never drift apart."""

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

N_HYPOTHESES = 5

EXAMPLE_OUTPUT = {
    "hypotheses": [
        {"hypothesis_id": "h1",
         "rationale": "single resident works away on weekdays; carry "
                      "items leave the house with them",
         "distinguishing_prediction": "keys_x absent from the entry "
                                      "table on weekday middays, back "
                                      "by 18:00",
         "rest": {"keys_x": "entry_shelf_1", "class:mug": "cupboard_1"},
         "activities": [
             {"name": "office_day", "days": "weekday",
              "frequency_per_week": 5, "start_hour": 8.0,
              "duration_h": 9.0,
              "moves": [
                  {"target": "keys_x", "to": "OUT_OF_HOUSE",
                   "chance": "almost_always", "after": "returned"}]},
             {"name": "morning_coffee", "days": "both",
              "frequency_per_week": 6, "start_hour": 6.5,
              "duration_h": 0.5,
              "moves": [
                  {"target": "class:mug", "to": "counter_1",
                   "chance": "usually", "after": "left"}]}]},
        {"hypothesis_id": "h2",
         "rationale": "resident mostly works from home; keys stay in",
         "distinguishing_prediction": "keys_x ON the entry table at "
                                      "weekday middays",
         "rest": {"keys_x": "entry_shelf_1", "class:mug": "desk_1"},
         "activities": [
             {"name": "desk_work", "days": "weekday",
              "frequency_per_week": 5, "start_hour": 9.0,
              "duration_h": 7.0,
              "moves": [
                  {"target": "class:mug", "to": "desk_1",
                   "chance": "usually", "after": "left"}]}]},
    ]
}


HYPOTHESES_SCHEMA = {
    "type": "object",
    "properties": {
        "hypotheses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hypothesis_id": {"type": "string"},
                    "rationale": {"type": "string"},
                    "distinguishing_prediction": {"type": "string"},
                    "rest": {"type": "object",
                             "additionalProperties": {"type": "string"}},
                    "activities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "days": {"type": "string",
                                         "enum": ["weekday", "weekend",
                                                  "both"]},
                                "frequency_per_week": {"type": "number"},
                                "start_hour": {"type": "number"},
                                "duration_h": {"type": "number"},
                                "moves": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "target": {"type": "string"},
                                            "to": {"type": "string"},
                                            "chance": {
                                                "type": "string",
                                                "enum": list(
                                                    ORDINAL_CHANCE_LABELS)},
                                            "after": {"type": "string",
                                                      "enum": ["returned",
                                                               "left"]}},
                                        "required": ["target", "to", "chance",
                                                     "after"]}}},
                            "required": ["name", "days",
                                         "frequency_per_week", "start_hour",
                                         "duration_h", "moves"]}}},
                "required": ["hypothesis_id", "rationale", "rest",
                             "activities"]}}},
    "required": ["hypotheses"],
}
"""Guided-decoding schema for the structured-output stage.

Constrains SHAPE and the closed vocabularies (day kinds, chance labels,
``after`` kinds) — everything a grammar can enforce. It deliberately
cannot constrain IDs: those are per-household and are checked by
:func:`~baselines.beliefs.hypothesis_program.parse_hypothesis`, which
reports exact offending strings for the repair round. Shape from the
grammar, vocabulary from the validator."""


_EXAMPLE_TOKEN_MAP = {
    "keys_x": "object_3", "class:mug": "class:class_2",
    "entry_shelf_1": "receptacle_1", "cupboard_1": "receptacle_4",
    "OUT_OF_HOUSE": "receptacle_9", "counter_1": "receptacle_2",
    "desk_1": "receptacle_5",
    "keys_x absent from the entry table on weekday middays, back by 18:00":
        "object_3 absent from receptacle_1 on weekday middays, back by "
        "18:00",
    "keys_x ON the entry table at weekday middays":
        "object_3 AT receptacle_1 at weekday middays",
}
"""The example rewritten for the anonymized condition: an example that
showed semantic tokens (OUT_OF_HOUSE, keys_x) would teach the model
vocabulary that does not exist in its anonymized tables, and it would
copy them straight into invalid output."""


def example_output_text(anonymized: bool) -> str:
    text = json.dumps(EXAMPLE_OUTPUT, indent=1)
    if anonymized:
        for token in sorted(_EXAMPLE_TOKEN_MAP, key=len, reverse=True):
            text = text.replace(token, _EXAMPLE_TOKEN_MAP[token])
    return text


# ----------------------------------------------------------- anonymization

def build_anonymization_maps(episode: Episode) -> Tuple[Dict[str, str],
                                                        Dict[str, str],
                                                        Dict[str, str]]:
    """Deterministic neutral-token maps (objects, receptacles, classes).

    Sorted order, not random: the measurement wants names REMOVED, not
    reassigned, and determinism keeps reruns and the cross-reference
    table byte-identical. Numbering starts at 1 and is NOT zero-padded
    (``object_1`` … ``object_35``), so tokens read the way the
    cross-reference table lists them."""
    omap = {obj: f"object_{i}"
            for i, obj in enumerate(sorted(episode.object_classes), 1)}
    rmap = {rec: f"receptacle_{i}"
            for i, rec in enumerate(sorted(episode.receptacle_ids), 1)}
    classes = sorted(set(episode.object_classes.values()))
    cmap = {cls: f"class_{i}" for i, cls in enumerate(classes, 1)}
    return omap, rmap, cmap


def crossref_table(episode: Episode, omap: Mapping[str, str],
                   rmap: Mapping[str, str],
                   cmap: Mapping[str, str]) -> str:
    """Markdown cross-reference: every anonymized token next to the real
    id it stands for. Written next to the elicitation logs so a token
    appearing in any prompt, think trace, or hypothesis can be looked
    up later."""
    lines = [f"# Anonymization cross-reference — {episode.household_id}",
             "", "## Objects", "",
             "| token | real object id | real class | class token |",
             "|---|---|---|---|"]
    for obj in sorted(episode.object_classes,
                      key=lambda o: int(omap[o].split("_")[1])):
        cls = episode.object_classes[obj]
        lines.append(f"| {omap[obj]} | {obj} | {cls} | {cmap[cls]} |")
    lines += ["", "## Receptacles", "", "| token | real receptacle id |",
              "|---|---|"]
    for rec in sorted(episode.receptacle_ids,
                      key=lambda r: int(rmap[r].split("_")[1])):
        lines.append(f"| {rmap[rec]} | {rec} |")
    lines += ["", "## Classes", "", "| token | real class |", "|---|---|"]
    for cls in sorted(cmap, key=lambda c: int(cmap[c].split("_")[1])):
        lines.append(f"| {cmap[cls]} | {cls} |")
    return "\n".join(lines) + "\n"


def deanonymize_hypothesis(raw: Mapping, omap: Dict[str, str],
                           rmap: Dict[str, str],
                           cmap: Dict[str, str]) -> dict:
    """Translate one anonymized-space hypothesis back to real IDs.

    Exact reverse-map lookups only; a token outside the maps passes
    through unchanged and then fails real-space validation loudly,
    which is the wanted behaviour (never guess)."""
    rev_o = {v: k for k, v in omap.items()}
    rev_r = {v: k for k, v in rmap.items()}
    rev_c = {v: k for k, v in cmap.items()}

    def target(token: str) -> str:
        if token.startswith("class:"):
            cls = token[len("class:"):]
            return "class:" + rev_c.get(cls, cls)
        return rev_o.get(token, token)

    out = dict(raw)
    out["rest"] = {target(str(k)): rev_r.get(str(v), str(v))
                   for k, v in dict(raw.get("rest", {})).items()}
    activities = []
    for act in raw.get("activities", ()):
        act = dict(act)
        act["moves"] = [dict(m, target=target(str(m.get("target", ""))),
                             to=rev_r.get(str(m.get("to", "")),
                                          str(m.get("to", ""))))
                        for m in act.get("moves", ())]
        activities.append(act)
    out["activities"] = activities
    return out


# ----------------------------------------------------------------- tables

def vocabulary_tables(episode: Episode,
                      omap: Mapping[str, str] | None = None,
                      rmap: Mapping[str, str] | None = None,
                      cmap: Mapping[str, str] | None = None) -> str:
    """The valid-ID tables the prompt states are the ONLY vocabulary."""
    o = omap or {}
    r = rmap or {}
    c = cmap or {}
    lines = ["RECEPTACLES (valid `to` and rest locations):"]
    for rec in episode.receptacle_ids:
        note = ""
        if rec in episode.unsensable_receptacle_ids:
            note = "  [never directly observable]"
        lines.append(f"  {r.get(rec, rec)}{note}")
    lines.append("")
    lines.append("OBJECTS (valid `target` ids, with class):")
    for obj in sorted(episode.object_classes):
        cls = episode.object_classes[obj]
        lines.append(f"  {o.get(obj, obj)}  (class: {c.get(cls, cls)})")
    lines.append("")
    classes = sorted(set(episode.object_classes.values()))
    lines.append("CLASSES (valid as `class:<name>` targets): "
                 + ", ".join(c.get(cls, cls) for cls in classes))
    return "\n".join(lines)


def sighting_digest(episode: Episode, warmup_days: int,
                    omap: Mapping[str, str] | None = None,
                    rmap: Mapping[str, str] | None = None) -> str:
    """Compact per-object timeline of the first ``warmup_days`` days.

    One line per (object, day) with sighting hours grouped by
    receptacle — not the raw log. Only positive sightings appear;
    the prompt separately explains that gaps are informative."""
    o = omap or {}
    r = rmap or {}
    per_object: Dict[str, Dict[int, List[Tuple[float, str]]]] = (
        collections.defaultdict(lambda: collections.defaultdict(list)))
    horizon = warmup_days * DAY_SECONDS
    for evidence in episode.evidence_stream():
        if evidence.t >= horizon:
            break
        day = evidence.t // DAY_SECONDS
        hour = (evidence.t % DAY_SECONDS) / 3600.0
        if hasattr(evidence, "contents"):
            for obj in evidence.contents:
                per_object[obj][day].append((hour, evidence.receptacle_id))
        else:
            per_object[evidence.object_id][day].append(
                (hour, evidence.receptacle_id))
    lines: List[str] = []
    for obj in sorted(episode.object_classes):
        lines.append(f"{o.get(obj, obj)}:")
        days = per_object.get(obj, {})
        if not days:
            lines.append("  never sighted in this period")
            continue
        for day in sorted(days):
            name = WEEKDAY_NAMES[day % 7]
            runs: List[str] = []
            for hour, rec in sorted(days[day]):
                token = r.get(rec, rec)
                stamp = f"{int(hour):02d}h"
                if runs and runs[-1].split(" ", 1)[1] == token:
                    head, _ = runs[-1].split(" ", 1)
                    runs[-1] = f"{head},{stamp} {token}"
                else:
                    runs.append(f"{stamp} {token}")
            lines.append(f"  d{day} {name}: " + "; ".join(runs))
    return "\n".join(lines)


# ----------------------------------------------------------------- prompt

SYSTEM_PROMPT = (
    "You are modelling how one household runs, for a home robot that "
    "must predict where objects are. You write competing hypotheses; a "
    "downstream statistical system converts them into probabilistic "
    "predictions and weighs them against future sightings. Be concrete "
    "and decisive; the sightings, not you, will settle who was right.")


def elicitation_prompt(episode: Episode, warmup_days: int,
                       anonymized: bool = False) -> Tuple[str, dict]:
    """The full user prompt, plus the maps used (empty when named)."""
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap)
    digest = sighting_digest(episode, warmup_days, omap, rmap)
    schema_text = example_output_text(anonymized)
    user = f"""A robot patrols a home a few times a day and records which objects it sees where. Below are the home's vocabulary tables and the first {warmup_days} days of its sighting log.

{tables}

SIGHTING LOG, days 0-{warmup_days - 1} (d0 is a Monday; hours are local; only positive sightings are recorded — an object missing from a day's log was simply not seen where the robot looked, which for portable items often means it was out of the house or on a person):

{digest}

Write exactly {N_HYPOTHESES} competing hypotheses about how this household works. Each hypothesis describes ACTIVITIES: what happens, which days (weekday, weekend, or both — mark this explicitly), roughly when, how many times per week, and which objects move where, plus a `rest` map saying where objects sit when nothing is going on.

Rules that matter:

1. Hypotheses must DISAGREE in ways sightings can settle. Two hypotheses predicting the same object in the same place at the same hour are wasted. Each hypothesis carries a one-line `distinguishing_prediction` naming a concrete observable difference from the others.
2. Cover every object, not only the interesting ones: every object id should appear in each hypothesis's `rest` map (directly or via its class).
3. Times and weekly frequencies: state them as numbers with your best guess ("dinner around 19:30" -> start_hour 19.5). They will be corrected by data, so a concrete guess beats a vague one.
4. Chances: NEVER numbers. Use exactly one of: rarely, sometimes, usually, almost_always.
5. `after` is "returned" (put back at rest when the activity ends) or "left" (stays where it was used until the next day). Distinguish objects put away after an activity from objects left where they were used.
6. Known failure modes to avoid: objects are often asked about while displaced, since queries cluster around activities — model the displacements, not just the rest states; the same resident can behave differently on weekdays and weekends; calling everything stationary is unfalsifiable and useless.
7. IDs: use ONLY identifiers from the tables above, exactly as printed. Nothing outside the tables is valid. You may put a short nickname in a parenthetical in your reasoning text, but every JSON field must contain the bare id.
8. One line of `rationale` per hypothesis.

Think it through first. Then end your reply with ONE json object, shaped exactly like this example (from a different, smaller home — do not copy its content):

{schema_text}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}
