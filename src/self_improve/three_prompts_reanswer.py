"""Does raising the answer step's generation ceiling change the answer? The causal test.

WHAT IS CAPPED. `baselines.patrol.llm.CONF_SCHEMA` gives the answer's `reasoning` field
`maxLength: 600`, and under guided decoding that is a hard ceiling: the model's reasoning
is cut off mid-thought and it then has to name a spot. Measured 2026-09-24 over the
15,560 frozen answers already on disk: **34.3% of answers sit exactly at 600 characters,
and those are 36.4% correct against 49.4% for the rest** - a 13-point gap. That is
CORRELATIONAL. A hard question produces long reasoning, so the gap could be entirely
about which questions hit the ceiling. Raising the ceiling and re-asking the same
questions from the same notes is the causal test, and it is the only way to tell the two
apart.

WHY THIS IS A RE-ANSWER RATHER THAN A RERUN. Inside a search-driven cell the answer step
runs AFTER all of that question's looking is finished, and nothing downstream reads the
answer: the notes are written from the look stream alone, and the next question's room
choice depends on the notes and the look history. So the answer cannot affect the search,
the observations or the memory. Re-asking it changes one number and nothing else, which
means the contrast is exact and costs a fraction of a rerun.

TWO KINDS OF QUESTION, AND ONLY ONE OF THEM CAN MOVE. A question whose search FOUND the
object is answered with the shelf the robot saw; no model call, no reasoning, no ceiling.
Only the questions answered FROM THE NOTES can move, so only those are re-asked - and the
report gives both the change on those questions and the change on the cell as a whole, in
that order, because the second is the first diluted by however often the search succeeded.

THE NOTES ARE RECONSTRUCTED, NOT GUESSED. The notes change only at night, so the notes a
question saw are the notes as they stood at the end of the previous day, which
`never_written_or_displaced.the_notes_as_they_stood` recovers exactly from the revision
history. The reconstruction is asserted against the cell's own `notes.json` before
anything is re-asked.

A CHECK THAT THE RE-ASK IS THE SAME QUESTION. Before the roomier call, the standard-cap
prompt is rebuilt and its answer must reproduce the answer the cell recorded. If it does
not, the prompt has not been reconstructed faithfully and the contrast is void, so the
cell is reported as a failure rather than scored. This is run for every cell and the count
of mismatches is in the output.

    python -m self_improve.three_prompts_reanswer --arms control
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

from baselines.patrol.llm import CONF_SCHEMA, LLMClient, parse_conf
from self_improve.frozen_household import FrozenHousehold
from self_improve.memory_notes import Notes
from self_improve.never_written_or_displaced import the_notes_as_they_stood
from self_improve.rebuild_the_frozen_snapshots import (check_the_reconstruction,
                                                       which_day_each_observation_was_made)
from self_improve.score_at_both_levels import room_of
from self_improve.search_driven import answer_prompt
from self_improve.three_prompts import ARMS, PILOT_BANKS, PILOT_TEN, cell_dir

ROOMIER_CHARACTERS = 2400
ROOMIER_TOKENS = 1200
STANDARD_CHARACTERS = 600
STANDARD_TOKENS = 400


def roomier_schema(max_characters: int = ROOMIER_CHARACTERS) -> Dict[str, Any]:
    """CONF_SCHEMA with one number changed. A deep copy, because CONF_SCHEMA is imported
    by other work and mutating it would silently move everyone else's numbers."""
    schema = copy.deepcopy(CONF_SCHEMA)
    schema["properties"]["reasoning"]["maxLength"] = max_characters
    return schema


