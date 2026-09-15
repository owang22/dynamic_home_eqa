"""Prompts for treeLongLeaf: installation (a library of 12-20 full
weekly models), revision (add documents, revive retired ones), repair.
Mechanics only, stated in the affirmative; the same hygiene rules as
the tree prompts (:data:`~baselines.llm_hypotheses.tree_prompt.
FORBIDDEN_PROMPT_STRINGS`)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from baselines.llm_hypotheses.longleaf import (DELIMITER, MAX_FETCH,
                                               REVISION_TARGET, TARGET_ELICITED)
from baselines.llm_hypotheses.prompt import (build_anonymization_maps,
                                             tour_stamp, vocabulary_tables)
from baselines.types import Episode

EXAMPLE_DOCUMENT = f'''{DELIMITER}
# p_3f1a — One commuter; the desk is the hub, the entry shelf the exit

One adult lives here and leaves for an office on weekdays around 8:30, back
around 18:00. The keys leave with her; mugs cycle between the cupboard and the
counter each morning; the towel stays on the rack. What sets this hypothesis
apart: the entry shelf is bare at weekday midday. What would refute it: keys_x
sighted anywhere in the house between 9:00 and 17:00 on a weekday.

```json
{{"claims": [
   {{"claim": "keys_x leave the house with the resident on weekdays",
    "target": "keys_x", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17}},
   {{"claim": "a mug is on the counter mid-morning",
    "target": "mug_1", "expect": "counter_1", "days": "both", "from": 7, "to": 10}}],
 "targets": {{
   "keys_x": [
     {{"days": "both", "from": 0, "to": 24, "at": "entry_shelf_1", "chance": "usually"}},
     {{"days": "weekday", "from": 8.5, "to": 18, "at": "OUT_OF_HOUSE", "chance": "almost_always"}}],
   "class:mug": [
     {{"days": "both", "from": 0, "to": 24, "at": "cupboard_1", "chance": "usually"}},
     {{"days": "both", "from": 6.5, "to": 10.5, "at": "counter_1", "chance": "usually"}}]
 }}}}
```
'''

MECHANICS = f"""How a document works:

