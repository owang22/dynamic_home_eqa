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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

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
         "rationale": "one resident who is at an office on weekdays",
         "distinguishing_prediction": "keys_x are on the entry shelf on "
                                      "weekday evenings and gone by 9:00",
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 19.0},
         "rest": {"class:mug": "cupboard_1"},
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
        {"hypothesis_id": "h2",
         "rationale": "one resident who works at the desk at home",
         "distinguishing_prediction": "keys_x on the entry shelf at "
                                      "weekday midday",
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 13.0},
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
                    "distinguishing_check": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "at": {"type": "string"},
                            "days": {"type": "string",
                                     "enum": ["weekday", "weekend", "both"]},
                            "hour": {"type": "number"},
                            "if_seen": {"type": "string",
                                        "enum": ["right", "wrong"]}},
                        "required": ["target", "at", "days", "hour"]},
                    "rest": {"anyOf": [
                        {"type": "object",
                         "additionalProperties": {"type": "string"}},
                        {"type": "array", "items": {
                            "type": "object",
                            "properties": {"target": {"type": "string"},
                                           "at": {"type": "string"}},
                            "required": ["target", "at"]}}]},
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
                                            "duration_h": {
                                                "type": "number"}},
                                        "required": ["target", "to",
                                                     "chance"]}}},
                            "required": ["name", "days",
                                         "frequency_per_week", "start_hour",
                                         "duration_h", "moves"]}}},
                "required": ["hypothesis_id", "rationale", "rest",
                             "activities"]}}},
    "required": ["hypotheses"],
}
"""Guided-decoding schema for the structured-output stage.

Constrains SHAPE and the closed vocabularies (day kinds, chance
labels) — everything a grammar can enforce. It deliberately
cannot constrain IDs: those are per-household and are checked by
:func:`~baselines.beliefs.hypothesis_program.parse_hypothesis`, which
reports exact offending strings for the repair round. Shape from the
grammar, vocabulary from the validator."""