def one_cell(cell: pathlib.Path, household: FrozenHousehold, client: LLMClient,
             max_characters: int = ROOMIER_CHARACTERS) -> Optional[Dict[str, Any]]:
    the_cell = json.loads((cell / "cell.json").read_text())
    notes = Notes.load(cell / "notes.json")
    observed_on = which_day_each_observation_was_made(cell / "looks.jsonl")
    ok, why = check_the_reconstruction(notes, observed_on)
    if not ok:
        return {"where": str(cell), "refused": f"reconstruction does not reproduce "
                                               f"notes.json: {why}"}
    allowed = set(household.places)
    schema = roomier_schema(max_characters)

    from_the_notes = [r for r in the_cell["searches"] if r["answered_from"] == "the notes"]
    rows: List[Dict[str, Any]] = []
    n_prompt_mismatches = 0
    stood_cache: Dict[int, Notes] = {}
    for record in from_the_notes:
        day = record["day"]
        if day - 1 not in stood_cache:
            stood_cache[day - 1] = the_notes_as_they_stood(notes, day - 1)
        stood = stood_cache[day - 1]
        was_read = stood.what_the_robot_can_read(None, about_object=record["object_id"])
        question = {"day_index": day, "t_query": record["time"],
                    "object_id": record["object_id"]}
        ruled_out = (record["rooms_opened"]
                     if record["the_answer_was_told_what_the_search_ruled_out"] else ())
        messages = answer_prompt(household, question, was_read.text, ruled_out)

        # the faithfulness check: the standard-cap prompt must reproduce what the cell
        # recorded. Served from the cache, so it costs nothing.
        again, _ = client.complete(messages, CONF_SCHEMA, max_tokens=STANDARD_TOKENS)
        same_place, _c, same_why, _s = parse_conf(again, allowed)
        faithful = same_place == record["answer_place"]
        if not faithful:
            n_prompt_mismatches += 1

        text, _ = client.complete(messages, schema, max_tokens=ROOMIER_TOKENS)
        place, confidence, reasoning, status = parse_conf(text, allowed)
        true_place = record["true_place"]
        rows.append({
            "question_id": record["question_id"], "object_id": record["object_id"],
            "day": day, "period": record["period"], "is_a_mover": record["is_a_mover"],
            "true_place": true_place,
            "standard_answer": record["answer_place"],
            "standard_correct_place": record["correct_place"],
            "standard_correct_room": record["correct_room"],
            "standard_reasoning_characters": len(same_why or ""),
            "roomier_answer": place,
            "roomier_correct_place": (None if place is None or not true_place
                                      else place == true_place),
            "roomier_correct_room": (None if place is None or not true_place else
                                     room_of(household, place)
                                     == room_of(household, true_place)),
            "roomier_reasoning_characters": len(reasoning or ""),
            "roomier_parse_status": status,
            "the_prompt_reproduced_the_cell's_answer": faithful,
        })

    def share(field: str, among: Sequence[Dict[str, Any]]) -> Optional[float]:
        got = [r for r in among if r[field] is not None]
        return (sum(1 for r in got if r[field]) / len(got)) if got else None

    at_the_old_ceiling = [r for r in rows
                          if r["standard_reasoning_characters"] >= STANDARD_CHARACTERS - 5]
    n_found = sum(1 for r in the_cell["searches"] if r["found_it"])
    n_all = len([r for r in the_cell["searches"] if r["correct_place"] is not None])
    return {
        "where": str(cell), "household": household.name,
        "arm": (the_cell.get("three_prompts") or {}).get("arm"),
        "how_memory_is_written": the_cell["how_memory_is_written"],
        "n_questions_in_the_cell": n_all,
        "n_answered_by_finding_it": n_found,
        "n_answered_from_the_notes": len(rows),
        "n_prompt_mismatches": n_prompt_mismatches,
        "the_reconstruction_is_faithful": n_prompt_mismatches == 0,
        # on the questions that CAN move
        "on_the_notes_answered_questions": {
            "n": len(rows),
            "standard_shelf": share("standard_correct_place", rows),
            "roomier_shelf": share("roomier_correct_place", rows),
            "standard_room": share("standard_correct_room", rows),
            "roomier_room": share("roomier_correct_room", rows),
            "mean_reasoning_characters_standard":
                statistics.mean(r["standard_reasoning_characters"] for r in rows)
                if rows else None,
            "mean_reasoning_characters_roomier":
                statistics.mean(r["roomier_reasoning_characters"] for r in rows)
                if rows else None,
            "share_at_the_old_600_ceiling": len(at_the_old_ceiling) / len(rows) if rows else None,
            "share_still_at_the_new_ceiling":
                sum(1 for r in rows
                    if r["roomier_reasoning_characters"] >= max_characters - 5)
                / len(rows) if rows else None,
        },
        # the same questions, but only those that HIT the old ceiling: where the cap
        # could actually have bitten
        "on_the_questions_that_hit_the_old_ceiling": {
            "n": len(at_the_old_ceiling),
            "standard_shelf": share("standard_correct_place", at_the_old_ceiling),
            "roomier_shelf": share("roomier_correct_place", at_the_old_ceiling),
            "standard_room": share("standard_correct_room", at_the_old_ceiling),
            "roomier_room": share("roomier_correct_room", at_the_old_ceiling),
        },
        # the whole cell, with found answers carried over unchanged - the headline unit
        "whole_cell": {
            "n": n_all,
            "standard_shelf": (sum(1 for r in the_cell["searches"] if r["correct_place"])
                               / n_all) if n_all else None,
            "roomier_shelf": ((sum(1 for r in the_cell["searches"]
                                   if r["correct_place"] and r["answered_from"] != "the notes")
                               + sum(1 for r in rows if r["roomier_correct_place"]))
                              / n_all) if n_all else None,
            "standard_room": (sum(1 for r in the_cell["searches"] if r["correct_room"])
                              / n_all) if n_all else None,
            "roomier_room": ((sum(1 for r in the_cell["searches"]
                                  if r["correct_room"] and r["answered_from"] != "the notes")
                              + sum(1 for r in rows if r["roomier_correct_room"]))
                             / n_all) if n_all else None,
        },
        "answers": rows,
    }


