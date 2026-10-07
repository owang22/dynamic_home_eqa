"""How many moved things does the room the chooser picked actually receive?

A within-household, between-rooms comparison, so it carries none of the selection-bias
trouble that dogs moved-object slices: the question is only "of the rooms available, did
it pick a good one", and every room is scored the same way.

The measure exists because a fixation can be shown not to be positional and still be
wrong. In `hh_s6_t03` the repaired chooser picked `living` on six of seven looks while
that room's position moved through 1, 2, 3 and 4 - so the choice is about content, not
about where the room sat in the list - but `living` receives one of the six moved objects
while `bedroom_1` receives three.

Read alongside the claim counts the chooser was shown, the mechanism is visible: at the
moment of choosing, the notes held **zero** claims about `living` and `storage` and two to
six about every other room, and those two rooms are exactly the ones it picked. So the
objective rewards whatever room the notes predict worst, and how badly the notes predict a
room has little to do with whether looking there would settle anything. **Least evidence
looks like least certainty.** That account covers both fixations without needing the room
to be empty, which the earlier "a permanently empty room is perfectly unpredictable"
sentence did not.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.measure_timeliness import where_the_moved_things_went
from self_improve.score_at_both_levels import room_of


def moved_things_per_room(household: FrozenHousehold) -> Dict[str, int]:
    """How many of the disruption's moved objects end up in each room."""
    counts: collections.Counter = collections.Counter()
    for _, place in where_the_moved_things_went(household).items():
        room = room_of(household, place)
        if room:
            counts[room] += 1
    return dict(counts)


def judge_a_look_stream(looks_file: pathlib.Path, household: FrozenHousehold,
                        per_room: Optional[Dict[str, int]] = None
                        ) -> Optional[Dict[str, Any]]:
    """`per_room` is passed in when judging several streams of one household, because
    working it out walks every object across every hour of the month."""
    if not looks_file.exists():
        return None
    if per_room is None:
        per_room = moved_things_per_room(household)
    if not per_room:
        return None
    best_room, best_count = max(per_room.items(), key=lambda kv: kv[1])
    total_moved = sum(per_room.values())

    chosen: List[str] = []
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") != "look" or "walkthrough" in row.get("chosen_by", ""):
            continue
        chosen.append(row["targets"][0]["name"])
    if not chosen:
        return None
    counts = collections.Counter(chosen)
    commonest, times = counts.most_common(1)[0]
    # What every look, not just the commonest room, actually bought.
    received = statistics.fmean(per_room.get(room, 0) for room in chosen)
    return {
        "n_looks": len(chosen),
        "n_distinct_rooms": len(counts),
        "the_room_it_chose_most": commonest,
        "times_it_chose_that_room": times,
        "moved_things_that_room_receives": per_room.get(commonest, 0),
        "mean_moved_things_per_look": received,
        "the_best_room_available": best_room,
        "moved_things_the_best_room_receives": best_count,
        "n_moved_things_in_this_household": total_moved,
        "moved_things_per_room": per_room,
        "how_many_it_gave_up_per_look_against_always_choosing_the_best_room":
            best_count - received,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweeps", type=pathlib.Path, nargs="+", required=True)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path(
                            "results/self_improve/was_the_room_worth_visiting.json"))
    args = parser.parse_args(argv)

    rows = []
    for root in args.sweeps:
        for household_dir in sorted(root.glob("hh_s*")):
            name = household_dir.name
            household = FrozenHousehold(args.banks / f"{name}.jsonl")
            per_room = moved_things_per_room(household)
            for cell_dir in sorted(d for d in household_dir.iterdir() if d.is_dir()):
                verdict = judge_a_look_stream(cell_dir / "looks.jsonl", household, per_room)
                if verdict:
                    rows.append({"household": name, "cell": cell_dir.name,
                                 "sweep": root.name, **verdict})
                    r = rows[-1]
                    print(f"{name} {r['cell'][:40]:40s} chose {r['the_room_it_chose_most']:10s} "
                          f"{r['times_it_chose_that_room']:2d}/{r['n_looks']:2d} -> that room "
                          f"receives {r['moved_things_that_room_receives']} of "
                          f"{r['n_moved_things_in_this_household']} moved things; best was "
                          f"{r['the_best_room_available']} with "
                          f"{r['moved_things_the_best_room_receives']}", flush=True)
    if not rows:
        print("no look streams found")
        return 0
    gave_up = [r["how_many_it_gave_up_per_look_against_always_choosing_the_best_room"]
               for r in rows]
    print()
    print(f"across {len(rows)} look streams, each look saw a mean of "
          f"{statistics.fmean(r['mean_moved_things_per_look'] for r in rows):.2f} moved "
          f"things, against {statistics.fmean(r['moved_things_the_best_room_receives'] for r in rows):.2f} "
          f"if it had always gone to the best room: a shortfall of "
          f"{statistics.fmean(gave_up):.2f} per look")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
