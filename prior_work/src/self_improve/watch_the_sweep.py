"""Check a sweep while it runs, on whatever has been written so far.

Five checks, each of which has already cost this project a night at least once, or
would have:

1. notes that stop changing - a claim count that plateaus, or a night whose notes
   copy the night before. Real if the model answered and chose to change nothing;
   a bug if the call never landed. We separate those two.
2. empty or vacuous edits - the incremental arm must produce at least one edit on
   any night that saw an asked-about object. Verify the forcing fires, and that the
   share of edits carrying new information has not collapsed.
3. request failures - nights where the model did not answer. A cell that lost a
   fifth of its nights to timeouts looks like a weak arm rather than a broken one.
4. degenerate looking - all the looks in one room, or the same room every day.
5. rooms the claims never mention - the diagnostic that caught the chooser
   pathology. If a chooser's claims never mention the room the change moved into,
   the policy is not working, whatever its accuracy says.

    python -m self_improve.watch_the_sweep
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Any, Dict, List, Optional

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold


def rooms_the_change_moved_into(household: FrozenHousehold) -> set:
    def rooms_over(days):
        out = set()
        for day in days:
            for object_id in household.asked_objects:
                room = household.room_of_object(object_id, day * 86400 + 13 * 3600)
                if room != "beyond the reach of any look":
                    out.add(room)
        return out
    return rooms_over(range(14, 24)) - rooms_over(range(0, 14))


def check_one_cell(cell_dir: pathlib.Path, household: FrozenHousehold) -> Dict[str, Any]:
    nightly_path = cell_dir / "nightly.json"
    if not nightly_path.exists():
        return {"cell": cell_dir.name, "state": "nothing written yet"}
    nightly = json.loads(nightly_path.read_text())
    notes = json.loads((cell_dir / "notes.json").read_text()) if (cell_dir / "notes.json").exists() else {}
    claims = notes.get("claims", [])
    summaries = notes.get("nightly_summaries", [])
    problems: List[str] = []

    # 1. notes that stop changing
    claim_counts = [n.get("n_claims_after_tonight", 0) for n in nightly]
    copied = [n["day"] for n in nightly if n.get("identical_to_last_night")]
    copied_but_model_answered = [n["day"] for n in nightly
                                 if n.get("identical_to_last_night")
                                 and not n.get("model_call_failed")]
    plateau = 0
    for i in range(len(claim_counts) - 1, 0, -1):
        if claim_counts[i] == claim_counts[i - 1]:
            plateau += 1
        else:
            break

    # 2. empty or vacuous edits
    saw = [n for n in nightly if n.get("the_look_saw_something_it_is_asked_about")]
    silent = [n for n in saw if not n.get("n_edits_offered")]
    judged = [n["were_the_edits_vacuous"] for n in nightly
              if n.get("were_the_edits_vacuous", {}).get("n_edits")]
    n_edits = sum(j["n_edits"] for j in judged)
    n_new = sum(j["n_that_carried_something_new"] for j in judged)

    # 3. request failures
    failed = [n["day"] for n in nightly if n.get("model_call_failed")]

    # 4. degenerate looking
    rooms = [r for n in nightly for r in (n.get("rooms_looked_in") or [])]
    room_counts = collections.Counter(rooms)
    repeats = sum(1 for i in range(1, len(rooms)) if rooms[i] == rooms[i - 1])

    # 5. rooms the claims never mention
    text = " ".join(c["statement"] for c in claims).lower()
    if summaries:
        text += " " + summaries[-1]["summary"].lower()
    mentioned = {room for room in household.rooms if room in text}
    change_rooms = rooms_the_change_moved_into(household)

    report = {
        "cell": cell_dir.name,
        "nights_done": len(nightly),
        "n_claims": len(claims),
        "claim_count_by_night": claim_counts,
        "nights_the_claim_count_has_not_moved": plateau,
        "nights_that_copied_the_night_before": len(copied),
        "of_those_where_the_model_did_answer": len(copied_but_model_answered),
        "nights_that_saw_something": len(saw),
        "nights_that_saw_something_but_made_no_edit": len(silent),
        "n_edits": n_edits,
        "share_of_edits_that_carried_something_new": (n_new / n_edits) if n_edits else None,
        "nights_the_model_did_not_answer": len(failed),
        "share_of_nights_the_model_did_not_answer": len(failed) / len(nightly) if nightly else None,
        "n_distinct_rooms_looked_in": len(room_counts),
        "share_of_looks_in_the_commonest_room": (
            room_counts.most_common(1)[0][1] / len(rooms)) if rooms else None,
        "share_of_looks_repeating_the_previous_room": (
            repeats / (len(rooms) - 1)) if len(rooms) > 1 else None,
        "rooms_the_notes_mention": sorted(mentioned),
        "rooms_the_notes_never_mention": sorted(set(household.rooms) - mentioned),
        "rooms_the_change_moved_into": sorted(change_rooms),
        "notes_mention_a_room_the_change_moved_into": bool(change_rooms & mentioned),
    }

    if plateau >= 8 and len(nightly) > 10:
        problems.append(f"the claim count has not moved for {plateau} nights")
    if len(copied) > 0.5 * len(nightly):
        problems.append(
            f"{len(copied)} of {len(nightly)} nights copied the night before "
            f"({len(copied_but_model_answered)} of them with the model answering, so "
            f"{'mostly real' if len(copied_but_model_answered) > len(copied) / 2 else 'possibly a broken write path'})")
    if silent:
        problems.append(f"{len(silent)} nights saw something and made no edit: the "
                        f"forced-edit rule is not firing")
    if n_edits and n_new / n_edits < 0.5:
        problems.append(f"only {n_new / n_edits:.0%} of edits carried anything new")
    if report["share_of_nights_the_model_did_not_answer"] and \
            report["share_of_nights_the_model_did_not_answer"] > 0.1:
        problems.append(f"{report['share_of_nights_the_model_did_not_answer']:.0%} of "
                        f"nights lost the model call")
    if report["share_of_looks_in_the_commonest_room"] and len(nightly) > 8 and \
            report["share_of_looks_in_the_commonest_room"] > 0.6:
        problems.append(f"{report['share_of_looks_in_the_commonest_room']:.0%} of looks "
                        f"went to one room: the looking is degenerate")
    if change_rooms and not (change_rooms & mentioned) and len(nightly) > 18:
        problems.append(
            f"the notes never mention {sorted(change_rooms)}, where the change moved: "
            f"this cell cannot have noticed the disruption")
    report["problems"] = problems
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/cells"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    parser.add_argument("--quiet-if-clean", action="store_true")
    args = parser.parse_args(argv)

    from self_improve.run_one_cell import assert_the_fixed_cells_saw_the_same_looks

    households: Dict[str, FrozenHousehold] = {}
    everything = []
    for household_dir in sorted(args.root.glob("hh_s*")):
        name = household_dir.name
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        household = households[name]
        cells = [check_one_cell(d, household) for d in sorted(household_dir.iterdir())
                 if d.is_dir()]
        shared = assert_the_fixed_cells_saw_the_same_looks(args.root, name)
        everything.append({"household": name, "cells": cells,
                           "shared_look_stream_check": shared})

    for row in everything:
        done = [c for c in row["cells"] if c.get("nights_done")]
        print(f"=== {row['household']}: {len(done)} of 6 cells started")
        for c in row["cells"]:
            if not c.get("nights_done"):
                continue
            share_new = c["share_of_edits_that_carried_something_new"]
            print(f"  {c['cell']:64s} night {c['nights_done']:2d}/32 | "
                  f"claims {c['n_claims']:3d} | rooms {c['n_distinct_rooms_looked_in']:2d} | "
                  f"edits new {('%.0f%%' % (100 * share_new)) if share_new is not None else '  n/a'} | "
                  f"lost {c['nights_the_model_did_not_answer']}")
            for p in c["problems"]:
                print(f"      PROBLEM: {p}")
        s = row["shared_look_stream_check"]
        if s.get("checked"):
            print(f"  shared look stream for the two fixed cells: {s['verdict']}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(everything, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
