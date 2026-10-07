"""Run the primary measurement. This is the caller `frozen_memory_test` never had.

Until now every number in this study was about what the notes CONTAIN. This is the
step that asks whether the notes HELP: freeze each arm's notes at each freeze point,
put the same questions to every arm with no further looking, and score them.

Three things this does that a bare accuracy run would not:

  it runs `sanity_assay` on each arm's first answers BEFORE any accuracy figure is
  believed, because both degenerate arms that cost this project a night would have
  been caught by it and neither would have shown up in accuracy;

  it reports each result as a share of the room its own freeze point has, against
  that point's measured floor and ceiling, so a number lands as "a third of the room
  available" rather than as a bare percentage;

  it says explicitly whether the control point - before anything changed, where no
  arm has seen a disrupted day - is the null it is supposed to be. If the arms
  differ there, something other than the intervention differs and every later number
  is suspect.

    python -m self_improve.answer_the_frozen_questions \
        --sweeps results/self_improve/memory_factor_v1 \
                 results/self_improve/looking_factor_illness_v1
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.frozen_memory_test import (FREEZE_POINTS, questions_in_the_window,
                                             run_frozen_memory_test, sanity_assay,
                                             yardsticks_for_a_window)
from self_improve.memory_notes import Notes
from self_improve.study_settings import LOCKED

CONTROL_POINT = "before anything changed"


def floor_and_ceiling(household: FrozenHousehold, freeze_point: str) -> Dict[str, float]:
    """This freeze point's room, measured on this household rather than assumed."""
    plan = FREEZE_POINTS[freeze_point]
    questions = questions_in_the_window(household, plan["questions_from_days"])
    yardsticks = yardsticks_for_a_window(household, questions)
    return {"floor_a_never_updated_memory_reaches": yardsticks["settled_memory_never_updated"],
            "ceiling_the_per_object_oracle_reaches": yardsticks["per_object_oracle"],
            "one_fact_for_the_whole_house": yardsticks["one_fact_for_the_whole_house"],
            "room_available": (yardsticks["per_object_oracle"]
                               - yardsticks["settled_memory_never_updated"])}


def share_of_the_room(share_correct: Optional[float], room: Dict[str, float]
                      ) -> Optional[float]:
    """Where in the room between floor and ceiling this arm landed. 0 means it did no
    better than never updating; 1 means it matched the oracle. Negative means worse
    than not updating at all, which is a real and reportable outcome."""
    if share_correct is None or not room["room_available"]:
        return None
    return ((share_correct - room["floor_a_never_updated_memory_reaches"])
            / room["room_available"])


def find_the_cells(sweep_roots: Sequence[pathlib.Path]) -> Dict[str, Dict[str, pathlib.Path]]:
    """household -> arm name -> directory, across both sweep layouts.

    The memory-factor sweep names its arms by directory ("wholesale_rewrite"), the
    looking-factor sweep by memory format and looking arm
    ("incremental_edits__the_repaired_chooser"). Both are read as they are.
    """
    found: Dict[str, Dict[str, pathlib.Path]] = collections.defaultdict(dict)
    for root in sweep_roots:
        if not root.exists():
            continue
        for household_dir in sorted(root.glob("hh_s*")):
            for cell_dir in sorted(d for d in household_dir.iterdir() if d.is_dir()):
                arm = cell_dir.name
                if root.name not in arm:
                    arm = f"{arm} [{root.name}]"
                found[household_dir.name][arm] = cell_dir
    return found


