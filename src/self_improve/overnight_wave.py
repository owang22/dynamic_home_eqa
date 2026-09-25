"""The overnight wave: five memory methods on the ten homes, with every gate kept.

WHY THIS EXISTS RATHER THAN `three_prompts`. That module injected prompt variants by
replacing `search_driven.write_the_notes` in-process. The prompts are now consolidated in
`what_the_robot_is_told`, so there is nothing to inject: an arm here is a `how_memory_is_written`
or a `sensing_arm` and nothing else. So this calls `search_driven.run_one_cell` directly and
keeps only the parts of the old runner that were about catching silent failure.

THE ARMS, in the order they matter. If time runs short the last three go, never the first two.

  1. the log and notes about the routine   ten homes. The robot reads its own record when
                                          asked, so its notes may not just copy places.
  2. claim store told if it was right      ten homes. ACE. TWO model calls a night.
  3. incremental edits                     ten homes. The plain claim store both are forks of.
  4. newest sighting, no model             ten homes. Calls NO model at all, so it is nearly
                                          free and needs no warm-up.
  5. prior only, no notes                  ten homes. Prices the prior. Without it we cannot
                                          say any of the above is the memory.
  6. wholesale rewrite                     ONE home. The published weak family and ACE's own
                                          baseline: it earns a reference, not ten cells.

FIVE GATES, every one of them because a wave was lost to the failure it catches:

  the header off disk     the cell's own `searches.jsonl` must say the asked-object list was
                          NOT in the prompt. A 42-cell wave ran a third of the way through
                          with it on because nothing read the artifact, only the code.
  a silent night          a night that saw an asked-about object and applied no edit is a
                          refusal. Night 0 has no looks and is out of scope.
  a completion that did   text came back, did not parse, the night wrote nothing, and
  not parse               `model_call_failed` stayed False. Refused.
  the read budget         if it truncated the notes on any question the arm was not run with
                          unlimited memory, whatever this module intended.
  a refused cell is       `run_one_cell` writes `cell.json` before any gate runs, and every
  RENAMED                 "which cells are missing" query treats that file as done. A refused
                          cell's file becomes `cell_REFUSED.json`.

    python -m self_improve.overnight_wave --arm "incremental edits" --household hh_s2_t03
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import time
from dataclasses import replace
from typing import Any, Dict, List, Optional, Tuple

from baselines.patrol.llm import LLMClient
from self_improve import search_driven as sd
from self_improve.frozen_household import FrozenHousehold
from self_improve.study_settings import LOCKED
from self_improve.three_prompts import PILOT_BANKS, PILOT_TEN, TimedClient, beat, take_the_lock

# No memory length limit, in writing or in reading. `search_driven` reads the budget off its
# module-global LOCKED at call time, so it is replaced in THIS PROCESS ONLY; the shared
# settings object is untouched because other jobs import it.
NO_LENGTH_LIMIT = replace(LOCKED, read_budget_lines=None)

# The asked-object list is OFF. Handing the writer the list of things it will be asked about
# turns the task from describing a home into caching answers to questions it knows are coming:
# measured, 94-100% of claims named an asked-about object with the list, 27% without it.
NAME_THE_QUIZ_LIST = False

MEMORY_GUIDED = sd.MEMORY_GUIDED

# arm name -> (how_memory_is_written, sensing_arm, how many homes)
ARMS: Dict[str, Tuple[str, str, int]] = {
    "the log and notes about the routine": ("the log and notes about the routine",
                                           MEMORY_GUIDED, 10),
    "claim store told if it was right": ("claim store told if it was right",
                                        MEMORY_GUIDED, 10),
    # MemGPT. A 1,200-character working memory in every prompt, an unbounded archive reached
    # only by searching, and the model moves notes between them. A write that would overflow
    # the working memory is REFUSED and the refusal handed back, which is the paper's
    # mechanism rather than an error. One call a night, plus a second only after a refusal.
    "a small working memory and an archive": ("a small working memory and an archive",
                                             MEMORY_GUIDED, 10),
    "incremental edits": ("incremental edits", MEMORY_GUIDED, 10),
    "newest sighting, no model": ("incremental edits", sd.NEWEST_SIGHTING, 10),
    "prior only, no notes": ("incremental edits", sd.PRIOR_ONLY, 10),
    "wholesale rewrite": ("wholesale rewrite", MEMORY_GUIDED, 1),
}
THE_ORDER = tuple(ARMS)

# ON HOLD, and the hold is in the code rather than in my head. MemGPT's five-day live check
# on hh_s109_t03 has to finish and be declared passed before its ten cells are queued: three
# new arms tonight have had a fault in their first hour. `cells_to_launch` refuses to emit a
# held arm, so a launcher cannot queue it by accident.
ON_HOLD = {"a small working memory and an archive":
           "waiting on the five-day live check at results/self_improve/memgpt/one_home"}


def cells_to_launch(arms=None, homes=PILOT_TEN):
    """(arm, household) pairs in priority order, with held arms refused.

    `newest sighting, no model` calls no model at all, so it is emitted first when it is in
    the list: it fills a gap for free while something else warms.
    """
    out = []
    for arm in (arms if arms is not None else THE_ORDER):
        if arm in ON_HOLD:
            raise RuntimeError(f"{arm!r} is ON HOLD: {ON_HOLD[arm]}. Refusing to queue it.")
        _how, _sensing, n_homes = ARMS[arm]
        for household in list(homes)[:n_homes]:
            out.append((arm, household))
    return out

# `newest sighting, no model` calls no model at all, so it writes no notes and has no
# night-one generation to warm. Everything else does.
NEEDS_WARMING = tuple(a for a in ARMS if a != "newest sighting, no model")


def cell_dir(out: pathlib.Path, arm: str, household: str) -> pathlib.Path:
    return out / "cells" / arm.replace(" ", "_").replace(",", "") / household


def run_one_arm(household: FrozenHousehold, arm: str, client: LLMClient,
                out_dir: pathlib.Path, last_day: int = 31,
                questions_per_day: int = 8, budget: int = 3, seed: int = 0
                ) -> Dict[str, Any]:
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; known: {list(ARMS)}")
    how, sensing, _homes = ARMS[arm]
    out_dir.mkdir(parents=True, exist_ok=True)
    take_the_lock(out_dir, arm, household.name)
    started = time.time()
    beat(out_dir, -1, last_day, arm, household.name, started)
    # THE DAY-RENDERER GUARD NEEDS NOTHING FROM THIS MODULE ANY MORE.
    #
    # It used to. `run_one_cell` asserts the note-writing prompt went through the
    # search-driven day renderer exactly once a night, and the record-reading arm built its
    # day with its own function that never called the counted one - while that function's
    # docstring claimed it did. So that arm could not start: the assert fired on day 0, and I
    # registered the render here rather than weakening the assert.
    #
    # Both are fixed upstream now. `the_day_this_arm_sees` calls
    # `write_the_notes._what_happened_today`, so the render is counted AND the arm sees
    # exactly what its control sees, absences included. Verified before removing the wrapper:
    # identical text and the counter incremented once, on looks with and without absences.
    #
    # Leaving the wrapper in would have been worse than useless: the upstream rename gave the
    # function a second required argument, so the wrapper's one-argument signature would have
    # raised - and had it matched, it would have counted the render TWICE and failed the very
    # assert it was written to satisfy.


    timed = TimedClient(client, out_dir)
    was_locked = sd.LOCKED
    sd.LOCKED = NO_LENGTH_LIMIT
    if sd.LOCKED.read_budget_lines is not None:
        raise AssertionError("the no-length-limit setting did not land on search_driven.LOCKED")
    try:
        result = sd.run_one_cell(
            household, how, sensing, timed, out_dir, last_day=last_day,
            questions_per_day=questions_per_day, budget=budget, seed=seed,
            tell_it_what_it_ruled_out=True,
            name_the_objects_it_will_be_quizzed_on=NAME_THE_QUIZ_LIST)
    finally:
        sd.LOCKED = was_locked

    def refuse(why: str) -> None:
        landed = out_dir / "cell.json"
        if landed.exists():
            landed.rename(out_dir / "cell_REFUSED.json")
        raise AssertionError(why)

    header = json.loads((out_dir / "searches.jsonl").open().readline())
    if header.get("name_the_objects_it_will_be_quizzed_on") != NAME_THE_QUIZ_LIST:
        refuse(f"{household.name}/{arm}: the cell's own header says the asked-object list "
               f"was {header.get('name_the_objects_it_will_be_quizzed_on')!r}, wanted "
               f"{NAME_THE_QUIZ_LIST!r}")
    bit = [r for r in result["searches"] if r.get("the_read_budget_bit")]
    if bit:
        refuse(f"{household.name}/{arm}: the read budget truncated the notes on {len(bit)} "
               f"questions, so this arm did not run with unlimited memory")
    nightly = result.get("nightly") or []
    did_not_parse = [n["day"] for n in nightly if n.get("the_completion_did_not_parse")]
    if did_not_parse:
        refuse(f"{household.name}/{arm}: the completion did not parse on nights "
               f"{did_not_parse}, so those nights wrote nothing")
    failed = [n["day"] for n in nightly if n.get("model_call_failed")]
    if failed:
        refuse(f"{household.name}/{arm}: the nightly call failed on nights {failed}")
    # a night that saw something and wrote nothing. Only for arms that write notes at all.
    if sensing != sd.NEWEST_SIGHTING:
        silent = [n["day"] for n in nightly
                  if n.get("the_look_saw_something_it_is_asked_about")
                  and not any((n.get("applied") or {}).values())
                  and not n.get("it_had_nothing_to_add")]
        if silent:
            refuse(f"{household.name}/{arm}: nights {silent} saw an asked-about object and "
                   f"applied no edit")

    about = {
        "arm": arm, "how_memory_is_written": how, "sensing_arm": sensing,
        "household": household.name, "bank": str(household.bank_path),
        "read_budget_lines": NO_LENGTH_LIMIT.read_budget_lines,
        "name_the_objects_it_will_be_quizzed_on_in_the_header":
            header.get("name_the_objects_it_will_be_quizzed_on"),
        "n_questions_where_the_read_budget_bit": len(bit),
        "n_nights_whose_completion_did_not_parse": len(did_not_parse),
        "n_model_calls_timed": timed.n_calls,
        "seconds": round(time.time() - started, 1),
        "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    (out_dir / "arm.json").write_text(json.dumps(about, indent=1))
    result["overnight_wave"] = about
    (out_dir / "cell.json").write_text(json.dumps(result, indent=1))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", required=True, choices=list(ARMS))
    parser.add_argument("--household", required=True)
    parser.add_argument("--banks", type=pathlib.Path, default=PILOT_BANKS)
    parser.add_argument("--last-day", type=int, default=31)
    parser.add_argument("--questions-per-day", type=int, default=8)
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/overnight_wave"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    args = parser.parse_args(argv)

    household = FrozenHousehold(args.banks / f"{args.household}.jsonl")
    client = LLMClient(args.cache)
    out = cell_dir(args.out, args.arm, household.name)
    result = run_one_arm(household, args.arm, client, out, args.last_day,
                         args.questions_per_day, args.budget, args.seed)
    print()
    print(json.dumps(result["overnight_wave"], indent=1))
    print(json.dumps(result["summary"], indent=1))
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
