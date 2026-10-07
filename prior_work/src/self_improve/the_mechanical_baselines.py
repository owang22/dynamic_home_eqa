"""What one line of code gets, on the same look stream, with no model calls at all.

Every arm in this study has to beat these. They are computed from the arm's OWN look
stream, so an arm that sees more is scored against a baseline that sees more too, and
none of the twenty-times-the-observation advantage leaks into the comparison.

FOUR references, and the two on the choice side are new because this design has a
choice side that the patrol design did not:

  THE NEWEST-SIGHTING CHOOSER    open the room where you last saw it. The mechanical
                                 rival to the whole memory-guided arm. If the model's
                                 chooser does not beat this, the language model in the
                                 chooser has not earned its place.
  THE NEWEST-ROOM-OF-CLASS CHOOSER  when the object has never been seen, fall back to
                                 the room where things of its class are usually seen.
                                 Otherwise identical. This is the mechanical stand-in
                                 for the commonsense prior.

  THE NEWEST-SIGHTING RULE       answer with the object's most recent sighting,
                                 including sightings made earlier the same day. The
                                 answer-side reference the patrol arms were measured
                                 against.
  THE STENOGRAPHER               writes down every sighting the night it sees it,
                                 never forgets, never curates, never reasons; so at
                                 question time it knows the newest sighting up to the
                                 END OF YESTERDAY. The write-side reference. It is
                                 strictly weaker than the newest-sighting rule and the
                                 gap between them is the value of same-day evidence.

Scored at BOTH levels, and the room level is primary here rather than secondary.
Three separate findings now point at room granularity: a claim store equals the
newest-sighting rule in seven households at shelf level but only three at room level;
room-level revisions are a coin flip at 53% while shelf-level revisions help; and the
prior in this design works by choosing ROOMS, reaching 92% with empty notes. So the
question "does a curated memory add anything" is asked at room level first.

    python -m self_improve.the_mechanical_baselines --days 14 23 --movers-only
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.types import DAY_SECONDS
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.search_cost_from_the_looks import find_the_cells, mean_and_standard_error
from self_improve.search_driven import (answerable_questions_on_day,
                                        questions_spread_across_the_day, the_movers)


def score_one_cell(looks_file: pathlib.Path, household: FrozenHousehold,
                   days: range, movers_only: bool, questions_per_day: int = 8
                   ) -> Optional[Dict[str, Any]]:
    """Replay the look stream in time order and score every mechanical reference at
    each question, using only evidence that existed before the question was asked."""
    movers = the_movers(household)
    wanted: Dict[Tuple[int, int], dict] = {}
    for day in range(household.n_days + 1):
        for question in questions_spread_across_the_day(
                answerable_questions_on_day(household, day), questions_per_day):
            wanted[(question["day_index"], question["t_query"])] = question

    by_moment: Dict[Tuple[int, int], List[dict]] = collections.defaultdict(list)
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") == "look":
            by_moment[(row["day"], row["time"])].append(row)

    newest: Dict[str, Tuple[int, str, str]] = {}          # object -> (time, place, room)
    newest_by_end_of: Dict[int, Dict[str, Tuple[int, str, str]]] = {}
    class_rooms: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    tally: Dict[str, int] = collections.Counter()
    n = 0
    last_day_seen = -1

    for moment in sorted(by_moment):
        day = moment[0]
        if day != last_day_seen:
            # freeze what a nightly writer would have known at the end of each earlier day
            for earlier in range(last_day_seen + 1, day + 1):
                newest_by_end_of[earlier] = dict(newest)
            last_day_seen = day
        looks = sorted(by_moment[moment], key=lambda r: r["look_id"])
        question = wanted.get(moment)
        in_scope = (question is not None and day in days
                    and (not movers_only or question["object_id"] in movers))
        if in_scope:
            object_id = question["object_id"]
            true_place = household.true_place_for_question(question)
            true_room = household.place_room.get(true_place or "")
            if true_place and true_room:
                n += 1
                first_room = looks[0]["targets"][0]["name"] if looks else None
                if first_room == true_room:
                    tally["the arm's own first room"] += 1

                # choice side: open the room where you last saw it
                mine = newest.get(object_id)
                if mine and mine[2] == true_room:
                    tally["newest-sighting chooser"] += 1
                # choice side, with a class fallback when it has never been seen
                if mine:
                    guess_room = mine[2]
                else:
                    klass = household.object_class.get(object_id, "")
                    counts = class_rooms.get(klass)
                    guess_room = counts.most_common(1)[0][0] if counts else None
                if guess_room == true_room:
                    tally["newest-room-of-class chooser"] += 1

                # answer side: the newest sighting, shelf and room
                if mine and mine[1] == true_place:
                    tally["newest-sighting rule, shelf"] += 1
                if mine and mine[2] == true_room:
                    tally["newest-sighting rule, room"] += 1
                # answer side: the stenographer, which only knows up to last night
                steno = (newest_by_end_of.get(day - 1) or {}).get(object_id)
                if steno and steno[1] == true_place:
                    tally["the stenographer, shelf"] += 1
                if steno and steno[2] == true_room:
                    tally["the stenographer, room"] += 1
                if mine is None:
                    tally["the object had never been seen at all"] += 1

        for look in looks:
            for s in look["sightings"]:
                newest[s["object_id"]] = (s["time"], s["place_id"], s["room"])
                klass = household.object_class.get(s["object_id"], "")
                if klass:
                    class_rooms[klass][s["room"]] += 1

    if not n:
        return None
    return {"household": household.name, "n_questions": n,
            "shares": {k: v / n for k, v in tally.items()},
            "counts": dict(tally)}


MEASURES = ("the arm's own first room", "newest-sighting chooser",
            "newest-room-of-class chooser", "newest-sighting rule, room",
            "the stenographer, room", "newest-sighting rule, shelf",
            "the stenographer, shelf", "the object had never been seen at all")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--days", type=int, nargs=2, default=None)
    parser.add_argument("--movers-only", action="store_true")
    parser.add_argument("--questions-per-day", type=int, default=8)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    windows = ([(f"days {args.days[0]}-{args.days[1]}",
                 range(args.days[0], args.days[1] + 1))] if args.days else
               [("the settled fortnight", range(1, 14)),
                ("the spell", range(14, 24)),
                ("back to normal", range(24, 32))])
    households: Dict[str, FrozenHousehold] = {}
    everything: Dict[str, Any] = {}

    for label, days in windows:
        per_cell: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        for key, looks_file in sorted(find_the_cells(args.root).items()):
            if key[0] not in households:
                households[key[0]] = FrozenHousehold(args.banks / f"{key[0]}.jsonl")
            got = score_one_cell(looks_file, households[key[0]], days,
                                 args.movers_only, args.questions_per_day)
            if got:
                per_cell[key] = got
        if not per_cell:
            continue
        print(f"\n=== {label}{', MOVERS ONLY' if args.movers_only else ''} ===")
        print("Every baseline is computed on the ARM'S OWN look stream, so an arm that "
              "sees\nmore is scored against a baseline that sees more too.\n")
        block: Dict[str, Any] = {}
        for sensing, how in sorted({(k[1], k[2]) for k in per_cell}):
            here = [v for k, v in per_cell.items() if k[1] == sensing and k[2] == how]
            print(f"--- {sensing} / {how}  ({len(here)} households, "
                  f"{sum(v['n_questions'] for v in here)} questions)")
            row: Dict[str, Any] = {}
            for measure in MEASURES:
                values = [v["shares"].get(measure, 0.0) for v in here]
                mean, se = mean_and_standard_error(values)
                row[measure] = {"mean": mean, "two_se": (2 * se) if se else None,
                                "per_household": values}
                print(f"      {measure:38s} {mean:6.1%}"
                      + (f"  (2 SE {2 * se:.3f})" if se else ""))
            # the contrast that decides whether the model earned its place
            own = row["the arm's own first room"]["mean"]
            rival = row["newest-sighting chooser"]["mean"]
            klass = row["newest-room-of-class chooser"]["mean"]
            diffs = [v["shares"].get("the arm's own first room", 0.0)
                     - v["shares"].get("newest-sighting chooser", 0.0) for v in here]
            mean_d, se_d = mean_and_standard_error(diffs)
            # The verdict has to be able to say the RULE won. A one-sided test that can
            # only report "the model beats it" or "not proven" would have printed
            # "does NOT clear the 2 SE bar" over a -10.3-point gap that clears the bar
            # in the rule's favour, which is the prose-not-matching-the-artifact error
            # this project keeps making.
            if se_d is None:
                verdict = "one household, no bar"
            elif mean_d > 2 * se_d:
                verdict = "THE MODEL BEATS THE RULE"
            elif -mean_d > 2 * se_d:
                verdict = "THE RULE BEATS THE MODEL"
            else:
                verdict = "neither clears the 2 SE bar; they are indistinguishable"
            print(f"      -> the model's chooser {own:.1%} against "
                  f"'open the room you last saw it in' {rival:.1%}: "
                  f"{mean_d:+.3f} paired within household"
                  + (f", 2 SE {2 * se_d:.3f}, {verdict}" if se_d is not None else ""))
            print(f"         and against the class fallback {klass:.1%}")
            row["the_models_chooser_minus_the_newest_sighting_chooser"] = {
                "mean": mean_d, "two_se": (2 * se_d) if se_d else None,
                "per_household": diffs, "verdict": verdict}
            block[f"{sensing} / {how}"] = row
            print()
        everything[label] = block

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(
            {"movers_only": args.movers_only, "windows": everything}, indent=1))
        print(f"written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