def run_everything(sweep_roots: Sequence[pathlib.Path], banks: pathlib.Path,
                   client: LLMClient, out_dir: pathlib.Path,
                   max_questions: Optional[int], only_freeze_points: Sequence[str],
                   only_households: Optional[Sequence[str]] = None,
                   read_budget_lines: Optional[int] = None) -> Dict[str, Any]:
    # None means the locked setting. A number here is a DIAGNOSTIC, never an arm: it
    # is reported beside the main result under its own name so nobody later mistakes
    # it for a condition of the study. LOCKED is not modified.
    budget = LOCKED.read_budget_lines if read_budget_lines is None else read_budget_lines
    cells = find_the_cells(sweep_roots)
    # One process per household, because the client blocks: concurrency has to come
    # from running several processes. Serially, a first pass over ten households at
    # 30 questions a cell is about 2,400 blocking calls.
    if only_households:
        cells = {k: v for k, v in cells.items() if k in set(only_households)}
    households: Dict[str, FrozenHousehold] = {}
    results: List[Dict[str, Any]] = []
    assay_problems: List[str] = []

    for household_name, arms in sorted(cells.items()):
        if household_name not in households:
            households[household_name] = FrozenHousehold(banks / f"{household_name}.jsonl")
        household = households[household_name]
        for arm_name, cell_dir in sorted(arms.items()):
            for freeze_point in only_freeze_points:
                day = FREEZE_POINTS[freeze_point]["notes_through_day"]
                snapshot = cell_dir / f"notes_frozen_at_day_{day}.json"
                if not snapshot.exists():
                    continue
                notes = Notes.load(snapshot)
                where = out_dir / household_name / arm_name.replace(" ", "_") / \
                    freeze_point.replace(" ", "_")
                try:
                    result = run_frozen_memory_test(
                        household, notes, client, freeze_point,
                        budget, where, max_questions=max_questions)
                except ValueError as problem:
                    results.append({"household": household_name, "arm": arm_name,
                                    "freeze_point": freeze_point,
                                    "could_not_run": str(problem)})
                    continue

                assay = sanity_assay(result)
                (where / "sanity_assay.json").write_text(json.dumps(assay, indent=1))
                room = floor_and_ceiling(household, freeze_point)
                is_diagnostic = read_budget_lines is not None
                row = {
                    "household": household_name, "arm": arm_name,
                    "freeze_point": freeze_point,
                    "n_questions_scored": result["n_questions_scored"],
                    "share_correct": result["share_correct"],
                    **room,
                    "share_of_the_room_it_took": share_of_the_room(result["share_correct"], room),
                    "sanity_assay": assay,
                    "share_of_questions_where_the_read_budget_bit":
                        result.get("share_of_questions_where_the_budget_bit"),
                    "read_budget_lines": budget,
                    "this_is_a_diagnostic_not_an_arm": is_diagnostic,
                }
                results.append(row)
                if assay["concerns"]:
                    for concern in assay["concerns"]:
                        assay_problems.append(
                            f"{household_name} / {arm_name} / {freeze_point}: {concern}")
                print(f"{household_name} | {arm_name:56s} | {freeze_point:34s} "
                      f"{result['share_correct']:.0%} correct "
                      f"(floor {room['floor_a_never_updated_memory_reaches']:.0%}, "
                      f"ceiling {room['ceiling_the_per_object_oracle_reaches']:.0%}) = "
                      f"{share_of_the_room(result['share_correct'], room):+.0%} of the room",
                      flush=True)
                for concern in assay["concerns"]:
                    print(f"      ASSAY CONCERN: {concern}", flush=True)

    control = is_the_control_point_the_null_it_should_be(results)
    summary = {"results": results, "sanity_assay_problems": assay_problems,
               "the_control_point": control}
    out_dir.mkdir(parents=True, exist_ok=True)
    name = ("frozen_memory_results.json" if not only_households
            else f"frozen_memory_results_{'_'.join(sorted(only_households))}.json")
    (out_dir / name).write_text(json.dumps(summary, indent=1))
    return summary


def is_the_control_point_the_null_it_should_be(results: Sequence[Dict[str, Any]]
                                              ) -> Dict[str, Any]:
    """At the control point no arm has seen a disrupted day, so the arms should
    agree. If they do not, something other than the intervention differs and every
    later number is suspect."""
    by_household: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    for row in results:
        if row.get("freeze_point") != CONTROL_POINT or row.get("share_correct") is None:
            continue
        by_household[row["household"]][row["arm"]] = row["share_correct"]
    spreads = {h: (max(a.values()) - min(a.values()))
               for h, a in by_household.items() if len(a) > 1}
    if not spreads:
        return {"checked": False,
                "why": "fewer than two arms have answered at the control point"}
    biggest = max(spreads.values())
    return {
        "checked": True,
        "n_households": len(spreads),
        "spread_between_arms_per_household": spreads,
        "largest_spread": biggest,
        "the_noise_floor_this_server_costs_us": LOCKED.noise_floor,
        "is_it_the_null_it_should_be": biggest <= LOCKED.noise_floor,
        "verdict": ("the arms agree at the control point, within the "
                    f"{LOCKED.noise_floor:.0%} the server's own non-determinism costs "
                    "us, so the later numbers rest on comparable arms"
                    if biggest <= LOCKED.noise_floor else
                    f"the arms differ by up to {biggest:.0%} at the control point, more "
                    f"than the {LOCKED.noise_floor:.0%} noise floor: something other "
                    f"than the intervention differs and EVERY later number is suspect"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweeps", type=pathlib.Path, nargs="+", required=True)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    parser.add_argument("--max-questions", type=int, default=None,
                        help="cap per freeze point. The window holds 72 to 240; a cap "
                             "buys speed at the price of a wider standard error, and "
                             "the number asked is recorded either way.")
    parser.add_argument("--freeze-points", nargs="+", default=list(FREEZE_POINTS),
                        choices=list(FREEZE_POINTS))
    parser.add_argument("--read-budget-lines", type=int, default=None,
                        help="DIAGNOSTIC ONLY: override the locked 8-line read window "
                             "to bound what reading more could buy. Results carry "
                             "this_is_a_diagnostic_not_an_arm so they are never read "
                             "as a condition of the study.")
    parser.add_argument("--households", nargs="+", default=None,
                        help="run only these; one process per household is how this "
                             "step gets concurrency, since the client blocks")
    args = parser.parse_args(argv)

    client = LLMClient(args.cache)
    summary = run_everything(args.sweeps, args.banks, client, args.out,
                             args.max_questions, args.freeze_points, args.households,
                             args.read_budget_lines)
    print()
    print("the control point:", summary["the_control_point"].get("verdict",
                                summary["the_control_point"].get("why")))
    if summary["sanity_assay_problems"]:
        print(f"{len(summary['sanity_assay_problems'])} sanity-assay concerns:")
        for problem in summary["sanity_assay_problems"][:10]:
            print("  ", problem)
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