_EXAMPLE_TOKEN_MAP = {
    "keys_x": "object_3", "class:mug": "class:class_2",
    "entry_shelf_1": "receptacle_1", "cupboard_1": "receptacle_4",
    "OUT_OF_HOUSE": "receptacle_9", "counter_1": "receptacle_2",
    "desk_1": "receptacle_5",
    "keys_x are on the entry shelf on weekday evenings and gone by 9:00":
        "object_3 is at receptacle_1 on weekday evenings and gone by 9:00",
    "keys_x are gone from the entry shelf at weekday midday":
        "object_3 is gone from receptacle_1 at weekday midday",
    "keys_x on the entry shelf at weekday midday":
        "object_3 at receptacle_1 at weekday midday",
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


def anonymize_hypothesis(raw: Mapping, omap: Mapping[str, str],
                         rmap: Mapping[str, str],
                         cmap: Mapping[str, str]) -> dict:
    """Translate one real-id hypothesis INTO the anonymized vocabulary —
    the inverse of :func:`deanonymize_hypothesis`, used when a previous
    (real-id) hypothesis set is shown back to the model in the
    anonymized condition. Exact lookups; unknown tokens pass through."""
    def target(token: str) -> str:
        if token.startswith("class:"):
            cls = token[len("class:"):]
            return "class:" + cmap.get(cls, cls)
        return omap.get(token, token)

    out = dict(raw)
    out["rest"] = {target(str(k)): rmap.get(str(v), str(v))
                   for k, v in dict(raw.get("rest", {})).items()}
    out["activities"] = [
        dict(act, moves=[dict(m, target=target(str(m.get("target", ""))),
                              to=rmap.get(str(m.get("to", "")),
                                          str(m.get("to", ""))))
                         for m in act.get("moves", ())])
        for act in raw.get("activities", ())]
    check = raw.get("distinguishing_check")
    if isinstance(check, Mapping) and check:
        out["distinguishing_check"] = dict(
            check, target=target(str(check.get("target", ""))),
            at=rmap.get(str(check.get("at", "")), str(check.get("at", ""))))
    return out


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
    check = raw.get("distinguishing_check")
    if isinstance(check, Mapping) and check:
        out["distinguishing_check"] = dict(
            check, target=target(str(check.get("target", ""))),
            at=rev_r.get(str(check.get("at", "")), str(check.get("at", ""))))
    return out


# ----------------------------------------------------------------- tables

def vocabulary_tables(episode: Episode,
                      omap: Mapping[str, str] | None = None,
                      rmap: Mapping[str, str] | None = None,
                      cmap: Mapping[str, str] | None = None,
                      tour: bool = False) -> str:
    """The id tables. Plain lists: receptacles, then objects with their
    class and — with ``tour`` — the receptacle the tour saw each one at.
    An object the tour did not see simply has no location on its row.
    ON_PERSON is left out: scoring folds it into OUT_OF_HOUSE."""
    o = omap or {}
    r = rmap or {}
    c = cmap or {}
    lines = ["RECEPTACLES:"]
    for rec in episode.receptacle_ids:
        if rec == "ON_PERSON":
            continue
        lines.append(f"  {r.get(rec, rec)}")
    lines.append("")
    seen = {obs.object_id: obs.receptacle_id for obs in episode.initial_observations}
    lines.append("OBJECTS" + (", with where the tour saw each one:" if tour else ":"))
    for obj in sorted(episode.object_classes):
        cls = episode.object_classes[obj]
        row = f"  {o.get(obj, obj)}  (class: {c.get(cls, cls)})"
        if tour and obj in seen:
            row += f"  at {r.get(seen[obj], seen[obj])}"
        lines.append(row)
    lines.append("")
    classes = sorted(set(episode.object_classes.values()))
    lines.append("CLASSES (usable as `class:<name>` targets): "
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
    "You model how one household runs, so that a home robot can predict "
    "where its objects are. You write several competing hypotheses; the "
    "robot's sightings over the following days decide between them, and "
    "you will later be shown how each one did and asked to revise it.")


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
5. State how long each object stays where the activity put it. A move lasts the activity's `duration_h` unless you give the move its own `duration_h`; do so whenever it differs (an object put away when the activity ends versus one that stays where it was used for the rest of the evening).
6. Known failure modes to avoid: objects are often asked about while displaced, since queries cluster around activities — model the displacements, not just the rest states; the same resident can behave differently on weekdays and weekends; calling everything stationary is unfalsifiable and useless.
7. IDs: use ONLY identifiers from the tables above, exactly as printed. Nothing outside the tables is valid. You may put a short nickname in a parenthetical in your reasoning text, but every JSON field must contain the bare id.
8. One line of `rationale` per hypothesis.

Think it through first. Then end your reply with ONE json object, shaped exactly like this example (from a different, smaller home — do not copy its content):

{schema_text}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}


# ------------------------------------------------- precomputed statistics

