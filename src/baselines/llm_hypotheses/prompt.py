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
         "rationale": "single resident works away on weekdays; carry "
                      "items leave the house with them",
         "distinguishing_prediction": "keys_x absent from the entry "
                                      "table on weekday middays, back "
                                      "by 18:00",
         "distinguishing_check": {"target": "keys_x", "at": "OUT_OF_HOUSE",
                                  "days": "weekday", "hour": 13.0},
         "rest": {"class:mug": "cupboard_1"},
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
         "distinguishing_check": {"target": "keys_x", "at": "entry_shelf_1",
                                  "days": "weekday", "hour": 13.0},
         "rest": {"class:mug": "desk_1"},
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
                    "distinguishing_check": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "at": {"type": "string"},
                            "days": {"type": "string",
                                     "enum": ["weekday", "weekend", "both"]},
                            "hour": {"type": "number"}},
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
    "and decisive; the sightings, not you, will settle who was right. "
    "This is not your only chance: you will be shown where each "
    "hypothesis was wrong and asked to revise it. Commit to sharp, "
    "different hypotheses now rather than hedging — hedged hypotheses "
    "all say the same thing and cannot be told apart by data.")


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
    "Length: exactly {n} hypotheses. Each needs 3-7 activities, each "
    "activity 1-6 moves. The `rest` map is OPTIONAL and should list only "
    "objects whose resting place differs from where the tour found them "
    "or that an activity moves; an object left out of `rest` is assumed "
    "to rest where the tour saw it — so if the tour caught something "
    "mid-use, say where it really lives. Do not enumerate every object. "
    "Rationale and distinguishing_prediction: one line each.")

SCHEMA_NOTE = (
    "The example below is ABBREVIATED — two hypotheses with one or two "
    "activities each, from a different, much smaller home — and shows the "
    "field shapes only, not the scale of the answer you should give.")


def tour_start_prompt(episode: Episode, anonymized: bool = False
                      ) -> Tuple[str, dict]:
    """The installation prompt: vocabulary tables plus the tour, and
    nothing about routines. Says so directly — the model is to write from
    what it knows about how homes work, and sightings will settle it. The
    tour is a snapshot at the installation instant, which need not be a
    quiet moment: the prompt names the time and lists what was absent."""
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap)
    tour = tour_digest(episode, omap, rmap)
    schema_text = example_output_text(anonymized)
    user = f"""A robot has just been installed in a home. It has done ONE walkthrough tour — one sighting of every object it could find, at one moment — and nothing else. It has seen no routines, no days, no movements. The tour is a snapshot of that moment, not a map of where things rest: an object may have been caught in use, and an object it could not find was out of the house or on someone. Below are the home's vocabulary tables and that tour.

{tables}

{tour}

You have almost no data. Write your hypotheses from what you know about how homes like this run — who lives here judging by the objects, what they do on weekdays and weekends, which objects leave the house with a person, which get used and left out, which get put away. The robot's sightings over the coming days will settle which hypotheses were right; your job is to give it sharply different candidates to test.

Write exactly {N_HYPOTHESES} competing hypotheses. Each hypothesis describes ACTIVITIES: what happens, which days (weekday, weekend, or both — mark this explicitly), roughly when, how many times per week, and which objects move where; plus an optional `rest` map for objects that do not rest where the tour found them.

Rules that matter:

1. Hypotheses must DISAGREE in ways sightings can settle. Two hypotheses predicting the same object in the same place at the same hour are wasted. Each hypothesis carries a one-line `distinguishing_prediction` naming a concrete observable difference from the others, AND a `distinguishing_check` object giving it in checkable form: {{"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>}}. You will be told whether it came true.
2. Times and weekly frequencies: state them as numbers with your best guess ("dinner around 19:30" -> start_hour 19.5). They will be corrected by data, so a concrete guess beats a vague one.
3. Chances: NEVER numbers. Use exactly one of: rarely, sometimes, usually, almost_always.
4. `after` is "returned" (put back at rest when the activity ends) or "left" (stays where it was used until the next day). Distinguish objects put away after an activity from objects left where they were used.
5. Known failure modes to avoid: objects are often asked about while displaced, since queries cluster around activities — model the displacements, not just the rest states; the same resident can behave differently on weekdays and weekends; calling everything stationary is unfalsifiable and useless. Objects that leave the house with a person go to {rmap.get("OUT_OF_HOUSE", "OUT_OF_HOUSE")}.
6. IDs: use ONLY identifiers from the tables above, exactly as printed. Nothing outside the tables is valid. Every JSON field must contain the bare id.
7. {OUTPUT_LENGTH_GUIDE.format(n=N_HYPOTHESES)}

Think it through first. Then end your reply with ONE json object. {SCHEMA_NOTE}

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