- Each hypothesis is one markdown document: a heading `# p_xxxx — <title>` (p_ plus 4 random hex characters), a few paragraphs of prose (who lives here and how the week runs; what this hypothesis predicts that sets it apart from the others; what would refute it), and ONE fenced ```json block at the end.
- The json block gives `targets`: for each object id or `class:<name>`, a list of BLOCKS in priority order. A block is {{"days": weekday|weekend|both, "from": <hour>, "to": <hour>, "at": <receptacle id>, "chance": rarely|sometimes|usually|almost_always}}. Later blocks override earlier ones, so "at the desk all day; out 9 to 17 on weekdays" is two blocks in that order. Hours no block covers fall through to the robot's own sighting statistics for that object. A `class:` target applies to every object of the class, including objects the robot meets later.
- The block's `chance` is a starting label; the sightings inside the block adjust it. `from` and `to` are the author's and stay fixed.
- A block whose `at` is `OUT_OF_HOUSE` or `ON_PERSON` is supported by empty looks at the receptacle it overrides (where the object would be otherwise) and weakened by looks that find it there.
- Objects leave the house. Residents take things with them to work, to school, to the gym, on errands and on trips, and the walkthrough happened at one instant: anything that was out with someone at that moment is missing from the object table and will first appear later. Say in each document which objects travel, when, and with whom, as `OUT_OF_HOUSE` blocks (or `ON_PERSON` while the resident is home and holding them); a document in which nothing ever leaves is a claim in itself.
- `claims` is a list of falsifiable statements the document makes, each {{"claim": <one sentence>, "target": <object id>, "expect": <receptacle id or OUT_OF_HOUSE or ON_PERSON>, "days": weekday|weekend|both, "from": <hour>, "to": <hour>}}. Write at least three per document, on the objects where the documents differ. How they are scored: an in-home claim counts FOR the document when a look at `expect` in the window finds the target, and AGAINST when that look is empty or the target is sighted anywhere else; an out-of-house claim counts AGAINST when the target is sighted anywhere in the house in the window, and WEAKLY FOR when a look at the place the document would otherwise put it finds nothing. Each document's tally is shown back to you.
- Identifiers come from the tables, exactly as printed. Documents are separated by a line reading exactly `{DELIMITER}`."""


def longleaf_tour_start_prompt(episode: Episode, anonymized: bool = False):
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    tables = vocabulary_tables(episode, omap, rmap, cmap, tour=True)
    mechanics = MECHANICS
    example = EXAMPLE_DOCUMENT
    if anonymized:
        for real, tok in (("OUT_OF_HOUSE", rmap["OUT_OF_HOUSE"]),
                          ("ON_PERSON", rmap["ON_PERSON"])):
            mechanics = mechanics.replace(f"`{real}`", f"`{tok}`")
            example = example.replace(real, tok)
    lo, hi = TARGET_ELICITED
    user = f"""A home robot has just been installed. Its only observation so far is one walkthrough of the home at {tour_stamp(episode.tour_t)}. Below are the home's receptacles and the objects the walkthrough saw, each with where it was. The home may hold further objects the walkthrough missed; those join your `class:<name>` blocks automatically once the robot meets them, so the ids below are the complete vocabulary for now.

{tables}

Write a LIBRARY of {lo} to {hi} competing hypotheses about how this home runs, each a complete weekly model: for every object the walkthrough saw (directly or through its class), where it is across the week. Make the library wide: different household compositions, work patterns, evening and weekend habits, and different guesses about which objects travel and which stay. Each document differs from every other in something the robot's looks can settle, and says so in its prose. The robot's sightings over the following weeks will weight the documents; you will then be shown the library with its weights and asked to add to it.

{mechanics}

Think it through, then write the documents one after another, each preceded by the `{DELIMITER}` line, and end your reply after the last document's json block. The example below shows the shape only; it is about a different, smaller home.

{example}"""
    return user, {"omap": omap, "rmap": rmap, "cmap": cmap}


def _verdict(v: Any) -> str:
    if not v:
        return "check untested so far"
    return str(v).replace("not yet tested (no look at that receptacle in the window)",
                          "check untested so far")


def longleaf_revision_prompt(report: Mapping[str, Any], tables: str,
                             omap=None, rmap=None,
                             fetched: Sequence[Mapping[str, Any]] = ()) -> str:
    """The revision prompt, in two phases over one layout. Stable parts
    first (mechanics, tables), then the library INDEX (weights, claim
    tallies), then the documents the model asked to read (``fetched``;
    none on the first phase), then the volatile evidence. The reply is
    either ``READ p_xxxx ...`` lines (the second phase then carries those
    documents) or the new documents themselves."""
    o = omap or {}
    r = rmap or {}
    def obj(x): return o.get(x, x)
    def rec(x): return r.get(x, x)
    day = report["day"]
    lib = report.get("library", [])
    def _claims(d):
        rows = d.get("claims") or []
        if not rows:
            return ""
        return "\n" + "\n".join(
            f"      claim: {c['claim']} [{obj(c['target'])} at {rec(c['expect'])}, "
            f"{c['days']} {c['from']:g}-{c['to']:g}h]: for {c['for']}, against "
            f"{c['against']}, weak for {c['weak_for']}" for c in rows)
    index_lines = "\n".join(
        f"  {d['hypothesis_id']}"
        + (f" (fork of {d['forked_from']})" if d.get('forked_from') else "")
        + f": weight {d['weight']:.3f}, {d['status']} — {d['title']}{_claims(d)}"
        for d in lib) or "  (empty)"
    stat = ""
    if report.get("statistical_weight") is not None:
        stat = (f"A plain statistical model (each object where it was most "
                f"often seen) competes for the same weight and holds "
                f"{report['statistical_weight']:.3f} of the mixture.")
    against = "\n".join(
        f"  {c['hypothesis_id']} (weight {c['weight']:.2f}): {c['claim']} — against "
        f"{c['against']}, for {c['for']}, weak for {c['weak_for']} since the last call"
        for c in report.get("claims_against", [])) or "  (none)"
    table = "\n".join(
        f"  {obj(a['object'])}: mostly {rec(a['modal'])} ({a['days_modal']}/{a['days_seen']} "
        f"sighted days; {a['distinct']} receptacle{'s' if a['distinct'] != 1 else ''}; "
        f"{a['sightings']} sightings); weekday 9-17h looks at {rec(a['modal'])} found it "
        f"{a['found']}, found nothing {a['empty']}"
        for a in report.get("object_table", [])) or "  (none yet)"
    bucket = "\n".join(
        f"  {obj(b['object'])} seen at {rec(b['receptacle'])} around "
        f"{b['hour_bin'] * 2:02d}:00-{b['hour_bin'] * 2 + 2:02d}:00 on "
        f"{b['count']} occasions; the best document gave it {b['max_p']:.2f}"
        for b in report.get("anomaly_bucket", [])) or "  (empty)"
    held = "\n".join(
        f"  {h['hypothesis_id']} {h['activity']}: {obj(h['target'])} at "
        f"{rec(h['to'])} held ({h['fitted_chance']:.2f} on "
        f"{h['evidence']:.0f} sightings)" for h in report["rules_held"]) or "  (none yet)"
    failed = "\n".join(
        f"  {h['hypothesis_id']} {h['activity']}: {obj(h['target'])} at "
        f"{rec(h['to'])} failed ({h['fitted_chance']:.2f} on "
        f"{h['evidence']:.0f} sightings)" for h in report["rules_failed"]) or "  (none)"
    misses = "\n".join(
        f"  {obj(m['object'])}: predicted {rec(m['predicted'])}, actually "
        f"{rec(m['actual'])} — {m['count']}x, e.g. day {m['example_day']} "
        f"{m['example_hour']:02d}:00" for m in report["worst_objects"]) or "  (none)"
    mechanics = MECHANICS
    if r:
        mechanics = (mechanics.replace("`OUT_OF_HOUSE`", f"`{rec('OUT_OF_HOUSE')}`")
                     .replace("`ON_PERSON`", f"`{rec('ON_PERSON')}`"))
    lo, hi = REVISION_TARGET
    docs = ""
    if fetched:
        docs = ("\n\nTHE DOCUMENTS YOU ASKED TO READ:\n\n"
                + "\n\n".join(f"{DELIMITER}\n{d['markdown'].rstrip()}" for d in fetched))
        ask = (f"Now write {lo} to {hi} NEW documents, one after another, each "
               f"preceded by the `{DELIMITER}` line, with fresh p_xxxx ids (a fork "
               f"has `(fork of p_xxxx)` at the end of its heading), and end your "
               f"reply after the last document's json block.")
    else:
        ask = (f"Reply in ONE of two ways. Either a single line `READ p_xxxx p_yyyy ...` "
               f"naming up to {MAX_FETCH} documents you want to see in full before "
               f"writing (a fork needs its parent's text, so ask for it), after which "
               f"you will get them and write; or, when the index and evidence are "
               f"enough, the {lo} to {hi} new documents themselves, one after another, "
               f"each preceded by the `{DELIMITER}` line, with fresh p_xxxx ids.")
    return f"""You maintain a LIBRARY of hypothesis documents about one home, kept as files. The robot's sightings weight them; you add documents and revive retired ones; existing documents stay exactly as they are.

{mechanics}

The valid identifiers are these, exactly as printed:

{tables}

It is now day {day}. This call was triggered by: {report.get('trigger', 'scheduled')}. Two ways to write a new document:
- FORK an existing one: copy it whole, give it a fresh id, put `(fork of p_xxxx)` at the end of the heading, change only what the evidence points at (a block, a claim, a travelling object), and say in the prose what changed and why. The parent stays with its weight; the fork starts at the weight its own replay of the log earns and competes with it.
- Write a fresh document for a routine the library lacks.
A retired document (weight under the floor for days) can come back: write a line `REVIVE p_xxxx` anywhere in your reply.

THE LIBRARY INDEX (weight = share of the mixture each document earns from the sightings; under each document, how its claims have resolved so far):
{index_lines}
{stat}
CLAIMS THAT WENT AGAINST A WEIGHTED DOCUMENT SINCE THE LAST CALL:
{against}{docs}

PER-OBJECT EVIDENCE (usual place; share of sighted days there; distinct receptacles; sightings; and weekday 9-17h looks at the usual place that found it versus found nothing — only positive sightings count in the first numbers, so an object that is out of the house shows as many empty daytime looks at a place it occupies mornings and evenings):
{table}

REPEATED SIGHTINGS THE LIBRARY MISSED (each seen on 3 or more occasions with every document giving it under 0.05):
{bucket}

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was, since the last call:
{misses}

BLOCKS THAT HELD UP (object was where the block said, inside its hours; tagged document, block):
{held}

BLOCKS THAT FAILED (object was elsewhere inside the block's hours):
{failed}

{ask}"""


def longleaf_repair_prompt(problems: Sequence[str], tables: str,
                           raw_text: str) -> str:
    listed = "\n".join(f"- {p}" for p in problems) or "- (none)"
    return f"""Some of your documents had these problems:

{listed}

The valid identifiers are these, exactly as printed:

{tables}

Here are the documents that failed:

{raw_text}

Reprint ONLY these documents, corrected, each preceded by the `{DELIMITER}` line and keeping its heading id: replace invalid strings with identifiers from the tables (or drop the entry when nothing valid expresses it), keep every block's from < to inside 0-24, chances as the four labels, and one ```json block per document. End your reply after the last document's json block."""


__all__ = ["EXAMPLE_DOCUMENT", "MECHANICS", "longleaf_repair_prompt",
           "longleaf_revision_prompt", "longleaf_tour_start_prompt"]
