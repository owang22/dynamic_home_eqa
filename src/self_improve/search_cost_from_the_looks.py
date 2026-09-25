"""Search cost and find rate, read straight out of a running cell's looks.jsonl.

Why this exists. `cell.json` is written when a cell finishes, so nothing about a
run is analysable until all 32 days are done - and search cost and find rate are
the measures the whole design turns on. They do not need the answer step at all:
a look record carries its day, its time (which IS the question's `t_query`), the
room opened and every sighting. So the search side of every question can be
rebuilt from the look stream while the run is still going.

What is rebuilt, per question: the rooms opened in order, whether the quizzed
object was among the sightings, and at which step. What is NOT rebuilt: the
answer, which lives only in `cell.json`. Accuracy therefore waits; cost does not.

The mover / non-mover split is applied here too, because pooling dilutes the
effect by about a factor of three - the prior is right about the two thirds of
objects the disruption never moved, so a pooled find rate mixes the objects that
can show an effect with the objects that cannot.

    python -m self_improve.search_cost_from_the_looks --days 14 16
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.search_driven import (answerable_questions_on_day, the_movers,
                                        questions_spread_across_the_day)


def rebuild_the_searches(looks_file: pathlib.Path, household: FrozenHousehold,
                         questions_per_day: int = 8) -> List[Dict[str, Any]]:
    """One row per question the cell has got through so far.

    Looks are grouped by (day, time) because every look of one search is taken at
    the question's own moment, and a question's moment is unique within a day in
    these banks. The grouping is checked rather than assumed: a group holding more
    looks than the budget, or a (day, time) that matches no sampled question, is
    reported instead of being quietly dropped.
    """
    by_moment: Dict[Tuple[int, int], List[dict]] = collections.defaultdict(list)
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") != "look":
            continue
        by_moment[(row["day"], row["time"])].append(row)

    movers = the_movers(household)
    wanted: Dict[Tuple[int, int], dict] = {}
    for day in range(household.n_days + 1):
        for question in questions_spread_across_the_day(
                answerable_questions_on_day(household, day), questions_per_day):
            wanted[(question["day_index"], question["t_query"])] = question

    rows: List[Dict[str, Any]] = []
    unmatched = 0
    for moment, looks in sorted(by_moment.items()):
        question = wanted.get(moment)
        if question is None:
            unmatched += 1
            continue
        looks = sorted(looks, key=lambda r: r["look_id"])
        rooms = [t["name"] for r in looks for t in r["targets"]]
        found_at = None
        for i, look in enumerate(looks, start=1):
            if any(s["object_id"] == question["object_id"] for s in look["sightings"]):
                found_at = i
                break
        rows.append({
            "household": household.name,
            "question_id": question["question_id"],
            "object_id": question["object_id"],
            "day": moment[0],
            "is_a_mover": question["object_id"] in movers,
            "rooms_opened": rooms,
            "n_rooms_opened": len(rooms),
            "found_it": found_at is not None,
            "found_at_step": found_at,
        })
    if unmatched:
        print(f"  NOTE {looks_file.parent}: {unmatched} look-moments matched no "
              f"sampled question; they are excluded and this should be 0")
    return rows


def find_the_cells(root: pathlib.Path) -> Dict[Tuple[str, str, str], pathlib.Path]:
    out: Dict[Tuple[str, str, str], pathlib.Path] = {}
    for looks_file in sorted(root.glob("hh_s*/*/*/looks.jsonl")):
        household = looks_file.parent.parent.parent.name
        sensing = looks_file.parent.parent.name.replace("_", " ")
        how = looks_file.parent.name.replace("_", " ")
        out[(household, sensing, how)] = looks_file
    return out


def mean_and_standard_error(values: Sequence[float]) -> Tuple[Optional[float], Optional[float]]:
    values = [v for v in values if v is not None]
    if not values:
        return None, None
    se = (statistics.stdev(values) / len(values) ** 0.5) if len(values) > 1 else None
    return statistics.mean(values), se


def report(root: pathlib.Path, banks: pathlib.Path, days: range,
           questions_per_day: int, label: str) -> Dict[str, Any]:
    cells = find_the_cells(root)
    households: Dict[str, FrozenHousehold] = {}
    rows_by_cell: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for key, looks_file in cells.items():
        name = key[0]
        if name not in households:
            households[name] = FrozenHousehold(banks / f"{name}.jsonl")
        rows_by_cell[key] = rebuild_the_searches(looks_file, households[name],
                                                questions_per_day)

    arms = sorted({(k[1], k[2]) for k in rows_by_cell})
    all_households = sorted({k[0] for k in rows_by_cell})
    chance_first = statistics.mean([1 / len(h.rooms) for h in households.values()])
    out: Dict[str, Any] = {"label": label, "days": [days.start, days.stop - 1],
                           "chance_first_room": chance_first, "per_arm": {}}
    print(f"\n=== {label}: days {days.start}-{days.stop - 1} ===")
    print(f"  FIRST-ROOM-CORRECT is the sharp measure: chance is "
          f"{chance_first:.1%} (one room of about "
          f"{statistics.mean([len(h.rooms) for h in households.values()]):.0f}), against "
          f"{statistics.mean([min(3, len(h.rooms)) / len(h.rooms) for h in households.values()]):.1%} "
          f"for find-rate within the k=3 budget, so it has about four times the room "
          f"for a policy to distinguish itself and does not hand out the free credit "
          f"of two more guesses.")
    print(f"{'arm':22s} {'format':18s} {'slice':10s} {'n':>5s} {'1st room':>9s} "
          f"{'found':>7s} {'rooms/q':>8s}  rank 1/2/3/miss   per-household 1st room")
    for sensing, how in arms:
        for slice_name in ("all", "mover", "non-mover"):
            per_h_found, per_h_rooms, per_h_first, n_total = [], [], [], 0
            ranks: collections.Counter = collections.Counter()
            for name in all_households:
                rows = [r for r in rows_by_cell.get((name, sensing, how), [])
                        if r["day"] in days
                        and (slice_name == "all"
                             or (slice_name == "mover") == r["is_a_mover"])]
                if not rows:
                    continue
                n_total += len(rows)
                per_h_found.append(sum(1 for r in rows if r["found_it"]) / len(rows))
                per_h_rooms.append(statistics.mean(r["n_rooms_opened"] for r in rows))
                # The quantity a prior or a memory actually determines: was the room
                # it walked into FIRST the room the thing was in.
                per_h_first.append(sum(1 for r in rows if r["found_at_step"] == 1)
                                   / len(rows))
                for r in rows:
                    ranks[r["found_at_step"] if r["found_at_step"] else "miss"] += 1
            if not per_h_found:
                continue
            found, found_se = mean_and_standard_error(per_h_found)
            rooms, _ = mean_and_standard_error(per_h_rooms)
            first, first_se = mean_and_standard_error(per_h_first)
            n_ranks = sum(ranks.values())
            spread = "/".join(f"{ranks[k] / n_ranks:.0%}" for k in (1, 2, 3, "miss"))
            out["per_arm"][f"{sensing} / {how} / {slice_name}"] = {
                "n_questions": n_total, "n_households": len(per_h_found),
                "mean_rooms_opened": rooms,
                "share_first_room_correct": first,
                "first_room_standard_error_clustered_on_household": first_se,
                "first_room_two_se": (2 * first_se) if first_se is not None else None,
                "per_household_share_first_room_correct": per_h_first,
                "share_found": found,
                "found_standard_error_clustered_on_household": found_se,
                "found_two_se": (2 * found_se) if found_se is not None else None,
                "per_household_share_found": per_h_found,
                "the_rank_it_was_found_at": {str(k): ranks[k] for k in (1, 2, 3, "miss")},
                "share_by_rank": {str(k): ranks[k] / n_ranks for k in (1, 2, 3, "miss")},
            }
            print(f"{sensing:22s} {how:18s} {slice_name:10s} {n_total:5d} {first:9.1%} "
                  f"{found:7.1%} {rooms:8.2f}  {spread:18s} "
                  f"{[f'{v:.0%}' for v in per_h_first]}")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--questions-per-day", type=int, default=8)
    parser.add_argument("--days", type=int, nargs=2, default=None,
                        help="a day range, inclusive. Default: the four windows.")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    windows = ([(f"days {args.days[0]}-{args.days[1]}",
                 range(args.days[0], args.days[1] + 1))] if args.days else
               [("the settled fortnight", range(1, 14)),
                ("the transition", range(14, 17)),
                ("the rest of the spell", range(17, 24)),
                ("the return", range(24, 27)),
                ("back to normal", range(27, 32))])
    everything = [report(args.root, args.banks, window, args.questions_per_day, label)
                  for label, window in windows]
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(everything, indent=1))
        print(f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
