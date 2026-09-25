"""A DIAGNOSTIC, not an arm's result: freeze the notes, stop all looking, and ask what
the notes ALONE contain.

WHAT THIS IS AND IS NOT, corrected 2026-09-24. This was written as the primary
measurement, copying the earlier PATROL experiment where the robot's memory could only
help at answer time. It does not fit this design. Here the robot searches IN ORDER TO
answer, and a search that finds the object is an observation that enters memory with
certainty - so memory quality shows up in the search: a better first room, fewer rooms
opened, more objects found. Those four end-to-end measures are the headline and live in
`three_prompts_outcomes`. This file answers one narrow question - what do the notes alone
contain - and every number it produces must be labelled that way.

WHY FREEZING IS STILL WORTH DOING. Inside a search-driven cell the robot can find the
object by walking into the room, and an object you have physically found hands you its
shelf for free. The diagnostic is shelf accuracy exactly equalling room accuracy - a
cell scoring 93.8% shelf and 93.8% room had been handed the shelf by its legs, which no
memory can do. So the live accuracy inside a cell is largely find-rate in different
units. Here the searches and the nightly writing run normally, the notes are then
frozen at the end of day 13 and day 23, and the questions are answered with looking
switched OFF.

THE FULL QUESTION WINDOW, NEVER A CAP. `max_questions` is not passed. A capped sample
takes the first two or three questions of every day, covers only hours 7-8 of a window
that runs 07:00 to 22:00, and lifts the trivial baseline by about 23 points. Days 14-23
give 240 questions a home.

THE SNAPSHOTS ARE REBUILT, NOT RERUN. `rebuild_the_frozen_snapshots` reconstructs the
notes at any day from the revision history and ASSERTS that rebuilding at the cell's
own last day reproduces `notes.json` exactly; a cell that fails that is skipped.

THE REASONING CAP IS A CONTRAST, NOT A FIX. `CONF_SCHEMA.reasoning` has maxLength 600.
Measured 2026-09-24 over the 15,560 frozen answers already on disk: 34.3% of answers sit
exactly at that ceiling and those are 36.4% correct against 49.4% for the rest, a 13-
point gap. That is correlational - a hard question produces long reasoning - so
`--roomier-reasoning` reruns the same notes and the same questions with the ceiling
raised, which is the causal test. It wraps the client rather than editing the shared
`CONF_SCHEMA`, because that schema is imported by other work.

    python -m self_improve.three_prompts_frozen --arms control rival_beliefs
    python -m self_improve.three_prompts_frozen --arms control --roomier-reasoning
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
from typing import Any, Dict, List, Optional

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FrozenHousehold
from self_improve.frozen_memory_test import FREEZE_POINTS, run_frozen_memory_test, sanity_assay
from self_improve.memory_notes import Notes
from self_improve.rebuild_the_frozen_snapshots import (check_the_reconstruction, rebuild,
                                                       which_day_each_observation_was_made)
from self_improve.study_settings import LOCKED
from self_improve.three_prompts import ARMS, PILOT_BANKS, PILOT_TEN, cell_dir

# The two freeze points the design turns on, plus the return. Day 13 is the control
# point: no arm has seen a disrupted day, so the arms should agree, and for the
# told-it arm the day-13 prompt is BYTE-IDENTICAL to the control's, so its day-13
# agreement is exact by construction rather than statistical.
FREEZE_DAYS = {"before anything changed": 13,
               "did it learn the new routine": 23,
               "did it keep the old routine": 28}

ROOMIER = "roomier_reasoning"
STANDARD = "standard_reasoning"


class RoomierReasoning:
    """A client that raises the reasoning ceiling, and nothing else.

    It wraps rather than replaces: the same endpoint, the same cache directory, the
    same temperature. Only the `reasoning` field's maxLength and the token budget move,
    and only for schemas that actually have that field, so the room-choice calls are
    untouched. The cache key includes the schema and max_tokens, so a roomier answer can
    never be served from a standard-cap cache entry or the other way round.
    """

    def __init__(self, inner: LLMClient, max_characters: int = 2400,
                 max_tokens: int = 1200) -> None:
        self.inner, self.max_characters, self.max_tokens = inner, max_characters, max_tokens
        self.n_raised = 0

    @property
    def stats(self):
        return self.inner.stats

    def complete(self, messages, schema, max_tokens: int = 400):
        if isinstance(schema, dict):
            reasoning = (schema.get("properties") or {}).get("reasoning")
            if isinstance(reasoning, dict) and "maxLength" in reasoning:
                schema = copy.deepcopy(schema)
                schema["properties"]["reasoning"]["maxLength"] = self.max_characters
                max_tokens = max(max_tokens, self.max_tokens)
                self.n_raised += 1
        return self.inner.complete(messages, schema, max_tokens)


def snapshots_for(cell: pathlib.Path, days: List[int]) -> Dict[int, pathlib.Path]:
    """Rebuild the frozen snapshots for one cell, refusing any cell whose
    reconstruction does not reproduce its own notes.json exactly."""
    notes = Notes.load(cell / "notes.json")
    observed_on = which_day_each_observation_was_made(cell / "looks.jsonl")
    ok, why = check_the_reconstruction(notes, observed_on)
    if not ok:
        raise AssertionError(f"{cell}: the reconstruction does not reproduce "
                             f"notes.json ({why}); no snapshot from it may be used")
    out: Dict[int, pathlib.Path] = {}
    for day in days:
        if notes.written_up_to_day < day:
            continue
        snapshot = rebuild(notes, day, observed_on)
        target = cell / f"notes_frozen_at_day_{day}.json"
        snapshot.path = target
        snapshot.save()
        back = Notes.load(target)
        if back.written_up_to_day != day:
            raise AssertionError(f"{target}: reloaded at day {back.written_up_to_day}, "
                                 f"wanted {day}")
        out[day] = target
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--banks", type=pathlib.Path, default=PILOT_BANKS)
    parser.add_argument("--arms", nargs="+", default=sorted(ARMS))
    parser.add_argument("--households", nargs="+", default=list(PILOT_TEN))
    parser.add_argument("--freeze-points", nargs="+",
                        default=["before anything changed", "did it learn the new routine"])
    parser.add_argument("--roomier-reasoning", action="store_true",
                        help="raise the reasoning ceiling from 600 to 2400 characters "
                             "and the token budget from 400 to 1200. A separate "
                             "contrast written to its own directory, never mixed with "
                             "the standard-cap numbers.")
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    args = parser.parse_args(argv)

    which = ROOMIER if args.roomier_reasoning else STANDARD
    inner = LLMClient(args.cache)
    client: Any = RoomierReasoning(inner) if args.roomier_reasoning else inner

    rows: List[Dict[str, Any]] = []
    problems: List[str] = []
    households: Dict[str, FrozenHousehold] = {}
    days = sorted({FREEZE_DAYS[f] for f in args.freeze_points})

    for arm in args.arms:
        for name in args.households:
            cell = cell_dir(args.root, arm, name)
            if not (cell / "notes.json").exists() or not (cell / "cell.json").exists():
                problems.append(f"{cell}: no finished cell yet")
                continue
            if name not in households:
                households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
            household = households[name]
            try:
                snapshots = snapshots_for(cell, days)
            except AssertionError as problem:
                problems.append(str(problem))
                continue
            for freeze_point in args.freeze_points:
                day = FREEZE_DAYS[freeze_point]
                if day not in snapshots:
                    problems.append(f"{cell}: never reached day {day}")
                    continue
                where = (args.root / "frozen" / which / arm / name
                         / freeze_point.replace(" ", "_"))
                try:
                    result = run_frozen_memory_test(
                        household, Notes.load(snapshots[day]), client, freeze_point,
                        LOCKED.read_budget_lines, where, max_questions=None)
                except ValueError as problem:
                    problems.append(f"{cell} / {freeze_point}: {problem}")
                    continue
                assay = sanity_assay(result)
                (where / "sanity_assay.json").write_text(json.dumps(assay, indent=1))
                reasoning_lengths = [len(a.get("reasoning") or "")
                                     for a in result["answers"]]
                ceiling = 2400 if args.roomier_reasoning else 600
                at_ceiling = sum(1 for n in reasoning_lengths if n >= ceiling - 5)
                row = {
                    "reasoning_cap": which, "arm": arm, "household": name,
                    "freeze_point": freeze_point, "notes_through_day": day,
                    "n_questions_asked": result["n_questions_asked"],
                    "n_questions_scored": result["n_questions_scored"],
                    "share_correct_shelf_NO_LOOKING": result["share_correct"],
                    "share_of_questions_where_the_read_budget_bit":
                        result.get("share_of_questions_where_the_budget_bit"),
                    "n_answers_at_the_reasoning_ceiling": at_ceiling,
                    "share_at_the_reasoning_ceiling":
                        at_ceiling / len(reasoning_lengths) if reasoning_lengths else None,
                    "question_ids": [a["question_id"] for a in result["answers"]],
                    "sanity_assay_concerns": assay["concerns"],
                }
                rows.append(row)
                print(f"{which:20s} {arm:20s} {name:12s} {freeze_point:28s} "
                      f"{result['share_correct']:.1%} shelf, no looking, "
                      f"{result['n_questions_scored']} questions, "
                      f"{row['share_at_the_reasoning_ceiling']:.0%} at the ceiling",
                      flush=True)
                for concern in assay["concerns"]:
                    print(f"      ASSAY: {concern}", flush=True)

    out = args.root / "frozen" / which
    out.mkdir(parents=True, exist_ok=True)
    # The filename carries the arms AND the households, because the follow-on driver runs
    # one (arm, household, freeze point) per process and a tag built from the arms alone
    # would have ten processes racing on one file.
    tag = ("_".join(a[:8] for a in args.arms) + "__"
           + ("all" if len(args.households) > 3
              else "_".join(h.replace("hh_", "") for h in args.households)))[:90]
    (out / f"frozen_results_{tag}.json").write_text(json.dumps(
        {"reasoning_cap": which, "rows": rows, "problems": problems,
         "note": ("the notes are frozen and no looking happens, so an answer cannot "
                  "have been obtained by finding the object. The full question window "
                  "is used, never a cap.")}, indent=1))
    if problems:
        print(f"\n{len(problems)} could not run:")
        for p in problems[:12]:
            print("   ", p)
    print(f"\nmodel calls {client.stats['calls']}, cache hits {client.stats['cached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