def per_object_statistics(object_ids: Sequence[str],
                          sightings: Sequence[Tuple[int, str, str]],
                          upto_t: int,
                          omap: Mapping[str, str] | None = None,
                          rmap: Mapping[str, str] | None = None) -> str:
    """One line per object: modal receptacle, share of sighted days it
    was there, number of distinct receptacles, days never sighted.

    Arithmetic the model would otherwise do by hand, slowly and badly
    (the first run's reasoning trace opened with a 35-object walk-through
    of exactly this). ``sightings`` is ``(t, object_id, receptacle_id)``
    triples — the belief's own record when called mid-episode.
    """
    o = omap or {}
    r = rmap or {}
    n_days = max(1, upto_t // DAY_SECONDS + 1)
    by_obj: Dict[str, List[Tuple[int, str]]] = collections.defaultdict(list)
    for t, obj, rec in sightings:
        if t <= upto_t:
            by_obj[obj].append((t, rec))
    lines = [f"PER-OBJECT STATISTICS over days 0-{n_days - 1} "
             f"(modal receptacle; share of sighted days it was there; "
             f"distinct receptacles seen; days with no sighting):"]
    for obj in sorted(object_ids):
        rows = by_obj.get(obj, [])
        if not rows:
            lines.append(f"  {o.get(obj, obj)}: never sighted")
            continue
        day_rec: Dict[int, collections.Counter] = collections.defaultdict(
            collections.Counter)
        for t, rec in rows:
            day_rec[t // DAY_SECONDS][rec] += 1
        modal = collections.Counter(rec for _, rec in rows).most_common(1)[0][0]
        days_seen = len(day_rec)
        days_modal = sum(1 for d in day_rec if day_rec[d].most_common(1)[0][0]
                         == modal)
        distinct = len({rec for _, rec in rows})
        unseen = n_days - days_seen
        lines.append(f"  {o.get(obj, obj)}: mostly {r.get(modal, modal)} "
                     f"({days_modal}/{days_seen} sighted days); "
                     f"{distinct} receptacle{'s' if distinct != 1 else ''}; "
                     f"unseen {unseen} day{'s' if unseen != 1 else ''}")
    return "\n".join(lines)


WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday")


def tour_stamp(t: int) -> str:
    """``14:20 on day 1, a Tuesday`` — day 0 is a Monday everywhere in
    the bank; the hour is whatever the exporter's tour draw gave."""
    day, rem = divmod(int(t), DAY_SECONDS)
    return (f"{rem // 3600:02d}:{rem % 3600 // 60:02d} on day {day}, "
            f"a {WEEKDAY_NAMES[day % 7]}")


def tour_digest(episode: Episode, omap: Mapping[str, str] | None = None,
                rmap: Mapping[str, str] | None = None) -> str:
    """The opening walkthrough: one sighting per sensable object, one
    moment. Objects out of the house at that moment are not in it, and
    the digest says so — the model should read their absence."""
    o = omap or {}
    r = rmap or {}
    seen = {obs.object_id for obs in episode.initial_observations}
    missing = sorted(set(episode.object_classes) - seen)
    lines = [f"WALKTHROUGH TOUR (a single pass through the home at "
             f"{tour_stamp(episode.tour_t)}; every object the robot could "
             f"see, seen once):"]
    for obs in sorted(episode.initial_observations, key=lambda x: x.object_id):
        lines.append(f"  {o.get(obs.object_id, obs.object_id)}  at  "
                     f"{r.get(obs.receptacle_id, obs.receptacle_id)}")
    if missing:
        lines.append("  NOT FOUND anywhere in the home during the tour: "
                     + ", ".join(o.get(m, m) for m in missing))
    return "\n".join(lines)


OUTPUT_LENGTH_GUIDE = (
    "Each hypothesis has a one-line rationale, a one-line "
    "distinguishing_prediction with its distinguishing_check, an optional "
    "rest map, and as many activities as its routine needs.")

SCHEMA_NOTE = (
    "The example below shows the field shapes only; it is abbreviated and "
    "is about a different, smaller home.")


def tour_start_prompt(episode: Episode, anonymized: bool = False,
                      graph: bool = False) -> Tuple[str, dict]:
    """The installation prompt: the id tables with the tour's sightings
    on the object rows, the tour's time, the task, and the output
    format. Nothing about how homes work, what kinds of objects exist,
    or what a hypothesis should look like beyond its fields.

    ``graph`` asks for the assumption-graph envelope instead of the flat
    list (:func:`graph_tour_start_prompt`)."""
    if graph:
        return graph_tour_start_prompt(episode, anonymized=anonymized)
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap, tour=True)
    schema_text = example_output_text(anonymized)
    user = f"""A home robot has just been installed. Its only observation so far is one walkthrough of the home at {tour_stamp(episode.tour_t)}. Below are the home's receptacles and objects; where the walkthrough saw an object, its row says so.

{tables}

Write {N_HYPOTHESES} competing hypotheses about this home's weekly routine. Each hypothesis is a set of ACTIVITIES: a name, which days (weekday, weekend, or both), roughly when it starts (start_hour, a number), how long it lasts (duration_h), how many times a week it happens (frequency_per_week), and its moves — which object (or class:<name>) goes to which receptacle, with a chance (rarely, sometimes, usually, almost_always) and, when it differs from the activity's, its own `duration_h` — how long the object stays where the activity put it. A hypothesis may also give a `rest` map: receptacles where objects sit when nothing is happening. Each hypothesis carries a one-line `distinguishing_prediction` and a `distinguishing_check` in the form {{"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>}}.

Use only ids from the tables above, exactly as printed. {OUTPUT_LENGTH_GUIDE}

Think it through, then end your reply with one json object. {SCHEMA_NOTE}

{schema_text}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}


def revision_prompt(report: Mapping[str, Any], tables: str,
                    previous_json: str, omap: Mapping[str, str] | None = None,
                    rmap: Mapping[str, str] | None = None) -> str:
    """The re-asking prompt: previous hypotheses with weights, the
    mismatch report, which rules held, uncovered objects, and each
    hypothesis's distinguishing-prediction verdict. Asks for repair.

    ``report`` is :meth:`LLMHypothesisMixture.revision_report`. Names in
    it are real ids; ``omap``/``rmap`` translate them for the anonymized
    condition at this one point."""
    o = omap or {}
    r = rmap or {}
    def obj(x): return o.get(x, x)
    def rec(x): return r.get(x, x)
    day = report["day"]
    weights = "\n".join(
        f"  {h['hypothesis_id']}: weight {h['weight']:.2f}"
        + (f" — distinguishing prediction {h['verdict']}"
           if h.get("verdict") else "")
        for h in report["hypotheses"])
    if report.get("statistical_weight") is not None:
        weights += (f"\n  (a plain statistical model with no hypotheses — "
                    f"each object where it was most often seen — competes "
                    f"for the same weight and currently holds "
                    f"{report['statistical_weight']:.2f}; weight it holds is "
                    f"weight your hypotheses failed to earn)")
    misses = "\n".join(
        f"  {obj(m['object'])}: predicted {rec(m['predicted'])}, actually "
        f"{rec(m['actual'])} — {m['count']}x, e.g. day {m['example_day']} "
        f"{m['example_hour']:02d}:00"
        for m in report["worst_objects"]) or "  (none)"
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
    uncovered = "\n".join(
        f"  {obj(u['object'])}: {u['summary']}"
        for u in report["uncovered_objects"]) or "  (none)"
    return f"""It is now day {day}. The robot has been watching since your hypotheses were written; here is how they did. Revise them — keep what held up, fix what did not, and add at most ONE new hypothesis only if something systematic is unexplained. Do not start over: revised hypotheses keep their hypothesis_id, and a new one gets the next id.

HYPOTHESIS WEIGHTS (share of the mixture each currently earns from the sightings):
{weights}

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was:
{misses}

RULES THAT HELD UP (object was where the rule said, during its activity):
{held}

RULES THAT FAILED (object was elsewhere during the rule's activity):
{failed}

OBJECTS NO HYPOTHESIS COVERS (no rule and no rest entry mentions them), with what the sightings show:
{uncovered}

{report['statistics']}

The ONLY valid identifiers are these, exactly as printed:

{tables}

YOUR PREVIOUS HYPOTHESES:

{previous_json}

Rules: same output format and the same seven rules as before (ids only from the tables; chances as labels; `rest` optional; every hypothesis carries a distinguishing_prediction and distinguishing_check). Keep {N_HYPOTHESES} hypotheses, or {N_HYPOTHESES + 1} if you add one. Think about what the mismatches imply, then end your reply with ONE json object holding the full revised set."""


# ================================================================== graph

GRAPH_EXAMPLE_OUTPUT = {
    "assumptions": {
        "composition": {
            "question": "how many people live here and who",
            "values": {"solo": "one adult resident",
                       "couple": "two adults, no children"}},
        "weekday_pattern": {
            "question": "where is the primary resident on weekdays",
            "values": {"works_away": "out of the house 9 to 6",
                       "works_from_home": "at the desk most of the day"}},
    },
    "leaf_set_rationale": "solo + works_from_home is skipped: with one "
                          "resident at home all day the tour would have "
                          "found the laptop out, and it was not",
    "leaves": [
        {"leaf_id": "p_a41c",
         "assumes": {"composition": "couple", "weekday_pattern": "works_away"},
         "rationale": "two commuters; the home is empty on weekdays",
         "distinguishing_prediction": "keys_x are gone from the entry "
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
        {"leaf_id": "p_9f02",
         "assumes": {"composition": "couple",
                     "weekday_pattern": "works_from_home"},
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
"""The envelope example. Leaf ids are opaque ``p_xxxx`` tokens on
purpose — an id spelled from the assumption path would be re-derived
by the model on every revision and break weight carry-over."""


_LEAF_SCHEMA = dict(HYPOTHESES_SCHEMA["properties"]["hypotheses"]["items"])
_LEAF_SCHEMA["properties"] = {
    "leaf_id": {"type": "string"},
    "assumes": {"type": "object", "additionalProperties": {"type": "string"}},
    **{k: v for k, v in _LEAF_SCHEMA["properties"].items()
       if k != "hypothesis_id"}}
_LEAF_SCHEMA["required"] = ["leaf_id", "assumes", "rationale", "rest",
                            "activities"]

GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "assumptions": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "values": {"type": "object",
                               "additionalProperties": {"type": "string"}}},
                "required": ["question", "values"]}},
        "leaf_set_rationale": {"type": "string"},
        "leaves": {"type": "array", "items": _LEAF_SCHEMA},
    },
    "required": ["assumptions", "leaves"],
}
"""Guided-decoding schema for the graph envelope (salvage stage). Shape
only; ids, the assumption rules, and the caps are checked by
:func:`~baselines.llm_hypotheses.assumption_graph.parse_graph`."""

OPERATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "op": {"type": "string",
                           "enum": ["edit_leaf", "add_assumption_value",
                                    "add_leaf", "add_assumption",
                                    "add_activity"]},
                    "leaf_id": {"type": "string"},
                    "reason": {"type": "string"},
                    "assumption": {"type": "string"},
                    "value": {"type": "string"},
                    "description": {"type": "string"},
                    "question": {"type": "string"},
                    "values": {"type": "object",
                               "additionalProperties": {"type": "string"}},
                    "body": _LEAF_SCHEMA,
                    "activity": (_LEAF_SCHEMA["properties"]["activities"]
                                 ["items"])},
                "required": ["op"]}}},
    "required": ["operations"],
}
"""Guided-decoding schema for a revision's operation list."""

_GRAPH_EXAMPLE_TOKEN_MAP = dict(_EXAMPLE_TOKEN_MAP)


def graph_example_output_text(anonymized: bool) -> str:
    text = json.dumps(GRAPH_EXAMPLE_OUTPUT, indent=1)
    if anonymized:
        for token in sorted(_GRAPH_EXAMPLE_TOKEN_MAP, key=len, reverse=True):
            text = text.replace(token, _GRAPH_EXAMPLE_TOKEN_MAP[token])
    return text


def anonymize_graph(envelope: Mapping[str, Any], omap: Mapping[str, str],
                    rmap: Mapping[str, str], cmap: Mapping[str, str]) -> dict:
    """Envelope with every leaf body translated INTO the anonymized
    vocabulary. Assumption names, value names, questions and
    descriptions are model-authored free text with no vocabulary ids in
    them (the parser enforces that), so they pass through untouched."""
    out = dict(envelope)
    out["leaves"] = [anonymize_hypothesis(leaf, omap, rmap, cmap)
                     for leaf in envelope.get("leaves", ())]
    return out


def deanonymize_graph(envelope: Mapping[str, Any], omap: Dict[str, str],
                      rmap: Dict[str, str], cmap: Dict[str, str]) -> dict:
    out = dict(envelope)
    out["leaves"] = [deanonymize_hypothesis(leaf, omap, rmap, cmap)
                     for leaf in envelope.get("leaves", ())]
    return out


def deanonymize_operations(operations: Sequence[Mapping[str, Any]],
                           omap: Dict[str, str], rmap: Dict[str, str],
                           cmap: Dict[str, str]) -> List[dict]:
    """Operations with any ``body`` translated back to real ids."""
    out = []
    for op in operations:
        op = dict(op)
        if isinstance(op.get("body"), Mapping):
            op["body"] = deanonymize_hypothesis(op["body"], omap, rmap, cmap)
        out.append(op)
    return out


GRAPH_RULES = """Rules that matter:

1. Leaves must DISAGREE in ways sightings can settle. Two leaves predicting the same object in the same place at the same hour are wasted. Each leaf carries a one-line `distinguishing_prediction` naming a concrete observable difference from the others, and a `distinguishing_check` in the form {"target": <object id>, "at": <in-home receptacle id>, "days": weekday|weekend|both, "hour": <number>, "if_seen": right|wrong}: a look at `at` around that hour that finds the target means the leaf is `if_seen`; an empty look means the opposite. `at` must be a receptacle the robot can look into. A leaf whose move sends the target out of the house checks the object's rest with "if_seen": "wrong".
2. Cover every object, not only the interesting ones: every object id should appear in each leaf's `rest` map (directly or via its class).
3. Times and weekly frequencies: state them as numbers with your best guess ("dinner around 19:30" -> start_hour 19.5). They will be corrected by data, so a concrete guess beats a vague one.
4. State how long each object stays where the activity put it. A move lasts the activity's `duration_h` unless you give the move its own `duration_h`; do so whenever it differs.
5. Chances: NEVER numbers. Use exactly one of: rarely, sometimes, usually, almost_always.
6. IDs: use ONLY identifiers from the tables above, exactly as printed. Nothing outside the tables is valid. Every JSON field must contain the bare id.
7. One line of `rationale` per leaf.

Assumptions:

- Name 2 to 3 assumptions. An assumption qualifies only if its different values lead to different observable predictions. If two values would produce leaves that predict the same object in the same place at the same hour, drop the assumption.
- Write one leaf per combination of assumption values worth testing. Skip combinations that do not fit together, and say which in `leaf_set_rationale`.
- `OUT_OF_HOUSE` is a location in the tables like any other, and the one destination a look can never confirm. A move that ends there gains support only from the object failing to turn up at its rest receptacle during the window, so write one only when you can say where the object would be found if the move did not happen (put that receptacle in `rest`), and keep the window narrow enough that the patrol reaches that place inside it.
- `leaf_id` is an opaque token: `p_` followed by 4 hex characters, chosen at random. Never spell an id from the assumption values. Assumption names, value names, questions and descriptions must not contain any object or receptacle id.
- At most 3 assumptions and 12 leaves."""


def graph_tour_start_prompt(episode: Episode, anonymized: bool = False
                            ) -> Tuple[str, dict]:
    """The installation prompt for the graph arm: the same tables and
    tour as the flat one, plus the envelope format and the assumption
    rules. Nothing about what the tour did or did not capture, how
    sightings are recorded, or how objects end up in odd places — the
    move duration is how the model says an object stays somewhere."""
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap, tour=True)
    schema_text = graph_example_output_text(anonymized)
    rules = GRAPH_RULES
    if anonymized:
        rules = rules.replace("`OUT_OF_HOUSE`", f"`{rmap['OUT_OF_HOUSE']}`")
    user = f"""A home robot has just been installed. Its only observation so far is one walkthrough of the home at {tour_stamp(episode.tour_t)}. Below are the home's receptacles and objects; where the walkthrough saw an object, its row says so.

{tables}

Write competing hypotheses about this home's weekly routine, organised as a small graph. The upper level is a set of ASSUMPTIONS: named latent facts about the household, each with a short list of named values (for example who lives here, or where the primary resident is on weekdays). The lower level is LEAVES: one full hypothesis per combination of assumption values you think worth testing, each with an `assumes` map naming one value of every assumption. A leaf is a set of ACTIVITIES: a name, which days (weekday, weekend, or both), roughly when it starts (start_hour, a number), how long it lasts (duration_h), how many times a week it happens (frequency_per_week), and its moves — which object (or class:<name>) goes to which receptacle, with a chance and, when it differs from the activity's, its own `duration_h`. A leaf may also give a `rest` map: receptacles where objects sit when nothing is happening.

{rules}

Think it through, then end your reply with one json object. {SCHEMA_NOTE}

{schema_text}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}


def graph_revision_prompt(report: Mapping[str, Any], tables: str,
                          graph_json: str,
                          omap: Mapping[str, str] | None = None,
                          rmap: Mapping[str, str] | None = None,
                          call_type: str | None = None) -> str:
    """The graph arm's re-asking prompt: assumption weights, leaf weights
    with their cells, the mismatch report, rules held and failed, the
    uncovered bank and what fired, statistics, tables, the graph as
    JSON — and a request for OPERATIONS, not a replacement set.

    ``report`` is :meth:`LLMHypothesisMixture.revision_report` in graph
    mode (it carries ``assumptions`` and ``uncovered_bank``)."""
    o = omap or {}
    r = rmap or {}
    def obj(x): return o.get(x, x)
    def rec(x): return r.get(x, x)
    day = report["day"]
    settled = dict(report.get("settled", {}))
    a_lines = []
    for name, node in report.get("assumptions", {}).items():
        values = ", ".join(f"{v} {w:.2f}" for v, w in node["values"].items())
        if name in settled:
            state = (f"SETTLED on {settled[name]!r} — not editable in this "
                     f"call; operations naming it are rejected")
        else:
            top = max(node["values"].values()) if node["values"] else 0.0
            state = "leaning" if top >= 0.6 else "open"
        a_lines.append(f"  {name} ({node['question']}): {values}; entropy "
                       f"{node['entropy']:.2f} nats — {state}")
    assumptions = "\n".join(a_lines) or "  (none)"
    open_names = [a for a in report.get("assumptions", {}) if a not in settled]
    checks = report.get("check_outcomes", [])
    unresolved = [h["hypothesis_id"] for h in report["hypotheses"]
                  if not h.get("verdict") or "not yet" in str(h.get("verdict"))]
    bucket_rows = report.get("anomaly_bucket", [])
    bucket_text = "\n".join(
        f"  {obj(b['object'])} seen at {rec(b['receptacle'])} around "
        f"{b['hour_bin'] * 2:02d}:00-{b['hour_bin'] * 2 + 2:02d}:00 on "
        f"{b['count']} occasions; no leaf gave it more than "
        f"{b['max_p']:.2f}"
        for b in bucket_rows) or "  (empty)"
    weights = "\n".join(
        f"  {h['hypothesis_id']}: weight {h['weight']:.2f}, assumes "
        + json.dumps(h.get("assumes", {}))
        + (f" — distinguishing prediction {h['verdict']}"
           if h.get("verdict") else "")
        for h in report["hypotheses"])
    if report.get("statistical_weight") is not None:
        weights += (f"\n  (a plain statistical model with no hypotheses — "
                    f"each object where it was most often seen — competes "
                    f"for the same weight and currently holds "
                    f"{report['statistical_weight']:.2f}; weight it holds is "
                    f"weight your leaves failed to earn)")
    misses = "\n".join(
        f"  {obj(m['object'])}: predicted {rec(m['predicted'])}, actually "
        f"{rec(m['actual'])} — {m['count']}x, e.g. day {m['example_day']} "
        f"{m['example_hour']:02d}:00"
        for m in report["worst_objects"]) or "  (none)"
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
    uncovered = "\n".join(
        f"  {obj(u['object'])}: {u['summary']}"
        for u in report["uncovered_objects"]) or "  (none)"
    bank = ", ".join(f"{obj(b['object'])} (class {b['class']}, first seen "
                     f"day {b['day']})"
                     for b in report.get("uncovered_bank", [])) or "(empty)"
    trigger = report.get("trigger", "scheduled")
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
    if call_type == "diversify":
        lead = f"""It is now day {day}. This is a DIVERSIFY call: the sightings below are ones no leaf predicted, repeatedly, so the graph is missing structure. Add to it — a new assumption, a new value, a new leaf, or a new activity on an existing leaf. Do not edit existing leaves otherwise (edit_leaf is rejected in this call). Leaves you do not mention are kept exactly as they are.

REPEATED SIGHTINGS NO LEAF EXPLAINS (the anomaly bucket):
{bucket_text}

ASSUMPTIONS STILL OPEN: {', '.join(open_names) or '(none)'}
LEAVES WHOSE DISTINGUISHING CHECK HAS NEVER RESOLVED: {', '.join(unresolved) or '(none)'}
"""
        header_ops = ("Operations allowed in this call: add_assumption, "
                      "add_assumption_value, add_leaf, add_activity.")
    elif call_type == "repair":
        lead = f"""It is now day {day}. This is a REPAIR call: the mixture has been predicting poorly. Fix the leaves the evidence points at — a failed rule is an edit_leaf on that leaf's activities; a value no leaf carries is an add_assumption_value or an add_leaf. Leaves you do not mention are kept exactly as they are, with the weight they have earned.
"""
        header_ops = ("Operations allowed in this call: edit_leaf (activities "
                      "only — rest is not editable), add_assumption_value, "
                      "add_leaf.")
    else:
        lead = f"""It is now day {day}. The robot has been watching since your graph was written; here is how it did. Revise it with OPERATIONS on the graph — leaves you do not mention are kept exactly as they are, with the weight they have earned.
"""
        header_ops = ("Operations allowed: add_assumption, "
                      "add_assumption_value, edit_leaf (activities only — "
                      "rest is not editable), add_activity, add_leaf.")
    return f"""{lead}
ASSUMPTION WEIGHTS (each value's share of the leaf weight, and the node's entropy):
{assumptions}

LEAF WEIGHTS (share of the mixture each leaf currently earns from the sightings):
{weights}

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was:
{misses}

RULES THAT HELD UP (object was where the rule said, during its activity; tagged leaf/activity):
{held}

RULES THAT FAILED (object was elsewhere during the rule's activity; tagged leaf/activity):
{failed}

OBJECTS NO LEAF COVERS (no rule and no rest entry mentions them), with what the sightings show:
{uncovered}

Uncovered bank (objects of classes no leaf models, seen since the last revision): {bank}
This call was triggered by: {trigger}.

{report['statistics']}

UNSEEN DURING MODELED AWAY WINDOWS (for each object some leaf sends out of the house: looks inside that window at its stated rest, and at the receptacle it is sighted at most, that found nothing versus looks that found it. "Seen at X on every sighted day" says nothing about the window; empty looks at X inside the window are the evidence the object is out):
{away_looks}

The ONLY valid identifiers are these, exactly as printed:

{tables}

THE CURRENT GRAPH:

{graph_json}

{header_ops}
Operations, applied in this order: add_assumption, add_assumption_value, edit_leaf, add_activity, add_leaf.
  {{"op": "edit_leaf", "leaf_id": "p_xxxx", "body": {{...the complete leaf body, with assumes, and the rest map EXACTLY as stored...}}}}
  {{"op": "add_activity", "leaf_id": "p_xxxx", "activity": {{...one complete activity with its moves...}}}}
  {{"op": "add_assumption_value", "assumption": "<name>", "value": "<new value>", "description": "..."}}
  {{"op": "add_leaf", "body": {{...the complete leaf body, with assumes; leaf_id p_ + 4 random hex...}}}}
  {{"op": "add_assumption", "assumption": "<name>", "question": "...", "values": {{"<value>": "..."}}}}
Every body is a complete leaf, never a partial patch. There is no operation that removes a leaf: leaves that stop earning weight are pruned automatically. The `rest` map is fit from sightings and is not yours to edit — an edit_leaf whose rest differs from the stored leaf is rejected. Operations that name a SETTLED assumption are rejected. An add_assumption must come with edit_leaf operations giving every existing leaf a value for it, or it is rejected. A new assumption value is crossed automatically with the values of the other assumptions that still carry weight; you may also add_leaf the combinations you care about yourself.

Guidance:
- Edit at the level the evidence points to. A failed rule inside one leaf is an edit_leaf. An assumption value losing weight across every leaf that depends on it means that premise is wrong, not those leaves individually. An object no leaf accounts for usually means a missing assumption value, not a missing rule.
- One sighting at a given place and hour is weaker evidence than a repeated one. The statistics section gives, per object, how many distinct receptacles it has been seen in and its share of sighted days at the most common one.
- Only positive sightings are recorded. An object that leaves the house is invisible while it is out, so "seen at X on every sighted day" is fully consistent with it being taken out most of the day; the "unseen during modeled windows" figure in the statistics is the evidence for a move ending out of the house.
- Do not propose an assumption whose values make the same observable predictions.
- Return only operations. Leaves you do not mention are kept exactly as they are.

Rules: ids only from the tables; chances as labels; a move's `duration_h` when it differs from the activity's; every leaf carries a distinguishing_prediction and a distinguishing_check whose `at` is an in-home receptacle with an `if_seen` direction; leaf ids are opaque p_xxxx tokens and an existing leaf keeps its id. At most 3 assumptions and 12 leaves. Think about what the mismatches imply, then end your reply with ONE json object of the form {{"operations": [...]}}."""


def graph_repair_prompt(problems: Sequence[str], tables: str,
                        raw_json: str, kind: str = "graph") -> str:
    """Repair round for an envelope (``kind="graph"``) or an operation
    set (``kind="operations"``): the exact problems, the tables, the
    previous JSON, and a request to reprint the whole object."""
    listed = "\n".join(f"- {p}" for p in problems) or "- (none)"
    what = ("the COMPLETE corrected envelope (assumptions and all leaves)"
            if kind == "graph" else
            "the COMPLETE corrected operation list")
    return f"""Your previous output had these problems:

{listed}

The ONLY valid identifiers are these, exactly as printed:

{tables}

Here is your previous JSON:

{raw_json}

Reprint {what}, same shape. Fix every problem listed: replace invalid strings with valid identifiers from the tables (or remove the entry if nothing valid expresses it), give every leaf a value for every assumption, keep leaf ids opaque (p_ plus 4 hex characters), and stay within 3 assumptions and 12 leaves. Do not change parts that were already valid. End your reply with the JSON object only."""