def gather(root: pathlib.Path) -> List[Dict[str, Any]]:
    """Every per-cell result already on disk. No model call."""
    out: List[Dict[str, Any]] = []
    for path in sorted((root / "reanswer").rglob("*.json")):
        try:
            out.append(json.loads(path.read_text())["cell"])
        except (ValueError, KeyError):
            continue
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--gather", action="store_true",
                        help="rebuild the aggregate from the per-cell files, no model call")
    parser.add_argument("--banks", type=pathlib.Path, default=PILOT_BANKS)
    parser.add_argument("--arms", nargs="+", default=sorted(ARMS))
    parser.add_argument("--households", nargs="+", default=list(PILOT_TEN))
    parser.add_argument("--max-characters", type=int, default=ROOMIER_CHARACTERS)
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    args = parser.parse_args(argv)

    client = LLMClient(args.cache)
    households: Dict[str, FrozenHousehold] = {}
    results: List[Dict[str, Any]] = []
    for arm in args.arms:
        for name in args.households:
            cell = cell_dir(args.root, arm, name)
            if not (cell / "cell.json").exists():
                continue
            if name not in households:
                households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
            got = one_cell(cell, households[name], client, args.max_characters)
            if got is None:
                continue
            if got.get("refused"):
                print(f"REFUSED {arm:22s} {name:12s} {got['refused']}", flush=True)
                results.append(got)
                continue
            n = got["on_the_notes_answered_questions"]
            print(f"{arm:22s} {name:12s} notes-answered {n['n']:4d} of "
                  f"{got['n_questions_in_the_cell']:4d}  shelf "
                  f"{n['standard_shelf']:.1%} -> {n['roomier_shelf']:.1%}  room "
                  f"{n['standard_room']:.1%} -> {n['roomier_room']:.1%}  "
                  f"({n['share_at_the_old_600_ceiling']:.0%} hit the old ceiling, "
                  f"{n['share_still_at_the_new_ceiling']:.0%} hit the new one"
                  + ("" if got["the_reconstruction_is_faithful"]
                     else f", {got['n_prompt_mismatches']} PROMPT MISMATCHES") + ")",
                  flush=True)
            results.append(got)
            # PER CELL, not one shared file. A single output path meant sixty parallel
            # re-answer processes would clobber one another, and the driver that waits for
            # a per-cell marker would never see one and would relaunch every cell every
            # ninety seconds for ever. Written as the cell finishes, so a partial run
            # leaves usable results.
            mine = args.root / "reanswer" / arm / f"{name}.json"
            mine.parent.mkdir(parents=True, exist_ok=True)
            mine.write_text(json.dumps({
                "standard": {"reasoning_max_characters": STANDARD_CHARACTERS,
                             "max_tokens": STANDARD_TOKENS},
                "roomier": {"reasoning_max_characters": args.max_characters,
                            "max_tokens": ROOMIER_TOKENS},
                "cell": got}, indent=1))

    # The aggregate is only written by a run that covered more than one cell, so the
    # per-cell driver processes never race on it. `--gather` rebuilds it from the per-cell
    # files without any model call.
    if args.gather or len(results) > 1:
        results = gather(args.root) if args.gather else results
    out = args.root / "the_answer_step_token_budget.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if len(results) > 1:
        out.write_text(json.dumps({
            "standard": {"reasoning_max_characters": STANDARD_CHARACTERS,
                         "max_tokens": STANDARD_TOKENS},
            "roomier": {"reasoning_max_characters": args.max_characters,
                        "max_tokens": ROOMIER_TOKENS},
            "note": ("the answer step runs after all looking for its question, and "
                     "nothing downstream reads the answer, so re-asking it changes one "
                     "number and nothing else: the contrast is exact"),
            "per_cell": results}, indent=1))
    good = [r for r in results if not r.get("refused")]
    if good:
        print()
        for label, key in (("on the questions answered from the notes",
                            "on_the_notes_answered_questions"),
                           ("on the questions that HIT the old 600 ceiling",
                            "on_the_questions_that_hit_the_old_ceiling"),
                           ("on the whole cell, found answers carried over", "whole_cell")):
            pairs = [(r[key]["standard_shelf"], r[key]["roomier_shelf"],
                      r[key]["standard_room"], r[key]["roomier_room"])
                     for r in good if r[key]["n"] and r[key]["standard_shelf"] is not None
                     and r[key]["roomier_shelf"] is not None]
            if len(pairs) < 2:
                continue
            shelf = [b - a for a, b, _c, _d in pairs]
            room = [d - c for _a, _b, c, d in pairs]
            for level, deltas in (("shelf", shelf), ("room", room)):
                mean = statistics.mean(deltas)
                se = statistics.stdev(deltas) / (len(deltas) ** 0.5)
                verdict = ("raising the cap HELPS" if mean > 2 * se else
                           "raising the cap HURTS" if -mean > 2 * se else
                           f"no change beyond 2 se; excludes a change larger "
                           f"than {2 * se:.1%}")
                print(f"  {label:48s} {level:5s} {mean:+6.1%} +- {2*se:.1%} "
                      f"(n={len(deltas)} cells, "
                      f"{sum(1 for d in deltas if d > 0)} up / "
                      f"{sum(1 for d in deltas if d < 0)} down) -> {verdict}")
    print(f"\nwritten to {out}")
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
