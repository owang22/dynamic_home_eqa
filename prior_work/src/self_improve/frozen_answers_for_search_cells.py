"""Run the frozen-memory test on the search-driven cells: freeze the notes, stop all
looking, answer the held-out questions from the notes alone.

Every answer inside a search-driven cell may have been obtained by LOOKING - a cell
opens 114 to 220 rooms to answer 80 questions and finds the object on 26 to 75 of them,
and an object you have physically found hands you its shelf for free. Shelf accuracy
exactly equalling room accuracy is the diagnostic, and a memory cannot produce it. So
those accuracy figures are largely find-rate in different units. THIS is the memory
measurement, and it is the only number from this framework comparable with the patrol
results.

The existing `answer_the_frozen_questions` walks a two-level sweep layout
(household/cell); the search-driven layout is three levels (household/sensing/format),
so this is its driver rather than a reimplementation - it calls the same
`run_frozen_memory_test` and the same `sanity_assay`.

    python -m self_improve.frozen_answers_for_search_cells --max-questions 40
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List, Optional

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.frozen_memory_test import (FREEZE_POINTS, run_frozen_memory_test,
                                             sanity_assay)
from self_improve.memory_notes import Notes
from self_improve.study_settings import LOCKED


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven/frozen"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    parser.add_argument("--max-questions", type=int, default=40)
    parser.add_argument("--freeze-points", nargs="+",
                        default=["before anything changed", "did it learn the new routine"])
    parser.add_argument("--only-household", default=None)
    parser.add_argument("--only-format", default=None)
    args = parser.parse_args(argv)

    client = LLMClient(args.cache)
    households: Dict[str, FrozenHousehold] = {}
    results: List[Dict[str, Any]] = []
    problems: List[str] = []

    for freeze_point in args.freeze_points:
        day = FREEZE_POINTS[freeze_point]["notes_through_day"]
        for snapshot in sorted(args.root.rglob(f"notes_frozen_at_day_{day}.json")):
            cell = snapshot.parent
            how = cell.name.replace("_", " ")
            sensing = cell.parent.name.replace("_", " ")
            household_name = cell.parent.parent.name
            configuration = ("no asked list" if "no_asked_list" in str(cell)
                             else "mechanical" if "mechanical" in str(cell)
                             else "told the asked list")
            if args.only_household and household_name != args.only_household:
                continue
            if args.only_format and how != args.only_format:
                continue
            if household_name not in households:
                households[household_name] = FrozenHousehold(
                    args.banks / f"{household_name}.jsonl")
            household = households[household_name]
            notes = Notes.load(snapshot)
            where = (args.out / configuration.replace(" ", "_") / household_name
                     / sensing.replace(" ", "_") / how.replace(" ", "_")
                     / freeze_point.replace(" ", "_"))
            try:
                result = run_frozen_memory_test(
                    household, notes, client, freeze_point, LOCKED.read_budget_lines,
                    where, max_questions=args.max_questions)
            except ValueError as problem:
                problems.append(f"{cell} / {freeze_point}: {problem}")
                continue
            assay = sanity_assay(result)
            (where / "sanity_assay.json").write_text(json.dumps(assay, indent=1))
            row = {
                "configuration": configuration, "household": household_name,
                "sensing_arm": sensing, "how_memory_is_written": how,
                "freeze_point": freeze_point,
                "n_questions_scored": result["n_questions_scored"],
                "share_correct_shelf_NO_LOOKING": result["share_correct"],
                "share_of_questions_where_the_read_budget_bit":
                    result.get("share_of_questions_where_the_budget_bit"),
                "sanity_assay_concerns": assay["concerns"],
            }
            results.append(row)
            print(f"{configuration:20s} {household_name} {sensing:22s} {how:18s} "
                  f"{freeze_point:28s} {result['share_correct']:.1%} shelf, no looking, "
                  f"{result['n_questions_scored']} questions", flush=True)
            for concern in assay["concerns"]:
                print(f"      ASSAY: {concern}", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    name = ("frozen_results.json" if not args.only_household
            else f"frozen_results_{args.only_household}.json")
    (args.out / name).write_text(json.dumps(
        {"results": results, "problems": problems,
         "note": ("these are the ONLY memory measurements from the search-driven "
                  "framework: the notes are frozen and no looking happens, so an "
                  "answer cannot have been obtained by finding the object")}, indent=1))
    if problems:
        print(f"\n{len(problems)} cells could not run:")
        for p in problems[:10]:
            print("   ", p)
    print(f"\nmodel calls {client.stats['calls']}, cache hits {client.stats['cached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
